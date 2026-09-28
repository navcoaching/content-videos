import React from "react";
import { useCurrentFrame } from "remotion";
import { FONT } from "../../theme";
import { L } from "../theme";
import { J, keyed } from "../tl";
import { BrowserWindow, MacCursor, Rect, Spotlight } from "../parts/Chrome";
import { Btn, Card, Choice, Eyebrow, H, P, SiteHeader } from "../parts/Site";
import { ramp, sp, SPR } from "../../lib/motion";
import { pg, useWindowIn } from "./common";

const C1 = J.ch1;
const [S0, S1] = J.segments.ch1 as [number, number];

// Packages as described in the site's quiz logic (src/lib/quiz.ts)
const CARDS = [
  { name: "الأساسية", body: "خطة تمرين ومتابعة كل أسبوعين." },
  { name: "التغذية", body: "خطة تغذية شاملة، وتتعلّم حساب السعرات، مع متابعة أسبوعية." },
  { name: "المكثفة", body: "تمرين وتغذية، مراجعة أسبوعية و4 مكالمات زوم شهرياً.", dark: true },
];
const cardX = (i: number) => 1000 - 40 - 296 - i * 316;

// Quiz (src/components/Quiz.tsx)
const Q = [
  { y: 910, title: "1. وش مستواك في التمرين؟", rows: [{ y: 960, w: 293, opts: ["مبتدئ · أقل من 6 أشهر", "متوسط · 6 أشهر – سنتين", "متقدم · أكثر من سنتين"] }] },
  {
    y: 1050,
    title: "2. وش تحتاج بالضبط؟",
    rows: [
      { y: 1100, w: 293, opts: ["تمرين وتغذية", "تمرين فقط", "تغذية فقط"] },
      { y: 1174, w: 450, opts: ["عندي أسئلة محددة في التمرين", "عندي أسئلة محددة في التغذية"] },
    ],
  },
  {
    y: 1264,
    title: "3. أي نوع متابعة يناسبك؟",
    rows: [
      { y: 1314, w: 450, opts: ["متابعة أسبوعية + مكالمات زوم", "متابعة أسبوعية بدون مكالمات"] },
      { y: 1388, w: 920, opts: ["ما أحتاج متابعة، أبي جدول وأمشي عليه"] },
    ],
  },
  { y: 1478, title: "4. تحتاج جلسة حضورية لتصحيح التكنيك؟", small: "(للبنات في المنطقة الشرقية)", rows: [{ y: 1528, w: 450, opts: ["نعم", "لا"] }] },
];
const chipX = (w: number, i: number) => 1000 - 40 - w - i * (w + (w === 293 ? 20 : 20));
// selected answers: [question, row, option]
const PICKS: [number, number, number][] = [
  [0, 0, 0],
  [1, 0, 0],
  [2, 0, 0],
  [3, 0, 1],
];
const pickRect = (k: number): Rect => {
  const [q, r, o] = PICKS[k];
  const row = Q[q].rows[r];
  return [chipX(row.w, o), row.y, row.w, 64];
};

const SCROLL_Q = 750;
const SCROLL_R = 1510;
const RES_Y = 1620;
const CTA_RECT: Rect = [1000 - 40 - 30 - 430, RES_Y + 350, 430, 72];

