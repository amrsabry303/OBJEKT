"""objekt faux books, draft 19. One size for every volume: Medium, 18 x 25 cm, 3.8 cm deep.
Writes one flat (back + spine + front) per volume plus a contact sheet. Units: mm, finished size, no bleed.
Lettering is a stand-in (Inter) for Galak Round, which is not licensed. Do not commit font files.
Usage: python3 make_flats.py <repo root>"""
import re, sys, random, math
from PIL import ImageFont
root = sys.argv[1]; out = root + '/plan/faux-books/artwork'
logo_d = re.search(r' d="([^"]+)"', open(root + '/brand/objekt-logo.svg').read()).group(1)
sym_d = re.search(r' d="([^"]+)"', open(root + '/brand/objekt-symbol.svg').read()).group(1)
C = {'Bone':'#E9E4D8','Putty':'#B9B2A5','Carbon':'#222222','Ink':'#1E2A44','Oxblood':'#5A1F25','Clay':'#A8553A','Chocolate':'#4A2A1B','Objekt Green':'#37613F'}
MF = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf', 100)
CAP = .727
def tw(txt, size, track=0.0): return sum(MF.getlength(c) for c in txt)/100*size + len(txt)*size*track
FT = 'font-family="Galak Round, Inter Display, Inter, Helvetica, Arial, sans-serif"'
W, H, D = 180, 250, 38            # every volume: 18 x 25 x 3.8 cm
Wf = 2*W + D; sx = W; fx = W + D
BOT = 14; SYM_W = 20; SYM_H = SYM_W*223/308; GAP = 10; LOGO_W = 40
TRK = -.012                       # tight tracking on the big type

# n, title lines, cover, lettering, front layout, spine lines, print
VOLS = [
 (1,['NOT A','BOOK'],'Bone','Objekt Green','crop',['NOT A','BOOK'],None),
 (2,['SHELF','LIFE'],'Putty','Chocolate','vert',['SHELF','LIFE'],None),
 (3,['HEAVY','READING'],'Carbon','Bone','fill',['HEAVY','READING'],None),
 (4,['JUDGE','THE','COVER'],'Ink','Putty','over',['JUDGE THE','COVER'],None),
 (5,['OBJEKTS OF','CHARACTER'],'Oxblood','Bone','fill',['OBJEKTS OF','CHARACTER'],None),
 (6,['USELESS','ON PURPOSE'],'Clay','Bone','vert',['USELESS','ON PURPOSE'],None),
 (7,['COFFEE','TABLE','BOOK'],'Chocolate','Putty','fill',['COFFEE TABLE','BOOK'],None),
 (8,['DESIGN','WORTH','NOTICING'],'Objekt Green','Bone','crop',['DESIGN WORTH','NOTICING'],None),
 (9,['EASY','TIGER'],'Clay','Bone','fill',['EASY','TIGER'],'tiger'),
 (10,['HOLY','COW'],'Bone','Bone','fill',['HOLY','COW'],'cow'),
 (11,['BETWEEN','THE','LINES'],'Bone','Clay','fill',['BETWEEN','THE LINES'],'stripe'),
]
def slug(lines): return '-'.join(lines).lower().replace(' ','-')
SP = min((D-9)/(CAP*2.35), (H-BOT-SYM_W-GAP-BOT)/max(tw(l,1,.02) for v in VOLS for l in v[5]))   # one spine size for all

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

def front_layout(kind, lines, ink):
    """returns (list of (x, y, size, rot, txt)) in flat coordinates"""
    m = 11; avail = W - 2*m; items = []
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
    n, lines, cover, ink, kind, slines, prt = vol
    bg, fg = C[cover], C[ink]; o = []
    o.append(f'<clipPath id="flat{n}"><rect x="0" y="0" width="{Wf}" height="{H}"/></clipPath><g clip-path="url(#flat{n})">')
    o.append(f'<rect x="0" y="0" width="{Wf}" height="{H}" fill="{bg}"/>')
    items = front_layout(kind, lines, ink)
    lw = LOGO_W; lh = lw*501/786; logo_x = (W-lw)/2; logo_y = H - BOT - lh
    cxs = sx + D/2; k = SYM_W/308; ty = H - BOT; ys = ty - SYM_W - GAP
    scap = SP*CAP; sstep = scap*1.32; bh = scap + sstep; x1 = cxs - bh/2 + scap
    def lettering(fill, clip=None):
        g = []
        for (x,y,s,rot,l) in items: g.append(text(x,y,s,l,fill,rot,extra='big'))
        g.append(f'<path transform="translate({logo_x:.1f} {logo_y:.1f}) scale({lw/786:.5f})" fill="{fill}" fill-rule="evenodd" d="{logo_d}"/>')
        g.append(f'<path transform="translate({cxs-SYM_H/2:.2f} {ty:.1f}) rotate(-90) scale({k:.5f}) translate(-238 0)" fill="{fill}" fill-rule="evenodd" d="{sym_d}"/>')
        for j,l in enumerate(slines): g.append(text(x1+j*sstep, ys, SP, l, fill, -90))
        s_ = '\n'.join(g)
        return f'<g clip-path="url(#{clip})">{s_}</g>' if clip else s_
    if prt == 'tiger':
        r = random.Random(n*11+1)
        o.append(f'<g>')
        excl = [(cxs-SYM_H/2-2, H-BOT-SYM_W-2, SYM_H+4, SYM_W+4, 4), (logo_x-6, logo_y-6, lw+12, lh+12, 6)]
        for d in tiger_shapes(r, Wf, H, cxs, H*.062, excl): o.append(f'<path fill="{C["Carbon"]}" d="{d}"/>')
        o.append('</g>')
        o.append(lettering(fg))
    elif prt == 'cow':
        o.append(f'<image href="prints/cow-hide_v1.png" x="0" y="0" width="{Wf}" height="{H}" preserveAspectRatio="none"/>')
        o.append(lettering(fg))
    elif prt == 'stripe':
        nb = 12; bhh = H/nb
        cb = ''.join(f'<rect x="0" y="{i*bhh:.2f}" width="{Wf}" height="{bhh+.01:.2f}"/>' for i in range(nb) if i % 2 == 0)   # Carbon bands
        bb = ''.join(f'<rect x="0" y="{i*bhh:.2f}" width="{Wf}" height="{bhh+.01:.2f}"/>' for i in range(nb) if i % 2 == 1)   # Bone bands
        o.append(f'<defs><clipPath id="cb{n}">{cb}</clipPath><clipPath id="bb{n}">{bb}</clipPath></defs>')
        o.append(f'<rect width="{Wf}" height="{H}" fill="{C["Bone"]}"/>')
        o.append(f'<g clip-path="url(#cb{n})"><rect width="{Wf}" height="{H}" fill="{C["Carbon"]}"/></g>')
        o.append(lettering(C['Clay']))
    else:
        o.append(lettering(fg))
    for x in (sx, sx+D):
        o.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#000" stroke-opacity=".22" stroke-width=".4" stroke-dasharray="3 2"/>')
    o.append('</g>')
    return '\n'.join(o)

