# -*- coding: utf-8 -*-
"""Generates whatsapp/catalog.html (25 square slides: 5 packages x [cover + 4 content])."""
import os
HERE=os.path.dirname(os.path.abspath(__file__))

CSS='''
:root{--ink:#07142a;--navy:#284da0;--navy2:#3558b0;--cyan:#4cc5ed;--cyan-ink:#0a6a8f;--paper:#f3f6fa;--surf:#eaf2fb;--surf2:#eaf0f6;--line:#d8e1ea;--muted:#56667a;--head:#0b1a33;--ok:#157347;--okbg:#e2f4ea}
*{box-sizing:border-box;margin:0}
body{background:#888;font-family:"IBM Plex Sans Arabic",Cairo,sans-serif;color:var(--head)}
.sl{width:1080px;height:1080px;position:relative;overflow:hidden;margin:0 0 30px;
 background:radial-gradient(60% 40% at 90% 8%,#cfeefa 0%,transparent 70%),radial-gradient(55% 40% at 5% 100%,#dbe7f7 0%,transparent 70%),linear-gradient(165deg,#fff,#eef3f9 80%)}
.sl::before{content:"";position:absolute;inset:0;background-image:linear-gradient(#284da012 1px,transparent 1px),linear-gradient(90deg,#284da012 1px,transparent 1px);background-size:60px 60px;-webkit-mask-image:linear-gradient(180deg,#000,transparent 65%)}
.sl::after{content:"";position:absolute;inset:0;background:linear-gradient(115deg,transparent 30%,#4cc5ed18 38%,transparent 47%),linear-gradient(115deg,transparent 60%,#284da010 66%,transparent 76%);pointer-events:none}
.hd{position:absolute;top:44px;right:60px;left:60px;display:flex;justify-content:space-between;align-items:center;z-index:5}
.hd img{height:54px}
.pk{display:flex;align-items:center;gap:12px;background:#fff;border:1.5px solid var(--line);box-shadow:0 8px 22px #284da018;padding:8px 20px 8px 8px;border-radius:99px;font:700 25px Cairo}
.pk i{font-style:normal;background:var(--navy);color:#fff;border-radius:99px;padding:3px 16px;font:700 24px "Readex Pro";direction:ltr}
.pk span{color:var(--navy)}
.t1{position:absolute;z-index:4;top:150px;right:60px;left:60px}
.t1 h1{font:900 80px/1.2 Cairo;color:var(--head)}
.t1 h1 em{font-style:normal;color:var(--navy)}
.t1 p{font-size:36px;line-height:1.6;color:#2c3c52;margin-top:14px;max-width:900px}
.glow{position:absolute;z-index:0;border-radius:50%;background:radial-gradient(closest-side,#4cc5ed55,transparent 72%)}
.slash{position:absolute;z-index:1;height:20px;background:var(--cyan);transform:skewX(-22deg)}
.num{position:absolute;z-index:6;left:60px;bottom:40px;font:500 24px "Readex Pro";color:var(--muted);direction:ltr;background:#fffc;border:1.5px solid var(--line);border-radius:99px;padding:5px 18px}
/* phone */
.phone{position:absolute;z-index:3;width:416px;height:820px;background:#050b16;border-radius:62px;padding:13px;box-shadow:0 40px 80px #284da044,0 0 0 2px #2a3d5c inset;overflow:hidden}
.pc{left:50%;top:420px;transform:translateX(-50%) scale(1.62);transform-origin:top center}
.screen{position:absolute;top:13px;right:13px;width:390px;height:794px;background:var(--paper);border-radius:50px;overflow:hidden;color:var(--head);direction:rtl}
.island{position:absolute;top:10px;left:50%;transform:translateX(-50%);width:100px;height:26px;background:#050b16;border-radius:20px}
.status{height:44px;display:flex;justify-content:space-between;align-items:center;padding:6px 26px 0;font:700 14px "Readex Pro";direction:ltr}
.body{padding:8px 16px}
.sh2{font:900 21px/1.25 Cairo;margin:6px 0 2px}.sub{font-size:12px;color:var(--muted);margin-bottom:12px}
.card{background:var(--surf);border-radius:14px;padding:12px 14px;margin-bottom:12px}
.row{display:flex;justify-content:space-between;align-items:center}
.pill{display:inline-flex;gap:5px;align-items:center;font-size:11px;font-weight:700;background:#fff3d4;color:#8a5a00;border-radius:99px;padding:3px 9px}
.pill i{width:7px;height:7px;border-radius:50%;background:#e5a50a}
.pill.g{background:var(--okbg);color:var(--ok)}.pill.g i{background:var(--ok)}
.pill.b{background:#e4f6fc;color:var(--cyan-ink)}.pill.b i{background:var(--cyan)}
.bar{height:11px;border-radius:9px;background:#fff;margin:9px 0 7px;overflow:hidden}.bar b{display:block;height:100%;background:var(--ok);border-radius:9px;margin-right:0}
.bar.n b{background:linear-gradient(270deg,var(--cyan),var(--navy))}
.t{font:700 15px "IBM Plex Sans Arabic"}.s{font-size:11.5px;color:var(--muted)}
.sec{font:900 16px Cairo;margin:14px 0 8px}
.day{background:var(--surf2);border-radius:12px;padding:12px 13px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;font:700 13px "Readex Pro";direction:ltr}
.day span{font:500 12px "IBM Plex Sans Arabic";color:var(--muted);direction:rtl}
.day.done{background:var(--okbg);color:var(--ok)}.day.done span{color:var(--ok);font-weight:700}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.st{background:var(--surf2);border-radius:12px;padding:10px 12px}.st small{display:block;font-size:11px;color:var(--muted)}.st b{font:900 18px "Readex Pro";direction:ltr;display:block;text-align:right}.st b em{font:500 11px "IBM Plex Sans Arabic";color:var(--muted);font-style:normal}
.chips{display:flex;gap:6px;margin-bottom:8px;direction:rtl;overflow:hidden}
.chip{font:700 11.5px "IBM Plex Sans Arabic";background:#fff;border:1px solid var(--line);border-radius:99px;padding:6px 11px;white-space:nowrap}.chip.on{background:var(--navy);border-color:var(--navy);color:#fff}
.chip.l{font-family:"Readex Pro";font-size:10.5px;direction:ltr}
.ex{background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px;margin-top:6px}
.ex h4{font:700 17px "Readex Pro";direction:ltr;text-align:right}
.tgt{font-size:12px;color:var(--muted);margin:4px 0 12px}.tgt b{color:var(--head);direction:ltr;unicode-bidi:embed}
.inp{display:flex;gap:6px;direction:rtl;align-items:flex-end;margin-bottom:12px}
.f{flex:1}.f label{display:block;font-size:11px;font-weight:700;margin-bottom:5px}
.box{height:40px;border:1px solid var(--line);border-radius:10px;display:flex;align-items:center;justify-content:center;font:700 15px "Readex Pro"}
.btn{background:var(--navy);color:#fff;border-radius:99px;text-align:center;padding:11px;font-weight:700;font-size:14px}
.ok{display:inline-block;width:18px;height:18px;border-radius:50%;background:var(--ok);color:#fff;font-size:12px;line-height:18px;text-align:center;vertical-align:middle;margin-inline-start:6px}
.meal{background:#fff;border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin-bottom:8px}
.meal .row b{font-size:13px}.meal .row span{font:700 12px "Readex Pro";color:var(--cyan-ink);direction:ltr}
.meal p{font-size:11.5px;color:var(--muted);margin-top:3px}
.mac{display:flex;align-items:center;gap:8px;margin-bottom:9px;font-size:12px}
.mac label{width:50px;font-weight:700}.mac .bar{flex:1;margin:0;height:9px}.mac em{font:700 11px "Readex Pro";font-style:normal;direction:ltr;width:66px;text-align:left;color:var(--muted)}
/* chat */
.chat{background:#e9f0f7;height:100%}
.chead{background:var(--navy);color:#fff;padding:50px 16px 12px;display:flex;align-items:center;gap:10px}
.av{width:38px;height:38px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;font:900 13px Cairo;color:var(--navy)}
.chead b{font:700 15px "IBM Plex Sans Arabic";display:block}.chead small{font-size:11px;opacity:.8}
.msgs{padding:14px 12px;display:flex;flex-direction:column;gap:9px}
.m{max-width:80%;padding:9px 12px;border-radius:14px;font-size:12.5px;line-height:1.6;box-shadow:0 1px 2px #0002}
.m.me{align-self:flex-start;background:#fff;border-top-left-radius:4px}
.m.co{align-self:flex-end;background:#d6ecff;border-top-right-radius:4px}
.m small{display:block;font-size:10px;color:var(--muted);margin-top:3px;direction:ltr;text-align:left}
.vn{display:flex;align-items:center;gap:8px;direction:ltr}.vn i{width:26px;height:26px;border-radius:50%;background:var(--navy);display:flex;align-items:center;justify-content:center;color:#fff;font-size:11px;font-style:normal}
.vn u{display:block;width:120px;height:14px;background:repeating-linear-gradient(90deg,#9db4d6 0 3px,transparent 3px 6px);-webkit-mask:linear-gradient(0deg,#000 40%,transparent 40%,transparent 60%,#000 60%)}
.zoom{background:#fff;border-radius:14px;padding:11px 13px;display:flex;align-items:center;gap:11px;border:1px solid var(--line);margin-bottom:2px}
.zoom i{width:36px;height:36px;border-radius:10px;background:#2d8cff;color:#fff;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:16px}
.zoom b{font-size:13px;display:block}.zoom small{font-size:11px;color:var(--muted)}
/* charts / tables */
.chart{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px;margin-bottom:10px}
.chart h5{font:900 15px Cairo;margin-bottom:4px}
.xl{width:100%;border-collapse:collapse;font:500 11.5px "Readex Pro";direction:ltr;background:#fff;border-radius:10px;overflow:hidden}
.xl th{background:#1f7a4d;color:#fff;font:700 11px "IBM Plex Sans Arabic";padding:7px 4px}
.xl td{border:1px solid var(--line);padding:7px 4px;text-align:center}
.xl tr:nth-child(even) td{background:#f1f7f3}
.as{display:flex;justify-content:space-between;align-items:center;background:#fff;border:1px solid var(--line);border-radius:12px;padding:11px 13px;margin-bottom:8px;font-size:13px;font-weight:700}
.tip{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin-bottom:9px;display:flex;gap:11px;align-items:flex-start}
.tip i{flex:0 0 38px;height:38px;border-radius:11px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:18px}
.tip b{font-size:13.5px;display:block;margin-bottom:2px}.tip p{font-size:11.5px;color:var(--muted);line-height:1.55}
.vid{height:150px;border-radius:12px;background:linear-gradient(135deg,#0d1f3c,#284da0);display:flex;align-items:center;justify-content:center;margin-bottom:10px;position:relative}
.vid i{width:52px;height:52px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;color:var(--navy);font-style:normal;font-size:20px;padding-right:3px}
.vid span{position:absolute;bottom:8px;left:10px;font:500 11px "Readex Pro";color:#fff;opacity:.85}
.demo{position:absolute;z-index:6;right:60px;bottom:40px;font:500 22px "IBM Plex Sans Arabic";color:var(--muted);background:#fffc;border:1.5px solid var(--line);border-radius:99px;padding:4px 16px}
/* cover */
.cv .tagp{position:absolute;z-index:4;right:60px;top:150px;display:inline-flex;align-items:center;gap:10px;background:var(--cyan);color:var(--ink);font:900 28px Cairo;padding:8px 26px}
.cv .tagp.n{background:var(--navy);color:#fff}
.cv h1{position:absolute;z-index:4;right:60px;top:210px;width:520px;font:900 108px/1.12 Cairo;color:var(--head)}
.cv h1 em{font-style:normal;color:var(--navy)}
.cv .ds{position:absolute;z-index:4;right:60px;top:462px;width:520px;font-size:32px;line-height:1.55;color:#2c3c52}
.cv .ft{position:absolute;z-index:4;right:60px;top:660px;width:520px;display:flex;flex-wrap:wrap;gap:10px}
.cv .ft span{background:#fff;border:1.5px solid var(--line);box-shadow:0 6px 16px #284da014;padding:5px 14px;font-size:23px;font-weight:700;color:var(--head)}
.price{position:absolute;z-index:5;right:60px;bottom:46px;width:520px;background:var(--ink);color:#fff;padding:22px 30px 22px;border-right:10px solid var(--cyan)}
.price .m1{display:flex;align-items:baseline;gap:14px}
.price .m1 b{font:700 96px/1 "Readex Pro";direction:ltr}
.price .m1 span{font:700 32px Cairo;color:var(--cyan)}
.price .m3{font-size:27px;margin-top:8px;color:#d4e0f0;line-height:1.5}
.price .m3 b{color:#fff;font-family:"Readex Pro";direction:ltr;unicode-bidi:isolate;display:inline-block}
.price .stu{font-size:23px;margin-top:10px;color:#a9d8ec;border-top:1px solid #ffffff30;padding-top:8px}.price .stu b{font-family:"Readex Pro";color:#fff}
.cphone{left:-20px;top:300px;transform:rotate(-5deg) scale(.98);transform-origin:top left}
'''

