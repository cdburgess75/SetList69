#!/usr/bin/env python3
# remote7300 -- iPad web control for the Icom IC-7300MK2 over your LAN.
#
# v2026.07.19.001  Initial release: connect to the radio's LAN port using the
#                  Icom network (RS-BA1) protocol, control frequency and mode
#                  from any browser on the network via a built-in web page.
#
# One file, standard library only. Run it on any always-on computer
# (Mac / Windows / Linux / Raspberry Pi) that is on the same network
# as the radio:
#
#     python3 remote7300.py --radio 192.168.1.50 --username ipad --password secret
#
# then open  http://<computer-ip>:7300  in Safari on the iPad and
# "Add to Home Screen".
#
# The radio must have network control enabled:
#   MENU >> SET >> Network >> Network Control : ON
#   MENU >> SET >> Network >> Network User1   : set ID + password
# (defaults: Control port 50001 -- leave as-is unless you changed it)
#
# Protocol notes: the LAN control protocol is Icom's RS-BA1 UDP protocol
# (control stream on 50001, then radio-assigned CI-V and audio streams).
# This implementation is based on the openly documented reverse engineering
# in the wfview (GPL, gitlab.com/eliggett/wfview) and kappanhang projects.
# Only the CI-V stream is used for data; the audio stream is opened but
# discarded (this tool is a head, not a remote receiver).

import argparse
import json
import os
import queue
import select
import socket
import struct
import sys
import threading
import time
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------- protocol --

PING_PERIOD = 0.5       # our ping cadence per stream
IDLE_PERIOD = 0.1       # tracked idle packet cadence
AYT_PERIOD = 0.5        # "are you there" retry cadence
TOKEN_RENEWAL = 60.0    # token renewal cadence (control stream)
CIV_POLL = 1.0          # freq/mode poll cadence (belt + braces with transceive)
STALE_SECONDS = 15.0    # no packets from radio -> reconnect
CONTROLLER_ADDR = 0xE0  # our CI-V bus address

MODES = {  # CI-V mode codes for cmd 0x01/0x04/0x06
    0x00: "LSB", 0x01: "USB", 0x02: "AM", 0x03: "CW",
    0x04: "RTTY", 0x05: "FM", 0x07: "CW-R", 0x08: "RTTY-R",
}
MODE_CODES = {v: k for k, v in MODES.items()}

# Username/password scrambler used by the login packet (fixed substitution
# table indexed by char code + position; same table as RS-BA1/wfview).
_PASSCODE_SEQ = bytes(32) + bytes([
    0x47, 0x5d, 0x4c, 0x42, 0x66, 0x20, 0x23, 0x46, 0x4e, 0x57, 0x45, 0x3d,
    0x67, 0x76, 0x60, 0x41, 0x62, 0x39, 0x59, 0x2d, 0x68, 0x7e, 0x7c, 0x65,
    0x7d, 0x49, 0x29, 0x72, 0x73, 0x78, 0x21, 0x6e, 0x5a, 0x5e, 0x4a, 0x3e,
    0x71, 0x2c, 0x2a, 0x54, 0x3c, 0x3a, 0x63, 0x4f, 0x43, 0x75, 0x27, 0x79,
    0x5b, 0x35, 0x70, 0x48, 0x6b, 0x56, 0x6f, 0x34, 0x32, 0x6c, 0x30, 0x61,
    0x6d, 0x7b, 0x2f, 0x4b, 0x64, 0x38, 0x2b, 0x2e, 0x50, 0x40, 0x3f, 0x55,
    0x33, 0x37, 0x25, 0x77, 0x24, 0x26, 0x74, 0x6a, 0x28, 0x53, 0x4d, 0x69,
    0x22, 0x5c, 0x44, 0x31, 0x36, 0x58, 0x3b, 0x7a, 0x51, 0x5f, 0x52,
]) + bytes(129 - 127)


def passcode(text):
    out = bytearray()
    data = text.encode("latin-1", "replace")[:16]
    for i, ch in enumerate(data):
        p = ch + i
        if p > 126:
            p = 32 + p % 127
        out.append(_PASSCODE_SEQ[p])
    return bytes(out)


def header(length, ptype, seq, my_id, remote_id):
    return struct.pack("<IHHII", length, ptype, seq, my_id, remote_id)


def freq_to_bcd(hz):
    d = "%010d" % hz
    return bytes(int(d[8 - 2 * i]) << 4 | int(d[9 - 2 * i]) for i in range(5))


def bcd_to_freq(b):
    hz = 0
    for i, byte in enumerate(b[:5]):
        hz += (byte & 0x0F) * 10 ** (2 * i)
        hz += (byte >> 4) * 10 ** (2 * i + 1)
    return hz


def now_ms():
    return int(time.monotonic() * 1000) & 0xFFFFFFFF


def log(*args):
    print(time.strftime("[%H:%M:%S]"), *args, flush=True)


