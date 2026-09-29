// Member guide page (/account/guide) — logged in, read-only.
import { open, go, capturePage } from "./lib.mjs";
const { browser, page } = await open({ storageState: process.argv[2] });
await go(page, "/account/guide");
const h = (re) => page.getByRole("heading", { name: re }).first();
await capturePage(page, "guide", {
  colors: h(/معاني الألوان/), s1: h(/البداية/), s2: h(/اختيار اليوم/), s3: h(/تسجيل التمرين/), s4: h(/الوزن والقياسات/), s5: h(/الغذاء والمراجعة/),
  side: page.locator(".account-side"),
});
await browser.close();
