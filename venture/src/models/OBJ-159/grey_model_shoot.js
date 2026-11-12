const {chromium}=require('/opt/node-tools/node_modules/playwright'); const fs=require('fs'); const out=process.argv[2], REV=process.argv[3]||'rev6';
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});const p=await b.newPage();
p.on('pageerror',e=>console.log('err',e.message));
await p.goto('http://localhost:8765/scene.html'); await p.waitForFunction('window.ready',null,{timeout:60000});
const IN=25.4, OH=74*IN, OW=34*IN, cx=OW/2, cy=OH/2;
const zs2=(OH-25-(OH-25-125)/5*2)-1.25*IN;       // underside of shelf 3 (index 2)
const V={ front:[1400,2000,-2300,[cx,cy,12500],[cx,cy,0]],
 side:[1000,2000,-2300,[12500,cy,0],[0,cy,0]],
 threeq:[1500,2000,14,[cx+6400,cy+800,8800],[cx,cy,0]],
 threeq_back:[1500,2000,14,[cx-6400,cy+800,8800],[cx,cy,0]],
 floor_edge:[1500,1100,20,[700,260,1300],[40,40,60]],
 screws:[1500,1100,22,[-1100,zs2+80,1100],[0,zs2-20,40]],
 shelf_end:[1500,1100,22,[700,zs2+160,1150],[60,zs2-10,40]],
 cutout:[1500,1100,22,[cx+1700,1350,2100],[cx,1100,0]]};
for(const [n,[w,h,f,pos,t]] of Object.entries(V)){const d=await p.evaluate(a=>window.shot(...a),[w,h,f,pos,t]);fs.writeFileSync(`${out}/OBJ-159_grey-model_${n}_${REV}-shape-to-confirm.png`,Buffer.from(d.split(',')[1],'base64'));console.log(n)}
await b.close()})();
