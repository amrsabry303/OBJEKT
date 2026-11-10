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
sym_d = re.search(r' d="([^"]+)"', open(root + '/brand/objekt-symbol.svg').read()).group(1)
BOT = 14          # distance from the foot edge to the logo, every size
SYM_W = 20        # spine symbol width
SYM_H = SYM_W*223/308
GAP = 10          # symbol to title
LOGO_W = 40       # back logo width, every size
SPINE_LINES = {1:['NOT A','BOOK'],2:['SHELF','LIFE'],3:['HEAVY','READING'],4:['JUDGE THE','COVER'],5:['OBJEKTS OF','CHARACTER'],
 6:['USELESS','ON PURPOSE'],7:['COFFEE TABLE','BOOK'],8:['DESIGN WORTH','NOTICING'],9:['EASY','TIGER'],10:['HOLY','COW'],11:['BETWEEN','THE LINES']}
# one spine type size for every volume: set by the longest spine line on the shortest book (S, 200 mm) and by the 45 mm spine width
SP_AVAIL = SZ['S'][1] - (BOT + SYM_W + GAP) - BOT
SP = min(SP_AVAIL/max(tw(l,1,.05) for ls in SPINE_LINES.values() for l in ls), (D-16)/(CAP*2.4))
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
    lw = LOGO_W; lh = lw*501/786
    logo_x = bx + (W-lw)/2; logo_y = H - BOT - lh
    logo_rect = (logo_x-6, logo_y-6, lw+12, lh+12)
    # prints wrap across back, spine and front; clear space is kept round the front title, the back logo and the spine title + symbol
    cxs = sx + D/2
    scap0 = SP*CAP; bh0 = scap0*2.4
    ys0 = H - BOT - SYM_W - GAP
    slen = max(tw(l, SP, .05) for l in SPINE_LINES[n])
    spine_rect = (cxs - bh0/2 - 4, ys0 - slen - 6, bh0 + 8, H - (ys0 - slen - 6))
    def hits(x0, y0, w, h, rect, pad=0):
        rx, ry, rw, rh = rect
        return not (x0+w < rx-pad or x0 > rx+rw+pad or y0+h < ry-pad or y0 > ry+rh+pad)
    sfg = fg
    if prt in ('tiger', 'cow'):
        r = random.Random(n*11+1)
        o.append(f'<clipPath id="w{n}"><rect x="0" y="0" width="{Wf}" height="{H}"/></clipPath><g clip-path="url(#w{n})">')
        if prt == 'tiger':
            pitch = W*.115; k = int(Wf/pitch)+1
            for i in range(k):
                for side in (0, 1):
                    x = (i + .5 + (.5 if side else 0) + r.uniform(-.12,.12))*pitch
                    th = pitch*r.uniform(.28,.42); ln = H*r.uniform(.2,.42); sag = r.uniform(-.5,.5)*pitch
                    on_spine = (sx - th) <= x <= (sx + D + th)
                    if on_spine: continue
                    y0, yl = (0, ln) if side == 0 else (H, H-ln)
                    if not on_spine and (hits(x-th/2-abs(sag), min(y0,yl), th+2*abs(sag), abs(ln), title_rect, 6) or hits(x-th/2-abs(sag), min(y0,yl), th+2*abs(sag), abs(ln), logo_rect, 6)): continue
                    ym = (y0+yl)/2
                    o.append(f'<path fill="{C["Carbon"]}" d="M{x-th/2:.1f} {y0:.1f} Q{x-th/2+sag*.4:.1f} {ym:.1f} {x+sag:.1f} {yl:.1f} Q{x+th/2+sag*.6:.1f} {ym:.1f} {x+th/2:.1f} {y0:.1f}Z"/>')
            # narrower stripes on the spine so the print visibly wraps round it
            sp_pitch = D/3.2
            for i in range(4):
                for side in (0, 1):
                    x = sx + (i + .5 + (.5 if side else 0) + r.uniform(-.1,.1))*sp_pitch
                    if x > sx + D - 2: continue
                    th = sp_pitch*r.uniform(.3,.45); ln = H*r.uniform(.18,.4); sag = r.uniform(-.4,.4)*sp_pitch
                    y0, yl = (0, ln) if side == 0 else (H, H-ln)
                    if side == 1 and hits(x-th/2-abs(sag), H-ln, th+2*abs(sag), ln, (cxs-SYM_H/2-2, H-BOT-SYM_W-2, SYM_H+4, SYM_W+4), 3): continue
                    ym = (y0+yl)/2
                    o.append(f'<path fill="{C["Carbon"]}" d="M{x-th/2:.1f} {y0:.1f} Q{x-th/2+sag*.4:.1f} {ym:.1f} {x+sag:.1f} {yl:.1f} Q{x+th/2+sag*.6:.1f} {ym:.1f} {x+th/2:.1f} {y0:.1f}Z"/>')
        else:
            placed = []; tries = 0
            while len(placed) < 9 and tries < 800:
                tries += 1
                rad = W*r.uniform(.07,.16); cx = r.uniform(-.02,1.02)*Wf; cy = r.uniform(.02,1.02)*H
                bb = (cx-rad*1.25, cy-rad*1.2, rad*2.5, rad*2.4)
                if any(hits(*bb, ex, 8) for ex in (title_rect, logo_rect, spine_rect)): continue
                if any(math.hypot(cx-a_, cy-b_) < (rad+c_)*1.15 for a_,b_,c_ in placed): continue
                placed.append((cx,cy,rad))
            free = spine_rect[1] - 6
            for _ in range(3):
                if free < 22: break
                rad = min(W*.1, free/2.5); cx = cxs + r.uniform(-.12,.12)*D; cy = r.uniform(rad*1.25, free - rad*1.2)
                if any(math.hypot(cx-a_, cy-b_) < (rad+c_)*1.15 for a_,b_,c_ in placed): continue
                placed.append((cx,cy,rad))
            for cx,cy,rad in placed:
                nn = 9; pts = []
                for i in range(nn):
                    a_ = 2*math.pi*i/nn + r.uniform(-.2,.2); q = rad*r.uniform(.6,1.15)
                    pts.append((cx+q*1.15*math.cos(a_), cy+q*math.sin(a_)))
                mid = lambda p1,p2: ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
                st = mid(pts[-1], pts[0]); d = 'M%.1f %.1f' % st
                for i in range(nn):
                    e = mid(pts[i], pts[(i+1)%nn]); d += ' Q%.1f %.1f %.1f %.1f' % (pts[i]+e)
                o.append(f'<path fill="{C["Chocolate"]}" d="{d}Z"/>')
        o.append('</g>')
    elif prt == 'stripe':
        for px in (bx, fx):
            for i in range(4):
                o.append(f'<rect x="{px}" y="{H*(.42+.085*i):.1f}" width="{W}" height="{H*.04:.1f}" fill="{C["Objekt Green"]}"/>')
        # the stripe wraps into a solid green spine, Bone lettering
        o.append(f'<rect x="{sx}" y="0" width="{D}" height="{H}" fill="{C["Objekt Green"]}"/>')
        sfg = C['Bone']
    # front title
    for j, l in enumerate(lines):
        o.append(f'<text x="{tx:.1f}" y="{m+cap+j*step:.1f}" {FT} font-size="{s:.2f}" font-weight="500" letter-spacing="{s*.02:.2f}" fill="{fg}">{l}</text>')
    # back logo
    o.append(f'<path transform="translate({logo_x:.1f} {logo_y:.1f}) scale({lw/786:.5f})" fill="{fg}" fill-rule="evenodd" d="{logo_d}"/>')
    # spine: symbol at the foot, title in caps above it, reading bottom to top (reads left to right when the book lies head right)
    cx = sx + D/2
    k = SYM_W/308
    ty = H - BOT
    o.append(f'<path transform="translate({cx-SYM_H/2:.2f} {ty:.1f}) rotate(-90) scale({k:.5f}) translate(-238 0)" fill="{sfg}" fill-rule="evenodd" d="{sym_d}"/>')
    ys = ty - SYM_W - GAP
    scap = SP*CAP; sstep = scap*1.4; bh = scap + sstep
    x1 = cx - bh/2 + scap
    for j, l in enumerate(SPINE_LINES[n]):
        o.append(f'<text transform="translate({x1+j*sstep:.2f} {ys:.1f}) rotate(-90)" {FT} font-size="{SP:.2f}" font-weight="500" letter-spacing="{SP*.05:.2f}" fill="{sfg}">{l}</text>')
    ss = SP
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
    fn = f'FB-{n:02d}_{slug(lines)}_flat_design-draft_v3.svg'
    open(f'{out}/{fn}', 'w').write(svg)
    return fn
