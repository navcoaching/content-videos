import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT, H, W } from "../theme";
import { chroma, clamp, cues, pulse, ramp, sp, SPR } from "../lib/motion";

// Vectorised from public/brand/logo-mark.png (256x108) so it stays sharp at any scale.
const MARK_OUTER =
  "M0,0 L36,0 L115,81 L115,0 L151,0 L230,81 L230,0 L256,0 L256,108 L220,108 L193,81 L140,81 L140,108 L104,108 L25,26 L25,81 L0,81 Z";
const MARK_HOLE = "M140,26 L169,55 L140,55 Z";
export const MARK_D = `${MARK_OUTER} ${MARK_HOLE}`;

type SliceAnim = { x: number; y: number; o: number; blur: number };

/**
 * NAV mark built from three vertical slices so each can fly in separately.
 * `slices` gives a per-slice offset; when all offsets are 0 the seams vanish.
 */
export const LogoMark: React.FC<{
  width: number;
  slices?: SliceAnim[];
  glow?: number;
  fill?: string;
  sheen?: number; // 0..1 position of a light sweep, <0 = none
}> = ({ width, slices, glow = 0.6, fill = C.logo, sheen = -1 }) => {
  const cuts = [
    [0, 115],
    [115, 230],
    [230, 256],
  ];
  const s = slices ?? cuts.map(() => ({ x: 0, y: 0, o: 1, blur: 0 }));
  const h = (width * 108) / 256;
  return (
    <svg
      width={width}
      height={h}
      viewBox="-4 -4 264 116"
      style={{ overflow: "visible", filter: `drop-shadow(0 0 ${24 * glow}px rgba(76,197,237,${0.9 * glow}))` }}
    >
      <defs>
        {cuts.map(([a, b], i) => (
          <clipPath id={`cut${i}`} key={i}>
            <rect x={a - (i === 0 ? 10 : 0.2)} y={-10} width={b - a + (i === 2 ? 10 : 0.4)} height={130} />
          </clipPath>
        ))}
        <linearGradient id="markGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#7fdcff" />
          <stop offset="0.5" stopColor={fill} />
          <stop offset="1" stopColor="#1a8fd0" />
        </linearGradient>
        <linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#fff" stopOpacity="0" />
          <stop offset="0.5" stopColor="#fff" stopOpacity="0.9" />
          <stop offset="1" stopColor="#fff" stopOpacity="0" />
        </linearGradient>
        <clipPath id="markClip">
          <path d={MARK_D} fillRule="evenodd" />
        </clipPath>
      </defs>
      {cuts.map((_, i) => (
        <g key={i} clipPath={`url(#cut${i})`}>
          <g
            transform={`translate(${s[i].x} ${s[i].y})`}
            opacity={s[i].o}
            style={{ filter: s[i].blur > 0.3 ? `blur(${s[i].blur}px)` : undefined }}
          >
            <path d={MARK_D} fillRule="evenodd" fill="url(#markGrad)" />
          </g>
        </g>
      ))}
      {sheen >= 0 && sheen <= 1 && (
        <g clipPath="url(#markClip)">
          <rect x={-120 + sheen * 440} y={-20} width={70} height={160} fill="url(#sheen)" transform="skewX(-28)" />
        </g>
      )}
    </svg>
  );
};

/** Full-screen flash on the big hits. */
export const Flash: React.FC = () => {
  const f = useCurrentFrame();
  const H_ = cues.hits;
  const a =
    0.9 * pulse(f, H_.drop, 16, 2.4) +
    0.45 * pulse(f, H_.wordC, 12, 2) +
    0.3 * pulse(f, H_.wordA, 8) +
    0.3 * pulse(f, H_.wordB, 8) +
    0.5 * pulse(f, H_.progressIn, 10) +
    0.35 * pulse(f, H_.feat1, 8) +
    0.25 * pulse(f, H_.feat2, 8) +
    0.25 * pulse(f, H_.feat3, 8) +
    0.25 * pulse(f, H_.feat4, 8) +
    1.0 * pulse(f, H_.final, 20, 2.2) +
    interpolate(f, [170, 179, 181, 190], [0, 0.85, 0.85, 0], clamp) +
    interpolate(f, [944, 958, 962, 972], [0, 0.7, 0.7, 0], clamp) +
    interpolate(f, [1068, 1079], [0, 0.6], clamp) * (f < H_.final ? 1 : 0);
  if (a <= 0.005) return null;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        opacity: Math.min(1, a),
        background: "radial-gradient(circle at 50% 46%, #ffffff 0%, rgba(160,230,255,0.85) 30%, rgba(76,197,237,0.25) 65%, rgba(76,197,237,0) 100%)",
        mixBlendMode: "screen",
      }}
    />
  );
};

