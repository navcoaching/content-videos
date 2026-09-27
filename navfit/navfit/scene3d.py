"""Blender (bpy) scene: the NavFit character, studio set, cameras, frame rendering.

Rendering uses the Workbench engine (≈1 s/frame at 1080x1920 on CPU with Mesa
llvmpipe) — a clean, shaded "3D explainer" look with outlines and soft shadows.

The character is built from smooth lofted rigid parts, one set per body segment
(see motion.SEGMENTS). A pose is applied by moving every part with its segment
transform, so there is no skinning distortion at deep knee/hip angles and the
chest logo never stretches.
"""
from __future__ import annotations

import json
import math
import os

import bpy
import cv2
import mathutils
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils.geometry import tessellate_polygon

from .motion import Body, rest_joints


def srgb_to_linear(hex_color, alpha=1.0):
    h = hex_color.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, alpha)


# ------------------------------------------------------------------ mesh helpers
def loft(name, stations, ring=28, cap_start=True, cap_end=True):
    """stations: list of (center(3), u(3), v(3), ru, rv[, squareness]) — an ellipse
    ring per station in the plane spanned by unit vectors u, v."""
    verts, faces = [], []
    for c, u, v, ru, rv, *rest in stations:
        sq = rest[0] if rest else 2.0
        c, u, v = map(np.asarray, (c, u, v))
        for k in range(ring):
            a = 2 * math.pi * k / ring
            ca, sa = math.cos(a), math.sin(a)
            # superellipse for boxier shapes (shoe soles etc.)
            ex = math.copysign(abs(ca) ** (2 / sq), ca)
            ey = math.copysign(abs(sa) ** (2 / sq), sa)
            verts.append(tuple(c + u * ru * ex + v * rv * ey))
    n = len(stations)
    for i in range(n - 1):
        for k in range(ring):
            a, b = i * ring + k, i * ring + (k + 1) % ring
            faces.append((a, b, b + ring, a + ring))
    if cap_start:
        verts.append(tuple(np.asarray(stations[0][0])))
        ci = len(verts) - 1
        faces += [(ci, (k + 1) % ring, k) for k in range(ring)]
    if cap_end:
        verts.append(tuple(np.asarray(stations[-1][0])))
        ci = len(verts) - 1
        base = (n - 1) * ring
        faces += [(ci, base + k, base + (k + 1) % ring) for k in range(ring)]
    return mesh_obj(name, verts, faces)


def mesh_obj(name, verts, faces, smooth=True):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate()
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def ellipsoid(name, center, r, seg=32, rings=16):
    verts, faces = [], []
    cx, cy, cz = center
    rx, ry, rz = r
    for i in range(1, rings):
        th = math.pi * i / rings
        for k in range(seg):
            ph = 2 * math.pi * k / seg
            verts.append((cx + rx * math.sin(th) * math.cos(ph), cy + ry * math.sin(th) * math.sin(ph),
                          cz + rz * math.cos(th)))
    top = len(verts)
    verts.append((cx, cy, cz + rz))
    bot = len(verts)
    verts.append((cx, cy, cz - rz))
    for i in range(rings - 2):
        for k in range(seg):
            a, b = i * seg + k, i * seg + (k + 1) % seg
            faces.append((a, a + seg, b + seg, b))
    faces += [(top, k, (k + 1) % seg) for k in range(seg)]
    base = (rings - 2) * seg
    faces += [(bot, base + (k + 1) % seg, base + k) for k in range(seg)]
    return mesh_obj(name, verts, faces)


def vstations(points, radii, ring_axes=((1, 0, 0), (0, 1, 0)), sq=2.0):
    """Stations along a (near-vertical) path; radii = [(rx, ry), ...]."""
    u, v = ring_axes
    return [(p, u, v, rx, ry, sq) for p, (rx, ry) in zip(points, radii)]


def lerp(a, b, t):
    return np.asarray(a) + (np.asarray(b) - np.asarray(a)) * t


def material(name, hex_color):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = srgb_to_linear(hex_color)
    m.roughness = 0.6
    return m


def set_mat(ob, mat):
    ob.data.materials.clear()
    ob.data.materials.append(mat)


