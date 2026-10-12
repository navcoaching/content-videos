const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.goto('file://'+__dirname+'/post.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(600);
await p.locator('#s1').screenshot({path:__dirname+'/scary.png'});await b.close();})();
