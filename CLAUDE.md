# SetList69 — Handoff Document

> For whoever (or whatever) picks this up next, including Claude Code. This describes the project as of revision **v2026.06.07.002**. You can drop this file into the repo as-is, or rename it `CLAUDE.md` so Claude Code reads it automatically as project context.

-----

## 1. What this is

SetList69 is a self-contained, offline-first web app for performing musicians: it stores songs (lyrics with chords), groups them into setlists, and displays them in a large, high-contrast, hands-free reading view for use while playing an instrument. It is the spiritual cousin of OnSong, rebuilt as a single HTML file the owner controls.

It is **one file**: `setlist69.html`. No build step, no framework, no package manager, no external runtime dependencies. Open it in a browser and it runs. Deployment target is GitHub Pages (static hosting) and "Add to Home Screen" on iPhone/iPad.

Design priorities, in order:

1. **Reliability** — never lose a song; never let the screen sleep mid-verse. An app that loses data is worse than paper.
1. **Readability while playing** — big text, high contrast, chords clearly tied to syllables, no horizontal scrolling.
1. **Offline** — works at a gig with zero signal.
1. **Ownership** — plain code the owner can read, fork, and host himself.

-----

## 2. Versioning & change discipline

Revision scheme: **`vYYYY.MM.DD.NNN`**

- `NNN` increments per shipped change within a day (`001`, `002`, …).
- The date segment tracks the calendar; the first change on a new day resets `NNN` to `001`.
- **Every change ships a revision bump.** No silent edits.

On each change you MUST:

1. Bump the version in **two** places: the HTML comment changelog at the very top of the file, and the `<small>` tag inside the `.brand` element in the header (`id="brand"`).
1. Add a one-line entry to the top-of-file changelog comment describing the change.

Current changelog (top of file):

```
v2026.06.07.001  Renamed project ChordStand -> SetList69; adopted dated revisions.
v2026.06.07.002  Fixed control dock drifting into mid-page on long songs (now pinned to viewport).
```

Note: the project was previously called **ChordStand**. Internal storage identifiers were deliberately left as `chordstand` (see §7) so the rename didn't wipe existing saved data. Do not rename them without a migration.

-----

## 3. Tech constraints (read before editing)

- **Single self-contained file.** All HTML, CSS, and JS live in `setlist69.html`. Keep it that way unless intentionally moving to the PWA bundle (see §13).
- **Vanilla JS only.** No React, no jQuery, no bundler. ES2017+ is fine (async/await, spread, template literals).
- **No external JS/CSS dependencies** except web fonts from Google Fonts (`Fraunces`, `Hanken Grotesk`, `JetBrains Mono`) loaded via `<link>`, with system fallbacks so it still works offline (fonts just fall back). For true offline fidelity these should eventually be self-hosted.
- **Browser-storage caveat:** when viewed inside the Claude artifact preview, IndexedDB / localStorage / the share sheet / file pickers are sandboxed and may not work. These all behave correctly when the file is run standalone (Safari, served, or installed). Don't "fix" non-persistence in the preview — it's expected.
- **Touch features** (swipe) require a real touchscreen; they no-op on desktop.

-----

## 4. Architecture overview

Single-page app with a manual screen router. Layout is a flex column (`.app`): a fixed **header**, a flexible **`main`** holding four absolutely-positioned full-screen `.screen` sections (only one `.show` at a time), and two `.modal` overlays.

**Screens** (`<section class="screen">`):

|id              |Purpose                                       |
|----------------|----------------------------------------------|
|`setlistsScreen`|Home / index. Lists all setlists.             |
|`setSongsScreen`|Songs inside the selected setlist, in order.  |
|`songView`      |The performance view for one song.            |
|`allSongsScreen`|Master song library + backup/restore + import.|

**Modals** (`<div class="modal">`):

|id      |Purpose                                          |
|--------|-------------------------------------------------|
|`editor`|Create/edit/delete a song.                       |
|`picker`|Add existing or new songs to the current setlist.|

**Navigation** is driven by `show(name)` where `name` ∈ `setlists | setSongs | song | allSongs`. It toggles `.show`, swaps the header between brand/back-button/title, manages the wake lock, and stops auto-scroll on leave. `goBack()` implements the back button's contextual target.

Navigation state globals:

- `screen` — current screen name.
- `curSetlist` — id of the setlist being viewed.
- `curSongId` — id of the song in the song view.
- `curIndex` — index of the current song *within* `curSetlist` (`-1` if opened standalone from All Songs; disables prev/next + swipe).
- `cameFromAll` — whether the song view was entered from All Songs (controls back target).

