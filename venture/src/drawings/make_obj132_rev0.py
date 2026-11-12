"""OBJ-132: set of three brushed-metal wall plates with a round window. Production drawing set, REV 0 (DRAFT).
Run: python3 make_obj132_rev0.py <repo root>   then: NODE_PATH=/opt/node22/lib/node_modules node make_pdf.js <dir> OBJ-132 0
Reference: images/OBJ-132.jpg (third-party photo, idea only). Photos shown in its windows are the reference's, NOT ours, and are not used.
ALL SIZES ARE PROPOSED BY CLAUDE (Sabry: "set of 3, draw", 12 Nov 2026), checked against proportions measured on the photo. To confirm.
Arabic is a draft. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
from shapely.geometry import Polygon, Point, box
from shapely import affinity
from shapely.ops import unary_union
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-132'; os.makedirs(OUT, exist_ok=True)
REV = 0; DATE = '12 Nov 2026'; PN = 'OBJ-132'
# ---- proposed sizes (mm) ----
PW, PH, T = 300, 330, 2          # face plate width, height, sheet thickness
WIN = 130                        # window diameter, centred on the plate (measured on the photo: centred)
WCX, WCY = PW/2, PH/2            # window centre, from the top-left of the plate
GAP = 60                         # vertical space between plates
SET_H = 3*PH + 2*GAP             # 1110
FRD = 13                         # frame strip height behind the face plate -> plate stands FRD+T = 15 off the wall
STAND = FRD + T
INSET = 10                       # frame sits 10 mm inside the plate edge (hidden)
FO_W, FO_H = PW-2*INSET, PH-2*INSET   # frame outside 280 x 310
LONG, SHORT = FO_H, FO_W-2*T          # strips: two 310 long, two 276 butted between
HW, HH = 274, 40                 # hanger plate
HTOP = 14                        # hanger top, from the plate top edge
KX, KHEAD, KSLOT, KSHAFT = 75, 9, 12, 5   # keyhole: centres +-75 from the centreline, head hole 9, slot 12 up, slot width 5
KY = HTOP + HH - 14              # head-hole centre from plate top = 40
SCREW_Y = KY - KSLOT             # screw rests here when hung = 28 from plate top
DISC, RING_OD, RING_ID, PCD, STUD_HOLE, DISC_T = 150, 176, 136, 160, 3.4, 3
SHEET_L, SHEET_W, GP = 2500, 1250, 10
ZW = 5                           # hanger rear face is 5 mm off the wall (room for the screw heads)

# ---- parts as shapely, in mm, y up from the part's own bottom-left ----
def keyhole(cx, cy_head):
    return unary_union([Point(cx, cy_head).buffer(KHEAD/2, 32),
                        box(cx-KSHAFT/2, cy_head, cx+KSHAFT/2, cy_head+KSLOT).union(Point(cx, cy_head+KSLOT).buffer(KSHAFT/2, 32))])
plate_outer = box(0, 0, PW, PH)
plate = plate_outer.difference(Point(WCX, WCY).buffer(WIN/2, 128))
frame_long = box(0, 0, LONG, FRD); frame_short = box(0, 0, SHORT, FRD)
hanger = box(0, 0, HW, HH)
for sx in (-KX, KX): hanger = hanger.difference(keyhole(HW/2+sx, 14))
ring = Point(0, 0).buffer(RING_OD/2, 128).difference(Point(0, 0).buffer(RING_ID/2, 128))
studs = [(PCD/2*math.cos(math.radians(a)), PCD/2*math.sin(math.radians(a))) for a in (90, 210, 330)]
for sx_, sy_ in studs: ring = ring.difference(Point(sx_, sy_).buffer(STUD_HOLE/2, 24))
assert ring.geom_type == 'Polygon' and len(ring.interiors) == 4
# checks
assert math.isclose(SET_H, 1110) and STAND == 15
assert RING_OD/2 + 0 < min(WCY, PH-WCY) - 0 and WCY - RING_OD/2 > HTOP + HH          # ring clear of the hanger plate
assert PCD/2 - STUD_HOLE/2 > DISC/2 and PCD/2 + STUD_HOLE/2 < RING_OD/2               # studs sit outside the disc, inside the ring
assert HW < FO_W - 2*T and FO_W == 280 and FO_H == 310
assert DISC > WIN and RING_ID < DISC and RING_ID > WIN
assert SCREW_Y == 28
print('plate cut length', round(plate.length, 1), 'hanger', round(hanger.length, 1), 'ring', round(ring.length, 1))

# ---- nest ----
items = [('1', plate, 3), ('2L', frame_long, 6), ('2S', frame_short, 6), ('3', hanger, 3), ('4', ring, 3)]
placed = []   # (label, polygon at position)
x = y = GP; rowh = 0
def norm(g): b = g.bounds; return affinity.translate(g, -b[0], -b[1])
order = sorted(items, key=lambda it: -norm(it[1]).bounds[3])
for lab, g, q in order:
    g = norm(g); w, h = g.bounds[2], g.bounds[3]
    for _ in range(q):
        if x + w + GP > SHEET_L: x = GP; y += rowh + GP; rowh = 0
        placed.append((lab, affinity.translate(g, x, y))); x += w + GP; rowh = max(rowh, h)
assert y + rowh + GP <= SHEET_W, (y, rowh)
sheet_poly = box(0, 0, SHEET_L, SHEET_W)
for i, (la, a) in enumerate(placed):
    assert sheet_poly.contains(a)
    for lb, b_ in placed[i+1:]:
        assert a.buffer(GP/2 - 1e-6).disjoint(b_.buffer(GP/2 - 1e-6)) or a.distance(b_) >= GP - 1e-6, (la, lb, a.distance(b_))
TOTAL_CUT = sum(g.length for _, g in placed)
ext = unary_union([g for _, g in placed]).bounds
print('nest ok', len(placed), 'parts; used', round(ext[2]), 'x', round(ext[3]), 'cut length m', round(TOTAL_CUT/1000, 2))

# ---- DXF ----
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4; d.layers.add('CUT', color=7); d.layers.add('SHEET', color=3); return d
def add_geom(msp, g, ox=0, oy=0, circ_centre=None):
    for ring_ in [g.exterior] + list(g.interiors):
        pts = [(ox+px, oy+py) for px, py in ring_.coords[:-1]]
        msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'CUT'})
def add_part(msp, lab, g, ox, oy):
    """Write the part with true CIRCLEs where the part has round holes/outline; keyholes stay polylines."""
    b = g.bounds
    if lab == '1':
        msp.add_lwpolyline([(ox, oy), (ox+PW, oy), (ox+PW, oy+PH), (ox, oy+PH)], close=True, dxfattribs={'layer': 'CUT'})
        msp.add_circle((ox+WCX, oy+WCY), WIN/2, dxfattribs={'layer': 'CUT'})
    elif lab == '4':
        cx, cy = ox+RING_OD/2, oy+RING_OD/2
        msp.add_circle((cx, cy), RING_OD/2, dxfattribs={'layer': 'CUT'}); msp.add_circle((cx, cy), RING_ID/2, dxfattribs={'layer': 'CUT'})
        for sx_, sy_ in studs: msp.add_circle((cx+sx_, cy+sy_), STUD_HOLE/2, dxfattribs={'layer': 'CUT'})
    elif lab == '3':
        msp.add_lwpolyline([(ox, oy), (ox+HW, oy), (ox+HW, oy+HH), (ox, oy+HH)], close=True, dxfattribs={'layer': 'CUT'})
        for sx in (-KX, KX): add_geom(msp, Polygon(keyhole(HW/2+sx, 14).exterior.coords), ox, oy)
    else:
        w, h = b[2]-b[0], b[3]-b[1]
        msp.add_lwpolyline([(ox, oy), (ox+w, oy), (ox+w, oy+h), (ox, oy+h)], close=True, dxfattribs={'layer': 'CUT'})
names = {'1': 'P1_face-plate', '2L': 'P2_frame-strip-long', '2S': 'P3_frame-strip-short', '3': 'P4_hanger-plate', '4': 'P5_retaining-ring'}
base = {'1': plate, '2L': frame_long, '2S': frame_short, '3': hanger, '4': ring}
for lab, g in base.items():
    d = new_doc(); add_part(d.modelspace(), lab, norm(g), 0, 0); d.saveas(f'{OUT}/{PN}_rev{REV}_{names[lab]}.dxf')
d = new_doc(); m = d.modelspace()
m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
for lab, g in placed: add_part(m, lab, g, g.bounds[0], g.bounds[1])
d.saveas(f'{OUT}/{PN}_rev{REV}_nest_{SHEET_L}x{SHEET_W}.dxf')

# ---- SVG helpers ----
FONT = "DejaVu Sans, Inter, Arial, sans-serif"
INK, DIM, HID, FILL, FILL2, RED = '#161616', '#2a4a7a', '#7a7a7a', '#f1efe9', '#dcd9d0', '#b3261e'
STEEL = '#b9bbbc'
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;')
def t(x, y, s, size=2.6, w=400, anchor='start', fill=INK, extra=''):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size}" font-weight="{w}" text-anchor="{anchor}" fill="{fill}"{extra}>{esc(s)}</text>'
def ar(x, y, s, size=2.6, w=400, fill=INK): return t(x, y, s, size, w, 'end', fill)
def bi(x, y, en, a, wd, size=2.6, w=400, fill=INK): return t(x, y, en, size, w, fill=fill) + t(x+wd, y+size*1.3, a, size, w, 'end', fill)
def line(x1, y1, x2, y2, sw=.3, col=INK, dash=None):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def rect(x, y, w, h, sw=.35, col=INK, fill='none', dash=None):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def circ(x, y, r, sw=.35, col=INK, fill='none', dash=None):
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def poly(pts, sw=.35, col=INK, fill='none', dash=None):
    return '<polygon points="' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts) + f'" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def arrow(x, y, dx, dy):
    n = math.hypot(dx, dy); ux, uy = dx/n, dy/n
    return f'<polygon points="{x:.2f},{y:.2f} {x-ux*2+uy*.7:.2f},{y-uy*2-ux*.7:.2f} {x-ux*2-uy*.7:.2f},{y-uy*2+ux*.7:.2f}" fill="{DIM}"/>'
def dim_h(x1, x2, y, label, ext=None, off=1):
    s = line(x1, y, x2, y, .2, DIM) + arrow(x1, y, 1, 0) + arrow(x2, y, -1, 0)
    if ext is not None: s += line(x1, ext, x1, y+(2 if y > ext else -2), .15, DIM) + line(x2, ext, x2, y+(2 if y > ext else -2), .15, DIM)
    return s + t((x1+x2)/2, y-off, label, 2.3, 500, 'middle', DIM)
def dim_v(x, y1, y2, label, ext=None):
    s = line(x, y1, x, y2, .2, DIM) + arrow(x, y1, 0, 1) + arrow(x, y2, 0, -1)
    if ext is not None: s += line(ext, y1, x+(2 if x > ext else -2), y1, .15, DIM) + line(ext, y2, x+(2 if x > ext else -2), y2, .15, DIM)
    return s + f'<text transform="translate({x-1:.2f} {(y1+y2)/2:.2f}) rotate(-90)" font-family="{FONT}" font-size="2.3" font-weight="500" text-anchor="middle" fill="{DIM}">{esc(label)}</text>'
def balloon(x, y, n):
    return circ(x, y, 3.2, .3, INK, '#fff') + t(x, y+1.1, str(n), 3, 600, 'middle')
N = 6
def frame(n, title_en, title_ar, scale):
    s = rect(5, 5, 410, 287, .5) + rect(7, 7, 406, 283, .2)
    X, Y, Wd = 228, 247, 185
    s += rect(X, Y, Wd, 41, .4, fill='#fff')
    s += line(X, Y+9, X+Wd, Y+9, .25) + line(X, Y+20, X+Wd, Y+20, .25) + line(X, Y+31, X+Wd, Y+31, .25) + line(X+92, Y+9, X+92, Y+41, .25)
    s += bi(X+2, Y+4, f'{PN}   Wall plates, set of three', 'ثلاث لوحات جدارية بنافذة دائرية', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  {PW} x {PH} x {T} mm each (PROPOSED)', 'مقاس اللوحة (مقترح)', 88, 2.1) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, 'MATERIAL  Stainless steel sheet, 2 mm proposed', 'الخامة: ستانلس ستيل ٢ مم مقترح', 88, 2.0) + bi(X+94, Y+25, 'FINISH  Brushed stainless (exposed metal)', 'التشطيب: ستانلس مصقول بالفرشاة', 88, 2.0)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, RED, '#fff')
    s += t(X+Wd/2, Y-8.6, 'DRAFT, not approved, not engineered', 2.9, 700, 'middle', RED) + t(X+Wd/2, Y-3.8, 'مسودة، غير معتمدة، غير مهندسة', 2.9, 700, 'middle', RED)
    return s + t(10, 14, title_en, 4.2, 700) + ar(410, 14, title_ar, 4.2, 700)
def sheet(n, te, ta, sc, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, te, ta, sc)}{body}</svg>'
def note(x, y, en, a, xr=None, size=2.0):
    s = t(x, y, en, size, 400, fill=HID)
    if a: s += ar(xr or 410, y+4, a, size, 400, HID)
    return s
im = Image.open(ROOT + '/images/OBJ-132.jpg').convert('RGB'); im.thumbnail((420, 560))
b_ = io.BytesIO(); im.save(b_, 'JPEG', quality=70); PHOTO = 'data:image/jpeg;base64,' + base64.b64encode(b_.getvalue()).decode()

def plate_front(ox, oy, S, hidden=True, dims=True):
    """Front elevation of one plate, top-left at (ox, oy), scale S sheet-mm per mm."""
    s = rect(ox, oy, PW*S, PH*S, .5, INK, FILL)
    s += circ(ox+WCX*S, oy+WCY*S, WIN/2*S, .5, INK, '#fff')
    if hidden:
        s += rect(ox+INSET*S, oy+INSET*S, FO_W*S, FO_H*S, .25, HID, 'none', '1.6 1')
        s += rect(ox+(PW-HW)/2*S, oy+HTOP*S, HW*S, HH*S, .25, HID, 'none', '1.6 1')
        s += circ(ox+WCX*S, oy+WCY*S, DISC/2*S, .25, HID, 'none', '1.6 1') + circ(ox+WCX*S, oy+WCY*S, RING_OD/2*S, .25, HID, 'none', '1.6 1')
        for sx in (-KX, KX): s += circ(ox+(WCX+sx)*S, oy+(KY)*S, KHEAD/2*S, .25, HID, 'none', '1.2 .8')
    return s

# ===== SHEET 1: views =====
S = .5; ox, oy = 28, 36
b = t(10, 24, 'FRONT, one plate, 1:2', 2.6, 600) + ar(200, 24, 'منظر أمامي للوحة واحدة', 2.6, 600)
b += plate_front(ox, oy, S)
b += dim_h(ox, ox+PW*S, oy+PH*S+8, f'{PW}', ext=oy+PH*S) + dim_v(ox-8, oy, oy+PH*S, f'{PH}', ext=ox)
b += dim_h(ox, ox+WCX*S, oy-6, f'{WCX:.0f}', ext=oy) + dim_h(ox+WCX*S, ox+PW*S, oy-6, f'{PW-WCX:.0f}', ext=oy)
b += dim_v(ox+PW*S+8, oy, oy+WCY*S, f'{WCY:.0f}', ext=ox+PW*S) + dim_v(ox+PW*S+8, oy+WCY*S, oy+PH*S, f'{PH-WCY:.0f}', ext=ox+PW*S)
b += t(ox+WCX*S+WIN/2*S*0.72, oy+WCY*S-WIN/2*S*0.72-1, f'window {WIN}', 2.3, 600, fill=RED)
b += t(ox, oy+PH*S+16, 'Solid lines: face plate (item 1). Dashed: hidden parts behind it: frame (2), hanger plate (3), disc (5), ring (4).', 2.0, 400, fill=HID)
b += ar(205, oy+PH*S+21, 'الخطوط المتقطعة: الأجزاء الخلفية المخفية.', 2.0, 400, HID)
b += t(ox, oy+PH*S+26, 'Window is centred: measured on the photo, the window centre sits on the plate centre.', 2.0, 400, fill=HID)
# side view
sx0 = 224
b += t(sx0-14, 24, 'SIDE, 1:2', 2.6, 600)
side_y = oy
b += rect(sx0, side_y, STAND*S, PH*S, .45, INK, FILL) + line(sx0-4, side_y-3, sx0-4, side_y+PH*S+3, .5, INK)
b += rect(sx0+FRD*S, side_y, T*S, PH*S, .45, INK, STEEL)
b += t(sx0-12, side_y+PH*S+8, 'wall', 2.0, 400, fill=HID)
b += dim_h(sx0, sx0+STAND*S, side_y+PH*S+8, f'{STAND}', ext=side_y+PH*S, off=-4)
b += t(205, oy+PH*S+16, 'Plate stands 15 off the wall', 2.0, 400, fill=HID) + t(205, oy+PH*S+19.6, '(13 frame + 2 plate), proposed.', 2.0, 400, fill=HID)
# reference photo
rx = 262; iw = 82; ih = iw*im.size[1]/im.size[0]
b += t(rx, 24, 'REFERENCE (idea only, not ours)', 2.4, 600)
b += f'<image x="{rx}" y="27" width="{iw}" height="{ih:.1f}" href="{PHOTO}"/>' + rect(rx, 27, iw, ih, .25, HID)
b += ar(410, 24, 'المرجع (للفكرة فقط)', 2.4, 600)
b += t(rx+iw+3, 33, 'Third-party photo. The pictures', 1.9, 400, fill=HID) + t(rx+iw+3, 36.6, 'in its windows are NOT ours', 1.9, 400, fill=HID) + t(rx+iw+3, 40.2, 'and are not used. Our window', 1.9, 400, fill=HID) + t(rx+iw+3, 43.8, 'takes a customer-supplied print', 1.9, 400, fill=HID) + t(rx+iw+3, 47.4, 'or a neutral insert.', 1.9, 400, fill=HID)
b += ar(410, 56, 'صور النوافذ في المرجع ليست لنا ولا تُستخدم.', 1.9, 400, HID)
b += t(rx+iw+3, 64, 'Measured on the photo (approx.):', 1.9, 600, fill=HID) + t(rx+iw+3, 67.6, 'plate 1.09 high : 1 wide (ours 1.10)', 1.9, 400, fill=HID) + t(rx+iw+3, 71.2, 'window 0.42 of plate width (ours 0.43)', 1.9, 400, fill=HID) + t(rx+iw+3, 74.8, 'gap 0.17 of plate height (ours 0.18)', 1.9, 400, fill=HID)
cy0 = 27+ih+8
b += t(rx, cy0, 'COLOURWAY', 2.6, 600) + ar(410, cy0, 'التشطيب', 2.6, 600)
b += rect(rx, cy0+3, 22, 14, .3, INK, STEEL) + t(rx+25, cy0+8, 'Brushed stainless steel', 2.3, 600) + t(rx+25, cy0+12, 'Exposed metal, no paint. Grain direction', 1.9, 400, fill=HID) + t(rx+25, cy0+15.6, 'across the width (to confirm).', 1.9, 400, fill=HID)
b += t(rx, cy0+24, 'Swatch is indicative. Brushed is the finish in the reference. Mirror is not proposed.', 1.9, 400, fill=HID)
b += t(rx, cy0+30, 'INSERT (behind the window): customer-supplied print, or a neutral disc.', 1.9, 600) + ar(410, cy0+34, 'الإدراج: طباعة من العميل أو قرص محايد.', 1.9, 400)
sh1 = sheet(1, 'VIEWS', 'المناظر', '1:2', b)

# ===== SHEET 2: part sheet =====
S2 = .5; ox2, oy2 = 28, 34
b = t(10, 24, 'ITEM 1  FACE PLATE, flat pattern, 1:2   (quantity 3, identical)', 2.5, 600) + ar(205, 24, 'بند ١، لوح أمامي، العدد ٣', 2.5, 600)
b += rect(ox2, oy2, PW*S2, PH*S2, .5, INK, FILL) + circ(ox2+WCX*S2, oy2+WCY*S2, WIN/2*S2, .5, INK, '#fff')
b += line(ox2+WCX*S2-4, oy2+WCY*S2, ox2+WCX*S2+4, oy2+WCY*S2, .2, RED) + line(ox2+WCX*S2, oy2+WCY*S2-4, ox2+WCX*S2, oy2+WCY*S2+4, .2, RED)
b += balloon(ox2+30*S2, oy2+30*S2, 1)
b += dim_h(ox2, ox2+PW*S2, oy2+PH*S2+8, f'{PW}', ext=oy2+PH*S2) + dim_v(ox2-8, oy2, oy2+PH*S2, f'{PH}', ext=ox2) + dim_v(ox2+PW*S2+8, oy2, oy2+WCY*S2, f'{WCY:.0f} to window centre', ext=ox2+PW*S2)
b += t(ox2+WCX*S2+WIN/2*S2*.75, oy2+WCY*S2+WIN/2*S2*.9+5, f'hole {WIN}', 2.3, 600, fill=RED)
b += t(ox2, oy2+PH*S2+16, 'Thickness 2 (proposed). Square corners, crisp edge as in the reference; edge break is Production\'s.', 2.0, 400, fill=HID)
b += t(ox2, oy2+PH*S2+20.5, 'Brush the face before or after cutting, Production decides; keep the protective film on the face.', 2.0, 400, fill=HID)
b += ar(205, oy2+PH*S2+25, 'حواف حادة كما في المرجع. القرار للتصنيع.', 2.0, 400, HID)
rx2 = 215
b += t(rx2, 24, 'ITEM 4  RETAINING RING, 1:2  (qty 3)', 2.5, 600) + ar(410, 24, 'بند ٤، حلقة تثبيت، العدد ٣', 2.5, 600)
rc = (rx2+RING_OD/2*S2+8, 36+RING_OD/2*S2)
b += circ(rc[0], rc[1], RING_OD/2*S2, .5, INK, FILL) + circ(rc[0], rc[1], RING_ID/2*S2, .5, INK, '#fff')
for sx_, sy_ in studs: b += circ(rc[0]+sx_*S2, rc[1]-sy_*S2, STUD_HOLE/2*S2+.4, .35, INK, '#fff')
b += circ(rc[0], rc[1], DISC/2*S2, .25, HID, 'none', '1.6 1')
b += dim_h(rc[0]-RING_OD/2*S2, rc[0]+RING_OD/2*S2, rc[1]+RING_OD/2*S2+7, f'OD {RING_OD}', ext=rc[1]+RING_OD/2*S2) + t(rc[0], rc[1]+3, f'ID {RING_ID}', 2.3, 600, 'middle', DIM)
b += t(rc[0]+RING_OD/2*S2+8, rc[1]-RING_OD/2*S2+8, f'3 holes {STUD_HOLE}', 2.0, 400, fill=HID) + t(rc[0]+RING_OD/2*S2+8, rc[1]-RING_OD/2*S2+11.6, f'on PCD {PCD}, 120 deg', 2.0, 400, fill=HID)
b += t(rc[0]+RING_OD/2*S2+8, rc[1]+2, 'Dashed: item 5 disc,', 2.0, 400, fill=HID) + t(rc[0]+RING_OD/2*S2+8, rc[1]+5.6, '150 dia x 3 thick.', 2.0, 400, fill=HID)
b += ar(410, rc[1]+RING_OD/2*S2+3, 'الحلقة تثبّت القرص خلف النافذة.', 2.0, 400, HID)
# hanger
hy = 152; HS = .5; hx = rx2
b += t(rx2, hy-9, 'ITEM 3  HANGER PLATE, 1:2  (qty 3)', 2.5, 600) + ar(410, hy-9, 'بند ٣، لوحة التعليق، العدد ٣', 2.5, 600)
b += rect(hx, hy, HW*HS, HH*HS, .5, INK, FILL)
for sx in (-KX, KX):
    k = keyhole(HW/2+sx, 14)
    b += poly([(hx+px*HS, hy+(HH-py)*HS) for px, py in k.exterior.coords], .4, INK, '#fff')
b += dim_h(hx, hx+HW*HS, hy+HH*HS+7, f'{HW}', ext=hy+HH*HS) + dim_v(hx-6, hy, hy+HH*HS, f'{HH}', ext=hx)
b += dim_h(hx+(HW/2-KX)*HS, hx+(HW/2+KX)*HS, hy-3, f'{2*KX} between keyholes', ext=hy+(HH-14)*HS)
b += t(hx, hy+HH*HS+13, 'Keyhole: head hole 9, slot 5 wide, slot goes UP 12 from the head-hole centre (14 above the bottom edge).', 1.9, 400, fill=HID)
b += t(hx, hy+HH*HS+16.6, 'Plate is lowered over the screws and slides down. Fixing to the frame: Production.', 1.9, 400, fill=HID)
b += ar(410, hy+HH*HS+21, 'فتحات التعليق: الرأس ٩ مم، الشق إلى أعلى ١٢ مم.', 1.9, 400, HID)
# frame strips
fy = 208; FS = .25
b += t(rx2, fy-6, 'ITEM 2  FRAME STRIPS, 1:4  (per plate: 2 long + 2 short)', 2.3, 600) + ar(410, fy-6, 'بند ٢، شرائط الإطار الخلفي', 2.3, 600)
b += rect(rx2, fy, LONG*FS, FRD*FS, .45, INK, FILL) + t(rx2+LONG*FS+3, fy+3, f'{LONG} x {FRD}   (x2)', 2.0, 400, fill=DIM)
b += rect(rx2, fy+9, SHORT*FS, FRD*FS, .45, INK, FILL) + t(rx2+SHORT*FS+3, fy+12, f'{SHORT} x {FRD}   (x2, butted between the long ones)', 2.0, 400, fill=DIM)
b += t(rx2, fy+20, 'Thickness 2. Frame outside 280 x 310, 10 inside the plate edge: not visible from the front.', 1.9, 400, fill=HID)
# data
b += t(10, 236, 'DATA', 2.5, 600) + ar(220, 236, 'بيانات', 2.5, 600)
rows = [('Face plate cut length (outline + window)', f'{plate.length:.0f} mm'), ('Hanger plate cut length (with 2 keyholes)', f'{hanger.length:.0f} mm'), ('Ring cut length (OD, ID, 3 holes)', f'{ring.length:.0f} mm'),
        ('Stand-off from wall', f'{STAND} mm (13 frame + 2 plate)'), ('Hanger rear face from wall', f'{ZW} mm (screw-head room)')]
for i, (k, v) in enumerate(rows):
    yy = 242 + i*5
    b += line(10, yy+1.5, 220, yy+1.5, .15, HID) + t(11, yy, k, 2.1) + t(219, yy, v, 2.1, 600, 'end')
sh2 = sheet(2, 'PART SHEET', 'ورقة الأجزاء', '1:2 / 1:4', b)

# ===== SHEET 3: one plate, exploded =====
S3 = .22; ox3, oy3 = 16, 118
LX, LY = 34, -20
b = t(10, 24, 'ONE PLATE, EXPLODED, about 1:4 (layers pulled out behind the face, to the upper right)', 2.5, 600) + ar(410, 24, 'منظر مفكك للوحة واحدة', 2.5, 600)
def L(k): return (ox3 + k*LX, oy3 + k*LY)
def lrect(k, w, h, cx, cy, fill, dash=None):
    ax, ay = L(k); return rect(ax+cx*S3, ay+cy*S3, w*S3, h*S3, .4, INK, fill, dash)
def lcirc(k, r, cx, cy, fill, dash=None):
    ax, ay = L(k); return circ(ax+cx*S3, ay+cy*S3, r*S3, .4, INK, fill, dash)
b += lrect(4, HW, HH, (PW-HW)/2, HTOP, FILL2)
for sx in (-KX, KX): b += lcirc(4, KHEAD/2*1.0, WCX+sx, KY, '#fff')
b += lrect(3, FO_W, FO_H, INSET, INSET, 'none') + lrect(3, FO_W-2*T, FO_H-2*T, INSET+T, INSET+T, 'none')
b += lcirc(2, RING_OD/2, WCX, WCY, FILL2) + lcirc(2, RING_ID/2, WCX, WCY, '#fff')
b += lcirc(1, DISC/2, WCX, WCY, '#4a4a4a')
b += lrect(0, PW, PH, 0, 0, FILL) + lcirc(0, WIN/2, WCX, WCY, '#4a4a4a')
b += balloon(L(0)[0]+PW*S3+7, L(0)[1]+14, 1) + balloon(L(1)[0]+(WCX+DISC/2)*S3+6, L(1)[1]+(WCY+10)*S3, 5)
b += balloon(L(2)[0]+(WCX+RING_OD/2)*S3+6, L(2)[1]+(WCY-35)*S3, 4) + balloon(L(3)[0]+(INSET+FO_W)*S3+6, L(3)[1]+(INSET+40)*S3, 2) + balloon(L(4)[0]+((PW-HW)/2+HW)*S3+6, L(4)[1]+(HTOP+HH/2)*S3, 3)
b += t(10, 232, 'Item numbers as in the bill of materials. Face (1) in front; behind it: disc (5), ring (4), frame (2), hanger plate (3).', 2.0, 400, fill=HID)
b += t(10, 236, 'The disc in the window is shown dark: a neutral insert. The pictures in the reference are not ours.', 2.0, 400, fill=HID) + ar(215, 240, 'الأرقام كما في قائمة المواد.', 2.0, 400, HID)
bx0 = 250
b += t(bx0, 38, 'BOUGHT-IN: M3 stud and nut (3 + 3 per plate)', 2.3, 600) + ar(410, 42, 'مشتريات جاهزة: مسمار ملولب وصامولة مقاس ٣ مم', 2.3, 600)
b += t(bx0, 46, 'Three M3 studs welded to the plate rear on PCD 160 hold the ring.', 2.0, 400, fill=HID) + t(bx0, 49.6, 'Stud length about 7: 3 disc + 2 ring + nut. Method: Production.', 2.0, 400, fill=HID)
sy0 = 68
b += t(bx0, sy0-6, 'ASSEMBLY SEQUENCE (proposed)', 2.5, 600) + ar(410, sy0-6, 'تسلسل التجميع (مقترح)', 2.5, 600)
steps = [('Cut parts 1, 2, 3, 4. Remove burrs. Brush the face (item 1).', 'قص الأجزاء وإزالة الحواف ثم تفريش الوجه.'),
         ('Fix the frame (2) to the back of the face, 10 in from every edge.', 'تثبيت الإطار الخلفي على بعد ١٠ مم من الحواف.'),
         ('Fix the hanger plate (3) inside the frame, 14 below the top edge.', 'تثبيت لوحة التعليق داخل الإطار.'),
         ('Weld the 3 M3 studs on PCD 160. Place the disc (5) behind the window.', 'لحام ٣ مسامير ووضع القرص خلف النافذة.'),
         ('Fit the ring (4) over the studs, tighten the 3 nuts lightly.', 'تركيب الحلقة وشد الصواميل بخفة.'),
         ('Remove the film from the face last.', 'إزالة الفيلم الواقي في النهاية.')]
for i, (en, a) in enumerate(steps):
    yy = sy0 + i*14
    b += balloon(bx0+3, yy-1, i+1) + t(bx0+9, yy, en, 2.1) + ar(410, yy+4.5, a, 2.1)
b += t(bx0, sy0+6*14+2, 'Jigs, welds, bonding and order of work are Production\'s decision.', 2.0, 400, fill=HID)
sh3 = sheet(3, 'ASSEMBLY, ONE PLATE', 'التجميع للوحة واحدة', '1:4', b)

# ===== SHEET 4: set of three + hanging layout =====
S4 = .2; ox4, oy4 = 55, 32
b = t(10, 22, 'ELEVATION OF THE SET, 1:5', 2.5, 600) + ar(410, 22, 'منظر أمامي للمجموعة', 2.5, 600)
for i in range(3):
    top = oy4 + i*(PH+GAP)*S4
    b += rect(ox4, top, PW*S4, PH*S4, .45, INK, FILL) + circ(ox4+WCX*S4, top+WCY*S4, WIN/2*S4, .45, INK, '#fff')
    for sx in (-KX, KX): b += circ(ox4+(WCX+sx)*S4, top+SCREW_Y*S4, .9, .3, RED, RED)
    b += t(ox4+PW*S4+3, top+PH*S4/2, f'plate {i+1}', 2.0, 400, fill=HID)
for i in range(2):
    g0 = oy4 + (i*(PH+GAP)+PH)*S4
    b += dim_v(ox4-6, g0, g0+GAP*S4, f'{GAP}', ext=ox4)
for i in range(3):
    top = oy4 + i*(PH+GAP)*S4
    b += dim_v(ox4-18, top, top+PH*S4, f'{PH}', ext=ox4)
b += dim_v(ox4-30, oy4, oy4+SET_H*S4, f'{SET_H} overall', ext=ox4)
b += dim_h(ox4, ox4+PW*S4, oy4+SET_H*S4+7, f'{PW}', ext=oy4+SET_H*S4)
b += t(ox4, oy4+SET_H*S4+14, 'red dots = wall screws', 2.0, 400, fill=RED)
tx0 = 150
b += t(tx0, 32, 'WALL SCREW POSITIONS (two per plate)', 2.5, 600) + ar(410, 32, 'مواضع براغي الحائط (برغيان لكل لوحة)', 2.5, 600)
b += rect(tx0, 35, 105, 7, .3, INK, '#e9e5dc')
for x_, s_ in zip([tx0+2, tx0+22, tx0+54], ['PLATE', 'X from the centreline', 'Y below top of stack']): b += t(x_, 40, s_, 2.0, 600)
for i in range(3):
    yy = 47 + i*7; y_top = i*(PH+GAP) + SCREW_Y
    b += line(tx0, yy+2, tx0+105, yy+2, .15, HID) + t(tx0+2, yy, f'{i+1}', 2.2) + t(tx0+22, yy, f'-{KX} and +{KX}', 2.2) + t(tx0+54, yy, f'{y_top}', 2.2)
b += note(tx0, 72, 'Screws rest at the top of the keyhole slot: 28 below the top edge of each plate. Pitch between plates 390 (330 + 60).', 'الشقوق إلى أعلى؛ المسافة بين اللوحات ٣٩٠ مم.')
b += note(tx0, 82, 'Screw head 8 dia max, 4 high max (hanger plate is 5 off the wall). Screw and plug: installer, wall type unknown.', 'نوع المسمار والدسار يحدده الفني حسب الحائط.')
b += note(tx0, 92, 'Level the screws with a spirit level before hanging. The three plates are identical and can swap places.', 'اضبط مستوى البراغي قبل التعليق.')
b += t(tx0, 108, 'MOUNTING HEIGHT (proposal)', 2.5, 600) + ar(410, 108, 'ارتفاع التعليق (مقترح)', 2.5, 600)
b += t(tx0, 114, 'Centre of the stack about 1500 above the floor: stack from about 945 to 2055.', 2.1) + ar(410, 118, 'مركز المجموعة نحو ١٥٠٠ مم من الأرض، مقترح.', 2.1)
b += t(tx0, 124, 'Final height is the customer\'s choice; the layout above does not change.', 2.0, 400, fill=HID)
b += t(tx0, 138, 'THE THREE PLATES ARE IDENTICAL', 2.5, 600, fill=RED) + ar(410, 138, 'اللوحات الثلاث متطابقة', 2.5, 600, RED)
b += note(tx0, 144, 'Checked on the reference: same size, same window size and position, same finish. Only the picture differs.', 'الفرق الوحيد هو الصورة داخل كل نافذة.')
b += t(tx0, 156, 'Each plate comes with its own insert. Whether the set is also sold singly is open (not costed).', 2.0, 400, fill=HID)
b += t(tx0, 170, 'WHAT SABRY DECIDES', 2.5, 600)
for i, s_ in enumerate(['Plate 300 x 330 x 2, window 130 (proposed).', 'Hanger: hidden keyholes (proposed) or a wall rail.', 'Insert: customer-supplied print or neutral disc.', 'Is a set always three, or also sold singly?']):
    b += t(tx0+2, 176+i*5, f'{i+1}. {s_}', 2.1)
sh4 = sheet(4, 'SET OF THREE, HANGING LAYOUT', 'مخطط المجموعة والتعليق', '1:5', b)

# ===== SHEET 5: cutting layout =====
S5 = .1; ox5, oy5 = 30, 40
b = t(10, 22, f'CUTTING LAYOUT, one set of three, assumed sheet {SHEET_L} x {SHEET_W} x {T}. To be confirmed by Production.', 2.4, 600) + ar(410, 22, 'مخطط القص لمجموعة واحدة', 2.4, 600)
b += rect(ox5, oy5, SHEET_L*S5, SHEET_W*S5, .5, '#2f6b45', '#fbfaf6') + t(ox5, oy5-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for lab, g in placed:
    b += poly([(ox5+px*S5, oy5+(SHEET_W-py)*S5) for px, py in g.exterior.coords[:-1]], .3, INK, FILL)
    for ir in g.interiors: b += poly([(ox5+px*S5, oy5+(SHEET_W-py)*S5) for px, py in ir.coords[:-1]], .25, INK, '#fff')
    cb = g.bounds
    if lab in ('1', '4', '3'): b += t(ox5+(cb[0]+cb[2])/2*S5, oy5+(SHEET_W-(cb[1]+cb[3])/2)*S5+1, lab, 3.4, 600, 'middle', '#555')
b += dim_h(ox5, ox5+SHEET_L*S5, oy5+SHEET_W*S5+7, f'{SHEET_L}', ext=oy5+SHEET_W*S5) + dim_v(ox5-6, oy5, oy5+SHEET_W*S5, f'{SHEET_W}', ext=ox5)
b += t(30, 195, f'Parts per set: 3 x item 1, 6 x item 2 long, 6 x item 2 short, 3 x item 3, 3 x item 4. {len(placed)} parts, {GP} mm spacing. The 3 window discs (130 dia) are scrap.', 2.1)
b += t(30, 200, f'They use about {ext[2]:.0f} x {ext[3]:.0f} mm of the sheet. No offcut or yield is claimed. Grain along the length, to confirm.', 2.1)
b += t(30, 206, f'Total cutting length of all parts: {TOTAL_CUT/1000:.2f} m ({TOTAL_CUT:.0f} mm), including windows, rings and keyholes.', 2.5, 600)
b += ar(410, 195, f'{len(placed)} قطعة بمسافة ١٠ مم. لا يُدّعى أي هالك.', 2.1) + ar(410, 206, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.5, 600)
sh5 = sheet(5, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)

# ===== SHEET 6: BOM and notes =====
import textwrap
b = t(10, 28, 'BILL OF MATERIALS (one set of three)', 2.8, 600) + ar(410, 28, 'قائمة المواد لمجموعة واحدة', 2.8, 600) + rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x_, s_ in zip([12, 22, 130, 150, 205], ['ITEM', 'PART / الجزء', 'QTY', 'SIZE (mm)', 'MATERIAL / الخامة']): b += t(x_, 36, s_, 2.2, 600)
bom = [('1', 'Face plate, laser cut, window', 'لوح أمامي بنافذة', '3', f'{PW} x {PH} x {T}, window {WIN}', 'Stainless steel sheet, brushed face (proposed)'),
       ('2', 'Frame strips, long / short', 'شرائط الإطار', '6 / 6', f'{LONG} x {FRD} x {T} / {SHORT} x {FRD} x {T}', 'Stainless steel sheet (proposed)'),
       ('3', 'Hanger plate with 2 keyholes', 'لوحة تعليق', '3', f'{HW} x {HH} x {T}', 'Stainless steel sheet (proposed)'),
       ('4', 'Retaining ring', 'حلقة تثبيت', '3', f'{RING_OD} / {RING_ID} dia x {T}', 'Stainless steel sheet (proposed)'),
       ('5', 'Insert disc, printed', 'قرص مطبوع', '3', f'{DISC} dia x {DISC_T}', 'Customer print or neutral; source open'),
       ('6', 'M3 stud and nut', 'مسمار ملولب وصامولة', '9 + 9', 'about 7 long', 'Stainless steel (proposed), bought-in'),
       ('7', 'Wall screws and plugs', 'براغي ودسار للحائط', '6', 'head 8 max, 4 high max', 'By installer, wall type unknown, not supplied')]
for i, (n_, en, a, q, sz, mat) in enumerate(bom):
    yy = 44 + i*8.2
    b += line(10, yy+2.4, 410, yy+2.4, .15, HID) + t(12, yy, n_, 2.3) + t(22, yy, en, 2.1) + ar(128, yy, a, 1.9) + t(130, yy, q, 2.1) + t(150, yy, sz, 2.0) + t(205, yy, mat, 2.0)
b += t(10, 110, 'NOTES', 2.8, 600) + ar(410, 110, 'ملاحظات', 2.8, 600)
notes = [('ALL SIZES ARE PROPOSED by Claude (Sabry asked for a set of 3 and a drawing, 12 Nov 2026): plate 300 x 330 x 2, window 130, gap 60, stand-off 15. To confirm.', 'كل المقاسات مقترحة وتحتاج تأكيداً.'),
         ('Proportions were measured on the reference photo (plate 1.09 : 1, window 0.42 of the width, gap 0.17 of the plate height). The window is centred on the plate in the photo, so it is drawn centred. The real size is not known.', 'النسب مقاسة من الصورة. المقاس الحقيقي غير معروف.'),
         ('The construction behind the face is inferred, not visible in the photo: flat face, hidden frame set back 10, shadow line on the wall. Hanger, ring and studs are our proposal.', 'التركيب الخلفي مستنتج ومقترح.'),
         ('The pictures in the reference windows are the reference\'s own and are not ours. Do not copy or sell them. The window takes a customer-supplied print or a neutral insert.', 'صور النوافذ في المرجع ليست لنا.'),
         ('Material, thickness, grain direction, edge break, tolerances, fixing and sheet size are Production\'s to decide. Not engineered: no structural claims, no load or weight figures, no costs or prices.', 'القرار للتصنيع. لا ادعاءات إنشائية ولا أسعار.'),
         ('Finish: brushed stainless, exposed metal, no paint, as in the reference. Mirror is not proposed. Keep the protective film on until installation.', 'التشطيب: ستانلس مصقول بالفرشاة بلا طلاء.'),
         ('Arabic wording is a draft for a technical reader.', 'الصياغة العربية مسودة.')]
yy = 119
for i, (en, a) in enumerate(notes):
    b += t(12, yy, f'{i+1}.', 2.3, 600)
    for ln in textwrap.wrap(en, 140): b += t(18, yy, ln, 2.1); yy += 4
    b += ar(410, yy-4, a, 2.1); yy += 5
sh6 = sheet(6, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)
for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5, sh6], 1): open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('written')
