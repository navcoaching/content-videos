import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { C, MONO } from "../theme";
import { cues, ramp } from "../lib/motion";

const LABELS: [keyof typeof cues.scenes, string][] = [
  ["intro", "INIT"],
  ["kinetic", "PHILOSOPHY"],
  ["training", "PROGRAM"],
  ["progress", "PROGRESS"],
  ["features", "PLATFORM"],
  ["cta", "START"],
];

const Corner: React.FC<{ pos: React.CSSProperties; rot: number; p: number }> = ({ pos, rot, p }) => (
  <div
    style={{
      position: "absolute",
      width: 64,
      height: 64,
      ...pos,
      transform: `rotate(${rot}deg) scale(${0.6 + 0.4 * p})`,
      opacity: p * 0.8,
      borderTop: `3px solid ${C.cyan}`,
      borderLeft: `3px solid ${C.cyan}`,
      filter: `drop-shadow(0 0 8px ${C.cyan})`,
    }}
  />
);

/** Futuristic heads-up overlay: corner brackets, section index, timecode, scan line. */
export const Hud: React.FC = () => {
  const f = useCurrentFrame();
  const p = ramp(f, [96, 130]);
  const idx = LABELS.findIndex(([k]) => f >= cues.scenes[k][0] && f < cues.scenes[k][1]);
  const [key, label] = LABELS[Math.max(0, idx)];
  const sceneStart = cues.scenes[key][0];
  const labelIn = ramp(f, [sceneStart, sceneStart + 14]);
  const sec = Math.floor(f / 60);
  const fr = f % 60;
  const tc = `00:${String(sec).padStart(2, "0")}:${String(fr).padStart(2, "0")}`;
  const scanY = ((f * 7) % 2300) - 200;
  const text: React.CSSProperties = {
    position: "absolute",
    fontFamily: MONO,
    fontSize: 24,
    letterSpacing: 4,
    color: C.muted,
    opacity: 0.85 * p,
  };
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <Corner pos={{ left: 44, top: 44 }} rot={0} p={p} />
      <Corner pos={{ right: 44, top: 44 }} rot={90} p={p} />
      <Corner pos={{ right: 44, bottom: 44 }} rot={180} p={p} />
      <Corner pos={{ left: 44, bottom: 44 }} rot={270} p={p} />
      <div style={{ ...text, left: 130, top: 66 }}>
        <span style={{ color: C.cyan }}>NAV</span>//COACHING
      </div>
      <div style={{ ...text, right: 130, top: 66, textAlign: "right" }}>
        <span style={{ color: C.cyan }}>{String(Math.max(0, idx) + 1).padStart(2, "0")}</span>/06{" "}
        <span style={{ opacity: labelIn, display: "inline-block", transform: `translateY(${(1 - labelIn) * 12}px)` }}>
          {label}
        </span>
      </div>
      <div style={{ ...text, left: 130, bottom: 66 }}>navcoaching.com</div>
      <div style={{ ...text, right: 130, bottom: 66 }}>
        <span style={{ color: C.cyan }}>●</span> {tc}
      </div>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: scanY,
          height: 140,
          background: "linear-gradient(to bottom, rgba(76,197,237,0), rgba(76,197,237,0.05), rgba(76,197,237,0))",
          opacity: p,
        }}
      />
    </AbsoluteFill>
  );
};