# ------------------------------------------------------------- UDP streams --

class UdpStream(threading.Thread):
    """One UDP stream of the Icom network protocol (control / CI-V / audio).

    Handles the shared plumbing: are-you-there handshake, ping request/reply,
    tracked-packet sequence numbers, retransmit requests both ways, and idle
    packets. Subclasses hook on_ready() and handle_other()."""

    name_ = "stream"
    sends_idle = True

    def __init__(self, radio_ip, sock=None):
        super().__init__(daemon=True)
        self.radio_ip = radio_ip
        self.port = 0  # set by connect_to()
        self.sock = sock or socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if sock is None:
            self.sock.bind(("", 0))
        self.local_port = self.sock.getsockname()[1]
        self.my_id = self._make_id()
        self.remote_id = 0
        self.send_seq = 1
        self.ping_seq = 0
        self.tx_buf = OrderedDict()     # seq -> datagram (for retransmits)
        self.rx_last_seq = None
        self.rx_requested = {}          # missing seq -> retry count
        self.got_here = False
        self.ready = False
        self.last_rx = time.monotonic()
        self.last_ping = 0.0
        self.last_idle = 0.0
        self.last_ayt = 0.0
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()

    def _make_id(self):
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.connect((self.radio_ip, 1))
            ip = struct.unpack(">I", socket.inet_aton(probe.getsockname()[0]))[0]
            probe.close()
        except OSError:
            ip = struct.unpack(">I", os.urandom(4))[0]
        return ((ip >> 8 & 0xFF) << 24 | (ip & 0xFF) << 16 | self.local_port) & 0xFFFFFFFF

    def connect_to(self, port):
        if self.port:
            return
        self.port = port
        self.start()

    def run(self):
        while not self.stop_flag.is_set():
            r, _, _ = select.select([self.sock], [], [], 0.02)
            if r:
                try:
                    while True:
                        data, addr = self.sock.recvfrom(4096)
                        self.last_rx = time.monotonic()
                        try:
                            self.handle_datagram(data)
                        except (struct.error, IndexError):
                            pass
                        rr, _, _ = select.select([self.sock], [], [], 0)
                        if not rr:
                            break
                except OSError:
                    break
            self.tick(time.monotonic())

    def close(self):
        self.stop_flag.set()
        try:
            self.sock.close()
        except OSError:
            pass

    # -- sending ------------------------------------------------------------

    def _sendto(self, data):
        try:
            self.sock.sendto(data, (self.radio_ip, self.port))
        except OSError:
            pass

    def send_control(self, ptype, seq=0):
        self._sendto(header(0x10, ptype, seq, self.my_id, self.remote_id))

    def send_tracked(self, data):
        with self.lock:
            seq = self.send_seq
            self.send_seq = (self.send_seq + 1) & 0xFFFF
            if self.send_seq == 0:
                self.send_seq = 1
                self.tx_buf.clear()
            data = data[:6] + struct.pack("<H", seq) + data[8:]
            self.tx_buf[seq] = data
            while len(self.tx_buf) > 500:
                self.tx_buf.popitem(last=False)
        self._sendto(data)
        self.last_idle = time.monotonic()

    def send_ping(self):
        p = header(0x15, 0x07, self.ping_seq, self.my_id, self.remote_id)
        p += b"\x00" + struct.pack("<I", now_ms())
        self._sendto(p)

    # -- receiving ----------------------------------------------------------

    def handle_datagram(self, r):
        if len(r) < 0x10:
            return
        length, ptype, seq, sentid, rcvdid = struct.unpack_from("<IHHII", r)

        if len(r) == 0x10:
            if ptype == 0x01:               # single retransmit request
                self._retransmit(seq)
            elif ptype == 0x04:             # "I am here"
                self.remote_id = sentid
                if not self.got_here:
                    self.got_here = True
                    log(self.name_, "radio is here (id %08x)" % sentid)
                self.send_control(0x06, 0x01)   # "are you ready"
            elif ptype == 0x06:             # "I am ready"
                self.remote_id = sentid
                if not self.ready:
                    self.ready = True
                    log(self.name_, "radio is ready")
                    self.on_ready()
            return

        if len(r) == 0x15 and ptype == 0x07:    # ping
            reply = r[0x10]
            if reply == 0x00:
                p = header(0x15, 0x07, seq, self.my_id, self.remote_id)
                p += b"\x01" + r[0x11:0x15]
                self._sendto(p)
            elif reply == 0x01 and seq == self.ping_seq:
                self.ping_seq = (self.ping_seq + 1) & 0xFFFF
            return

        if ptype == 0x01:                   # multi retransmit request
            for off in range(0x10, len(r) - 1, 2):
                self._retransmit(struct.unpack_from("<H", r, off)[0])
            return

        if ptype == 0x00 and seq != 0:
            self._track_incoming(seq)
        self.handle_other(r, ptype)

    def _retransmit(self, seq):
        with self.lock:
            data = self.tx_buf.get(seq)
        if data is not None:
            self._sendto(data)
        else:
            self.send_control(0x00, seq)    # gone; placate with an idle

    def _track_incoming(self, seq):
        last = self.rx_last_seq
        self.rx_last_seq = seq
        if last is None:
            return
        gap = (seq - last) & 0xFFFF
        if 1 < gap <= 50:
            for missing in range(1, gap):
                m = (last + missing) & 0xFFFF
                if self.rx_requested.get(m, 0) < 2:
                    self.rx_requested[m] = self.rx_requested.get(m, 0) + 1
                    self.send_control(0x01, m)
            if len(self.rx_requested) > 200:
                self.rx_requested.clear()

    # -- timers -------------------------------------------------------------

    def tick(self, now):
        if not self.got_here:
            if now - self.last_ayt >= AYT_PERIOD:
                self.last_ayt = now
                self.send_control(0x03)
            return
        if now - self.last_ping >= PING_PERIOD:
            self.last_ping = now
            self.send_ping()
        if self.sends_idle and self.ready and now - self.last_idle >= IDLE_PERIOD:
            self.send_tracked(header(0x10, 0x00, 0, self.my_id, self.remote_id))
        self.tick_extra(now)

    # -- subclass hooks -----------------------------------------------------

    def on_ready(self):
        pass

    def handle_other(self, r, ptype):
        pass

    def tick_extra(self, now):
        pass

    def disconnect(self):
        self.send_control(0x05)
        self.close()


