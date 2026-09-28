import React from "react";
import { AbsoluteFill, Img, interpolate, random, staticFile, useCurrentFrame } from "remotion";
import { FONT, MONO } from "../../theme";
import { L, SHADOW_2, SHADOW_3 } from "../theme";
import { J } from "../tl";
import { LogoMark } from "../../components/Brand";
import { BrowserWindow } from "../parts/Chrome";
import { Btn, Eyebrow, H, P, SiteHeader } from "../parts/Site";
import { clamp, pulse, ramp, sp, SPR } from "../../lib/motion";

const HK = J.hook;
const PV = J.pivot;
const LG = J.logoSeq;

/* ---------------- HOOK: scattered fitness advice ---------------- */

type Scrap = { x: number; y: number; r: number; w: number; el: React.ReactNode };
const scrapCard = (children: React.ReactNode, style?: React.CSSProperties) => (
  <div style={{ background: "#fff", borderRadius: 22, boxShadow: SHADOW_2, padding: "20px 24px", fontFamily: FONT, direction: "rtl", ...style }}>{children}</div>
);
const Video: React.FC<{ title: string; dur: string }> = ({ title, dur }) =>
  scrapCard(
    <>
      <div style={{ height: 150, borderRadius: 14, background: "linear-gradient(135deg,#1b2a44,#0b1322)", position: "relative", display: "grid", placeItems: "center" }}>
        <span style={{ width: 0, height: 0, borderTop: "20px solid transparent", borderBottom: "20px solid transparent", borderLeft: "32px solid #fff" }} />
        <span style={{ position: "absolute", left: 10, bottom: 8, fontFamily: MONO, fontSize: 18, color: "#fff", background: "rgba(0,0,0,0.6)", padding: "2px 8px", borderRadius: 6 }}>{dur}</span>
      </div>
      <div style={{ marginTop: 10, fontSize: 22, fontWeight: 600, color: L.heading }}>{title}</div>
    </>,
  );

const SCRAPS: Scrap[] = [
  { x: 560, y: 560, r: -6, w: 400, el: <Video title="أقوى تمرين بطن في 5 دقايق 🔥" dur="0:47" /> },
  {
    x: 90, y: 600, r: 5, w: 380,
    el: scrapCard(
      <>
        <div style={{ fontSize: 26, fontWeight: 700, color: L.heading }}>جدول 12 أسبوع (من يوتيوب)</div>
        {["الأحد ✓", "الإثنين ✓", "الثلاثاء", "الأربعاء", "الخميس"].map((d, i) => (
          <div key={d} style={{ fontSize: 22, marginTop: 6, color: i < 2 ? L.text : "#c0392b", textDecoration: i >= 2 ? "line-through" : undefined }}>{d}</div>
        ))}
      </>,
    ),
  },
  { x: 640, y: 1000, r: 8, w: 330, el: scrapCard(<div style={{ fontSize: 28, fontWeight: 700, color: "#5a3d00" }}>لازم أبدأ!!<br /><span style={{ fontWeight: 400, fontSize: 24 }}>بس من وين؟</span></div>, { background: "#ffe8a3" }) },
  {
    x: 120, y: 1050, r: -4, w: 420,
    el: scrapCard(
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <span style={{ width: 54, height: 54, borderRadius: 14, background: "#fdecea", color: "#b42318", display: "grid", placeItems: "center", fontSize: 30, fontWeight: 700 }}>✕</span>
        <div>
          <div style={{ fontSize: 26, fontWeight: 700, color: L.heading }}>حمية الكيتو</div>
          <div style={{ fontSize: 22, color: "#b42318" }}>وقفت في اليوم 3</div>
        </div>
      </div>,
    ),
  },
  {
    x: 560, y: 1300, r: -7, w: 420,
    el: scrapCard(
      <>
        <div style={{ fontSize: 24, fontWeight: 700, color: L.heading }}>تطبيق السعرات 📱</div>
        <div style={{ fontSize: 21, color: L.muted }}>آخر دخول: قبل 21 يوم</div>
      </>,
    ),
  },
  {
    x: 70, y: 1380, r: 6, w: 420,
    el: scrapCard(
      <>
        <div style={{ fontSize: 22, color: L.muted }}>الالتزام</div>
        <div style={{ height: 14, borderRadius: 99, background: L.line, marginTop: 10 }}>
          <div style={{ width: "18%", height: "100%", borderRadius: 99, background: "#e5484d" }} />
        </div>
      </>,
    ),
  },
  { x: 600, y: 1580, r: 4, w: 380, el: scrapCard(<div style={{ fontSize: 26, color: L.heading }}>وش أتمرن اليوم؟ 🤔</div>, { borderRadius: "26px 26px 6px 26px" }) },
  { x: 110, y: 1620, r: -5, w: 400, el: <Video title="روتين الجيم الكامل" dur="1:12:40" /> },
];