# ------------------------------------------------------------------ logo
def logo_mesh(name, png_path, width_m, center_z, surface_rx, surface_ry, surface_y0, lift=0.004):
    """Trace the logo alpha into polygons and wrap them onto the hoodie front
    (elliptic cylinder x²/rx² + (y-y0)²/ry² = 1). Proportions are preserved:
    horizontal logo units map to arc length on the chest."""
    img = cv2.imread(png_path, cv2.IMREAD_UNCHANGED)
    alpha = img[..., 3] if img.shape[2] == 4 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ys, xs = np.where(alpha > 20)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    alpha = alpha[y0:y1 + 1, x0:x1 + 1]
    h_px, w_px = alpha.shape
    scale = width_m / w_px
    _, bw = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)
    contours, hier = cv2.findContours(bw, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    hier = hier[0]

    def to3d(px, py):
        # arc-length wrap around the chest
        s = (px - w_px / 2) * scale
        theta = s / surface_rx  # approximate (good near the front centre)
        x = surface_rx * math.sin(theta)
        y = surface_y0 - (surface_ry + lift) * math.cos(theta)
        z = center_z + (h_px / 2 - py) * scale
        return (x, y, z)

    verts, faces = [], []
    for i, c in enumerate(contours):
        if hier[i][3] != -1:
            continue  # holes are handled with their parent
        loops = [c]
        ch = hier[i][2]
        while ch != -1:
            loops.append(contours[ch])
            ch = hier[ch][0]
        polys = []
        for lp in loops:
            eps = 0.6
            ap = cv2.approxPolyDP(lp, eps, True).reshape(-1, 2)
            if len(ap) >= 3:
                polys.append([(float(p[0]), float(-p[1]), 0.0) for p in ap])
        if not polys:
            continue
        tris = tessellate_polygon(polys)
        flat = [p for poly in polys for p in poly]
        base = len(verts)
        verts += [to3d(p[0], -p[1]) for p in flat]
        faces += [(base + a, base + b, base + c) for a, b, c in tris]
    ob = mesh_obj(name, verts, faces, smooth=False)
    # make every face point outwards (towards -Y)
    for p in ob.data.polygons:
        if p.normal.y > 0:
            p.flip()
    return ob, (w_px, h_px)


# ------------------------------------------------------------------ character
class Character:
    def __init__(self, cfg, brand_dir):
        self.cfg = cfg
        self.body = Body()
        self.rest = rest_joints(self.body)
        self.parts = {}  # segment -> [objects]
        self.brand_dir = brand_dir
        self.build()

    def add(self, seg, ob, mat):
        set_mat(ob, mat)
        self.parts.setdefault(seg, []).append(ob)
        return ob

    def build(self):
        c = self.cfg
        J, b = self.rest, self.body
        hood = material("hoodie", c["hoodie_color"])
        hood_dark = material("hoodie_trim", c.get("hoodie_trim_color", c["hoodie_color"]))
        hood_in = material("hood_inside", c.get("hood_inside_color", "#0E5E7A"))
        pants = material("pants", c["pants_color"])
        skin = material("skin", c.get("skin_color", "#C99A7B"))
        shoe = material("shoe", c.get("shoe_color", "#F4F6F8"))
        sole = material("sole", c.get("sole_color", "#2B303A"))
        logo_mat = material("logo", c.get("logo_color", "#FFFFFF"))
        string = material("string", c.get("drawstring_color", "#F4F6F8"))

        X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
        P = J["pelvis"]

        # ---- torso (hoodie), two overlapping shells: abdomen + chest
        hem = P[2] - 0.035
        ab = [(hem - 0.005, 0.165, 0.118), (hem + 0.02, 0.172, 0.123), (hem + 0.03, 0.168, 0.121),
              (P[2] + 0.08, 0.158, 0.116), (J["waist"][2] + 0.0, 0.148, 0.108)]
        self.add("abdomen", loft("hoodie_abdomen", [((0, 0.004, z), X, Y, rx, ry) for z, rx, ry in ab]), hood)
        band = [(hem - 0.012, 0.164, 0.117), (hem + 0.018, 0.169, 0.121)]
        self.add("abdomen", loft("hoodie_hem", [((0, 0.004, z), X, Y, rx + 0.004, ry + 0.004) for z, rx, ry in band]),
                 hood_dark)
        wz = J["waist"][2]
        ch = [(wz - 0.075, 0.163, 0.121, 0.004), (wz - 0.05, 0.161, 0.12, 0.004), (wz + 0.06, 0.160, 0.122, 0.0), (wz + 0.15, 0.170, 0.132, -0.006),
              (wz + 0.215, 0.180, 0.124, -0.002), (wz + 0.255, 0.188, 0.108, 0.006), (wz + 0.285, 0.16, 0.095, 0.01),
              (wz + 0.305, 0.10, 0.078, 0.01), (wz + 0.312, 0.07, 0.065, 0.01)]
        self.chest_profile = ch
        self.add("chest", loft("hoodie_chest", [((0, y, z), X, Y, rx, ry) for z, rx, ry, y in ch]), hood)
        # kangaroo pocket (a flattened pad on the lower front)
        pk = [(P[2] + 0.00, 0.105, 0.012), (P[2] + 0.06, 0.112, 0.014), (P[2] + 0.12, 0.09, 0.010)]
        self.add("abdomen", loft("pocket", [((0, -0.117, z), X, Y, rx, ry, 3.0) for z, rx, ry in pk]), hood_dark)

        # ---- collar + hood (hood on head segment)
        col = [(J["neck"][2] - 0.035, 0.105, 0.09), (J["neck"][2] + 0.01, 0.095, 0.085),
               (J["neck"][2] + 0.045, 0.085, 0.082)]
        self.add("chest", loft("collar", [((0, 0.012, z), X, Y, rx, ry) for z, rx, ry in col]), hood)
        hc = J["head"] + np.array([0, 0.012, 0.004])
        hood_ob = ellipsoid("hood", hc, (0.126, 0.136, 0.138), seg=96, rings=64)
        # open the face: delete faces looking forward (-Y) within a cone, and the bottom
        me = hood_ob.data
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(me)
        kill = []
        for f in bm.faces:
            cc = f.calc_center_median() - mathutils.Vector(hc)
            d = cc.normalized()
            face_open = d.y < -0.2 and (d.x / 0.62) ** 2 + ((d.z + 0.08) / 0.8) ** 2 < 1.0
            if face_open or d.z < -0.82:
                kill.append(f)
        bmesh.ops.delete(bm, geom=kill, context="FACES")
        bm.to_mesh(me)
        bm.free()
        sol = hood_ob.modifiers.new("solid", "SOLIDIFY")
        sol.thickness = 0.014
        sol.offset = 1.0
        sol.material_offset = 1
        sol.use_rim = True
        hood_ob.data.materials.append(hood)
        hood_ob.data.materials.append(hood_in)
        self.parts.setdefault("head", []).append(hood_ob)
        # hood drape: fabric falling from the hood onto the upper back/shoulders
        nz = J["neck"][2]
        dr = [(nz - 0.05, 0.13, 0.10, 0.03), (nz + 0.01, 0.12, 0.105, 0.035), (nz + 0.06, 0.105, 0.105, 0.035)]
        self.add("chest", loft("hood_drape", [((0, y, z), X, Y, rx, ry) for z, rx, ry, y in dr]), hood)
        # face/head (always blurred in post) and neck
        self.add("head", ellipsoid("head", J["head"] + np.array([0, -0.004, 0]), (0.078, 0.092, 0.1)), skin)
        self.add("head", loft("neck", vstations([J["neck"] - [0, 0, 0.03], J["head_joint"] + [0, 0, 0.04]],
                                                [(0.045, 0.048), (0.043, 0.046)])), skin)
        # drawstrings
        for sx in (1, -1):
            top = np.array([sx * 0.035, -0.085, J["neck"][2] - 0.01])
            self.add("chest", loft(f"string_{sx}", vstations([top, top + [0, -0.012, -0.13]],
                                                             [(0.006, 0.006), (0.006, 0.006)], sq=2.0)), string)
            self.add("chest", ellipsoid(f"aglet_{sx}", top + [0, -0.012, -0.135], (0.009, 0.009, 0.014)), string)

        # ---- logo on the chest
        logo_path = os.path.join(self.brand_dir, c["logo_on_hoodie"])
        lz = wz + c.get("logo_height_on_chest", 0.155)
        # hoodie surface at that height (interpolate chest profile)
        zs = [p[0] for p in ch]
        rx = float(np.interp(lz, zs, [p[1] for p in ch]))
        ry = float(np.interp(lz, zs, [p[2] for p in ch]))
        y0 = float(np.interp(lz, zs, [p[3] for p in ch]))
        logo_ob, _ = logo_mesh("logo", logo_path, c.get("logo_width_m", 0.2), lz, rx, ry, y0)
        self.add("chest", logo_ob, logo_mat)

        # ---- arms (sleeves), hands
        for s, sx in (("L", 1), ("R", -1)):
            S, E, W, H = J[f"shoulder_{s}"], J[f"elbow_{s}"], J[f"wrist_{s}"], J[f"hand_{s}"]
            self.add(f"upper_arm_{s}", ellipsoid(f"shoulder_{s}", S + [-sx * 0.006, 0, -0.012], (0.058, 0.06, 0.062)), hood)
            ua = [lerp(S, E, t) for t in (0.0, 0.3, 0.7, 1.0)]
            self.add(f"upper_arm_{s}", loft(f"sleeve_up_{s}", vstations(ua, [(0.057, 0.058), (0.055, 0.055),
                                                                         (0.05, 0.05), (0.047, 0.047)])), hood)
            self.add(f"forearm_{s}", ellipsoid(f"elbow_{s}", E, (0.047, 0.047, 0.048)), hood)
            fa = [lerp(E, W, t) for t in (0.0, 0.4, 0.82, 0.9, 1.0)]
            self.add(f"forearm_{s}", loft(f"sleeve_lo_{s}", vstations(fa, [(0.05, 0.049), (0.05, 0.048), (0.043, 0.042),
                                                                         (0.043, 0.042), (0.04, 0.039)])), hood)
            self.add(f"forearm_{s}", loft(f"cuff_{s}", vstations([lerp(E, W, 0.84), W], [(0.045, 0.044), (0.042, 0.041)])),
                     hood_dark)
            hd = W + (H - W) * 1.0
            self.add(f"hand_{s}", ellipsoid(f"hand_{s}", lerp(W, hd, 0.55) + [0, 0, -0.02], (0.026, 0.045, 0.075)), skin)

        # ---- pelvis (pants) + legs
        pz = P[2]
        pel = [(pz - 0.13, 0.155, 0.105, 0.004), (pz - 0.07, 0.172, 0.118, 0.012), (pz - 0.01, 0.17, 0.115, 0.008),
               (pz + 0.03, 0.16, 0.11, 0.004)]
        self.add("pelvis", loft("pants_pelvis", [((0, y, z), X, Y, rx, ry) for z, rx, ry, y in pel]), pants)
        for s, sx in (("L", 1), ("R", -1)):
            Hh, K, A = J[f"hip_{s}"], J[f"knee_{s}"], J[f"ankle_{s}"]
            self.add(f"thigh_{s}", ellipsoid(f"hipball_{s}", Hh + [sx * 0.005, 0.005, -0.01], (0.088, 0.092, 0.095)), pants)
            th = [lerp(Hh, K, t) + [0, off, 0] for t, off in ((0.0, 0.004), (0.25, 0.006), (0.6, 0.0), (0.9, -0.004),
                                                              (1.0, -0.004))]
            self.add(f"thigh_{s}", loft(f"thigh_{s}", vstations(th, [(0.088, 0.092), (0.083, 0.086), (0.07, 0.072),
                                                                    (0.058, 0.06), (0.056, 0.058)])), pants)
            self.add(f"shin_{s}", ellipsoid(f"knee_{s}", K + [0, -0.004, 0], (0.058, 0.06, 0.062)), pants)
            sh = [lerp(K, A, t) + [0, off, 0] for t, off in ((0.0, 0.0), (0.28, 0.012), (0.6, 0.006), (0.86, 0.0),
                                                             (1.0, 0.0))]
            self.add(f"shin_{s}", loft(f"shin_{s}", vstations(sh, [(0.055, 0.057), (0.056, 0.063), (0.047, 0.05),
                                                                  (0.038, 0.04), (0.036, 0.038)])), pants)
            self.add(f"shin_{s}", loft(f"jogger_cuff_{s}", vstations([lerp(K, A, 0.85), lerp(K, A, 1.0)],
                                                                     [(0.041, 0.043), (0.04, 0.042)])), pants)
            # shoe: along the (toe-out) foot direction
            yaw = math.radians(sx * b.toe_out_deg)
            f = np.array([math.sin(yaw), -math.cos(yaw), 0])
            lat = np.array([math.cos(yaw), math.sin(yaw), 0]) * (1 if sx > 0 else 1)
            up = np.array([0, 0, 1.0])
            base = np.array([A[0], A[1], 0.0])
            st = []
            for d, w, h, zc in ((-0.075, 0.03, 0.035, 0.05), (-0.062, 0.042, 0.05, 0.055), (-0.02, 0.048, 0.052, 0.055),
                                (0.05, 0.05, 0.043, 0.047), (0.12, 0.049, 0.034, 0.04), (0.175, 0.04, 0.026, 0.034),
                                (0.2, 0.022, 0.016, 0.03)):
                st.append((base + f * d + up * zc, lat, up, w, h, 2.6))
            self.add(f"foot_{s}", loft(f"shoe_{s}", st), shoe)
            so = []
            for d, w in ((-0.078, 0.028), (-0.066, 0.043), (0.0, 0.049), (0.12, 0.052), (0.185, 0.042), (0.212, 0.02)):
                so.append((base + f * d + up * 0.011, lat, up, w + 0.003, 0.012, 3.5))
            self.add(f"foot_{s}", loft(f"sole_{s}", so), sole)
            # laces stripe
            self.add(f"foot_{s}", loft(f"tongue_{s}", [(base + f * d + up * (zc + 0.002), lat, up, 0.022, h, 2.2)
                                                      for d, zc, h in ((0.0, 0.085, 0.012), (0.09, 0.07, 0.01))]), sole)

    # pose application ----------------------------------------------------
    def apply(self, pose):
        for seg, obs in self.parts.items():
            R, origin = pose.seg[seg]
            prox = self.rest[_prox(seg)]
            M = np.eye(4)
            M[:3, :3] = R
            M[:3, 3] = np.asarray(origin) - R @ prox
            mw = mathutils.Matrix(M.tolist())
            for ob in obs:
                ob.matrix_world = mw


def _prox(seg):
    from .motion import SEGMENTS
    return SEGMENTS[seg][0]


# ------------------------------------------------------------------ studio
def build_studio(style):
    floor = material("floor", style.get("floor_color", "#E7ECF1"))
    wall = material("wall", style.get("wall_color", "#DDE4EB"))
    plat = material("platform", style.get("platform_color", "#15213B"))
    ring = material("platform_ring", style.get("accent_color", "#1CB8E8"))
    # floor disk + cyclorama wall
    bpy.ops.mesh.primitive_circle_add(vertices=96, radius=9, fill_type="NGON", location=(0, 0, 0))
    set_mat(bpy.context.object, floor)
    verts, faces = [], []
    n, r = 96, 9.0
    for i in range(n):
        a = 2 * math.pi * i / n
        for k, (rr, z) in enumerate(((r, 0.0), (r, 6.0))):
            verts.append((rr * math.cos(a), rr * math.sin(a), z))
    for i in range(n):
        a, b2 = 2 * i, 2 * ((i + 1) % n)
        faces.append((a, b2, b2 + 1, a + 1))
    set_mat(mesh_obj("cyc", verts, faces), wall)
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.78, depth=0.02, location=(0, -0.02, 0.0))
    set_mat(bpy.context.object, plat)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.78, minor_radius=0.012, location=(0, -0.02, 0.012),
                                     major_segments=96, minor_segments=8)
    set_mat(bpy.context.object, ring)


