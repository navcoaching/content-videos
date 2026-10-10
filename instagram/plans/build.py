# -*- coding: utf-8 -*-
"""Instagram carousels for the six free plans (site style, Cairo font).

Inputs : plans-data.json (DAYS extracted from pdf/prog-*-portrait.html), panels.json (+ panel PNGs)
Output : <plan>/slides.html  +  <plan>/slides.json (render spec for render.js)
"""
import json, os, html
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, 'plans-data.json'), encoding='utf8'))
PANELS = json.load(open(os.path.join(HERE, 'panels.json'), encoding='utf8'))
ANAT = json.load(open(os.path.join(HERE, '../../pdf/anatomy-data.json'), encoding='utf8'))

# exercise -> stock clip (Coverr, free licence). crop = w:h:x:y on the 1920x1080 source
CLIPS = {
    'LATS PULLDOWN': dict(f='coverr-doing-chest-exercises-in-the-gym-3449.mp4', ss=1, crop='1283:1080:222:0'),
    'BARBELL BENCH PRESS': dict(f='coverr-weight-lifting-in-the-gym-7769.mp4', ss=2, crop='1283:1080:400:0'),
    'DB CURL': dict(f='coverr-man-training-in-the-gym-8192.mp4', ss=7, crop='1283:1080:150:0'),
    'MACHINE INCLINE CHEST PRESS': dict(f='coverr-using-the-machines-at-the-gym-1295.mp4', ss=2, crop='1283:1080:318:0'),
    'HANGING LEG RAISES': dict(f='wm-leg-raises.webm', ss=0, crop='400:337:0:0', src='854:480', credit='FitnessScape · CC BY 3.0 · Wikimedia Commons'),
    'LEG PRESS': dict(f='wm-hip-sled.webm', ss=48, crop='571:480:99:0', src='854:480', credit='FitnessScape · CC BY 3.0 · Wikimedia Commons'),
}

PLANS = {
    'gym3':   dict(title='جدول تمرين <em>3 أيام</em>', place='بالنادي', sub='يوم علوي · يوم سفلي · يوم شامل', fem=False, site='تمرين 3 أيام | نادي'),
    'home3':  dict(title='جدول تمرين <em>3 أيام</em>', place='بالمنزل', sub='يوم علوي · يوم سفلي · يوم شامل', fem=False, site='تمرين 3 أيام | منزل'),
    '4days':  dict(title='جدول تمرين <em>4 أيام</em>', place='نادي ومنزل', sub='التمرين الأساسي بالنادي · والبديل بالمنزل', fem=False, site='تمرين 4 أيام | نادي | منزل'),
    'glutes': dict(title='جدول بناء <em>القلوتس</em>', place='نادي ومنزل', sub='3 أيام بالأسبوع · التمرين بالنادي والبديل بالمنزل', fem=True, site='جدول بناء القلوتس'),
    'back':   dict(title='جدول <em>الظهر</em>', place='نادي أو منزل', sub='أعلى الظهر (التحدّب) وأسفل الظهر', fem=False, site='جدول استقامة الظهر'),
    'flex':   dict(title='جدول زيادة <em>المرونة</em>', place='من المنزل', sub='الحوض · الظهر · الأكتاف · الأرجل', fem=False, site='جدول زيادة المرونة'),
}

MAP = {'chest': ['CHEST'], 'fdelt': ['FRONT_DELTOIDS'], 'sdelt': ['FRONT_DELTOIDS', 'BACK_DELTOIDS'], 'rdelt': ['BACK_DELTOIDS'],
       'biceps': ['BICEPS'], 'triceps': ['TRICEPS'], 'lats': ['UPPER_BACK'], 'rhomb': ['TRAPEZIUS'], 'gmed': ['GLUTEAL'],
       'lowb': ['LOWER_BACK'], 'obl': ['OBLIQUES'], 'hflex': ['QUADRICEPS'], 'add': ['ABDUCTORS', 'ABDUCTOR'], 'abs': ['ABS'],
       'quads': ['QUADRICEPS'], 'glutes': ['GLUTEAL'], 'hams': ['HAMSTRING'], 'calves': ['CALVES', 'LEFT_SOLEUS', 'RIGHT_SOLEUS']}
LOW = {'quads', 'glutes', 'hams', 'calves', 'gmed', 'hflex', 'add'}
MID = {'abs', 'obl', 'lowb'}


