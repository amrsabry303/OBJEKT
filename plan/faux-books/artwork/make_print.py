"""objekt faux books: print files. One flat per volume (back + spine + front) at one of three sizes, with 3 mm bleed and crop marks.
Usage: python3 make_print.py <repo root> <S|M|L>
Sizes (width x height x spine): S 14 x 20 x 2.0 cm, M 18 x 25 x 2.8 cm, L 23 x 30 x 3.5 cm (Sabry, 10 Nov).
Lettering is a stand-in (Inter) for Galak Round, which is not licensed. Do not commit font files.
No wrap/turn-in allowance is included: the maker's template is not known. RGB hex values, to be converted to CMYK/Pantone by the printer."""
import re, sys, random, math
from PIL import ImageFont
root = sys.argv[1]; SIZE = sys.argv[2]; out = root + '/plan/faux-books/print'
logo_d = re.search(r' d="([^"]+)"', open(root + '/brand/objekt-logo.svg').read()).group(1)
sym_d = re.search(r' d="([^"]+)"', open(root + '/brand/objekt-symbol.svg').read()).group(1)
C = {'Bone':'#E9E4D8','Putty':'#B9B2A5','Carbon':'#222222','Ink':'#1E2A44','Oxblood':'#5A1F25','Clay':'#A8553A','Chocolate':'#4A2A1B','Objekt Green':'#37613F'}
MF = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf', 100)
CAP = .727
import numpy as np
from PIL import Image as _Im, ImageDraw as _ID
_F200 = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf', 200); _INK = {}
def ink(txt):
    """left side-bearing and inked width per unit of font size, measured from real pixels (optical alignment)"""
    if txt not in _INK:
        im = _Im.new('L', (4200,400), 0); _ID.Draw(im).text((100,80), txt, font=_F200, fill=255)
        cols = np.where((np.asarray(im) > 60).any(0))[0]; _INK[txt] = ((cols[0]-100)/200, (cols[-1]-cols[0]+1)/200)
    return _INK[txt]
def iwid(txt): return ink(txt)[1] + (len(txt)-1)*TRK
def tw(txt, size, track=0.0): return sum(MF.getlength(c) for c in txt)/100*size + len(txt)*size*track
FT = 'font-family="Galak Round, Inter Display, Inter, Helvetica, Arial, sans-serif"'
SIZES = {'S':(140,200,20), 'M':(180,250,28), 'L':(230,300,35)}
W, H, D = SIZES[SIZE]; B = 3      # trim size in mm, spine width, bleed
Wf = 2*W + D; sx = W; fx = W + D
BOT = 14; SYM_W = .55*D; SYM_H = SYM_W*223/308; GAP = 8; LOGO_W = 40      # logo and symbol sit a fixed 14 mm from the foot on every size
TRK = -.012                       # tight tracking on the big type

# n, title lines, cover, lettering, front layout, spine lines, print
VOLS = [
 (1,['NOT A','BOOK'],'Bone','Objekt Green','crop',['NOT A','BOOK'],None),
 (2,['SHELF','LIFE'],'Putty','Chocolate','vert',['SHELF','LIFE'],None),
 (3,['HEAVY','READING'],'Carbon','Bone','fill',['HEAVY','READING'],None),
 (4,['JUDGE','THE','COVER'],'Ink','Putty','fill',['JUDGE THE','COVER'],None),
 (5,['OBJEKTS OF','CHARACTER'],'Oxblood','Bone','fill',['OBJEKTS OF','CHARACTER'],None),
 (6,['USELESS','ON PURPOSE'],'Clay','Bone','vert',['USELESS','ON PURPOSE'],None),
 (7,['COFFEE','TABLE','BOOK'],'Chocolate','Putty','fill',['COFFEE TABLE','BOOK'],None),
 (8,['DESIGN','WORTH','NOTICING'],'Objekt Green','Bone','crop',['DESIGN WORTH','NOTICING'],None),
 (9,['EASY','TIGER'],'Clay','Bone','fill',['EASY','TIGER'],'tiger'),
 (10,['HOLY','COW'],'Bone','Bone','fill',['HOLY','COW'],'cow'),
 (11,['BETWEEN','THE','LINES'],'Bone','Carbon','bands',['BETWEEN','THE LINES'],'stripe'),
]
import os
NUMS = {int(x) for x in os.environ.get('SPINE_NUMS','1,2,3,4,5,6,7,8,9,10,11').split(',') if x}   # volumes that carry the spine number (proposal)
def slug(lines): return '-'.join(lines).lower().replace(' ','-')
# spine type: two lines must fit the spine with a 12% margin each side, and the longest title must clear the number at the head by 12 mm
SP = min(.76*D/(CAP*2.32), (H-2*BOT-SYM_W-GAP-12)/(max(tw(l,1,.05) for v in VOLS for l in v[5]) + tw('00',1,.18)))

