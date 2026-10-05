// Static preview of the outro's main frame (1080x1920). Real logo file from public/brand, unaltered.
// usage: node outro/preview/build.mjs  -> outro/preview/outro-preview.png
import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import { pathToFileURL } from "node:url";
const root = path.resolve(".");
const u = (p) => pathToFileURL(path.join(root, p)).href;
const URL_TEXT = "navcoaching.com";
const fonts = ["latin-500", "latin-600"].map((f) => `<link rel="stylesheet" href="${u(`node_modules/@fontsource/readex-pro/${f}.css`)}">`).join("");
const html = `<!doctype html><html><head><meta charset="utf-8">${fonts}<style>
html,body{margin:0;width:1080px;height:1920px;overflow:hidden}
body{position:relative;background:radial-gradient(ellipse 80% 46% at 50% 44%, #0c2144 0%, #07142a 52%, #030914 100%);font-family:"Readex Pro",sans-serif}
.beam{position:absolute;left:-20%;top:-10%;width:140%;height:70%;background:linear-gradient(115deg, rgba(76,197,237,0) 38%, rgba(76,197,237,0.10) 50%, rgba(76,197,237,0) 62%);filter:blur(30px);transform:rotate(-8deg)}
.glow{position:absolute;left:50%;top:840px;width:900px;height:460px;transform:translate(-50%,-50%);background:radial-gradient(ellipse at center, rgba(76,197,237,0.20) 0%, rgba(76,197,237,0) 68%)}
.streak{position:absolute;left:50%;top:840px;width:980px;height:2px;transform:translate(-50%,-50%);background:linear-gradient(90deg, rgba(76,197,237,0) 0%, rgba(76,197,237,0.28) 50%, rgba(76,197,237,0) 100%);filter:blur(1px)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse 75% 65% at 50% 46%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)}
img{position:absolute;left:50%;top:840px;width:528px;transform:translate(-50%,-50%)}
.line{position:absolute;left:50%;top:1042px;width:120px;height:4px;border-radius:4px;background:#4cc5ed;transform:translateX(-50%)}
.url{position:absolute;left:0;right:0;top:1100px;text-align:center;direction:ltr;font-weight:500;font-size:68px;letter-spacing:1.5px;color:#eaf2fb}
</style></head><body><div class="beam"></div><div class="glow"></div><div class="streak"></div><div class="vig"></div>
<img src="${u("public/brand/logo-white.webp")}"><div class="line"></div><div class="url">${URL_TEXT}</div></body></html>`;
const f = path.join(root, "outro/preview/_p.html");
fs.writeFileSync(f, html);
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto(pathToFileURL(f).href, { waitUntil: "load" });
await p.evaluate(() => document.fonts.ready);
await p.waitForTimeout(400);
console.log(await p.evaluate(() => ({ img: document.querySelector("img").naturalWidth, font: document.fonts.check('500 40px "Readex Pro"') })));
await p.screenshot({ path: "outro/preview/outro-preview.png" });
await browser.close();
fs.unlinkSync(f);
