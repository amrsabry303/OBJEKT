"""Generate the faux book flats (back + spine + front) and a contact sheet.
Usage: python3 make_flats.py <repo root>
Units: mm. Finished size, no bleed (maker's template not known yet).
Lettering is a stand-in: Galak Round is not licensed, so the SVG asks for it first
and falls back to Inter. Do not commit font files."""
import re, sys, random, math, subprocess, os
from PIL import ImageFont
root = sys.argv[1]
out = root + '/plan/faux-books/artwork'
logo_d = re.search(r' d="([^"]+)"', open(root + '/brand/objekt-logo.svg').read()).group(1)
C = {'Bone':'#E9E4D8','Putty':'#B9B2A5','Carbon':'#222222','Ink':'#1E2A44','Oxblood':'#5A1F25','Clay':'#A8553A','Chocolate':'#4A2A1B','Objekt Green':'#37613F'}
MF = ImageFont.truetype('/usr/share/fonts/opentype/inter/InterDisplay-Regular.otf', 100)
CAP = .727
def tw(txt, size, track): return sum(MF.getlength(c) for c in txt)/100*size + len(txt)*size*track
FT = 'font-family="Galak Round, Inter Display, Inter, Helvetica, Arial, sans-serif"'
SZ = {'L':(230,300),'M':(180,250),'S':(140,200)}
D = 45
def _avail(size):
    H = SZ[size][1]; ms = 14
    return (H - ms - 25 - 8 - 2*5.0*.75 - 10 - 5.0) - ms
# n, title lines, cover, lettering, size, print
VOLS = [
 (1,['NOT A','BOOK'],'Bone','Objekt Green','M',None),
 (2,['SHELF','LIFE'],'Putty','Chocolate','M',None),
 (3,['HEAVY','READING'],'Carbon','Bone','L',None),
 (4,['JUDGE','THE','COVER'],'Ink','Putty','L',None),
 (5,['OBJEKTS OF','CHARACTER'],'Oxblood','Bone','S',None),
 (6,['USELESS','ON PURPOSE'],'Clay','Bone','S',None),
 (7,['COFFEE','TABLE','BOOK'],'Chocolate','Putty','L',None),
 (8,['DESIGN','WORTH','NOTICING'],'Objekt Green','Bone','S',None),
 (9,['EASY','TIGER'],'Clay','Bone','L','tiger'),
 (10,['HOLY','COW'],'Bone','Chocolate','M','cow'),
 (11,['BETWEEN','THE','LINES'],'Bone','Objekt Green','S','stripe'),
]
SPINE_SIZE = {}
for _sz in SZ:
    SPINE_SIZE[_sz] = min([D*.22] + [_avail(_sz)/tw(' '.join(v[1]),1,.05) for v in VOLS if v[4]==_sz])
def slug(lines): return '-'.join(lines).lower().replace(' ','-')

