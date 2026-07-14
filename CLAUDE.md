# SetList69 — Handoff Document

> For whoever (or whatever) picks this up next, including Claude Code. This describes the project as of revision **v2026.07.12.006**. Kept in the repo as `CLAUDE.md` so Claude Code reads it automatically as project context.

-----

## 0. North Star (read this before proposing anything)

**SetList69 exists to be the app a working band runs its live set from — with their existing catalog brought over from OnSong and other chord apps.** Every decision, feature, and refactor is checked against this. Success = the band runs a full gig from it, having imported their whole library.

> **Framing (public):** lead with *compatibility* — "imports from OnSong and other apps" — never competition. Do not describe the project as "replacing" or "an alternative to" any named product in the README, marketing, or commit messages. Internally the bar is simply that it's good enough a band doesn't need the app they came from; that's a quality target, not a slogan.

Goals, ranked — when they conflict, the higher one wins:

1. **Reliability at the gig** — never lose a song, never sleep mid-verse, work with **zero signal**.
2. **Get the band's real catalog in** — high-fidelity **import (OnSong exports first)** is the gate to real use. Until the whole library loads cleanly, nothing else matters; a rehearsal test is the only proof the North Star is reachable.
3. **Readable while playing** — big text, high contrast, chords on the syllable, no horizontal scroll, hands-free.
4. **Ownership** — local-first, **no backend/account/telemetry**, **zero runtime dependencies**; data lives on the device and moves by file.

**Hard constraints (product-defining, do not break):** no server; fully offline-capable; no runtime dependencies; data local to the device.
**Pragmatic constraint (breakable when it hurts correctness — but flag it loudly):** the single-file build. It's a convenience for deploy/fork, not a commandment.
**Sync:** a *someday*. When it comes it is "shared storage the band controls" (a shared folder / iCloud / Dropbox / local network), **never a server we stand up**. Design toward that seam; don't build it yet.
**Audience:** working bands, not a solo toy and not an open-source project first (though it is MIT-licensed — see §17). **Maintainer:** undecided — so keep the code human-readable *and* keep this doc AI-usable.

-----

## 1. What this is

SetList69 is an offline-first web app for performing musicians: it stores songs (lyrics with chords), groups them into setlists, and displays them in a large, high-contrast, hands-free reading view for use while playing. It is the spiritual cousin of OnSong, rebuilt as a small static bundle the owner controls.

Deployment target: GitHub Pages + "Add to Home Screen" on iPhone/iPad.

Design priorities, in order — see §0 for the full North Star:

1. **Reliability** — never lose a song; never let the screen sleep mid-verse.
2. **Catalog in** — high-fidelity import (OnSong first) is the gate to real gig use.
3. **Readability while playing** — big text, high contrast, chords tied to syllables, no horizontal scrolling.
4. **Offline** — works at a gig with zero signal.
5. **Ownership** — local-first, no server, no dependencies; plain code the owner can read, fork, and host.

The project was previously called **ChordStand**. Internal storage identifiers remain `chordstand` (see §7) so the rename didn't wipe existing saved data. Do not rename them without a migration.

-----

## 2. Versioning & change discipline

Revision scheme: **`vYYYY.MM.DD.NNN`**

- `NNN` increments per shipped change within a day (`001`, `002`, …).
- The date segment tracks the calendar; the first change on a new day resets `NNN` to `001`.
- **Every change ships a revision bump.** No silent edits.

On each change you MUST update **three** places:

1. The HTML comment changelog at the very top of `setlist69.html`.
2. The `<small>` version tag inside the `.brand` element (`id="brand"`) in `setlist69.html`.
3. The `CACHE` constant at the top of `sw.js` — must match the HTML version exactly (`setlist69-vYYYY.MM.DD.NNN`).

Current changelog:

