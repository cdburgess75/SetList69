const { chromium } = require('playwright');
const path = require('path');
const OUT = path.resolve(__dirname, 'screenshots');
const APP = 'file://' + path.resolve(__dirname, '..', 'setlist69.html');

const VP = { width: 400, height: 840 };

async function fresh(browser) {
  const ctx = await browser.newContext({ viewport: VP, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.goto(APP);
  await page.waitForTimeout(400);
  return { ctx, page };
}

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

  // 1. Home — setlists + song library
  {
    const { ctx, page } = await fresh(browser);
    await page.screenshot({ path: path.join(OUT, 'home.png') });
    await ctx.close();
  }

  // 2. Performance view — chords above lyrics (dark)
  {
    const { ctx, page } = await fresh(browser);
    await page.evaluate(() => {
      curSetlist = state.setlists[0].id;   // Front Porch
      renderSetSongs();
      openSongInSet(0);                    // House of the Rising Sun
    });
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, 'song.png') });
    await ctx.close();
  }

  // 3. Set view with "played" marks
  {
    const { ctx, page } = await fresh(browser);
    await page.evaluate(() => {
      curSetlist = state.setlists[0].id;
      const sl = state.setlists.find(s => s.id === curSetlist);
      playedSongs.add(sl.songIds[0]);
      playedSongs.add(sl.songIds[1]);
      renderSetSongs();
      show('setSongs');
    });
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, 'played.png') });
    await ctx.close();
  }

  // 4. Performance view — light theme
  {
    const { ctx, page } = await fresh(browser);
    await page.evaluate(() => {
      state.theme = 'light'; applyTheme();
      curSetlist = state.setlists[0].id;
      renderSetSongs();
      openSongInSet(2);                    // Scarborough Fair
    });
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, 'song-light.png') });
    await ctx.close();
  }

  // 5. Chord fingering diagram — tap a chord pill in the performance view
  {
    const { ctx, page } = await fresh(browser);
    await page.evaluate(() => {
      curSetlist = state.setlists[0].id;
      renderSetSongs();
      openSongInSet(0);                    // House of the Rising Sun
    });
    await page.waitForTimeout(300);
    await page.evaluate(() => {
      const pill = document.querySelector('#sheet .chordpill');
      if (pill) showChordPop(pill);
    });
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, 'chord-diagram.png') });
    await ctx.close();
  }

  // 6. Editor — how a song is stored (chords + lyrics)
  {
    const { ctx, page } = await fresh(browser);
    await page.evaluate(() => {
      const s = state.songs.find(x => /Rising Sun/.test(x.title)) || state.songs[0];
      openEditor(s.id);
    });
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, 'editor.png') });
    await ctx.close();
  }

  // 7. Two-column sheet — iPad landscape (columns engage automatically on wide screens)
  {
    const ctx = await browser.newContext({ viewport: { width: 1024, height: 768 }, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    await page.goto(APP);
    await page.waitForTimeout(400);
    await page.evaluate(() => openSongStandalone('danny'));
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, 'twocol.png') });
    await ctx.close();
  }

  await browser.close();
  console.log('screenshots written to', OUT);
})();
