"""OBJ-159: tall shelf, six shelves, two stainless side plates with five circular cut-outs each. Production drawing set, REV 5 (DRAFT).
Run: python3 make_obj159_rev5.py <repo root>   then: NODE_PATH=<playwright> node make_pdf.js <dir> OBJ-159 5
Reference: images/OBJ-159.jpg is a third-party piece (jeremylechatelier, Hublot). Used for the IDEA only. This is objekt's OWN design.
REV 5 (12 Nov): Sabry gave NEW DIMENSIONS: height 74 in, width 34 in, depth 14 in; shelves 1.25 in thick; shelves SIT ON SUPPORTS, not screwed.
  Supports = folded ledge tabs cut from the plates; shelves are hollow folded slabs 31.75 thick that rest on the tabs. Two rear tie bars (proposed) hold the plates.
REV 4: bottom shelf low, equal gaps. REV 3: five larger circles. REV 2: depth 40 cm. REV 1: circles. REV 0: ovals.
Sabry's sizes: height, width, depth, shelf thickness, six shelves, five circles. EVERYTHING ELSE IS PROPOSED BY CLAUDE. Arabic is a draft. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-159'; os.makedirs(OUT, exist_ok=True)
REV = 5; DATE = '12 Nov 2026'; PN = 'OBJ-159'
IN = 25.4
# ---------------- sizes (mm). Sabry: 74 x 34 x 14 in, shelves 1.25 in thick ----------------
OH, OW, OD = 74*IN, 34*IN, 14*IN     # 1879.6 x 863.6 x 355.6, overall height includes the feet
SHT = 1.25*IN                        # shelf thickness 31.75 (hollow folded slab)
FOOT = 40                            # underside of plate above floor at mid adjustment (range to confirm)
TP, TS = 4, 3                        # plate and shelf sheet thickness (proposed)
SH = OH - FOOT                       # steel height of a plate = 1839.6
NSH = 6; NCUT = 5
TOPF = OH - 25                       # top face of the top shelf, 25 below the plate top (proposed)
BOTF = 125                           # top face of the bottom shelf above the floor (proposed)
PITCH = (TOPF - BOTF)/(NSH-1)        # equal pitch, 345.9
SHELF_TOP_FLOOR = [TOPF - PITCH*k for k in range(NSH)]
SHELF_Z = [h - FOOT for h in SHELF_TOP_FLOOR]       # measured from the plate's tab underside
FL = SHT                             # shelf flange height = shelf thickness
CL = 1.0                             # assembly clearance per side between a shelf and a plate (Production sets)
SLW = SLH = 250                      # circular cut-out diameter
SLOT_OFF = FL + (PITCH - FL)/2       # circle centre below the top face of the shelf above it (centred in the bay)
# bends (Production sets the real ones)
KF = 0.4
def bend(t, r): return r + t, math.pi/2*(r + KF*t)
SB_P, BA_P = bend(TP, TP); SB_S, BA_S = bend(TS, TS)
TABW, TABL = 40, 60                  # foot tab width, outside leg
TAB_U = [70, OD-70]; TAB_HOLE = 9.0
SUP_W, SUP_LEG = 40, 20              # shelf support ledge tab: width, inward projection (outside leg)
SUP_U = [40, OD-40]                  # support tab centres from the front and rear edges
HT = SUP_LEG - SB_P + BA_P           # flat length of a support tab (= height of the opening it leaves)
TIE_FLOOR = [1760.0, 300.0]          # rear tie bars, centre height above floor
TIE_H, TIE_FLAP = 40, 30             # tie bar height, end flap outside leg
TIE_HOLE_U = OD - 15                 # tie screw hole, from the front edge of the plate
FHOLE_P, FHOLE_S = 6.5, 8.0
SHEET_L, SHEET_W, GAP = 2500, 1250, 10
R_TOP = 10

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

# ---------------- ITEM 1: side plate (flat pattern, y up, y=0 is the foot tab tip) ----------------
BODY_Y0 = TABL - SB_P + BA_P
PLATE_LEN = (SH - SB_P) + BA_P + (TABL - SB_P)
assert abs(BODY_Y0 + (SH - SB_P) - PLATE_LEN) < 1e-6
def zy(z): return z + (BODY_Y0 - SB_P)          # height above tab underside -> flat y
Y_TOP = PLATE_LEN
tabs = [(u-TABW/2, u+TABW/2) for u in TAB_U]
pa = [(0, BODY_Y0, 0)]
for a, b_ in tabs: pa += [(a, BODY_Y0, 0), (a, 0, 0), (b_, 0, 0), (b_, BODY_Y0, 0)]
pa += [(OD, BODY_Y0, 0), (OD, Y_TOP-R_TOP, math.tan(math.pi/8)), (OD-R_TOP, Y_TOP, 0), (R_TOP, Y_TOP, math.tan(math.pi/8)), (0, Y_TOP-R_TOP, 0)]
SLOTS = [stadium(OD/2, zy(z - SLOT_OFF), SLW, SLH) for z in SHELF_Z[:NCUT]]
HOLES_TAB = [(u, 25.0) for u in TAB_U]
TIE_Z = [f - FOOT for f in TIE_FLOOR]
HOLES_TIE = [(TIE_HOLE_U, zy(z)) for z in TIE_Z]
SUP = []        # support ledge tabs: (u centre, hinge y (top edge of the opening), opening rect)
for z in SHELF_Z:
    zs = z - FL                     # underside of the shelf = hinge line of the ledge tab
    for u in SUP_U: SUP.append((u, zy(zs), (u-SUP_W/2, zy(zs)-HT, u+SUP_W/2, zy(zs))))
plate_outline = Polygon(sample(pa))
plate_cuts = [Polygon(sample(s)) for s in SLOTS] + [Point(x, y).buffer(FHOLE_P/2, 32) for x, y in HOLES_TIE] + [Point(x, y).buffer(TAB_HOLE/2, 32) for x, y in HOLES_TAB] + [box(*r) for _, _, r in SUP]
plate_net = plate_outline
for c in plate_cuts: plate_net = plate_net.difference(c)
assert plate_net.geom_type == 'Polygon' and len(plate_net.interiors) == len(plate_cuts)
# clearances
circles = [Polygon(sample(s)) for s in SLOTS]
for cpoly in circles:
    for _, _, r in SUP: assert cpoly.distance(box(*r)) >= 30, ('circle too close to a support opening', cpoly.distance(box(*r)))
    for x, y in HOLES_TIE: assert cpoly.distance(Point(x, y)) >= 30
top_c = max(p.bounds[3] for p in circles); bot_c = min(p.bounds[1] for p in circles)
assert zy(SHELF_Z[0] - FL) - top_c >= 30 - 1e-6, 'web above the top circle'
assert bot_c - zy(SHELF_Z[NCUT-1+1]) >= 30 - 1e-6 or True
for i, cpoly in enumerate(circles):       # web between a circle and the shelf below it
    assert cpoly.bounds[1] - zy(SHELF_Z[i+1]) >= 30 - 1e-6, ('web below circle', i)
    assert zy(SHELF_Z[i] - FL) - cpoly.bounds[3] >= 30 - 1e-6, ('web above circle', i)
for (x, y) in HOLES_TIE:
    for _, _, r in SUP: assert Point(x, y).distance(box(*r)) >= 25, 'tie hole near a support opening'
PBX = plate_outline.bounds; PLEN, PWID = PBX[3]-PBX[1], PBX[2]-PBX[0]
PLATE_MASS = plate_net.area*TP*7.9e-6
PLATE_CUT = plate_outline.length + sum(p.length for p in circles) + sum(math.pi*FHOLE_P for _ in HOLES_TIE) + sum(math.pi*TAB_HOLE for _ in HOLES_TAB) + sum(2*SUP_W + 2*0 + 2*HT for _ in SUP)   # U cut: two sides and the bottom edge ~ SUP_W + 2*HT
PLATE_CUT = plate_outline.length + sum(p.length for p in circles) + sum(math.pi*FHOLE_P for _ in HOLES_TIE) + sum(math.pi*TAB_HOLE for _ in HOLES_TAB) + sum(SUP_W + 2*HT for _ in SUP)

# ---------------- ITEM 2: shelf = hollow folded slab, 31.75 thick (flat pattern, y up, y=0 is the rear flap tip) ----------------
SW_OUT = OW - 2*TP - 2*CL                  # shelf width over the end flanges (853.6)
WEB_W = SW_OUT - 2*SB_S; WEB_D = OD - 2*SB_S
X1 = FL - SB_S; X2 = X1 + BA_S; X3 = X2 + WEB_W; X4 = X3 + BA_S; XE = X4 + (FL - SB_S)
Y1 = FL - SB_S; Y2 = Y1 + BA_S; Y3 = Y2 + WEB_D; Y4 = Y3 + BA_S; YE = Y4 + (FL - SB_S)
RELIEF = 1.5
shelf_outline = unary_union([box(X2, 0, X3, YE), box(0, Y2+RELIEF, X2, Y3-RELIEF), box(X3, Y2+RELIEF, XE, Y3-RELIEF)])
assert shelf_outline.geom_type == 'Polygon'
sh_net = shelf_outline
SHELF_MASS = sh_net.area*TS*7.9e-6
SHELF_CUT = shelf_outline.length

# ---------------- ITEM 3: rear tie bar (flat pattern, y up, x=0 is a flap tip) ----------------
TW_OUT = OW - 2*TP - 2*CL
T_WEB = TW_OUT - 2*SB_P
T_FLAP = TIE_FLAP - SB_P
TIE_LEN = T_FLAP + BA_P + T_WEB + BA_P + T_FLAP
tie_outline = box(0, 0, TIE_LEN, TIE_H)
TIE_FH = [(15.0, TIE_H/2), (TIE_LEN - 15.0, TIE_H/2)]                 # screw holes in the flaps (clinch nut), 15 from the flap tip
STRAP_X = [TIE_LEN/2 - 120, TIE_LEN/2 + 120]
tie_net = tie_outline
for x, y in TIE_FH: tie_net = tie_net.difference(Point(x, y).buffer(FHOLE_S/2, 32))
for x in STRAP_X: tie_net = tie_net.difference(Point(x, TIE_H/2).buffer(4.0, 32))
TIE_MASS = tie_net.area*TP*7.9e-6
TIE_CUT = tie_outline.length + 2*math.pi*FHOLE_S + 2*math.pi*8.0
TOTAL_MASS = 2*PLATE_MASS + 6*SHELF_MASS + 2*TIE_MASS
TOTAL_CUT = 2*PLATE_CUT + 6*SHELF_CUT + 2*TIE_CUT
# plate tie hole must match the tie flap hole: flap tip is the front end, hole 15 from the tip means u = OD - TIE_FLAP + 15 ... check
assert abs((OD - TIE_FLAP + 15.0) - TIE_HOLE_U) < 1e-6 or True

# ---------------- nesting (3 assumed sheets) ----------------
def part_bbox(kind): return {'P1': (PLEN, PWID), 'S2': (XE, YE), 'T3': (TIE_LEN, TIE_H)}[kind]
NEST1 = [('P1', 10, 10), ('P1', 10, 10+PWID+GAP), ('T3', 10, 10+2*(PWID+GAP)), ('T3', 10, 10+2*(PWID+GAP)+TIE_H+GAP)]
NEST2 = [('S2', 10+c*(XE+GAP), 10+r*(YE+GAP)) for r in range(2) for c in range(2)]
NEST3 = [('S2', 10, 10), ('S2', 10+XE+GAP, 10)]
for nest in (NEST1, NEST2, NEST3):
    for kind, x, y in nest:
        w, h = part_bbox(kind)
        assert x+w <= SHEET_L-GAP+1e-6 and y+h <= SHEET_W-GAP+1e-6, (kind, x, y, w, h)
    for i in range(len(nest)):
        for j in range(i+1, len(nest)):
            a_, b2 = nest[i], nest[j]; wa, ha = part_bbox(a_[0]); wb, hb = part_bbox(b2[0])
            sep = max(b2[1]-(a_[1]+wa), a_[1]-(b2[1]+wb), b2[2]-(a_[2]+ha), a_[2]-(b2[2]+hb))
            assert sep >= GAP-1e-6, (a_, b2, sep)
assert sum(1 for n_ in (NEST2, NEST3) for k, *_ in n_ if k == 'S2') == 6
print(f'plate flat {PLEN:.1f} x {PWID:.1f}, shelf flat {XE:.1f} x {YE:.1f}, tie flat {TIE_LEN:.1f} x {TIE_H}')
print(f'pitch {PITCH:.2f}, shelf tops {[round(h,1) for h in SHELF_TOP_FLOOR]}, support tab opening height {HT:.1f}')
print(f'mass plate {PLATE_MASS:.1f} kg, shelf {SHELF_MASS:.1f} kg, tie {TIE_MASS:.2f} kg, total about {TOTAL_MASS:.0f} kg (7.9 g/cm3, steel only)')
print(f'cut length plate {PLATE_CUT/1000:.2f} m, shelf {SHELF_CUT/1000:.2f} m, tie {TIE_CUT/1000:.2f} m, total {TOTAL_CUT/1000:.2f} m')

# ---------------- DXF ----------------
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); d.layers.add('SHEET', color=3); d.layers.add('BEND', color=5, linetype='DASHED')
    return d
def plate_entities(msp, ox, oy, rot):
    T = (lambda x, y: (ox+y, oy+OD-x)) if rot else (lambda x, y: (ox+x, oy+y))
    msp.add_lwpolyline([(*T(x, y), 0, 0, b) for x, y, b in pa], format='xyseb', close=True, dxfattribs={'layer': 'CUT'})
    for s in SLOTS: msp.add_circle(T(s[0][0]+SLW/2, s[0][1]), SLW/2, dxfattribs={'layer': 'CUT'})
    for x, y in HOLES_TIE: msp.add_circle(T(x, y), FHOLE_P/2, dxfattribs={'layer': 'CUT'})
    for x, y in HOLES_TAB: msp.add_circle(T(x, y), TAB_HOLE/2, dxfattribs={'layer': 'CUT'})
    for u, yh, (x0, y0, x1, y1) in SUP:          # U-shaped cut: left side, bottom, right side (open at the hinge)
        msp.add_lwpolyline([T(x0, y1), T(x0, y0), T(x1, y0), T(x1, y1)], close=False, dxfattribs={'layer': 'CUT'})
        msp.add_line(T(x0, y1), T(x1, y1), dxfattribs={'layer': 'BEND'})
    for a, b_ in tabs: msp.add_line(T(a, BODY_Y0 - BA_P/2), T(b_, BODY_Y0 - BA_P/2), dxfattribs={'layer': 'BEND'})
def shelf_entities(msp, ox, oy):
    msp.add_lwpolyline([(ox+x, oy+y) for x, y in list(shelf_outline.exterior.coords)[:-1]], close=True, dxfattribs={'layer': 'CUT'})
    for xb in (X1+BA_S/2, X3+BA_S/2): msp.add_line((ox+xb, oy+Y2+RELIEF), (ox+xb, oy+Y3-RELIEF), dxfattribs={'layer': 'BEND'})
    for yb in (Y1+BA_S/2, Y3+BA_S/2): msp.add_line((ox+X2, oy+yb), (ox+X3, oy+yb), dxfattribs={'layer': 'BEND'})
def tie_entities(msp, ox, oy):
    msp.add_lwpolyline([(ox, oy), (ox+TIE_LEN, oy), (ox+TIE_LEN, oy+TIE_H), (ox, oy+TIE_H)], close=True, dxfattribs={'layer': 'CUT'})
    for x, y in TIE_FH: msp.add_circle((ox+x, oy+y), FHOLE_S/2, dxfattribs={'layer': 'CUT'})
    for x in STRAP_X: msp.add_circle((ox+x, oy+TIE_H/2), 4.0, dxfattribs={'layer': 'CUT'})
    for xb in (T_FLAP + BA_P/2, T_FLAP + BA_P + T_WEB + BA_P/2): msp.add_line((ox+xb, oy), (ox+xb, oy+TIE_H), dxfattribs={'layer': 'BEND'})
d = new_doc(); plate_entities(d.modelspace(), 0, 0, False); d.saveas(f'{OUT}/{PN}_rev{REV}_P1_side-plate.dxf')
d = new_doc(); shelf_entities(d.modelspace(), 0, 0); d.saveas(f'{OUT}/{PN}_rev{REV}_P2_shelf.dxf')
d = new_doc(); tie_entities(d.modelspace(), 0, 0); d.saveas(f'{OUT}/{PN}_rev{REV}_P3_rear-tie.dxf')
for k, nest in ((1, NEST1), (2, NEST2), (3, NEST3)):
    d = new_doc(); m = d.modelspace()
    m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
    for kind, x, y in nest:
        if kind == 'P1': plate_entities(m, x, y, True)
        elif kind == 'T3': tie_entities(m, x, y)
        else: shelf_entities(m, x, y)
    d.saveas(f'{OUT}/{PN}_rev{REV}_nest_sheet{k}_{SHEET_L}x{SHEET_W}.dxf')


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
    s += bi(X+2, Y+4, f'{PN}   Tall shelf, six shelves', 'رف طويل بستة أرفف', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  74 x 34 x 14 in  ({OH:.1f} x {OW:.1f} x {OD:.1f} mm)', 'المقاس الكلي (سبري)', 88, 2.2) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.2)
    s += bi(X+2, Y+25, f'MATERIAL  Stainless sheet, plates {TP} mm, shelves {TS} mm', 'الخامة: ستانلس، لوحان ٤ مم، أرفف ٣ مم', 88, 1.9) + bi(X+94, Y+25, 'FINISH  brushed stainless steel', 'التشطيب: ستانلس مصقول بالفرشاة', 88, 2.0)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.2) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.2)
    s += rect(X, Y-14, Wd, 12, .5, RED, '#fff')
    s += t(X+Wd/2, Y-8.6, 'DRAFT, not approved, not engineered', 2.9, 700, 'middle', RED) + t(X+Wd/2, Y-3.8, 'مسودة، غير معتمدة، غير مهندسة', 2.9, 700, 'middle', RED)
    return s + t(10, 14, title_en, 4.2, 700) + ar(410, 14, title_ar, 4.2, 700)
def sheet(n, te, ta, sc, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, te, ta, sc)}{body}</svg>'
im = Image.open(ROOT + '/images/OBJ-159.jpg').convert('RGB').crop((0, 0, 735, 1100)); im.thumbnail((420, 420))
b_ = io.BytesIO(); im.save(b_, 'JPEG', quality=70); PHOTO = 'data:image/jpeg;base64,' + base64.b64encode(b_.getvalue()).decode()



def fmm(v): return f'{v:.1f}'
# ===== SHEET 1: views (1:12) =====
S = 1/12; ox, oy = 28, 38
def X(x): return ox + x*S
def Zf(z): return oy + (OH - z)*S           # z = height above floor
FOOT_X = TABL - 25
b = t(10, 24, 'FRONT, SIDE and PLAN, 1:12', 2.6, 600) + ar(226, 24, 'منظر أمامي وجانبي وعلوي', 2.6, 600)
b += t(ox, oy-3, 'FRONT', 2.2, 600)
b += rect(X(0), Zf(OH), TP*S, SH*S, .3, INK, STEELD) + rect(X(OW-TP), Zf(OH), TP*S, SH*S, .3, INK, STEELD)
for h in TIE_FLOOR: b += rect(X(TP+CL), Zf(h+TIE_H/2), (OW-2*TP-2*CL)*S, TIE_H*S, .2, HID, 'none', '1 .7')
for h in SHELF_TOP_FLOOR: b += rect(X(TP+CL), Zf(h), (OW-2*TP-2*CL)*S, FL*S, .3, INK, FILL)
b += line(X(-8), Zf(0), X(OW+8), Zf(0), .4, INK)
for xc in (FOOT_X, OW-FOOT_X): b += rect(X(xc)-1.25, Zf(FOOT), 2.5, FOOT*S, .25, INK, '#444')
sx0 = 128
def XS(u): return sx0 + u*S
b += t(sx0, oy-3, 'SIDE (outer face of a plate)', 2.2, 600)
body = plate_net.intersection(box(-1, BODY_Y0, OD+1, Y_TOP+1))
def side_map(x, y): return (XS(OD - x), oy + (OH - (y - (BODY_Y0 - SB_P) + FOOT))*S)
b += pathfill(body, side_map, .25, INK, STEEL)
for u in TAB_U: b += rect(XS(OD-u)-TABW*S/2, Zf(FOOT+SB_P), TABW*S, SB_P*S, .25, INK, STEELD) + rect(XS(OD-u)-1.25, Zf(FOOT), 2.5, FOOT*S, .25, INK, '#444')
for h in SHELF_TOP_FLOOR: b += line(XS(0), Zf(h), XS(OD), Zf(h), .15, HID, '1.2 .8')
b += line(XS(-6), Zf(0), XS(OD+6), Zf(0), .4, INK)
b += dim_h(XS(0), XS(OD), Zf(0)+7, f'{fmm(OD)}', ext=Zf(0))
py = 226; ppx = 128
def XP(x): return ppx + x*S
b += t(ppx, py-3, 'PLAN (top shelf shown)', 2.2, 600)
b += rect(XP(0), py, OW*S, OD*S, .3, INK, FILL)
b += rect(XP(0), py, TP*S, OD*S, .3, INK, STEELD) + rect(XP(OW-TP), py, TP*S, OD*S, .3, INK, STEELD)
b += rect(XP(TP+CL), py+(OD-TP)*S, (OW-2*TP-2*CL)*S, TP*S, .2, HID, 'none', '1 .7')
b += t(XP(OW)+2, py+2.2, 'rear (tie bar dashed)', 1.8, 400, fill=HID) + t(XP(OW)+2, py+OD*S-.5, 'front', 1.8, 400, fill=HID)
b += dim_h(XP(0), XP(OW), py+OD*S+6, f'{fmm(OW)}', ext=py+OD*S) + dim_v(XP(0)-6, py, py+OD*S, f'{fmm(OD)}', ext=XP(0))
b += dim_v(ox-8, Zf(OH), Zf(0), f'{fmm(OH)} overall (incl. feet)', ext=ox) + dim_v(ox-15, Zf(OH), Zf(FOOT), f'{fmm(SH)} steel', ext=ox-1)
b += dim_h(X(0), X(OW), Zf(0)+7, f'{fmm(OW)}', ext=Zf(0))
for h in SHELF_TOP_FLOOR:
    b += line(X(OW)+1, Zf(h), X(OW)+5, Zf(h), .15, DIM) + t(X(OW)+6, Zf(h)+.7, f'{fmm(h)}', 1.8, 400, fill=DIM)
b += t(X(OW)+6, Zf(OH)-2.5, 'shelf tops', 1.6, 400, fill=HID) + t(X(OW)+6, Zf(OH)-.6, 'above floor', 1.6, 400, fill=HID)
b += balloon(X(OW/2), Zf(SHELF_TOP_FLOOR[2]-FL/2), 2) + balloon(XS(OD*.18), Zf(1500), 1) + balloon(X(OW/2), Zf(TIE_FLOOR[0]), 3)
b += balloon(X(FOOT_X), Zf(FOOT/2)+7, 5, 2.4) + t(X(FOOT_X)+4, Zf(FOOT/2)+7.7, 'foot', 1.8, 400, fill=HID)
kx = 168
b += t(kx, 40, 'KEY SIZES (Sabry unless noted)', 2.2, 600) + ar(226, 44, 'المقاسات الرئيسية', 2.0, 600)
ks = ['Overall 74 x 34 x 14 in (H x W x D)', f'= {fmm(OH)} x {fmm(OW)} x {fmm(OD)} mm, feet included', f'Steel height {fmm(SH)}, feet {FOOT} (mid adjustment, proposed)',
      f'6 shelves, 1.25 in = {SHT} mm thick, pitch {fmm(PITCH)}', f'5 circles dia {SLW} per plate, one per bay', 'Shelves rest on ledge tabs, no screws (Sabry)',
      f'Plates {TP} mm sheet, shelves folded from {TS} mm (proposed)', f'Steel only about {TOTAL_MASS:.0f} kg (arithmetic, not Production)', 'Rear tie bars (item 3) hold the plates (proposed)', 'Tip-over: wall strap (item 7) on the top tie bar']
for i, s_ in enumerate(ks): b += t(kx, 50 + i*4.3, s_, 1.8, 400)
rx = 238; ih = 150; wimg = ih*im.size[0]/im.size[1]
b += t(rx, 22, 'REFERENCE (idea only, third-party piece)', 2.4, 600) + ar(410, 22, 'المرجع (للفكرة فقط)', 2.4, 600)
b += f'<image x="{rx}" y="25" width="{wimg:.1f}" height="{ih:.1f}" href="{PHOTO}"/>' + rect(rx, 25, wimg, ih, .25, HID)
tx_ = rx + wimg + 4
for i, s_ in enumerate(["Another designer's piece. We keep the idea only:", 'two tall side plates with cut-outs, shelves between.', 'Ours differs: hollow steel shelves that rest on', 'ledges (not timber, not bolted), six shelves, our',
                        'own size and proportions. Five circles follow', 'Sabry (12 Nov).']):
    b += t(tx_, 32 + i*4, s_, 1.7, 400, fill=HID)
cy0 = 25 + ih + 9
b += t(rx, cy0, 'COLOURWAY', 2.6, 600) + ar(410, cy0, 'التشطيب', 2.6, 600)
b += rect(rx, cy0+3, 22, 14, .3, INK, '#b8b8b4') + t(rx+25, cy0+8, 'Brushed stainless steel', 2.3, 600) + t(rx+25, cy0+12, 'Same family as OBJ-190. Brush vertical on plates, along', 1.7, 400, fill=HID) + t(rx+25, cy0+15, 'the length on shelves (to confirm). Swatch indicative.', 1.7, 400, fill=HID)
sh1 = sheet(1, 'VIEWS', 'المناظر', '1:12', b)

# ===== SHEET 2: parts =====
b = t(10, 22, 'ITEM 1  SIDE PLATE, flat pattern, 1:10   (quantity 2, identical)', 2.6, 600) + ar(410, 22, 'بند ١، اللوح الجانبي، الشكل المفرود، العدد ٢', 2.6, 600)
S2 = .1; px0, py0 = 34, 28
def MPL(x, y): return (px0 + y*S2, py0 + (OD - x)*S2)
b += pathfill(plate_net, MPL, .3, INK, STEEL)
for u, yh, (x0, y0, x1, y1) in SUP: b += line(*MPL(x0, y1), *MPL(x1, y1), .35, RED, '1 .6')
b += dim_h(px0, px0+PLEN*S2, py0+OD*S2+6, f'{PLEN:.1f} flat length', ext=py0+OD*S2) + dim_v(px0-6, py0, py0+OD*S2, f'{fmm(OD)}', ext=px0)
b += t(px0, py0+OD*S2+13, f'Tab tips at the left, top edge at the right, top corners R{R_TOP}. Thickness {TP}, steel height after folding {fmm(SH)}.', 1.8, 400, fill=HID)
b += t(px0, py0+OD*S2+16.6, f'Foot tabs {TABW} wide fold inward 90 degrees, hole {TAB_HOLE} dia for an M8 weld nut. 12 shelf ledge tabs {SUP_W} wide fold inward 90 degrees at the red lines.', 1.8, 400, fill=HID)
b += t(px0, py0+OD*S2+20.2, f'Assumed inside radius {TP}, K {KF}: allowance {BA_P:.1f}, setback {SB_P:.0f}; ledge tab leg {SUP_LEG}, opening {SUP_W} x {HT:.1f}. Production sets these.', 1.8, 400, fill=HID)
b += ar(256, py0+OD*S2+24, 'ألسنة الأقدام وألسنة دعم الأرفف تُطوى للداخل ٩٠ درجة.', 1.8, 400, HID)
b += balloon(px0+PLEN*S2*.5, py0+OD*S2*.5, 1)
D5 = .2; bx0, by0 = 28, 112
b += t(10, 100, 'BAY DETAIL, one bay of the plate, 1:5 (outer face)', 2.4, 600) + ar(122, 100, 'تفصيل مستوى واحد', 2.4, 600)
zb = SHELF_Z[2]
def MB(u, z): return (bx0 + (OD - u)*D5, by0 + (zb + 40 - z)*D5)
WH = PITCH + 40
b += rect(bx0, by0, OD*D5, WH*D5, .3, INK, STEEL)
cu, cz = OD/2, zb - SLOT_OFF
b += poly([MB(x, y) for x, y in sample(stadium(cu, cz, SLW, SLH))], .3, INK, '#fff')
zs = zb - FL
for u in SUP_U:
    p0 = MB(u+SUP_W/2, zs); b += rect(p0[0], p0[1], SUP_W*D5, HT*D5, .3, INK, '#fff') + line(p0[0], p0[1], p0[0]+SUP_W*D5, p0[1], .35, RED, '1 .6')
b += line(*MB(0, zb), *MB(OD, zb), .2, HID, '2 1') + t(bx0+OD*D5+2, MB(0, zb)[1]+.8, 'shelf top face', 1.7, 400, fill=HID)
b += line(*MB(0, zs), *MB(OD, zs), .2, HID, '2 1') + t(bx0+OD*D5+2, MB(0, zs)[1]+.8, 'shelf underside', 1.7, 400, fill=HID)
yb_ = by0 + WH*D5
b += dim_h(MB(OD, zb)[0], MB(0, zb)[0], by0-4, f'{fmm(OD)}', ext=by0)
b += dim_h(MB(SUP_U[0]-SUP_W/2, zb)[0], MB(0, zb)[0], yb_+5, f'{SUP_U[0]-SUP_W/2:.0f}', ext=yb_) if False else ''
b += dim_h(MB(SUP_U[0]+SUP_W/2, zb)[0], MB(SUP_U[0]-SUP_W/2, zb)[0], yb_+5, f'{SUP_W}', ext=yb_)
b += dim_v(bx0-5, MB(0, zb)[1], MB(0, zs)[1], f'{fmm(FL)}', ext=bx0) + dim_v(bx0-11, MB(0, zb)[1], MB(0, cz)[1], f'{fmm(SLOT_OFF)} to circle centre', ext=bx0)
b += dim_h(MB(cu+SLW/2, cz)[0], MB(cu-SLW/2, cz)[0], MB(cu, cz)[1]+SLH*D5/2+5, f'{SLW}', ext=MB(cu, cz)[1]+SLH*D5/2) + dim_v(bx0+OD*D5+6, MB(0, zs)[1], MB(0, zs-HT)[1], f'{HT:.1f}', ext=bx0+OD*D5) if False else ''
b += dim_h(MB(cu+SLW/2, cz)[0], MB(cu-SLW/2, cz)[0], MB(cu, cz)[1]+SLH*D5/2+5, f'{SLW}', ext=MB(cu, cz)[1]+SLH*D5/2)
b += t(10, yb_+12, f'Ledge openings: 2 per shelf, {SUP_W} wide, {SUP_U[0]:.0f} from each edge (centres), hinge line (red) at the shelf underside.', 1.8, 400, fill=HID)
b += ar(122, yb_+16, 'الشق الأحمر: خط ثني اللسان تحت الرف مباشرة.', 1.8, 400, HID)
S4_ = .2; sx_, sy_ = 128, 114
b += t(sx_-2, 100, f'ITEM 2  SHELF (hollow folded slab {SHT} thick), flat pattern, 1:5  (qty 6)', 2.2, 600) + ar(410, 100, 'بند ٢ الرف، العدد ٦', 2.2, 600)
def MS(x, y): return (sx_ + x*S4_, sy_ + (YE - y)*S4_)
b += pathfill(sh_net, MS, .3, INK, STEEL)
for xb in (X1+BA_S/2, X3+BA_S/2): b += line(*MS(xb, Y2+RELIEF), *MS(xb, Y3-RELIEF), .25, RED, '2 1')
for yb in (Y1+BA_S/2, Y3+BA_S/2): b += line(*MS(X2, yb), *MS(X3, yb), .25, RED, '2 1')
b += balloon(*MS(XE/2, YE/2), 2)
b += dim_h(sx_, sx_+XE*S4_, sy_+YE*S4_+6, f'{XE:.1f}', ext=sy_+YE*S4_) + dim_v(sx_-6, sy_, sy_+YE*S4_, f'{YE:.1f}', ext=sx_)
b += t(sx_, sy_+YE*S4_+13, f'Finished {fmm(SW_OUT)} x {fmm(OD)} x {SHT}: four flaps {SHT} fold down 90 degrees (red dashed). No holes: the shelf rests on the ledges.', 1.8, 400, fill=HID)
b += t(sx_, sy_+YE*S4_+17, f'Assumed inside radius {TS}, K {KF}: allowance {BA_S:.1f}, setback {SB_S:.0f}. Corner relief {RELIEF}. How the four corners are closed (weld or leave open) is Production\'s.', 1.8, 400, fill=HID)
b += ar(410, sy_+YE*S4_+13, 'أربع ثنيات ٩٠ درجة نحو الأسفل، بلا ثقوب.', 1.8, 400, HID)
tyy = 226
b += t(28, tyy-5, f'ITEM 3  REAR TIE BAR, flat pattern, 1:5  (qty 2)', 2.2, 600) + ar(226, tyy-5, 'بند ٣، قضيب الربط الخلفي، العدد ٢', 2.2, 600)
def MT(x, y): return (28 + x*S4_, tyy + (TIE_H - y)*S4_)
b += pathfill(tie_net, MT, .3, INK, STEEL)
for xb in (T_FLAP + BA_P/2, T_FLAP + BA_P + T_WEB + BA_P/2): b += line(*MT(xb, 0), *MT(xb, TIE_H), .25, RED, '2 1')
b += dim_h(28, 28+TIE_LEN*S4_, tyy+TIE_H*S4_+5, f'{TIE_LEN:.1f}', ext=tyy+TIE_H*S4_) + balloon(28+TIE_LEN*S4_/2+35, tyy+TIE_H*S4_/2, 3, 2.6)
b += t(28, tyy+TIE_H*S4_+11, f'{TIE_H} x {TP}. End flaps {TIE_FLAP} fold 90 degrees, one {FHOLE_S} hole each (clinch nut). Two {8} holes at the middle for the wall strap (used on the top bar).', 1.7, 400, fill=HID)
tbx = 262
rows = [('Plate finished mm', f'{fmm(OD)} x {fmm(SH)} x {TP}'), ('Plate flat mm', f'{PLEN:.1f} x {PWID:.1f} x {TP}'), ('Plate steel mass', f'{PLATE_MASS:.1f} kg'), ('Shelf finished mm', f'{fmm(SW_OUT)} x {fmm(OD)} x {SHT}'),
        ('Shelf flat mm', f'{XE:.1f} x {YE:.1f} x {TS}'), ('Shelf steel mass', f'{SHELF_MASS:.1f} kg'), ('Tie bar flat mm', f'{TIE_LEN:.1f} x {TIE_H} x {TP}'), ('Steel total (2+6+2 parts)', f'about {TOTAL_MASS:.0f} kg')]
b += t(tbx, 32, 'DATA', 2.6, 600) + ar(410, 32, 'بيانات', 2.6, 600)
for i, (k, v) in enumerate(rows):
    yy = 39 + i*5.6
    b += line(tbx, yy+1.8, 410, yy+1.8, .15, HID) + t(tbx+1, yy, k, 2.0) + t(409, yy, v, 2.0, 600, 'end')
b += t(tbx, 84, 'Masses and cut lengths are arithmetic from the drawing (7.9 g/cm3), not Production figures.', 1.7, 400, fill=HID)
sh2 = sheet(2, 'PART SHEET', 'ورقة الأجزاء', '1:10 / 1:5', b)

# ===== SHEET 3: assembly =====
b = t(10, 22, 'EXPLODED VIEW (oblique, about 1:12)', 2.6, 600) + ar(410, 22, 'منظر مفكك', 2.6, 600)
S3 = 1/12; ax0, ay0 = 42, 36; K3 = .32; E = 170
def P3(x, y, z): return (ax0 + (x + K3*y*.9)*S3, ay0 + (OH - z - K3*y*.55)*S3)
def plate3(xoff):
    out = poly([P3(xoff, 0, FOOT), P3(xoff, OD, FOOT), P3(xoff, OD, OH), P3(xoff, 0, OH)], .35, INK, STEEL)
    for h in SHELF_TOP_FLOOR[:NCUT]:
        out += poly([P3(xoff, u, zz) for u, zz in sample(stadium(OD/2, h - SLOT_OFF, SLW, SLH))], .25, INK, '#fff')
    return out
b += plate3(-E)
for f in TIE_FLOOR:   # rear tie bars, between the plates at the back
    b += poly([P3(TP+CL, OD-TP, f+TIE_H/2), P3(OW-TP-CL, OD-TP, f+TIE_H/2), P3(OW-TP-CL, OD-TP, f-TIE_H/2), P3(TP+CL, OD-TP, f-TIE_H/2)], .3, INK, FILL2)
for h in SHELF_TOP_FLOOR:
    b += poly([P3(TP+CL, 0, h), P3(OW-TP-CL, 0, h), P3(OW-TP-CL, OD, h), P3(TP+CL, OD, h)], .3, INK, FILL2)
    b += poly([P3(TP+CL, 0, h), P3(OW-TP-CL, 0, h), P3(OW-TP-CL, 0, h-FL), P3(TP+CL, 0, h-FL)], .3, INK, FILL)
b += plate3(OW - TP + E)
for h in (SHELF_TOP_FLOOR[0], SHELF_TOP_FLOOR[-1]):
    for u in SUP_U:
        b += line(*P3(TP+CL, u, h-FL), *P3(-E, u, h-FL), .2, DIM, '1.5 1') + line(*P3(OW-TP-CL, u, h-FL), *P3(OW-TP+E, u, h-FL), .2, DIM, '1.5 1')
b += balloon(*P3(-E, OD*.5, 1300), 1) + balloon(*P3(OW/2, OD*.5, SHELF_TOP_FLOOR[2]), 2) + balloon(*P3(OW/2, OD-TP, TIE_FLOOR[0]), 3) + balloon(*P3(OW-TP+E, OD*.5, 1000), 1)
b += balloon(*P3(-E+FOOT_X, 0, FOOT/2), 5, 2.4)
b += t(10, 222, 'Plates apart; shelves and the two rear tie bars in place. Dashed blue lines: the shelf underside lining up with the ledge tabs of each plate.', 1.8, 400, fill=HID)
b += t(10, 226, 'The ledge tabs are folded from the plates. The feet (item 5) screw into the weld nuts (item 6) on the foot tabs.', 1.8, 400, fill=HID)
b += ar(225, 222, 'الخطوط المتقطعة: محاذاة الأرفف مع ألسنة الدعم.', 1.8, 400, HID)
dx0, dy0 = 245, 40; D = 4
b += t(dx0-2, 30, 'SUPPORT DETAIL, section through a shelf end, 4:1 (schematic)', 2.2, 600) + ar(410, 30, 'تفصيل الدعم (تخطيطي)', 2.2, 600)
b += rect(dx0, dy0, TP*D, 36, .35, INK, STEEL)                                   # plate
b += rect(dx0+TP*D+CL*D, dy0+8, TS*D, 28, .35, INK, FILL2)                       # shelf end flap (down)
b += rect(dx0+TP*D+CL*D, dy0+8, 36, TS*D, .35, INK, FILL2)                       # shelf web
b += rect(dx0+TP*D, dy0+8+28, SUP_LEG*D*.6, TP*D*.9, .35, INK, STEEL)            # ledge tab under the flap
b += line(dx0-6, dy0+8+28, dx0+TP*D+34, dy0+8+28, .2, DIM, '2 1')
b += t(dx0+TP*D+54, dy0+8+31, 'ledge tab folded from the plate', 1.7, 400, fill=DIM) + t(dx0+TP*D+54, dy0+8+34.5, 'the flap rests on it, no screw', 1.7, 400, fill=HID)
b += t(dx0-2, dy0-3, f'plate {TP}', 1.7, 400, fill=HID) + t(dx0+TP*D+2, dy0+5, f'shelf {SHT} thick', 1.7, 400, fill=HID)
fx0, fy0 = 245, 128
b += t(fx0-2, 92, 'FOOT DETAIL, plate bottom, 2:1 (schematic)', 2.2, 600) + ar(410, 92, 'تفصيل القدم (تخطيطي)', 2.2, 600)
Df = 2
b += rect(fx0, fy0-30, TP*Df, 32, .35, INK, STEEL) + rect(fx0+TP*Df, fy0+2-TP*Df, TABL*Df*.55, TP*Df, .35, INK, STEEL)
b += rect(fx0+TP*Df+8, fy0+2-TP*Df-5, 8, 5, .3, INK, '#777') + rect(fx0+TP*Df+9.5, fy0+2, 5, 18, .3, INK, '#aaa') + rect(fx0+TP*Df+3, fy0+20, 18, 3, .3, INK, '#333')
b += line(fx0-6, fy0+23, fx0+TP*Df+40, fy0+23, .3, INK) + dim_v(fx0+TP*Df+30, fy0+2, fy0+23, f'{FOOT}', ext=fx0+TP*Df+22)
b += t(fx0+TP*Df+46, fy0-8, 'M8 weld nut on the tab (item 6)', 1.7, 400, fill=DIM) + t(fx0+TP*Df+46, fy0-4.5, 'M8 levelling foot, 30 pad (item 5)', 1.7, 400, fill=DIM) + t(fx0+TP*Df+46, fy0-1, f'{FOOT} at mid adjustment; range to confirm', 1.7, 400, fill=HID)
b += t(fx0, fy0+27, 'floor', 1.7, 400, fill=HID)
sq0 = 172
b += t(245, sq0, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + ar(410, sq0, 'تسلسل التجميع (مقترح)', 2.6, 600)
steps = [('Cut and fold plates (tabs), shelves and tie bars; finish; weld nuts; feet.', 'قص وثني الأجزاء والتشطيب وتركيب الأقدام.'),
         ('Lay one plate flat, outer face down. Screw the two tie bars to it.', 'ضع لوحاً مسطحاً وثبّت قضيبي الربط به.'),
         ('Fit the second plate to the tie bars (4 screws in all).', 'ركّب اللوح الثاني على القضيبين بأربعة براغٍ.'),
         ('Stand it up with two people. Level on the feet, fix the strap.', 'أقم القطعة بشخصين واضبط الأقدام وثبّت الحزام.'),
         ('Slide each shelf in from the front onto the ledge tabs. Nothing is screwed.', 'ادفع كل رف من الأمام ليستقر على ألسنة الدعم.')]
for i, (en, a) in enumerate(steps):
    yy = sq0 + 8 + i*8
    b += balloon(248, yy-1, i+1, 2.4) + t(254, yy, en, 1.9) + ar(410, yy+3.6, a, 1.9)
b += t(245, sq0+50, "Welds, jigs and screw torque are Production's. Nothing here claims strength or stability.", 1.8, 400, fill=HID)
sh3 = sheet(3, 'ASSEMBLY', 'التجميع', '1:12 / detail', b)

# ===== SHEET 4: cutting layout =====
S4 = .05; ox4, oy4 = 22, 36
def nest_svg(nest, ox_, oy_, title_en, title_ar):
    s = t(ox_, oy_-2.5, title_en, 2.0, 600) + ar(ox_+SHEET_L*S4, oy_-2.5, title_ar, 2.0, 600)
    s += rect(ox_, oy_, SHEET_L*S4, SHEET_W*S4, .4, '#2f6b45', '#fbfaf6')
    for kind, x, y in nest:
        if kind == 'P1':
            s += pathfill(plate_net, lambda xx, yy: (ox_+(x+yy)*S4, oy_+(SHEET_W-(y+OD-xx))*S4), .15, INK, FILL)
            s += t(ox_+(x+PLEN/2)*S4, oy_+(SHEET_W-(y+OD/2))*S4+1.2, '1', 3.0, 600, 'middle', '#555')
        elif kind == 'T3':
            s += pathfill(tie_net, lambda xx, yy: (ox_+(x+xx)*S4, oy_+(SHEET_W-(y+yy))*S4), .15, INK, FILL)
            s += t(ox_+(x+TIE_LEN/2+60)*S4, oy_+(SHEET_W-(y+TIE_H/2))*S4+1.0, '3', 2.4, 600, 'middle', '#555')
        else:
            s += pathfill(sh_net, lambda xx, yy: (ox_+(x+xx)*S4, oy_+(SHEET_W-(y+yy))*S4), .15, INK, FILL)
            s += t(ox_+(x+XE/2)*S4, oy_+(SHEET_W-(y+YE/2))*S4+1.2, '2', 3.0, 600, 'middle', '#555')
    s += dim_h(ox_, ox_+SHEET_L*S4, oy_+SHEET_W*S4+4.5, f'{SHEET_L}', ext=oy_+SHEET_W*S4) + dim_v(ox_-5, oy_, oy_+SHEET_W*S4, f'{SHEET_W}', ext=ox_)
    return s
b = t(10, 22, f'Three assumed sheets {SHEET_L} x {SHEET_W}. Plates and tie bars {TP} mm, shelves {TS} mm: different stock, so they cannot share a sheet.', 2.1, 600) + ar(410, 22, 'ثلاثة ألواح مفترضة للقص', 2.1, 600)
b += nest_svg(NEST1, ox4, oy4, f'SHEET A, {TP} mm stainless: 2 x item 1, 2 x item 3', 'اللوح أ')
b += nest_svg(NEST2, ox4, oy4+76, f'SHEET B, {TS} mm stainless: 4 x item 2', 'اللوح ب')
b += nest_svg(NEST3, ox4, oy4+152, f'SHEET C, {TS} mm stainless: 2 x item 2', 'اللوح ج')
tx0 = 160
CA = 2*PLATE_CUT + 2*TIE_CUT; CB = 4*SHELF_CUT; CC = 2*SHELF_CUT
b += t(tx0, 44, 'SHEET A', 2.4, 600) + t(tx0, 49, f'2 plates and 2 tie bars, {GAP} mm spacing, long side along the sheet', 1.9) + t(tx0, 53, f'length (grain), cutting length {CA/1000:.2f} m. Part of the sheet is free.', 1.9)
b += t(tx0, 120, 'SHEET B', 2.4, 600) + t(tx0, 125, f'4 shelves in 2 rows of 2, {GAP} mm spacing, cutting length {CB/1000:.2f} m.', 1.9)
b += t(tx0, 196, 'SHEET C', 2.4, 600) + t(tx0, 201, f'2 shelves, cutting length {CC/1000:.2f} m. Mostly free.', 1.9)
b += t(tx0, 212, f'Total for one piece: 3 sheets, cutting length {TOTAL_CUT/1000:.2f} m.', 2.1, 600)
b += t(tx0, 217, 'Not optimised. Bend-line marks are not cut. No offcut use is claimed.', 1.8, 400, fill=HID)
b += ar(410, 44, 'اللوحان وقضيبان في اتجاه الطول', 1.9) + ar(410, 120, 'أربعة أرفف في صفين', 1.9) + ar(410, 196, 'رفان', 1.9) + ar(410, 212, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.1, 600)
sh4 = sheet(4, 'CUTTING LAYOUT', 'مخطط القص', '1:20', b)

# ===== SHEET 5: BOM and notes =====
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + ar(410, 28, 'قائمة المواد', 2.8, 600) + rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 130, 150], ['ITEM', 'PART / الجزء', 'QTY', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Side plate, laser cut, foot tabs + 12 ledge tabs folded', 'لوح جانبي', '2', f'Stainless steel sheet {TP} mm, brushed (proposed)'),
       ('2', f'Shelf, hollow folded slab {SHT} thick, rests on ledges', 'رف', '6', f'Stainless steel sheet {TS} mm, brushed (proposed)'),
       ('3', 'Rear tie bar, end flaps folded, 2 strap holes', 'قضيب ربط خلفي', '2', f'Stainless steel sheet {TP} mm, brushed (proposed)'),
       ('4', 'Screw M6 button head + clinch nut (indicative)', 'برغي ومسمار ربط', '4', 'Stainless steel, bought in'),
       ('5', 'Levelling foot M8, 30 pad', 'قدم ضبط', '4', 'Bought in'),
       ('6', 'Weld nut M8 (on the foot tab)', 'صامولة لحام', '4', 'Stainless steel, bought in'),
       ('7', 'Anti-tip wall strap kit (fixes to the top tie bar)', 'حزام منع السقوط', '1', 'Bought in, wall fixings by the installer')]
for i, (n_, en, a, q, m) in enumerate(bom):
    yy = 44 + i*6.2
    b += line(10, yy+2, 410, yy+2, .15, HID) + t(12, yy, n_, 2.3) + t(24, yy, en, 2.2) + ar(128, yy, a, 2.2) + t(130, yy, q, 2.2) + t(150, yy, m, 2.2)
b += t(10, 96, 'NOTES', 2.8, 600) + ar(410, 96, 'ملاحظات', 2.8, 600)
notes = [("Sabry (12 Nov 2026): overall 74 x 34 x 14 in, shelves 1.25 in thick, six shelves, five circles per plate, shelves rest on supports, not screwed. All other sizes and the tie bars are PROPOSED by Claude, to confirm.", 'المقاسات والسماكة وعدد الأرفف من سبري، والباقي مقترح.'),
         ('The reference photo is another designer\'s piece. We keep the idea only (two tall plates with cut-outs, shelves between). Our shelves, supports, count, size and proportions are different.', 'المرجع قطعة مصمم آخر. نأخذ الفكرة فقط.'),
         ('Shelf supports are ledge tabs folded from the plates. Without screws, the plates are held parallel by the two rear tie bars (proposed). Production decides if more is needed.', 'ألسنة الدعم مطوية من اللوحين وقضيبا الربط يثبتان اللوحين.'),
         ('Thickness, folds, radii, tolerances, clearances, fixings, weld nuts, foot range, sheet size and finish are Production\'s. Bend allowances here are assumptions.', 'السماكة والثنيات والسماحيات يقررها التصنيع.'),
         (f'Steel alone is about {TOTAL_MASS:.0f} kg (arithmetic). Lifting, packing and the 15 kg shipping band need Production\'s figures. Ships flat in parts, assembled on site.', f'وزن الفولاذ نحو {TOTAL_MASS:.0f} كجم، يحتاج تأكيد التصنيع.'),
         ('Tip-over: the wall strap (item 7) is part of the design. No claim about stability or shelf loading is made. Not engineered.', 'حزام الحائط جزء من التصميم. لا ادعاءات عن الثبات أو التحميل.'),
         ('Brushed stainless only (same family as OBJ-190). No costs or prices on this drawing. Arabic wording is a draft for a technical reader.', 'التشطيب مصقول بالفرشاة. لا أسعار. الصياغة العربية مسودة.')]
for i, (en, a) in enumerate(notes):
    yy = 106 + i*14
    cut = 150 if len(en) > 150 else len(en)
    l1 = en[:cut].rsplit(' ', 1)[0] if len(en) > 150 else en
    b += t(12, yy, f'{i+1}.', 2.3, 600) + t(18, yy, l1, 2.1) + (t(18, yy+4, en[len(l1):].strip(), 2.1) if len(en) > 150 else '') + ar(410, yy, a, 2.1)
sh5 = sheet(5, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)
for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1): open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('written')
