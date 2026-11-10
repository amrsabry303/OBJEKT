"""Procedural cow-hide print for the HOLY COW wrap (back + spine + front), 398 x 250 mm at 4 px/mm.
Hair is drawn as thousands of fine strands along a flow field, so the patch edges are fuzzy like real hide.
Colours stay inside the objekt palette: Chocolate / Oxblood browns and Bone."""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]
PX = 4; WF, H = 398, 250; Wp, Hp = WF*PX, H*PX
rng = np.random.default_rng(11)
def field(scale_px, seed):
    r = np.random.default_rng(seed); gw, gh = max(2,int(Wp/scale_px)+2), max(2,int(Hp/scale_px)+2)
    g = (r.random((gh,gw))*255).astype(np.uint8)
    im = Image.fromarray(g).resize((Wp,Hp), Image.BICUBIC)
    a = np.asarray(im).astype(np.float32)/255
    return (a-a.mean())/(a.std()+1e-6)
s = .55*field(520,1) + .32*field(210,2) + .20*field(80,3) + .10*field(30,4)
# keep the title, spine and back-logo zones brown so the lettering reads (Bone on dark)
def bump(cx, cy, rx, ry, k):
    yy, xx = np.mgrid[0:Hp,0:Wp].astype(np.float32); d = ((xx-cx*PX)/(rx*PX))**2 + ((yy-cy*PX)/(ry*PX))**2
    return k*np.exp(-d**2*.9)
s = s + bump(300,70,95,80,3.4) + bump(199,125,34,150,3.4) + bump(90,205,48,30,3.4) + bump(330,200,40,40,-1.2)
thr = np.quantile(s, .52)
soft = 1/(1+np.exp(-(s-thr)/.13))             # 0 white .. 1 brown
# flow field for the hair
flow = 1.15 + 1.6*(field(260,5)*.35)
base_brown = np.array([66,28,24],np.float32); base_white = np.array([228,219,205],np.float32)
img = (soft[...,None]*base_brown + (1-soft[...,None])*base_white)
im = Image.fromarray(np.clip(img,0,255).astype(np.uint8)); d = ImageDraw.Draw(im)
N = 330000
xs = rng.random(N)*Wp; ys = rng.random(N)*Hp; Ls = rng.uniform(7,20,N); jit = rng.normal(0,.35,N)
for i in range(N):
    x, y = xs[i], ys[i]; xi, yi = int(x)%Wp, int(y)%Hp
    th = flow[yi,xi] + jit[i]; L = Ls[i]
    dx, dy = np.cos(th)*L, np.sin(th)*L
    # membership sampled a little along the strand so brown and white hairs cross the patch edge
    sx_, sy_ = int(min(max(x+dx*rng.uniform(-1,1),0),Wp-1)), int(min(max(y+dy*rng.uniform(-1,1),0),Hp-1))
    p = soft[sy_, sx_]
    if rng.random() < p:
        t = rng.random(); c = (np.array([58,24,20])*(1-t) + np.array([112,54,42])*t) * rng.uniform(.8,1.15)
    else:
        t = rng.random(); c = (np.array([238,229,214])*(1-t) + np.array([226,206,192])*t) * rng.uniform(.93,1.02)
    d.line([(x,y),(x+dx,y+dy)], fill=tuple(int(max(0,min(255,v))) for v in c), width=1)
im = im.filter(ImageFilter.GaussianBlur(.5))
a = np.asarray(im).astype(np.float32)
shade = 1 + .05*field(150,9)[...,None]; a = a*shade + rng.normal(0,2.2,a.shape)
Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save(out)
print('ok', Wp, Hp)
