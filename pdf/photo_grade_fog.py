import numpy as np, cv2
rng=np.random.default_rng(11)
im=cv2.imread('scratchpad/hood2.png')[287:1813,0:858]
im=cv2.fastNlMeansDenoisingColored(im,None,3,3,7,21)
im=cv2.resize(im,None,fx=2,fy=2,interpolation=cv2.INTER_LANCZOS4)
H,W=im.shape[:2]
# ---- natural grade: luminance-only local contrast, mild saturation, gentle sharpen
lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB); L,a,b=cv2.split(lab)
L=cv2.createCLAHE(clipLimit=1.3,tileGridSize=(6,6)).apply(L)
im=cv2.cvtColor(cv2.merge([L,a,b]),cv2.COLOR_LAB2BGR).astype(np.float32)/255
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); hsv[...,1]=np.clip(hsv[...,1]*1.06,0,1)
im=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
im=np.clip(im+0.4*(im-cv2.GaussianBlur(im,(0,0),1.8)),0,1)
# ---- procedural smoke over the lower body
def noise(sx,sy,oct=5):
    acc=np.zeros((H,W),np.float32); amp=1; tot=0
    for o in range(oct):
        gh,gw=max(2,int(H/sy/2**-o)),max(2,int(W/sx/2**-o))
        n=rng.random((gh,gw)).astype(np.float32)
        acc+=amp*cv2.resize(n,(W,H),interpolation=cv2.INTER_CUBIC); tot+=amp; amp*=0.52
    return acc/tot
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
n1=noise(420,160); n2=noise(260,120,4)
smoke=np.clip((0.6*n1+0.4*n2-0.30)*2.4,0,1)
smoke=cv2.GaussianBlur(smoke,(0,0),6)
# density: the edge follows the hips (higher at the knees, lower under the "Coach" print)
edge=1372+ (xx-480)*0.14
v=np.clip((yy-edge+ (smoke-0.5)*80)/85,0,1); v=v*v*(3-2*v)
core=np.exp(-(((xx-960)/620)**2+((yy-1820)/430)**2))
alpha=np.clip(v*(0.9+0.2*smoke)*np.clip(0.7+core,0,1),0,0.97)
# fade the fog out over the floor so it looks like it rises from the platform
floor=np.clip((yy-2250)/450,0,1); alpha*=1-0.55*floor
# wisps drifting up a little above the edge
wisp=np.clip((smoke-0.62)*3,0,1)*np.clip(1-(edge-yy)/140,0,1)*(yy<edge)*0.45
alpha=np.maximum(alpha,wisp)
alpha=cv2.GaussianBlur(alpha,(0,0),3)
# smoke colour: lit by the red neon from above, cool cyan kick from the right, soft white core
red=np.array([60,70,235],np.float32)/255; cyan=np.array([235,215,120],np.float32)/255; white=np.array([225,228,232],np.float32)/255
wr=np.clip(1-(yy-1420)/650,0,1)[...,None]*0.5
wc=np.clip((xx-900)/800,0,1)[...,None]*0.35
col=white*(1-wr-wc)+red*wr+cyan*wc
col=col*(0.62+0.45*smoke[...,None])          # volume variation
out=im*(1-alpha[...,None])+col*alpha[...,None]
# a little bloom so it feels like light in haze
glow=cv2.GaussianBlur(out,(0,0),18)
out=np.clip(out+0.12*glow*alpha[...,None],0,1)
# film grain to tie layers together
out=np.clip(out+rng.normal(0,0.012,out.shape).astype(np.float32),0,1)
o8=(out*255).astype(np.uint8)
cv2.imwrite('/home/user/content-videos/pdf/coach-split-squat.jpg',o8,[cv2.IMWRITE_JPEG_QUALITY,93])
cv2.imwrite('scratchpad/final_small.jpg',cv2.resize(o8,None,fx=0.45,fy=0.45))
