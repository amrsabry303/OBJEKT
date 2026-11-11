"""OBJ-149: blackened steel ashtray, interlocking plates. Production drawing set, REV 0 (DRAFT).
Run: python3 make_obj149_rev0.py <repo root>   then   node make_pdf.js venture/drawings/OBJ-149 OBJ-149 0
Reference photo: images/OBJ-149.jpg (two views of one piece, not ours). NO dimensions were given: every size here is
ESTIMATED FROM THE PHOTOS, using a standing cigarette (about 84 mm) for scale. Construction is inferred. Arabic is a draft.
No costs, no structural claims. Plate thickness is drawn at 3 mm for the layout only, Production decides."""
import sys, os, math
import ezdxf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dwg_common as dc
from dwg_common import *
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
PN = 'OBJ-149'; REV = 0; DATE = '11 Nov 2026'
OUT = f'{ROOT}/venture/drawings/{PN}'; os.makedirs(OUT, exist_ok=True)
REFIMG = ROOT + '/images/OBJ-149.jpg'

# ---- geometry (mm), all estimated from the photos ----
T = 3.0            # plate thickness, assumed for the layout only
L, H = 220.0, 60.0 # plate length and height
CL = 81.5          # plate centre line from the middle (clear gap between parallel plates = 160)
SLOT_D = H/2       # cross-halving slot depth
C1, C2 = L/2-CL, L/2+CL   # slot centres along a plate (28.5, 191.5)
PAIR_GAP = 10.0    # clear gap between the two plates of the doubled side (cigarette storage in the reference)
TRAY, TRAY_H, TRAY_R = 160.0, 50.0, 12.0   # tray outside size, wall height, inside bend radius (proposed)
FRONT_IN, FRONT_OUT, BACK = -CL, -(CL+T+PAIR_GAP), CL        # X plate centre lines (world y): front inner, front outer, back
YMID = ((FRONT_OUT-T/2)+(BACK+T/2))/2      # middle of the assembly in y
Y_START, Y_END = YMID-L/2, YMID+L/2        # the two Y plates are centred on it
SLOTS_Y = [FRONT_OUT-Y_START, FRONT_IN-Y_START, BACK-Y_START]   # slot centres along a Y plate from its end
SHEET_L, SHEET_W, GAP = 2500, 1250, 10
dc.CFG.update(PN=PN, TITLE_EN='Ashtray, interlocking plates', TITLE_AR='منفضة سجائر بألواح متقاطعة',
              SIZE=f'{L:.0f} x {L:.0f} x {H:.0f} mm (estimated)', MAT_EN='MATERIAL  Stainless steel sheet, thickness by Production', MAT_AR='الخامة: ستانلس ستيل، السماكة من التصنيع',
              FIN_EN='FINISH  brushed stainless steel', FIN_AR='التشطيب: ستانلس ستيل مصقول بالفرشاة', DATE=DATE, REV=REV,
              STAMP_EN=f'Approved by Sabry {DATE}. Production review pending. Not engineered', STAMP_AR='معتمد من سبري. مراجعة التصنيع قيد الانتظار. غير مهندس', STAMP_COL='#2f6b45')

def plate_x():   # slots from the top; y up, origin bottom left
    s = [(0, 0), (L, 0), (L, H)]
    for c in (C2, C1): s += [(c+T/2, H), (c+T/2, H-SLOT_D), (c-T/2, H-SLOT_D), (c-T/2, H)]
    return s + [(0, H)]
def plate_y():   # slots from the bottom: three (front outer, front inner, back plate)
    s = [(0, 0)]
    for c in SLOTS_Y: s += [(c-T/2, 0), (c-T/2, SLOT_D), (c+T/2, SLOT_D), (c+T/2, 0)]
    return s + [(L, 0), (L, H), (0, H)]
def tray_blank():  # cross-shaped blank
    a, b = TRAY_H, TRAY_H+TRAY
    return [(a, 0), (b, 0), (b, a), (b+a, a), (b+a, b), (b, b), (b, b+a), (a, b+a), (a, b), (0, b), (0, a), (a, a)]
