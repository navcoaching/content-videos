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


def build(fname, title, cover_html, days, hdr, pages_after):
    script = SCRIPT_T
    script = re.sub(r'const DAYS=\[.*?\n\];', 'const DAYS=' + json.dumps(days, ensure_ascii=False) + ';', script, flags=re.S)
    script = script.replace('const TOTAL=7;', 'let TOTAL=0;')
    script = script.replace('// ---- pager on every page', '// ---- pager on every page\nTOTAL=document.querySelectorAll(".page").length;')
    script = script.replace(
        "lats:['UPPER_BACK'],rhomb:['TRAPEZIUS'],",
        "lats:['UPPER_BACK'],rhomb:['TRAPEZIUS'],gmed:['GLUTEAL'],lowb:['LOWER_BACK'],obl:['OBLIQUES'],")
    script = script.replace("LOW=['quads','glutes','hams','calves'];",
                            "LOW=['quads','glutes','hams','calves','gmed'],MID=['abs','obl','lowb'];")
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
    html = head + EXTRA_CSS + '</style></head><body>\n' + cover_html + '\n<div id="dayPages"></div>\n' + '\n'.join(pages_after) + '\n' + script + '\n</body></html>'
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
      [pg_principles, pg_week, RIR_PAGE, THANKS])

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
print('built')