class CivStream(UdpStream):
    """The CI-V data stream: carries raw CI-V frames to/from the radio."""

    name_ = "civ"

    def __init__(self, radio_ip, link):
        super().__init__(radio_ip)
        self.link = link
        self.civ_seq = 0            # separate counter for open/close + data
        self.buf = bytearray()
        self.open_sent_at = 0.0
        self.got_data = False
        self.last_poll = 0.0

    def on_ready(self):
        self.send_openclose(True)

    def send_openclose(self, open_):
        p = header(0x16, 0x00, 0, self.my_id, self.remote_id)
        p += struct.pack("<H", 0x01C0) + b"\x00"
        p += struct.pack(">H", self.civ_seq)
        p += b"\x04" if open_ else b"\x00"
        self.civ_seq = (self.civ_seq + 1) & 0xFFFF
        self.open_sent_at = time.monotonic()
        self.send_tracked(p)

    def send_civ(self, body):
        frame = bytes([0xFE, 0xFE, self.link.civ_addr, CONTROLLER_ADDR]) + body + b"\xFD"
        p = header(0x15 + len(frame), 0x00, 0, self.my_id, self.remote_id)
        p += b"\xC1" + struct.pack("<H", len(frame)) + struct.pack(">H", self.civ_seq)
        self.civ_seq = (self.civ_seq + 1) & 0xFFFF
        self.send_tracked(p + frame)

    def handle_other(self, r, ptype):
        if len(r) <= 0x15 or ptype == 0x01:
            return
        length = struct.unpack_from("<I", r)[0]
        datalen = struct.unpack_from("<H", r, 0x11)[0]
        if datalen + 0x15 != length or len(r) < 0x15 + datalen:
            return
        self.got_data = True
        self.buf += r[0x15:0x15 + datalen]
        self._parse_civ()

    def _parse_civ(self):
        while True:
            start = self.buf.find(b"\xFE\xFE")
            if start < 0:
                self.buf.clear()
                return
            end = self.buf.find(b"\xFD", start)
            if end < 0:
                if start:
                    del self.buf[:start]
                return
            frame = bytes(self.buf[start:end + 1])
            del self.buf[:end + 1]
            if len(frame) >= 6 and frame[3] != CONTROLLER_ADDR:
                self.link.handle_civ_frame(frame)

    def tick_extra(self, now):
        if not self.ready:
            return
        # keep asking the radio to start CI-V until data flows
        if not self.got_data and now - self.open_sent_at >= 0.5:
            self.send_openclose(True)
        if now - self.last_poll >= CIV_POLL:
            self.last_poll = now
            self.send_civ(b"\x03")      # read frequency
            self.send_civ(b"\x04")      # read mode

    def disconnect(self):
        if self.ready:
            self.send_openclose(False)
        super().disconnect()


class AudioStream(UdpStream):
    """We must accept the audio stream for the session to be healthy, but we
    discard everything: this tool is a controller, not a remote receiver."""

    name_ = "audio"
    sends_idle = False