```
v2026.06.07.001  Renamed project ChordStand -> SetList69; adopted dated revisions.
v2026.06.07.002  Fixed control dock drifting into mid-page on long songs (now pinned to viewport).
v2026.06.07.003  PWA wrapper: manifest, service worker, self-hosted fonts, app icons.
v2026.06.07.004  Add-to-setlist from All Songs; picker import option; lyrics fetch + chord search.
v2026.06.07.005  Bug fixes: persist font/speed/flats; custom prompt/confirm modals; goBack fix;
                 hide Play FAB on empty sets; swipe hint auto-hide; backdrop tap closes modals;
                 card hover theme fix; font size CSS-only update; simplified chord lookup.
v2026.06.07.006  Live search in All Songs + Picker; setlist settings (rename, notes, reorder,
                 duplicate); preferred transpose persisted per song; narrow-screen card fix.
v2026.06.07.007  Long-press context menu on songs (edit/move/remove/delete); drag-to-reorder
                 songs in a set via ≡ handle; removes ▲▼ buttons.
v2026.06.07.008  Fix long-press context menu not firing on All Songs screen.
v2026.06.08.001  Unified home screen: setlists and songs together; backup/import moved to tools sheet.
v2026.06.08.002  ZIP bundle import: .zip files containing .onsong/.chordpro/.txt expand on import.
v2026.06.08.003  Gig fixes: wake lock no longer drops between songs; swipe threshold 60→40px;
                 scroll-end haptic + visual flash; current song highlighted in set view;
                 search debounced 150ms.
v2026.06.08.004  Stage mode (hides editing chrome during performance); fit-to-screen font button;
                 global set transpose; OpenSong XML import.
v2026.06.09.001  Fit-to-screen two-pass correction so re-wrapping at smaller size doesn't overshoot.
v2026.06.09.002  Search & paste modal: type song name, open chord sites in new tab, paste result
                 back — drops straight into editor pre-filled.
v2026.06.09.003  Replaced Ultimate Guitar with Chordie/E-Chords/Cifraclub (no forced signup);
                 added Google "chords lyrics" search; two-row layout with section labels.
v2026.06.09.004  Editor "Find chords" button now opens the paste modal instead of going to UG.
v2026.06.09.005  Auto-clean Chordie embedded chords on paste: "Gmget"→"[Gm]get" etc.
v2026.06.09.006  Fix chord detection: "Gm!" accent marker recognised; "/" and "-" separators
                 allowed in chord lines so "Cm / Bb / Dm - D" parses correctly.
v2026.06.09.007  Capo support: per-song capo field in editor (0-11), chords display as fingering
                 shapes, "Capo N" badge in song view, OnSong Capo: metadata imported.
                 Strip tab notes button in editor removes := lines and pure parentheticals.
v2026.07.04.001  Stage-safe back button: while auto-scroll runs or stage mode is on, leaving a
                 song takes two taps ("Tap again to leave") within 1.5s.
v2026.07.04.002  Update pill: controllerchange from an updated SW surfaces "⟳ Update ready —
                 tap to refresh" on the home screen only; never auto-reloads.
v2026.07.04.003  Share one setlist (⇪ in setlist settings) as {app,kind:"set",version:1,setlist,
                 songs}; restoreData detects kind:"set" and MERGES (title+artist dedupe).
v2026.07.04.004  Minimal performance dock (prev/pos/next, play, speed, ⚙) + #dockSheet holding
                 transpose, ♯/♭, font, fit, edit. Ids unchanged; edit hidden in stage mode.
v2026.07.04.005  Scroll progress bar (3px, scaleX) at top edge of dock; hidden when song fits.
v2026.07.04.006  Install nudge banner: beforeinstallprompt on Android/desktop, A2HS hint on iOS
                 Safari; dismissal in localStorage "setlist69.installDismissed" (not state).
v2026.07.04.007  GitHub Actions check workflow (syntax, version match, duplicate ids); docs.
v2026.07.04.008  New app icons: setlist rows with glowing gold "now playing" row (512/192/180).
v2026.07.04.009  "S69" Fraunces wordmark upper-left on icons; icon-512-maskable.png (rows only,
                 no wordmark) for Android maskable purpose; manifest + SW precache updated.
v2026.07.04.010  "Played" marks on set songs (ham-radio "worked" styling): dim row, green
                 strikethrough, "✓ Played" pill; auto-mark on open, long-press toggle, ↺ Reset.
v2026.07.04.011  "Played" marks persist per-set in localStorage ("setlist69.played"), surviving
                 reloads/backgrounding; kept out of state so backups stay clean.
v2026.07.12.001  Update banner replaces the pill: slides down on the home screen naming the new
                 version (SW GET_VERSION postMessage handshake), auto-hides after 6s; header ⟳
                 persists to re-open/authorize. Never auto-reloads; never shown mid-song.
v2026.07.12.002  Audit tier-1 hardening: esc() escapes quotes + ids escaped into attributes
                 (stored-XSS via restored backups closed); isValidState() guards restore/boot;
                 navigator.storage.persist(); debounced save flushed on hide/pagehide; localStorage
                 fallback read when IDB empty; merge tolerates non-string fields.
v2026.07.12.003  Audit tier-2 (correctness): file import keeps OnSong Capo:; unzip reads the ZIP
                 central directory (data-descriptor zips no longer drop entries) + skipped counts;
                 collision-proof newSongId(); window.open noopener; back-guard disarms on song
                 change; drag ignores a 2nd finger.
v2026.07.12.004  Audit tier-3 (a11y): pinch-zoom re-enabled; aria-labels on all icon buttons;
                 modals role=dialog/aria-modal + Escape + Tab-trap + focus restore; aria-live toast;
                 --faint lifted to AA; prefers-reduced-motion; focus-visible ring.
v2026.07.12.005  Audit tier-4 (perf): transpose/♯♭ retunes chord pills in place (retuneSheet,
                 data-ch) instead of re-parsing; drag touchmove bound only during a drag;
                 structuredClone; deduped .card CSS.
v2026.07.12.006  Infra: SW offline navigation falls back to the app shell (ignoreSearch match);
                 index.html precached; CI parses manifest + asserts PRECACHE files exist, adds
                 permissions/concurrency; manifest gains id/scope/lang/categories/screenshots and
                 a theme_color that matches the page meta.
```