LOGO='<img src="../brand/logo-color-hd.png" alt="Nav Coaching">'
def status(): return '<div class="island"></div><div class="status"><span>9:41</span><span>5G ▮▮▮</span></div>'
def phone(inner,cls='pc',style=''): return f'<div class="phone {cls}" style="{style}"><div class="screen">{status()}{inner}</div></div>'

# ---------- screens ----------
def scr_program(name='الباقة المكثفة'):
    return '''<div class="body"><div class="sh2">البلوك 1 — بناء القوة</div><div class="sub">الأسبوع 3 من 4</div>
<div class="chips"><span class="chip">الأسبوع 1</span><span class="chip">الأسبوع 2</span><span class="chip on">الأسبوع 3</span><span class="chip">الأسبوع 4</span></div>
<div class="chips"><span class="chip l on">DAY 1 — LOWER BODY</span><span class="chip l">DAY 2 — UPPER BODY</span></div>
<div class="ex"><div class="row"><h4>1. Mid Leg Press <i class="ok">✓</i></h4></div><div class="tgt">المستهدف: <b>4×10 · RIR 2</b></div>
<div class="inp"><div class="f"><label>الوزن (كغ)</label><div class="box">88</div></div><div class="f" style="flex:2.4"><label>التكرارات لكل مجموعة</label><div style="display:flex;gap:5px"><div class="box" style="flex:1">10</div><div class="box" style="flex:1">10</div><div class="box" style="flex:1">10</div><div class="box" style="flex:1">10</div></div></div><div class="f" style="flex:.7"><label>RIR</label><div class="box">2</div></div></div>
<div class="btn">تحديث</div></div>
<div class="ex"><h4>2. Romanian Deadlift</h4><div class="tgt">المستهدف: <b>3×8 · RIR 2</b></div></div></div>'''

