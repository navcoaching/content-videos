"""NavFit command line.

  python -m navfit render squat [--aspect 9:16|16:9|both] [--quality draft|final] [--lang ar|en]
                                [--preview 1.5,8,20]
  python -m navfit check  squat              # claims that still need a coach's review
  python -m navfit ref    <youtube-url> --exercise squat
  python -m navfit blur-video in.mp4 out.mp4 # face blur for real footage (path A)
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

from .compose import ROOT, Project, compose, plan, render_frames


def ffmpeg_bin():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found: install ffmpeg or `pip install imageio-ffmpeg`")


def cmd_check(args):
    pr = Project(args.exercise)
    keys = set()
    for sc in pr.board["scenes"]:
        if sc.get("vo"):
            keys.add(sc["vo"])
        for ov in sc.get("overlays", []):
            for k in ("text", "sub", "title"):
                if isinstance(ov.get(k), str):
                    keys.add(ov[k])
            for k in ov.get("items", []):
                keys.add(k)
    missing = [k for k in keys if k not in pr.content]
    rows = pr.review(sorted(keys))
    print(f"{len(keys)} claims used in the storyboard, {len(rows)} need review, {len(missing)} missing")
    for k, st, ar, note in rows:
        print(f"  [{st}] {k}: {ar}\n      -> {note}")
    for k in missing:
        print(f"  [missing] {k}")
    return rows


def write_reports(pr, out_dir, info, aspect):
    fps = pr.fps
    with open(os.path.join(out_dir, "VOICEOVER.md"), "w", encoding="utf-8") as fh:
        fh.write(f"# Voice-over — {pr.cfg['title'].get(pr.lang)} ({aspect}, {info['total']:.1f}s)\n\n")
        fh.write("| from | to | scene | line |\n|---|---|---|---|\n")
        for a, b, sid, line in info["vo"]:
            fh.write(f"| {a:5.1f}s | {b:5.1f}s | {sid} | {line} |\n")
    rows = pr.review()
    with open(os.path.join(out_dir, "REVIEW.md"), "w", encoding="utf-8") as fh:
        fh.write("# Coach review checklist\n\n")
        if not rows:
            fh.write("All on-screen claims are marked verified.\n")
        for k, st, ar, note in rows:
            fh.write(f"- [ ] **{k}** ({st}): {ar}\n  - {note}\n")
        fh.write(f"\nPrivacy: face mask applied on {'every' if info['privacy_ok'] else 'NOT every'} frame "
                 f"({info['frames']} frames).\n")


def cmd_render(args):
    pr = Project(args.exercise, aspect=None, quality=args.quality, lang=args.lang)
    aspects = [args.aspect or pr.aspect]
    if aspects[0] == "both":
        aspects = ["9:16", "16:9"]
    ff = ffmpeg_bin()
    preview = [float(x) for x in args.preview.split(",")] if args.preview else None
    planned, base, k = plan(pr)
    print(f"[plan] {len(planned)} scenes, base {base:.1f}s, hold scale x{k:.2f}")
    for asp in aspects:
        tag = asp.replace(":", "x")
        out_dir = os.path.join(ROOT, "output", pr.name, f"{tag}_{pr.lang}" + ("_draft" if pr.quality == "draft" else ""))
        if preview:
            out_dir = os.path.join(out_dir, "preview")
        cache = os.path.join(ROOT, "output", "cache")
        t0 = time.time()
        render_frames(pr, planned, asp, cache)
        print(f"[render] done in {time.time() - t0:.0f}s")
        info = compose(pr, planned, asp, out_dir, preview=preview, ffmpeg=ff)
        if preview:
            print(f"[preview] stills in {out_dir}")
            continue
        base_name = f"{pr.name}_{tag}_{pr.lang}"
        vid = info["video"]
        final_sfx = os.path.join(out_dir, base_name + "_sfx.mp4")
        final_clean = os.path.join(out_dir, base_name + "_clean.mp4")
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", vid, "-i", os.path.join(out_dir, "sfx.wav"), "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", final_sfx], check=True)
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", vid, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", final_clean], check=True)
        write_reports(pr, out_dir, info, asp)
        rows = pr.review()
        print(f"[done] {final_sfx}\n       {final_clean}\n       {info['total']:.1f}s, privacy mask on every frame: "
              f"{info['privacy_ok']}, claims needing review: {len(rows)} (see REVIEW.md)")


def cmd_ref(args):
    from .reference import ingest
    ingest(args.url, args.exercise)


def cmd_blur(args):
    from .privacy_video import blur_video
    blur_video(args.input, args.output, debug=args.debug)


def main():
    ap = argparse.ArgumentParser(prog="navfit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("exercise")
    r.add_argument("--aspect", choices=["9:16", "16:9", "both"])
    r.add_argument("--quality", choices=["draft", "final"])
    r.add_argument("--lang", choices=["ar", "en"])
    r.add_argument("--preview", help="comma-separated seconds: write stills only")
    r.set_defaults(fn=cmd_render)
    c = sub.add_parser("check")
    c.add_argument("exercise")
    c.set_defaults(fn=cmd_check)
    f = sub.add_parser("ref")
    f.add_argument("url")
    f.add_argument("--exercise", required=True)
    f.set_defaults(fn=cmd_ref)
    b = sub.add_parser("blur-video")
    b.add_argument("input")
    b.add_argument("output")
    b.add_argument("--debug", action="store_true")
    b.set_defaults(fn=cmd_blur)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
