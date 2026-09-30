"""
Nav Coaching "3-day split" reel — cinematic gym soundtrack (procedural, royalty-free).

Timing comes from src/split/split.json (shots) + the few constants below, which mirror src/split/data.ts
(list reveals, highlighted captions, CTA). 120 BPM: 1 beat = 30 frames, 1 bar = 120 frames.

Arrangement:  hook (riser, heartbeat) -> DROP at title -> Day 1 groove -> rest (breakdown) -> Day 2 (16th hats, arp)
              -> rest -> Day 3 (peak, key up a tone) -> add-ons (light) -> CTA (impact, resolve).
Outputs: public/audio/split.wav, audio/stems/split_music.wav, audio/stems/split_sfx.wav
"""
import json
import os
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "src", "split", "split.json")))
SR = 48000
FPS = D["fps"]
BEAT = 60.0 / D["bpm"]
BAR = BEAT * 4
DUR = D["durationInFrames"] / FPS
N = int(DUR * SR)
rng = np.random.default_rng(21)

# ---- constants mirrored from src/split/data.ts
SECT = {"hook": (0, 240), "title": (240, 360), "day1": (360, 960), "rest1": (960, 1080), "day2": (1080, 1680),
        "rest2": (1680, 1800), "day3": (1800, 2400), "addons": (2400, 2640), "cta": (2640, 3120)}
LIST_FROM = [690, 1440, 2160]
LIST_ITEMS = [5, 5, 6]
HL_CAPTIONS = [66, 198, 660, 1530, 1860]
CTA = dict(logo=2670, type0=2810, nchars=15, button=2890, click=2990)
ADDON_LABELS = [2404, 2484, 2564]


def f2s(fr):
    return fr / FPS


def t_arr(n):
    return np.arange(n) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a, d):
    t = t_arr(n)
    return np.clip(t / max(a, 1e-4), 0, 1) * np.exp(-np.maximum(t - a, 0) / d)


def sos(kind, fc, order=2):
    return signal.butter(order, fc, kind, fs=SR, output="sos")


def lp(x, fc, o=2):
    return signal.sosfilt(sos("low", min(fc, SR * 0.45), o), x)


def hp(x, fc, o=2):
    return signal.sosfilt(sos("high", fc, o), x)


def bp(x, lo, hi):
    return signal.sosfilt(sos("band", [lo, min(hi, SR * 0.45)]), x)


def noise(n):
    return rng.standard_normal(n)


def mix(*parts):
    n = max(len(p[0] if isinstance(p, tuple) else p) for p in parts)
    o = np.zeros(n)
    for p in parts:
        x, w = p if isinstance(p, tuple) else (p, 1.0)
        o[: len(x)] += x * w
    return o


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N + SR * 5))

    def add(self, sec, mono, gain=1.0, pan=0.0):
        s = int(sec * SR)
        gl, gr = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
        a = max(0, s)
        e = min(self.x.shape[1], s + len(mono))
        if e <= a:
            return
        seg = mono[a - s: e - s] * gain
        self.x[0, a:e] += seg * gl
        self.x[1, a:e] += seg * gr


def sweep(x, f0, f1, kind="band", chunk=256):
    out = np.zeros_like(x)
    zi = None
    k = int(np.ceil(len(x) / chunk))
    for i in range(k):
        fc = float(np.clip(f0 * (f1 / f0) ** (i / max(k - 1, 1)), 30, SR * 0.4))
        s_ = sos("band", [fc / 1.6, min(fc * 1.6, SR * 0.45)]) if kind == "band" else sos(kind, fc)
        if zi is None:
            zi = np.zeros((s_.shape[0], 2))
        y, zi = signal.sosfilt(s_, x[i * chunk:(i + 1) * chunk], zi=zi)
        out[i * chunk:(i + 1) * chunk] = y
    return out


# ------------------------------------------------------------------ instruments
def kick(punch=1.0):
    n = int(0.42 * SR)
    f = 46 + 130 * np.exp(-t_arr(n) / 0.032)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.17)
    click = hp(noise(n), 3500) * env(n, 0.0005, 0.004) * 0.35
    return np.tanh(1.9 * punch * (body + click))


def clap():
    n = int(0.32 * SR)
    e = sum(np.concatenate([np.zeros(int(o * SR)), env(n - int(o * SR), 0.0005, 0.012 if k < 3 else 0.09)]) for k, o in enumerate((0, 0.009, 0.018, 0.027)))
    return bp(noise(n), 900, 3400) * e


def hat(open_=False):
    n = int((0.22 if open_ else 0.05) * SR)
    return hp(noise(n), 7500) * env(n, 0.0005, 0.06 if open_ else 0.012)