def smooth_noise(r, n, k=5):
    v = [r.uniform(-1,1) for _ in range(n+2*k+2)]
    o = [sum(v[i:i+2*k+1])/(2*k+1) for i in range(n+1)]; m = max(1e-6, max(abs(x) for x in o)); return [x/m for x in o]
def tiger_shapes(r, Wf_, H_, ax, p, excl):
    def blocked(x, y):
        for (rx, ry, rw, rh, pad) in excl:
            if rx-pad <= x <= rx+rw+pad and ry-pad <= y <= ry+rh+pad: return True
        return False
    def arm(y0, sign, tan, lmax, wob):
        pts = []; u = 0.0; a1,f1,p1,a2,f2,p2 = wob
        while u <= lmax:
            x = ax + sign*u
            if x < -4 or x > Wf_+4: break
            y = y0 - tan*u*(1 - .16*u/max(lmax,1)) + a1*math.sin(u/f1+p1) + a2*math.sin(u/f2+p2)
            if y < -12 or y > H_+12: break
            if u > 3 and blocked(x, y): break
            pts.append((x, y)); u += 2.0
        return pts
    def outline(cl, ws, nz):
        L = len(cl); left = []; right = []
        for i,(x,y) in enumerate(cl):
            a = cl[max(i-1,0)]; b = cl[min(i+1,L-1)]; dx, dy = b[0]-a[0], b[1]-a[1]; d = math.hypot(dx,dy) or 1
            nx, ny = -dy/d, dx/d; wl = ws[i]/2*(1+.30*nz[(i*2)%len(nz)]); wr = ws[i]/2*(1+.30*nz[(i*2+1)%len(nz)])
            left.append((x+nx*wl, y+ny*wl)); right.append((x-nx*wr, y-ny*wr))
        return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x,y in left + right[::-1]) + 'Z'
    out = []; y0 = -.18*H_
    while y0 < 1.3*H_:
        wmax = p*r.uniform(.3,.6); tl, tr = [math.tan(math.radians(r.uniform(17,33))) for _ in (0,1)]
        wob = lambda: (r.uniform(1,3.2), r.uniform(10,18), r.uniform(0,6.28), r.uniform(.4,1.3), r.uniform(3,6), r.uniform(0,6.28))
        La = arm(y0,-1,tl,Wf_*r.uniform(.45,1.1),wob()); Ra = arm(y0,1,tr,Wf_*r.uniform(.45,1.1),wob())
        if len(La)+len(Ra) > 14:
            cl = La[::-1]+Ra[1:]; na, nb = len(La), len(Ra); ws = []
            for i in range(len(cl)):
                u = (na-1-i)/max(na-1,1) if i < na else (i-na+1)/max(nb-1,1)
                ws.append(wmax*max(0.0, 1-min(u,1.0)**1.4)**.85)
            out.append(outline(cl, ws, smooth_noise(r, len(cl)*2+2, 2)))
        y0 += p*r.uniform(.75,1.3)
    for _ in range(int(Wf_*H_/(p*p)*.09)):
        cx = r.uniform(0,Wf_); cy = r.uniform(0,H_)
        if blocked(cx,cy): continue
        sg = 1 if cx > ax else -1; ang = math.radians(r.uniform(14,34)); Ld = r.uniform(.8,2.8)*p
        cl = []; u = 0; a1,f1,p1 = r.uniform(.5,1.8), r.uniform(8,14), r.uniform(0,6.28)
        while u <= Ld:
            x = cx + sg*u*math.cos(ang); y = cy - u*math.sin(ang) + a1*math.sin(u/f1+p1)
            if blocked(x,y): break
            cl.append((x,y)); u += 1.6
        if len(cl) > 6:
            wm = p*r.uniform(.12,.28); ws = [wm*max(0.0, math.sin(math.pi*i/(len(cl)-1)))**.8 for i in range(len(cl))]
            out.append(outline(cl, ws, smooth_noise(r, len(cl)*2+2, 2)))
    return out