class ControlStream(UdpStream):
    """The main control stream: login, token upkeep, stream negotiation."""

    name_ = "control"

    def __init__(self, radio_ip, port, username, password, link):
        super().__init__(radio_ip)
        self.port = port
        self.username = username
        self.password = password
        self.link = link
        self.auth_seq = 0x30
        self.tok_request = struct.unpack("<H", os.urandom(2))[0]
        self.token = b"\x00\x00\x00\x00"
        self.authenticated = False
        self.stream_requested = False
        self.radio_cap = None
        self.last_token = 0.0
        comp = socket.gethostname().split(".")[0][:8] or "bridge"
        self.comp_name = (comp + "-r7300")[:15]

    # -- auth-style packet builders -----------------------------------------

    def _auth_header(self, size, reqtype):
        p = bytearray(header(size, 0x00, 0, self.my_id, self.remote_id))
        p += bytearray(size - 0x10)
        struct.pack_into(">I", p, 0x10, size - 0x10)
        p[0x14] = 0x01
        p[0x15] = reqtype
        struct.pack_into(">H", p, 0x16, self.auth_seq)
        self.auth_seq = (self.auth_seq + 1) & 0xFFFF
        struct.pack_into("<H", p, 0x1A, self.tok_request)
        p[0x1C:0x20] = self.token
        return p

    def send_login(self):
        log("control", "logging in as", self.username)
        p = self._auth_header(0x80, 0x00)
        p[0x1C:0x20] = b"\x00\x00\x00\x00"
        user = passcode(self.username)
        pw = passcode(self.password)
        p[0x40:0x40 + len(user)] = user
        p[0x50:0x50 + len(pw)] = pw
        name = self.comp_name.encode()
        p[0x60:0x60 + len(name)] = name
        self.send_tracked(bytes(p))

    def send_token(self, reqtype):
        p = self._auth_header(0x40, reqtype)
        struct.pack_into(">H", p, 0x24, 0x0798)
        self.send_tracked(bytes(p))

    def send_stream_request(self):
        cap = self.radio_cap
        p = self._auth_header(0x90, 0x03)
        p[0x20:0x30] = cap["identity"]
        name = cap["name"].encode()[:31]
        p[0x40:0x40 + len(name)] = name
        user = passcode(self.username)
        p[0x60:0x60 + len(user)] = user
        p[0x70] = 0x01                          # rx audio enable
        p[0x71] = 0x00                          # tx audio disable
        p[0x72] = 0x04                          # rx codec: LPCM 16-bit
        p[0x73] = 0x00
        struct.pack_into(">I", p, 0x74, 48000)  # rx sample rate
        struct.pack_into(">I", p, 0x78, 0)
        struct.pack_into(">I", p, 0x7C, self.link.civ.local_port)
        struct.pack_into(">I", p, 0x80, self.link.audio.local_port)
        struct.pack_into(">I", p, 0x84, 150)
        p[0x88] = 0x01
        self.stream_requested = True
        self.send_tracked(bytes(p))

    # -- protocol events ----------------------------------------------------

    def on_ready(self):
        self.send_login()

    def handle_other(self, r, ptype):
        if ptype == 0x01:
            return
        size = len(r)
        if size == 0x60:
            self._on_login_response(r)
        elif size == 0x40:
            self._on_token_response(r)
        elif size == 0x50:
            self._on_status(r)
        elif size == 0x90:
            self._on_conninfo(r)
        elif size >= 0x42 + 0x66 and (size - 0x42) % 0x66 == 0:
            self._on_capabilities(r)

    def _on_login_response(self, r):
        error = struct.unpack_from("<I", r, 0x30)[0]
        if error == 0xFEFFFFFF:
            log("control", "LOGIN REJECTED: invalid username/password")
            self.link.fail("Invalid username/password (check radio's Network User1)")
            return
        if struct.unpack_from("<H", r, 0x1A)[0] != self.tok_request:
            return
        if not self.authenticated:
            self.authenticated = True
            self.token = bytes(r[0x1C:0x20])
            log("control", "login OK, token %s" % self.token.hex())
            self.send_token(0x02)               # confirm token
            self.last_token = time.monotonic()

    def _on_token_response(self, r):
        response = struct.unpack_from("<I", r, 0x30)[0]
        if response == 0xFFFFFFFF:
            log("control", "token rejected, re-requesting stream")
            self.stream_requested = False
        # response 0x0000 = renewal OK; nothing to do

    def _on_capabilities(self, r):
        cap = r[0x42:0x42 + 0x66]
        commoncap = struct.unpack_from("<H", cap, 0x07)[0]
        self.radio_cap = {
            "identity": bytes(cap[0:16]),
            "commoncap": commoncap,
            "name": cap[0x10:0x30].split(b"\x00")[0].decode("ascii", "replace"),
            "civ": cap[0x52],
        }
        log("control", "radio: %s  civ addr %02x" % (self.radio_cap["name"], cap[0x52]))
        self.link.on_capabilities(self.radio_cap)

    def _on_conninfo(self, r):
        busy = struct.unpack_from("<I", r, 0x60)[0]
        computer = r[0x64:0x74].split(b"\x00")[0].decode("ascii", "replace")
        if busy and computer and computer != self.comp_name:
            log("control", "radio in use by", computer)
            self.link.set_status("Radio in use by " + computer)
            seq = struct.unpack_from("<H", r, 0x06)[0]
            self.send_control(0x00, seq)
            return
        if self.radio_cap and self.authenticated and not self.stream_requested:
            log("control", "requesting CI-V + audio streams")
            self.send_stream_request()

    def _on_status(self, r):
        ptype = struct.unpack_from("<H", r, 0x04)[0]
        if ptype == 0x01:
            return
        error = struct.unpack_from("<I", r, 0x30)[0]
        disc = r[0x40]
        if error == 0xFFFFFFFF:
            log("control", "radio refused connection (reboot radio?)")
            self.link.fail("Radio refused connection - try power-cycling it")
            return
        if error == 0 and disc == 0x01:
            log("control", "radio closed the streams")
            self.stream_requested = False
            return
        civ_port = struct.unpack_from(">H", r, 0x42)[0]
        audio_port = struct.unpack_from(">H", r, 0x46)[0]
        if civ_port:
            self.link.on_streams_granted(civ_port, audio_port)

    def tick_extra(self, now):
        if self.authenticated and now - self.last_token >= TOKEN_RENEWAL:
            self.last_token = now
            self.send_token(0x05)               # renew

    def disconnect(self):
        if self.authenticated:
            self.send_token(0x01)               # remove token
        super().disconnect()


