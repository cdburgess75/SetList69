#!/usr/bin/env python3
# End-to-end test: run the bridge against the fake radio (radiosim) and drive
# it through the HTTP API exactly the way the iPad page does.
#
#     python3 test_remote7300.py

import json
import threading
import time
import urllib.request

import remote7300
from remote7300 import RadioLink, Handler, freq_to_bcd, bcd_to_freq, passcode
from radiosim import RadioSim
from http.server import ThreadingHTTPServer


def wait_for(fn, timeout=10, what="condition"):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if fn():
            return
        time.sleep(0.05)
    raise AssertionError("timed out waiting for " + what)


def test_units():
    assert freq_to_bcd(14_074_000) == bytes.fromhex("0040071400")
    assert freq_to_bcd(7_200_123) == bytes.fromhex("2301200700")
    for f in (30_000, 1_836_600, 7_074_000, 14_250_000, 52_525_000):
        assert bcd_to_freq(freq_to_bcd(f)) == f, f
    assert len(passcode("user")) == 4
    assert passcode("user") != b"user"          # actually scrambled
    assert passcode("user") == passcode("user")  # deterministic
    print("unit tests: OK")


def api(port, path, payload=None):
    url = "http://127.0.0.1:%d%s" % (port, path)
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def test_end_to_end():
    sim = RadioSim(port=0, username="user", password="pass")
    sim.start()

    link = RadioLink("127.0.0.1", sim.control_port, "user", "pass")
    threading.Thread(target=link.supervise, daemon=True).start()

    Handler.link = link
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    httpd.daemon_threads = True
    http_port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    # 1. bridge connects, logs in, opens CI-V, reads initial freq + mode
    wait_for(lambda: api(http_port, "/api/state")["connected"],
             what="bridge to connect")
    state = api(http_port, "/api/state")
    assert state["radio"] == "IC-7300MK2", state
    assert state["freq"] == 7_074_000, state
    assert state["mode"] == "USB", state
    print("connect + initial poll: OK")

    # 2. set frequency from the web API -> radio state changes, gets FB ack
    out = api(http_port, "/api/set", {"freq": 14_074_000})
    assert out["ok"], out
    wait_for(lambda: sim.freq == 14_074_000, what="sim freq change")
    print("set frequency: OK")

    # 3. set mode
    out = api(http_port, "/api/set", {"mode": "CW"})
    assert out["ok"], out
    wait_for(lambda: sim.mode == 0x03, what="sim mode change")
    print("set mode: OK")

    # 4. operator turns the dial (CI-V transceive) -> state updates
    sim.push_freq(21_200_500)
    wait_for(lambda: api(http_port, "/api/state")["freq"] == 21_200_500,
             what="transceive freq update")
    sim.push_mode(0x00)  # LSB
    wait_for(lambda: api(http_port, "/api/state")["mode"] == "LSB",
             what="transceive mode update")
    print("radio-side updates: OK")

    # 5. invalid mode is rejected
    out = api(http_port, "/api/set", {"mode": "NOPE"})
    assert not out["ok"], out
    print("bad input rejected: OK")

    link.shutdown()
    httpd.shutdown()
    sim.close()


def test_bad_password():
    sim = RadioSim(port=0, username="user", password="pass")
    sim.start()
    link = RadioLink("127.0.0.1", sim.control_port, "user", "WRONG")
    threading.Thread(target=link.supervise, daemon=True).start()
    wait_for(lambda: "username/password" in link.snapshot()[0]["status"],
             what="login rejection")
    print("bad password surfaced: OK")
    link.shutdown()
    sim.close()


if __name__ == "__main__":
    test_units()
    test_end_to_end()
    test_bad_password()
    print("\nALL TESTS PASSED")
