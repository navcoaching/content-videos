import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT, glass, MONO } from "../theme";
import { Eyebrow, KWord } from "../components/Brand";
import { Cursor, Tag } from "../components/Ui";
import { clamp, cues, pulse, ramp, sp, SPR } from "../lib/motion";

const U = cues.ui;
const [S, E] = cues.scenes.training;

// Real sample day from the trainee file (navcoaching.com → "نظرة داخل برنامج المتدرب")
const ROWS = [
  { name: "Mid Leg Press", muscle: "الأمامية", en: "Quads", reps: "12" },
  { name: "Hip Thrusts", muscle: "المؤخرة", en: "Glutes", reps: "10" },
  { name: "DB RDL", muscle: "الخلفية", en: "Hamstrings", reps: "10" },
  { name: "Lying Leg Curl", muscle: "الخلفية", en: "Hamstrings", reps: "10" },
  { name: "Leg Extension", muscle: "الأمامية", en: "Quads", reps: "10" },
  { name: "Cable Twisted", muscle: "البطن والكور", en: "Core", reps: "10" },
];
const ALTS = ["Hip Thrusts", "Glute Bridge", "Cable Kickback"];
const CHIPS = ["الجولات", "التكرارات", "الوزن", "RIR"];

const CARD_X = 60;
const CARD_Y = 540;
const CARD_W = 960;
const HEAD_H = 104;
const COLS_H = 64;
const ROW_H = 116;
const rowY = (i: number) => HEAD_H + COLS_H + i * ROW_H;

// column geometry (RTL: # at right edge)
const COL = { idx: 90, name: 520, sets: 110, reps: 110, rir: 130 };