def body(view, pri, sec):
    P = {m for k in pri for m in MAP[k]}
    S = {m for k in sec for m in MAP[k]}
    allm = set(pri) | set(sec)
    kind = 'low' if allm <= LOW else 'mid' if allm <= MID else 'up'
    vb = {'f': {'up': '2 0 96 104', 'mid': '8 30 84 88', 'low': '24 88 52 108'},
          'b': {'up': '2 0 96 116', 'mid': '8 34 84 98', 'low': '24 98 52 122'}}[view][kind]
    o = []
    for m, ps in (ANAT['anteriorData'] if view == 'f' else ANAT['posteriorData']):
        if kind == 'low' and m == 'FOREARM':
            continue
        col = '#284da0' if m in P else ('#4cc5ed' if m in S else '#cfd8e3')
        o += [f'<polygon points="{p}" fill="{col}" stroke="#fff" stroke-width=".6" stroke-linejoin="round"/>' for p in ps]
    return f'<svg viewBox="{vb}" preserveAspectRatio="xMidYMid meet">{"".join(o)}</svg>'


CSS = r'''
:root{--ink:#07142a;--navy:#284da0;--cyan:#4cc5ed;--cyan-ink:#0a6a8f;--cyan-soft:#e4f6fc;--paper:#f3f6fa;--line:#d8e1ea;--muted:#56667a;--head:#0b1a33}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#888;font-family:Cairo,"IBM Plex Sans Arabic",sans-serif;color:var(--head)}
.s{width:1080px;height:1350px;position:relative;overflow:hidden;margin:0 0 30px;background:var(--paper)}
.s::before{content:"";position:absolute;inset:0;background-image:linear-gradient(#284da00f 1px,transparent 1px),linear-gradient(90deg,#284da00f 1px,transparent 1px);background-size:56px 56px;pointer-events:none}
.top{position:absolute;z-index:5;top:44px;right:48px;left:48px;display:flex;justify-content:space-between;align-items:center}
.top img{height:50px}
.eb{display:inline-flex;align-items:center;gap:10px;font:700 25px Cairo;color:var(--cyan-ink);background:#fff;border:1.5px solid var(--line);border-radius:99px;padding:7px 22px;white-space:nowrap}
.mk{height:1.05em;width:auto;display:inline-block;vertical-align:middle}
.eb i,.lab i,.sl i{display:inline-block;width:7px;height:20px;background:var(--cyan);transform:skewX(-22deg);margin-left:3px}
.foot{position:absolute;z-index:6;bottom:38px;right:48px;left:48px;display:flex;justify-content:space-between;align-items:center;font:500 22px "Readex Pro";color:var(--muted)}
.foot .n{border:1.5px solid var(--line);background:#fff;border-radius:99px;padding:4px 18px;direction:ltr}
.foot .r{font-family:Cairo;font-weight:700}
/* grid */
.grid{position:absolute;z-index:2;top:126px;right:48px;left:48px;bottom:96px;display:grid;column-gap:24px}
.L4{grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;row-gap:96px}
.L3{grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;row-gap:96px}
.L3 .t:nth-child(3){grid-column:1 / span 2}
.L2{grid-template-columns:1fr 1fr;grid-template-rows:1fr;top:226px}
.L1{grid-template-columns:1fr;grid-template-rows:1fr;top:226px}
.t{min-height:0;display:flex;flex-direction:column;border-radius:28px;overflow:hidden;box-shadow:0 16px 36px #284da014}
.vid{flex:1;min-height:0;position:relative;overflow:hidden;border:1.5px solid var(--line);border-bottom:none;border-radius:28px 28px 0 0;
 background:linear-gradient(160deg,#ffffff,#e6eef8)}
.vid.live{background:transparent}
.bod{position:absolute;inset:34px 18px 12px;display:flex;justify-content:center;gap:4%}
.bod svg{height:100%;width:46%}
.no{position:absolute;z-index:3;top:14px;right:14px;width:50px;height:50px;border-radius:15px;background:var(--cyan);color:var(--ink);font:700 27px "Readex Pro";display:flex;align-items:center;justify-content:center}
.legend{position:absolute;z-index:3;top:20px;left:16px;display:flex;gap:10px;font:500 17px Cairo;color:var(--muted)}
.legend b{display:inline-block;width:13px;height:13px;border-radius:4px;margin-left:5px;vertical-align:-1px}
.vnote{position:absolute;z-index:3;bottom:12px;left:12px;right:12px;text-align:center;font:600 17px Cairo;color:#fff;background:#07142acc;border-radius:99px;padding:4px 10px}
.cap{background:#fff;border:1.5px solid var(--line);border-top:none;border-radius:0 0 28px 28px;padding:12px 18px 14px}
.cap b{display:block;font:700 23px "Readex Pro";direction:ltr;text-align:right;color:var(--head);line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cap .m{font-size:18px;color:var(--muted);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cap .row{display:flex;gap:8px;margin-top:8px;align-items:center;flex-wrap:nowrap}
.chip{background:var(--cyan-soft);color:var(--navy);border-radius:10px;padding:3px 10px;font:700 18px Cairo;white-space:nowrap}
.chip em{font-style:normal;font-family:"Readex Pro";direction:ltr;unicode-bidi:isolate}
.alt{display:block;margin-top:6px;font-size:17px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.alt bdi{font-family:"Readex Pro";font-weight:500;color:var(--head)}
.lab{position:absolute;z-index:4;left:50%;transform:translate(-50%,-50%);background:var(--ink);color:#fff;border-radius:99px;padding:14px 38px;font:900 36px Cairo;display:flex;align-items:center;gap:14px;box-shadow:0 18px 40px #07142a40;white-space:nowrap}
.lab small{font:500 22px "IBM Plex Sans Arabic";color:#a9d8ec}
/* panels */
.pw{position:absolute;z-index:2;top:130px;right:48px;left:48px;bottom:96px;display:flex;align-items:center;justify-content:center}
.pw img{max-width:100%;max-height:100%;border-radius:28px;box-shadow:0 16px 36px #284da018}
/* cover */
.cv h1{font:900 112px/1.12 Cairo;color:var(--head)}
.cv h1 em{font-style:normal;color:var(--navy)}
.cv .c{position:absolute;z-index:3;top:170px;right:64px;left:64px}
.cv .place{display:inline-block;margin-top:14px;background:var(--cyan);color:var(--ink);font:900 34px Cairo;padding:6px 26px;border-radius:99px}
.cv .sub{font-size:32px;color:var(--muted);margin-top:18px;line-height:1.6;font-family:"IBM Plex Sans Arabic"}
.days{margin-top:44px;display:flex;flex-direction:column;gap:22px}
.day{background:#fff;border:1.5px solid var(--line);border-radius:28px;padding:24px 28px;display:flex;align-items:center;gap:20px;box-shadow:0 12px 28px #284da012}
.day .k{flex:0 0 104px;height:104px;border-radius:22px;background:var(--navy);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;font:900 36px/1 "Readex Pro"}
.day .k small{font:700 17px Cairo;margin-bottom:3px}
.day:nth-child(1) .k{background:var(--cyan);color:var(--ink)}.day:nth-child(3) .k{background:var(--ink)}
.day h3{font:900 40px/1.3 Cairo}.day p{font-size:24px;color:var(--muted);font-family:"IBM Plex Sans Arabic"}
.day .cnt{margin-inline-start:auto;font:700 25px Cairo;color:var(--cyan-ink);white-space:nowrap}
.free{position:absolute;z-index:3;bottom:110px;right:64px;left:64px;background:var(--ink);color:#fff;border-radius:28px;padding:24px 30px;display:flex;align-items:center;justify-content:space-between}
.free b{font:900 34px Cairo}.free span{font:700 28px "Readex Pro";color:var(--cyan)}
/* ad */
.ad{background:radial-gradient(70% 50% at 85% 10%,#1f4a8f 0%,transparent 70%),linear-gradient(165deg,#0d1f3c,#07142a 75%);color:#fff}
.ad::before{background-image:linear-gradient(#4cc5ed12 1px,transparent 1px),linear-gradient(90deg,#4cc5ed12 1px,transparent 1px)}
.ad .c{position:absolute;z-index:3;top:150px;right:64px;left:64px}
.ad .ebd{display:inline-flex;align-items:center;gap:10px;font:700 26px Cairo;color:var(--cyan)}
.ad h2{font:900 80px/1.2 Cairo;margin-top:16px}
.ad h2 em{font-style:normal;color:var(--cyan)}
.ad ul{list-style:none;margin-top:30px;display:flex;flex-direction:column;gap:16px}
.ad li{display:flex;align-items:center;gap:18px;font:700 32px Cairo}
.ad li i{flex:0 0 46px;height:46px;border-radius:14px;background:var(--cyan);color:var(--ink);display:flex;align-items:center;justify-content:center;font-style:normal;font-size:26px}
.ad .price{margin-top:34px;display:flex;gap:14px;flex-wrap:wrap}
.ad .price span{border:1.5px solid #ffffff40;border-radius:99px;padding:8px 22px;font:700 26px Cairo;color:#d4e0f0}
.ad .price b{font-family:"Readex Pro";color:#fff}
.ad .cta{position:absolute;z-index:3;bottom:120px;right:64px;left:64px;background:var(--cyan);color:var(--ink);border-radius:30px;padding:26px 34px;display:flex;align-items:center;justify-content:space-between}
.ad .cta b{font:900 44px Cairo}.ad .cta span{font:700 32px "Readex Pro"}
.ad .foot{color:#a9bad0}.ad .foot .n{background:transparent;border-color:#ffffff40;color:#a9bad0}
'''

