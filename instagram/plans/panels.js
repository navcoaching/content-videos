// node panels.js  -> re-shoots the PDF info panels used by the carousels at their natural height
// (the PDF stretches them to fill the page; for posts that leaves dead gaps and clips the flow boxes)
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const HERE=__dirname, PDF=path.join(HERE,'../../pdf');
const PANELS=JSON.parse(fs.readFileSync(HERE+'/panels.json'));
const CSS=`.portrait .ip .panel{flex:none!important}
.portrait .ip .pbody{position:static!important;justify-content:flex-start!important;gap:22px}
.portrait .ip .fs b{white-space:normal}`;
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
for(const [k,list] of Object.entries(PANELS)){
 const src=`${PDF}/prog-${k}-portrait.html`;
 for(const p of list){ if(!p.sub) continue;
  const pg=await b.newPage({viewport:{width:1080,height:2520}});
  await pg.goto('file://'+src);await pg.addStyleTag({content:CSS});await pg.evaluate(()=>document.fonts.ready);await pg.waitForTimeout(500);
  const idx=await pg.evaluate(sub=>{const n=s=>s.replace(/\s+/g,'');return [...document.querySelectorAll('.panel')].findIndex(e=>{const h=e.querySelector('.ph');return h&&n(h.textContent)===n(sub)})},p.sub);
  if(idx<0){console.log('MISSING',k,p.sub);await pg.close();continue}
  const w=await pg.evaluate(i=>document.querySelectorAll('.panel')[i].getBoundingClientRect().width,idx);
  await pg.close();
  const pg2=await b.newPage({viewport:{width:1080,height:2520},deviceScaleFactor:1230/w});
  await pg2.goto('file://'+src);await pg2.addStyleTag({content:CSS});await pg2.evaluate(()=>document.fonts.ready);await pg2.waitForTimeout(500);
  await pg2.locator('.panel').nth(idx).screenshot({path:p.f});await pg2.close();
  console.log('ok',k,path.basename(p.f));
 }}
await b.close();})();
