import React from "react";
import { AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import "../fonts";
import { FONT, MONO } from "../theme";
import { L, SHADOW_3 } from "../journey/theme";
import { LightBg } from "../journey/parts/Chrome";
import { LogoMark } from "../components/Brand";
import { clamp, pulse, ramp, sp, SPR } from "../lib/motion";
import { CAPTIONS, CHAPTERS, DURATION, MAN, RINGS, TAPS, captionAt, chapterAt, resolveRect, scrollOf, viewAt, viewIndexAt } from "./engine";

// Phone screen geometry: the 390x844 CSS viewport shown at 600 px wide.
const SW = 600;
const K = SW / MAN.device.w;
const SH = Math.round(MAN.device.h * K);
const BEZEL = 18;
const PX = (1080 - SW) / 2;
const PY = 372;

const TINTS = ["cyan", "lavender", "mint"] as const;
const TINT_OF = (i: number) => (i <= 0 || i >= CHAPTERS.length - 1 ? "neutral" : TINTS[i % 3]);

/** One view (page at a scroll, or a state screenshot) rendered at screen scale. */
const ViewLayer: React.FC<{ i: number; f: number; style?: React.CSSProperties }> = ({ i, f, style }) => {
  const v = viewAt(i);
  if (v.state) {
    return <Img src={staticFile(MAN.states[v.state].src)} style={{ position: "absolute", left: 0, top: 0, width: SW, height: SH, ...style }} />;
  }
  const p = MAN.pages[v.page];
  const s = scrollOf(i, f);
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", ...style }}>
      <div style={{ position: "absolute", left: 0, top: -s * K, width: SW }}>
        {p.tiles
          .filter((t) => t.y + t.h > s - 50 && t.y < s + MAN.device.h + 50)
          .map((t) => (
            <Img key={t.src} src={staticFile(t.src)} style={{ position: "absolute", left: 0, top: t.y * K, width: SW, height: t.h * K }} />
          ))}
      </div>
      {s > 0.5 && <Img src={staticFile(p.header)} style={{ position: "absolute", left: 0, top: 0, width: SW, height: 69 * K }} />}
    </div>
  );
};

