import React from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame } from "remotion";
import "./fonts";
import { Background } from "./components/Background";
import { Hud } from "./components/Hud";
import { Flash, SlashWipe } from "./components/Brand";
import { Intro } from "./scenes/Intro";
import { Kinetic } from "./scenes/Kinetic";
import { Training } from "./scenes/Training";
import { Progress } from "./scenes/Progress";
import { Features } from "./scenes/Features";
import { Cta } from "./scenes/Cta";
import { cues, inWindow, shake } from "./lib/motion";

const S = cues.scenes;

/** Scenes read the absolute frame so every animation keys off cues.json directly. */
const Win: React.FC<{ from: number; to: number; children: React.ReactNode }> = ({ from, to, children }) => {
  const f = useCurrentFrame();
  return inWindow(f, from, to) ? <>{children}</> : null;
};

export const Promo: React.FC = () => {
  const f = useCurrentFrame();
  const sh = shake(f);
  return (
    <AbsoluteFill style={{ background: "#02070f" }}>
      <Background />
      <AbsoluteFill style={{ transform: `translate(${sh.x}px, ${sh.y}px) rotate(${sh.r}deg)` }}>
        <Win from={S.intro[0]} to={S.intro[1]}>
          <Intro />
        </Win>
        <Win from={S.kinetic[0]} to={S.kinetic[1]}>
          <Kinetic />
        </Win>
        <Win from={S.training[0]} to={S.training[1]}>
          <Training />
        </Win>
        <Win from={S.progress[0]} to={S.progress[1]}>
          <Progress />
        </Win>
        <Win from={S.features[0]} to={S.features[1]}>
          <Features />
        </Win>
        <Win from={S.cta[0]} to={S.cta[1]}>
          <Cta />
        </Win>
      </AbsoluteFill>
      <SlashWipe cut={S.training[0]} len={30} />
      <SlashWipe cut={S.progress[0]} len={30} />
      <Flash />
      <Hud />
      <Audio src={staticFile("audio/soundtrack.wav")} />
    </AbsoluteFill>
  );
};
