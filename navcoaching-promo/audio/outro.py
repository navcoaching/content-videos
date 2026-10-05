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

# click: clear two-part "mouse click" (press + softer release), crisp but rounded — no harsh transient
def tick(gain, decay, tone_hz):
    n = int(0.06 * SR)
    ct = np.arange(n) / SR
    e = (1 - np.exp(-ct / 0.0006)) * np.exp(-ct / decay)
    cb, ca = signal.butter(2, [900 / (SR / 2), 7000 / (SR / 2)], btype="band")
    nz = signal.lfilter(cb, ca, rng.standard_normal(n))
    nz /= np.max(np.abs(nz)) + 1e-9
    return (nz * 0.7 + np.sin(2 * np.pi * tone_hz * ct) * 0.45) * e * gain
click = place(tick(1.0, 0.006, 2400), T["click"]) + place(tick(0.45, 0.005, 2900), T["click"] + 0.075)
click = stereo(click / (np.max(np.abs(click)) + 1e-9), 0)

# bed (pad + swell + bells) is levelled to peakDb; the click sits on top at clickPeakDb (still well under a voice-over)
bed = pad + swell + bells
lb, la = signal.butter(2, 6000 / (SR / 2))
bed = signal.lfilter(lb, la, bed, axis=1)
fi, fo = A["fadeInSec"], A["fadeOutSec"]
fade = np.minimum(t / fi, 1.0) * np.minimum((DUR - t) / fo, 1.0)
bed = bed * np.sin(np.clip(fade, 0, 1) * np.pi / 2) ** 2
bed = bed / (np.max(np.abs(bed)) + 1e-9) * 10 ** (A["peakDb"] / 20)
mix = bed + click * 10 ** (A["clickPeakDb"] / 20)
out = os.path.join(ROOT, "public", "audio", "outro.wav")
wavfile.write(out, SR, (mix.T * 32767).astype(np.int16))
rms = 20 * np.log10(np.sqrt(np.mean(mix ** 2)) + 1e-12)
print(f"{out}  dur={DUR}s  peak={A['peakDb']} dBFS  rms={rms:.1f} dBFS")
