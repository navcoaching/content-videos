"""
Nav Coaching "user journey" video — procedural music bed + UI sound design.

Built to sit UNDER a voiceover recorded later:
  * music is kept low and low-passed so the 1–4 kHz voice band stays clear,
  * every sound is placed from src/journey/journey.json (same file the scenes read).

Outputs:
  public/audio/journey.wav          full mix (music + sfx)
  audio/stems/journey_music.wav     music only
  audio/stems/journey_sfx.wav       sound effects only
"""
import json
import os
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = json.load(open(os.path.join(ROOT, "src", "journey", "journey.json")))
SR = 48000
FPS = J["fps"]
BEAT = 60.0 / J["bpm"]  # 0.5 s = 30 frames
BAR = BEAT * 4
DUR = J["durationInFrames"] / FPS
N = int(DUR * SR)
rng = np.random.default_rng(11)


def f2s(fr):
    return int(round(fr / FPS * SR))


def t_arr(n):
    return np.arange(n) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a, d):
    t = t_arr(n)
    return np.clip(t / max(a, 1e-4), 0, 1) * np.exp(-np.maximum(t - a, 0) / d)


def sos(kind, fc, order=2):
    return signal.butter(order, fc, kind, fs=SR, output="sos")


def lp(x, fc):
    return signal.sosfilt(sos("low", min(fc, SR * 0.45)), x)


def hp(x, fc):
    return signal.sosfilt(sos("high", fc), x)


def bp(x, lo, hi):
    return signal.sosfilt(sos("band", [lo, min(hi, SR * 0.45)]), x)


def noise(n):
    return rng.standard_normal(n)


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


def mix(*parts):
    n = max(len(p[0] if isinstance(p, tuple) else p) for p in parts)
    o = np.zeros(n)
    for p in parts:
        x, w = p if isinstance(p, tuple) else (p, 1.0)
        o[: len(x)] += x * w
    return o


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N + SR * 4))

    def add(self, start, mono, gain=1.0, pan=0.0):
        gl, gr = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
        s = max(0, start)
        e = min(self.x.shape[1], start + len(mono))
        if e <= s:
            return
        seg = mono[s - start: e - start] * gain
        self.x[0, s:e] += seg * gl
        self.x[1, s:e] += seg * gr


# ------------------------------------------------------------------ MUSIC
music = Bus()
S = J["segments"]
t_pivot = S["pivot"][0] / FPS
t_logo = J["logoSeq"]["hit"] / FPS
t_groove = S["ch1"][0] / FPS
t_outro = S["outro"][0] / FPS
t_start = J["outro"]["start"] / FPS
t_brand = J["outro"]["logo"] / FPS

# D major: D  A  Bm  G  (hook sits on Bm for tension)
PROG = [[62, 66, 69], [57, 61, 64], [59, 62, 66], [55, 59, 62]]
ROOTS = [38, 45, 47, 43]


def chord_at(t):
    if t < t_pivot:
        return [59, 62, 66], 47  # Bm
    i = int((t - t_pivot) // BAR) % 4
    return PROG[i], ROOTS[i]


def pad_note(freq, n, bright):
    x = np.zeros(n)
    for det in (-0.08, 0.0, 0.08):
        ph = rng.random()
        x += 2 * ((freq * 2 ** (det / 12) * t_arr(n) + ph) % 1.0) - 1
    return lp(x / 3, bright)


# pad: one block per bar
t = 0.0
while t < DUR:
    ch, _ = chord_at(t + 0.01)
    n = int((BAR + 0.5) * SR)
    bright = 900 if t < t_pivot else 1800
    if t_outro <= t < t_brand:
        bright = 1400
    x = sum(pad_note(midi(m), n, bright) for m in ch) / len(ch)
    e = np.minimum(1, t_arr(n) / 0.35) * np.minimum(1, (n - np.arange(n)) / (0.5 * SR))
    g = 0.12 if t < t_groove else 0.07
    music.add(int(t * SR), x * e, gain=g, pan=-0.15)
    music.add(int(t * SR) + int(0.012 * SR), x * e, gain=g, pan=0.15)
    t += BAR

# hook: clock tick + heartbeat (tension)
t = 0.0
while t < t_pivot - 0.2:
    n = int(0.05 * SR)
    tick = hp(noise(n), 3000) * env(n, 0.0005, 0.006) + np.sin(2 * np.pi * 1800 * t_arr(n)) * env(n, 0.0005, 0.01) * 0.3
    music.add(int(t * SR), tick, gain=0.12, pan=0.3 if int(t / BEAT) % 2 else -0.3)
    if int(round(t / BEAT)) % 2 == 0:
        n2 = int(0.3 * SR)
        hb = np.sin(2 * np.pi * np.cumsum(55 + 30 * np.exp(-t_arr(n2) / 0.03)) / SR) * env(n2, 0.002, 0.08)
        music.add(int(t * SR), hb, gain=0.22)
        music.add(int((t + 0.22) * SR), hb, gain=0.14)
    t += BEAT

# groove: half-time kick, soft clap, shaker, pluck arp, sub — from ch1 until the outro breakdown
def kick():
    n = int(0.4 * SR)
    f = 46 + 90 * np.exp(-t_arr(n) / 0.03)
    return np.tanh(1.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.14))