def text(x, y, s, txt, fill, rot=0, w=500, extra=''):
    tr = f' transform="translate({x:.2f} {y:.2f}) rotate({rot})"' if rot else f' x="{x:.2f}" y="{y:.2f}"'
    return f'<text{tr} {FT} font-size="{s:.2f}" font-weight="{w}" letter-spacing="{s*TRK if "big" in extra else s*.05:.2f}" fill="{fill}">{txt}</text>'

def front_layout(kind, lines, ink_, n=0):
    """returns (list of (x, y, size, rot, txt)) in flat coordinates"""
    m = 11*W/180; avail = W - 2*m; items = []
    if n != 10:
        if kind in ('fill','over'):
            over = 1.0 if kind == 'fill' else 1.14
            s = over*avail/max(iwid(l) for l in lines); cap = s*CAP; step = cap*1.14
            for j,l in enumerate(lines): items.append((fx+m-ink(l)[0]*s, m+cap+j*step, s, 0, l))
        elif kind == 'vert':
            s = (H-2*m)/max(iwid(l) for l in lines); cap = s*CAP; step = cap*1.14
            for j,l in enumerate(lines): items.append((fx+m+cap+j*step, H-m+ink(l)[0]*s, s, -90, l))
        elif kind == 'crop':
            small, big = lines[:-1], lines[-1]
            sb = (W-m)/(iwid(big) - 0.2*ink(big[-1])[1]); capb = sb*CAP; ss = 0.34*sb; caps = ss*CAP; stp = caps*1.3   # the trim cuts the last letter at about 80%
            for j,l in enumerate(small): items.append((fx+m-ink(l)[0]*ss, m+caps+j*stp, ss, 0, l))
            items.append((fx+m-ink(big)[0]*sb, H + 0.08*capb, sb, 0, big))   # only the foot of the word is cut by the bottom trim
        elif kind == 'bands':
            hb = H/12; s = avail/max(iwid(l) for l in lines); cap = s*CAP
            for j,l in enumerate(lines): items.append((fx+m-ink(l)[0]*s, (2*j+1)*hb + cap/2, s, 0, l))
        return items
    if kind in ('fill','over'):
        over = 1.0 if kind == 'fill' else 1.14
        s = over*avail/max(tw(l,1,TRK) for l in lines); cap = s*CAP; step = cap*1.14
        for j,l in enumerate(lines): items.append((fx+m, m+cap+j*step, s, 0, l))
    elif kind == 'vert':
        length = H - 2*m; s = length/max(tw(l,1,TRK) for l in lines); cap = s*CAP; step = cap*1.14
        for j,l in enumerate(lines): items.append((fx+m+cap+j*step, H-m, s, -90, l))
    elif kind == 'crop':
        small, big = lines[:-1], lines[-1]
        sb = 1.22*avail/tw(big,1,TRK); capb = sb*CAP
        ss = 0.34*sb; caps = ss*CAP; stp = caps*1.3
        for j,l in enumerate(small): items.append((fx+m, m+caps+j*stp, ss, 0, l))
        items.append((fx+m, H - .02*capb + 0.28*capb, sb, 0, big))        # baseline pushed below the trim: letters are cropped
    return items

