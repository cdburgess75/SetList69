<div align="center">

<img src="icons/icon-512.png" alt="SetList69" width="110" height="110">

# SetList69

### Your songs. Your setlists. On stage, offline, in your hands.

Chord & lyric setlists for gigging musicians — one file, no cloud, no account.

[![Open App](https://img.shields.io/badge/▶_Open_App-e2563a?style=for-the-badge)](https://cdburgess75.github.io/SetList69/)

[![PWA](https://img.shields.io/badge/PWA-installable-8250df?style=flat-square)](#get-it-on-your-phone)
[![Offline](https://img.shields.io/badge/works-offline-2E8B7A?style=flat-square)](#features)
[![CI](https://github.com/cdburgess75/SetList69/actions/workflows/check.yml/badge.svg)](https://github.com/cdburgess75/SetList69/actions/workflows/check.yml)

<table>
<tr>
<td width="25%"><img src="docs/screenshots/home.png" alt="Home" width="100%"></td>
<td width="25%"><img src="docs/screenshots/song.png" alt="Performance view" width="100%"></td>
<td width="25%"><img src="docs/screenshots/played.png" alt="Played tracking" width="100%"></td>
<td width="25%"><img src="docs/screenshots/song-light.png" alt="Light theme" width="100%"></td>
</tr>
<tr>
<td align="center"><sub><b>Sets & songs</b></sub></td>
<td align="center"><sub><b>Chords on the syllable</b></sub></td>
<td align="center"><sub><b>Cross off as you play</b></sub></td>
<td align="center"><sub><b>Light theme</b></sub></td>
</tr>
</table>

</div>

## Features

- 🎸 **Chords sit right above the syllable** — big, color-coded, never splitting a word
- 📶 **Fully offline** at the gig; screen stays awake the whole set
- 🎛 **Transpose & capo** — per song or the whole set; chords show as fingering shapes
- ▶ **Auto-scroll** with speed control, progress bar, and a swipe to change songs
- ✅ **Played tracking** — songs cross off as you go; survives reloads, resets in one tap
- 🎤 **Stage mode** — hides all editing clutter; back button needs two taps so you can't fall out mid-song
- 📥 **Imports** ChordPro, OnSong, OpenSong XML, plain text, ZIP bundles — plus paste from chord sites
- 🤝 **Share a set** with a bandmate as a file; it merges into their library cleanly
- 🔒 **Your data stays on your device** — backup/restore by file, nothing sent anywhere

## Get it on your phone

1. Open **[cdburgess75.github.io/SetList69](https://cdburgess75.github.io/SetList69/)** in Safari (iPhone) or Chrome (Android)
2. **Share → Add to Home Screen** (iPhone) · **⋮ → Add to Home Screen** (Android)
3. Open it once — it's yours offline from then on

## How to use it

1. **Add songs** — tap **+** next to *Songs*, or import files via the **≡** tools menu. Paste `[G]inline chords` or chords-above-lyrics; both just work
2. **Build a set** — tap **+** next to *Setlists*, then add songs and drag **≡** to order them
3. **Play the gig** — open the set, hit **▶ Stage**, tap the first song. Swipe for the next one; songs cross off behind you
4. **Tweak on the fly** — the **⚙** button holds transpose, sharp/flat, font size, and fit-to-screen

## Under the hood

One hand-written HTML file. No framework, no build, no dependencies. Vanilla JS + service worker + IndexedDB, hosted on GitHub Pages, checked by CI on every push.

```bash
git clone https://github.com/cdburgess75/SetList69.git && npx serve .
```

Full changelog lives at the top of [`setlist69.html`](setlist69.html); architecture notes in [`CLAUDE.md`](CLAUDE.md).

---

<div align="center"><sub>Built for performing musicians. No cloud, no subscription, no ads — just your songs.</sub></div>