def clap():
    n = int(0.3 * SR)
    e = sum(np.concatenate([np.zeros(int(o * SR)), env(n - int(o * SR), 0.0005, 0.012 if k < 2 else 0.07)]) for k, o in enumerate((0, 0.01, 0.02)))
    return bp(noise(n), 900, 2800) * e


def shaker():
    n = int(0.08 * SR)
    return hp(noise(n), 6500) * env(n, 0.006, 0.02)


def pluck(freq):
    n = int(0.45 * SR)
    tt = t_arr(n)
    x = np.sin(2 * np.pi * freq * tt) + 0.35 * np.sin(2 * np.pi * 2 * freq * tt) * np.exp(-tt / 0.05) + 0.15 * np.sin(2 * np.pi * 3 * freq * tt) * np.exp(-tt / 0.03)
    return lp(x * env(n, 0.002, 0.16), 3200)


groove_end = t_outro
t = t_groove
k = 0
while t < groove_end - 1e-6:
    ch, root = chord_at(t + 0.01)
    beat_in_bar = k % 4
    if beat_in_bar in (0, 2) and not (beat_in_bar == 2 and k % 8 == 6):
        music.add(int(t * SR), kick(), gain=0.15)
    if beat_in_bar == 2:
        music.add(int(t * SR), clap(), gain=0.05)
    for h in (0, 0.5):
        music.add(int((t + h * BEAT) * SR), shaker(), gain=0.03 if h else 0.018, pan=0.35)
    # 8th-note arp (upper register, gentle)
    notes = ch + [ch[0] + 12]
    for h in (0, 0.5):
        m = notes[(k * 2 + int(h * 2)) % len(notes)] + 12
        music.add(int((t + h * BEAT) * SR), pluck(midi(m)), gain=0.035, pan=-0.35 + 0.7 * ((k * 2 + int(h * 2)) % 4) / 3)
    # sub on the beat
    n = int(BEAT * SR)
    sub = np.sin(2 * np.pi * midi(root - 12 + 12) * t_arr(n)) * np.minimum(1, (n - np.arange(n)) / 400) * np.minimum(1, np.arange(n) / 200)
    music.add(int(t * SR), lp(sub, 180), gain=0.07)
    t += BEAT
    k += 1

# pivot: bright bell arp introduces the "one place" moment (before the groove)
t = t_pivot
k = 0
while t < t_logo - 1e-6:
    ch, _ = chord_at(t + 0.01)
    m = (ch + [ch[0] + 12])[k % 4] + 24
    music.add(int(t * SR), pluck(midi(m)), gain=0.07, pan=-0.3 + 0.2 * (k % 4))
    t += BEAT / 2
    k += 1

# outro: sparse plucks until the brand hit, then a sustained Dadd9 chord
t = t_outro
k = 0
while t < t_brand - 1e-6:
    ch, _ = chord_at(t + 0.01)
    m = (ch + [ch[0] + 12])[k % 4] + 12
    music.add(int(t * SR), pluck(midi(m)), gain=0.06, pan=-0.3 + 0.2 * (k % 4))
    t += BEAT
    k += 1
