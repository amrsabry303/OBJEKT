// Joins the A3 SVG sheets of one product into one PDF. Usage: NODE_PATH=<playwright> node make_pdf.js <product dir> <product number> <rev>
const fs = require('fs'); const { chromium } = require('playwright');
(async () => {
  const [dir, pn, rev] = process.argv.slice(2);
  const sheets = fs.readdirSync(dir).filter(f => f.startsWith(`${pn}_rev${rev}_sheet`) && f.endsWith('.svg')).sort();
  const html = '<!doctype html><meta charset="utf-8"><style>@page{size:420mm 297mm;margin:0}body{margin:0}svg{display:block;page-break-after:always}</style>' + sheets.map(f => fs.readFileSync(`${dir}/${f}`, 'utf8')).join('');
  const b = await chromium.launch(); const p = await b.newPage(); await p.setContent(html);
  await p.pdf({ path: `${dir}/${pn}_rev${rev}_drawings.pdf`, preferCSSPageSize: true, printBackground: true });
  await b.close(); console.log('pages', sheets.length);
})();