def tray_folds():
    a, b = TRAY_H, TRAY_H+TRAY
    return [((a, a), (b, a)), ((b, a), (b, b)), ((b, b), (a, b)), ((a, b), (a, a))]
def perim(p): return sum(math.dist(p[i], p[(i+1) % len(p)]) for i in range(len(p)))
def bbox(p): xs = [q[0] for q in p]; ys = [q[1] for q in p]; return min(xs), min(ys), max(xs), max(ys)
PARTS = {'P1': ('Plate with slots from the top', 'لوح بشقوق من الأعلى', 3, plate_x(), 'plate-top-slots'),
         'P2': ('Plate with slots from the bottom', 'لوح بشقوق من الأسفل', 2, plate_y(), 'plate-bottom-slots'),
         'P3': ('Tray, one-piece blank, folded', 'صينية قطعة واحدة مثنية', 1, tray_blank(), 'tray-blank')}
TOTAL_CUT = sum(perim(v[3])*v[2] for v in PARTS.values())

# ---- nesting (hand placed, checked) ----
BW0 = TRAY_H*2+TRAY
NEST = [('P3', GAP, GAP)] + [('P1', 2*GAP+BW0+i*(L+GAP), GAP) for i in range(3)] + [('P2', 2*GAP+BW0+i*(L+GAP), 2*GAP+H) for i in range(2)]
def nsize(k): b = bbox(PARTS[k][3]); return b[2]-b[0], b[3]-b[1]
def nest_ok():
    r = [(k, x, y, x+nsize(k)[0], y+nsize(k)[1]) for k, x, y in NEST]
    for k, x0, y0, x1, y1 in r:
        if x0 < 0 or y0 < 0 or x1 > SHEET_L or y1 > SHEET_W: return False, f'{k} outside'
    for i in range(len(r)):
        for j in range(i+1, len(r)):
            a, b = r[i], r[j]
            if not (a[3]+GAP-1e-6 <= b[1] or b[3]+GAP-1e-6 <= a[1] or a[4]+GAP-1e-6 <= b[2] or b[4]+GAP-1e-6 <= a[2]): return False, f'{a[0]}/{b[0]} spacing'
    return True, 'ok'
OK, MSG = nest_ok(); assert OK, MSG

# ---- DXF ----
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); d.layers.add('FOLD', color=1); d.layers.add('SHEET', color=3); return d
def add_part(msp, k, ox, oy):
    pts = PARTS[k][3]; b = bbox(pts)
    msp.add_lwpolyline([(ox+x-b[0], oy+y-b[1]) for x, y in pts], close=True, dxfattribs={'layer': 'CUT'})
    if k == 'P3':
        for p, q in tray_folds(): msp.add_line((ox+p[0]-b[0], oy+p[1]-b[1]), (ox+q[0]-b[0], oy+q[1]-b[1]), dxfattribs={'layer': 'FOLD'})
for k, v in PARTS.items():
    d = new_doc(); add_part(d.modelspace(), k, 0, 0); d.saveas(f'{OUT}/{PN}_rev{REV}_{k}_{v[4]}.dxf')
d = new_doc(); m = d.modelspace()
m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
for k, x, y in NEST: add_part(m, k, x, y)
d.saveas(f'{OUT}/{PN}_rev{REV}_nest_{SHEET_L}x{SHEET_W}.dxf')

