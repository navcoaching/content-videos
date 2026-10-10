"""Generate Nav Coaching program PDFs (HTML sources) that reuse the approved design.

Base CSS + anatomy/day-page script come from program-home.html / program.html.
Run:  python3 pdf/build_programs.py   -> writes pdf/prog-*.html
"""
import json, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
gym = open(os.path.join(HERE, 'program.html'), encoding='utf8').read()
home = open(os.path.join(HERE, 'program-home.html'), encoding='utf8').read()

HEAD = home[:home.index('</style>')]
SCRIPT_T = gym[gym.index('<script>'):gym.index('</script>') + len('</script>')]


def section(src, marker):
    a = src.index(marker)
    return src[a:src.index('</section>', a) + len('</section>')]


THANKS = section(gym, '<!-- ================= PAGE 7 : THANK YOU')
RIR_PAGE = section(gym, '<!-- ================= PAGE 6 : INSTRUCTIONS 2')
EQUIP_PAGE = section(home, '<!-- ================= PAGE 5 : HOME EQUIPMENT')

EXTRA_CSS = '''
.flex .rep.t{font-size:15px;line-height:1.4;padding:5px 8px;text-align:center;white-space:nowrap}
.flex .num.t{font-size:22px}
/* ---------- generator additions */
.cover .lead{position:absolute;top:572px;right:84px;font:600 23px/1.5 "IBM Plex Sans Arabic";color:var(--navy);max-width:640px}
.days.d4{top:104px;gap:16px}
.days.d4 .day{padding:17px 26px}
.days.d4 .day .n{width:70px;height:70px}
.days .day h3 small{font:700 15px "IBM Plex Sans Arabic";color:var(--muted);margin-right:8px}
.dp .td{height:var(--rh,86px)}
.dp .top h2 small{display:block;font:600 17px "IBM Plex Sans Arabic";color:var(--muted);margin-top:6px}
.dp .badge.d{background:var(--navy2)}
.rep.t{direction:rtl;font-size:18px}
.num.t{font-size:21px;direction:ltr}
.refs{position:absolute;left:24px;right:24px;bottom:14px;font:500 12.5px/1.6 "IBM Plex Sans Arabic";color:var(--muted)}
.refs b{color:var(--navy)}
.refs a{color:var(--navy);text-decoration:underline;text-underline-offset:3px}
.week{padding:10px 22px}
.wd{display:flex;align-items:center;gap:14px;height:62px;border-bottom:1px dashed var(--line)}
.wd:last-child{border:0}
.wd .dn{width:92px;font:700 17px "IBM Plex Sans Arabic";color:var(--ink)}
.wd .ss{display:flex;gap:8px;flex-wrap:wrap}
.wd .ss span{font:700 15px "IBM Plex Sans Arabic";border-radius:10px;padding:7px 14px;background:var(--navy);color:#fff}
.wd .ss span.a{background:var(--cyan);color:var(--ink)}
.wd .ss span.c{background:var(--ink)}
.wd .ss span.r{background:var(--surf);color:var(--muted)}
.wd .ss span.o{background:#fff;border:1.5px solid var(--cyan);color:var(--cyan-ink)}
.alert{background:var(--ink);color:#fff;border-radius:18px;padding:18px 22px;margin:14px 24px 0}
.alert h4{font:800 20px Cairo;color:var(--cyan);margin-bottom:8px}
.alert li{font:500 16px/1.65 "IBM Plex Sans Arabic";color:#dbe6f3;margin-right:18px}
.alert p{font:500 15px/1.6 "IBM Plex Sans Arabic";color:var(--onm);margin-top:8px}
.kv{display:flex;gap:10px;margin:6px 0 2px}
.kv div{flex:1;background:var(--paper);border:1.5px solid var(--line);border-radius:12px;padding:10px 12px;text-align:center}
.kv b{display:block;font:800 22px "Readex Pro";color:var(--navy);direction:ltr}
.kv small{font:600 13px "IBM Plex Sans Arabic";color:var(--muted)}
.days .day.d .n{background:var(--navy2);color:#fff}.days .day.d{border-right-color:var(--navy2)}
.ip .notes .note p{font-size:18px;line-height:1.75}
.ip .notes .note{padding:10px 0}
.alert li{font-size:18px;line-height:1.8}
.alert p{font-size:16px}
'''

ICO = ('<div class="ico"><svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#284da0" '
       'stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 7v6"/>'
       '<circle cx="12" cy="16.6" r=".6" fill="#284da0"/></svg></div>')
LOGO = '<img class="logo" src="../brand/logo-color-hd.png" alt="Nav Coaching">'
SLASH = '<i class="slash" style="left:-40px;bottom:-40px;width:90px;height:190px;opacity:.25"></i>'


def top(title):
    return f'<div class="top">{ICO}<h2>{title}</h2>\n  {LOGO}</div>'


def cover(h1, lead, cards):
    d4 = ' d4' if len(cards) > 3 else ''
    cls = ['a', 'b', 'c', 'd']
    cc = ''.join(
        f'<div class="day {cls[i]}"><div class="n"><small>{c.get("lbl","اليوم")}</small>{c["n"]}</div>'
        f'<div><h3>{c["t"]}</h3><p>{c["p"]}</p></div><div class="cnt"><b>{c["k"]}</b>تمارين</div></div>\n'
        for i, c in enumerate(cards))
    return f'''
<section class="page light grid cover" data-sec="الغلاف">
 <i class="slash" style="left:-30px;bottom:-40px;width:120px;height:330px"></i>
 <i class="slash n" style="left:120px;bottom:-40px;width:120px;height:220px"></i>
 <i class="slash" style="right:640px;top:-40px;width:70px;height:170px;opacity:.25"></i>
 {LOGO}
 <span class="chip"><i></i>جدول مجاني</span>
 <h1>{h1}</h1>
 <span class="rule"></span>
 <div class="lead">{lead}</div>
 <div class="sign"><span>إعداد <b>كوتش ناڤ</b></span><span>navcoaching.com</span></div>
 <div class="days{d4}">
{cc} </div>
</section>'''


# ---------- volume helper (primary = full sets, secondary = half)
def weekly(days, groups):
    out = []
    for label, keys in groups:
        tot = 0.0
        for d in days:
            for r in d['rows']:
                sets = r[5] if isinstance(r[5], (int, float)) else 0
                if any(k in r[3] for k in keys):
                    tot += sets
                elif any(k in r[4] for k in keys):
                    tot += sets / 2
        out.append((label, tot))
    return out


def fmt(v):
    return str(int(v)) if float(v).is_integer() else f'{v:.1f}'


def chart_panel(rows, vmax, ticks, band=None, rng_label='', head=('مجموعة العضلات', 'مجموع الجولات')):
    rh = min(80, int(460 / len(rows)))
    band_css = f'right:{band[0]/vmax*100:.1f}%;left:{100-band[1]/vmax*100:.1f}%' if band else 'display:none'
    rr = ''.join(
        f'<div class="srow" style="height:{rh}px"><div class="mg">{n}</div><div class="trk">'
        f'<i class="band" style="{band_css}"></i><b style="width:{min(v,vmax)/vmax*100:.1f}%"></b></div>'
        f'<div class="v">{fmt(v)}</div></div>' for n, v in rows)
    ax = ''.join(f'<span style="right:{t/vmax*100:.1f}%">{t}</span>' for t in ticks)
    rng = ''
    if band:
        rng = (f'<span class="rng" style="right:{band[0]/vmax*100:.1f}%;left:{100-band[1]/vmax*100:.1f}%">'
               f'{rng_label}</span>')
    return f'''<div class="panel sets">
  <div class="ph"><span>{head[0]}</span><span>{head[1]}</span></div>
  {rr}
  <div class="scale"><div></div><div class="ax">{rng}{ax}</div><div></div></div>
 </div>'''


def notes_panel(title, notes, refs='', warm=''):
    nn = ''.join(f'<div class="note"><span class="k">{i+1}</span><p>{t}</p></div>' for i, t in enumerate(notes))
    return f'''<div class="panel notes">
  <div class="ph"><span>{title}</span></div>
  <div class="nl">{nn}</div>{warm}
  {f'<div class="refs">{refs}</div>' if refs else ''}
 </div>'''


def page(sec, title, *panels, extra_cls=''):
    body = '\n '.join(panels)
    return f'''
<section class="page light grid ip{extra_cls}" data-sec="{sec}">
 {SLASH}
 {top(title)}
 {body}
</section>'''


def week_panel(title, days, side='right:56px;width:560px'):
    rows = ''.join(
        f'<div class="wd"><span class="dn">{d}</span><div class="ss">'
        + ''.join(f'<span class="{c}">{t}</span>' for c, t in ss) + '</div></div>'
        for d, ss in days)
    return f'''<div class="panel" style="{side}">
  <div class="ph"><span>{title}</span></div>
  <div class="week">{rows}</div>
 </div>'''


WARM = '''<div class="warm">
   <p>تحمية خاصة للعضلات الي بتمرنونها, أول جولتين بنص الوزن الأساسي الي تشتغلون عليه، مثال: تمرين <b>سكوات بالبار</b> — وزن التمرين الأساسي: <b>20 كيلو</b></p>
   <div class="steps">
    <div class="st s1"><small>أول جولة تحمية</small><b>10 kg</b><span>50% من الوزن الأساسي</span></div>
    <div class="st s2"><small>ثاني جولة تحمية</small><b>14 kg</b><span>70% من الوزن الأساسي</span></div>
    <div class="st s3"><small>الجولة الأساسية الأولى</small><b>20 kg</b><span>100%</span></div>
   </div>
  </div>'''

MENNO_REFS = ('<b>المراجع:</b> Menno Henselmans — '
              '<a href="https://mennohenselmans.com/optimal-training-volume/">Optimal training volume</a> · '
              '<a href="https://mennohenselmans.com/maximum-productive-training-volume-per-session/">Max productive volume per session</a> · '
              '<a href="https://mennohenselmans.com/how-close-to-failure-should-you-train/">How close to failure</a>')



