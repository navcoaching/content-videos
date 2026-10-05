"""Wrap a vertical clip with the Nav Coaching intro + outro.
usage: python3 scripts/wrap.py input.mp4 output.mp4
- scales the clip to 1080x1920 (no crop for 9:16 sources),
- converts it to a smooth 30 fps with motion interpolation (scene-cut aware, so cuts stay clean),
- 0.5 s soft dissolve intro -> clip, 0.5 s dip to black clip -> outro,
- keeps the clip's own audio if it has one, otherwise silence; intro/outro sounds fade in/out."""
import re, subprocess, sys, os
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTRO = os.path.join(ROOT, "render/intro/nav-intro-with-sound.mp4")
OUTRO = os.path.join(ROOT, "render/outro/nav-outro-with-sound.mp4")
X1, X2 = 0.5, 0.5  # transition lengths (s)


def probe(p):
    r = subprocess.run([FF, "-hide_banner", "-i", p], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r)
    dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    return dur, "Audio:" in r


src, out = sys.argv[1], sys.argv[2]
tmp = out + ".clip30.mp4"
# 1) smooth 30 fps master of the clip
subprocess.run([FF, "-y", "-loglevel", "error", "-i", src, "-vf",
                "scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,"
                "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=fdiff:scd_threshold=8",
                "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-an", tmp], check=True)
di, _ = probe(INTRO)
dc, has_audio = probe(tmp)[0], probe(src)[1]
o1 = di - X1
o2 = o1 + dc - X2
clip_audio = "[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];" if has_audio else ""
inputs = ["-i", INTRO, "-i", tmp if not has_audio else tmp, "-i", OUTRO]
if has_audio:
    inputs = ["-i", INTRO, "-i", tmp, "-i", OUTRO, "-i", src]
    clip_audio = f"[3:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{dc},asetpts=PTS-STARTPTS[a1];"
else:
    inputs += ["-f", "lavfi", "-t", f"{dc}", "-i", "anullsrc=r=48000:cl=stereo"]
    clip_audio = "[3:a]aresample=48000[a1];"
fc = (
    "[0:v]setpts=PTS-STARTPTS,fps=30,format=yuv420p,setsar=1[v0];"
    "[1:v]setpts=PTS-STARTPTS,fps=30,format=yuv420p,setsar=1[v1];"
    "[2:v]setpts=PTS-STARTPTS,fps=30,format=yuv420p,setsar=1[v2];"
    f"[v0][v1]xfade=transition=fade:duration={X1}:offset={o1:.3f}[v01];"
    f"[v01][v2]xfade=transition=fadeblack:duration={X2}:offset={o2:.3f},format=yuv420p[v];"
    "[0:a]aresample=48000[a0];" + clip_audio + "[2:a]aresample=48000[a2];"
    f"[a0][a1]acrossfade=d={X1}:c1=tri:c2=tri[a01];[a01][a2]acrossfade=d={X2}:c1=tri:c2=tri[a]"
)
subprocess.run([FF, "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-r", "30",
                "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
os.remove(tmp)
print(out, f"{o2 + 7.5:.2f}s")