def build(vol):
    n, lines, cover, inkc, kind, slines, prt = vol
    bg, fg = C[cover], C[inkc]; o = []
    o.append(f'<clipPath id="flat{n}"><rect x="{-B}" y="{-B}" width="{Wf+2*B}" height="{H+2*B}"/></clipPath><g clip-path="url(#flat{n})">')
    o.append(f'<rect x="{-B}" y="{-B}" width="{Wf+2*B}" height="{H+2*B}" fill="{bg}"/>')
    items = front_layout(kind, lines, inkc, n)
    lw = LOGO_W; lh = lw*501/786; logo_x = (W-lw)/2; logo_y = H - BOT - lh
    cxs = sx + D/2; k = SYM_W/308; ty = H - BOT; ys = ty - SYM_W - GAP
    scap = SP*CAP; sstep = scap*1.32; bh = scap + sstep; x1 = cxs - bh/2 + scap
    def lettering(fill, clip=None, front=True):
        g = []
        for (x,y,s,rot,l) in (items if front else []): g.append(text(x,y,s,l,fill,rot,extra='big'))
        g.append(f'<path transform="translate({logo_x:.1f} {logo_y:.1f}) scale({lw/786:.5f})" fill="{fill}" fill-rule="evenodd" d="{logo_d}"/>')
        g.append(f'<path transform="translate({cxs-SYM_H/2:.2f} {ty:.1f}) rotate(-90) scale({k:.5f}) translate(-238 0)" fill="{fill}" fill-rule="evenodd" d="{sym_d}"/>')
        for j,l in enumerate(slines): g.append(text(x1+j*sstep, ys + (ink(l)[0]*SP if n != 10 else 0), SP, l, fill, -90))
        if n in NUMS:
            # volume number at the head of the spine: same type size, tracked wide, 14 mm from the head, same baseline as a one-line title
            nx = cxs + SP*CAP/2
            g.append(f'<text transform="translate({nx:.2f} {BOT:.2f}) rotate(-90)" {FT} font-size="{SP:.2f}" font-weight="500" letter-spacing="{SP*.18:.2f}" text-anchor="end" fill="{fill}">{n:02d}</text>')
        s_ = '\n'.join(g)
        return f'<g clip-path="url(#{clip})">{s_}</g>' if clip else s_
    if prt == 'tiger':
        # realistic coat drawn by make_tiger.py (hair strands, fuzzy stripe edges); the pattern comes from tiger_shapes() above
        o.append(f'<image href="../../textures/tiger-hide_{SIZE}.jpg" x="{-B}" y="{-B}" width="{Wf+2*B}" height="{H+2*B}" preserveAspectRatio="none"/>')
        o.append(lettering(fg))
    elif prt == 'cow':
        o.append(f'<image href="../../textures/cow-hide_{SIZE}.jpg" x="{-B}" y="{-B}" width="{Wf+2*B}" height="{H+2*B}" preserveAspectRatio="none"/>')
        o.append(lettering(fg))
    elif prt == 'stripe':
        # twelve thin bands (Carbon, Bone, ...) across back, spine and front. Eleven equal bands run to y = 225 and a taller one
        # finishes the foot, so the band edge falls between the back logo's symbol and its wordmark.
        bh = (H-25)/11; edges = [i*bh for i in range(12)] + [H]; edges[0] = -B; edges[-1] = H + B   # last band 25 mm so the edge falls between the back logo's symbol and wordmark
        dark = ''.join(f'<rect x="{-B}" y="{edges[i]:.2f}" width="{Wf+2*B}" height="{edges[i+1]-edges[i]+.02:.2f}"/>' for i in range(12) if i % 2 == 0)
        light = ''.join(f'<rect x="{-B}" y="{edges[i]:.2f}" width="{Wf+2*B}" height="{edges[i+1]-edges[i]+.02:.2f}"/>' for i in range(12) if i % 2 == 1)
        o.append(f'<defs><clipPath id="sd{n}">{dark}</clipPath><clipPath id="sl{n}">{light}</clipPath></defs>')
        o.append(f'<rect x="{-B}" y="{-B}" width="{Wf+2*B}" height="{H+2*B}" fill="{C["Bone"]}"/>')
        o.append(f'<g clip-path="url(#sd{n})"><rect x="{-B}" y="{-B}" width="{Wf+2*B}" height="{H+2*B}" fill="{C["Carbon"]}"/></g>')
        # title: one line per band, light on dark and dark on light, letter-spaced out to the full width
        m = 11*W/180; avail = W - 2*m; cap = .86*bh; s_ = cap/CAP
        extra = (avail - iwid('BETWEEN')*s_)/(len('BETWEEN')-1)
        ls = s_*TRK + extra
        for j,l in enumerate(lines):
            col = C['Bone'] if j % 2 == 0 else C['Carbon']
            o.append(f'<text x="{fx+m-ink(l)[0]*s_:.2f}" y="{j*bh + (bh+cap)/2:.2f}" {FT} font-size="{s_:.2f}" font-weight="500" letter-spacing="{ls:.2f}" fill="{col}">{l}</text>')
        # back logo and spine (symbol and title): Bone where they cross a dark band, Carbon where they cross a light one
        o.append(lettering(C['Bone'], f'sd{n}', front=False)); o.append(lettering(C['Carbon'], f'sl{n}', front=False))
    else:
        o.append(lettering(fg))
    o.append('</g>')
    return '\n'.join(o)

import os, time
from PIL import ImageFilter
PX = 12                                # raster print art: 12 px/mm = 305 dpi
PXL = 4                                # low-res working grid, px/mm
TEXDIR = out + '/textures'; os.makedirs(TEXDIR, exist_ok=True)
def field_ref(scale_px, seed, Wl, Hl):
    """smooth noise whose grid is fixed to the Medium reference (1592 x 1000 px at 4 px/mm), so the look is the same on every size"""
    r = np.random.default_rng(seed); gw, gh = max(2,int(1592/scale_px)+2), max(2,int(1000/scale_px)+2)
    g = (r.random((gh,gw))*255).astype(np.uint8)
    a = np.asarray(Image.fromarray(g).resize((Wl,Hl), _Im.BICUBIC)).astype(np.float32)/255
    return (a-a.mean())/(a.std()+1e-6)