A GitHub Actions workflow (`.github/workflows/check.yml`) enforces the version discipline on every push: it syntax-checks the extracted inline script and `sw.js`, **fails if the `<small>` brand version ≠ `sw.js` CACHE version**, and fails on duplicate element ids in the markup.

-----

## 3. File structure

The PWA wrapper is complete. The repo contains:

```
setlist69.html      — the entire app (HTML + CSS + JS)
index.html          — meta-refresh stub → setlist69.html (GitHub Pages root URL)
sw.js               — service worker (cache-first, precaches all assets)
manifest.json       — PWA manifest (id, icons, screenshots, display:standalone)
.github/workflows/check.yml — CI: syntax, version-match, duplicate-id, manifest+precache checks
fonts/
  fraunces-latin.woff2
  hanken-grotesk-latin.woff2
  jetbrains-mono-latin.woff2
icons/
  icon-192.png
  icon-512.png
  icon-512-maskable.png   — rows-only variant for Android's circular mask
  apple-touch-icon.png
docs/
  shots.js                — Playwright helper: regenerates the README screenshots
  screenshots/            — real app captures used by README.md
  DEVICE-TESTING.md       — manual on-device test checklist
```

All app logic lives in `setlist69.html`. The other files exist solely to make it installable and offline-capable.

**Tech constraints:**

- **Vanilla JS only.** No React, no jQuery, no bundler. ES2017+ is fine.
- **No external JS/CSS dependencies.** Fonts are self-hosted WOFF2 (offline-safe).
- **Browser-storage caveat:** when viewed inside the Claude artifact preview, IndexedDB / localStorage / the share sheet / file pickers are sandboxed. These behave correctly when run standalone. Don't "fix" non-persistence in the preview — it's expected.
- **Touch features** (swipe) require a real touchscreen; they no-op on desktop.

-----

## 4. Architecture overview

Single-page app with a manual screen router. Layout is a flex column (`.app`): a fixed **header**, a flexible **`main`** holding three absolutely-positioned full-screen `.screen` sections (only one `.show` at a time), and modal overlays.

**Screens** (`<section class="screen">`):

| id | Purpose |
|----|---------|
| `setlistsScreen` | Home / index. Lists all setlists + song library (the `allSongList` container — `renderAllSongs()` renders into it despite the name; there is no separate All Songs screen anymore). |
| `setSongsScreen` | Songs inside the selected setlist, in order. |
| `songView` | Performance view for one song. |

