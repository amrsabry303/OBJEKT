// Usage: FONT_DIR=/path/with/jost-*.woff2 node build.mjs   (Inter is read from the system)
import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_PATH || 'playwright'); import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';
const here = path.dirname(fileURLToPath(import.meta.url)), brand = path.join(here, '../../brand');
const fonts = process.env.FONT_DIR;
const b64 = (s, t) => `data:${t};base64,` + Buffer.from(s).toString('base64');
const sym = fs.readFileSync(path.join(brand, 'objekt-symbol.svg'), 'utf8').replace(/#263A5A/gi, '#E2D9CF');
const logo = fs.readFileSync(path.join(brand, 'objekt-logo.svg'), 'utf8');
let html = fs.readFileSync(path.join(here, 'posts.html'), 'utf8').replace('SYM_SAND', b64(sym, 'image/svg+xml')).replace(/LOGO_NAVY/g, b64(logo, 'image/svg+xml'));
const ff = [300, 400, 500].map(w => `@font-face{font-family:Jost;font-weight:${w};src:url(file://${fonts}/jost-${w}.woff2)}`).join('');
html = html.replace('<style>', `<style>${ff}`);
const tmp = path.join(fonts, 'posts.built.html'); fs.writeFileSync(tmp, html);
const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
await pg.goto('file://' + tmp); await pg.evaluate(() => document.fonts.ready);
for (const [i, n] of [[1, 'statement'], [2, 'position'], [3, 'range']])
  await pg.locator('#p' + i).screenshot({ path: path.join(here, `objekt_post-0${i}_${n}_draft.png`) });
await br.close();
