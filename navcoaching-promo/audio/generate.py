"""
Nav Coaching promo — procedural soundtrack + sound design.

Everything is synthesized from scratch (no samples, royalty-free) and every
sound is placed from src/cues.json, the same file the Remotion scenes read,
so picture and sound share one timeline.

Output: public/audio/soundtrack.wav (48 kHz, 24-bit-ish float -> 16-bit stereo)
"""
import json
import os
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUES = json.load(open(os.path.join(ROOT, "src", "cues.json")))
SR = 48000
FPS = CUES["fps"]
BPM = CUES["bpm"]
BEAT = 60.0 / BPM
DUR = CUES["durationInFrames"] / FPS
N = int(DUR * SR)
rng = np.random.default_rng(7)


def f2s(frame):
    return int(round(frame / FPS * SR))


def t_arr(n):
    return np.arange(n) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


class Bus:
    def __init__(self):
        self.l = np.zeros(N + SR * 4)
        self.r = np.zeros(N + SR * 4)

    def add(self, start, mono=None, left=None, right=None, gain=1.0, pan=0.0):
        if mono is not None:
            gl = np.cos((pan + 1) * np.pi / 4)
            gr = np.sin((pan + 1) * np.pi / 4)
            left, right = mono * gl * 1.414, mono * gr * 1.414
        n = len(left)
        s = max(0, start)
        off = s - start
        e = min(len(self.l), start + n)
        if e <= s:
            return
        self.l[s:e] += left[off:off + (e - s)] * gain
        self.r[s:e] += right[off:off + (e - s)] * gain

    def stereo(self):
        return np.stack([self.l, self.r])


def env_ad(n, a, d, curve=4.0):
    """attack seconds, exp decay time constant d seconds"""
    t = t_arr(n)
    att = np.clip(t / max(a, 1e-4), 0, 1)
    dec = np.exp(-np.maximum(t - a, 0) / d)
    return att * dec