**Modals** (`<div class="modal">`):

| id | Purpose |
|----|---------|
| `editor` | Create/edit/delete a song. |
| `picker` | Add existing or new songs to the current setlist. |
| `pasteModal` | Search-and-paste lyrics assistant (opens chord sites, parses pasted text). |
| `dockSheet` | ⚙ song-controls sheet: transpose, ♯/♭, font/fit, edit (edit hidden in stage mode). |

**Navigation** is driven by `show(name)` where `name` ∈ `setlists | setSongs | song`. It toggles `.show`, swaps the header, manages the wake lock, and stops auto-scroll on leave. `goBack()` implements contextual back.

**Navigation state globals:**

- `screen` — current screen name.
- `curSetlist` — id of the setlist being viewed.
- `curSongId` — id of the song in the song view.
- `curIndex` — index of the current song within `curSetlist` (`-1` = opened standalone; disables prev/next + swipe).
- Back target is derived, not stored: `goBack()` returns to the set when `curIndex>=0 && curSetlist`, else home.
- `curSetTranspose` — global semitone offset applied to every song in the current set.
- `stageMode` — boolean; hides editing chrome and enlarges cards for hands-free reading.
- `capoVal` — capo fret number for the current song (0 = no capo); used in transpose math.

-----

## 5. Data model

A single in-memory `state` object, persisted whole (see §7):

```js
state = {
  songs: [
    {
      id: "am",
      title: "Amazing Grace",
      sub: "Traditional",
      key: "G",
      capo: 0,               // optional; 0 or absent = no capo
      defaultTranspose: 0,   // semitones saved from last session
      body: "[G]Amazing [G7]grace..."
    }
  ],
  setlists: [
    { id: "set1", name: "Front Porch", notes: "", setTranspose: 0, songIds: ["hr", "wf", "sf"] }
  ],
  theme: "dark"   // "dark" | "light"
}
```

Key relationships:

- **Songs are a shared master store.** Edit a song once, every setlist referencing it updates.
- **Setlists reference songs by id.** `setlist.songIds` is an ordered array. Same song can appear in multiple setlists.
- Deleting from a setlist removes the id from that `songIds` only. Deleting from All Songs scrubs it from every setlist.
- `song.body` is freeform text — inline ChordPro (`[C]word`) or chords-above-lyrics.
- Ids: seed songs use short literals; runtime songs use `"s" + Date.now()` (+ random for imports); setlists use `uid("set")`.

The seed (`seed()`) ships 6 public-domain songs and 2 demo setlists. Runs only when no saved state is found.

-----

## 6. The rendering engine (most complex part — read carefully)

Goal: render chords stacked directly above the correct syllable, wrapping to screen width, **never** splitting a word across a line break, **never** scrolling horizontally.

### Pipeline

`renderSheet(song)` → `parseSong(song)` → per-line `renderLine(segs)`.

**`parseSong(song)`** returns `{ meta, lines }`:

- `meta` = `{ title, sub, key }`, seeded from song fields and overridden by ChordPro directives.
- `lines` = array of `{ type, ... }`:
  - `{ type:"blank" }` — empty line.
  - `{ type:"comment", text }` — from `{c:...}` / `{comment:...}`.
  - `{ type:"segs", segs:[{chord,text}], chorus }` — a content line.
- Detects per-song whether to use inline parsing (`hasInline` = body contains `[...]`) vs. chords-above.

**Segment producers** (return raw, *un-transposed* `[{chord, text}]`):

- `inlineToSegs(line)` — splits `[C]lyric` into chord+following-text segments.
- `pairToSegs(chordStr, lyricStr)` — for chords-above format; finds each chord's column and slices the lyric.

**`renderLine(segs)`** — the wrapping/alignment logic:

1. Chords are transposed here (calls `transposeChord` with global `transpose`); re-rendering after a change is just a re-run.
2. Splits text into **word-groups** (`.wg`, `white-space:nowrap`) — prevents mid-word splits.
3. Break opportunities (`.wgspace`) inserted only *between* word-groups.
4. Each cell: `.seg` → `.c` (chord row) over `.l` (lyric). Chord is `.chordpill` with `background:keyColor(chord)`.
5. Lines with no chords skip the chord row entirely.