def setup_render(w, h, style):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    sc.display.render_aa = style.get("aa", "8")
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.studio_light = style.get("studio_light", "Default")
    sh.color_type = "MATERIAL"
    sh.show_shadows = True
    sh.shadow_intensity = 0.45
    sh.show_cavity = True
    sh.cavity_type = "WORLD"
    sh.cavity_ridge_factor = 0.6
    sh.cavity_valley_factor = 0.8
    sh.show_object_outline = False
    sh.object_outline_color = (0.05, 0.08, 0.14)
    sh.show_specular_highlight = True
    sc.display.light_direction = (0.35, -0.45, 0.82)
    sc.display.shadow_shift = 0.05
    sc.display.shadow_focus = 0.3
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = style.get("exposure", 0.0)


def make_camera(name, preset, aspect):
    """preset: azimuth (deg, 0 = front, +90 = her right side), elevation (deg),
    target (x,y,z), coverage (metres of subject height that fit vertically in 9:16;
    for 16:9 the same vertical coverage * 0.82 is used), focal (mm)."""
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam)
    az = math.radians(preset.get("azimuth", 0))
    el = math.radians(preset.get("elevation", 4))
    focal = preset.get("focal", 60)
    if aspect == "9:16":
        target = mathutils.Vector(preset.get("target_v", preset.get("target", (0, 0, 0.95))))
        cov = preset.get("coverage_v", preset.get("coverage", 2.3))
    else:
        target = mathutils.Vector(preset.get("target", (0, 0, 0.95)))
        cov = preset.get("coverage", 2.3) * 0.86
    cam_data.sensor_fit = "VERTICAL"
    cam_data.sensor_height = 24
    cam_data.lens = focal
    dist = cov * focal / 24
    # azimuth 0: camera at -Y (in front); +90: camera at -X (her right side, she faces image-right)
    d = mathutils.Vector((-math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    cam.location = target + d * dist
    rot = (target - cam.location).to_track_quat("-Z", "Y")
    cam.rotation_euler = rot.to_euler()
    cam_data.clip_end = 60
    cam_data.shift_x = preset.get("shift_x_16x9", 0.0) if aspect == "16:9" else preset.get("shift_x", 0.0)
    return cam


def camera_matrix(cam, w, h):
    """3x4 pixel projection matrix (so overlays can project any 3D point)."""
    cd = cam.data
    f = cd.lens / cd.sensor_height * h if cd.sensor_fit == "VERTICAL" else cd.lens / cd.sensor_width * w
    m = h if cd.sensor_fit == "VERTICAL" else w  # Blender shift unit follows the fitted axis
    K = np.array([[f, 0, w / 2 - cd.shift_x * m], [0, f, h / 2 + cd.shift_y * m], [0, 0, 1]])
    V = np.array(cam.matrix_world.inverted())
    # camera looks down -Z with +Y up; image y grows downwards
    flip = np.diag([1, -1, -1])
    return K @ flip @ V[:3, :]


def project(cam, pts, w, h):
    sc = bpy.context.scene
    out = {}
    for k, p in pts.items():
        v = world_to_camera_view(sc, cam, mathutils.Vector(tuple(p)))
        out[k] = [v.x * w, (1 - v.y) * h, v.z]
    return out


class Renderer:
    """Builds the scene once, then renders (camera, pose) frames on demand."""

    def __init__(self, character_cfg, studio_cfg, cameras_cfg, brand_dir, aspect, size):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.w, self.h = size
        self.aspect = aspect
        build_studio(studio_cfg)
        self.char = Character(character_cfg, brand_dir)
        setup_render(self.w, self.h, studio_cfg)
        self.cams = {k: make_camera(k, v, aspect) for k, v in cameras_cfg.items()}
        self.head_r = self.char.body.head_r

    def render_preset(self, preset, pose, out_png):
        """Render with an ad-hoc camera (e.g. orbit moves)."""
        old = self.cams.get("_dyn")
        if old is not None:
            bpy.data.objects.remove(old, do_unlink=True)
        self.cams["_dyn"] = make_camera("_dyn", preset, self.aspect)
        return self.render("_dyn", pose, out_png)

    def render(self, cam_name, pose, out_png):
        sc = bpy.context.scene
        self.char.apply(pose)
        cam = self.cams[cam_name]
        sc.camera = cam
        sc.render.filepath = out_png
        bpy.ops.render.render(write_still=True)
        pts = dict(pose.joints)
        pts["com"] = pose.info.get("com", pose.joints["pelvis"])
        pts["com_floor"] = np.array([pts["com"][0], pts["com"][1], 0.0])
        pts["midfoot_floor"] = np.array([0.0, pose.info["midfoot"][1], 0.0]) if "midfoot" in pose.info else pts["pelvis"]
        # head sphere extents for the privacy mask (4 points around the face)
        hc = np.asarray(pose.joints["head"])
        cam_pos = np.array(cam.matrix_world.translation)
        view = hc - cam_pos
        view /= np.linalg.norm(view)
        up = np.array([0, 0, 1.0])
        right = np.cross(view, up)
        right /= np.linalg.norm(right)
        up2 = np.cross(right, view)
        r = self.head_r * 1.35
        pts["head_l"], pts["head_r"] = hc - right * r, hc + right * r
        pts["head_t"], pts["head_b"] = hc + up2 * r, hc - up2 * r
        proj = project(cam, pts, self.w, self.h)
        P = camera_matrix(cam, self.w, self.h)
        info = {k: (float(v) if isinstance(v, (int, float, np.floating)) else None) for k, v in pose.info.items()}
        info = {k: v for k, v in info.items() if v is not None}
        with open(out_png[:-4] + ".json", "w") as fh:
            json.dump({"joints2d": proj, "joints3d": {k: list(map(float, v)) for k, v in pts.items()},
                       "P": P.tolist(), "info": info}, fh)
