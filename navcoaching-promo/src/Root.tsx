import React from "react";
import { Composition } from "remotion";
import { Promo } from "./Promo";
import cues from "./cues.json";
import { Journey } from "./journey/Journey";
import J from "./journey/journey.json";
import { Tutorial, TUTORIAL_DURATION } from "./tutorial/Tutorial";
import { Split } from "./split/Split";
import { DURATION as SPLIT_DURATION } from "./split/data";
import { Intro, INTRO_DURATION, INTRO_FPS } from "./intro/Intro";

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
  <Composition
    id="NavSplit"
    component={Split}
    durationInFrames={SPLIT_DURATION}
    fps={60}
    width={1080}
    height={1920}
    defaultProps={{ withAudio: false }}
  />
  <Composition
    id="NavIntro"
    component={Intro}
    durationInFrames={INTRO_DURATION}
    fps={INTRO_FPS}
    width={1080}
    height={1920}
    defaultProps={{ withAudio: false }}
  />
  </>
);
