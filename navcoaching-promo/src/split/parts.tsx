import React from "react";
import { AbsoluteFill, Img, interpolate, OffthreadVideo, random, staticFile, useCurrentFrame } from "remotion";
import { C, FONT, MONO } from "../theme";
import { KWord, LogoMark } from "../components/Brand";
import { clamp, pulse, ramp, sp, SPR } from "../lib/motion";
import { CAPTIONS, DAYS, SHOTS, Day, Shot, listActiveAt } from "./data";

/* ------------------------------------------------------------------ film look overlays */

export const Grain: React.FC<{ opacity?: number }> = ({ opacity = 0.17 }) => {
  const f = useCurrentFrame();
  const x = Math.floor(random(`gx${f}`) * 600);
  const y = Math.floor(random(`gy${f}`) * 900);
  return (
    <AbsoluteFill
      style={{
        backgroundImage: `url(${staticFile("split/noise.png")})`,
        backgroundSize: "1080px 1920px",
        backgroundPosition: `${-x}px ${-y}px`,
        mixBlendMode: "overlay",
        opacity,
        pointerEvents: "none",
      }}
    />
  );
};

export const Vignette: React.FC<{ strength?: number }> = ({ strength = 0.55 }) => (
  <AbsoluteFill
    style={{
      pointerEvents: "none",
      background: `radial-gradient(ellipse 78% 62% at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,${strength}) 100%)`,
    }}
  />
);

/** Warm/teal light leak that blooms on cuts. */
export const LightLeaks: React.FC<{ at: number[] }> = ({ at }) => {
  const f = useCurrentFrame();
  let a = 0;
  let k = 0;
  at.forEach((t, i) => {
    const p = pulse(f, t, 22, 1.6);
    if (p > a) {
      a = p;
      k = i;
    }
  });
  if (a <= 0.01) return null;
  const warm = k % 2 === 0;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        mixBlendMode: "screen",
        opacity: a * 0.55,
        background: warm
          ? "radial-gradient(ellipse 70% 40% at 100% 20%, rgba(255,150,60,0.9), rgba(255,90,30,0) 70%), radial-gradient(ellipse 50% 40% at 0% 90%, rgba(76,197,237,0.7), rgba(76,197,237,0) 70%)"
          : "radial-gradient(ellipse 70% 40% at 0% 25%, rgba(76,197,237,0.9), rgba(40,77,160,0) 70%), radial-gradient(ellipse 50% 40% at 100% 85%, rgba(255,140,60,0.6), rgba(255,90,30,0) 70%)",
      }}
    />
  );
};

export const Flash: React.FC<{ at: number[]; strong?: number[] }> = ({ at, strong = [] }) => {
  const f = useCurrentFrame();
  let a = 0;
  for (const t of at) a = Math.max(a, 0.55 * pulse(f, t, 10, 2));
  for (const t of strong) a = Math.max(a, 0.9 * pulse(f, t, 16, 2));
  if (a <= 0.01) return null;
  return <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 45%, #fff 0%, rgba(160,225,255,0.8) 40%, rgba(76,197,237,0) 100%)", opacity: a, mixBlendMode: "screen", pointerEvents: "none" }} />;
};

