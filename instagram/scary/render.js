// node render.js -> scary.png (final frame) + scary.mp4 (6.5 s reel, 30 fps)
const {chromium}=require('playwright');const fs=require('fs');const {execSync}=require('child_process');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.goto('file://'+__dirname+'/post.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(600);
await p.locator('#s1').screenshot({path:__dirname+'/scary.png'});
const dir='/tmp/claude-0/scary-frames';fs.rmSync(dir,{recursive:true,force:true});fs.mkdirSync(dir,{recursive:true});
const N=Math.round(6.5*30);
for(let i=0;i<N;i++){await p.evaluate(t=>setT(t),i/30);await p.locator('#s1').screenshot({path:`${dir}/${String(i).padStart(4,'0')}.png`})}
await b.close();
execSync(`ffmpeg -loglevel error -y -framerate 30 -i ${dir}/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart ${__dirname}/scary.mp4`);
console.log('frames',N)})();