n = int((DUR - t_brand + 1) * SR)
final = sum(pad_note(midi(m), n, 2600) for m in (50, 62, 66, 69, 76)) / 5
final *= np.minimum(1, t_arr(n) / 0.05) * np.exp(-t_arr(n) / 2.2)
music.add(int(t_brand * SR), final, gain=0.30)

# ------------------------------------------------------------------ SFX
sfx = Bus()


def whoosh(frames):
    dur = frames / FPS + 0.25
    n = int(dur * SR)
    tt = np.linspace(0, 1, n)
    peak = (frames / FPS) / dur
    e = np.where(tt < peak, (tt / peak) ** 2.2, np.exp(-(tt - peak) / 0.08))
    return sweep(noise(n), 400, 3800) * e * 1.3


def riser(frames):
    n = int(frames / FPS * SR)
    tt = np.linspace(0, 1, n)
    x = sweep(noise(n), 500, 7000) * 0.7 + np.sin(2 * np.pi * np.cumsum(220 * 2 ** (tt * 2)) / SR) * 0.2
    x *= tt ** 1.8
    x[-200:] *= np.linspace(1, 0, 200)
    return x


def impact(size=1.0):
    n = int(1.6 * SR)
    f = 40 + 80 * np.exp(-t_arr(n) / 0.07)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.4 * size)
    return np.tanh(1.2 * (boom + lp(noise(n), 3000) * env(n, 0.0005, 0.03) * 0.4))


def click():
    n = int(0.05 * SR)
    return hp(noise(n), 2500) * env(n, 0.0002, 0.003) + np.sin(2 * np.pi * 1100 * t_arr(n)) * env(n, 0.0005, 0.01) * 0.7


def tick():
    n = int(0.03 * SR)
    return hp(noise(n), 4000) * env(n, 0.0002, 0.004) * 0.8 + np.sin(2 * np.pi * 3000 * t_arr(n)) * env(n, 0.0005, 0.006) * 0.3


def pop(f0=420, f1=1100):
    n = int(0.12 * SR)
    f = f0 + (f1 - f0) * (1 - np.exp(-t_arr(n) / 0.02))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.035)


def blip(freq, d=0.08):
    n = int(d * SR)
    return np.sin(2 * np.pi * freq * t_arr(n)) * env(n, 0.001, d / 3.5)


def chime(notes, gap=0.07):
    n = int(1.2 * SR)
    x = np.zeros(n)
    for i, m in enumerate(notes):
        s = int(i * gap * SR)
        tt = t_arr(n - s)
        x[s:] += (np.sin(2 * np.pi * midi(m) * tt) + 0.3 * np.sin(4 * np.pi * midi(m) * tt)) * env(n - s, 0.002, 0.28)
    return x


def shimmer(d=1.6):
    n = int(d * SR)
    tt = t_arr(n)
    x = sum(np.sin(2 * np.pi * midi(m) * tt + rng.random() * 6) * (0.6 + 0.4 * np.sin(2 * np.pi * (5 + m % 3) * tt)) for m in (86, 90, 93, 98))
    return x * env(n, 0.05, d / 3) / 4


def paper():
    n = int(0.16 * SR)
    return bp(noise(n), 1500, 6000) * env(n, 0.01, 0.04)


def downer():
    n = int(0.7 * SR)
    f = 420 * np.exp(-t_arr(n) / 0.25) + 60
    return np.tanh(2 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))) * env(n, 0.005, 0.25) * 0.4


def typing():
    return mix(tick(), (click(), 0.4))


