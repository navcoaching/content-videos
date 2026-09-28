import React from "react";
import { useCurrentFrame } from "remotion";
import { FONT, MONO } from "../../theme";
import { L } from "../theme";
import { J } from "../tl";
import { BrowserWindow, MacCursor, Rect, Spotlight } from "../parts/Chrome";
import { Btn, Card, Choice, Eyebrow, Field, H, IconFile, P, SiteHeader } from "../parts/Site";
import { interpolate } from "remotion";
import { clamp, pulse, ramp } from "../../lib/motion";
import { pg, useWindowIn } from "./common";
import { pressAt } from "./Ch1Programs";

const C = J.ch6;
const [S0, S1] = J.segments.ch6 as [number, number];

const typed = (f: number, text: string, cues: number[]) => text.slice(0, Math.round((cues.filter((t) => f >= t).length / cues.length) * text.length));
const GOAL: Rect = [40, 520, 920, 110];
const RESULT: Rect = [40, 660, 920, 150];
const DL: Rect = [40, 560, 300, 72];
const RESULT_KCAL = 1720; // illustrative output for the sample inputs shown

export const Ch6Tools: React.FC = () => {
  const f = useCurrentFrame();
  const win = useWindowIn(S0, S1);
  const aOut = ramp(f, [C.plans - 10, C.plans + 4]);
  const bIn = ramp(f, [C.plans, C.plans + 16]);
  const kcal = Math.round(interpolate(f, [C.calc, C.calcEnd], [0, RESULT_KCAL], { ...clamp, easing: (t) => 1 - Math.pow(1 - t, 3) }) / 10) * 10;

  const spots: [number, Rect | null][] = [
    [S0, null],
    [C.goal - 18, GOAL],
    [C.calc - 4, RESULT],
    [C.plans - 10, null],
    [C.download - 24, [DL[0], DL[1], DL[2], DL[3]]],
    [S1 - 10, null],
  ];
  const ctr = (r: Rect) => pg(r[0] + r[2] / 2, r[1] + r[3] / 2);
  const cursor: [number, number, number][] = [
    [C.goal - 30, 980, 1560],
    [C.goal - 6, ...pg(500, 590)],
    [C.plans, ...pg(500, 700)],
    [C.download - 6, ...ctr(DL)],
    [S1, ...ctr(DL)],
  ];

  return (
    <>
      <BrowserWindow style={win.style}>
        {aOut < 1 && (
          <div style={{ position: "absolute", inset: 0, opacity: 1 - aOut }}>
            <Eyebrow style={{ position: "absolute", top: 110, right: 40 }}>أداة مجانية</Eyebrow>
            <H size={44} style={{ position: "absolute", top: 146, right: 40 }}>حاسبة السعرات اليومية</H>
            <Choice label="أعرف نسبة الدهون" style={{ position: "absolute", top: 222, right: 40, width: 440 }} />
            <Choice label="ما أعرف نسبة الدهون" on={1} style={{ position: "absolute", top: 222, left: 40, width: 440 }} />
            <Field label="الوزن (كغ)" value={typed(f, "65", C.type.slice(0, 2))} caret={f >= C.type[0] - 6 && f < C.type[2] - 6} ltr style={{ position: "absolute", top: 310, right: 40, width: 280 }} />
            <Field label="الطول (سم)" value={typed(f, "165", C.type.slice(2, 4))} caret={f >= C.type[2] - 6 && f < C.type[4] - 6} ltr style={{ position: "absolute", top: 310, right: 360, width: 280 }} />
            <Field label="العمر" value={typed(f, "28", C.type.slice(4, 6))} caret={f >= C.type[4] - 6 && f < C.goal - 20} ltr style={{ position: "absolute", top: 310, left: 40, width: 280 }} />
            <Field
              label="الهدف"
              value={f >= C.goal ? "تنشيف تدريجي (عجز 10٪) ▾" : "المحافظة على الوزن ▾"}
              style={{ position: "absolute", top: GOAL[1], left: GOAL[0], width: GOAL[2], transform: `scale(${1 + 0.03 * pulse(f, C.goal, 12)})` }}
            />
            <div
              style={{
                position: "absolute",
                left: RESULT[0],
                top: RESULT[1],
                width: RESULT[2],
                height: RESULT[3],
                boxSizing: "border-box",
                borderRadius: 22,
                background: L.ink,
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "0 36px",
                opacity: ramp(f, [C.calc - 8, C.calc + 4]),
              }}
            >
              <div>
                <div style={{ fontFamily: FONT, fontSize: 26, color: "#a9bad0" }}>سعراتك اليومية لهدفك</div>
                <span style={{ fontFamily: FONT, fontSize: 20, color: L.cyan }}>مثال توضيحي</span>
              </div>
              <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 78, color: L.cyan, direction: "ltr", transform: `scale(${1 + 0.08 * pulse(f, C.calcEnd, 16)})` }}>
                {kcal.toLocaleString("en-US")}
                <span style={{ fontFamily: FONT, fontSize: 28, color: "#fff", marginLeft: 12 }}>سعرة</span>
              </div>
            </div>
          </div>
        )}
        {bIn > 0 && (
          <div style={{ position: "absolute", inset: 0, opacity: bIn, transform: `translateY(${(1 - bIn) * 40}px)` }}>
            <Eyebrow style={{ position: "absolute", top: 110, right: 40 }}>حسابي</Eyebrow>
            <H size={44} style={{ position: "absolute", top: 146, right: 40 }}>جداولي المجانية</H>
            <Card style={{ position: "absolute", top: 240, left: 40, width: 920, height: 420, boxSizing: "border-box" }}>
              <div style={{ display: "flex", gap: 22, alignItems: "center" }}>
                <span style={{ width: 96, height: 96, borderRadius: 24, background: L.cyanSoft, display: "grid", placeItems: "center" }}>
                  <IconFile size={52} color={L.cyanInk} />
                </span>
                <div>
                  <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 34, color: L.heading }}>جدول مجاني</div>
                  <P size={23}>تبدأ فيه اليوم، وتحمّله PDF من حسابك.</P>
                </div>
              </div>
            </Card>
            <Btn style={{ position: "absolute", top: DL[1], left: DL[0], width: DL[2] }} press={pressAt(f, C.download)}>
              تحميل PDF
            </Btn>
          </div>
        )}
        <SiteHeader account />
        <Spotlight keys={spots} />
      </BrowserWindow>
      <MacCursor path={cursor} clicks={[C.goal, C.download]} from={C.goal - 30} to={S1} />
    </>
  );
};
