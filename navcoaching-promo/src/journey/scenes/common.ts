import type React from "react";
import { useCurrentFrame } from "remotion";
import { CONTENT } from "../theme";
import { ramp, sp, SPR } from "../../lib/motion";

/** Content coords -> page coords. */
export const pg = (x: number, y: number): [number, number] => [x + CONTENT.x, y + CONTENT.y];

/** Window entrance/exit shared by chapters: rises in with depth, zooms slightly out on exit. */
export const useWindowIn = (start: number, end: number) => {
  const f = useCurrentFrame();
  const p = sp(f, start, SPR.soft);
  const out = ramp(f, [end - 16, end], [0, 1], (t) => t * t);
  return {
    p,
    style: {
      opacity: Math.min(1, p * 1.6) * (1 - out),
      transform: `perspective(2000px) translateY(${(1 - p) * 120 - out * 40}px) rotateX(${(1 - p) * 10}deg) scale(${0.94 + 0.06 * p - out * 0.04})`,
    } as React.CSSProperties,
  };
};
