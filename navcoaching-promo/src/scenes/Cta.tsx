import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT, MONO } from "../theme";
import { KWord, LogoMark, Shockwave } from "../components/Brand";
import { Cursor } from "../components/Ui";
import { cues, pulse, ramp, sp, SPR } from "../lib/motion";

const HT = cues.hits;
const U = cues.ui;
const URL = "navcoaching.com";

export const Cta: React.FC = () => {
  const f = useCurrentFrame();
  const slam = sp(f, HT.final, SPR.heavy);
  const logoScale = interpolate(slam, [0, 1], [3.2, 1]);
  const settle = Math.sin((f - HT.final) / 20) * 0.01;

  const typed = U.urlType.filter((t) => f >= t).length;
  const btn = sp(f, HT.final + 22, SPR.bouncy);
  const press = pulse(f, U.ctaClick, 10, 1);
  const clickGlow = pulse(f, U.ctaClick, 26, 1.5);
  const tag = ramp(f, [HT.final + 10, HT.final + 26]);

  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <Shockwave at={HT.final} y={620} size={1.1} />

      <div
        style={{
          position: "absolute",
          top: 450,
          transform: `scale(${logoScale + settle})`,
          opacity: Math.min(1, slam * 3),
        }}
      >
        <LogoMark width={560} glow={0.5 + 1.4 * pulse(f, HT.final, 40)} sheen={ramp(f, [HT.final + 30, HT.final + 70])} />
      </div>

      <div
        style={{
          position: "absolute",
          top: 750,
          textAlign: "center",
          fontFamily: FONT,
          fontWeight: 700,
          fontSize: 80,
          letterSpacing: interpolate(tag, [0, 1], [40, 6]),
          color: C.text,
          opacity: tag,
          textShadow: "0 0 30px rgba(76,197,237,0.55)",
        }}
      >
        Nav Coaching
      </div>

      <div style={{ position: "absolute", top: 910, width: "100%", display: "flex", justifyContent: "center", gap: 30, direction: "rtl" }}>
        <KWord text="تدريب" at={HT.final + 12} size={112} from="up" />
        <KWord text="مبني" at={HT.final + 16} size={112} from="up" />
        <KWord text="عليك" at={HT.final + 20} size={112} from="up" color={C.cyan} glow />
      </div>

      {/* CTA button */}
      <div
        style={{
          position: "absolute",
          top: 1190,
          display: "flex",
          alignItems: "center",
          gap: 22,
          padding: "34px 80px",
          borderRadius: 999,
          direction: "rtl",
          background: `linear-gradient(100deg, ${C.cyan}, #8ee3ff 50%, ${C.cyan})`,
          color: C.ink,
          fontFamily: FONT,
          fontWeight: 700,
          fontSize: 64,
          opacity: Math.min(1, btn * 2),
          transform: `scale(${interpolate(btn, [0, 1], [0.4, 1]) * (1 - press * 0.07)})`,
          boxShadow: `0 0 ${50 + 120 * clickGlow}px rgba(76,197,237,${0.6 + 0.4 * clickGlow}), 0 20px 50px rgba(0,0,0,0.5)`,
        }}
      >
        اختر برنامجك
        <span style={{ fontSize: 60, transform: `translateX(${-12 * clickGlow}px)` }}>←</span>
      </div>

      {/* URL typing */}
      <div
        style={{
          position: "absolute",
          top: 1400,
          padding: "20px 44px",
          borderRadius: 22,
          border: "2px solid rgba(76,197,237,0.4)",
          background: "rgba(7,20,42,0.7)",
          fontFamily: MONO,
          fontWeight: 700,
          fontSize: 54,
          letterSpacing: 2,
          color: C.text,
          opacity: ramp(f, [U.urlType[0] - 8, U.urlType[0]]),
          direction: "ltr",
          minWidth: 640,
          textAlign: "center",
        }}
      >
        <span style={{ color: C.cyan }}>{URL.slice(0, Math.min(typed, 3))}</span>
        {URL.slice(3, typed)}
        <span style={{ opacity: f % 30 < 15 ? 1 : 0, color: C.cyan }}>|</span>
      </div>

      <Cursor
        path={[
          [1148, 900, 1760],
          [1172, 640, 1260],
          [1180, 640, 1260],
          [1199, 760, 1330],
        ]}
        clicks={[U.ctaClick]}
      />
    </AbsoluteFill>
  );
};