def snare():
    n = int(0.25 * SR)
    return np.tanh(1.4 * (bp(noise(n), 1400, 7000) * env(n, 0.0005, 0.06) + np.sin(2 * np.pi * 190 * t_arr(n)) * env(n, 0.0005, 0.05) * 0.5))


def pluck(f0):
    n = int(0.42 * SR)
    tt = t_arr(n)
    x = np.sin(2 * np.pi * f0 * tt) + 0.35 * np.sin(4 * np.pi * f0 * tt) * np.exp(-tt / 0.05) + 0.15 * np.sin(6 * np.pi * f0 * tt) * np.exp(-tt / 0.03)
    return lp(x * env(n, 0.002, 0.15), 3800)


def saw(f0, n):
    return 2 * ((f0 * t_arr(n) + rng.random()) % 1) - 1


def pad_notes(notes, n, fc):
    x = np.zeros(n)
    for m in notes:
        for det in (-0.09, 0.0, 0.09):
            x += saw(midi(m) * 2 ** (det / 12), n)
    return lp(x / (3 * len(notes)), fc)


def sub(f0, n):
    tt = t_arr(n)
    x = np.sin(2 * np.pi * f0 * tt) + 0.22 * np.sin(4 * np.pi * f0 * tt)
    x = np.tanh(1.5 * x)
    a = min(400, n // 4)
    x[:a] *= np.linspace(0, 1, a)
    x[-a:] *= np.linspace(1, 0, a)
    return lp(x, 240)


def impact(size=1.0):
    n = int(2.4 * SR)
    f = 34 + 100 * np.exp(-t_arr(n) / 0.08)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.6 * size)
    crack = lp(noise(n), 6000) * env(n, 0.0005, 0.05)
    body = bp(noise(n), 100, 1000) * env(n, 0.001, 0.2 * size)
    tail = hp(lp(noise(n), 9000), 2500) * env(n, 0.002, 0.5 * size) * 0.25
    return np.tanh(1.5 * (boom + 0.55 * crack + 0.5 * body + tail))


def bass_hit():
    n = int(2.2 * SR)
    f = 38 + 60 * np.exp(-t_arr(n) / 0.06)
    return lp(np.tanh(2.4 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(n, 0.002, 0.8), 320)


def whoosh(frames, lead=0.0):
    dur = frames / FPS + 0.22
    n = int(dur * SR)
    tt = np.linspace(0, 1, n)
    peak = (frames / FPS) / dur
    e = np.where(tt < peak, (tt / peak) ** 2.2, np.exp(-(tt - peak) / 0.08))
    x = sweep(noise(n), 300, 4200) * e
    return x * 1.3


def riser(sec, top=1.0):
    n = int(sec * SR)
    tt = np.linspace(0, 1, n)
    x = sweep(noise(n), 400, 9000) * 0.8 + np.sin(2 * np.pi * np.cumsum(140 * 2 ** (tt * 3.2)) / SR) * 0.22
    x *= tt ** 1.8 * top
    x[-200:] *= np.linspace(1, 0, 200)
    return x


def reverse_cymbal(sec):
    n = int(sec * SR)
    tt = np.linspace(0, 1, n)
    return hp(noise(n), 3000) * tt ** 3 * 0.8


def click():
    n = int(0.05 * SR)
    return hp(noise(n), 2500) * env(n, 0.0002, 0.003) * 0.8 + np.sin(2 * np.pi * 1200 * t_arr(n)) * env(n, 0.0005, 0.012) * 0.7


def tick(freq=3200):
    n = int(0.035 * SR)
    return hp(noise(n), 4000) * env(n, 0.0002, 0.005) * 0.7 + np.sin(2 * np.pi * freq * t_arr(n)) * env(n, 0.0004, 0.008) * 0.4


def blip(freq, d=0.08):
    n = int(d * SR)
    return np.sin(2 * np.pi * freq * t_arr(n)) * env(n, 0.001, d / 3.5)


def pop(f0=420, f1=1200):
    n = int(0.12 * SR)
    f = f0 + (f1 - f0) * (1 - np.exp(-t_arr(n) / 0.02))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.035)


def chime(notes, gap=0.07, d=0.3):
    n = int(1.4 * SR)
    x = np.zeros(n)
    for i, m in enumerate(notes):
        s = int(i * gap * SR)
        tt = t_arr(n - s)
        x[s:] += (np.sin(2 * np.pi * midi(m) * tt) + 0.28 * np.sin(4 * np.pi * midi(m) * tt)) * env(n - s, 0.002, d)
    return x


