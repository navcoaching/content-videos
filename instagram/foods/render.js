const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.goto('file://'+__dirname+'/slides.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
fs.mkdirSync(__dirname+'/out',{recursive:true});const n=await p.locator('section.s').count();
for(let i=0;i<n;i++) await p.locator('section.s').nth(i).screenshot({path:`${__dirname}/out/${String(i+1).padStart(2,'0')}.png`});
await b.close();console.log(n)})();