def build(vol):
    n, lines, cover, ink, size, prt = vol
    W, H = SZ[size]
    o = []
    bg, fg = C[cover], C[ink]
    # panels
    bx, sx, fx = 0, W, W + D
    Wf = 2*W + D
    o.append(f'<rect x="0" y="0" width="{Wf}" height="{H}" fill="{bg}"/>')
    m = W*.08
    # title (front, top left)
    s = min(.70*W/max(tw(l,1,.02) for l in lines), W*.2)
    cap = s*CAP; step = cap*1.4
    tx = fx + m
    title_h = cap + (len(lines)-1)*step
    title_rect = (tx-4, m-4, .70*W+8, title_h+8)       # x,y,w,h in flat coords
    # back logo
    lw = W*.28; lh = lw*501/786
    logo_x = bx + (W-lw)/2; logo_y = H - m - lh
    logo_rect = (logo_x-6, logo_y-6, lw+12, lh+12)
    # prints on back and front only
    def panel(px, kind, seed):
        r = random.Random(seed)
        o.append(f'<clipPath id="p{n}_{px:.0f}"><rect x="{px}" y="0" width="{W}" height="{H}"/></clipPath><g clip-path="url(#p{n}_{px:.0f})">')
        def hits(x0, y0, w, h, rect, pad=0):
            rx, ry, rw, rh = rect
            return not (x0+w < rx-pad or x0 > rx+rw+pad or y0+h < ry-pad or y0 > ry+rh+pad)
        excl = title_rect if px == fx else logo_rect
        if kind == 'tiger':
            pitch = W*.115; k = int(W/pitch)+1
            for i in range(k):
                for side in (0, 1):
                    x = px + (i + .5 + (.5 if side else 0) + r.uniform(-.12,.12))*pitch
                    th = pitch*r.uniform(.28,.42); ln = H*r.uniform(.2,.42); sag = r.uniform(-.5,.5)*pitch
                    y0, yl = (0, ln) if side == 0 else (H, H-ln)
                    if hits(x-th/2-sag.__abs__(), min(y0,yl), th+2*abs(sag), abs(ln), excl, 6): continue
                    ym = (y0+yl)/2
                    o.append(f'<path fill="{C["Carbon"]}" d="M{x-th/2:.1f} {y0:.1f} Q{x-th/2+sag*.4:.1f} {ym:.1f} {x+sag:.1f} {yl:.1f} Q{x+th/2+sag*.6:.1f} {ym:.1f} {x+th/2:.1f} {y0:.1f}Z"/>')
        elif kind == 'cow':
            placed = []
            tries = 0
            while len(placed) < 6 and tries < 400:
                tries += 1
                rad = W*r.uniform(.07,.17); cx = px + r.uniform(-.02,1.02)*W; cy = r.uniform(.02,1.02)*H
                if hits(cx-rad*1.25, cy-rad*1.2, rad*2.5, rad*2.4, excl, 8): continue
                if any(math.hypot(cx-a, cy-b) < (rad+c)*1.15 for a,b,c in placed): continue
                placed.append((cx,cy,rad))
            for cx,cy,rad in placed:
                nn = 9; pts = []
                for i in range(nn):
                    a = 2*math.pi*i/nn + r.uniform(-.2,.2); q = rad*r.uniform(.6,1.15)
                    pts.append((cx+q*1.15*math.cos(a), cy+q*math.sin(a)))
                mid = lambda a,b: ((a[0]+b[0])/2, (a[1]+b[1])/2)
                st = mid(pts[-1], pts[0]); d = 'M%.1f %.1f' % st
                for i in range(nn):
                    e = mid(pts[i], pts[(i+1)%nn]); d += ' Q%.1f %.1f %.1f %.1f' % (pts[i]+e)
                o.append(f'<path fill="{C["Chocolate"]}" d="{d}Z"/>')
        elif kind == 'stripe':
            for i in range(4):
                o.append(f'<rect x="{px}" y="{H*(.42+.085*i):.1f}" width="{W}" height="{H*.04:.1f}" fill="{C["Objekt Green"]}"/>')
        o.append('</g>')
    if prt:
        panel(bx, prt, n*11+1); panel(fx, prt, n*11+2)
    # front title
    for j, l in enumerate(lines):
        o.append(f'<text x="{tx:.1f}" y="{m+cap+j*step:.1f}" {FT} font-size="{s:.2f}" font-weight="500" letter-spacing="{s*.02:.2f}" fill="{fg}">{l}</text>')
    # back logo
    o.append(f'<path transform="translate({logo_x:.1f} {logo_y:.1f}) scale({lw/786:.5f})" fill="{fg}" fill-rule="evenodd" d="{logo_d}"/>')
    # spine, all caps, reads bottom to top: logo, number, title
    cx = sx + D/2; ms = 14
    slw = 25; slh = slw*501/786
    ly = H - ms
    o.append(f'<path transform="translate({cx-slh/2:.2f} {ly:.1f}) rotate(-90) scale({slw/786:.5f})" fill="{fg}" fill-rule="evenodd" d="{logo_d}"/>')
    ns = 5.0; ny = ly - slw - 8
    o.append(f'<text transform="translate({cx+ns*CAP/2:.2f} {ny:.1f}) rotate(-90)" {FT} font-size="{ns}" font-weight="500" letter-spacing="{ns*.12:.2f}" fill="{fg}">{n:02d}</text>')
    ty = ny - 2*ns*.75 - 10
    ttl = ' '.join(lines)
    avail = ty - ms
    ss = SPINE_SIZE[size]
    o.append(f'<text transform="translate({cx+ss*CAP/2:.2f} {ty:.1f}) rotate(-90)" {FT} font-size="{ss:.2f}" font-weight="500" letter-spacing="{ss*.05:.2f}" fill="{fg}">{ttl}</text>')
    # fold lines
    for x in (sx, sx+D):
        o.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#000" stroke-opacity=".25" stroke-width=".4" stroke-dasharray="3 2"/>')
    return '\n'.join(o), Wf, H, ss