# ------------------------------------------------------------- radio link --

class RadioLink:
    """Owns the three streams, the CI-V conversation, and published state."""

    def __init__(self, radio_ip, control_port, username, password, civ_addr=None):
        self.radio_ip = radio_ip
        self.control_port = control_port
        self.username = username
        self.password = password
        self.civ_addr_override = civ_addr
        self.civ_addr = civ_addr or 0xA4
        self.control = None
        self.civ = None
        self.audio = None
        self.stop_flag = threading.Event()
        self.fatal = None
        self.cond = threading.Condition()
        self.version = 0
        self.state = {
            "connected": False, "status": "Connecting to radio...",
            "radio": "", "freq": 0, "mode": "", "filter": 1,
        }

    # -- published state ----------------------------------------------------

    def update(self, **kw):
        with self.cond:
            changed = False
            for k, v in kw.items():
                if self.state.get(k) != v:
                    self.state[k] = v
                    changed = True
            if changed:
                self.version += 1
                self.cond.notify_all()

    def snapshot(self):
        with self.cond:
            return dict(self.state), self.version

    def wait_change(self, version, timeout):
        with self.cond:
            self.cond.wait_for(lambda: self.version != version or self.stop_flag.is_set(),
                               timeout)
            return dict(self.state), self.version

    def set_status(self, text):
        self.update(status=text)

    def fail(self, text):
        self.fatal = text
        self.update(connected=False, status=text)

    # -- lifecycle ----------------------------------------------------------

    def supervise(self):
        """Blocking: keep a session up, reconnecting whenever it goes stale."""
        while not self.stop_flag.is_set():
            self.fatal = None
            self.update(connected=False, status="Connecting to radio...")
            try:
                self._run_session()
            except Exception as exc:
                log("link", "session error:", repr(exc))
            self._teardown()
            if self.stop_flag.is_set():
                break
            delay = 30 if self.fatal else 3
            self.update(connected=False,
                        status=(self.fatal or "Connection lost") + " - retrying...")
            log("link", "reconnecting in %ds" % delay)
            self.stop_flag.wait(delay)

    def _run_session(self):
        self.civ = CivStream(self.radio_ip, self)
        self.audio = AudioStream(self.radio_ip)
        self.control = ControlStream(self.radio_ip, self.control_port,
                                     self.username, self.password, self)
        log("link", "connecting to %s:%d" % (self.radio_ip, self.control_port))
        self.control.start()
        while not self.stop_flag.is_set() and self.fatal is None:
            time.sleep(0.5)
            quiet = time.monotonic() - self.control.last_rx
            if self.control.got_here and quiet > STALE_SECONDS:
                log("link", "control stream stale (%.0fs quiet)" % quiet)
                return
            if not self.control.got_here and quiet > 10:
                self.update(status="Radio not responding at %s:%d"
                            % (self.radio_ip, self.control_port))

    def _teardown(self):
        for s in (self.civ, self.audio, self.control):
            if s is not None:
                try:
                    s.disconnect()
                except Exception:
                    pass
        for s in (self.civ, self.audio, self.control):
            if s is not None and s.is_alive():
                s.join(timeout=1)
        self.civ = self.audio = self.control = None

    def shutdown(self):
        self.stop_flag.set()
        with self.cond:
            self.cond.notify_all()

    # -- events from streams ------------------------------------------------

    def on_capabilities(self, cap):
        if self.civ_addr_override is None and cap["civ"]:
            self.civ_addr = cap["civ"]
        self.update(radio=cap["name"])

    def on_streams_granted(self, civ_port, audio_port):
        if self.civ and not self.civ.is_alive():
            log("link", "opening CI-V stream to port %d, audio to %d"
                % (civ_port, audio_port))
            self.civ.connect_to(civ_port)
            self.audio.connect_to(audio_port)

    def handle_civ_frame(self, frame):
        # frame = FE FE <to> <from> <cmd...> FD
        body = frame[4:-1]
        if not body:
            return
        cmd = body[0]
        if cmd in (0x00, 0x03) and len(body) >= 6:      # frequency
            self.update(connected=True, status="Connected",
                        freq=bcd_to_freq(body[1:6]))
        elif cmd in (0x01, 0x04) and len(body) >= 2:    # mode + filter
            filt = body[2] if len(body) >= 3 else 1
            self.update(connected=True, status="Connected",
                        mode=MODES.get(body[1], "?%02x" % body[1]), filter=filt)
        elif cmd == 0xFA:
            log("civ", "radio replied NG to last command")

    # -- commands from the web UI -------------------------------------------

    def _civ_ready(self):
        return self.civ is not None and self.civ.got_data

    def set_frequency(self, hz):
        hz = max(30_000, min(74_800_000, int(hz)))
        if not self._civ_ready():
            return False
        self.civ.send_civ(b"\x05" + freq_to_bcd(hz))
        self.update(freq=hz)
        return True

    def set_mode(self, mode_name):
        code = MODE_CODES.get(mode_name)
        if code is None or not self._civ_ready():
            return False
        self.civ.send_civ(bytes([0x06, code, 0x01]))
        self.update(mode=mode_name)
        return True


