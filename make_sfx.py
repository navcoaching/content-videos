"""Synthesise the sound effects for nav-story-pro2 (times match story-pro2.html)."""
import numpy as np, wave
SR=44100; DUR=14.3
N=int(SR*DUR); buf=np.zeros((2,N)); rng=np.random.default_rng(7)
def T(n): return np.arange(n)/SR
def add(sig,t,gain=1.0,pan=0.0):
    i=int(t*SR); 
    if i>=N: return
    sig=sig[:N-i]; l=np.sqrt((1-pan)/2); r=np.sqrt((1+pan)/2)
    buf[0,i:i+len(sig)]+=sig*gain*l; buf[1,i:i+len(sig)]+=sig*gain*r
def att(sig,ms=2):
    a=int(SR*ms/1000); sig=sig.copy(); sig[:a]*=np.linspace(0,1,a); return sig
def lp(x,fc):  # one-pole low-pass, fc scalar or array
    fc=np.broadcast_to(fc,x.shape); a=1-np.exp(-2*np.pi*fc/SR); y=np.zeros_like(x); s=0.0
    for i in range(len(x)): s+=a[i]*(x[i]-s); y[i]=s
    return y
def tap():
    n=int(.09*SR); t=T(n)
    click=np.diff(rng.standard_normal(n+1))*np.exp(-t/.003)*.5
    body=np.sin(2*np.pi*1900*t)*np.exp(-t/.010)*.35+np.sin(2*np.pi*170*t)*np.exp(-t/.028)*.6
    return att(click+body,.5)
def whoosh(dur,f0,f1,shape=.55):
    n=int(dur*SR); t=np.linspace(0,1,n)
    fc=np.exp(np.log(f0)+(np.log(f1)-np.log(f0))*t)
    y=lp(rng.standard_normal(n),fc)
    env=np.sin(np.pi*np.minimum(1,t/shape/2*1.0)**1)**2 if False else np.where(t<shape,np.sin(.5*np.pi*t/shape)**2,np.cos(.5*np.pi*(t-shape)/(1-shape))**2)
    y=y*env; return y/ (np.abs(y).max()+1e-9)
def pop(f0=420,f1=900,dur=.09):
    n=int(dur*SR); t=T(n); f=f0+(f1-f0)*np.minimum(1,t/dur*1.6)
    ph=2*np.pi*np.cumsum(f)/SR; return att(np.sin(ph)*np.exp(-t/.032),2)
def blip(f,dur=.13):
    n=int(dur*SR); t=T(n); return att((np.sin(2*np.pi*f*t)+.3*np.sin(4*np.pi*f*t))*np.exp(-t/.05),2)*.8
def chime(f,dur=1.0):
    n=int(dur*SR); t=T(n); y=np.zeros(n)
    for m,a,d in [(1,1,.55),(2,.45,.35),(3,.25,.25),(4.2,.12,.15),(5.4,.06,.1)]:
        y+=a*np.sin(2*np.pi*f*m*t)*np.exp(-t/d)
    return att(y,3)*.55
def tick(f,dur=.035):
    n=int(dur*SR); t=T(n); return att(np.sin(2*np.pi*f*t)*np.exp(-t/.011),1.5)
def tickseq(t0,t1,n,f0,f1,g):
    for i in range(n):
        u=1-(1-i/n)**.25; add(tick(f0+(f1-f0)*i/n),t0+(t1-t0)*u,g*(.6+.4*i/n),pan=.15*np.sin(i))
def arp(t,notes,g,gap=.07):
    for k,f in enumerate(notes): add(chime(f,.9+.1*k),t+k*gap,g,pan=(k-1)*.12)

# ---- intro
add(whoosh(.75,250,2600),.20,.20,-.2); add(whoosh(.7,300,2800),.42,.15,.2)
add(whoosh(1.3,180,3200,.7),.38,.33)
# ---- screen A
for i,tt in enumerate([1.75,2.45,2.6,2.75]): add(pop(380+i*60,760+i*60),tt,.10,pan=-.2+.13*i)
tickseq(2.1,3.4,22,900,2200,.13)
add(pop(520,1050,.1),3.15,.30); arp(3.5,[1319,1568],.22,.08)
# ---- tap -> screen B
add(tap(),4.05,.55); add(whoosh(.75,400,3600),4.32,.30,-.3)
for i,tt in enumerate([4.65,4.8,4.95]): add(pop(400+i*70,800+i*70),tt,.09,pan=.2)
add(blip(660),5.5,.32)
for i,f in enumerate([523,587,659,784]): add(blip(f),5.85+i*.22,.30,pan=(i-1.5)*.15)
add(blip(880),6.85,.32)
add(tap(),7.05,.5); arp(7.2,[659,784,1047],.45); add(pop(500,1100),7.25,.22)
add(whoosh(.4,600,3000),7.33,.10,.4)
# ---- tap -> screen C
add(tap(),7.45,.55); add(whoosh(.75,400,3600),7.72,.30,.3)
for i,tt in enumerate([8.15,8.3]): add(pop(420+i*80,850+i*80),tt,.09)
tickseq(8.55,10.0,30,700,2000,.12)
for i,tt in enumerate([8.75,8.9,9.05]): add(pop(450+i*60,900+i*60,.07),tt,.10,pan=-.3+.3*i)
add(whoosh(.5,500,2600),9.33,.12)
for i,tt in enumerate([9.75,9.85,9.95]): add(pop(440+i*70,880+i*70,.07),tt,.09,pan=.3)
# ---- dropdown flow
add(tap(),10.35,.55); add(pop(300,720,.12),10.42,.28); add(whoosh(.35,800,3500),10.40,.09)
for i,f in enumerate([1600,1800,2050]): add(tick(f),10.5+i*.07,.20)
add(tick(1500),11.3,.15)
add(tap(),11.55,.55); add(whoosh(.3,3200,500),11.68,.10); add(pop(700,1150,.1),11.85,.28)
add(tap(),12.5,.5); arp(12.65,[523,659,784,1047],.55,.075); add(pop(500,1150),12.68,.20)
add(whoosh(.5,700,3000),12.7,.14)
tickseq(12.75,13.75,20,1000,2400,.11)
add(pop(560,1200,.11),13.0,.28)
# ---- soft reverb + master
ir_n=int(.4*SR); ir=lp(rng.standard_normal(ir_n),3500)*np.exp(-T(ir_n)/.11); ir/=np.abs(ir).sum()*.5
wet=np.stack([np.fft.irfft(np.fft.rfft(buf[c],N+ir_n)*np.fft.rfft(ir,N+ir_n),N+ir_n)[:N] for c in (0,1)])
mix=buf+wet*.22
fade=np.ones(N); f=int(.6*SR); fade[-f:]=np.linspace(1,0,f)**1.5; mix*=fade
mix=np.tanh(mix*1.15); mix*=0.89/np.abs(mix).max()
pcm=(mix.T*32767).astype('<i2')
with wave.open('nav-story-sfx.wav','wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok',pcm.shape)
