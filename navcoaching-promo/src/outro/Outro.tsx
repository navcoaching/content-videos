import React from "react";
import { AbsoluteFill, Audio, Easing, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import "../fonts";
import cfg from "./config.json";

export const OUTRO_FPS = cfg.fps;
export const OUTRO_DURATION = Math.round(cfg.durationSec * cfg.fps);

const T = cfg.timing;
const C = cfg.colors;
const fr = (s: number) => s * cfg.fps;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const easeOut = Easing.bezier(0.22, 1, 0.36, 1);
const spinEase = Easing.bezier(0.33, 0, 0.12, 1); // starts moving, settles softly — no overshoot
const tw = (f: number, [a, b]: number[], from: number, to: number, easing = easeOut) =>
  interpolate(f, [fr(a), fr(b)], [from, to], { ...clamp, easing });

const Cursor: React.FC<{ f: number }> = ({ f }) => {
  const o = tw(f, T.cursorIn, 0, 1) * tw(f, T.cursorOut, 1, 0);
  if (o <= 0) return null;
  const x = tw(f, T.cursorIn, 900, 760, Easing.bezier(0.45, 0, 0.2, 1));
  const y = tw(f, T.cursorIn, 1850, 1662, Easing.bezier(0.45, 0, 0.2, 1));
  const c = fr(T.click);
  const press = f >= c - 3 && f < c + 5 ? 1 - Math.abs(f - c) / 5 : 0;
  const r = f >= c ? Math.min(1, (f - c) / 18) : -1;
  return (
    <>
      {r >= 0 && r < 1 && (
        <div style={{ position: "absolute", left: x, top: y, width: 40 + r * 70, height: 40 + r * 70, transform: "translate(-50%,-50%)", borderRadius: "50%", border: `3px solid ${C.accent}`, opacity: (1 - r) * 0.85, boxShadow: "0 0 22px rgba(76,197,237,0.45)" }} />
      )}
      <svg viewBox="0 0 24 36" style={{ position: "absolute", left: x, top: y, width: 52, opacity: o, transform: `scale(${1 - press * 0.12})`, transformOrigin: "0 0", filter: "drop-shadow(0 6px 10px rgba(0,0,0,0.55))" }}>
        <path d="M1.5 1.5 L1.5 28 L8 22 L12.5 33 L17 31 L12.6 20.5 L21 20.5 Z" fill="#ffffff" stroke="#0a1628" strokeWidth={2} strokeLinejoin="round" />
      </svg>
    </>
  );
};

/** 7.5 s outro: light reveal → logo → 3D phone spin (real site screenshot) → services → URL + click → hold → fade to black. */
export const Outro: React.FC<{ withAudio?: boolean }> = ({ withAudio = true }) => {
  const f = useCurrentFrame();
  const light = tw(f, T.lightIn, 0, 1);
  const logoO = tw(f, T.logo, 0, 1);
  const logoS = tw(f, T.logo, 0.96, 1);
  const angle = tw(f, T.phoneSpin, -360, 0, spinEase);
  const phoneS = tw(f, T.phoneSpin, 0.86, 1);
  const phoneO = tw(f, [T.phoneSpin[0], T.phoneSpin[0] + 0.4], 0, 1);
  const cosA = Math.cos((angle * Math.PI) / 180);
  const sheen = 0.22 * (1 - Math.abs(cosA));
  const line = tw(f, T.line, 0, 1);
  const urlO = tw(f, T.url, 0, 1);
  const urlY = tw(f, T.url, 14, 0);
  const c = fr(T.click);
  const urlGlow = f >= c ? Math.max(0, 1 - (f - c) / 24) : 0;
  const end = tw(f, T.fadeOut, 0, 1, Easing.inOut(Easing.quad));
  const face: React.CSSProperties = {
    position: "absolute", inset: 0, borderRadius: 58, padding: 14, boxSizing: "border-box", backfaceVisibility: "hidden",
    background: "linear-gradient(160deg,#1b2b45,#0b1424)",
    boxShadow: "0 0 0 2px rgba(76,197,237,0.35),0 50px 110px rgba(0,0,0,0.6),0 0 90px rgba(76,197,237,0.18)",
  };
  return (
    <AbsoluteFill style={{ background: "#000", fontFamily: '"Readex Pro", sans-serif' }}>
      <AbsoluteFill style={{ opacity: light }}>
        <AbsoluteFill style={{ background: `radial-gradient(ellipse 85% 50% at 50% 42%, ${C.bgInner} 0%, ${C.bgMid} 52%, ${C.bgOuter} 100%)` }} />
        <div style={{ position: "absolute", left: "-20%", top: "-10%", width: "140%", height: "70%", background: "linear-gradient(115deg, rgba(76,197,237,0) 38%, rgba(76,197,237,0.09) 50%, rgba(76,197,237,0) 62%)", filter: "blur(30px)", transform: `rotate(-8deg) translateX(${(f / OUTRO_DURATION) * 40 - 20}px)` }} />
        <div style={{ position: "absolute", left: "50%", top: 820, width: 900, height: 900, transform: "translate(-50%,-50%)", background: "radial-gradient(circle at center, rgba(76,197,237,0.18) 0%, rgba(76,197,237,0) 62%)" }} />
        <AbsoluteFill style={{ background: "radial-gradient(ellipse 80% 70% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)" }} />
      </AbsoluteFill>

      <Img src={staticFile(cfg.logo)} style={{ position: "absolute", left: "50%", top: 225, width: 456, transform: `translate(-50%,-50%) scale(${logoS})`, opacity: logoO }} />

      <div style={{ position: "absolute", left: "50%", top: 395, width: 408, height: 850, transform: "translateX(-50%)", perspective: 1700 }}>
        <div style={{ position: "relative", width: "100%", height: "100%", transformStyle: "preserve-3d", transform: `rotateY(${angle}deg) scale(${phoneS})`, opacity: phoneO }}>
          <div style={face}>
            <div style={{ width: "100%", height: "100%", borderRadius: 46, overflow: "hidden", background: "#fff" }}>
              <Img src={staticFile(cfg.siteScreenshot)} style={{ width: "100%", display: "block" }} />
            </div>
            <div style={{ position: "absolute", inset: 0, borderRadius: 58, background: `linear-gradient(${100 + angle / 4}deg, rgba(255,255,255,0) 30%, rgba(255,255,255,${sheen}) 50%, rgba(255,255,255,0) 70%)` }} />
          </div>
          <div style={{ ...face, transform: "rotateY(180deg)", display: "flex", alignItems: "center", justifyContent: "center", background: "linear-gradient(150deg,#16263f 0%,#0a1322 55%,#132741 100%)" }}>
            <Img src={staticFile(cfg.phoneBackLogo)} style={{ width: 150, opacity: 0.9 }} />
          </div>
        </div>
      </div>

      <div style={{ position: "absolute", left: 90, right: 90, top: 1282, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, direction: "rtl" }}>
        {cfg.services.map((s, i) => {
          const a = cfg.timing.servicesStart + i * cfg.timing.servicesStagger;
          const o = tw(f, [a, a + 0.45], 0, 1);
          return (
            <span key={s} style={{ display: "flex", alignItems: "center", gap: 16, padding: "0 36px", height: 88, borderRadius: 22, background: "rgba(10,24,46,0.72)", border: "1.5px solid rgba(76,197,237,0.42)", color: C.text, fontWeight: 500, fontSize: 38, opacity: o, transform: `translateY(${(1 - o) * 14}px)` }}>
              <i style={{ width: 10, height: 10, borderRadius: "50%", background: C.accent, flex: "none" }} />
              {s}
            </span>
          );
        })}
      </div>

      <div style={{ position: "absolute", left: "50%", top: 1532, width: 120, height: 4, borderRadius: 4, background: C.accent, transform: `translateX(-50%) scaleX(${line})` }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 1566, textAlign: "center", direction: "ltr", fontWeight: 500, fontSize: 68, letterSpacing: 1.5, color: C.text, opacity: urlO, transform: `translateY(${urlY}px)`, textShadow: `0 0 ${30 * urlGlow}px rgba(76,197,237,${0.8 * urlGlow})` }}>
        {cfg.url}
      </div>

      <Cursor f={f} />
      <AbsoluteFill style={{ background: "#000", opacity: end }} />
      {withAudio && <Audio src={staticFile("audio/outro.wav")} />}
    </AbsoluteFill>
  );
};