def scr_week(name):
    return f'''<div class="body"><div class="sh2">{name}</div><div class="sub">أسابيع متتالية من الالتزام</div>
<div class="card"><div class="row"><span class="t">التزامك 100%</span><span class="pill"><i></i>3 أسابيع متتالية</span></div><div class="bar"><b style="width:100%"></b></div></div>
<div class="sec">برنامجك الحالي</div>
<div class="day done"><span>تم <i class="ok">✓</i></span>DAY 1 — LOWER BODY</div><div class="day"><span>0 من 5</span>DAY 2 — UPPER BODY</div><div class="day"><span>0 من 5</span>DAY 3 — GLUTES &amp; HAMSTRINGS</div>
<div class="sec">التغذية اليوم</div><div class="grid"><div class="st"><small>السعرات</small><b>1,228 <em>من 1,850</em></b></div><div class="st"><small>بروتين</small><b>85 <em>من 130 غ</em></b></div></div></div>'''

def scr_nutrition():
    return '''<div class="body"><div class="sh2">التغذية اليوم</div><div class="sub">أهدافك اليومية — نموذج توضيحي</div>
<div class="card"><div class="row"><span class="t">السعرات</span><span class="t" style="font-family:'Readex Pro';direction:ltr">1,228 / 1,850</span></div><div class="bar n"><b style="width:66%"></b></div>
<div class="mac"><label>بروتين</label><div class="bar n"><b style="width:65%"></b></div><em>85 / 130 g</em></div>
<div class="mac"><label>كارب</label><div class="bar n"><b style="width:62%"></b></div><em>119 / 190 g</em></div>
<div class="mac" style="margin-bottom:0"><label>دهون</label><div class="bar n"><b style="width:74%"></b></div><em>46 / 62 g</em></div></div>
<div class="sec">وجباتك</div>
<div class="meal"><div class="row"><b>الفطور</b><span>420 kcal</span></div><p>من جدولك الغذائي · بالغرام</p></div>
<div class="meal"><div class="row"><b>الغداء</b><span>560 kcal</span></div><p>اختر من جداولك أو قاعدة الأكل</p></div>
<div class="meal"><div class="row"><b>العشاء</b><span>248 kcal</span></div><p>أضف وجبة +</p></div></div>'''

