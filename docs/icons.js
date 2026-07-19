// Regenerates the app icons (icons/*.png): a grand staff (treble + bass clef on a
// braced two-staff system with a red "now playing" note) inside a glowing amber card,
// on black — the SetList69 x PileUp look.
//
// The clefs are the real Bravura engraving glyphs (SMuFL U+E050 gClef / U+E062 fClef).
// Bravura is SIL OFL 1.1 (© Steinberg Media Technologies GmbH, Reserved Font Name
// "Bravura"). It is used ONLY at build time to rasterize these PNGs — no font ships in
// the app, and musical clefs as symbols aren't copyrightable. Only the PNGs are committed.
//
// The font is not vendored here. To regenerate, fetch Bravura once (it is bundled, OFL,
// inside the `vexflow` npm package as a base64 woff2) and point BRAVURA at it:
//   npm install vexflow
//   node -e "const s=require('fs').readFileSync('node_modules/vexflow/build/esm/src/fonts/bravura.js','utf8');\
//     require('fs').writeFileSync('docs/bravura.woff2',Buffer.from(s.match(/base64,([A-Za-z0-9+/=]+)/)[1],'base64'))"
//   NODE_PATH=/opt/node22/lib/node_modules node docs/icons.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BRAVURA = process.env.BRAVURA || path.resolve(__dirname, 'bravura.woff2');
if (!fs.existsSync(BRAVURA)) {
  console.error('Bravura font not found at', BRAVURA, '\nSee the header of this file for the one-time fetch step.');
  process.exit(1);
}
const FONT = 'data:font/woff2;base64,' + fs.readFileSync(BRAVURA).toString('base64');
const ICONS = path.resolve(__dirname, '..', 'icons');
const TREBLE = '\uE050', BASS = '\uE062';   // SMuFL gClef / fClef

// mask=true pulls the card inward so it survives Android's circular maskable crop.
function scene({ mask }) {
  const inset = mask ? 46 : 0;
  const cx0 = 70 + inset, cy0 = 74 + inset, cw = 372 - 2 * inset, ch = 364 - 2 * inset;
  const sp = 26, x1 = 132 + inset * 0.5, x2 = 380 - inset * 0.5, tTop = 140 + inset * 0.55, bTop = 300 - inset * 0.15;
  const line = y => `<line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" stroke="#6b5836" stroke-width="4"/>`;
  const staff = y0 => [0, 1, 2, 3, 4].map(i => line(y0 + i * sp)).join('');
  const bY0 = tTop, bY1 = bTop + 4 * sp, bx = 118 + inset * 0.5;
  const brace = `<path d="M${bx} ${bY0} C${bx-20} ${bY0+52} ${bx-20} ${(bY0+bY1)/2-6} ${bx-6} ${(bY0+bY1)/2}
                 C${bx-20} ${(bY0+bY1)/2+6} ${bx-20} ${bY1-52} ${bx} ${bY1}" fill="none" stroke="#f0923c" stroke-width="8" stroke-linecap="round"/>`;
  const card = `<rect x="${cx0}" y="${cy0}" width="${cw}" height="${ch}" rx="34" fill="none" stroke="#f0923c" stroke-width="7" opacity="0.92" filter="url(#gl)"/>`;
  const nx = mask ? 300 : 312;
  const note = `<circle cx="${nx}" cy="${tTop + 2*sp}" r="15" fill="#e8635a"/><line x1="${nx+14}" y1="${tTop + 2*sp}" x2="${nx+14}" y2="${tTop - sp}" stroke="#e8635a" stroke-width="6" stroke-linecap="round"/>`;
  const g = (ch2, cx, cy, h) => `<g class="ph" data-cx="${cx}" data-cy="${cy}" data-h="${h}"><text font-family="Bravura" font-size="300" fill="#f0923c" filter="url(#gl)">${ch2}</text></g>`;
  const k = mask ? 0.86 : 1;
  return card + staff(tTop) + staff(bTop) + brace
    + g(TREBLE, 176 + inset * 0.5, tTop + 2 * sp, 208 * k)
    + g(BASS, 174 + inset * 0.5, bTop + 1.35 * sp, 104 * k)
    + note;
}

const VARIANTS = [
  { file: 'icon-512.png', size: 512, mask: false },
  { file: 'icon-192.png', size: 192, mask: false },
  { file: 'apple-touch-icon.png', size: 180, mask: false },
  { file: 'icon-512-maskable.png', size: 512, mask: true },
];

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const v of VARIANTS) {
    const ctx = await browser.newContext({ viewport: { width: v.size, height: v.size }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    const html = `<!doctype html><html><head><style>
      @font-face{font-family:'Bravura';src:url('${FONT}') format('woff2');}
      *{margin:0;padding:0}html,body{width:${v.size}px;height:${v.size}px;overflow:hidden;background:#000}
    </style></head><body>
      <svg width="${v.size}" height="${v.size}" viewBox="0 0 512 512">
        <defs><radialGradient id="bg" cx="50%" cy="42%" r="75%"><stop offset="0%" stop-color="#111015"/><stop offset="100%" stop-color="#000"/></radialGradient>
        <filter id="gl" x="-60%" y="-60%" width="220%" height="220%"><feDropShadow dx="0" dy="0" stdDeviation="10" flood-color="#f0923c" flood-opacity="0.75"/></filter></defs>
        <rect width="512" height="512" fill="url(#bg)"/>${scene(v)}
      </svg></body></html>`;
    await page.setContent(html, { waitUntil: 'load' });
    await page.evaluate(async () => { await document.fonts.ready; });
    await page.waitForTimeout(250);
    // Center + scale each Bravura glyph by its measured bounding box.
    await page.evaluate(() => {
      document.querySelectorAll('g.ph').forEach(g => {
        const t = g.querySelector('text'); const bb = t.getBBox();
        const cx = +g.dataset.cx, cy = +g.dataset.cy, h = +g.dataset.h; const s = h / bb.height;
        g.setAttribute('transform', `translate(${cx - s * (bb.x + bb.width / 2)} ${cy - s * (bb.y + bb.height / 2)}) scale(${s})`);
      });
    });
    await page.waitForTimeout(120);
    await page.screenshot({ path: path.join(ICONS, v.file), clip: { x: 0, y: 0, width: v.size, height: v.size } });
    console.log('wrote', v.file, `(${v.size}px${v.mask ? ', maskable' : ''})`);
    await ctx.close();
  }
  await browser.close();
  console.log('icons written to', ICONS);
})();
