// Shared capture helpers: exact screenshots of navcoaching.com at iPhone size (390x844 CSS @3x).
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";

export const SITE = "https://navcoaching.com";
export const DEV = { w: 390, h: 844, dpr: 3 };
export const OUT = path.resolve("public/tut");
const MANIFEST = path.join(OUT, "manifest.json");

export const manifest = fs.existsSync(MANIFEST)
  ? JSON.parse(fs.readFileSync(MANIFEST, "utf8"))
  : { device: DEV, pages: {}, states: {}, overlays: {} };
export const saveManifest = () => fs.writeFileSync(MANIFEST, JSON.stringify(manifest, null, 1));

export async function open({ storageState } = {}) {
  const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
  const ctx = await browser.newContext({
    viewport: { width: DEV.w, height: DEV.h },
    deviceScaleFactor: DEV.dpr,
    isMobile: true,
    hasTouch: true,
    locale: "ar-SA",
    colorScheme: "light",
    reducedMotion: "reduce",
    storageState,
  });
  const page = await ctx.newPage();
  return { browser, ctx, page };
}

export async function go(page, url) {
  await page.goto(SITE + url, { waitUntil: "networkidle" });
  await settle(page);
}

export async function settle(page) {
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
}

const dir = (id) => {
  const d = path.join(OUT, id);
  fs.mkdirSync(d, { recursive: true });
  return d;
};

// Hide the fixed Netlify badge while capturing; it is re-added as a fixed overlay in the video.
const HIDE_FIXED = "#nl-badge-frame{visibility:hidden!important}";
async function withFixedHidden(page, fn) {
  const h = await page.addStyleTag({ content: HIDE_FIXED });
  try {
    return await fn();
  } finally {
    await h.evaluate((n) => n.remove());
  }
}

/** Full page as vertical tiles + the sticky header, for smooth scrolling in the video. */
export async function capturePage(page, id, rects = {}) {
  const d = dir(id);
  await page.evaluate(() => window.scrollTo(0, 0));
  await settle(page);
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  const TILE = 1300;
  const tiles = [];
  await withFixedHidden(page, async () => {
    for (let y = 0, i = 0; y < height; y += TILE, i++) {
      const h = Math.min(TILE, height - y);
      const file = path.join(d, `tile${i}.jpg`);
      await page.screenshot({ path: file, type: "jpeg", quality: 90, fullPage: true, clip: { x: 0, y, width: DEV.w, height: h } });
      tiles.push({ src: `tut/${id}/tile${i}.jpg`, y, h });
    }
    await page.screenshot({ path: path.join(d, "header.jpg"), type: "jpeg", quality: 92, clip: { x: 0, y: 0, width: DEV.w, height: 69 } });
  });
  const r = {};
  for (const [name, loc] of Object.entries(rects)) r[name] = await rectOf(page, loc);
  manifest.pages[id] = { tiles, height, header: `tut/${id}/header.jpg`, rects: r };
  saveManifest();
  console.log("page", id, height);
}

/** Exact viewport screenshot at a given scroll (what the phone shows after an interaction). */
export async function captureState(page, id, { scroll, rects = {}, pageId }) {
  const d = dir("states");
  if (scroll != null) {
    await page.evaluate((y) => window.scrollTo(0, y), scroll);
    await page.waitForTimeout(250);
  }
  const s = await page.evaluate(() => window.scrollY);
  await withFixedHidden(page, () => page.screenshot({ path: path.join(d, `${id}.jpg`), type: "jpeg", quality: 90 }));
  const r = {};
  for (const [name, loc] of Object.entries(rects)) r[name] = await rectOf(page, loc);
  manifest.states[id] = { src: `tut/states/${id}.jpg`, scroll: s, page: pageId, rects: r };
  saveManifest();
  console.log("state", id, s);
}

/** Rect of a locator in page coordinates (CSS px). */
export async function rectOf(page, loc) {
  const l = typeof loc === "string" ? page.locator(loc).first() : loc;
  const b = await l.boundingBox();
  const sy = await page.evaluate(() => window.scrollY);
  if (!b) return null;
  return { x: Math.round(b.x), y: Math.round(b.y + sy), w: Math.round(b.width), h: Math.round(b.height) };
}

export async function captureBadge(page) {
  const f = page.locator("#nl-badge-frame");
  if (!(await f.count())) return;
  const d = dir("overlays");
  const b = await f.boundingBox();
  await f.screenshot({ path: path.join(d, "badge.png"), omitBackground: true });
  manifest.overlays.badge = { src: "tut/overlays/badge.png", x: b.x, y: b.y, w: b.width, h: b.height };
  saveManifest();
}
