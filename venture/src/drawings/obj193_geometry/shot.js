const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});const p=await b.newPage({viewport:{width:1600,height:1200}});
p.on('console',m=>console.log('console',m.text()));p.on('pageerror',e=>console.log('err',e.message));
await p.goto('file://'+process.argv[2]+'/scene.html');await p.waitForFunction(()=>document.title==='done',null,{timeout:30000});
await p.locator('#c').screenshot({path:process.argv[2]+'/geo.png'});await b.close();console.log('ok')})();
