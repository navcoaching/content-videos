"""Chest Press Machine — educational vertical edit (1080x1920, 30fps).

Pipeline:
  1. Source clips (iPhone HLG HDR, .MOV) are tone-mapped to SDR mp4 beforehand
     (see build.sh) and read from SDR_DIR.
  2. Each segment maps output frames -> source time (play / slow-mo / freeze).
     Slow-mo frames are synthesized with DIS optical flow.
  3. A per-frame camera (slow push-in + punch on cuts), a colour grade and
     animated overlays (Arabic titles, step chips, annotations) are applied.
  4. Frames are piped to ffmpeg; an SFX track is generated alongside.
"""
import math
import os
import subprocess
import sys
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
SDR_DIR = os.environ.get("SDR_DIR", os.path.join(HERE, "work", "sdr"))
FONT_DIR = os.environ.get("FONT_DIR", os.path.join(HERE, "fonts"))
OUT_DIR = os.environ.get("OUT_DIR", os.path.join(HERE, "out"))
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
PREVIEW = os.environ.get("PREVIEW")  # "t1,t2,..." -> write stills only

ACCENT = (25, 227, 198)
WHITE = (255, 255, 255)
DARK = (12, 14, 18)
WARN = (255, 77, 77)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


AR_BLACK = lambda s: font("Tajawal-900.ttf", s)
AR_BOLD = lambda s: font("Tajawal-800.ttf", s)
AR_MED = lambda s: font("Tajawal-500.ttf", s)
EN_BLACK = lambda s: font("Montserrat-900.ttf", s)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def back_out(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def anim(t, start, dur=0.3):
    """0..1 progress of an intro animation starting at `start`."""
    return clamp((t - start) / dur)


# ---------------------------------------------------------------- source access
class Clip:
    def __init__(self, name, flip=False):
        self.path = os.path.join(SDR_DIR, f"{name}.mp4")
        self.flip = flip
        self.cache = {}
        cap = cv2.VideoCapture(self.path)
        self.n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        cap.release()
        self.dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)

    def load(self, i0, i1):
        """Decode frames [i0, i1] into cache (drop everything else)."""
        i0, i1 = max(0, i0), min(self.n - 1, i1)
        self.cache = {k: v for k, v in self.cache.items() if i0 <= k <= i1}
        cap = cv2.VideoCapture(self.path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, i0)
        for i in range(i0, i1 + 1):
            ok, f = cap.read()
            if not ok:
                break
            if i not in self.cache:
                if self.flip:
                    f = f[:, ::-1].copy()
                self.cache[i] = f
        cap.release()

    def frame(self, idx):
        idx = min(max(idx, 0), self.n - 1)
        while idx not in self.cache and idx > 0:
            idx -= 1
        return self.cache[idx]

    def at(self, t):
        """Frame at source time t (seconds), optical-flow interpolated."""
        x = t * self.fps
        i = int(math.floor(x))
        a = x - i
        if a < 0.08 or i + 1 >= self.n:
            return self.frame(i)
        if a > 0.92:
            return self.frame(i + 1)
        f0, f1 = self.frame(i), self.frame(i + 1)
        s = 0.5
        g0 = cv2.cvtColor(cv2.resize(f0, None, fx=s, fy=s), cv2.COLOR_BGR2GRAY)
        g1 = cv2.cvtColor(cv2.resize(f1, None, fx=s, fy=s), cv2.COLOR_BGR2GRAY)
        fw = cv2.resize(self.dis.calc(g0, g1, None), (f0.shape[1], f0.shape[0])) / s
        bw = cv2.resize(self.dis.calc(g1, g0, None), (f0.shape[1], f0.shape[0])) / s
        hh, ww = f0.shape[:2]
        gx, gy = np.meshgrid(np.arange(ww, dtype=np.float32), np.arange(hh, dtype=np.float32))
        w0 = cv2.remap(f0, gx - fw[..., 0] * a, gy - fw[..., 1] * a, cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_REPLICATE)
        w1 = cv2.remap(f1, gx - bw[..., 0] * (1 - a), gy - bw[..., 1] * (1 - a), cv2.INTER_LINEAR,
                       borderMode=cv2.BORDER_REPLICATE)
        return cv2.addWeighted(w0, 1 - a, w1, a, 0)


