import numpy as np, cv2
img=cv2.imread('images/5.jpg').astype(np.float32)
H,W=img.shape[:2]; yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
rng=np.random.default_rng(9)
top,yc,ybot=470.,522.,578.
cxy=np.where(yy<yc,372.,372.+(yy-yc)*0.05)
u=np.clip((yy-top)/(yc-top),0,1)
w_top=60*np.power(np.sin(u*np.pi/2),0.62)          # rounder crown, no point
dy=np.clip(yy-yc,0,None)
wl=60+dy*0.05-2*np.sin(np.clip(dy/70,0,1)*np.pi)   # left side tucks in toward the neck
wr=60+dy*0.14
half=np.where(xx<cxy,np.where(yy<yc,w_top,wl),np.where(yy<yc,w_top,wr))
nx=(xx-cxy)/np.maximum(half,1)
inside=(np.abs(nx)<=1)&(yy>=top)&(yy<=ybot)
mask=cv2.GaussianBlur(inside.astype(np.float32),(0,0),1.5)
fade=np.clip((ybot-yy)/40,0,1); fade=fade*fade*(3-2*fade)   # long, soft blend into the collar
mask*=np.where(yy>ybot-40,fade,1)
# ---- tone from the real hood fold / hoodie
fold=np.median(img[560:600,320:420].reshape(-1,3),0)
base=fold*0.80
ny=np.clip((yy-top)/(ybot-top),0,1)
cyl=np.clip(1-0.62*np.abs(nx)**2.0,0.3,1)                 # round volume
side=1+0.10*np.clip(-nx,0,1)-0.12*np.clip(nx,0,1)          # light from left
crown=np.exp(-(((xx-360)/50)**2+((yy-482)/30)**2))*0.07    # soft top highlight
col=base*(cyl*side*(0.92+0.10*ny)+crown)[...,None]
# centre seam: subtle recessed line + highlight next to it
sx=cxy+2
seam=np.exp(-((xx-sx)/1.4)**2)*np.clip((yy-top-6)/12,0,1)*np.clip((560-yy)/20,0,1)
hl=np.exp(-((xx-sx+3.5)/2.4)**2)*np.clip((yy-top-6)/12,0,1)*np.clip((555-yy)/25,0,1)
col=col*(1-0.20*seam[...,None])+hl[...,None]*base*0.08
# drape folds toward the neck
for x0,ang,st,w in [(335,0.5,0.12,5),(410,-0.45,0.12,5)]:
    dd=xx-(x0+(yy-545)*ang)
    cr=np.exp(-(dd/w)**2)*np.clip((yy-530)/20,0,1)*np.clip((572-yy)/20,0,1)
    col*=(1-st*cr[...,None])
# red neon rim along the left silhouette
rim=np.exp(-((nx+0.96)/0.06)**2)*np.clip((560-yy)/40,0,1)
col[...,2]+=rim*55; col[...,1]+=rim*5; col[...,0]+=rim*7
# fine knit texture (procedural, very low amplitude) + camera grain
n=cv2.GaussianBlur(rng.normal(0,1,(H,W)).astype(np.float32),(0,0),0.9)*4.5
col+=n[...,None]+rng.normal(0,2.0,col.shape).astype(np.float32)
col=cv2.GaussianBlur(col,(0,0),0.55)
out=np.clip(img*(1-mask[...,None])+col*mask[...,None],0,255).astype(np.uint8)
cv2.imwrite('scratchpad/hoodB.png',out)
o=cv2.imread('images/5.jpg'); p=o
z=lambda a:cv2.resize(a[420:760,220:620],None,fx=1.6,fy=1.6,interpolation=cv2.INTER_CUBIC)
cv2.imwrite('scratchpad/hcmpB.png',np.hstack([z(o),z(p),z(out)]))