# feminine singular wording (same forms used in the original home PDF)
FEM_MAP = [
    ('اضغط على اسم التمرين لمشاهدة الشرح', 'اضغطي على اسم التمرين لمشاهدة الشرح'),
    ('تحمية خاصة للعضلات الي بتمرنونها, أول جولتين بنص الوزن الأساسي الي تشتغلون عليه،',
     'تحمية خاصة للعضلات الي بتمرنينها, أول جولتين بنص الوزن الأساسي الي تشتغلين عليه،'),
    ('في اول جلسة وقمت بـ <b>12 عدة</b>', 'في اول جلسة وقمتِ بـ <b>12 عدة</b>'),
    ('فالوزن كان تقدرون تزيدونه. ولو ماقدرتم تزيدون الوزن؟ وصلوا الى سقف العدات',
     'فالوزن كان تقدرين تزيدينه. ولو ماقدرتِ تزيدين الوزن؟ وصلي الى سقف العدات'),
    ('الاسبوع الي بعده تزيدون الوزن وتكون بنطاق', 'الاسبوع الي بعده تزيدين الوزن وتكون بنطاق'),
    ('<b>تزيدون الوزن</b>', '<b>تزيدين الوزن</b>'),
    ('<p>اذا عندكم اي استفسار بخصوص الرياضة او التغذية، تواصلوا معي.</p>',
     '<p>اذا عندك اي استفسار بخصوص الرياضة او التغذية، تواصلي معي.</p>'),
    ('<p>ولا عليكم أمر أتمنى منكم مشاركتي تعليقاتكم ونقدكم البناء من أجل تحسين جودة المحتوى</p>',
     '<p>ولا عليك أمر أتمنى منك مشاركتي تعليقاتك ونقدك البناء من أجل تحسين جودة المحتوى</p>'),
    ('بالليق برس: حطّوا الرجول <b>أعلى المنصة</b>', 'بالليق برس: حطّي رجولك <b>أعلى المنصة</b>'),
]


def feminize(html):
    for a, b in FEM_MAP:
        assert a in html, a
        html = html.replace(a, b)
    return html

def build(fname, title, cover_html, days, hdr, pages_after, fem=False, body_cls=''):
    script = SCRIPT_T
    script = re.sub(r'const DAYS=\[.*?\n\];', 'const DAYS=' + json.dumps(days, ensure_ascii=False) + ';', script, flags=re.S)
    script = script.replace('const TOTAL=7;', 'let TOTAL=0;')
    script = script.replace('// ---- pager on every page', '// ---- pager on every page\nTOTAL=document.querySelectorAll(".page").length;')
    script = script.replace(
        "lats:['UPPER_BACK'],rhomb:['TRAPEZIUS'],",
        "lats:['UPPER_BACK'],rhomb:['TRAPEZIUS'],gmed:['GLUTEAL'],lowb:['LOWER_BACK'],obl:['OBLIQUES'],hflex:['QUADRICEPS'],add:['ABDUCTORS','ABDUCTOR'],")
    script = script.replace("LOW=['quads','glutes','hams','calves'];",
                            "LOW=['quads','glutes','hams','calves','gmed','hflex','add'],MID=['abs','obl','lowb'];")
    script = script.replace("(all.length===1&&all[0]==='abs')?'mid'", "all.every(m=>MID.includes(m))?'mid'")
    # headers + per-day subtitle / row height / small label
    script = script.replace('<div class="r">اسم التمرين</div>', '<div class="r">' + hdr[0] + '</div>')
    script = script.replace('<div class="alt-h">بديل التمرين</div>', '<div class="alt-h">' + hdr[1] + '</div>')
    script = script.replace(
        """html+='<section class="page light grid dp" data-sec="اليوم '+d.n+' · '+d.title+'">'""",
        """html+='<section class="page light grid dp" style="--rh:'+(d.rows.length<=4?118:d.rows.length==5?100:86)+'px" data-sec="'+(d.sec||('اليوم '+d.n+' · '+d.title))+'">'""")
    script = script.replace("""<small>اليوم</small>'+d.n+'</div><h2>'+d.title+'</h2>'""",
                            """<small>'+(d.lbl||'اليوم')+'</small>'+d.n+'</div><h2>'+d.title+(d.sub?'<small>'+d.sub+'</small>':'')+'</h2>'""")
    script = script.replace("""'<div class="num">'+sets+'</div><div><span class="rep">'+reps+'</span></div>""",
                            """'<div class="num'+(typeof sets==='string'?' t':'')+'">'+sets+'</div><div><span class="rep'+(/[\\u0600-\\u06FF]/.test(reps)?' t':'')+'">'+reps+'</span></div>""")
    assert 'let TOTAL=0;' in script and 'MID.includes' in script and "d.lbl||" in script and "' t':''" in script
    head = HEAD.replace('<title>جدول تمرين 3 أيام بالمنزل — Nav Coaching</title>', f'<title>{title} — Nav Coaching</title>')
    html = head + EXTRA_CSS + f'</style></head><body class="{body_cls}">\n' + cover_html + '\n<div id="dayPages"></div>\n' + '\n'.join(pages_after) + '\n' + script + '\n</body></html>'
    if fem:
        html = feminize(html)
    open(os.path.join(HERE, fname), 'w', encoding='utf8').write(html)
    return fname


# =====================================================================
# 1) 4-DAY  (gym main + home alternative)
# =====================================================================
D4 = [
 {'n': 1, 'cls': 'a', 'title': 'علوي A', 'rows': [
  ['BARBELL BENCH PRESS', 'w:hWbUlkb5Ms4', ['صدر', 'أكتاف أمامية', 'تراي'], ['chest'], ['fdelt', 'triceps'], 3, '6-10', 'DB FLOOR PRESS', 'w:Bx4QPVH-J1g'],
  ['SEATED ROW', 'w:YKAeU55CkVk', ['لاتس', 'رومبويد', 'باي', 'كتف خلفي'], ['lats', 'rhomb'], ['biceps', 'rdelt'], 3, '8-12', 'ONE ARM DB ROW', 'KaCcBqhiXtc'],
  ['MACHINE SHOULDER PRESS', 'w:3R14MnZbcpw', ['أكتاف أمامية', 'تراي'], ['fdelt'], ['triceps'], 3, '8-12', 'SEATED DB SHOULDER PRESS', 'w:rO_iEImwHyo'],
  ['LATS PULLDOWN', 'w:hnSqbBk15tw', ['لاتس', 'باي'], ['lats'], ['biceps'], 3, '8-12', 'DB PULLOVER', 'w:jQjWlIwG4sI'],
  ['CABLE LATERAL RAISE', 'w:Z5FA9aq3L6A', ['كتف جانبي'], ['sdelt'], [], 3, '10-15', 'DB LATERAL RAISE', 'JIhbYYA1Q90'],
  ['TRICEPS PUSHDOWN', 'Rc7-euA8FDI', ['تراي'], ['triceps'], [], 3, '10-15', 'OVERHEAD DB TRICEPS EXTENSION', 'w:2jl4M0Dnq4c']]},
 {'n': 2, 'cls': 'b', 'title': 'سفلي A', 'rows': [
  ['SQUAT', 'PPmvh7gBTi0', ['أفخاذ أمامية', 'قلوتس'], ['quads'], ['glutes'], 3, '6-10', 'DB GOBLET SQUAT', 'w:gCESNsDsbqk'],
  ['BARBELL RDL', '5rIqP63yWFg', ['أفخاذ خلفية', 'قلوتس'], ['hams'], ['glutes'], 3, '6-10', 'DB RDL', 'u14AwrUcwWw'],
  ['LEG PRESS', 'nDh_BlnLCGc', ['أفخاذ أمامية', 'قلوتس'], ['quads'], ['glutes'], 3, '10-15', 'DB BULGARIAN SPLIT SQUAT', 'w:SkNsa3eBwLA'],
  ['LYING LEG CURL', 'ANKSmhT0dTk', ['أفخاذ خلفية'], ['hams'], [], 3, '10-15', 'SLIDING LEG CURL', 'w:kkkTfzi2gj4'],
  ['STANDING CALF RAISES', '95itLfMBG40', ['بطات'], ['calves'], [], 3, '10-15', 'SINGLE LEG CALF RAISE', 'w:ORT4oJ_R8Qs'],
  ['CABLE CRUNCHES', 'dkGwcfo9zto', ['بطن'], ['abs'], [], 3, '10-15', 'CRUNCHES', 'eeJ_CYqSoT4']]},
 {'n': 3, 'cls': 'c', 'title': 'علوي B', 'rows': [
  ['MACHINE INCLINE CHEST PRESS', 'w:tiWPSwt8_zM', ['صدر علوي', 'أكتاف أمامية', 'تراي'], ['chest'], ['fdelt', 'triceps'], 3, '8-12', 'PUSH UP', 'w:IODxDxX7oi4'],
  ['ASSISTED PULL UP', 'WLzut1ZxxTY', ['لاتس', 'باي'], ['lats'], ['biceps'], 3, '6-12', 'DB CHEST SUPPORTED ROW', 'w:tZUYS7X50so'],
  ['MACHINE CHEST PRESS', 'relql3kwCi8', ['صدر', 'أكتاف أمامية', 'تراي'], ['chest'], ['fdelt', 'triceps'], 3, '8-12', 'FLAT DB PRESS', '1V3vpcaxRYQ'],
  ['CABLE FACE PULL', 'w:3pToT5_DUiY', ['كتف خلفي', 'ترابيس'], ['rdelt'], ['rhomb'], 3, '12-15', 'DB REVERSE FLY', 'w:d1QEddtoOq0'],
  ['MACHINE LATERAL RAISE', 'AydmHFgOn6U', ['كتف جانبي'], ['sdelt'], [], 3, '10-15', 'DB LATERAL RAISE', 'JIhbYYA1Q90'],
  ['CABLE CURL', 'w:2MUEL4nL6hA', ['باي'], ['biceps'], [], 3, '10-15', 'DB CURL', 'YgHnvJQkfhc']]},
 {'n': 4, 'cls': 'd', 'title': 'سفلي B', 'rows': [
  ['HIP THRUST', 'PqOnYf6Slkg', ['قلوتس', 'أفخاذ خلفية'], ['glutes'], ['hams'], 3, '8-12', 'DB HIP THRUST', 'w:29OfN4ztW_g'],
  ['LEG EXTENSION', 'w:ljO4jkwv8wQ', ['أفخاذ أمامية'], ['quads'], [], 3, '10-15', 'DB REVERSE LUNGE', 'w:RZKXLMxPF_I'],
  ['SEATED LEG CURL', 'w:Orxowest56U', ['أفخاذ خلفية'], ['hams'], [], 3, '10-15', 'DB SINGLE LEG RDL', 'w:lI8-igvsnVQ'],
  ['HIP ABDUCTION MACHINE', 'w:OjI5OpV6IWA', ['قلوتس جانبي'], ['gmed'], [], 3, '12-20', 'SIDE LYING HIP ABDUCTION', 'w:-rDiQXjeXO0'],
  ['LEG PRESS CALF RAISES', '1cvpm--Y-4I', ['بطات'], ['calves'], [], 3, '10-15', 'SINGLE LEG CALF RAISE', 'w:ORT4oJ_R8Qs'],
  ['HANGING LEG RAISES', '2n4UqRIJyk4', ['بطن'], ['abs'], [], 3, '10-15', 'LYING LEG RAISES', 'PpZxg66ftYc']]},
]
g4 = weekly(D4, [('صدر', ['chest']), ('ظهر (لاتس · رومبويد · كتف خلفي)', ['lats', 'rhomb', 'rdelt']),
                 ('أكتاف (أمامية · جانبية)', ['fdelt', 'sdelt']), ('باي', ['biceps']), ('تراي', ['triceps']),
                 ('أفخاذ أمامية', ['quads']), ('أفخاذ خلفية', ['hams']), ('قلوتس', ['glutes', 'gmed']),
                 ('بطات', ['calves']), ('بطن', ['abs'])])