LOGO = '<img src="../../../brand/logo-color-hd.png">'
LOGO_W = '<img src="../../../brand/logo-white.webp">'
SL = '<img class="mk" src="../../../brand/nav-mark-navy.png">'
SLW = '<img class="mk" src="../../../brand/nav-mark-white.png">'


def esc(s):
    return html.escape(s, quote=False)


def tile(i, r, rl, al):
    name, _yt, musc, pri, sec, sets, reps, alt = r[:8]
    clip = CLIPS.get(name)
    reps = reps.replace('<br>', ' ')
    sets_s = f'<em>{sets}</em> جولات' if isinstance(sets, int) else f'<em>{sets}</em>'
    if clip:
        media = (f'<div class="vid live" data-clip="{clip["f"]}" data-ss="{clip["ss"]}" data-crop="{clip["crop"]}" data-src="{clip.get("src", "1920:1080")}" data-credit="{clip.get("credit", "Coverr")}"><span class="no">{i}</span>'
                 + (f'<span class="vnote">{clip["note"]}</span>' if clip.get('note') else '') + '</div>')
    else:
        media = (f'<div class="vid"><span class="no">{i}</span>'
                 '<span class="legend"><span><b style="background:#284da0"></b>أساسية</span><span><b style="background:#4cc5ed"></b>مساعدة</span></span>'
                 f'<div class="bod">{body("f", pri, sec)}{body("b", pri, sec)}</div></div>')
    return (f'<div class="t">{media}<div class="cap"><b>{esc(name)}</b><div class="m">{" · ".join(musc)}</div>'
            f'<div class="row"><span class="chip">{sets_s}</span><span class="chip">{rl or "العدات"}: <em>{esc(reps)}</em></span>'
            f'</div><span class="alt">{al or "البديل"}: <bdi>{esc(alt)}</bdi></span></div></div>')