export const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const collapse = ramp(f, [HK.collapse - 10, HK.collapse + 40], [0, 1], (t) => t * t * t);
  const jitterAmt = ramp(f, [240, 380]);
  const L2 = HK.lines2[0][0] as number;
  const phase2 = f >= L2 - 6;
  const outA = ramp(f, [L2 - 12, L2 - 2]);
  const exit = ramp(f, [430, 450]);
  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      {SCRAPS.map((s, i) => {
        const at = HK.cards[i];
        const p = sp(f, at, SPR.bouncy);
        if (f < at) return null;
        const jx = Math.sin(f / 3 + i * 2) * 5 * jitterAmt;
        const jy = Math.cos(f / 4 + i) * 5 * jitterAmt;
        const cx = 540 - (s.x + s.w / 2);
        const cy = 1150 - (s.y + 100);
        const drift = Math.sin(f / 40 + i) * 8;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: s.x + cx * collapse + jx,
              top: s.y + cy * collapse + jy + drift,
              width: s.w,
              transform: `rotate(${s.r * (1 - collapse) + (random(`r${i}`) - 0.5) * 60 * collapse}deg) scale(${interpolate(p, [0, 1], [0.5, 1]) * (1 - 0.8 * collapse)})`,
              opacity: Math.min(1, p * 2) * (1 - ramp(f, [HK.collapse + 20, HK.collapse + 45])),
              filter: collapse > 0.1 ? `blur(${collapse * 6}px)` : undefined,
            }}
          >
            {s.el}
          </div>
        );
      })}
      <div style={{ position: "absolute", top: 170, right: 70, left: 70, opacity: 1 - exit }}>
        {!phase2 &&
          HK.lines.map(([at, t]) => {
            const p = sp(f, at as number, SPR.snappy);
            return (
              <div key={t as string} style={{ fontFamily: FONT, fontWeight: 700, fontSize: 70, lineHeight: 1.3, color: L.heading, opacity: Math.min(1, p * 2) * (1 - outA), transform: `translateY(${(1 - p) * 30}px)` }}>
                {t}
              </div>
            );
          })}
        {phase2 &&
          HK.lines2.map(([at, t], i) => {
            const p = sp(f, at as number, i ? SPR.slam : SPR.snappy);
            return (
              <div
                key={t as string}
                style={{
                  fontFamily: FONT,
                  fontWeight: 700,
                  fontSize: i ? 96 : 70,
                  lineHeight: 1.3,
                  color: i ? "#e5484d" : L.heading,
                  opacity: Math.min(1, p * 2),
                  transform: `translateY(${(1 - p) * 30}px) scale(${i ? interpolate(p, [0, 1], [1.4, 1]) : 1})`,
                  transformOrigin: "right center",
                }}
              >
                {t}
              </div>
            );
          })}
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- PIVOT: one place ---------------- */

const HomeHero: React.FC = () => (
  <>
    <div style={{ position: "absolute", top: 120, right: 40, left: 40 }}>
      <Eyebrow>Nav Coaching</Eyebrow>
      <H size={60} style={{ marginTop: 14 }}>
        تدريب مبني عليك،
        <br />
        <span style={{ backgroundImage: `linear-gradient(transparent 62%, rgba(76,197,237,0.45) 62%)` }}>مو جدول جاهز</span>
      </H>
      <P size={28} style={{ marginTop: 14 }}>كل البرامج مخصصة لك بعد الاستبيان.</P>
    </div>
    <Btn style={{ position: "absolute", top: 440, right: 40 }}>اختر برنامجك ←</Btn>
    <Btn kind="ghost" style={{ position: "absolute", top: 440, right: 330 }}>أي برنامج يناسبني؟</Btn>
    <div style={{ position: "absolute", top: 560, left: 40, right: 40, borderRadius: 20, overflow: "hidden", border: `1px solid ${L.line}`, boxShadow: SHADOW_2 }}>
      <Img src={staticFile("shots/training.webp")} style={{ width: "100%", display: "block" }} />
    </div>
  </>
);