### Transposition & capo

- `SHARP` / `FLAT` arrays, `IDX` map (note name → pitch class 0–11).
- `transposeNote(n)` shifts a single root by global `transpose`, honoring `preferFlats`.
- `transposeChord(ch)` handles slash chords (`C/E`) and preserves suffixes via `CHORD_RE = /^([A-G][#b]?)(.*)$/`.
- **Capo math in `openCurrent`:** `transpose = (song.defaultTranspose || 0) + curSetTranspose - capoVal`. Subtracting `capoVal` means chords display as fingering shapes (what your fingers fret), not sounding pitch.
- **Saving transpose back:** `song.defaultTranspose = transpose + capoVal - curSetTranspose` — stores the sounding key, not the capo-relative value, so it survives capo changes.

### Chord detection

`looksChord(tok)` — regex heuristic; accepts trailing `!` and `*` (E-Chords accent markers):
```js
/^[A-G][#b]?(m|maj|min|dim|aug|sus|add)?[0-9]*(\([^)]*\))?(\/[A-G][#b]?)?[!*]?$/
```

`isChordLine(line)` — all tokens must be chords OR pure separators (`/`, `-`, `|`); at least one chord required. This handles "Cm / Bb / Dm - D" correctly.

### Chordie auto-clean

`cleanEmbeddedChords(text)` runs as a pre-pass in `parseImport()`. Converts Chordie's embedded format (chord names stuffed directly into words) to inline ChordPro:

- **Mid-word:** chord preceded by a lowercase letter → `"Gmget"` after `"li"` becomes `"li[Gm]get"`.
- **Word-start:** only matches chords with accidentals or suffixes — bare `A–G` are skipped to prevent `"And"` → `"[A]nd"`.

### Color coding

`keyColor(key)` maps root pitch class to `hsl(pitchClass*30 52% 42%)`. Unknown root → `#7a7160`.

-----

## 7. Persistence

- **Primary:** IndexedDB. `idbOpen()` opens db `"chordstand"`, object store `"kv"`; the entire `state` is stored under key `"state"`.
- `persist()` is **debounced 250ms** (`structuredClone(state)` → IDB). On failure falls back to `localStorage["chordstand.fallback"]`; if that also fails, toasts a warning.
- `flushPersist()` writes immediately (sync localStorage mirror + best-effort IDB) on `visibilitychange→hidden` and `pagehide`, closing the 250ms loss window (e.g. the "Update now" reload). `boot()` requests `navigator.storage.persist()` so the library isn't evicted under storage pressure.
- **`isValidState(d)`** structurally validates ANY payload loaded from disk — restore file, IndexedDB, or the localStorage fallback — before it can replace `state`. A malformed payload is rejected (toast) instead of being persisted and bricking every render. `boot()` reads the localStorage fallback whenever IDB yields no valid state (not only when it throws).
- **Internal names remain `chordstand`** — don't rename without a migration.

Call `persist()` after every mutation of `state`.

-----

## 8. Backup, restore, and import

**Backup** — `exportData()` (async) → `saveJsonFile(name,json,title)`, the shared tiered save helper:
1. `window.showSaveFilePicker` (desktop Chromium) → save dialog.
2. `navigator.share({files})` (iOS/iPadOS) → share sheet.
3. Anchor `download` fallback.

Filename: `setlist69-backup-YYYY-MM-DD.json`. Payload: full `state`.

**Share one setlist** — `shareSetlist(id)` (⇪ button in setlist settings) exports `{app:"setlist69",kind:"set",version:1,setlist:{name,notes,setTranspose},songs:[full song objects]}` via `saveJsonFile`.

