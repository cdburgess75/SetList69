<div align="center">

<img src="icons/icon-512.png" alt="SetList69 icon" width="96" height="96">

# SetList69

**Offline-first chord & lyric setlists for the stage — your whole songbook in one installable HTML file that runs with zero signal.**

[![Live app](https://img.shields.io/badge/live_app-cdburgess75.github.io-cf3c28?style=flat-square)](https://cdburgess75.github.io/SetList69/)
[![CI](https://github.com/cdburgess75/SetList69/actions/workflows/check.yml/badge.svg)](https://github.com/cdburgess75/SetList69/actions/workflows/check.yml)
[![Version](https://img.shields.io/badge/version-2026.07.19.016-informational?style=flat-square)](#versioning)
[![PWA](https://img.shields.io/badge/PWA-installable-8250df?style=flat-square)](#installation)
[![Offline](https://img.shields.io/badge/offline-first-2ea043?style=flat-square)](#overview)
[![Runtime deps](https://img.shields.io/badge/runtime_dependencies-0-f5a623?style=flat-square)](#tech-stack)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

**[▶ Open the live app](https://cdburgess75.github.io/SetList69/)** · [User Guide](docs/USER-GUIDE.md) · [Features](#key-features) · [Tech stack](#tech-stack) · [Install](#installation) · [Usage](#usage) · [Architecture](#architecture)

<br>

<table>
<tr>
<td width="50%"><img src="docs/screenshots/song.png" alt="Performance view with chords locked above each syllable" width="100%"></td>
<td width="50%"><img src="docs/screenshots/home.png" alt="Home screen showing setlists and the song library" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>Performance view — chords locked above the syllable</sub></td>
<td align="center"><sub>Home — setlists &amp; song library</sub></td>
</tr>
</table>

</div>

---

## Overview

SetList69 stores songs (lyrics with chords), organizes them into setlists, and renders them in a large, high-contrast reading view designed to be operated while holding an instrument. It **imports your existing library from OnSong and other chord apps** and keeps everything on your device — no subscription, no account, no cloud.

**The problems it solves:**

| Problem | How SetList69 answers it |
|---|---|
| Chord apps stop working when the venue has no signal | Full offline operation via a service worker; every asset is precached |
| Screens sleep mid-verse | Wake Lock held for the entire set, not just one song |
| Chord charts wrap badly on phones | A custom rendering engine: chords lock to their syllable, words never split across lines, and the page never scrolls sideways |
| Moving your songs between apps is a hassle | Imports ChordPro, OnSong, OpenSong XML, plain text, and ZIP bundles; exports plain JSON |
| Cloud accounts, subscriptions, telemetry | None. Data stays in the browser's local storage; moving it between devices is a file you control |

**Why it stands out:** the whole app is a single `setlist69.html` — no framework, no build step, no `node_modules`. You can read every line, fork it, and host it on any static server. Reliability, readability while playing, offline operation, and ownership are the four design priorities, in that order.

---

## Screenshots

<div align="center">
<table>
<tr>
<td width="50%"><img src="docs/screenshots/chord-diagram.png" alt="Guitar fingering diagram shown when a chord is tapped" width="100%"></td>
<td width="50%"><img src="docs/screenshots/editor.png" alt="Song editor showing inline ChordPro, key, and capo fields" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>Tap any chord for a guitar fingering</sub></td>
<td align="center"><sub>Editor — inline ChordPro, capo, and import</sub></td>
</tr>
<tr>
<td width="50%"><img src="docs/screenshots/played.png" alt="Set view with played songs crossed off" width="100%"></td>
<td width="50%"><img src="docs/screenshots/song-light.png" alt="Performance view in the light theme" width="100%"></td>
</tr>
<tr>
<td align="center"><sub>Set view with ✓ Played tracking</sub></td>
<td align="center"><sub>Light theme</sub></td>
</tr>
</table>
</div>

---

## Key features

| Area | Capability |
|---|---|
| **Rendering** | Chords positioned above the exact syllable, color-coded by root pitch; inline ChordPro (`[G]word`) and chords-above-lyrics formats both parse; tap a chord for a guitar fingering diagram |
| **Transposition** | Per-song transpose (remembered), set-wide transpose, sharp/flat spelling toggle, capo support with fingering-shape display, Nashville number notation (key-invariant) |
| **Performance** | Auto-scroll with live speed control and a progress bar, swipe between songs, fit-to-screen font sizing, wake lock across the whole set, one-tap fullscreen gig mode |
| **Stage safety** | Stage mode hides all editing chrome; leaving a song mid-performance takes a deliberate double tap |
| **Set management** | Drag-to-reorder, per-set notes, duplicate sets, and ✓ Played tracking that survives reloads and resets in one tap |
| **Import** | ChordPro (`.cho/.chordpro/.pro`), OnSong (`.onsong/.txt`, incl. `Key:`/`Capo:`), OpenSong XML, plain text, ZIP bundles, and paste-from-chord-sites with automatic cleanup |
| **Export / share** | Full library backup to JSON; single-setlist share files that *merge* into a bandmate's library without creating duplicates |
| **PWA** | Installable on iOS/Android, offline-first caching, in-app update notifications, and an install nudge |
| **Theming** | Dark (default) and light themes, both at or above WCAG AA contrast |

---

## Tech stack

No framework, no bundler, no `node_modules` in the shipped app — the runtime dependency count is zero. Everything below is either a browser API or a self-hosted asset.

| Layer | What it uses |
|---|---|
| **App** | Hand-written HTML5, CSS (custom-property theming, flexbox/grid), and vanilla JavaScript (ES2017+) — all in one `setlist69.html` |
| **Storage** | IndexedDB for the library with a `localStorage` fallback; state is structurally validated on load and persisted whole |
| **Offline / install** | Web App Manifest + a cache-first Service Worker that precaches every asset; the Wake Lock API keeps the screen awake through a set |
| **Sharing / files** | File System Access API, Web Share API, and an anchor-download fallback — selected per platform at runtime |
| **Import** | ChordPro, OnSong, and OpenSong XML parsers (the last via `DOMParser`); ZIP bundles unpacked with the native `DecompressionStream` |
| **Fonts** | Self-hosted WOFF2 (JetBrains Mono, Hanken Grotesk) — no external CDN, so text renders identically offline |
| **Dev tooling** | Node.js `--check` for syntax, Playwright for screenshots, GitHub Actions for CI, GitHub Pages for hosting — none of it ships to the browser |

---

## Installation

### Prerequisites

- **To use:** any modern browser. Nothing else — no account, no API keys, no install step beyond the browser.
- **To develop:** `git`, and Node.js ≥ 18 (only for the syntax checks and screenshot tooling; the app itself has no build).

### As a phone app (recommended)

1. Open **[cdburgess75.github.io/SetList69](https://cdburgess75.github.io/SetList69/)** — Safari on iPhone/iPad, Chrome on Android.
2. **iPhone:** Share → *Add to Home Screen* · **Android:** ⋮ → *Add to Home Screen*.
3. Launch it once with signal; it works fully offline afterward. When a new version ships, the app slides down an *"Update ready"* banner naming it (and keeps a ⟳ button in the header to apply it) — no cache clearing needed.

### Self-hosted

```bash
git clone https://github.com/cdburgess75/SetList69.git
cd SetList69
npx serve .          # any static file server works; or just open setlist69.html
```

Deploying your own copy is a push to any static host — GitHub Pages, Netlify, or a folder on your own server. There is no build step.

---

## Usage

**Add a song** — tap **+** next to *Songs* and paste either format:

```
[G]Amazing [G7]grace how [C]sweet the [G]sound        ← inline ChordPro

G        G7        C          G
Amazing  grace how sweet the  sound                    ← chords above lyrics
```

**Build a set** — tap **+** next to *Setlists*, add songs, and drag the `≡` handle to order them.

**Play the gig** — open the set, tap **▶ Stage**, then tap the first song. Swipe left for the next; each one is crossed off behind you. The **⚙** button holds transpose, sharp/flat, font size, and fit-to-screen.

**Import an existing library** — **≡** menu → *Import songs*. Point it at `.onsong` / `.chordpro` / `.txt` / `.xml` files or a ZIP of them. From OnSong: export songs individually, zip them, and import the zip.

A fuller walkthrough lives in the **[User Guide](docs/USER-GUIDE.md)**.

---

## Architecture

```
SetList69/
├── setlist69.html          # The entire application — HTML, CSS, and JS in one file
├── sw.js                   # Service worker: cache-first, precaches all assets
├── manifest.json           # PWA manifest (id, icons, screenshots, standalone)
├── index.html              # Redirect stub → setlist69.html
├── .nojekyll               # Tell GitHub Pages to serve the files as-is (no Jekyll)
├── fonts/                  # Self-hosted WOFF2 (Hanken Grotesk, JetBrains Mono)
├── icons/                  # App icons incl. an Android-maskable variant
├── docs/
│   ├── USER-GUIDE.md       # End-user walkthrough
│   ├── DEVICE-TESTING.md   # Manual test pass for touch/visual behavior
│   ├── shots.js            # Playwright helper — regenerates the README screenshots
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

## Development

There is no unit-test framework by design; correctness is enforced by CI checks plus targeted Node harnesses for the music core.

```bash
# What CI runs on every push — syntax-check the extracted script and the service worker:
node -e "const s=require('fs').readFileSync('setlist69.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];require('fs').writeFileSync('/tmp/app.js',s)" \
  && node --check /tmp/app.js && node --check sw.js

# Regenerate the README screenshots after a UI change (needs Playwright + a Chromium):
node docs/shots.js

# Manual touch/visual verification on a real device:
# → follow docs/DEVICE-TESTING.md
```

CI (`.github/workflows/check.yml`) also fails the build on a version mismatch (see below), duplicate element ids, or a manifest that references a missing precache file.

---

## Versioning

Revisions use **`vYYYY.MM.DD.NNN`**. Every app change bumps the version in three synced places — the changelog comment at the top of `setlist69.html`, the on-screen brand tag, and the `CACHE` constant in `sw.js`. CI fails the build if they drift. The full changelog lives at the top of [`setlist69.html`](setlist69.html).

---

## Contributing

This is a personal tool developed in the open; issues and PRs are welcome:

1. Read [`CLAUDE.md`](CLAUDE.md) first — it documents the architecture, the rendering engine's invariants, and the change checklist.
2. Keep the constraints: **vanilla JS, one file, zero runtime dependencies, no build step.**
3. Bump the version in all three places (CI will catch you if you don't).
4. `node --check` the extracted script; add a small Node harness if you touch the music core.
5. Flag anything that needs real-device testing (touch, share sheet, install flow) in your PR description.

---

## License

[MIT](LICENSE) — use it, fork it, self-host it, gig with it. Attribution is the only condition.

---

<div align="center"><sub>Built for performing musicians. No cloud, no subscription, no ads — just your songs.</sub></div>
