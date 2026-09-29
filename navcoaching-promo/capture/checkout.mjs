// Checkout questionnaire (5 steps) with TEST data, then (only with --submit) create the order and capture the order + account pages.
// Usage: node capture/checkout.mjs <session-file> <order-file> [--submit]
import fs from "node:fs";
import { open, go, settle, capturePage, captureState, rectOf, manifest, saveManifest } from "./lib.mjs";

const [SESSION, ORDERFILE, flag] = process.argv.slice(2);
const SUBMIT = flag === "--submit";
const { browser, page } = await open({ storageState: SESSION });
const HDR = 69;

const choice = (name, text) => page.locator(`label.choice:has(input[name="${name}"])`, { hasText: text }).first();
const top = async (loc, off = 150) => Math.max(0, (await rectOf(page, loc)).y - HDR - off);
const shot = (id, scroll, rects = {}) => captureState(page, id, { scroll, pageId: "checkout", rects });

await go(page, manifest.checkoutHref || "/checkout/int1");

// ---- step 1: package & contact
await shot("co1_0", 0);
const name = page.locator("#name");
await name.fill("");
let y = await top(name, 260);
for (const [i, part] of ["نو", "نورة"].entries()) {
  await name.fill(part);
  await shot(`co1_name${i}`, y, { field: name });
}
const phone = page.locator("#phone");
await phone.fill("512345678");
await shot("co1_phone", await top(phone, 300), { field: phone });
const female = choice("gender", "أنثى");
await female.click();
const age = page.locator("#age");
await age.fill("28");
y = await top(female, 300);
await shot("co1_gender", y, { gender: female, age });
const next = page.getByRole("button", { name: "التالي" });
await shot("co1_next", await top(next, 560), { next });
await next.click();
await settle(page);

// ---- step 2: goal & training
await shot("co2_0", 0);
const goal = choice("goal", "نزول دهون + بناء عضل");
await goal.click();
await shot("co2_goal", await top(goal, 260), { pick: goal });
const level = choice("level", "مبتدئ");
await level.click();
const place = choice("place", "نادي");
await place.click();
await shot("co2_level", await top(level, 300), { level, place });
await page.locator("#days").selectOption("4 أيام");
await page.locator("#duration").selectOption("ساعة");
await shot("co2_next", await top(next, 560), { next, days: page.locator("#days"), duration: page.locator("#duration") });
await next.click();
await settle(page);

// ---- step 3: health (private)
await choice("injury", "لا").click();
await choice("condition", "لا").click();
await shot("co3_0", 0, { alert: page.locator("fieldset[data-step='3'] .alert").first() });
await page.locator("input[name=health_ack]").check();
await shot("co3_next", await top(next, 560), { ack: page.locator("input[name=health_ack]").locator(".."), next });
await next.click();
await settle(page);

// ---- step 4: measurements
await page.locator("#weight").fill("65");
await page.locator("#height").fill("165");
const cal = page.locator("#calories");
const calOpts = await cal.locator("option").allTextContents();
await cal.selectOption({ index: Math.min(1, calOpts.length - 1) });
await shot("co4_0", 0, { weight: page.locator("#weight"), height: page.locator("#height") });
await shot("co4_next", await top(next, 560), { next, calories: cal });
await next.click();
await settle(page);

// ---- step 5: expectations & consents
const exp = page.locator("#expectations");
await exp.fill("متابعة قريبة، وتعديل البرنامج حسب تقدّمي.");
await shot("co5_0", 0, { exp });
const media = page.locator("#media");
const mOpts = await media.locator("option").allTextContents();
await media.selectOption({ index: mOpts.length - 1 });
await page.locator("input[name=consent_terms]").check();
await page.locator("input[name=consent_wa]").check();
const submit = page.getByRole("button", { name: "أرسل الاستبيان وانتقل للدفع" });
await shot("co5_submit", await top(submit, 560), { submit, terms: page.locator("input[name=consent_terms]").locator(".."), wa: page.locator("input[name=consent_wa]").locator("..") });
console.log("options calories:", calOpts, "media:", mOpts);

if (!SUBMIT) {
  console.log("DRY_RUN_DONE");
  await browser.close();
  process.exit(0);
}
if (fs.existsSync(ORDERFILE)) {
  console.log("ORDER_ALREADY_CREATED", fs.readFileSync(ORDERFILE, "utf8"));
  await browser.close();
  process.exit(0);
}
await submit.click();
await page.waitForURL(/\/account\/orders\//, { timeout: 45000 });
await page.waitForLoadState("networkidle");
await settle(page);
const orderUrl = new URL(page.url()).pathname;
fs.writeFileSync(ORDERFILE, orderUrl);
manifest.orderUrl = orderUrl;
saveManifest();
console.log("ORDER_CREATED", orderUrl);
await browser.close();
