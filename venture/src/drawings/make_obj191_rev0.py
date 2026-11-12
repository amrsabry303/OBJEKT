"""OBJ-191: tray of two interlocking plates. Production drawing set, REV 0 (DRAFT).
Run: python3 make_obj191_rev0.py <repo root>   then: NODE_PATH=<playwright> node make_pdf.js <dir> OBJ-191 0
Reference: one screenshot (images/OBJ-191.jpg) of a third-party maker's reel, used for the idea only.
ALL SIZES ARE PROPOSED BY CLAUDE at Sabry's request (12 Nov 2026, "u suggest"), to confirm. Arabic is a draft. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
from shapely.geometry import Polygon
from shapely import affinity
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-191'; os.makedirs(OUT, exist_ok=True)
REV = 0; DATE = '12 Nov 2026'; PN = 'OBJ-191'
PL, PW, T = 360, 160, 3          # plate length, width, thickness (proposed)
STAG = 40                         # stagger between the plates along the length
OW, OD = PL + STAG, 2*PW          # overall 400 x 320
TX, TB, TH, TD = 100, 20, 32, 12  # tongue centre from end, base width, tip width, depth (dovetail)
SHEET_L, SHEET_W, GAP = 2500, 1250, 10

def plate():
    sx = OW - TX                  # socket centre (mirror of tongue about the overall centre)
    return [(0, 0), (PL, 0), (PL, PW),
            (sx+TB/2, PW), (sx+TH/2, PW-TD), (sx-TH/2, PW-TD), (sx-TB/2, PW),
            (TX+TB/2, PW), (TX+TH/2, PW+TD), (TX-TH/2, PW+TD), (TX-TB/2, PW), (0, PW)]
A = plate()
B = [(OW-x, OD-y) for x, y in A]
pa, pb = Polygon(A), Polygon(B)
inter = pa.intersection(pb).area; uni = pa.union(pb)
assert inter < 1e-6, inter
assert abs(uni.area - 2*pa.area) < 1e-6 and uni.geom_type == 'Polygon'
ub = uni.bounds; assert (round(ub[2]-ub[0]), round(ub[3]-ub[1])) == (OW, OD), ub
PERIM = pa.length
bx = pa.bounds; PBW, PBH = bx[2]-bx[0], bx[3]-bx[1]
NEST = [(0, 0), (PBW+GAP, 0)]
assert all(x+PBW <= SHEET_L-GAP and y+PBH <= SHEET_W-GAP for x, y in NEST)
TOTAL_CUT = 2*PERIM
print('plate bbox', PBW, PBH, 'perimeter', round(PERIM, 1), 'overlap', inter, 'union ok, overall', OW, OD)

# ---- DXF ----
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4; d.layers.add('CUT', color=7); d.layers.add('SHEET', color=3); return d
def add_plate(msp, ox, oy):
    msp.add_lwpolyline([(ox+x, oy+y) for x, y in A], close=True, dxfattribs={'layer': 'CUT'})
doc = new_doc(); add_plate(doc.modelspace(), 0, 0); doc.saveas(f'{OUT}/{PN}_rev{REV}_P1_plate.dxf')
doc = new_doc(); m = doc.modelspace()
m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
for x, y in NEST: add_plate(m, 10+x, 10+y)
doc.saveas(f'{OUT}/{PN}_rev{REV}_nest_{SHEET_L}x{SHEET_W}.dxf')

# ---- SVG helpers ----
FONT = "DejaVu Sans, Inter, Arial, sans-serif"
INK, DIM, HID, FILL, FILL2 = '#161616', '#2a4a7a', '#7a7a7a', '#f1efe9', '#dcd9d0'
RED = '#b3261e'
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
def arrow(x, y, dx, dy):
    n = math.hypot(dx, dy); ux, uy = dx/n, dy/n
    return f'<polygon points="{x:.2f},{y:.2f} {x-ux*2+uy*.7:.2f},{y-uy*2-ux*.7:.2f} {x-ux*2-uy*.7:.2f},{y-uy*2+ux*.7:.2f}" fill="{DIM}"/>'
def dim_h(x1, x2, y, label, ext=None):
    s = line(x1, y, x2, y, .2, DIM) + arrow(x1, y, 1, 0) + arrow(x2, y, -1, 0)
    if ext is not None: s += line(x1, ext, x1, y+(2 if y > ext else -2), .15, DIM) + line(x2, ext, x2, y+(2 if y > ext else -2), .15, DIM)
    return s + t((x1+x2)/2, y-1, label, 2.4, 500, 'middle', DIM)
def dim_v(x, y1, y2, label, ext=None):
    s = line(x, y1, x, y2, .2, DIM) + arrow(x, y1, 0, 1) + arrow(x, y2, 0, -1)
    if ext is not None: s += line(ext, y1, x+(2 if x > ext else -2), y1, .15, DIM) + line(ext, y2, x+(2 if x > ext else -2), y2, .15, DIM)
    return s + f'<text transform="translate({x-1:.2f} {(y1+y2)/2:.2f}) rotate(-90)" font-family="{FONT}" font-size="2.4" font-weight="500" text-anchor="middle" fill="{DIM}">{esc(label)}</text>'
def balloon(x, y, n):
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.2" fill="#fff" stroke="{INK}" stroke-width=".3"/>' + t(x, y+1.1, str(n), 3, 600, 'middle')
N = 5
def frame(n, title_en, title_ar, scale):
    s = rect(5, 5, 410, 287, .5) + rect(7, 7, 406, 283, .2)
    X, Y, Wd = 228, 247, 185
    s += rect(X, Y, Wd, 41, .4, fill='#fff')
    s += line(X, Y+9, X+Wd, Y+9, .25) + line(X, Y+20, X+Wd, Y+20, .25) + line(X, Y+31, X+Wd, Y+31, .25) + line(X+92, Y+9, X+92, Y+41, .25)
    s += bi(X+2, Y+4, f'{PN}   Tray, two interlocking plates', 'صينية من لوحين متداخلين', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  {OW} x {OD} x {T} mm (PROPOSED)', 'المقاس الكلي (مقترح)', 88, 2.3) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, 'MATERIAL  Stainless steel sheet, 3 mm proposed', 'الخامة: ستانلس ستيل، ٣ مم مقترح', 88, 2.1) + bi(X+94, Y+25, 'FINISH  brushed OR mirror stainless', 'التشطيب: مصقول بالفرشاة أو مرآة', 88, 2.1)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, RED, '#fff')
    s += t(X+Wd/2, Y-8.6, 'DRAFT, not approved, not engineered', 2.9, 700, 'middle', RED) + t(X+Wd/2, Y-3.8, 'مسودة، غير معتمدة، غير مهندسة', 2.9, 700, 'middle', RED)
    return s + t(10, 14, title_en, 4.2, 700) + ar(410, 14, title_ar, 4.2, 700)
def sheet(n, te, ta, sc, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, te, ta, sc)}{body}</svg>'
def tx(pts, ox, oy, S, H):  # drawing coords (mm, y up) -> sheet
    return [(ox+x*S, oy+(H-y)*S) for x, y in pts]
im = Image.open(ROOT + '/images/OBJ-191.jpg').convert('RGB').crop((0, 430, 640, 1000)); im.thumbnail((520, 520))
b_ = io.BytesIO(); im.save(b_, 'JPEG', quality=72); PHOTO = 'data:image/jpeg;base64,' + base64.b64encode(b_.getvalue()).decode()

# ===== SHEET 1: views =====
S = .5; ox, oy = 22, 38
b = t(ox, oy-5, 'PLAN, assembled, 1:2', 2.6, 600) + ar(220, oy-5, 'منظر علوي، مجمّع', 2.6, 600)
b += poly(tx(A, ox, oy, S, OD), .45, INK, FILL) + poly(tx(B, ox, oy, S, OD), .45, INK, FILL2)
b += balloon(ox+60*S, oy+(OD-60)*S, 1) + t(ox+72*S, oy+(OD-56)*S, 'plate A', 2.2, 400, fill=HID)
b += balloon(ox+340*S, oy+(OD-260)*S, 1) + t(ox+300*S, oy+(OD-256)*S, 'plate B', 2.2, 400, fill=HID)
gx, gy = 200, 160
for cx, cy in [(120, 80), (280, 240)]:
    p = (ox+cx*S, oy+(OD-cy)*S)
    b += f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="{40*S}" fill="none" stroke="{HID}" stroke-width=".25" stroke-dasharray="1.4 1"/>'
b += t(ox+8*S, oy+(OD+14)*S+0, '', 2)
b += t(ox+95*S, oy+(OD-110)*S, 'glass, about 80 mm (position only)', 2.0, 400, fill=HID)
b += dim_h(ox, ox+OW*S, oy+OD*S+7, f'{OW}', ext=oy+OD*S) + dim_v(ox-7, oy, oy+OD*S, f'{OD}', ext=ox)
b += dim_h(ox, ox+STAG*S, oy+OD*S+14, f'{STAG}', ext=oy+OD*S+6)
b += t(ox, oy+OD*S+22, 'Both plates are the same part (item 1); plate B is plate A turned 180 degrees. Stagger 40 mm along the length.', 2.1, 400, fill=HID)
b += t(ox, oy+OD*S+26.5, 'الجزءان متطابقان؛ اللوح ب هو اللوح أ مدوّراً ١٨٠ درجة. الإزاحة ٤٠ مم.', 2.1, 400, fill=HID)
# elevations (3 mm strips)
ey = 245
b += t(ox, ey-6, 'FRONT / SIDE (thickness only), 1:2', 2.6, 600) + ar(220, ey-6, 'منظر أمامي وجانبي', 2.6, 600)
b += rect(ox, ey, OW*S, T*S, .4, INK, FILL) + dim_v(ox-3, ey, ey+T*S, f'{T}') + dim_h(ox, ox+OW*S, ey+10, f'{OW}', ext=ey+T*S)
b += t(ox, ey+17, 'Flat tray, no rim. Plate thickness 3 mm is proposed; Production decides.', 2.1, 400, fill=HID) + ar(220, ey+22, 'صينية مسطحة بلا حافة، السماكة ٣ مم مقترحة والقرار للتصنيع.', 2.1, 400, HID)
# reference photo
rx = 238
b += t(rx, 22, 'REFERENCE (idea only, not ours)', 2.4, 600) + ar(410, 22, 'المرجع (للفكرة فقط)', 2.4, 600)
ih = 160*im.size[1]/im.size[0]
b += f'<image x="{rx}" y="25" width="160" height="{ih:.1f}" href="{PHOTO}"/>' + rect(rx, 25, 160, ih, .25, HID)
b += t(rx, 25+ih+4, 'Screenshot of a third-party reel. Two plates, a slot in each, two glasses. We draw our own design.', 1.9, 400, fill=HID)
# colourways
cy0 = 25+ih+12
b += t(rx, cy0, 'COLOURWAYS', 2.6, 600) + ar(410, cy0, 'خيارات التشطيب', 2.6, 600)
b += rect(rx, cy0+3, 22, 14, .3, INK, '#b8b8b4') + t(rx+25, cy0+8, 'Brushed stainless steel', 2.3, 600) + t(rx+25, cy0+12, 'Satin grain, direction along the length (to confirm)', 1.9, 400, fill=HID)
b += rect(rx, cy0+20, 22, 14, .3, INK, '#e4e6e8') + t(rx+25, cy0+25, 'Mirror stainless steel', 2.3, 600) + t(rx+25, cy0+29, 'Mirror polish: few skilled polishers, Production to confirm', 1.9, 400, fill=HID)
b += t(rx, cy0+39, 'Swatches are indicative only. Both finishes proposed by Sabry; he chooses.', 1.9, 400, fill=HID)
sh1 = sheet(1, 'VIEWS', 'المناظر', '1:2', b)

# ===== SHEET 2: part =====
S2 = .5; ox2, oy2 = 40, 48; HH = PW+TD
b = t(10, 24, 'ITEM 1  PLATE, flat pattern, 1:2   (quantity 2, identical)', 2.6, 600) + ar(410, 24, 'بند ١، لوح، الشكل المفرود، العدد ٢', 2.6, 600)
b += poly(tx(A, ox2, oy2, S2, HH), .5, INK, FILL)
b += balloon(ox2+180*S2, oy2+(HH-90)*S2, 1)
b += dim_h(ox2, ox2+PL*S2, oy2+HH*S2+8, f'{PL}', ext=oy2+HH*S2) + dim_h(ox2, ox2+(OW-TX)*S2, oy2+HH*S2+16, f'{OW-TX} (socket centre)', ext=oy2+HH*S2)
b += dim_v(ox2-8, oy2+TD*S2, oy2+HH*S2, f'{PW}', ext=ox2) + dim_h(ox2, ox2+TX*S2, oy2-6, f'{TX} (tongue centre)', ext=oy2)
b += t(ox2+TX*S2+14, oy2+3, 'tongue', 2.2, 600, fill=RED) + t(ox2+(OW-TX)*S2+12, oy2+(TD+22)*S2, 'socket', 2.2, 600, fill=RED)
b += t(ox2+PL*S2/2, oy2+HH*S2-10, 'THICKNESS 3 (proposed)', 2.4, 500, 'middle', HID)
# joint detail 4:1
D4 = 3.5; dx, dy = 95, 228
b += t(10, 156, 'JOINT DETAIL, tongue and socket, 3.5:1', 2.6, 600) + ar(225, 156, 'تفصيل الوصلة: اللسان والتجويف', 2.6, 600)
tg = [(-TB/2, 0), (-TH/2, TD), (TH/2, TD), (TB/2, 0)]
def T4(pts, cx, cyy, flip=1): return [(cx+x*D4, cyy-y*D4*flip) for x, y in pts]
b += poly(T4(tg, dx+30, dy), .5, INK, FILL) + line(dx-20, dy, dx+80, dy, .3, HID, '2 1')
b += dim_h(dx+30-TB/2*D4, dx+30+TB/2*D4, dy+8, f'{TB}', ext=dy) + dim_h(dx+30-TH/2*D4, dx+30+TH/2*D4, dy-TD*D4-6, f'{TH}', ext=dy-TD*D4) + dim_v(dx+30+TH/2*D4+8, dy-TD*D4, dy, f'{TD}', ext=dx+30+TB/2*D4)
b += t(dx-20, dy+14, 'Plate A tongue. Plate B socket is the same shape cut into the plate edge (dashed in sheet 3).', 2.0, 400, fill=HID)
b += t(dx-20, dy+18, 'Dovetail shape: wider at the tip than at the base, so the plates cannot pull apart sideways.', 2.0, 400, fill=HID)
b += ar(225, dy+22, 'اللسان على شكل ذيل حمامة، أعرض عند الطرف.', 2.0, 400, HID)
# data table
tbx = 120
b += t(tbx+120, 156, 'DATA', 2.6, 600) + ar(410, 158, 'بيانات', 2.6, 600)
rows = [('Plate (finished) mm', f'{PL} x {PW} x {T}'), ('Plate incl. tongue mm', f'{PBW:.0f} x {PBH:.0f} x {T}'), ('Cut length per plate', f'{PERIM:.0f} mm'),
        ('Tongue / socket', f'{TB} base, {TH} tip, {TD} deep'), ('Tongue centre', f'{TX} from the left end'), ('Socket centre', f'{OW-TX} from the left end'),
        ('Quantity', '2, identical')]
for i, (k, v) in enumerate(rows):
    yy = 166 + i*6.2
    b += line(tbx+120, yy+2, 410, yy+2, .15, HID) + t(tbx+122, yy, k, 2.2) + t(408, yy, v, 2.2, 600, 'end')
b += t(10, 262, 'Fit: tongue and socket are drawn to the same size (nominal). Fit clearance and laser kerf are Production\'s to set.', 2.1, 400, fill=HID)
b += t(10, 266.5, 'الخلوص والقص يحددهما التصنيع.', 2.1, 400, fill=HID)
sh2 = sheet(2, 'PART SHEET', 'ورقة الأجزاء', '1:1', b)

# ===== SHEET 3: assembly =====
S3 = .4; ox3, oy3 = 15, 64
b = t(10, 24, 'EXPLODED, 1:2.5 (plate B lifted straight up)', 2.6, 600) + ar(410, 24, 'منظر مفكك: اللوح ب مرفوع للأعلى', 2.6, 600)
LX, LY = 20, 24   # lift in sheet mm (oblique)
Aq = tx(A, ox3, oy3+OD*S3*0+20, S3, OD)   # A in lower position
Bq = [(x+LX, y-LY) for x, y in tx(B, ox3, oy3+20, S3, OD)]
def tx2(pts, dx_, dy_): return [(x+dx_, y+dy_) for x, y in tx(pts, ox3, oy3, S3, OD)]
Aq = tx2(A, 0, 0); Bq = tx2(B, LX, -LY)
b += poly(Aq, .45, INK, FILL)
# guide lines from plate B tongue (B-socket location) to plate A tongue positions
for (px_, py_) in [(TX, PW+TD), (OW-TX, PW+TD)]:
    pass
for cx in (TX, OW-TX):
    # socket in B at global x = OW - (OW-TX... ) positions: A tongue at global TX ; B tongue at global OW-TX; mating socket in B at TX, in A at OW-TX
    for gx_, gy_ in [(cx, PW)]:
        p0 = (ox3+gx_*S3, oy3+(OD-gy_)*S3); p1 = (p0[0]+LX, p0[1]-LY)
        b += line(p0[0], p0[1], p1[0], p1[1], .2, DIM, '1.5 1')
b += poly(Bq, .45, INK, FILL2)
b += balloon(ox3+60*S3, oy3+(OD-60)*S3, 1) + t(ox3+70*S3, oy3+(OD-56)*S3, 'A', 2.4, 600) + balloon(ox3+340*S3+LX, oy3+(OD-260)*S3-LY, 1) + t(ox3+300*S3+LX, oy3+(OD-256)*S3-LY, 'B', 2.4, 600)
b += t(ox3, 212, 'Dashed blue lines: where each tongue enters the socket of the other plate.', 2.1, 400, fill=HID) + ar(215, 212, 'الخطوط المتقطعة: مدخل كل لسان في تجويف اللوح الآخر.', 2.1, 400, HID)
sx0 = 238
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + ar(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600)
steps = [('Cut two identical plates (item 1), remove burrs, apply the finish.', 'قص لوحين متطابقين وإزالة الحواف الحادة ثم التشطيب.'),
         ('Lay plate A flat on a clean surface.', 'ضع اللوح أ مسطحاً على سطح نظيف.'),
         ('Turn plate B by 180 degrees and hold it above A, stagger 40 mm.', 'دوّر اللوح ب ١٨٠ درجة وأمسكه فوق اللوح أ مع إزاحة ٤٠ مم.'),
         ('Lower B straight down: both tongues drop into both sockets at once.', 'أنزل اللوح ب عمودياً: يدخل اللسانان في التجويفين معاً.'),
         ('Check the two plates sit flat in one plane. Nothing is welded or glued.', 'تأكد أن اللوحين في مستوى واحد. بلا لحام ولا لصق.')]
for i, (en, a) in enumerate(steps):
    yy = 48 + i*17
    b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 2.3) + ar(410, yy+5, a, 2.3)
b += t(sx0, 140, 'The joint holds the plates together sideways only. They can be lifted apart straight up.', 2.1, 400, fill=HID)
b += t(sx0, 144.5, 'Whether it needs a fixing underneath is for Production to decide.', 2.1, 400, fill=HID)
sh3 = sheet(3, 'ASSEMBLY', 'التجميع', '1:2.5', b)

# ===== SHEET 4: cutting layout =====
S4 = .1; ox4, oy4 = 30, 40
b = t(10, 22, f'CUTTING LAYOUT on an assumed sheet {SHEET_L} x {SHEET_W} x 3. Assumed, to be confirmed by Production.', 2.4, 600) + ar(410, 22, 'مخطط القص على لوح مفترض', 2.4, 600)
b += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6') + t(ox4, oy4-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for x, y in NEST:
    b += poly(tx([(10+x+px, 10+y+py) for px, py in A], ox4, oy4, S4, 0)[:0] or [(ox4+(10+x+px)*S4, oy4+(10+y+(PBH-py))*S4) for px, py in A], .3, INK, FILL)
    b += t(ox4+(10+x+PBW/2)*S4, oy4+(10+y+PBH/2)*S4+1, '1', 3.4, 600, 'middle', '#555')
b += dim_h(ox4, ox4+SHEET_L*S4, oy4+SHEET_W*S4+7, f'{SHEET_L}', ext=oy4+SHEET_W*S4) + dim_v(ox4-6, oy4, oy4+SHEET_W*S4, f'{SHEET_W}', ext=ox4)
used = 10+NEST[1][0]+PBW
b += t(30, 195, f'2 plates nested with {GAP} mm spacing, same direction (grain along the length). They use about {used:.0f} x {PBH+20:.0f} mm of the sheet. No offcut is claimed.', 2.3)
b += t(30, 200, f'Total cutting length of both plates: {TOTAL_CUT/1000:.2f} m ({TOTAL_CUT:.0f} mm).', 2.5, 600)
b += ar(410, 195, 'لوحان بمسافة ١٠ مم. لا يُدّعى أي هالك.', 2.3) + ar(410, 200, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.5, 600)
sh4 = sheet(4, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)

# ===== SHEET 5: BOM and notes =====
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + ar(410, 28, 'قائمة المواد', 2.8, 600) + rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
b += line(10, 46.2, 410, 46.2, .15, HID) + t(12, 44, '1', 2.4) + t(24, 44, 'Plate, flat, laser cut', 2.4) + ar(120, 44, 'لوح مسطح، قص ليزر', 2.4) + t(150, 44, '2', 2.4) + t(215, 44, 'Stainless steel sheet 3 mm (proposed), brushed or mirror', 2.4)
b += t(10, 60, 'NOTES', 2.8, 600) + ar(410, 60, 'ملاحظات', 2.8, 600)
notes = [('ALL SIZES ARE PROPOSED by Claude at Sabry\'s request (12 Nov 2026): plate 360 x 160 x 3, stagger 40, overall 400 x 320. Sabry has not given sizes. To confirm.', 'كل المقاسات مقترحة وتحتاج تأكيداً من سبري.'),
         ('The shape is inferred from one screenshot of a third-party reel: two flat plates, each with a notch, slotting together; two glasses sit on top. The exact joint in the reference is not visible, so the dovetail tongue and socket are our proposal.', 'الشكل مستنتج من صورة واحدة، والوصلة المقترحة من تصميمنا.'),
         ('This is objekt\'s own design. Nothing from the reference maker\'s name or marks is used.', 'تصميم objekt الخاص، بلا أي اسم أو علامة للمصنّع المرجعي.'),
         ('Material, thickness, edge break, corner radius, tolerances, fit clearance, laser kerf and sheet size are Production\'s to decide.', 'الخامة والسماكة والسماحيات والخلوص يقررها التصنيع.'),
         ('Finish: brushed stainless steel or mirror stainless steel (Sabry, 12 Nov). Mirror needs the few skilled polishers; Production to confirm. Brush direction along the length, to confirm.', 'التشطيب: مصقول بالفرشاة أو مرآة. المرآة تحتاج مصقلين مهرة.'),
         ('The joint holds the plates sideways only; the plates lift apart straight up. No structural claims, stress figures, costs or prices. Not engineered.', 'الوصلة تمسك اللوحين جانبياً فقط. لا ادعاءات إنشائية ولا أسعار.'),
         ('Arabic wording is a draft for a technical reader.', 'الصياغة العربية مسودة.')]
for i, (en, a) in enumerate(notes):
    yy = 69 + i*14
    b += t(12, yy, f'{i+1}.', 2.4, 600) + t(18, yy, en if len(en) < 150 else en[:150].rsplit(' ', 1)[0], 2.2) + (t(18, yy+4, en[len(en[:150].rsplit(' ', 1)[0]):].strip(), 2.2) if len(en) >= 150 else '') + ar(410, yy+8, a, 2.2)
sh5 = sheet(5, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)
for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1): open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('written')