files = [single(v) for v in VOLS]
# contact sheet
Ks = 1.3; gap = 40
rows = [[1,2],[3,4],[5,6,8],[7,9],[10,11]]
W0 = 1600; y = 220
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W0} 2700" width="{W0}" height="2700"><rect width="100%" height="100%" fill="#E1D9CF"/>']
F = 'font-family="Inter, Helvetica, Arial, sans-serif"'
o.append(f'<text x="80" y="90" {F} font-size="30" font-weight="500" fill="#25395A">01 // faux books: flats, back · spine · front, draft 3</text>')
o.append(f'<text x="80" y="158" {F} font-size="19" fill="#25395A">Lettering is Inter, a stand-in for Galak Round (not licensed). Prints are placeholders. Not print-ready: no bleed.</text>')
o.append(f'<text x="80" y="130" {F} font-size="19" fill="#25395A">Finished size, to scale (1 mm = {Ks} px). Prints wrap onto the spine. Spine: icon and caps title, one size.</text>')
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
def spine_view(v):
    body, Wf, H, _ = build(v); W = SZ[v[4]][0]
    return (f'<g transform="translate(-{W},0)"><clipPath id="sv{v[0]}"><rect x="{W}" y="0" width="{D}" height="{H}"/></clipPath>'
            f'<g clip-path="url(#sv{v[0]})">{body}</g></g>'), H
y += 30
o.append(f'<text x="80" y="{y}" {F} font-size="30" font-weight="500" fill="#25395A">02 // lying stacks, spines out, head to the right</text>')
y += 40
for si, (lab, ids) in enumerate([('Plain set A',[3,1,5]),('Plain set B',[7,2,8]),('Print set',[9,10,11])]):
    sx0 = 80 + si*(300*Ks + 90); yy = y + 3*(D*Ks+2)
    for n in ids:
        yy -= D*Ks + 2
        g, H = spine_view(byn[n]); off = (300 - H)/2*Ks + (6 if n in (1,10) else 0)
        o.append(f'<g transform="translate({sx0+off:.1f} {yy:.1f}) scale({Ks}) translate({H},0) rotate(90)">{g}</g>')
    o.append(f'<text x="{sx0}" y="{y+3*(D*Ks+2)+30}" {F} font-size="17" fill="#25395A">{lab}</text>')
y += 3*(D*Ks+2) + 60
o.append('</svg>')
H0 = int(y + 20)
sheet = '\n'.join(o).replace('2700', str(H0))
open(f'{out}/faux-books-flats_contact-sheet_v3.svg', 'w').write(sheet)
print(files, H0)
