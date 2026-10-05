"""Calm sound for the Nav Coaching intro (procedural, no samples -> no third-party licence).
Soft D-major pad + two quiet bell notes (logo reveal, tagline). Peak level / fades come from src/intro/config.json.
Output: public/audio/intro.wav (48 kHz stereo)."""
import json, os
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(ROOT, "src", "intro", "config.json")))
SR = 48000
DUR = C["durationSec"]
N = int(DUR * SR)
t = np.arange(N) / SR


def env(a, d, start, length):
    """attack/decay envelope placed at `start` seconds for `length` seconds."""
    x = np.zeros(N)
    i0 = int(start * SR)
    n = min(int(length * SR), N - i0)
    tt = np.arange(n) / SR
    x[i0:i0 + n] = np.minimum(tt / a, 1.0) ** 2 * np.exp(-tt / d)
    return x


def tone(f, harm=((1, 1.0), (2, 0.25), (3, 0.08))):
    return sum(a * np.sin(2 * np.pi * f * h * t + 0.3 * h) for h, a in harm)


# pad: D3 A3 E4 F#4, very slow swell, slight detune for width (L/R)
pad_notes = [146.83, 220.0, 329.63, 369.99]
pad_env = np.minimum(t / 1.4, 1.0) ** 2
L = sum(tone(f * 0.998) * g for f, g in zip(pad_notes, (1.0, 0.7, 0.45, 0.28))) * pad_env
R = sum(tone(f * 1.002) * g for f, g in zip(pad_notes, (1.0, 0.7, 0.45, 0.28))) * pad_env
pad = np.stack([L, R]) * 0.22

# bells: soft sine bells, A5 at the logo reveal, D6 when the tagline lands
def bell(f, start, gain):
    e = env(0.045, 0.6, start, 2.4)
    x = (np.sin(2 * np.pi * f * t) + 0.12 * np.sin(2 * np.pi * f * 2.76 * t)) * e * gain
    return np.stack([x, np.roll(x, int(0.007 * SR))])  # tiny Haas offset for width

bells = bell(880.0, 0.6, 0.12) + bell(1174.66, 2.3, 0.09)

mix = pad + bells
# gentle low-pass so nothing is bright or sharp
b, a = signal.butter(2, 3200 / (SR / 2))
mix = signal.lfilter(b, a, mix, axis=1)
# fades in / out
fi, fo = C["audio"]["fadeInSec"], C["audio"]["fadeOutSec"]
fade = np.minimum(t / fi, 1.0) * np.minimum((DUR - t) / fo, 1.0)
fade = np.sin(np.clip(fade, 0, 1) * np.pi / 2) ** 2
mix = mix * fade
peak = 10 ** (C["audio"]["peakDb"] / 20)
mix = mix / (np.max(np.abs(mix)) + 1e-9) * peak
out = os.path.join(ROOT, "public", "audio", "intro.wav")
wavfile.write(out, SR, (mix.T * 32767).astype(np.int16))
rms = 20 * np.log10(np.sqrt(np.mean(mix ** 2)) + 1e-12)
print(f"{out}  dur={DUR}s  peak={C['audio']['peakDb']} dBFS  rms={rms:.1f} dBFS")
