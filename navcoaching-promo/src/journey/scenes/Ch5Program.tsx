import React from "react";
import { useCurrentFrame } from "remotion";
import { FONT, MONO } from "../../theme";
import { L } from "../theme";
import { J } from "../tl";
import { BrowserWindow, Rect, Spotlight } from "../parts/Chrome";
import { Alert, Card, P, SiteHeader, Status } from "../parts/Site";
import { ramp, sp, SPR } from "../../lib/motion";
import { useWindowIn } from "./common";

const C = J.ch5;
const [S0, S1] = J.segments.ch5 as [number, number];

// Sample day from the site's illustrative trainee file (public/shots/training.webp)
const ROWS = [
  ["Mid Leg Press", "الأمامية", "3", "12"],
  ["Hip Thrusts", "المؤخرة", "3", "10"],
  ["DB RDL", "الخلفية", "3", "10"],
  ["Lying Leg Curl", "الخلفية", "3", "10"],
  ["Leg Extension", "الأمامية", "3", "10"],
];
const WEEKS: [string, string, "ok" | "wait"][] = [
  ["✅", "الأسبوع 1 — تمت", "ok"],
  ["✅", "الأسبوع 2 — تمت", "ok"],
  ["⏳", "الأسبوع 3 — الأسبوع الحالي", "wait"],
];
const REPLY: Rect = [70, 690, 860, 120];