def scr_chat(kind):
    z='<div class="msgs" style="padding-bottom:0"><div class="zoom"><i>▶</i><div><b>4 مكالمات زوم شهريًا</b><small>نتابع فيها تطورك واستفساراتك</small></div></div></div>' if kind=='zoom' else ''
    if kind=='biweekly': head,sub='مراجعة كل أسبوعين','تعديل التمرين عند الحاجة'
    elif kind=='gamers': head,sub='متابعة مستمرة','تعديل الخطة حسب أدائك'
    else: head,sub='مراجعة أسبوعية','تعديل السعرات أو التمرين عند الحاجة'
    q={'zoom':'كان أسبوعي ممتاز، التزمت بكل التمارين','biweekly':'خلصت أسبوعين تمرين، وحاسس الأوزان صارت أخف','gamers':'أحس بتعب بالظهر بعد جلسات اللعب الطويلة','nutri':'صعب علي ألتزم بالأكل خارج البيت'}.get(kind,'كان أسبوعي ممتاز، التزمت بكل التمارين')
    a={'zoom':'ممتاز! رفعنا الوزن شوي هالأسبوع، وراجعنا سعراتك','biweekly':'زدنا الوزن وعدّلنا الحجم، ونراجع بعد أسبوعين','gamers':'ضفنا لك تمارين للظهر والرقبة وتذكير للحركة','nutri':'نرتب لك خيارات تناسب أكلك خارج البيت'}.get(kind,'ممتاز! عدّلنا السعرات والتمرين على تقدمك')
    return f'''<div class="chat"><div class="chead"><div class="av">NAV</div><div><b>Nav Coaching</b><small>{head} · {sub}</small></div></div>{z}
<div class="msgs"><div class="m me"><div class="vn"><i>▶</i><u></u><span style="font:500 11px 'Readex Pro'">0:42</span></div><small>9:12</small></div>
<div class="m me">{q}<small>9:13</small></div>
<div class="m co">{a}<small>11:05</small></div>
<div class="m co">رد خلال 48 ساعة عمل على أي سؤال 💙<small>11:06</small></div></div></div>'''

