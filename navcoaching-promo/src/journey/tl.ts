import J from "./journey.json";

export { J };
export const SEG = J.segments as unknown as Record<string, [number, number]>;
export const CHAPTERS = J.chapters;

export const chapterIndexAt = (f: number) => CHAPTERS.findIndex((c) => f >= SEG[c.key][0] && f < SEG[c.key][1]);

export const captionAt = (f: number): { text: string; at: number } | null => {
  let cur: { text: string; at: number } | null = null;
  for (const [at, text] of J.captions as [number, string][]) if (f >= at) cur = { text, at };
  // captions only live inside chapter segments
  const i = chapterIndexAt(f);
  if (i < 0 || !cur) return null;
  const [s] = SEG[CHAPTERS[i].key];
  return cur.at >= s ? cur : null;
};

/** Piecewise value from keyframes [[frame, value], ...] with easing between them. */
export const keyed = (f: number, keys: [number, number][], dur = 14) => {
  let v = keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    const [at, to] = keys[i];
    if (f <= at) break;
    const t = Math.min(1, (f - at) / dur);
    const e = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    v = v + (to - v) * e;
  }
  return v;
};