# ---------------------------------------------------------------- grade
def _grade_lut():
    x = np.arange(256) / 255.0
    # gentle S-curve + slight lift of blacks
    s = x + 0.10 * np.sin((x - 0.5) * 2 * math.pi) * -0.5 * (1 - abs(2 * x - 1)) * 2
    s = 0.02 + 0.97 * s
    return np.clip(s * 255, 0, 255).astype(np.uint8)


LUT = _grade_lut()
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGNETTE = (1 - 0.28 * (((_xx - W / 2) / (W * 0.75)) ** 2 + ((_yy - H / 2) / (H * 0.7)) ** 2)).clip(0.6, 1)[..., None]
del _yy, _xx


def grade(bgr, desat=0.0, dim=1.0):
    img = cv2.LUT(bgr, LUT)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= 1.12 * (1 - desat)
    img = cv2.cvtColor(hsv.clip(0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
    img *= VIGNETTE * dim
    return img.clip(0, 255).astype(np.uint8)


def camera(bgr, zoom, cx=0.5, cy=0.5, blur=0.0):
    """Zoom about (cx, cy) in normalized coordinates; zoom>=1."""
    if zoom <= 1.0005:
        out = bgr
    else:
        cw, ch = W / zoom, H / zoom
        x0 = clamp(cx * W - cw / 2, 0, W - cw)
        y0 = clamp(cy * H - ch / 2, 0, H - ch)
        M = np.float32([[zoom, 0, -x0 * zoom], [0, zoom, -y0 * zoom]])
        out = cv2.warpAffine(bgr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    if blur > 0.5:
        k = int(blur) * 2 + 1
        kern = np.zeros((k, k), np.float32)
        kern[k // 2, :] = 1.0 / k
        out = cv2.filter2D(out, -1, kern)
    return out


# ---------------------------------------------------------------- drawing helpers
class Layer:
    """RGBA overlay canvas with Arabic-aware text helpers."""

    def __init__(self):
        self.im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    @staticmethod
    def measure(text, f, rtl):
        kw = dict(direction="rtl", language="ar") if rtl else {}
        b = f.getbbox(text, **kw)
        return b, b[2] - b[0], b[3] - b[1]

    def text(self, xy, text, f, fill=WHITE, alpha=1.0, anchor="c", rtl=True, shadow=True, dx=0, dy=0):
        """anchor: 'c' centre, 'r' right edge at x, 'l' left edge at x. y is text centre."""
        if alpha <= 0:
            return
        b, tw, th = self.measure(text, f, rtl)
        x, y = xy
        x += dx
        y += dy
        if anchor == "c":
            x0 = x - tw / 2
        elif anchor == "r":
            x0 = x - tw
        else:
            x0 = x
        pos = (x0 - b[0], y - th / 2 - b[1])
        kw = dict(direction="rtl", language="ar") if rtl else {}
        a = int(255 * alpha)
        if shadow:
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).text((pos[0], pos[1] + 5), text, font=f, fill=(0, 0, 0, int(170 * alpha)), **kw)
            sh = sh.filter(ImageFilter.GaussianBlur(9))
            self.im.alpha_composite(sh)
        self.d.text(pos, text, font=f, fill=fill + (a,), **kw)
        return tw, th

    def rrect(self, box, r, fill, alpha=1.0, outline=None, width=0):
        x0, y0, x1, y1 = box
        if x1 <= x0 or y1 <= y0 or alpha <= 0:
            return
        base = fill[3] if len(fill) == 4 else 255
        fc = tuple(fill[:3]) + (int(base * alpha),)
        oc = None if outline is None else outline + (int(255 * alpha),)
        self.d.rounded_rectangle(box, r, fill=fc, outline=oc, width=width)

    def shadow_box(self, box, r, alpha):
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((box[0], box[1] + 10, box[2], box[3] + 10), r,
                                             fill=(0, 0, 0, int(120 * alpha)))
        self.im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))

    def dashed(self, p0, p1, color, alpha, width=8, dash=26, gap=16, prog=1.0):
        x0, y0 = p0
        x1, y1 = p1
        L = math.hypot(x1 - x0, y1 - y0) * prog
        ux, uy = (x1 - x0) / max(1e-6, math.hypot(x1 - x0, y1 - y0)), (y1 - y0) / max(1e-6, math.hypot(x1 - x0, y1 - y0))
        s = 0.0
        c = color + (int(255 * alpha),)
        while s < L:
            e = min(L, s + dash)
            self.d.line([(x0 + ux * s, y0 + uy * s), (x0 + ux * e, y0 + uy * e)], fill=c, width=width)
            s = e + gap

    def arrow(self, p0, p1, color, alpha, width=14, prog=1.0, head=46):
        x0, y0 = p0
        x1 = x0 + (p1[0] - x0) * prog
        y1 = y0 + (p1[1] - y0) * prog
        c = color + (int(255 * alpha),)
        ang = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - math.cos(ang) * head * 0.8, y1 - math.sin(ang) * head * 0.8
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.line([(x0, y0), (bx, by)], fill=color + (int(150 * alpha),), width=width + 18)
        self.im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
        self.d.line([(x0, y0), (bx, by)], fill=c, width=width)
        l = (x1 + math.cos(ang + 2.6) * head, y1 + math.sin(ang + 2.6) * head)
        r = (x1 + math.cos(ang - 2.6) * head, y1 + math.sin(ang - 2.6) * head)
        self.d.polygon([(x1, y1), l, r], fill=c)

    def dot(self, xy, rad, color, alpha, ring=True, pulse=0.0):
        x, y = xy
        if ring:
            rr = rad * (1.8 + pulse)
            self.d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=color + (int(200 * alpha * (1 - pulse * 0.6)),),
                           width=5)
        self.d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=color + (int(255 * alpha),),
                       outline=WHITE + (int(255 * alpha),), width=4)

    def glow_ellipse(self, box, color, alpha):
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse(box, fill=color + (int(110 * alpha),))
        self.im.alpha_composite(g.filter(ImageFilter.GaussianBlur(40)))

    def check(self, xy, size, color, alpha, prog=1.0):
        x, y = xy
        pts = [(x - size * 0.5, y), (x - size * 0.12, y + size * 0.38), (x + size * 0.55, y - size * 0.42)]
        c = color + (int(255 * alpha),)
        if prog < 0.5:
            p = prog / 0.5
            self.d.line([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * p, pts[0][1] + (pts[1][1] - pts[0][1]) * p)],
                        fill=c, width=int(size * 0.18))
        else:
            p = (prog - 0.5) / 0.5
            self.d.line([pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * p,
                                          pts[1][1] + (pts[2][1] - pts[1][1]) * p)], fill=c,
                        width=int(size * 0.18), joint="curve")