def lp(x, fc, order=2):
    sos = signal.butter(order, min(fc, SR * 0.45), "low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def hp(x, fc, order=2):
    sos = signal.butter(order, fc, "high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def sweep_filter(x, f_start, f_end, kind="low", chunk=256, q_order=2, curve="exp"):
    """Time-varying filter: process in chunks, carrying filter state."""
    out = np.zeros_like(x)
    nchunks = int(np.ceil(len(x) / chunk))
    zi = None
    for i in range(nchunks):
        p = i / max(nchunks - 1, 1)
        if curve == "exp":
            fc = f_start * (f_end / f_start) ** p
        else:
            fc = f_start + (f_end - f_start) * p
        fc = float(np.clip(fc, 20, SR * 0.45))
        if kind == "band":
            lo, hi = fc / 1.6, fc * 1.6
            sos = signal.butter(q_order, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos")
        else:
            sos = signal.butter(q_order, fc, kind, fs=SR, output="sos")
        seg = x[i * chunk:(i + 1) * chunk]
        if zi is None or zi.shape != (sos.shape[0], 2):
            zi = signal.sosfilt_zi(sos) * 0
        y, zi = signal.sosfilt(sos, seg, zi=zi)
        out[i * chunk:(i + 1) * chunk] = y
    return out


def saw(freq, n, phase=0.0):
    t = t_arr(n)
    ph = (freq * t + phase) % 1.0
    return 2 * ph - 1


def noise(n):
    return rng.standard_normal(n)


def mix2(*parts):
    """Sum sounds of different lengths (weights via tuples (x, w))."""
    n = max(len(p[0] if isinstance(p, tuple) else p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        x, w = p if isinstance(p, tuple) else (p, 1.0)
        out[: len(x)] += x * w
    return out


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


# --------------------------------------------------------------------------
# MUSIC
# --------------------------------------------------------------------------
music = Bus()
drums = Bus()
bar = BEAT * 4
# A minor: Am F C G — one chord per bar; last bar is the resolving hit
CHORDS = [
    [57, 60, 64],  # bar0 Am (intro)
    [57, 60, 64],  # bar1 Am (drop)
    [53, 57, 60],  # F
    [48, 52, 55],  # C
    [55, 59, 62],  # G
    [57, 60, 64],  # Am
    [53, 57, 60],  # F
    [48, 52, 55],  # C
    [55, 59, 62],  # G (build)
    [57, 60, 64, 71],  # Am(add9) final
]
ROOTS = [45, 45, 41, 36, 43, 45, 41, 36, 43, 45]

drop_s = CUES["hits"]["drop"] / FPS          # 2.0 s
final_s = CUES["hits"]["final"] / FPS        # 18.0 s
build_s = CUES["scenes"]["features"][0] / FPS  # 16.0 s
arp_s = CUES["scenes"]["training"][0] / FPS    # 7.0 s

# sidechain envelope (pump) from kicks
kick_times = []
t = drop_s
while t < final_s - 1e-6:
    kick_times.append(t)
    t += BEAT
# build: kicks double in the last bar before the final hit
t = build_s + BEAT * 2
while t < final_s - 1e-6:
    if not any(abs(t - k) < 1e-6 for k in kick_times):
        kick_times.append(t)
    t += BEAT / 2
kick_times.sort()

pump = np.ones(len(music.l))
for kt in kick_times:
    s = int(kt * SR)
    n = int(0.28 * SR)
    tt = t_arr(n)
    shape = 1 - 0.72 * np.exp(-tt / 0.07)
    e = min(len(pump), s + n)
    pump[s:e] = np.minimum(pump[s:e], shape[: e - s])

# ---- Pad (detuned supersaw, filtered) ----
for bi, chord in enumerate(CHORDS):
    start = bi * bar
    length = bar + 0.6 if bi < 9 else 2.6
    n = int(length * SR)
    x = np.zeros(n)
    for note in chord:
        for det in (-0.13, -0.06, 0.0, 0.06, 0.13):
            x += saw(midi(note + 12 * 0) * (1 + det / 100 * 1.0) * 2 ** (det / 12 * 0.1), n, rng.random())
    x /= len(chord) * 5
    e = env_ad(n, 0.05 if bi else 1.6, 10.0)
    fade = np.ones(n)
    tail = int(0.6 * SR)
    if bi < 9:
        fade[-tail:] = np.linspace(1, 0, tail)
    else:
        fade = np.exp(-t_arr(n) / 0.9)
    if bi == 0:
        y = sweep_filter(x * e, 250, 2400, "low")
    elif bi == 8:
        y = sweep_filter(x * e, 1500, 7000, "low")
    else:
        y = lp(x * e, 2600 if bi < 9 else 5000)
    y *= fade
    # stereo widen: haas-ish offset
    d = int(0.011 * SR)
    left = y
    right = np.concatenate([np.zeros(d), y[:-d]])
    music.add(int(start * SR), left=left, right=right, gain=0.20)

# ---- Sub bass (sidechained) ----
for bi, root in enumerate(ROOTS):
    if bi == 0:
        continue
    start = bi * bar
    if bi == 9:
        continue  # final bar handled by the 808 hit
    n = int(bar * SR)
    tt = t_arr(n)
    f = midi(root - 12 + 12)  # ~55-110 Hz
    x = np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt)
    x = np.tanh(1.6 * x)
    # eighth-note rhythmic gate for drive
    gate = np.ones(n)
    fadeN = int(0.01 * SR)
    gate[:fadeN] = np.linspace(0, 1, fadeN)
    gate[-fadeN:] = np.linspace(1, 0, fadeN)
    music.add(int(start * SR), mono=lp(x * gate, 220), gain=0.34)

# ---- Arp pluck (16ths) from the UI section to the build ----
arp_pattern = [0, 1, 2, 1, 3, 2, 1, 2]
step = BEAT / 4
t = arp_s
i = 0
while t < final_s - 1e-6:
    bi = int(t // bar)
    chord = CHORDS[min(bi, 9)]
    notes = chord + [chord[0] + 12]
    note = notes[arp_pattern[i % len(arp_pattern)] % len(notes)] + 12
    n = int(0.22 * SR)
    tt = t_arr(n)
    f = midi(note)
    x = 0.6 * np.sin(2 * np.pi * f * tt) + 0.4 * (2 * np.abs(2 * ((f * tt) % 1) - 1) - 1)
    x *= env_ad(n, 0.002, 0.06)
    x = lp(x, 5200)
    pan = 0.45 * np.sin(i * 0.9)
    g = 0.085 if t < build_s else 0.11
    music.add(int(t * SR), mono=x, gain=g, pan=pan)
    # ping-pong echo
    music.add(int((t + BEAT * 0.75) * SR), mono=x, gain=g * 0.35, pan=-pan)
    t += step
    i += 1

music.l *= pump[: len(music.l)] * 0.5 + 0.5
music.r *= pump[: len(music.r)] * 0.5 + 0.5


# ---- Drums ----
def kick():
    n = int(0.45 * SR)
    tt = t_arr(n)
    f = 48 + 120 * np.exp(-tt / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * env_ad(n, 0.001, 0.16)
    click = hp(noise(n), 3000) * env_ad(n, 0.0005, 0.004) * 0.35
    return np.tanh(1.8 * (x + click))


def clap():
    n = int(0.35 * SR)
    nz = bp(noise(n), 900, 3200)
    e = np.zeros(n)
    for k, off in enumerate((0, 0.009, 0.018, 0.027)):
        s = int(off * SR)
        e[s:] += env_ad(n - s, 0.0005, 0.012 if k < 3 else 0.09)
    return nz * e


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    x = hp(noise(n), 7500) * env_ad(n, 0.0005, 0.07 if open_ else 0.014)
    return x


K = kick()
for kt in kick_times:
    g = 0.62 if kt < build_s + BEAT * 2 else 0.5
    drums.add(int(kt * SR), mono=K, gain=g)

# claps on 2 & 4 from the kinetic section
t = CUES["scenes"]["kinetic"][0] / FPS + BEAT
while t < build_s - 1e-6:
    drums.add(int(t * SR), mono=clap(), gain=0.30, pan=0.05)
    t += BEAT * 2

# hats: offbeat 8ths from 3s, 16ths from 7s
t = CUES["scenes"]["kinetic"][0] / FPS
k = 0
while t < final_s - 1e-6:
    sixteenth = t >= arp_s
    stepn = BEAT / 4 if sixteenth else BEAT / 2
    if sixteenth or (k % 2 == 1):
        accent = 1.0 if (k % 2 == 1) else 0.55
        drums.add(int(t * SR), mono=hat(open_=(not sixteenth)), gain=0.11 * accent, pan=0.25)
    t += stepn if sixteenth else BEAT / 2
    k += 1

# build: snare roll accelerating into the final hit
roll_start = build_s
t = roll_start
while t < final_s - 1e-6:
    p = (t - roll_start) / (final_s - roll_start)
    stepn = BEAT / 2 if p < 0.25 else (BEAT / 4 if p < 0.75 else BEAT / 8)
    n = int(0.12 * SR)
    sn = bp(noise(n), 1200, 6000) * env_ad(n, 0.0005, 0.03)
    sn += np.sin(2 * np.pi * 190 * t_arr(n)) * env_ad(n, 0.0005, 0.04) * 0.4
    drums.add(int(t * SR), mono=sn, gain=0.10 + 0.20 * p, pan=0.0)
    t += stepn

# --------------------------------------------------------------------------
# SFX
# --------------------------------------------------------------------------
sfx = Bus()


def impact(size=1.0):
    n = int(2.2 * SR)
    tt = t_arr(n)
    f = 32 + 90 * np.exp(-tt / 0.09)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.001, 0.55 * size)
    crack = lp(noise(n), 5000) * env_ad(n, 0.0005, 0.05)
    body = bp(noise(n), 120, 900) * env_ad(n, 0.001, 0.18 * size)
    tail = lp(hp(noise(n), 2500), 9000) * env_ad(n, 0.002, 0.45 * size) * 0.25
    x = boom * 1.0 + crack * 0.55 + body * 0.5 + tail
    return np.tanh(1.4 * x)


def impact_small():
    n = int(0.8 * SR)
    tt = t_arr(n)
    f = 55 + 140 * np.exp(-tt / 0.05)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.001, 0.2)
    crack = bp(noise(n), 1500, 7000) * env_ad(n, 0.0005, 0.03)
    return np.tanh(1.3 * (boom + 0.6 * crack))


def bass_hit():
    n = int(2.6 * SR)
    tt = t_arr(n)
    f = 41 + 70 * np.exp(-tt / 0.06)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x = np.tanh(2.2 * x) * env_ad(n, 0.002, 0.9)
    return lp(x, 400)


def whoosh(frames):
    dur = frames / FPS + 0.25
    n = int(dur * SR)
    tt = np.linspace(0, 1, n)
    nz = noise(n)
    # bell envelope peaking at 70% of the move
    # peak lands exactly on start+frames (the cut), then a short tail
    peak = (frames / FPS) / dur
    e = np.where(tt < peak, (tt / peak) ** 2.2, np.exp(-(tt - peak) / 0.09))
    up = sweep_filter(nz, 350, 4200, "band", curve="exp")
    x = up * e
    # stereo motion: pan left -> right
    pan = np.linspace(-0.8, 0.8, n)
    gl = np.cos((pan + 1) * np.pi / 4)
    gr = np.sin((pan + 1) * np.pi / 4)
    # align the peak on the cue frame + frames*0.7
    return x * gl * 1.4, x * gr * 1.4


def riser(frames):
    dur = frames / FPS
    n = int(dur * SR)
    tt = np.linspace(0, 1, n)
    nz = sweep_filter(noise(n), 400, 9000, "band", curve="exp")
    f = 180 * (2 ** (tt * 3.0))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    vib = 1 + 0.3 * np.sin(2 * np.pi * (4 + 18 * tt) * tt * dur)
    e = tt ** 1.7
    x = (nz * 0.8 + tone * 0.25 * vib) * e
    fade = int(0.004 * SR)
    x[-fade:] *= np.linspace(1, 0, fade)
    return x


def blip(freq=2200, dur=0.07):
    n = int(dur * SR)
    tt = t_arr(n)
    x = np.sin(2 * np.pi * freq * tt) * env_ad(n, 0.001, dur / 3.5)
    x += np.sin(2 * np.pi * freq * 2.01 * tt) * env_ad(n, 0.0005, dur / 8) * 0.3
    return x


def click():
    n = int(0.05 * SR)
    x = hp(noise(n), 2500) * env_ad(n, 0.0002, 0.003)
    x += np.sin(2 * np.pi * 900 * t_arr(n)) * env_ad(n, 0.0005, 0.012) * 0.8
    return x


def pop(f0=380, f1=1100):
    n = int(0.12 * SR)
    tt = t_arr(n)
    f = f0 + (f1 - f0) * (1 - np.exp(-tt / 0.02))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.001, 0.035)


def swipe():
    n = int(0.28 * SR)
    x = sweep_filter(noise(n), 6000, 900, "band", curve="exp") * env_ad(n, 0.01, 0.07)
    return x * 1.6


def glitch():
    n = int(0.22 * SR)
    x = np.zeros(n)
    seg = int(0.018 * SR)
    for k in range(0, n, seg):
        if rng.random() < 0.7:
            f = rng.choice([220, 440, 880, 1760, 3520])
            tt = t_arr(min(seg, n - k))
            sq = np.sign(np.sin(2 * np.pi * f * tt))
            x[k:k + len(tt)] = sq * rng.uniform(0.3, 1.0)
    crushed = np.round(x * 6) / 6
    return lp(crushed, 7000) * 0.6


def chime(notes=(76, 81, 88), spacing=0.06):
    n = int(1.2 * SR)
    x = np.zeros(n)
    for k, m in enumerate(notes):
        s = int(k * spacing * SR)
        tt = t_arr(n - s)
        f = midi(m)
        x[s:] += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * env_ad(n - s, 0.002, 0.25)
    return x


def shimmer(dur=1.6):
    n = int(dur * SR)
    tt = t_arr(n)
    x = np.zeros(n)
    for m in (81, 84, 88, 93, 96):
        x += np.sin(2 * np.pi * midi(m) * tt + rng.random() * 6) * (0.6 + 0.4 * np.sin(2 * np.pi * (5 + m % 3) * tt))
    return x * env_ad(n, 0.05, dur / 3) / 5


def tick():
    n = int(0.03 * SR)
    return mix2(hp(noise(n), 4000) * env_ad(n, 0.0002, 0.004), (blip(3400, 0.03), 0.4))


H = CUES["hits"]
U = CUES["ui"]

# risers (end exactly at their target frame)
for start, frames in CUES["risers"]:
    sfx.add(f2s(start), mono=riser(frames), gain=0.42 if start == 0 else 0.34)

# intro: sub drone + reverse swell into the drop
n = f2s(H["drop"])
tt = t_arr(n)
drone = (np.sin(2 * np.pi * 55 * tt) + 0.35 * np.sin(2 * np.pi * 110.4 * tt)) * np.clip(tt / 1.2, 0, 1) ** 1.5
drone += lp(noise(n), 300) * 0.25 * (tt / tt[-1]) ** 2
drone[-240:] *= np.linspace(1, 0, 240)
sfx.add(0, mono=drone, gain=0.22)
nrev = int(0.9 * SR)
rev = hp(noise(nrev), 1800) * (np.linspace(0, 1, nrev) ** 3)
sfx.add(f2s(H["drop"]) - nrev, left=rev, right=np.roll(rev, 300), gain=0.22)

# impacts
sfx.add(f2s(H["drop"]), mono=impact(1.0), gain=0.62)
for key in ("wordA", "wordB"):
    sfx.add(f2s(H[key]), mono=impact_small(), gain=0.45)
sfx.add(f2s(H["wordC"]), mono=impact(0.7), gain=0.55)
sfx.add(f2s(H["notReady"]), mono=pop(300, 800), gain=0.28)
sfx.add(f2s(H["strike"]) - int(0.04 * SR), mono=swipe(), gain=0.5, pan=-0.2)
sfx.add(f2s(H["glitch"]), mono=glitch(), gain=0.32)
sfx.add(f2s(H["progressIn"]), mono=impact_small(), gain=0.42)
for key in ("feat1", "feat2", "feat3", "feat4"):
    sfx.add(f2s(H[key]), mono=impact_small(), gain=0.40)
sfx.add(f2s(H["final"]), mono=impact(1.3), gain=0.66)

# bass hits (808 drops)
for fr in CUES["bass"]:
    sfx.add(f2s(fr), mono=bass_hit(), gain=0.55)

# whooshes: [start, frames] -> peak on start+frames
for start, frames in CUES["whooshes"]:
    L, R = whoosh(frames)
    sfx.add(f2s(start), left=L, right=R, gain=0.52)

# logo slashes
for k, fr in enumerate(U["logoSlashes"]):
    sfx.add(f2s(fr), mono=mix2(blip(1400 + 300 * k, 0.09), (click(), 0.5)), gain=0.22, pan=-0.3 + 0.3 * k)
sfx.add(f2s(H["drop"]) + int(0.12 * SR), mono=shimmer(1.8), gain=0.16)

# UI: card flying in
sfx.add(f2s(U["cardIn"]), mono=mix2(pop(200, 700), click()), gain=0.3)
for k, fr in enumerate(U["rows"]):
    sfx.add(f2s(fr), mono=blip(1600 + 110 * k, 0.06), gain=0.32, pan=0.35 - 0.14 * k)
for k, fr in enumerate(U["chips"]):
    sfx.add(f2s(fr), mono=pop(500 + 80 * k, 1300 + 80 * k), gain=0.27, pan=-0.3 + 0.2 * k)
sfx.add(f2s(U["dropdownOpen"]), mono=mix2(click(), (blip(1200, 0.05), 0.6)), gain=0.5)
for k, fr in enumerate(U["dropdownItems"]):
    sfx.add(f2s(fr), mono=tick(), gain=0.3, pan=0.1 * k)
sfx.add(f2s(U["dropdownPick"]), mono=mix2(click(), (blip(1760, 0.08), 0.8), (pop(600, 1500), 0.5)), gain=0.55)
sfx.add(f2s(U["muscleSwap"]), mono=pop(450, 1400), gain=0.36)

# chart points ascend in pitch (progress = going up)
for k, fr in enumerate(U["chartPoints"]):
    sfx.add(f2s(fr), mono=blip(midi(84 + [0, 3, 7, 10, 12][k]), 0.1), gain=0.36, pan=-0.4 + 0.2 * k)
# ring fill: short rising tone
rs, re_ = U["ringStart"], U["ringEnd"]
n = f2s(re_) - f2s(rs)
tt = np.linspace(0, 1, n)
ring = np.sin(2 * np.pi * np.cumsum(500 + 900 * tt ** 1.5) / SR) * (0.3 + 0.7 * tt) * 0.5
ring += hp(noise(n), 5000) * tt * 0.15
ring[-200:] *= np.linspace(1, 0, 200)
sfx.add(f2s(rs), mono=ring, gain=0.2)
for fr in U["checks"][:-1]:
    sfx.add(f2s(fr), mono=mix2(pop(700, 1500), (blip(2400, 0.05), 0.5)), gain=0.3)
sfx.add(f2s(U["check"]), mono=chime((76, 81, 88)), gain=0.36)

# CTA: typing the URL, then the button click
for k, fr in enumerate(U["urlType"]):
    sfx.add(f2s(fr), mono=mix2(tick(), (click(), 0.6)), gain=0.4, pan=-0.3 + 0.04 * k)
sfx.add(f2s(U["ctaClick"]), mono=mix2(click(), (pop(600, 1600), 0.6)), gain=0.42)
sfx.add(f2s(H["final"]) + int(0.1 * SR), mono=shimmer(2.2), gain=0.12)
sfx.add(f2s(U["ctaClick"]) + int(0.05 * SR), mono=chime((81, 88, 93)), gain=0.2)


# --------------------------------------------------------------------------
# MIX
# --------------------------------------------------------------------------
def reverb(x, secs=1.8, damp=6000):
    n = int(secs * SR)
    ir = noise(n) * np.exp(-t_arr(n) / (secs / 5))
    ir = lp(ir, damp)
    ir /= np.sqrt(np.sum(ir ** 2))
    return signal.fftconvolve(x, ir)[: len(x)]


mus = music.stereo()
drm = drums.stereo()
fx = sfx.stereo()

wet_m = np.stack([reverb(mus[0]), reverb(mus[1])]) * 0.35
wet_fx = np.stack([reverb(fx[0], 2.4), reverb(fx[1], 2.4)]) * 0.28
wet_d = np.stack([reverb(drm[0], 0.9), reverb(drm[1], 0.9)]) * 0.12

# duck the bed under the UI sections so interface sounds read clearly
duck = np.ones(mus.shape[1])
for a, b in ((445, 700), (745, 925)):
    sa, sb = f2s(a), f2s(b)
    ramp_n = int(0.15 * SR)
    duck[sa:sb] = 0.62
    duck[sa - ramp_n:sa] = np.linspace(1, 0.62, ramp_n)
    duck[sb:sb + ramp_n] = np.linspace(0.62, 1, ramp_n)
mix = (mus * 0.95 + wet_m) * duck + (drm * 1.0 + wet_d) * (0.5 + 0.5 * duck) + fx * 1.0 + wet_fx
mix = mix[:, :N]

# master: gentle high-pass, soft clip, fade out, normalize
mix = np.stack([hp(mix[0], 28), hp(mix[1], 28)])
fade_n = int(0.5 * SR)
mix[:, -fade_n:] *= np.linspace(1, 0, fade_n) ** 1.5
mix = np.tanh(mix * 1.25) / np.tanh(1.25)
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.93

out_dir = os.path.join(ROOT, "public", "audio")
os.makedirs(out_dir, exist_ok=True)
wavfile.write(os.path.join(out_dir, "soundtrack.wav"), SR, (mix.T * 32767).astype(np.int16))

# stems for inspection
stem_dir = os.path.join(ROOT, "audio", "stems")
os.makedirs(stem_dir, exist_ok=True)
for name, st in (("music", mus + wet_m), ("drums", drm + wet_d), ("sfx", fx + wet_fx)):
    st = st[:, :N]
    wavfile.write(os.path.join(stem_dir, f"{name}.wav"), SR, (st.T / (np.max(np.abs(st)) + 1e-9) * 0.9 * 32767).astype(np.int16))

print("wrote", os.path.join(out_dir, "soundtrack.wav"), f"{DUR:.2f}s", "peak", float(np.max(np.abs(mix))))
