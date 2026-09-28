// Recreations of navcoaching.com UI primitives (from src/app/globals.css), scaled for a 1000px viewport.
import React from "react";
import { Img, staticFile } from "remotion";
import { FONT, MONO } from "../../theme";
import { L, SHADOW_1 } from "../theme";

export const HEADER_H = 88;

export const SiteHeader: React.FC<{ account?: boolean }> = ({ account }) => (
  <div
    style={{
      position: "absolute",
      top: 0,
      left: 0,
      right: 0,
      height: HEADER_H,
      background: "rgba(255,255,255,0.94)",
      borderBottom: `1px solid ${L.line}`,
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 36px",
      zIndex: 20,
      direction: "rtl",
    }}
  >
    <Img src={staticFile("brand/logo-color.webp")} style={{ height: 50 }} />
    <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
      <span style={{ fontFamily: FONT, fontWeight: 600, fontSize: 24, color: L.navy, padding: "10px 22px", borderRadius: 999, border: `1.5px solid ${L.line}` }}>
        {account ? "حسابي" : "دخول"}
      </span>
      <span style={{ display: "grid", gap: 6 }}>
        {[0, 1, 2].map((i) => (
          <span key={i} style={{ width: 30, height: 3.5, borderRadius: 2, background: L.heading, display: "block" }} />
        ))}
      </span>
    </div>
  </div>
);

export const Eyebrow: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 12, fontFamily: FONT, fontWeight: 600, fontSize: 24, color: L.cyanInk, ...style }}>
    <span style={{ width: 30, height: 12, background: `linear-gradient(90deg, ${L.cyan}, ${L.navy})`, transform: "skewX(-28deg)" }} />
    {children}
  </div>
);

export const H: React.FC<{ size?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ size = 50, children, style }) => (
  <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: size, color: L.heading, lineHeight: 1.25, ...style }}>{children}</div>
);

export const P: React.FC<{ size?: number; children: React.ReactNode; style?: React.CSSProperties; muted?: boolean }> = ({
  size = 26,
  children,
  style,
  muted = true,
}) => (
  <div style={{ fontFamily: FONT, fontWeight: 400, fontSize: size, color: muted ? L.muted : L.text, lineHeight: 1.55, ...style }}>{children}</div>
);