export const Ch5Program: React.FC = () => {
  const f = useCurrentFrame();
  const win = useWindowIn(S0, S1);
  const aOut = ramp(f, [C.switch - 10, C.switch + 4]);
  const bIn = ramp(f, [C.switch, C.switch + 16]);

  const spots: [number, Rect | null][] = [
    [S0, null],
    [C.weeks[2] + 4, [40, 312, 920, 64]],
    [C.reply - 16, null],
    [C.reply + 6, REPLY],
    [S1 - 10, null],
  ];

  return (
    <BrowserWindow style={win.style}>
      {/* A: training table */}
      {aOut < 1 && (
        <div style={{ position: "absolute", inset: 0, opacity: 1 - aOut, transform: `translateX(${aOut * 80}px)` }}>
          <P size={22} style={{ position: "absolute", top: 108, right: 40 }}>ملفاتي / جدول التمرين</P>
          <span style={{ position: "absolute", top: 104, left: 40, fontFamily: FONT, fontSize: 20, padding: "6px 14px", borderRadius: 99, background: L.cyanSoft, color: L.cyanInk }}>
            نموذج توضيحي
          </span>
          <Card style={{ position: "absolute", top: 160, left: 40, width: 920, height: 650, padding: 0, overflow: "hidden", boxSizing: "border-box" }}>
            <div style={{ height: 84, background: `linear-gradient(90deg, ${L.navy}, ${L.cyanInk})`, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 30px", direction: "ltr" }}>
              <span style={{ fontFamily: MONO, fontWeight: 700, fontSize: 30, color: "#fff" }}>DAY 1 — LOWER BODY</span>
              <span style={{ fontFamily: MONO, fontSize: 22, color: "#fff", border: "1.5px solid rgba(255,255,255,0.5)", borderRadius: 99, padding: "4px 14px" }}>WEEK 1</span>
            </div>
            <div style={{ display: "flex", height: 60, alignItems: "center", fontFamily: FONT, fontSize: 22, color: L.muted, borderBottom: `1px solid ${L.line}` }}>
              <span style={{ width: 80, textAlign: "center" }}>#</span>
              <span style={{ flex: 1 }}>التمرين والعضلة</span>
              <span style={{ width: 120, textAlign: "center" }}>جولات</span>
              <span style={{ width: 120, textAlign: "center" }}>تكرار</span>
              <span style={{ width: 110, textAlign: "center" }}>RIR</span>
            </div>
            {ROWS.map((r, i) => {
              const p = sp(f, C.rows[i], SPR.snappy);
              const hl = ramp(f, [C.rows[i], C.rows[i] + 20]);
              return (
                <div
                  key={r[0]}
                  style={{
                    height: 100,
                    display: "flex",
                    alignItems: "center",
                    borderBottom: `1px solid ${L.line}`,
                    opacity: Math.min(1, p * 2),
                    transform: `translateX(${(1 - p) * -80}px)`,
                    background: `rgba(76,197,237,${0.18 * (1 - hl)})`,
                  }}
                >
                  <span style={{ width: 80, textAlign: "center", fontFamily: MONO, fontSize: 26, color: L.muted }}>{String(i + 1).padStart(2, "0")}</span>
                  <span style={{ flex: 1 }}>
                    <div style={{ fontFamily: FONT, fontWeight: 600, fontSize: 30, color: L.heading, direction: "ltr", textAlign: "right" }}>{r[0]}</div>
                    <span style={{ fontFamily: FONT, fontSize: 20, color: L.cyanInk, background: L.cyanSoft, borderRadius: 99, padding: "2px 12px" }}>{r[1]}</span>
                  </span>
                  <span style={{ width: 120, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 32 }}>{r[2]}</span>
                  <span style={{ width: 120, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 32 }}>{r[3]}</span>
                  <span style={{ width: 110, textAlign: "center", fontFamily: MONO, fontWeight: 700, fontSize: 32, color: L.cyanInk }}>3</span>
                </div>
              );
            })}
          </Card>
        </div>
      )}
      {/* B: weekly reviews */}
      {bIn > 0 && (
        <div style={{ position: "absolute", inset: 0, opacity: bIn, transform: `translateX(${(1 - bIn) * -80}px)` }}>
          <Card style={{ position: "absolute", top: 110, left: 40, width: 920, height: 290, boxSizing: "border-box", padding: "24px 30px" }}>
            <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 30, color: L.heading, marginBottom: 10 }}>سجل المراجعات الأسبوعية</div>
            {WEEKS.map(([ico, t, tone], i) => {
              const p = sp(f, C.weeks[i], SPR.bouncy);
              return (
                <div key={t} style={{ display: "flex", alignItems: "center", gap: 14, height: 64, opacity: Math.min(1, p * 2), transform: `translateX(${(1 - p) * -40}px)` }}>
                  <span style={{ fontSize: 28 }}>{ico}</span>
                  <span style={{ fontFamily: FONT, fontWeight: 600, fontSize: 27, color: tone === "ok" ? L.heading : L.cyanInk }}>{t}</span>
                </div>
              );
            })}
          </Card>
          <Card style={{ position: "absolute", top: 430, left: 40, width: 920, height: 400, boxSizing: "border-box", padding: "24px 30px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontFamily: FONT, fontWeight: 700, fontSize: 28, color: L.heading }}>مراجعة الأسبوع 2</span>
              {f >= C.reply ? <Status tone="ok">وصل الرد</Status> : <Status tone="wait">بانتظار الرد</Status>}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "220px 1fr", rowGap: 10, marginTop: 16, fontFamily: FONT, fontSize: 24 }}>
              <span style={{ color: L.muted }}>الوزن هالأسبوع</span>
              <span style={{ color: L.text }}>70.7 كغ</span>
              <span style={{ color: L.muted }}>الالتزام بالتمرين</span>
              <span style={{ color: L.text }}>4 من 4 أيام</span>
            </div>
          </Card>
          <Alert
            tone="info"
            style={{
              position: "absolute",
              left: REPLY[0],
              top: REPLY[1],
              width: REPLY[2],
              height: REPLY[3],
              boxSizing: "border-box",
              opacity: ramp(f, [C.reply, C.reply + 12]),
              transform: `translateY(${(1 - ramp(f, [C.reply, C.reply + 14])) * 30}px)`,
            }}
          >
            <b>رد المدربة:</b> ممتاز! كمّل على نفس الجدول، ونزيد الخطوات 1,000 هالأسبوع.
          </Alert>
        </div>
      )}
      <SiteHeader account />
      <Spotlight keys={spots} />
    </BrowserWindow>
  );
};