p4_principles = page('مبادئ الجدول', 'مبادئ الجدول',
    chart_panel(g4, 20, (0, 6, 10, 15, 20), band=(6, 20), rng_label='النطاق: من 6 إلى 20 جولة أسبوعيًا',
                head=('مجموعة العضلات', 'جولات الأسبوع')),
    notes_panel('كيف بُني الجدول', [
        'كل عضلة تتمرن <b>مرتين بالأسبوع</b>: توزيع الجولات على أكثر من جلسة يعطي نمو أفضل من جمعها في يوم واحد.',
        'ما نتجاوز تقريبًا <b>10 جولات</b> للعضلة في نفس الجلسة، لأن الجولات الزايدة بعدها فايدتها قليلة.',
        'نطاق العدات اللي يبني العضل واسع (<b>5–30</b> عدة)، لذلك العدات <b>6–10</b> للتمارين المركبة و<b>10–20</b> لتمارين العزل.',
        'كل جولة تكون قريبة من الفشل العضلي: <b>RIR 1–3</b>. كل ما قربت من الفشل زاد النمو.',
        'العضلة المساعدة تنحسب <b>نص جولة</b> في الرسم (مثال: الباي في تمارين السحب).',
    ], refs=MENNO_REFS))
p4_week = page('جدولك الأسبوعي', 'جدولك الأسبوعي',
    week_panel('مثال لتوزيع الأسبوع', [
        ('السبت', [('a', 'اليوم 1 · علوي A')]), ('الأحد', [('', 'اليوم 2 · سفلي A')]), ('الاثنين', [('r', 'راحة')]),
        ('الثلاثاء', [('c', 'اليوم 3 · علوي B')]), ('الأربعاء', [('', 'اليوم 4 · سفلي B')]), ('الخميس', [('r', 'راحة')]),
        ('الجمعة', [('r', 'راحة')])]),
    notes_panel('النادي أو المنزل', [
        'العمود الأول هو <b>التمرين الأساسي بالنادي</b>، والعمود الأخير هو <b>البديل بالمنزل</b> لنفس العضلة وبنفس الجولات والعدات.',
        'تقدرون تخلطون: لو ما توفر جهاز بالنادي، استخدموا البديل.',
        'بالمنزل لو الأوزان خفيفة: زيدوا العدات لين <b>20–30</b> عدة بشرط تقربون من الفشل.',
    ], warm=WARM))
build('prog-4days.html', 'جدول تمرين 4 أيام — نادي ومنزل',
      cover('جدول تمرين<br><em>4 أيام</em>', 'التمرين الأساسي بالنادي · والبديل بالمنزل', [
          {'n': 1, 't': 'علوي A', 'p': 'صدر · ظهر · أكتاف · تراي', 'k': 6},
          {'n': 2, 't': 'سفلي A', 'p': 'أفخاذ · قلوتس · بطات · بطن', 'k': 6},
          {'n': 3, 't': 'علوي B', 'p': 'صدر · ظهر · أكتاف · باي', 'k': 6},
          {'n': 4, 't': 'سفلي B', 'p': 'قلوتس · أفخاذ خلفية · بطات · بطن', 'k': 6}]),
      D4, ('التمرين الأساسي · النادي', 'البديل · المنزل'),
      [p4_principles, p4_week, RIR_PAGE, EQUIP_PAGE, THANKS])

# =====================================================================
# 2) GLUTES
# =====================================================================
DG = [
 {'n': 1, 'cls': 'a', 'title': 'قلوتس A', 'sub': 'هيب ثرست · سكوات · هنج · أبدكشن', 'rows': [
  ['HIP THRUST', 'PqOnYf6Slkg', ['قلوتس', 'أفخاذ خلفية'], ['glutes'], ['hams'], 4, '8-12', 'DB HIP THRUST', 'w:29OfN4ztW_g'],
  ['SQUAT', 'PPmvh7gBTi0', ['قلوتس', 'أفخاذ أمامية'], ['glutes', 'quads'], [], 3, '6-10', 'DB GOBLET SQUAT', 'w:gCESNsDsbqk'],
  ['BARBELL RDL', '5rIqP63yWFg', ['أفخاذ خلفية', 'قلوتس'], ['hams'], ['glutes'], 3, '8-10', 'DB RDL', 'u14AwrUcwWw'],
  ['HIP ABDUCTION MACHINE', 'w:OjI5OpV6IWA', ['قلوتس جانبي'], ['gmed'], [], 3, '12-20', 'SIDE LYING HIP ABDUCTION', 'w:-rDiQXjeXO0']]},
 {'n': 2, 'cls': 'b', 'title': 'قلوتس B', 'sub': 'سبليت سكوات · باك اكستنشن · كيك باك', 'rows': [
  ['BULGARIAN SPLIT SQUAT', 'w:SkNsa3eBwLA', ['قلوتس', 'أفخاذ أمامية'], ['glutes', 'quads'], [], 3, '8-12', 'DB REVERSE LUNGE', 'w:RZKXLMxPF_I'],
  ['45° BACK EXTENSION', 'w:OMb1VFQK9Tk', ['قلوتس', 'أفخاذ خلفية', 'أسفل الظهر'], ['glutes'], ['hams', 'lowb'], 3, '10-15', 'DB SINGLE LEG RDL', 'w:lI8-igvsnVQ'],
  ['CABLE KICKBACK', 'w:l4zReIOfPCQ', ['قلوتس'], ['glutes'], [], 3, '12-15', 'QUADRUPED KICKBACK', 'w:GprFzvlHKmA'],
  ['CABLE HIP ABDUCTION', 'w:vSqhrbzZb7A', ['قلوتس جانبي'], ['gmed'], [], 3, '12-20', 'SIDE LYING HIP ABDUCTION', 'w:-rDiQXjeXO0']]},
 {'n': 3, 'cls': 'c', 'title': 'قلوتس C', 'sub': 'ليق برس · هيب ثرست · ليق كيرل', 'rows': [
  ['LEG PRESS', 'nDh_BlnLCGc', ['قلوتس', 'أفخاذ أمامية'], ['glutes', 'quads'], [], 3, '10-15', 'DB STEP UP', 'w:aKj-6hgiViA'],
  ['HIP THRUST', 'PqOnYf6Slkg', ['قلوتس', 'أفخاذ خلفية'], ['glutes'], ['hams'], 3, '10-15', 'GLUTE BRIDGE', 'w:L9KZfxT654Y'],
  ['SEATED LEG CURL', 'w:Orxowest56U', ['أفخاذ خلفية'], ['hams'], [], 3, '10-15', 'SLIDING LEG CURL', 'w:kkkTfzi2gj4'],
  ['HIP ABDUCTION MACHINE', 'w:OjI5OpV6IWA', ['قلوتس جانبي'], ['gmed'], [], 3, '15-20', 'SIDE LYING HIP ABDUCTION', 'w:-rDiQXjeXO0']]},
]
gg = weekly(DG, [('قلوتس', ['glutes']), ('قلوتس جانبي', ['gmed']), ('أفخاذ أمامية', ['quads']),
                 ('أفخاذ خلفية', ['hams'])])
