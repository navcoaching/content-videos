// Capture the new order page and the account page (logged in). Nothing is uploaded.
// Usage: node capture/order.mjs <session-file> <order-file>
import fs from "node:fs";
import { open, go, settle, capturePage, captureState, rectOf } from "./lib.mjs";

const [SESSION, ORDERFILE] = process.argv.slice(2);
const orderUrl = fs.readFileSync(ORDERFILE, "utf8").trim();
const { browser, ctx, page } = await open({ storageState: SESSION });
await ctx.grantPermissions(["clipboard-read", "clipboard-write"], { origin: "https://navcoaching.com" });
const HDR = 69;
const top = async (loc, off = 150) => Math.max(0, (await rectOf(page, loc)).y - HDR - off);

await go(page, orderUrl + "?new=1");
await capturePage(page, "order", {
  banner: page.locator(".alert.ok").first(),
  status: page.locator("[data-testid=order-status]"),
  next: page.getByRole("heading", { name: "الخطوة التالية" }),
  bank: page.locator(".bank").first(),
  copyIban: page.getByRole("button", { name: "نسخ الآيبان" }),
  timeline: page.getByRole("heading", { name: "حالة الطلب" }),
});
const bank = page.locator(".bank").first();
const by = await top(bank, 260);
await captureState(page, "orderBank", { scroll: by, pageId: "order", rects: { bank, copy: page.getByRole("button", { name: "نسخ الآيبان" }) } });
await page.getByRole("button", { name: "نسخ الآيبان" }).click();
await page.waitForTimeout(300);
await captureState(page, "orderCopied", { scroll: by, pageId: "order", rects: { copy: page.getByRole("button", { name: /نسخ الآيبان|تم النسخ/ }).first() } });
const upload = page.locator("input[type=file]").first().locator("xpath=ancestor::form[1]");
const uy = await top(upload, 200);
await captureState(page, "orderUpload", { scroll: uy, pageId: "order", rects: { upload } });
const tl = page.getByRole("heading", { name: "حالة الطلب" });
await captureState(page, "orderTimeline", { scroll: await top(tl, 40), pageId: "order", rects: { timeline: tl.locator("xpath=..") } });

await go(page, "/account");
await capturePage(page, "account", {
  orders: page.getByRole("heading", { name: "طلباتي" }),
  orderCard: page.locator("a.order-card").first(),
  freePlans: page.getByRole("heading", { name: "جداولي المجانية" }),
  profile: page.getByRole("heading", { name: "بياناتي" }),
  prefs: page.getByRole("heading", { name: "تفضيلات التواصل" }),
  install: page.locator("[data-testid=install-link]"),
  blurEmail: page.locator("bdi[dir=ltr]", { hasText: "@" }).first(),
});
await browser.close();
console.log("DONE");
