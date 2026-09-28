import React from "react";
import { useCurrentFrame } from "remotion";
import { FONT, MONO } from "../../theme";
import { L } from "../theme";
import { J } from "../tl";
import { BrowserWindow, MacCursor, Rect, Spotlight } from "../parts/Chrome";
import { Alert, Btn, Card, H, P, SiteHeader, Status } from "../parts/Site";
import { ramp, sp, SPR } from "../../lib/motion";
import { pg, useWindowIn } from "./common";
import { pressAt } from "./Ch1Programs";

const C = J.ch3;
const [S0, S1] = J.segments.ch3 as [number, number];
export const ORDER_NO = "NC-1042"; // demo order number

const ALERT: Rect = [40, 150, 920, 110];
const BANK: Rect = [70, 474, 860, 164];
const COPY: Rect = [70, 648, 240, 54];
const DROP: Rect = [70, 716, 860, 96];
const PILL: Rect = [40, 290, 330, 58];

export const Ch3Pay: React.FC = () => {
  const f = useCurrentFrame();
  const win = useWindowIn(S0, S1);
  const created = sp(f, C.created, SPR.bouncy);
  const reviewed = f >= C.review;
  const uploaded = f >= C.fileIn;
  const copied = f >= C.copy && f < C.copy + 60;
  const revA = ramp(f, [C.review, C.review + 14]);

  const spots: [number, Rect | null][] = [
    [S0, null],
    [C.created + 6, ALERT],
    [C.bankSpot, [BANK[0], BANK[1], BANK[2], COPY[1] + COPY[3] - BANK[1]]],
    [C.upload - 24, DROP],
    [C.review + 4, PILL],
    [S1 - 10, null],
  ];
  const ctr = (r: Rect) => pg(r[0] + r[2] / 2, r[1] + r[3] / 2);
  const cursor: [number, number, number][] = [
    [C.bankSpot, 980, 1560],
    [C.copy - 8, ...ctr(COPY)],
    [C.upload - 8, ...ctr(DROP)],
    [C.review - 10, ...pg(480, 820)],
    [S1, ...pg(480, 820)],
  ];

  return (
    <>
      <BrowserWindow style={win.style}>
        <P size={22} style={{ position: "absolute", top: 108, right: 40 }}>
          طلباتي / <span style={{ fontFamily: MONO }}>{ORDER_NO}</span>
        </P>
        <Alert
          tone="ok"
          style={{
            position: "absolute",
            top: ALERT[1],
            left: ALERT[0],
            width: ALERT[2],
            height: ALERT[3],
            boxSizing: "border-box",
            opacity: Math.min(1, created * 2),
            transform: `scale(${0.9 + 0.1 * created})`,
          }}
        >
          <b>وصل استبيانك وتم إنشاء طلبك.</b> رقم طلبك <b style={{ fontFamily: MONO }}>{ORDER_NO}</b>. احتفظ به للتواصل.
        </Alert>
        <H size={44} style={{ position: "absolute", top: 290, right: 40 }}>الباقة المكثفة</H>
        <div style={{ position: "absolute", top: PILL[1] + 4, left: PILL[0] }}>
          {reviewed ? <Status tone="wait" style={{ transform: `scale(${0.8 + 0.2 * revA})` }}>جارٍ التحقق من الدفع</Status> : <Status tone="action">بانتظار الدفع</Status>}
        </div>
        <P size={22} style={{ position: "absolute", top: 352, right: 40 }}>
          طلب رقم <span style={{ fontFamily: MONO }}>{ORDER_NO}</span> · الدفع: تحويل بنكي
        </P>

        <Card style={{ position: "absolute", top: 400, left: 40, width: 920, height: 430, boxSizing: "border-box", padding: "20px 30px" }}>
          <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 30, color: L.heading }}>الخطوة التالية</div>
          {!reviewed || revA < 1 ? (
            <div style={{ opacity: 1 - revA }}>
              <P size={24} muted={false} style={{ marginTop: 4 }}>حوّل المبلغ على الحساب التالي، ثم ارفع صورة الإيصال.</P>
            </div>
          ) : null}
          {reviewed && (
            <P size={27} muted={false} style={{ marginTop: 20, opacity: revA, lineHeight: 1.7 }}>
              وصلنا إيصالك. نتحقق من وصول المبلغ في الحساب، وتتحدث حالة طلبك هنا. <b>ما عليك أي إجراء الآن.</b>
            </P>
          )}
        </Card>
        {/* bank details (IBAN masked for the video) */}
        <div
          style={{
            position: "absolute",
            left: BANK[0],
            top: BANK[1],
            width: BANK[2],
            height: BANK[3],
            background: L.paper,
            borderRadius: 18,
            padding: "18px 24px",
            boxSizing: "border-box",
            opacity: 1 - revA,
          }}
        >
          <Row k="اسم الحساب" v="مؤسسة ناف كوتشنق للتدريب الرياضي" />
          <Row k="البنك" v="مصرف الراجحي" />
          <Row k="الآيبان" v="SA•• •••• •••• •••• •••• ••••" mono />
        </div>
        <Btn
          kind="ghost"
          style={{ position: "absolute", left: COPY[0], top: COPY[1], width: COPY[2], height: COPY[3], fontSize: 23, background: copied ? L.okBg : "#fff", color: copied ? L.ok : L.navy, opacity: 1 - revA }}
          press={pressAt(f, C.copy)}
        >
          {copied ? "✓ تم النسخ" : "نسخ الآيبان"}
        </Btn>
        <div
          style={{
            position: "absolute",
            left: DROP[0],
            top: DROP[1],
            width: DROP[2],
            height: DROP[3],
            boxSizing: "border-box",
            borderRadius: 18,
            border: `3px dashed ${uploaded ? L.ok : L.cyan}`,
            background: uploaded ? L.okBg : L.cyanSoft,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 14,
            fontFamily: FONT,
            fontWeight: 600,
            fontSize: 27,
            color: uploaded ? L.ok : L.cyanInk,
            opacity: 1 - revA,
            transform: `scale(${1 + 0.04 * Math.max(0, 1 - Math.abs(f - C.fileIn) / 10)})`,
          }}
        >
          {uploaded ? (
            <>
              ✓ <span style={{ fontFamily: MONO, fontSize: 25 }}>receipt.jpg</span> · تم رفع الإيصال
            </>
          ) : (
            <>⬆ ارفع صورة الإيصال</>
          )}
        </div>
        <SiteHeader account />
        <Spotlight keys={spots} />
      </BrowserWindow>
      <MacCursor path={cursor} clicks={[C.copy, C.upload]} from={C.bankSpot} to={S1} />
    </>
  );
};

const Row: React.FC<{ k: string; v: string; mono?: boolean }> = ({ k, v, mono }) => (
  <div style={{ display: "flex", gap: 20, alignItems: "baseline", marginBottom: 8 }}>
    <span style={{ width: 150, fontFamily: FONT, fontSize: 21, color: L.muted }}>{k}</span>
    <span style={{ fontFamily: mono ? MONO : FONT, fontSize: mono ? 24 : 25, fontWeight: 600, color: L.text, direction: mono ? "ltr" : "rtl" }}>{v}</span>
  </div>
);