Image = _Im
def strands(img_low_rgb, soft, flow, kind, seed):
    """draw hair strands over the resized base; membership of each hair comes from the soft map"""
    Wl, Hl = soft.shape[1], soft.shape[0]; Wp, Hp = Wl*PX//PXL, Hl*PX//PXL; k = PX/PXL
    base = Image.fromarray(np.clip(img_low_rgb,0,255).astype(np.uint8)).resize((Wp,Hp), Image.BICUBIC)
    d = ImageDraw.Draw(base) if 'ImageDraw' in globals() else _ID.Draw(base)
    rng = np.random.default_rng(seed)
    N = int(3.32*(Wp*Hp)/(PX*PX)); xs = rng.random(N)*Wp; ys = rng.random(N)*Hp
    if kind == 'cow': Ls = rng.uniform(1.75,5.0,N)*PX; jit = rng.normal(0,.35,N)
    else: Ls = rng.uniform(1.5,4.0,N)*PX; jit = rng.normal(0,.3,N)
    for i in range(N):
        x, y = xs[i], ys[i]; xl, yl = min(int(x/k),Wl-1), min(int(y/k),Hl-1)
        th = flow[yl,xl] + jit[i]; L = Ls[i]; dx, dy = np.cos(th)*L, np.sin(th)*L
        sxl = int(min(max((x+dx*rng.uniform(-1,1))/k,0),Wl-1)); syl = int(min(max((y+dy*rng.uniform(-1,1))/k,0),Hl-1))
        p = soft[syl,sxl]
        if kind == 'cow':
            if rng.random() < p: t = rng.random(); c = (np.array([58,24,20])*(1-t) + np.array([112,54,42])*t) * rng.uniform(.8,1.15)
            else: t = rng.random(); c = (np.array([238,229,214])*(1-t) + np.array([226,206,192])*t) * rng.uniform(.93,1.02)
        else:
            if rng.random() < p: t = rng.random(); c = (np.array([22,16,14])*(1-t) + np.array([70,44,34])*t) * rng.uniform(.8,1.2)
            else: t = rng.random(); c = (np.array([150,70,46])*(1-t) + np.array([196,112,78])*t) * rng.uniform(.82,1.15)
        d.line([(x,y),(x+dx,y+dy)], fill=tuple(int(max(0,min(255,v))) for v in c), width=3)
    return base.filter(ImageFilter.GaussianBlur(1.4))
