import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame } from "remotion";
import "../fonts";
import { SlashWipe } from "../components/Brand";
import { pulse } from "../lib/motion";
import { DAYS, SEC, SHOTS } from "./data";
import { AddOnsScene, CtaScene, RestScene, TitleScene } from "./scenes";
import { Backdrop, Corners, DayChip, DayTitle, ExerciseList, Flash, Grain, LightLeaks, ShotView, TopBar, Vignette, Words } from "./parts";

const SHAKES: [number, number][] = [[240, 14], [360, 16], [1080, 16], [1800, 16], [2400, 10], [2670, 20]];
const shake = (f: number) => {
  let x = 0, y = 0, r = 0;
  for (const [at, len] of SHAKES) {
    const p = pulse(f, at, len, 2);
    if (p <= 0) continue;
    const t = f - at;
    x += Math.sin(t * 2.9 + at) * len * 1.0 * p;
    y += Math.cos(t * 3.7 + at * 0.7) * len * 0.8 * p;
    r += Math.sin(t * 2.3 + at * 0.3) * p * 0.5;
  }
  return { x, y, r };
};

export const Split: React.FC<{ withAudio?: boolean }> = ({ withAudio = true }) => {
  const f = useCurrentFrame();
  const sh = shake(f);
  const cuts = [360, 1080, 1800];
  return (
    <AbsoluteFill style={{ background: "#03060b" }}>
      <Backdrop />
      <AbsoluteFill style={{ transform: `translate(${sh.x}px, ${sh.y}px) rotate(${sh.r}deg) scale(1.02)` }}>
        {SHOTS.map((s) => (
          <Sequence key={s.id} from={s.from} durationInFrames={s.dur}>
            <ShotView shot={s} />
          </Sequence>
        ))}
        <Vignette strength={0.5} />
        <TitleScene />
        <RestScene from={SEC.rest1[0]} to={SEC.rest1[1]} />
        <RestScene from={SEC.rest2[0]} to={SEC.rest2[1]} />
        <AddOnsScene />
        {DAYS.map((d) => (
          <DayTitle key={d.key} day={d} />
        ))}
        <DayChip />
        <ExerciseList />
        <Words />
        <CtaScene />
      </AbsoluteFill>
      <Corners from={8} to={236} />
      <TopBar />
      <LightLeaks at={[240, 360, 1080, 1800, 2400, 2670]} />
      <Grain opacity={0.17} />
      {cuts.map((c) => (
        <SlashWipe key={c} cut={c} len={26} />
      ))}
      <Flash at={[240, 960, 1680, 2400]} strong={[360, 1080, 1800, 2670]} />
      {withAudio && <Audio src={staticFile("audio/split.wav")} />}
    </AbsoluteFill>
  );
};
