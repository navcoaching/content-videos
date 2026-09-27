import React from "react";
import { Composition } from "remotion";
import { Promo } from "./Promo";
import cues from "./cues.json";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="NavPromo"
    component={Promo}
    durationInFrames={cues.durationInFrames}
    fps={cues.fps}
    width={1080}
    height={1920}
  />
);
