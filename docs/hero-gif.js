/*
 * Regenerates the animated hero image used at the top of README.md.
 *
 * Dev-only tooling — nothing here ships to the browser. It needs Playwright and
 * two pure-JS encoders that are NOT dependencies of the app:
 *
 *     npm install playwright gifenc pngjs
 *     node docs/hero-gif.js
 *
 * Output: docs/screenshots/demo.gif
 *
 * The sequence is a scripted run through the real app on seed data — home, into
 * a set, into a song, auto-scroll running, then a chord tapped for its fingering.
 * Holds are single frames with a long delay rather than repeated frames, and every
 * frame after the first is diffed against its predecessor so unchanged pixels are
 * written as transparent. Both keep the file small.
 *
 * The seed songs all fit the viewport whole, so auto-scroll would have nothing to
 * scroll and every motion frame would come out identical. The capture therefore
 * builds its own tall fixture by repeating a seed song's verses — in page memory
 * only, never persisted and never shipped.
 */
const { chromium } = require('playwright');
const { GIFEncoder, quantize, applyPalette } = require('gifenc');
const { PNG } = require('pngjs');
const fs = require('fs');
const path = require('path');

const OUT = path.resolve(__dirname, 'screenshots', 'demo.gif');
const APP = 'file://' + path.resolve(__dirname, '..', 'setlist69.html');

const VP = { width: 360, height: 740 };
const SCROLL_FRAMES = 18;   // frames of auto-scroll motion
const FRAME_MS = 110;       // delay on each motion frame
const COLORS = 200;         // global palette size; index COLORS is transparent

const frames = [];          // { buf: PNG buffer, delay: ms }
const shoot = async (page, delay) => frames.push({ buf: await page.screenshot(), delay });

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await browser.newContext({ viewport: VP, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  await page.goto(APP);
  await page.waitForTimeout(500);

  // 1. Home — setlists and the song library.
  await shoot(page, 1200);

  // 2. Into the set holding the longest song, so step 4 has something to scroll.
  //    No shipped song is long enough on its own (the demo showcase song was retired), so the
  //    capture builds its own fixture by repeating a seed song's verses. Capture-only — it lives
  //    in the page's memory for the length of this run and is never persisted.
  const target = await page.evaluate(() => {
    const seed = [...state.songs].sort((a, b) => b.body.length - a.body.length)[0];
    const demo = { id: '__demo', title: seed.title, sub: seed.sub, key: seed.key,
                   banter: 'Hold the last line — let it ring.',
                   body: [seed.body, seed.body, seed.body].join('\n\n') };
    state.songs.push(demo);
    state.setlists[0].songIds.push('__demo');
    const song = demo;
    const set = state.setlists.find(s => s.songIds.includes(song.id));
    if (!set) return null;
    curSetlist = set.id;
    renderSetSongs();
    show('setSongs');
    return { index: set.songIds.indexOf(song.id), title: song.title, set: set.name };
  });
  if (!target) throw new Error('no setlist contains the longest song');
  console.log(`sequence: ${target.set} → ${target.title}`);
  await page.waitForTimeout(350);
  await shoot(page, 950);

  // 3. Open it.
  await page.evaluate(i => openSongInSet(i), target.index);
  await page.waitForTimeout(400);
  await shoot(page, 950);

  // 4. Auto-scroll, captured while it actually runs.
  const runway = await page.evaluate(() => {
    const v = document.getElementById('songView');
    return v.scrollHeight - v.clientHeight;
  });
  if (runway < 120) throw new Error(`only ${runway}px of scroll runway — motion frames would be identical`);
  await page.evaluate(() => { scrollSpeed = 8; startScroll(); });
  for (let i = 0; i < SCROLL_FRAMES; i++) {
    await page.waitForTimeout(FRAME_MS);
    await shoot(page, FRAME_MS);
  }
  await page.evaluate(() => stopScroll());
  await page.waitForTimeout(150);

  // 5. Tap a chord — fingering diagram.
  await page.evaluate(() => {
    const pills = [...document.querySelectorAll('#sheet .chordpill')];
    const view = document.getElementById('songView');
    // pick a pill comfortably inside the viewport so the popover isn't clipped
    const pill = pills.find(p => {
      const r = p.getBoundingClientRect();
      return r.top > view.clientHeight * 0.25 && r.top < view.clientHeight * 0.55;
    }) || pills[0];
    if (pill) showChordPop(pill);
  });
  await page.waitForTimeout(350);
  await shoot(page, 2000);

  await browser.close();

  // ---- encode -------------------------------------------------------------
  const rgba = frames.map(f => PNG.sync.read(f.buf).data);
  const { width, height } = PNG.sync.read(frames[0].buf);
  const px = width * height;

  // One global palette, sampled across the whole run so colours stay stable.
  const step = 3;
  const sample = new Uint8Array(Math.ceil((px * frames.length) / step) * 4);
  let s = 0;
  for (const data of rgba) {
    for (let i = 0; i < px; i += step, s += 4) {
      sample[s] = data[i * 4]; sample[s + 1] = data[i * 4 + 1];
      sample[s + 2] = data[i * 4 + 2]; sample[s + 3] = 255;
    }
  }
  const palette = quantize(sample.subarray(0, s), COLORS);

  // Every frame is written whole. Inter-frame differencing (unchanged pixels ->
  // a transparent index, dispose:1) was tried and abandoned: the theme background
  // is pure black, so any reserved dark slot got aliased onto by real background
  // pixels and earlier frames bled through. At this size it isn't worth the risk.
  const gif = GIFEncoder();
  frames.forEach((f, n) => {
    gif.writeFrame(applyPalette(rgba[n], palette), width, height, {
      palette,
      first: n === 0,
      delay: f.delay,
      repeat: 0,
    });
  });
  gif.finish();

  fs.writeFileSync(OUT, Buffer.from(gif.bytes()));
  const kb = (fs.statSync(OUT).size / 1024).toFixed(0);
  console.log(`wrote ${OUT} — ${frames.length} frames, ${width}x${height}, ${kb} KB`);
})();
