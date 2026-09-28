import React from "react";
import { useCurrentFrame } from "remotion";
import { FONT } from "../../theme";
import { L } from "../theme";
import { J } from "../tl";
import { BrowserWindow, MacCursor, Rect, Spotlight } from "../parts/Chrome";
import { Alert, Btn, Card, Check, Choice, Field, P, SiteHeader, Steps5 } from "../parts/Site";
import { ramp, sp, SPR } from "../../lib/motion";
import { pg, useWindowIn } from "./common";
import { pressAt } from "./Ch1Programs";

const C = J.ch2;
const [S0, S1] = J.segments.ch2 as [number, number];

// Step titles and options exactly as in CheckoutForm.tsx / intake.ts
const TITLES = ["الباقة والتواصل", "الهدف والتمرين", "الصحة والإصابات", "القياسات ونمط الحياة", "التوقعات والإرسال"];
const GOALS = ["نزول دهون", "بناء عضل", "نزول دهون + بناء عضل", "زيادة وزن", "لياقة وقوة", "أداء رياضي", "أخرى"];
const LEVELS = ["مبتدئ · أقل من 6 أشهر", "متوسط · 6 أشهر – سنتين", "متقدم · أكثر من سنتين"];
const PLACES = ["نادي", "البيت", "كلاهما"];
const col3 = (i: number) => 1000 - 40 - 293 - (i % 3) * 313;
const NEXT: Rect = [40, 764, 240, 72];

/** Visible step 1..5 at frame f (step 4 is passed through quickly on the way to 5). */
const stepAt = (f: number) => (f < C.next1 ? 1 : f < C.next2 ? 2 : f < C.next3 ? 3 : 5);
const viewA = (f: number, from: number, to: number) => {
  const a = ramp(f, [from, from + 12]) * (1 - ramp(f, [to - 8, to]));
  return { opacity: a, transform: `translateX(${(1 - ramp(f, [from, from + 14])) * -60}px)` };
};