pg_principles = page('مبادئ الجدول', 'مبادئ بناء القلوتس',
    chart_panel(gg, 25, (0, 5, 10, 15, 20, 25), head=('العضلة', 'جولات الأسبوع')),
    notes_panel('ليش هذي التمارين؟', [
        '<b>الهيب ثرست والسكوات</b> يبنون القلوتس بدرجة متقاربة، وغالبًا يحفّزونها بطريقة مختلفة، لذلك الجدول فيه الاثنين.',
        '<b>القلوتس الجانبية</b> (الميديس والمينيمس) ما تكبر كفاية من السكوات والهيب ثرست، وتحتاج <b>أبدكشن</b> مباشر، وهو موجود بكل يوم.',
        'تركيبة كل جلسة: نوع من <b>الهيب ثرست</b>، وتمرين للأفخاذ الأمامية والقلوتس، و<b>هنج</b> للخلفية والقلوتس، وأبدكشن أو كيك باك بالنهاية.',
        'التمارين اللي تمطّ العضلة (<b>RDL والسبليت سكوات</b>) تحتاج استشفاء أطول، لذلك كل واحد منها مرة وحدة بالأسبوع.',
        'القلوتس هي العضلة المستهدفة، لذلك جولاتها أعلى (حوالي <b>20–25</b> بالأسبوع) وما تتجاوز تقريبًا <b>10</b> جولات بالجلسة.',
    ], refs=('<b>المراجع:</b> Menno Henselmans — '
             '<a href="https://mennohenselmans.com/new-study-hip-thrust-and-back-squat-training-elicit-similar-gluteus-muscle-hypertrophy-and-transfer-similarly-to-the-deadlift/">Hip thrust vs back squat</a> · '
             '<a href="https://mennohenselmans.com/optimal-training-frequency-glutes-part-ii/">Optimal glute frequency</a> · '
             '<a href="https://mennohenselmans.com/maximum-productive-training-volume-per-session/">Volume per session</a>')))
pg_week = page('جدولك الأسبوعي', 'جدولك الأسبوعي',
    week_panel('مثال لتوزيع الأسبوع', [
        ('السبت', [('a', 'اليوم 1 · قلوتس A')]), ('الأحد', [('r', 'راحة أو جزء علوي')]),
        ('الاثنين', [('', 'اليوم 2 · قلوتس B')]), ('الثلاثاء', [('r', 'راحة أو جزء علوي')]),
        ('الأربعاء', [('c', 'اليوم 3 · قلوتس C')]), ('الخميس', [('r', 'راحة')]), ('الجمعة', [('r', 'راحة')])]),
    notes_panel('طريقة التنفيذ', [
        'السبليت سكوات والريفيرس لانج: <b>الجولات لكل رجل</b>.',
        'بالليق برس: حطّوا الرجول <b>أعلى المنصة</b> عشان يزيد شغل القلوتس.',
        'بالهيب ثرست: ثبات ثانية فوق مع عصر القلوتس، وبدون تقويس أسفل الظهر.',
    ], warm=WARM))
build('prog-glutes.html', 'جدول بناء القلوتس',
      cover('جدول<br><em>بناء القلوتس</em>', '3 أيام بالأسبوع · التمرين بالنادي والبديل بالمنزل', [
          {'n': 1, 't': 'قلوتس A', 'p': 'هيب ثرست · سكوات · RDL · أبدكشن', 'k': 4},
          {'n': 2, 't': 'قلوتس B', 'p': 'سبليت سكوات · باك اكستنشن · كيك باك', 'k': 4},
          {'n': 3, 't': 'قلوتس C', 'p': 'ليق برس · هيب ثرست · ليق كيرل', 'k': 4}]),
      DG, ('التمرين الأساسي · النادي', 'البديل · المنزل'),
      [pg_principles, pg_week, RIR_PAGE, THANKS], fem=True)

# =====================================================================
# 3) BACK PAIN (upper-back rounding + lower back)
# =====================================================================
DB = [
 {'n': 1, 'cls': 'a', 'lbl': 'يوميًا', 'title': 'روتين يومي', 'sub': '5–10 دقائق · كل يوم', 'sec': 'الروتين اليومي', 'rows': [
  ['CAT CAMEL', 'w:UScu7P0yua4', ['أسفل الظهر', 'أعلى الظهر'], ['lowb'], ['rhomb'], 1, '8-10', 'FOAM ROLLER THORACIC EXT.', 'w:SQF-0s1CckA'],
  ['MCGILL CURL UP', 'w:I_drRVYlHbc', ['بطن'], ['abs'], [], '5-3-1', '10 ثوانٍ', 'DEAD BUG', 'w:GbSC02oU3To'],
  ['SIDE PLANK', 'w:44ND4bOB-T0', ['بطن جانبي', 'قلوتس جانبي'], ['obl'], ['gmed'], '5-3-1', '10 ثوانٍ', 'SIDE PLANK (KNEES)', 'w:CofbfhHCWCY'],
  ['BIRD DOG', 'w:vM_4Y_-N0ds', ['أسفل الظهر', 'قلوتس'], ['lowb'], ['glutes'], '5-3-1', '10 ثوانٍ', 'BIRD DOG REGRESSIONS', 'w:hjQB8wf_dRc']]},
 {'n': 'A', 'cls': 'b', 'lbl': 'تقوية', 'title': 'تقوية A', 'sub': 'أعلى الظهر · القلوتس', 'sec': 'تقوية A', 'rows': [
  ['CHEST SUPPORTED ROW', 'w:FU6YQawma2Q', ['رومبويد', 'لاتس', 'كتف خلفي'], ['rhomb'], ['lats', 'rdelt'], 3, '12-15', 'DB CHEST SUPPORTED ROW', 'w:tZUYS7X50so'],
  ['CABLE FACE PULL', 'w:3pToT5_DUiY', ['كتف خلفي', 'ترابيس'], ['rdelt'], ['rhomb'], 3, '12-20', 'DB REVERSE FLY', 'w:d1QEddtoOq0'],
  ['LATS PULLDOWN', 'w:hnSqbBk15tw', ['لاتس', 'باي'], ['lats'], ['biceps'], 3, '12-15', 'DB PULLOVER', 'w:jQjWlIwG4sI'],
  ['INCLINE Y RAISE', 'w:lXp16YozXgk', ['ترابيس سفلي', 'كتف خلفي'], ['rhomb'], ['rdelt'], 2, '12-15', 'PRONE Y T W', 'w:QdGTI4Lshg4'],
  ['HIP THRUST', 'PqOnYf6Slkg', ['قلوتس', 'أفخاذ خلفية'], ['glutes'], ['hams'], 3, '12-15', 'GLUTE BRIDGE', 'w:L9KZfxT654Y']]},
 {'n': 'B', 'cls': 'c', 'lbl': 'تقوية', 'title': 'تقوية B', 'sub': 'الظهر كامل · الرجول', 'sec': 'تقوية B', 'rows': [
  ['SEATED ROW', 'w:YKAeU55CkVk', ['لاتس', 'رومبويد', 'باي', 'كتف خلفي'], ['lats', 'rhomb'], ['biceps', 'rdelt'], 3, '12-15', 'ONE ARM DB ROW', 'KaCcBqhiXtc'],
  ['45° BACK EXTENSION', 'w:OMb1VFQK9Tk', ['أسفل الظهر', 'قلوتس', 'أفخاذ خلفية'], ['lowb'], ['glutes', 'hams'], 2, '10-15', 'PRONE BACK EXTENSION', 'w:cIYeKqLqVVs'],
  ['DB RDL', 'u14AwrUcwWw', ['أفخاذ خلفية', 'قلوتس', 'أسفل الظهر'], ['hams'], ['glutes', 'lowb'], 2, '12-15', 'GLUTE BRIDGE', 'w:L9KZfxT654Y'],
  ['REVERSE PEC DECK', 'w:dC7jhEk-29A', ['كتف خلفي', 'ترابيس'], ['rdelt'], ['rhomb'], 3, '12-20', 'DB REVERSE FLY', 'w:d1QEddtoOq0'],
  ['GOBLET BOX SQUAT', 'w:mIJub2k6YNg', ['أفخاذ أمامية', 'قلوتس'], ['quads'], ['glutes'], 3, '10-15', 'BODYWEIGHT BOX SQUAT', 'w:7LpLZOdz68A']]},
]
pb_safety = page('قبل ما تبدأ', 'قبل ما تبدأ',
    f'''<div class="panel" style="right:56px;width:600px">
  <div class="ph"><span>راجعوا طبيب أو أخصائي علاج طبيعي أولًا إذا:</span></div>
  <div class="alert" style="margin-top:18px"><h4>علامات تحتاج تقييم قبل التمرين</h4><ul>
   <li>الألم بدأ بعد حادث أو سقوط.</li>
   <li>ألم ينزل للرجل مع خدر أو ضعف.</li>
   <li>ألم شديد بالليل، أو مع حرارة أو نزول وزن بدون سبب.</li>
   <li>صعوبة في التحكم بالبول أو الإخراج.</li>
   <li>ألم يزيد باستمرار رغم الراحة.</li></ul>
   <p>هذا الجدول للألم العام في الظهر، وما يغني عن التشخيص.</p></div>
 </div>''',
    notes_panel('مبادئ الجدول', [
        'القوام نفسه (تحدّب أعلى الظهر أو ميلان الحوض) <b>ما له علاقة ثابتة بألم الظهر</b> في الدراسات. هدف الجدول تقوية الظهر وزيادة تحمّله، مو "تعديل القوام".',
        'الأهم هو <b>اللي ما تسوونه</b>: ابتعدوا عن التمارين والحركات اللي تثير الألم، حتى بحياتكم اليومية.',
        'ابدأوا بتمارين <b>ما تسبب ألم</b>، ابنوا الثقة، ثم زيدوا الشدة بالتدريج.',
        '<b>أوزان أخف وعدات أعلى</b> (12–20)، لأنها غالبًا أقل ألم، ومع ذلك تبني العضل.',
        '<b>لا تتمرنون وأنتم تحسون بالألم</b>: هذا اللي يحوّل مشكلة بسيطة لإصابة تطول أشهر.',
    ], refs=('<b>المراجع:</b> Menno Henselmans — '
             '<a href="https://mennohenselmans.com/posture-myths/">3 Plausibly potent myths about your posture</a> · '
             '<a href="https://mennohenselmans.com/injury-rehab-interview-ruscio/">Injury rehab: a no BS approach</a> · '
             '<a href="https://mennohenselmans.com/7-essential-injury-management-tips-for-lifters/">7 Injury management tips</a>')),
    )