-----

## 5. Data model

A single in-memory `state` object, persisted whole (see §7):

```js
state = {
  songs: [
    { id: "am", title: "Amazing Grace", sub: "Traditional", key: "G", body: "[G]Amazing [G7]grace..." }
  ],
  setlists: [
    { id: "set1", name: "Front Porch", songIds: ["hr", "wf", "sf"] }
  ],
  theme: "dark"   // "dark" | "light"
}
```

Key relationships:

- **Songs are a shared master store.** A song exists once in `state.songs`. Edit it once, every setlist referencing it updates.
- **Setlists reference songs by id.** `setlist.songIds` is an ordered array of `song.id`. The same id may appear in multiple setlists — that is the intended "one song, many setlists" behavior.
- Deleting a song from a setlist removes the id from that `songIds` array only. Deleting a song from All Songs removes it from `state.songs` **and** scrubs its id from every setlist.
- `song.body` is freeform text in either inline-ChordPro (`[C]word`) or chords-above-lyrics format (see §6).
- Ids: seed songs use short literals; runtime songs use `"s" + Date.now()` (+ random for imports); setlists use `uid("set")`.

The seed (`seed()`) ships 6 public-domain songs (Amazing Grace, House of the Rising Sun, Wayfaring Stranger, Will the Circle Be Unbroken, Scarborough Fair, When the Saints Go Marching In) and 2 demo setlists. It runs only when no saved state is found.

-----

## 6. The rendering engine (most complex part — read carefully)

This is the heart of the app and where most subtle bugs live. Goal: render chords stacked directly above the correct syllable, wrapping to the screen width, **never** splitting a word across a line break, **never** scrolling horizontally.

### Pipeline

`renderSheet(song)` → `parseSong(song)` → per-line `renderLine(segs)`.

**`parseSong(song)`** returns `{ meta, lines }`:

- `meta` = `{ title, sub, key }`, seeded from the song fields and overridden by any `{title}`/`{subtitle}`/`{key}` ChordPro directives found in the body.
- `lines` = array of `{ type, ... }`:
  - `{ type:"blank" }` — empty line.
  - `{ type:"comment", text }` — from `{c:...}` / `{comment:...}`.
  - `{ type:"segs", segs:[{chord,text}], chorus }` — a content line. `chorus` is true between `{soc}`/`{eoc}`.
- Detects per-song whether to use inline parsing (`hasInline` = body contains `[...]`) vs. chords-above parsing.

**Segment producers** (both return raw, *un-transposed* `[{chord, text}]`):

- `inlineToSegs(line)` — splits `[C]lyric` into chord+following-text segments.
- `pairToSegs(chordStr, lyricStr)` — for chords-above format: finds each chord's column in the chord line and slices the lyric line at those columns.

**`renderLine(segs)`** — the wrapping/alignment logic:

1. Chords are transposed here (calls `transposeChord`, using the global `transpose`), so re-rendering after a transpose change is just a re-run.
1. Splits text into **word-groups** at spaces. A word-group is wrapped in `.wg` (`white-space:nowrap`) so it cannot break internally — this is what prevents mid-word splits when a chord changes mid-word (e.g. "Or[Am]leans" keeps "Orleans" intact with Am over "leans").
1. Break opportunities (a `.wgspace`) are inserted only *between* word-groups.
1. Each cell renders as `.seg` → `.c` (chord row) over `.l` (lyric). The chord is a `.chordpill` with `background:keyColor(chord)`.
1. **Lines with no chords skip the chord row entirely**, so pure-lyric lines stay vertically compact.

### Transposition

- `SHARP` / `FLAT` arrays, `IDX` map (note name → pitch class 0–11, includes enharmonics like `Db`, `E#`, `Cb`).
- `transposeNote(n)` shifts a single root by the global `transpose` (semitones), honoring the global `preferFlats`.
- `transposeChord(ch)` handles full chords and slash chords (`C/E`) by splitting on `/` and transposing each root, preserving suffixes (`m7`, `sus4`, etc.) via `CHORD_RE = /^([A-G][#b]?)(.*)$/`.
- `looksChord(tok)` / `isChordLine(line)` — heuristics for detecting chords and chord-only lines (used by chords-above detection and the importer).

### Color coding