export const Training: React.FC = () => {
  const f = useCurrentFrame();

  const card = sp(f, U.cardIn, SPR.soft);
  const float = Math.sin((f - S) / 50) * 2.5;
  const exit = ramp(f, [E - 22, E], [0, 1], (t) => t * t);
  const rx = interpolate(card, [0, 1], [48, 6]) + float * 0.6 - exit * 20;
  const ry = interpolate(card, [0, 1], [-38, -4]) + float + exit * 30;
  const z = interpolate(card, [0, 1], [-900, 0]);

  const picked = f >= U.dropdownPick;
  const ddOpen = ramp(f, [U.dropdownOpen, U.dropdownOpen + 10]) * (1 - ramp(f, [U.dropdownPick + 4, U.dropdownPick + 14]));
  const hoverIdx = f < 612 ? 0 : 1;
  const hoverY = interpolate(f, [612, 624], [0, 1], clamp);
  const swap = pulse(f, U.muscleSwap, 30);

  const caption2 = ramp(f, [U.dropdownOpen - 8, U.dropdownOpen + 10]);

  // cursor keyframes in page coordinates
  const nameX = CARD_X + CARD_W - COL.idx - 170;
  const row1Y = CARD_Y + rowY(1) + 40;
  const cursorPath: [number, number, number][] = [
    [560, 820, 1760],
    [584, nameX, row1Y],
    [606, nameX, row1Y],
    [630, nameX - 20, row1Y + 76 + 80],
    [660, nameX - 40, row1Y + 76 + 80],
    [700, 980, 1800],
  ];

  return (
    <AbsoluteFill style={{ direction: "rtl" }}>
      {/* heading */}
      <div style={{ position: "absolute", top: 210, right: 90, left: 90, opacity: 1 - exit }}>
        <Eyebrow text="نظرة داخل برنامجك" at={S + 2} />
        <div style={{ marginTop: 18, display: "flex", gap: 22, flexWrap: "nowrap" }}>
          <KWord text="جدول" at={S + 6} size={86} from="up" />
          <KWord text="لكل" at={S + 12} size={86} from="up" />
          <KWord text="يوم" at={S + 18} size={86} from="up" />
          <KWord text="تدريبي" at={S + 24} size={86} from="up" color={C.cyan} glow />
        </div>
        <div style={{ marginTop: 26, display: "flex", gap: 16 }}>
          {CHIPS.map((c, i) => {
            const p = sp(f, U.chips[i], SPR.bouncy);
            return (
              <Tag
                key={c}
                style={{
                  fontSize: 32,
                  padding: "10px 26px",
                  opacity: Math.min(1, p * 2),
                  transform: `scale(${interpolate(p, [0, 1], [0.4, 1])})`,
                  color: C.text,
                  background: "rgba(76,197,237,0.16)",
                }}
              >
                {c}
              </Tag>
            );
          })}
        </div>
      </div>

      {/* 3D card */}
      <div style={{ position: "absolute", inset: 0, perspective: 1600 }}>
        <div
          style={{
            position: "absolute",
            left: CARD_X,
            top: CARD_Y,
            width: CARD_W,
            height: rowY(6) + 20,
            ...glass,
            transform: `translateZ(${z}px) rotateX(${rx}deg) rotateY(${ry}deg) scale(${1 + exit * 0.1})`,
            opacity: Math.min(1, card * 2) * (1 - exit),
            overflow: "visible",
            isolation: "isolate",
          }}
        >
          {/* header */}
          <div
            style={{
              height: HEAD_H,
              borderRadius: "36px 36px 0 0",
              background: `linear-gradient(90deg, ${C.navy}, ${C.cyanDeep})`,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0 40px",
              direction: "ltr",
            }}
          >
            <span style={{ fontFamily: MONO, fontWeight: 700, fontSize: 34, color: "#fff", letterSpacing: 2 }}>
              DAY 1 — LOWER BODY
            </span>
            <Tag style={{ color: "#fff", background: "rgba(255,255,255,0.14)", border: "1px solid rgba(255,255,255,0.4)", fontSize: 26 }}>
              WEEK 1
            </Tag>
          </div>
          {/* columns */}
          <div
            style={{
              height: COLS_H,
              display: "flex",
              alignItems: "center",
              fontFamily: FONT,
              fontSize: 26,
              color: C.muted,
              borderBottom: "1px solid rgba(76,197,237,0.2)",
            }}
          >
            <div style={{ width: COL.idx, textAlign: "center" }}>#</div>
            <div style={{ width: COL.name, paddingRight: 10 }}>التمرين والعضلة</div>
            <div style={{ width: COL.sets, textAlign: "center" }}>جولات</div>
            <div style={{ width: COL.reps, textAlign: "center" }}>تكرار</div>
            <div style={{ width: COL.rir, textAlign: "center" }}>RIR</div>
          </div>
          {ROWS.map((r, i) => {
            const p = sp(f, U.rows[i], SPR.snappy);
            const sweep = ramp(f, [U.rows[i], U.rows[i] + 18]);
            const isPick = i === 1;
            const name = isPick && picked ? "Glute Bridge" : r.name;
            const flash = isPick ? pulse(f, U.dropdownPick, 24) : 0;
            const active = isPick && f >= U.dropdownOpen - 4 && f < U.dropdownPick + 30;
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  top: rowY(i),
                  left: 0,
                  right: 0,
                  height: ROW_H,
                  display: "flex",
                  alignItems: "center",
                  borderBottom: i < 5 ? "1px solid rgba(76,197,237,0.12)" : undefined,
                  opacity: p > 0.62 ? undefined : p * 1.6,
                  transform: Math.abs(1 - p) < 0.002 ? undefined : `translateX(${(1 - p) * -120}px)`,
                  background: active
                    ? "linear-gradient(90deg, rgba(76,197,237,0.05), rgba(76,197,237,0.22))"
                    : `linear-gradient(270deg, rgba(76,197,237,${0.28 * (1 - sweep)}) ${sweep * 100}%, rgba(76,197,237,0) ${sweep * 100 + 10}%)`,
                  boxShadow: flash > 0 ? `inset 0 0 0 3px rgba(76,197,237,${flash})` : undefined,
                }}
              >
                <div style={{ width: COL.idx, textAlign: "center", fontFamily: MONO, fontSize: 30, color: C.muted }}>
                  {String(i + 1).padStart(2, "0")}
                </div>
                <div style={{ width: COL.name, paddingRight: 10 }}>
                  <div
                    style={{
                      fontFamily: FONT,
                      fontWeight: 600,
                      fontSize: 36,
                      color: C.text,
                      direction: "ltr",
                      textAlign: "right",
                    }}
                  >
                    {name}
                    {isPick && (
                      <span style={{ color: C.cyan, fontSize: 26, marginLeft: 12, opacity: f > 560 ? 1 : 0.5 }}>▾</span>
                    )}
                  </div>
                  <div style={{ marginTop: 6, display: "flex", gap: 10 }}>
                    <Tag
                      style={{
                        fontSize: 22,
                        padding: "3px 14px",
                        transform: isPick ? `scale(${1 + swap * 0.18})` : undefined,
                        boxShadow: isPick && swap > 0 ? `0 0 ${30 * swap}px ${C.cyan}` : undefined,
                      }}
                    >
                      {r.muscle} · {r.en}
                    </Tag>
                    {isPick && f >= U.muscleSwap && (
                      <Tag style={{ fontSize: 22, padding: "3px 14px", color: C.muted, opacity: ramp(f, [U.muscleSwap, U.muscleSwap + 8]) }}>
                        الخلفية · Hamstrings
                      </Tag>
                    )}
                  </div>
                </div>
                <Cell w={COL.sets} v="3" />
                <Cell w={COL.reps} v={r.reps} />
                <Cell w={COL.rir} v="3" accent />
              </div>
            );
          })}

          {/* exercise picker dropdown */}
          {ddOpen > 0.01 && (
            <div
              style={{
                position: "absolute",
                top: rowY(1) + ROW_H - 6,
                right: COL.idx - 10,
                width: 470,
                padding: 12,
                borderRadius: 24,
                background: "#0a1a34",
                border: `2px solid ${C.cyan}`,
                boxShadow: `0 30px 60px rgba(0,0,0,0.6), 0 0 40px rgba(76,197,237,0.35)`,
                transformOrigin: "top right",
                transform: `scaleY(${0.6 + 0.4 * ddOpen}) translateY(${(1 - ddOpen) * -10}px)`,
                opacity: ddOpen > 0.999 ? undefined : ddOpen,
                zIndex: 10,
              }}
            >
              <div style={{ position: "relative" }}>
                <div
                  style={{
                    position: "absolute",
                    left: 0,
                    right: 0,
                    top: (hoverIdx === 0 ? 0 : hoverY) * 78,
                    height: 72,
                    borderRadius: 16,
                    background: "linear-gradient(90deg, rgba(76,197,237,0.1), rgba(76,197,237,0.35))",
                  }}
                />
                {ALTS.map((a, k) => {
                  const ip = ramp(f, [U.dropdownItems[k], U.dropdownItems[k] + 8]);
                  return (
                    <div
                      key={a}
                      style={{
                        position: "relative",
                        height: 72,
                        marginBottom: 6,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "0 22px",
                        fontFamily: FONT,
                        fontSize: 32,
                        fontWeight: 500,
                        color: C.text,
                        direction: "ltr",
                        opacity: ip,
                        transform: `translateY(${(1 - ip) * -14}px)`,
                      }}
                    >
                      <span>{a}</span>
                      <span style={{ fontSize: 22, color: C.muted, fontFamily: MONO }}>{k === 0 ? "CURRENT" : "ALT"}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      <Cursor path={cursorPath} clicks={[U.dropdownOpen, U.dropdownPick]} hideAfter={690} />

      {/* caption */}
      <div
        style={{
          position: "absolute",
          top: 1490,
          left: 90,
          right: 90,
          fontFamily: FONT,
          fontSize: 46,
          fontWeight: 500,
          lineHeight: 1.45,
          color: C.text,
          opacity: caption2 * (1 - exit),
          transform: `translateY(${(1 - caption2) * 30}px)`,
        }}
      >
        اختر التمرين أو بديله…
        <br />
        <span style={{ color: C.cyan }}>والعضلات المستهدفة تتحدث مباشرة</span>
      </div>
    </AbsoluteFill>
  );
};

const Cell: React.FC<{ w: number; v: string; accent?: boolean }> = ({ w, v, accent }) => (
  <div
    style={{
      width: w,
      textAlign: "center",
      fontFamily: MONO,
      fontWeight: 700,
      fontSize: 38,
      color: accent ? C.cyan : C.text,
      textShadow: accent ? `0 0 16px rgba(76,197,237,0.7)` : undefined,
    }}
  >
    {v}
  </div>
);