# ---------------------------------------------------------------- reusable graphics
def step_header(L, t, num, title, sub=None, t0=0.0, out_t=None):
    """Top-of-frame step card: accent number badge + Arabic title (+ subtitle)."""
    p = ease_out(anim(t, t0, 0.35))
    fade = 1.0 if out_t is None else 1 - ease_in_out(anim(t, out_t, 0.25))
    a = p * fade
    if a <= 0:
        return
    y = 300
    ff = AR_BLACK(92)
    _, tw, _ = L.measure(title, ff, True)
    badge = 118
    gap = 26
    total = tw + gap + badge + 70
    right = W / 2 + total / 2
    slide = (1 - p) * 60
    box = (W / 2 - total / 2 + slide, y - 82, right + slide, y + 82)
    L.shadow_box(box, 40, a)
    L.rrect(box, 40, (12, 14, 18, 215), a)
    bx1 = box[2] - 24
    bx0 = bx1 - badge
    L.rrect((bx0, y - badge / 2, bx1, y + badge / 2), 30, ACCENT, a)
    L.text(((bx0 + bx1) / 2, y + 4), str(num), EN_BLACK(80), fill=DARK, alpha=a, rtl=False, shadow=False)
    L.text((bx0 - gap, y + 6), title, ff, alpha=a, anchor="r", shadow=False)
    if sub:
        ps = ease_out(anim(t, t0 + 0.25, 0.35)) * fade
        L.text((W / 2, y + 150), sub, AR_BOLD(56), alpha=ps, dy=(1 - ps) * 30)