def shimmer(d=2.0):
    n = int(d * SR)
    tt = t_arr(n)
    x = sum(np.sin(2 * np.pi * midi(m) * tt + rng.random() * 6) * (0.6 + 0.4 * np.sin(2 * np.pi * (5 + m % 3) * tt)) for m in (86, 90, 93, 98))
    return x * env(n, 0.05, d / 3) / 4


def heartbeat():
    n = int(0.3 * SR)
    f = 52 + 34 * np.exp(-t_arr(n) / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.08)


def thump():
    n = int(0.16 * SR)
    f = 70 + 60 * np.exp(-t_arr(n) / 0.02)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.05)


# ------------------------------------------------------------------ MUSIC
music, drums = Bus(), Bus()
PROG = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 66]]  # Am7 Fmaj7 Cmaj7 G
ROOT_N = [45, 41, 36, 43]


def section_at(fr):
    for k, (a, b) in SECT.items():
        if a <= fr < b:
            return k
    return "cta"


def key_offset(sec):
    return 2 if sec in ("day3", "addons", "cta") else 0


groove_sections = {"title", "day1", "day2", "day3", "addons"}
kick_times = []

# --- pads / bass / arps, bar by bar
bars = int(np.ceil(DUR / BAR))
for b in range(bars):
    t0 = b * BAR
    fr0 = int(round(t0 * FPS))
    sec = section_at(fr0)
    off = key_offset(sec)
    ci = b % 4
    if sec == "hook":
        ci = 0
    if sec in ("rest1", "rest2"):
        ci = 0
    chord = [m + off for m in PROG[ci]]
    root = ROOT_N[ci] + off
    n = int((BAR + 0.6) * SR)
    if sec == "hook":
        fc = 500 + 900 * (t0 / 4.0)
        gain = 0.16
    elif sec in ("rest1", "rest2"):
        fc, gain = 700, 0.17
    elif sec == "cta" and fr0 >= 2880:
        fc, gain = 2600, 0.15
    else:
        fc, gain = 1700, 0.11
    x = pad_notes(chord, n, fc)
    fade = np.minimum(1, t_arr(n) / 0.3) * np.minimum(1, (n - np.arange(n)) / (0.6 * SR))
    music.add(t0, x * fade, gain, -0.2)
    music.add(t0 + 0.013, x * fade, gain, 0.2)
    # sub bass pattern
    if sec in groove_sections or (sec == "cta" and fr0 < 2880):
        pat = [(0, 1.0), (1.5, 0.5), (2, 1.0), (3.5, 0.5)] if sec != "addons" else [(0, 1.5), (2, 1.5)]
        for pos, ln in pat:
            nn = int(ln * BEAT * SR * 0.95)
            music.add(t0 + pos * BEAT, sub(midi(root), nn), 0.30 if sec != "addons" else 0.22)
            if sec in ("day2", "day3"):
                gr = lp(saw(midi(root + 12), nn), 700) * env(nn, 0.005, ln * BEAT * 0.5)
                music.add(t0 + pos * BEAT, gr, 0.06 if sec == "day2" else 0.09)
    if sec in ("rest1", "rest2", "hook"):
        nn = int(BAR * SR)
        music.add(t0, sub(midi(root - 12 + 12 if sec == "hook" else root), nn), 0.24)
    # arps
    step = BEAT / 4 if sec in ("day2", "day3") else BEAT / 2
    if sec in ("day1", "day2", "day3", "addons", "cta") and not (sec == "cta" and fr0 >= 2880):
        k = 0
        tt = t0
        notes = chord + [chord[0] + 12, chord[1] + 12]
        pat = [0, 2, 1, 3, 2, 4, 3, 5]
        while tt < t0 + BAR - 1e-6:
            m = notes[pat[k % len(pat)]] + 12
            g = {"day1": 0.035, "day2": 0.05, "day3": 0.06, "addons": 0.04, "cta": 0.04}[sec]
            music.add(tt, pluck(midi(m)), g, -0.4 + 0.8 * ((k * 3) % 5) / 4)
            tt += step
            k += 1
    # stabs on day3 bar starts
    if sec == "day3":
        nn = int(0.5 * SR)
        st = lp(pad_notes([m + 12 for m in chord[:3]], nn, 3200) * env(nn, 0.004, 0.16), 3200)
        music.add(t0, st, 0.18)
        music.add(t0 + 1.5 * BEAT, st, 0.12)

# --- drums
def is_groove(fr):
    s = section_at(fr)
    return s in groove_sections or (s == "cta" and fr < 2880)

