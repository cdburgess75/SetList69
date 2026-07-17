// Regenerates the app icons (icons/*.png) in the amber-on-black "PileUp" style:
// three setlist rows with a glowing "now playing" row + an S69 monospace wordmark.
// Renders vector SVG through headless Chromium using the app's own JetBrains Mono.
// Run: NODE_PATH=/opt/node22/lib/node_modules node docs/icons.js
const { chromium } = require('playwright');
const path = require('path');

const FONT = 'file://' + path.resolve(__dirname, '..', 'fonts', 'jetbrains-mono-latin.woff2');
const ICONS = path.resolve(__dirname, '..', 'icons');

// Fixed 0 0 512 512 viewBox; width/height set the output size so it scales crisply.
function svg({ size, wordmark, mask }) {
  const rowW = 300, rowH = 62, rowX = 106, rad = 18, gap = 30;
  const blockH = rowH * 3 + gap * 2;
  const startY = mask ? (256 - blockH / 2) : 176;   // maskable: center inside the safe zone
  const ys = [0, 1, 2].map(i => startY + i * (rowH + gap));
  const active = 1;                                  // middle row is "now playing"

  const inactiveRow = (y) => `
    <rect x="${rowX}" y="${y}" width="${rowW}" height="${rowH}" rx="${rad}" fill="#181818" stroke="#282828" stroke-width="1.5"/>
    <circle cx="${rowX + 30}" cy="${y + rowH / 2}" r="11" fill="#3a3a3a"/>
    <rect x="${rowX + 52}" y="${y + rowH / 2 - 6}" width="150" height="12" rx="6" fill="#333"/>`;

  const activeRow = (y) => `
    <rect x="${rowX}" y="${y}" width="${rowW}" height="${rowH}" rx="${rad}" fill="#f0923c" filter="url(#glow)"/>
    <circle cx="${rowX + 30}" cy="${y + rowH / 2}" r="11" fill="#e8635a"/>
    <rect x="${rowX + 52}" y="${y + rowH / 2 - 6}" width="176" height="12" rx="6" fill="#1c1205" opacity="0.85"/>`;

  const rows = ys.map((y, i) => i === active ? activeRow(y) : inactiveRow(y)).join('');
  const mark = wordmark ? `
    <text x="52" y="118" font-family="'JetBrains Mono', monospace" font-weight="700"
      font-size="86" letter-spacing="2" fill="#f0923c" filter="url(#textglow)">S69</text>` : '';

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 512 512">
    <defs>
      <radialGradient id="bg" cx="50%" cy="42%" r="75%">
        <stop offset="0%" stop-color="#111015"/><stop offset="100%" stop-color="#000000"/>
      </radialGradient>
      <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
        <feDropShadow dx="0" dy="0" stdDeviation="13" flood-color="#f0923c" flood-opacity="0.85"/>
      </filter>
      <filter id="textglow" x="-40%" y="-40%" width="180%" height="180%">
        <feDropShadow dx="0" dy="0" stdDeviation="8" flood-color="#f0923c" flood-opacity="0.55"/>
      </filter>
    </defs>
    <rect width="512" height="512" fill="url(#bg)"/>
    ${mark}
    ${rows}
  </svg>`;
}

const VARIANTS = [
  { file: 'icon-512.png', size: 512, wordmark: true, mask: false },
  { file: 'icon-192.png', size: 192, wordmark: true, mask: false },
  { file: 'apple-touch-icon.png', size: 180, wordmark: true, mask: false },
  { file: 'icon-512-maskable.png', size: 512, wordmark: false, mask: true },
];

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  for (const v of VARIANTS) {
    const ctx = await browser.newContext({ viewport: { width: v.size, height: v.size }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    const html = `<!doctype html><html><head><style>
      @font-face{font-family:'JetBrains Mono';src:url('${FONT}') format('woff2');font-weight:700;}
      *{margin:0;padding:0}html,body{width:${v.size}px;height:${v.size}px;overflow:hidden;background:#000}
    </style></head><body>${svg(v)}</body></html>`;
    await page.setContent(html, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(ICONS, v.file), clip: { x: 0, y: 0, width: v.size, height: v.size } });
    console.log('wrote', v.file, `(${v.size}px)`);
    await ctx.close();
  }
  await browser.close();
  console.log('icons written to', ICONS);
})();
