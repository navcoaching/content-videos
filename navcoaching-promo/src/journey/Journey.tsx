import React from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame } from "remotion";
import "../fonts";
import { ChapterHeader, Caption, LightBg } from "./parts/Chrome";
import { CHAPTERS, J, SEG, chapterIndexAt } from "./tl";
import { inWindow } from "../lib/motion";
import { Ch1Programs } from "./scenes/Ch1Programs";
import { Ch2Checkout } from "./scenes/Ch2Checkout";
import { Ch3Pay } from "./scenes/Ch3Pay";
import { Ch4Track } from "./scenes/Ch4Track";
import { Ch5Program } from "./scenes/Ch5Program";
import { Ch6Tools } from "./scenes/Ch6Tools";
import { Hook, LogoScene, Pivot } from "./scenes/Intro";
import { Outro } from "./scenes/Outro";

const Win: React.FC<{ from: number; to: number; children: React.ReactNode }> = ({ from, to, children }) => {
  const f = useCurrentFrame();
  return inWindow(f, from, to) ? <>{children}</> : null;
};

const tintAt = (f: number) => {
  const i = chapterIndexAt(f);
  return i >= 0 ? CHAPTERS[i].tint : "neutral";
};

export const Journey: React.FC<{ withAudio?: boolean }> = ({ withAudio = true }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#f3f6fa" }}>
      <LightBg tint={tintAt(f)} />
      <ChapterHeader />
      <Win from={SEG.hook[0]} to={SEG.hook[1]}>
        <Hook />
      </Win>
      <Win from={SEG.pivot[0]} to={SEG.pivot[1]}>
        <Pivot />
      </Win>
      <Win from={SEG.logo[0]} to={SEG.logo[1]}>
        <LogoScene />
      </Win>
      <Win from={SEG.ch1[0]} to={SEG.ch1[1]}>
        <Ch1Programs />
      </Win>
      <Win from={SEG.ch2[0]} to={SEG.ch2[1]}>
        <Ch2Checkout />
      </Win>
      <Win from={SEG.ch3[0]} to={SEG.ch3[1]}>
        <Ch3Pay />
      </Win>
      <Win from={SEG.ch4[0]} to={SEG.ch4[1]}>
        <Ch4Track />
      </Win>
      <Win from={SEG.ch5[0]} to={SEG.ch5[1]}>
        <Ch5Program />
      </Win>
      <Win from={SEG.ch6[0]} to={SEG.ch6[1]}>
        <Ch6Tools />
      </Win>
      <Win from={SEG.outro[0]} to={SEG.outro[1]}>
        <Outro />
      </Win>
      <Caption />
      {withAudio && J && <Audio src={staticFile("audio/journey.wav")} />}
    </AbsoluteFill>
  );
};
