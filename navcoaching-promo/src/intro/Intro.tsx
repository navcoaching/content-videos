import React from "react";
import { AbsoluteFill, Audio, Easing, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import "../fonts";
import cfg from "./config.json";

export const INTRO_FPS = cfg.fps;
export const INTRO_DURATION = Math.round(cfg.durationSec * cfg.fps);

const sec = (s: number) => Math.round(s * cfg.fps);
const ease = Easing.bezier(0.22, 1, 0.36, 1); // gentle ease-out, no overshoot
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const tween = (f: number, a: number, b: number, from: number, to: number) =>
  interpolate(f, [sec(a), sec(b)], [from, to], { ...clamp, easing: ease });

/** 4 s calm intro: logo fades in with a slight scale-up, accent line opens, tagline fades in. Last frame is static. */
export const Intro: React.FC<{ withAudio?: boolean }> = ({ withAudio = true }) => {
  const f = useCurrentFrame();
  const c = cfg.colors;
  const logoO = tween(f, 0.4, 1.8, 0, 1);
  const logoS = tween(f, 0.4, 1.8, 0.96, 1);
  const line = tween(f, 1.8, 2.4, 0, 1);
  const tagO = tween(f, 2.2, 3.0, 0, 1);
  const tagY = tween(f, 2.2, 3.0, 12, 0);
  const glow = tween(f, 0.4, 2.2, 0, 1);
  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse 70% 42% at 50% 46%, ${c.bgInner} 0%, ${c.bgMid} 60%, ${c.bgOuter} 100%)`, direction: "rtl" }}>
      <div style={{ position: "absolute", left: "50%", top: 880, width: 760, height: 380, transform: "translate(-50%,-50%)", background: "radial-gradient(ellipse at center, rgba(76,197,237,0.16) 0%, rgba(76,197,237,0) 70%)", opacity: glow }} />
      <Img src={staticFile(cfg.logo)} style={{ position: "absolute", left: "50%", top: 880, width: cfg.logoWidth, transform: `translate(-50%,-50%) scale(${logoS})`, opacity: logoO }} />
      <div style={{ position: "absolute", left: "50%", top: 1062, width: 120, height: 4, borderRadius: 4, background: c.accent, transform: `translateX(-50%) scaleX(${line})` }} />
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 1112,
          textAlign: "center",
          fontFamily: '"Readex Pro", sans-serif',
          fontWeight: 500,
          fontSize: 46,
          color: c.tagline,
          opacity: tagO,
          transform: `translateY(${tagY}px)`,
        }}
      >
        {cfg.tagline}
      </div>
      {withAudio && <Audio src={staticFile("audio/intro.wav")} />}
    </AbsoluteFill>
  );
};
