// Reconnaissance: full-page thumbnails + outline of each public page (read-only browsing).
import { chromium } from "playwright";
import fs from "node:fs";
const OUT = process.argv[2];
fs.mkdirSync(OUT, { recursive: true });
const pages = ["/", "/programs", "/calculator", "/free-plans", "/reviews", "/faq", "/about", "/install", "/login", "/policies"];
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true, locale: "ar-SA", reducedMotion: "reduce" });
const page = await ctx.newPage();
const outline = {};
for (const p of pages) {
  await page.goto("https://navcoaching.com" + p, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  const name = p === "/" ? "home" : p.slice(1);
  await page.screenshot({ path: `${OUT}/${name}.jpg`, fullPage: true, quality: 70, type: "jpeg" });
  outline[p] = await page.evaluate(() => ({
    height: document.documentElement.scrollHeight,
    heads: [...document.querySelectorAll("h1,h2,h3")].map((e) => e.tagName + ": " + e.textContent.trim().slice(0, 70)),
    links: [...new Set([...document.querySelectorAll("a[href^='/']")].map((a) => a.getAttribute("href")))].slice(0, 40),
    buttons: [...document.querySelectorAll("button,.btn")].map((b) => b.textContent.trim().slice(0, 40)).filter(Boolean).slice(0, 25),
  }));
}
fs.writeFileSync(`${OUT}/outline.json`, JSON.stringify(outline, null, 1));
await browser.close();