def single(vol):
    body, Wf, H, ss = build(vol)
    n, lines, cover, ink, size, prt = vol
    pad = 12
    cap = f'FB-{n:02d} {" ".join(lines)} · {size} {SZ[size][0]/10:g} × {SZ[size][1]/10:g} × 4.5 cm · {cover} / {ink}' + (f' · {prt} print' if prt else '') + ' · design draft, stand-in lettering, not print-ready'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wf+2*pad} {H+2*pad+14}" width="{(Wf+2*pad)*3}" height="{(H+2*pad+14)*3}">'
           f'<rect width="100%" height="100%" fill="#E1D9CF"/><g transform="translate({pad} {pad})">{body}</g>'
           f'<text x="{pad}" y="{H+pad+10}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="4.2" fill="#25395A">{cap}</text></svg>')
    fn = f'FB-{n:02d}_{slug(lines)}_flat_design-draft_v1.svg'
    open(f'{out}/{fn}', 'w').write(svg)
    return fn
files = [single(v) for v in VOLS]
# contact sheet
Ks = 1.3; gap = 40
rows = [[1,2],[3,4],[5,6,8],[7,9],[10,11]]
W0 = 1600; y = 220
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W0} 2700" width="{W0}" height="2700"><rect width="100%" height="100%" fill="#E1D9CF"/>']
F = 'font-family="Inter, Helvetica, Arial, sans-serif"'
o.append(f'<text x="80" y="90" {F} font-size="30" font-weight="500" fill="#25395A">01 // faux books: flats, back · spine · front, draft 1</text>')
o.append(f'<text x="80" y="158" {F} font-size="19" fill="#25395A">Prints are placeholders. Not print-ready: no bleed, because the maker\'s template is not known.</text>')
o.append(f'<text x="80" y="130" {F} font-size="19" fill="#25395A">Finished size, to scale (1 mm = {Ks} px). Spine title in caps, one size per book size. Stand-in lettering (Inter) for Galak Round, not licensed.</text>')
byn = {v[0]: v for v in VOLS}
for row in rows:
    x = 80; rh = 0
    for n in row:
        v = byn[n]; body, Wf, H, ss = build(v)
        o.append(f'<g transform="translate({x} {y}) scale({Ks})">{body}</g>')
        lab = f'{n:02d} · {" ".join(v[1])}'
        lab2 = f'{v[4]} {SZ[v[4]][0]/10:g} × {SZ[v[4]][1]/10:g} cm · {v[2]} / {v[3]}' + (f' · {v[5]}' if v[5] else '')
        o.append(f'<text x="{x}" y="{y+H*Ks+26}" {F} font-size="17" font-weight="500" fill="#25395A">{lab}</text><text x="{x}" y="{y+H*Ks+48}" {F} font-size="15" fill="#25395A">{lab2}</text>')
        x += Wf*Ks + gap; rh = max(rh, H*Ks)
    y += rh + 90
o.append('</svg>')
H0 = int(y + 20)
sheet = '\n'.join(o).replace('2700', str(H0))
open(f'{out}/faux-books-flats_contact-sheet_v1.svg', 'w').write(sheet)
print(files, H0)