export const Backdrop: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#04070d" }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse 90% 55% at 50% ${40 + Math.sin(f / 90) * 4}%, #0f2748 0%, #070f1d 55%, #03060b 100%)` }} />
      <AbsoluteFill
        style={{
          backgroundImage: "linear-gradient(rgba(76,197,237,0.07) 2px, transparent 2px), linear-gradient(90deg, rgba(76,197,237,0.07) 2px, transparent 2px)",
          backgroundSize: "90px 90px",
          backgroundPosition: `0 ${(f * 0.6) % 90}px`,
          WebkitMaskImage: "radial-gradient(ellipse 80% 60% at 50% 50%, #000 20%, transparent 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ shots */

const BOX: Record<string, [number, number, number, number]> = {
  t1: [60, 600, 470, 352],
  t2: [550, 600, 470, 352],
  t3: [60, 980, 960, 540],
  a1: [60, 560, 960, 720],
  a2: [60, 560, 960, 720],
  a3: [60, 560, 960, 720],
};
const DEFAULT_BOX: [number, number, number, number] = [60, 700, 960, 720];
const DELAY: Record<string, number> = { t2: 7, t3: 14 };
const PLAIN_BG = new Set(["t1", "t2", "t3", "a1", "a2", "a3"]);

export const ShotView: React.FC<{ shot: Shot }> = ({ shot }) => {
  const f = useCurrentFrame();
  const src = staticFile(`split/clips/${shot.id}.mp4`);
  const push = interpolate(f, [0, shot.dur], [1, 1.055], clamp);
  const vid: React.CSSProperties = { width: "100%", height: "100%", objectFit: "cover" };

  if (shot.layout === "full") {
    const punch = interpolate(f, [0, 10], [1.09, 1], { ...clamp, easing: (t) => 1 - Math.pow(1 - t, 3) });
    const isBg = shot.id === "cta";
    return (
      <AbsoluteFill style={{ transform: `scale(${punch * push * (isBg ? 1.12 : 1)})`, filter: isBg ? "blur(16px) brightness(0.68) saturate(1.15)" : undefined }}>
        <OffthreadVideo src={src} muted style={vid} />
      </AbsoluteFill>
    );
  }

  const dflt: [number, number, number, number] = listActiveAt(shot.from + f) ? [60, 430, 960, 720] : DEFAULT_BOX;
  const [x, y, w, h] = BOX[shot.id] ?? dflt;
  const p = sp(f, DELAY[shot.id] ?? 0, SPR.snappy);
  const blurredBg = !PLAIN_BG.has(shot.id);
  return (
    <>
      {blurredBg && (
        <AbsoluteFill style={{ transform: "scale(1.35)", filter: "blur(38px) brightness(0.42) saturate(1.2)" }}>
          <OffthreadVideo src={src} muted style={vid} />
        </AbsoluteFill>
      )}
      <div
        style={{
          position: "absolute",
          left: x,
          top: y,
          width: w,
          height: h,
          borderRadius: 34,
          overflow: "hidden",
          opacity: Math.min(1, p * 2.2),
          transform: `scale(${0.9 + 0.1 * p}) rotate(${(1 - p) * -2.5}deg)`,
          boxShadow: "0 34px 90px rgba(0,0,0,0.65), 0 0 0 2px rgba(76,197,237,0.4), 0 0 70px rgba(76,197,237,0.2)",
        }}
      >
        <div style={{ position: "absolute", inset: 0, transform: `scale(${push})` }}>
          <OffthreadVideo src={src} muted style={vid} />
        </div>
      </div>
    </>
  );
};

/** Layout of the shot playing at frame f (decides where captions sit). */
export const layoutAt = (f: number): Shot["layout"] => {
  const s = SHOTS.filter((x) => f >= x.from && f < x.from + x.dur && !PLAIN_BG.has(x.id));
  return s.length ? s[0].layout : "full";
};

/* ------------------------------------------------------------------ captions (word by word, like the reference) */

export const Words: React.FC = () => {
  const f = useCurrentFrame();
  const c = CAPTIONS.find((x) => f >= x.at && f < (x.to ?? x.at + 50));
  if (!c) return null;
  const to = c.to ?? c.at + 50;
  const p = sp(f, c.at, { damping: 14, stiffness: 300, mass: 0.55 });
  const out = ramp(f, [to - 4, to]);
  const layout = layoutAt(f);
  const listing = listActiveAt(f);
  const y = layout === "card" ? (listing ? 1205 : 1580) : listing ? 1140 : 1230;
  const fs = c.text.length > 18 ? 66 : c.text.length > 12 ? 78 : 92;
  const base: React.CSSProperties = {
    display: "inline-block",
    fontFamily: FONT,
    fontWeight: 700,
    fontSize: fs,
    lineHeight: 1.25,
    direction: "rtl",
    whiteSpace: "nowrap",
  };
  return (
    <div
      style={{
        position: "absolute",
        left: 20,
        right: 20,
        top: y,
        textAlign: "center",
        opacity: Math.min(1, p * 2.5) * (1 - out),
        transform: `translateY(${-50 + (1 - p) * 4}%) scale(${0.72 + 0.28 * p})`,
        filter: p < 0.6 ? `blur(${(0.6 - p) * 12}px)` : undefined,
      }}
    >
      {c.hl ? (
        <span
          style={{
            ...base,
            color: "#04121f",
            background: C.cyan,
            padding: "4px 34px 10px",
            borderRadius: 22,
            transform: "rotate(-2deg)",
            boxShadow: "0 0 50px rgba(76,197,237,0.65), 0 14px 30px rgba(0,0,0,0.5)",
          }}
        >
          {c.text}
        </span>
      ) : (
        <span style={{ ...base, color: "#fff", textShadow: "0 4px 30px rgba(0,0,0,0.9), 0 0 3px rgba(0,0,0,0.85), 0 0 70px rgba(0,0,0,0.6)" }}>{c.text}</span>
      )}
    </div>
  );
};

/* ------------------------------------------------------------------ day title, chip, list */

export const DayTitle: React.FC<{ day: Day }> = ({ day }) => {
  const f = useCurrentFrame();
  const t = f - day.from;
  if (t < 0 || t > 122) return null;
  const out = ramp(f, [day.from + 96, day.from + 118]);
  const bar = ramp(f, [day.from + 14, day.from + 40]);
  return (
    <AbsoluteFill style={{ direction: "rtl", opacity: 1 - out, transform: `translateY(${-out * 50}px)` }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 1000, background: "linear-gradient(180deg, rgba(0,0,0,0.72), rgba(0,0,0,0.35) 60%, rgba(0,0,0,0))" }} />
      <div style={{ position: "absolute", top: 250, right: 70, left: 70 }}>
        <div style={{ fontFamily: MONO, fontSize: 30, letterSpacing: 9, color: C.cyan, direction: "ltr", textAlign: "right", opacity: ramp(f, [day.from + 6, day.from + 20]) }}>{day.en}</div>
        <div style={{ transform: "skewX(-7deg)", transformOrigin: "right center" }}>
          <KWord text={day.big} at={day.from} size={200} weight={800} glow style={{ display: "block", lineHeight: 1.05 }} />
        </div>
        <div style={{ transform: "skewX(-7deg)", transformOrigin: "right center", marginTop: -6 }}>
          <KWord
            text={day.sub}
            at={day.from + 10}
            size={day.sub.length > 8 ? 112 : 150}
            weight={700}
            gradient={`linear-gradient(100deg, #ffffff 0%, ${C.cyan} 55%, #7fdcff 100%)`}
            style={{ display: "block", lineHeight: 1.15 }}
          />
        </div>
        <div style={{ marginTop: 22, height: 9, width: 640 * bar, background: `linear-gradient(90deg, ${C.cyan}, rgba(76,197,237,0))`, marginLeft: "auto", transform: "skewX(-28deg)", boxShadow: `0 0 24px ${C.cyan}` }} />
      </div>
    </AbsoluteFill>
  );
};

export const DayChip: React.FC = () => {
  const f = useCurrentFrame();
  const day = DAYS.find((d) => f >= d.from && f < d.to);
  if (!day) return null;
  const inP = ramp(f, [day.from + 108, day.from + 126]);
  const out = ramp(f, [day.to - 10, day.to]);
  return (
    <div
      style={{
        position: "absolute",
        top: 196,
        right: 60,
        direction: "rtl",
        display: "flex",
        alignItems: "center",
        gap: 14,
        padding: "10px 26px",
        borderRadius: 999,
        background: "rgba(4,10,20,0.7)",
        border: `2px solid ${C.cyan}`,
        boxShadow: "0 0 30px rgba(76,197,237,0.3)",
        fontFamily: FONT,
        fontWeight: 700,
        fontSize: 34,
        color: "#fff",
        opacity: inP * (1 - out),
        transform: `translateY(${(1 - inP) * -20}px)`,
      }}
    >
      <span style={{ color: C.cyan, fontFamily: MONO }}>{String(day.n).padStart(2, "0")}</span>
      {day.sub}
    </div>
  );
};

export const ExerciseList: React.FC = () => {
  const f = useCurrentFrame();
  const day = DAYS.find((d) => f >= d.list.from && f < d.to);
  if (!day) return null;
  const { list } = day;
  const p = sp(f, list.from, SPR.soft);
  const out = ramp(f, [day.to - 10, day.to]);
  return (
    <div
      style={{
        position: "absolute",
        top: 1290,
        left: 60,
        right: 60,
        direction: "rtl",
        borderRadius: 26,
        padding: "20px 30px 14px",
        background: "linear-gradient(90deg, rgba(4,10,20,0.62), rgba(4,10,20,0.84))",
        borderRight: `6px solid ${C.cyan}`,
        boxShadow: "0 24px 70px rgba(0,0,0,0.55), 0 0 0 1px rgba(76,197,237,0.18)",
        opacity: Math.min(1, p * 2) * (1 - out),
        transform: `translateY(${(1 - p) * 90}px)`,
      }}
    >
      <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 30, color: C.cyan, marginBottom: 8, display: "flex", justifyContent: "space-between" }}>
        <span>{list.title}</span>
        <span style={{ fontFamily: MONO, fontSize: 22, color: C.muted, letterSpacing: 3 }}>SETS×REPS</span>
      </div>
      {list.items.map(([name, sets], i) => {
        const at = list.from + 10 + i * 9;
        const r = sp(f, at, SPR.snappy);
        return (
          <div
            key={name}
            style={{
              height: 62,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              borderTop: i ? "1px solid rgba(255,255,255,0.1)" : undefined,
              opacity: Math.min(1, r * 2),
              transform: `translateX(${(1 - r) * 60}px)`,
            }}
          >
            <span style={{ display: "flex", alignItems: "center", gap: 18, fontFamily: FONT, fontWeight: 600, fontSize: 38, color: "#fff" }}>
              <span style={{ width: 40, height: 40, borderRadius: "50%", background: C.cyan, color: "#04121f", display: "grid", placeItems: "center", fontFamily: MONO, fontWeight: 700, fontSize: 24 }}>{i + 1}</span>
              {name}
            </span>
            <span style={{ fontFamily: MONO, fontWeight: 700, fontSize: 32, color: C.cyan, direction: "ltr" }}>{sets}</span>
          </div>
        );
      })}
    </div>
  );
};