def progress_bar(L, t, active, fill):
    """Four-step progress bar at the very top. `fill` = progress of the active step."""
    n, gap, x0, x1, y = 4, 14, 70, W - 70, 150
    sw = (x1 - x0 - gap * (n - 1)) / n
    for i in range(n):
        # steps read right-to-left for Arabic
        r = x1 - i * (sw + gap)
        l = r - sw
        L.rrect((l, y - 7, r, y + 7), 7, (255, 255, 255, 80), 1.0)
        f = 1.0 if i + 1 < active else (fill if i + 1 == active else 0.0)
        if f > 0:
            L.rrect((r - sw * f, y - 7, r, y + 7), 7, ACCENT, 1.0)


def chip(L, xy, text, t, t0, color=ACCENT, fg=DARK, size=54, anchor="c"):
    p = back_out(anim(t, t0, 0.35))
    a = clamp(anim(t, t0, 0.2))
    if a <= 0:
        return
    f = AR_BLACK(size)
    _, tw, th = L.measure(text, f, True)
    pw, ph = 36, 24
    x, y = xy
    wbox = (tw + 2 * pw) * p
    if anchor == "c":
        box = (x - wbox / 2, y - (size * 0.62 + ph / 2), x + wbox / 2, y + (size * 0.62 + ph / 2))
    elif anchor == "r":
        box = (x - wbox, y - (size * 0.62 + ph / 2), x, y + (size * 0.62 + ph / 2))
    else:
        box = (x, y - (size * 0.62 + ph / 2), x + wbox, y + (size * 0.62 + ph / 2))
    L.shadow_box(box, 22, a)
    L.rrect(box, 22, color, a)
    if p > 0.6:
        L.text(((box[0] + box[2]) / 2, y + 4), text, f, fill=fg, alpha=a * clamp((p - 0.6) / 0.4), shadow=False)
    return box


def label_pointer(L, t, t0, target, text_xy, text, anchor="r"):
    """Dot on the body + connector line + chip label."""
    p = ease_out(anim(t, t0, 0.3))
    if p <= 0:
        return
    pulse = (math.sin((t - t0) * 6) + 1) / 2 * 0.4
    L.dot(target, 16, ACCENT, p, pulse=pulse)
    lp = ease_out(anim(t, t0 + 0.1, 0.3))
    ex = target[0] + (text_xy[0] - target[0]) * lp
    ey = target[1] + (text_xy[1] - target[1]) * lp
    L.d.line([target, (ex, ey)], fill=WHITE + (int(255 * p),), width=6)
    if lp >= 1:
        chip(L, text_xy, text, t, t0 + 0.4, color=WHITE, fg=DARK, size=50, anchor=anchor)


# ---------------------------------------------------------------- timeline
def play(a, b, speed=1.0):
    return ("play", a, b, speed)


def freeze(t, dur):
    return ("freeze", t, dur)


def build_map(pieces):
    """Return list of (source_time, is_frozen) per output frame."""
    out = []
    for p in pieces:
        if p[0] == "play":
            _, a, b, sp = p
            n = int(round((b - a) / sp * FPS))
            out += [(a + i * sp / FPS, False) for i in range(n)]
        else:
            _, t, dur = p
            out += [(t, True)] * int(round(dur * FPS))
    return out


class Segment:
    def __init__(self, clip, pieces, draw, zoom=(1.0, 1.06), center=(0.5, 0.5), punch=True, sfx=None,
                 desat_freeze=0.0):
        self.clip, self.map, self.draw = clip, build_map(pieces), draw
        self.zoom, self.center, self.punch = zoom, center, punch
        self.sfx = sfx or []
        self.desat_freeze = desat_freeze

    @property
    def dur(self):
        return len(self.map) / FPS


# ---------------------------------------------------------------- the edit
C2880 = Clip("2880")
C2881 = Clip("2881", flip=True)  # front-camera footage is mirrored
C2882 = Clip("2882")
C2883 = Clip("2883")


def s_hook(L, t, T, st):
    # Title card over slow-motion press
    p = ease_out(anim(t, 0.15, 0.45))
    L.im.alpha_composite(gradient_bottom(0.85 * p, start=0.45))
    L.text((W / 2, 1150), "CHEST PRESS", EN_BLACK(128), alpha=p, rtl=False, dy=(1 - p) * 50)
    p2 = ease_out(anim(t, 0.35, 0.45))
    L.text((W / 2, 1280), "MACHINE", EN_BLACK(96), fill=ACCENT, alpha=p2, rtl=False, dy=(1 - p2) * 50)
    p3 = ease_out(anim(t, 0.7, 0.4))
    L.text((W / 2, 1410), "جهاز الضغط للصدر", AR_BLACK(80), alpha=p3, dy=(1 - p3) * 40)
    chip(L, (W / 2, 1530), "الطريقة الصحيحة خطوة بخطوة", t, 1.1, size=50)