# the notes panel sits left of a 600px panel
pb_safety = pb_safety.replace('<div class="panel notes">', '<div class="panel notes" style="right:676px">')
pb_how = page('طريقة التنفيذ', 'طريقة التنفيذ',
    week_panel('مثال لتوزيع الأسبوع', [
        ('السبت', [('o', 'روتين يومي'), ('', 'تقوية A')]), ('الأحد', [('o', 'روتين يومي')]),
        ('الاثنين', [('o', 'روتين يومي'), ('c', 'تقوية B')]), ('الثلاثاء', [('o', 'روتين يومي')]),
        ('الأربعاء', [('o', 'روتين يومي'), ('', 'تقوية A')]), ('الخميس', [('o', 'روتين يومي')]),
        ('الجمعة', [('o', 'روتين يومي')])], side='right:56px;width:600px'),
    notes_panel('كيف تتقدّمون', [
        '<b>تمارين McGill الثلاثة</b> (Curl up · Side plank · Bird dog) كل يوم. <b>5-3-1</b> يعني: الجولة الأولى 5 تكرارات، الثانية 3، الثالثة 1، وكل تكرار <b>ثبات 10 ثوانٍ</b>.',
        'تقوية A و B بالتناوب <b>3 أيام بالأسبوع</b> (الأسبوع اللي بعده: B ثم A ثم B).',
        'اتركوا <b>2–3 عدات</b> قبل الفشل (RIR 2–3) في تمارين التقوية.',
        'لما تخلصون كل الجولات <b>بدون ألم</b>: زيدوا العدات أول، ثم الوزن.',
        'إذا زاد الألم أثناء التمرين أو باليوم الثاني: خففوا الوزن أو المدى، أو استخدموا البديل الأسهل.',
    ]).replace('<div class="panel notes">', '<div class="panel notes" style="right:676px">'))
build('prog-back.html', 'جدول تخفيف ألم الظهر',
      cover('جدول تخفيف<br><em>ألم الظهر</em>', 'أعلى الظهر (التحدّب) وأسفل الظهر · نادي أو منزل', [
          {'n': '1', 'lbl': 'يوميًا', 't': 'روتين يومي', 'p': '5–10 دقائق · حركة وثبات', 'k': 4},
          {'n': 'A', 'lbl': 'تقوية', 't': 'تقوية A', 'p': 'أعلى الظهر · القلوتس', 'k': 5},
          {'n': 'B', 'lbl': 'تقوية', 't': 'تقوية B', 'p': 'الظهر كامل · الرجول', 'k': 5}]),
      DB, ('التمرين', 'البديل · المنزل / أسهل'),
      [pb_safety, pb_how, THANKS])

# =====================================================================
# 4) FLEXIBILITY (hips, back, shoulders, legs)
# =====================================================================
FLEX_CSS = """
.flex .rep.t{font-size:15px;line-height:1.4;padding:5px 8px;text-align:center;white-space:nowrap}
.flex .num.t{font-size:22px}
"""
EXTRA_CSS_FLEX = FLEX_CSS
# (name, video, muscles, pri, sec, sets, reps text, alt name, alt video, secs/round, sides)
FX = [
 # day 1 - hips
 ('HALF KNEELING HIP FLEXOR STRETCH', 'w:gqoPYLUgP48', ['مثنيات الورك', 'أفخاذ أمامية'], ['hflex'], [], 2, '45 ثانية<br>لكل جهة', 'STANDING HIP FLEXOR STRETCH', 'w:ljCDEb_MIto', 45, 2),
 ('90/90 HIP SWITCH', 'w:t4Zz6-aG8Iw', ['دوّارات الورك', 'قلوتس', 'فخذ داخلي'], ['glutes'], ['add'], 2, '8 تبديلات', 'SEATED HIP ROTATION', 'w:WLMSzXQTVrA', 30, 1),
 ('PIGEON STRETCH', 'w:e99cdZ_Nl3I', ['قلوتس', 'دوّارات الورك'], ['glutes'], [], 2, '45 ثانية<br>لكل جهة', 'LYING FIGURE-4 STRETCH', 'w:nj1-GzbAauI', 45, 2),
 ('FROG STRETCH', 'w:orMZYFWo9P0', ['فخذ داخلي', 'الحوض'], ['add'], [], 3, '50 ثانية', 'BUTTERFLY STRETCH', 'w:aaQVOFRDvRo', 50, 1),
 ('DEEP SQUAT HOLD (GOBLET)', 'w:ShvTpCsgTiw', ['قلوتس', 'حوض', 'كاحل وبطات'], ['glutes'], ['add', 'calves'], 2, '40 ثانية', 'SUPPORTED DEEP SQUAT HOLD', 'w:uQbUORRwzqk', 40, 1),
 ('COSSACK SQUAT', 'w:nLNqEQ4B6XI', ['فخذ داخلي', 'قلوتس'], ['add'], ['glutes'], 2, '6-8 تكرارات<br>لكل جهة', 'SIDE LUNGE ADDUCTOR STRETCH', 'w:lmVhur0mHkY', 30, 2),
 # day 2 - back & shoulders
 ('CAT CAMEL', 'w:UScu7P0yua4', ['أسفل الظهر', 'أعلى الظهر'], ['lowb'], ['rhomb'], 2, '8-10 تكرارات', 'SEATED CAT COW', 'w:ab40Gphamag', 45, 1),
 ('THORACIC EXTENSION (FOAM ROLLER)', 'w:SQF-0s1CckA', ['أعلى الظهر', 'ترابيس'], ['rhomb'], ['lats'], 2, '40 ثانية', 'THORACIC EXTENSION OVER CHAIR', 'w:SvDHk_ar8FA', 40, 1),
 ('THREAD THE NEEDLE', 'w:blBC6222kuU', ['أعلى الظهر', 'كتف خلفي'], ['rhomb'], ['rdelt'], 2, '8 تكرارات<br>لكل جهة', 'SEATED THORACIC ROTATION', 'w:QwsdhRTdqqs', 30, 2),
 ("CHILD'S POSE WITH SIDE REACH", 'w:uGWsHEXSg4U', ['لاتس', 'أسفل الظهر'], ['lats'], ['lowb'], 2, '40 ثانية<br>لكل جهة', 'STANDING WALL LAT STRETCH', 'w:JUglskfkdgQ', 40, 2),
 ('DOORWAY PEC STRETCH', 'w:CEQMx4zFwYs', ['صدر', 'أكتاف أمامية'], ['chest'], ['fdelt'], 3, '45 ثانية<br>لكل جهة', 'WALL PEC STRETCH', 'w:40BBXdyJdak', 45, 2),
 ('WALL SLIDES', 'w:tWDGEyMWv10', ['ترابيس سفلي', 'كتف'], ['rhomb'], ['sdelt'], 2, '8-10 تكرارات', 'ARM CIRCLES', 'w:ndmSvkEdNQQ', 30, 1),
 # day 3 - full
 ("WORLD'S GREATEST STRETCH", 'w:-CiWQ2IvY34', ['مثنيات الورك', 'أفخاذ خلفية', 'أعلى الظهر'], ['hflex'], ['hams', 'rhomb'], 2, '5 تكرارات<br>لكل جهة', 'LUNGE WITH ROTATION', 'w:Mwkh9MWbF04', 30, 2),
 ('HAMSTRING STRETCH (STRAP)', 'w:Il1L75v6gq0', ['أفخاذ خلفية'], ['hams'], [], 3, '45 ثانية<br>لكل جهة', 'SEATED HAMSTRING STRETCH', 'w:aJvfeuu71gw', 45, 2),
 ('WALL CALF STRETCH', 'w:mtVqe4CR_60', ['بطات'], ['calves'], [], 3, '45 ثانية<br>لكل جهة', 'KNEE TO WALL ANKLE MOBILITY', 'w:ElrpduJn92Y', 45, 2),
 ('COUCH STRETCH', 'w:d9pOjXCKGN8', ['مثنيات الورك', 'أفخاذ أمامية'], ['hflex'], [], 2, '45 ثانية<br>لكل جهة', 'STANDING QUAD STRETCH', 'w:aNXGOpP37CY', 45, 2),
 ('SUPINE SPINAL TWIST', 'w:mNdJti7ZwKI', ['جانبي البطن', 'أسفل الظهر'], ['obl'], ['lowb'], 2, '45 ثانية<br>لكل جهة', 'SEATED SPINAL TWIST', 'w:6URMDkf2Uxk', 45, 2),
 ('OPEN BOOK', 'w:peeW19ofFUg', ['أعلى الظهر', 'صدر'], ['rhomb'], ['chest'], 2, '8 تكرارات<br>لكل جهة', 'SEATED THORACIC ROTATION', 'w:QwsdhRTdqqs', 30, 2),
]
def fx_rows(a, b):
    return [list(r[:9]) for r in FX[a:b]]
DF = [
 {'n': 1, 'cls': 'a', 'title': 'الحوض', 'sub': 'مثنيات الورك · الأرداف · الفخذ الداخلي', 'rows': fx_rows(0, 6)},
 {'n': 2, 'cls': 'b', 'title': 'الظهر', 'sub': 'أسفل الظهر · أعلى الظهر · الصدر · الأكتاف', 'rows': fx_rows(6, 12)},
 {'n': 3, 'cls': 'c', 'title': 'شامل', 'sub': 'الورك · الأرجل · الظهر · الصدر', 'rows': fx_rows(12, 18)},
]
def fx_minutes(keys):
    tot = 0.0
    for r in FX:
        m = r[5] * r[9] * r[10] / 60
        if any(k in r[3] for k in keys):
            tot += m
        elif any(k in r[4] for k in keys):
            tot += m / 2
    return tot
FX_AREAS = [('مثنيات الورك', ['hflex']), ('قلوتس ودوّارات الورك', ['glutes']), ('الفخذ الداخلي', ['add']),
            ('الأفخاذ الخلفية', ['hams']), ('البطات', ['calves']), ('أسفل الظهر والجذع', ['lowb', 'obl']),
            ('أعلى الظهر', ['rhomb', 'lats']), ('الصدر والأكتاف', ['chest', 'fdelt'])]