N = 5
S = .5   # 1:2 for views and flat patterns
# ================= SHEET 1: views =================
px = lambda x: 85 + x*S
py = lambda y: 116 - y*S
b = t(22, 50, 'PLAN', 2.8, 600) + t(150, 50, 'المسقط الأفقي', 2.6, 500, 'end')
PYC = 116 - (-YMID)*S*0 # plan keeps y world
for y0 in (FRONT_IN, FRONT_OUT, BACK): b += rect(px(-L/2), py(y0+T/2), L*S, T*S, .4, INK, FILL)
for x0 in (-CL, CL): b += rect(px(x0-T/2), py(Y_END), T*S, L*S, .4, INK, '#e3dfd6')
b += rect(px(-TRAY/2), py(TRAY/2), TRAY*S, TRAY*S, .3, HID, 'none', '1.4 1')
b += t(px(0), py(0)+1, 'tray (dashed: inside the plates)', 1.9, 400, 'middle', HID) + t(px(0), py(0)+4, 'الصينية داخل الألواح', 1.9, 400, 'middle', HID)
b += t(px(L/2)+3, py(FRONT_OUT-T/2)+3, 'front: two plates', 1.9, 400, fill=HID) + t(px(L/2)+3, py(BACK)+1, 'back: one plate', 1.9, 400, fill=HID)
b += dim_v(px(L/2)+8, py(FRONT_IN-T/2), py(FRONT_OUT+T/2), f'{PAIR_GAP:.0f}', ext=px(L/2)+1) if False else ''
b += dim_h(px(-L/2), px(L/2), py(Y_START)+8, f'{L:.0f}', ext=py(Y_START)) + dim_v(px(-L/2)-7, py(Y_END), py(Y_START), f'{L:.0f}', ext=px(-L/2))
b += dim_h(px(-CL+T/2), px(CL-T/2), py(Y_END)-5, '160 clear', ext=py(Y_END)-1)
b += balloon(px(-L/2)-3, py(BACK), 1) + balloon(px(CL), py(Y_END)-7, 2) + balloon(px(0)+25, py(-30), 3)
fx = lambda x: 160 + (x+L/2)*S; fz = lambda z: 150 - z*S
sx = lambda y: 290 + (y-Y_START)*S
b += t(160, 100, 'FRONT ELEVATION', 2.8, 600) + t(270, 104, 'الواجهة الأمامية', 2.6, 500, 'end')
b += rect(fx(-L/2), fz(H), L*S, H*S, .4, INK, FILL)
for x0 in (-CL, CL): b += rect(fx(x0-T/2), fz(H), T*S, H*S, .4, INK, '#e3dfd6')
b += rect(fx(-TRAY/2), fz(TRAY_H), TRAY*S, TRAY_H*S, .3, HID, 'none', '1.4 1')
b += dim_h(fx(-L/2), fx(L/2), fz(0)+7, f'{L:.0f}', ext=fz(0)) + dim_v(fx(L/2)+7, fz(H), fz(0), f'{H:.0f}', ext=fx(L/2))
b += t(290, 100, 'SIDE ELEVATION', 2.8, 600) + t(400, 104, 'الواجهة الجانبية', 2.6, 500, 'end')
b += rect(sx(Y_START), fz(H), L*S, H*S, .4, INK, FILL)
for y0 in (FRONT_IN, FRONT_OUT, BACK): b += rect(sx(y0-T/2), fz(H), T*S, H*S, .4, INK, '#e3dfd6')
b += rect(sx(-TRAY/2), fz(TRAY_H), TRAY*S, TRAY_H*S, .3, HID, 'none', '1.4 1')
b += dim_h(sx(Y_START), sx(Y_END), fz(0)+7, f'{L:.0f}', ext=fz(0))
b += t(160, 175, 'The side shows the two plates of the front (left) and the one plate of the back (right).', 2.0, 400, fill=HID) + t(400, 175, 'الجانب: لوحان في الأمام ولوح واحد في الخلف.', 2.0, 400, 'end', HID)
b += t(22, 191, 'REFERENCE PHOTO (not ours; the construction is inferred from it, approximate)', 2.5, 600) + t(212, 195, 'صورة مرجعية (ليست لنا، والتركيب مستنتج منها)', 2.4, 500, 'end')
b += f'<image href="{datauri(REFIMG, 1100)}" x="22" y="198" width="190" height="70.4" preserveAspectRatio="xMidYMid meet"/>' + rect(22, 198, 190, 70.4, .2, HID)
b += t(22, 272, 'Photo as received. A cigarette (about 84 mm) is the only scale in it.', 2.0) + t(212, 275, 'الصورة كما وردت. السيجارة (حوالي ٨٤ مم) هي المقياس الوحيد.', 2.0, 400, 'end')
cx = 228
b += t(cx, 205, 'FINISH (approved by Sabry)', 2.5, 600) + t(410, 205, 'التشطيب (معتمد من سبري)', 2.4, 500, 'end')
rows = [('Brushed stainless steel  #A7ACB1', 'ستانلس ستيل مصقول بالفرشاة', '#A7ACB1', 'Natural metal, no paint. Brush pattern and polish: Production')]
for i, (en, ar, hexv, note) in enumerate(rows):
    yy = 212 + i*7
    b += rect(cx, yy-3, 6, 4, .2, INK, hexv) + t(cx+8, yy, en, 2.2) + t(410, yy, ar, 2.2, 400, 'end') + t(cx+8, yy+2.7, note, 1.8, 400, fill=HID)
