# remote7300 — iPad control for the Icom IC-7300MK2

Control your IC-7300MK2 from an iPad (or any browser) over your home network:
see the frequency and mode live, change them with big touch-friendly buttons.

It follows the SetList69 philosophy: **no dependencies, no cloud, you own it.**
One Python file, standard library only, talking directly to the radio's LAN
port using Icom's network protocol (the same one RS-BA1 uses).

```
iPad (Safari)  ──WiFi──▶  bridge computer (remote7300.py)  ──WiFi/LAN──▶  IC-7300MK2
```

The iPad can't speak the radio's UDP protocol from a browser, so a small
**bridge** runs on any always-on computer on the same network — a Mac, a
Windows PC, or a $40 Raspberry Pi. The bridge serves the touch UI as a plain
web page.

## 1. Set up the radio (one time)

On the IC-7300MK2:

1. `MENU` » `SET` » `WLAN Set` (or Network) — confirm the radio is on your
   network and note its **IP address**.
2. `MENU` » `SET` » `Network` » **Network Control** → `ON`
3. `MENU` » `SET` » `Network` » **Network User1** → set an ID and password
   (these are what the bridge logs in with).
4. Leave **Control Port (UDP)** at its default `50001`.

Tip: give the radio a fixed IP (DHCP reservation in your router) so the
address never changes.

## 2. Run the bridge

Any machine with Python 3.8+ (preinstalled on macOS and most Linux;
[python.org](https://www.python.org/downloads/) for Windows):

```sh
python3 remote7300.py --radio 192.168.1.50 --username ipad --password secret
```

Replace the IP and credentials with what you set on the radio. You should see
`radio is here` … `login OK` … `opening CI-V stream` within a couple of
seconds.

Options:

| flag | default | meaning |
|---|---|---|
| `--http-port` | `7300` | port the web UI is served on |
| `--control-port` | `50001` | radio's UDP control port |
| `--civ-addr` | auto | CI-V address override (normally auto-detected) |

## 3. Open it on the iPad

Browse to `http://<bridge-computer-ip>:7300`, then **Share » Add to Home
Screen** for a full-screen app feel. You get:

- **Live frequency display** — updates as you turn the dial on the radio.
  Tap it to type a frequency directly (MHz, e.g. `7.2`; numbers over 75 are
  treated as kHz).
- **Tune** — ▲/▼ buttons with press-and-hold repeat, step selectable from
  10 Hz to 100 kHz.
- **Mode** — LSB / USB / CW / CW-R / AM / FM / RTTY / RTTY-R.
- **Band** — 160 m through 6 m; remembers your last frequency and mode per
  band (stored in the browser).

Multiple devices can view at once; they all stay in sync.

## Security note

The web page has no password — anyone on your LAN can tune the radio while
the bridge is running. Fine on a home network; don't port-forward it to the
internet. The radio credentials live only on the bridge command line.

## Testing without the radio

`radiosim.py` is a fake radio that implements the same protocol:

```sh
python3 test_remote7300.py     # full automated end-to-end test
python3 radiosim.py            # or run a fake radio to point the bridge at
```

## Notes & credits

- Only the CI-V control stream is used; the audio stream is accepted and
  discarded (this is a control head, not a remote receiver — you still listen
  on the radio).
- If another RS-BA1/wfview client holds the radio, the UI will say so.
- The Icom network protocol implementation is based on the reverse
  engineering openly documented by the
  [wfview](https://gitlab.com/eliggett/wfview) (GPL) and kappanhang projects
  — with thanks.
- CI-V commands follow Icom's published IC-7300MK2 CI-V Reference Guide.
