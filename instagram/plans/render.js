// node render.js <plan>  -> renders slides to PNG; for video slides also fg (alpha) + rects json
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const k=process.argv[2];const dir=__dirname+'/'+k;
const spec=JSON.parse(fs.readFileSync(dir+'/slides.json'));
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.goto('file://'+dir+'/slides.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
fs.mkdirSync(dir+'/out',{recursive:true});
for(const s of spec){const n=s.id.slice(1).padStart(2,'0');
 await p.locator('#'+s.id).screenshot({path:`${dir}/out/${n}.png`});
 if(s.video){
  const rects=await p.evaluate(id=>{const sec=document.getElementById(id);const o=sec.getBoundingClientRect();
    return [...sec.querySelectorAll('.vid.live')].map(e=>{const r=e.getBoundingClientRect();return {x:Math.round(r.left-o.left),y:Math.round(r.top-o.top),w:Math.round(r.width),h:Math.round(r.height),clip:e.dataset.clip,ss:+e.dataset.ss,crop:e.dataset.crop}})},s.id);
  fs.writeFileSync(`${dir}/out/${n}-rects.json`,JSON.stringify(rects));
  const st=await p.addStyleTag({content:`#${s.id},#${s.id} *{visibility:hidden} #${s.id}{visibility:visible!important;background:#000!important} #${s.id}::before{display:none} #${s.id} .vid.live{visibility:visible!important;background:#fff!important;border-color:#fff!important} #${s.id} .vid.live *{visibility:hidden!important} #${s.id} .vid.live .no,#${s.id} .vid.live .vnote{visibility:visible!important;background:#000!important;color:#000!important}`});
  await p.locator('#'+s.id).screenshot({path:`${dir}/out/${n}-mask.png`});
  await st.evaluate(e=>e.remove());
 }}
await b.close();})();