**Restore** — `restoreData(file)` parses JSON. If the payload has `kind:"set"`, it **merges** via `mergeSetImport(d)` instead of replacing: song identity is **title+sub, case-insensitive, trimmed** (joined with a `"\u0000"` separator — don't "simplify" to a space, it collides); existing songs are reused untouched, unknown ones added with fresh import-style ids, and the set is appended with `uid("set")`. Otherwise it confirms and replaces state wholesale as before. Merge logic has a Node harness (see §13).

**Import** — `parseImport(text, fallbackName)` ingests multiple formats:

| Format | Notes |
|--------|-------|
| ChordPro (`.cho`, `.chordpro`, `.pro`) | Full; lifts `{title}`, `{subtitle}`, `{artist}`, `{key}` directives |
| OnSong (`.onsong`, `.txt`) | Full; reads `Key:`, `Capo:` metadata; drops `Tempo:`, `Time:`, `CCLI:` etc. |
| OpenSong XML (`.xml`) | `DOMParser`-based; reads `<lyrics>`, `<title>`, `<author>`, `<key>`, `<capo>` |
| Plain chords-above-lyrics | Full |
| Chordie embedded format | Auto-cleaned to inline ChordPro by `cleanEmbeddedChords()` |
| ZIP bundle | `expandFiles()` decompresses with native `DecompressionStream`, passes each entry to `parseImport()` |

**Not supported:** `.onsongarchive` / `.onsongbook` (proprietary binary), `.backup` (ZIP but SQLite inside). Bulk OnSong export path: export individual songs as `.onsong`, zip them, import the zip.

**Search & paste modal** (`pasteModal`) — editor has a "Find chords" button that opens this. User types a song name, opens one of 6 linked sites in a new tab (Chordie, E-Chords, Cifraclub, AZLyrics, Genius, Google), copies the result, pastes into the textarea, taps Import. `parseImport()` handles the rest. There is no server-side proxy — CORS prevents fetching arbitrary external sites from the browser; the manual copy-paste step is intentional.

-----

## 9. Song-view controls & behavior

Globals: `transpose` (semitones, 0 on song open), `preferFlats` (bool), `fontSize` (rem, default **1.35**), `scrollSpeed` (1–9, default 3), `capoVal` (fret, 0 if no capo), `curSetTranspose` (set-level offset), `stageMode` (bool).

**Transpose:** `♭−` / `+♯` buttons; `#/b` toggle. Saved as `defaultTranspose` on the song.

**Capo:** Set in editor (0–11). Shown as "Capo N" badge in song view (amber, monospaced). Subtracts from `transpose` so chords display as fingering shapes.

**Font:** `A−` / `A+` (0.7–2.4 rem). **`fit`** button scales font so the full song fits the viewport — two-pass (`requestAnimationFrame` after first `reRender()`) to correct for re-wrapping at smaller sizes.

**Auto-scroll:** `startScroll()` / `stopScroll()` use `requestAnimationFrame` with fractional pixel accumulator. Stops at bottom with haptic + amber flash. Speed adjustable live.

**Stage mode:** `stageMode` toggle — hides the editor chrome (context menu, edit button) and enlarges song cards so cards are easier to tap during a performance. ▶ Stage enters; ✎ Edit exits.

**Global set transpose:** `curSetTranspose` offset applied on top of each song's `defaultTranspose`. Set from the set view header control (±N semitones). Resets to 0 when leaving the set.

**Prev/next:** `nextSong()` / `prevSong()` — hidden when `curIndex < 0`. Swipe left/right triggers these (40px threshold, ignores vertical-dominant gestures).

**Wake lock:** `requestWake()` on entering song view. `releaseWake()` only on leaving the app entirely — **not** between songs, so the screen stays on through the whole set. Re-acquired on `visibilitychange`.

**Dock layout (v2026.07.04.004):** the dock keeps only the between-songs-frequent controls with ≥2.6rem targets — prev/pos/next, play/pause (`scrollBtn`), speed −/+, and a `⚙` (`dockMore`) button. Transpose, `♯/♭`, font (`A−`/`fit`/`A+`) and `✎ Edit` live in `#dockSheet`, a `.modal.bottom` opened by `⚙`. **The controls kept their original ids**, so all handlers, boot wiring, and `openCurrent`'s set-nav hide still work after the DOM move — don't rename them. `openDockSheet()` hides `#editSong` when `stageMode` is on.

**Scroll progress bar (v2026.07.04.005):** `#scrollProg` (3px, `transform:scaleX`) sits at the top edge of the dock. `updateScrollProg()` is a closure with a passive rAF-throttled `scroll` listener on `#songView`; also called explicitly from `openCurrent`, `reRender`, and the font handlers (height changes that don't fire a scroll event). Hidden when `scrollHeight - clientHeight <= 4`.

**Stage-safe back (v2026.07.04.001):** the `#backBtn` handler, not `goBack` directly. When `screen==="song" && (scrolling || stageMode)`, the first tap arms `backArmed` + toasts "Tap again to leave"; a second tap within 1.5s calls `goBack()`. Reset on any successful leave.

**Played marks (v2026.07.04.010–011):** `playedSongs` is a `Set` of song ids for the *current* set. Auto-added in `openSongInSet`; long-press context menu toggles; `#resetPlayed` (visible only when any mark exists) clears the set's marks. Persisted per-setlist in localStorage key `"setlist69.played"` (`{setlistId:[songIds]}`) via `loadPlayed(setId)` / `savePlayed(setId)` — deliberately **not** in `state`, so backups never carry gig state. Styling: `.card.played` + `.wkd` pill using `--green`/`--green-dim` (swapped in light theme).

The dock is `position:fixed` to the viewport bottom. `#songView` has `padding-bottom:7.5rem` so the last lyric line clears it.

-----

## 10. Editor

**Fields:** Title, Artist/Note, Key, Capo (0–11 stepper), Body textarea.

**Capo stepper** (`capoEdUp`/`capoEdDown`): increments the `<span id="fCapo">` value (clamped 0–11). On save, `saveSong()` reads it as `parseInt(fCapo.textContent) || 0`.

**"Find chords" button (`findChordsBtn`):** opens `pasteModal` pre-filled with the song's title + artist as the search query.

**"Strip tab/performance notes" button (`stripNotesBtn`):** removes lines containing `:=` (E-Chords rhythm notation) and lines that are pure parentheticals `(...)` and are not chord lines. Collapses 3+ consecutive blank lines to 2. Conservative — doesn't try to detect all performance annotation formats.

-----

## 11. Theming & design tokens

CSS custom properties define both themes:

- `:root` = **dark** (near-black `--bg:#121110`, near-white `--ink`, gold `--chord:#ffc24d`).
- `[data-theme="light"]` = **light** (warm white bg, near-black ink, deep red-orange `--chord:#bd3c1c`).
- Toggle: `themeBtn` (☀/☾) → flips `state.theme`, `applyTheme()` sets `data-theme`. Persisted.

Contrast: lyrics ≈17:1 both modes; chords 11.7:1 dark / 5.2:1 light (≥ WCAG AA). Keep new colors above AA.

Fonts: `--display` Fraunces (titles), `--ui` Hanken Grotesk (UI + lyrics), `--mono` JetBrains Mono (chords/version).

**Capo badge** (`.capo-badge`): monospaced, amber border, shown beneath the key pill in the song view header when `capoVal > 0`.

-----

## 12. Function reference (quick map)

```
Storage:       idbOpen  idbGet  idbSet  persist  flushPersist  isValidState
Seed/init:     seed  boot  uid  newSongId  applyTheme  toast
Music core:    transposeNote  transposeChord  looksChord  isChordLine
               pitchClass  keyColor  cleanEmbeddedChords
Parse/render:  esc  parseSong  inlineToSegs  pairToSegs  renderLine  renderSheet  retuneSheet
Router/nav:    show  goBack
List renders:  renderSetlists  renderSetSongs  renderAllSongs  renderPicker  renderAdder
Song view:     openSongInSet  openSongStandalone  openCurrent  reRender
               nextSong  prevSong  startScroll  stopScroll  updateScrollProg
               requestWake  releaseWake  openDockSheet  closeDockSheet
Editor:        openEditor  closeEditor  saveSong
Context/dialogs: openSongContext  closeSongContext  openAdder  closeAdder  showPrompt  showConfirm
                 closeModal  loadPlayed  savePlayed
Backup/share:  saveJsonFile  exportData  shareSetlist  restoreData  mergeSetImport
Import:        parseImport  expandFiles  unzip  parseOpenSong
PWA:           showUpdateBanner  maybeShowUpdatePill  maybeShowInstallBanner  isStandalone  dismissInstall
```
Note: `maybeShowUpdatePill` kept its name but now surfaces the slide-down **update banner** + header ⟳ (not the old pill); `renderAllSongs` renders the song library *section of the home screen* (there is no separate All Songs screen).

All DOM event wiring is in one block near the bottom of the script (search `===== events =====`).

-----

## 13. Testing approach (do this before every ship)

No test framework — verification is manual:

1. **Syntax check:** `node --check setlist69.html` (Node tolerates the surrounding HTML surprisingly well, or extract the `<script>` body first).
2. **Logic check for music/parse changes:** write a small Node harness replicating the affected functions and assert against known cases. The harness can `eval` a function out of the HTML by regex-extracting it (see the `mergeSetImport` harness pattern). Historically useful cases: `G+2=A`, `Am7+3=Cm7`, `C/E+5=F/A`, `"New Or[Am]leans"` word stays glued, `Gm!` recognized as chord, `"Cm / Bb / Dm - D"` recognized as chord line, OnSong `Key:`/`Capo:` metadata extracted, Chordie `"Gmget"` cleaned, `mergeSetImport` dedupe (title+sub case-fold, in-payload repeats, `"a b"+"c"` vs `"a"+"b c"` non-collision).
3. **Duplicate-id / version-match:** CI (`.github/workflows/check.yml`) now enforces both, but you can run the same checks locally — extract markup before `<script>`, scan for repeated `id="..."`, and diff the `<small>` version against `sw.js` CACHE.
4. **Visual/touch behaviors** (swipe, stage mode, capo display, share sheet, dock ⚙ sheet, scroll progress bar, install banner, update pill) require a real device — flag for owner testing rather than claiming them verified.

-----

## 14. Roadmap & known gaps

**Parked (owner deprioritized; pick up on request):**

- Nashville number display.
- Chord diagrams / fingering charts.
- Setlist-level notes shown during performance.
- **Dedicated `banter` field per song** — stage patter/talk-up notes, distinct from `sub` (artist/note), shown directly under the title in the performance view alongside or instead of `sub`. Needs: a new `song.banter` field, an editor input, and a render line in `renderSheet()`/`svSub` area. Interim workaround in place: the "Doubloon Bayou Band" setlist (imported 2026.07.14) stores its banter text in each song's `sub` field, since `sub` already renders under the title (`svSub`) — expect to migrate those 36 songs to the real field once it exists.

**Explicitly out of scope (by design):** cloud sync and any built-in online song catalog. Moving songs between devices is handled by backup-to-file.

-----

## 15. Known limitations / gotchas

- **In-app preview** (Claude artifact viewer): storage, share sheet, and file pickers are sandboxed — test standalone.
- **Chords-above format** relies on column alignment; if source spacing is irregular, chord placement may drift. Inline `[C]` format is most robust.
- **Mid-word chords**: a chord change mid-word keeps the word whole (correct) but the pill sits over the second fragment — correct musically, occasionally looks tight visually.
- **Chordie auto-clean** is conservative: bare `A–G` at word-start are not converted (to avoid `"And"` → `"[A]nd"`). Unusual bare-note chords at word boundaries may need manual cleanup.
- **CORS** prevents any client-side fetch of lyrics or chords from external sites. The search-and-paste modal (manual copy) is the correct architecture — do not attempt a server proxy or API that would require serving user content.

-----

## 16. How to make a change (checklist)

1. Edit `setlist69.html` only (for app changes).
2. Bump the version `NNN` in the `<small>` brand tag in `setlist69.html`.
3. Add a changelog line in the top `<!-- ... -->` comment of `setlist69.html`.
4. Bump `CACHE` in `sw.js` to the same version string (`setlist69-vYYYY.MM.DD.NNN`).
5. `node --check` the script; logic-test music/parse core if touched.
6. If you changed storage shape, add a migration in `boot()`.
7. Flag anything needing real-device verification (touch, share, install) to the owner.

-----

## 17. License

**MIT** (see `LICENSE`). Chosen per the North Star's "ownership + shareable on your terms" —
it lets bandmates and anyone else use, fork, and self-host, requiring only attribution. The
copyright holder line is `cdburgess75`; swap it for a legal name if desired. This is the first
license the project has carried; before MIT it was all-rights-reserved by default.