/** Shockwave ring on a hit. */
export const Shockwave: React.FC<{ at: number; y?: number; size?: number }> = ({ at, y = H / 2 - 60, size = 1 }) => {
  const f = useCurrentFrame();
  if (f < at || f > at + 50) return null;
  const t = (f - at) / 50;
  const r = (120 + 1300 * (1 - Math.pow(1 - t, 3))) * size;
  return (
    <>
      {[0, 1].map((k) => {
        const rr = r * (1 - k * 0.22);
        return (
          <div
            key={k}
            style={{
              position: "absolute",
              left: W / 2 - rr,
              top: y - rr,
              width: rr * 2,
              height: rr * 2,
              borderRadius: "50%",
              border: `${(k ? 3 : 8) * (1 - t) + 1}px solid ${k ? "#fff" : C.cyan}`,
              boxShadow: `0 0 40px ${C.cyan}, inset 0 0 40px rgba(76,197,237,0.5)`,
              opacity: (1 - t) * (k ? 0.6 : 0.9),
            }}
          />
        );
      })}
    </>
  );
};

/** Brand diagonal-slash wipe (echoes the NAV mark's diagonals). Covers fully at `cut`. */
export const SlashWipe: React.FC<{ cut: number; len?: number }> = ({ cut, len = 30 }) => {
  const f = useCurrentFrame();
  const start = cut - len * 0.55;
  const end = cut + len * 0.55;
  if (f < start - 1 || f > end + 1) return null;
  const bars = [
    { color: C.navy, delay: 0, w: 900 },
    { color: C.cyan, delay: 3, w: 640 },
    { color: "#ffffff", delay: 6, w: 160 },
  ];
  return (
    <AbsoluteFill style={{ pointerEvents: "none", overflow: "hidden" }}>
      {bars.map((b, i) => {
        const x = interpolate(f, [start + b.delay, end + b.delay * 0.5], [W + 1400, -W - 1500], {
          ...clamp,
          easing: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
        });
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: -400,
              height: H + 800,
              left: x,
              width: b.w * 2.2,
              background: b.color,
              transform: "skewX(-28deg)",
              boxShadow: i === 1 ? `0 0 80px ${C.cyan}` : undefined,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/** Kinetic word: slams in with spring scale, motion blur and RGB split. */
export const KWord: React.FC<{
  text: string;
  at: number;
  size: number;
  color?: string;
  weight?: number;
  glow?: boolean;
  from?: "zoom" | "up" | "down" | "right";
  style?: React.CSSProperties;
  gradient?: string;
}> = ({ text, at, size, color = C.text, weight = 700, glow, from = "zoom", style, gradient }) => {
  const f = useCurrentFrame();
  const s = sp(f, at, SPR.slam);
  const vis = f >= at;
  const t = f - at;
  const scale = from === "zoom" ? interpolate(s, [0, 1], [2.6, 1]) : 1;
  const ty = from === "up" ? (1 - s) * 140 : from === "down" ? (s - 1) * 140 : 0;
  const tx = from === "right" ? (1 - s) * 220 : 0;
  const blur = Math.max(0, (1 - ramp(t, [0, 10])) * 14);
  const d = Math.max(0, 12 * (1 - t / 12));
  return (
    <span
      style={{
        display: "inline-block",
        fontFamily: FONT,
        fontWeight: weight,
        fontSize: size,
        lineHeight: 1.15,
        color,
        opacity: vis ? ramp(t, [0, 5]) : 0,
        transform: `translate(${tx}px, ${ty}px) scale(${scale})`,
        filter: blur > 0.3 ? `blur(${blur}px)` : undefined,
        textShadow: chroma(d, glow ? `0 0 40px rgba(76,197,237,0.85), 0 0 90px rgba(76,197,237,0.45)` : ""),
        ...(gradient
          ? {
              backgroundImage: gradient,
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
              textShadow: "none",
              filter: `${blur > 0.3 ? `blur(${blur}px) ` : ""}drop-shadow(0 0 30px rgba(76,197,237,0.7))`,
            }
          : {}),
        ...style,
      }}
    >
      {text}
    </span>
  );
};

export const Eyebrow: React.FC<{ text: string; at: number; style?: React.CSSProperties }> = ({ text, at, style }) => {
  const f = useCurrentFrame();
  const p = ramp(f, [at, at + 16]);
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 16,
        fontFamily: FONT,
        fontWeight: 500,
        fontSize: 38,
        color: C.cyan,
        opacity: p,
        transform: `translateY(${(1 - p) * 20}px)`,
        letterSpacing: 1,
        ...style,
      }}
    >
      <span
        style={{
          width: 64 * p,
          height: 4,
          background: C.cyan,
          boxShadow: `0 0 12px ${C.cyan}`,
          transform: "skewX(-28deg)",
        }}
      />
      {text}
    </div>
  );
};
