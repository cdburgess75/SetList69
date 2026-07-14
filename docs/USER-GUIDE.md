# SetList69 — User Guide

Everything you need to run a gig from SetList69. No account, no internet required once it's installed — your songs live on your device.

**Jump to:** [Install](#1-put-it-on-your-phone) · [The home screen](#2-the-home-screen) · [Add songs](#3-add-songs) · [Import your library](#4-import-your-library) · [Build a setlist](#5-build-a-setlist) · [Perform](#6-perform-the-main-event) · [Transpose & capo](#7-transpose--capo) · [Backup & share](#8-backup-restore--share) · [Updates](#9-updates-the-coloured-dot) · [Tips](#10-tips--troubleshooting)

---

## 1. Put it on your phone

SetList69 is a web app that installs like a native one — no App Store.

**iPhone / iPad (Safari)**
1. Open **https://cdburgess75.github.io/SetList69/**
2. Tap the **Share** button → **Add to Home Screen** → **Add**
3. Open it once with signal. After that it works fully offline.

**Android (Chrome)**
1. Open the link, tap **⋮** → **Add to Home Screen** (or the install banner that pops up)

> Once installed it runs full-screen, keeps the screen awake while you play, and works with zero signal.

---

## 2. The home screen

<div align="center"><img src="screenshots/home.png" alt="Home screen" width="300"></div>

Two sections stacked on one page:

- **Setlists** — your sets (e.g. *Front Porch*, *Sunday Morning*). Each shows how many songs it has and colored dots for the keys inside. Use **▲ ▼** to reorder, **✎** for settings, **✕** to delete the set (the songs stay in your library).
- **Songs** — your **whole library**, every song you've added or imported. Search it with the box; a song appears here once no matter how many sets use it.

**Header buttons (top right):**

| Button | What it does |
|---|---|
| 🟢 / 🔴 dot | Status light — green = up to date, red = an update is available |
| **≡** | Tools: import, search & paste lyrics, backup, restore |
| **☾ / ☀** | Switch between dark and light themes |
| **+** (next to a heading) | New setlist / new song |

---

## 3. Add songs

Tap **+** next to **Songs**. The editor opens:

- **Title**, **Artist / note**, **Key**, and **Capo** (0–11, use the − / + stepper)
- **Chords & lyrics** — paste in either format, both work:

```
[G]Amazing [G7]grace how [C]sweet the [G]sound      ← inline (chords in brackets)

G        G7        C          G
Amazing  grace how sweet the  sound                  ← chords on the line above
```

Two helpers in the editor:

- **↗ Find chords & lyrics online** — opens a search box. Type the song, tap a site (Chordie, E-Chords, Cifraclub, AZLyrics, Genius, Google), copy the result, paste it back, and tap **Import** — it drops straight into the editor.
- **✕ Strip tab / performance notes** — cleans out rhythm-notation and stray `(...)` lines from a messy paste.

Tap **Save**. The song is now in your library under **Songs**.

> **Editing a song updates it everywhere.** Songs are shared — fix a chord once and every setlist that uses that song reflects it.

---

## 4. Import your library

Already have your songs in another app? Bring them in with **≡ → Import songs**.

| Format | Notes |
|---|---|
| OnSong (`.onsong`, `.txt`) | Reads the **Key:** and **Capo:** too |
| ChordPro (`.cho`, `.chordpro`, `.pro`) | Full support |
| OpenSong XML (`.xml`) | Full support |
| Plain text (chords above lyrics) | Full support |
| **`.zip` of any of the above** | Unpacks and imports every song inside |

**Bulk import from OnSong:** export your songs as individual `.onsong` files, put them in a `.zip`, and import the zip — the whole batch lands in your library at once. (If any files can't be read, the toast tells you how many were skipped.)

---

## 5. Build a setlist

1. Tap **+** next to **Setlists** and name it.
2. Open the set and tap **+ Add song to this set**. From there you can:
   - **✏ Write new song** — create one on the spot
   - **♫ Import file** — pull songs from files/zip straight into this set
   - **Search** your existing library and tap a song to add it
3. **Reorder** — drag the **≡** handle on a song up or down.
4. **Long-press a song** (hold ~½ second) for its menu:
   - Edit song · Add / move to another set · Remove from this set · **Mark played / unplayed** · Delete everywhere

**Setlist settings (✎ on the set):** rename it, add **notes** (venue, date, reminders), **⧉ Duplicate** it, or **⇪ Share** it (see §8).

---

## 6. Perform — the main event

Open a set and tap a song (or tap the big **▶** to start from the first). This is the performance view:

<div align="center"><img src="screenshots/song.png" alt="Performance view" width="300"></div>

**Chords sit directly above the syllable they change on**, color-coded by key, and never split a word across a line.

### The dock (bottom bar)

| Control | Does |
|---|---|
| **◀ 1/3 ▶** | Previous / next song (shows your position in the set) |
| **▶ / ⏸** | Start / stop **auto-scroll** |
| **− 3 +** | Auto-scroll speed (1–9) |
| **⚙** | Opens more controls: transpose, ♯/♭, font size, fit-to-screen, and **✎ Edit** |

- A thin **progress bar** on top of the dock shows how much song is left.
- **Swipe left / right** on the lyrics to change songs.
- The screen **won't sleep** while you're in a song.

### Stage mode

On the set screen, tap **▶ Stage**. This hides all the editing clutter and enlarges the song cards for clean, hands-free tapping during a show. Tap **✎ Edit** to come back out.

### Won't-lose-your-place protection

While auto-scroll is running or you're in stage mode, the **Back** button needs **two taps** ("Tap again to leave") — so a stray thumb can't knock you out of a song mid-verse.

### Played tracking

<div align="center"><img src="screenshots/played.png" alt="Played tracking" width="300"></div>

As you play through a set, each song **crosses off behind you** — dimmed, green strikethrough, a **✓ Played** tag. Long-press to toggle it by hand. These marks **survive reloads** so they last the whole gig, and **↺ Reset played** (top of the set) clears them for the next one.

---

## 7. Transpose & capo

- **Whole set:** on the set screen, use **♭− ±0 +♯** ("set key") to shift *every* song in the set at once.
- **One song:** open it, tap **⚙**, and use **♭− / +♯**. Your choice is remembered per song. **♯/♭** switches how accidentals are spelled.
- **Capo:** set it in the editor (0–11). The song view shows a **"Capo N"** badge and displays chords as the **shapes your fingers actually play** — so a Capo 3 song in the key of C shows you A-shape, D-shape, etc.

---

## 8. Backup, restore & share

Your data lives only on your device, so **back it up** and that's also how you move it between phones.

- **Back up everything:** **≡ → Back up all data to a file** → save/share the `.json`.
- **Restore:** **≡ → Restore from a backup file** → pick the `.json`. (This *replaces* your current library — you'll be asked to confirm.)
- **Share one setlist:** on a set, **✎ settings → ⇪ Share**. Send the file to a bandmate; when they import it, it **merges** into their library — songs they already have aren't duplicated, and the set is added.

---

## 9. Updates (the colored dot)

The dot next to the SetList69 logo is a status light:

- **🟢 Green** — you're running the latest version. Nothing to do.
- **🔴 Red** + a **⟳** button appear when a new version is available. A banner also slides down naming the version. Tap **Update now** (or the **⟳**) when you're *not* mid-song, and it refreshes.

It **never** updates on its own mid-performance, and it won't nag you when you're already current.

---

## 10. Tips & troubleshooting

- **Nothing is sent anywhere.** No account, no cloud, no ads. Your catalog is yours, on your device.
- **Back up before a big gig.** It's one tap and it's your safety net (and your way onto a second device).
- **Song too long to fit?** Open it, tap **⚙ → fit** to auto-size it to the screen, or use auto-scroll.
- **Chords look misaligned?** The inline `[C]word` format is the most reliable. If a chords-above paste drifts, the spacing in the source was uneven — re-paste or switch that song to inline.
- **A song won't import?** `.onsongarchive`, `.onsongbook`, and `.backup` are OnSong's private binary formats and can't be read directly — export those songs as individual `.onsong` (or ChordPro) files first, then zip and import.
- **Two taps to leave a song** is on purpose — you're either auto-scrolling or in stage mode. Tap Back again within a moment to leave.

---

*Questions or something acting up? Open an issue on the [GitHub repo](https://github.com/cdburgess75/SetList69).*
