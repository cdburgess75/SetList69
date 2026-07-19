#!/usr/bin/env python3
# radiosim -- a fake IC-7300MK2 LAN endpoint for testing remote7300 without
# a radio on the bench. Implements the radio side of the Icom network
# protocol: control-stream handshake, login/token, capabilities/conninfo,
# stream grant, and a CI-V responder that keeps freq/mode state.
#
# Run standalone:  python3 radiosim.py [port]   (default 50001)
# then point remote7300.py at 127.0.0.1 with username "user" password "pass".

import socket
import select
import struct
import sys
import threading
import time

from remote7300 import (header, passcode, freq_to_bcd, bcd_to_freq, now_ms)

RADIO_NAME = b"IC-7300MK2"
CIV_ADDR = 0xA4


class RadioSim(threading.Thread):
    def __init__(self, port=0, username="user", password="pass"):
        super().__init__(daemon=True)
        self.username = username
        self.password = password
        self.freq = 7_074_000
        self.mode = 0x01        # USB
        self.filter = 0x02
        self.my_id = 0x76300001
        self.token = 0x5A5A1234
        self.stop_flag = threading.Event()
        self.log_lines = []

        self.ctl = self._bind(port)
        self.civ = self._bind(0)
        self.aud = self._bind(0)
        self.control_port = self.ctl.getsockname()[1]
        self.peers = {}          # sock -> (addr, state dict)
        self.civ_seq = 0
        self.seen_login = False
        self.civ_client = None   # addr of the CI-V stream client

    @staticmethod
    def _bind(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("127.0.0.1", port))
        return s

    def log(self, *a):
        line = " ".join(str(x) for x in a)
        self.log_lines.append(line)

    # ------------------------------------------------------------------ run

    def run(self):
        socks = [self.ctl, self.civ, self.aud]
        while not self.stop_flag.is_set():
            r, _, _ = select.select(socks, [], [], 0.05)
            for s in r:
                try:
                    data, addr = s.recvfrom(4096)
                except OSError:
                    return
                self.handle(s, data, addr)

    def close(self):
        self.stop_flag.set()
        for s in (self.ctl, self.civ, self.aud):
            try:
                s.close()
            except OSError:
                pass

    # ------------------------------------------------------------- helpers

    def _send(self, sock, addr, data):
        try:
            sock.sendto(data, addr)
        except OSError:
            pass

    def _hdr(self, size, ptype, seq, client_id):
        return header(size, ptype, seq, self.my_id, client_id)

    # ------------------------------------------------------------- handler

    def handle(self, sock, r, addr):
        if len(r) < 0x10:
            return
        length, ptype, seq, sentid, rcvdid = struct.unpack_from("<IHHII", r)

        if len(r) == 0x10:
            if ptype == 0x03:       # are you there
                self._send(sock, addr, self._hdr(0x10, 0x04, 0, sentid))
            elif ptype == 0x06:     # are you ready
                self._send(sock, addr, self._hdr(0x10, 0x06, 1, sentid))
                if sock is self.civ:
                    self.civ_client = addr
            return

        if len(r) == 0x15 and ptype == 0x07:
            if r[0x10] == 0x00:     # ping request -> reply
                p = self._hdr(0x15, 0x07, seq, sentid) + b"\x01" + r[0x11:0x15]
                self._send(sock, addr, p)
            return

        if sock is self.ctl:
            self.handle_control(r, addr, seq, sentid)
        elif sock is self.civ:
            self.handle_civ(r, addr, sentid)

    # -------------------------------------------------------- control side

    def handle_control(self, r, addr, seq, client_id):
        size = len(r)
        if size == 0x80:            # login
            user = bytes(r[0x40:0x50]).rstrip(b"\x00")
            pw = bytes(r[0x50:0x60]).rstrip(b"\x00")
            tokrequest = struct.unpack_from("<H", r, 0x1A)[0]
            ok = (user == passcode(self.username) and pw == passcode(self.password))
            self.log("login", "ok" if ok else "BAD")
            p = bytearray(self._hdr(0x60, 0x00, 0, client_id) + bytes(0x50))
            struct.pack_into(">I", p, 0x10, 0x50)
            p[0x14] = 0x02
            p[0x15] = 0x00
            struct.pack_into("<H", p, 0x1A, tokrequest)
            struct.pack_into("<I", p, 0x1C, self.token)
            struct.pack_into("<I", p, 0x30, 0 if ok else 0xFEFFFFFF)
            p[0x40:0x46] = b"WFVIEW"
            self._send(self.ctl, addr, bytes(p))
            self.seen_login = ok
        elif size == 0x40:          # token packet
            reqtype = r[0x15]
            tokrequest = struct.unpack_from("<H", r, 0x1A)[0]
            p = bytearray(self._hdr(0x40, 0x00, 0, client_id) + bytes(0x30))
            struct.pack_into(">I", p, 0x10, 0x30)
            p[0x14] = 0x02
            p[0x15] = 0x05
            struct.pack_into("<H", p, 0x1A, tokrequest)
            struct.pack_into("<I", p, 0x1C, self.token)
            struct.pack_into("<I", p, 0x30, 0x0000)
            self._send(self.ctl, addr, bytes(p))
            self.log("token", "%02x" % reqtype)
            if reqtype == 0x02 and self.seen_login:
                self.send_capabilities(addr, client_id)
                self.send_conninfo(addr, client_id)
        elif size == 0x90:          # stream request
            civ_port = struct.unpack_from(">I", r, 0x7C)[0]
            audio_port = struct.unpack_from(">I", r, 0x80)[0]
            self.log("streamreq", civ_port, audio_port)
            # radio replies with a status packet carrying its stream ports
            p = bytearray(self._hdr(0x50, 0x00, 0, client_id) + bytes(0x40))
            struct.pack_into(">I", p, 0x10, 0x40)
            p[0x14] = 0x02
            p[0x15] = 0x03
            struct.pack_into("<I", p, 0x1C, self.token)
            struct.pack_into("<I", p, 0x30, 0)          # no error
            p[0x40] = 0x00                              # not disconnected
            struct.pack_into(">H", p, 0x42, self.civ.getsockname()[1])
            struct.pack_into(">H", p, 0x46, self.aud.getsockname()[1])
            self._send(self.ctl, addr, bytes(p))

    def send_capabilities(self, addr, client_id):
        p = bytearray(self._hdr(0x42 + 0x66, 0x00, 0, client_id) + bytes(0x32 + 0x66))
        struct.pack_into(">I", p, 0x10, len(p) - 0x10)
        p[0x14] = 0x02
        struct.pack_into("<H", p, 0x40, 1)              # one radio
        cap = 0x42
        struct.pack_into("<H", p, cap + 0x07, 0x8010)   # commoncap -> MAC form
        p[cap + 0x0A:cap + 0x10] = bytes.fromhex("aabbccddeeff")
        p[cap + 0x10:cap + 0x10 + len(RADIO_NAME)] = RADIO_NAME
        p[cap + 0x52] = CIV_ADDR
        struct.pack_into("<H", p, cap + 0x53, 0x8007)   # rx sample rates
        struct.pack_into("<H", p, cap + 0x55, 0x8007)   # tx sample rates
        struct.pack_into(">I", p, cap + 0x5A, 115200)
        self._send(self.ctl, addr, bytes(p))

    def send_conninfo(self, addr, client_id):
        p = bytearray(self._hdr(0x90, 0x00, 0, client_id) + bytes(0x80))
        struct.pack_into(">I", p, 0x10, 0x80)
        p[0x14] = 0x02
        struct.pack_into("<H", p, 0x27, 0x8010)
        p[0x2A:0x30] = bytes.fromhex("aabbccddeeff")
        p[0x40:0x40 + len(RADIO_NAME)] = RADIO_NAME
        struct.pack_into("<I", p, 0x60, 0)              # not busy
        self._send(self.ctl, addr, bytes(p))

    # ------------------------------------------------------------ CIV side

    def handle_civ(self, r, addr, client_id):
        self.civ_client = addr
        if len(r) == 0x16:          # open/close request -> ack with idle
            return
        if len(r) > 0x15:
            datalen = struct.unpack_from("<H", r, 0x11)[0]
            if datalen + 0x15 == len(r):
                self.process_civ_frames(bytes(r[0x15:]), addr, client_id)

    def process_civ_frames(self, payload, addr, client_id):
        for chunk in payload.split(b"\xFD"):
            if len(chunk) < 5 or not chunk.startswith(b"\xFE\xFE"):
                continue
            to, frm = chunk[2], chunk[3]
            body = chunk[4:]
            if to != CIV_ADDR or not body:
                continue
            cmd = body[0]
            if cmd == 0x03:
                self.send_civ(bytes([0x03]) + freq_to_bcd(self.freq), frm)
            elif cmd == 0x04:
                self.send_civ(bytes([0x04, self.mode, self.filter]), frm)
            elif cmd == 0x05:
                self.freq = bcd_to_freq(body[1:6])
                self.log("setfreq", self.freq)
                self.send_ok(frm)
            elif cmd == 0x06:
                self.mode = body[1]
                if len(body) > 2:
                    self.filter = body[2]
                self.log("setmode", self.mode)
                self.send_ok(frm)
            else:
                self.send_civ(bytes([0xFA]), frm)

    def _civ_datagram(self, frame, client_id):
        p = header(0x15 + len(frame), 0x00, self.civ_seq, self.my_id, client_id)
        p += b"\xC1" + struct.pack("<H", len(frame)) + struct.pack(">H", self.civ_seq)
        self.civ_seq = (self.civ_seq + 1) & 0xFFFF
        if self.civ_seq == 0:
            self.civ_seq = 1
        return p + frame

    def send_civ(self, body, dest=0xE0, client_id=0):
        if self.civ_client is None:
            return
        frame = bytes([0xFE, 0xFE, dest, CIV_ADDR]) + body + b"\xFD"
        self._send(self.civ, self.civ_client, self._civ_datagram(frame, client_id))

    def send_ok(self, dest):
        self.send_civ(bytes([0xFB]), dest)

    def push_freq(self, hz):
        """Simulate the operator turning the dial (CI-V transceive)."""
        self.freq = hz
        self.send_civ(bytes([0x00]) + freq_to_bcd(hz), 0x00)

    def push_mode(self, mode, filt=0x02):
        self.mode = mode
        self.filter = filt
        self.send_civ(bytes([0x01, mode, filt]), 0x00)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50001
    sim = RadioSim(port)
    sim.start()
    print("radiosim on 127.0.0.1:%d (user/pass), civ %d, audio %d"
          % (sim.control_port, sim.civ.getsockname()[1], sim.aud.getsockname()[1]))
    try:
        while True:
            time.sleep(5)
            sim.push_freq(sim.freq + 100)   # slow drift so you can see updates
    except KeyboardInterrupt:
        sim.close()