const Screen: React.FC = () => {
  const f = useCurrentFrame();
  const i = viewIndexAt(f);
  const cur = viewAt(i);
  const prev = i > 0 ? viewAt(i - 1) : null;
  const t = f - cur.at;
  let content: React.ReactNode;
  if (prev && t < 18) {
    const samePage = prev.page === cur.page;
    const ps = scrollOf(i - 1, cur.at);
    const cs = scrollOf(i, f);
    const d = (cs - ps) * K;
    if (samePage && Math.abs(d) > 4) {
      // scroll-like transition between two captures of the same page
      const p = interpolate(t, [0, 16], [0, 1], { ...clamp, easing: (x) => 1 - Math.pow(1 - x, 3) });
      content = (
        <>
          <ViewLayer i={i - 1} f={cur.at} style={{ transform: `translateY(${-d * p}px)`, opacity: 1 - p }} />
          <ViewLayer i={i} f={f} style={{ transform: `translateY(${d * (1 - p)}px)`, opacity: p }} />
        </>
      );
    } else if (samePage) {
      const p = ramp(t, [0, 5]);
      content = (
        <>
          <ViewLayer i={i - 1} f={cur.at} />
          <ViewLayer i={i} f={f} style={{ opacity: p }} />
        </>
      );
    } else {
      // navigation to another page: quick fade with a slight lift
      const p = ramp(t, [0, 12]);
      content = (
        <>
          <ViewLayer i={i - 1} f={cur.at} style={{ opacity: 1 - p }} />
          <ViewLayer i={i} f={f} style={{ opacity: p, transform: `translateY(${(1 - p) * 30}px)` }} />
        </>
      );
    }
  } else {
    content = <ViewLayer i={i} f={f} />;
  }

  // visible scroll right now, for placing taps/rings on page coordinates
  const sNow = scrollOf(i, f);
  const toScreen = (r: { x: number; y: number; w: number; h: number }) => ({ x: r.x * K, y: (r.y - sNow) * K, w: r.w * K, h: r.h * K });
  const badge = MAN.overlays.badge;

  return (
    <div style={{ position: "absolute", left: PX, top: PY, width: SW, height: SH, overflow: "hidden", borderRadius: 46, background: "#fff" }}>
      {content}
      {badge && <Img src={staticFile(badge.src)} style={{ position: "absolute", left: badge.x * K, top: badge.y * K, width: badge.w * K, height: badge.h * K }} />}
      {RINGS.filter((r) => f >= r.at && f < r.at + r.dur).map((r) => {
        const rect = resolveRect(r.ref);
        if (!rect) return null;
        const s = toScreen(rect);
        const p = ramp(f, [r.at, r.at + 10]) * (1 - ramp(f, [r.at + r.dur - 10, r.at + r.dur]));
        const g = 0.5 + 0.5 * Math.sin((f - r.at) / 6);
        return (
          <div
            key={r.at}
            style={{
              position: "absolute",
              left: s.x - 8,
              top: s.y - 8,
              width: s.w + 16,
              height: s.h + 16,
              borderRadius: 18,
              border: `4px solid rgba(76,197,237,${p})`,
              boxShadow: `0 0 ${16 + 12 * g}px rgba(76,197,237,${0.7 * p}), 0 0 0 2000px rgba(11,26,51,${0.28 * p})`,
            }}
          />
        );
      })}
      {TAPS.filter((tp) => f >= tp.at - 10 && f < tp.at + 22).map((tp) => {
        const rect = resolveRect(tp.ref);
        if (!rect) return null;
        const s = toScreen(rect);
        const cx = s.x + s.w / 2;
        const cy = s.y + s.h / 2;
        const pre = ramp(f, [tp.at - 10, tp.at]);
        const post = f >= tp.at ? (f - tp.at) / 22 : 0;
        const r0 = 34;
        return (
          <React.Fragment key={tp.at}>
            <div
              style={{
                position: "absolute",
                left: cx - r0,
                top: cy - r0,
                width: r0 * 2,
                height: r0 * 2,
                borderRadius: "50%",
                background: `rgba(20,30,50,${0.28 * pre * (1 - post)})`,
                border: `3px solid rgba(255,255,255,${0.9 * pre * (1 - post)})`,
                transform: `scale(${f < tp.at ? 1.25 - 0.25 * pre : 0.9})`,
              }}
            />
            {post > 0 && (
              <div
                style={{
                  position: "absolute",
                  left: cx - r0 * (1 + post * 1.6),
                  top: cy - r0 * (1 + post * 1.6),
                  width: r0 * 2 * (1 + post * 1.6),
                  height: r0 * 2 * (1 + post * 1.6),
                  borderRadius: "50%",
                  border: `4px solid rgba(76,197,237,${1 - post})`,
                }}
              />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};

const Phone: React.FC = () => {
  const f = useCurrentFrame();
  const inP = sp(f, 20, SPR.soft);
  const outro = CHAPTERS[CHAPTERS.length - 1];
  const out = ramp(f, [outro.start + 200, outro.start + 240], [0, 1], (t) => t * t);
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        opacity: Math.min(1, inP * 1.5) * (1 - out),
        transform: `translateY(${(1 - inP) * 400 + out * 120}px) scale(${0.92 + 0.08 * inP - out * 0.08})`,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: PX - BEZEL,
          top: PY - BEZEL,
          width: SW + BEZEL * 2,
          height: SH + BEZEL * 2,
          borderRadius: 64,
          background: "#0b1322",
          boxShadow: `${SHADOW_3}, inset 0 0 0 2px #2a3550`,
        }}
      />
      <Screen />
      {/* dynamic island */}
      <div style={{ position: "absolute", left: 540 - 60, top: PY + 8, width: 120, height: 30, borderRadius: 20, background: "#0b1322" }} />
    </div>
  );
};

const Header: React.FC = () => {
  const f = useCurrentFrame();
  const idx = chapterAt(f);
  if (idx < 0) return null;
  const ch = CHAPTERS[idx];
  const inP = sp(f, ch.start, SPR.snappy);
  const out = ramp(f, [ch.end - 12, ch.end]);
  const steps = CHAPTERS.slice(1, -1);
  return (
    <div style={{ position: "absolute", left: 60, right: 60, top: 70, direction: "rtl" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <span style={{ fontFamily: FONT, fontWeight: 700, fontSize: 28, color: L.heading, whiteSpace: "nowrap" }}>Nav Coaching</span>
        <div style={{ flex: 1, display: "flex", gap: 6 }}>
          {steps.map((c, k) => {
            const fill = interpolate(f, [c.start, c.end], [0, 1], clamp);
            return (
              <div key={c.key} style={{ flex: 1, height: 8, borderRadius: 99, background: "rgba(40,77,160,0.14)", overflow: "hidden" }}>
                <div style={{ width: `${fill * 100}%`, height: "100%", background: k + 1 === idx ? L.navy : L.cyan }} />
              </div>
            );
          })}
        </div>
      </div>
      <div style={{ opacity: inP * (1 - out), transform: `translateY(${(1 - inP) * 30}px)` }}>
        {idx > 0 && idx < CHAPTERS.length - 1 && (
          <span
            style={{
              display: "inline-flex",
              marginTop: 26,
              fontFamily: FONT,
              fontWeight: 600,
              fontSize: 24,
              background: L.ink,
              color: "#fff",
              padding: "6px 18px",
              borderRadius: 999,
            }}
          >
            الخطوة {idx} من {steps.length}
          </span>
        )}
        <div style={{ marginTop: idx > 0 && idx < CHAPTERS.length - 1 ? 6 : 34, fontFamily: FONT, fontWeight: 700, fontSize: 70, lineHeight: 1.15, color: L.heading }}>{ch.title}</div>
        <div style={{ fontFamily: FONT, fontSize: 32, color: L.muted }}>{ch.sub}</div>
      </div>
    </div>
  );
};

const Caption: React.FC = () => {
  const f = useCurrentFrame();
  const c = captionAt(f);
  if (!c) return null;
  const p = sp(f, c.at, SPR.snappy);
  const out = ramp(f, [c.end - 10, c.end]);
  const next = CAPTIONS.find((x) => x.at > c.at && x.at <= c.end);
  const leave = next ? ramp(f, [next.at - 6, next.at]) : 0;
  return (
    <div
      style={{
        position: "absolute",
        top: PY + SH + BEZEL + 26,
        left: 60,
        right: 60,
        display: "flex",
        justifyContent: "center",
        opacity: Math.min(1, p * 1.5) * (1 - out) * (1 - leave),
        transform: `translateY(${(1 - p) * 20}px)`,
      }}
    >
      <div
        style={{
          direction: "rtl",
          fontFamily: FONT,
          fontWeight: 700,
          fontSize: 40,
          lineHeight: 1.35,
          color: L.heading,
          textAlign: "center",
          background: "rgba(255,255,255,0.85)",
          border: `1px solid ${L.line}`,
          borderRadius: 26,
          padding: "14px 30px",
          boxShadow: "0 10px 30px rgba(7,20,42,0.10)",
        }}
      >
        {c.text}
      </div>
    </div>
  );
};

const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  const o = CHAPTERS[CHAPTERS.length - 1];
  const at = o.start + 230;
  if (f < at) return null;
  const s = sp(f, at, SPR.heavy);
  const btn = sp(f, at + 40, SPR.bouncy);
  const typed = Math.min(15, Math.max(0, Math.floor((f - at - 20) / 3)));
  return (
    <AbsoluteFill style={{ alignItems: "center", direction: "rtl" }}>
      <div style={{ position: "absolute", top: 620, transform: `scale(${interpolate(s, [0, 1], [2, 1])})`, opacity: Math.min(1, s * 3) }}>
        <LogoMark width={440} glow={0.3 + 0.6 * pulse(f, at, 30)} />
      </div>
      <div style={{ position: "absolute", top: 840, fontFamily: FONT, fontWeight: 700, fontSize: 76, color: L.navy, opacity: ramp(f, [at + 10, at + 26]) }}>Nav Coaching</div>
      <div
        style={{
          position: "absolute",
          top: 1010,
          padding: "16px 44px",
          borderRadius: 22,
          background: "#fff",
          border: `2px solid ${L.line}`,
          fontFamily: MONO,
          fontWeight: 700,
          fontSize: 52,
          color: L.heading,
          direction: "ltr",
          minWidth: 600,
          textAlign: "center",
          opacity: ramp(f, [at + 14, at + 24]),
        }}
      >
        {"navcoaching.com".slice(0, typed)}
        <span style={{ opacity: f % 30 < 15 ? 1 : 0, color: L.cyan }}>|</span>
      </div>
      <div
        style={{
          position: "absolute",
          top: 1170,
          height: 104,
          padding: "0 64px",
          display: "flex",
          alignItems: "center",
          borderRadius: 999,
          background: L.navy,
          color: "#fff",
          fontFamily: FONT,
          fontWeight: 700,
          fontSize: 50,
          opacity: Math.min(1, btn * 2),
          transform: `scale(${interpolate(btn, [0, 1], [0.5, 1])})`,
        }}
      >
        اختر برنامجك ←
      </div>
    </AbsoluteFill>
  );
};

export const Tutorial: React.FC<{ withAudio?: boolean }> = ({ withAudio = true }) => {
  const f = useCurrentFrame();
  const idx = Math.max(0, chapterAt(f));
  return (
    <AbsoluteFill style={{ background: L.paper }}>
      <LightBg tint={TINT_OF(idx)} />
      <Header />
      <Phone />
      <Caption />
      <EndCard />
      {withAudio && <Audio src={staticFile("audio/tutorial.wav")} />}
    </AbsoluteFill>
  );
};

export const TUTORIAL_DURATION = DURATION;