export const Btn: React.FC<{
  children: React.ReactNode;
  kind?: "navy" | "cyan" | "ghost";
  style?: React.CSSProperties;
  press?: number;
}> = ({ children, kind = "navy", style, press = 0 }) => {
  const bg = kind === "navy" ? L.navy : kind === "cyan" ? L.cyan : "transparent";
  const fg = kind === "navy" ? "#fff" : kind === "cyan" ? L.ink : L.navy;
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 12,
        height: 72,
        padding: "0 34px",
        borderRadius: 999,
        background: bg,
        color: fg,
        border: `2px solid ${kind === "ghost" ? L.line : "transparent"}`,
        fontFamily: FONT,
        fontWeight: 600,
        fontSize: 27,
        whiteSpace: "nowrap",
        transform: `scale(${1 - press * 0.05})`,
        boxShadow: kind === "ghost" ? undefined : `0 10px 24px rgba(40,77,160,${0.22 + press * 0.2})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties; dark?: boolean }> = ({ children, style, dark }) => (
  <div
    style={{
      background: dark ? L.ink : L.surface,
      color: dark ? "#eaf2fb" : L.text,
      border: `1px solid ${dark ? L.ink : L.line}`,
      borderRadius: 26,
      padding: 30,
      boxShadow: SHADOW_1,
      ...style,
    }}
  >
    {children}
  </div>
);

export const Choice: React.FC<{ label: string; on?: number; style?: React.CSSProperties }> = ({ label, on = 0, style }) => (
  <div
    style={{
      height: 64,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "0 16px",
      borderRadius: 16,
      border: `2px solid ${on > 0.5 ? L.navy : L.line}`,
      background: on > 0.5 ? L.choiceBg : L.surface,
      color: on > 0.5 ? L.navy : L.text,
      fontFamily: FONT,
      fontWeight: on > 0.5 ? 600 : 400,
      fontSize: 24,
      whiteSpace: "nowrap",
      transform: `scale(${1 + 0.06 * Math.sin(Math.min(1, on) * Math.PI)})`,
      boxShadow: on > 0.5 ? "0 0 0 4px rgba(40,77,160,0.10)" : undefined,
      ...style,
    }}
  >
    {label}
  </div>
);

const TONES = {
  action: [L.warnBg, L.warn],
  wait: [L.cyanSoft, L.cyanInk],
  ok: [L.okBg, L.ok],
  muted: [L.surface2, L.muted],
} as const;

export const Status: React.FC<{ tone: keyof typeof TONES; children: React.ReactNode; style?: React.CSSProperties }> = ({ tone, children, style }) => (
  <span
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      padding: "10px 20px",
      borderRadius: 999,
      background: TONES[tone][0],
      color: TONES[tone][1],
      fontFamily: FONT,
      fontWeight: 600,
      fontSize: 24,
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    <span style={{ width: 12, height: 12, borderRadius: "50%", background: TONES[tone][1] }} />
    {children}
  </span>
);

export const Alert: React.FC<{ tone: "ok" | "info" | "warn"; children: React.ReactNode; style?: React.CSSProperties }> = ({ tone, children, style }) => {
  const [bg, fg] = tone === "ok" ? [L.okBg, L.ok] : tone === "info" ? [L.cyanSoft, L.cyanInk] : [L.warnBg, L.warn];
  return (
    <div style={{ background: bg, color: fg, borderRadius: 18, padding: "20px 24px", fontFamily: FONT, fontSize: 25, lineHeight: 1.55, ...style }}>
      {children}
    </div>
  );
};

export const Field: React.FC<{ label: string; value?: string; placeholder?: string; caret?: boolean; style?: React.CSSProperties; ltr?: boolean }> = ({
  label,
  value,
  placeholder,
  caret,
  style,
  ltr,
}) => (
  <div style={{ display: "grid", gap: 10, ...style }}>
    <div style={{ fontFamily: FONT, fontWeight: 600, fontSize: 24, color: L.heading }}>
      {label} <span style={{ color: L.err }}>*</span>
    </div>
    <div
      style={{
        height: 66,
        borderRadius: 14,
        border: `2px solid ${caret ? L.navy : L.line}`,
        background: L.surface,
        display: "flex",
        alignItems: "center",
        padding: "0 20px",
        fontFamily: ltr ? MONO : FONT,
        fontSize: 26,
        color: value ? L.text : "#9aa8b8",
        direction: ltr ? "ltr" : "rtl",
        boxShadow: caret ? "0 0 0 4px rgba(76,197,237,0.25)" : undefined,
      }}
    >
      {value || placeholder}
      {caret && <span style={{ width: 2.5, height: 32, background: L.navy, marginInline: 3 }} />}
    </div>
  </div>
);

export const Check: React.FC<{ on: boolean; children: React.ReactNode; style?: React.CSSProperties }> = ({ on, children, style }) => (
  <div style={{ display: "flex", gap: 16, alignItems: "flex-start", fontFamily: FONT, fontSize: 24, color: L.text, lineHeight: 1.5, ...style }}>
    <span
      style={{
        flex: "none",
        width: 34,
        height: 34,
        borderRadius: 9,
        border: `2px solid ${on ? L.navy : L.line}`,
        background: on ? L.navy : "#fff",
        color: "#fff",
        display: "grid",
        placeItems: "center",
        fontSize: 22,
        marginTop: 2,
      }}
    >
      {on ? "✓" : ""}
    </span>
    <span>{children}</span>
  </div>
);

export const Steps5: React.FC<{ step: number }> = ({ step }) => (
  <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10 }}>
    {[1, 2, 3, 4, 5].map((i) => {
      const fill = Math.max(0, Math.min(1, step - i + 1));
      return (
        <span key={i} style={{ height: 10, borderRadius: 99, background: L.line, overflow: "hidden" }}>
          <span style={{ display: "block", height: "100%", width: `${fill * 100}%`, background: L.navy, borderRadius: 99 }} />
        </span>
      );
    })}
  </div>
);

export const Timeline: React.FC<{ steps: { label: string; when?: string; state: "done" | "now" | "todo"; pop?: number }[] }> = ({ steps }) => (
  <div style={{ display: "grid" }}>
    {steps.map((s, i) => (
      <div key={s.label} style={{ position: "relative", paddingRight: 56, height: 84, boxSizing: "border-box" }}>
        {i < steps.length - 1 && (
          <span style={{ position: "absolute", right: 16, top: 34, bottom: -4, width: 3, background: s.state === "done" ? L.navy : L.line }} />
        )}
        <span
          style={{
            position: "absolute",
            right: 4,
            top: 6,
            width: 28,
            height: 28,
            borderRadius: "50%",
            border: `3px solid ${s.state === "done" ? L.navy : s.state === "now" ? L.cyan : L.line}`,
            background: s.state === "done" ? L.navy : s.state === "now" ? L.cyan : "#fff",
            boxShadow: s.state === "now" ? `0 0 0 ${7 + 6 * (s.pop ?? 0)}px rgba(76,197,237,0.28)` : undefined,
            transform: `scale(${1 + 0.35 * (s.pop ?? 0)})`,
            color: "#fff",
            display: "grid",
            placeItems: "center",
            fontSize: 16,
          }}
        >
          {s.state === "done" ? "✓" : ""}
        </span>
        <div style={{ fontFamily: FONT, fontSize: 28, fontWeight: s.state === "now" ? 700 : 500, color: s.state === "todo" ? L.muted : L.heading }}>{s.label}</div>
        {s.when && <div style={{ fontFamily: FONT, fontSize: 21, color: L.muted }}>{s.when}</div>}
      </div>
    ))}
  </div>
);

export const IconFile: React.FC<{ size?: number; color?: string }> = ({ size = 30, color = L.navy }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
    <path d="M14 3v5h5M9 13h6M9 17h4" />
  </svg>
);