b += t(10, 284, 'All sizes are estimated from the photos. Overall 220 x 220 x 60 mm. Real size or the original file is still needed.', 2.1, 400, fill=HID)
b += t(10, 287.5, 'المقاسات كلها مقدّرة من الصور. نحتاج المقاس الحقيقي أو الملف الأصلي.', 2.1, 400, fill=HID)
sh1 = sheet(1, N, 'VIEWS', 'المناظير', '1:2', b)

# ================= SHEET 2: flat patterns =================
def draw_poly(x, y, pts, h):
    return poly([(x+px_*S, y+(h-py_)*S) for px_, py_ in pts], .4, INK, FILL)
b = t(10, 22, 'Flat patterns at 1:2. Fold lines dashed. Slot width is the plate thickness, fit clearance by Production.', 2.3, 400, fill=HID) + t(410, 22, 'الأنماط المسطحة بمقياس ١:٢. خطوط الطي متقطعة. خلوص التركيب من التصنيع.', 2.3, 400, 'end', HID)
x1, y1 = 40, 50
b += draw_poly(x1, y1, plate_x(), H) + t(x1, y1-3, '1  PLATE, slots from the top, 3 off', 2.4, 600) + t(x1+L*S, y1-3, 'لوح بشقوق من الأعلى، عدد ٣', 2.4, 600, 'end') + balloon(x1-14, y1+H*S/2, 1)
b += dim_h(x1, x1+L*S, y1+H*S+7, f'{L:.0f}', ext=y1+H*S) + dim_v(x1-4, y1, y1+H*S, f'{H:.0f}', ext=x1)
b += dim_h(x1, x1+C1*S, y1-6, f'{C1:.1f}', ext=y1) + dim_v(x1+L*S+6, y1, y1+SLOT_D*S, f'{SLOT_D:.0f}', ext=x1+L*S) if False else ''
b += dim_h(x1, x1+C1*S, y1+H*S+14, f'{C1:.1f} to slot centre', ext=y1+H*S) + dim_v(x1+L*S+6, y1+H*S-SLOT_D*S, y1+H*S, f'{SLOT_D:.0f} deep', ext=x1+L*S)
x2, y2 = 40, 130
b += draw_poly(x2, y2, plate_y(), H)
for c_ in SLOTS_Y: b += t(x2+c_*S, y2+H*S+3.5, f'{c_:.1f}', 1.8, 400, 'middle', DIM) + t(x2, y2-3, '2  PLATE, slots from the bottom, 2 off', 2.4, 600) + t(x2+L*S, y2-3, 'لوح بشقوق من الأسفل، عدد ٢', 2.4, 600, 'end') + balloon(x2-14, y2+H*S/2, 2)
b += dim_h(x2, x2+L*S, y2+H*S+7, f'{L:.0f}', ext=y2+H*S) + dim_v(x2-4, y2, y2+H*S, f'{H:.0f}', ext=x2) + dim_v(x2+L*S+6, y2, y2+SLOT_D*S, f'{SLOT_D:.0f} deep', ext=x2+L*S)
x3, y3 = 230, 50
bb = bbox(tray_blank()); BW = bb[2]-bb[0]
b += draw_poly(x3, y3, tray_blank(), BW)
for p, q in tray_folds(): b += line(x3+p[0]*S, y3+(BW-p[1])*S, x3+q[0]*S, y3+(BW-q[1])*S, .25, '#b3261e', '2 1.2')
b += t(x3, y3-3, '3  TRAY, one-piece blank, 1 off', 2.4, 600) + t(x3+BW*S, y3-3, 'الصينية: قطعة واحدة، عدد ١', 2.4, 600, 'end') + balloon(x3-14, y3+BW*S/2, 3)
b += dim_h(x3, x3+BW*S, y3+BW*S+7, f'{BW:.0f}', ext=y3+BW*S) + dim_v(x3-4, y3, y3+BW*S, f'{BW:.0f}', ext=x3) + dim_h(x3+TRAY_H*S, x3+(TRAY_H+TRAY)*S, y3+BW*S+14, f'{TRAY:.0f} base', ext=y3+BW*S) + dim_v(x3+BW*S+6, y3, y3+TRAY_H*S, f'{TRAY_H:.0f} wall', ext=x3+BW*S)
dx, dy = 24, 200
b += t(dx, dy, 'DATA', 2.4, 600) + t(224, dy, 'بيانات', 2.4, 600, 'end')
for i, ln in enumerate([f'Plates: {L:.0f} x {H:.0f}, thickness {T:.0f} assumed for the layout only. Clear gap between the inner front plate and the back plate {2*CL-T:.0f}.',
                        f'Slots {T:.0f} wide, {SLOT_D:.0f} deep (half the height). Parts 1: slots at {C1} and {C2:.1f} from one end, from the top. Parts 2: three slots at {SLOTS_Y[0]:.1f}, {SLOTS_Y[1]:.1f} and {SLOTS_Y[2]:.1f}, from the bottom.',
                        f'Tray: base {TRAY:.0f} x {TRAY:.0f}, walls {TRAY_H:.0f} high, proposed inside bend radius {TRAY_R:.0f} (from the photo). Corner relief and closing: Production.',
                        f'Front side: two parallel plates {PAIR_GAP:.0f} apart (the reference keeps standing cigarettes in that gap). Back side: one plate. Parts 1 are the three X plates, parts 2 the two cross plates.']):
    b += t(dx, dy+6+i*4.2, ln, 2.0)