def s_muscles(L, t, T, st):
    p = ease_out(anim(t, 0.0, 0.35))
    L.text((W / 2, 300), "العضلات المستهدفة", AR_BLACK(92), alpha=p, dy=(1 - p) * 40)
    gl = ease_out(anim(t, 0.3, 0.6))
    L.glow_ellipse((430, 800, 715, 1000), ACCENT, gl)
    label_pointer(L, t, 0.5, (572, 900), (572, 1200), "الصدر", anchor="c")
    label_pointer(L, t, 1.3, (790, 840), (1010, 620), "الكتف الأمامي", anchor="r")
    label_pointer(L, t, 2.1, (235, 905), (70, 1380), "الترايسبس", anchor="l")


def gradient_bottom(a, start=0.52):
    g = np.zeros((H, W, 4), np.uint8)
    ys = np.linspace(0, 1, H)
    alpha = np.clip((ys - start) / (1 - start), 0, 1) ** 1.2 * 235 * a
    g[..., 3] = alpha[:, None].astype(np.uint8)
    return Image.fromarray(g, "RGBA")


def gradient_top(a, end=0.3):
    g = np.zeros((H, W, 4), np.uint8)
    ys = np.linspace(0, 1, H)
    alpha = np.clip(1 - ys / end, 0, 1) ** 1.3 * 200 * a
    g[..., 3] = alpha[:, None].astype(np.uint8)
    return Image.fromarray(g, "RGBA")


def s_step1(L, t, T, st):
    L.im.alpha_composite(gradient_top(1.0))
    progress_bar(L, t, 1, clamp(t / T))
    step_header(L, t, 1, "ضبط المقعد", "المقابض بمستوى منتصف الصدر")
    # freeze annotation window
    f0, f1 = 1.0, 3.6
    if f0 <= t < f1 + 0.3:
        fade = 1 - ease_in_out(anim(t, f1, 0.3))
        pl = ease_out(anim(t, f0 + 0.1, 0.5))
        L.dashed((120, 800), (880, 800), ACCENT, fade, width=10, prog=pl)
        L.dot((245, 815), 18, ACCENT, fade * ease_out(anim(t, f0 + 0.1, 0.3)))
        L.dot((520, 800), 18, ACCENT, fade * ease_out(anim(t, f0 + 0.5, 0.3)))
        box = chip(L, (720, 700), "منتصف الصدر", t, f0 + 0.7, size=52)
        if fade < 1 and box:
            pass


def s_step2(L, t, T, st):
    L.im.alpha_composite(gradient_top(1.0))
    L.im.alpha_composite(gradient_bottom(0.9, start=0.6))
    progress_bar(L, t, 2, clamp(t / T))
    step_header(L, t, 2, "ثبّت ظهرك")
    # line along the back pad
    pl = ease_out(anim(t, 0.5, 0.6))
    L.arrow((935, 330), (561, 1200), ACCENT, pl, width=12, prog=pl, head=0.01)
    items = ["الظهر ملاصق للمسند", "الصدر مرفوع", "لوحا الكتف للخلف"]
    for i, s in enumerate(items):
        t0 = 0.9 + i * 0.7
        pa = ease_out(anim(t, t0, 0.35))
        y = 1290 + i * 118
        L.check((W - 120, y), 60, ACCENT, pa, prog=clamp(anim(t, t0, 0.35)))
        L.text((W - 190, y + 4), s, AR_BLACK(64), alpha=pa, anchor="r", dx=(1 - pa) * 50)


