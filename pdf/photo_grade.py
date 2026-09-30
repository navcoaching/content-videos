import numpy as np, cv2
im=cv2.imread('scratchpad/hood5.png')[287:1813,0:858]
im=cv2.fastNlMeansDenoisingColored(im,None,3,3,7,21)
im=cv2.resize(im,None,fx=2,fy=2,interpolation=cv2.INTER_LANCZOS4)
lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB); L,a,b=cv2.split(lab)
L=cv2.createCLAHE(clipLimit=1.4,tileGridSize=(6,6)).apply(L)
im=cv2.cvtColor(cv2.merge([L,a,b]),cv2.COLOR_LAB2BGR).astype(np.float32)/255
# gentle S-curve + slightly cooler shadows, mild saturation
im=np.clip((im-0.5)*1.06+0.5+0.01,0,1)
lum=(0.114*im[...,0]+0.587*im[...,1]+0.299*im[...,2])[...,None]
im[...,0:1]+=0.025*np.clip(1-lum*2.5,0,1)
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); hsv[...,1]=np.clip(hsv[...,1]*1.08,0,1)
im=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
im=np.clip(im+0.45*(im-cv2.GaussianBlur(im,(0,0),1.8)),0,1)
im=np.clip(im+np.random.default_rng(2).normal(0,0.008,im.shape).astype(np.float32),0,1)
out=(im*255).astype(np.uint8)
cv2.imwrite('/home/user/content-videos/pdf/coach-split-squat.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,93])
cv2.imwrite('scratchpad/final_small.jpg',cv2.resize(out,None,fx=0.45,fy=0.45))
cv2.imwrite('scratchpad/final_head.jpg',out[650:1350,700:1500])
