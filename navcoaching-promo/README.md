# Nav Coaching — Promo (Remotion)

مقطع ترويجي عمودي لـ navcoaching.com
**1080×1920 · 60fps · 20 ثانية · H.264 + صوت 320k**

## المشاهد

| الوقت | المشهد | الحركة | الصوت |
|---|---|---|---|
| 0–3s | INIT | جزيئات تتجمع، شعار NAV يتركّب من 3 قطع، Drop عند 2s، ثم Zoom-through | Riser + Sub drone ← Impact + Bass hit + Shimmer |
| 3–7s | PHILOSOPHY | Kinetic: «تدريب / مبني / عليك» ← «مو جدول جاهز» يُشطب ويتكسّر ← «مخصص لك بعد الاستبيان» | Impact لكل كلمة، Bass على «عليك»، Swipe + Glitch |
| 7–12s | PROGRAM | بطاقة 3D لجدول اليوم، الصفوف تنبني، اختيار بديل التمرين من القائمة وتحديث العضلات | UI blips لكل صف، Clicks، Pops |
| 12–16s | PROGRESS | رسم متوسط الوزن الأسبوعي، حلقة هدف الخطوات، المراجعة الأسبوعية | Blips صاعدة، نغمة تعبئة، Chime |
| 16–18s | PLATFORM | 4 مزايا على 4 ضربات مع Warp | Impact لكل بطاقة + Riser + Snare roll |
| 18–20s | START | الشعار، «تدريب مبني عليك»، زر «اختر برنامجك»، كتابة الرابط | Final impact + Bass، Typing ticks، Click |

## التزامن

`src/cues.json` هو المصدر الوحيد للتوقيت: المشاهد (`src/scenes/*`) ومولّد الصوت (`audio/generate.py`) يقرآن منه نفس الفريمات. أي تعديل على توقيت يُطبّق على الصورة والصوت معاً بعد إعادة توليد الصوت.

الموسيقى 120 BPM، يعني كل Beat = 30 فريم، فكل الضربات والقطعات على الإيقاع.

## الصوت

كل الأصوات مولّدة برمجياً (synthesis) بدون عينات خارجية، فلا توجد مشكلة حقوق:
Music (Pad + Sub + Arp + Drums) · Impacts · Bass hits (808) · Whooshes · Risers · UI sounds (blips/clicks/pops/ticks) · Glitch · Shimmer · Chimes.
مع Sidechain على الـPad وخفض الموسيقى تحت مقاطع الواجهة عشان أصوات الـUI تكون واضحة.

## التشغيل

```bash
npm install
pip install numpy scipy          # لتوليد الصوت
npm run audio                     # يولّد public/audio/soundtrack.wav
npm run studio                    # معاينة
npm run stills -- 120 240 600     # فريمات للفحص البصري → stills/
npm run render                    # out/navcoaching-promo.mp4
```

`remotion.config.ts` يستخدم Chromium المثبت مسبقاً في البيئة. على جهازك احذف سطر `setBrowserExecutable`.

## المحتوى

النصوص والمزايا والألوان مأخوذة من كود الموقع (`navcoaching/navcoaching-website`): ألوان `globals.css`، شعار NAV (محوّل إلى SVG)، عناوين الصفحة الرئيسية، وعيّنة جدول «DAY 1 — LOWER BODY». أرقام لوحة التقدم من اللقطة التوضيحية في الموقع، وعليها وسم «نموذج توضيحي».