b += t(224, dy+27, 'الألواح: سماكتها مفترضة للرسم فقط، والشقوق نصف الارتفاع. لوحان في الجهة الأمامية ولوح واحد في الخلفية.', 2.0, 400, 'end') + t(224, dy+31, 'الصينية قطعة واحدة مثنية، ونصف قطر الثني مقترح من الصورة.', 2.0, 400, 'end')
sh2 = sheet(2, N, 'PART SHEET', 'ورقة القطع', '1:2', b)

# ================= SHEET 3: assembly (exploded, oblique) =================
S3 = .56
def pr(x, y, z, ox=110, oy=238): return (ox + (x + .5*y)*S3*.8, oy - (z + .5*y)*S3*.8)
def box(x0, x1, y0, y1, z0, z1, fill=FILL):
    f = [pr(x0, y0, z0), pr(x1, y0, z0), pr(x1, y0, z1), pr(x0, y0, z1)]
    top = [pr(x0, y0, z1), pr(x1, y0, z1), pr(x1, y1, z1), pr(x0, y1, z1)]
    rt = [pr(x1, y0, z0), pr(x1, y1, z0), pr(x1, y1, z1), pr(x1, y0, z1)]
    return poly(rt, .35, INK, '#cfcac0') + poly(top, .35, INK, '#f7f5ef') + poly(f, .35, INK, fill)
b = t(10, 22, 'EXPLODED VIEW (proposed assembly, Production decides jigs, welds and fixings)', 2.5, 600) + t(410, 22, 'منظر مفكك (تجميع مقترح، والتصنيع يقرر القوالب واللحام)', 2.5, 600, 'end')
items = []
for y0 in (FRONT_IN, FRONT_OUT, BACK): items.append((y0+T/2, box(-L/2, L/2, y0-T/2, y0+T/2, 0, H)))   # X plates, bottom row
for x0 in (-CL, CL): items.append((Y_END, box(x0-T/2, x0+T/2, Y_START, Y_END, 110, 110+H, '#e3dfd6')))   # Y plates lifted
for _, s_ in sorted(items, key=lambda i: -i[0]): b += s_
b += box(-TRAY/2, TRAY/2, -TRAY/2, TRAY/2, 260, 260+TRAY_H, '#d9d4ca')
for xx, yy in ((-CL, Y_START), (CL, Y_START)):
    a_ = pr(xx, yy, 110); c_ = pr(xx, yy, H); b += line(a_[0], a_[1]+1, c_[0], c_[1]-1, .2, HID, '1 1')
