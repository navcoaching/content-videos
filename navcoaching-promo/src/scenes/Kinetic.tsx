import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";
import { C, FONT, W } from "../theme";
import { KWord } from "../components/Brand";
import { clamp, cues, ramp, sp, SPR } from "../lib/motion";

const HT = cues.hits;

export const Kinetic: React.FC = () => {
  const f = useCurrentFrame();

  // hero stack pushes back in depth once the counter-statement lands
  const back = ramp(f, [HT.notReady - 6, HT.notReady + 20]);
  const pushIn = ramp(f, [392, 420], [0, 1], (t) => t * t);
  const stackScale = 1 - back * 0.14 + pushIn * 0.12;
  const stackY = 190 - back * 330;

  const breathe = f > HT.wordC + 20 ? Math.sin((f - HT.wordC) / 16) * 0.01 : 0;

  // "مو جدول جاهز" -> strike -> glitch -> gone
  const nr = sp(f, HT.notReady, SPR.bouncy);
  const strike = ramp(f, [HT.strike - 4, HT.strike + 6], [0, 1], (t) => 1 - Math.pow(1 - t, 3));
  const glitchOn = f >= HT.glitch && f < HT.glitch + 14;
  const nrOut = ramp(f, [HT.glitch + 8, HT.glitch + 18]);

  // closing pill: tailored after the questionnaire
  const pill = sp(f, 360, SPR.bouncy);
  const pillExit = ramp(f, [398, 410]);

  const slices = new Array(6).fill(0).map((_, i) => ({
    off: glitchOn ? (random(`g${i}-${Math.floor(f / 2)}`) - 0.5) * 90 : 0,
  }));

  return (
    <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", direction: "rtl" }}>
      <div
        style={{
          position: "absolute",
          top: 330,
          width: W,
          textAlign: "center",
          transform: `translateY(${stackY}px) scale(${stackScale + breathe})`,
        }}
      >
        <div>
          <KWord text="تدريب" at={HT.wordA} size={200} />
        </div>
        <div style={{ marginTop: -10 }}>
          <KWord text="مبني" at={HT.wordB} size={200} />
        </div>
        <div style={{ marginTop: 0 }}>
          <KWord
            text="عليك"
            at={HT.wordC}
            size={300}
            gradient={`linear-gradient(100deg, #ffffff 0%, ${C.cyan} 35%, #7fdcff ${
              interpolate(f, [HT.wordC, HT.wordC + 80], [40, 120], clamp)
            }%, ${C.cyan} 100%)`}
          />
        </div>
      </div>

      {/* counter-statement */}
      <div
        style={{
          position: "absolute",
          top: 1180,
          width: W,
          display: "flex",
          justifyContent: "center",
          opacity: f >= HT.notReady ? 1 - nrOut : 0,
        }}
      >
        <div style={{ position: "relative", transform: `scale(${interpolate(nr, [0, 1], [0.6, 1])})`, opacity: Math.min(1, nr * 2) }}>
          {glitchOn ? (
            slices.map((s, i) => (
              <div
                key={i}
                style={{
                  position: i === 0 ? "relative" : "absolute",
                  inset: i === 0 ? undefined : 0,
                  clipPath: `inset(${(i * 100) / 6}% 0 ${100 - ((i + 1) * 100) / 6}% 0)`,
                  transform: `translateX(${s.off}px)`,
                }}
              >
                <NotReady strike={strike} glitch />
              </div>
            ))
          ) : (
            <NotReady strike={strike} />
          )}
        </div>
      </div>

      {/* bridge pill */}
      <div
        style={{
          position: "absolute",
          top: 1200,
          display: "flex",
          alignItems: "center",
          gap: 20,
          padding: "26px 48px",
          borderRadius: 999,
          background: "linear-gradient(90deg, rgba(40,77,160,0.55), rgba(76,197,237,0.30))",
          border: `2px solid ${C.cyan}`,
          boxShadow: `0 0 50px rgba(76,197,237,0.45)`,
          fontFamily: FONT,
          fontWeight: 600,
          fontSize: 52,
          color: C.text,
          opacity: f >= 360 ? Math.min(1, pill * 2) * (1 - pillExit) : 0,
          transform: `scale(${interpolate(pill, [0, 1], [0.5, 1])}) translateY(${pillExit * -30}px)`,
        }}
      >
        <span
          style={{
            width: 56,
            height: 56,
            borderRadius: "50%",
            background: C.cyan,
            color: C.ink,
            display: "grid",
            placeItems: "center",
            fontSize: 38,
            fontWeight: 700,
          }}
        >
          ✓
        </span>
        مخصص لك بعد الاستبيان
      </div>
    </AbsoluteFill>
  );
};

const NotReady: React.FC<{ strike: number; glitch?: boolean }> = ({ strike, glitch }) => (
  <div
    style={{
      position: "relative",
      fontFamily: FONT,
      fontWeight: 500,
      fontSize: 110,
      color: glitch ? "#ff5f8a" : C.muted,
      opacity: 1 - strike * 0.35,
      padding: "0 20px",
      textShadow: glitch ? "6px 0 0 rgba(40,220,255,0.8), -6px 0 0 rgba(255,40,110,0.8)" : "none",
    }}
  >
    مو جدول جاهز
    <div
      style={{
        position: "absolute",
        right: 0,
        top: "54%",
        height: 12,
        width: `${strike * 100}%`,
        background: C.cyan,
        boxShadow: `0 0 24px ${C.cyan}`,
        borderRadius: 6,
        transform: "rotate(-4deg)",
      }}
    />
  </div>
);