fx_chart = [(n, round(fx_minutes(k), 1)) for n, k in FX_AREAS]
print('flex minutes/week:', fx_chart)
day_min = [round(sum(r[5] * r[9] * r[10] / 60 for r in FX[a:b])) for a, b in ((0, 6), (6, 12), (12, 18))]
print('flex minutes/day:', day_min)

FX_REFS = ('<b>المراجع:</b> '
           '<a href="https://pubmed.ncbi.nlm.nih.gov/29506306/">Thomas 2018 — Stretching typology & duration vs ROM</a> · '
           '<a href="https://estudogeral.uc.pt/handle/10316/104612">Afonso 2021 — Strength training vs stretching for ROM</a> · '
           '<a href="https://sportsmedicine-open.springeropen.com/articles/10.1186/s40798-024-00772-y">Optimising the dose of static stretching</a>')
pf_principles = page('مبادئ الجدول', 'مبادئ زيادة المرونة',
    chart_panel(fx_chart, 12, (0, 5, 10), band=(5, 10), rng_label='المنصوح: 5–10 دقائق أسبوعيًا',
                head=('المنطقة', 'دقائق التمدد أسبوعيًا')),
    notes_panel('ليش هالتوزيع؟', [
        'الأهم هو <b>مجموع وقت التمدد بالأسبوع</b> لكل منطقة: حوالي <b style="white-space:nowrap">5–10 دقائق</b> تكفي لزيادة المدى، وما يضيف الزيادة الكثيرة بعدها فايدة تُذكر.',
        'كل جولة تمدد حوالي <b>45 ثانية</b> لمدى مريح: شد خفيف إلى متوسط، وليس ألمًا.',
        'الحوض وأعلى الظهر يتمرنون <b>مرتين بالأسبوع</b>: الحوض باليوم 1 و3، وأعلى الظهر باليوم 2 و3.',
        'تمارين القوة بمدى حركة كامل (مثل السكوات العميق) <b>تزيد المرونة بدرجة مقاربة للتمدد</b> حسب مراجعة منهجية لدراسات مقارنة، فلا تتركون تمارين القوة.',
        'أرقام الرسم <b>تقديرية</b>: التمرين الأساسي للمنطقة يُحسب كاملًا، والمساعد نصفه، وتمارين الجهتين تُحسب لكلا الجهتين.',
    ], refs=FX_REFS))
pf_how = page('طريقة التنفيذ', 'طريقة التنفيذ',
    week_panel('مثال لتوزيع الأسبوع', [
        ('السبت', [('a', 'اليوم 1 · الحوض')]), ('الأحد', [('r', 'راحة')]),
        ('الاثنين', [('', 'اليوم 2 · الظهر')]), ('الثلاثاء', [('r', 'راحة')]),
        ('الأربعاء', [('c', 'اليوم 3 · شامل')]), ('الخميس', [('r', 'راحة')]), ('الجمعة', [('r', 'راحة')])],
        side='right:56px;width:600px'),
    notes_panel('كيف تنفذون الجدول', [
        f'مدة كل يوم تقريبًا: <b>{day_min[0]} · {day_min[1]} · {day_min[2]} دقيقة</b> بدون فترات الراحة بين الجولات.',
        'التمارين المكتوب فيها <b>«لكل جهة»</b>: كرروا الجولة على الجهة الثانية بنفس المدة.',
        'الأفضل بعد التمرين، أو بيوم مستقل. وقبل التمدد سخّنوا <b style="white-space:nowrap">3–5 دقائق</b> (مشي أو حركة خفيفة).',
        'العمود الأول هو <b>التمرين الأساسي</b>، والأخير <b>بديل أسهل</b> لنفس المنطقة إذا كان الأساسي صعبًا.',
        'تتقدمون بالتدريج: أضيفوا جولة، أو زيدوا المدة، أو انتقلوا من البديل الأسهل إلى الأساسي.',
    ]).replace('<div class="panel notes">', '<div class="panel notes" style="right:676px">'))
pf_safety = page('قبل ما تبدأ', 'قبل ما تبدأ',
    """<div class="panel" style="right:56px;width:600px">
  <div class="ph"><span>وقّفوا التمرين واستشيروا مختص إذا:</span></div>
  <div class="alert" style="margin-top:18px"><h4>علامات تحتاج انتباه</h4><ul>
   <li>ألم حاد، أو وخز وتنميل، أثناء التمدد.</li>
   <li>ألم يستمر أكثر من يوم بعد التمرين.</li>
   <li>ألم مفاجئ بالظهر بعد حادث، أو ألم ينزل للرجل مع ضعف.</li>
   <li>إصابة أو عملية سابقة بالحوض أو الركبة أو الكتف، أو انزلاق غضروفي: راجعوا الطبيب أو أخصائي العلاج الطبيعي قبل البدء.</li></ul>
   <p>هذا الجدول للمرونة العامة، وما يغني عن التشخيص.</p></div>
 </div>""",
    notes_panel('ملاحظات مهمة', [
        'التمدد يكون عند <b>حد الشد المريح</b>، وليس عند أقصى ما تتحملون.',
        'إذا عندكم ألم بالظهر: استبدلوا <b>اللف الأرضي (Supine spinal twist)</b> بالبديل الجالس، أو استخدموا جدول تخفيف ألم الظهر.',
        'المرونة تحتاج <b>استمرارية</b>: 3 جلسات بالأسبوع لمدة 6–8 أسابيع، ثم قيّموا التقدم.',
    ]).replace('<div class="panel notes">', '<div class="panel notes" style="right:676px">'))
build('prog-flex.html', 'جدول زيادة المرونة',
      cover('جدول زيادة<br><em>المرونة</em>', 'الحوض · الظهر · الأكتاف · الأرجل — من المنزل', [
          {'n': 1, 't': 'الحوض', 'p': 'مثنيات · قلوتس · فخذ داخلي', 'k': 6},
          {'n': 2, 't': 'الظهر', 'p': 'أسفل · أعلى · صدر · أكتاف', 'k': 6},
          {'n': 3, 't': 'شامل', 'p': 'ورك · أرجل · ظهر · صدر', 'k': 6}]),
      DF, ('التمرين الأساسي', 'البديل · أسهل'),
      [pf_principles, pf_how, pf_safety, THANKS], body_cls='flex')

