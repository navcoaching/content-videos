import React from "react";
import { AbsoluteFill, interpolate, random, useCurrentFrame } from "remotion";
import { C, H, W } from "../theme";
import { clamp, cues, pulse, ramp } from "../lib/motion";

const S = cues.scenes;
const HIT = cues.hits;

/** Grid speed (px/frame) — surges on the warp section and the drops. */
const gridSpeed = (f: number) => {
  let v = 1.6;
  v += 14 * pulse(f, HIT.drop, 40, 2);
  v += interpolate(f, [S.features[0] - 10, S.features[0] + 40, S.cta[0] - 2, S.cta[0] + 30], [0, 16, 22, 0], clamp);
  v += 10 * pulse(f, S.progress[1] - 30, 40, 1) * (f > S.progress[1] - 30 ? 1 : 0);
  return v;
};

const offsets: number[] = [];
{
  let acc = 0;
  for (let f = 0; f <= cues.durationInFrames + 60; f++) {
    offsets.push(acc);
    acc += gridSpeed(f);
  }
}

const GridPlane: React.FC<{ top: number; flip?: boolean; offset: number; alpha: number }> = ({
  top,
  flip,
  offset,
  alpha,
}) => {
  const line = `rgba(76,197,237,${alpha})`;
  return (
    <div
      style={{
        position: "absolute",
        left: W / 2 - 2400,
        top: flip ? top - 3000 : top,
        width: 4800,
        height: 3000,
        transformOrigin: flip ? "bottom center" : "top center",
        transform: `perspective(900px) rotateX(${flip ? -80 : 80}deg)`,
        backgroundImage: `linear-gradient(${line} 3px, transparent 3px), linear-gradient(90deg, ${line} 3px, transparent 3px)`,
        backgroundSize: "96px 96px",
        backgroundPosition: `0px ${flip ? -offset % 96 : offset % 96}px`,
        WebkitMaskImage: flip
          ? "linear-gradient(to top, rgba(0,0,0,0) 0%, rgba(0,0,0,1) 35%, rgba(0,0,0,0.6) 75%, rgba(0,0,0,0) 100%)"
          : "linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,1) 35%, rgba(0,0,0,0.6) 75%, rgba(0,0,0,0) 100%)",
      }}
    />
  );
};

type P = { x: number; y: number; z: number; v: number; a: number; tw: number };
const PARTICLES: P[] = new Array(120).fill(0).map((_, i) => ({
  x: random(`px${i}`) * W,
  y: random(`py${i}`) * H,
  z: 0.25 + random(`pz${i}`) * 0.75,
  v: 0.4 + random(`pv${i}`) * 1.4,
  a: random(`pa${i}`) * Math.PI * 2,
  tw: random(`pt${i}`) * 10,
}));

const Particles: React.FC<{ f: number }> = ({ f }) => {
  const cx = W / 2;
  const cy = H / 2 - 60;
  // pull toward the logo during the intro riser, then burst on the drop
  const pull = interpolate(f, [10, HIT.drop - 2, HIT.drop], [0, 0.82, 0], {
    ...clamp,
    easing: (t) => t * t,
  });
  const burstA = f >= HIT.drop ? 1 - Math.exp(-(f - HIT.drop) / 10) : 0;
  const burstB = f >= HIT.final ? 1 - Math.exp(-(f - HIT.final) / 10) : 0;
  const warpFade = interpolate(f, [S.features[0] - 20, S.features[0], S.cta[0] - 4, S.cta[0] + 10], [1, 0.25, 0.25, 1], clamp);
  return (
    <>
      {PARTICLES.map((p, i) => {
        let x = p.x + Math.sin(f / 60 + p.a) * 30 * p.z;
        let y = (((p.y - f * p.v * p.z * 1.4) % H) + H) % H;
        const dx = x - cx;
        const dy = y - cy;
        const d = Math.hypot(dx, dy) + 1e-3;
        x = x - dx * pull;
        y = y - dy * pull;
        const push = (burstA * 520 * (1 - pull) + burstB * 620) * p.z;
        x += (dx / d) * push * (f >= HIT.drop ? 1 : 0);
        y += (dy / d) * push * (f >= HIT.drop ? 1 : 0);
        const size = 3 + p.z * 7;
        const twinkle = 0.55 + 0.45 * Math.sin(f / 9 + p.tw);
        const op = (0.25 + 0.75 * p.z) * twinkle * warpFade * ramp(f, [0, 30]);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x - size * 2,
              top: y - size * 2,
              width: size * 4,
              height: size * 4,
              borderRadius: "50%",
              opacity: op,
              background: `radial-gradient(circle, ${i % 5 === 0 ? "#ffffff" : C.cyan} 0%, rgba(76,197,237,0.35) 22%, rgba(76,197,237,0) 60%)`,
            }}
          />
        );
      })}
    </>
  );
};

