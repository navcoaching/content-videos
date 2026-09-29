"""Blur private text (rects named 'blur*' in the manifest) inside captured state screenshots. Idempotent."""
import json, sys
from PIL import Image, ImageFilter
M = "public/tut/manifest.json"
m = json.load(open(M))
dpr = m["device"]["dpr"]
done = set(m.get("blurred", []))
for sid, st in m["states"].items():
    rects = [r for k, r in st["rects"].items() if k.startswith("blur") and r]
    if not rects or sid in done:
        continue
    path = "public/" + st["src"]
    im = Image.open(path)
    for r in rects:
        pad = 6
        box = (max(0, int((r["x"] - pad) * dpr)), max(0, int((r["y"] - st["scroll"] - pad) * dpr)),
               min(im.width, int((r["x"] + r["w"] + pad) * dpr)), min(im.height, int((r["y"] - st["scroll"] + r["h"] + pad) * dpr)))
        region = im.crop(box).filter(ImageFilter.GaussianBlur(18))
        im.paste(region, box)
    im.save(path, quality=90)
    done.add(sid)
    print("blurred", sid, len(rects))
# full-page captures: blur 'blur*' rects inside the tiles they fall in
for pid, pg in m["pages"].items():
    key = "page:" + pid
    rects = [r for k, r in pg["rects"].items() if k.startswith("blur") and r]
    if not rects or key in done:
        continue
    for t in pg["tiles"]:
        path = "public/" + t["src"]
        im = Image.open(path)
        hit = False
        for r in rects:
            if r["y"] + r["h"] < t["y"] or r["y"] > t["y"] + t["h"]:
                continue
            pad = 6
            box = (max(0, int((r["x"] - pad) * dpr)), max(0, int((r["y"] - t["y"] - pad) * dpr)),
                   min(im.width, int((r["x"] + r["w"] + pad) * dpr)), min(im.height, int((r["y"] - t["y"] + r["h"] + pad) * dpr)))
            im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(18)), box)
            hit = True
        if hit:
            im.save(path, quality=90)
    done.add(key)
    print("blurred page", pid, len(rects))
m["blurred"] = sorted(done)
json.dump(m, open(M, "w"), ensure_ascii=False, indent=1)