# =====================================================================
# PORTRAIT (phone-first) builder — one vertical card per exercise
# =====================================================================
PORTRAIT_H = 2520
PORTRAIT_CSS = """
@page{size:1080px 2520px;margin:0}
.portrait .page{width:1080px;height:2520px}
.portrait .grid::before{background-size:72px 72px;mask-image:radial-gradient(85% 55% at 50% 35%,#000,transparent)}
.portrait .pager{left:48px;right:48px;bottom:46px;height:48px;gap:24px}
.portrait .pager .sec{font-size:24px}
.portrait .pager .num{font-size:28px}
.portrait .pager .bar i{height:11px}
/* cover */
.portrait .cover .logo{top:84px;right:64px;height:104px}
.portrait .cover .chip{top:300px;right:64px;font-size:28px;padding:12px 30px}
.portrait .cover .chip i{width:34px;height:13px}
.portrait .cover h1{top:390px;right:60px;font-size:170px;line-height:1.1}
.portrait .cover .rule{top:850px;right:64px;width:220px;height:9px}
.portrait .cover .lead{top:905px;right:64px;left:64px;max-width:none;font-size:36px}
.portrait .cover .days{left:64px;right:64px;width:auto;top:1130px;gap:30px}
.portrait .cover .day{padding:36px 44px;border-radius:34px;gap:34px}
.portrait .cover .day .n{width:130px;height:130px;border-radius:30px;font-size:64px}
.portrait .cover .day .n small{font-size:24px}
.portrait .cover .day h3{font-size:64px}
.portrait .cover .day p{font-size:30px;margin-top:10px}
.portrait .cover .day .cnt{font-size:24px}
.portrait .cover .day .cnt b{font-size:62px}
.portrait .cover .sign{bottom:150px;right:64px;font-size:30px}
.portrait .cover .sign b{font-size:32px}
/* day pages */
.portrait .dp .top{top:64px;right:48px;left:48px;height:150px;gap:28px}
.portrait .dp .badge{width:130px;height:130px;border-radius:30px;font-size:62px}
.portrait .dp .badge small{font-size:24px}
.portrait .dp h2{font-size:88px}
.portrait .dp .top h2 small{font-size:26px;margin-top:8px}
.portrait .dp .logo{height:70px;margin-right:auto}
.pd-hint{position:absolute;top:236px;right:48px;left:48px;display:flex;justify-content:space-between;align-items:center;gap:20px;font:600 26px "IBM Plex Sans Arabic";color:var(--muted);z-index:2}
.pd-hint>span{display:flex;align-items:center;gap:12px}
.pd-hint .lg{font-size:24px;gap:22px}
.pd-hint .lg i{width:20px;height:20px}
.pd-cards{position:absolute;top:300px;left:48px;right:48px;bottom:128px;display:flex;flex-direction:column;gap:18px;z-index:2}
.card{flex:1;min-height:0;background:#fff;border:2px solid var(--line);border-right:12px solid var(--cyan);border-radius:30px;box-shadow:0 12px 34px #07142a12;padding:16px 28px 16px 26px;display:flex;flex-direction:column;justify-content:space-between;gap:8px}
.pd-cards.b .card{border-right-color:var(--navy)}
.pd-cards.c .card{border-right-color:var(--ink)}
.c-top{display:flex;align-items:center;gap:20px}
.c-num{flex:none;width:60px;height:60px;border-radius:18px;background:var(--navy);color:#fff;font:800 32px/60px "Readex Pro";text-align:center}
.c-name{display:flex;align-items:center;gap:14px;direction:ltr;text-align:left}
.c-name b{font:700 33px/1.15 "Readex Pro";color:var(--ink)}
.c-mid{display:flex;align-items:center;gap:22px;flex:1;min-height:0}
.c-info{flex:1;display:flex;flex-direction:column;gap:9px}
.c-info .mrow{gap:12px}
.c-info .mrow i{width:16px;height:16px;border-radius:5px}
.c-info .mrow.p b{font:800 36px/1.2 Cairo}
.c-info .mrow.s span{font:600 27px "IBM Plex Sans Arabic"}
.c-chips{display:flex;gap:12px;margin-top:4px;flex-wrap:wrap}
.c2{display:flex;align-items:baseline;gap:10px;background:var(--cyan-soft);border-radius:16px;padding:8px 18px}
.c2 small{font:600 24px "IBM Plex Sans Arabic";color:var(--muted)}
.c2 b{font:800 32px/1.2 "Readex Pro";color:var(--navy)}
.c-fig{flex:none;display:flex;gap:4px;align-items:center}
.c-fig svg{width:150px;height:172px}
.c-alt{display:flex;align-items:center;gap:14px;background:var(--paper);border:1.5px solid var(--line);border-radius:18px;padding:8px 18px;direction:ltr}
.c-alt small{font:600 24px "IBM Plex Sans Arabic";color:var(--muted);direction:rtl}
.c-alt b{font:600 28px "Readex Pro";color:#33445c}
/* other pages: stacked panels, zoomed for phone reading */
.portrait .ip{display:flex;flex-direction:column;gap:34px;padding:270px 48px 150px}
.portrait .ip .top{top:64px;right:48px;left:48px;height:150px;gap:28px}
.portrait .ip .ico{width:112px;height:112px;border-radius:26px}
.portrait .ip .ico svg{width:64px;height:64px}
.portrait .ip h2{font-size:72px}
.portrait .ip .logo{height:62px}
.portrait .ip .panel{position:relative!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;width:auto!important;zoom:var(--z,1.5);flex:none}
.portrait .ip .notes{flex:1}
.portrait .ip .refs{position:relative;left:auto;right:auto;bottom:auto;padding:0 24px 16px;margin-top:6px}
.portrait .ip .srow .mg{font-size:16px}
.portrait .ip .scale .ax span{font-size:15px}
.portrait .ip .scale .ax .rng{font-size:15px;top:24px}
.portrait .ip .scale{height:64px}
/* thanks */
.portrait .ty .logo{top:84px;left:64px;height:104px}
.portrait .ty .msg{right:64px;left:64px;width:auto;top:330px}
.portrait .ty .msg .chip{font-size:28px;padding:10px 28px}
.portrait .ty h2{font-size:230px;margin:26px 0 8px}
.portrait .ty .rule{width:200px;height:9px;margin:10px 0 44px}
.portrait .ty .msg p{font-size:40px;line-height:1.7}
.portrait .ty .sig b{font-size:48px}
.portrait .ty .contact{left:64px;right:64px;width:auto;top:1380px;gap:26px}
.portrait .ty .contact h4{font-size:32px}
.portrait .cc{padding:30px 34px;gap:28px;border-radius:30px}
.portrait .cc .ic{width:100px;height:100px;border-radius:26px}
.portrait .cc .ic svg{width:54px;height:54px}
.portrait .cc div small{font-size:28px}
.portrait .cc div b{font-size:34px}
.portrait .cc .go{width:64px;height:64px}
.portrait .credit{left:64px;bottom:120px;font-size:20px}
.pd-cards.d .card{border-right-color:var(--navy2)}
.pd-cards.five .c-name b{font-size:36px}
.pd-cards.five .c-info .mrow.p b{font-size:40px}
.pd-cards.five .c-info .mrow.s span{font-size:30px}
.pd-cards.five .c2 b{font-size:35px}.pd-cards.five .c2 small{font-size:26px}
.pd-cards.five .c-fig svg{width:170px;height:206px}
.pd-cards.five .c-alt b{font-size:30px}
.pd-cards.few .c-name b{font-size:42px}
.pd-cards.few .c-num{width:74px;height:74px;font-size:40px;line-height:74px;border-radius:22px}
.pd-cards.few .c-name svg{width:60px;height:60px}
.pd-cards.few .c-info .mrow.p b{font-size:48px}
.pd-cards.few .c-info .mrow.s span{font-size:34px}
.pd-cards.few .c-info .mrow i{width:20px;height:20px}
.pd-cards.few .c2 b{font-size:40px}.pd-cards.few .c2 small{font-size:30px}
.pd-cards.few .c-fig svg{width:210px;height:270px}
.pd-cards.few .c-alt{padding:14px 22px}.pd-cards.few .c-alt b{font-size:34px}.pd-cards.few .c-alt small{font-size:28px}

.portrait .cover .lead:empty{display:none}
/* RIR / progression page */
.portrait .ip .prog,.portrait .ip .rirp{flex:1 1 0;min-height:0}
.portrait .ip .fs b{font-size:18px}
.portrait .ip .fs small{font-size:13px}
/* home equipment page */
.portrait .eq .grid3{position:absolute;top:270px;left:48px;right:48px;bottom:150px;grid-template-columns:1fr;grid-template-rows:1.35fr .8fr 1fr;gap:28px}
.portrait .eq .equip{grid-row:auto}
.portrait .eq .ecard{zoom:1.38}
"""
PORTRAIT_DAYS_JS = r"""
// ---- portrait day pages: one card per exercise
const PLAY2=s=>'<svg width="'+s+'" height="'+s+'" viewBox="0 0 34 34"><circle cx="17" cy="17" r="16" fill="#e4f6fc" stroke="#4cc5ed" stroke-width="1.5"/><path d="M14 11.5v11l9-5.5z" fill="#284da0"/></svg>';
const vurl=id=>id.startsWith('w:')?'https://www.youtube.com/watch?v='+id.slice(2):'https://www.youtube.com/shorts/'+id;
let html='';
DAYS.forEach(d=>{
  html+='<section class="page light grid dp" data-sec="'+(d.sec||('اليوم '+d.n+' · '+d.title))+'">'
   +'<i class="slash" style="left:-40px;bottom:-40px;width:110px;height:230px;opacity:.25"></i>'
   +'<div class="top"><div class="badge '+d.cls+'"><small>'+(d.lbl||'اليوم')+'</small>'+d.n+'</div><h2'+(d.title.length>8?' style="font-size:70px"':'')+'>'+d.title+(d.sub?'<small>'+d.sub+'</small>':'')+'</h2><img class="logo" src="../brand/logo-color-hd.png" alt="Nav Coaching"></div>'
   +'<div class="pd-hint"><span>'+PLAY2(36)+'اضغط على اسم التمرين لمشاهدة الشرح</span><span class="lg"><span><i></i>عضلة أساسية</span><span><i class="s"></i>عضلة مساعدة</span></span></div>'
   +'<div class="pd-cards '+d.cls+(d.rows.length<=4?' few':d.rows.length==5?' five':'')+'">';
  d.rows.forEach((r,i)=>{const [name,id,mus,pri,sec,sets,reps,alt,altId]=r;
    html+='<div class="card">'
     +'<div class="c-top"><span class="c-num">'+(i+1)+'</span><a class="c-name" href="'+vurl(id)+'">'+PLAY2(48)+'<b>'+name+'</b></a></div>'
     +'<div class="c-mid"><div class="c-info">'
     +'<div class="mrow p"><i></i><b>'+mus[0]+'</b></div>'+(mus.length>1?'<div class="mrow s"><i></i><span>'+mus.slice(1).join('<em>·</em>')+'</span></div>':'')
     +'<div class="c-chips"><span class="c2"><small>جولات</small><b>'+sets+'</b></span><span class="c2"><small>'+(d.rl||'المطلوب')+'</small><b>'+reps.replace('<br>',' ')+'</b></span></div></div>'
     +'<div class="c-fig">'+body('f',pri,sec)+body('b',pri,sec)+'</div></div>'
     +'<a class="c-alt" href="'+vurl(altId)+'">'+PLAY2(34)+'<small>'+(d.al||'بديل أسهل')+'</small><b>'+alt+'</b></a></div>';});
  html+='</div></section>';
});
document.getElementById('dayPages').outerHTML=html;
// ---- pager on every page
const TOTAL=document.querySelectorAll('.page').length;
document.querySelectorAll('.page').forEach((pg,i)=>{const n=i+1;
  let bar='';for(let k=1;k<=TOTAL;k++)bar+='<i class="'+(k<n?'done':k===n?'cur':'')+'"></i>';
  pg.insertAdjacentHTML('beforeend','<footer class="pager"><span class="sec"><b>'+(pg.dataset.sec||'')+'</b></span><div class="bar">'+bar+'</div><span class="num">'+String(n).padStart(2,'0')+' <span>/ '+String(TOTAL).padStart(2,'0')+'</span></span></footer>');});
</script>
"""

def build_portrait(fname, title, cover_html, days, pages_after, body_cls='portrait', fem=False):
    head_js = SCRIPT_T[:SCRIPT_T.index('// ---- data (content kept')]
    head_js = head_js.replace('const TOTAL=7;\n', '')
    head_js = head_js.replace("lats:['UPPER_BACK'],rhomb:['TRAPEZIUS'],",
        "lats:['UPPER_BACK'],rhomb:['TRAPEZIUS'],gmed:['GLUTEAL'],lowb:['LOWER_BACK'],obl:['OBLIQUES'],hflex:['QUADRICEPS'],add:['ABDUCTORS','ABDUCTOR'],")
    head_js = head_js.replace("LOW=['quads','glutes','hams','calves'];",
        "LOW=['quads','glutes','hams','calves','gmed','hflex','add'],MID=['abs','obl','lowb'];")
    head_js = head_js.replace("(all.length===1&&all[0]==='abs')?'mid'", "all.every(m=>MID.includes(m))?'mid'")
    assert "hflex" in head_js and "MID.includes" in head_js
    script = head_js + '// ---- data\nconst DAYS=' + json.dumps(days, ensure_ascii=False) + ';\n' + PORTRAIT_DAYS_JS
    head = HEAD.replace('<title>جدول تمرين 3 أيام بالمنزل — Nav Coaching</title>', f'<title>{title} — Nav Coaching</title>')
    html = (head + EXTRA_CSS + PORTRAIT_CSS + f'</style></head><body class="{body_cls}">\n' + cover_html
            + '\n<div id="dayPages"></div>\n' + '\n'.join(pages_after) + '\n' + script + '\n</body></html>')
    if fem:
        html = feminize(html)
    open(os.path.join(HERE, fname), 'w', encoding='utf8').write(html)

