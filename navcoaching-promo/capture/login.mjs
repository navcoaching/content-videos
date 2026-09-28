// Log in with the owner's email (one-time code), capturing each screen. The session is saved OUTSIDE the repo.
// Usage: node capture/login.mjs <email> <session-file> <code-file>
import fs from "node:fs";
import { open, go, captureState, rectOf, saveManifest, manifest } from "./lib.mjs";

const [email, SESSION, CODEFILE] = process.argv.slice(2);
const { browser, ctx, page } = await open();

await go(page, "/programs/intensive");
const sub = page.locator("a[href^='/checkout/']").first();
const href = await sub.getAttribute("href");
manifest.checkoutHref = href;
saveManifest();
await sub.click();
await page.waitForURL(/\/login/);
await page.waitForLoadState("networkidle");
await captureState(page, "login0", { scroll: 0, pageId: "login", rects: { email: page.locator("input[type=email]"), send: page.getByRole("button", { name: "أرسل رمز الدخول" }) } });
const input = page.locator("input[type=email]");
await input.click();
await input.fill(email);
await captureState(page, "login1", { scroll: 0, pageId: "login", rects: { email: input, send: page.getByRole("button", { name: "أرسل رمز الدخول" }), blur: input } });
await page.getByRole("button", { name: "أرسل رمز الدخول" }).click();
const codeInput = page.locator("input[autocomplete=one-time-code], input[inputmode=numeric]").first();
await codeInput.waitFor({ timeout: 30000 });
await page.waitForTimeout(500);
await captureState(page, "login2", {
  scroll: 0,
  pageId: "login",
  rects: { code: codeInput, blur: page.getByText(email).first(), enter: page.getByRole("button", { name: "دخول" }) },
});
console.log("CODE_REQUESTED");

// wait (up to 20 min) for the code to be written to CODEFILE
let code = "";
for (let i = 0; i < 1200 && !code; i++) {
  if (fs.existsSync(CODEFILE)) code = fs.readFileSync(CODEFILE, "utf8").trim();
  else await new Promise((r) => setTimeout(r, 1000));
}
if (!/^\d{6}$/.test(code)) {
  console.log("NO_CODE");
  process.exit(1);
}
await codeInput.click();
for (let i = 1; i <= 6; i++) {
  await codeInput.type(code[i - 1]);
  if (i === 3 || i === 6) await captureState(page, `login3_${i}`, { scroll: 0, pageId: "login", rects: { code: codeInput, blur: page.getByText(email).first() } });
}
await page.getByRole("button", { name: "دخول" }).click();
await page.waitForURL(/\/checkout\//, { timeout: 30000 });
await page.waitForLoadState("networkidle");
await ctx.storageState({ path: SESSION });
fs.unlinkSync(CODEFILE);
console.log("LOGGED_IN", page.url());
await browser.close();
