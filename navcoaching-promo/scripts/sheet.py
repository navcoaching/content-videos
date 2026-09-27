# Contact sheet of rendered stills with frame labels: python3 scripts/sheet.py out.jpg f1 f2 ...
import sys
from PIL import Image, ImageDraw
out, frames = sys.argv[1], [int(x) for x in sys.argv[2:]]
ims = [Image.open(f"stills/f{f:04d}.jpg") for f in frames]
w, h = ims[0].size
cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
tw, th = w // 2 * 1, h // 2 * 1
sheet = Image.new("RGB", (cols * tw, rows * th), "black")
for i, (im, f) in enumerate(zip(ims, frames)):
    t = im.resize((tw, th))
    d = ImageDraw.Draw(t); d.rectangle([0, 0, 120, 26], fill="black"); d.text((6, 6), f"f{f} {f/60:.2f}s", fill="yellow")
    sheet.paste(t, ((i % cols) * tw, (i // cols) * th))
sheet.save(out, quality=88)
print(out, sheet.size)