build_portrait('prog-flex-portrait.html', 'جدول زيادة المرونة',
      cover('جدول زيادة<br><em>المرونة</em>', 'الحوض · الظهر · الأكتاف · الأرجل — من المنزل', [
          {'n': 1, 't': 'الحوض', 'p': 'مثنيات · قلوتس · فخذ داخلي', 'k': 6},
          {'n': 2, 't': 'الظهر', 'p': 'أسفل · أعلى · صدر · أكتاف', 'k': 6},
          {'n': 3, 't': 'شامل', 'p': 'ورك · أرجل · ظهر · صدر', 'k': 6}]),
      DF, [pf_principles.replace('class="page light grid ip"','class="page light grid ip" style="--z:1.72"').replace('<h2>مبادئ زيادة المرونة</h2>','<h2>مبادئ الجدول</h2>'),
           pf_how.replace('class="page light grid ip"','class="page light grid ip" style="--z:1.95"'),
           pf_safety.replace('class="page light grid ip"','class="page light grid ip" style="--z:2.1"'), THANKS])

# ---------------------------------------------------------------------
# Portrait versions of every program
# ---------------------------------------------------------------------
import ast
def parse_days(src):
    t = src[src.index('const DAYS=[') + len('const DAYS='):]
    t = t[:t.index('\n];') + 2]
    t = re.sub(r"\b(n|cls|title|rows):", r"'\1':", t)
    return ast.literal_eval(t)
def zz(html, z):
    return html.replace('class="page light grid ip"', f'class="page light grid ip" style="--z:{z}"', 1)
def split_panels(sec_html, first_marker, second_marker):
    a = sec_html.index(first_marker); b = sec_html.index(second_marker)
    head = sec_html[:a]
    return (head + sec_html[a:b] + '</section>', head + sec_html[b:])
GYM_DAYS  = [dict(d, rl='العدات', al='بديل') for d in parse_days(gym)]
HOME_DAYS = [dict(d, rl='العدات', al='بديل') for d in parse_days(home)]
# home version: same muscles/sets/reps as the gym days, but only dumbbells (+ optional bench) and bodyweight
HOME_SWAP = [
 [('INCLINE DB PRESS', 'Gruq177Psnk', 'DB FLOOR PRESS', 'w:Bx4QPVH-J1g'),
  ('DB FLOOR PRESS', 'w:Bx4QPVH-J1g', 'PUSH UP', 'w:IODxDxX7oi4'),
  ('ONE ARM DB ROW', 'KaCcBqhiXtc', 'DB PULLOVER', 'w:jQjWlIwG4sI'),
  ('DB CHEST SUPPORTED ROW', 'w:tZUYS7X50so', 'ONE ARM DB ROW', 'KaCcBqhiXtc'),
  ('DB LATERAL RAISE', 'JIhbYYA1Q90', 'LEANING DB LATERAL RAISE', 'w:qWif_7SOYpQ'),
  ('DB CURL', 'YgHnvJQkfhc', 'DB HAMMER CURL', 'w:BRVDS6HVR9Q')],
 [('DB GOBLET SQUAT', 'w:gCESNsDsbqk', 'DB BULGARIAN SPLIT SQUAT', 'w:SkNsa3eBwLA'),
  ('DB RDL', 'u14AwrUcwWw', 'DB SINGLE LEG RDL', 'w:lI8-igvsnVQ'),
  ('SLIDING LEG CURL', 'w:kkkTfzi2gj4', 'GLUTE BRIDGE', 'w:L9KZfxT654Y'),
  ('DB CALF RAISE', 'w:wxwY7GXxL4k', 'SINGLE LEG CALF RAISE', 'w:ORT4oJ_R8Qs'),
  ('CRUNCHES', 'eeJ_CYqSoT4', 'DEAD BUG', 'w:GbSC02oU3To'),
  ('LYING LEG RAISES', 'PpZxg66ftYc', 'REVERSE CRUNCH', 'w:lmSP-c1X_iY')],
 [('DB BULGARIAN SPLIT SQUAT', 'w:SkNsa3eBwLA', 'DB REVERSE LUNGE', 'w:RZKXLMxPF_I'),
  ('DB HIP THRUST', 'w:29OfN4ztW_g', 'GLUTE BRIDGE', 'w:L9KZfxT654Y'),
  ('DB CHEST SUPPORTED ROW', 'w:tZUYS7X50so', 'ONE ARM DB ROW', 'KaCcBqhiXtc'),
  ('ONE ARM DB ROW', 'KaCcBqhiXtc', 'DB PULLOVER', 'w:jQjWlIwG4sI'),
  ('DB FLOOR PRESS', 'w:Bx4QPVH-J1g', 'PUSH UP', 'w:IODxDxX7oi4'),
  ('OVERHEAD DB TRICEPS EXTENSION', 'w:2jl4M0Dnq4c', 'BENCH DIPS', 'w:0326dy_-CzM')]]
for _d, _sw in zip(HOME_DAYS, HOME_SWAP):
    assert len(_d['rows']) == len(_sw)
    for _r, (_n, _v, _an, _av) in zip(_d['rows'], _sw):
        _r[0], _r[1], _r[7], _r[8] = _n, _v, _an, _av
GYM_CARDS = [{'n': 1, 't': 'علوي', 'p': 'صدر · ظهر · أكتاف · ذراعين', 'k': 6},
             {'n': 2, 't': 'سفلي', 'p': 'أفخاذ · قلوتس · بطات · بطن', 'k': 6},
             {'n': 3, 't': 'شامل', 'p': 'الجسم كامل', 'k': 6}]
def sets_notes_pages(src, z=1.68):
    sec = section(src, '<!-- ================= PAGE 5 : INSTRUCTIONS')
    return zz(sec, z)
RIR_GYM  = section(gym,  '<!-- ================= PAGE 6 : INSTRUCTIONS 2')
RIR_HOME = section(home, '<!-- ================= PAGE 6 : INSTRUCTIONS 2')
EQ = EQUIP_PAGE
gsn = sets_notes_pages(gym); hsn = sets_notes_pages(home)
hsn = hsn.replace('سكوات بالبار', 'قوبلت سكوات بالدمبل'); RIR_HOME = RIR_HOME.replace('سكوات بالبار', 'قوبلت سكوات بالدمبل')
build_portrait('prog-gym3-portrait.html', 'جدول تمرين 3 أيام بالنادي',
    cover('جدول تمرين<br><em>3 أيام</em> بالنادي', '', GYM_CARDS).replace('<h1>','<h1 style="font-size:140px">'), GYM_DAYS,
    [gsn, zz(RIR_GYM, 1.6), THANKS])
build_portrait('prog-home3-portrait.html', 'جدول تمرين 3 أيام بالمنزل',
    cover('جدول تمرين<br><em>3 أيام</em> بالمنزل', '', GYM_CARDS).replace('<h1>','<h1 style="font-size:140px">'), HOME_DAYS,
    [EQ, hsn, zz(RIR_HOME, 1.6), THANKS])
D4P = [dict(d, rl='العدات', al='بديل المنزل') for d in D4]
build_portrait('prog-4days-portrait.html', 'جدول تمرين 4 أيام — نادي ومنزل',
    cover('جدول تمرين<br><em>4 أيام</em>', 'التمرين الأساسي بالنادي · والبديل بالمنزل', [
        {'n': 1, 't': 'علوي A', 'p': 'صدر · ظهر · أكتاف · تراي', 'k': 6},
        {'n': 2, 't': 'سفلي A', 'p': 'أفخاذ · قلوتس · بطات · بطن', 'k': 6},
        {'n': 3, 't': 'علوي B', 'p': 'صدر · ظهر · أكتاف · باي', 'k': 6},
        {'n': 4, 't': 'سفلي B', 'p': 'قلوتس · أفخاذ خلفية · بطات · بطن', 'k': 6}]), D4P,
    [zz(p4_principles, 1.6), zz(p4_week, 1.85), zz(RIR_PAGE, 1.5), EQ, THANKS])
DGP = [dict(d, rl='العدات', al='بديل المنزل') for d in DG]
build_portrait('prog-glutes-portrait.html', 'جدول بناء القلوتس',
    cover('جدول<br><em>بناء القلوتس</em>', '3 أيام بالأسبوع · التمرين بالنادي والبديل بالمنزل', [
        {'n': 1, 't': 'قلوتس A', 'p': 'هيب ثرست · سكوات · RDL · أبدكشن', 'k': 4},
        {'n': 2, 't': 'قلوتس B', 'p': 'سبليت سكوات · باك اكستنشن · كيك باك', 'k': 4},
        {'n': 3, 't': 'قلوتس C', 'p': 'ليق برس · هيب ثرست · ليق كيرل', 'k': 4}]), DGP,
    [zz(pg_principles, 2.0), zz(pg_week, 2.0), zz(RIR_PAGE, 1.5), THANKS], fem=True)
DBP = [dict(d, rl='المطلوب', al='بديل / أسهل') for d in DB]
build_portrait('prog-back-portrait.html', 'جدول تخفيف ألم الظهر',
    cover('جدول تخفيف<br><em>ألم الظهر</em>', 'أعلى الظهر (التحدّب) وأسفل الظهر · نادي أو منزل', [
        {'n': '1', 'lbl': 'يوميًا', 't': 'روتين يومي', 'p': '5–10 دقائق · حركة وثبات', 'k': 4},
        {'n': 'A', 'lbl': 'تقوية', 't': 'تقوية A', 'p': 'أعلى الظهر · القلوتس', 'k': 5},
        {'n': 'B', 'lbl': 'تقوية', 't': 'تقوية B', 'p': 'الظهر كامل · الرجول', 'k': 5}]), DBP,
    [zz(pb_safety, 2.0), zz(pb_how, 1.9), THANKS])

print('built')
