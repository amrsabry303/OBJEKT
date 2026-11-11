"""OBJ-190 (provisional number): side table, faceted top on two legs. Production drawing set, REV 0.
Run: python3 make_obj190_rev0.py <repo root>
Writes A3 sheets (SVG), DXF flat patterns and the nested sheet to venture/drawings/OBJ-190/. PDF is made by make_pdf.js.
Sizes: overall 550 x 450 x 550 mm are Sabry's. Everything else is TRACED FROM THREE PHOTOS, approximate.
Arabic wording is a draft and needs a technical reader. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-190'; os.makedirs(OUT, exist_ok=True)
IMG = ROOT + '/images/'
PHOTOS = [('front', '/tmp/claude-0/-home-user-OBJEKT/e5a0d9e6-9e92-52c4-9230-15fce9d80fe4/images/16.webp', 'Photo 1, end view', 'صورة ١، منظر من الطرف'),
          ('legs', '/tmp/claude-0/-home-user-OBJEKT/e5a0d9e6-9e92-52c4-9230-15fce9d80fe4/images/17.webp', 'Photo 2, side view', 'صورة ٢، منظر جانبي'),
          ('ctx', '/tmp/claude-0/-home-user-OBJEKT/e5a0d9e6-9e92-52c4-9230-15fce9d80fe4/images/18.webp', 'Photo 3, in a room', 'صورة ٣، في غرفة')]
REV = 0; DATE = '11 Nov 2026'; PN = 'OBJ-190'
W, D, H = 550, 450, 550           # overall, Sabry
TOP_T = 160; LEG_H = H - TOP_T    # top block thickness (from photo), leg height
LEG_X = [(50, 215), (335, 500)]; LEG_Y = (25, 425); TOP_A = 15; LEG_A = 13   # V depth: top (each side), leg (outer face); same angle
SHEET_L, SHEET_W, GAP = 2500, 1250, 10

# ---- geometry (mm) ----
def top_poly():
    """8-sided plan: a rectangle with one shallow V (apex pointing out) in the middle of each of the 4 sides. Origin at centre.
    Corners at (+-(W/2-A), +-(D/2-A)), apexes at (+-W/2, 0) and (0, +-D/2). Approximate."""
    hw, hd, a = W/2, D/2, TOP_A
    x1, y1 = hw-a, hd-a
    return [(-hw, 0), (-x1, -y1), (0, -hd), (x1, -y1), (hw, 0), (x1, y1), (0, hd), (-x1, y1)]
def leg_poly(side=-1):
    """5-sided plan: a rectangle with one V on the outer face (side -1 = left leg, apex to the left; +1 = right leg), at mid depth,
    under the matching V of the top. Origin at centre. Approximate."""
    hw, hd, a = (LEG_X[0][1]-LEG_X[0][0])/2, (LEG_Y[1]-LEG_Y[0])/2, LEG_A
    p = [(-hw, 0), (-hw+a, -hd), (hw, -hd), (hw, hd), (-hw+a, hd)]
    return p if side < 0 else [(-x, y) for x, y in p][::-1]
def edges(p): return [math.dist(p[i], p[(i+1) % len(p)]) for i in range(len(p))]
def perim(p): return sum(edges(p))
def bbox(p): xs = [q[0] for q in p]; ys = [q[1] for q in p]; return min(xs), min(ys), max(xs), max(ys)
TOP, LEG = top_poly(), leg_poly(-1)
def strip(poly, h):
    e = edges(poly); L = sum(e); cum = []; s = 0
    for v in e[:-1]: s += v; cum.append(s)
    return L, h, cum
TS = strip(TOP, TOP_T); LS = strip(LEG, LEG_H)
PARTS = {  # key: (name EN, name AR, qty, kind, data)
 'P1': ('Top block, side strip', 'حافة الكتلة العلوية', 1, 'strip', TS),
 'P2': ('Top block, top and bottom plate', 'لوح علوي وسفلي للكتلة العلوية', 2, 'poly', TOP),
 'P3': ('Leg, side strip', 'حافة الساق', 2, 'strip', LS),
 'P4': ('Leg, top and bottom cap', 'غطاء علوي وسفلي للساق', 4, 'poly', LEG)}
def part_perim(k):
    kind, d = PARTS[k][3], PARTS[k][4]
    return 2*(d[0]+d[1]) if kind == 'strip' else perim(d)
TOTAL_CUT = sum(part_perim(k)*PARTS[k][2] for k in PARTS)

# ---- nesting (hand placed, bbox checked) ----
def size(k):
    kind, d = PARTS[k][3], PARTS[k][4]
    if kind == 'strip': return d[0], d[1]
    b = bbox(d); return b[2]-b[0], b[3]-b[1]
NEST = []  # (key, x, y)
NEST.append(('P1', GAP, GAP)); y = GAP+size('P1')[1]+GAP
NEST += [('P3', GAP, y), ('P3', GAP+size('P3')[0]+GAP, y)]; y += size('P3')[1]+GAP
x = GAP
for _ in range(2): NEST.append(('P2', x, y)); x += size('P2')[0]+GAP
for _ in range(4): NEST.append(('P4', x, y)); x += size('P4')[0]+GAP
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
USED = max(y+size(k)[1] for k, x, y in NEST)

# ---- DXF ----
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); d.layers.add('FOLD', color=1); d.layers.add('SHEET', color=3); return d
def add_part(msp, key, ox, oy):
    kind, d = PARTS[key][3], PARTS[key][4]
    if kind == 'strip':
        L, h, cum = d
        msp.add_lwpolyline([(ox, oy), (ox+L, oy), (ox+L, oy+h), (ox, oy+h)], close=True, dxfattribs={'layer': 'CUT'})
        for c in cum: msp.add_line((ox+c, oy), (ox+c, oy+h), dxfattribs={'layer': 'FOLD'})
    else:
        b = bbox(d); msp.add_lwpolyline([(ox+px-b[0], oy+py-b[1]) for px, py in d], close=True, dxfattribs={'layer': 'CUT'})
FN = {'P1': 'top-side-strip', 'P2': 'top-plate', 'P3': 'leg-side-strip', 'P4': 'leg-cap'}
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
def frame(n, N, title_en, title_ar, scale):
    s = rect(5, 5, 410, 287, .5) + rect(7, 7, 406, 283, .2)
    # title block
    X, Y, Wd = 228, 247, 185
    s += rect(X, Y, Wd, 41, .4, fill='#fff')
    s += line(X, Y+9, X+Wd, Y+9, .25) + line(X, Y+20, X+Wd, Y+20, .25) + line(X, Y+31, X+Wd, Y+31, .25) + line(X+92, Y+9, X+92, Y+41, .25)
    s += bi(X+2, Y+4, f'{PN} (provisional number)  Side table, faceted top on two legs', 'طاولة جانبية بسطح متعدد الأوجه على ساقين', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  {W} x {D} x {H} mm (overall, Sabry)', 'المقاس الكلي', 88, 2.3) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, 'MATERIAL  Stainless steel sheet, thickness by Production', 'الخامة: ستانلس ستيل، السماكة من التصنيع', 88, 2.1) + bi(X+94, Y+25, 'FINISH  brushed (to be confirmed)', 'التشطيب: مصقول بالفرشاة (يؤكد لاحقاً)', 88, 2.1)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, '#b3261e', '#fff')
    s += t(X+Wd/2, Y-8.6, 'DRAFT, not approved, not engineered', 3.6, 700, 'middle', '#b3261e') + t(X+Wd/2, Y-3.8, 'مسودة، غير معتمدة، غير مهندسة', 3.4, 700, 'middle', '#b3261e', extra=' direction="rtl"')
    s += t(10, 14, title_en, 4.2, 700) + t(410, 14, title_ar, 4.2, 700, 'end', extra=' direction="rtl"')
    return s
def sheet(n, N, title_en, title_ar, scale, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, N, title_en, title_ar, scale)}{body}</svg>'
def datauri(path, w=360):
    im = Image.open(path).convert('RGB'); im.thumbnail((w, w)); b = io.BytesIO(); im.save(b, 'JPEG', quality=72)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()

N = 5
# ================= SHEET 1: views =================
S = .2
ox_f, oy = 22, 188          # front elevation origin (left, ground line)
def fx(x): return ox_f + x*S
def fz(z): return oy - z*S
b = ''
b += t(22, 25, 'FRONT ELEVATION (looking along the depth)', 2.8, 600) + t(22+110, 29, 'الواجهة الأمامية (بالنظر على امتداد العمق)', 2.6, 500, 'end', extra=' direction="rtl"')
# legs
for x0, x1 in LEG_X:
    b += rect(fx(x0), fz(LEG_H), (x1-x0)*S, LEG_H*S, .4, INK, FILL)
    xc_ = x0+LEG_A if x0 < W/2 else x1-LEG_A   # corner edge of the V on the front face
    b += line(fx(xc_), fz(LEG_H), fx(xc_), fz(0), .15, HID)
b += rect(fx(0), fz(H), W*S, TOP_T*S, .45, INK, '#e7e3da')
for xv in sorted({round(W/2+p[0]) for p in TOP if p[0] != 0}) + [W//2]:
    b += line(fx(xv), fz(H), fx(xv), fz(LEG_H), .15, HID)
b += dim_h(fx(0), fx(W), fz(0)+9, f'{W}', ext=fz(0)) + t(fx(W/2), fz(0)+14, 'OVERALL WIDTH / العرض الكلي', 2, 400, 'middle', DIM)
b += dim_v(fx(0)-8, fz(H), fz(0), f'{H}', ext=fx(0)) + dim_v(fx(W)+8, fz(H), fz(LEG_H), f'{TOP_T}', ext=fx(W)) + dim_v(fx(W)+8, fz(LEG_H), fz(0), f'{LEG_H}', ext=fx(W))
b += dim_h(fx(LEG_X[0][0]), fx(LEG_X[0][1]), fz(0)-4+30, f'{LEG_X[0][1]-LEG_X[0][0]}') if False else ''
b += dim_h(fx(LEG_X[0][1]), fx(LEG_X[1][0]), fz(LEG_H)+11, f'{LEG_X[1][0]-LEG_X[0][1]}', ext=fz(LEG_H)) + dim_h(fx(LEG_X[0][0]), fx(LEG_X[0][1]), fz(LEG_H)+11, f'{LEG_X[0][1]-LEG_X[0][0]}', ext=fz(LEG_H)) + dim_h(fx(LEG_X[1][0]), fx(LEG_X[1][1]), fz(LEG_H)+11, f'{LEG_X[1][1]-LEG_X[1][0]}', ext=fz(LEG_H))
b += balloon(fx(W/2), fz(H)+5, 1) + balloon(fx(LEG_X[0][0])-4, fz(150), 2)
# side elevation
ox_s = 165
def sx(y): return ox_s + y*S
b += t(ox_s-2, 25, 'SIDE ELEVATION (looking along the width)', 2.8, 600) + t(ox_s+92, 29, 'الواجهة الجانبية (بالنظر على امتداد العرض)', 2.6, 500, 'end', extra=' direction="rtl"')
b += rect(sx(LEG_Y[0]), fz(LEG_H), (LEG_Y[1]-LEG_Y[0])*S, LEG_H*S, .4, INK, FILL)
b += line(sx(D/2), fz(LEG_H), sx(D/2), fz(0), .15, HID)   # V on the outer face, mid depth
b += rect(sx(0), fz(H), D*S, TOP_T*S, .45, INK, '#e7e3da')
for yv in sorted({round(D/2+p[1]) for p in TOP if p[1] != 0}) + [D//2]:
    b += line(sx(yv), fz(H), sx(yv), fz(LEG_H), .15, HID)
b += dim_h(sx(0), sx(D), fz(0)+9, f'{D}', ext=fz(0)) + t(sx(D/2), fz(0)+14, 'OVERALL DEPTH / العمق الكلي', 2, 400, 'middle', DIM)
b += dim_h(sx(LEG_Y[0]), sx(LEG_Y[1]), fz(LEG_H)+11, f'{LEG_Y[1]-LEG_Y[0]}', ext=fz(LEG_H))
b += t(sx(D/2), fz(LEG_H/2)+1, 'second leg behind', 2, 400, 'middle', HID) + t(sx(D/2), fz(LEG_H/2)+4, 'الساق الثانية خلفها', 2, 400, 'middle', HID, extra=' direction="rtl"')
# plan
ox_p, oy_p = 290, 160
def px(x): return ox_p + x*S
def py(y): return oy_p - y*S
b += t(ox_p-2, 25, 'PLAN', 2.8, 600) + t(ox_p+110, 29, 'المسقط الأفقي', 2.6, 500, 'end', extra=' direction="rtl"')
for sd, (x0, x1) in zip((-1, 1), LEG_X):
    b += poly([(px((x0+x1)/2+q[0]), py(D/2+q[1])) for q in leg_poly(sd)], .3, HID, 'none', '1.2 .8')
b += poly([(px(W/2+p[0]), py(D/2+p[1])) for p in TOP], .45, INK, 'rgba(231,227,218,.55)')
b += dim_h(px(0), px(W), py(0)+7, f'{W}', ext=py(0)) + dim_v(px(0)-6, py(D), py(0), f'{D}', ext=px(0))
b += t(px(W/2), py(D/2)+1, 'legs shown dashed', 2, 400, 'middle', HID) + t(px(W/2), py(D/2)+4, 'الساقان بخط متقطع', 2, 400, 'middle', HID, extra=' direction="rtl"')
# photos and notes
b += t(22, 207, 'REFERENCE PHOTOS (not ours; the shape is traced from these, approximate)', 2.5, 600) + t(210, 210.5, 'صور مرجعية (ليست لنا، الشكل مستخرج منها تقريباً)', 2.4, 500, 'end', extra=' direction="rtl"')
for i, (key, path, en, ar) in enumerate(PHOTOS):
    x = 22 + i*62
    b += f'<image href="{datauri(path)}" x="{x}" y="212" width="58" height="58" preserveAspectRatio="xMidYMid slice"/>' + rect(x, 212, 58, 58, .2, HID) + t(x, 273, en, 2, 400) + t(x+58, 275.5, ar, 2, 400, 'end', extra=' direction="rtl"')
# colourways
cx = 264
b += t(cx, 182, 'COLOURWAYS (proposed)', 2.5, 600) + t(410, 182, 'ألوان مقترحة', 2.4, 500, 'end')
rows = [('Brushed stainless  #A7ACB1', 'ستانلس مصقول بالفرشاة', '#A7ACB1', 'Brushed, proposed default'), ('Mirror stainless  #DCE0E4', 'ستانلس مرآة', '#DCE0E4', 'Mirror finish: few skilled polishers'), ('Painted objekt colour, matte', 'لون أوبجيكت مطلي، مطفي', '#222222', 'Powder coat or Duco: to be confirmed')]
for i, (en, ar, hexv, note) in enumerate(rows):
    yy = 188 + i*5.6
    b += rect(cx, yy-3, 6, 4, .2, INK, hexv) + t(cx+8, yy, en, 2.2) + t(410, yy, ar, 2.2, 400, 'end') + t(cx+8, yy+2.6, note, 1.8, 400, fill=HID)
b += t(10, 284, 'The reference piece is a warm brushed bronze-grey metal. That tone is not on the objekt finish list: Sabry to decide the finish.', 2.1, 400, fill=HID)
b += t(10, 287.5, 'Sizes other than the overall 550 x 450 x 550 mm are estimated from the photos.  ما عدا المقاسات الكلية فالمقاسات مقدّرة من الصور.', 2.1, 400, fill=HID)
sh1 = sheet(1, N, 'VIEWS', 'المناظير', '1:5', b)

# ================= SHEET 2: flat patterns =================
S2 = .2
b = t(10, 22, 'Flat patterns at 1:5. Fold lines dashed. Developed lengths are along the outside, bend allowance is Production\'s.', 2.3, 400, fill=HID) + t(410, 22, 'الأنماط المسطحة بمقياس ١:٥. خطوط الطي متقطعة. سماحية الثني من التصنيع.', 2.3, 400, 'end', HID)
def draw_strip(x, y, data, label_en, label_ar, balloon_n):
    L, h, cum = data
    s = rect(x, y, L*S2, h*S2, .4, INK, FILL)
    for c in cum: s += line(x+c*S2, y, x+c*S2, y+h*S2, .2, '#b3261e', '2 1.2')
    s += dim_h(x, x+L*S2, y+h*S2+6, f'{L:.0f}', ext=y+h*S2) + dim_v(x-5, y, y+h*S2, f'{h:.0f}', ext=x)
    s += t(x, y-2, label_en, 2.4, 600) + t(x+L*S2, y-2, label_ar, 2.4, 600, 'end', extra=' direction="rtl"') + balloon(x-9, y+h*S2/2, balloon_n)
    return s
b += draw_strip(30, 36, TS, '1  TOP BLOCK SIDE STRIP, 1 off, 8 folds, one seam', 'حافة الكتلة العلوية، عدد ١، ٨ ثنيات', 1)
b += draw_strip(30, 100, LS, '3  LEG SIDE STRIP, 2 off, 5 folds, one seam', 'حافة الساق، عدد ٢، ٥ ثنيات', 3)
bl = bbox(LEG); b0 = bbox(TOP)
# leg cap
xc, yc = 262, 100
b += poly([(xc+(p[0]-bl[0])*S2, yc+(p[1]-bl[1])*S2) for p in LEG], .4, INK, FILL)
b += dim_h(xc, xc+(bl[2]-bl[0])*S2, yc+(bl[3]-bl[1])*S2+6, f'{bl[2]-bl[0]:.0f}', ext=yc+(bl[3]-bl[1])*S2) + dim_v(xc-4, yc, yc+(bl[3]-bl[1])*S2, f'{bl[3]-bl[1]:.0f}', ext=xc)
b += balloon(xc+(bl[2]-bl[0])*S2/2, yc-5, 4) + t(xc-2, yc+(bl[3]-bl[1])*S2+13, '4  LEG CAP, 4 off', 2.3, 600) + t(xc-2, yc+(bl[3]-bl[1])*S2+16.5, 'غطاء الساق، عدد ٤', 2.3, 600)
# top plate
xp, yp = 303, 100
b += poly([(xp+(p[0]-b0[0])*S2, yp+(p[1]-b0[1])*S2) for p in TOP], .4, INK, FILL)
b += dim_h(xp, xp+W*S2, yp+D*S2+6, f'{W}', ext=yp+D*S2) + dim_v(xp-4, yp, yp+D*S2, f'{D}', ext=xp)
b += balloon(xp+W*S2/2, yp-5, 2) + t(xp, yp+D*S2+13, '2  TOP BLOCK PLATE, 2 off', 2.3, 600) + t(xp, yp+D*S2+16.5, 'لوح الكتلة العلوية، عدد ٢', 2.3, 600)
# DATA
dx, dy = 24, 202
b += t(dx, dy, 'DATA  face lengths along each strip, mm (in fold order)', 2.4, 600) + t(224, dy, 'بيانات: أطوال الأوجه بالترتيب', 2.4, 600, 'end')
def row(y, lab, vals):
    return t(dx, y, lab, 2.1, 600) + t(dx+14, y, ', '.join(f'{v:.0f}' for v in vals), 2.1, 400)
b += row(dy+5, 'Part 1', edges(TOP)) + row(dy+9.5, 'Part 3', edges(LEG))
for i, line_ in enumerate(['Parts 2 and 4: the outline is the plan shape; its 8 and 5 sides match the strip faces in order. Left and right legs are mirror images.',
                           'Strip height: part 1 = 160, part 3 = 390 (outside). Plate and cap thickness, and whether they sit',
                           'inside the strip or on top: Production. Weld seam proposed on a corner fold, ground flush.',
                           'Plan shapes are traced from three photos and are approximate: top block with one V (depth 15) on each of its 4 sides;',
                           'each leg has one V (depth 13, same angle) on its outer face, under the matching V of the top.']):
    b += t(dx, dy+15+i*3.8, line_, 2.0)
b += t(224, dy+15, 'الأشكال مستخرجة من ثلاث صور وهي تقريبية.', 2.0, 400, 'end') + t(224, dy+19, 'ارتفاع الشريط ١٦٠ للقطعة ١ و٣٩٠ للقطعة ٣.', 2.0, 400, 'end')
sh2 = sheet(2, N, 'PART SHEET', 'ورقة القطع', '1:5', b)

# ================= SHEET 3: assembly =================
S3 = .2
oy3 = 215
def ex(x): return 40 + x*S3
def ez(z, lift=0): return oy3 - (z+lift)*S3
b = t(10, 22, 'EXPLODED VIEW (proposed assembly, Production decides jigs, welds and fixings)', 2.5, 600) + t(410, 22, 'منظر مفكك (تجميع مقترح، والتصنيع يقرر القوالب واللحام)', 2.5, 600, 'end', extra=' direction="rtl"')
for x0, x1 in LEG_X:
    b += rect(ex(x0), ez(LEG_H, 0), (x1-x0)*S3, LEG_H*S3, .4, INK, FILL)
    b += rect(ex(x0), ez(8, 0)+0, (x1-x0)*S3, 1.6, .3, INK, '#d5d0c4') if False else ''
    b += line(ex((x0+x1)/2), ez(LEG_H), ex((x0+x1)/2), ez(LEG_H, 60), .2, HID, '1 1')
    b += rect(ex(x0), ez(LEG_H, 60)-1.6, (x1-x0)*S3, 1.6, .3, INK, '#d5d0c4') + t(ex(x1)+2, ez(LEG_H, 60), 'cap', 2, 400, fill=HID)
    b += rect(ex(x0), oy3+4, (x1-x0)*S3, 1.6, .3, INK, '#d5d0c4') + t(ex(x1)+2, oy3+5.4, 'cap', 2, 400, fill=HID)
b += rect(ex(0), ez(H, 110), W*S3, TOP_T*S3, .45, INK, '#e7e3da') + line(ex(W/2), ez(LEG_H, 60)-4, ex(W/2), ez(H, 110)+TOP_T*S3, .2, HID, '1 1')
b += rect(ex(0), ez(H, 110)-1.6, W*S3, 1.6, .3, INK, '#d5d0c4') + rect(ex(0), ez(H, 110)+TOP_T*S3, W*S3, 1.6, .3, INK, '#d5d0c4')
b += balloon(ex(W/2), ez(H, 110)-8, 1) + balloon(ex(0)-6, ez(H, 110)+TOP_T*S3/2, 2) + balloon(ex(LEG_X[0][0])-5, ez(250), 3) + balloon(ex(LEG_X[0][0])-5, ez(LEG_H, 60), 4)
b += t(22, 262, 'Floor protectors on the underside of each leg: bought-in, type and number to be decided by Production.', 2.1, 400, fill=HID)
b += t(224, 266, 'واقيات الأرضية: قطع جاهزة، النوع والعدد من التصنيع.', 2.1, 400, 'end', HID)
sx0 = 235
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end', extra=' direction="rtl"')
steps = [('Cut and fold the two leg strips (3) and the top strip (1).', 'قص وثني شريطي الساقين (٣) وشريط الكتلة العلوية (١).'),
         ('Close each leg: weld the seam, weld one cap (4) in each end.', 'إغلاق كل ساق: لحام الوصلة ولحام غطاء (٤) في كل طرف.'),
         ('Close the top block: weld the seam, weld the two plates (2).', 'إغلاق الكتلة العلوية: لحام الوصلة ولحام اللوحين (٢).'),
         ('Weld the two legs to the underside of the top block (sheet 1), each leg V under the matching V of the top.', 'لحام الساقين أسفل الكتلة العلوية (الورقة ١)، وزاوية كل ساق تحت الزاوية المقابلة في الأعلى.'),
         ('Grind welds flush, brush or polish, fit floor protectors.', 'صنفرة اللحام، التشطيب، تركيب واقيات الأرضية.')]
for i, (en, ar) in enumerate(steps):
    yy = 48 + i*17
    b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 2.4) + t(410, yy+5, ar, 2.4, 400, 'end', extra=' direction="rtl"')
sh3 = sheet(3, N, 'ASSEMBLY', 'التجميع', '1:5', b)

# ================= SHEET 4: cutting layout =================
S4 = .1
b = t(10, 22, f'CUTTING LAYOUT on an assumed sheet {SHEET_L} x {SHEET_W} (thickness by Production). Assumed, to be confirmed by Production.', 2.4, 600) + t(410, 22, 'مخطط القص على لوح مفترض، السماكة من التصنيع', 2.4, 600, 'end', extra=' direction="rtl"')
ox4, oy4 = 30, 40
b += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6') + t(ox4, oy4-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for k, x, y in NEST:
    kind, d = PARTS[k][3], PARTS[k][4]
    if kind == 'strip':
        L, h, cum = d; X, Y = ox4+x*S4, oy4+y*S4
        b += rect(X, Y, L*S4, h*S4, .3, INK, FILL)
        for c in cum: b += line(X+c*S4, Y, X+c*S4, Y+h*S4, .12, '#b3261e', '1 .8')
    else:
        bb = bbox(d); b += poly([(ox4+(x+p[0]-bb[0])*S4, oy4+(y+p[1]-bb[1])*S4) for p in d], .3, INK, FILL)
    sw, sh_ = size(k)
    b += t(ox4+(x+sw/2)*S4, oy4+(y+sh_/2)*S4+1, {'P1': '1', 'P2': '2', 'P3': '3', 'P4': '4'}[k], 3.4, 600, 'middle', '#555')
b += dim_h(ox4, ox4+SHEET_L*S4, oy4+SHEET_W*S4+7, f'{SHEET_L}', ext=oy4+SHEET_W*S4) + dim_v(ox4-6, oy4, oy4+SHEET_W*S4, f'{SHEET_W}', ext=ox4)
b += t(30, 195, f'Parts nested with {GAP} mm spacing. Material used: about {USED:.0f} mm of the {SHEET_W} mm width, full {SHEET_L} mm length. No offcut is claimed.', 2.3)
b += t(30, 200, f'Total cutting length of all parts: {TOTAL_CUT/1000:.2f} m ({TOTAL_CUT:.0f} mm), outlines only, not counting folds.', 2.5, 600)
b += t(410, 195, 'الأجزاء مرتبة بمسافة ١٠ مم. لا يُدّعى أي هالك.', 2.3, 400, 'end', extra=' direction="rtl"') + t(410, 200, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.5, 600, 'end', extra=' direction="rtl"')
b += t(30, 210, 'Fold lines (red, dashed) are marked on the strips for reference; they are not cut.  خطوط الطي لا تُقص.', 2.2, 400, fill=HID)
sh4 = sheet(4, N, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)

# ================= SHEET 5: BOM and notes =================
b = ''
cols = [10, 24, 130, 150, 245]
b += t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + t(410, 28, 'قائمة المواد', 2.8, 600, 'end', extra=' direction="rtl"')
b += rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Top block, side strip', 'حافة الكتلة العلوية', '1', 'Stainless steel sheet'), ('2', 'Top block plate (top and bottom)', 'لوح الكتلة العلوية', '2', 'Stainless steel sheet'), ('3', 'Leg, side strip', 'حافة الساق', '2', 'Stainless steel sheet'), ('4', 'Leg cap (top and bottom)', 'غطاء الساق', '4', 'Stainless steel sheet'), ('5', 'Floor protector', 'واقي أرضية', 'by Production', 'Bought-in, to be decided')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*7
    b += line(10, yy+2.2, 410, yy+2.2, .15, HID) + t(12, yy, n_, 2.4) + t(24, yy, en, 2.4) + t(120, yy, ar, 2.4, 400, 'end', extra=' direction="rtl"') + t(150, yy, q, 2.4) + t(215, yy, m_, 2.4)
b += t(10, 90, 'NOTES', 2.8, 600) + t(410, 90, 'ملاحظات', 2.8, 600, 'end', extra=' direction="rtl"')
notes = [('Overall size 550 x 450 x 550 mm is Sabry\'s. All other sizes are estimated from three photos of a reference piece (not ours).', 'المقاس الكلي من سبري، وبقية المقاسات مقدّرة من ثلاث صور.'),
         ('The construction (hollow folded and welded boxes: one top block and two legs) is inferred from the photos. Production to confirm.', 'طريقة الصنع (صناديق مجوفة مثنية وملحومة) مستنتجة من الصور. يؤكدها التصنيع.'),
         ('Plan shapes (top: 8 sides, four Vs, one per side; legs: 5 sides, one V each, matching the V of the top above it) are traced from the photos and are approximate. Real sizes or the original CAD are still needed.', 'الأشكال الأفقية تقريبية. نحتاج المقاسات الحقيقية أو ملف التصميم الأصلي.'),
         ('Material, thickness, bend allowance, tolerances, sheet size, joints, welding, plate fit and finish are Production\'s to decide.', 'الخامة والسماكة والسماحيات واللحام والتشطيب يقررها التصنيع.'),
         ('The reference is a warm brushed bronze-grey metal. Finish to be decided by Sabry: brushed or mirror stainless, or a painted objekt colour.', 'المرجع معدن برونزي رمادي مصقول. التشطيب يقرره سبري.'),
         ('Height 550 is the overall height: top block 160 + legs 390. Floor protectors, if fitted, are inside this figure; Production to confirm.', 'الارتفاع الكلي ٥٥٠: الكتلة العلوية ١٦٠ والساقان ٣٩٠.'),
         ('No structural claims, stress figures, costs or prices on this drawing. Not engineered. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا تكاليف ولا أسعار. الصياغة العربية مسودة.'),
         (f'{PN} is a provisional product number, not yet confirmed by Sabry.', 'رقم المنتج مؤقت.')]
for i, (en, ar) in enumerate(notes):
    yy = 99 + i*13
    b += t(12, yy, f'{i+1}.', 2.4, 600) + t(18, yy, en, 2.3) + t(410, yy+5, ar, 2.3, 400, 'end', extra=' direction="rtl"')
sh5 = sheet(5, N, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)

for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1):
    open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('perimeters (mm):', {k: round(part_perim(k)) for k in PARTS}, 'total cut', round(TOTAL_CUT), 'nest ok:', MSG, 'used width', USED)
print('top edges', [round(e) for e in edges(TOP)], 'strip L', round(TS[0]), '| leg strip L', round(LS[0]))