def line_svg(w=330,h=120,pts=None,col='#284da0'):
    pts=pts or [68.8,67.9,68.1,67.3,67.4,67.0,67.1,66.4,66.5,66.0]
    lo,hi=min(pts)-.3,max(pts)+.3; n=len(pts)
    xy=[(8+(w-16)*i/(n-1),h-8-(h-16)*(p-lo)/(hi-lo)) for i,p in enumerate(pts)]
    # time runs left to right, like the site's charts
    d=' '.join(('M' if i==0 else 'L')+f'{x:.1f} {y:.1f}' for i,(x,y) in enumerate(xy))
    dots=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{col}"/>' for x,y in xy)
    return f'<svg viewBox="0 0 {w} {h}" width="100%"><path d="{d}" fill="none" stroke="{col}" stroke-width="2.4" stroke-linejoin="round"/>{dots}</svg>'

def scr_progress():
    return f'''<div class="body"><div class="sh2">لوحة التقدم</div><div class="sub">أسبوعًا بأسبوع — ببيانات مثال</div>
<div class="chart"><div class="row"><h5>الوزن (كغ)</h5><span class="pill g"><i></i>−1.5 كغ</span></div>{line_svg()}<div class="s">متوسط أول أسبوع 68.3 ← آخر أسبوع 66.8 كغ</div></div>
<div class="chart"><h5>القياسات (سم)</h5>{line_svg(h=90,pts=[88,87.5,87,86.4,86,85.2],col='#4cc5ed')}{line_svg(h=70,pts=[102,101.7,101.4,101.2,100.8,100.6],col='#284da0')}<div class="s">الخصر · الحوض</div></div></div>'''