# -------------------------------------------------------------- web server --

class Handler(BaseHTTPRequestHandler):
    link = None  # injected
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/state":
            state, _ = self.link.snapshot()
            self._json(state)
        elif self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            state, version = self.link.snapshot()
            try:
                self.wfile.write(b"data: " + json.dumps(state).encode() + b"\n\n")
                self.wfile.flush()
                while not self.link.stop_flag.is_set():
                    state, new_version = self.link.wait_change(version, 15)
                    if new_version != version:
                        version = new_version
                        self.wfile.write(b"data: " + json.dumps(state).encode() + b"\n\n")
                    else:
                        self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
            except OSError:
                pass
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path != "/api/set":
            self._json({"error": "not found"}, 404)
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, TypeError):
            self._json({"error": "bad request"}, 400)
            return
        ok = True
        if "freq" in req:
            ok = self.link.set_frequency(req["freq"]) and ok
        if "mode" in req:
            ok = self.link.set_mode(str(req["mode"])) and ok
        state, _ = self.link.snapshot()
        state["ok"] = ok
        self._json(state, 200 if ok else 503)


# The whole iPad UI, self-contained (no external fonts/libs: works offline).
PAGE = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>IC-7300 Remote</title>
<style>
:root{
  --bg:#121110; --panel:#1c1a18; --ink:#f4efe7; --dim:#9b9184;
  --chord:#ffc24d; --line:#33302c; --good:#5fbf77; --bad:#d06a4e;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --ui:"Hanken Grotesk",-apple-system,system-ui,sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
html,body{height:100%;background:var(--bg);color:var(--ink);font-family:var(--ui);
  -webkit-user-select:none;user-select:none;overscroll-behavior:none}
.app{max-width:44rem;margin:0 auto;padding:calc(.6rem + env(safe-area-inset-top)) 1rem calc(1rem + env(safe-area-inset-bottom));
  display:flex;flex-direction:column;gap:.8rem;min-height:100%}
header{display:flex;align-items:center;gap:.6rem}
.dot{width:.7rem;height:.7rem;border-radius:50%;background:var(--bad);flex:none;transition:background .3s}
.dot.on{background:var(--good)}
h1{font-size:1rem;font-weight:700;letter-spacing:.02em}
#status{font-size:.8rem;color:var(--dim);margin-left:auto;text-align:right}
.freqbox{background:var(--panel);border:1px solid var(--line);border-radius:1rem;
  padding:1rem .5rem;text-align:center;cursor:pointer}
#freq{font-family:var(--mono);font-weight:600;font-size:clamp(2.4rem,11vw,4.6rem);
  letter-spacing:.02em;color:var(--chord);line-height:1.1;white-space:nowrap}
#freq .hz{color:var(--dim);font-size:.55em}
#freq.stale{color:var(--dim)}
.hint{font-size:.72rem;color:var(--dim);margin-top:.2rem}
.grid{display:grid;gap:.5rem}
.modes{grid-template-columns:repeat(4,1fr)}
.bands{grid-template-columns:repeat(6,1fr)}
.steps{grid-template-columns:repeat(5,1fr)}
.tune{grid-template-columns:1fr 1fr}
button{font-family:var(--ui);font-size:1.05rem;font-weight:700;color:var(--ink);
  background:var(--panel);border:1px solid var(--line);border-radius:.8rem;
  padding:.85rem 0;cursor:pointer;touch-action:manipulation}
