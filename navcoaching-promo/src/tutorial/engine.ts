import T from "./tutorial.json";
import M from "../../public/tut/manifest.json";

export type Rect = { x: number; y: number; w: number; h: number };
type View = { page?: string; state?: string; scroll?: number };
type Beat = { t: number; view?: View; scroll?: number; dur?: number; tap?: string; ring?: string };
type Chapter = { key: string; title: string; sub: string; dur: number; beats: Beat[]; captions: [number, string][] };

export const MAN = M as unknown as {
  device: { w: number; h: number; dpr: number };
  pages: Record<string, { tiles: { src: string; y: number; h: number }[]; height: number; header: string; rects: Record<string, Rect | null> }>;
  states: Record<string, { src: string; scroll: number; page: string; rects: Record<string, Rect | null> }>;
  overlays: Record<string, { src: string; x: number; y: number; w: number; h: number }>;
};

export const CHAPTERS = (T.chapters as unknown as Chapter[]).map((c, i, all) => {
  const start = all.slice(0, i).reduce((a, b) => a + b.dur, 0);
  return { ...c, start, end: start + c.dur };
});
export const DURATION = CHAPTERS[CHAPTERS.length - 1].end;
export const FPS = T.fps;

type AbsView = View & { at: number; page: string };
type AbsScroll = { at: number; to: number; dur: number };

const VIEWS: AbsView[] = [];
const SCROLLS: AbsScroll[] = [];
export const TAPS: { at: number; ref: string }[] = [];
export const RINGS: { at: number; ref: string; dur: number }[] = [];
export const CAPTIONS: { at: number; text: string; end: number }[] = [];

for (const c of CHAPTERS) {
  for (const b of c.beats) {
    const at = c.start + b.t;
    if (b.view) {
      const page = b.view.page ?? MAN.states[b.view.state!].page;
      VIEWS.push({ ...b.view, at, page });
    }
    if (b.scroll != null && !b.view) SCROLLS.push({ at, to: b.scroll, dur: b.dur ?? 60 });
    if (b.tap) TAPS.push({ at, ref: b.tap });
    if (b.ring) RINGS.push({ at, ref: b.ring, dur: b.dur ?? 80 });
  }
  for (const [t, text] of c.captions) CAPTIONS.push({ at: c.start + t, text, end: c.end });
}
VIEWS.sort((a, b) => a.at - b.at);

const ease = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

export const viewIndexAt = (f: number) => {
  let i = 0;
  for (let k = 0; k < VIEWS.length; k++) if (VIEWS[k].at <= f) i = k;
  return i;
};
export const viewAt = (i: number) => VIEWS[i];

/** Scroll (CSS px) of view i at frame f. States are fixed; pages follow scroll beats. */
export const scrollOf = (i: number, f: number) => {
  const v = VIEWS[i];
  if (v.state) return MAN.states[v.state].scroll;
  const until = VIEWS[i + 1]?.at ?? Infinity;
  let s = v.scroll ?? 0;
  for (const sc of SCROLLS) {
    if (sc.at < v.at || sc.at >= until || f < sc.at) continue;
    const p = ease(Math.min(1, (f - sc.at) / sc.dur));
    s = s + (sc.to - s) * p;
  }
  const maxS = MAN.pages[v.page].height - MAN.device.h;
  return Math.max(0, Math.min(maxS, s));
};

/** "page.rect" (page rects) or "@state.rect" (rects measured in a state). */
export const resolveRect = (ref: string): Rect | null => {
  const st = ref.startsWith("@");
  const [id, name] = ref.replace("@", "").split(".");
  const r = st ? MAN.states[id]?.rects[name] : MAN.pages[id]?.rects[name];
  return r ?? null;
};

export const chapterAt = (f: number) => CHAPTERS.findIndex((c) => f >= c.start && f < c.end);
export const captionAt = (f: number) => {
  let cur: (typeof CAPTIONS)[number] | null = null;
  for (const c of CAPTIONS) if (f >= c.at && f < c.end) cur = c;
  return cur;
};
