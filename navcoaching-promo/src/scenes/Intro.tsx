import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT, H, MONO } from "../theme";
import { LogoMark, Shockwave } from "../components/Brand";
import { clamp, cues, pulse, ramp, sp, SPR } from "../lib/motion";

const DROP = cues.hits.drop;
const [s1, s2, s3] = cues.ui.logoSlashes;

export const Intro: React.FC = () => {
  const f = useCurrentFrame();

  // three slices of the NAV mark fly in on the three ticks
  const a = sp(f, s1 - 6, SPR.snappy);
  const b = sp(f, s2 - 6, SPR.snappy);
  const c = sp(f, s3 - 6, SPR.snappy);
  const slices = [
    { x: (1 - a) * -260, y: (1 - a) * 90, o: Math.min(1, a * 1.5), blur: (1 - a) * 8 },
    { x: 0, y: (1 - b) * -220, o: Math.min(1, b * 1.5), blur: (1 - b) * 8 },
    { x: (1 - c) * 260, y: (1 - c) * 90, o: Math.min(1, c * 1.5), blur: (1 - c) * 8 },
  ];

  // drop: punch + glow; then zoom-through into the next scene
  const punch = sp(f, DROP, SPR.bouncy);
  const preTension = interpolate(f, [s3, DROP], [1, 0.9], { ...clamp, easing: (t) => t * t });
  const scaleDrop = f < DROP ? preTension : interpolate(punch, [0, 1], [1.35, 1]);
  const exit = ramp(f, [158, 180], [0, 1], (t) => t * t * t);
  const zoom = 1 + exit * 9;
  const glow = 0.35 + 1.2 * pulse(f, DROP, 40) + 0.3 * ramp(f, [90, 118]);
  const shiver = f > 96 && f < DROP ? Math.sin(f * 3.1) * ramp(f, [96, DROP]) * 5 : 0;

  // wordmark + tagline after the drop
  const word = sp(f, DROP + 6, SPR.soft);
  const tag = ramp(f, [DROP + 18, DROP + 36]);
  const tracking = interpolate(word, [0, 1], [70, 18]);
  const textOut = 1 - ramp(f, [156, 168]);

  const pre = ramp(f, [8, 30]) * (1 - ramp(f, [56, 66]));

  return (
    <AbsoluteFill>
      {/* boot line before the mark assembles */}
      <div
        style={{
          position: "absolute",
          top: H / 2 - 20,
          width: "100%",
          textAlign: "center",
          fontFamily: MONO,
          fontSize: 30,
          letterSpacing: 10,
          color: C.cyan,
          opacity: pre,
        }}
      >
        {"LOADING PROGRAM".slice(0, Math.floor(ramp(f, [8, 40]) * 15))}
        <span style={{ opacity: f % 20 < 10 ? 1 : 0 }}>_</span>
      </div>

      <Shockwave at={DROP} />

      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          transform: `translateY(-150px) scale(${scaleDrop * zoom}) translateX(${shiver}px)`,
          opacity: 1 - ramp(f, [172, 180]),
          filter: exit > 0.05 ? `blur(${exit * 10}px)` : undefined,
        }}
      >
        <LogoMark width={640} slices={slices} glow={glow} sheen={f >= DROP + 4 ? ramp(f, [DROP + 4, DROP + 34]) : -1} />
      </AbsoluteFill>

      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: textOut }}>
        <div style={{ transform: "translateY(170px)", textAlign: "center" }}>
          <div
            style={{
              fontFamily: FONT,
              fontWeight: 700,
              fontSize: 92,
              letterSpacing: tracking,
              color: C.text,
              opacity: Math.min(1, word * 1.4),
              transform: `scale(${interpolate(word, [0, 1], [1.2, 1])})`,
              textShadow: "0 0 40px rgba(76,197,237,0.6)",
              marginRight: -tracking,
              whiteSpace: "nowrap",
            }}
          >
            NAV COACHING
          </div>
          <div
            style={{
              marginTop: 18,
              fontFamily: MONO,
              fontSize: 34,
              letterSpacing: 8,
              color: C.cyan,
              opacity: tag,
              transform: `translateY(${(1 - tag) * 16}px)`,
            }}
          >
            WHERE PASSION MEETS QUALITY
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