a_ = pr(0, -TRAY/2, 260); c_ = pr(0, -TRAY/2, 115); b += line(a_[0], a_[1], c_[0], c_[1], .2, HID, '1 1')
b += balloon(*[v+d for v, d in zip(pr(-L/2, BACK, H/2), (-7, 0))], 1) + balloon(*[v+d for v, d in zip(pr(-CL, Y_START, 110+H/2), (-8, 0))], 2) + balloon(*[v+d for v, d in zip(pr(-TRAY/2, -TRAY/2, 260+TRAY_H/2), (-8, 0))], 3)
b += t(22, 262, 'Feet or pads under the plates: bought-in, to be decided by Production.', 2.1, 400, fill=HID) + t(224, 266, 'قطع حماية تحت الألواح: جاهزة، تقررها التصنيع.', 2.1, 400, 'end', HID)
sx0 = 235
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end')
steps = [('Cut the three plates 1, the two plates 2 and the tray blank 3.', 'قص الألواح الثلاثة (١) واللوحين (٢) وقطعة الصينية (٣).'),
         ('Fold the tray: four walls up from the base, proposed rounded bottom edges.', 'ثني الصينية: أربعة جدران من القاعدة بحواف سفلية مستديرة.'),
         ('Set the three plates 1 on edge, parallel (two at the front, 10 apart; one at the back). Drop plates 2 across them, slots mating.', 'تثبيت الألواح (١) على حافتها: لوحان في الأمام بينهما ١٠ مم، ولوح في الخلف، ثم إنزال اللوحين (٢).'),
         ('Lower the tray into the square. Fix as Production decides.', 'إنزال الصينية داخل المربع وتثبيتها كما يقرر التصنيع.'),
         ('Finish, fit feet or pads.', 'التشطيب وتركيب قطع الحماية.')]
for i, (en, ar) in enumerate(steps):
    yy = 48 + i*17
    b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 2.4) + t(410, yy+5, ar, 2.4, 400, 'end')
sh3 = sheet(3, N, 'ASSEMBLY', 'التجميع', 'n/a', b)

# ================= SHEET 4: cutting layout =================
S4 = .1
b = t(10, 22, f'CUTTING LAYOUT on an assumed sheet {SHEET_L} x {SHEET_W} (thickness by Production). Assumed, to be confirmed by Production.', 2.4, 600) + t(410, 22, 'مخطط القص على لوح مفترض، السماكة من التصنيع', 2.4, 600, 'end')
ox4, oy4 = 30, 40
b += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6') + t(ox4, oy4-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for k, x, y in NEST:
    pts = PARTS[k][3]; bbx = bbox(pts); H_ = bbx[3]-bbx[1]
    b += poly([(ox4+(x+p[0]-bbx[0])*S4, oy4+(y+(H_-(p[1]-bbx[1])))*S4) for p in pts], .3, INK, FILL)
    sw, sh_ = nsize(k); b += t(ox4+(x+sw/2)*S4, oy4+(y+sh_/2)*S4+1, {'P1': '1', 'P2': '2', 'P3': '3'}[k], 3, 600, 'middle', '#555')
