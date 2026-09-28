import React from "react";
import { useCurrentFrame } from "remotion";
import { FONT } from "../../theme";
import { L } from "../theme";
import { J, keyed } from "../tl";
import { BrowserWindow, Rect, Spotlight } from "../parts/Chrome";
import { Card, H, IconFile, P, SiteHeader, Status, Timeline } from "../parts/Site";
import { pulse, ramp, sp, SPR } from "../../lib/motion";
import { useWindowIn } from "./common";

const C = J.ch4;
const [S0, S1] = J.segments.ch4 as [number, number];

// timelineSteps("follow", false) from src/lib/status.ts
const STEPS = ["تم الاستلام", "بانتظار الدفع", "التحقق من الدفع", "قيد الإعداد", "البرنامج نشط", "مكتمل"];
const WHEN = ["الأحد 9:12 م", "الأحد 9:40 م", "الإثنين 10:05 ص", "الإثنين 1:30 م", "الإثنين 6:00 م"];
const STATUS = [
  { tone: "wait", label: "جارٍ التحقق من الدفع" },
  { tone: "wait", label: "جارٍ التحقق من الدفع" },
  { tone: "wait", label: "قيد الإعداد" },
  { tone: "wait", label: "قيد الإعداد" },
  { tone: "ok", label: "البرنامج نشط" },
] as const;

const FILES_Y = 900;
const SCROLL = 420;

export const Ch4Track: React.FC = () => {
  const f = useCurrentFrame();
  const win = useWindowIn(S0, S1);
  const done = C.steps.filter((t) => f >= t).length; // 0..5
  const scroll = keyed(f, [[0, 0], [C.files - 24, SCROLL]], 26);
  const st = STATUS[Math.max(0, done - 1)];

  // each cue completes the next step; the step after the last completed one is "now"
  const k = Math.min(done, 4);
  const steps = STEPS.map((label, i) => {
    const state: "done" | "now" | "todo" = i < k ? "done" : i === k && done > 0 ? "now" : "todo";
    return { label, state, when: i < k ? WHEN[i] : undefined, pop: i === k ? pulse(f, C.steps[Math.max(0, done - 1)], 20) : 0 };
  });

  const spots: [number, Rect | null][] = [
    [S0, null],
    [C.steps[4] - 4, [40, 200 + 26 + 58 + 4 * 84 - 8, 920, 80]],
    [C.files - 24, null],
    [C.files + 20, [40, FILES_Y - SCROLL, 920, 330]],
    [S1 - 10, null],
  ];
  const filesP = sp(f, C.files - 10, SPR.soft);

  return (
    <BrowserWindow style={win.style}>
      <div style={{ position: "absolute", left: 0, right: 0, top: -scroll }}>
        <H size={44} style={{ position: "absolute", top: 112, right: 40 }}>الباقة المكثفة</H>
        <div style={{ position: "absolute", top: 118, left: 40, transform: `scale(${1 + 0.1 * pulse(f, C.steps[Math.max(0, done - 1)], 16)})` }}>
          <Status tone={st.tone}>{st.label}</Status>
        </div>
        <Card style={{ position: "absolute", top: 200, left: 40, width: 920, boxSizing: "border-box", padding: "26px 34px" }}>
          <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 30, color: L.heading, marginBottom: 18 }}>حالة الطلب</div>
          <Timeline steps={steps} />
        </Card>
        <Card
          style={{
            position: "absolute",
            top: FILES_Y,
            left: 40,
            width: 920,
            height: 330,
            boxSizing: "border-box",
            opacity: filesP,
            transform: `translateY(${(1 - filesP) * 60}px)`,
          }}
        >
          <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 32, color: L.heading }}>ملفاتي</div>
          {["جدول التمرين", "خطة التغذية"].map((t, i) => {
            const p = sp(f, C.fileItems[i], SPR.bouncy);
            return (
              <div
                key={t}
                style={{
                  marginTop: 16,
                  height: 76,
                  borderRadius: 999,
                  border: `2px solid ${L.line}`,
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  padding: "0 28px",
                  fontFamily: FONT,
                  fontWeight: 600,
                  fontSize: 27,
                  color: L.navy,
                  opacity: Math.min(1, p * 2),
                  transform: `translateX(${(1 - p) * -60}px)`,
                }}
              >
                <IconFile /> {t}
              </div>
            );
          })}
          <P size={21} style={{ marginTop: 12, opacity: ramp(f, [C.fileItems[1] + 10, C.fileItems[1] + 24]) }}>🔒 تظهر بعد تأكيد الدفع، ولا يفتحها غيرك.</P>
        </Card>
      </div>
      <SiteHeader account />
      <Spotlight keys={spots} />
    </BrowserWindow>
  );
};
