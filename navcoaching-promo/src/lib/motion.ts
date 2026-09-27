import { Easing, interpolate, spring } from "remotion";
import cues from "../cues.json";

export { cues };
export const FPS = cues.fps;

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Clamped interpolate with optional easing. */
export const ramp = (
  f: number,
  input: [number, number],
  output: [number, number] = [0, 1],
  easing: (t: number) => number = Easing.bezier(0.2, 0.7, 0.2, 1),
) => interpolate(f, input, output, { ...clamp, easing });

export const SPR = {
  slam: { damping: 13, stiffness: 210, mass: 0.9 },
  snappy: { damping: 18, stiffness: 240, mass: 0.7 },
  soft: { damping: 22, stiffness: 110, mass: 1 },
  bouncy: { damping: 9, stiffness: 160, mass: 0.8 },
  heavy: { damping: 15, stiffness: 120, mass: 1.6 },
};

export const sp = (f: number, at: number, config = SPR.snappy, durationInFrames?: number) =>
  f < at ? 0 : spring({ frame: f - at, fps: FPS, config, durationInFrames });

/** 1 at `at`, decaying to 0 over `len` frames. */
export const pulse = (f: number, at: number, len: number, power = 2) =>
  f < at || f > at + len ? 0 : Math.pow(1 - (f - at) / len, power);

/** Camera shake driven by cues.shakes. */
export const shake = (f: number) => {
  let x = 0;
  let y = 0;
  let r = 0;
  for (const [at, len] of cues.shakes) {
    const p = pulse(f, at, len, 2);
    if (p <= 0) continue;
    const amp = len * 1.1 * p;
    const t = f - at;
    x += Math.sin(t * 2.9 + at) * amp;
    y += Math.cos(t * 3.7 + at * 0.7) * amp * 0.8;
    r += Math.sin(t * 2.3 + at * 0.3) * p * 0.6;
  }
  return { x, y, r };
};

/** RGB-split text-shadow for impact frames. */
export const chroma = (d: number, extra = "") =>
  [
    d > 0.2 ? `${d}px 0 0 rgba(255,40,110,0.75)` : "",
    d > 0.2 ? `${-d}px 0 0 rgba(40,220,255,0.75)` : "",
    extra,
  ]
    .filter(Boolean)
    .join(", ") || "none";

export const inWindow = (f: number, from: number, to: number) => f >= from && f < to;
