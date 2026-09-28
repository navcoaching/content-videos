// Render selected frames as JPEGs for visual QA: node scripts/stills.mjs 60 120 240 ...
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition, openBrowser } from "@remotion/renderer";
import path from "node:path";
import fs from "node:fs";

const frames = process.argv.slice(2).map(Number);
const outDir = path.resolve(process.env.OUT || "stills");
fs.mkdirSync(outDir, { recursive: true });
const browserExecutable = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell";
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const browser = await openBrowser("chrome", { browserExecutable, chromiumOptions: { gl: "angle" } });
const composition = await selectComposition({ serveUrl, id: process.env.COMP || "NavPromo", puppeteerInstance: browser });
for (const frame of frames) {
  const output = path.join(outDir, `f${String(frame).padStart(4, "0")}.jpg`);
  await renderStill({ serveUrl, composition, frame, output, imageFormat: "jpeg", jpegQuality: 85, puppeteerInstance: browser, scale: 0.5 });
  console.log("rendered", output);
}
await browser.close({ silent: true });