export const Ch1Programs: React.FC = () => {
  const f = useCurrentFrame();
  const win = useWindowIn(S0, S1);
  const scroll = keyed(f, [[0, 0], [C1.scroll, SCROLL_Q], [C1.result - 22, SCROLL_R]], 26);
  const toContent = (r: Rect, s: number): Rect => [r[0], r[1] - s, r[2], r[3]];

  const spots: [number, Rect | null][] = [
    [S0, null],
    [C1.quizClick - 26, [40, 646, 260, 72]],
    [C1.scroll - 6, null],
    [C1.result + 4, [40, RES_Y - SCROLL_R, 920, 460]],
    [C1.cta - 22, toContent(CTA_RECT, SCROLL_R)],
    [S1 - 10, null],
  ];

  const center = (r: Rect, s: number) => pg(r[0] + r[2] / 2, r[1] - s + r[3] / 2);
  const cursor: [number, number, number][] = [
    [C1.cursorIn, 900, 1520],
    [C1.quizClick - 8, ...pg(170, 682)],
    [C1.scroll + 30, ...pg(500, 500)],
    ...PICKS.map((_, k) => [C1.answers[k] - 6, ...center(pickRect(k), SCROLL_Q)] as [number, number, number]),
    [C1.result + 20, ...pg(620, 620)],
    [C1.cta - 6, ...center(CTA_RECT, SCROLL_R)],
    [S1, ...center(CTA_RECT, SCROLL_R)],
  ];

  const resP = sp(f, C1.result - 10, SPR.soft);

  return (
    <>
      <BrowserWindow style={win.style}>
        <div style={{ position: "absolute", left: 0, right: 0, top: -scroll }}>
          {/* programs */}
          <div style={{ position: "absolute", top: 118, right: 40, left: 40 }}>
            <Eyebrow>البرامج</Eyebrow>
            <H size={46} style={{ marginTop: 10 }}>اختر مستوى المتابعة اللي يناسبك</H>
            <P style={{ marginTop: 6 }}>كل البرامج مخصصة لك بعد الاستبيان.</P>
          </div>
          {CARDS.map((c, i) => {
            const p = sp(f, S0 + 14 + i * 7, SPR.snappy);
            return (
              <Card
                key={c.name}
                dark={c.dark}
                style={{
                  position: "absolute",
                  top: 300,
                  left: cardX(i),
                  width: 296,
                  height: 300,
                  padding: 26,
                  opacity: Math.min(1, p * 2),
                  transform: `translateY(${(1 - p) * 40}px)`,
                  display: "flex",
                  flexDirection: "column",
                  gap: 12,
                }}
              >
                <span style={{ fontFamily: FONT, fontSize: 20, fontWeight: 500, color: c.dark ? "#a9bad0" : L.muted }}>مع متابعة</span>
                <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 700, color: c.dark ? "#fff" : L.heading }}>{c.name}</span>
                <span style={{ fontFamily: FONT, fontSize: 21, lineHeight: 1.5, color: c.dark ? "#a9bad0" : L.muted }}>{c.body}</span>
                <span style={{ marginTop: "auto", fontFamily: FONT, fontSize: 21, fontWeight: 600, color: c.dark ? L.cyan : L.navy }}>التفاصيل والاشتراك ←</span>
              </Card>
            );
          })}
          <P style={{ position: "absolute", top: 640, right: 40, width: 600 }}>مو متأكد أي برنامج يناسبك؟ جاوب على 4 أسئلة، وأقترح لك الباقة الأنسب.</P>
          <Btn kind="ghost" style={{ position: "absolute", top: 646, left: 40, width: 260 }} press={pressAt(f, C1.quizClick)}>
            ابدأ الاختبار
          </Btn>

          {/* quiz */}
          <Eyebrow style={{ position: "absolute", top: 850, right: 40 }}>أي برنامج يناسبني؟</Eyebrow>
          {Q.map((q, qi) => (
            <React.Fragment key={qi}>
              <div style={{ position: "absolute", top: q.y, right: 40, left: 40, fontFamily: FONT, fontWeight: 600, fontSize: 28, color: L.heading }}>
                {q.title} {q.small && <span style={{ fontWeight: 400, fontSize: 22, color: L.muted }}>{q.small}</span>}
              </div>
              {q.rows.map((row, ri) =>
                row.opts.map((o, oi) => {
                  const k = PICKS.findIndex(([a, b, c]) => a === qi && b === ri && c === oi);
                  const on = k >= 0 ? sp(f, C1.answers[k], SPR.bouncy) : 0;
                  return <Choice key={o} label={o} on={on} style={{ position: "absolute", top: row.y, left: chipX(row.w, oi), width: row.w }} />;
                }),
              )}
            </React.Fragment>
          ))}

          {/* recommendation (same wording as recommend() for a beginner who wants training + nutrition) */}
          <Card
            style={{
              position: "absolute",
              top: RES_Y,
              left: 40,
              width: 920,
              height: 460,
              opacity: resP,
              transform: `translateY(${(1 - resP) * 60}px)`,
              borderColor: L.navy,
              borderWidth: 2,
            }}
          >
            <Eyebrow>الباقة الأنسب لك</Eyebrow>
            <H size={48} style={{ marginTop: 8 }}>الباقة المكثفة</H>
            {[
              "الباقة المكثفة هي الأفضل للمبتدئين: متابعة أسبوعية و4 مكالمات زوم وشرح MyFitnessPal.",
              "وتُصمَّم لك بعد الاستبيان، مو جدول جاهز.",
            ].map((w, i) => {
              const p = ramp(f, [C1.why[i], C1.why[i] + 12]);
              return (
                <div key={w} style={{ display: "flex", gap: 14, marginTop: 14, opacity: p, transform: `translateX(${(1 - p) * -30}px)` }}>
                  <span style={{ color: L.cyanInk, fontSize: 28, fontWeight: 700 }}>✓</span>
                  <P size={25} muted={false}>{w}</P>
                </div>
              );
            })}
          </Card>
          <Btn style={{ position: "absolute", top: CTA_RECT[1], left: CTA_RECT[0], width: CTA_RECT[2] }} press={pressAt(f, C1.cta)}>
            اشترك في الباقة المكثفة
          </Btn>
          <Btn kind="ghost" style={{ position: "absolute", top: CTA_RECT[1], left: CTA_RECT[0] - 290, width: 270 }}>
            شوف تفاصيلها
          </Btn>
        </div>
        <SiteHeader />
        <Spotlight keys={spots} />
      </BrowserWindow>
      <MacCursor path={cursor} clicks={[C1.quizClick, ...C1.answers, C1.cta]} from={C1.cursorIn} to={S1} />
    </>
  );
};

export const pressAt = (f: number, at: number) => (f >= at - 3 && f < at + 8 ? 1 - Math.abs(f - at) / 8 : 0);
