const {chromium}=require('/opt/node-tools/node_modules/playwright'); const fs=require('fs'); const out=process.argv[2];
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});const p=await b.newPage();
p.on('console',m=>console.log('console',m.text())); p.on('pageerror',e=>console.log('err',e.message));
await p.goto('http://localhost:8765/scene.html'); await p.waitForFunction('window.ready',null,{timeout:60000});
const cx=400,cy=1075;
const V={ front:[1400,2000,-2500,[cx,cy,12500],[cx,cy,0]],
 side:[1000,2000,-2500,[12500,cy,0],[0,cy,0]],
 threeq:[1500,2000,14,[cx+6800,cy+900,9400],[cx,cy,0]],
 threeq_back:[1500,2000,14,[cx-6800,cy+900,9400],[cx,cy,0]],
 foot:[1500,1100,20,[620,330,1300],[40,70,60]],
 fixing:[1500,1100,22,[-1000,1560,1350],[0,1420,40]],
 cutout:[1500,1100,22,[cx+1700,1350,2100],[400,1100,0]]};
for(const [n,[w,h,f,pos,t]] of Object.entries(V)){const d=await p.evaluate(a=>window.shot(...a),[w,h,f,pos,t]);fs.writeFileSync(`${out}/OBJ-159_grey-model_${n}_rev3-shape-to-confirm.png`,Buffer.from(d.split(',')[1],'base64'));console.log(n)}
await b.close()})();
