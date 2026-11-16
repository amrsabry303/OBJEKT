"""OBJ-164: corner shelf, WEDGE, sold as a pair. Production drawing set, REV 1 (DRAFT, replaces rev 0).
Run: python3 make_obj164_rev1.py <repo root>   Then make_pdf.js for the PDF.
Rev 1 (15 Nov 2026): Sabry said the shelf is a wedge and rev 0 (vertical gusset in the corner diagonal) was wrong, and that it is
ONE TRIANGLE SHEET BENT AT 90 DEGREES. Reading: the flat sheet is a triangle R-L-P with the bend line K-L (K on the base R-P).
Folded 90 degrees along K-L it gives a horizontal top plate K-R-L (right angle at K, legs 250 x 250, along the two walls) and a
vertical plate K-L-P in the plane of the left wall (top edge K-L = 250, vertical edge K-P = 250 in the wall corner, sloped edge L-P).
Size 250 x 250 mm legs is Sabry's (15 Nov: "make it 25 x 25"; it was 220 x 220, production-book caption "2pc 22x22CM", until then). 2 mm brushed stainless, a 15 mm
two screw holes in the vertical plate (Sabry 16 Nov: only these two, no flange), pair: PROPOSALS, not costed, Production to confirm.
Sabry 16 Nov: the two triangles (top and vertical plate) are symmetrical and equal size, so the plate is 250 x 250 as well (rev 1 first had it 150 deep).
The flat sheet is then one right isosceles triangle (hypotenuse 2 x 250 = 500) folded 90 degrees along its altitude.
Arabic wording is a draft for a technical reader. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-164'; os.makedirs(OUT, exist_ok=True)
PHOTO = ROOT + '/images/OBJ-164.jpg'
REV = 1; DATE = '16 Nov 2026'; PN = 'OBJ-164'
LEG = 250; T = 2; DROP = LEG                       # DROP = LEG: the vertical plate is the same triangle as the top (Sabry, 16 Nov: symmetrical, equal size)
HYP = LEG*math.sqrt(2)                                  # front edge 311.1
PEDGE = math.hypot(LEG, DROP)                           # sloped edge of the vertical plate 266.2
OH = T + DROP
HOLE_D = 5
PLATE_HOLES = [(40, 20), (130, 20)]                      # (distance along K-L from K, depth below the bend line): 2 screw holes in the vertical plate (Sabry, 15 Nov)
SHEET_L, SHEET_W, GAP = 2500, 1250, 10
OX, OY = DROP, 0                                       # flat origin offset so the bbox starts at (0,0); K = (OX, OY)
KX, KY = OX, OY
def flat_pts():
    L = (KX, KY+LEG); R = (KX+LEG, KY); Pp = (KX-DROP, KY)
    return [Pp, L, R]
def holes(): return [(KX-z, KY+d) for d, z in PLATE_HOLES]
def perim(p): return sum(math.dist(p[i], p[(i+1) % len(p)]) for i in range(len(p)))
BBW, BBH = DROP+LEG, LEG
PARTS = {'P1': ('Wedge sheet: one triangle, flat', 'لوح الوتد: مثلث واحد مسطح', 2, 'wedge', (BBW, BBH), perim(flat_pts())+len(holes())*math.pi*HOLE_D)}
TOTAL_CUT = sum(v[2]*v[5] for v in PARTS.values())
NEST = [('P1', GAP, GAP), ('P1', GAP+BBW+GAP, GAP)]
def size(k): return PARTS[k][4]
def nest_ok():
    r = [(k, x, y, x+size(k)[0], y+size(k)[1]) for k, x, y in NEST]
    for k, x0, y0, x1, y1 in r:
        if x0 < 0 or y0 < 0 or x1 > SHEET_L or y1 > SHEET_W: return False, f'{k} outside sheet'
    for i in range(len(r)):
        for j in range(i+1, len(r)):
            a, b = r[i], r[j]
            if not (a[3]+GAP-1e-6 <= b[1] or b[3]+GAP-1e-6 <= a[1] or a[4]+GAP-1e-6 <= b[2] or b[4]+GAP-1e-6 <= a[2]): return False, f'{a[0]} / {b[0]} spacing'
    return True, 'ok'
OK, MSG = nest_ok(); assert OK, MSG
USED_Y = max(y+size(k)[1] for k, x, y in NEST); USED_X = max(x+size(k)[0] for k, x, y in NEST)
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); d.layers.add('FOLD', color=5); d.layers.add('SHEET', color=3); return d
def add_part(msp, key, ox, oy, fold=True):
    msp.add_lwpolyline([(ox+x, oy+y) for x, y in flat_pts()], close=True, dxfattribs={'layer': 'CUT'})
    for hx, hy in holes(): msp.add_circle((ox+hx, oy+hy), HOLE_D/2, dxfattribs={'layer': 'CUT'})
    if fold:
        msp.add_line((ox+KX, oy+KY), (ox+KX, oy+KY+LEG), dxfattribs={'layer': 'FOLD'})                # main bend, 90 deg, K-L
FN = {'P1': 'wedge-sheet'}
for k in PARTS:
    doc = new_doc(); add_part(doc.modelspace(), k, 0, 0); doc.saveas(f'{OUT}/{PN}_rev{REV}_{k}_{FN[k]}.dxf')
doc = new_doc(); m = doc.modelspace()
m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
for k, x, y in NEST: add_part(m, k, x, y)
doc.saveas(f'{OUT}/{PN}_rev{REV}_nest_{SHEET_L}x{SHEET_W}.dxf')

# ---- SVG helpers (A3 landscape, mm) ----
FONT = "DejaVu Sans, Inter, Arial, sans-serif"
INK, DIM, HID, FILL = '#161616', '#2a4a7a', '#7a7a7a', '#f1efe9'
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;')
def t(x, y, s, size=2.6, w=400, anchor='start', fill=INK, rtl=False, extra=''):
    extra = extra.replace(' direction="rtl"', '')
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size}" font-weight="{w}" text-anchor="{anchor}" fill="{fill}"{extra}>{esc(s)}</text>'
def bi(x, y, en, ar, wd, size=2.6, w=400, fill=INK):
    """English on the left, Arabic on the next line, right aligned in a column of width wd."""
    return t(x, y, en, size, w, fill=fill) + t(x+wd, y+size*1.3, ar, size, w, 'end', fill)
def line(x1, y1, x2, y2, sw=.3, col=INK, dash=None):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def rect(x, y, w, h, sw=.35, col=INK, fill='none', dash=None):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def poly(pts, sw=.35, col=INK, fill='none', dash=None):
    return '<polygon points="' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in pts) + f'" fill="{fill}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
def arrow(x, y, dx, dy):
    n = math.hypot(dx, dy); ux, uy = dx/n, dy/n
    return f'<polygon points="{x:.2f},{y:.2f} {x-ux*2+uy*.7:.2f},{y-uy*2-ux*.7:.2f} {x-ux*2-uy*.7:.2f},{y-uy*2+ux*.7:.2f}" fill="{DIM}"/>'
def dim_h(x1, x2, y, label, off=0, ext=None):
    s = line(x1, y, x2, y, .2, DIM) + arrow(x1, y, 1, 0) + arrow(x2, y, -1, 0)
    if ext is not None: s += line(x1, ext, x1, y+(2 if y > ext else -2), .15, DIM) + line(x2, ext, x2, y+(2 if y > ext else -2), .15, DIM)
    return s + t((x1+x2)/2, y-1, label, 2.4, 500, 'middle', DIM)
def dim_v(x, y1, y2, label, ext=None):
    s = line(x, y1, x, y2, .2, DIM) + arrow(x, y1, 0, 1) + arrow(x, y2, 0, -1)
    if ext is not None: s += line(ext, y1, x+(2 if x > ext else -2), y1, .15, DIM) + line(ext, y2, x+(2 if x > ext else -2), y2, .15, DIM)
    return s + f'<text transform="translate({x-1:.2f} {(y1+y2)/2:.2f}) rotate(-90)" font-family="{FONT}" font-size="2.4" font-weight="500" text-anchor="middle" fill="{DIM}">{esc(label)}</text>'
def balloon(x, y, n):
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.2" fill="#fff" stroke="{INK}" stroke-width=".3"/>' + t(x, y+1.1, str(n), 3, 600, 'middle')
def datauri(path, w=360):
    im = Image.open(path).convert('RGB'); im.thumbnail((w, w)); b = io.BytesIO(); im.save(b, 'JPEG', quality=72)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()


STAMP = 'DRAFT, not approved, not engineered'; STAMP_AR = 'مسودة، غير معتمدة، غير مهندسة'
AR = ' direction="rtl"'
def frame(n, N, title_en, title_ar, scale):
    s = rect(5, 5, 410, 287, .5) + rect(7, 7, 406, 283, .2)
    X, Y, Wd = 228, 247, 185
    s += rect(X, Y, Wd, 41, .4, fill='#fff')
    s += line(X, Y+9, X+Wd, Y+9, .25) + line(X, Y+20, X+Wd, Y+20, .25) + line(X, Y+31, X+Wd, Y+31, .25) + line(X+92, Y+9, X+92, Y+41, .25)
    s += bi(X+2, Y+4, f'{PN}   Corner shelf, wedge (pair)', 'رف زاوية وتد (زوج)', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  {LEG} x {LEG} x {OH} mm each', 'المقاس لكل رف', 88, 2.1) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, 'MATERIAL  Stainless sheet 2 mm (proposal)', 'الخامة: ستانلس ٢ مم (مقترح)', 88, 2.1) + bi(X+94, Y+25, 'FINISH  Brushed (proposal)', 'التشطيب: مبشور (مقترح)', 88, 2.1)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, '#b3261e', '#fff')
    s += t(X+Wd/2, Y-8.6, STAMP, 2.9, 700, 'middle', '#b3261e') + t(X+Wd/2, Y-3.8, STAMP_AR, 2.9, 700, 'middle', '#b3261e')
    s += t(10, 14, title_en, 4.2, 700) + t(410, 14, title_ar, 4.2, 700, 'end', extra=' direction="rtl"')
    return s
def sheet(n, N, title_en, title_ar, scale, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, N, title_en, title_ar, scale)}{body}</svg>'
N = 5; S = .28
# ================= SHEET 1: views =================
oxp, oyp = 30, 40
def px(x): return oxp + x*S
def py(y): return oyp + y*S
b = t(22, 30, 'PLAN (top, true shape)', 2.8, 600) + t(205, 34, 'المسقط الأفقي', 2.6, 500, 'end', extra=AR)
b += poly([(px(x), py(y)) for x, y in [(0, 0), (LEG, 0), (0, LEG)]], .45, INK, '#e6e6e4')
b += rect(px(0)-1.5, py(0), 1.5, LEG*S, .6, '#555', '#bbb') + rect(px(0), py(0)-1.5, LEG*S, 1.5, .3, '#999', '#ddd')
b += t(px(LEG/2), py(0)-3, 'RIGHT WALL / الحائط الأيمن', 2, 400, 'middle', HID) + t(px(0)-4, py(LEG)+4, 'LEFT WALL (plate here) / الحائط الأيسر', 2, 400, 'start', HID)
b += dim_h(px(0), px(LEG), py(0)-9, f'{LEG}', ext=py(0)-1.5) + dim_v(px(0)-9, py(0), py(LEG), f'{LEG}', ext=px(0)-1.5)
mx, my = (px(LEG)+px(0))/2, (py(0)+py(LEG))/2
b += t(mx+8, my-3, f'front edge {HYP:.1f}', 2.3, 500, fill=DIM) + t(mx+8, my+.5, 'الحافة الأمامية', 2.2, 400, 'start', DIM, extra=AR)
b += t(px(8), py(LEG*.28), '90°', 2.4, 500, fill=DIM) + t(px(LEG*.06), py(LEG*.5), 'K', 2.4, 600, fill=DIM)
b += t(px(LEG*.12), py(LEG*.7), 'The vertical plate hangs from the left leg,', 2.0, 400, fill=HID) + t(px(LEG*.12), py(LEG*.7)+3, 'flat on the left wall (see next view).', 2.0, 400, fill=HID)
# ELEVATION A: looking at the left wall (plate in true shape)
ox, oz = 245, 48
def fx(x): return ox + x*S
def fz(z): return oz + z*S
b += t(215, 30, 'ELEVATION A (looking at the left wall: plate in true shape)', 2.8, 600) + t(410, 34, 'منظر أ (نحو الحائط الأيسر: اللوح بحجمه الحقيقي)', 2.6, 500, 'end', extra=AR)
b += poly([(fx(0), fz(T)), (fx(LEG), fz(T)), (fx(0), fz(T+DROP))], .45, INK, '#cfcfcc')
b += rect(fx(0), fz(0), LEG*S, T*S, .45, INK, '#d8d8d5')
for d_, z_ in PLATE_HOLES: b += f'<circle cx="{fx(d_):.2f}" cy="{fz(T+z_):.2f}" r="{HOLE_D/2*S:.2f}" fill="#fff" stroke="{INK}" stroke-width=".3"/>'
b += t(fx(PLATE_HOLES[0][0]), fz(T+PLATE_HOLES[0][1])+9, f'2 holes dia {HOLE_D}, {PLATE_HOLES[0][1]} below the top edge, at {PLATE_HOLES[0][0]} and {PLATE_HOLES[1][0]} from the corner', 2.0, 400, fill=DIM) + t(fx(PLATE_HOLES[0][0]), fz(T+PLATE_HOLES[0][1])+12, 'ثقبان لبراغي اللوح الرأسي', 2.0, 400, fill=DIM, extra=AR)
b += rect(fx(0)-1.5, fz(-5), 1.5, (OH+10)*S, .6, '#555', '#bbb') + t(fx(0)-4, fz(OH/2), 'CORNER', 2, 400, 'end', HID)
b += dim_h(fx(0), fx(LEG), fz(0)-5, f'{LEG}', ext=fz(0)) + dim_v(fx(LEG)+8, fz(0), fz(OH), f'{OH}', ext=fx(LEG)) + dim_v(fx(LEG)+16, fz(T), fz(OH), f'{DROP}', ext=fx(LEG))
b += t(fx(LEG*.4), fz(T+DROP*.3), f'sloped edge {PEDGE:.1f}', 2.0, 400, fill=HID) + t(fx(LEG*.4), fz(T+DROP*.3)+3, 'الحافة المائلة', 2.0, 400, fill=HID, extra=AR)
b += balloon(fx(LEG*.3), fz(0)-12, 1) + balloon(fx(14), fz(T+DROP*.75), 2)
# ELEVATION B: looking at the right wall
ox2 = 245; oz2 = 138
def sx(x): return ox2 + x*S
def sz(z): return oz2 + z*S
b += t(215, 128, 'ELEVATION B (looking at the right wall: plate edge-on)', 2.8, 600) + t(410, 132, 'منظر ب (نحو الحائط الأيمن: اللوح من جانبه)', 2.6, 500, 'end', extra=AR)
b += rect(sx(0), sz(0), LEG*S, T*S, .45, INK, '#d8d8d5')
b += rect(sx(0), sz(T), T*S, DROP*S, .45, INK, '#bdbdb9')
b += rect(sx(0)-1.5, sz(-5), 1.5, (OH+10)*S, .3, '#999', '#ddd') + t(sx(0)-4, sz(OH/2), 'CORNER', 2, 400, 'end', HID)
b += dim_h(sx(0), sx(LEG), sz(OH)+8, f'{LEG}', ext=sz(OH)) + dim_v(sx(LEG)+8, sz(0), sz(OH), f'{OH}', ext=sx(LEG))
b += t(sx(70), sz(T+30), 'the plate is edge-on here (2 mm line); no flange', 2.0, 400, fill=HID) + t(sx(70), sz(T+30)+3, 'اللوح من جانبه: خط بسماكة ٢ مم', 2.0, 400, fill=HID, extra=AR)
# reference photo + notes
b += t(22, 160, 'REFERENCE PHOTO (Sabry, 12 Nov; maker unknown, device on the shelf is not ours)', 2.3, 600) + t(205, 164, 'صورة مرجعية (الجهاز ليس لنا)', 2.3, 500, 'end', extra=AR)
b += f'<image href="{datauri(PHOTO)}" x="22" y="166" width="64" height="74" preserveAspectRatio="xMidYMid slice"/>' + rect(22, 166, 64, 74, .2, HID)
for i, ln in enumerate(['Rev 1 (Sabry, 15 Nov): a wedge, one triangle', 'sheet bent 90 degrees. Horizontal triangular', 'top, and a vertical triangular plate hanging', 'from its left leg, flat on the left wall.', 'The shelf-top device in the photo is not drawn.']):
    b += t(92, 172+i*3.6, ln, 2.0, 400, fill=HID)
b += t(205, 172, 'مراجعة ١: وتد من مثلث واحد مثني ٩٠°', 2.0, 400, 'end', HID, extra=AR)
b += t(22, 262, 'Colourways: bare brushed stainless (proposal). No paint colour.  ألوان: ستانلس مبشور بدون دهان (مقترح).', 2.0, 400, fill=HID)
b += t(22, 276, f'Leg {LEG} x {LEG} is Sabry\'s (15 Nov, "make it 25 x 25"; was 22 x 22). Thickness 2, screw holes, pair: PROPOSALS,', 2.0, 400, fill=HID)
b += t(22, 279.5, f'not costed, Production to confirm. Overall height {OH} = top plate {T} + plate {DROP} below it.  المقاسات عدا ٢٥٠ مقترحة، يؤكدها التصنيع.', 2.0, 400, fill=HID)
sh1 = sheet(1, N, 'VIEWS', 'المناظير', '1:3.5', b)

# ================= SHEET 2: flat pattern =================
S2 = .6
b = t(10, 22, 'Flat pattern at about 1:1.7, bend allowance NOT applied (Production adds it). Fold lines dashed.', 2.3, 400, fill=HID) + t(410, 22, 'النمط المسطح، بدون سماحية الثني (يضيفها التصنيع). خطوط الثني متقطعة.', 2.3, 400, 'end', HID)
x1, y1 = 40, 50
def fx1(x): return x1 + x*S2
def fy1(y): return y1 + (BBH-y)*S2
b += poly([(fx1(x), fy1(y)) for x, y in flat_pts()], .4, INK, FILL)
for hx, hy in holes(): b += f'<circle cx="{fx1(hx):.2f}" cy="{fy1(hy):.2f}" r="{HOLE_D/2*S2:.2f}" fill="#fff" stroke="{INK}" stroke-width=".3"/>'
b += line(fx1(KX), fy1(KY), fx1(KX), fy1(KY+LEG), .35, DIM, '2.5 1.2') + line(fx1(KX+10), fy1(KY), fx1(KX+LEG-10), fy1(KY), .25, DIM, '2 1')
b += t(fx1(KX)+2, fy1(KY+LEG*.55), 'bend 90 deg, K-L', 2.2, 500, fill=DIM) + t(fx1(KX)+2, fy1(KY+LEG*.55)+3, 'ثنية ٩٠° K-L', 2.0, 400, fill=DIM)
b += t(fx1(KX-DROP*.6), fy1(KY+LEG*.18), 'VERTICAL PLATE', 2.2, 600, fill='#555') + t(fx1(KX-DROP*.6), fy1(KY+LEG*.18)+3, 'اللوح الرأسي', 2.0, 400, fill='#555', extra=AR)
b += t(fx1(KX+LEG*.3), fy1(KY+LEG*.18), 'HORIZONTAL TOP', 2.2, 600, fill='#555') + t(fx1(KX+LEG*.3), fy1(KY+LEG*.18)+3, 'الرف الأفقي', 2.0, 400, fill='#555', extra=AR)
b += t(fx1(KX)-2, fy1(KY)+4, 'K', 2.4, 600, fill=DIM) + t(fx1(KX)-2, fy1(KY+LEG)-1.5, 'L', 2.4, 600, fill=DIM) + t(fx1(KX+LEG)+1.5, fy1(KY)+1, 'R', 2.4, 600, fill=DIM) + t(fx1(KX-DROP)-4, fy1(KY)+1, 'P', 2.4, 600, fill=DIM)
b += dim_h(fx1(KX-DROP), fx1(KX), fy1(KY)+8, f'{DROP}', ext=fy1(KY)) + dim_h(fx1(KX), fx1(KX+LEG), fy1(KY)+8, f'{LEG}', ext=fy1(KY))
b += dim_v(fx1(KX-DROP)-6, fy1(KY+LEG), fy1(KY), f'{LEG}  (K-L)', ext=fx1(KX))
b += t(x1, y1-8, '1  WEDGE SHEET, one flat triangle, 2 off (one per shelf)', 2.4, 600) + t(x1+BBW*S2, y1-8, 'لوح الوتد، مثلث واحد، عدد ٢', 2.4, 600, 'end', extra=AR) + balloon(x1-14, y1+BBH*S2/2, 1)
dx, dy = 235, 60
b += t(dx, dy, 'DATA  mm', 2.4, 600) + t(410, dy, 'بيانات', 2.4, 600, 'end', extra=AR)
rows = [('Flat sheet outline', 'triangle R-L-P'), ('Flat size (bbox)', f'{BBW:.0f} x {BBH:.0f}'), ('Base P-R (K on it)', f'{DROP+LEG}'), ('Height K-L (bend line)', f'{LEG}'),
        ('Top plate (folded)', f'K-R-L, right angle at K, {LEG} x {LEG}'), ('Vertical plate (folded)', f'K-L-P, {LEG} x {DROP}, sloped edge {PEDGE:.1f}'), ('Bend', '90 deg along K-L'),
        ('Vertical plate holes', f'{len(PLATE_HOLES)} dia {HOLE_D}, {PLATE_HOLES[0][1]} from the bend'), ('Outline length each', f'{PARTS["P1"][5]:.0f}')]
for i, (k, v) in enumerate(rows):
    yy = dy+6+i*5
    b += t(dx, yy, k, 2.1, 400) + t(dx+60, yy, v, 2.1, 600) + line(dx, yy+1.6, dx+165, yy+1.6, .12, HID)
for i, ln in enumerate(['One triangle sheet, bent 90 degrees along K-L (Sabry, 15 Nov). Folded: K-R-L lies flat as the shelf; K-L-P stands vertical on the left wall.',
                        f'Vertical edge K-P = {DROP} in the wall corner; sloped edge L-P = {PEDGE:.1f}.',
                        f'Vertical plate: two dia {HOLE_D} screw holes (Sabry, 15 Nov), {PLATE_HOLES[0][1]} below the bend line, at {PLATE_HOLES[0][0]} and {PLATE_HOLES[1][0]} from K along K-L (in the flat sheet they are {PLATE_HOLES[0][1]} left of the bend line).',
                        'The two plate screws are seen from the room (screw type and finish: Production). Wall type and plugs are not known.',
                        'Left-hand and mirrored right-hand versions: the drawing shows one hand. Whether the pair is two of the same or a mirrored pair: Sabry to confirm.',
                        'Bend radius and allowance, brushing direction and blending: Production.']):
    b += t(22, 232+i*3.8, ln, 2.0)
b += t(410, 232, 'مثلث واحد مثني ٩٠° عند K-L. طريقة تثبيت اللوح الرأسي بالحائط الأيسر يقررها التصنيع.', 2.0, 400, 'end', extra=AR)
sh2 = sheet(2, N, 'PART SHEET', 'ورقة القطع', '1:1.7', b)

# ================= SHEET 3: folded view =================
SC = .62
def P(x, y, z): return 5+130*SC + (x*.9 - y*.4)*SC, 70 + (x*.25 + y*.45 + z)*SC   # z down
def pl(pts3, fill, sw=.35): return poly([P(*q) for q in pts3], sw, INK, fill)
b = t(10, 22, 'FOLDED SHELF (proposed; Production decides forming, jigs and fixings)', 2.5, 600) + t(410, 22, 'الرف بعد الثني (مقترح، والتصنيع يقرر التشكيل والقوالب والتثبيت)', 2.5, 600, 'end', extra=AR)
b += pl([(0, 0, T), (0, LEG, T), (0, 0, T+DROP)], '#bdbdb9')                                    # vertical plate, left wall plane x = 0
b += pl([(0, 0, 0), (LEG, 0, 0), (0, LEG, 0)], '#d8d8d5', .45)                                  # top plate
b += ''
for q in [(0, 0, 0), (LEG, 0, 0), (0, LEG, 0)]: pass
ax, ay = P(LEG*.3, LEG*.3, 0); b += balloon(ax, ay-6, 1)
ax, ay = P(0, LEG*.3, T+DROP*.3); b += balloon(ax-10, ay+2, 2)
ax, ay = P(0, 0, 0); b += t(ax-8, ay-3, 'K', 2.6, 600, fill=DIM)
ax, ay = P(0, LEG, 0); b += t(ax-6, ay+1, 'L', 2.6, 600, fill=DIM)
ax, ay = P(LEG, 0, 0); b += t(ax+2, ay-1, 'R', 2.6, 600, fill=DIM)
ax, ay = P(0, 0, T+DROP); b += t(ax-8, ay+4, 'P', 2.6, 600, fill=DIM)
b += t(22, 262, 'Fixing: 2 screws and plugs per shelf, through the two holes in the vertical plate (2) into the left wall, seen from the room. No flange.', 2.0, 400, fill=HID)
b += t(224, 266, 'التثبيت: مسماران وفيشر لكل رف عبر ثقبي اللوح الرأسي في الحائط الأيسر، ظاهران من الغرفة. بدون زعنفة.', 2.0, 400, 'end', HID, extra=AR)
sx0 = 245
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end', extra=AR)
steps = [('Cut part 1 (one triangle, outline and holes) from the DXF file; deburr.', 'قص القطعة ١ (مثلث واحد بالفتحات) من ملف DXF وتنعيم الحواف.'),
         ('Bend the sheet 90 degrees along K-L: K-R-L becomes the top, K-L-P the vertical plate.', 'ثني اللوح ٩٠° عند K-L: يصبح K-R-L الرف وK-L-P اللوح الرأسي.'),
         ('Brush the finish in one direction on all visible faces.', 'بشر السطح في اتجاه واحد على كل الوجوه الظاهرة.'),
         ('Fix to the left wall with 2 screws per shelf, through the plate holes; make two shelves for the pair (same hand or mirrored: Sabry to confirm).', 'التثبيت بالحائطين، وصنع رفين للزوج (نفس الاتجاه أو معكوس: سبري يؤكد).')]
for i, (en, ar) in enumerate(steps):
    yy = 48 + i*17
    b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 2.2) + t(410, yy+5, ar, 2.2, 400, 'end', extra=AR)
sh3 = sheet(3, N, 'FOLDED VIEW AND ASSEMBLY', 'منظر مثني والتجميع', 'n/a', b)

# ================= SHEET 4: cutting layout =================
S4 = .1
b = t(10, 22, f'CUTTING LAYOUT for one PAIR on an assumed sheet {SHEET_L} x {SHEET_W} x {T} (proposal, Production to confirm).', 2.4, 600) + t(410, 22, 'مخطط القص لزوج على لوح مفترض، يؤكده التصنيع', 2.4, 600, 'end', extra=AR)
ox4, oy4 = 30, 40
b += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6') + t(ox4, oy4-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for k, x, y in NEST:
    w, h = size(k)
    b += poly([(ox4+(x+px_)*S4, oy4+(y+h-py_)*S4) for px_, py_ in flat_pts()], .3, INK, FILL)
    b += t(ox4+(x+w/2)*S4, oy4+(y+h/2)*S4+1, k[1], 3.4, 600, 'middle', '#555')
b += dim_h(ox4, ox4+SHEET_L*S4, oy4+SHEET_W*S4+7, f'{SHEET_L}', ext=oy4+SHEET_W*S4) + dim_v(ox4-6, oy4, oy4+SHEET_W*S4, f'{SHEET_W}', ext=ox4)
b += t(30, 195, f'Parts nested with {GAP} mm spacing in one corner: about {USED_X:.0f} x {USED_Y:.0f} mm used. No offcut is claimed. Two same-hand sheets shown; a mirrored pair is the same shapes flipped.', 2.3)
b += t(30, 200, f'Total cutting length, 2 wedge sheets (with holes): {TOTAL_CUT/1000:.2f} m ({TOTAL_CUT:.0f} mm), outlines only.', 2.5, 600)
b += t(410, 195, 'الأجزاء مرتبة بمسافة ١٠ مم. لا يُدّعى أي هالك.', 2.3, 400, 'end', extra=AR) + t(410, 200, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.5, 600, 'end', extra=AR)
sh4 = sheet(4, N, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)

# ================= SHEET 5: BOM and notes =================
b = t(10, 28, 'BILL OF MATERIALS (for one PAIR = 2 shelves)', 2.8, 600) + t(410, 28, 'قائمة المواد (لزوج = رفان)', 2.8, 600, 'end', extra=AR)
b += rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Wedge sheet: one triangle bent 90 deg (top and vertical plate)', 'لوح الوتد: مثلث واحد مثني ٩٠°', '2', 'Stainless sheet 2 mm, brushed (proposal)'),
       ('2', 'Wall screw and plug', 'مسمار وفيشر للحائط', '4 (2 per shelf, through the plate)', 'Bought-in; for the wall type, by Production'),
       ('3', 'Screw finish for the visible plate screws', 'تشطيب مسماري اللوح الرأسي', '4', 'Production to decide (match the brushed stainless)')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*7
    b += line(10, yy+2.2, 410, yy+2.2, .15, HID) + t(12, yy, n_, 2.4) + t(24, yy, en, 2.4) + t(140, yy, ar, 2.4, 400, 'end', extra=AR) + t(150, yy, q, 2.4) + t(215, yy, m_, 2.4)
b += t(10, 80, 'NOTES', 2.8, 600) + t(410, 80, 'ملاحظات', 2.8, 600, 'end', extra=AR)
notes = [('REV 1 (15 Nov 2026) replaces rev 0, which was wrong. Sabry: it is a wedge, one triangle sheet bent at 90 degrees. Folded along K-L it gives a horizontal triangular top and a vertical triangular plate flat on the left wall.', 'المراجعة ١ تحل محل ٠: وتد من مثلث واحد مثني ٩٠°، رف أفقي ولوح رأسي على الحائط الأيسر.'),
         (f'Leg length {LEG} x {LEG} mm is Sabry\'s size (15 Nov: "make it 25 x 25"; it was 220 x 220 / book caption "2pc 22x22CM" before), the two straight edges along the walls. Front edge about {HYP:.0f} mm.', 'الضلعان ٢٥٠ × ٢٥٠ مم (مقاس سبري) على الحائطين، والحافة الأمامية حوالي ٣٥٤ مم.'),
         (f'Proposals, not costed, Production to confirm: stainless 2 mm, brushed; vertical plate the same triangle as the top, {LEG} x {DROP} mm (Sabry, 16 Nov: symmetrical, equal size), so overall height {OH}; 2 screw holes dia {HOLE_D} in the vertical plate per shelf and no flange (Sabry, 16 Nov); sold as a pair.', 'مقترحات غير مسعرة يؤكدها التصنيع: ستانلس ٢ مم مبشور، عمق ١٥٠ مم (الصورة توحي بأعمق)، زعنفة ١٥ مم، زوج.'),
         ('Shape read from one photo of unknown maker and Sabry\'s correction. Drawn as objekt\'s own design. The device on the shelf is not ours and not drawn.', 'الشكل من صورة واحدة وتصحيح سبري ومرسوم كتصميم خاص بأوبجيكت. الجهاز على الرف ليس لنا.'),
         ('Open for Sabry: is the pair two of the same hand or a mirrored pair (plate on the left wall for one, on the right wall for the other)? Drawing shows the plate on the left wall.', 'مفتوح: هل الزوج متماثل الاتجاه أم معكوس؟ الرسم يبين اللوح على الحائط الأيسر.'),
         ('Fixing (Sabry, 15-16 Nov): two screw holes dia 5 in the vertical plate, seen from the room, and nothing else: no flange, no other holes. Wall type, plugs and screw finish are not known: Production / installer to decide. A shelf held by two screws on one wall only: Production to confirm it is enough.', 'التثبيت: ثقبان في الزعنفة مخفيان وثقبان في اللوح الرأسي ظاهران من الغرفة. النوع والفيشر يقررهما التصنيع.'),
         ('Finish: exposed brushed stainless, no paint (proposal). Stainless grade, brushing direction, bend radius and allowance, tolerances, sheet size are Production\'s to decide.', 'التشطيب: ستانلس مبشور بدون دهان (مقترح). باقي التفاصيل يقررها التصنيع.'),
         ('No structural claims, stress figures, load figures, costs or prices on this drawing. Not engineered. A stated shelf load is not claimed until Production tests it. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا حمل مذكور ولا تكاليف. الصياغة العربية مسودة.')]
for i, (en, ar) in enumerate(notes):
    yy = 89 + i*12.5
    b += t(12, yy, f'{i+1}.', 2.4, 600) + t(18, yy, en, 2.0) + t(410, yy+4.5, ar, 2.0, 400, 'end', extra=AR)
sh5 = sheet(5, N, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)

for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1):
    open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('outline (mm):', round(PARTS['P1'][5]), 'total', round(TOTAL_CUT), 'bbox', BBW, BBH, 'sloped', round(PEDGE, 1), 'nest', MSG, 'used', round(USED_X), round(USED_Y))