`keyColor(key)` maps a chord/key's root pitch class to a hue: `hue = pitchClass * 30`, returned as `hsl(hue 52% 42%)`. Used for chord pills, the per-song key pills in lists, and the colored dots on setlist cards. Same root = same color everywhere. Unknown/no root → neutral grey `#7a7160`.

-----

## 7. Persistence

- **Primary:** IndexedDB. `idbOpen()` opens db `"chordstand"`, object store `"kv"`; the entire `state` is stored under key `"state"`. `idbGet`/`idbSet` are thin promise wrappers.
- `persist()` is **debounced 250ms** and serializes the whole state to IndexedDB. On failure it sets `canPersist=false` and falls back to `localStorage["chordstand.fallback"]`; if that also fails it toasts a storage-blocked warning.
- `boot()` loads `state` from IndexedDB on startup (falling back to localStorage, then to `seed()`), normalizes missing fields, applies theme, renders, and shows the setlists screen. If persistence is unavailable it toasts "Preview mode."
- **Internal names remain `chordstand`** intentionally (data continuity across the rename). Don't change without a migration that reads the old db/key first.

Call `persist()` after every mutation of `state`.

-----

## 8. Backup, restore, and import

- **Backup** — `exportData()` (async), tiered so the user can choose a destination:
1. `window.showSaveFilePicker` (desktop Chromium) → real save dialog.
1. `navigator.share({files})` (iOS/iPadOS) → share sheet → Save to Files / send anywhere.
1. Anchor `download` fallback.
   Filename: `setlist69-backup-YYYY-MM-DD.json`. Payload is the full `state`.
- **Restore** — `restoreData(file)` parses a backup JSON, confirms, replaces `state` wholesale, persists, re-renders.
- **Import** — `parseImport(text, fallbackName)` ingests **OnSong native**, **ChordPro**, and **plain text**:
  - Lifts ChordPro `{title}/{subtitle}/{artist}/{key}` directives out of the body.
  - Reads OnSong plain header (first content line = title, next = artist) and `Key:` metadata.
  - Drops known OnSong metadata keys (`tempo`, `time`, `capo`, `ccli`, etc.) but **keeps section labels** like `Verse:`/`Chorus:` in the body.
  - Falls back to the filename for the title.
  - Wired to a **multi-file** picker on All Songs (`onsongInput`), so it doubles as bulk import. Each file becomes a new song in the library.
  - **Supported:** `.zip` bundles containing `.onsong`/ChordPro/`.txt` files — `expandFiles()` unzips using native `DecompressionStream` then passes each entry to `parseImport()`. Works in both the tools sheet importer and the picker importer.
  - **Not supported:** `.onsongarchive` / `.onsongbook` — these are proprietary binary formats (not ZIPs), readable only by OnSong. `.backup` is a ZIP but its song content lives in an SQLite3 database, also not practical. For bulk migration from OnSong, the path is: export songs as `.onsong` or ChordPro individually, zip them, import the zip.

-----

## 9. Song-view controls & behavior

Globals: `transpose` (semitones), `preferFlats` (bool), `fontSize` (rem, default **1.35**), `scrollSpeed` (1–9, default 3).

- **Transpose** `♭−` / `+♯`, with a **`#/b`** toggle for sharp vs flat spelling. Transpose resets to 0 each time a song opens.
- **Font** `A−` / `A+` (0.7–2.4rem).
- **Auto-scroll** — `startScroll()` / `stopScroll()` use `requestAnimationFrame` with a fractional pixel accumulator for smooth slow scrolling; stops at the bottom. Speed adjustable live.
- **Prev/next** — `nextSong()` / `prevSong()` move within `curSetlist` (hidden/disabled when `curIndex < 0`).
- **Swipe** — left/right on `#songView` calls next/prev (touch handlers; ignores vertical-dominant or slow gestures).
- **Edit** (✎) opens the editor for the current song.
- **Wake lock** — `requestWake()` on entering the song view, `releaseWake()` on leaving; re-acquired on `visibilitychange`. Keeps the screen on while performing.

The control **dock is `position:fixed`** to the viewport bottom (was `absolute` and drifted into mid-page on long songs — fixed in .002). `#songView` carries `padding-bottom:7.5rem` so the last line clears the dock.

-----

## 10. Theming & design tokens

CSS custom properties define both themes:

- `:root` = **dark** (near-black `--bg:#121110`, near-white `--ink`, gold `--chord:#ffc24d`).
- `[data-theme="light"]` = **light** (warm white bg, near-black ink, deep red-orange `--chord:#bd3c1c`).
- Toggle: `themeBtn` (☀/☾) → flips `state.theme`, `applyTheme()` sets `data-theme` and swaps the icon. Persisted.