def split(rows):
    n = len(rows)
    if n <= 4:
        return [rows]
    if n == 5:
        return [rows[:3], rows[3:]]
    if n == 6:
        return [rows[:3], rows[3:]]
    return [rows[i:i + 4] for i in range(0, n, 4)]


def build(key):
    P = PLANS[key]
    D = DATA[key]['D']
    fem = P['fem']
    plain_title = html.unescape(P['title'].replace('<em>', '').replace('</em>', ''))
    slides = []   # (html, kind)

    # ---- cover
    days_html = ''.join(
        f'<div class="day"><div class="k"><small>{d.get("lbl", "اليوم")}</small>{d["n"]}</div><div><h3>{d["title"]}</h3>'
        f'<p>{d.get("sub", "")}</p></div><span class="cnt">{len(d["rows"])} تمارين</span></div>' for d in D)
    slides.append(('cover', f'''<div class="top">{LOGO}<span class="eb">جدول مجاني {SL}</span></div>
<div class="c"><h1>{P["title"]}</h1><span class="place">{P["place"]}</span><div class="sub">{P["sub"]}</div><div class="days">{days_html}</div></div>
<div class="free"><b>{"حمّليه" if fem else "حمّله"} PDF مجانًا</b><span>navcoaching.com</span></div>'''))

    # ---- day slides
    for d in D:
        parts = split(d['rows'])
        idx = 1
        for pi, part in enumerate(parts):
            lay = {4: 'L4', 3: 'L3', 2: 'L2', 1: 'L1'}[len(part)]
            tiles = ''.join(tile(idx + j, r, d.get('rl'), d.get('al')) for j, r in enumerate(part))
            idx += len(part)
            lbl = d.get('lbl', 'اليوم')
            more = f' · {pi + 1}/{len(parts)}' if len(parts) > 1 else ''
            lab_top = '685px' if lay in ('L4', 'L3') else '176px'
            slides.append(('day', f'''<div class="top">{LOGO}<span class="eb">{plain_title} {SL}</span></div>
<div class="grid {lay}">{tiles}</div>
<div class="lab" style="top:{lab_top}">{SLW}{lbl} {d["n"]} · {d["title"]}<small>{len(d["rows"])} تمارين{more}</small></div>'''))

    # ---- info panels (everything else in the PDF)
    for p in PANELS[key]:
        img = Image.open(p['f'])
        rel = os.path.relpath(p['f'], os.path.join(HERE, key))
        if img.height > 1900:   # equipment page: split in two halves
            w, h = img.size
            for part, (a, b) in enumerate(((0, h // 2), (h // 2, h))):
                fn = p['f'].replace('.png', f'-{part}.png')
                img.crop((0, a, w, b)).save(fn)
                slides.append(('info', f'''<div class="top">{LOGO}<span class="eb">{p["title"]} {SL}</span></div>
<div class="pw"><img src="{os.path.relpath(fn, os.path.join(HERE, key))}"></div>'''))
            continue
        slides.append(('info', f'''<div class="top">{LOGO}<span class="eb">{p["title"]} {SL}</span></div>
<div class="pw"><img src="{rel}"></div>'''))

    # ---- ad
    you = dict(want='تبين' if fem else 'تبي', start='ابدئي' if fem else 'ابدأ', your='لك')
    slides.append(('ad', f'''<div class="top">{LOGO_W}<span class="ebd" style="font:700 24px Cairo;color:#a9d8ec">navcoaching.com</span></div>
<div class="c"><span class="ebd">Nav Coaching {SLW}</span>
<h2>{you["want"]} نتيجة أسرع؟<br><em>برنامج مصمم {you["your"]}</em></h2>
<ul><li><i>✓</i>تمرين وتغذية مخصصة لهدفك</li><li><i>✓</i>متابعة أسبوعية بالفيديو أو الصوت</li>
<li><i>✓</i>تعديلات حسب تقدمك وقياساتك</li><li><i>✓</i>تواصل يومي على واتساب</li></ul>
<div class="price"><span>الباقات من <b>250</b> ر.س / شهر</span><span>خصم <b>10%</b> للطلاب</span><span>ضمان استرجاع بشروط</span></div></div>
<div class="cta"><b>{you["start"]} برنامجك ←</b><span>navcoaching.com</span></div>'''))

    # ---- assemble
    N = len(slides)
    out = ['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>' + CSS + '</style></head><body>']
    spec = []
    for i, (kind, inner) in enumerate(slides, 1):
        live = 'data-clip=' in inner
        import re as _re
        creds = sorted(set(_re.findall(r'data-credit="([^"]+)"', inner)))
        credit = ('Videos: ' + ' | '.join(creds)) if live else 'navcoaching.com'
        cls = 's ad' if kind == 'ad' else ('s cv' if kind == 'cover' else 's')
        out.append(f'<section class="{cls}" id="s{i}">{inner}<div class="foot"><span class="n">{i} / {N}</span>'
                   f'<span class="r">{credit}</span></div></section>')
        spec.append(dict(id=f's{i}', kind=kind, video=live))
    out.append('</body></html>')
    os.makedirs(os.path.join(HERE, key), exist_ok=True)
    open(os.path.join(HERE, key, 'slides.html'), 'w', encoding='utf8').write('\n'.join(out))
    json.dump(spec, open(os.path.join(HERE, key, 'slides.json'), 'w'))
    return N, sum(s['video'] for s in spec)


if __name__ == '__main__':
    import sys
    for k in (sys.argv[1:] or PLANS):
        print(k, build(k))
