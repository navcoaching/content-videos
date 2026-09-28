import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { FONT } from "../../theme";
import { L, SHADOW_3, TINTS, WIN } from "../theme";
import { CHAPTERS, SEG, captionAt, chapterIndexAt } from "../tl";
import { clamp, ramp, sp, SPR } from "../../lib/motion";

/** Soft pastel background whose tint follows the current chapter. */
export const LightBg: React.FC<{ tint: string }> = ({ tint }) => {
  const f = useCurrentFrame();
  const [a, b] = TINTS[tint] ?? TINTS.neutral;
  return (
    <AbsoluteFill style={{ background: L.paper, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          width: 1500,
          height: 1500,
          right: -600 + Math.sin(f / 160) * 60,
          top: -700 + Math.cos(f / 190) * 60,
          background: `radial-gradient(circle, ${a} 0%, rgba(255,255,255,0) 62%)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 1500,
          height: 1500,
          left: -700 + Math.cos(f / 170) * 60,
          bottom: -700 + Math.sin(f / 150) * 60,
          background: `radial-gradient(circle, ${b} 0%, rgba(255,255,255,0) 62%)`,
        }}
      />
      {/* faint dot grid */}
      <AbsoluteFill
        style={{
          backgroundImage: "radial-gradient(rgba(40,77,160,0.10) 2px, transparent 2px)",
          backgroundSize: "44px 44px",
          backgroundPosition: `0 ${(f * 0.3) % 44}px`,
          WebkitMaskImage: "linear-gradient(to bottom, rgba(0,0,0,0.9), rgba(0,0,0,0.2))",
        }}
      />
    </AbsoluteFill>
  );
};

/** Top chrome: brand + chapter progress bar + "N من 6" chip + title + subtitle. */
export const ChapterHeader: React.FC = () => {
  const f = useCurrentFrame();
  const idx = chapterIndexAt(f);
  if (idx < 0) return null;
  const ch = CHAPTERS[idx];
  const [s, e] = SEG[ch.key];
  const inP = sp(f, s, SPR.snappy);
  const out = ramp(f, [e - 14, e]);
  const firstIn = ramp(f, [SEG.ch1[0], SEG.ch1[0] + 20]);
  const lastOut = 1 - ramp(f, [SEG.ch6[1] - 16, SEG.ch6[1]]);
  const progressInChapter = interpolate(f, [s, e], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: 120, direction: "rtl" }}>
      {/* brand + segmented progress */}
      <div style={{ display: "flex", alignItems: "center", gap: 18, opacity: firstIn * lastOut }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, fontFamily: FONT, fontWeight: 700, fontSize: 30, color: L.heading, whiteSpace: "nowrap" }}>
          <span style={{ width: 40, height: 40, borderRadius: 12, background: L.ink, display: "grid", placeItems: "center" }}>
            <svg width="28" height="12" viewBox="0 0 256 108">
              <path
                d="M0,0 L36,0 L115,81 L115,0 L151,0 L230,81 L230,0 L256,0 L256,108 L220,108 L193,81 L140,81 L140,108 L104,108 L25,26 L25,81 L0,81 Z M140,26 L169,55 L140,55 Z"
                fill={L.logo}
                fillRule="evenodd"
              />
            </svg>
          </span>
          Nav Coaching
        </div>
        <div style={{ flex: 1, display: "flex", gap: 8 }}>
          {CHAPTERS.map((c, i) => {
            const fill = i < idx ? 1 : i === idx ? progressInChapter : 0;
            return (
              <div key={c.key} style={{ flex: 1, height: 10, borderRadius: 99, background: "rgba(40,77,160,0.14)", overflow: "hidden" }}>
                <div style={{ width: `${fill * 100}%`, height: "100%", background: i === idx ? L.navy : L.cyan, borderRadius: 99 }} />
              </div>
            );
          })}
        </div>
      </div>
      <div style={{ opacity: inP * (1 - out), transform: `translateY(${(1 - inP) * 40 - out * 20}px)` }}>
        <div style={{ marginTop: 44, display: "flex", gap: 14, alignItems: "center" }}>
          <span
            style={{
              fontFamily: FONT,
              fontWeight: 600,
              fontSize: 28,
              background: L.ink,
              color: "#fff",
              padding: "8px 20px",
              borderRadius: 999,
              display: "inline-flex",
              gap: 10,
              alignItems: "center",
            }}
          >
            <span style={{ width: 34, height: 34, borderRadius: "50%", background: L.cyan, color: L.ink, display: "grid", placeItems: "center", fontSize: 22 }}>
              {idx + 1}
            </span>
            من {CHAPTERS.length}
          </span>
        </div>
        <div style={{ marginTop: 10, fontFamily: FONT, fontWeight: 700, fontSize: 112, lineHeight: 1.15, color: L.heading }}>{ch.title}</div>
        <div style={{ marginTop: 4, fontFamily: FONT, fontWeight: 400, fontSize: 38, color: L.muted }}>{ch.sub}</div>
      </div>
    </div>
  );
};

/** Caption under the window — like the reference's narration line. */
export const Caption: React.FC = () => {
  const f = useCurrentFrame();
  const c = captionAt(f);
  if (!c) return null;
  const idx = chapterIndexAt(f);
  const [, e] = SEG[CHAPTERS[idx].key];
  const p = sp(f, c.at, SPR.snappy);
  const out = ramp(f, [e - 12, e]);
  return (
    <div
      style={{
        position: "absolute",
        top: WIN.y + WIN.h + 50,
        left: 60,
        right: 60,
        textAlign: "center",
        direction: "rtl",
        fontFamily: FONT,
        fontWeight: 700,
        fontSize: 60,
        color: L.heading,
        opacity: Math.min(1, p * 1.5) * (1 - out),
        transform: `translateY(${(1 - p) * 26}px)`,
        filter: p < 0.6 ? `blur(${(0.6 - p) * 10}px)` : undefined,
      }}
    >
      {c.text}
    </div>
  );
};

/** macOS-style browser window. Children render in content coordinates (1000 x 844). */
export const BrowserWindow: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
  title?: string;
}> = ({ children, style, title = "navcoaching.com" }) => (
  <div
    style={{
      position: "absolute",
      left: WIN.x,
      top: WIN.y,
      width: WIN.w,
      height: WIN.h,
      borderRadius: 28,
      background: L.surface,
      boxShadow: SHADOW_3,
      overflow: "hidden",
      border: `1px solid ${L.line}`,
      ...style,
    }}
  >
    <div
      style={{
        height: WIN.bar,
        background: "#f6f8fb",
        borderBottom: `1px solid ${L.line}`,
        display: "flex",
        alignItems: "center",
        padding: "0 22px",
        gap: 10,
        direction: "ltr",
        position: "relative",
      }}
    >
      {["#ff5f57", "#febc2e", "#28c840"].map((c) => (
        <span key={c} style={{ width: 16, height: 16, borderRadius: "50%", background: c }} />
      ))}
      <div
        style={{
          position: "absolute",
          left: "50%",
          transform: "translateX(-50%)",
          padding: "6px 26px",
          borderRadius: 10,
          background: "#fff",
          border: `1px solid ${L.line}`,
          fontFamily: FONT,
          fontSize: 22,
          color: L.muted,
        }}
      >
        🔒 {title}
      </div>
    </div>
    <div style={{ position: "relative", width: WIN.w, height: WIN.h - WIN.bar, overflow: "hidden", direction: "rtl" }}>{children}</div>
  </div>
);

export type Rect = [number, number, number, number];

/** Dims the page and cuts a glowing hole around the focused element. keys: [frame, rect|null]. */
export const Spotlight: React.FC<{ keys: [number, Rect | null][] }> = ({ keys }) => {
  const f = useCurrentFrame();
  let from: Rect | null = null;
  let to: Rect | null = null;
  let at = -1e9;
  for (const [k, r] of keys) {
    if (f >= k) {
      from = to;
      to = r;
      at = k;
    }
  }
  const t = Math.min(1, (f - at) / 14);
  const e = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  let rect: Rect | null;
  let op: number;
  if (to && from) {
    rect = from.map((v, i) => v + (to![i] - v) * e) as Rect;
    op = 1;
  } else if (to) {
    rect = to;
    op = e;
  } else if (from) {
    rect = from;
    op = 1 - e;
  } else return null;
  const [x, y, w, h] = rect;
  const pulseGlow = 0.5 + 0.5 * Math.sin((f - at) / 7);
  return (
    <div
      style={{
        position: "absolute",
        left: x - 10,
        top: y - 10,
        width: w + 20,
        height: h + 20,
        borderRadius: 20,
        boxShadow: `0 0 0 3000px rgba(11,26,51,${0.42 * op})`,
        border: `4px solid rgba(76,197,237,${op})`,
        outline: `${6 + 4 * pulseGlow}px solid rgba(76,197,237,${0.22 * op})`,
        zIndex: 40,
        pointerEvents: "none",
      }}
    />
  );
};

/** macOS arrow cursor, keyframes [frame, x, y] in page coords; clicks ripple. */
export const MacCursor: React.FC<{ path: [number, number, number][]; clicks: number[]; from: number; to: number }> = ({
  path,
  clicks,
  from,
  to,
}) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  const frames = path.map((p) => p[0]);
  const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const x = interpolate(f, frames, path.map((p) => p[1]), { ...clamp, easing: ease });
  const y = interpolate(f, frames, path.map((p) => p[2]), { ...clamp, easing: ease });
  const op = ramp(f, [from, from + 8]) * (1 - ramp(f, [to - 8, to]));
  let press = 0;
  let ripple: number | null = null;
  for (const c of clicks) {
    if (f >= c - 4 && f < c + 6) press = Math.max(press, 1 - Math.abs(f - c) / 6);
    if (f >= c && f < c + 22) ripple = (f - c) / 22;
  }
  return (
    <div style={{ position: "absolute", left: x, top: y, opacity: op, zIndex: 100 }}>
      {ripple !== null && (
        <div
          style={{
            position: "absolute",
            left: -40 * (0.4 + ripple),
            top: -40 * (0.4 + ripple),
            width: 80 * (0.4 + ripple),
            height: 80 * (0.4 + ripple),
            borderRadius: "50%",
            background: `rgba(76,197,237,${0.45 * (1 - ripple)})`,
            border: `3px solid rgba(40,77,160,${0.8 * (1 - ripple)})`,
          }}
        />
      )}
      <svg width={52} height={52} viewBox="0 0 24 24" style={{ transform: `scale(${1 - press * 0.18})`, transformOrigin: "4px 3px", filter: "drop-shadow(0 3px 5px rgba(0,0,0,0.35))" }}>
        <path d="M4 2 L4 19 L8.5 14.8 L11.4 21.3 L14.2 20.1 L11.3 13.7 L17.5 13.7 Z" fill="#111" stroke="#fff" strokeWidth="1.4" strokeLinejoin="round" />
      </svg>
    </div>
  );
};