K = kick()
t = 0.0
step = BEAT
while t < DUR - 1e-6:
    fr = int(round(t * FPS))
    s = section_at(fr)
    if is_groove(fr):
        beat_idx = int(round(t / BEAT)) % 4
        half = s == "addons"
        if (not half) or beat_idx in (0, 2):
            drums.add(t, K, 0.52 if s != "day3" else 0.60)
            kick_times.append(t)
        if beat_idx in (1, 3) and s != "addons":
            drums.add(t, clap(), 0.20 if s != "day3" else 0.26, 0.05)
        # hats
        if s in ("day2", "day3"):
            for q in range(4):
                v = 0.09 if q % 2 == 0 else 0.055
                if q == 2:
                    v = 0.075
                drums.add(t + q * BEAT / 4, hat(False), v, 0.25)
            if s == "day3":
                drums.add(t + BEAT / 2, hat(True), 0.06, -0.25)
        else:
            drums.add(t + BEAT / 2, hat(beat_idx == 3), 0.09, 0.25)
            if s in ("day1", "cta"):
                drums.add(t, hat(False), 0.04, 0.25)
    elif s == "hook":
        # heartbeat kick, half-time, rising
        beat_idx = int(round(t / BEAT))
        if beat_idx % 2 == 0:
            g = 0.10 + 0.22 * (t / 4.0)
            drums.add(t, heartbeat(), g)
            drums.add(t + 0.22, heartbeat(), g * 0.6)
        drums.add(t + BEAT / 2, tick(2600), 0.05 + 0.05 * (t / 4.0), 0.3 if int(round(t / BEAT)) % 2 else -0.3)
    elif s in ("rest1", "rest2"):
        beat_idx = int(round(t / BEAT)) % 4
        if beat_idx in (0, 2):
            drums.add(t, heartbeat(), 0.24)
            drums.add(t + 0.22, heartbeat(), 0.14)
    t += step

# snare-roll fills into the day changes (last bar before 1080 / 1800 / cta) and the last bar of each day
for end_fr in (960, 1680, 2400):
    st = f2s(end_fr) - BAR
    tt = st
    while tt < f2s(end_fr) - 1e-6:
        p = (tt - st) / BAR
        sn = snare()
        drums.add(tt, sn, 0.10 + 0.20 * p)
        tt += BEAT / 2 if p < 0.4 else BEAT / 4 if p < 0.85 else BEAT / 8

# ------------------------------------------------------------------ SFX
sfx = Bus()

# hook: riser + reverse cymbal into the title drop
sfx.add(0, riser(f2s(240) - 0.02, 0.9), 0.22)
sfx.add(f2s(240) - 1.0, reverse_cymbal(1.0), 0.20)
sfx.add(f2s(15), tick(2000), 0.06)

# chapter impacts / bass hits / crashes
for fr, size, g in ((240, 1.0, 0.55), (360, 1.0, 0.55), (1080, 1.0, 0.55), (1800, 1.1, 0.60), (2670, 1.3, 0.66), (2400, 0.6, 0.35)):
    sfx.add(f2s(fr), impact(size), g)
    sfx.add(f2s(fr), bass_hit(), 0.42 if fr != 2400 else 0.25)
    n = int(1.6 * SR)
    sfx.add(f2s(fr), hp(noise(n), 5000) * env(n, 0.002, 0.7) * 0.5, 0.10)

# whooshes on the brand slash wipes and section changes (peak lands on the cut)
for cut in (360, 1080, 1800):
    sfx.add(f2s(cut) - 0.55, whoosh(28), 0.34)
for fr in (960, 1680, 2400, 2640):
    sfx.add(f2s(fr) - 0.4, whoosh(20), 0.26)
# risers before the second/third day and the logo slam
for fr, sec in ((1080, 2.0), (1800, 2.0), (2670, 2.0)):
    sfx.add(f2s(fr) - sec, riser(sec, 0.55), 0.20)

# every full-bleed cut: a soft low punch (matches the zoom punch), card pop = tiny air
for s in D["shots"]:
    fr = s["from"]
    if fr < 360 or fr in (360, 1080, 1800, 2640):
        continue
    if s["layout"] == "full":
        sfx.add(f2s(fr), thump(), 0.16)
    else:
        sfx.add(f2s(fr) - 0.02, pop(300, 900), 0.10)
        sfx.add(f2s(fr) - 0.05, whoosh(6), 0.07)

# title-scene cards & chips
for fr in (246, 253, 260):
    sfx.add(f2s(fr), pop(300 + (fr - 246) * 20, 900), 0.16)
for i in range(3):
    sfx.add(f2s(240 + 40 + i * 9), blip(midi(88 + i * 4), 0.08), 0.12, -0.3 + 0.3 * i)

