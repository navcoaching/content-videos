import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { FONT, MONO } from "../../theme";
import { L, SHADOW_2 } from "../theme";
import { J } from "../tl";
import { LogoMark } from "../../components/Brand";
import { MacCursor } from "../parts/Chrome";
import { pulse, ramp, sp, SPR } from "../../lib/motion";

const O = J.outro;
const URL = "navcoaching.com";

const RECAP = [
  { t: "برنامج مبني عليك", img: "shots/training.webp", dot: L.cyan },
  { t: "متابعة كل أسبوع", img: "shots/weekly-review.webp", dot: L.navy },
  { t: "كل شي في حسابك", img: "shots/progress.webp", dot: L.ok },
];

export const Outro: React.FC = () => {
  const f = useCurrentFrame();
  const cardsOut = ramp(f, [O.cardsOut, O.cardsOut + 24], [0, 1], (t) => t * t);
  const start = sp(f, O.start, SPR.slam);
  const startUp = ramp(f, [O.logo - 20, O.logo + 10]);
  const logo = sp(f, O.logo, SPR.heavy);
  const typed = O.urlType.filter((t) => f >= t).length;
  const btn = sp(f, O.button, SPR.bouncy);
  const press = f >= O.click - 3 && f < O.click + 8 ? 1 - Math.abs(f - O.click) / 8 : 0;
  const glow = pulse(f, O.click, 30, 1.5);

  return (
    <AbsoluteFill style={{ direction: "rtl", alignItems: "center" }}>
      {RECAP.map((r, i) => {
        const p = sp(f, O.cards[i], SPR.snappy);
        if (f < O.cards[i] || cardsOut >= 1) return null;
        return (
          <div
            key={r.t}
            style={{
              position: "absolute",
              top: 520 + i * 250,
              left: 80,
              right: 80,
              height: 220,
              borderRadius: 30,
              background: "#fff",
              boxShadow: SHADOW_2,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0 24px 0 20px",
              opacity: Math.min(1, p * 2) * (1 - cardsOut),
              transform: `translateY(${(1 - p) * 80 - cardsOut * (300 + i * 80)}px) scale(${0.9 + 0.1 * p})`,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 18, fontFamily: FONT, fontWeight: 700, fontSize: 52, color: L.heading }}>
              <span style={{ width: 18, height: 18, borderRadius: "50%", background: r.dot }} />
              {r.t}
            </div>
            <div style={{ width: 330, height: 180, borderRadius: 18, overflow: "hidden", border: `1px solid ${L.line}` }}>
              <Img src={staticFile(r.img)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "right top" }} />
            </div>
          </div>
        );
      })}

      {f >= O.start && (
        <div
          style={{
            position: "absolute",
            top: interpolate(startUp, [0, 1], [820, 930]),
            fontFamily: FONT,
            fontWeight: 700,
            fontSize: interpolate(startUp, [0, 1], [170, 96]),
            color: L.heading,
            opacity: Math.min(1, start * 2),
            transform: `scale(${interpolate(start, [0, 1], [1.5, 1])})`,
          }}
        >
          ابدأ{" "}
          <span style={{ backgroundImage: `linear-gradient(${L.cyan}, ${L.cyan})`, backgroundSize: `${ramp(f, [O.start + 8, O.start + 24]) * 100}% 38%`, backgroundPosition: "right 88%", backgroundRepeat: "no-repeat", padding: "0 6px" }}>
            صح.
          </span>
        </div>
      )}

      {f >= O.logo && (
        <>
          <div style={{ position: "absolute", top: 470, transform: `scale(${interpolate(logo, [0, 1], [2.2, 1])})`, opacity: Math.min(1, logo * 3) }}>
            <LogoMark width={440} glow={0.25 + 0.6 * pulse(f, O.logo, 30)} sheen={ramp(f, [O.logo + 30, O.logo + 70])} />
          </div>
          <div style={{ position: "absolute", top: 690, fontFamily: FONT, fontWeight: 700, fontSize: 76, color: L.navy, opacity: ramp(f, [O.logo + 10, O.logo + 26]) }}>Nav Coaching</div>
        </>
      )}

      {f >= O.urlType[0] - 8 && (
        <div
          style={{
            position: "absolute",
            top: 1150,
            padding: "18px 44px",
            borderRadius: 22,
            background: "#fff",
            border: `2px solid ${L.line}`,
            boxShadow: SHADOW_2,
            fontFamily: MONO,
            fontWeight: 700,
            fontSize: 54,
            color: L.heading,
            direction: "ltr",
            minWidth: 620,
            textAlign: "center",
            opacity: ramp(f, [O.urlType[0] - 8, O.urlType[0]]),
          }}
        >
          <span style={{ color: L.cyanInk }}>{URL.slice(0, Math.min(typed, 3))}</span>
          {URL.slice(3, typed)}
          <span style={{ opacity: f % 30 < 15 ? 1 : 0, color: L.cyan }}>|</span>
        </div>
      )}

      {f >= O.button && (
        <div
          style={{
            position: "absolute",
            top: 1320,
            display: "flex",
            alignItems: "center",
            gap: 16,
            height: 110,
            padding: "0 70px",
            borderRadius: 999,
            background: L.navy,
            color: "#fff",
            fontFamily: FONT,
            fontWeight: 700,
            fontSize: 54,
            opacity: Math.min(1, btn * 2),
            transform: `scale(${interpolate(btn, [0, 1], [0.5, 1]) * (1 - press * 0.06)})`,
            boxShadow: `0 16px 40px rgba(40,77,160,${0.3 + 0.4 * glow}), 0 0 0 ${glow * 18}px rgba(76,197,237,${0.35 * glow})`,
          }}
        >
          اختر برنامجك <span>←</span>
        </div>
      )}
      <MacCursor
        path={[
          [O.button + 10, 900, 1700],
          [O.click - 6, 640, 1380],
          [J.durationInFrames, 760, 1520],
        ]}
        clicks={[O.click]}
        from={O.button + 10}
        to={J.durationInFrames + 20}
      />
    </AbsoluteFill>
  );
};
