"""Cinematic grade + vertical crop for the split reel (ffmpeg filter graph builder)."""
import imageio_ffmpeg, subprocess, os
FF = imageio_ffmpeg.get_ffmpeg_exe()

def grade_chain(strength=1.0):
    s = strength
    return ",".join([
        "eq=contrast=%.3f:saturation=%.3f:gamma=0.97" % (1 + 0.09 * s, 1 + 0.05 * s),
        "curves=all='0/0 0.14/0.09 0.5/0.525 0.86/0.93 1/1'",
        # teal shadows / warm highlights (split-toning)
        "colorbalance=rs=%.3f:gs=%.3f:bs=%.3f:rm=%.3f:gm=0:bm=%.3f:rh=%.3f:gh=%.3f:bh=%.3f" % (-0.07 * s, -0.01 * s, 0.10 * s, 0.02 * s, 0.03 * s, 0.10 * s, 0.03 * s, -0.10 * s),
    ])

def build_vf(crop, size, strength=1.0, grain=0, bloom=0.22, vignette="PI/4.4"):
    """crop = (w,h,x,y) in source pixels; size = (W,H) output."""
    cw, ch, cx, cy = crop
    W, H = size
    pre = f"crop={cw}:{ch}:{cx}:{cy},scale={W}:{H}:flags=lanczos,{grade_chain(strength)}"
    bl = f"split[a][b];[b]gblur=sigma=22,eq=brightness=-0.12:contrast=1.5[bl];[a][bl]blend=all_mode=screen:all_opacity={bloom}"
    post = f"vignette=angle={vignette}," + (f"noise=alls={grain}:allf=t," if grain else "") + "format=yuv420p"
    return f"{pre},{bl},{post}"

def run(args):
    r = subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y"] + args, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-800:])
