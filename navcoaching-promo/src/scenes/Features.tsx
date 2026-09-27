import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT, glass, MONO } from "../theme";
import { clamp, cues, ramp, sp, SPR } from "../lib/motion";

const HT = cues.hits;
const [, E] = cues.scenes.features;

const Icon: React.FC<{ kind: number }> = ({ kind }) => {
  const p = { fill: "none", stroke: C.cyan, strokeWidth: 3.2, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  return (
    <svg width={96} height={96} viewBox="0 0 48 48" style={{ filter: `drop-shadow(0 0 8px ${C.cyan})` }}>
      {kind === 0 && (
        <>
          <path {...p} d="M6 36 L18 24 L26 30 L42 12" />
          <path {...p} d="M32 12 H42 V22" />
        </>
      )}
      {kind === 1 && (
        <>
          <path {...p} d="M12 6 H28 L38 16 V42 H12 Z" />
          <path {...p} d="M28 6 V16 H38" />
          <path {...p} d="M18 26 H32 M18 33 H28" />
        </>
      )}
      {kind === 2 && (
        <>
          <path {...p} d="M24 5 L39 11 V23 C39 33 32 40 24 43 C16 40 9 33 9 23 V11 Z" />
          <path {...p} d="M17 24 L22 29 L31 19" />
        </>
      )}
      {kind === 3 && (
        <>
          <rect {...p} x="10" y="5" width="28" height="38" rx="4" />
          <path {...p} d="M16 12 H32 V18 H16 Z" />
          <path {...p} d="M17 26 H18 M24 26 H25 M31 26 H32 M17 33 H18 M24 33 H25 M31 33 H32" />
        </>
      )}
    </svg>
  );
};

// Platform features, wording from navcoaching.com
const FEATS = [
  { at: HT.feat1, t: "تتابع طلبك خطوة بخطوة", b: "حالة طلبك وتاريخ كل تحديث من حسابك" },
  { at: HT.feat2, t: "ملفاتك في مكان واحد", b: "تظهر بعد تأكيد الدفع ولا يفتحها غيرك" },
  { at: HT.feat3, t: "بياناتك خاصة", b: "إجاباتك الصحية لا يطّلع عليها إلا المدربة" },
  { at: HT.feat4, t: "حاسبة سعرات مجانية", b: "احسب سعراتك اليومية لهدفك" },
];

export const Features: React.FC = () => {
  const f = useCurrentFrame();
  const active = FEATS.reduce((acc, ft, i) => (f >= ft.at ? i : acc), 0);
  const exit = ramp(f, [E - 16, E], [0, 1], (t) => t * t);

  return (
    <AbsoluteFill style={{ direction: "rtl", perspective: 1400 }}>
      {/* counter */}
      <div
        style={{
          position: "absolute",
          top: 250,
          width: "100%",
          textAlign: "center",
          fontFamily: MONO,
          fontWeight: 700,
          fontSize: 44,
          letterSpacing: 8,
          color: C.cyan,
          direction: "ltr",
          opacity: 1 - exit,
        }}
      >
        <span style={{ fontSize: 120, color: C.text, textShadow: `0 0 30px ${C.cyan}` }}>
          {String(active + 1).padStart(2, "0")}
        </span>
        <span style={{ opacity: 0.7 }}> / 04</span>
      </div>
      <div
        style={{
          position: "absolute",
          top: 460,
          width: "100%",
          textAlign: "center",
          fontFamily: FONT,
          fontSize: 50,
          fontWeight: 500,
          color: C.muted,
          opacity: ramp(f, [HT.feat1, HT.feat1 + 12]) * (1 - exit),
        }}
      >
        كل شيء في حسابك
      </div>

      {FEATS.map((ft, i) => {
        const inP = sp(f, ft.at, { damping: 19, stiffness: 420, mass: 0.7 });
        const depth = Math.max(0, active - i); // how many cards have landed on top
        const back = FEATS.slice(i + 1).reduce((acc, nx) => acc + sp(f, nx.at, { damping: 20, stiffness: 300, mass: 0.7 }), 0);
        if (f < ft.at) return null;
        const z = interpolate(inP, [0, 1], [420, 0]) - back * 380;
        const y = -back * 150;
        const op = Math.min(1, inP * 3) * interpolate(back, [0, 1, 1.5], [1, 0.12, 0], clamp) * (1 - exit);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: 90,
              right: 90,
              top: 850,
              height: 520,
              ...glass,
              padding: "56px 60px",
              transform: `translateY(${y}px) translateZ(${z}px) rotateX(${back * 8}deg)`,
              opacity: op,
              filter: back > 0.1 ? `blur(${Math.min(8, back * 5)}px) brightness(${1 - Math.min(0.5, back * 0.3)})` : undefined,
              zIndex: 10 + i,
              boxShadow: depth === 0 ? `${glass.boxShadow}, 0 0 90px rgba(76,197,237,0.35)` : glass.boxShadow,
            }}
          >
            <div
              style={{
                width: 150,
                height: 150,
                borderRadius: 40,
                display: "grid",
                placeItems: "center",
                background: "radial-gradient(circle, rgba(76,197,237,0.28), rgba(40,77,160,0.2))",
                border: `2px solid rgba(76,197,237,0.5)`,
              }}
            >
              <Icon kind={i} />
            </div>
            <div style={{ marginTop: 40, fontFamily: FONT, fontWeight: 700, fontSize: 64, color: C.text, lineHeight: 1.2, whiteSpace: "nowrap" }}>
              {ft.t}
            </div>
            <div style={{ marginTop: 18, fontFamily: FONT, fontWeight: 400, fontSize: 40, color: C.muted, lineHeight: 1.4 }}>
              {ft.b}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