def scr_calc():
    return '''<div class="body"><div class="sh2">احسب سعراتك</div><div class="sub">هدفك اليومي من السعرات والماكروز — نموذج توضيحي</div>
<div class="card" style="text-align:center"><div class="s">سعراتك اليومية</div><div style="font:700 44px 'Readex Pro';direction:ltr;color:var(--navy)">1,850</div><div class="s">kcal</div></div>
<div class="grid" style="margin-bottom:12px"><div class="st"><small>بروتين</small><b>130 <em>غ</em></b></div><div class="st"><small>كارب</small><b>190 <em>غ</em></b></div><div class="st"><small>دهون</small><b>62 <em>غ</em></b></div><div class="st"><small>الهدف</small><b style="font-family:Cairo;font-size:14px">تنشيف</b></div></div>
<div class="sec">كيف أحسب؟</div>
<div class="tip"><i>1</i><div><b>زِن وجبتك</b><p>بالغرام من قاعدة الأكل</p></div></div>
<div class="tip"><i>2</i><div><b>سجّلها في اليوم</b><p>وشوف كم باقي لك</p></div></div></div>'''

def scr_excel():
    rows=''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a,b,c,d in [('1','68.8','88.0','102.0'),('2','68.1','87.5','101.7'),('3','67.4','87.0','101.4'),('4','67.0','86.4','101.2'),('5','66.5','86.0','100.8')])
    return f'''<div class="body"><div class="sh2">ملف متابعة التطور</div><div class="sub">Excel — أسبوعًا بأسبوع (نموذج توضيحي)</div>
<table class="xl"><tr><th>الأسبوع</th><th>الوزن</th><th>الخصر</th><th>الحوض</th></tr>{rows}</table>
<div class="chart" style="margin-top:12px"><h5>الوزن عبر الأسابيع</h5>{line_svg(h=100,pts=[68.8,68.1,67.4,67.0,66.5])}</div></div>'''

def scr_assess():
    items=[('جودة النوم','تحتاج تحسين','b'),('الطاقة والتركيز','متوسط','b'),('الظهر والرقبة','يوجد شد','b'),('اللياقة الحالية','مبتدئ','g')]
    rows=''.join(f'<div class="as"><span>{a}</span><span class="pill {c}"><i></i>{b}</span></div>' for a,b,c in items)
    return f'''<div class="body"><div class="sh2">تقييم شامل</div><div class="sub">لحالتك البدنية والعقلية — نموذج توضيحي</div>{rows}
<div class="card" style="margin-top:6px"><div class="t">نوع اللعبة التي تلعبها</div><div class="s" style="margin-top:4px">يُسجَّل في الاستبيان لتخصيص برنامجك</div></div></div>'''

def scr_sleep():
    return '''<div class="body"><div class="sh2">عادات تدعم أداءك</div><div class="sub">نصائح عملية داخل برنامجك</div>
<div class="tip"><i>☾</i><div><b>النوم</b><p>روتين نوم يثبّت طاقتك وتركيزك</p></div></div>
<div class="tip"><i>≈</i><div><b>الاسترخاء</b><p>عادات بسيطة تخفف التوتر بين الجلسات</p></div></div>
<div class="tip"><i>↕</i><div><b>ظهر ورقبة أريح</b><p>تمارين تساعد مع الجلوس الطويل</p></div></div></div>'''

def scr_exercise():
    return '''<div class="body"><div class="sh2">شرح التمرين</div><div class="sub">لكل تمرين فيديو شرح وبديل</div>
<div class="vid"><i>▶</i><span>YouTube</span></div>
<div class="ex" style="margin-top:0"><h4>Mid Leg Press</h4><div class="tgt">المستهدف: <b>4×10 · RIR 2</b></div><div class="row"><span class="pill b"><i></i>شاهد الشرح</span><span class="pill"><i></i>بديل تختاره المدربة</span></div></div>
<div class="ex"><h4>Romanian Deadlift</h4><div class="tgt">المستهدف: <b>3×8 · RIR 2</b></div></div></div>'''

