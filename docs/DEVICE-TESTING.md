# Device test pass — v2026.07.04.011

A ~10-minute ordered checklist covering everything shipped in the v2026.07.04.x
batch that can only be verified on a real phone. Run top to bottom; each step
lists the expected result. Anything that doesn't match: note the step number.

> App: https://cdburgess75.github.io/SetList69/

---

## 1 · Update & install

| # | Do | Expect |
|---|----|--------|
| 1.1 | Open the installed app (or the site in Safari) and wait a few seconds on the home screen | If you were on an old version: **"⟳ Update ready — tap to refresh"** pill appears bottom-center. Tap it → app reloads, version tag under the logo reads **v2026.07.04.011** |
| 1.2 | Remove the app from your home screen, re-add via Share → Add to Home Screen | New **S69 icon**: dark tile, setlist rows with glowing gold row, "S69" wordmark upper-left |
| 1.3 | Open the site in a plain browser tab (not the installed app) | One-time **install banner** at the top of the home screen. Dismiss with ✕ → it stays gone, even after reload |

## 2 · Played tracking (new)

| # | Do | Expect |
|---|----|--------|
| 2.1 | Open a setlist, tap the first song, then go back | Song row is **dimmed** with a **green strikethrough** and a **✓ PLAYED** pill; **↺ Reset played** appears in the toolbar |
| 2.2 | Play through another song via swipe/next, go back | It's marked too; marks accumulate |
| 2.3 | **Kill the app completely** (swipe away), reopen, enter the same set | Marks are **still there** (this is the .011 persistence) |
| 2.4 | Long-press an unplayed song → "Mark as played"; long-press again → "Mark unplayed" | Toggles both ways |
| 2.5 | Tap **↺ Reset played** | All marks clear; button hides itself |

## 3 · Performance dock & song view

| # | Do | Expect |
|---|----|--------|
| 3.1 | Open a song from a set | Dock shows only: ◀ 1/3 ▶ · play · − 3 + · ⚙ — targets big enough to hit without looking |
| 3.2 | Tap ⚙ | Sheet slides up with transpose, ♯/♭, font A−/fit/A+, ✎ Edit. Transpose/font changes render live behind the sheet |
| 3.3 | Tap **fit** on a long song | Whole song fits the screen, no horizontal scroll |
| 3.4 | Start auto-scroll | Thin **gold progress bar** along the dock's top edge tracks position; at the bottom: haptic buzz + play button flashes |
| 3.5 | While auto-scrolling, tap **‹ Back** once | Toast: **"Tap again to leave"** — app stays on the song. Second tap within 1.5s leaves |
| 3.6 | Swipe left/right on the lyrics | Next/previous song; screen never sleeps mid-set |

## 4 · Stage mode

| # | Do | Expect |
|---|----|--------|
| 4.1 | In a set, tap **▶ Stage** | Drag handles, ✕ remove, add-song, play FAB, set-key control all hide; cards get bigger |
| 4.2 | Open a song in stage mode, tap ⚙ | **✎ Edit is hidden** in the sheet |
| 4.3 | In stage mode, tap ‹ Back once from a song (not scrolling) | Still guarded: "Tap again to leave" |

## 5 · Share & backup

| # | Do | Expect |
|---|----|--------|
| 5.1 | Setlist ✎ settings → **⇪ Share** | iOS share sheet opens with a `.json` file — AirDrop/Files/Messages all work |
| 5.2 | Import that file on another device (or after Reset): Tools ≡ → Restore | Dialog says **"Add setlist … with N songs?"** — it **merges**, existing songs aren't duplicated, your library is untouched |
| 5.3 | Tools ≡ → **Back up all data** | Share sheet with `setlist69-backup-YYYY-MM-DD.json` |

## 6 · Both themes

| # | Do | Expect |
|---|----|--------|
| 6.1 | Toggle ☾/☀ and repeat 2.1 | Played styling reads clearly in **light** theme too (darker green strike on light bg) |

---

**Reporting back:** just list the step numbers that failed or felt wrong
("3.2 sheet covers too much", "2.3 marks gone"). One line each is plenty.
