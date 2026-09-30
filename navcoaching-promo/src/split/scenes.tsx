import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT, MONO } from "../theme";
import { KWord, LogoMark, Shockwave } from "../components/Brand";
import { Cursor } from "../components/Ui";
import { clamp, pulse, ramp, sp, SPR } from "../lib/motion";
import { CREDIT, SEC, URL_TEXT } from "./data";

export const TitleScene: React.FC = () => {
  const f = useCurrentFrame();
  const [a] = SEC.title;
  if (f < a - 2 || f >= SEC.title[1]) return null;
  const out = ramp(f, [SEC.title[1] - 10, SEC.title[1]]);
  const chips = ["أرجل", "جزء علوي", "جسم كامل"];
  return (
    <AbsoluteFill style={{ direction: "rtl", opacity: 1 - out }}>
      <div style={{ position: "absolute", top: 70, left: 0, right: 0, display: "flex", justifyContent: "center", transform: `scale(${interpolate(sp(f, a, SPR.slam), [0, 1], [1.8, 1])})`, opacity: Math.min(1, sp(f, a, SPR.slam) * 3) }}>
        <LogoMark width={250} glow={0.6} />
      </div>
      <div style={{ position: "absolute", top: 230, left: 40, right: 40, textAlign: "center" }}>
        <KWord text="خطة تمرين" at={a + 6} size={92} weight={600} color={C.text} />
        <div>
          <KWord text="3 أيام" at={a + 14} size={230} weight={800} glow gradient={`linear-gradient(100deg, #ffffff 0%, ${C.cyan} 50%, #7fdcff 100%)`} />
        </div>
      </div>
      <div style={{ position: "absolute", top: 1590, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 18 }}>
        {chips.map((c, i) => {
          const p = sp(f, a + 40 + i * 9, SPR.bouncy);
          return (
            <span
              key={c}
              style={{
                fontFamily: FONT,
                fontWeight: 700,
                fontSize: 42,
                color: i === 1 ? "#04121f" : "#fff",
                background: i === 1 ? C.cyan : "rgba(255,255,255,0.1)",
                border: `2px solid ${i === 1 ? C.cyan : "rgba(255,255,255,0.35)"}`,
                borderRadius: 999,
                padding: "8px 30px 12px",
                opacity: Math.min(1, p * 2),
                transform: `scale(${0.4 + 0.6 * p})`,
              }}
            >
              {c}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const RestScene: React.FC<{ from: number; to: number }> = ({ from, to }) => {
  const f = useCurrentFrame();
  if (f < from || f >= to) return null;
  const inP = ramp(f, [from, from + 10]);
  const out = ramp(f, [to - 8, to]);
  const sub = sp(f, from + 34, SPR.soft);
  return (
    <AbsoluteFill style={{ direction: "rtl", opacity: inP * (1 - out) }}>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(3,6,12,0.78), rgba(3,6,12,0.5) 40%, rgba(3,6,12,0.82))" }} />
      <div style={{ position: "absolute", top: 640, left: 40, right: 40, textAlign: "center" }}>
        <div style={{ fontFamily: MONO, fontSize: 30, letterSpacing: 14, color: C.cyan, opacity: ramp(f, [from + 4, from + 18]) }}>REST DAY</div>
        <div style={{ transform: "skewX(-7deg)" }}>
          <KWord text="يوم راحة" at={from + 6} size={190} weight={800} glow />
        </div>
        <div style={{ marginTop: 8, fontFamily: FONT, fontWeight: 600, fontSize: 54, color: "#fff", textShadow: "0 3px 24px rgba(0,0,0,0.95)", opacity: sub, transform: `translateY(${(1 - sub) * 24}px)` }}>جسمك يبني وأنت مرتاح</div>
      </div>
    </AbsoluteFill>
  );
};

export const AddOnsScene: React.FC = () => {
  const f = useCurrentFrame();
  const [a, b] = SEC.addons;
  if (f < a || f >= b) return null;
  const out = ramp(f, [b - 8, b]);
  const labels = ["مرونة", "قفزات بلايو", "كارديو"];
  const idx = Math.min(2, Math.floor((f - a) / 80));
  const head = sp(f, a + 2, SPR.snappy);
  return (
    <AbsoluteFill style={{ direction: "rtl", opacity: 1 - out }}>
      <div style={{ position: "absolute", top: 210, left: 40, right: 40, textAlign: "center", opacity: Math.min(1, head * 2), transform: `translateY(${(1 - head) * 30}px)` }}>
        <div style={{ fontFamily: MONO, fontSize: 28, letterSpacing: 10, color: C.cyan }}>OPTIONAL</div>
        <div style={{ fontFamily: FONT, fontWeight: 800, fontSize: 118, color: "#fff", lineHeight: 1.15, textShadow: "0 0 50px rgba(76,197,237,0.45)" }}>وإذا تبي أكثر…</div>
      </div>
      <div style={{ position: "absolute", top: 1360, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        {labels.map((l, i) => {
          if (i !== idx) return null;
          const p = sp(f, a + i * 80 + 4, SPR.bouncy);
          return (
            <span
              key={l}
              style={{
                fontFamily: FONT,
                fontWeight: 700,
                fontSize: 78,
                color: "#04121f",
                background: C.cyan,
                borderRadius: 26,
                padding: "6px 46px 14px",
                transform: `scale(${0.5 + 0.5 * p}) rotate(-2deg)`,
                opacity: Math.min(1, p * 2),
                boxShadow: "0 0 60px rgba(76,197,237,0.6)",
              }}
            >
              {l}
            </span>
          );
        })}
      </div>
      <div style={{ position: "absolute", top: 1560, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 16 }}>
        {labels.map((_, i) => (
          <span key={i} style={{ width: i === idx ? 54 : 16, height: 16, borderRadius: 99, background: i === idx ? C.cyan : "rgba(255,255,255,0.3)" }} />
        ))}
      </div>
    </AbsoluteFill>
  );
};

export const CtaScene: React.FC = () => {
  const f = useCurrentFrame();
  const [a, b] = SEC.cta;
  if (f < a) return null;
  const logoAt = a + 30;
  const s = sp(f, logoAt, SPR.heavy);
  const word = ramp(f, [logoAt + 16, logoAt + 34]);
  const typed = Math.max(0, Math.min(URL_TEXT.length, Math.floor((f - (a + 170)) / 4)));
  const btn = sp(f, a + 250, SPR.bouncy);
  const click = a + 350;
  const press = f >= click - 3 && f < click + 8 ? 1 - Math.abs(f - click) / 8 : 0;
  const glow = pulse(f, click, 30, 1.5);
  const credit = ramp(f, [a + 120, a + 150]);
  const end = ramp(f, [b - 22, b]);
  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(3,6,12,0.55), rgba(3,6,12,0.2) 40%, rgba(3,6,12,0.7))" }} />
      <Shockwave at={logoAt} y={720} size={1.1} />
      <div style={{ position: "absolute", top: 380, left: 0, right: 0, display: "flex", justifyContent: "center", transform: `scale(${interpolate(s, [0, 1], [3, 1])})`, opacity: Math.min(1, s * 3) }}>
        <LogoMark width={600} glow={0.5 + 1.4 * pulse(f, logoAt, 40)} sheen={ramp(f, [logoAt + 30, logoAt + 70])} />
      </div>
      <div style={{ position: "absolute", top: 640, left: 0, right: 0, textAlign: "center", fontFamily: FONT, fontWeight: 700, fontSize: 92, letterSpacing: interpolate(word, [0, 1], [30, 5]), color: "#fff", opacity: word, textShadow: "0 0 40px rgba(76,197,237,0.6)" }}>Nav Coaching</div>
      <div style={{ position: "absolute", top: 820, left: 40, right: 40, textAlign: "center" }}>
        <KWord text="تدريب مبني عليك" at={a + 80} size={104} weight={800} glow color={C.text} />
        <div>
          <KWord text="مو جدول جاهز" at={a + 100} size={64} weight={500} color={C.muted} from="up" />
        </div>
      </div>
      <div style={{ position: "absolute", top: 1160, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: ramp(f, [a + 160, a + 170]) }}>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 56, letterSpacing: 2, color: "#fff", direction: "ltr", minWidth: 640, textAlign: "center", padding: "18px 44px", borderRadius: 22, border: "2px solid rgba(76,197,237,0.5)", background: "rgba(4,10,20,0.7)" }}>
          <span style={{ color: C.cyan }}>{URL_TEXT.slice(0, Math.min(typed, 3))}</span>
          {URL_TEXT.slice(3, typed)}
          <span style={{ opacity: f % 30 < 15 ? 1 : 0, color: C.cyan }}>|</span>
        </div>
      </div>
      <div style={{ position: "absolute", top: 1330, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 20,
            padding: "30px 80px",
            borderRadius: 999,
            background: `linear-gradient(100deg, ${C.cyan}, #8ee3ff 50%, ${C.cyan})`,
            color: "#04121f",
            fontFamily: FONT,
            fontWeight: 700,
            fontSize: 62,
            opacity: Math.min(1, btn * 2),
            transform: `scale(${interpolate(btn, [0, 1], [0.4, 1]) * (1 - press * 0.07)})`,
            boxShadow: `0 0 ${50 + 110 * glow}px rgba(76,197,237,${0.6 + 0.4 * glow}), 0 20px 50px rgba(0,0,0,0.5)`,
          }}
        >
          اختر برنامجك <span style={{ transform: `translateX(${-12 * glow}px)` }}>←</span>
        </div>
      </div>
      <Cursor path={[[a + 300, 900, 1760], [click - 6, 640, 1420], [click + 40, 700, 1470]]} clicks={[click]} />
      {/* source credit — small, at the bottom (Mixkit Stock Video Free License) */}
      <div style={{ position: "absolute", bottom: 46, left: 40, right: 40, textAlign: "center", fontFamily: MONO, fontSize: 21, lineHeight: 1.5, letterSpacing: 0.5, color: "#b8c8d8", opacity: credit * 0.85, direction: "ltr" }}>
        {CREDIT.split(" · ").slice(0, 2).join(" · ")}
        <br />
        {CREDIT.split(" · ")[2]}
      </div>
      <AbsoluteFill style={{ background: "#000", opacity: end }} />
    </AbsoluteFill>
  );
};
