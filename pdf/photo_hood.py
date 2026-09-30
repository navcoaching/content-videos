import numpy as np, cv2
img=cv2.imread('images/4.jpg').astype(np.float32)
H,W=img.shape[:2]
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
top,yc,ybot=697.,768.,860.
# centre line drifts slightly right going down (hood falls toward the fold)
cxy=np.where(yy<yc,572.,572.+(yy-yc)*0.22)
# half width: rounded, slightly peaked dome above yc, gentle flare below
u=np.clip((yy-top)/(yc-top),0,1)
w_top=78*np.power(np.sin(u*np.pi/2),0.8)
w_bot=78+np.clip(yy-yc,0,None)*0.28
half=np.where(yy<yc,w_top,w_bot)
nx=(xx-cxy)/np.maximum(half,1)
inside=(np.abs(nx)<=1)&(yy>=top)&(yy<=ybot)
mask=inside.astype(np.float32)
# feather: soft sides, long fade into the real hoodie fold at the bottom
mask=cv2.GaussianBlur(mask,(0,0),1.8)
fade=np.clip((ybot-8-yy)/34,0,1); fade=fade*fade*(3-2*fade)
mask*=np.where(yy>ybot-42,fade,1)
# ---------- colour (BGR) from the real hood fold at the neck
fold=np.median(img[800:850,540:640].reshape(-1,3),0)
base=fold*np.clip(0.80+0.20*(yy-top)/(ybot-top),0.8,1.0)[...,None]
cyl=np.clip(1-0.55*np.abs(nx)**2.2,0.35,1)            # round volume
topl=np.exp(-(((xx-548)/55)**2+((yy-728)/42)**2))       # soft overhead highlight
col=base*cyl[...,None]*(1+0.16*topl[...,None])
# fabric folds: two soft diagonal creases near the bottom
for x0,ang,st in [(535,0.55,0.18),(612,-0.45,0.15)]:
    d=(xx-(x0+(yy-800)*ang))
    crease=np.exp(-(d/5)**2)*np.clip((yy-782)/40,0,1)*np.clip((850-yy)/30,0,1)
    col*=(1-st*crease[...,None])
# centre seam (soft) following the dome
sx=cxy+1.5
seam=np.exp(-((xx-sx)/1.6)**2)*np.clip((yy-top-4)/10,0,1)*np.clip((835-yy)/20,0,1)
col*=(1-0.22*seam[...,None])
col+=np.exp(-((xx-sx+3.5)/2)**2)[...,None]*seam.max()*0*0
# faint red neon rim on the left edge
rim=np.exp(-((nx+0.97)/0.07)**2)*(yy<840)
col[...,2]+=rim*45; col[...,1]+=rim*4
# grain like the photo
rng=np.random.default_rng(7); col+=rng.normal(0,3.5,col.shape).astype(np.float32)
col=cv2.GaussianBlur(col,(0,0),0.8)
out=np.clip(img*(1-mask[...,None])+col*mask[...,None],0,255).astype(np.uint8)
cv2.imwrite('scratchpad/hood2.png',out)
cv2.imwrite('scratchpad/hood2_zoom.png',cv2.resize(out[600:1150,350:800],None,fx=1.2,fy=1.2))
