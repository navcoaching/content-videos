import D from "./split.json";

export const FPS = D.fps;
export const DURATION = D.durationInFrames;
export type Shot = {
  id: string;
  clip: string;
  from: number;
  dur: number;
  layout: "full" | "card" | "wide";
};
export const SHOTS = D.shots as unknown as Shot[];

/** Section boundaries (frames) — shared with the audio generator through split.json timing. */
export const SEC = {
  hook: [0, 240],
  title: [240, 360],
  day1: [360, 960],
  rest1: [960, 1080],
  day2: [1080, 1680],
  rest2: [1680, 1800],
  day3: [1800, 2400],
  addons: [2400, 2640],
  cta: [2640, 3120],
} as const;

export type Cap = { at: number; text: string; hl?: boolean; to?: number };

export const CAPTIONS: Cap[] = [
  // hook
  { at: 15, text: "لو تقدر تتمرن", to: 66 },
  { at: 66, text: "3 أيام بس", hl: true, to: 120 },
  { at: 120, text: "في الأسبوع؟", to: 168 },
  { at: 168, text: "وتبي جسم", to: 198 },
  { at: 198, text: "قوي… ورياضي", hl: true, to: 236 },
  // day 1
  { at: 420, text: "نبدأ بتسخين ومرونة", to: 480 },
  { at: 480, text: "وقفزات خفيفة", to: 540 },
  { at: 540, text: "بعدها سكوات", to: 600 },
  { at: 600, text: "وصعود الدرج", to: 660 },
  { at: 660, text: "ولانجز", hl: true, to: 750 },
  { at: 750, text: "كل تمرين 3–4 جولات", to: 840 },
  { at: 840, text: "وتختم بتمدد خفيف", to: 950 },
  // day 2
  { at: 1140, text: "صدر وظهر وأكتاف", to: 1200 },
  { at: 1200, text: "تمرين الضغط", to: 1260 },
  { at: 1260, text: "وسحب علوي", to: 1320 },
  { at: 1320, text: "وضغط أكتاف", to: 1380 },
  { at: 1380, text: "وضغط دمبل", to: 1440 },
  { at: 1440, text: "وتمرين بالبار", to: 1530 },
  { at: 1530, text: "وتختم بكارديو خفيف", hl: true, to: 1670 },
  // day 3
  { at: 1860, text: "قوة وسرعة", hl: true, to: 1920 },
  { at: 1920, text: "رفعة انفجارية", to: 1980 },
  { at: 1980, text: "وكيتل بل", to: 2040 },
  { at: 2040, text: "وحركات كاملة", to: 2100 },
  { at: 2100, text: "ورجل وحدة", to: 2160 },
  { at: 2160, text: "وحبال ثقيلة", to: 2250 },
  { at: 2250, text: "ورفعة رومانية", to: 2390 },
];

export type Day = {
  key: "day1" | "day2" | "day3";
  n: number;
  big: string;
  sub: string;
  en: string;
  from: number;
  to: number;
  list: { from: number; title: string; items: [string, string][] };
};

export const DAYS: Day[] = [
  {
    key: "day1", n: 1, big: "اليوم 1", sub: "الأرجل", en: "DAY 01 · LEGS", from: 360, to: 960,
    list: { from: 690, title: "خطة الأرجل", items: [
      ["مرونة وتسخين", "5 د"], ["قفزات خفيفة", "3×10"], ["سكوات", "4×6–8"], ["صعود الدرج", "3×12 لكل رجل"], ["لانجز", "3×10 لكل رجل"],
    ] },
  },
  {
    key: "day2", n: 2, big: "اليوم 2", sub: "الجزء العلوي", en: "DAY 02 · UPPER BODY", from: 1080, to: 1680,
    list: { from: 1440, title: "خطة الجزء العلوي", items: [
      ["تمرين الضغط", "4×10–15"], ["سحب علوي", "4×8–10"], ["ضغط أكتاف", "3×8–10"], ["ضغط دمبل", "3×10–12"], ["كارديو فترات", "30ث × 6"],
    ] },
  },
  {
    key: "day3", n: 3, big: "اليوم 3", sub: "الجسم كامل", en: "DAY 03 · FULL BODY · POWER", from: 1800, to: 2400,
    list: { from: 2160, title: "قوة وقدرة", items: [
      ["رفعة انفجارية", "4×3–5"], ["كيتل بل سوينغ", "3×12"], ["حركات كاملة", "3×8"], ["لانجز بوزن", "3×8 لكل رجل"], ["حبال ثقيلة", "5×30ث"], ["رفعة رومانية", "3×8"],
    ] },
  },
];

export const CREDIT = "Footage: Mixkit · mixkit.co/free-stock-video · Mixkit Stock Video Free License";
export const URL_TEXT = "navcoaching.com";

/** True while an exercise list is on screen (captions and cards make room for it). */
export const listActiveAt = (f: number) => DAYS.some((d) => f >= d.list.from && f < d.to);