export const Ch2Checkout: React.FC = () => {
  const f = useCurrentFrame();
  const win = useWindowIn(S0, S1);
  const step = stepAt(f);
  const barStep = f < C.next3 ? step : 3 + Math.min(2, (f - C.next3) / 8);
  const name = "نورة".slice(0, C.typeName.filter((t) => f >= t).length);
  const typing = f >= C.typeName[0] - 10 && f < C.typeName[3] + 30;

  const goalRect: Rect = [col3(2), 250, 293, 64];
  const levelRect: Rect = [col3(0), 520, 293, 64];
  const placeRect: Rect = [col3(0), 660, 293, 64];
  const SUBMIT: Rect = [40, 764, 520, 72];

  const spots: [number, Rect | null][] = [
    [S0, null],
    [C.typeName[0] - 14, [40, 350, 920, 110]],
    [C.typeName[3] + 30, null],
    [C.healthSpot, [40, 196, 920, 150]],
    [C.next3 - 20, null],
    [C.submit - 28, SUBMIT],
    [S1 - 8, null],
  ];
  const ctr = (r: Rect) => pg(r[0] + r[2] / 2, r[1] + r[3] / 2);
  const cursor: [number, number, number][] = [
    [S0 + 20, 980, 1500],
    [C.typeName[0] - 12, ...pg(700, 420)],
    [C.next1 - 30, ...pg(700, 420)],
    [C.next1 - 6, ...ctr(NEXT)],
    [C.choices[0] - 6, ...ctr(goalRect)],
    [C.choices[1] - 6, ...ctr(levelRect)],
    [C.choices[2] - 6, ...ctr(placeRect)],
    [C.next2 - 4, ...ctr(NEXT)],
    [C.next3 - 30, ...pg(500, 520)],
    [C.next3 - 4, ...ctr(NEXT)],
    [C.submit - 6, ...ctr(SUBMIT)],
    [S1, ...ctr(SUBMIT)],
  ];

  return (
    <>
      <BrowserWindow style={win.style}>
        <div style={{ position: "absolute", top: 112, left: 40, right: 40 }}>
          <Steps5 step={barStep} />
          <P size={24} style={{ marginTop: 14 }}>
            الخطوة {Math.floor(barStep)} من 5 — {TITLES[Math.floor(barStep) - 1]}
          </P>
        </div>

        {/* step 1 */}
        {step === 1 && (
          <div style={{ position: "absolute", inset: 0, ...viewA(f, S0, C.next1 + 1) }}>
            <Field label="الباقة والمدة" value="الباقة المكثفة ▾" style={{ position: "absolute", top: 196, left: 40, right: 40 }} />
            <P size={21} style={{ position: "absolute", top: 308, right: 40 }}>تدفعه بتحويل بنكي بعد إرسال الاستبيان.</P>
            <Field label="الاسم" value={name} placeholder="" caret={typing} style={{ position: "absolute", top: 350, left: 40, right: 40 }} />
            <Field label="رقم واتساب" value="+966  5X XXX XXXX" ltr style={{ position: "absolute", top: 478, left: 40, right: 40 }} />
            <div style={{ position: "absolute", top: 610, right: 40, fontFamily: FONT, fontWeight: 600, fontSize: 24, color: L.heading }}>الجنس</div>
            <Choice label="أنثى" on={f > C.typeName[3] + 20 ? 1 : 0} style={{ position: "absolute", top: 652, left: col3(0), width: 293 }} />
            <Choice label="ذكر" style={{ position: "absolute", top: 652, left: col3(1), width: 293 }} />
          </div>
        )}
        {/* step 2 */}
        {step === 2 && (
          <div style={{ position: "absolute", inset: 0, ...viewA(f, C.next1, C.next2 + 1) }}>
            <Legend y={200}>هدفك الرئيسي</Legend>
            {GOALS.map((g, i) => (
              <Choice key={g} label={g} on={i === 2 ? sp(f, C.choices[0], SPR.bouncy) : 0} style={{ position: "absolute", top: 250 + Math.floor(i / 3) * 74, left: col3(i), width: 293 }} />
            ))}
            <Legend y={470}>مستواك</Legend>
            {LEVELS.map((g, i) => (
              <Choice key={g} label={g} on={i === 0 ? sp(f, C.choices[1], SPR.bouncy) : 0} style={{ position: "absolute", top: 520, left: col3(i), width: 293 }} />
            ))}
            <Legend y={610}>مكان التمرين</Legend>
            {PLACES.map((g, i) => (
              <Choice key={g} label={g} on={i === 0 ? sp(f, C.choices[2], SPR.bouncy) : 0} style={{ position: "absolute", top: 660, left: col3(i), width: 293 }} />
            ))}
          </div>
        )}
        {/* step 3 */}
        {step === 3 && (
          <div style={{ position: "absolute", inset: 0, ...viewA(f, C.next2, C.next3 + 1) }}>
            <Alert tone="info" style={{ position: "absolute", top: 196, left: 40, right: 40, height: 150, boxSizing: "border-box" }}>
              هذه الأسئلة لسلامتك فقط، ولا تُحفظ على جهازك أثناء التعبئة، <b>ولا يطّلع عليها إلا المدربة.</b>
            </Alert>
            <Legend y={380}>هل عندك إصابة حالية أو ألم يحد من التمرين؟</Legend>
            <Choice label="لا" on={f > C.healthSpot + 30 ? 1 : 0} style={{ position: "absolute", top: 430, left: col3(0), width: 293 }} />
            <Choice label="نعم" style={{ position: "absolute", top: 430, left: col3(1), width: 293 }} />
            <Check on={f > C.healthSpot + 50} style={{ position: "absolute", top: 540, left: 40, right: 40 }}>
              أفهم أن البرنامج لا يغني عن استشارة الطبيب أو أخصائي العلاج الطبيعي عند وجود حالة صحية أو إصابة.
            </Check>
          </div>
        )}
        {/* step 5 */}
        {step === 5 && (
          <div style={{ position: "absolute", inset: 0, ...viewA(f, C.next3, S1 + 20) }}>
            <Field label="ماذا تتوقع مني أثناء التدريب؟" value="متابعة قريبة، وتعديل البرنامج حسب تقدّمي." style={{ position: "absolute", top: 196, left: 40, right: 40 }} />
            <Check on style={{ position: "absolute", top: 330, left: 40, right: 40 }}>أؤكد صحة البيانات وأوافق على الشروط وسياسة الخصوصية.</Check>
            <Check on style={{ position: "absolute", top: 400, left: 40, right: 40 }}>أوافق على التواصل معي عبر واتساب بخصوص طلبي.</Check>
            <Card style={{ position: "absolute", top: 490, left: 40, right: 40, padding: 24, boxShadow: "none" }}>
              <P size={23} muted={false}>
                <b>بعد الإرسال:</b> يظهر لك رقم طلبك والمبلغ وبيانات التحويل في حسابك. حوّل وارفع صورة الإيصال من صفحة الطلب.
              </P>
            </Card>
          </div>
        )}
        {step < 5 ? (
          <Btn style={{ position: "absolute", top: NEXT[1], left: NEXT[0], width: NEXT[2] }} press={pressAt(f, step === 1 ? C.next1 : step === 2 ? C.next2 : C.next3)}>
            التالي
          </Btn>
        ) : (
          <Btn kind="cyan" style={{ position: "absolute", top: SUBMIT[1], left: SUBMIT[0], width: SUBMIT[2] }} press={pressAt(f, C.submit)}>
            أرسل الاستبيان وانتقل للدفع
          </Btn>
        )}
        {step > 1 && (
          <Btn kind="ghost" style={{ position: "absolute", top: NEXT[1], right: 40, width: 200, opacity: step === 5 ? 0 : 1 }}>
            رجوع
          </Btn>
        )}
        <SiteHeader account />
        <Spotlight keys={spots} />
      </BrowserWindow>
      <MacCursor path={cursor} clicks={[C.next1, ...C.choices, C.next2, C.next3, C.submit]} from={S0 + 20} to={S1} />
    </>
  );
};

const Legend: React.FC<{ y: number; children: React.ReactNode }> = ({ y, children }) => (
  <div style={{ position: "absolute", top: y, right: 40, left: 40, fontFamily: FONT, fontWeight: 600, fontSize: 27, color: L.heading }}>
    {children} <span style={{ color: L.err }}>*</span>
  </div>
);