# ---------- slide builders ----------
def content(pkg,price,idx,total,title,cap,screen,demo=True):
    return f'''<section class="sl"><div class="glow" style="left:50%;top:500px;width:900px;height:700px;transform:translateX(-50%)"></div>
<div class="hd">{LOGO}<div class="pk"><i>{price}</i><span>{pkg}</span></div></div>
<div class="t1"><h1>{title}</h1><p>{cap}</p></div>
{phone(screen)}
{'<div class="demo">نموذج توضيحي</div>' if demo else ''}<div class="num">{idx} / {total}</div></section>'''

def cover(pkg_em,pkg_rest,desc,feats,tag,tagnavy,m1,m3,phone_screen):
    f=''.join(f'<span>{x}</span>' for x in feats)
    m3h=f'<div class="m3">{m3}</div>' if m3 else '<div class="m3">شهر واحد</div>'
    return f'''<section class="sl cv"><div class="glow" style="left:-120px;top:250px;width:700px;height:850px"></div>
<div class="hd">{LOGO}<div class="pk"><span style="color:var(--head)">navcoaching.com</span></div></div>
<div class="tagp {'n' if tagnavy else ''}">{tag}</div>
<h1>{pkg_rest}<br><em>{pkg_em}</em></h1>
<div class="ds">{desc}</div><div class="ft">{f}</div>
{phone(phone_screen,'cphone')}
<div class="price"><div class="m1"><b>{m1}</b><span>ر.س / شهر</span></div>{m3h}<div class="stu">خصم <b>10%</b> للطلاب · الدفع بتحويل بنكي</div></div>
</section>'''