type St = { a: number; r0: number; s: number; w: number };
const STREAKS: St[] = new Array(70).fill(0).map((_, i) => ({
  a: random(`sa${i}`) * Math.PI * 2,
  r0: random(`sr${i}`) * 1400,
  s: 0.6 + random(`ss${i}`) * 1.2,
  w: 2 + random(`sw${i}`) * 3,
}));

/** Radial hyperspace streaks: flying forward through the grid. */
export const Warp: React.FC<{ f: number; intensity: number }> = ({ f, intensity }) => {
  if (intensity <= 0.01) return null;
  const cx = W / 2;
  const cy = H / 2 - 40;
  return (
    <AbsoluteFill style={{ opacity: intensity }}>
      {STREAKS.map((s, i) => {
        const speed = 26 * s.s;
        const r = (s.r0 + f * speed) % 1400;
        const len = 40 + r * 0.35 * s.s;
        const op = Math.min(1, r / 300);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: cx,
              top: cy,
              width: len,
              height: s.w,
              transformOrigin: "0 50%",
              transform: `rotate(${s.a}rad) translateX(${r}px)`,
              background: `linear-gradient(90deg, rgba(76,197,237,0), ${i % 4 === 0 ? "#fff" : C.cyan})`,
              opacity: op,
              borderRadius: 4,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

export const Background: React.FC = () => {
  const f = useCurrentFrame();
  const off = offsets[Math.min(f, offsets.length - 1)];
  const gridIn = ramp(f, [0, 70]);
  const dropGlow = pulse(f, HIT.drop, 50) + pulse(f, HIT.final, 60) + 0.5 * pulse(f, HIT.wordC, 30);
  const warp =
    interpolate(f, [S.features[0] - 8, S.features[0] + 20, S.cta[0], S.cta[0] + 16], [0, 1, 1, 0], clamp) +
    interpolate(f, [150, 176, 190], [0, 0.9, 0], clamp) +
    interpolate(f, [930, 956, 966], [0, 0.6, 0], clamp);
  // slow camera drift + depth breathing
  const camScale = 1 + 0.04 * Math.sin(f / 90) + 0.08 * pulse(f, HIT.drop, 30) + 0.08 * pulse(f, HIT.final, 30);
  const hue = interpolate(f, [0, 600, 1200], [0, 18, 0]);

  return (
    <AbsoluteFill style={{ background: C.void, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 90% 60% at 50% 45%, ${C.ink3} 0%, ${C.ink} 45%, ${C.void} 100%)`,
        }}
      />
      <AbsoluteFill style={{ transform: `scale(${camScale})`, filter: `hue-rotate(${hue}deg)` }}>
        <div style={{ opacity: 0.85 * gridIn }}>
          <GridPlane top={1330} offset={off} alpha={0.55} />
          <GridPlane top={590} offset={off} alpha={0.28} flip />
        </div>
        {/* horizon glows */}
        <div
          style={{
            position: "absolute",
            left: -200,
            right: -200,
            top: 1330 - 180,
            height: 360,
            background: `radial-gradient(ellipse 50% 50% at 50% 50%, rgba(76,197,237,${0.35 + 0.4 * dropGlow}) 0%, rgba(40,77,160,0.15) 45%, rgba(0,0,0,0) 70%)`,
            opacity: gridIn,
          }}
        />
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: 1328,
            height: 3,
            background: `linear-gradient(90deg, rgba(76,197,237,0), ${C.cyan}, rgba(76,197,237,0))`,
            opacity: 0.8 * gridIn,
            boxShadow: `0 0 24px ${C.cyan}`,
          }}
        />
        {/* drifting orbs */}
        <div
          style={{
            position: "absolute",
            width: 1300,
            height: 1300,
            left: -520 + Math.sin(f / 140) * 120,
            top: 180 + Math.cos(f / 170) * 140,
            background: "radial-gradient(circle, rgba(40,77,160,0.55) 0%, rgba(40,77,160,0) 62%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            width: 1200,
            height: 1200,
            left: 420 + Math.cos(f / 120) * 120,
            top: 980 + Math.sin(f / 150) * 160,
            background: "radial-gradient(circle, rgba(76,197,237,0.28) 0%, rgba(76,197,237,0) 62%)",
          }}
        />
        <Particles f={f} />
      </AbsoluteFill>
      <Warp f={f} intensity={Math.min(1, warp)} />
      {/* vignette */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse 75% 60% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.75) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};