def s_step3(L, t, T, st):
    L.im.alpha_composite(gradient_top(1.0))
    progress_bar(L, t, 3, clamp(t / T))
    step_header(L, t, 3, "ادفع للأمام", "ادفع حتى تمتد ذراعك بالكامل")
    fz = st["freeze_start"]
    if t >= fz:
        pa = ease_out(anim(t, fz + 0.1, 0.5))
        L.arrow((690, 700), (150, 520), ACCENT, pa, prog=pa)
        L.dot((395, 585), 20, WARN, ease_out(anim(t, fz + 0.6, 0.3)),
              pulse=(math.sin((t - fz) * 6) + 1) / 2 * 0.4)
        chip(L, (W / 2, 1400), "لا تقفل المرفق", t, fz + 0.8, color=WARN, fg=WHITE, size=62)
        pb = ease_out(anim(t, fz + 1.3, 0.35))
        L.text((W / 2, 1535), "خلّ فيه ثنية بسيطة", AR_BOLD(58), alpha=pb, dy=(1 - pb) * 30)


def s_step4(L, t, T, st):
    L.im.alpha_composite(gradient_top(1.0))
    progress_bar(L, t, 4, clamp(t / T))
    step_header(L, t, 4, "ارجع ببطء")
    # tempo counter during the slow eccentric
    e0, e1 = st["ecc_start"], st["ecc_end"]
    if e0 - 0.1 <= t <= e1 + 0.6:
        pa = ease_out(anim(t, e0 - 0.1, 0.3)) * (1 - ease_in_out(anim(t, e1 + 0.3, 0.3)))
        L.arrow((150, 440), (470, 520), ACCENT, pa, prog=clamp((t - e0) / (e1 - e0)))
        k = int(clamp((t - e0) / (e1 - e0), 0, 0.999) * 3) + 1
        local = ((t - e0) / (e1 - e0) * 3) % 1
        sc = 1 + 0.25 * (1 - ease_out(local / 0.35)) if t >= e0 else 1
        L.rrect((W / 2 - 170, 1290, W / 2 + 170, 1590), 60, (12, 14, 18, 200), pa)
        L.text((W / 2, 1410), str(k), EN_BLACK(int(190 * sc)), fill=ACCENT, alpha=pa, rtl=False, shadow=False)
        L.text((W / 2, 1535), "رجوع بطيء", AR_BOLD(52), alpha=pa, shadow=False)


def s_summary(L, t, T, st):
    L.rrect((0, 0, W, H), 0, (8, 10, 14, 150), ease_out(anim(t, 0, 0.4)))
    p = ease_out(anim(t, 0.1, 0.35))
    L.text((W / 2, 330), "الخلاصة", AR_BLACK(110), fill=ACCENT, alpha=p, dy=(1 - p) * 40)
    items = ["المقابض بمستوى منتصف الصدر", "الظهر ثابت على المسند", "ادفع بدون قفل المرفق",
             "ارجع ببطء وتحكّم"]
    for i, s in enumerate(items):
        t0 = 0.6 + i * 0.75
        pa = ease_out(anim(t, t0, 0.35))
        y = 600 + i * 190
        box = (50 + (1 - pa) * 80, y - 70, W - 50 + (1 - pa) * 80, y + 70)
        L.shadow_box(box, 34, pa)
        L.rrect(box, 34, (255, 255, 255, 235), pa)
        cx = box[2] - 80
        L.rrect((cx - 44, y - 44, cx + 44, y + 44), 22, ACCENT, pa)
        L.check((cx, y + 2), 50, DARK, pa, prog=clamp(anim(t, t0 + 0.1, 0.3)))
        L.text((cx - 76, y + 6), s, AR_BLACK(50), fill=DARK, alpha=pa, anchor="r", shadow=False)
    pe = ease_out(anim(t, 4.0, 0.4))
    L.text((W / 2, 1480), "احفظ المقطع وطبّقه في تمرينك الجاي", AR_BOLD(56), alpha=pe, dy=(1 - pe) * 30)