b += dim_h(ox4, ox4+SHEET_L*S4, oy4+SHEET_W*S4+7, f'{SHEET_L}', ext=oy4+SHEET_W*S4) + dim_v(ox4-6, oy4, oy4+SHEET_W*S4, f'{SHEET_W}', ext=ox4)
used_x = max(x+nsize(k)[0] for k, x, y in NEST); used_y = max(y+nsize(k)[1] for k, x, y in NEST)
b += t(30, 195, f'Parts nested with {GAP} mm spacing in a corner of the sheet ({used_x:.0f} x {used_y:.0f} mm). No offcut is claimed.', 2.3)
b += t(30, 200, f'Total cutting length of all parts: {TOTAL_CUT/1000:.2f} m ({TOTAL_CUT:.0f} mm), outlines only, not counting folds.', 2.5, 600)
b += t(410, 195, 'الأجزاء مرتبة بمسافة ١٠ مم في ركن اللوح. لا يُدّعى أي هالك.', 2.3, 400, 'end') + t(410, 200, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.5, 600, 'end')
b += t(30, 210, 'The sheet is far larger than the parts; a real run would nest many ashtrays or use a smaller sheet. Production decides.', 2.2, 400, fill=HID)
sh4 = sheet(4, N, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)

# ================= SHEET 5: BOM and notes =================
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + t(410, 28, 'قائمة المواد', 2.8, 600, 'end') + rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Plate, slots from the top', 'لوح بشقوق من الأعلى', '3', 'Stainless steel sheet'), ('2', 'Plate, slots from the bottom', 'لوح بشقوق من الأسفل', '2', 'Stainless steel sheet'), ('3', 'Tray, one-piece folded blank', 'صينية مثنية', '1', 'Stainless steel sheet'), ('4', 'Feet or pads', 'قطع حماية', 'by Production', 'Bought-in, to be decided')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*7
    b += line(10, yy+2.2, 410, yy+2.2, .15, HID) + t(12, yy, n_, 2.4) + t(24, yy, en, 2.4) + t(120, yy, ar, 2.4, 400, 'end') + t(150, yy, q, 2.4) + t(215, yy, m_, 2.4)
b += t(10, 82, 'NOTES', 2.8, 600) + t(410, 82, 'ملاحظات', 2.8, 600, 'end')
notes = [('No dimensions were supplied. All sizes (220 x 220 x 60 overall) are estimated from the photos, with a cigarette (about 84 mm) as scale. Real size or the original file is needed.', 'لم تُقدَّم مقاسات. كل المقاسات مقدّرة من الصور بالسيجارة كمقياس.'),
         ('The construction is inferred from the photos: five plates in a # pattern, interlocking (two parallel plates on the front side, one on the back, two cross plates), with a folded tray in the middle. Production to confirm.', 'طريقة الصنع مستنتجة من الصور: خمسة ألواح متقاطعة (لوحان في جهة ولوح في الجهة المقابلة ولوحان متقاطعان) وصينية مثنية في الوسط.'),
         ('Plate thickness is drawn at 3 mm for the layout only. Material, thickness, bend radius and allowance, tolerances, fit clearance, joints and welding are Production\'s to decide.', 'السماكة ٣ مم للرسم فقط. الخامة والسماكة والثني والسماحيات واللحام يقررها التصنيع.'),
         ('Joint: cross-halving (slots to half the height) is proposed because the product is called interlocking plates. Welded or other joints are Production\'s call.', 'الوصلة المقترحة: تقاطع بنصف الارتفاع. غير ذلك يقرره التصنيع.'),
         ('The reference shows a small clip for resting a cigarette. It is not clear in the photos and is not drawn.', 'يظهر في المرجع مشبك صغير لوضع السيجارة، وهو غير واضح في الصور ولم يُرسم.'),
         ('Finish: brushed stainless steel, approved by Sabry. The reference is dark blackened steel; the brush and tone are Production\'s to match with a sample.', 'التشطيب: ستانلس ستيل مصقول بالفرشاة، معتمد من سبري. المرجع فولاذ مسوّد، ويطابقه التصنيع بعينة.'),
         ('No structural claims, stress figures, costs or prices on this drawing. Not engineered. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا تكاليف ولا أسعار. الصياغة العربية مسودة.')]
for i, (en, ar) in enumerate(notes):
    yy = 91 + i*13
    b += t(12, yy, f'{i+1}.', 2.4, 600) + t(18, yy, en, 2.2) + t(410, yy+5, ar, 2.3, 400, 'end')
sh5 = sheet(5, N, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)

for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1): open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('perimeters', {k: round(perim(v[3])) for k, v in PARTS.items()}, 'total cut', round(TOTAL_CUT), 'nest', MSG)