def bass():
    n = int(1.8 * SR)
    f = 40 + 50 * np.exp(-t_arr(n) / 0.06)
    return lp(np.tanh(2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(n, 0.002, 0.6), 300)


HK, PV, LG = J["hook"], J["pivot"], J["logoSeq"]
C1, C2, C3, C4, C5, C6, O = (J[k] for k in ("ch1", "ch2", "ch3", "ch4", "ch5", "ch6", "outro"))

for s_, fr in J["whooshes"]:
    sfx.add(f2s(s_), whoosh(fr), gain=0.28)
for s_, fr in J["risers"]:
    sfx.add(f2s(s_), riser(fr), gain=0.22)

# hook
for i, fr in enumerate(HK["cards"]):
    sfx.add(f2s(fr), mix(pop(300 + 40 * i, 800 + 60 * i), (paper(), 0.6)), gain=0.20, pan=-0.5 + (i % 4) / 3)
for fr, _ in HK["lines"]:
    sfx.add(f2s(fr), tick(), gain=0.25)
sfx.add(f2s(HK["lines2"][0][0]), impact(0.5), gain=0.35)
sfx.add(f2s(HK["lines2"][1][0]), downer(), gain=0.30)
# pivot
sfx.add(f2s(PV["lines"][0][0]), click(), gain=0.35)
sfx.add(f2s(PV["lines"][1][0]), mix(impact(0.5), (shimmer(1.4), 0.5)), gain=0.38)
for fr, _ in PV["lines"][2:]:
    sfx.add(f2s(fr), tick(), gain=0.22)
sfx.add(f2s(PV["window"]), pop(200, 600), gain=0.25)
sfx.add(f2s(PV["phone"]), pop(300, 900), gain=0.22)
# logo
sfx.add(f2s(LG["hit"]), impact(1.0), gain=0.50)
sfx.add(f2s(LG["hit"]), bass(), gain=0.40)
sfx.add(f2s(LG["hit"]) + int(0.1 * SR), shimmer(2.0), gain=0.16)
sfx.add(f2s(LG["line"]), tick(), gain=0.22)
sfx.add(f2s(LG["pill"]), pop(500, 1300), gain=0.25)
# ch1
for fr in [C1["quizClick"], *C1["answers"], C1["cta"]]:
    sfx.add(f2s(fr), click(), gain=0.40)
for i, fr in enumerate(C1["answers"]):
    sfx.add(f2s(fr) + 200, blip(midi(79 + [0, 2, 4, 7][i]), 0.07), gain=0.16)
sfx.add(f2s(C1["scroll"]), whoosh(12), gain=0.12)
sfx.add(f2s(C1["result"] - 22), whoosh(20), gain=0.12)
sfx.add(f2s(C1["result"]), chime((74, 78, 81, 86)), gain=0.22)
for fr in C1["why"]:
    sfx.add(f2s(fr), pop(600, 1400), gain=0.14)
# ch2
for fr in C2["typeName"]:
    sfx.add(f2s(fr), typing(), gain=0.26)
for fr in [C2["next1"], C2["next2"], C2["next3"], *C2["choices"]]:
    sfx.add(f2s(fr), click(), gain=0.40)
sfx.add(f2s(C2["healthSpot"]), chime((81, 86), 0.09), gain=0.14)
sfx.add(f2s(C2["submit"]), mix(click(), (pop(500, 1500), 0.6)), gain=0.42)
# ch3
sfx.add(f2s(C3["created"]), chime((74, 78, 81)), gain=0.22)
sfx.add(f2s(C3["copy"]), mix(click(), (blip(1760, 0.06), 0.5)), gain=0.40)
sfx.add(f2s(C3["upload"]), click(), gain=0.40)
sfx.add(f2s(C3["fileIn"]), pop(400, 1200), gain=0.25)
sfx.add(f2s(C3["review"]), blip(1318, 0.12), gain=0.20)
# ch4
for i, fr in enumerate(C4["steps"]):
    sfx.add(f2s(fr), blip(midi(76 + [0, 2, 4, 7, 12][i]), 0.1), gain=0.22)
sfx.add(f2s(C4["steps"][-1]), chime((81, 86, 90)), gain=0.18)
sfx.add(f2s(C4["files"]), pop(300, 900), gain=0.22)
for fr in C4["fileItems"]:
    sfx.add(f2s(fr), tick(), gain=0.22)
# ch5
for i, fr in enumerate(C5["rows"]):
    sfx.add(f2s(fr), blip(1500 + 90 * i, 0.06), gain=0.16)
for i, fr in enumerate(C5["weeks"]):
    sfx.add(f2s(fr), pop(500 + 80 * i, 1300 + 80 * i), gain=0.20)
sfx.add(f2s(C5["reply"]), chime((78, 83, 86)), gain=0.22)
# ch6
for fr in C6["type"]:
    sfx.add(f2s(fr), typing(), gain=0.26)
sfx.add(f2s(C6["goal"]), click(), gain=0.40)
n = f2s(C6["calcEnd"]) - f2s(C6["calc"])
tt = np.linspace(0, 1, n)
roll = np.sin(2 * np.pi * np.cumsum(600 + 900 * tt) / SR) * (0.3 + 0.7 * tt) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 18 * tt * n / SR)))
roll[-200:] *= np.linspace(1, 0, 200)
sfx.add(f2s(C6["calc"]), lp(roll, 3000), gain=0.07)
sfx.add(f2s(C6["calcEnd"]), chime((79, 83, 86)), gain=0.20)
sfx.add(f2s(C6["plans"]), pop(300, 800), gain=0.2)
sfx.add(f2s(C6["download"]), mix(click(), (pop(700, 1600), 0.5)), gain=0.40)
# outro
for i, fr in enumerate(O["cards"]):
    sfx.add(f2s(fr), pop(350 + 60 * i, 1000 + 60 * i), gain=0.24)
