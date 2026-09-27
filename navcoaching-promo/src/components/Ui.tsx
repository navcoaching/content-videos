import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C, FONT, MONO } from "../theme";
import { clamp, ramp } from "../lib/motion";

/** Glowing futuristic pointer following keyframes [frame, x, y]; clicks ripple. */
export const Cursor: React.FC<{ path: [number, number, number][]; clicks: number[]; hideAfter?: number }> = ({
  path,
  clicks,
  hideAfter = 1e9,
}) => {
  const f = useCurrentFrame();
  const frames = path.map((p) => p[0]);
  if (f < frames[0] || f > hideAfter + 10) return null;
  const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const x = interpolate(f, frames, path.map((p) => p[1]), { ...clamp, easing: ease });
  const y = interpolate(f, frames, path.map((p) => p[2]), { ...clamp, easing: ease });
  const op = ramp(f, [frames[0], frames[0] + 8]) * (1 - ramp(f, [hideAfter, hideAfter + 10]));
  let press = 0;
  let ripple: number | null = null;
  for (const c of clicks) {
    if (f >= c - 4 && f < c + 6) press = Math.max(press, 1 - Math.abs(f - c) / 6);
    if (f >= c && f < c + 24) ripple = (f - c) / 24;
  }
  return (
    <div style={{ position: "absolute", left: x, top: y, opacity: op, zIndex: 50 }}>
      {ripple !== null && (
        <div
          style={{
            position: "absolute",
            left: -20 - ripple * 70,
            top: -20 - ripple * 70,
            width: 40 + ripple * 140,
            height: 40 + ripple * 140,
            borderRadius: "50%",
            border: `4px solid ${C.cyan}`,
            opacity: 1 - ripple,
            boxShadow: `0 0 30px ${C.cyan}`,
          }}
        />
      )}
      <div
        style={{
          position: "absolute",
          left: -26,
          top: -26,
          width: 52,
          height: 52,
          borderRadius: "50%",
          border: `3px solid rgba(255,255,255,0.9)`,
          transform: `scale(${1 - press * 0.35})`,
          boxShadow: `0 0 24px ${C.cyan}, inset 0 0 14px rgba(76,197,237,0.6)`,
          background: "rgba(76,197,237,0.18)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: -7,
          top: -7,
          width: 14,
          height: 14,
          borderRadius: "50%",
          background: "#fff",
          boxShadow: `0 0 12px #fff`,
        }}
      />
    </div>
  );
};

export const Tag: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <span
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 8,
      padding: "6px 16px",
      borderRadius: 999,
      fontFamily: FONT,
      fontWeight: 500,
      fontSize: 24,
      color: C.cyan,
      background: "rgba(76,197,237,0.12)",
      border: "1px solid rgba(76,197,237,0.35)",
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    {children}
  </span>
);

export const Num: React.FC<{ v: string; style?: React.CSSProperties }> = ({ v, style }) => (
  <span style={{ fontFamily: MONO, fontWeight: 700, ...style }}>{v}</span>
);
