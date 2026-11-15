"""OBJ-159: tall shelf, six WOOD shelves, two stainless side plates with five circular cut-outs each. Production drawing set, REV 9 (approved 15 Nov).
Run: python3 make_obj159_rev9.py <repo root>   then: NODE_PATH=<playwright> node make_pdf.js <dir> OBJ-159 9
Reference: images/OBJ-159.jpg is a third-party piece (jeremylechatelier, Hublot). Used for the IDEA only. This is objekt's OWN design.
REV 9 (15 Nov): Sabry: the drawing said the shelves are metal, they are WOOD SLABS like the reference photo. Wood options: light wood (oak) like the reference, or dark oak.
  Shelves are now solid wood slabs 1.25 in (31.75 mm) thick, rounded long edges, made by a woodworker (not Polycraft sheet metal). Only the two stainless plates are cut and nested.
  Fixing: M6 threaded inserts in the slab ends and M6 screws through the plate holes, centred in the slab thickness (hole 15.875 below the top face).
Rev 8 (approved 12 Nov) had hollow folded stainless shelves: superseded. Everything else is as rev 8: 74 x 34 x 14 in, five circles per plate, equal shelf gaps, no feet, 3 mm step and two 40 mm pads.
Sabry's sizes: height, width, depth, shelf thickness, six shelves, five circles, no feet, screwed shelves, wood shelves. EVERYTHING ELSE IS PROPOSED BY CLAUDE. Arabic is a draft. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-159'; os.makedirs(OUT, exist_ok=True)
REV = 9; DATE = '15 Nov 2026'; PN = 'OBJ-159'
IN = 25.4
OH, OW, OD = 74*IN, 34*IN, 14*IN     # 1879.6 x 863.6 x 355.6. The plates stand on the floor: overall height = plate height
SHT = 1.25*IN                        # wood slab thickness 31.75 (Sabry)
TP = 4                               # plate sheet thickness (proposed)
SH = OH
NSH = 6; NCUT = 5
TOPF = OH - 25
BOTF = 25 + SHT
PITCH = (TOPF - BOTF)/(NSH-1)
SHELF_Z = [TOPF - PITCH*k for k in range(NSH)]      # slab top faces above the floor
FL = SHT                             # slab thickness (used for circle spacing)
SLW = SLH = 250
SLOT_OFF = FL + (PITCH - FL)/2
HOLE_U = [80, OD-80]                 # fixing holes, from the front edge of the plate
FHOLE_P = 6.5                        # plate hole
FHOLE_DROP = SHT/2                   # hole centre below the slab top face = middle of the slab thickness
INS_D, INS_DEPTH = 10.0, 25.0        # insert hole in the slab end (indicative): dia, depth
EDGE_R = 12.0                        # rounded front and rear long edges of the slab, like the reference (proposed)
SHEET_L, SHEET_W, GAP = 2500, 1250, 10
R_TOP = 10
PAD_W, STEP = 40, 3
WOOD_LIGHT, WOOD_DARK = '#C9A06A', '#4B3426'   # indicative swatches only, not brand colours

def sample(path, n=24):
    pts = []; N = len(path)
    for i in range(N):
        x0, y0, bu = path[i]; x1, y1, _ = path[(i+1) % N]
        pts.append((x0, y0))
        if abs(bu) > 1e-9:
            th = 4*math.atan(bu); c = math.hypot(x1-x0, y1-y0); rr = c/(2*math.sin(abs(th)/2))
            lx, ly = -(y1-y0)/c, (x1-x0)/c
            d = rr*math.cos(th/2); sg = 1 if th > 0 else -1
            cx, cy = (x0+x1)/2 + sg*lx*d, (y0+y1)/2 + sg*ly*d
            a_s = math.atan2(y0-cy, x0-cx)
            for k in range(1, n):
                a = a_s + th*k/n
                pts.append((cx+rr*math.cos(a), cy+rr*math.sin(a)))
    return pts
def stadium(cu, cy, w, h):
    r = w/2
    if w == h: return [(cu-r, cy, -1), (cu+r, cy, -1)]
    return [(cu-r, cy-(h/2-r), 0), (cu-r, cy+(h/2-r), -1), (cu+r, cy+(h/2-r), 0), (cu+r, cy-(h/2-r), -1)]


# ---------------- ITEM 1: side plate (flat, y up, y=0 is the bottom edge that stands on the floor) ----------------
PLATE_LEN = SH
def zy(z): return z
pa = [(0, 0, 0), (PAD_W, 0, 0), (PAD_W, STEP, 0), (OD-PAD_W, STEP, 0), (OD-PAD_W, 0, 0), (OD, 0, 0), (OD, SH-R_TOP, math.tan(math.pi/8)), (OD-R_TOP, SH, 0), (R_TOP, SH, math.tan(math.pi/8)), (0, SH-R_TOP, 0)]
SLOTS = [stadium(OD/2, SHELF_Z[k] - SLOT_OFF, SLW, SLH) for k in range(NCUT)]
HOLES_P = [(u, z - FHOLE_DROP) for z in SHELF_Z for u in HOLE_U]
plate_outline = Polygon(sample(pa))
circles = [Polygon(sample(s)) for s in SLOTS]
plate_net = plate_outline
for c in circles: plate_net = plate_net.difference(c)
for x, y in HOLES_P: plate_net = plate_net.difference(Point(x, y).buffer(FHOLE_P/2, 32))
assert plate_net.geom_type == 'Polygon' and len(plate_net.interiors) == NCUT + len(HOLES_P)
for i, cp in enumerate(circles):
    assert cp.bounds[1] - SHELF_Z[i+1] >= 30 - 1e-6, ('web below circle', i)
    assert (SHELF_Z[i] - FL) - cp.bounds[3] >= 30 - 1e-6, ('web above circle', i)
    for x, y in HOLES_P: assert cp.distance(Point(x, y)) >= 25, 'fixing hole too close to a circle'
assert SHELF_Z[-1] - FL >= 25 - 1e-6
GAP_TOP = SH - circles[0].bounds[3]; GAP_BOT = circles[-1].bounds[1]
assert abs(GAP_TOP - GAP_BOT) < 1e-6
PLATE_MASS = plate_net.area*TP*7.9e-6
PLATE_CUT = plate_outline.length + sum(p.length for p in circles) + len(HOLES_P)*math.pi*FHOLE_P
PLEN, PWID = PLATE_LEN, OD
TOTAL_STEEL = 2*PLATE_MASS
# ---------------- ITEM 2: wood slab (no flat pattern, made by a woodworker) ----------------
WS = OW - 2*TP                       # slab length between the plates, nominal
NEST1 = [('P1', 10, 10), ('P1', 10, 10+PWID+GAP)]
for kind, x, y in NEST1:
    assert x+PLEN <= SHEET_L-GAP+1e-6 and y+PWID <= SHEET_W-GAP+1e-6
print(f'plate flat {PLEN:.1f} x {PWID:.1f}, wood slab {WS:.1f} x {OD:.1f} x {SHT}, pitch {PITCH:.2f}, circle gaps {GAP_TOP:.1f} / {GAP_BOT:.1f}')
print(f'steel plates {PLATE_MASS:.1f} kg each, {TOTAL_STEEL:.1f} kg both; wood weight not calculated (species not given); plate cut length {PLATE_CUT/1000:.2f} m')

def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); d.layers.add('SHEET', color=3); d.layers.add('BEND', color=5, linetype='DASHED')
    return d
def plate_entities(msp, ox, oy, rot):
    T = (lambda x, y: (ox+y, oy+OD-x)) if rot else (lambda x, y: (ox+x, oy+y))
    msp.add_lwpolyline([(*T(x, y), 0, 0, b) for x, y, b in pa], format='xyseb', close=True, dxfattribs={'layer': 'CUT'})
    for s in SLOTS: msp.add_circle(T(s[0][0]+SLW/2, s[0][1]), SLW/2, dxfattribs={'layer': 'CUT'})
    for x, y in HOLES_P: msp.add_circle(T(x, y), FHOLE_P/2, dxfattribs={'layer': 'CUT'})
d = new_doc(); plate_entities(d.modelspace(), 0, 0, False); d.saveas(f'{OUT}/{PN}_rev{REV}_P1_side-plate.dxf')
d = new_doc(); m = d.modelspace()
m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
for kind, x, y in NEST1: plate_entities(m, x, y, True)
d.saveas(f'{OUT}/{PN}_rev{REV}_nest_sheet1_{SHEET_L}x{SHEET_W}.dxf')

# ---------------- SVG helpers ----------------
FONT = "DejaVu Sans, Inter, Arial, sans-serif"
INK, DIM, HID, FILL, FILL2 = '#161616', '#2a4a7a', '#7a7a7a', '#f1efe9', '#dcd9d0'
RED = '#b3261e'; STEEL = '#c9cbcc'; STEELD = '#9ea1a3'
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;')
def t(x, y, s, size=2.6, w=400, anchor='start', fill=INK, extra=''):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size}" font-weight="{w}" text-anchor="{anchor}" fill="{fill}"{extra}>{esc(s)}</text>'
def ar(x, y, s, size=2.6, w=400, fill=INK): return t(x, y, s, size, w, 'end', fill)
def bi(x, y, en, a, wd, size=2.6, w=400, fill=INK): return t(x, y, en, size, w, fill=fill) + t(x+wd, y+size*1.3, a, size, w, 'end', fill)
def line(x1, y1, x2, y2, sw=.3, col=INK, dash=None):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def rect(x, y, w, h, sw=.35, col=INK, fill='none', dash=None):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def poly(pts, sw=.35, col=INK, fill='none', dash=None):
    return '<polygon points="' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts) + f'" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def pathfill(shape, mapper, sw=.3, col=INK, fill='none', evenodd=True):
    d = ''
    rings = [shape.exterior] + list(shape.interiors)
    for r in rings:
        pts = [mapper(x, y) for x, y in r.coords]
        d += 'M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in pts) + ' Z '
    return f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"/>'
def circ(x, y, r, sw=.25, col=INK, fill='none', dash=None):
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def arrow(x, y, dx, dy):
    n = math.hypot(dx, dy); ux, uy_ = dx/n, dy/n
    return f'<polygon points="{x:.2f},{y:.2f} {x-ux*2+uy_*.7:.2f},{y-uy_*2-ux*.7:.2f} {x-ux*2-uy_*.7:.2f},{y-uy_*2+ux*.7:.2f}" fill="{DIM}"/>'
def dim_h(x1, x2, y, label, ext=None, above=True):
    s = line(x1, y, x2, y, .2, DIM) + arrow(x1, y, 1, 0) + arrow(x2, y, -1, 0)
    if ext is not None: s += line(x1, ext, x1, y+(2 if y > ext else -2), .15, DIM) + line(x2, ext, x2, y+(2 if y > ext else -2), .15, DIM)
    return s + t((x1+x2)/2, y-1, label, 2.2, 500, 'middle', DIM)
def dim_v(x, y1, y2, label, ext=None):
    s = line(x, y1, x, y2, .2, DIM) + arrow(x, y1, 0, 1) + arrow(x, y2, 0, -1)
    if ext is not None: s += line(ext, y1, x+(2 if x > ext else -2), y1, .15, DIM) + line(ext, y2, x+(2 if x > ext else -2), y2, .15, DIM)
    return s + f'<text transform="translate({x-1:.2f} {(y1+y2)/2:.2f}) rotate(-90)" font-family="{FONT}" font-size="2.2" font-weight="500" text-anchor="middle" fill="{DIM}">{esc(label)}</text>'
def balloon(x, y, n, r=3.0):
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="#fff" stroke="{INK}" stroke-width=".3"/>' + t(x, y+1.1, str(n), 3, 600, 'middle')
N = 5
def frame(n, title_en, title_ar, scale):
    s = rect(5, 5, 410, 287, .5) + rect(7, 7, 406, 283, .2)
    X, Y, Wd = 228, 247, 185
    s += rect(X, Y, Wd, 41, .4, fill='#fff')
    s += line(X, Y+9, X+Wd, Y+9, .25) + line(X, Y+20, X+Wd, Y+20, .25) + line(X, Y+31, X+Wd, Y+31, .25) + line(X+92, Y+9, X+92, Y+41, .25)
    s += bi(X+2, Y+4, f'{PN}   Tall shelf, six wood shelves', 'رف طويل بستة أرفف', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  74 x 34 x 14 in  ({OH:.1f} x {OW:.1f} x {OD:.1f} mm)', 'المقاس الكلي (سبري)', 88, 2.2) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.2)
    s += bi(X+2, Y+25, f'MATERIAL  Plates stainless {TP} mm, shelves solid wood', 'اللوحان ستانلس ٤ مم، الأرفف خشب', 88, 1.9) + bi(X+94, Y+25, 'FINISH  brushed steel / light wood or dark oak', 'ستانلس مصقول / خشب فاتح أو بلوط داكن', 88, 2.0)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.2) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.2)
    OKC = '#2f6b45'
    s += rect(X, Y-14, Wd, 12, .5, OKC, '#fff')
    s += t(X+Wd/2, Y-8.6, 'Approved by Sabry 15 Nov 2026. Production review pending. Not engineered', 2.25, 700, 'middle', OKC) + t(X+Wd/2, Y-3.8, 'اعتمده سبري ١٥ نوفمبر ٢٠٢٦. مراجعة التصنيع قيد الانتظار. غير مهندسة', 2.25, 700, 'middle', OKC)
    return s + t(10, 14, title_en, 4.2, 700) + ar(410, 14, title_ar, 4.2, 700)
def sheet(n, te, ta, sc, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, te, ta, sc)}{body}</svg>'
im = Image.open(ROOT + '/images/OBJ-159.jpg').convert('RGB').crop((0, 0, 735, 1100)); im.thumbnail((420, 420))
b_ = io.BytesIO(); im.save(b_, 'JPEG', quality=70); PHOTO = 'data:image/jpeg;base64,' + base64.b64encode(b_.getvalue()).decode()




def fmm(v): return f'{v:.1f}'
WOODN = 'Solid timber slab, light wood (oak) like the reference, or dark oak'
# ===== SHEET 1: views (1:12) =====
S = 1/12; ox, oy = 28, 38
def X(x): return ox + x*S
def Zf(z): return oy + (OH - z)*S
b = t(10, 24, 'FRONT, SIDE and PLAN, 1:12', 2.6, 600) + ar(226, 24, 'منظر أمامي وجانبي وعلوي', 2.6, 600)
b += t(ox, oy-3, 'FRONT', 2.2, 600)
b += rect(X(0), Zf(OH), TP*S, SH*S, .3, INK, STEELD) + rect(X(OW-TP), Zf(OH), TP*S, SH*S, .3, INK, STEELD)
for h in SHELF_Z: b += rect(X(TP), Zf(h), (OW-2*TP)*S, FL*S, .3, INK, '#c9a06a')
b += line(X(-8), Zf(0), X(OW+8), Zf(0), .4, INK)
sx0 = 128
def XS(u): return sx0 + u*S
b += t(sx0, oy-3, 'SIDE (outer face of a plate)', 2.2, 600)
def side_map(x, y): return (XS(OD - x), oy + (OH - y)*S)
b += pathfill(plate_net, side_map, .25, INK, STEEL)
for h in SHELF_Z: b += line(XS(0), Zf(h), XS(OD), Zf(h), .15, HID, '1.2 .8')
b += line(XS(-6), Zf(0), XS(OD+6), Zf(0), .4, INK)
b += dim_h(XS(0), XS(OD), Zf(0)+7, f'{fmm(OD)}', ext=Zf(0))
py = 226; ppx = 128
def XP(x): return ppx + x*S
b += t(ppx, py-3, 'PLAN (top shelf shown)', 2.2, 600)
b += rect(XP(0), py, OW*S, OD*S, .3, INK, '#c9a06a')
b += rect(XP(0), py, TP*S, OD*S, .3, INK, STEELD) + rect(XP(OW-TP), py, TP*S, OD*S, .3, INK, STEELD)
b += t(XP(OW)+2, py+2.2, 'rear', 1.8, 400, fill=HID) + t(XP(OW)+2, py+OD*S-.5, 'front', 1.8, 400, fill=HID)
b += dim_h(XP(0), XP(OW), py+OD*S+6, f'{fmm(OW)}', ext=py+OD*S) + dim_v(XP(0)-6, py, py+OD*S, f'{fmm(OD)}', ext=XP(0))
b += dim_v(ox-8, Zf(OH), Zf(0), f'{fmm(OH)} overall', ext=ox)
b += dim_h(X(0), X(OW), Zf(0)+7, f'{fmm(OW)}', ext=Zf(0))
for h in SHELF_Z:
    b += line(X(OW)+1, Zf(h), X(OW)+5, Zf(h), .15, DIM) + t(X(OW)+6, Zf(h)+.7, f'{fmm(h)}', 1.8, 400, fill=DIM)
b += t(X(OW)+6, Zf(OH)-2.5, 'shelf tops', 1.6, 400, fill=HID) + t(X(OW)+6, Zf(OH)-.6, 'above floor', 1.6, 400, fill=HID)
b += balloon(X(OW/2), Zf(SHELF_Z[2]-FL/2), 2) + balloon(XS(OD*.18), Zf(1500), 1) + balloon(X(OW/2), Zf(SHELF_Z[0]-FL/2), 3)
kx = 168
b += t(kx, 40, 'KEY SIZES (Sabry unless noted)', 2.2, 600) + ar(226, 44, 'المقاسات الرئيسية', 2.0, 600)
ks = ['Overall 74 x 34 x 14 in (H x W x D)', f'= {fmm(OH)} x {fmm(OW)} x {fmm(OD)} mm', 'Plates stand on two 40 mm pads cut in the bottom edge',
      f'6 wood shelves, 1.25 in = {SHT} mm thick, pitch {fmm(PITCH)}', f'5 circles dia {SLW} per plate, one per bay', 'Shelves screwed to the plates, 4 screws per level',
      f'Plates {TP} mm stainless (proposed). Shelves solid wood', f'Steel plates only about {TOTAL_STEEL:.0f} kg; wood weight not calculated', f'Bottom shelf top face {fmm(SHELF_Z[-1])} above floor', 'Tip-over: wall strap (item 5) on the top shelf rear edge']
for i, s_ in enumerate(ks): b += t(kx, 50 + i*4.3, s_, 1.8, 400)
rx = 238; ih = 150; wimg = ih*im.size[0]/im.size[1]
b += t(rx, 22, 'REFERENCE (idea only, third-party piece)', 2.4, 600) + ar(410, 22, 'المرجع (للفكرة فقط)', 2.4, 600)
b += f'<image x="{rx}" y="25" width="{wimg:.1f}" height="{ih:.1f}" href="{PHOTO}"/>' + rect(rx, 25, wimg, ih, .25, HID)
tx_ = rx + wimg + 4
for i, s_ in enumerate(["Another designer's piece. We keep the idea only:", 'two tall side plates with cut-outs, solid wood', 'slab shelves between, as in the photo.', 'Plates stand on the floor edge as in the reference.', 'Our own size, six shelves, five circles per', 'plate (Sabry, 12 Nov).']):
    b += t(tx_, 32 + i*4, s_, 1.7, 400, fill=HID)
cy0 = 25 + ih + 9
b += t(rx, cy0, 'COLOURWAYS', 2.6, 600) + ar(410, cy0, 'التشطيبات', 2.6, 600)
b += rect(rx, cy0+3, 22, 10, .3, INK, '#b8b8b4') + t(rx+25, cy0+7, 'Plates: brushed stainless steel (Sabry)', 2.1, 600) + t(rx+25, cy0+10.5, 'Same family as OBJ-190. Swatch indicative.', 1.7, 400, fill=HID)
b += rect(rx, cy0+16, 22, 10, .3, INK, WOOD_LIGHT) + t(rx+25, cy0+20, 'Shelves option 1: light wood (oak), like the reference (Sabry)', 2.1, 600) + t(rx+25, cy0+23.5, f'Oak. Finish to confirm. Swatch {WOOD_LIGHT}, indicative.', 1.7, 400, fill=HID)
b += rect(rx, cy0+29, 22, 10, .3, INK, WOOD_DARK) + t(rx+25, cy0+33, 'Shelves option 2: dark oak (Sabry)', 2.1, 600) + t(rx+25, cy0+36.5, f'Finish to confirm. Swatch {WOOD_DARK}, indicative.', 1.7, 400, fill=HID)
sh1 = sheet(1, 'VIEWS', 'المناظر', '1:12', b)

# ===== SHEET 2: parts =====
b = t(10, 22, 'ITEM 1  SIDE PLATE, flat pattern, 1:10   (quantity 2, identical)', 2.6, 600) + ar(410, 22, 'بند ١، اللوح الجانبي، الشكل المفرود، العدد ٢', 2.6, 600)
S2 = .1; px0, py0 = 34, 28
def MPL(x, y): return (px0 + y*S2, py0 + (OD - x)*S2)
b += pathfill(plate_net, MPL, .3, INK, STEEL)
b += dim_h(px0, px0+PLEN*S2, py0+OD*S2+6, f'{PLEN:.1f}', ext=py0+OD*S2) + dim_v(px0-6, py0, py0+OD*S2, f'{fmm(OD)}', ext=px0)
b += t(px0, py0+OD*S2+13, f'Left edge (y = 0) is the bottom edge that stands on the floor; right edge is the top, corners R{R_TOP}. Thickness {TP}. Flat, no folds.', 1.8, 400, fill=HID)
b += t(px0, py0+OD*S2+16.6, f'12 fixing holes {FHOLE_P} dia, 5 circles dia {SLW}. Bottom edge: {STEP} mm step, two {PAD_W} mm contact pads (proposed). Edge break is Production\'s.', 1.8, 400, fill=HID)
b += ar(256, py0+OD*S2+24, 'الحافة السفلية: درجة ٣ مم تترك قاعدتين للارتكاز بطول ٤٠ مم. بلا أقدام.', 1.8, 400, HID)
b += balloon(px0+PLEN*S2*.5, py0+OD*S2*.5, 1)
D5 = .2; bx0, by0 = 28, 112
b += t(10, 100, 'BAY DETAIL, one bay of the plate, 1:5 (outer face)', 2.4, 600) + ar(122, 100, 'تفصيل مستوى واحد', 2.4, 600)
zb = SHELF_Z[2]
def MB(u, z): return (bx0 + (OD - u)*D5, by0 + (zb + 40 - z)*D5)
WH = PITCH + 40
b += rect(bx0, by0, OD*D5, WH*D5, .3, INK, STEEL)
cu, cz = OD/2, zb - SLOT_OFF
b += poly([MB(x, y) for x, y in sample(stadium(cu, cz, SLW, SLH))], .3, INK, '#fff')
for u in HOLE_U: b += circ(*MB(u, zb - FHOLE_DROP), FHOLE_P/2*D5, .3, INK, '#fff')
b += line(*MB(0, zb), *MB(OD, zb), .2, HID, '2 1') + t(bx0+OD*D5+2, MB(0, zb)[1]+.8, 'shelf top face', 1.7, 400, fill=HID)
b += line(*MB(0, zb-FL), *MB(OD, zb-FL), .2, HID, '2 1') + t(bx0+OD*D5+2, MB(0, zb-FL)[1]+.8, 'shelf underside', 1.7, 400, fill=HID)
yb_ = by0 + WH*D5
b += dim_h(MB(OD, zb)[0], MB(0, zb)[0], by0-4, f'{fmm(OD)}', ext=by0)
b += dim_h(MB(HOLE_U[0], zb)[0], MB(0, zb)[0], yb_+5, f'{HOLE_U[0]}', ext=yb_) + dim_h(MB(OD, zb)[0], MB(HOLE_U[1], zb)[0], yb_+5, f'{fmm(OD-HOLE_U[1])}', ext=yb_)
b += dim_v(bx0-5, MB(0, zb)[1], MB(0, zb-FHOLE_DROP)[1], f'{FHOLE_DROP:.1f}', ext=bx0) + dim_v(bx0-11, MB(0, zb)[1], MB(0, cz)[1], f'{fmm(SLOT_OFF)} to circle centre', ext=bx0)
b += dim_h(MB(cu+SLW/2, cz)[0], MB(cu-SLW/2, cz)[0], MB(cu, cz)[1]+SLH*D5/2+5, f'{SLW}', ext=MB(cu, cz)[1]+SLH*D5/2)
b += t(10, yb_+12, f'Fixing holes {FHOLE_P} dia, two per shelf level, {FHOLE_DROP:.1f} below the shelf top face (middle of the slab), {HOLE_U[0]} from the front and rear edges.', 1.8, 400, fill=HID)
b += ar(122, yb_+16, 'ثقبان لكل مستوى رف في منتصف سماكة الرف.', 1.8, 400, HID)
# wood slab
sx_, sy_ = 128, 112
b += t(sx_-2, 100, f'ITEM 2  WOOD SHELF, solid slab {SHT} thick (qty 5)   ITEM 3  TOP SHELF (qty 1)', 2.1, 600) + ar(410, 100, 'بند ٢ الرف الخشبي، بند ٣ الرف العلوي', 2.1, 600)
SS = .2
b += rect(sx_, sy_, WS*SS, OD*SS, .3, INK, '#c9a06a')
b += t(sx_+2, sy_+OD*SS/2, 'PLAN, 1:5', 1.8, 600, fill=INK)
for u in HOLE_U:
    for xe in (0, WS):
        b += circ(sx_+xe*SS + (3 if xe == 0 else -3), sy_+u*SS, INS_D*SS/2+.6, .25, RED, '#fff')
b += dim_h(sx_, sx_+WS*SS, sy_+OD*SS+6, f'{fmm(WS)} between plates', ext=sy_+OD*SS) + dim_v(sx_-6, sy_, sy_+OD*SS, f'{fmm(OD)}', ext=sx_)
b += t(sx_+WS*SS/2-26, sy_+3.8, 'item 3 only: 2 strap pilot holes dia 5 in the rear edge', 1.5, 400, fill=HID)
# end section at 1:1 scale reduced to 2:1? use 2:1
ex, ey = 128, 203; E2 = 2.0
b += t(ex-2, ey-6, 'END SECTION, about 0.45:1', 2.1, 600) + ar(332, ey-6, 'مقطع طرفي', 2.1, 600)
sw_ = OD*E2*.2    # scale 2:1 on a 1:5 sheet is too big: draw at 0.5:1 instead
EP = .45
w_ = OD*EP; h_ = SHT*EP; rr = EDGE_R*EP
b += f'<path d="M{ex+rr:.2f},{ey:.2f} L{ex+w_-rr:.2f},{ey:.2f} Q{ex+w_:.2f},{ey:.2f} {ex+w_:.2f},{ey+rr:.2f} L{ex+w_:.2f},{ey+h_-rr:.2f} Q{ex+w_:.2f},{ey+h_:.2f} {ex+w_-rr:.2f},{ey+h_:.2f} L{ex+rr:.2f},{ey+h_:.2f} Q{ex:.2f},{ey+h_:.2f} {ex:.2f},{ey+h_-rr:.2f} L{ex:.2f},{ey+rr:.2f} Q{ex:.2f},{ey:.2f} {ex+rr:.2f},{ey:.2f} Z" fill="#c9a06a" stroke="{INK}" stroke-width=".3"/>'
b += t(ex-1, ey-1.5, 'front', 1.6, 400, fill=HID) + t(ex+w_+1, ey-1.5, 'rear', 1.6, 400, fill=HID, extra='')
b += dim_h(ex, ex+w_, ey+h_+6, f'{fmm(OD)}', ext=ey+h_) + dim_v(ex-6, ey, ey+h_, f'{SHT}', ext=ex) + t(ex+w_+4, ey+h_/2+.6, f'long edges R{EDGE_R:.0f} (proposed)', 1.7, 400, fill=HID)
b += t(sx_, ey+h_+13, f'Wood species, grain direction, joins and finish are for the woodworker. Light wood or dark oak (Sabry). Insert holes (red) dia {INS_D:.0f}, {INS_DEPTH:.0f} deep in each slab end, centre {HOLE_U[0]} from front/rear and {SHT/2:.1f} from top.', 1.7, 400, fill=HID)
b += ar(330, ey+h_+9.5, 'الخشب: النوع والتجميع والتشطيب من النجار.', 1.8, 400, HID)
cdx, cdy = 332, 150
b += t(cdx-2, 124, 'BOTTOM EDGE, corner, 1:1', 2.1, 600) + ar(410, 124, 'الحافة السفلية، ١:١', 2.1, 600)
b += poly([(cdx, cdy-20), (cdx, cdy), (cdx+PAD_W, cdy), (cdx+PAD_W, cdy-STEP), (cdx+60, cdy-STEP), (cdx+60, cdy-20)], .35, INK, STEEL)
b += line(cdx-6, cdy, cdx+66, cdy, .4, INK) + t(cdx+62, cdy+3, 'floor', 1.7, 400, fill=HID)
b += dim_h(cdx, cdx+PAD_W, cdy+7, f'{PAD_W}', ext=cdy) + dim_v(cdx+66, cdy-STEP, cdy, f'{STEP}', ext=cdx+60)
tbx = 262
rows = [('Plate finished mm', f'{fmm(OD)} x {fmm(SH)} x {TP}'), ('Plate flat mm', f'{PLEN:.1f} x {PWID:.1f} x {TP}'), ('Plate steel mass', f'{PLATE_MASS:.1f} kg'), ('Shelf finished mm', f'{fmm(WS)} x {fmm(OD)} x {SHT}'),
        ('Shelf wood weight', 'not calculated'), ('Plate cut length', f'{PLATE_CUT/1000:.2f} m'), ('Steel total (2 plates)', f'about {TOTAL_STEEL:.0f} kg')]
b += t(tbx, 32+0, 'DATA', 2.6, 600) + ar(410, 32, 'بيانات', 2.6, 600)
for i, (k, v) in enumerate(rows):
    yy = 39 + i*5.6
    b += line(tbx, yy+1.8, 410, yy+1.8, .15, HID) + t(tbx+1, yy, k, 2.0) + t(409, yy, v, 2.0, 600, 'end')
b += t(tbx, 80, 'Steel mass is arithmetic from the drawing (7.9 g/cm3), not a Production figure.', 1.7, 400, fill=HID)
sh2 = sheet(2, 'PART SHEET', 'ورقة الأجزاء', '1:10 / 1:5', b)

# ===== SHEET 3: assembly =====
b = t(10, 22, 'EXPLODED VIEW (oblique, about 1:12)', 2.6, 600) + ar(410, 22, 'منظر مفكك', 2.6, 600)
S3 = 1/12; ax0, ay0 = 42, 36; K3 = .32; E = 170
def P3(x, y, z): return (ax0 + (x + K3*y*.9)*S3, ay0 + (OH - z - K3*y*.55)*S3)
def plate3(xoff):
    out = poly([P3(xoff, 0, 0), P3(xoff, OD, 0), P3(xoff, OD, OH), P3(xoff, 0, OH)], .35, INK, STEEL)
    for h in SHELF_Z[:NCUT]:
        out += poly([P3(xoff, u, zz) for u, zz in sample(stadium(OD/2, h - SLOT_OFF, SLW, SLH))], .25, INK, '#fff')
    return out
b += plate3(-E)
for h in SHELF_Z:
    b += poly([P3(TP, 0, h), P3(OW-TP, 0, h), P3(OW-TP, OD, h), P3(TP, OD, h)], .3, INK, '#d8b27c')
    b += poly([P3(TP, 0, h), P3(OW-TP, 0, h), P3(OW-TP, 0, h-FL), P3(TP, 0, h-FL)], .3, INK, '#c9a06a')
b += plate3(OW - TP + E)
for h in (SHELF_Z[0], SHELF_Z[-1]):
    for u in HOLE_U:
        b += line(*P3(TP, u, h-FHOLE_DROP), *P3(-E, u, h-FHOLE_DROP), .2, DIM, '1.5 1') + line(*P3(OW-TP, u, h-FHOLE_DROP), *P3(OW-TP+E, u, h-FHOLE_DROP), .2, DIM, '1.5 1')
b += balloon(*P3(-E, OD*.5, 1300), 1) + balloon(*P3(OW/2, OD*.5, SHELF_Z[2]), 2) + balloon(*P3(OW/2, OD*.5, SHELF_Z[0]), 3) + balloon(*P3(OW-TP+E, OD*.5, 1000), 1)
b += t(10, 222, 'Plates apart, wood shelves in place. Dashed blue lines: the insert holes in the top and bottom slab ends lining up with the plate holes. Shelves 2 to 5 fix the same way.', 1.8, 400, fill=HID)
b += t(10, 226, 'The plates stand on their own bottom edge on the floor (no feet). The wall strap (item 5) fixes to the rear edge of the top shelf.', 1.8, 400, fill=HID)
b += ar(225, 222, 'الخطوط المتقطعة: محاذاة ثقوب التثبيت.', 1.8, 400, HID)
dx0, dy0 = 245, 44; D = 4
b += t(dx0-2, 32, 'FIXING DETAIL, section through a shelf end, 4:1 (schematic)', 2.2, 600) + ar(410, 32, 'تفصيل التثبيت (تخطيطي)', 2.2, 600)
b += rect(dx0, dy0, TP*D, 44, .35, INK, STEEL) + rect(dx0+TP*D, dy0+6, 30, 28, .35, INK, '#c9a06a')
cyd = dy0+6+28/2
b += rect(dx0-3.5, cyd-1.6, 3.5, 3.2, .3, INK, '#666') + rect(dx0+TP*D, cyd-INS_D*D*.1, INS_DEPTH*D*.35, INS_D*D*.2, .3, INK, '#888')
b += line(dx0-6, cyd, dx0+TP*D+INS_DEPTH*D*.35+4, cyd, .2, DIM, '2 1')
b += t(dx0+TP*D+38, cyd+.8, 'M6 screw into M6 threaded insert (indicative)', 1.7, 400, fill=DIM) + t(dx0+TP*D+38, cyd+4, 'Woodworker and Production decide.', 1.7, 400, fill=HID)
b += t(dx0-2, dy0-3, f'plate {TP}', 1.7, 400, fill=HID) + t(dx0+TP*D+2, dy0+3.5, f'wood slab {SHT} thick (section schematic)', 1.7, 400, fill=HID)
sq0 = 120
b += t(245, sq0, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + ar(410, sq0, 'تسلسل التجميع (مقترح)', 2.6, 600)
steps = [('Cut and finish the plates. Make and finish the wood slabs, fit the M6 inserts.', 'قص اللوحين وتشطيبهما وتجهيز الأرفف الخشبية.'),
         ('Lay one plate flat, outer face down.', 'ضع لوحاً مسطحاً بوجهه الخارجي للأسفل.'),
         ('Stand the slabs on it, holes to holes. Four screws per shelf level.', 'ثبّت كل مستوى رف بأربعة براغٍ.'),
         ('Fit the second plate and its screws. Stand up with two people.', 'ركّب اللوح الثاني ثم أقم القطعة بشخصين.'),
         ('Check it stands on both pads. Fix the strap to the wall.', 'تأكد من ارتكازها على القاعدتين وثبّت الحزام.')]
for i, (en, a) in enumerate(steps):
    yy = sq0 + 8 + i*8
    b += balloon(248, yy-1, i+1, 2.4) + t(254, yy, en, 1.9) + ar(410, yy+3.6, a, 1.9)
b += t(245, sq0+50, "Screw torque and wood treatment are not specified here. Nothing here claims strength or stability.", 1.8, 400, fill=HID)
sh3 = sheet(3, 'ASSEMBLY', 'التجميع', '1:12 / detail', b)

# ===== SHEET 4: cutting layout =====
S4 = .05; ox4, oy4 = 22, 40
s = t(ox4, oy4-2.5, f'SHEET A, {TP} mm stainless: 2 x item 1', 2.0, 600) + ar(ox4+SHEET_L*S4, oy4-2.5, 'اللوح أ', 2.0, 600)
s += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .4, '#2f6b45', '#fbfaf6')
for kind, x, y in NEST1:
    s += pathfill(plate_net, lambda xx, yy, x=x, y=y: (ox4+(x+yy)*S4, oy4+(SHEET_W-(y+OD-xx))*S4), .15, INK, FILL)
    s += t(ox4+(x+PLEN/2)*S4, oy4+(SHEET_W-(y+OD/2))*S4+1.2, '1', 3.0, 600, 'middle', '#555')
s += dim_h(ox4, ox4+SHEET_L*S4, oy4+SHEET_W*S4+4.5, f'{SHEET_L}', ext=oy4+SHEET_W*S4) + dim_v(ox4-5, oy4, oy4+SHEET_W*S4, f'{SHEET_W}', ext=ox4)
b = t(10, 22, f'One assumed sheet {SHEET_L} x {SHEET_W} x {TP}. Only the two plates are laser cut. The shelves are timber and are not nested.', 2.1, 600) + ar(410, 22, 'لوح واحد مفترض للقص، اللوحان فقط', 2.1, 600) + s
tx0 = 160
b += t(tx0, 44, 'SHEET A', 2.4, 600) + t(tx0, 49, f'2 plates, {GAP} mm spacing, long side along the sheet length', 1.9) + t(tx0, 53, f'(grain), cutting length {2*PLATE_CUT/1000:.2f} m. Most of the sheet is free.', 1.9)
b += t(tx0, 64, 'Not optimised. No offcut use is claimed.', 1.8, 400, fill=HID)
b += t(10, 150, 'WOOD CUTTING LIST (for the woodworker, not nested)', 2.6, 600) + ar(410, 150, 'قائمة الخشب', 2.6, 600)
b += t(10, 158, f'6 slabs, each about {fmm(WS)} x {fmm(OD)} x {SHT} mm finished (length is nominal, between the plates). Long edges R{EDGE_R:.0f}. One piece or glued boards: the woodworker decides.', 2.0)
b += t(10, 163, f'Light wood or dark oak (Sabry). Light wood is oak (Sabry). M6 insert holes dia {INS_D:.0f} x {INS_DEPTH:.0f} deep in both ends of every slab (4 per slab).', 2.0)
b += t(10, 168, 'The top slab (item 3) also gets 2 strap pilot holes dia 5 in its rear edge (indicative).', 2.0)
b += ar(410, 158, 'ستة ألواح خشب، النوع غير محدد.', 2.0)
sh4 = sheet(4, 'CUTTING LAYOUT', 'مخطط القص', '1:20', b)

# ===== SHEET 5: BOM and notes =====
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + ar(410, 28, 'قائمة المواد', 2.8, 600) + rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 130, 150], ['ITEM', 'PART / الجزء', 'QTY', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Side plate, laser cut, flat, stands on its bottom edge', 'لوح جانبي', '2', f'Stainless steel sheet {TP} mm, brushed (proposed)'),
       ('2', f'Shelf, solid wood slab {SHT} thick, R{EDGE_R:.0f} long edges, M6 inserts in the ends', 'رف خشبي', '5', 'Solid oak: light wood or dark oak (Sabry); finish to confirm'),
       ('3', 'Top shelf (item 2 + 2 strap pilot holes in the rear edge)', 'الرف العلوي', '1', 'Solid wood, same as item 2'),
       ('4', 'Screw M6 button head + M6 threaded insert (indicative)', 'برغي وقلاووظ داخلي', '24', 'Stainless screw, insert bought in'),
       ('5', 'Anti-tip wall strap kit', 'حزام منع السقوط', '1', 'Bought in, wall fixings by the installer')]
for i, (n_, en, a, q, m) in enumerate(bom):
    yy = 44 + i*6.2
    b += line(10, yy+2, 410, yy+2, .15, HID) + t(12, yy, n_, 2.3) + t(24, yy, en, 2.2) + ar(128, yy, a, 2.2) + t(130, yy, q, 2.2) + t(150, yy, m, 2.2)
b += t(10, 82, 'NOTES', 2.8, 600) + ar(410, 82, 'ملاحظات', 2.8, 600)
notes = [("Sabry (12 and 15 Nov 2026): overall 74 x 34 x 14 in, shelves 1.25 in thick and screwed to the plates, six shelves, five circles per plate, no feet (plates stand on two 40 mm pads, 3 mm step between), plates brushed stainless, shelves WOOD SLABS like the reference: light wood or dark oak. All other sizes are PROPOSED by Claude, to confirm.", 'المقاسات من سبري: الأرفف ألواح خشب، واللوحان ستانلس، والباقي مقترح.'),
         ('The reference photo is another designer\'s piece. We keep the idea only (two tall plates with cut-outs, wood slabs between, plates standing on the floor edge). Our count, size and proportions are different.', 'المرجع قطعة مصمم آخر. نأخذ الفكرة فقط.'),
         ('Plate thickness, tolerances, sheet size, edge treatment and finish are Production\'s. The wood species, grain, joins, edge radius, insert type and finish are the woodworker\'s. Who makes the timber is not decided (Polycraft works sheet metal).', 'السماكة والسماحيات يقررها التصنيع، والخشب يقرره النجار.'),
         (f'Steel plates alone are about {TOTAL_STEEL:.0f} kg (arithmetic). Wood weight is not calculated (dark oak finish to confirm). Lifting, packing and the 15 kg shipping band need real figures. Ships in parts, assembled on site.', f'وزن اللوحين نحو {TOTAL_STEEL:.0f} كجم، ووزن الخشب غير محسوب.'),
         ('Tip-over: the wall strap (item 5) is part of the design. No levelling feet, so an uneven floor is for Production and the installer to consider. No claim about stability or shelf loading. Not engineered.', 'حزام الحائط جزء من التصميم. لا ادعاءات عن الثبات أو التحميل.'),
         ('Plates brushed stainless (same family as OBJ-190). No costs or prices on this drawing. Arabic wording is a draft for a technical reader.', 'لا أسعار. الصياغة العربية مسودة.')]
for i, (en, a) in enumerate(notes):
    yy = 92 + i*14
    cut = 150 if len(en) > 150 else len(en)
    l1 = en[:cut].rsplit(' ', 1)[0] if len(en) > 150 else en
    rest = en[len(l1):].strip()
    b += t(12, yy, f'{i+1}.', 2.3, 600) + t(18, yy, l1, 2.1)
    if rest:
        l2 = rest[:150].rsplit(' ', 1)[0] if len(rest) > 150 else rest
        b += t(18, yy+4, l2, 2.1)
        if len(rest) > len(l2): b += t(18, yy+8, rest[len(l2):].strip(), 2.1)
    b += ar(410, yy, a, 2.1)
sh5 = sheet(5, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)
for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1): open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('written')