def make_segments():
    segs = []
    # 0) Hook — slow-motion press from the clean side angle
    segs.append(Segment(C2880, [play(2.4, 4.4, 0.5)], s_hook, zoom=(1.12, 1.02), center=(0.55, 0.42),
                        punch=False, sfx=[(0.15, "whoosh"), (1.1, "pop")]))
    # 1) Muscles — front view
    segs.append(Segment(C2881, [play(0.3, 4.3, 1.0)], s_muscles, zoom=(1.0, 1.04), center=(0.5, 0.4),
                        sfx=[(0.0, "whoosh"), (0.9, "pop"), (1.7, "pop"), (2.5, "pop")]))
    # 2) Step 1 — set-up close-up with freeze + chest-height guide line
    segs.append(Segment(C2883, [play(0.0, 1.0), freeze(1.0, 2.6), play(1.0, 2.0)], s_step1, zoom=(1.0, 1.05),
                        center=(0.4, 0.45), desat_freeze=0.35,
                        sfx=[(0.0, "whoosh"), (1.0, "shutter"), (1.7, "pop")]))
    # 3) Step 2 — back on pad close-up
    segs.append(Segment(C2882, [play(2.0, 6.8, 1.0)], s_step2, zoom=(1.0, 1.05), center=(0.6, 0.5),
                        sfx=[(0.0, "whoosh"), (0.9, "pop"), (1.6, "pop"), (2.3, "pop")]))
    # 4) Step 3 — press: real-time rep, slow-mo press, freeze at lockout
    p3 = [play(4.6, 7.6, 1.0), play(7.6, 9.4, 0.5), freeze(9.4, 2.4)]
    fz3 = (3.0 + 1.8 / 0.5)
    segs.append(Segment(C2880, p3, s_step3, zoom=(1.0, 1.08), center=(0.45, 0.4), desat_freeze=0.35,
                        sfx=[(0.0, "whoosh"), (3.0, "slow"), (fz3, "shutter"), (fz3 + 0.8, "pop")]))
    segs[-1].state = {"freeze_start": fz3}
    # 5) Step 4 — slow eccentric with tempo counter
    #    source 6.9 (extended) -> 8.5 (chest) played at ~0.55x => ~2.9 s
    p4 = [play(5.8, 6.9, 1.0), play(6.9, 8.5, 0.55), play(8.5, 9.6, 1.0)]
    e0 = 1.1
    e1 = e0 + 1.6 / 0.55
    segs.append(Segment(C2883, p4, s_step4, zoom=(1.0, 1.06), center=(0.4, 0.4),
                        sfx=[(0.0, "whoosh"), (e0, "tick"), (e0 + (e1 - e0) / 3, "tick"),
                             (e0 + 2 * (e1 - e0) / 3, "tick")]))
    segs[-1].state = {"ecc_start": e0, "ecc_end": e1}
    # 6) Summary over real-time reps
    segs.append(Segment(C2883, [play(2.6, 8.6, 1.0)], s_summary, zoom=(1.0, 1.05), center=(0.5, 0.5),
                        sfx=[(0.0, "whoosh")] + [(0.6 + i * 0.75, "pop") for i in range(4)]))
    return segs


# ---------------------------------------------------------------- sfx
SR = 48000


def _env(n, a, r):
    e = np.ones(n)
    ai = int(a * SR)
    ri = int(r * SR)
    e[:ai] = np.linspace(0, 1, ai)
    e[-ri:] = np.linspace(1, 0, ri) ** 2
    return e


def sfx_sample(kind, rng):
    if kind == "whoosh":
        n = int(0.45 * SR)
        x = rng.standard_normal(n)
        # sweeping one-pole low-pass
        y = np.zeros(n)
        cut = np.linspace(0.02, 0.35, n) * np.hanning(n) + 0.01
        s = 0.0
        for i in range(n):
            s += cut[i] * (x[i] - s)
            y[i] = s
        y *= np.hanning(n) ** 1.5
        return 0.55 * y / (np.abs(y).max() + 1e-9)
    if kind == "slow":
        n = int(0.8 * SR)
        t = np.arange(n) / SR
        f = 220 * np.exp(-t * 2.2)
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5)
        return 0.35 * y
    if kind in ("pop", "tick"):
        n = int(0.12 * SR)
        t = np.arange(n) / SR
        f0 = 900 if kind == "pop" else 1500
        y = np.sin(2 * np.pi * f0 * t * (1 - t * 3)) * np.exp(-t * (45 if kind == "pop" else 70))
        return (0.35 if kind == "pop" else 0.28) * y
    if kind == "shutter":
        n = int(0.18 * SR)
        x = rng.standard_normal(n)
        e = np.exp(-np.arange(n) / SR * 60)
        e2 = np.zeros(n)
        k = int(0.07 * SR)
        e2[k:] = np.exp(-np.arange(n - k) / SR * 70)
        return 0.4 * x * (e + 0.7 * e2)
    raise ValueError(kind)