def single(vol):
    n, lines = vol[0], vol[1]; pad = 12; body = build(vol)
    cap = f'FB-{n:02d} {" ".join(lines)} · 18 × 25 × 3.8 cm · {vol[2]} / {vol[3]}' + (f' · {vol[6]} print' if vol[6] else '') + ' · design draft, stand-in lettering, not print-ready'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {Wf+2*pad} {H+2*pad+14}" width="{(Wf+2*pad)*3}" height="{(H+2*pad+14)*3}">'
           f'<rect width="100%" height="100%" fill="#E1D9CF"/><g transform="translate({pad} {pad})">{body}</g>'
           f'<text x="{pad}" y="{H+pad+10}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="4.2" fill="#25395A">{cap}</text></svg>')
    fn = f'FB-{n:02d}_{slug(lines)}_flat_design-draft_v4.svg'; open(f'{out}/{fn}','w').write(svg); return fn
files = [single(v) for v in VOLS]

# contact sheet: 3 flats per row, then the sets lying flat
Ks = 1.2; gap = 40; F = 'font-family="Inter, Helvetica, Arial, sans-serif"'
o = []; y = 210
o.append(f'<text x="80" y="90" {F} font-size="30" font-weight="500" fill="#25395A">01 // faux books: flats, back · spine · front, draft 4</text>')
o.append(f'<text x="80" y="130" {F} font-size="19" fill="#25395A">One size, 18 × 25 × 3.8 cm. Finished size to scale (1 mm = {Ks} px). Bigger type, cropped and overflowing. Lettering is Inter, a stand-in for Galak Round.</text>')
o.append(f'<text x="80" y="158" {F} font-size="19" fill="#25395A">Not print-ready: no bleed, because the maker\'s template is not known.</text>')
for i,v in enumerate(VOLS):
    col = i % 3; row = i // 3; x = 80 + col*(Wf*Ks+gap); yy = y + row*(H*Ks + 95)
    o.append(f'<g transform="translate({x} {yy}) scale({Ks})">{build(v)}</g>')
    o.append(f'<text x="{x}" y="{yy+H*Ks+26}" {F} font-size="17" font-weight="500" fill="#25395A">{v[0]:02d} · {" ".join(v[1])}</text>')
    o.append(f'<text x="{x}" y="{yy+H*Ks+48}" {F} font-size="15" fill="#25395A">{v[2]} / {v[3]}' + (f' · {v[6]}' if v[6] else '') + '</text>')
y += 4*(H*Ks+95) + 20
o.append(f'<text x="80" y="{y}" {F} font-size="30" font-weight="500" fill="#25395A">02 // sets of three, lying flat, spines out, head to the right</text>')
y += 40
def spine_view(v):
    return (f'<g transform="translate(-{W},0)"><clipPath id="sv{v[0]}"><rect x="{W}" y="0" width="{D}" height="{H}"/></clipPath>'
            f'<g clip-path="url(#sv{v[0]})">{build(v)}</g></g>')
byn = {v[0]: v for v in VOLS}
SETS = [('Plain set A',[3,1,5]),('Plain set B',[7,2,8]),('Print set',[9,10,11])]
for si,(lab,ids) in enumerate(SETS):
    sx0 = 80 + si*(H*Ks + 120); yy = y + 3*(D*Ks+2)
    for n in ids:
        yy -= D*Ks + 2
        o.append(f'<g transform="translate({sx0} {yy:.1f}) scale({Ks}) translate({H},0) rotate(90)">{spine_view(byn[n])}</g>')
    o.append(f'<text x="{sx0}" y="{y+3*(D*Ks+2)+30}" {F} font-size="17" fill="#25395A">{lab}</text>')
y += 3*(D*Ks+2) + 70
sheet = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 {int(y)}" width="1600" height="{int(y)}"><rect width="100%" height="100%" fill="#E1D9CF"/>' + '\n'.join(o) + '</svg>')
open(f'{out}/faux-books-flats_contact-sheet_v4.svg','w').write(sheet)
print(files, int(y), 'SP', round(SP,2))
