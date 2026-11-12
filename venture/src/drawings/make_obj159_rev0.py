"""OBJ-159: tall shelf, six shelves, two stainless side plates with stadium cut-outs. Production drawing set, REV 0 (DRAFT).
Run: python3 make_obj159_rev0.py <repo root>   then: NODE_PATH=<playwright> node make_pdf.js <dir> OBJ-159 0
Reference: images/OBJ-159.jpg is a third-party piece (jeremylechatelier, Hublot). Used for the IDEA only. This is objekt's OWN design
(Sabry approved the redesign 12 Nov 2026: 210-220 cm tall, six shelves, stainless, Furniture).
ALL SIZES ARE PROPOSED BY CLAUDE except height (Sabry: 210-220 cm, 2150 chosen) and shelf count (six). Arabic is a draft. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-159'; os.makedirs(OUT, exist_ok=True)
REV = 0; DATE = '12 Nov 2026'; PN = 'OBJ-159'

# ---------------- proposed sizes (mm) ----------------
OH, OW, OD = 2150, 800, 350          # overall height (incl. feet), width, depth
FOOT = 40                            # underside of plate above floor, feet at mid adjustment (adjustment range to confirm)
TP, TS = 4, 3                        # plate and shelf thickness
SH = OH - FOOT                       # steel height of a plate (tab underside to top edge) = 2110
NSH = 6; PITCH = 350                 # shelves, pitch
TOP_BELOW = 30                       # top face of top shelf is 30 below the plate top, so its 30 mm rear lip is flush with the plate top
SHELF_TOP_FLOOR = [OH - TOP_BELOW - PITCH*k for k in range(NSH)]   # shelf top faces above floor: 2120 ... 370
SHELF_Z = [h - FOOT for h in SHELF_TOP_FLOOR]                       # same, measured from the plate's tab underside
FL = 30                              # shelf flange / front return / rear lip height (outside)
SLW, SLH = 100, 200                  # stadium slot width, height
SLOT_OFF = 185                       # slot centre below shelf top face
HOLE_U = [80, 270]                   # fixing holes, distance from front edge of plate
FHOLE_P, FHOLE_S = 6.5, 8.0          # plate hole, shelf flange clinch-nut hole (indicative)
FHOLE_DROP = 15                      # hole centre below shelf top face
# bend assumptions (Production sets the real ones)
KF = 0.4
def bend(t, r): return r + t, math.pi/2*(r + KF*t)      # setback, bend allowance
SB_P, BA_P = bend(TP, TP)            # plate foot bend, inside radius = t
SB_S, BA_S = bend(TS, TS)            # shelf bends, inside radius = t
TABW, TABL = 40, 60                  # foot tab width, outside leg length
TAB_U = [70, 280]                    # foot tab centres from front edge
TAB_HOLE = 9.0                       # M8 weld nut over a 9 mm hole (indicative)
SHEET_L, SHEET_W, GAP = 2500, 1250, 10
R_TOP = 10

# ---------------- path helpers: list of (x, y, bulge) ----------------
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
    return [(cu-r, cy-(h/2-r), 0), (cu-r, cy+(h/2-r), -1), (cu+r, cy+(h/2-r), 0), (cu+r, cy-(h/2-r), -1)]

# ---------------- ITEM 1: side plate (flat pattern, y up, y=0 is the tab tip) ----------------
BODY_Y0 = TABL - SB_P + BA_P                  # y where the straight body starts (above the bend zone)
PLATE_LEN = (SH - SB_P) + BA_P + (TABL - SB_P)  # flat length
assert abs(BODY_Y0 + (SH - SB_P) - PLATE_LEN) < 1e-6
def zy(z): return z + (BODY_Y0 - SB_P)         # final height above tab underside -> flat y (body points)
Y_TOP = PLATE_LEN
tabs = [(u-TABW/2, u+TABW/2) for u in TAB_U]
pa = [(0, BODY_Y0, 0)]
for a, b_ in tabs:
    pa += [(a, BODY_Y0, 0), (a, 0, 0), (b_, 0, 0), (b_, BODY_Y0, 0)]
pa += [(OD, BODY_Y0, 0), (OD, Y_TOP-R_TOP, math.tan(math.pi/8)), (OD-R_TOP, Y_TOP, 0), (R_TOP, Y_TOP, math.tan(math.pi/8)), (0, Y_TOP-R_TOP, 0)]
# plate slots and holes
SLOTS = [stadium(OD/2, zy(z - SLOT_OFF), SLW, SLH) for z in SHELF_Z]
HOLES_P = [(u, zy(z - FHOLE_DROP)) for z in SHELF_Z for u in HOLE_U]
HOLES_TAB = [(u, TABL - SB_P - 25 + 0) for u in TAB_U]   # hole centre 25 flat-mm from the tab tip... see note: tab leg 60 outside, hole 35 from the plate face
HOLES_TAB = [(u, 25.0) for u in TAB_U]
plate_outline = Polygon(sample(pa))
plate_cuts = [Polygon(sample(s)) for s in SLOTS] + [Point(x, y).buffer(FHOLE_P/2, 32) for x, y in HOLES_P] + [Point(x, y).buffer(TAB_HOLE/2, 32) for x, y in HOLES_TAB]
plate_net = plate_outline
for c in plate_cuts: plate_net = plate_net.difference(c)
assert plate_net.geom_type == 'Polygon' and len(plate_net.interiors) == len(plate_cuts)
# clearances (min web between slot and holes, slot and bottom edge)
for z in SHELF_Z:
    cy = zy(z - SLOT_OFF)
    assert cy - SLH/2 > BODY_Y0 + 25, (cy, BODY_Y0)         # at least 25 mm of web below the lowest slot
    assert zy(z - FL) - (cy + SLH/2) >= 50 - 1e-6 or z != SHELF_Z[0], 'top slot web'
for i, z in enumerate(SHELF_Z):
    top_of_slot = zy(z - SLOT_OFF) + SLH/2
    assert zy(z - FHOLE_DROP) - top_of_slot > 40, 'hole too close to slot'
PBX = plate_outline.bounds; PLEN, PWID = PBX[3]-PBX[1], PBX[2]-PBX[0]
PLATE_AREA = plate_net.area; PLATE_MASS = PLATE_AREA*TP*7.9e-6
PLATE_CUT = plate_outline.length + sum(Polygon(sample(s)).length for s in SLOTS) + sum(math.pi*FHOLE_P for _ in HOLES_P) + sum(math.pi*TAB_HOLE for _ in HOLES_TAB)

# ---------------- ITEM 2 / 3: shelf (flat pattern, y up, y=0 is the rear lip tip) ----------------
WEB_W = OW - 2*TP - 2*SB_S                     # flat web width
WEB_D = OD - 2*SB_S
X1 = FL - SB_S; X2 = X1 + BA_S; X3 = X2 + WEB_W; X4 = X3 + BA_S; XE = X4 + (FL - SB_S)
Y1 = FL - SB_S; Y2 = Y1 + BA_S; Y3 = Y2 + WEB_D; Y4 = Y3 + BA_S; YE = Y4 + (FL - SB_S)
RELIEF = 1.0
shelf_outline = unary_union([box(X2, 0, X3, YE), box(0, Y2+RELIEF, X2, Y3-RELIEF), box(X3, Y2+RELIEF, XE, Y3-RELIEF)])
assert shelf_outline.geom_type == 'Polygon'
def uy(u): return Y2 + (OD - SB_S - u) - 0 if False else (Y2 + (OD - SB_S) - u)  # u from front outer face -> flat y (web region)
FH_Y = [uy(u) for u in HOLE_U]
FH = [(15.0, y) for y in FH_Y] + [(XE-15.0, y) for y in FH_Y]
STRAP = [(XE/2-250, 12.0), (XE/2+250, 12.0)]
def shelf_poly(strap=False):
    cuts = [Point(x, y).buffer(FHOLE_S/2, 32) for x, y in FH] + ([Point(x, y).buffer(4.0, 32) for x, y in STRAP] if strap else [])
    p = shelf_outline
    for c in cuts: p = p.difference(c)
    return p, cuts
sh_net, _ = shelf_poly(False); sht_net, _ = shelf_poly(True)
SHELF_MASS = sh_net.area*TS*7.9e-6
SHELF_CUT = shelf_outline.length + len(FH)*math.pi*FHOLE_S
SHELFT_CUT = SHELF_CUT + 2*math.pi*8.0
# fixing hole positions: shelf flange hole vs plate hole must agree (distance from front edge)
assert all(abs(uy(u) - y) < 1e-6 for u, y in zip(HOLE_U, FH_Y))
TOTAL_MASS = 2*PLATE_MASS + 5*SHELF_MASS + SHELF_MASS
TOTAL_CUT = 2*PLATE_CUT + 5*SHELF_CUT + SHELFT_CUT

# ---------------- nesting (2 assumed sheets: 4 mm for the plates, 3 mm for the shelves) ----------------
NEST1 = [('P1', 10, 10), ('P1', 10, 10+PWID+GAP)]
NEST2 = [('S2', 10+c*(XE+GAP), 10+r*(YE+GAP)) for r in range(3) for c in range(2)]
NEST2[-1] = ('S3',) + NEST2[-1][1:]
def part_bbox(kind): return (PLEN, PWID) if kind == 'P1' else (XE, YE)
for nest in (NEST1, NEST2):
    for kind, x, y in nest:
        w, h = part_bbox(kind)
        assert x+w <= SHEET_L-GAP+1e-6 and y+h <= SHEET_W-GAP+1e-6, (kind, x, y, w, h)
    for i in range(len(nest)):
        for j in range(i+1, len(nest)):
            a_, b2 = nest[i], nest[j]; wa, ha = part_bbox(a_[0]); wb, hb = part_bbox(b2[0])
            sep = max(b2[1]-(a_[1]+wa), a_[1]-(b2[1]+wb), b2[2]-(a_[2]+ha), a_[2]-(b2[2]+hb))
            assert sep >= GAP-1e-6, (a_, b2, sep)
assert sum(1 for k, *_ in NEST2 if k == 'S2') == 5 and sum(1 for k, *_ in NEST2 if k == 'S3') == 1
print(f'plate flat {PLEN:.1f} x {PWID:.0f}, shelf flat {XE:.1f} x {YE:.1f}')
print(f'mass plate {PLATE_MASS:.1f} kg, shelf {SHELF_MASS:.1f} kg, total about {TOTAL_MASS:.0f} kg (7.9 g/cm3, steel only)')
print(f'cut length plate {PLATE_CUT/1000:.2f} m, shelf {SHELF_CUT/1000:.2f} m, total {TOTAL_CUT/1000:.2f} m')

# ---------------- DXF ----------------
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); d.layers.add('SHEET', color=3); d.layers.add('BEND', color=5, linetype='DASHED')
    return d
def plate_entities(msp, ox, oy, rot):
    # rotation by +90 deg about the origin then shift: (x,y)->(y, -x)+ (0,OD)  keeps ccw orientation and bulge sign
    T = (lambda x, y: (ox+y, oy+OD-x)) if rot else (lambda x, y: (ox+x, oy+y))
    def poly(path):
        msp.add_lwpolyline([(*T(x, y), 0, 0, b if not rot else b) for x, y, b in path], format='xyseb', close=True, dxfattribs={'layer': 'CUT'})
    poly(pa)
    for s in SLOTS: poly(s)
    for x, y in HOLES_P + HOLES_TAB: msp.add_circle(T(x, y), FHOLE_P/2 if (x, y) in HOLES_P else TAB_HOLE/2, dxfattribs={'layer': 'CUT'})
    for y in [BODY_Y0 - BA_P/2]:
        for a, b_ in tabs: msp.add_line(T(a, y), T(b_, y), dxfattribs={'layer': 'BEND'})
def shelf_entities(msp, ox, oy, strap):
    msp.add_lwpolyline([(ox+x, oy+y) for x, y in list(shelf_outline.exterior.coords)[:-1]], close=True, dxfattribs={'layer': 'CUT'})
    for x, y in FH: msp.add_circle((ox+x, oy+y), FHOLE_S/2, dxfattribs={'layer': 'CUT'})
    if strap:
        for x, y in STRAP: msp.add_circle((ox+x, oy+y), 4.0, dxfattribs={'layer': 'CUT'})
    for xb in (X1+BA_S/2, X3+BA_S/2): msp.add_line((ox+xb, oy+Y2+RELIEF), (ox+xb, oy+Y3-RELIEF), dxfattribs={'layer': 'BEND'})
    for yb in (Y1+BA_S/2, Y3+BA_S/2): msp.add_line((ox+X2, oy+yb), (ox+X3, oy+yb), dxfattribs={'layer': 'BEND'})
d = new_doc(); plate_entities(d.modelspace(), 0, 0, False); d.saveas(f'{OUT}/{PN}_rev{REV}_P1_side-plate.dxf')
d = new_doc(); shelf_entities(d.modelspace(), 0, 0, False); d.saveas(f'{OUT}/{PN}_rev{REV}_P2_shelf.dxf')
d = new_doc(); shelf_entities(d.modelspace(), 0, 0, True); d.saveas(f'{OUT}/{PN}_rev{REV}_P3_top-shelf.dxf')
for k, nest in ((1, NEST1), (2, NEST2)):
    d = new_doc(); m = d.modelspace()
    m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
    for kind, x, y in nest:
        if kind == 'P1': plate_entities(m, x, y, True)
        else: shelf_entities(m, x, y, kind == 'S3')
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
    s += bi(X+2, Y+14, f'SIZE  {OH} x {OW} x {OD} mm (PROPOSED)', 'المقاس الكلي (مقترح)', 88, 2.2) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.2)
    s += bi(X+2, Y+25, f'MATERIAL  Stainless sheet, plates {TP} mm, shelves {TS} mm', 'الخامة: ستانلس، لوحان ٤ مم، أرفف ٣ مم', 88, 1.9) + bi(X+94, Y+25, 'FINISH  brushed stainless steel', 'التشطيب: ستانلس مصقول بالفرشاة', 88, 2.0)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.2) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.2)
    s += rect(X, Y-14, Wd, 12, .5, RED, '#fff')
    s += t(X+Wd/2, Y-8.6, 'DRAFT, not approved, not engineered', 2.9, 700, 'middle', RED) + t(X+Wd/2, Y-3.8, 'مسودة، غير معتمدة، غير مهندسة', 2.9, 700, 'middle', RED)
    return s + t(10, 14, title_en, 4.2, 700) + ar(410, 14, title_ar, 4.2, 700)
def sheet(n, te, ta, sc, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, te, ta, sc)}{body}</svg>'
im = Image.open(ROOT + '/images/OBJ-159.jpg').convert('RGB').crop((0, 0, 735, 1100)); im.thumbnail((420, 420))
b_ = io.BytesIO(); im.save(b_, 'JPEG', quality=70); PHOTO = 'data:image/jpeg;base64,' + base64.b64encode(b_.getvalue()).decode()


# ===== SHEET 1: views (1:12) =====
S = 1/12; ox, oy = 28, 38
def X(x): return ox + x*S
def Zf(z): return oy + (OH - z)*S           # z = height above floor
FOOT_X = TABL - 25                          # foot centre from the plate's outer face (tab leg 60, hole 25 from the tip)
b = t(10, 24, 'FRONT, SIDE and PLAN, 1:12', 2.6, 600) + ar(226, 24, 'منظر أمامي وجانبي وعلوي', 2.6, 600)
b += t(ox, oy-3, 'FRONT', 2.2, 600)
b += rect(X(0), Zf(OH), TP*S, SH*S, .3, INK, STEELD) + rect(X(OW-TP), Zf(OH), TP*S, SH*S, .3, INK, STEELD)
for h in SHELF_TOP_FLOOR: b += rect(X(TP), Zf(h), (OW-2*TP)*S, FL*S, .3, INK, FILL)
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
b += dim_h(XS(0), XS(OD), Zf(0)+7, f'{OD}', ext=Zf(0))
b += dim_v(XS(OD)+8, Zf(SHELF_TOP_FLOOR[1]), Zf(SHELF_TOP_FLOOR[0]), f'{PITCH}', ext=XS(OD))
# plan, below the front view
py = 232; ppx = 128
def XP(x): return ppx + x*S
b += t(ppx, py-3, 'PLAN (top shelf shown)', 2.2, 600)
b += rect(XP(0), py, OW*S, OD*S, .3, INK, FILL)
b += rect(XP(0), py, TP*S, OD*S, .3, INK, STEELD) + rect(XP(OW-TP), py, TP*S, OD*S, .3, INK, STEELD)
b += line(XP(TP), py+TS*S, XP(OW-TP), py+TS*S, .5, INK) + line(XP(TP), py+(OD-TS)*S, XP(OW-TP), py+(OD-TS)*S, .5, INK)
b += t(XP(OW/2), py+OD*S/2+1, 'front return at the bottom edge of the view', 1.4, 400, 'middle', HID) if False else ''
b += t(XP(OW)+2, py+2.2, 'rear', 1.8, 400, fill=HID) + t(XP(OW)+2, py+OD*S-.5, 'front', 1.8, 400, fill=HID)
b += dim_h(XP(0), XP(OW), py+OD*S+6, f'{OW}', ext=py+OD*S) + dim_v(XP(0)-6, py, py+OD*S, f'{OD}', ext=XP(0))
# dims on the front view
b += dim_v(ox-8, Zf(OH), Zf(0), f'{OH} overall (incl. feet)', ext=ox) + dim_v(ox-15, Zf(OH), Zf(FOOT), f'{SH} steel', ext=ox-1)
b += dim_h(X(0), X(OW), Zf(0)+7, f'{OW}', ext=Zf(0))
for h in SHELF_TOP_FLOOR:
    b += line(X(OW)+1, Zf(h), X(OW)+5, Zf(h), .15, DIM) + t(X(OW)+6, Zf(h)+.7, f'{h}', 1.8, 400, fill=DIM)
b += t(X(OW)+6, Zf(OH)-2.5, 'shelf tops', 1.6, 400, fill=HID) + t(X(OW)+6, Zf(OH)-.6, 'above floor', 1.6, 400, fill=HID)
b += balloon(X(OW/2), Zf(SHELF_TOP_FLOOR[2]-FL/2), 2) + balloon(XS(OD*0.22), Zf(1650), 1) + balloon(X(OW/2), Zf(SHELF_TOP_FLOOR[0]-FL/2), 3)
b += balloon(X(FOOT_X), Zf(FOOT/2)+7, 5, 2.4) + t(X(FOOT_X)+4, Zf(FOOT/2)+7.7, 'foot', 1.8, 400, fill=HID)
# key sizes, middle column
kx = 168
b += t(kx, 40, 'KEY SIZES (PROPOSED unless noted)', 2.2, 600) + ar(226, 44, 'المقاسات (مقترحة)', 2.0, 600)
ks = [f'Overall {OH} H x {OW} W x {OD} D  (height: Sabry)', f'Steel height {SH}; feet {FOOT} at mid adjustment', f'{NSH} shelves (Sabry), pitch {PITCH}, top face {SHELF_TOP_FLOOR[0]}',
      f'Clear width between plates {OW-2*TP}, shelf depth {OD}', f'Plates {TP} mm, shelves {TS} mm, folded stainless', f'Stadium slot {SLW} x {SLH}, one per bay, centred', f'Open below the lowest shelf: {SHELF_TOP_FLOOR[-1]-FL} from floor',
      f'Steel only about {TOTAL_MASS:.0f} kg (arithmetic, not Production)', 'Tip-over: wall strap (item 7) is part of the design']
for i, s_ in enumerate(ks): b += t(kx, 50 + i*4.3, s_, 1.8, 400)
# reference photo and colourway
rx = 238
ih = 150; wimg = ih*im.size[0]/im.size[1]
b += t(rx, 22, 'REFERENCE (idea only, third-party piece)', 2.4, 600) + ar(410, 22, 'المرجع (للفكرة فقط)', 2.4, 600)
b += f'<image x="{rx}" y="25" width="{wimg:.1f}" height="{ih:.1f}" href="{PHOTO}"/>' + rect(rx, 25, wimg, ih, .25, HID)
tx_ = rx + wimg + 4
for i, s_ in enumerate(["Another designer's piece. We keep the idea only:", 'two tall side plates with cut-outs, shelves between.', 'Ours is changed: stadium slots not circles, one per',
                        'bay not stacked, six shelves, folded steel shelves', 'not timber, taller, our own proportions.']):
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
b += dim_h(px0, px0+PLEN*S2, py0+OD*S2+6, f'{PLEN:.1f} flat length', ext=py0+OD*S2) + dim_v(px0-6, py0, py0+OD*S2, f'{OD}', ext=px0)
b += t(px0, py0+OD*S2+13, f'Tab tips at the left, top edge at the right, top corners R{R_TOP}. Thickness {TP}, steel height after folding {SH}.', 1.8, 400, fill=HID)
b += t(px0, py0+OD*S2+16.6, f'Two foot tabs {TABW} wide, folded inward 90 degrees, {TABL} outside leg, hole {TAB_HOLE} dia for an M8 weld nut. Assumed inside radius {TP}, K {KF}: allowance {BA_P:.1f}, setback {SB_P:.0f}.', 1.8, 400, fill=HID)
b += ar(410, py0+OD*S2+25, 'لسانان للأقدام يُطويان للداخل ٩٠ درجة. نصف قطر الثني ومعامل K افتراضيان.', 1.8, 400, HID)
b += balloon(px0+PLEN*S2*0.5, py0+OD*S2*0.5, 1)
# bay detail 1:5
D5 = .2; bx0, by0 = 28, 108
b += t(10, 94, 'BAY DETAIL, one shelf level of the plate, 1:5 (outer face)', 2.4, 600) + ar(122, 94, 'تفصيل مستوى رف واحد', 2.4, 600)
zb = SHELF_Z[2]
def MB(u, z): return (bx0 + (OD - u)*D5, by0 + (zb + 40 - z)*D5)
b += rect(bx0, by0, OD*D5, (PITCH+40)*D5, .3, INK, STEEL)
cu, cz = OD/2, zb - SLOT_OFF
b += poly([MB(x, y) for x, y in sample(stadium(cu, cz, SLW, SLH))], .3, INK, '#fff')
for u in HOLE_U: b += circ(*MB(u, zb - FHOLE_DROP), FHOLE_P/2*D5, .3, INK, '#fff')
b += line(*MB(0, zb), *MB(OD, zb), .2, HID, '2 1') + t(bx0+OD*D5+2, MB(0, zb)[1]+.8, 'shelf top face', 1.7, 400, fill=HID)
yb_ = by0 + (PITCH+40)*D5
b += dim_h(MB(OD, zb)[0], MB(0, zb)[0], by0-4, f'{OD}', ext=by0)
b += dim_h(MB(HOLE_U[0], zb)[0], MB(0, zb)[0], yb_+5, f'{HOLE_U[0]}', ext=yb_) + dim_h(MB(OD, zb)[0], MB(HOLE_U[1], zb)[0], yb_+5, f'{OD-HOLE_U[1]}', ext=yb_)
b += dim_v(bx0-5, MB(0, zb)[1], MB(0, zb-FHOLE_DROP)[1], f'{FHOLE_DROP}', ext=bx0) + dim_v(bx0-11, MB(0, zb)[1], MB(0, cz)[1], f'{SLOT_OFF} to slot centre', ext=bx0)
b += dim_h(MB(cu+SLW/2, cz)[0], MB(cu-SLW/2, cz)[0], MB(cu, cz)[1]+SLH*D5/2+5, f'{SLW}', ext=MB(cu, cz)[1]+SLH*D5/2) + dim_v(bx0+OD*D5+6, MB(0, cz+SLH/2)[1], MB(0, cz-SLH/2)[1], f'{SLH}', ext=bx0+OD*D5)
b += t(10, yb_+12, f'Fixing holes {FHOLE_P} dia, two per shelf level, {FHOLE_DROP} below the shelf top face. Slot ends are full radius.', 1.8, 400, fill=HID)
b += ar(110, yb_+16, 'ثقبان لكل مستوى رف. نهايتا الشق نصف دائريتان.', 1.8, 400, HID)
# shelf flat 1:4
S4_ = .25; sx_, sy_ = 128, 108
b += t(sx_-2, 94, 'ITEM 2  SHELF, flat pattern, 1:4  (qty 5)   ITEM 3  TOP SHELF (qty 1, two strap holes)', 2.2, 600) + ar(410, 94, 'بند ٢ الرف، بند ٣ الرف العلوي', 2.2, 600)
def MS(x, y): return (sx_ + x*S4_, sy_ + (YE - y)*S4_)
b += pathfill(sht_net, MS, .3, INK, STEEL)
for xb in (X1+BA_S/2, X3+BA_S/2): b += line(*MS(xb, Y2+RELIEF), *MS(xb, Y3-RELIEF), .25, RED, '2 1')
for yb in (Y1+BA_S/2, Y3+BA_S/2): b += line(*MS(X2, yb), *MS(X3, yb), .25, RED, '2 1')
b += balloon(*MS(XE/2, YE/2), 2)
b += t(MS(XE/2, 14)[0]-40, MS(XE/2, 14)[1]+1, 'rear lip, 2 strap holes dia 8 (item 3 only)', 1.7, 400, fill=HID)
b += dim_h(sx_, sx_+XE*S4_, sy_+YE*S4_+6, f'{XE:.1f}', ext=sy_+YE*S4_) + dim_v(sx_-6, sy_, sy_+YE*S4_, f'{YE:.1f}', ext=sx_)
b += t(sx_, sy_+YE*S4_+13, f'Finished {OW-2*TP} x {OD} x {TS}: side flanges {FL} (bolted to the plates), front return {FL} down, rear lip {FL} up. Folds red dashed.', 1.8, 400, fill=HID)
b += t(sx_, sy_+YE*S4_+17, f'Assumed inside radius {TS}, K {KF}: allowance {BA_S:.1f}, setback {SB_S:.0f}. Corner relief {RELIEF:.0f}. Clinch-nut holes {FHOLE_S} dia (indicative).', 1.8, 400, fill=HID)
b += ar(410, sy_+YE*S4_+13, 'الأرفف أربع ثنيات ٩٠ درجة. الأنصاف والمعامل افتراضية.', 1.8, 400, HID)
# data table
tbx = 262
rows = [('Plate finished mm', f'{OD} x {SH} x {TP}'), ('Plate flat mm', f'{PLEN:.1f} x {PWID:.0f} x {TP}'), ('Plate steel mass', f'{PLATE_MASS:.1f} kg'), ('Shelf finished mm', f'{OW-2*TP} x {OD} x {TS}'),
        ('Shelf flat mm', f'{XE:.1f} x {YE:.1f} x {TS}'), ('Shelf steel mass', f'{SHELF_MASS:.1f} kg'), ('Cut length plate / shelf', f'{PLATE_CUT/1000:.2f} / {SHELF_CUT/1000:.2f} m'), ('Steel total (2 + 6 parts)', f'about {TOTAL_MASS:.0f} kg')]
b += t(tbx, 32, 'DATA', 2.6, 600) + ar(410, 32, 'بيانات', 2.6, 600)
for i, (k, v) in enumerate(rows):
    yy = 39 + i*5.6
    b += line(tbx, yy+1.8, 410, yy+1.8, .15, HID) + t(tbx+1, yy, k, 2.0) + t(409, yy, v, 2.0, 600, 'end')
b += t(tbx, 84, 'Masses and cut lengths are arithmetic from the drawing (7.9 g/cm3), not Production figures.', 1.7, 400, fill=HID)
sh2 = sheet(2, 'PART SHEET', 'ورقة الأجزاء', '1:10 / 1:5 / 1:4', b)

# ===== SHEET 3: assembly =====
b = t(10, 22, 'EXPLODED VIEW (oblique, about 1:12)', 2.6, 600) + ar(410, 22, 'منظر مفكك', 2.6, 600)
S3 = 1/12; ax0, ay0 = 42, 36; K3 = .32; E = 170
def P3(x, y, z): return (ax0 + (x + K3*y*.9)*S3, ay0 + (OH - z - K3*y*.55)*S3)
def plate3(xoff):
    out = poly([P3(xoff, 0, FOOT), P3(xoff, OD, FOOT), P3(xoff, OD, OH), P3(xoff, 0, OH)], .35, INK, STEEL)
    for h in SHELF_TOP_FLOOR:
        out += poly([P3(xoff, u, zz) for u, zz in sample(stadium(OD/2, h - SLOT_OFF, SLW, SLH))], .25, INK, '#fff')
    return out
b += plate3(-E)
for h in SHELF_TOP_FLOOR:
    b += poly([P3(TP, 0, h), P3(OW-TP, 0, h), P3(OW-TP, OD, h), P3(TP, OD, h)], .3, INK, FILL2)
    b += poly([P3(TP, 0, h), P3(OW-TP, 0, h), P3(OW-TP, 0, h-FL), P3(TP, 0, h-FL)], .3, INK, FILL)
b += plate3(OW - TP + E)
for h in (SHELF_TOP_FLOOR[0], SHELF_TOP_FLOOR[-1]):
    for u in HOLE_U:
        b += line(*P3(TP, u, h-FHOLE_DROP), *P3(-E, u, h-FHOLE_DROP), .2, DIM, '1.5 1') + line(*P3(OW-TP, u, h-FHOLE_DROP), *P3(OW-TP+E, u, h-FHOLE_DROP), .2, DIM, '1.5 1')
b += balloon(*P3(-E, OD*.5, 1500), 1) + balloon(*P3(OW/2, OD*.5, SHELF_TOP_FLOOR[2]), 2) + balloon(*P3(OW/2, OD*.5, SHELF_TOP_FLOOR[0]), 3) + balloon(*P3(OW-TP+E, OD*.5, 1000), 1)
b += balloon(*P3(-E+FOOT_X, 0, FOOT/2), 5, 2.4)
b += t(10, 222, 'Plates apart; shelves in place. Dashed blue lines: the fixing holes of the top and bottom shelf lining up with the plate holes. Shelves 2 to 5 fix the same way.', 1.8, 400, fill=HID)
b += t(10, 226, 'The feet (item 5) screw into the weld nuts (item 6) on the foot tabs. The wall strap (item 7) fixes to the two holes in the top shelf rear lip.', 1.8, 400, fill=HID)
b += ar(225, 222, 'الخطوط المتقطعة: محاذاة ثقوب التثبيت.', 1.8, 400, HID)
dx0, dy0 = 245, 40; D = 4
b += t(dx0-2, 30, 'FIXING DETAIL, section through a shelf end, 4:1 (schematic)', 2.2, 600) + ar(410, 30, 'تفصيل التثبيت (تخطيطي)', 2.2, 600)
b += rect(dx0, dy0, TP*D, 36, .35, INK, STEEL) + rect(dx0+TP*D, dy0+8, TS*D, 26, .35, INK, FILL2) + rect(dx0+TP*D, dy0+8, 38, TS*D, .35, INK, FILL2)
b += rect(dx0-3.5, dy0+8+16-1.6, 3.5, 3.2, .3, INK, '#666') + rect(dx0+TP*D+TS*D, dy0+8+16-2.4, 3, 4.8, .3, INK, '#888')
b += line(dx0-6, dy0+8+16, dx0+TP*D+TS*D+10, dy0+8+16, .2, DIM, '2 1')
b += t(dx0+TP*D+TS*D+12, dy0+8+16+.8, 'M6 button-head screw + clinch nut (indicative)', 1.7, 400, fill=DIM) + t(dx0+TP*D+TS*D+12, dy0+8+16+4, 'Production decides screw, nut, torque.', 1.7, 400, fill=HID)
b += t(dx0-2, dy0-3, f'plate {TP}', 1.7, 400, fill=HID) + t(dx0+TP*D+2, dy0+4, f'shelf {TS}', 1.7, 400, fill=HID)
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
steps = [('Cut and fold the plates and six shelves, finish, weld the nuts, fit the feet.', 'قص وثني اللوحين والأرفف وتركيب الأقدام.'),
         ('Lay one plate flat, outer face down.', 'ضع لوحاً مسطحاً بوجهه الخارجي للأسفل.'),
         ('Stand the shelves on it, holes to holes. Four screws per shelf level.', 'ثبّت كل مستوى رف بأربعة براغٍ.'),
         ('Fit the second plate and its screws. Stand up with two people.', 'ركّب اللوح الثاني ثم أقم القطعة بشخصين.'),
         ('Level on the feet. Fix the strap to the wall. Check all screws.', 'اضبط الأقدام وثبّت الحزام وافحص البراغي.')]
for i, (en, a) in enumerate(steps):
    yy = sq0 + 8 + i*8
    b += balloon(248, yy-1, i+1, 2.4) + t(254, yy, en, 1.9) + ar(410, yy+3.6, a, 1.9)
b += t(245, sq0+50, "Welds, jigs and screw torque are Production's. Nothing here claims strength or stability.", 1.8, 400, fill=HID)
sh3 = sheet(3, 'ASSEMBLY', 'التجميع', '1:12 / detail', b)

# ===== SHEET 4: cutting layout (two assumed sheets) =====
S4 = .08; ox4, oy4 = 22, 40
def nest_svg(nest, ox_, oy_, title_en, title_ar):
    s = t(ox_, oy_-2.5, title_en, 2.2, 600) + ar(ox_+SHEET_L*S4, oy_-2.5, title_ar, 2.2, 600)
    s += rect(ox_, oy_, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6')
    for kind, x, y in nest:
        if kind == 'P1':
            s += pathfill(plate_net, lambda xx, yy: (ox_+(x+yy)*S4, oy_+(SHEET_W-(y+OD-xx))*S4), .2, INK, FILL)
            s += t(ox_+(x+PLEN/2)*S4, oy_+(SHEET_W-(y+OD/2))*S4+1.2, '1', 3.4, 600, 'middle', '#555')
        else:
            sp = sht_net if kind == 'S3' else sh_net
            s += pathfill(sp, lambda xx, yy: (ox_+(x+xx)*S4, oy_+(SHEET_W-(y+yy))*S4), .2, INK, FILL)
            s += t(ox_+(x+XE/2)*S4, oy_+(SHEET_W-(y+YE/2))*S4+1.2, '3' if kind == 'S3' else '2', 3.4, 600, 'middle', '#555')
    s += dim_h(ox_, ox_+SHEET_L*S4, oy_+SHEET_W*S4+6, f'{SHEET_L}', ext=oy_+SHEET_W*S4) + dim_v(ox_-6, oy_, oy_+SHEET_W*S4, f'{SHEET_W}', ext=ox_)
    return s
b = t(10, 22, f'Two assumed sheets {SHEET_L} x {SHEET_W}. Plates {TP} mm and shelves {TS} mm are different stock, so they cannot share a sheet.', 2.1, 600) + ar(410, 22, 'لوحان مفترضان للقص', 2.1, 600)
b += nest_svg(NEST1, ox4, oy4, f'SHEET A, {TP} mm stainless: 2 x item 1', 'اللوح أ')
b += nest_svg(NEST2, ox4, oy4+112, f'SHEET B, {TS} mm stainless: 5 x item 2, 1 x item 3', 'اللوح ب')
tx0 = 232
b += t(tx0, 46, 'SHEET A', 2.4, 600) + t(tx0, 51, f'2 plates, {GAP} mm spacing, long side along the sheet', 1.9) + t(tx0, 55, f'length (grain), cutting length {2*PLATE_CUT/1000:.2f} m.', 1.9)
b += t(tx0, 59, 'Most of this sheet is free. No offcut use is claimed.', 1.9, 400, fill=HID)
b += t(tx0, 158, 'SHEET B', 2.4, 600) + t(tx0, 163, f'6 shelves in 3 rows of 2, {GAP} mm spacing, cutting', 1.9) + t(tx0, 167, f'length {(5*SHELF_CUT+SHELFT_CUT)/1000:.2f} m.', 1.9)
b += t(tx0, 171, 'Total for one piece: 2 sheets, cutting length', 1.9) + t(tx0, 175, f'{TOTAL_CUT/1000:.2f} m (plates and shelves).', 2.1, 600)
b += ar(410, 46, 'اللوحان في اتجاه الطول', 1.9) + ar(410, 158, 'ستة أرفف في ثلاثة صفوف', 1.9) + ar(410, 175, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.1, 600)
sh4 = sheet(4, 'CUTTING LAYOUT', 'مخطط القص', '1:12.5', b)

# ===== SHEET 5: BOM and notes =====
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + ar(410, 28, 'قائمة المواد', 2.8, 600) + rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 130, 150, 190], ['ITEM', 'PART / الجزء', 'QTY', 'MATERIAL / الخامة', '']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Side plate, laser cut, 2 foot tabs folded', 'لوح جانبي', '2', f'Stainless steel sheet {TP} mm, brushed (proposed)'),
       ('2', 'Shelf, laser cut, 4 folds', 'رف', '5', f'Stainless steel sheet {TS} mm, brushed (proposed)'),
       ('3', 'Top shelf (item 2 + 2 strap holes)', 'الرف العلوي', '1', f'Stainless steel sheet {TS} mm, brushed (proposed)'),
       ('4', 'Screw M6 button head + clinch nut (indicative)', 'برغي ومسمار ربط', '24', 'Stainless steel, bought in'),
       ('5', 'Levelling foot M8, 30 pad', 'قدم ضبط', '4', 'Bought in'),
       ('6', 'Weld nut M8 (on the foot tab)', 'صامولة لحام', '4', 'Stainless steel, bought in'),
       ('7', 'Anti-tip wall strap kit', 'حزام منع السقوط', '1', 'Bought in, wall fixings by the installer')]
for i, (n_, en, a, q, m) in enumerate(bom):
    yy = 44 + i*6.2
    b += line(10, yy+2, 410, yy+2, .15, HID) + t(12, yy, n_, 2.3) + t(24, yy, en, 2.2) + ar(128, yy, a, 2.2) + t(130, yy, q, 2.2) + t(150, yy, m, 2.2)
b += t(10, 96, 'NOTES', 2.8, 600) + ar(410, 96, 'ملاحظات', 2.8, 600)
notes = [("Sabry (12 Nov 2026): own redesign approved, Furniture, brushed stainless, height 210 to 220 cm (2150 drawn), six shelves. All other sizes are PROPOSED by Claude, to confirm.", 'التصميم الخاص معتمد. الارتفاع وعدد الأرفف من سبري والباقي مقترح.'),
         ('The reference photo is another designer\'s piece. We keep the idea only (two tall plates with cut-outs, shelves between). Our slots, count, proportions and shelves are different.', 'المرجع قطعة مصمم آخر. نأخذ الفكرة فقط.'),
         ('Thickness, folds, radii, tolerances, fixings, weld nuts, foot range, sheet size and finish are Production\'s to decide. Bend allowances here are assumptions.', 'السماكة والثنيات والتثبيت يقررها التصنيع.'),
         (f'Steel alone is about {TOTAL_MASS:.0f} kg (arithmetic). Lifting, packing and the 15 kg shipping band need Production\'s figures. Ships flat in parts, assembled on site.', f'وزن الفولاذ نحو {TOTAL_MASS:.0f} كجم، يحتاج تأكيد التصنيع.'),
         ('Tip-over: the wall strap (item 7) is part of the design. No claim about stability or shelf loading is made. Not engineered.', 'حزام الحائط جزء من التصميم. لا ادعاءات عن الثبات أو التحميل.'),
         ('Mirror finish is not proposed; brushed only (Sabry, same family as OBJ-190). No costs or prices on this drawing.', 'التشطيب مصقول بالفرشاة فقط. لا أسعار.'),
         ('Arabic wording is a draft for a technical reader.', 'الصياغة العربية مسودة.')]
for i, (en, a) in enumerate(notes):
    yy = 106 + i*14
    cut = 150 if len(en) > 150 else len(en)
    l1 = en[:cut].rsplit(' ', 1)[0] if len(en) > 150 else en
    b += t(12, yy, f'{i+1}.', 2.3, 600) + t(18, yy, l1, 2.1) + (t(18, yy+4, en[len(l1):].strip(), 2.1) if len(en) > 150 else '') + ar(410, yy, a, 2.1)
sh5 = sheet(5, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)
for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1): open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('written')