Backgrounds on `html`, `main`, and `.screen` are explicitly painted with `--bg` (this fixed a dark-mode bug where the song area was transparent in the in-app viewer and light text vanished). Header and dock backgrounds are **solid** `--panel` (gradients were removed per owner preference).

Contrast was verified: lyrics ≈17:1 both modes; chords 11.7:1 dark / 5.2:1 light (all ≥ WCAG AA). Keep new colors above AA.

Fonts: `--display` Fraunces (titles), `--ui` Hanken Grotesk (UI + lyrics), `--mono` JetBrains Mono (chords/version).

-----

## 11. Function reference (quick map)

Storage: `idbOpen` `idbGet` `idbSet` `persist`
Seed/init: `seed` `boot` `uid` `applyTheme` `toast`
Music core: `transposeNote` `transposeChord` `looksChord` `isChordLine` `pitchClass` `keyColor`
Parse/render: `esc` `parseSong` `inlineToSegs` `pairToSegs` `renderLine` `renderSheet`
Router/nav: `show` `goBack`
List renderers: `renderSetlists` `renderSetSongs` `renderAllSongs` `renderPicker`
Song view: `openSongInSet` `openSongStandalone` `openCurrent` `reRender` `nextSong` `prevSong` `startScroll` `stopScroll` `requestWake` `releaseWake`
Editor/picker: `openEditor` `closeEditor` `saveSong` `openPicker` `closePicker`
Backup/import: `exportData` `restoreData` `parseImport`

All DOM event wiring is in one block near the bottom (search "events"). `~728` lines total.

-----

## 12. Testing approach (do this before every ship)

There's no test framework — verification is manual but disciplined:

1. **Syntax check:** extract the `<script>` body and run `node --check` on it.
1. **Logic check:** for any change to the music core or parser, write a small Node harness replicating the affected functions and assert against known cases (transpose results, chord-above alignment, word-group splitting, importer field extraction). Examples of cases used historically: `G+2=A`, `Am7+3=Cm7`, `C/E+5=F/A`, "New Or[Am]leans" stays glued, OnSong `Key:`/`Tempo:` handling.
1. **Visual/touch behaviors** (swipe, share sheet, persistence) can only be confirmed on a real device — call those out to the owner for device testing rather than claiming them verified.

-----

## 13. Roadmap & next steps

**Immediate next piece — PWA wrapper** (the last big structural item; makes it truly installable + offline):

- Add `manifest.json` (name, icons, `display:standalone`, theme/background colors).
- Add a service worker that precaches the app shell so it loads with zero signal.
- Add app icons (owner likes the dark/amber theme; design to match).
- Self-host the three fonts so offline rendering keeps the intended type.
- **This is the point where the project stops being one file** and becomes a small static bundle (still trivially GitHub Pages-deployable). Confirm with the owner before splitting the file.

**Parked (owner deprioritized; pick up on request):**

- Capo support.
- Nashville number display.
- Chord diagrams.
- Fit-to-width auto-sizing of the song text.
- OpenSong XML (`.xml`) import — `DOMParser`-based, ~30 lines, covers migration from OpenSong/church projection apps.

**Explicitly out of scope (by design):** cloud sync and any built-in online song catalog. Both fight the offline-first, copyright-clean, owner-controlled design. Moving songs between devices is handled by backup-to-file.

-----

## 14. Known limitations / gotchas

- In-app preview (Claude artifact viewer): storage, share sheet, and file pickers are sandboxed — test standalone.
- Chords-above (non-inline) input relies on column alignment; if the source text's spacing is irregular, chord placement may drift. Inline `[C]` format is the most robust.
- A chord change in the exact middle of a word keeps the word whole (good) but the chord pill sits over the second fragment — correct musically, occasionally looks tight.
- Fonts require network on first load; offline they fall back to system fonts until self-hosted (PWA step).
- The importer handles individual song files, not ZIP archives.

-----

## 15. How to make a change (checklist)

1. Edit `setlist69.html` only.
1. `node --check` the script; logic-test the music/parse core if touched.
1. Bump `NNN` in the header `<small>` **and** add a changelog line in the top comment.
1. If you changed storage shape, add a migration in `boot()` (don't break existing saved state).
1. Hand the owner anything that needs real-device verification (touch, share, install).
