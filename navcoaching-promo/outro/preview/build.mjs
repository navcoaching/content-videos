// Static preview of the outro's main frame (1080x1920): real logo + real site screenshot + site services + URL.
// usage: node outro/preview/build.mjs  -> outro/preview/outro-preview.png
import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import { pathToFileURL } from "node:url";
const root = path.resolve(".");
const u = (p) => pathToFileURL(path.join(root, p)).href;
const URL_TEXT = "navcoaching.com";
const SERVICES = ["برامج مع متابعة", "ملفات بدون متابعة", "استشارات", "باقة القيمرز"];
const fonts = ["arabic-500", "arabic-600", "latin-500", "latin-600"].map((f) => `<link rel="stylesheet" href="${u(`node_modules/@fontsource/readex-pro/${f}.css`)}">`).join("");
const html = `<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">${fonts}<style>
html,body{margin:0;width:1080px;height:1920px;overflow:hidden}
body{position:relative;background:radial-gradient(ellipse 85% 50% at 50% 42%, #0c2144 0%, #07142a 52%, #030914 100%);font-family:"Readex Pro",sans-serif}
.beam{position:absolute;left:-20%;top:-10%;width:140%;height:70%;background:linear-gradient(115deg, rgba(76,197,237,0) 38%, rgba(76,197,237,0.09) 50%, rgba(76,197,237,0) 62%);filter:blur(30px);transform:rotate(-8deg)}
.glow{position:absolute;left:50%;top:820px;width:900px;height:900px;transform:translate(-50%,-50%);background:radial-gradient(circle at center, rgba(76,197,237,0.18) 0%, rgba(76,197,237,0) 62%)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse 80% 70% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)}
.logo{position:absolute;left:50%;top:225px;width:456px;transform:translate(-50%,-50%)}
.phone{position:absolute;left:50%;top:395px;width:380px;height:822px;transform:translateX(-50%);border-radius:58px;padding:14px;background:linear-gradient(160deg,#1b2b45,#0b1424);box-shadow:0 0 0 2px rgba(76,197,237,0.35),0 50px 110px rgba(0,0,0,0.6),0 0 90px rgba(76,197,237,0.18)}
.screen{width:100%;height:100%;border-radius:46px;overflow:hidden;background:#fff}
.screen img{width:100%;display:block}
.svc{position:absolute;left:90px;right:90px;top:1282px;display:grid;grid-template-columns:1fr 1fr;gap:18px}
.svc span{display:flex;align-items:center;justify-content:flex-start;padding:0 36px;gap:16px;height:88px;border-radius:22px;background:rgba(10,24,46,0.72);border:1.5px solid rgba(76,197,237,0.42);color:#eaf2fb;font-weight:500;font-size:38px}
.svc span i{width:10px;height:10px;border-radius:50%;background:#4cc5ed;flex:none}
.line{position:absolute;left:50%;top:1532px;width:120px;height:4px;border-radius:4px;background:#4cc5ed;transform:translateX(-50%)}
.ring{position:absolute;left:760px;top:1662px;width:64px;height:64px;transform:translate(-50%,-50%);border-radius:50%;border:3px solid rgba(76,197,237,0.75);box-shadow:0 0 24px rgba(76,197,237,0.45)}
.cursor{position:absolute;left:760px;top:1662px;width:52px;filter:drop-shadow(0 6px 10px rgba(0,0,0,0.55))}
.url{position:absolute;left:0;right:0;top:1566px;text-align:center;direction:ltr;font-weight:500;font-size:68px;letter-spacing:1.5px;color:#eaf2fb}
</style></head><body><div class="beam"></div><div class="glow"></div><div class="vig"></div>
<img class="logo" src="${u("public/brand/logo-white.webp")}">
<div class="phone"><div class="screen"><img src="${u("public/brand/site-home.jpg")}"></div></div>
<div class="svc">${SERVICES.map((s) => `<span><i></i>${s}</span>`).join("")}</div>
<div class="line"></div><div class="url">${URL_TEXT}</div><div class="ring"></div><svg class="cursor" viewBox="0 0 24 36"><path d="M1.5 1.5 L1.5 28 L8 22 L12.5 33 L17 31 L12.6 20.5 L21 20.5 Z" fill="#ffffff" stroke="#0a1628" stroke-width="2" stroke-linejoin="round"/></svg></body></html>`;
const f = path.join(root, "outro/preview/_p.html");
fs.writeFileSync(f, html);
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto(pathToFileURL(f).href, { waitUntil: "load" });
await p.evaluate(() => document.fonts.ready);
await p.waitForTimeout(400);
console.log(await p.evaluate(() => ({ imgs: [...document.images].map((i) => i.naturalWidth), font: document.fonts.check('500 40px "Readex Pro"') })));
await p.screenshot({ path: "outro/preview/outro-preview.png" });
await browser.close();
fs.unlinkSync(f);
