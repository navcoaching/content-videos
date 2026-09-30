"""Cut, crop (vertical / card / wide), cinematic-grade and grain every shot in src/split/split.json.
Reads split/src/<clip>.mp4 (downloaded by fetch.py) -> writes public/split/clips/<shot id>.mp4
Usage: python3 split/process.py [shot_id ...]   (no args = all)"""
import json, os, re, subprocess, sys, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import grade

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "src", "split", "split.json")))
OUT = os.path.join(ROOT, "public", "split", "clips")
SRC = os.path.join(ROOT, "split", "src")
os.makedirs(OUT, exist_ok=True)
SIZES = {"full": (1080, 1920), "card": (1280, 960), "wide": (1440, 810)}
ASPECT = {"full": 9 / 16, "card": 4 / 3, "wide": 16 / 9}


def probe(path):
    r = subprocess.run([grade.FF, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    line = [l for l in r.splitlines() if "Video:" in l][0]
    w, h = map(int, re.search(r",\s(\d{3,5})x(\d{3,5})", line).groups())
    return w, h


def crop_for(shot, w, h):
    a = ASPECT[shot["layout"]]  # width / height of the crop
    z = shot["zoom"]
    # largest window of aspect a that fits the source, then zoom in
    cw = min(w, h * a)
    cw = cw / z
    ch = cw / a
    cw, ch = int(cw) // 2 * 2, int(ch) // 2 * 2
    x = int(shot["cx"] * w - cw / 2)
    y = int(shot["cy"] * h - ch / 2)
    x = max(0, min(w - cw, x))
    y = max(0, min(h - ch, y))
    return cw, ch, x, y


def process(shot):
    src = os.path.join(SRC, shot["clip"] + ".mp4")
    out = os.path.join(OUT, shot["id"] + ".mp4")
    w, h = probe(src)
    crop = crop_for(shot, w, h)
    size = SIZES[shot["layout"]]
    vf = grade.build_vf(crop, size, strength=shot.get("strength", 1.0))
    if shot.get("flip"):
        vf = "hflip," + vf
    dur = shot["dur"] / 60 + 0.35
    grade.run(["-ss", str(shot["ss"]), "-t", f"{dur:.3f}", "-i", src, "-an", "-vf", vf,
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-g", "12", "-movflags", "+faststart", out])
    return shot["id"], crop, os.path.getsize(out) // 1024


if __name__ == "__main__":
    want = set(sys.argv[1:])
    shots = [s for s in DATA["shots"] if not want or s["id"] in want]
    with cf.ThreadPoolExecutor(3) as ex:
        for sid, crop, kb in ex.map(process, shots):
            print(f"{sid:6s} crop={crop} {kb} KB")
