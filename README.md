# SetList69

**Offline-first chord & lyric setlist app for performing musicians.**

[![Live App](https://img.shields.io/badge/Live%20App-GitHub%20Pages-brightgreen?style=flat-square)](https://cdburgess75.github.io/SetList69/)
[![PWA](https://img.shields.io/badge/PWA-Installable-blueviolet?style=flat-square)](#installing-to-your-phone)
[![Version](https://img.shields.io/badge/Version-v2026.06.09.007-informational?style=flat-square)](#revision-history)
[![No Dependencies](https://img.shields.io/badge/Dependencies-None-orange?style=flat-square)](#tech)

**→ [Open SetList69](https://cdburgess75.github.io/SetList69/)**

---

## What it does

SetList69 stores your songs — lyrics with chords — groups them into setlists, and displays them in a large, high-contrast reading view built for use while you're playing. It's the spiritual cousin of OnSong, rebuilt as a file you control.

- Works at a gig with **zero signal** — fully offline once installed
- **Chords render above the correct syllable**, wrapping cleanly to any screen width
- **Never splits a word** across a line break, no matter how long the chord symbol
- Screen stays **awake** during a performance (Wake Lock API, persists between songs)
- **Swipe left/right** to move between songs in a set (40px threshold)
- Auto-scroll with adjustable speed

---

## Features

### Setlists
- Create, rename, reorder, and duplicate setlists
- Add notes per setlist (venue, date, key reminders) — shown on the card and inside the set
- Color-coded key dots show the harmonic flavor at a glance
- Live search/filter when browsing songs to add
- **Global set transpose** — shift every song in a set by ±N semitones without touching individual songs
- **Stage mode** — tap ▶ Stage to hide editing chrome and enlarge cards for hands-free reading; tap ✎ Edit to return

### Songs
- Store title, artist/note, key, body — plus optional **capo** (0–11)
- **Inline ChordPro** (`[G]Amazing [G7]grace`) and **chords-above-lyrics** formats both work
- Supports ChordPro directives: `{key:}`, `{soc}` / `{eoc}`, `{c:note}`
- Chord pills are **color-coded by root pitch** — same root = same color everywhere
- Transpose up/down by semitone; **preferred transpose saved per song**
- **Capo support** — set capo in the editor; chords display as fingering shapes; "Capo N" badge shown in song view
- Sharp/flat spelling toggle, persisted across sessions
- Font size adjustable (0.7 – 2.4 rem), persisted across sessions
- **Fit-to-screen** — one tap scales the font so the full song fits in the viewport
- **Live search** in All Songs by title or artist

### Song view controls
The dock at the bottom of the song view provides:

| Control | What it does |
|---------|-------------|
| ♭− / +♯ | Transpose down/up by semitone |
| #/b | Toggle sharp vs flat spelling |
| A− / A+ | Decrease/increase font size |
| fit | Scale font so song fits on screen |
| Speed 1–9 | Auto-scroll speed |
| ▶/⏸ | Start/stop auto-scroll |
| ◀ ▶ | Previous/next song in set |
| ✎ | Edit current song |
| ☀/☾ | Toggle dark/light theme |

### Song management (long-press)
Hold any song card for half a second — the phone vibrates and a context sheet slides up:

| Action | Available in |
|--------|-------------|
| Edit song | Set · All Songs |
| Add / move to another set | Set · All Songs |
| Remove from this set | Set only |
| Delete everywhere | Set · All Songs |

### Reordering
- **Drag to reorder** songs within a set — touch the `≡` handle and pull up or down
- An accent-colored indicator shows where it will land

### Import & Export

| Format | Support |
|--------|---------|
| ChordPro (`.cho`, `.chordpro`, `.pro`) | ✅ Full |
| OnSong (`.onsong`, `.txt`) | ✅ Full — including `Key:` and `Capo:` metadata |
| OpenSong XML (`.xml`) | ✅ Full |
| Plain text with chords above lyrics | ✅ Full |
| ZIP bundle (multiple songs) | ✅ Expands `.onsong`/ChordPro/`.txt` entries |
| Chordie embedded chord format | ✅ Auto-cleaned on paste (`"Gmget"` → `"[Gm]get"`) |
| Full backup to JSON | ✅ Share sheet / save dialog / download |
| Restore from JSON backup | ✅ |

#### Search & paste lyrics
The editor includes a **"Find chords"** button that opens a search-and-paste modal. Type a song name, then open any of the linked sites in a new tab:

- **Chordie** · **E-Chords** · **Cifraclub** (no forced sign-up)
- **AZLyrics** · **Genius** · **Google** (chords + lyrics search)

Copy the result, paste it into the text area, and tap **Import** — the app parses it straight into the editor. Chordie's embedded chord format is cleaned automatically. The editor also has a **"Strip tab/performance notes"** button to remove `:=` lines and pure parenthetical annotations before saving.

### Themes
- **Dark** (default) — near-black with amber chords, ≈17:1 contrast
- **Light** — warm white with deep red-orange chords, ≥ WCAG AA throughout

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
v2026.06.07.007  Long-press context menu on songs (edit/move/remove/delete);
                 drag-to-reorder songs in a set via ≡ handle.
v2026.06.07.008  Fix long-press context menu not firing on All Songs screen.
v2026.06.08.001  Unified home screen: setlists and songs together; backup/import
                 moved to tools sheet.
v2026.06.08.002  ZIP bundle import: .zip files containing song files expand on import.
v2026.06.08.003  Gig fixes: wake lock persists between songs; swipe threshold 40px;
                 scroll-end haptic + visual flash; current song highlighted in set;
                 search debounced.
v2026.06.08.004  Stage mode; fit-to-screen font button; global set transpose;
                 OpenSong XML import.
v2026.06.09.001  Fit-to-screen two-pass correction (no overshoot after re-wrap).
v2026.06.09.002  Search & paste modal: open chord sites, paste result, auto-fills editor.
v2026.06.09.003  Replaced Ultimate Guitar with Chordie/E-Chords/Cifraclub/Google.
v2026.06.09.004  Editor "Find chords" button opens paste modal instead of going to UG.
v2026.06.09.005  Auto-clean Chordie embedded chords on paste.
v2026.06.09.006  Fix chord detection: Gm! accent marker; / and - separators in chord lines.
v2026.06.09.007  Capo support: per-song editor field, "Capo N" badge in song view,
                 chords display as fingering shapes; OnSong Capo: metadata imported;
                 strip tab/performance notes button in editor.
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
