"""Soft cinematic sound for the Nav Coaching outro (procedural, no samples -> no third-party licence).
Warm D-major pad, a soft airy swell under the 3D phone spin, quiet bells on the logo and the URL,
and a gentle click synced to the cursor press. Timing / levels come from src/outro/config.json.
Output: public/audio/outro.wav (48 kHz stereo)."""
import json, os
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(ROOT, "src", "outro", "config.json")))
T, A = C["timing"], C["audio"]
SR = 48000
DUR = C["durationSec"]
N = int(DUR * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)


def place(x, start):
    out = np.zeros(N)
    i0 = int(start * SR)
    n = min(len(x), N - i0)
    out[i0:i0 + n] = x[:n]
    return out


def stereo(x, haas_ms=6):
    return np.stack([x, np.roll(x, int(haas_ms / 1000 * SR))])


# pad: D3 A3 D4 F#4 A4, slow swell, detuned L/R
notes = [(146.83, 1.0), (220.0, 0.7), (293.66, 0.5), (369.99, 0.32), (440.0, 0.2)]
def pad_ch(det):
    return sum(g * (np.sin(2 * np.pi * f * det * t) + 0.2 * np.sin(2 * np.pi * 2 * f * det * t + 0.4)) for f, g in notes)
pad_env = np.minimum(t / 1.6, 1.0) ** 2
pad = np.stack([pad_ch(0.998), pad_ch(1.002)]) * pad_env * 0.16

# airy swell under the phone spin: band-passed noise that rises and settles with the turn
s0, s1 = T["phoneSpin"]
n = int((s1 - s0 + 0.6) * SR)
tt = np.arange(n) / SR
noise = rng.standard_normal(n)
b, a = signal.butter(2, [500 / (SR / 2), 2600 / (SR / 2)], btype="band")
noise = signal.lfilter(b, a, noise)
sw_env = np.sin(np.clip(tt / (s1 - s0 + 0.6), 0, 1) * np.pi) ** 2
swell = stereo(place(noise * sw_env * 0.10, s0), 9)

# bells: soft attack, long decay
def bell(f, start, gain):
    n = int(2.6 * SR)
    tt = np.arange(n) / SR
    e = np.minimum(tt / 0.04, 1.0) ** 2 * np.exp(-tt / 0.65)
    x = (np.sin(2 * np.pi * f * tt) + 0.1 * np.sin(2 * np.pi * f * 2.76 * tt)) * e * gain
    return stereo(place(x, start))
bells = bell(880.0, T["logo"][0] + 0.15, 0.12) + bell(1174.66, T["url"][0] + 0.1, 0.09)

# click: short, rounded tick (low-passed noise burst + tiny 1.8 kHz tone), no harsh transient
cn = int(0.05 * SR)
ct = np.arange(cn) / SR
ce = (1 - np.exp(-ct / 0.0015)) * np.exp(-ct / 0.012)
cb, ca = signal.butter(2, 3500 / (SR / 2))
click = (signal.lfilter(cb, ca, rng.standard_normal(cn)) * 0.6 + np.sin(2 * np.pi * 1800 * ct) * 0.5) * ce
click = stereo(place(click * A["clickGain"], T["click"]), 0)

mix = pad + swell + bells + click
lb, la = signal.butter(2, 6000 / (SR / 2))
mix = signal.lfilter(lb, la, mix, axis=1)
fi, fo = A["fadeInSec"], A["fadeOutSec"]
fade = np.minimum(t / fi, 1.0) * np.minimum((DUR - t) / fo, 1.0)
mix = mix * np.sin(np.clip(fade, 0, 1) * np.pi / 2) ** 2
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 10 ** (A["peakDb"] / 20)
out = os.path.join(ROOT, "public", "audio", "outro.wav")
wavfile.write(out, SR, (mix.T * 32767).astype(np.int16))
rms = 20 * np.log10(np.sqrt(np.mean(mix ** 2)) + 1e-12)
print(f"{out}  dur={DUR}s  peak={A['peakDb']} dBFS  rms={rms:.1f} dBFS")