/* ------------------------------------------------------------------ persistent brand chrome */

export const TopBar: React.FC = () => {
  const f = useCurrentFrame();
  const show = ramp(f, [20, 40]) * (1 - ramp(f, [236, 244])) * (f < 360 ? 0 : 1) + (f >= 360 && f < 2640 ? 0 : 0);
  const brand = f < 240 ? ramp(f, [10, 34]) : f >= 360 && f < 2640 ? 1 : 0;
  const bars = f >= 360 && f < 2400 ? ramp(f, [360, 390]) * (1 - ramp(f, [2380, 2400])) : 0;
  if (brand <= 0 && bars <= 0 && show <= 0) return null;
  return (
    <div style={{ position: "absolute", top: 64, left: 60, right: 60, height: 90, direction: "rtl", opacity: 1 }}>
      <div style={{ position: "absolute", left: 0, top: 6, opacity: brand }}>
        <LogoMark width={150} glow={0.35} />
      </div>
      <div style={{ position: "absolute", right: 0, top: 20, width: 560, opacity: bars }}>
        <div style={{ fontFamily: FONT, fontWeight: 600, fontSize: 26, color: "#fff", textAlign: "right", marginBottom: 10, textShadow: "0 2px 12px rgba(0,0,0,0.8)" }}>خطة 3 أيام</div>
        <div style={{ display: "flex", gap: 10, direction: "rtl" }}>
          {DAYS.map((d) => {
            const fill = interpolate(f, [d.from, d.to], [0, 1], clamp);
            return (
              <div key={d.key} style={{ flex: 1, height: 8, borderRadius: 99, background: "rgba(255,255,255,0.22)", overflow: "hidden" }}>
                <div style={{ width: `${fill * 100}%`, height: "100%", background: C.cyan, boxShadow: `0 0 12px ${C.cyan}` }} />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export const Corners: React.FC<{ from: number; to: number }> = ({ from, to }) => {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const p = ramp(f, [from, from + 16]) * (1 - ramp(f, [to - 10, to]));
  const c = (pos: React.CSSProperties, rot: number) => (
    <div style={{ position: "absolute", width: 70, height: 70, ...pos, transform: `rotate(${rot}deg) scale(${0.7 + 0.3 * p})`, opacity: p * 0.85, borderTop: `3px solid ${C.cyan}`, borderLeft: `3px solid ${C.cyan}`, filter: `drop-shadow(0 0 8px ${C.cyan})` }} />
  );
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {c({ left: 40, top: 40 }, 0)}
      {c({ right: 40, top: 40 }, 90)}
      {c({ right: 40, bottom: 40 }, 180)}
      {c({ left: 40, bottom: 40 }, 270)}
    </AbsoluteFill>
  );
};

export { Img };
