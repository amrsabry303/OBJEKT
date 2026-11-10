import numpy as np, json, sys
from PIL import Image, ImageFilter, ImageDraw
base = Image.open('couch_ai.png').convert('RGB'); BW, BH = base.size
B = np.asarray(base).astype(np.float32)/255
meta = {m['n']: m for m in json.load(open('r3d/meta.json'))}
D = 45.0
def coeffs(dst, src):
    A=[];Bv=[]
    for (x,y),(u,v) in zip(dst,src):
        A.append([x,y,1,0,0,0,-u*x,-u*y]); Bv.append(u)
        A.append([0,0,0,x,y,1,-v*x,-v*y]); Bv.append(v)
    return np.linalg.solve(np.array(A,float),np.array(Bv,float))
def warp(art, quad, mode=Image.BICUBIC):
    w,h = art.size
    return art.transform((BW,BH), Image.PERSPECTIVE, coeffs(quad,[(0,0),(w,0),(w,h),(0,h)]), mode)
def dist(a,b): return float(np.hypot(a[0]-b[0],a[1]-b[1]))
def tex(n): return Image.open(f'r3d/tex/tex_{n:02d}.png').convert('RGB')
def spine_art(n, quad):
    m = meta[n]; Wm, Hm = int(m['Wmm']), int(m['H']*10)
    t = tex(n); s = t.crop((Wm*5,0,(Wm+int(D))*5,Hm*5)).rotate(-90, expand=True)   # reads left to right, foot at left
    h_px = (dist(quad[0],quad[3])+dist(quad[1],quad[2]))/2; l_px = (dist(quad[0],quad[1])+dist(quad[3],quad[2]))/2
    need_mm = l_px/(h_px/D); have = Hm
    if need_mm > have:     # extend the head end with the plain cover colour
        c = s.getpixel((s.width-3, s.height//2)); ext = Image.new('RGB',(int((need_mm-have)*5),s.height),c)
        out = Image.new('RGB',(s.width+ext.width,s.height)); out.paste(s,(0,0)); out.paste(ext,(s.width,0)); s = out
    else:                  # cut the head end
        s = s.crop((0,0,int(need_mm*5),s.height))
    return s
def cover_art(n):
    m = meta[n]; Wm, Hm = int(m['Wmm']), int(m['H']*10)
    return tex(n).crop(((Wm+int(D))*5,0,(2*Wm+int(D))*5,Hm*5))
def lum(a): return 0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]
Lb = lum(B)
def median_img(L, size):
    im = Image.fromarray((np.clip(L,0,1)*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(size))
    return np.asarray(im).astype(np.float32)/255
# cloth grain taken from the photo's own cover (a clean patch), as a ratio so it works on any colour
patch = Lb[650:780, 800:1000]; pb = np.asarray(Image.fromarray((patch*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32)/255
grain = np.clip(patch/np.maximum(pb,1e-3), .8, 1.25)
def tile_grain():
    g = np.concatenate([grain, grain[:, ::-1]], 1); g = np.concatenate([g, g[::-1]], 0)
    return np.tile(g, (BH//g.shape[0]+1, BW//g.shape[1]+1))[:BH,:BW]
G = tile_grain()
# photo noise level on a clean leather patch
lp = Lb[1300:1400, 250:450]; lpb = np.asarray(Image.fromarray((lp*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32)/255
NOISE = float((lp-lpb).std())
rng = np.random.default_rng(3)
Bf = B.copy()
def poly_mask(q):
    im = Image.new('L',(BW,BH),0); ImageDraw.Draw(im).polygon([tuple(p) for p in q], fill=255); return np.asarray(im).astype(np.float32)/255
def composite(art, quad, vis_extra=None, text_sign=0, feather=0.8, tag=''):
    A = warp(art, quad); al = np.asarray(warp(Image.new('L',art.size,255), quad, Image.BILINEAR)).astype(np.float32)/255
    al = np.minimum(al, poly_mask(quad))
    vis = np.ones((BH,BW),np.float32) if vis_extra is None else vis_extra
    m = al*vis
    region = m > .5
    L = Lb.copy()
    Lm = median_img(L, 15)
    diff = L - Lm
    if text_sign >= 0: L = np.where(diff > .06, Lm, L)      # remove bright lettering
    if text_sign <= 0: L = np.where(diff < -.06, Lm, L)     # remove dark lettering
    L = np.asarray(Image.fromarray((np.clip(L,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32)/255
    mean = L[region].mean(); shade = np.clip(L/mean, .35, 1.7)[...,None]
    Aarr = np.asarray(A).astype(np.float32)/255
    out = Aarr*shade*G[...,None]**1.0
    mm = np.asarray(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(feather))).astype(np.float32)/255
    mm = np.minimum(mm, np.asarray(Image.fromarray((np.maximum(al,0)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(feather+.6))).astype(np.float32)/255 + 0)
    global Bf
    Bf = Bf*(1-mm[...,None]) + out*mm[...,None]
    return mm
# --- surfaces ---
q_cover = [(395,661),(730,550),(1069,802),(710,945)]
q_mid   = [(364,839),(880,1018),(880,1084),(365,905)]
q_bot   = [(365,905),(880,1084),(873,1152),(369,975)]
# visibility for the middle spine: not where the oxblood cover or white page block sit
R_,G_,B_ = B[...,0],B[...,1],B[...,2]
occl = (((R_-G_)>.12)&(R_<.7)) | (np.minimum(np.minimum(R_,G_),B_) > .90)
occl = np.asarray(Image.fromarray((occl*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))).astype(np.float32)/255
vis_mid = 1-occl
composite(spine_art(3,q_bot), q_bot, None, text_sign=1)           # bottom: Heavy Reading, Carbon, cream lettering
composite(spine_art(1,q_mid), q_mid, vis_mid, text_sign=-1)       # middle: Not a Book, Bone, green lettering
composite(cover_art(5), q_cover, None, text_sign=1)               # top: Objekts of Character front
# soften and add the photo's own noise level over the books
bf = Image.fromarray((np.clip(Bf,0,1)*255).astype(np.uint8))
region = poly_mask(q_cover)+poly_mask(q_mid)+poly_mask(q_bot); region = np.clip(region,0,1)
rg = np.asarray(Image.fromarray((region*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32)/255
soft = np.asarray(bf.filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)/255
Bf = Bf*(1-rg[...,None]*.6) + soft*(rg[...,None]*.6)
Bf = Bf + (rng.normal(0,NOISE*.8,(BH,BW,1))*rg[...,None]).astype(np.float32)
Image.fromarray((np.clip(Bf,0,1)*255).astype(np.uint8)).save('couch_overlay.png')
print('noise',NOISE)
