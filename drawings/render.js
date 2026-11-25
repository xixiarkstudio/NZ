// Render every SVG in this folder to a PNG of the same name.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const dir = __dirname;
  const scale = Number(process.argv[2] || 2);
  const browser = await chromium.launch();
  for (const f of fs.readdirSync(dir).filter((n) => n.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    const m = svg.match(/width="(\d+)" height="(\d+)"/);
    const page = await browser.newPage({
      viewport: { width: Number(m[1]), height: Number(m[2]) },
      deviceScaleFactor: scale,
    });
    await page.setContent(`<body style="margin:0">${svg}</body>`);
    await page.screenshot({ path: path.join(dir, f.replace('.svg', '.png')) });
    await page.close();
    console.log('rendered', f);
  }
  await browser.close();
})();
