const fs=require('fs');const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for(let n=1;n<=11;n++){const id=String(n).padStart(2,'0');const svg=fs.readFileSync(`tex/tex_${id}.svg`,'utf8');
const [w,h]=[+svg.match(/width="(\d+)"/)[1],+svg.match(/height="(\d+)"/)[1]];
const p=await b.newPage({viewport:{width:w,height:h}});await p.goto('file://'+process.cwd()+`/tex/tex_${id}.svg`);await p.screenshot({path:`tex/tex_${id}.png`});await p.close();}
await b.close();})()