PK=[
 dict(key='intensive',name='المكثفة',price='599',pre='الباقة',
  desc='تمرين + تغذية + زوم + جلسة حضورية. الأنسب للمبتدئين ولمن يحتاج متابعة أسبوعية.',
  feats=['4 زوم شهريًا','جلسة حضورية*','تمرين + تغذية'],tag='الأكثر طلبًا',navy=False,
  m3='3 أشهر: <b>1,550</b> ر.س (≈ <b>516.67</b> شهريًا)',
  slides=[('جدول <em>التمرين</em>','ملف شامل للخطة التدريبية مع شروحات وافية للتمارين، بالمنزل أو بالنادي.',scr_program()),
          ('خطة <em>التغذية</em>','تغذية مخصصة لهدفك مع شرح تطبيق MyFitnessPal وكتيب شامل للرياضة والتغذية.',scr_nutrition()),
          ('زوم + <em>متابعة أسبوعية</em>','4 مكالمات زوم شهريًا، ومناقشة أسبوعية لتطورك بالفيديو أو الصوت.',scr_chat('zoom')),
          ('تتبّع <em>تقدّمك</em>','نعدّل السعرات أو التمرين حسب قياساتك والتزامك لتثبت النتيجة.',scr_progress())]),
 dict(key='advanced',name='المتقدمة',price='499',pre='الباقة',
  desc='لمن عنده خبرة ويحتاج تمرين + تغذية مع متابعة أسبوعية، بدون زوم.',
  feats=['تمرين + تغذية','متابعة أسبوعية','كتيب شامل'],tag='مع متابعة',navy=True,
  m3='3 أشهر: <b>1,250</b> ر.س (≈ <b>416.67</b> شهريًا)',
  slides=[('جدول <em>التمرين</em>','ملف شامل للخطة التدريبية مع شروحات وافية للتمارين، بالمنزل أو بالنادي.',scr_program()),
          ('خطة <em>التغذية</em>','خطة تغذية تناسب هدفك ونمط حياتك، وكتيب شامل للرياضة والتغذية.',scr_nutrition()),
          ('متابعة <em>أسبوعية</em>','مناقشة أسبوعية لتطورك (فيديو أو صوت) مع تعديل السعرات أو التمرين.',scr_chat('weekly')),
          ('تتبّع <em>تقدّمك</em>','وزنك وقياساتك بالرسوم أسبوعًا بأسبوع، ونعدّل الخطة عليها.',scr_progress())]),
 dict(key='basic',name='الأساسية',price='349',pre='الباقة',
  desc='لمن يعرف يضبط أكله ويحتاج خطة تمرين فقط، ومتابعة كل أسبوعين.',
  feats=['خطة تمرين','متابعة كل أسبوعين','بدون خطة تغذية'],tag='مع متابعة',navy=True,
  m3='3 أشهر: <b>950</b> ر.س (≈ <b>316.67</b> شهريًا)',
  slides=[('برنامجك <em>الأسبوعي</em>','ملف شامل للخطة التدريبية، بالمنزل أو بالنادي، تتابعه من حسابك.',scr_week('الباقة الأساسية')),
          ('شرح <em>التمارين</em>','شروحات وافية لكل تمرين، ولك تبديله ببديل تختاره المدربة.',scr_exercise()),
          ('متابعة كل <em>أسبوعين</em>','مناقشة كل أسبوعين لتطورك (فيديو أو صوت) مع تعديل التمرين عند الحاجة.',scr_chat('biweekly')),
          ('تتبّع <em>تقدّمك</em>','سجّل أوزانك وتكراراتك وشوف تقدمك بالرسوم.',scr_progress())]),
 dict(key='nutrition',name='التغذية',price='250',pre='باقة',
  desc='لمن يحتاج خطة تغذية شاملة ويتعلم حساب السعرات، بدون خطة تمرين.',
  feats=['خطة تغذية','حساب السعرات','ملف Excel'],tag='مع متابعة',navy=True,
  m3=None,
  slides=[('خطة <em>التغذية</em>','خطة تغذية شاملة تناسب هدفك ونمط حياتك.',scr_nutrition()),
          ('تعلّم <em>حساب السعرات</em>','نحدد سعراتك المناسبة ونعلّمك الحسبة وخيارات تناسبك.',scr_calc()),
          ('ملف <em>متابعة التطور</em>','ملف Excel لمتابعة التطور والقياسات أسبوعًا بأسبوع.',scr_excel()),
          ('متابعة <em>أسبوعية</em>','مناقشة أسبوعية لعلاقتك بالتغذية في المنزل أو خارجه.',scr_chat('nutri'))]),
 dict(key='gamers',name='القيمرز',price='399',pre='باقة',
  desc='للاعبين الإلكترونيين وصانعي المحتوى: لياقة أفضل داخل وخارج الشاشة.',
  feats=['تقييم شامل','تدريب + تغذية','نوم واسترخاء'],tag='للقيمرز 🎮',navy=False,
  m3=None,
  slides=[('تقييم <em>شامل</em>','تقييم لحالتك البدنية والعقلية قبل تصميم برنامجك.',scr_assess()),
          ('تدريب <em>وتغذية</em>','برنامج تدريب وتغذية مخصص لك، تتابعه من حسابك.',scr_week('باقة القيمرز')),
          ('متابعة <em>مستمرة</em>','متابعة وتعديل الخطط حسب تطور أدائك.',scr_chat('gamers')),
          ('نوم <em>واسترخاء</em>','نصائح عملية لتحسين عادات النوم والاسترخاء، وتمارين لظهر ورقبة أريح.',scr_sleep())]),
]

out=['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>Nav Coaching — WhatsApp catalog</title><style>'+CSS+'</style></head><body>']
order=[]
for p in PK:
    pre=p['pre']
    out.append(cover(p['name'],pre,p['desc'],p['feats'],p['tag'],p['navy'],p['price'],p['m3'],scr_week(f"{pre} {p['name']}")).replace('<section class="sl cv">',f'<section class="sl cv" id="{p["key"]}-1">',1))
    order.append(f"{p['key']}-1")
    for i,(t,c,sc) in enumerate(p['slides'],start=2):
        out.append(content(f"{pre} {p['name']}",p['price'],i,5,t,c,sc).replace('<section class="sl">',f'<section class="sl" id="{p["key"]}-{i}">',1))
        order.append(f"{p['key']}-{i}")
out.append('</body></html>')
open(os.path.join(HERE,'catalog.html'),'w',encoding='utf8').write('\n'.join(out))
open(os.path.join(HERE,'order.txt'),'w').write('\n'.join(order))
print(len(order),'slides')
