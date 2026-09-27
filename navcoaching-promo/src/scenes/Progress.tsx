import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT, glass, MONO } from "../theme";
import { Eyebrow, KWord } from "../components/Brand";
import { Tag } from "../components/Ui";
import { clamp, cues, pulse, ramp, sp, SPR } from "../lib/motion";

const U = cues.ui;
const [S, E] = cues.scenes.progress;

// Weekly average weight from the site's illustrative progress board (labelled "EXAMPLE ONLY" there)
const WEEKS = ["BEFORE", "W1", "W2", "W3", "W4"];
const AVG = [72.3, 71.9, 71.3, 70.7, 70.4];

const CH_W = 840;
const CH_H = 300;
const yOf = (v: number) => interpolate(v, [70, 72.8], [CH_H - 20, 20]);
const xOf = (i: number) => 40 + (i * (CH_W - 80)) / 4;

export const Progress: React.FC = () => {
  const f = useCurrentFrame();
  const exit = ramp(f, [E - 30, E], [0, 1], (t) => t * t * t);
  const camZ = 1 + exit * 1.8;

  const c1 = sp(f, S + 4, SPR.soft);
  const c2 = sp(f, S + 20, SPR.soft);
  const c3 = sp(f, S + 30, SPR.soft);

  // line draws through the points on their cue frames
  const pts = AVG.map((v, i) => [xOf(i), yOf(v)] as const);
  const drawIdx = interpolate(f, [U.chartPoints[0] - 6, ...U.chartPoints.slice(1)], [0, 1, 2, 3, 4], clamp);
  const seg = Math.floor(drawIdx);
  const frac = drawIdx - seg;
  const drawn: [number, number][] = pts.slice(0, seg + 1).map((p) => [p[0], p[1]]);
  if (seg < 4) {
    const [x0, y0] = pts[seg];
    const [x1, y1] = pts[seg + 1];
    drawn.push([x0 + (x1 - x0) * frac, y0 + (y1 - y0) * frac]);
  }
  const lineD = drawn.map((p, i) => `${i ? "L" : "M"}${p[0]},${p[1]}`).join(" ");
  const areaD = `${lineD} L${drawn[drawn.length - 1][0]},${CH_H} L${drawn[0][0]},${CH_H} Z`;
  const shown = Math.min(4, Math.max(0, Math.floor(drawIdx + 0.001)));
  const current = interpolate(drawIdx, [0, 1, 2, 3, 4], AVG, clamp);
  const delta = sp(f, U.chartPoints[4] + 6, SPR.bouncy);

  const ring = ramp(f, [U.ringStart, U.ringEnd], [0, 0.99], (t) => 1 - Math.pow(1 - t, 2.2));
  const steps = Math.round((ring / 0.99) * 69000);
  const R = 118;
  const circ = 2 * Math.PI * R;
  const ringDone = pulse(f, U.ringEnd, 24);

  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      <AbsoluteFill style={{ transform: `scale(${camZ})`, opacity: 1 - ramp(f, [E - 12, E]), filter: exit > 0.05 ? `blur(${exit * 12}px)` : undefined }}>
        <div style={{ position: "absolute", top: 210, right: 90, left: 90 }}>
          <Eyebrow text="لوحة التقدم" at={S} />
          <div style={{ marginTop: 14, display: "flex", gap: 28, flexWrap: "wrap", alignItems: "baseline" }}>
            <KWord text="تقدمك" at={S} size={112} />
            <KWord text="واضح" at={S + 8} size={112} color={C.cyan} glow />
          </div>
          <div style={{ marginTop: -6 }}>
            <KWord text="أسبوع بأسبوع" at={S + 18} size={70} weight={400} color={C.muted} from="up" />
          </div>
        </div>

        {/* weight chart */}
        <div
          style={{
            position: "absolute",
            left: 60,
            top: 600,
            width: 960,
            height: 520,
            ...glass,
            padding: "34px 40px",
            opacity: Math.min(1, c1 * 2),
            transform: `perspective(1600px) translateZ(${(1 - c1) * -700}px) rotateX(${(1 - c1) * 30}deg)`,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <div>
              <div style={{ fontFamily: FONT, fontSize: 34, color: C.muted }}>متوسط الوزن الأسبوعي</div>
              <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 84, color: C.text, direction: "ltr", textAlign: "right" }}>
                {current.toFixed(1)}
                <span style={{ fontSize: 36, color: C.muted, marginLeft: 10 }}>kg</span>
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 14 }}>
              <Tag style={{ fontSize: 22, color: C.muted, border: "1px solid rgba(169,186,208,0.35)", background: "rgba(169,186,208,0.08)" }}>
                نموذج توضيحي
              </Tag>
              <div
                style={{
                  fontFamily: MONO,
                  fontWeight: 700,
                  fontSize: 40,
                  color: C.ink,
                  background: C.ok,
                  padding: "8px 22px",
                  borderRadius: 16,
                  direction: "ltr",
                  opacity: Math.min(1, delta * 2),
                  transform: `scale(${interpolate(delta, [0, 1], [0.3, 1])})`,
                  boxShadow: `0 0 40px rgba(111,211,156,0.6)`,
                }}
              >
                −1.9 kg
              </div>
            </div>
          </div>
          <svg width={CH_W} height={CH_H + 50} style={{ marginTop: 10, direction: "ltr", overflow: "visible" }}>
            <defs>
              <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor={C.cyan} stopOpacity="0.45" />
                <stop offset="1" stopColor={C.cyan} stopOpacity="0" />
              </linearGradient>
            </defs>
            {[0, 1, 2, 3].map((k) => (
              <line key={k} x1={0} x2={CH_W} y1={20 + k * 87} y2={20 + k * 87} stroke="rgba(76,197,237,0.12)" strokeWidth={2} />
            ))}
            {f >= U.chartPoints[0] - 6 && (
              <>
                <path d={areaD} fill="url(#area)" />
                <path d={lineD} fill="none" stroke={C.cyan} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" style={{ filter: `drop-shadow(0 0 10px ${C.cyan})` }} />
              </>
            )}
            {pts.map(([x, y], i) => {
              const p = sp(f, U.chartPoints[i], SPR.bouncy);
              const hot = pulse(f, U.chartPoints[i], 20);
              return (
                <g key={i} opacity={f >= U.chartPoints[i] ? 1 : 0}>
                  <circle cx={x} cy={y} r={10 + 26 * hot} fill={C.cyan} opacity={0.35 * hot} />
                  <circle cx={x} cy={y} r={12 * p} fill={C.ink} stroke="#fff" strokeWidth={5} />
                  <text x={x} y={y - 26} textAnchor="middle" fontFamily={MONO} fontWeight={700} fontSize={26} fill={i <= shown ? C.text : "transparent"} opacity={p}>
                    {AVG[i].toFixed(1)}
                  </text>
                </g>
              );
            })}
            {WEEKS.map((w, i) => (
              <text key={w} x={xOf(i)} y={CH_H + 44} textAnchor="middle" fontFamily={MONO} fontSize={24} fill={C.muted}>
                {w}
              </text>
            ))}
          </svg>
        </div>

        {/* steps ring */}
        <div
          style={{
            position: "absolute",
            right: 60,
            top: 1160,
            width: 468,
            height: 470,
            ...glass,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            paddingTop: 30,
            opacity: Math.min(1, c2 * 2),
            transform: `perspective(1600px) translateZ(${(1 - c2) * -700}px) rotateY(${(1 - c2) * -30}deg)`,
            boxShadow: `${glass.boxShadow}, 0 0 ${80 * ringDone}px rgba(76,197,237,${0.7 * ringDone})`,
          }}
        >
          <div style={{ fontFamily: FONT, fontSize: 32, color: C.muted }}>هدف الخطوات الأسبوعي</div>
          <div style={{ position: "relative", width: 290, height: 290, marginTop: 12 }}>
            <svg width={290} height={290} style={{ transform: "rotate(-90deg)" }}>
              <circle cx={145} cy={145} r={R} fill="none" stroke="rgba(76,197,237,0.15)" strokeWidth={22} />
              <circle
                cx={145}
                cy={145}
                r={R}
                fill="none"
                stroke={C.cyan}
                strokeWidth={22}
                strokeLinecap="round"
                strokeDasharray={circ}
                strokeDashoffset={circ * (1 - ring)}
                style={{ filter: `drop-shadow(0 0 12px ${C.cyan})` }}
              />
            </svg>
            <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", direction: "ltr" }}>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 76, color: C.text, transform: `scale(${1 + ringDone * 0.12})` }}>
                  {Math.round(ring * 100)}%
                </div>
              </div>
            </div>
          </div>
          <div style={{ marginTop: 8, fontFamily: MONO, fontSize: 28, color: C.muted, direction: "ltr" }}>
            <span style={{ color: C.text }}>{steps.toLocaleString("en-US")}</span> / 70,000
          </div>
        </div>

        {/* weekly review checklist */}
        <div
          style={{
            position: "absolute",
            left: 60,
            top: 1160,
            width: 468,
            height: 470,
            ...glass,
            padding: "30px 34px",
            opacity: Math.min(1, c3 * 2),
            transform: `perspective(1600px) translateZ(${(1 - c3) * -700}px) rotateY(${(1 - c3) * 30}deg)`,
          }}
        >
          <div style={{ fontFamily: FONT, fontSize: 32, color: C.muted }}>المراجعة الأسبوعية</div>
          {["القياسات", "الخطوات", "تقييم التمرين"].map((t, k) => {
            const at = U.checks[k];
            const p = sp(f, at, SPR.bouncy);
            const on = f >= at;
            return (
              <div key={t} style={{ display: "flex", alignItems: "center", gap: 20, marginTop: 34 }}>
                <div
                  style={{
                    width: 64,
                    height: 64,
                    borderRadius: 18,
                    border: `3px solid ${on ? C.ok : "rgba(169,186,208,0.4)"}`,
                    background: on ? "rgba(111,211,156,0.18)" : "transparent",
                    display: "grid",
                    placeItems: "center",
                    boxShadow: on ? `0 0 ${24 * pulse(f, at, 20) + 8}px rgba(111,211,156,0.6)` : undefined,
                  }}
                >
                  <span style={{ color: C.ok, fontSize: 40, fontWeight: 700, transform: `scale(${p})` }}>✓</span>
                </div>
                <span style={{ fontFamily: FONT, fontSize: 40, fontWeight: 500, color: on ? C.text : C.muted }}>{t}</span>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