def write_sfx(segs, path, total):
    rng = np.random.default_rng(7)
    buf = np.zeros(int(total * SR) + SR)
    t0 = 0.0
    for s in segs:
        for at, kind in s.sfx:
            smp = sfx_sample(kind, rng)
            i = int((t0 + at) * SR)
            buf[i:i + len(smp)] += smp[:len(buf) - i]
        t0 += s.dur
    buf = np.clip(buf * 0.8, -1, 1)
    pcm = (buf * 32767).astype(np.int16)
    st = np.stack([pcm, pcm], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


# ---------------------------------------------------------------- render
def render():
    os.makedirs(OUT_DIR, exist_ok=True)
    segs = make_segments()
    total = sum(s.dur for s in segs)
    print(f"total {total:.2f}s, {sum(len(s.map) for s in segs)} frames")
    starts = np.cumsum([0] + [s.dur for s in segs])

    want = None
    if PREVIEW:
        want = [float(x) for x in PREVIEW.split(",")]

    enc = None
    video_path = os.path.join(OUT_DIR, "video_only.mp4")
    if want is None:
        enc = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                                "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p",
                                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                                "-movflags", "+faststart", video_path], stdin=subprocess.PIPE)

    for si, seg in enumerate(segs):
        frames_needed = [i for i in range(len(seg.map))]
        if want is not None:
            frames_needed = [i for i in frames_needed if any(abs(starts[si] + i / FPS - w) < 0.5 / FPS for w in want)]
            if not frames_needed:
                continue
        ts = [seg.map[i][0] for i in frames_needed]
        seg.clip.load(int(min(ts) * seg.clip.fps) - 1, int(max(ts) * seg.clip.fps) + 2)
        state = getattr(seg, "state", {})
        T = seg.dur
        for i in frames_needed:
            src_t, frozen = seg.map[i]
            t = i / FPS
            img = seg.clip.at(src_t)
            u = i / max(1, len(seg.map) - 1)
            z = seg.zoom[0] + (seg.zoom[1] - seg.zoom[0]) * ease_in_out(u)
            blur = 0.0
            if seg.punch and t < 0.27:
                k = 1 - ease_out(t / 0.27)
                z *= 1 + 0.10 * k
                blur = 10 * k
            img = camera(img, z, *seg.center, blur=blur)
            desat = seg.desat_freeze * (ease_out(clamp((i - first_freeze(seg, i)) / 6)) if frozen else 0)
            img = grade(img, desat=desat, dim=0.9 if frozen else 1.0)
            if frozen and first_freeze(seg, i) == i:
                pass
            rgb = Image.fromarray(img[:, :, ::-1]).convert("RGBA")
            L = Layer()
            seg.draw(L, t, T, state)
            rgb.alpha_composite(L.im)
            # white flash on freeze entry
            if frozen:
                k = i - first_freeze(seg, i)
                if k < 4:
                    fl = Image.new("RGBA", (W, H), (255, 255, 255, int(150 * (1 - k / 4))))
                    rgb.alpha_composite(fl)
            out = np.asarray(rgb.convert("RGB"))
            if enc:
                enc.stdin.write(out.tobytes())
            else:
                gt = starts[si] + t
                Image.fromarray(out).save(os.path.join(OUT_DIR, f"preview_{gt:05.2f}.jpg"), quality=88)
        print(f"segment {si} done ({seg.dur:.2f}s)", flush=True)

    if enc:
        enc.stdin.close()
        enc.wait()
        write_sfx(segs, os.path.join(OUT_DIR, "sfx.wav"), total)
        with open(os.path.join(OUT_DIR, "timeline.txt"), "w") as fh:
            names = ["Hook", "Muscles", "Step 1", "Step 2", "Step 3", "Step 4", "Summary"]
            for n, a, s in zip(names, starts, segs):
                fh.write(f"{n:8s} {a:6.2f}s -> {a + s.dur:6.2f}s\n")


def first_freeze(seg, i):
    j = i
    while j > 0 and seg.map[j - 1][1] and seg.map[j - 1][0] == seg.map[i][0]:
        j -= 1
    return j


if __name__ == "__main__":
    render()
