"""2D overlay primitives (PIL, RGBA) with Arabic shaping (libraqm).

Identity: parallelogram labels skewed like the strokes of the NAV mark, sky/navy
palette, white guide lines, green = correct / red = mistake.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def back_out(x):
    x = clamp(x)
    c1 = 1.70158
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def prog(t, start, dur=0.35):
    return clamp((t - start) / dur)


class Fonts:
    def __init__(self, brand_dir, fonts_cfg):
        self.dir = brand_dir
        self.cfg = fonts_cfg
        self.cache = {}

    def get(self, key, size):
        k = (key, int(size))
        if k not in self.cache:
            self.cache[k] = ImageFont.truetype(f"{self.dir}/{self.cfg[key]}", int(size))
        return self.cache[k]


class Canvas:
    def __init__(self, w, h, fonts: Fonts, lang="ar", scale=1.0):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.fonts = fonts
        self.lang = lang
        self.s = scale  # 1.0 at 1080 px on the short side

    # ---------------- text
    def font(self, weight, size):
        base = "ar_" if self.lang == "ar" else "en_"
        key = {"black": base + "black", "bold": base + "bold", "regular": base + ("regular" if self.lang == "ar" else "bold")}[weight]
        # Montserrat looks larger than Tajawal at equal size
        k = 0.82 if self.lang == "en" else 1.0
        return self.fonts.get(key, size * self.s * k)

    def _kw(self, rtl):
        return dict(direction="rtl", language="ar") if rtl else {}

    def measure(self, text, f, rtl=None):
        rtl = (self.lang == "ar") if rtl is None else rtl
        b = f.getbbox(text, **self._kw(rtl))
        return b, b[2] - b[0], b[3] - b[1]

    def text(self, xy, text, f, fill=(255, 255, 255), alpha=1.0, anchor="c", rtl=None, shadow=True,
             dx=0, dy=0):
        if alpha <= 0 or not text:
            return (0, 0)
        rtl = (self.lang == "ar") if rtl is None else rtl
        b, tw, th = self.measure(text, f, rtl)
        x, y = xy[0] + dx, xy[1] + dy
        x0 = x - tw / 2 if anchor == "c" else (x - tw if anchor == "r" else x)
        pos = (x0 - b[0], y - th / 2 - b[1])
        a = int(255 * alpha)
        if shadow:
            sh = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).text((pos[0], pos[1] + 4 * self.s), text, font=f, fill=(0, 0, 0, int(160 * alpha)),
                                    **self._kw(rtl))
            self.im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8 * self.s)))
        self.d.text(pos, text, font=f, fill=tuple(fill[:3]) + (a,), **self._kw(rtl))
        return tw, th

    def wrap(self, text, f, max_w):
        words = text.split()
        lines, cur = [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if self.measure(t, f)[1] <= max_w or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    # ---------------- shapes
    def skew_box(self, x0, y0, x1, y1, fill, alpha=1.0, skew_deg=14, shadow=True):
        if alpha <= 0 or x1 <= x0:
            return
        k = math.tan(math.radians(skew_deg)) * (y1 - y0)
        pts = [(x0 + k, y0), (x1 + k, y0), (x1, y1), (x0, y1)]
        if shadow:
            sh = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
            ImageDraw.Draw(sh).polygon([(px, py + 8 * self.s) for px, py in pts], fill=(0, 0, 0, int(110 * alpha)))
            self.im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14 * self.s)))
        c = tuple(fill[:3]) + (int((fill[3] if len(fill) == 4 else 255) * alpha),)
        self.d.polygon(pts, fill=c)

    def rrect(self, box, r, fill, alpha=1.0):
        if alpha <= 0:
            return
        c = tuple(fill[:3]) + (int((fill[3] if len(fill) == 4 else 255) * alpha),)
        self.d.rounded_rectangle(box, r, fill=c)

    def line(self, pts, color, alpha=1.0, width=6, glow=False):
        if alpha <= 0 or len(pts) < 2:
            return
        w = max(1, int(width * self.s))
        if glow:
            g = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
            ImageDraw.Draw(g).line(pts, fill=tuple(color[:3]) + (int(140 * alpha),), width=w * 3, joint="curve")
            self.im.alpha_composite(g.filter(ImageFilter.GaussianBlur(8 * self.s)))
        self.d.line(pts, fill=tuple(color[:3]) + (int(255 * alpha),), width=w, joint="curve")
        for p in (pts[0], pts[-1]):
            r = w / 2
            self.d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=tuple(color[:3]) + (int(255 * alpha),))

    def dashed(self, p0, p1, color, alpha=1.0, width=5, dash=22, gap=14, progress=1.0):
        x0, y0 = p0
        x1, y1 = p1
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1:
            return
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        s, end = 0.0, L * progress
        c = tuple(color[:3]) + (int(255 * alpha),)
        while s < end:
            e = min(end, s + dash * self.s)
            self.d.line([(x0 + ux * s, y0 + uy * s), (x0 + ux * e, y0 + uy * e)], fill=c, width=max(1, int(width * self.s)))
            s = e + gap * self.s

    def arrow(self, p0, p1, color, alpha=1.0, width=12, head=38, progress=1.0):
        if alpha <= 0:
            return
        x0, y0 = p0
        x1, y1 = x0 + (p1[0] - x0) * progress, y0 + (p1[1] - y0) * progress
        ang = math.atan2(y1 - y0, x1 - x0)
        hd = head * self.s
        bx, by = x1 - math.cos(ang) * hd * 0.7, y1 - math.sin(ang) * hd * 0.7
        self.line([(x0, y0), (bx, by)], color, alpha, width, glow=True)
        l = (x1 + math.cos(ang + 2.55) * hd, y1 + math.sin(ang + 2.55) * hd)
        r = (x1 + math.cos(ang - 2.55) * hd, y1 + math.sin(ang - 2.55) * hd)
        self.d.polygon([(x1, y1), l, r], fill=tuple(color[:3]) + (int(255 * alpha),))

    def ring(self, xy, r, color, alpha=1.0, pulse=0.0, fill_white=True):
        if alpha <= 0:
            return
        x, y = xy
        r *= self.s
        rr = r * (1.9 + pulse)
        self.d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=tuple(color[:3]) + (int(200 * alpha * (1 - pulse * 0.7)),),
                       width=max(2, int(4 * self.s)))
        self.d.ellipse((x - r, y - r, x + r, y + r), fill=((255, 255, 255) if fill_white else tuple(color[:3])) + (int(255 * alpha),),
                       outline=tuple(color[:3]) + (int(255 * alpha),), width=max(2, int(5 * self.s)))

    def glow(self, xy, rx, ry, color, alpha=1.0, angle=0.0):
        if alpha <= 0:
            return
        g = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        e = Image.new("RGBA", (int(rx * 2 + 4), int(ry * 2 + 4)), (0, 0, 0, 0))
        ImageDraw.Draw(e).ellipse((2, 2, rx * 2 + 2, ry * 2 + 2), fill=tuple(color[:3]) + (int(150 * alpha),))
        e = e.rotate(angle, expand=True)
        g.paste(e, (int(xy[0] - e.width / 2), int(xy[1] - e.height / 2)), e)
        self.im.alpha_composite(g.filter(ImageFilter.GaussianBlur(max(rx, ry) * 0.35)))

    def icon_check(self, xy, size, color, alpha=1.0, progress=1.0):
        x, y = xy
        s = size * self.s
        pts = [(x - s * 0.5, y), (x - s * 0.12, y + s * 0.38), (x + s * 0.55, y - s * 0.42)]
        c = tuple(color[:3]) + (int(255 * alpha),)
        w = max(2, int(s * 0.2))
        if progress < 0.5:
            p = progress / 0.5
            self.d.line([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * p, pts[0][1] + (pts[1][1] - pts[0][1]) * p)], fill=c, width=w)
        else:
            p = (progress - 0.5) / 0.5
            self.d.line([pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * p, pts[1][1] + (pts[2][1] - pts[1][1]) * p)],
                        fill=c, width=w, joint="curve")

    def icon_x(self, xy, size, color, alpha=1.0, progress=1.0):
        x, y = xy
        s = size * self.s * 0.42
        c = tuple(color[:3]) + (int(255 * alpha),)
        w = max(2, int(size * self.s * 0.18))
        p1 = clamp(progress * 2)
        p2 = clamp(progress * 2 - 1)
        self.d.line([(x - s, y - s), (x - s + 2 * s * p1, y - s + 2 * s * p1)], fill=c, width=w)
        if p2 > 0:
            self.d.line([(x + s, y - s), (x + s - 2 * s * p2, y - s + 2 * s * p2)], fill=c, width=w)

    def arc(self, center, r, a0, a1, color, alpha=1.0, width=5):
        x, y = center
        self.d.arc((x - r, y - r, x + r, y + r), a0, a1, fill=tuple(color[:3]) + (int(255 * alpha),),
                   width=max(1, int(width * self.s)))
