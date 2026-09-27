// Brand tokens taken from navcoaching.com (src/app/globals.css) + logo colour.
export const C = {
  void: "#02070f",
  ink: "#07142a",
  ink2: "#0d1f3c",
  ink3: "#15294b",
  navy: "#284da0",
  cyan: "#4cc5ed",
  logo: "#1ebae9",
  cyanDeep: "#0a6a8f",
  text: "#eaf2fb",
  muted: "#a9bad0",
  ok: "#6fd39c",
};

export const FONT = `"Readex Pro", "IBM Plex Sans Arabic", Tahoma, sans-serif`;
export const MONO = `"JetBrains Mono", ui-monospace, monospace`;

export const W = 1080;
export const H = 1920;

export const glass = {
  background: "linear-gradient(160deg, rgba(40,77,160,0.30), rgba(7,20,42,0.72) 55%, rgba(7,20,42,0.86))",
  border: "1.5px solid rgba(76,197,237,0.35)",
  boxShadow:
    "0 0 0 1px rgba(76,197,237,0.08) inset, 0 30px 80px rgba(0,0,0,0.55), 0 0 60px rgba(76,197,237,0.18)",
  borderRadius: 36,
} as const;