# exercise lists
for i, lf in enumerate(LIST_FROM):
    sfx.add(f2s(lf), whoosh(12), 0.16)
    for j in range(LIST_ITEMS[i]):
        sfx.add(f2s(lf + 10 + j * 9), blip(midi(84 + [0, 2, 4, 5, 7, 9][j]), 0.07), 0.14, 0.4)
        sfx.add(f2s(lf + 10 + j * 9), tick(3400), 0.10)

# highlighted captions: bright ding
for fr in HL_CAPTIONS:
    sfx.add(f2s(fr), chime((86, 93), 0.06, 0.25), 0.11)

# rest days: deep breath swell
for fr in (960, 1680):
    n = int(1.6 * SR)
    swell = lp(noise(n), 900) * np.sin(np.linspace(0, np.pi, n)) ** 2
    sfx.add(f2s(fr) + 0.1, swell, 0.20)

# add-on chips
for fr in ADDON_LABELS:
    sfx.add(f2s(fr), pop(500, 1500), 0.20)
    sfx.add(f2s(fr), chime((81, 88), 0.06, 0.2), 0.08)

# CTA
sfx.add(f2s(CTA["logo"]) + 0.1, shimmer(2.2), 0.13)
for i in range(CTA["nchars"]):
    sfx.add(f2s(CTA["type0"] + i * 4), mix(tick(3000 + 40 * i), (click(), 0.5)), 0.20)
sfx.add(f2s(CTA["button"]), pop(400, 1300), 0.24)
sfx.add(f2s(CTA["click"]), mix(click(), (pop(600, 1600), 0.6), (chime((81, 88, 93)), 0.6)), 0.34)
# final resolve chord
n = int((DUR - f2s(3000) + 1) * SR)
fin = pad_notes([50 + 2, 62 + 2, 66 + 2, 69 + 2, 76 + 2], n, 3000) * np.minimum(1, t_arr(n) / 0.08) * np.exp(-t_arr(n) / 1.6)
music.add(f2s(3000), fin, 0.26)

# ------------------------------------------------------------------ MIX
def verb(x, secs=1.6):
    n = int(secs * SR)
    ir = lp(noise(n) * np.exp(-t_arr(n) / (secs / 5)), 5500)
    ir /= np.sqrt(np.sum(ir ** 2))
    return signal.fftconvolve(x, ir)[: len(x)]


mus, drm, fx = music.x[:, :N], drums.x[:, :N], sfx.x[:, :N]

# sidechain pump on the music (pad/bass/arp) from the kicks
pump = np.ones(N)
for kt in kick_times:
    s = int(kt * SR)
    n = int(0.26 * SR)
    shape = 1 - 0.62 * np.exp(-t_arr(n) / 0.07)
    e = min(N, s + n)
    pump[s:e] = np.minimum(pump[s:e], shape[: e - s])
mus = mus * (0.4 + 0.6 * pump)

mus = mus + np.stack([verb(mus[0]), verb(mus[1])]) * 0.30
drm = drm + np.stack([verb(drm[0], 0.8), verb(drm[1], 0.8)]) * 0.10
fx = fx + np.stack([verb(fx[0], 2.2), verb(fx[1], 2.2)]) * 0.24

# gentle dip in the voice band (1.5-4 kHz) on music+drums so a voiceover sits clearly
dip = signal.butter(2, [1500, 4000], "bandstop", fs=SR, output="sos")
bed = mus + drm
bed = 0.62 * bed + 0.38 * np.stack([signal.sosfilt(dip, bed[0]), signal.sosfilt(dip, bed[1])])

out = bed + fx
out = np.stack([hp(out[0], 28), hp(out[1], 28)])
fade = int(1.0 * SR)
out[:, -fade:] *= np.linspace(1, 0, fade) ** 1.5
out = np.tanh(out * 1.12) / np.tanh(1.12)
peak = np.max(np.abs(out)) + 1e-9
out = out / peak * 0.64


def write(path, x):
    wavfile.write(path, SR, (np.clip(x, -1, 1).T * 32767).astype(np.int16))


os.makedirs(os.path.join(ROOT, "public", "audio"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "audio", "stems"), exist_ok=True)
write(os.path.join(ROOT, "public", "audio", "split.wav"), out)
write(os.path.join(ROOT, "audio", "stems", "split_music.wav"), bed / peak * 0.64)
write(os.path.join(ROOT, "audio", "stems", "split_sfx.wav"), fx / peak * 0.64)
print(f"split.wav {DUR:.1f}s  rms {20 * np.log10(np.sqrt(np.mean(out ** 2))):.1f} dBFS  kicks {len(kick_times)}")