sfx.add(f2s(O["start"]), impact(0.7), gain=0.40)
sfx.add(f2s(O["logo"]), impact(0.9), gain=0.42)
sfx.add(f2s(O["logo"]), bass(), gain=0.32)
sfx.add(f2s(O["logo"]) + int(0.08 * SR), shimmer(2.2), gain=0.16)
for fr in O["urlType"]:
    sfx.add(f2s(fr), typing(), gain=0.24)
sfx.add(f2s(O["button"]), pop(400, 1200), gain=0.24)
sfx.add(f2s(O["click"]), mix(click(), (chime((81, 86, 93)), 0.6)), gain=0.40)

# ------------------------------------------------------------------ MIX
def reverb(x, secs=1.6):
    n = int(secs * SR)
    ir = lp(noise(n) * np.exp(-t_arr(n) / (secs / 5)), 5000)
    ir /= np.sqrt(np.sum(ir ** 2))
    return signal.fftconvolve(x, ir)[: len(x)]


mus = music.x[:, :N]
fx = sfx.x[:, :N]
mus = mus + np.stack([reverb(mus[0]), reverb(mus[1])]) * 0.3
fx = fx + np.stack([reverb(fx[0], 1.8), reverb(fx[1], 1.8)]) * 0.18
# keep the voice band open: gentle dip around 2.5 kHz on the music
dip = signal.butter(2, [1500, 4000], "bandstop", fs=SR, output="sos")
mus = 0.6 * mus + 0.4 * np.stack([signal.sosfilt(dip, mus[0]), signal.sosfilt(dip, mus[1])])

out = mus + fx
out = np.stack([hp(out[0], 30), hp(out[1], 30)])
fade = int(0.6 * SR)
out[:, -fade:] *= np.linspace(1, 0, fade) ** 1.5
out = np.tanh(out * 1.1) / np.tanh(1.1)
peak = np.max(np.abs(out)) + 1e-9
out = out / peak * 0.85  # leave headroom for the voiceover mix


def write(path, x, norm=None):
    y = x / (np.max(np.abs(x)) + 1e-9) * norm if norm else x
    wavfile.write(path, SR, (np.clip(y, -1, 1).T * 32767).astype(np.int16))


os.makedirs(os.path.join(ROOT, "public", "audio"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "audio", "stems"), exist_ok=True)
write(os.path.join(ROOT, "public", "audio", "journey.wav"), out)
write(os.path.join(ROOT, "audio", "stems", "journey_music.wav"), mus / peak * 0.85)
write(os.path.join(ROOT, "audio", "stems", "journey_sfx.wav"), fx / peak * 0.85)
rms = 20 * np.log10(np.sqrt(np.mean(out ** 2)))
print(f"wrote journey.wav {DUR:.1f}s  rms {rms:.1f} dBFS")
