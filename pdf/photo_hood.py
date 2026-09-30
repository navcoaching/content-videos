import numpy as np, cv2
img=cv2.imread('images/4.jpg').astype(np.float32)
H,W=img.shape[:2]; yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
rng=np.random.default_rng(9)
top,yc,ybot=694.,772.,868.
cxy=np.where(yy<yc,574.,574.+(yy-yc)*0.25)
u=np.clip((yy-top)/(yc-top),0,1)
w_top=82*np.power(np.sin(u*np.pi/2),0.5)          # rounder crown, no point
dy=np.clip(yy-yc,0,None)
wl=82-dy*0.10-4*np.sin(np.clip(dy/70,0,1)*np.pi)   # left side tucks in toward the neck
wr=82+dy*0.32
half=np.where(xx<cxy,np.where(yy<yc,w_top,wl),np.where(yy<yc,w_top,wr))
nx=(xx-cxy)/np.maximum(half,1)
inside=(np.abs(nx)<=1)&(yy>=top)&(yy<=ybot)
mask=cv2.GaussianBlur(inside.astype(np.float32),(0,0),1.5)
fade=np.clip((ybot-yy)/60,0,1); fade=fade*fade*(3-2*fade)   # long, soft blend into the collar
mask*=np.where(yy>ybot-60,fade,1)
# ---- tone from the real hood fold / hoodie
fold=np.median(img[805:850,545:635].reshape(-1,3),0)
base=fold*0.86
ny=np.clip((yy-top)/(ybot-top),0,1)
cyl=np.clip(1-0.62*np.abs(nx)**2.0,0.3,1)                 # round volume
side=1+0.10*np.clip(-nx,0,1)-0.12*np.clip(nx,0,1)          # light from left
crown=np.exp(-(((xx-560)/60)**2+((yy-722)/40)**2))*0.14    # soft top highlight
col=base*(cyl*side*(0.92+0.10*ny)+crown)[...,None]
# centre seam: subtle recessed line + highlight next to it
sx=cxy+2
seam=np.exp(-((xx-sx)/1.4)**2)*np.clip((yy-top-6)/12,0,1)*np.clip((840-yy)/25,0,1)
hl=np.exp(-((xx-sx+3.5)/2.4)**2)*np.clip((yy-top-6)/12,0,1)*np.clip((835-yy)/30,0,1)
col=col*(1-0.20*seam[...,None])+hl[...,None]*base*0.08
# drape folds toward the neck
for x0,ang,st,w in [(532,0.55,0.16,6),(618,-0.45,0.14,7)]:
    dd=xx-(x0+(yy-805)*ang)
    cr=np.exp(-(dd/w)**2)*np.clip((yy-790)/30,0,1)*np.clip((862-yy)/30,0,1)
    col*=(1-st*cr[...,None])
# red neon rim along the left silhouette
rim=np.exp(-((nx+0.96)/0.06)**2)*np.clip((850-yy)/60,0,1)
col[...,2]+=rim*55; col[...,1]+=rim*5; col[...,0]+=rim*7
# fine knit texture (procedural, very low amplitude) + camera grain
n=cv2.GaussianBlur(rng.normal(0,1,(H,W)).astype(np.float32),(0,0),0.9)*4.5
col+=n[...,None]+rng.normal(0,2.0,col.shape).astype(np.float32)
col=cv2.GaussianBlur(col,(0,0),0.55)
out=np.clip(img*(1-mask[...,None])+col*mask[...,None],0,255).astype(np.uint8)
cv2.imwrite('scratchpad/hood5.png',out)
o=cv2.imread('images/4.jpg'); p=cv2.imread('scratchpad/hood2.png')
z=lambda a:cv2.resize(a[640:1000,420:760],None,fx=1.6,fy=1.6,interpolation=cv2.INTER_CUBIC)
cv2.imwrite('scratchpad/hcmp5.png',np.hstack([z(o),z(p),z(out)]))
