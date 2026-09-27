"""Kinematic body model and exercise motion generators.

World frame (Blender): +Z up, the character faces -Y, her left side is +X.
Every rigid body segment has a rest frame equal to the world axes placed at its
proximal joint, so a posed segment is fully described by (R, origin):
    world_point = origin + R @ (rest_point - rest_origin)

Motions are generated from biomechanical constraints instead of hand keys:
feet stay planted, legs are solved with two-bone IK, and the pelvis fore-aft
position is solved every frame so the whole-body centre of mass (segment mass
fractions after Dempster/Winter) stays over the mid-foot.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

# ------------------------------------------------------------------ body
@dataclass
class Body:
    """Segment lengths in metres (athletic female, ~1.66 m)."""
    ankle_h: float = 0.075
    shin: float = 0.39
    thigh: float = 0.40
    hip_half: float = 0.085          # hip joint lateral offset
    pelvis_up: float = 0.06          # pelvis centre above hip joints
    abdomen: float = 0.17            # pelvis centre -> waist joint
    chest: float = 0.305             # waist -> neck base
    shoulder_up: float = 0.27        # waist -> shoulder joint height
    shoulder_half: float = 0.165
    neck: float = 0.07
    head_c: float = 0.095            # neck top -> head centre
    head_r: float = 0.105
    upper_arm: float = 0.27
    forearm: float = 0.23
    hand: float = 0.08
    stance_half: float = 0.165       # ankle lateral offset (~shoulder width)
    toe_out_deg: float = 20.0
    heel: float = 0.055              # ankle -> heel (backwards)
    ball: float = 0.135              # ankle -> ball of foot (forwards)
    toe: float = 0.19                # ankle -> toe tip

    @property
    def hip_h(self):
        return self.ankle_h + self.shin + self.thigh - 0.004


# segment mass fraction, COM position along segment (0 proximal .. 1 distal)
MASS = {
    "pelvis": (0.142, 0.4), "abdomen": (0.139, 0.5), "chest": (0.216, 0.55),
    "head": (0.081, 0.6),
    "upper_arm": (0.028, 0.436), "forearm": (0.016, 0.43), "hand": (0.006, 0.5),
    "thigh": (0.100, 0.433), "shin": (0.0465, 0.433), "foot": (0.0145, 0.5),
}


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def frame_from(down, lateral):
    """Rotation whose local -Z maps to `down` and local +X is close to `lateral`."""
    z = -np.asarray(down, float)
    z /= np.linalg.norm(z)
    x = np.asarray(lateral, float) - np.dot(lateral, z) * z
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return np.stack([x, y, z], axis=1)


def two_bone_ik(root, target, l1, l2, pole):
    d = target - root
    D = min(np.linalg.norm(d), l1 + l2 - 1e-5)
    u = d / np.linalg.norm(d)
    a = (l1 * l1 - l2 * l2 + D * D) / (2 * D)
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))
    v = pole - np.dot(pole, u) * u
    v /= np.linalg.norm(v)
    return root + a * u + h * v


# ------------------------------------------------------------------ rest pose
def rest_joints(b: Body):
    """Joint positions of the neutral standing pose (used to model the meshes)."""
    j = {}
    P = np.array([0.0, 0.0, b.hip_h + b.pelvis_up])
    j["pelvis"] = P
    j["waist"] = P + [0, 0, b.abdomen]
    j["neck"] = j["waist"] + [0, 0, b.chest]
    j["head_joint"] = j["neck"] + [0, 0, b.neck]
    j["head"] = j["head_joint"] + [0, 0, b.head_c]
    for side, sx in (("L", 1), ("R", -1)):
        j[f"hip_{side}"] = P + [sx * b.hip_half, 0, -b.pelvis_up]
        j[f"ankle_{side}"] = np.array([sx * b.stance_half, 0.0, b.ankle_h])
        # rest legs: straight line hip->ankle, knee on it
        H, A = j[f"hip_{side}"], j[f"ankle_{side}"]
        j[f"knee_{side}"] = A + (H - A) * (b.shin / (b.shin + b.thigh))
        S = j["waist"] + [sx * b.shoulder_half, 0, b.shoulder_up]
        j[f"shoulder_{side}"] = S
        j[f"elbow_{side}"] = S + [sx * 0.02, 0, -b.upper_arm]
        j[f"wrist_{side}"] = j[f"elbow_{side}"] + [sx * 0.01, 0, -b.forearm]
        j[f"hand_{side}"] = j[f"wrist_{side}"] + [0, 0, -b.hand * 0.6]
        yaw = rot_z(sx * math.radians(b.toe_out_deg))
        j[f"heel_{side}"] = A + yaw @ [0, b.heel, -b.ankle_h]
        j[f"ball_{side}"] = A + yaw @ [0, -b.ball, -b.ankle_h]
        j[f"toe_{side}"] = A + yaw @ [0, -b.toe, -b.ankle_h + 0.02]
    return j


# segment -> (proximal joint, distal joint) in the rest pose
SEGMENTS = {
    "pelvis": ("pelvis", None), "abdomen": ("pelvis", "waist"), "chest": ("waist", "neck"),
    "head": ("head_joint", "head"),
}
for _s in "LR":
    SEGMENTS.update({
        f"upper_arm_{_s}": (f"shoulder_{_s}", f"elbow_{_s}"),
        f"forearm_{_s}": (f"elbow_{_s}", f"wrist_{_s}"),
        f"hand_{_s}": (f"wrist_{_s}", f"hand_{_s}"),
        f"thigh_{_s}": (f"hip_{_s}", f"knee_{_s}"),
        f"shin_{_s}": (f"knee_{_s}", f"ankle_{_s}"),
        f"foot_{_s}": (f"ankle_{_s}", f"ball_{_s}"),
    })


@dataclass
class Pose:
    seg: dict = field(default_factory=dict)      # name -> (R, origin)
    joints: dict = field(default_factory=dict)   # name -> world position
    info: dict = field(default_factory=dict)     # angles etc. for overlays


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ squat
@dataclass
class SquatStyle:
    """Parameters of one squat variant. Defaults = the taught technique."""
    thigh_bottom_deg: float = 0.0        # thigh angle below horizontal at the bottom (0 = parallel)
    lean_bottom_deg: float = 40.0        # trunk lean from vertical at the bottom
    lean_stand_deg: float = 3.0
    arms_forward: bool = True
    valgus: float = 0.0                  # 0..1 knees collapsing inward
    heel_lift_deg: float = 0.0           # heel rise at the bottom
    spine_round_deg: float = 0.0         # extra thoracic flexion (+) and pelvic tuck
    com_shift: float = 0.0               # COM target shift forward (m), e.g. toes


STYLES = {
    "correct": SquatStyle(),
    "knees_cave": SquatStyle(valgus=1.0),
    "heels_lift": SquatStyle(heel_lift_deg=24.0, com_shift=0.07, lean_bottom_deg=30.0),
    "rounded_back": SquatStyle(spine_round_deg=28.0, lean_bottom_deg=44.0),
}


class Squat:
    """One repetition: descend, pause, ascend, stand."""

    def __init__(self, body: Body | None = None, style: SquatStyle | str = "correct",
                 down=2.0, pause=0.35, up=1.4, hold=0.5):
        self.b = body or Body()
        self.st = STYLES[style] if isinstance(style, str) else style
        self.down, self.pause, self.up, self.hold = down, pause, up, hold
        self.rest = rest_joints(self.b)

    @property
    def period(self):
        return self.down + self.pause + self.up + self.hold

    def phase(self, t):
        """Depth progress 0 (standing) .. 1 (bottom) and a +1/-1 direction flag."""
        t = t % self.period
        if t < self.down:
            return smooth(t / self.down), -1
        t -= self.down
        if t < self.pause:
            return 1.0, 0
        t -= self.pause
        if t < self.up:
            return 1 - smooth(t / self.up), +1
        return 0.0, 0

    # -- building blocks --------------------------------------------------
    def _feet(self, p):
        b, st = self.b, self.st
        out = {}
        for side, sx in (("L", 1), ("R", -1)):
            yaw = rot_z(sx * math.radians(b.toe_out_deg))
            pitch = rot_x(math.radians(st.heel_lift_deg) * p)
            R = yaw @ pitch
            ball_rest = self.rest[f"ball_{side}"]
            ball_local = np.array([0, -b.ball, -b.ankle_h])
            A = ball_rest - R @ ball_local
            f = yaw @ np.array([0, -1.0, 0])
            out[side] = (R, A, f, yaw)
        return out

    def _solve(self, p, thigh_deg, py):
        """Pose for a given depth progress, thigh angle and pelvis y."""
        b, st = self.b, self.st
        lean = math.radians(st.lean_stand_deg + (st.lean_bottom_deg - st.lean_stand_deg) * p)
        rnd = math.radians(st.spine_round_deg) * p
        R_pel = rot_x(lean - 0.5 * rnd)
        R_abd = rot_x(lean + 0.35 * rnd)
        R_chest = rot_x(lean + rnd)
        R_head = rot_x(lean * 0.75 + rnd * 0.3)

        feet = self._feet(p)
        # hip height from the requested thigh angle (thigh length is fixed);
        # knee comes from IK, so iterate hip height a few times.
        pz = self.rest["pelvis"][2]
        th = math.radians(thigh_deg)
        for _ in range(3):
            P = np.array([0.0, py, pz])
            hips = {s: P + R_pel @ (self.rest[f"hip_{s}"] - self.rest["pelvis"]) for s in "LR"}
            ks = {}
            for s, sx in (("L", 1), ("R", -1)):
                Rf, A, f, yaw = feet[s]
                pole = f + np.array([-sx * 0.25 * st.valgus * p ** 0.8, 0, 0])
                ks[s] = two_bone_ik(hips[s], A, b.thigh, b.shin, pole / np.linalg.norm(pole))
            # adjust pelvis height to reach the requested thigh angle (left leg)
            K = ks["L"]
            want_hip_z = K[2] + b.thigh * math.sin(th)
            pz += (want_hip_z - hips["L"][2]) * 0.9
            # keep legs reachable
            for s in "LR":
                A = feet[s][1]
                pz = min(pz, A[2] + 0.999 * (b.thigh + b.shin) + b.pelvis_up * math.cos(lean) - 0.002)

        P = np.array([0.0, py, pz])
        pose = Pose()
        J = pose.joints
        J["pelvis"] = P
        J["waist"] = P + R_abd @ [0, 0, b.abdomen]
        J["neck"] = J["waist"] + R_chest @ [0, 0, b.chest]
        J["head_joint"] = J["neck"] + R_head @ [0, 0, b.neck]
        J["head"] = J["head_joint"] + R_head @ [0, 0, b.head_c]
        seg = pose.seg
        seg["pelvis"] = (R_pel, P)
        seg["abdomen"] = (R_abd, P)
        seg["chest"] = (R_chest, J["waist"])
        seg["head"] = (R_head, J["head_joint"])

        arm_raise = math.radians(12 + 78 * smooth(min(1.0, p * 1.25))) if st.arms_forward else math.radians(12)
        for s, sx in (("L", 1), ("R", -1)):
            Rf, A, f, yaw = feet[s]
            H = P + R_pel @ (self.rest[f"hip_{s}"] - self.rest["pelvis"])
            pole = f + np.array([-sx * 0.25 * st.valgus * p ** 0.8, 0, 0])
            K = two_bone_ik(H, A, b.thigh, b.shin, pole / np.linalg.norm(pole))
            lat = np.cross([0, 0, 1.0], f)
            lat = lat if sx > 0 else -lat  # keep local +X pointing world +X for both legs
            J[f"hip_{s}"], J[f"knee_{s}"], J[f"ankle_{s}"] = H, K, A
            seg[f"thigh_{s}"] = (frame_from(K - H, lat), H)
            seg[f"shin_{s}"] = (frame_from(A - K, lat), K)
            seg[f"foot_{s}"] = (Rf, A)
            for n in ("heel", "ball", "toe"):
                J[f"{n}_{s}"] = A + Rf @ (self.rest[f"{n}_{s}"] - self.rest[f"ankle_{s}"])
            # arms: straight, raised forward in world space for counter-balance
            S = J["waist"] + R_chest @ (self.rest[f"shoulder_{s}"] - self.rest["waist"])
            d = np.array([sx * 0.07, -math.sin(arm_raise), -math.cos(arm_raise)])
            d /= np.linalg.norm(d)
            E = S + d * b.upper_arm
            W = E + d * b.forearm
            Hd = W + d * b.hand * 0.6
            J[f"shoulder_{s}"], J[f"elbow_{s}"], J[f"wrist_{s}"], J[f"hand_{s}"] = S, E, W, Hd
            Rarm = frame_from(d, [1, 0, 0])
            seg[f"upper_arm_{s}"] = (Rarm, S)
            seg[f"forearm_{s}"] = (Rarm, E)
            seg[f"hand_{s}"] = (Rarm, W)
        return pose

    def com(self, pose):
        J = pose.joints
        tot = 0.0
        acc = np.zeros(3)

        def add(name, a, bb):
            nonlocal tot, acc
            m, c = MASS[name]
            acc += m * (a + (bb - a) * c)
            tot += m

        add("pelvis", J["pelvis"] - (J["waist"] - J["pelvis"]) * 0.3, J["pelvis"])
        add("abdomen", J["pelvis"], J["waist"])
        add("chest", J["waist"], J["neck"])
        add("head", J["neck"], J["head"])
        for s in "LR":
            add("upper_arm", J[f"shoulder_{s}"], J[f"elbow_{s}"])
            add("forearm", J[f"elbow_{s}"], J[f"wrist_{s}"])
            add("hand", J[f"wrist_{s}"], J[f"hand_{s}"])
            add("thigh", J[f"hip_{s}"], J[f"knee_{s}"])
            add("shin", J[f"knee_{s}"], J[f"ankle_{s}"])
            add("foot", J[f"heel_{s}"], J[f"toe_{s}"])
        return acc / tot

    def pose(self, t):
        p, direction = self.phase(t)
        st = self.st
        thigh_stand = 86.0
        thigh = thigh_stand + (st.thigh_bottom_deg - thigh_stand) * p
        # target: COM over the mid-foot (between heel and ball), optionally shifted
        mid = np.mean([(self.rest[f"heel_{s}"] + self.rest[f"ball_{s}"]) / 2 for s in "LR"], axis=0)
        target_y = mid[1] - st.com_shift * p
        lo, hi = -0.25, 0.45
        for _ in range(28):
            m = (lo + hi) / 2
            c = self.com(self._solve(p, thigh, m))
            if c[1] > target_y:
                hi = m
            else:
                lo = m
        pose = self._solve(p, thigh, (lo + hi) / 2)
        add_anchors(pose, self.rest)
        J = pose.joints
        pose.info = {
            "depth": p, "direction": direction,
            "com": self.com(pose),
            "midfoot": mid,
            "knee_angle_L": _angle(J["hip_L"], J["knee_L"], J["ankle_L"]),
            "hip_angle_L": _angle(J["neck"], J["hip_L"], J["knee_L"]),
            "thigh_deg": math.degrees(math.atan2(J["hip_L"][2] - J["knee_L"][2],
                                                 np.linalg.norm((J["hip_L"] - J["knee_L"])[:2]))),
            "trunk_lean_deg": math.degrees(math.atan2(-(J["neck"][1] - J["pelvis"][1]),
                                                      J["neck"][2] - J["pelvis"][2])),
            "shin_lean_deg": math.degrees(math.atan2(-(J["knee_L"][1] - J["ankle_L"][1]),
                                                     J["knee_L"][2] - J["ankle_L"][2])),
        }
        return pose


# muscle / landmark anchors: (segment, rest-space point builder)
def _anchor_defs(rest):
    d = {"core": ("abdomen", rest["waist"] + np.array([0, -0.12, -0.04]))}
    for s, sx in (("L", 1), ("R", -1)):
        H, K = rest[f"hip_{s}"], rest[f"knee_{s}"]
        d[f"quads_{s}"] = (f"thigh_{s}", H + (K - H) * 0.45 + np.array([0, -0.065, 0]))
        d[f"adductor_{s}"] = (f"thigh_{s}", H + (K - H) * 0.3 + np.array([-sx * 0.055, 0, 0]))
        d[f"glute_{s}"] = ("pelvis", H + np.array([sx * 0.015, 0.095, -0.03]))
        d[f"hamstring_{s}"] = (f"thigh_{s}", H + (K - H) * 0.5 + np.array([0, 0.07, 0]))
    return d


def add_anchors(pose, rest):
    for name, (seg, pt) in _anchor_defs(rest).items():
        R, origin = pose.seg[seg]
        prox = rest[SEGMENTS[seg][0]]
        pose.joints[name] = np.asarray(origin) + R @ (pt - prox)


def _angle(a, b, c):
    u, v = a - b, c - b
    return math.degrees(math.acos(np.clip(np.dot(u, v) / np.linalg.norm(u) / np.linalg.norm(v), -1, 1)))


MOTIONS = {"squat": Squat}


if __name__ == "__main__":
    for name in STYLES:
        sq = Squat(style=name)
        for t in (0.0, 1.0, 2.1):
            ps = sq.pose(t)
            i = ps.info
            print(f"{name:13s} t={t:.1f} depth={i['depth']:.2f} knee={i['knee_angle_L']:.0f} "
                  f"hip={i['hip_angle_L']:.0f} thigh={i['thigh_deg']:.0f} trunk={i['trunk_lean_deg']:.0f} "
                  f"shin={i['shin_lean_deg']:.0f} com_y={i['com'][1]:.3f} mid_y={i['midfoot'][1]:.3f} "
                  f"knee_x={ps.joints['knee_L'][0]:.3f} heel_z={ps.joints['heel_L'][2]:.3f}")
