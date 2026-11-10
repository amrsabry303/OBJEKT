import sys, numpy as np
from PIL import Image, ImageFilter
src=Image.open(sys.argv[1]).convert('RGB'); out=sys.argv[2]
a=np.asarray(src).astype(float)/255; h,w,_=a.shape
a=0.02+a*0.96; a=a-0.05*(a**3)+0.015*np.sin(np.pi*a)
yy,xx=np.mgrid[0:h,0:w]; r=np.sqrt(((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2)
a*=(1-0.08*np.clip(r-0.4,0,1)**1.6)[...,None]
img=Image.fromarray((np.clip(a,0,1)*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.4))
a=np.asarray(img).astype(float)/255
g=np.random.default_rng(3).normal(0,1,(h,w)); gi=Image.fromarray(((g*20)+128).clip(0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.7))
g=(np.asarray(gi).astype(float)-128)/20
a=a+(g*0.024*(1-0.5*np.abs(a.mean(2)-0.5)*2))[...,None]
Image.fromarray((np.clip(a,0,1)*255).astype('uint8')).save(out,quality=93)