def gen_texture(kind):
    fn = f'{TEXDIR}/{kind}-hide_{SIZE}.jpg'
    if os.path.exists(fn): return fn
    t0 = time.time(); Wl, Hl = (Wf+2*B)*PXL, (H+2*B)*PXL
    if kind == 'cow':
        s_ = .55*field_ref(520,1,Wl,Hl) + .32*field_ref(210,2,Wl,Hl) + .20*field_ref(80,3,Wl,Hl) + .10*field_ref(30,4,Wl,Hl)
        yy, xx = np.mgrid[0:Hl,0:Wl].astype(np.float32); sx_, sy_ = Wf/398, H/250
        def bump(cx,cy,rx,ry,kk): return kk*np.exp(-(((xx-(cx*sx_+B)*PXL)/(rx*sx_*PXL))**2 + ((yy-(cy*sy_+B)*PXL)/(ry*sy_*PXL))**2)**2*.9)
        s_ = s_ + bump(300,70,95,80,3.4) + bump(199,125,34,150,3.4) + bump(90,205,48,30,3.4) + bump(330,200,40,40,-1.2)
        thr = np.quantile(s_, .52); soft = 1/(1+np.exp(-(s_-thr)/.13))
        flow = 1.15 + 1.6*(field_ref(260,5,Wl,Hl)*.35)
        low = soft[...,None]*np.array([66,28,24],np.float32) + (1-soft[...,None])*np.array([228,219,205],np.float32)
        low = low*(1+.05*field_ref(150,9,Wl,Hl)[...,None])
    else:
        # stripe pattern from tiger_shapes(), V line down the spine; the logo and spine symbol zones are kept clear
        cxs = sx + D/2; lh = LOGO_W*501/786
        excl = [(cxs-SYM_H/2-2, H-BOT-SYM_W-2, SYM_H+4, SYM_W+4, 4), ((W-LOGO_W)/2-6, H-BOT-lh-6, LOGO_W+12, lh+12, 6)]
        paths = tiger_shapes(random.Random(9*11+1), Wf, H, cxs, H*.062, excl); SS = 2
        mk = Image.new('L', (Wl*SS, Hl*SS), 0); dd = _ID.Draw(mk)
        for p in paths:
            pts = [((float(a)+B)*PXL*SS, (float(b)+B)*PXL*SS) for a,b in re.findall(r'(-?\d+\.?\d*) (-?\d+\.?\d*)', p)]
            if len(pts) > 2: dd.polygon(pts, fill=255)
        m = np.asarray(mk.resize((Wl,Hl), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.2))).astype(np.float32)/255
        soft = 1/(1+np.exp(-((m-.5) + .10*field_ref(14,3,Wl,Hl) + .06*field_ref(6,4,Wl,Hl))/.11))
        tone = 1 + .10*field_ref(120,5,Wl,Hl)[...,None]
        low = soft[...,None]*np.array([34,24,21],np.float32) + (1-soft[...,None])*np.array([156,76,50],np.float32)*tone
        flow = 1.45 + .9*field_ref(240,6,Wl,Hl)*.35
        low = low*(1+.05*field_ref(150,9,Wl,Hl)[...,None])
    im = strands(low, soft, flow, kind, 23 if kind=='tiger' else 11)
    im.convert('RGB').save(fn, quality=88, dpi=(305,305)); print(kind, SIZE, im.size, round(time.time()-t0), 's', os.path.getsize(fn)//1024, 'KB')
    return fn

MARK = 7; PAD = B + 1 + MARK + 6                 # page margin outside the trim: bleed, gap, mark length, room for the info line
PW, PH = Wf + 2*PAD, H + 2*PAD
def page(vol):
    n, lines = vol[0], vol[1]; body = build(vol); G = 'stroke="#000" stroke-width=".1" fill="none"'
    marks = []
    for (cx,cy,sxn,syn) in ((0,0,-1,-1),(Wf,0,1,-1),(0,H,-1,1),(Wf,H,1,1)):      # crop marks at the four trim corners
        marks.append(f'<line x1="{cx+sxn*(B+1)}" y1="{cy}" x2="{cx+sxn*(B+1+MARK)}" y2="{cy}" {G}/><line x1="{cx}" y1="{cy+syn*(B+1)}" x2="{cx}" y2="{cy+syn*(B+1+MARK)}" {G}/>')
    for x in (sx, sx+D):                                                          # fold marks (spine edges), top and bottom
        marks.append(f'<line x1="{x}" y1="{-(B+1)}" x2="{x}" y2="{-(B+1+MARK)}" {G} stroke-dasharray=".8 .6"/><line x1="{x}" y1="{H+B+1}" x2="{x}" y2="{H+B+1+MARK}" {G} stroke-dasharray=".8 .6"/>')
    cols = f'{vol[2]} / {vol[3]}' + (f' / {vol[6]} print' if vol[6] else '')
    info = (f'FB-{n:02d} {" ".join(lines)}  ·  size {SIZE} {W/10:g} × {H/10:g} × {D/10:g} cm  ·  flat trim {Wf} × {H} mm, bleed {B} mm  ·  spine {D} mm  ·  {cols}  ·  '
            f'RGB hex, convert to CMYK/Pantone  ·  stand-in lettering (Inter), not final  ·  no wrap allowance')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}">'
           f'<rect width="{PW}" height="{PH}" fill="#fff"/><g transform="translate({PAD} {PAD})">{body}{"".join(marks)}'
           f'<text x="{-B}" y="{H+B+MARK+5}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="2.6" fill="#000">{info}</text></g></svg>')
    return svg
if __name__ == '__main__':
    for kind in ('cow','tiger'): gen_texture(kind)
    os.makedirs(f'{out}/{SIZE}/svg', exist_ok=True); names = []
    for v in VOLS:
        fn = f'FB-{v[0]:02d}_{slug(v[1])}_{SIZE}_{W//10}x{H//10}x{D/10:g}cm_print'
        open(f'{out}/{SIZE}/svg/{fn}.svg','w').write(page(v)); names.append(fn)
    print(SIZE, 'spine type', round(SP,2), 'mm; page', PW, 'x', PH, 'mm;', len(names), 'files')
