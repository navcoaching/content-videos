// Static preview of the intro's main frame (1080x1920). Uses the real logo files from public/brand, unaltered.
// usage: node intro/preview/build.mjs   -> intro/preview/intro-preview-A.png (dark) + intro-preview-B.png (light)
import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import { pathToFileURL } from "node:url";
const root = path.resolve(".");
const u = (p) => pathToFileURL(path.join(root, p)).href;
const fonts = ["arabic-500", "arabic-600", "latin-500"].map((f) => `<link rel="stylesheet" href="${u(`node_modules/@fontsource/readex-pro/${f}.css`)}">`).join("");
const page = (variant) => {
  const dark = variant === "A";
  const logo = u(`public/brand/${dark ? "logo-white.webp" : "logo-color.webp"}`);
  return `<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">${fonts}<style>
  html,body{margin:0;width:1080px;height:1920px;overflow:hidden}
  body{background:${dark ? "radial-gradient(ellipse 70% 42% at 50% 46%, #0d1f3c 0%, #07142a 60%, #040c1b 100%)" : "radial-gradient(ellipse 70% 42% at 50% 46%, #ffffff 0%, #f1f6fb 70%, #e6eef7 100%)"};font-family:"Readex Pro",sans-serif;position:relative}
  .glow{position:absolute;left:50%;top:880px;width:760px;height:380px;transform:translate(-50%,-50%);background:radial-gradient(ellipse at center, rgba(76,197,237,${dark ? 0.16 : 0.10}) 0%, rgba(76,197,237,0) 70%)}
  img{position:absolute;left:50%;top:880px;width:528px;transform:translate(-50%,-50%)}
  .line{position:absolute;left:50%;top:1062px;width:120px;height:4px;border-radius:4px;background:#4cc5ed;transform:translateX(-50%)}
  .tag{position:absolute;left:0;right:0;top:1112px;text-align:center;font-weight:500;font-size:46px;color:${dark ? "#c9d7e8" : "#34507a"};letter-spacing:0}
  </style></head><body><div class="glow"></div><img src="${logo}"><div class="line"></div><div class="tag">تدريب مبني عليك</div></body></html>`;
};
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
for (const v of ["A", "B"]) {
  const p = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const f = path.join(root, `intro/preview/_${v}.html`);
  fs.writeFileSync(f, page(v));
  await p.goto(pathToFileURL(f).href, { waitUntil: "load" });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  const ok = await p.evaluate(() => ({ img: document.querySelector("img").naturalWidth, font: document.fonts.check('500 40px "Readex Pro"') }));
  console.log(v, ok);
  await p.screenshot({ path: `intro/preview/intro-preview-${v}.png` });
}
await browser.close();
console.log("ok");
