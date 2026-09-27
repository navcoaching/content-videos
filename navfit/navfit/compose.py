"""Storyboard -> frames -> video.

1. Plan: every scene becomes a list of output frames (camera, variant, motion time).
2. Render: unique 3D frames are rendered once with Blender (cached on disk).
3. Composite: face blur, zoom, overlays, transitions, progress bar, watermark.
4. Export: MP4 with SFX, clean MP4 (silent), VOICEOVER.md, REVIEW.md.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import wave

import cv2
import numpy as np
import yaml
from PIL import Image

from . import graphics as G
from .motion import MOTIONS, STYLES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_yaml(p):
    with open(p, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ------------------------------------------------------------------ project
class Project:
    def __init__(self, exercise, aspect=None, quality=None, lang=None):
        self.ex_dir = os.path.join(ROOT, "exercises", exercise)
        self.brand_dir = os.path.join(ROOT, "brand")
        self.cfg = load_yaml(os.path.join(self.ex_dir, "config.yaml"))
        self.content = load_yaml(os.path.join(self.ex_dir, "content.yaml"))
        self.board = load_yaml(os.path.join(self.ex_dir, "storyboard.yaml"))
        self.brand = load_yaml(os.path.join(self.brand_dir, "brand.yaml"))
        self.character = load_yaml(os.path.join(self.brand_dir, "character.yaml"))
        self.studio = load_yaml(os.path.join(self.brand_dir, "studio.yaml"))
        if self.cfg.get("logo_on_hoodie"):
            self.character["logo_on_hoodie"] = self.cfg["logo_on_hoodie"]
        self.lang = lang or self.cfg.get("language", "ar")
        self.aspect = aspect or self.cfg.get("aspect", "9:16")
        self.quality = quality or self.cfg.get("quality", "final")
        self.fps = int(self.cfg.get("fps", 30))
        self.name = exercise
        self.used_keys = set()

    def text(self, key):
        self.used_keys.add(key)
        item = self.content.get(key)
        if item is None:
            return f"[{key}]"
        return item.get(self.lang) or item.get("ar") or ""

    def size(self, aspect):
        full = (1080, 1920) if aspect == "9:16" else (1920, 1080)
        if self.quality == "draft":
            return full[0] // 2, full[1] // 2
        return full

    def review(self, keys=None):
        keys = keys or sorted(self.used_keys)
        rows = []
        for k in keys:
            it = self.content.get(k, {})
            if it.get("status") != "verified":
                rows.append((k, it.get("status", "missing"), it.get("ar", ""), it.get("review_note", it.get("basis", ""))))
        return rows


# ------------------------------------------------------------------ planning
def plan(project: Project):
    """Return list of scenes, each with frames [(cam, variant, t_motion, frozen)]."""
    fps = project.fps
    scenes = project.board["scenes"]
    # scale freeze holds towards the target duration
    base = 0.0
    freeze_total = 0.0
    for sc in scenes:
        for p in sc["motion"]:
            if p[0] == "play":
                base += (p[2] - p[1]) / p[3]
            else:
                base += p[2]
                freeze_total += p[2]
    target = float(project.cfg.get("target_duration", base))
    k = 1.0
    if freeze_total > 0:
        k = (target - (base - freeze_total)) / freeze_total
        k = G.clamp(k, 0.6, 1.5)
    planned = []
    for sc in scenes:
        frames = []
        for p in sc["motion"]:
            if p[0] == "play":
                _, a, b, sp = p
                n = int(round((b - a) / sp * fps))
                frames += [(a + i * sp / fps, False) for i in range(n)]
            else:
                _, t, dur = p
                frames += [(t, True)] * max(1, int(round(dur * k * fps)))
        planned.append({"scene": sc, "frames": frames})
    return planned, base, k


def cam_for(scene, local_u, studio):
    cam = scene["camera"]
    if isinstance(cam, str):
        return cam, studio["cameras"][cam]
    base = dict(studio["cameras"][cam.get("base", "threeq")])
    a0, a1 = cam["orbit"]
    az = a0 + (a1 - a0) * G.ease_in_out(local_u)
    base["azimuth"] = round(az, 2)
    return f"orbit_{az:.2f}", base


# ------------------------------------------------------------------ rendering (Blender)
def render_frames(project: Project, planned, aspect, cache_dir, log=print):
    from .scene3d import Renderer  # imports bpy
    W, H = project.size(aspect)
    motion_cls = MOTIONS[project.cfg["exercise"]]
    motions = {}
    jobs = {}
    for ps in planned:
        sc = ps["scene"]
        n = len(ps["frames"])
        paths = []
        for i, (t, frozen) in enumerate(ps["frames"]):
            u = i / max(1, n - 1)
            cam_key, preset = cam_for(sc, u, project.studio)
            var = sc.get("variant", "correct")
            key = f"{aspect}_{W}x{H}_{cam_key}_{var}_{int(round(t * 1000))}"
            h = hashlib.md5((key + json.dumps(preset, sort_keys=True) + json.dumps(project.character, sort_keys=True)
                             + json.dumps(project.studio["set"], sort_keys=True)).encode()).hexdigest()[:10]
            path = os.path.join(cache_dir, f"{key}_{h}.png")
            paths.append(path)
            if not os.path.exists(path) and path not in jobs:
                jobs[path] = (cam_key, preset, var, t)
        ps["paths"] = paths
    log(f"[render] {aspect}: {len(jobs)} new 3D frames to render ({W}x{H})")
    if not jobs:
        return
    os.makedirs(cache_dir, exist_ok=True)
    named = {k: v for k, v in project.studio["cameras"].items()}
    r = Renderer(project.character, project.studio["set"], named, project.brand_dir, aspect, (W, H))
    for i, (path, (cam_key, preset, var, t)) in enumerate(sorted(jobs.items())):
        if var not in motions:
            motions[var] = motion_cls(style=var)
        pose = motions[var].pose(t)
        if cam_key in named:
            r.render(cam_key, pose, path)
        else:
            r.render_preset(preset, pose, path)
        if i % 50 == 0:
            log(f"[render] {i + 1}/{len(jobs)}")


# ------------------------------------------------------------------ layout
class Layout:
    def __init__(self, aspect, W, H, lang):
        self.W, self.H, self.lang = W, H, lang
        self.vertical = aspect == "9:16"
        self.s = (W if self.vertical else H) / 1080
        rtl = lang == "ar"
        if self.vertical:
            self.col = (0.07 * W, 0.93 * W)
            self.header_y = 0.10 * H
            self.progress_y = 0.158 * H
            self.bullets_y = 0.845 * H
            self.badge_y = 0.85 * H
            self.title_y = 0.70 * H
            self.check_y0 = 0.30 * H
        else:
            self.col = (0.56 * W, 0.95 * W)
            self.header_y = 0.19 * H
            self.progress_y = 0.09 * H
            self.bullets_y = 0.42 * H
            self.badge_y = 0.74 * H
            self.title_y = 0.47 * H
            self.check_y0 = 0.30 * H
        self.cx = (self.col[0] + self.col[1]) / 2
        self.text_edge = self.col[1] if rtl else self.col[0]
        self.anchor = "r" if rtl else "l"
        self.dir = -1 if rtl else 1  # direction text grows from the edge


def P2(P, X):
    v = np.asarray(P) @ np.append(np.asarray(X, float), 1.0)
    return (float(v[0] / v[2]), float(v[1] / v[2]))


# ------------------------------------------------------------------ overlays
class OverlayEngine:
    def __init__(self, project, layout, fonts, colors):
        self.pr = project
        self.L = layout
        self.fonts = fonts
        self.c = {k: G.hex_rgb(v) for k, v in colors.items()}
        self.skew = project.brand.get("style", {}).get("skew_deg", 14)

    # helpers ------------------------------------------------------------
    def jt(self, fr, name):
        j = fr["joints2d"][name]
        return (j[0], j[1])

    def color(self, name):
        return self.c.get(name, self.c["sky"])

    def label_box(self, cv, edge_x, y, text, size, fg, bg, alpha, anchor, pad=(30, 18), weight="black"):
        f = cv.font(weight, size)
        _, tw, th = cv.measure(text, f)
        s = cv.s
        bw, bh = tw + 2 * pad[0] * s, size * s * 1.15 + 2 * pad[1] * s * 0.5
        if anchor == "r":
            x0, x1 = edge_x - bw, edge_x
        elif anchor == "l":
            x0, x1 = edge_x, edge_x + bw
        else:
            x0, x1 = edge_x - bw / 2, edge_x + bw / 2
        cv.skew_box(x0, y - bh / 2, x1, y + bh / 2, bg, alpha, self.skew)
        cv.text(((x0 + x1) / 2 + math.tan(math.radians(self.skew)) * bh / 2 * 0.0, y + 2 * s), text, f, fill=fg,
                alpha=alpha, shadow=False)
        return (x0, y - bh / 2, x1, y + bh / 2)

    # overlay types ------------------------------------------------------
    def draw(self, cv, ov, t, T, fr, scene_frames, idx):
        fn = getattr(self, "ov_" + ov["type"], None)
        if fn is None:
            raise ValueError(f"unknown overlay type {ov['type']}")
        fn(cv, ov, t, T, fr, scene_frames, idx)

    def ov_title(self, cv, ov, t, T, fr, sf, idx):
        L, s = self.L, cv.s
        p = G.ease_out(G.prog(t, 0.1, 0.45))
        # dark gradient for legibility
        grad = np.zeros((L.H, L.W, 4), np.uint8)
        if L.vertical:
            ys = np.linspace(0, 1, L.H)
            grad[..., 3] = (np.clip((ys - 0.5) / 0.5, 0, 1) ** 1.3 * 220 * p)[:, None].astype(np.uint8)
        else:
            xs = np.linspace(0, 1, L.W)
            grad[..., 3] = (np.clip((xs - 0.45) / 0.55, 0, 1) ** 1.2 * 210 * p)[None, :].astype(np.uint8)
        grad[..., :3] = self.c["deep"]
        cv.im.alpha_composite(Image.fromarray(grad, "RGBA"))
        title = self.pr.text(ov["text"])
        cv.text((L.cx, L.title_y), title, cv.font("black", 150), alpha=p, dy=(1 - p) * 40 * s)
        other = self.pr.cfg["title"].get("en" if self.pr.lang == "ar" else "ar", "")
        p2 = G.ease_out(G.prog(t, 0.35, 0.4))
        f_en = cv.fonts.get("en_black" if self.pr.lang == "ar" else "ar_black", 46 * s)
        cv.text((L.cx, L.title_y + 120 * s), other.upper() if self.pr.lang == "ar" else other, f_en,
                fill=self.c["sky"], alpha=p2, rtl=self.pr.lang != "ar", dy=(1 - p2) * 30 * s)
        p3 = G.back_out(G.prog(t, 0.7, 0.4))
        if p3 > 0:
            self.label_box(cv, L.cx, L.title_y + 220 * s, self.pr.text(ov["sub"]), 50, self.c["deep"], self.c["sky"],
                           G.clamp(p3), "c")

    def _header_box(self, cv, t, text, num=None, color_bg=None):
        L, s = self.L, cv.s
        p = G.ease_out(G.prog(t, 0.0, 0.35))
        if p <= 0:
            return
        f = cv.font("black", 84)
        _, tw, _ = cv.measure(text, f)
        bh = 132 * s
        badge = 128 * s if num is not None else 0
        gap = 18 * s if num is not None else 0
        total = tw + 70 * s + badge + gap
        slide = (1 - p) * 80 * s * (-L.dir)
        x1 = L.cx + total / 2 + slide
        x0 = L.cx - total / 2 + slide
        y = L.header_y
        cv.skew_box(x0, y - bh / 2, x1, y + bh / 2, (*self.c["deep"], 225), p, self.skew)
        if num is not None:
            # number badge on the reading-start side
            if L.lang == "ar":
                bx1 = x1 - 14 * s
                bx0 = bx1 - badge
                tx = bx0 - gap - 22 * s
                anchor = "r"
            else:
                bx0 = x0 + 14 * s + math.tan(math.radians(self.skew)) * bh
                bx1 = bx0 + badge
                tx = bx1 + gap + 10 * s
                anchor = "l"
            cv.skew_box(bx0, y - bh / 2 + 12 * s, bx1, y + bh / 2 - 12 * s, self.c["sky"], p, self.skew, shadow=False)
            cv.text(((bx0 + bx1) / 2 + 8 * s, y + 3 * s), str(num), cv.fonts.get("en_black", 76 * s),
                    fill=self.c["deep"], alpha=p, rtl=False, shadow=False)
            cv.text((tx, y + 4 * s), text, f, alpha=p, anchor=anchor, shadow=False)
        else:
            cv.text(((x0 + x1) / 2 + 12 * s, y + 4 * s), text, f, alpha=p, shadow=False)

    def ov_header(self, cv, ov, t, T, fr, sf, idx):
        self._header_box(cv, t, self.pr.text(ov["text"]))

    def ov_step(self, cv, ov, t, T, fr, sf, idx):
        self._header_box(cv, t, self.pr.text(ov["text"]), num=ov["n"])

    def ov_section(self, cv, ov, t, T, fr, sf, idx):
        L, s = self.L, cv.s
        p = G.ease_out(G.prog(t, 0.0, 0.3))
        self.label_box(cv, L.cx, L.header_y, self.pr.text(ov["text"]), 70, self.c["white"], self.c["bad"], p, "c")

    def ov_bullets(self, cv, ov, t, T, fr, sf, idx):
        L, s = self.L, cv.s
        if L.vertical:
            return self._captions(cv, ov, t, T)
        start, gap = ov.get("start", 0.5), ov.get("gap", 0.8)
        y = L.bullets_y
        f = cv.font("black", 58)
        maxw = (L.col[1] - L.col[0]) - 130 * s
        for i, key in enumerate(ov["items"]):
            t0 = start + i * gap
            p = G.ease_out(G.prog(t, t0, 0.35))
            lines = cv.wrap(self.pr.text(key), f, maxw)
            if p <= 0:
                y += (len(lines) * 72 + 34) * s
                continue
            icon_x = L.text_edge + L.dir * 40 * s
            cv.rrect((icon_x - 34 * s, y - 34 * s, icon_x + 34 * s, y + 34 * s), 14 * s, self.c["sky"], p)
            cv.icon_check((icon_x, y + 2 * s), 44, self.c["deep"], p, G.clamp(G.prog(t, t0 + 0.05, 0.3)))
            tx = L.text_edge + L.dir * 100 * s
            for j, ln in enumerate(lines):
                cv.text((tx, y + j * 72 * s + 4 * s), ln, f, alpha=p, anchor=L.anchor, dx=-L.dir * (1 - p) * 50 * s)
            y += (len(lines) * 72 + 34) * s

    def _captions(self, cv, ov, t, T):
        """9:16: one cue at a time in the caption zone under the character."""
        L, s = self.L, cv.s
        start, gap = ov.get("start", 0.5), ov.get("gap", 0.8)
        items = ov["items"]
        f = cv.font("black", 60)
        maxw = L.W * 0.78
        for i, key in enumerate(items):
            t0 = start + i * gap
            t1 = start + (i + 1) * gap if i + 1 < len(items) else 1e9
            p = G.ease_out(G.prog(t, t0, 0.3)) * (1 - G.ease_in_out(G.prog(t, t1 - 0.2, 0.2)))
            if p <= 0:
                continue
            lines = cv.wrap(self.pr.text(key), f, maxw)
            tw = max(cv.measure(ln, f)[1] for ln in lines)
            bh = (len(lines) * 76 + 50) * s
            bw = tw + 170 * s
            y = L.bullets_y
            x0, x1 = L.W / 2 - bw / 2, L.W / 2 + bw / 2
            cv.skew_box(x0, y - bh / 2, x1, y + bh / 2, (*self.c["deep"], 230), p, self.skew)
            icx = (x1 - 60 * s) if L.lang == "ar" else (x0 + 60 * s + math.tan(math.radians(self.skew)) * bh * 0.5)
            cv.rrect((icx - 34 * s, y - 34 * s, icx + 34 * s, y + 34 * s), 12 * s, self.c["sky"], p)
            cv.icon_check((icx, y + 2 * s), 44, self.c["deep"], p, G.clamp(G.prog(t, t0 + 0.05, 0.3)))
            tx = icx + (-66 * s if L.lang == "ar" else 66 * s)
            for j, ln in enumerate(lines):
                cv.text((tx, y + (j - (len(lines) - 1) / 2) * 76 * s + 4 * s), ln, f, alpha=p, anchor=L.anchor,
                        shadow=False, dy=(1 - p) * 20 * s)

    def ov_shoulder_width(self, cv, ov, t, T, fr, sf, idx):
        p = G.ease_out(G.prog(t, ov.get("start", 0.5), 0.6))
        if p <= 0:
            return
        P = fr["P"]
        J3 = fr["joints3d"]
        for sd in "LR":
            top = P2(P, J3[f"shoulder_{sd}"])
            bot = P2(P, [J3[f"shoulder_{sd}"][0], J3[f"ankle_{sd}"][1], 0.0])
            cv.dashed(top, bot, self.c["white"], p, width=5, progress=p)
            cv.ring(top, 9, self.c["sky"], p)
        # stance width arrow between ankles
        a, b = P2(P, [J3["ankle_L"][0], J3["ankle_L"][1], 0.01]), P2(P, [J3["ankle_R"][0], J3["ankle_R"][1], 0.01])
        pa = G.ease_out(G.prog(t, ov.get("start", 0.5) + 0.5, 0.4))
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        cv.arrow(mid, a, self.c["sky"], pa, width=8, head=26, progress=pa)
        cv.arrow(mid, b, self.c["sky"], pa, width=8, head=26, progress=pa)

    def ov_toe_angle(self, cv, ov, t, T, fr, sf, idx):
        p = G.ease_out(G.prog(t, ov.get("start", 1.0), 0.5))
        if p <= 0:
            return
        P, J3 = fr["P"], fr["joints3d"]
        for sd in "LR":
            heel = np.array(J3[f"heel_{sd}"]) + [0, 0, 0.01]
            toe = np.array(J3[f"toe_{sd}"])
            toe[2] = 0.01
            fwd = heel + [0, -0.3, 0]
            h2, t2, f2 = P2(P, heel), P2(P, toe + (toe - heel) * 0.25), P2(P, fwd)
            cv.dashed(h2, f2, self.c["white"], p, width=4, progress=p)
            cv.line([h2, t2], self.c["sky"], p, width=7, glow=True)

    def ov_trail(self, cv, ov, t, T, fr, sf, idx):
        j = ov["joint"]
        start_i = int(ov.get("start", 0) * self.pr.fps)
        pts = [tuple(f["joints2d"][j][:2]) for f in sf[start_i:idx + 1] if f is not None]
        if len(pts) >= 2:
            for k in range(1, len(pts)):
                a = 0.25 + 0.75 * k / len(pts)
                cv.line([pts[k - 1], pts[k]], self.c["sky"], a, width=6)
            cv.ring(pts[-1], 10, self.c["sky"], 1.0)

    def ov_arrow3d(self, cv, ov, t, T, fr, sf, idx):
        st, en = ov.get("start", 0.3), ov.get("end", 99)
        p = G.ease_out(G.prog(t, st, 0.5)) * (1 - G.ease_in_out(G.prog(t, en, 0.3)))
        if p <= 0:
            return
        P, J3 = fr["P"], fr["joints3d"]
        base = np.array(J3[ov["joint"]])
        off = np.array(ov.get("offset", [0, 0, 0]), float)
        a = P2(P, base + off)
        b = P2(P, base + off + np.array(ov["vec"], float))
        cv.arrow(a, b, self.c["sky"], p, width=14, head=44, progress=G.ease_out(G.prog(t, st, 0.6)))

    def ov_knee_toe(self, cv, ov, t, T, fr, sf, idx):
        p = G.ease_out(G.prog(t, ov.get("start", 0.5), 0.4))
        sd = ov.get("side", "R")
        k, to = self.jt(fr, f"knee_{sd}"), self.jt(fr, f"toe_{sd}")
        cv.dashed(k, to, self.c["white"], p, width=5, progress=p)
        cv.ring(k, 11, self.c["sky"], p)
        cv.ring(to, 9, self.c["sky"], p)

    def ov_plumb(self, cv, ov, t, T, fr, sf, idx):
        p = G.ease_out(G.prog(t, ov.get("start", 0.5), 0.5))
        if p <= 0:
            return
        c, cf = self.jt(fr, "com"), self.jt(fr, "com_floor")
        cv.dashed(c, cf, self.c["white"], p, width=5, progress=p)
        cv.ring(c, 13, self.c["sky"], p, fill_white=False)
        mf = self.jt(fr, "midfoot_floor")
        cv.glow(mf, 60 * cv.s, 18 * cv.s, self.c["sky"], p)
        cv.ring(mf, 8, self.c["sky"], p)

    def ov_parallel(self, cv, ov, t, T, fr, sf, idx):
        p = G.ease_out(G.prog(t, ov.get("start", 0.3), 0.5))
        if p <= 0:
            return
        P, J3 = fr["P"], fr["joints3d"]
        hip, knee = np.array(J3[ov["hip"]]), np.array(J3[ov["knee"]])
        h2, k2 = P2(P, hip), P2(P, knee)
        ext = P2(P, hip + (hip - knee) * 0.25)
        cv.line([k2, ext], self.c["sky"], p, width=10, glow=True)
        a, b = P2(P, knee + [0, -0.15, 0]), P2(P, knee + [0, 0.6, 0])
        cv.dashed(a, b, self.c["white"], G.ease_out(G.prog(t, ov.get("start", 0.3) + 0.3, 0.5)), width=5,
                  progress=G.ease_out(G.prog(t, ov.get("start", 0.3) + 0.3, 0.5)))

    def ov_rings(self, cv, ov, t, T, fr, sf, idx):
        col = self.color(ov.get("color", "sky"))
        for i, j in enumerate(ov["joints"]):
            p = G.ease_out(G.prog(t, ov.get("start", 0.2) + i * 0.12, 0.3))
            pulse = (math.sin((t - i * 0.3) * 5) + 1) / 2 * 0.5
            cv.ring(self.jt(fr, j), 11, col, p, pulse=pulse)

    def ov_chains(self, cv, ov, t, T, fr, sf, idx):
        col = self.color(ov.get("color", "sky"))
        p = G.ease_out(G.prog(t, ov.get("start", 0.2), 0.4))
        for ch in ov["chains"]:
            pts = [self.jt(fr, j) for j in ch]
            cv.line(pts, col, p, width=9, glow=True)
            for q in pts:
                cv.ring(q, 9, col, p)

    def ov_heel_gap(self, cv, ov, t, T, fr, sf, idx):
        col = self.color(ov.get("color", "sky"))
        p = G.ease_out(G.prog(t, ov.get("start", 0.3), 0.4))
        sd = ov.get("side", "R")
        P, J3 = fr["P"], fr["joints3d"]
        heel = np.array(J3[f"heel_{sd}"])
        floor = heel.copy()
        floor[2] = 0.0
        h2, f2 = P2(P, heel), P2(P, floor)
        a, b = P2(P, floor + [0, -0.25, 0]), P2(P, floor + [0, 0.12, 0])
        cv.dashed(a, b, self.c["white"], p, width=4)
        if abs(h2[1] - f2[1]) > 4:
            cv.line([h2, f2], col, p, width=8, glow=True)
        pulse = (math.sin(t * 5) + 1) / 2 * 0.5
        cv.ring(h2, 13, col, p, pulse=pulse)

    def ov_spine(self, cv, ov, t, T, fr, sf, idx):
        col = self.color(ov.get("color", "sky"))
        p = G.ease_out(G.prog(t, ov.get("start", 0.3), 0.4))
        P, J3 = fr["P"], fr["joints3d"]
        # draw on the back surface: offset backwards from the joints along the trunk normal
        pel, wai, nec = (np.array(J3[k]) for k in ("pelvis", "waist", "neck"))
        pts3 = []
        for a, b, u in ((pel, wai, 0.0), (pel, wai, 0.5), (wai, nec, 0.0), (wai, nec, 0.5), (wai, nec, 1.0)):
            q = a + (b - a) * u
            pts3.append(q)
        # back offset (towards +Y rotated with trunk): perpendicular to the segment in the sagittal plane
        out = []
        for i, q in enumerate(pts3):
            a = pts3[max(0, i - 1)]
            b = pts3[min(len(pts3) - 1, i + 1)]
            d = b - a
            d /= np.linalg.norm(d)
            back = np.array([0, d[2], -d[1]])  # rotate (y,z) by -90°
            if back[1] < 0:
                back = -back
            out.append(P2(P, q + back * 0.14 + [-0.2, 0, 0]))
        # smooth curve through points
        pts = []
        for i in range(len(out) - 1):
            for u in np.linspace(0, 1, 8, endpoint=False):
                pts.append((out[i][0] + (out[i + 1][0] - out[i][0]) * u, out[i][1] + (out[i + 1][1] - out[i][1]) * u))
        pts.append(out[-1])
        cv.line(pts, col, p, width=10, glow=True)
        if ov.get("color") == "good":
            cv.dashed(out[0], out[-1], self.c["white"], p * 0.9, width=4)

    def ov_muscle(self, cv, ov, t, T, fr, sf, idx):
        st, en = ov.get("start", 0.3), ov.get("end", 99)
        p = G.ease_out(G.prog(t, st, 0.4)) * (1 - G.ease_in_out(G.prog(t, en, 0.3)))
        if p <= 0:
            return
        L, s = self.L, cv.s
        a = self.jt(fr, ov["anchor"])
        thigh_px = math.dist(self.jt(fr, "hip_R"), self.jt(fr, "knee_R"))
        r = thigh_px * (0.28 if not ov.get("small") else 0.2)
        cv.glow(a, r, r * 0.8, self.c["sky"], p)
        cv.ring(a, 10, self.c["sky"], p, pulse=(math.sin(t * 5) + 1) / 4)
        side = ov.get("side", "right")
        lx = (L.col[1] - 20 * s) if side == "right" else (L.col[0] + 20 * s)
        if not L.vertical:
            lx = a[0] + (260 * s if side == "right" else -260 * s)
        ly = a[1] - 120 * s
        lp = G.ease_out(G.prog(t, st + 0.1, 0.35)) * p
        ex, ey = a[0] + (lx - a[0]) * lp, a[1] + (ly - a[1]) * lp
        cv.line([a, (ex, ey)], self.c["white"], lp, width=4)
        if lp > 0.9:
            anchor = "r" if side == "right" else "l"
            self.label_box(cv, lx, ly, self.pr.text(ov["text"]), 46 if not ov.get("small") else 38, self.c["deep"],
                           self.c["white"], p, anchor, pad=(22, 14))

    def ov_badge(self, cv, ov, t, T, fr, sf, idx):
        L, s = self.L, cv.s
        good = ov["kind"] == "good"
        col = self.c["good"] if good else self.c["bad"]
        p = G.back_out(G.prog(t, ov.get("start", 0.4), 0.35))
        a = G.clamp(G.prog(t, ov.get("start", 0.4), 0.2))
        if a <= 0:
            return
        text = self.pr.text(ov["text"])
        f = cv.font("black", 60)
        maxw = (L.col[1] - L.col[0]) - 190 * s
        lines = cv.wrap(text, f, maxw)
        tw = max(cv.measure(ln, f)[1] for ln in lines)
        bh = (len(lines) * 74 + 56) * s
        bw = (tw + 170 * s) * G.clamp(p, 0, 1.1)
        y = L.badge_y
        x0, x1 = L.cx - bw / 2, L.cx + bw / 2
        cv.skew_box(x0, y - bh / 2, x1, y + bh / 2, (*self.c["deep"], 235), a, self.skew)
        if p > 0.5:
            icx = (x1 - 62 * s) if L.lang == "ar" else (x0 + 62 * s + math.tan(math.radians(self.skew)) * bh * 0.5)
            cv.rrect((icx - 40 * s, y - 40 * s, icx + 40 * s, y + 40 * s), 40 * s, col, a)
            ip = G.clamp(G.prog(t, ov.get("start", 0.4) + 0.15, 0.3))
            if good:
                cv.icon_check((icx, y + 3 * s), 50, self.c["white"], a, ip)
            else:
                cv.icon_x((icx, y), 50, self.c["white"], a, ip)
            tx = icx - L.dir * 0 + (-70 * s if L.lang == "ar" else 70 * s)
            for j, ln in enumerate(lines):
                cv.text((tx, y + (j - (len(lines) - 1) / 2) * 74 * s + 4 * s), ln, f, alpha=a * G.clamp((p - 0.5) * 2),
                        anchor=L.anchor, shadow=False)

    def ov_checklist(self, cv, ov, t, T, fr, sf, idx):
        L, s = self.L, cv.s
        dim = G.ease_out(G.prog(t, 0, 0.4))
        if L.vertical:
            cv.rrect((0, 0, L.W, L.H), 0, (*self.c["deep"], 150), dim)
            x0, x1 = 0.06 * L.W, 0.94 * L.W
        else:
            cv.rrect((L.col[0] - 40 * s, 0, L.W, L.H), 0, (*self.c["deep"], 170), dim)
            x0, x1 = L.col[0], L.col[1]
        p = G.ease_out(G.prog(t, ov.get("start", 0.2), 0.35))
        cv.text(((x0 + x1) / 2, L.check_y0 - 30 * s), self.pr.text(ov["title"]), cv.font("black", 110), fill=self.c["sky"],
                alpha=p, dy=(1 - p) * 40 * s)
        f = cv.font("black", 52)
        for i, key in enumerate(ov["items"]):
            t0 = ov.get("start", 0.2) + 0.5 + i * 0.6
            pa = G.ease_out(G.prog(t, t0, 0.35))
            y = L.check_y0 + (140 + i * 170) * s
            bx0 = x0 + (1 - pa) * 60 * s
            bx1 = x1 + (1 - pa) * 60 * s
            cv.skew_box(bx0, y - 62 * s, bx1, y + 62 * s, (255, 255, 255, 240), pa, self.skew)
            icx = (bx1 - 80 * s) if L.lang == "ar" else (bx0 + 90 * s)
            cv.rrect((icx - 38 * s, y - 38 * s, icx + 38 * s, y + 38 * s), 12 * s, self.c["sky"], pa)
            cv.icon_check((icx, y + 3 * s), 44, self.c["deep"], pa, G.clamp(G.prog(t, t0 + 0.1, 0.3)))
            tx = icx + (-70 * s if L.lang == "ar" else 70 * s)
            cv.text((tx, y + 5 * s), self.pr.text(key), f, fill=self.c["deep"], alpha=pa, anchor=L.anchor, shadow=False)

    def ov_endcard(self, cv, ov, t, T, fr, sf, idx):
        L, s = self.L, cv.s
        p = G.ease_out(G.prog(t, 0, 0.4))
        cv.rrect((0, 0, L.W, L.H), 0, (*self.c["deep"], 225), p)
        logo = Image.open(os.path.join(self.pr.brand_dir, self.pr.brand["logo_light"])).convert("RGBA")
        lw = int((0.72 * L.W) if L.vertical else (0.42 * L.W))
        lh = int(logo.height * lw / logo.width)
        logo = logo.resize((lw, lh), Image.LANCZOS)
        a = np.asarray(logo).copy()
        a[..., 3] = (a[..., 3] * p).astype(np.uint8)
        cv.im.alpha_composite(Image.fromarray(a), (int(L.W / 2 - lw / 2), int(L.H * 0.42 - lh / 2)))
        pc = G.ease_out(G.prog(t, 0.4, 0.4))
        cv.text((L.W / 2, L.H * 0.42 + lh / 2 + 110 * s), self.pr.text(ov["text"]), cv.font("bold", 54), alpha=pc,
                dy=(1 - pc) * 30 * s)


# ------------------------------------------------------------------ privacy
def blur_face(img, fr, cfg, s):
    """Blur an ellipse around the projected head (every frame; mask derived from 3D)."""
    if not cfg.get("face_blur", True):
        return img, None
    j = fr["joints2d"]
    (lx, ly), (rx, ry) = j["head_l"][:2], j["head_r"][:2]
    (tx, ty), (bx, by) = j["head_t"][:2], j["head_b"][:2]
    cx, cy = (lx + rx + tx + bx) / 4, (ly + ry + ty + by) / 4
    ax = max(abs(rx - lx) / 2, 6) * cfg.get("mask_scale", 1.18) / 1.18
    ay = max(abs(by - ty) / 2, 6) * cfg.get("mask_scale", 1.18) / 1.18
    H, W = img.shape[:2]
    x0, x1 = int(max(0, cx - ax * 1.6)), int(min(W, cx + ax * 1.6))
    y0, y1 = int(max(0, cy - ay * 1.6)), int(min(H, cy + ay * 1.6))
    if x1 <= x0 or y1 <= y0:
        return img, (cx, cy, ax, ay)
    roi = img[y0:y1, x0:x1].copy()
    blk = max(2, int(cfg.get("pixelate", 14) * s))
    if blk > 1:
        small = cv2.resize(roi, (max(1, roi.shape[1] // blk), max(1, roi.shape[0] // blk)), interpolation=cv2.INTER_AREA)
        roi = cv2.resize(small, (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_LINEAR)
    sig = cfg.get("blur_strength", 38) * s
    roi = cv2.GaussianBlur(roi, (0, 0), sig)
    mask = np.zeros(roi.shape[:2], np.float32)
    cv2.ellipse(mask, (int(cx - x0), int(cy - y0)), (int(ax), int(ay)), 0, 0, 360, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (0, 0), max(2, ax * 0.12))[..., None]
    img[y0:y1, x0:x1] = (roi * mask + img[y0:y1, x0:x1] * (1 - mask)).astype(np.uint8)
    return img, (cx, cy, ax, ay)


def zoom_frame(img, fr, z, center):
    H, W = img.shape[:2]
    if z <= 1.0005:
        return img, fr
    cw, ch = W / z, H / z
    x0 = G.clamp(center[0] * W - cw / 2, 0, W - cw)
    y0 = G.clamp(center[1] * H - ch / 2, 0, H - ch)
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    fr = dict(fr)
    fr["joints2d"] = {k: [(v[0] - x0) * z, (v[1] - y0) * z, v[2]] for k, v in fr["joints2d"].items()}
    A = np.array([[z, 0, -x0 * z], [0, z, -y0 * z], [0, 0, 1]])
    fr["P"] = (A @ np.array(fr["P"])).tolist()
    return out, fr


# ------------------------------------------------------------------ sfx
SR = 48000


def sfx_sample(kind, rng):
    t_ = lambda d: np.arange(int(d * SR)) / SR
    if kind == "whoosh":
        n = int(0.42 * SR)
        x = rng.standard_normal(n)
        y = np.zeros(n)
        cut = np.linspace(0.02, 0.32, n) * np.hanning(n) + 0.01
        acc = 0.0
        for i in range(n):
            acc += cut[i] * (x[i] - acc)
            y[i] = acc
        y *= np.hanning(n) ** 1.5
        return 0.5 * y / (np.abs(y).max() + 1e-9)
    if kind in ("pop", "tick"):
        t = t_(0.12)
        f0 = 880 if kind == "pop" else 1500
        return (0.3 if kind == "pop" else 0.22) * np.sin(2 * np.pi * f0 * t * (1 - t * 3)) * np.exp(-t * 45)
    if kind == "good":
        t = t_(0.5)
        return 0.22 * (np.sin(2 * np.pi * 880 * t) + 0.6 * np.sin(2 * np.pi * 1320 * t)) * np.exp(-t * 7)
    if kind == "bad":
        t = t_(0.35)
        return 0.2 * np.sign(np.sin(2 * np.pi * 150 * t)) * np.exp(-t * 8) * (1 - np.exp(-t * 200))
    raise ValueError(kind)


def write_sfx(events, total, path):
    rng = np.random.default_rng(3)
    buf = np.zeros(int(total * SR) + SR)
    for at, kind in events:
        smp = sfx_sample(kind, rng)
        i = int(at * SR)
        if i < len(buf):
            buf[i:i + len(smp)] += smp[:len(buf) - i]
    pcm = (np.clip(buf * 0.85, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.stack([pcm, pcm], 1).tobytes())


# ------------------------------------------------------------------ main compose
def compose(project: Project, planned, aspect, out_dir, preview=None, log=print, ffmpeg="ffmpeg"):
    W, H = project.size(aspect)
    fps = project.fps
    L = Layout(aspect, W, H, project.lang)
    fonts = G.Fonts(project.brand_dir, project.brand["fonts"])
    eng = OverlayEngine(project, L, fonts, project.brand["colors"])
    colors = eng.c
    privacy = project.character.get("privacy", {})
    wipe = int(project.brand.get("style", {}).get("wipe_frames", 12))
    os.makedirs(out_dir, exist_ok=True)

    starts, t0 = [], 0
    for ps in planned:
        starts.append(t0)
        t0 += len(ps["frames"])
    total_frames = t0
    steps_total = max([ps["scene"].get("step", 0) for ps in planned] + [0])

    wm = None
    if project.brand.get("style", {}).get("watermark", True):
        logo = Image.open(os.path.join(project.brand_dir, project.brand["logo_light"])).convert("RGBA")
        ww = int((0.26 if L.vertical else 0.14) * W)
        wm = logo.resize((ww, int(logo.height * ww / logo.width)), Image.LANCZOS)
        a = np.asarray(wm).copy()
        a[..., 3] = (a[..., 3] * 0.85).astype(np.uint8)
        wm = Image.fromarray(a)

    enc = None
    video_path = os.path.join(out_dir, "video_only.mp4")
    if preview is None:
        enc = subprocess.Popen([ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                                "-pix_fmt", "yuv420p", "-movflags", "+faststart", video_path], stdin=subprocess.PIPE)
    sfx, vo_rows, privacy_log = [], [], []

    for si, ps in enumerate(planned):
        sc = ps["scene"]
        n = len(ps["frames"])
        T = n / fps
        frames_meta = []
        for pth in ps["paths"]:
            with open(pth[:-4] + ".json") as fh:
                frames_meta.append(json.load(fh))
        gstart = starts[si] / fps
        if sc.get("vo"):
            vo_rows.append((gstart, gstart + T, sc["id"], project.text(sc["vo"])))
        # sfx cues
        if si > 0 and sc.get("transition", "wipe") != "cut":
            sfx.append((max(0, gstart - wipe / 2 / fps), "whoosh"))
        for ov in sc.get("overlays", []):
            st = ov.get("start", 0.0)
            if ov["type"] == "badge":
                sfx.append((gstart + st, "good" if ov["kind"] == "good" else "bad"))
            elif ov["type"] == "bullets":
                sfx += [(gstart + st + i * ov.get("gap", 0.8), "pop") for i in range(len(ov["items"]))]
            elif ov["type"] == "checklist":
                sfx += [(gstart + st + 0.5 + i * 0.6, "pop") for i in range(len(ov["items"]))]
            elif ov["type"] in ("step", "header", "section", "title"):
                sfx.append((gstart + st + 0.05, "tick"))

        for i in range(n):
            gi = starts[si] + i
            if preview is not None and not any(abs(gi / fps - p) < 0.5 / fps for p in preview):
                continue
            t = i / fps
            img = cv2.imread(ps["paths"][i])
            fr = frames_meta[i]
            z0, z1 = sc.get("zoom", [1.0, 1.0])
            z = z0 + (z1 - z0) * G.ease_in_out(i / max(1, n - 1))
            img, fr = zoom_frame(img, fr, z, sc.get("zoom_center", [0.5, 0.5]))
            img, m = blur_face(img, fr, privacy, L.s)
            privacy_log.append(m is not None)
            rgb = Image.fromarray(img[:, :, ::-1]).convert("RGBA")
            cv = G.Canvas(W, H, fonts, project.lang, L.s)
            # zoomed metadata for trails
            sf = frames_meta  # trails use raw coordinates (scenes with trails are not zoomed)
            for ov in sc.get("overlays", []):
                eng.draw(cv, ov, t, T, fr, sf, i)
            # progress bar for numbered steps
            if sc.get("step") and steps_total:
                seg_w = (L.col[1] - L.col[0] - 12 * L.s * (steps_total - 1)) / steps_total
                for k in range(steps_total):
                    if L.lang == "ar":
                        xr = L.col[1] - k * (seg_w + 12 * L.s)
                        xl = xr - seg_w
                    else:
                        xl = L.col[0] + k * (seg_w + 12 * L.s)
                        xr = xl + seg_w
                    y = L.progress_y
                    cv.skew_box(xl, y - 7 * L.s, xr, y + 7 * L.s, (255, 255, 255, 90), 1.0, 30, shadow=False)
                    fill = 1.0 if k + 1 < sc["step"] else (G.clamp(t / T) if k + 1 == sc["step"] else 0)
                    if fill > 0:
                        if L.lang == "ar":
                            cv.skew_box(xr - seg_w * fill, y - 7 * L.s, xr, y + 7 * L.s, colors["sky"], 1.0, 30, shadow=False)
                        else:
                            cv.skew_box(xl, y - 7 * L.s, xl + seg_w * fill, y + 7 * L.s, colors["sky"], 1.0, 30, shadow=False)
            if wm is not None and sc["id"] not in ("end",):
                mx = int(0.05 * W) if project.lang == "ar" or not L.vertical else int(W - wm.width - 0.05 * W)
                cv.im.alpha_composite(wm, (int(W - wm.width - 0.04 * W) if not L.vertical else mx, int(0.025 * H)))
            rgb.alpha_composite(cv.im)
            # diagonal two-band wipe around scene boundaries
            for bj, b0 in enumerate(starts[1:], start=1):
                if planned[bj]["scene"].get("transition", "wipe") == "cut":
                    continue
                pp = (gi - (b0 - wipe / 2)) / wipe
                if 0 <= pp <= 1:
                    draw_wipe(rgb, pp, colors, W, H, L.s)
            out = np.asarray(rgb.convert("RGB"))
            if enc:
                enc.stdin.write(out.tobytes())
            else:
                Image.fromarray(out).save(os.path.join(out_dir, f"preview_{gi / fps:06.2f}.jpg"), quality=90)
        log(f"[compose] {aspect} scene {sc['id']} ({T:.1f}s)")

    total = total_frames / fps
    if enc:
        enc.stdin.close()
        enc.wait()
        write_sfx(sfx, total, os.path.join(out_dir, "sfx.wav"))
    return {"total": total, "vo": vo_rows, "privacy_ok": all(privacy_log), "frames": total_frames,
            "video": video_path}


def draw_wipe(rgb, p, colors, W, H, s):
    from PIL import ImageDraw
    d = ImageDraw.Draw(rgb)
    k = math.tan(math.radians(20)) * H
    span = W + k
    for off, col in ((0.0, colors["navy"]), (0.12, colors["sky"])):
        q = G.ease_in_out(G.clamp((p - off) / (1 - 0.12)))
        # band enters from the right, covers, exits to the left
        center = W + k - q * (span + W + k) * 1.0
        half = W * 0.75
        x0, x1 = center - half, center + half
        d.polygon([(x0 + k, 0), (x1 + k, 0), (x1, H), (x0, H)], fill=col)
