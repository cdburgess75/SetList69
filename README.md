<div align="center">

<img src="icons/icon-512.png" alt="SetList69" width="120" height="120">

# SetList69

### Your songs. Your setlists. On stage, offline, in your hands.

A fast, offline-first chord &amp; lyric app for performing musicians — the spiritual cousin of OnSong, rebuilt as a single file you own and control.

[![Live App](https://img.shields.io/badge/▶_Open_App-e2563a?style=for-the-badge)](https://cdburgess75.github.io/SetList69/)

[![PWA](https://img.shields.io/badge/PWA-installable-8250df?style=flat-square)](#install)
[![Offline](https://img.shields.io/badge/works-offline-2E8B7A?style=flat-square)](#why-setlist69)
[![Version](https://img.shields.io/badge/version-v2026.07.04.010-informational?style=flat-square)](#changelog)
[![CI](https://github.com/cdburgess75/SetList69/actions/workflows/check.yml/badge.svg)](https://github.com/cdburgess75/SetList69/actions/workflows/check.yml)
[![Dependencies](https://img.shields.io/badge/dependencies-none-f5a623?style=flat-square)](#tech)

</div>

<div align="center">

<table>
<tr>
<td width="33%"><img src="docs/screenshots/home.png" alt="Home screen" width="100%"></td>
<td width="33%"><img src="docs/screenshots/song.png" alt="Performance view" width="100%"></td>
<td width="33%"><img src="docs/screenshots/played.png" alt="Played tracking" width="100%"></td>
</tr>
<tr>
<td align="center"><b>Home</b><br><sub>Setlists + song library</sub></td>
<td align="center"><b>Performance view</b><br><sub>Chords locked to syllables</sub></td>
<td align="center"><b>Played tracking</b><br><sub>Cross off as you go</sub></td>
</tr>
</table>

</div>

---

## Why SetList69

Built for the moment you're standing on stage with a guitar in your hands and no free attention to spare:

- 🎸 **Chords render above the exact syllable** — and never split a word across a line, no matter how wide the chord symbol
- 📶 **Works with zero signal** — fully offline once installed; nothing phones home
- 🔆 **Screen stays awake** through the whole set (Wake Lock), never sleeping mid-verse
- 👆 **Swipe between songs**, auto-scroll hands-free, and huge tap targets for the controls you actually touch mid-song
- 🎛 **Transpose, capo, and set-wide key changes** — see the shapes your fingers actually play
- 🗂 **You own the data** — everything lives on your device; move it between phones with a file, not a cloud account

---

## Features

### 🎵 Songs
- Title, artist, key, body — plus optional **capo** (0–11), shown as a badge and folded into the transpose math so chords display as **fingering shapes**
- **Inline ChordPro** (`[G]Amazing [G7]grace`) *and* **chords-above-lyrics** both parse; ChordPro directives (`{key:}`, `{soc}`/`{eoc}`, `{c:note}`) supported
- Chord pills **color-coded by root pitch** — the same root is the same color everywhere
- **Transpose** per song (remembered), **sharp/flat** toggle, adjustable **font size**, and one-tap **fit-to-screen**

### 🗂 Setlists
- Create, rename, reorder, and duplicate sets; per-set **notes** for venue / date / reminders
- **Global set transpose** — shift every song in a set by ±N semitones at once
- **Played tracking** — songs cross off (dimmed row, green strike, `✓ Played` pill) as you open them; long-press to toggle, one tap to reset for the next gig
- **Stage mode** hides all editing chrome and enlarges cards for hands-free reading
- **Share a set** as a file — your bandmate imports it and it *merges* into their library (dedupes by title + artist) without disturbing their songs

### 🎚 Performance dock
The bottom dock keeps only what you touch between songs, with oversized targets:

| Control | Does |
|---|---|
| ◀ · ▶ | Previous / next song (position shown between) |
| ▶ / ⏸ | Start / stop auto-scroll |
| − · + | Auto-scroll speed (1–9) |
| ⚙ | Opens a sheet with transpose, ♯/♭, font, fit &amp; edit |

A thin **progress bar** on the dock shows how much song is left. And **accident-proofing**: while auto-scrolling or in stage mode, leaving a song takes two taps (*"Tap again to leave"*) — a stray thumb can't knock you out mid-verse.

### ✋ Long-press any song
A context sheet slides up: **edit**, **add / move to another set**, **remove from set**, or **delete everywhere**. Drag the `≡` handle to reorder within a set.

---

## Import &amp; Export

| Format | Support |
|---|---|
| ChordPro (`.cho` `.chordpro` `.pro`) | ✅ Full |
| OnSong (`.onsong` `.txt`) | ✅ Full — reads `Key:` &amp; `Capo:` |
| OpenSong XML (`.xml`) | ✅ Full |
| Plain chords-above-lyrics | ✅ Full |
| ZIP bundle of songs | ✅ Expands and imports each entry |
| Chordie embedded chords | ✅ Auto-cleaned (`"Gmget"` → `"[Gm]get"`) |
| Full backup ⇄ JSON | ✅ Save dialog / share sheet / download |
| Single-setlist share file | ✅ Merges into your library |

**Search &amp; paste:** the editor's **Find chords** button opens a helper — type a song, jump to Chordie · E-Chords · Cifraclub · AZLyrics · Genius · Google in a new tab, paste the result back, and it parses straight into the editor.

---

## Install

SetList69 is a **Progressive Web App** — no App Store, no account.

**iPhone / iPad (Safari)**
1. Open **[cdburgess75.github.io/SetList69](https://cdburgess75.github.io/SetList69/)**
2. Share → **Add to Home Screen** → **Add**
3. Open it once with signal — after that it's fully offline

**Android (Chrome)**
1. Open the link and tap **⋮** → **Add to Home Screen** (or the install banner)

> After a new version deploys, installed apps surface an **"⟳ Update ready — tap to refresh"** pill on the home screen — no manual cache clearing.

<div align="center">
<br>
<img src="docs/screenshots/song-light.png" alt="Light theme" width="260">
<br>
<sub><b>Light theme</b> — warm white with deep red-orange chords, WCAG-AA throughout. Dark is the default.</sub>
</div>

---

## Data &amp; privacy

Everything lives **on your device** — IndexedDB with a localStorage fallback. Nothing is sent to any server. Devices sync the way paper setlists always have: export a backup, send it to yourself, import on the other phone.

---

## Tech

| | |
|---|---|
| **Stack** | Vanilla HTML / CSS / JS — no framework, no bundler, no runtime dependencies |
| **Offline** | Service worker (cache-first) + self-hosted WOFF2 fonts |
| **Storage** | IndexedDB, localStorage fallback |
| **Type** | Fraunces (display) · Hanken Grotesk (UI/lyrics) · JetBrains Mono (chords) |
| **Hosting** | GitHub Pages, auto-deployed on push to `main` |
| **CI** | Syntax check · HTML↔SW version-match · duplicate-id guard |

The entire app is **one file** — `setlist69.html`. Everything else exists only to make it installable and offline-capable.

---

## Develop &amp; self-host

```bash
git clone https://github.com/cdburgess75/SetList69.git
cd SetList69
npx serve .          # or just open setlist69.html in a browser
```

Regenerate the README screenshots (headless Chromium via Playwright):

```bash
node docs/shots.js
```

Every change bumps a dated revision (`vYYYY.MM.DD.NNN`) in three synced places — the HTML changelog, the on-screen version tag, and the service-worker cache key — enforced by CI. See [`CLAUDE.md`](CLAUDE.md) for the full architecture and contribution notes.

---

<details>
<summary><b>Changelog</b></summary>

```
v2026.07.04.010  "Played" marks on set songs (dim row, green strike, ✓ Played pill).
v2026.07.04.009  "S69" wordmark on the icon; separate maskable icon for Android crop.
v2026.07.04.008  New app icons: setlist rows with a glowing gold "now playing" row.
v2026.07.04.007  CI workflow: syntax, version-match, and duplicate-id checks.
v2026.07.04.006  One-time install nudge banner (Android prompt / iOS hint).
v2026.07.04.005  Scroll progress bar along the top of the dock.
v2026.07.04.004  Minimal performance dock (big targets) + ⚙ controls sheet.
v2026.07.04.003  Share a single setlist as a file; importing merges into the library.
v2026.07.04.002  Update pill: installed PWAs see "tap to refresh" after a deploy.
v2026.07.04.001  Stage-safe back button: two taps to leave a song while performing.
v2026.06.09.007  Capo support: editor field, badge, fingering-shape display, OnSong Capo:.
v2026.06.09.006  Chord detection: Gm! accent marker; / and - separators in chord lines.
v2026.06.09.005  Auto-clean Chordie embedded chords on paste.
v2026.06.09.004  Editor "Find chords" opens the paste modal.
v2026.06.09.003  Chordie / E-Chords / Cifraclub / Google lookup (dropped Ultimate Guitar).
v2026.06.09.002  Search & paste modal: open chord sites, paste back into the editor.
v2026.06.09.001  Fit-to-screen two-pass correction (no overshoot after re-wrap).
v2026.06.08.004  Stage mode; fit-to-screen; global set transpose; OpenSong XML import.
v2026.06.08.003  Gig fixes: persistent wake lock, 40px swipe, scroll-end haptic, now-playing.
v2026.06.08.002  ZIP bundle import.
v2026.06.08.001  Unified home screen; backup/import moved to a tools sheet.
v2026.06.07.007  Long-press context menu; drag-to-reorder songs in a set.
v2026.06.07.006  Live search; setlist settings; per-song preferred transpose.
v2026.06.07.005  Persistence + custom modals + assorted bug fixes.
v2026.06.07.004  Add-to-setlist from All Songs; picker import; chord search.
v2026.06.07.003  PWA wrapper: manifest, service worker, self-hosted fonts, icons.
v2026.06.07.002  Fixed control dock drifting on long songs.
v2026.06.07.001  Renamed ChordStand → SetList69; adopted dated revisions.
```

</details>

---

<div align="center">
<sub>Built for performing musicians. No cloud, no subscription, no ads — just your songs.</sub>
</div>
