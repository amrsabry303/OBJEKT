// Renders every print SVG to a PDF of exactly the page size. Usage: NODE_PATH=<playwright> node make_print_pdf.js <repo root>
const fs = require('fs'), path = require('path'); const { chromium } = require('playwright');
(async () => {
  const root = process.argv[2]; const b = await chromium.launch(); let n = 0;
  for (const z of ['S','M','L']) {
    const dir = `${root}/plan/faux-books/print/${z}/svg`; if (!fs.existsSync(dir)) continue;
    for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.svg'))) {
      const svg = fs.readFileSync(`${dir}/${f}`, 'utf8'); const w = svg.match(/width="([\d.]+)mm"/)[1], h = svg.match(/height="([\d.]+)mm"/)[1];
      const p = await b.newPage(); await p.goto('file://' + `${dir}/${f}`); await p.waitForTimeout(300);
      await p.pdf({ path: `${root}/plan/faux-books/print/${z}/${f.replace('.svg','.pdf')}`, width: `${w}mm`, height: `${h}mm`, printBackground: true, margin: {top:0,right:0,bottom:0,left:0}, pageRanges: '1' });
      await p.close(); n++;
    }
  }
  await b.close(); console.log('pdfs', n);
})();
