import React from "react";
import { Composition } from "remotion";
import { Promo } from "./Promo";
import cues from "./cues.json";
import { Journey } from "./journey/Journey";
import J from "./journey/journey.json";
import { Tutorial, TUTORIAL_DURATION } from "./tutorial/Tutorial";

export const RemotionRoot: React.FC = () => (
  <>
  <Composition
    id="NavPromo"
    component={Promo}
    durationInFrames={cues.durationInFrames}
    fps={cues.fps}
    width={1080}
    height={1920}
  />
  <Composition
    id="NavJourney"
    component={Journey}
    durationInFrames={J.durationInFrames}
    fps={J.fps}
    width={1080}
    height={1920}
    defaultProps={{ withAudio: false }}
  />
  <Composition
    id="NavTutorial"
    component={Tutorial}
    durationInFrames={TUTORIAL_DURATION}
    fps={60}
    width={1080}
    height={1920}
    defaultProps={{ withAudio: false }}
  />
  </>
);