button:active{background:#2a2724}
button.sel{background:var(--chord);color:#161310;border-color:var(--chord)}
button.big{font-size:2rem;padding:1.05rem 0;line-height:1}
button:disabled{opacity:.35}
.sect{font-size:.7rem;letter-spacing:.14em;color:var(--dim);text-transform:uppercase;margin:.2rem 0 -.2rem .2rem}
/* keypad modal */
#pad{position:fixed;inset:0;background:rgba(10,9,8,.82);display:none;
  align-items:center;justify-content:center;z-index:10}
#pad.show{display:flex}
.padbox{background:var(--panel);border:1px solid var(--line);border-radius:1.2rem;
  padding:1rem;width:min(20rem,92vw);display:flex;flex-direction:column;gap:.6rem}
#padout{font-family:var(--mono);font-size:1.9rem;text-align:right;color:var(--chord);
  min-height:2.4rem;padding:0 .3rem}
.padgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem}
.padhint{font-size:.72rem;color:var(--dim);text-align:center}
</style></head><body>
<div class="app">
  <header>
    <div class="dot" id="dot"></div>
    <h1 id="radioname">IC-7300</h1>
    <div id="status">connecting&hellip;</div>
  </header>

  <div class="freqbox" id="freqbox">
    <div id="freq" class="stale">--.---.---</div>
    <div class="hint">tap to enter a frequency</div>
  </div>

  <div class="sect">Tune</div>
  <div class="grid steps" id="steprow"></div>
  <div class="grid tune">
    <button class="big" id="down">&#9660;</button>
    <button class="big" id="up">&#9650;</button>
  </div>

  <div class="sect">Mode</div>
  <div class="grid modes" id="moderow"></div>

  <div class="sect">Band</div>
  <div class="grid bands" id="bandrow"></div>
</div>

<div id="pad"><div class="padbox">
  <div id="padout">&nbsp;</div>
  <div class="padgrid" id="padgrid"></div>
  <div class="padhint">MHz (e.g. 7.2) &mdash; or kHz if &gt; 75</div>
</div></div>

<script>
"use strict";
var state={freq:0,mode:"",connected:false};
var MODES=["LSB","USB","CW","CW-R","AM","FM","RTTY","RTTY-R"];
var STEPS=[[10,"10 Hz"],[100,"100 Hz"],[1000,"1 kHz"],[10000,"10 kHz"],[100000,"100 kHz"]];
var BANDS=[["160",1800000,2000000,1900000,"LSB"],["80",3500000,4000000,3850000,"LSB"],
 ["60",5330500,5406400,5358500,"USB"],["40",7000000,7300000,7200000,"LSB"],
 ["30",10100000,10150000,10120000,"CW"],["20",14000000,14350000,14250000,"USB"],
 ["17",18068000,18168000,18130000,"USB"],["15",21000000,21450000,21300000,"USB"],
 ["12",24890000,24990000,24950000,"USB"],["10",28000000,29700000,28400000,"USB"],
 ["6",50000000,54000000,50125000,"USB"]];
var step=1000;
var mem={};
try{mem=JSON.parse(localStorage.getItem("r7300.bands")||"{}")}catch(e){}

function $(id){return document.getElementById(id)}
function fmt(f){
  if(!f)return "--.---.---";
  var s=(""+f).padStart(7,"0");
  var mhz=s.slice(0,-6).replace(/^0+(?=\d)/,""), khz=s.slice(-6,-3), hz=s.slice(-3);
  return mhz+"."+khz+'.<span class="hz">'+hz+"</span>";
}
function bandOf(f){for(var i=0;i<BANDS.length;i++){if(f>=BANDS[i][1]&&f<=BANDS[i][2])return BANDS[i][0]}return null}
function render(){
  $("dot").className="dot"+(state.connected?" on":"");
  $("status").textContent=state.status||"";
  if(state.radio)$("radioname").textContent=state.radio;
  $("freq").innerHTML=fmt(state.freq);
  $("freq").className=state.connected?"":"stale";
  MODES.forEach(function(m){$("m-"+m).className=(m===state.mode)?"sel":""});
  var b=bandOf(state.freq);
  BANDS.forEach(function(bd){$("b-"+bd[0]).className=(bd[0]===b)?"sel":""});
  if(state.connected&&state.freq&&b){mem[b]={f:state.freq,m:state.mode};
    try{localStorage.setItem("r7300.bands",JSON.stringify(mem))}catch(e){}}
}
function send(obj){
  fetch("/api/set",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify(obj)}).catch(function(){});
}
function setFreq(f){f=Math.round(f);if(f<30000||f>74800000)return;
  state.freq=f;render();send({freq:f})}
function nudge(dir){if(state.freq)setFreq(state.freq+dir*step)}