export const Pivot: React.FC = () => {
  const f = useCurrentFrame();
  const [S0, S1] = J.segments.pivot as [number, number];
  const w = sp(f, PV.window, SPR.soft);
  const ph = sp(f, PV.phone, SPR.bouncy);
  const exit = ramp(f, [S1 - 26, S1], [0, 1], (t) => t * t);
  return (
    <AbsoluteFill style={{ direction: "rtl", opacity: 1 - ramp(f, [S1 - 10, S1]) }}>
      <div style={{ position: "absolute", top: 150, right: 70, left: 70, transform: `translateY(${-exit * 60}px)` }}>
        {PV.lines.map(([at, t], i) => {
          const p = sp(f, at as number, i === 1 ? SPR.slam : SPR.snappy);
          const hl = ramp(f, [(at as number) + 6, (at as number) + 22]);
          return (
            <div
              key={t as string}
              style={{
                fontFamily: FONT,
                fontWeight: 700,
                fontSize: i === 1 ? 120 : i === 0 ? 64 : 46,
                lineHeight: 1.25,
                color: i >= 2 ? L.text : L.heading,
                opacity: Math.min(1, p * 2),
                transform: `translateY(${(1 - p) * 30}px) scale(${i === 1 ? interpolate(p, [0, 1], [1.3, 1]) : 1})`,
                transformOrigin: "right center",
              }}
            >
              {i === 1 ? (
                <span style={{ backgroundImage: `linear-gradient(${L.cyan}, ${L.cyan})`, backgroundSize: `${hl * 100}% 40%`, backgroundPosition: "right 88%", backgroundRepeat: "no-repeat", padding: "0 8px" }}>{t}</span>
              ) : (
                t
              )}
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", inset: 0, transform: `translateY(${(1 - w) * 500 + 120}px) scale(${0.9 + 0.1 * w - exit * 0.1})`, opacity: Math.min(1, w * 2) }}>
        <BrowserWindow>
          <HomeHero />
          <SiteHeader />
        </BrowserWindow>
      </div>
      {/* phone */}
      <div
        style={{
          position: "absolute",
          left: 20,
          top: 1180,
          width: 300,
          height: 610,
          borderRadius: 48,
          background: "#0b1322",
          padding: 12,
          boxShadow: SHADOW_3,
          opacity: Math.min(1, ph * 2) * (1 - exit),
          transform: `translateY(${(1 - ph) * 300}px) rotate(${-4 * ph}deg)`,
        }}
      >
        <div style={{ width: 276, height: 586, borderRadius: 38, overflow: "hidden", background: "#fff", position: "relative" }}>
          <div style={{ width: 1000, height: 2030, transform: "scale(0.276)", transformOrigin: "top left", position: "absolute", left: 0, top: 0, direction: "rtl" }}>
            <div style={{ position: "absolute", top: 0, left: 0, width: 1000, height: 2030 }}>
              <HomeHero />
              <SiteHeader />
            </div>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- LOGO ---------------- */

export const LogoScene: React.FC = () => {
  const f = useCurrentFrame();
  const [, S1] = J.segments.logo as [number, number];
  const s = sp(f, LG.hit, SPR.heavy);
  const word = sp(f, LG.hit + 10, SPR.soft);
  const line = sp(f, LG.line, SPR.snappy);
  const pill = sp(f, LG.pill, SPR.bouncy);
  const exit = ramp(f, [S1 - 20, S1], [0, 1], (t) => t * t);
  const ring = f >= LG.hit ? (f - LG.hit) / 40 : -1;
  return (
    <AbsoluteFill style={{ alignItems: "center", direction: "rtl", opacity: 1 - exit, transform: `translateY(${-exit * 80}px)` }}>
      {ring >= 0 && ring <= 1 && (
        <div
          style={{
            position: "absolute",
            left: 540 - 700 * ring,
            top: 700 - 700 * ring,
            width: 1400 * ring,
            height: 1400 * ring,
            borderRadius: "50%",
            border: `${6 * (1 - ring) + 1}px solid rgba(76,197,237,${1 - ring})`,
          }}
        />
      )}
      <div style={{ position: "absolute", top: 560, transform: `scale(${interpolate(s, [0, 1], [2.4, 1])})`, opacity: Math.min(1, s * 3) }}>
        <LogoMark width={520} glow={0.25 + 0.6 * pulse(f, LG.hit, 30)} sheen={ramp(f, [LG.hit + 20, LG.hit + 60])} />
      </div>
      <div style={{ position: "absolute", top: 820, fontFamily: FONT, fontWeight: 700, fontSize: 84, color: L.navy, opacity: word, letterSpacing: interpolate(word, [0, 1], [30, 2]) }}>Nav Coaching</div>
      <div style={{ position: "absolute", top: 935, fontFamily: MONO, fontSize: 28, letterSpacing: 7, color: L.cyanInk, opacity: ramp(f, [LG.hit + 24, LG.hit + 40]) }}>
        WHERE PASSION MEETS QUALITY
      </div>
      <div style={{ position: "absolute", top: 1080, fontFamily: FONT, fontWeight: 700, fontSize: 60, color: L.heading, opacity: Math.min(1, line * 2), transform: `translateY(${(1 - line) * 30}px)` }}>
        خلني أوريك الرحلة كاملة
      </div>
      <div
        style={{
          position: "absolute",
          top: 1190,
          padding: "14px 34px",
          borderRadius: 999,
          background: L.ink,
          color: L.cyan,
          fontFamily: FONT,
          fontWeight: 700,
          fontSize: 44,
          opacity: Math.min(1, pill * 2),
          transform: `scale(${interpolate(pill, [0, 1], [0.4, 1])})`,
        }}
      >
        ⏱ في دقيقة
      </div>
    </AbsoluteFill>
  );
};
