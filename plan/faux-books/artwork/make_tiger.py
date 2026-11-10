"""Realistic tiger-coat print for EASY TIGER (back + spine + front), 398 x 250 mm at 4 px/mm.
The stripe pattern (V line down the spine) comes from tiger_shapes() in make_flats.py. Each stripe is rasterised, its edge is
roughened, and the coat is then drawn as ~330,000 fine hair strands, so stripe edges are soft and fuzzy like real fur.
Colours: Clay ground with Clay tonal variation, Carbon-brown stripes. Usage: python3 make_tiger.py <repo root>"""
import sys, re, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter
root = sys.argv[1]
src = open(root + '/plan/faux-books/artwork/make_flats.py').read().split("files = [single(v) for v in VOLS]")[0]
sys.argv = ['x', root]; exec(src)                      # gives tiger_shapes, W, H, D, SYM_H ...
PX = 4; Wp, Hp = Wf*PX, H*PX
cxs = sx + D/2; lw = LOGO_W; lh = lw*501/786
excl = [(cxs-SYM_H/2-2, H-BOT-SYM_W-2, SYM_H+4, SYM_W+4, 4), ((W-lw)/2-6, H-BOT-lh-6, lw+12, lh+12, 6)]
paths = tiger_shapes(random.Random(9*11+1), Wf, H, cxs, H*.062, excl)
SS = 2; mask = Image.new('L', (Wp*SS, Hp*SS), 0); d = ImageDraw.Draw(mask)
for p in paths:
    pts = [(float(a)*PX*SS, float(b)*PX*SS) for a,b in re.findall(r'(-?\d+\.?\d*) (-?\d+\.?\d*)', p)]
    if len(pts) > 2: d.polygon(pts, fill=255)
mask = mask.resize((Wp,Hp), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.2))
m = np.asarray(mask).astype(np.float32)/255
rng = np.random.default_rng(23)
def field(scale_px, seed):
    r = np.random.default_rng(seed); gw, gh = max(2,int(Wp/scale_px)+2), max(2,int(Hp/scale_px)+2)
    g = (r.random((gh,gw))*255).astype(np.uint8); a = np.asarray(Image.fromarray(g).resize((Wp,Hp), Image.BICUBIC)).astype(np.float32)/255
    return (a-a.mean())/(a.std()+1e-6)
soft = 1/(1+np.exp(-((m - .5) + .10*field(14,3) + .06*field(6,4))/.11))       # 0 ground .. 1 stripe, fuzzy irregular edge
base_ground = np.array([156,76,50],np.float32); base_stripe = np.array([34,24,21],np.float32)
tone = 1 + .10*field(120,5)[...,None]                                           # slow tonal variation of the coat
img = (soft[...,None]*base_stripe + (1-soft[...,None])*base_ground*tone)
im = Image.fromarray(np.clip(img,0,255).astype(np.uint8)); dr = ImageDraw.Draw(im)
flow = 1.45 + .9*field(240,6)*.35                                              # hair mostly runs down the body
N = 330000; xs = rng.random(N)*Wp; ys = rng.random(N)*Hp; Ls = rng.uniform(6,16,N); jit = rng.normal(0,.3,N)
for i in range(N):
    x, y = xs[i], ys[i]; xi, yi = int(x)%Wp, int(y)%Hp; th = flow[yi,xi] + jit[i]; L = Ls[i]
    dx, dy = np.cos(th)*L, np.sin(th)*L
    sx_, sy_ = int(min(max(x+dx*rng.uniform(-1,1),0),Wp-1)), int(min(max(y+dy*rng.uniform(-1,1),0),Hp-1))
    p = soft[sy_, sx_]
    if rng.random() < p:
        t = rng.random(); c = (np.array([22,16,14])*(1-t) + np.array([70,44,34])*t) * rng.uniform(.8,1.2)
    else:
        t = rng.random(); c = (np.array([150,70,46])*(1-t) + np.array([196,112,78])*t) * rng.uniform(.82,1.15)
    dr.line([(x,y),(x+dx,y+dy)], fill=tuple(int(max(0,min(255,v))) for v in c), width=1)
im = im.filter(ImageFilter.GaussianBlur(.5))
a = np.asarray(im).astype(np.float32); a = a*(1+.05*field(150,9)[...,None]) + rng.normal(0,2.2,a.shape)
Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save(root + '/plan/faux-books/artwork/prints/tiger-hide_v1.png')
print('ok', Wp, Hp, len(paths))
