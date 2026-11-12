"""OBJ-168: tall square column planter with round holes. Production drawing set, REV 0 (DRAFT).
Run: python3 make_obj168_rev0.py <repo root>   Then make_pdf.js for the PDF.
Sizes are a PROPOSAL (Sabry 12 Nov: "approve the proposal, but height 80 cm"): 160 x 160 x 800 mm keeps the 1:5 look of the proposal. Sheet 2 mm brushed stainless,
liner depth, hole sizes and positions are proposals, not costed, Production to confirm. Hole layout is our own, not a copy of the reference.
Reference photo: third-party maker, unknown; the shape (square tube, flat top, round holes on several faces) is read from it. Arabic is a draft. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-168'; os.makedirs(OUT, exist_ok=True)
PHOTO = ROOT + '/images/OBJ-168.jpg'
REV = 0; DATE = '12 Nov 2026'; PN = 'OBJ-168'
B, H = 160, 800                  # outside square, overall height (Sabry: 80 cm)
T = 2                            # sheet thickness, proposal
LINER_D = 220                    # liner depth hanging from the top, proposal
ZMAX = H - LINER_D - 60          # no hole above this height (soil zone + 60 mm margin) = 520
FLAT_W = 4*B                     # developed width, nominal outside dims (bend allowance by Production)
BASE = B - 2*T                   # base plate 156 x 156
# holes: (id, face A..D, diameter, centre height above base, centre x on the face = centred)
HOLES = [(1, 'A', 95, 440), (2, 'A', 65, 290), (3, 'B', 105, 360), (4, 'C', 80, 230), (5, 'D', 70, 100)]
FACES = {'A': 'Front / الأمامي', 'B': 'Right / الأيمن', 'C': 'Back / الخلفي', 'D': 'Left / الأيسر'}
FX = {'A': 80, 'B': 240, 'C': 400, 'D': 560}   # face centre on the flat pattern
for h in HOLES:
    assert h[3] + h[2]/2 <= ZMAX and h[3] - h[2]/2 >= 40 and h[2]/2 + 25 <= B/2, h   # inside zone, 40 from base, 25 mm to folds
SHEET_L, SHEET_W, GAP = 2500, 1250, 10
HOLE_CUT = sum(math.pi*h[2] for h in HOLES)
OUTLINE = {'P1': 2*(FLAT_W + H), 'P2': 4*BASE}
TOTAL_CUT = OUTLINE['P1'] + HOLE_CUT + OUTLINE['P2']
NEST = [('P1', GAP, GAP), ('P2', GAP + FLAT_W + GAP, GAP)]
SIZE = {'P1': (FLAT_W, H), 'P2': (BASE, BASE)}
for k, x, y in NEST: assert x + SIZE[k][0] <= SHEET_L and y + SIZE[k][1] <= SHEET_W
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); d.layers.add('FOLD', color=5); d.layers.add('SHEET', color=3); return d
def add_part(msp, k, ox, oy):
    w, h = SIZE[k]
    msp.add_lwpolyline([(ox, oy), (ox+w, oy), (ox+w, oy+h), (ox, oy+h)], close=True, dxfattribs={'layer': 'CUT'})
    if k == 'P1':
        for _, f, d, z in HOLES: msp.add_circle((ox + FX[f], oy + z), d/2, dxfattribs={'layer': 'CUT'})
        for xf in (B, 2*B, 3*B): msp.add_line((ox+xf, oy), (ox+xf, oy+h), dxfattribs={'layer': 'FOLD'})
FN = {'P1': 'wrapped-body', 'P2': 'base'}
for k in SIZE:
    doc = new_doc(); add_part(doc.modelspace(), k, 0, 0); doc.saveas(f'{OUT}/{PN}_rev{REV}_{k}_{FN[k]}.dxf')
doc = new_doc(); m = doc.modelspace()
m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
for k, x, y in NEST: add_part(m, k, x, y)
doc.saveas(f'{OUT}/{PN}_rev{REV}_nest_{SHEET_L}x{SHEET_W}.dxf')

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
def frame(n, N, title_en, title_ar, scale):
    s = rect(5, 5, 410, 287, .5) + rect(7, 7, 406, 283, .2)
    X, Y, Wd = 228, 247, 185
    s += rect(X, Y, Wd, 41, .4, fill='#fff')
    s += line(X, Y+9, X+Wd, Y+9, .25) + line(X, Y+20, X+Wd, Y+20, .25) + line(X, Y+31, X+Wd, Y+31, .25) + line(X+92, Y+9, X+92, Y+41, .25)
    s += bi(X+2, Y+4, f'{PN}   Planter, tall square column with round holes', 'جاردينيرا عمود مربع طويل بفتحات دائرية', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  {B} x {B} x {H} mm (proposal)', 'المقاس الكلي (مقترح)', 88, 2.1) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, 'MATERIAL  Stainless sheet 2 mm (proposal), folded, welded', 'الخامة: ستانلس ٢ مم (مقترح)، ثني ولحام', 88, 2.0) + bi(X+94, Y+25, 'FINISH  Brushed stainless (no paint)', 'التشطيب: ستانلس مبروش', 88, 2.1)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, '#b3261e', '#fff')
    s += t(X+Wd/2, Y-8.6, STAMP, 2.9, 700, 'middle', '#b3261e') + t(X+Wd/2, Y-3.8, STAMP_AR, 2.9, 700, 'middle', '#b3261e')
    s += t(10, 14, title_en, 4.2, 700) + t(410, 14, title_ar, 4.2, 700, 'end', extra=' direction="rtl"')
    return s
def sheet(n, N, title_en, title_ar, scale, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, N, title_en, title_ar, scale)}{body}</svg>'
AR = ' direction="rtl"'
N = 5
def circ(cx, cy, r): return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="#fff" stroke="{INK}" stroke-width=".35"/>'
# ================= SHEET 1: views =================
S = .21                      # about 1:4.8
oz = 228                     # base line y
b = ''
for i, f in enumerate('ABCD'):
    x0 = 24 + i*52
    b += t(x0, 28, f'{f}  {FACES[f].split(" / ")[0]}', 2.6, 600) + t(x0+B*S, 31.5, FACES[f].split(' / ')[1], 2.4, 500, 'end', extra=AR)
    b += rect(x0, oz-H*S, B*S, H*S, .45, INK, '#d9dbdc')
    b += line(x0, oz-(H-LINER_D)*S, x0+B*S, oz-(H-LINER_D)*S, .15, HID, '1.2 .8')
    for hid, ff, d, z in HOLES:
        if ff == f:
            b += circ(x0+B*S/2, oz-z*S, d/2*S) + balloon(x0+B*S/2, oz-z*S, hid)
b += dim_v(14, oz-H*S, oz, f'{H}', ext=24) + dim_h(24, 24+B*S, oz+7, f'{B}', ext=oz)
b += t(24, oz-(H-LINER_D)*S-1.5, f'no holes above {ZMAX}', 1.9, 400, fill=HID)
b += t(24, oz+13, 'Holes centred on each face; sizes and heights in the table on sheet 2.  الفتحات في منتصف كل وجه، والجدول في الورقة ٢.', 2.0, 400, fill=HID)
# plan
px0, py0 = 262, 46
b += t(px0, 38, 'PLAN', 2.8, 600) + t(px0+70, 41, 'المسقط الأفقي', 2.6, 500, 'end', extra=AR)
b += rect(px0, py0, B*S*1.5, B*S*1.5, .45, INK, '#d9dbdc') + rect(px0+T*S*1.5, py0+T*S*1.5, BASE*S*1.5, BASE*S*1.5, .3, INK, '#fff')
b += rect(px0+14, py0+14, 12*1.5*S*B/60, 12*1.5*S*B/60, .2, HID, 'none', '1 .7') if False else ''
b += dim_h(px0, px0+B*S*1.5, py0+B*S*1.5+6, f'{B}', ext=py0+B*S*1.5)
b += t(px0, py0+B*S*1.5+11, 'Open top. Faces A (front) to D (left) as seen on the left.', 2.0, 400, fill=HID) + t(px0+70, py0+B*S*1.5+14.5, 'الواجهة الأمامية A إلى اليسرى D.', 2.0, 400, 'end', HID, extra=AR)
# reference photo
b += t(px0, 132, 'REFERENCE PHOTO (not ours; third-party maker, unknown)', 2.3, 600) + t(410, 136, 'صورة مرجعية (ليست لنا، الصانع مجهول)', 2.3, 500, 'end', extra=AR)
b += f'<image href="{datauri(PHOTO, 300)}" x="{px0}" y="140" width="55" height="73.3" preserveAspectRatio="xMidYMid slice"/>' + rect(px0, 140, 55, 73.3, .2, HID)
b += t(px0+60, 146, 'Square tube, flat top, round holes on', 2.0, 400, fill=HID) + t(px0+60, 149, 'several faces. Our hole layout, size and', 2.0, 400, fill=HID) + t(px0+60, 152, 'proportion are our own, not a copy.', 2.0, 400, fill=HID)
b += t(px0+60, 160, 'Reference finish: raw brushed aluminium or', 2.0, 400, fill=HID) + t(px0+60, 163, 'stainless. Ours: brushed stainless (proposal).', 2.0, 400, fill=HID)
b += t(22, 262, 'FINISH: exposed metal, brushed (objekt colour and finish guide). No paint, no colourways. Mirror is not proposed.  التشطيب: معدن مكشوف مبروش، بدون دهان.', 2.0, 400, fill=HID)
b += t(22, 266, f'Overall {B} x {B} x {H} mm (height 800 from Sabry; width and all else is a PROPOSAL, not costed, Production to confirm).  المقاسات مقترحة ويؤكدها التصنيع.', 2.0, 400, fill=HID)
sh1 = sheet(1, N, 'VIEWS', 'المناظير', '1:5', b)
# ================= SHEET 2: flat patterns =================
S2 = .22
fx0, fy0 = 24, 42
b = t(10, 22, 'Flat patterns at 1:4.5, outside dimensions, bend allowance not applied (Production).', 2.3, 400, fill=HID) + t(410, 22, 'الأنماط المسطحة، الأبعاد الخارجية، وسماحية الثني من التصنيع.', 2.3, 400, 'end', HID)
b += rect(fx0, fy0, FLAT_W*S2, H*S2, .4, INK, FILL)
for xf in (B, 2*B, 3*B): b += line(fx0+xf*S2, fy0-2, fx0+xf*S2, fy0+H*S2+2, .25, '#b3261e', '3 1 .6 1')
for i, f in enumerate('ABCD'): b += t(fx0+(i*B+B/2)*S2, fy0+H*S2+9, f, 3, 600, 'middle')
for hid, f, d, z in HOLES:
    cx, cy = fx0+FX[f]*S2, fy0+H*S2-z*S2
    b += circ(cx, cy, d/2*S2) + balloon(cx+d/2*S2+4.5, cy, hid)
b += dim_h(fx0, fx0+FLAT_W*S2, fy0+H*S2+14, f'{FLAT_W}  (4 x {B})', ext=fy0+H*S2) + dim_v(fx0-6, fy0, fy0+H*S2, f'{H}', ext=fx0)
b += t(fx0, fy0-5, '1  WRAPPED BODY, 1 off (folds at 160, 320, 480; one welded seam at the edge)', 2.4, 600) + t(fx0+FLAT_W*S2, fy0-9, 'الجسم الملفوف، عدد ١', 2.4, 600, 'end', extra=AR)
b += t(fx0+FLAT_W*S2/2, fy0-1.5, 'dash-dot red = fold', 1.8, 400, 'middle', '#b3261e')
bx, by = 255, 60
b += rect(bx, by, BASE*S2, BASE*S2, .4, INK, FILL) + dim_h(bx, bx+BASE*S2, by+BASE*S2+6, f'{BASE}', ext=by+BASE*S2) + dim_v(bx-5, by, by+BASE*S2, f'{BASE}', ext=bx)
b += t(bx, by-4, '2  BASE PLATE, 1 off', 2.4, 600) + t(bx+BASE*S2+20, by-4, 'لوح القاع، عدد ١', 2.4, 600, 'end', extra=AR)
dx, dy = 255, 110
b += t(dx, dy, 'HOLE TABLE  mm (all through, laser cut before folding)', 2.4, 600) + t(410, dy, 'جدول الفتحات', 2.4, 600, 'end', extra=AR)
rows = [('No', 'Face', 'Diameter', 'Centre height', 'Centre across face')] + [(str(h[0]), h[1], f'{h[2]}', f'{h[3]}', f'{B//2} (centred)') for h in HOLES]
for i, r_ in enumerate(rows):
    yy = dy+5+i*4.2
    b += line(dx, yy+1.3, 410, yy+1.3, .12, HID)
    for xx, v in zip((dx, dx+12, dx+26, dx+48, dx+78), r_): b += t(xx, yy, v, 2.1, 600 if i == 0 else 400)
notes = [f'Holes: Ø65 to Ø105, five in all, on faces A (2), B, C and D. None above {ZMAX} mm: that zone is the liner and soil.',
         'Hole edges: deburred and brushed. At least 25 mm from every fold; at least 40 mm from the base.',
         'Base plate 156 x 156 = 160 - 2 x 2. How it joins the body (inside, welded) is Production\'s.',
         'Open top. The liner hangs on the rim; rim support and liner size are not drawn (Production).']
for i, ln in enumerate(notes): b += t(dx, dy+34+i*3.8, ln, 1.9)
b += t(410, dy+52, 'الفتحات خمس، لا شيء منها فوق ٥٢٠ مم. حواف الفتحات تنعيم وتبريش.', 1.9, 400, 'end', extra=AR)
sh2 = sheet(2, N, 'PART SHEET', 'ورقة القطع', '1:4.5', b)
# ================= SHEET 3: assembly =================
SC = .17; KK = .5; AA = math.radians(35)
def P(x, y, z): return 60 + (x + KK*y*math.cos(AA))*SC, 235 - (z + KK*y*math.sin(AA))*SC
def pl(pts3, fill, sw=.35): return poly([P(*q) for q in pts3], sw, INK, fill)
b = t(10, 22, 'EXPLODED VIEW (proposed assembly; Production decides jigs, welds and fixings)', 2.5, 600) + t(410, 22, 'منظر مفكك (تجميع مقترح، والتصنيع يقرر القوالب واللحام)', 2.5, 600, 'end', extra=AR)
def holes3(face, fill='#fff'):
    s = ''
    for hid, f, d, z in HOLES:
        if f != face: continue
        pts = []
        for i in range(36):
            a = 2*math.pi*i/36; u, v = d/2*math.cos(a), d/2*math.sin(a)
            pts.append(P(B/2+u, 0, z+v) if face == 'A' else P(B, B/2+u, z+v) if face == 'B' else P(0, 0, 0))
        s += poly(pts, .3, INK, fill)
    return s
# body: front face A (y=0), right face B (x=B), top rim
b += pl([(0, 0, 0), (B, 0, 0), (B, 0, H), (0, 0, H)], '#d9dbdc') + holes3('A')
b += pl([(B, 0, 0), (B, B, 0), (B, B, H), (B, 0, H)], '#bfc2c4') + holes3('B', '#8d9093')
b += pl([(0, 0, H), (B, 0, H), (B, B, H), (0, B, H)], '#eceeef')
b += pl([(T, T, H), (B-T, T, H), (B-T, B-T, H), (T, B-T, H)], '#9a9da0', .25)
# base plate lowered, liner raised
b += pl([(T, T, -90), (B-T, T, -90), (B-T, B-T, -90), (T, B-T, -90)], '#e2e4e5')
for (x_, y_) in [(T, T), (B-T, T), (B-T, B-T)]:
    (ax, ay), (bx2, by2) = P(x_, y_, -90), P(x_, y_, 0); b += line(ax, ay, bx2, by2, .2, HID, '1 1')
LZ = H + 160
b += pl([(8, 8, LZ-LINER_D), (B-8, 8, LZ-LINER_D), (B-8, 8, LZ), (8, 8, LZ)], '#c9c5bb') + pl([(B-8, 8, LZ-LINER_D), (B-8, B-8, LZ-LINER_D), (B-8, B-8, LZ), (B-8, 8, LZ)], '#b2aea3')
b += pl([(8, 8, LZ), (B-8, 8, LZ), (B-8, B-8, LZ), (8, B-8, LZ)], '#e6e2d8')
for (x_, y_) in [(8, 8), (B-8, 8), (B-8, B-8)]:
    (ax, ay), (bx2, by2) = P(x_, y_, LZ-LINER_D), P(x_, y_, H-LINER_D+40); b += line(ax, ay, bx2, by2, .2, HID, '1 1')
ax, ay = P(B, 0, H/2); b += balloon(ax+10, ay, 1)
ax, ay = P(B/2, B/2, -90); b += balloon(ax, ay+8, 2)
ax, ay = P(B, B, LZ-LINER_D/2); b += balloon(ax+10, ay, 3)
b += t(22, 262, 'Liner (3): loose, closed bottom, no drain hole, hangs on the rim; size and material by Production, not drawn in detail. Overall height stays 800.', 2.0, 400, fill=HID)
b += t(224, 270, 'البطانة: سائبة، قاعها مغلق وبدون فتحة صرف، وتتعلق على الحافة. المقاس والخامة من التصنيع.', 2.0, 400, 'end', HID, extra=AR)
sx0 = 245
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end', extra=AR)
steps = [('Laser cut part 1 (with the five holes) and part 2 from the DXF files; deburr all edges.', 'قص القطعة ١ بالفتحات الخمس والقطعة ٢ بالليزر وتنعيم الحواف.'),
         ('Fold part 1 at the three fold lines into a square tube.', 'ثني القطعة ١ عند خطوط الثني الثلاثة لتصبح أنبوباً مربعاً.'),
         ('Weld the single seam along the edge; weld the base plate (2) inside the bottom.', 'لحام الوصلة الوحيدة، ولحام لوح القاع (٢) داخل القاع.'),
         ('Grind the welds and brush the whole piece to one grain; deburr hole edges.', 'صنفرة اللحام وتبريش القطعة كلها في اتجاه واحد وتنعيم حواف الفتحات.'),
         ('Hang the loose liner (3) on the rim.', 'تعليق البطانة السائبة (٣) على الحافة.')]
for i, (en, ar) in enumerate(steps):
    yy = 48 + i*17
    b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 2.0) + t(410, yy+5, ar, 2.0, 400, 'end', extra=AR)
sh3 = sheet(3, N, 'ASSEMBLY', 'التجميع', 'n/a', b)
# ================= SHEET 4: cutting layout =================
S4 = .1
b = t(10, 22, f'CUTTING LAYOUT on an assumed sheet {SHEET_L} x {SHEET_W} x {T} (proposal, to be confirmed by Production).', 2.4, 600) + t(410, 22, 'مخطط القص على لوح مفترض، يؤكده التصنيع', 2.4, 600, 'end', extra=AR)
ox4, oy4 = 30, 40
b += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6') + t(ox4, oy4-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for k, x, y in NEST:
    w, h = SIZE[k]; b += rect(ox4+x*S4, oy4+y*S4, w*S4, h*S4, .3, INK, FILL)
    if k == 'P1':
        for _, f, d, z in HOLES: b += circ(ox4+(x+FX[f])*S4, oy4+(y+H-z)*S4, d/2*S4)
    b += t(ox4+(x+w/2)*S4, oy4+(y+h/2)*S4+1, k[1], 3.4, 600, 'middle', '#555')
b += dim_h(ox4, ox4+SHEET_L*S4, oy4+SHEET_W*S4+7, f'{SHEET_L}', ext=oy4+SHEET_W*S4) + dim_v(ox4-6, oy4, oy4+SHEET_W*S4, f'{SHEET_W}', ext=ox4)
b += t(30, 195, f'Two parts, {GAP} mm spacing, one corner of the sheet. No offcut is claimed. Part 1 is 800 long: the fold length Production must be able to press.', 2.3)
b += t(30, 200, f'Total cutting length: {TOTAL_CUT/1000:.2f} m ({TOTAL_CUT:.0f} mm): outlines {(OUTLINE["P1"]+OUTLINE["P2"]):.0f} + five holes {HOLE_CUT:.0f}.', 2.5, 600)
b += t(410, 195, 'قطعتان بمسافة ١٠ مم. لا يُدّعى أي هالك. القطعة ١ بطول ٨٠٠ مم.', 2.3, 400, 'end', extra=AR) + t(410, 200, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.5, 600, 'end', extra=AR)
sh4 = sheet(4, N, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)
# ================= SHEET 5: BOM and notes =================
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + t(410, 28, 'قائمة المواد', 2.8, 600, 'end', extra=AR)
b += rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Wrapped body, 5 holes', 'الجسم الملفوف بخمس فتحات', '1', 'Stainless sheet 2 mm (proposal)'), ('2', 'Base plate', 'لوح القاع', '1', 'Stainless sheet 2 mm (proposal)'), ('3', 'Loose liner, closed bottom', 'بطانة سائبة', '1', 'By Production; not drawn')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*7
    b += line(10, yy+2.2, 410, yy+2.2, .15, HID) + t(12, yy, n_, 2.4) + t(24, yy, en, 2.4) + t(140, yy, ar, 2.4, 400, 'end', extra=AR) + t(150, yy, q, 2.4) + t(215, yy, m_, 2.4)
b += t(10, 80, 'NOTES', 2.8, 600) + t(410, 80, 'ملاحظات', 2.8, 600, 'end', extra=AR)
nts = [('Height 800 mm is Sabry\'s (12 Nov). Width 160, sheet 2 mm, hole sizes and heights, liner depth 220 are proposals, not costed. Production to confirm.', 'الارتفاع ٨٠٠ مم من سبري. باقي المقاسات مقترحة ويؤكدها التصنيع.'),
       ('Reference: a photo of a third-party piece (maker unknown): square tube, flat top, five round holes on several faces. Drawn as objekt\'s own design with our own hole layout.', 'المرجع صورة لقطعة من صانع آخر مجهول. مرسومة كتصميم خاص بأوبجيكت.'),
       ('Planter (Sabry, 12 Nov). Holes below the liner leak if soil sits there, so no hole is above 520 mm and the liner is loose, closed bottom, no drain hole. Plants and water stay in the liner.', 'جاردينيرا: لا فتحات فوق ٥٢٠ مم، والبطانة سائبة بقاع مغلق بدون صرف.'),
       ('Finish: brushed stainless, no paint (objekt guide: exposed metal, brushed). Production to say how to brush the weld seam and the hole edges.', 'التشطيب: ستانلس مبروش بدون دهان. التصنيع يحدد تبريش اللحام.'),
       ('Production-fit points to check (Production): body flat 640 x 800 fits a 1250 x 2500 sheet; 800 mm fold length on the press brake; distortion of a long seam in 2 mm stainless; hole edge to fold distance.', 'نقاط للتصنيع: طول الثني ٨٠٠ مم، وتشوه اللحام الطويل في ٢ مم.'),
       ('Material, thickness, bend allowance, tolerances, sheet size, joints, welding and finish details are Production\'s to decide.', 'الخامة والسماكة والسماحيات واللحام يقررها التصنيع.'),
       ('No structural claims, stress or load figures, costs or prices. Not engineered. A tall light column may need a heavier base or fixing: Production to say.', 'لا ادعاءات إنشائية ولا تكاليف. قد يحتاج العمود الطويل لقاعدة أثقل: التصنيع.'),
       ('Arabic wording is a draft for a technical reader.', 'الصياغة العربية مسودة.')]
for i, (en, ar) in enumerate(nts):
    yy = 89 + i*13
    b += t(12, yy, f'{i+1}.', 2.4, 600) + t(18, yy, en, 2.1) + t(410, yy+5, ar, 2.1, 400, 'end', extra=AR)
sh5 = sheet(5, N, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)
for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1):
    open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('outlines', OUTLINE, 'holes', round(HOLE_CUT), 'total', round(TOTAL_CUT), 'zmax', ZMAX)
