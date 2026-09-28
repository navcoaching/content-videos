# python3 scripts/jsheet.py name f1 f2 ... -> stills/j/sheet_name.jpg (4 cols)
import sys
from PIL import Image, ImageDraw
name, fr = sys.argv[1], [int(x) for x in sys.argv[2:]]
ims=[Image.open(f"stills/j/f{f:04d}.jpg").resize((270,480)) for f in fr]
cols=4; rows=(len(ims)+cols-1)//cols
s=Image.new('RGB',(270*cols,480*rows),'black')
for i,(im,f) in enumerate(zip(ims,fr)):
    d=ImageDraw.Draw(im); d.rectangle([0,0,80,14],fill='black'); d.text((3,2),f"{f} {f/60:.1f}s",fill='yellow'); s.paste(im,((i%cols)*270,(i//cols)*480))
s.save(f'stills/j/sheet_{name}.jpg'); print('ok')
