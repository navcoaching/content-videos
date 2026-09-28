// Capture the public (logged-out) part of the tutorial. Read-only: nothing is submitted to the site.
import { open, go, settle, capturePage, captureState, captureBadge, rectOf } from "./lib.mjs";

const { browser, page } = await open();
const only = process.argv[2]; // optional: run a single section
const run = (name) => !only || only === name;

if (run("home")) {
  await go(page, "/");
  await captureBadge(page);
  await capturePage(page, "home", {
    menu: page.locator("details.menu > summary"),
    heroCta: page.locator(".hero a.btn-cyan").first(),
    heroQuiz: page.locator(".hero a.btn-ghost").first(),
    why: page.getByRole("heading", { name: "تدريب مبني عليك، مو جدول جاهز" }),
    programs: page.getByRole("heading", { name: "اختر مستوى المتابعة اللي يناسبك" }),
    gamers: page.getByRole("heading", { name: /قيمر؟/ }),
    inside: page.getByRole("heading", { name: "كيف يبدو برنامجك؟" }),
    how: page.getByRole("heading", { name: "ثلاث خطوات لأول تمرين" }),
    coach: page.getByRole("heading", { name: /الكوتش/ }),
    reviews: page.getByRole("heading", { name: "تقييمات المتدربين" }),
    faq: page.getByRole("heading", { name: "قبل ما تشترك" }),
    calc: page.getByRole("heading", { name: "حاسبة السعرات اليومية" }),
  });
  // open the menu
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.locator("details.menu > summary").click();
  await page.waitForTimeout(500);
  await captureState(page, "menuOpen", { scroll: 0, pageId: "home", rects: { programsLink: page.locator("details.menu a", { hasText: "البرامج" }).first() } });
}

if (run("programs")) {
  await go(page, "/programs");
  await capturePage(page, "programs", {
    quizBtn: page.getByRole("link", { name: /محتار أي باقة/ }),
    tabs: page.locator("[role=tab]").first(),
    tabFiles: page.locator("[role=tab]", { hasText: "ملفات بدون متابعة" }),
    tabConsult: page.locator("[role=tab]", { hasText: "استشارات" }),
    intensive: page.locator("a.pcard", { hasText: "المكثفة" }).first(),
    compare: page.getByRole("heading", { name: "قارن بين باقات المتابعة" }),
    quiz: page.getByRole("heading", { name: /جاوب على 4 أسئلة/ }),
  });
  // tabs (they are links: ?cat=files / ?cat=consult) — capture the same scroll position
  const tabsY = (await rectOf(page, page.locator("[role=tab]").first())).y - 69 - 90;
  for (const [id, cat] of [["tabFiles", "files"], ["tabConsult", "consult"]]) {
    await go(page, `/programs?cat=${cat}`);
    await captureState(page, id, { scroll: tabsY, pageId: "programs" });
  }
  // quiz: answer the 4 questions like a beginner who wants training + nutrition
  await go(page, "/programs");
  const quizTop = (await rectOf(page, page.getByRole("heading", { name: /جاوب على 4 أسئلة/ }))).y - 69 - 16;
  await captureState(page, "quiz0", { scroll: quizTop, pageId: "programs" });
  const answers = [
    ["level", "مبتدئ · أقل من 6 أشهر"],
    ["need", "تمرين وتغذية"],
    ["follow", "متابعة أسبوعية + مكالمات زوم"],
    ["live", "لا"],
  ];
  const aRects = {};
  for (let i = 0; i < answers.length; i++) {
    const [name, label] = answers[i];
    const loc = page.locator(`label.choice:has(input[name="${name}"])`, { hasText: label }).first();
    aRects[`a${i}`] = await rectOf(page, loc);
    await loc.click();
    await page.waitForTimeout(300);
    // keep the question being answered comfortably in view
    const y = Math.max(quizTop, aRects[`a${i}`].y - 69 - 380);
    await captureState(page, `quiz${i + 1}`, { scroll: y, pageId: "programs", rects: { answer: loc } });
  }
  // recommendation card
  const card = page.locator(".card[aria-live]").first();
  const cy = (await rectOf(page, card)).y - 69 - 20;
  await captureState(page, "quizResult", { scroll: cy, pageId: "programs", rects: { card, subscribe: card.locator("a.btn").first(), details: card.locator("a.btn-ghost").first() } });
}

if (run("detail")) {
  await go(page, "/programs/intensive");
  await capturePage(page, "detail", {
    subscribe: page.locator("a[href^='/checkout/']").first(),
  });
}

if (run("calculator")) {
  await go(page, "/calculator");
  await capturePage(page, "calculator", {
    form: page.getByRole("heading", { name: "حاسبة السعرات اليومية" }).last(),
    submit: page.getByRole("button", { name: "احسب السعرات" }),
  });
  const top = (await rectOf(page, page.getByText("طريقة الحساب").first())).y - 69 - 12;
  await captureState(page, "calc0", { scroll: top, pageId: "calculator" });
  const noBf = page.locator("label", { hasText: "ما أعرف نسبة الدهون" }).first();
  await noBf.click();
  await captureState(page, "calc1", { scroll: top, pageId: "calculator", rects: { method: noBf } });
  const fields = page.locator("input[type=number], input[inputmode=decimal], input[inputmode=numeric]");
  const vals = [["65"], ["165"], ["28"]];
  const fRects = [];
  for (let i = 0; i < 3; i++) {
    const f = fields.nth(i);
    fRects.push(await rectOf(page, f));
    await f.fill(vals[i][0]);
    await page.waitForTimeout(150);
    await captureState(page, `calcF${i}`, { scroll: Math.max(top, fRects[i].y - 69 - 360), pageId: "calculator", rects: { field: f } });
  }
  const female = page.locator("label", { hasText: /^أنثى$/ }).first();
  const fy0 = (await rectOf(page, female)).y - 69 - 360;
  await female.click();
  await captureState(page, "calcGender", { scroll: fy0, pageId: "calculator", rects: { gender: female } });
  const submit = page.getByRole("button", { name: "احسب السعرات" });
  const sy = (await rectOf(page, submit)).y - 69 - 560;
  await captureState(page, "calcReady", { scroll: sy, pageId: "calculator", rects: { submit } });
  await submit.click();
  await page.waitForTimeout(700);
  await captureState(page, "calcResult0", { scroll: sy, pageId: "calculator" });
  const res = page.locator("[aria-live]").filter({ hasText: /سعرة|kcal/ }).first();
  if (await res.count()) {
    const ry = (await rectOf(page, res)).y - 69 - 20;
    await captureState(page, "calcResult", { scroll: ry, pageId: "calculator", rects: { result: res } });
  }
}

if (run("more")) {
  await go(page, "/free-plans");
  await capturePage(page, "freePlans", {});
  await go(page, "/reviews");
  await capturePage(page, "reviews", {});
  await go(page, "/faq");
  const q1 = page.locator("main details:not(.menu) summary").first();
  await capturePage(page, "faq", { first: q1 });
  await q1.click();
  await page.waitForTimeout(400);
  const fy = (await rectOf(page, q1)).y - 69 - 200;
  await captureState(page, "faqOpen", { scroll: Math.max(0, fy), pageId: "faq", rects: { q: q1 } });
  await go(page, "/about");
  await capturePage(page, "about", {});
  await go(page, "/install");
  await capturePage(page, "install", {});
}

await browser.close();
