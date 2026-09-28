// Light theme tokens from navcoaching.com globals.css (:root, light mode)
export const L = {
  ink: "#07142a",
  navy: "#284da0",
  cyan: "#4cc5ed",
  cyanInk: "#0a6a8f",
  cyanSoft: "#e4f6fc",
  paper: "#f3f6fa",
  surface: "#ffffff",
  surface2: "#eaf0f6",
  line: "#d8e1ea",
  text: "#15233a",
  heading: "#0b1a33",
  muted: "#56667a",
  ok: "#157347",
  okBg: "#e2f4ea",
  warn: "#7a4e00",
  warnBg: "#fff3d4",
  err: "#b42318",
  errBg: "#fdecea",
  choiceBg: "#eef3ff",
  logo: "#1ebae9",
};

export const TINTS: Record<string, [string, string]> = {
  cyan: ["rgba(76,197,237,0.34)", "rgba(40,77,160,0.14)"],
  lavender: ["rgba(150,130,255,0.26)", "rgba(76,197,237,0.18)"],
  mint: ["rgba(90,210,160,0.28)", "rgba(76,197,237,0.16)"],
  neutral: ["rgba(76,197,237,0.20)", "rgba(40,77,160,0.10)"],
};

export const SHADOW_1 = "0 1px 2px rgba(7,20,42,0.06), 0 6px 18px rgba(7,20,42,0.06)";
export const SHADOW_2 = "0 2px 6px rgba(7,20,42,0.08), 0 18px 40px rgba(7,20,42,0.12)";
export const SHADOW_3 = "0 4px 10px rgba(7,20,42,0.10), 0 40px 90px rgba(7,20,42,0.22)";

// Browser window geometry (page coordinates)
export const WIN = { x: 40, y: 520, w: 1000, h: 900, bar: 56 };
export const CONTENT = { x: WIN.x, y: WIN.y + WIN.bar, w: WIN.w, h: WIN.h - WIN.bar };
