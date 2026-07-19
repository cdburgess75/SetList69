<div align="center">

<img src="icons/icon-512.png" alt="SetList69 icon" width="110" height="110">

# SetList69

**An offline-first chord & lyric performance app for gigging musicians — the entire application is one hand-written HTML file you own, host, and control.**

[![CI](https://github.com/cdburgess75/SetList69/actions/workflows/check.yml/badge.svg)](https://github.com/cdburgess75/SetList69/actions/workflows/check.yml)
[![Version](https://img.shields.io/badge/version-v2026.07.12.006-informational?style=flat-square)](#versioning)
[![PWA](https://img.shields.io/badge/PWA-installable-8250df?style=flat-square)](#installation)
[![Dependencies](https://img.shields.io/badge/runtime_dependencies-0-f5a623?style=flat-square)](#architecture)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

**[▶ Live app](https://cdburgess75.github.io/SetList69/)** · [User Guide](docs/USER-GUIDE.md) · [Features](#key-features) · [Installation](#installation) · [Usage](#quickstart) · [Architecture](#architecture) · [Contributing](#contributing)

</div>

---

## Overview

SetList69 stores songs (lyrics with chords), organizes them into setlists, and renders them in a large, high-contrast reading view designed to be operated while holding an instrument. It **imports your existing library from OnSong and other chord apps** and keeps everything on your device — no subscription, no account, no cloud.

**The problems it solves:**

| Problem | How SetList69 answers it |
|---|---|
| Chord apps stop working when the venue has no signal | Full offline operation via service worker; every asset is precached |
| Screens sleep mid-verse | Wake Lock held for the entire set, not just one song |
| Chord charts wrap badly on phones | Custom rendering engine: chords lock to their syllable, words never split across lines, no horizontal scrolling — ever |
| Moving your songs between apps is a hassle | Imports from OnSong and other apps — ChordPro, OnSong, OpenSong XML, plain text, and ZIP bundles; exports plain JSON |
| Cloud accounts, subscriptions, telemetry | None. All data stays in the browser's local storage; sync between devices is a file you control |

**Why it stands out:** the whole app is a single `setlist69.html` — no framework, no build step, no `node_modules`. You can read every line, fork it, and host it on any static server. Reliability, readability while playing, offline operation, and ownership are the four design priorities, in that order.

---

## Key features

| Area | Capability |
|---|---|
| **Rendering** | Chords positioned above the exact syllable; color-coded by root pitch; inline ChordPro (`[G]word`) and chords-above-lyrics formats both parse; tap a chord for a guitar fingering diagram |
| **Transposition** | Per-song transpose (remembered), set-wide transpose, sharp/flat spelling toggle, capo support with fingering-shape display, Nashville number notation (key-invariant) |
| **Performance** | Auto-scroll with live speed control and progress bar, swipe between songs, fit-to-screen font sizing, wake lock across the whole set, one-tap fullscreen gig mode |
| **Stage safety** | Stage mode hides all editing chrome; leaving a song mid-performance requires a deliberate double tap |
| **Set management** | Drag-to-reorder, per-set notes, duplicate sets, ✓ Played tracking that survives reloads and resets in one tap |
| **Import** | ChordPro (`.cho/.chordpro/.pro`), OnSong (`.onsong/.txt` incl. `Key:`/`Capo:`), OpenSong XML, plain text, ZIP bundles, paste-from-chord-sites with automatic cleanup |
| **Export / share** | Full library backup to JSON; single-setlist share files that *merge* into a bandmate's library without duplicates |
| **PWA** | Installable on iOS/Android, offline-first caching, in-app update notification, install nudge |
| **Theming** | Dark (default) and light themes, both ≥ WCAG AA contrast |

<div align="center">
<table>
<tr>
<td width="25%"><img src="docs/screenshots/home.png" alt="Home screen" width="100%"></td>
<td width="25%"><img src="docs/screenshots/song.png" alt="Performance view" width="100%"></td>
<td width="25%"><img src="docs/screenshots/played.png" alt="Played tracking" width="100%"></td>
<td width="25%"><img src="docs/screenshots/song-light.png" alt="Light theme" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>Setlists & library</sub></td>
<td align="center"><sub>Performance view</sub></td>
<td align="center"><sub>Played tracking</sub></td>
<td align="center"><sub>Light theme</sub></td>
</tr>
</table>
</div>

---

## Architecture

```
SetList69/
├── setlist69.html          # The entire application — HTML, CSS, and JS in one file
├── sw.js                   # Service worker: cache-first, precaches all assets
├── manifest.json           # PWA manifest (id, icons, screenshots, standalone)
├── index.html              # Redirect stub → setlist69.html
├── fonts/                  # Self-hosted WOFF2 (Fraunces, Hanken Grotesk, JetBrains Mono)
├── icons/                  # App icons incl. Android-maskable variant
├── docs/
│   ├── DEVICE-TESTING.md   # Manual test pass for touch/visual behavior
│   ├── shots.js            # Playwright helper — regenerates README screenshots
│   └── screenshots/
└── .github/workflows/
    └── check.yml           # CI: syntax, version-match, duplicate-id, manifest+precache checks
```

Inside `setlist69.html`, the code reads top to bottom: persistence (IndexedDB + localStorage fallback) → seed data → music core (transposition, chord detection) → parsing/rendering engine → screen router → renderers → import/export → event wiring. A single in-memory `state` object holds everything and is persisted whole:

```js
state = {
  songs:    [{ id, title, sub, banter, key, capo, defaultTranspose, body }],
  setlists: [{ id, name, notes, setTranspose, songIds: [...] }],
  theme:    "dark"
}
```

Songs are a shared master store; setlists reference them by id, so editing a song updates every set that uses it. Deep architecture notes (rendering pipeline, capo math, merge-import rules) live in [`CLAUDE.md`](CLAUDE.md).

---

## Installation

### Prerequisites

- **To use:** any modern browser. Nothing else — no account, no API keys, no install step beyond the browser.
- **To develop:** `git`, and Node.js ≥ 18 (only for the syntax checks and screenshot tooling; the app itself has no build).

### As a phone app (recommended)

1. Open **[cdburgess75.github.io/SetList69](https://cdburgess75.github.io/SetList69/)** — Safari on iPhone/iPad, Chrome on Android
2. **iPhone:** Share → *Add to Home Screen* · **Android:** ⋮ → *Add to Home Screen*
3. Launch it once with signal; it works fully offline afterward. When a new version ships, the app slides down an *"Update ready"* banner naming the new version (and keeps a ⟳ button in the header to apply it) — no cache clearing needed.

### Self-hosted

```bash
git clone https://github.com/cdburgess75/SetList69.git
cd SetList69
npx serve .          # any static file server works; or just open setlist69.html
```

Deploying your own copy is a push to any static host (GitHub Pages, Netlify, a folder on your own server).

---

## Quickstart

**Add a song** — tap **+** next to *Songs* and paste either format:

```
[G]Amazing [G7]grace how [C]sweet the [G]sound        ← inline ChordPro

G        G7        C          G
Amazing  grace how sweet the  sound                    ← chords above lyrics
```

**Build a set** — tap **+** next to *Setlists*, add songs, drag the `≡` handle to order them.

**Play the gig** — open the set, tap **▶ Stage**, tap the first song. Swipe left for the next song; each one is crossed off behind you. The **⚙** button holds transpose, sharp/flat, font size, and fit-to-screen.

**Import an existing library** — **≡** menu → *Import songs*. Point it at `.onsong`/`.chordpro`/`.txt`/`.xml` files or a ZIP of them. From OnSong: export songs individually, zip them, import the zip.

### Running the checks (the "test suite")

There is no unit-test framework by design; correctness is enforced by CI checks plus targeted Node harnesses for the music core:

```bash
# What CI runs on every push:
node -e "const s=require('fs').readFileSync('setlist69.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];require('fs').writeFileSync('/tmp/app.js',s)" \
  && node --check /tmp/app.js && node --check sw.js

# Regenerate the README screenshots after UI changes:
node docs/shots.js

# Manual touch/visual verification (real device):
# → follow docs/DEVICE-TESTING.md
```

---

## Versioning

Revisions use **`vYYYY.MM.DD.NNN`**. Every change bumps the version in three synced places — the changelog comment at the top of `setlist69.html`, the on-screen brand tag, and the `CACHE` constant in `sw.js`. CI fails the build if they drift. The full changelog lives at the top of [`setlist69.html`](setlist69.html).

---

## Contributing

This is a personal tool developed in the open, and issues/PRs are welcome:

1. Read [`CLAUDE.md`](CLAUDE.md) first — it documents the architecture, the rendering engine's invariants, and the change checklist.
2. Keep the constraints: **vanilla JS, one file, zero runtime dependencies, no build step.**
3. Bump the version in all three places (CI will catch you if you don't).
4. `node --check` the extracted script; add a small Node harness if you touch the music core.
5. Flag anything needing real-device testing (touch, share sheet, install flow) in your PR description.

## License

[MIT](LICENSE) — use it, fork it, self-host it, gig with it. Attribution is the only condition.

---

<div align="center"><sub>Built for performing musicians. No cloud, no subscription, no ads — just your songs.</sub></div>
