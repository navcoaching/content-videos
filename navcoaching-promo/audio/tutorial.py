"""
Nav Coaching site tutorial — calm music bed + UI sounds placed from src/tutorial/tutorial.json.

Taps -> soft click, page navigation -> swipe, scrolls -> air swish scaled by distance,
highlight rings -> focus chime, chapter starts -> soft whoosh + ding, end card -> resolve.
Output: public/audio/tutorial.wav (+ stems in audio/stems/).
"""
import json
import os
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, "src", "tutorial", "tutorial.json")))
M = json.load(open(os.path.join(ROOT, "public", "tut", "manifest.json")))
SR, FPS = 48000, T["fps"]
chapters, start = [], 0
for c in T["chapters"]:
    chapters.append((start, c))
    start += c["dur"]
DUR = start / FPS
N = int(DUR * SR)
rng = np.random.default_rng(5)
BEAT = 60 / 96
BAR = BEAT * 4


def t_arr(n):
    return np.arange(n) / SR


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def env(n, a, d):
    t = t_arr(n)
    return np.clip(t / max(a, 1e-4), 0, 1) * np.exp(-np.maximum(t - a, 0) / d)


def filt(kind, fc, x, order=2):
    return signal.sosfilt(signal.butter(order, fc, kind, fs=SR, output="sos"), x)


def noise(n):
    return rng.standard_normal(n)


class Bus:
    def __init__(self):
        self.x = np.zeros((2, N + SR * 4))

    def add(self, sec, mono, gain=1.0, pan=0.0):
        s = int(sec * SR)
        gl, gr = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
        e = min(self.x.shape[1], s + len(mono))
        if e <= max(0, s):
            return
        seg = mono[max(0, -s): e - s] * gain
        self.x[0, max(0, s):e] += seg * gl
        self.x[1, max(0, s):e] += seg * gr


# ---------------------------------------------------------------- music (calm, looped progression)
music = Bus()
PROG = [[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 69]]  # Dmaj7 Bm7 Gmaj7 A
ROOTS = [38, 47, 43, 45]
end_card = (chapters[-1][0] + 230) / FPS


def pad(freqs, n, fc):
    x = np.zeros(n)
    for f in freqs:
        for det in (-0.07, 0.07):
            x += 2 * ((f * 2 ** (det / 12) * t_arr(n) + rng.random()) % 1) - 1
    return filt("low", fc, x / (2 * len(freqs)))


def pluck(f):
    n = int(0.5 * SR)
    tt = t_arr(n)
    x = np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / 0.05)
    return filt("low", 3000, x * env(n, 0.003, 0.18))


t, b = 0.0, 0
while t < DUR:
    ch = PROG[b % 4]
    n = int((BAR + 0.6) * SR)
    x = pad([midi(m) for m in ch], n, 1400)
    fade = np.minimum(1, t_arr(n) / 0.4) * np.minimum(1, (n - np.arange(n)) / (0.6 * SR))
    music.add(t, x * fade, 0.10, -0.2)
    music.add(t + 0.013, x * fade, 0.10, 0.2)
    # soft sub
    nb = int(BAR * SR)
    sub = np.sin(2 * np.pi * midi(ROOTS[b % 4]) * t_arr(nb)) * np.minimum(1, (nb - np.arange(nb)) / 800) * np.minimum(1, np.arange(nb) / 800)
    music.add(t, filt("low", 160, sub), 0.08)
    if 4 <= t < end_card:
        for k in range(8):  # 8th-note arp
            m = (ch + [ch[0] + 12])[(k * 3) % 5] + 12
            music.add(t + k * BEAT / 2, pluck(midi(m)), 0.028, -0.4 + 0.8 * ((k * 3) % 5) / 4)
        for k in range(4):  # half-time kick + light shaker
            if k in (0, 2):
                nk = int(0.35 * SR)
                fk = 48 + 70 * np.exp(-t_arr(nk) / 0.03)
                music.add(t + k * BEAT, np.sin(2 * np.pi * np.cumsum(fk) / SR) * env(nk, 0.001, 0.12), 0.09)
            ns = int(0.07 * SR)
            music.add(t + k * BEAT + BEAT / 2, filt("high", 7000, noise(ns)) * env(ns, 0.005, 0.02), 0.015, 0.3)
    t += BAR
    b += 1