/* build buttons */
MODES.forEach(function(m){var b=document.createElement("button");b.id="m-"+m;
  b.textContent=m;b.onclick=function(){state.mode=m;render();send({mode:m})};
  $("moderow").appendChild(b)});
BANDS.forEach(function(bd){var b=document.createElement("button");b.id="b-"+bd[0];
  b.textContent=bd[0];b.onclick=function(){
    var m=mem[bd[0]];var f=m?m.f:bd[3];var md=m?m.m:bd[4];
    setFreq(f);if(md&&md!==state.mode){state.mode=md;send({mode:md})}render()};
  $("bandrow").appendChild(b)});
STEPS.forEach(function(s){var b=document.createElement("button");b.id="s-"+s[0];
  b.textContent=s[1];b.style.fontSize=".85rem";
  b.onclick=function(){step=s[0];STEPS.forEach(function(x){$("s-"+x[0]).classList.remove("sel")});
    b.classList.add("sel")};
  if(s[0]===step)b.className="sel";
  $("steprow").appendChild(b)});

/* press-and-hold repeat on tune buttons */
function holdable(el,dir){
  var t=null,iv=null;
  function start(ev){ev.preventDefault();nudge(dir);
    t=setTimeout(function(){iv=setInterval(function(){nudge(dir)},140)},450)}
  function stop(){clearTimeout(t);clearInterval(iv)}
  el.addEventListener("touchstart",start,{passive:false});
  el.addEventListener("touchend",stop);el.addEventListener("touchcancel",stop);
  el.addEventListener("mousedown",start);
  el.addEventListener("mouseup",stop);el.addEventListener("mouseleave",stop);
}
holdable($("up"),1);holdable($("down"),-1);

/* keypad */
var padval="";
function padRender(){$("padout").textContent=padval||" "}
[["7","8","9"],["4","5","6"],["1","2","3"],[".","0","⌫"]].forEach(function(row){
  row.forEach(function(k){var b=document.createElement("button");b.textContent=k;
    b.onclick=function(){
      if(k==="⌫")padval=padval.slice(0,-1);
      else if(k==="."){if(padval.indexOf(".")<0)padval+=k}
      else padval+=k;
      padRender()};
    $("padgrid").appendChild(b)})});
var ok=document.createElement("button");ok.textContent="SET";ok.className="sel";
ok.style.gridColumn="1 / span 3";
ok.onclick=function(){
  var v=parseFloat(padval);
  if(!isNaN(v)&&v>0){setFreq(v<=75?v*1e6:v*1e3)}
  $("pad").classList.remove("show")};
$("padgrid").appendChild(ok);
$("freqbox").onclick=function(){padval="";padRender();$("pad").classList.add("show")};
$("pad").onclick=function(e){if(e.target===this)this.classList.remove("show")};

/* live updates */
function connectSSE(){
  var es=new EventSource("/events");
  es.onmessage=function(e){try{state=JSON.parse(e.data);render()}catch(err){}};
  es.onerror=function(){state.connected=false;state.status="bridge offline";render()};
}
connectSSE();

/* keep the screen awake while performing station duties */
var wl=null;
function wake(){if(navigator.wakeLock&&!wl){
  navigator.wakeLock.request("screen").then(function(l){wl=l;
    l.addEventListener("release",function(){wl=null})}).catch(function(){})}}
document.addEventListener("visibilitychange",function(){
  if(document.visibilityState==="visible")wake()});
document.addEventListener("touchstart",wake,{once:true});
document.addEventListener("click",wake,{once:true});
render();
</script></body></html>
"""


# --------------------------------------------------------------------- main --

def main():
    ap = argparse.ArgumentParser(
        description="Web control bridge for the Icom IC-7300MK2 (LAN).")
    ap.add_argument("--radio", required=True, help="radio IP address or hostname")
    ap.add_argument("--username", required=True, help="Network User1 ID set on the radio")
    ap.add_argument("--password", required=True, help="Network User1 password")
    ap.add_argument("--control-port", type=int, default=50001,
                    help="radio UDP control port (default 50001)")
    ap.add_argument("--http-port", type=int, default=7300,
                    help="web UI port (default 7300)")
    ap.add_argument("--civ-addr", type=lambda v: int(v, 0), default=None,
                    help="override CI-V address (default: reported by radio)")
    args = ap.parse_args()

    try:
        radio_ip = socket.gethostbyname(args.radio)
    except OSError:
        sys.exit("Cannot resolve radio address: " + args.radio)

    link = RadioLink(radio_ip, args.control_port, args.username, args.password,
                     args.civ_addr)
    Handler.link = link
    httpd = ThreadingHTTPServer(("", args.http_port), Handler)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    log("http", "web UI on http://<this-computer>:%d" % args.http_port)

    try:
        link.supervise()
    except KeyboardInterrupt:
        log("main", "shutting down")
    finally:
        link.shutdown()
        link._teardown()
        httpd.shutdown()


if __name__ == "__main__":
    main()
