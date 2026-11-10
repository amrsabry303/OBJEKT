import sys, numpy as np
from PIL import Image, ImageFilter
src, mask, out, target = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
lo, hi = float(sys.argv[5]), float(sys.argv[6])     # hue band to move (degrees, wraps)
im=Image.open(src).convert('RGB'); W,H=im.size
mk=Image.open(mask).convert('L').resize((W,H)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(3))
hsv=np.asarray(im.convert('HSV')).astype(float); m=np.asarray(mk).astype(float)/255
h=hsv[...,0]*360/255; s=hsv[...,1]/255
sel=(((h>=lo)|(h<=hi)) if lo>hi else ((h>=lo)&(h<=hi)))&(s>0.08)
w=m*sel
hsv[...,0]=np.where(w>0,target/360*255,hsv[...,0]); hsv[...,1]*=(1-w*0.18); hsv[...,2]*=(1-w*0.06)
res=Image.composite(Image.fromarray(hsv.clip(0,255).astype('uint8'),'HSV').convert('RGB'),im,mk); res.save(out)
a=np.asarray(res).astype(float); print('sample',a[int(H*.45):int(H*.6), int(W*.42):int(W*.5)].reshape(-1,3).mean(0).round(0))