# final chord under the end card
n = int((DUR - end_card + 1) * SR)
fin = pad([midi(m) for m in (50, 62, 66, 69, 76)], n, 2400) * np.minimum(1, t_arr(n) / 0.05) * np.exp(-t_arr(n) / 2.4)
music.add(end_card, fin, 0.3)

# ---------------------------------------------------------------- UI sounds
sfx = Bus()


def click():
    n = int(0.06 * SR)
    return filt("high", 2500, noise(n)) * env(n, 0.0002, 0.003) * 0.8 + np.sin(2 * np.pi * 1250 * t_arr(n)) * env(n, 0.0005, 0.012) * 0.6


def swish(sec, lo=500, hi=3500):
    n = int(sec * SR)
    tt = np.linspace(0, 1, n)
    e = np.sin(np.pi * tt) ** 1.5
    x = noise(n) * e
    # moving band via two static bands crossfaded
    return (filt("band", [lo, lo * 2.5], x) * (1 - tt) + filt("band", [hi / 2.5, hi], x) * tt) * 1.4


def chime(notes, gap=0.07, d=0.3):
    n = int(1.2 * SR)
    x = np.zeros(n)
    for i, m in enumerate(notes):
        s = int(i * gap * SR)
        tt = t_arr(n - s)
        x[s:] += (np.sin(2 * np.pi * midi(m) * tt) + 0.25 * np.sin(4 * np.pi * midi(m) * tt)) * env(n - s, 0.002, d)
    return x


def page_of(view):
    return view.get("page") or M["states"][view["state"]]["page"]


last_page = None
for cs, c in chapters:
    sec0 = cs / FPS
    if cs > 0:
        sfx.add(sec0 - 0.35, swish(0.5, 300, 2500), 0.18)
        sfx.add(sec0, chime((74, 81) if c["key"] != "outro" else (74, 78, 81, 86), 0.08, 0.35), 0.12)
    for bt in c["beats"]:
        sec = (cs + bt["t"]) / FPS
        if "tap" in bt:
            sfx.add(sec, click(), 0.30)
        if "ring" in bt:
            sfx.add(sec, chime((86, 90), 0.05, 0.2), 0.07)
        if "view" in bt:
            p = page_of(bt["view"])
            if last_page is not None and p != last_page:
                sfx.add(sec, swish(0.28, 800, 5000), 0.12)
            last_page = p
        if "scroll" in bt and "view" not in bt:
            d = bt.get("dur", 60) / FPS
            sfx.add(sec, swish(max(0.25, d), 400, 2200), 0.09)
# end card
sfx.add(end_card, chime((74, 78, 81, 86, 90), 0.09, 0.5), 0.16)

# ---------------------------------------------------------------- mix
mus, fx = music.x[:, :N], sfx.x[:, :N]


def verb(x, secs=1.6):
    n = int(secs * SR)
    ir = filt("low", 5000, noise(n) * np.exp(-t_arr(n) / (secs / 5)))
    ir /= np.sqrt(np.sum(ir ** 2))
    return signal.fftconvolve(x, ir)[: len(x)]


mus = mus + np.stack([verb(mus[0]), verb(mus[1])]) * 0.3
fx = fx + np.stack([verb(fx[0], 1.2), verb(fx[1], 1.2)]) * 0.15
out = mus + fx
fade = int(0.8 * SR)
out[:, -fade:] *= np.linspace(1, 0, fade) ** 1.5
out = np.tanh(out * 1.1) / np.tanh(1.1)
peak = np.max(np.abs(out)) + 1e-9
out = out / peak * 0.85


def write(p, x):
    wavfile.write(p, SR, (np.clip(x, -1, 1).T * 32767).astype(np.int16))


os.makedirs(os.path.join(ROOT, "audio", "stems"), exist_ok=True)
write(os.path.join(ROOT, "public", "audio", "tutorial.wav"), out)
write(os.path.join(ROOT, "audio", "stems", "tutorial_music.wav"), mus / peak * 0.85)
write(os.path.join(ROOT, "audio", "stems", "tutorial_sfx.wav"), fx / peak * 0.85)
print(f"tutorial.wav {DUR:.1f}s rms {20*np.log10(np.sqrt(np.mean(out**2))):.1f} dBFS")
