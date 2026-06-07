# SetList69

**Offline-first chord & lyric setlist app for performing musicians.**

[![Live App](https://img.shields.io/badge/Live%20App-GitHub%20Pages-brightgreen?style=flat-square)](https://cdburgess75.github.io/SetList69/)
[![PWA](https://img.shields.io/badge/PWA-Installable-blueviolet?style=flat-square)](#installing-to-your-phone)
[![No Dependencies](https://img.shields.io/badge/Dependencies-None-orange?style=flat-square)](#tech)

**→ [Open SetList69](https://cdburgess75.github.io/SetList69/)**

---

## What it does

SetList69 stores your songs — lyrics with chords — groups them into setlists, and displays them in a large, high-contrast reading view built for use while you're playing. It's the spiritual cousin of OnSong, rebuilt as a file you control.

- Works at a gig with **zero signal** — fully offline once installed
- **Chords render above the correct syllable**, wrapping cleanly to any screen width
- **Never splits a word** across a line break, no matter how long the chord symbol
- Screen stays **awake** during a performance (Wake Lock API)
- **Swipe left/right** to move between songs in a set
- Auto-scroll with adjustable speed

---

## Features

### Setlists
- Create, rename, reorder (▲▼), and duplicate setlists
- Add notes per setlist (venue, date, key reminders)
- Color-coded key dots show the harmonic flavor at a glance
- Play ▶ starts at the first song; swipe or tap ◀▶ to navigate

### Songs
- Store title, artist/note, key, and chord/lyric body
- **Inline ChordPro** (`[G]Amazing [G7]grace`) and **chords-above-lyrics** formats both work
- Supports ChordPro directives: `{key:}`, `{soc}` / `{eoc}`, `{c:note}`
- Chord pills are **color-coded by root pitch** — same root = same color everywhere
- Transpose up/down by semitone; preferred transpose **saved per song**
- Sharp/flat spelling toggle
- Font size adjustable (0.7 – 2.4 rem), persisted across sessions

### Import & Export
| Format | Support |
|--------|---------|
| ChordPro (`.cho`, `.chordpro`, `.pro`) | ✅ Full |
| OnSong (`.onsong`, `.txt`) | ✅ Full |
| Plain text with chords above lyrics | ✅ Full |
| Multi-file bulk import | ✅ Picker + All Songs |
| Full backup to JSON | ✅ Share sheet / save dialog / download |
| Restore from JSON backup | ✅ |

- **All Songs screen** — search your library, import files, back up / restore everything
- **Picker** — live search when adding songs to a set

### Themes
- Dark (default) — near-black with amber chords, ≈17:1 contrast
- Light — warm white with deep red-orange chords, ≥ WCAG AA

---

## Installing to your phone

SetList69 is a **Progressive Web App** — no App Store needed.

**iPhone / iPad (Safari):**
1. Open [cdburgess75.github.io/SetList69](https://cdburgess75.github.io/SetList69/) in Safari
2. Tap the Share button → **Add to Home Screen**
3. Tap **Add** — the app icon appears on your home screen
4. Open it once with signal; after that it works fully offline

**Android (Chrome):**
1. Open the link in Chrome
2. Tap the **⋮** menu → **Add to Home Screen** (or the install banner if it appears)

---

## Data & Privacy

All data lives **on your device** — IndexedDB primary, localStorage fallback. Nothing is sent to any server. Songs sync between your devices the same way paper setlists do: export a backup, send it to yourself, import on the other device.

> **Internal storage keys** are named `chordstand` (legacy from a project rename). This is intentional — renaming them would wipe existing saved data.

---

## Tech

| | |
|-|-|
| **Stack** | Vanilla HTML/CSS/JS — no framework, no bundler, no runtime deps |
| **Offline** | Service Worker (cache-first), self-hosted WOFF2 fonts |
| **Storage** | IndexedDB + localStorage fallback |
| **Fonts** | Fraunces (display), Hanken Grotesk (UI/lyrics), JetBrains Mono (chords) |
| **Hosting** | GitHub Pages |
| **Size** | ~1 HTML file + fonts + icons |

---

## Revision history

```
v2026.06.07.001  Renamed project ChordStand → SetList69; adopted dated revisions.
v2026.06.07.002  Fixed control dock drifting into mid-page on long songs.
v2026.06.07.003  PWA wrapper: manifest, service worker, self-hosted fonts, app icons.
v2026.06.07.004  Add-to-setlist from All Songs; picker import; chord search.
v2026.06.07.005  Bug fixes: persist settings; custom modals; goBack fix; swipe hint;
                 backdrop close; card hover fix; font size CSS-only update.
v2026.06.07.006  Live search; setlist settings (rename, notes, reorder, duplicate);
                 preferred transpose per song; narrow-screen card fix.
```

---

## Self-hosting

The app is a static bundle — clone the repo and open `setlist69.html` directly, or deploy to any static host:

```bash
git clone https://github.com/cdburgess75/SetList69.git
# Open setlist69.html in a browser, or:
npx serve .
```

GitHub Pages deploys automatically on every push to `main`.

---

*Built for performing musicians. No cloud, no subscription, no ads — just your songs.*
