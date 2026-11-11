const fs=require('fs');const {chromium}=require('playwright');
const cfgs=JSON.parse(process.argv[2]);
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1600,height:2000}});p.on('console',m=>console.log('console:',m.text()));p.on('pageerror',e=>console.log('err:',e.message));
await p.goto('http://localhost:8765/scene.html');await p.waitForFunction('window.ready===true',{timeout:60000});
for(const c of cfgs){const url=await p.evaluate(cfg=>window.renderScene(cfg),c);fs.writeFileSync('out/'+c.name+'.png',Buffer.from(url.split(',')[1],'base64'));console.log('wrote',c.name);}
await b.close();})()
