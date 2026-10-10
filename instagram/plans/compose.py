"""Compose video slides: paper bg + graded clips in rects + foreground (alpha from mask)."""
import json, glob, os, subprocess, sys
from PIL import Image, ImageOps
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
G = ("curves=all='0/0.03 0.25/0.20 0.55/0.55 0.85/0.88 1/0.96',"
     "colorbalance=rs=-0.06:gs=0.01:bs=0.07:rm=0.02:bm=-0.01:rh=0.07:gh=0.02:bh=-0.06,eq=contrast=1.08:saturation=0.88,vignette=angle=PI/6")

def crop_for(spec, w, h, src='1920:1080'):
    SW, SH = map(int, src.split(':'))
    cw, ch, cx, cy = map(int, spec.split(':'))
    xc, yc = cx + cw / 2, cy + ch / 2
    H0 = min(ch, SH) if src != '1920:1080' else SH
    W = round(H0 * w / h)
    if W <= SW:
        H = H0
    else:
        W, H = SW, round(SW * h / w)
    x = min(max(0, round(xc - W / 2)), SW - W)
    y = min(max(0, round(yc - H / 2)), SH - H)
    return f'{W - W % 2}:{H - H % 2}:{x}:{y}'

for k in sys.argv[1:]:
    for rj in sorted(glob.glob(f'{HERE}/{k}/out/*-rects.json')):
        n = os.path.basename(rj).split('-')[0]
        base = f'{HERE}/{k}/out/{n}'
        fg = Image.open(base + '.png').convert('RGBA')
        fg.putalpha(ImageOps.invert(Image.open(base + '-mask.png').convert('L')))
        fg.save(base + '-fg.png')
        rects = json.load(open(rj))
        args = [FF, '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=0xf3f6fa:s=1080x1350:r=30:d=6']
        for r in rects:
            args += ['-stream_loop', '2', '-ss', str(r['ss']), '-i', f"{HERE}/clips/{r['clip']}"]
        args += ['-loop', '1', '-i', base + '-fg.png']
        fc, last = [], '[0:v]'
        for i, r in enumerate(rects, 1):
            if r['w'] / r['h'] > 2:   # wide tile: sharp centre + blurred fill
                cw = round(r['h'] * 1.5) // 2 * 2
                fc.append(f"[{i}:v]fps=30,split[a{i}][b{i}]")
                fc.append(f"[a{i}]crop={crop_for(r['crop'], r['w'], r['h'], r.get('src', '1920:1080'))},scale={r['w']}:{r['h']},boxblur=20:2,eq=brightness=-0.08[bg{i}]")
                fc.append(f"[b{i}]crop={crop_for(r['crop'], cw, r['h'], r.get('src', '1920:1080'))},scale={cw}:{r['h']}[fgv{i}]")
                fc.append(f"[bg{i}][fgv{i}]overlay=(W-w)/2:0,setsar=1,{G}[v{i}]")
            else:
                fc.append(f"[{i}:v]fps=30,crop={crop_for(r['crop'], r['w'], r['h'], r.get('src', '1920:1080'))},scale={r['w']}:{r['h']},setsar=1,{G}[v{i}]")
            fc.append(f"{last}[v{i}]overlay={r['x']}:{r['y']}[t{i}]"); last = f'[t{i}]'
        fc.append(f"{last}[{len(rects) + 1}:v]overlay=0:0,format=yuv420p[out]")
        args += ['-filter_complex', ';'.join(fc), '-map', '[out]', '-t', '6', '-r', '30', '-c:v', 'libx264', '-crf', '19',
                 '-preset', 'medium', '-movflags', '+faststart', base + '.mp4']
        subprocess.run(args, check=True)
        for f in (base + '-fg.png', base + '-mask.png', rj):
            os.remove(f)
        os.remove(base + '.png')
        print('video', k, n)
