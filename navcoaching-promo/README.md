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

---

# المقطع الثاني: رحلة المستخدم (NavJourney)

**1080×1920 · 60fps · 72 ثانية** — على فكرة «رحلة كاملة للمستخدم»: مشكلة ← «اليوم غير» ← الشعار ← 6 فصول بواجهات الموقع (سبوت لايت + مؤشر + ترجمة) ← خاتمة.

| الملف | الوصف |
|---|---|
| `render/navcoaching-journey.mp4` | المقطع (موسيقى + مؤثرات، بدون تعليق) |
| `render/navcoaching-journey-bed.wav` | الموسيقى + المؤثرات لتركيب صوتك عليها |
| `journey/VOICEOVER_SCRIPT.md` | سكربت التعليق مع التوقيت لكل جملة |

- التوقيت كله في `src/journey/journey.json`: الفصول، الترجمة، النقرات، والأصوات.
- الواجهات مبنية من كود الموقع نفسه (النصوص، الألوان، خطوات الاستبيان، حالات الطلب)، وما هي لقطات شاشة.
- الأرقام التوضيحية (رقم الطلب، نتيجة الحاسبة، ردّ المدربة) أمثلة وليست بيانات حقيقية، والآيبان مخفي.

```bash
python3 audio/journey.py                     # public/audio/journey.wav + stems
COMP=NavJourney OUT=stills/j npm run stills -- 1000 2000
npx remotion render NavJourney out/navcoaching-journey.mp4 --props='{"withAudio":true}'
```

---

# المقطع الثالث: دليل استخدام الموقع (NavTutorial)

**1080×1920 · 60fps · 2:52** — `render/navcoaching-tutorial.mp4`

- كل الصور لقطات حقيقية من navcoaching.com بحجم iPhone (390×844 بدقة 3×)، ملتقطة بـ Playwright (`capture/`).
- الفصول: الرئيسية، القائمة، البرامج، الاختبار، تفاصيل الباقة، الدخول، الاستبيان، الدفع، حسابي، بعد التفعيل (دليل الاستخدام)، الحاسبة، التقييمات والأسئلة.
- الاستبيان عُبّي ببيانات تجريبية، والطلب التجريبي أُلغي بعد التصوير، والإيميل مموّه في كل اللقطات (`capture/blur.py`).
- التوقيت في `src/tutorial/tutorial.json`، والصوت من `audio/tutorial.py`.

```bash
node capture/public.mjs                 # الصفحات العامة (قراءة فقط)
python3 audio/tutorial.py
npx remotion render NavTutorial out/navcoaching-tutorial.mp4 --props='{"withAudio":true}'
```

---

# المقطع الرابع: «خطة 3 أيام» بمقاطع رياضية (NavSplit)

**1080×1920 · 60fps · 52 ثانية** — `render/navcoaching-split.mp4` — على فكرة ريل «3-day split»: هوك ← عنوان ← 3 أيام (أرجل / جزء علوي / جسم كامل) بينها أيام راحة ← إضافات اختيارية ← شعار وموقع.

- **المقاطع الرياضية** من مكتبة Mixkit (رخصة Mixkit Stock Video Free License: استخدام تجاري وتعديل مسموح، الإشارة غير إلزامية)، والمصدر مكتوب بخط صغير في آخر المقطع، والتفاصيل لكل مقطع في `split/CREDITS.md`.
- **الفلتر السينمائي**: تصحيح لوني (ظلال تيل / إضاءات دافئة)، Vignette، توهّج (Bloom)، وحبيبات فيلم (Grain) كطبقة فوق الفيديو.
- التوقيت في `src/split/split.json` و`src/split/data.ts`، والصوت (موسيقى + مؤثرات) من `audio/split.py`، وسكربت التعليق في `split/VOICEOVER_SCRIPT.md`.

```bash
python3 split/fetch.py            # تحميل المقاطع المرخّصة (split/src)
python3 split/process.py          # قص + تدريج لوني -> public/split/clips
python3 audio/split.py            # الصوت
npx remotion render NavSplit out/navcoaching-split.mp4 --props='{"withAudio":true}'
```

# الانترو (NavIntro) — 4 ثوانٍ عمودي 1080×1920 · 30fps

الملفات: `render/intro/nav-intro-with-sound.mp4` و`render/intro/nav-intro-silent.mp4`.
المصدر: `src/intro/Intro.tsx` (التحريك) و`src/intro/config.json` (الإعدادات) و`audio/intro.py` (الصوت) — والشعار الأصلي من `public/brand/` بلا أي تعديل.

**التعديل** (كله في `src/intro/config.json`):
- الجملة: `tagline`. الاسم جزء من صورة الشعار؛ لتغييره بدّل الملف في `logo` (مثلاً `brand/logo-color.webp`) وعدّل `logoWidth`.
- الألوان: `colors` (الخلفية `bgInner/bgMid/bgOuter`، الإبراز `accent`، لون الجملة `tagline`).
- المدة: `durationSec` (التوقيتات داخل `Intro.tsx` بالثواني: الشعار 0.4–1.8، الخط 1.8–2.4، الجملة 2.2–3.0).
- الصوت: `audio.peakDb` (مستوى الذروة، الحالي -22 dBFS) و`fadeInSec` و`fadeOutSec`.

```bash
python3 audio/intro.py                                    # يعيد توليد الصوت من الإعدادات
npx remotion render NavIntro out/intro-audio.mp4  --props='{"withAudio":true}'  --codec h264 --crf 14
npx remotion render NavIntro out/intro-silent.mp4 --props='{"withAudio":false}' --codec h264 --crf 14
```
المعاينة الثابتة: `node intro/preview/build.mjs`.

# الخاتمة (NavOutro) — 7.5 ثانية عمودي 1080×1920 · 30fps

الملفات: `render/outro/nav-outro-with-sound.mp4` و`render/outro/nav-outro-silent.mp4` وصورة الإطار النهائي `render/outro/nav-outro-final-frame.png`.
المصدر: `src/outro/Outro.tsx` (التحريك) و`src/outro/config.json` (الإعدادات) و`audio/outro.py` (الصوت). الشعار الأصلي من `public/brand/` بلا تعديل، وصورة الموقع `public/brand/site-home.jpg` لقطة حقيقية للصفحة الرئيسية.

**التعديل** (كله في `src/outro/config.json`):
- رابط الموقع: `url` — وأسماء الخدمات: `services` (أربعة عناصر، تُرتّب يمين ثم يسار).
- المدة: `durationSec` — والتوقيتات بالثواني في `timing` (مثلاً `phoneSpin` لدوران الجوال، `click` للنقرة، `fadeOut` للتلاشي). عند تغيير المدة حرّك `fadeOut` معها وأبقِ ثانيتين على الأقل بين نهاية `url` وبداية `fadeOut`.
- الصوت: `audio.peakDb` (الذروة، الحالية -22 dBFS)، `fadeInSec`، `fadeOutSec`، و`clickGain` لقوة صوت النقرة.
- الألوان: `colors`.

```bash
python3 audio/outro.py      # بعد أي تعديل في التوقيت أو الصوت
npx remotion render NavOutro out/outro-audio.mp4  --props='{"withAudio":true}'  --codec h264 --crf 14
npx remotion render NavOutro out/outro-silent.mp4 --props='{"withAudio":false}' --codec h264 --crf 14
npx remotion still  NavOutro render/outro/nav-outro-final-frame.png --frame=180 --image-format=png
```
