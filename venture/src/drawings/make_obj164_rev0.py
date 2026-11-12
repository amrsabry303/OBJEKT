"""OBJ-164: corner shelf, triangular, sold as a pair. Production drawing set, REV 0 (approved by Sabry 12 Nov 2026).
Run: python3 make_obj164_rev0.py <repo root>   Then make_pdf.js for the PDF.
Size 220 x 220 mm legs is Sabry's (production-book caption "2pc 22x22CM"). Everything else (2 mm stainless, 10 mm folded front edge,
150 mm gusset, 15 mm wall flanges, 4 screws per shelf, pair) is a PROPOSAL, not costed, Production to confirm.
Gusset reading of the photo (a vertical triangular plate in the corner's bisector plane, vertical edge in the wall corner) is inferred.
Arabic wording is a draft for a technical reader. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-164'; os.makedirs(OUT, exist_ok=True)
PHOTO = ROOT + '/images/OBJ-164.jpg'
REV = 0; DATE = '12 Nov 2026'; PN = 'OBJ-164'
LEG = 220; T = 2; LIP = 10; FL = 15; DROP = 150
HYP = LEG*math.sqrt(2); GL = LEG/math.sqrt(2)         # hypotenuse 311.1, gusset top edge 155.6
GH = math.hypot(GL, DROP)                              # gusset sloped edge
OH = T + DROP                                          # overall height 152
HOLE_D = 5; HOLES_AT = (60, 160)
SHEET_L, SHEET_W, GAP = 2500, 1250, 10
O = FL                                                 # flat origin offset so bbox min = (0,0)
nn = LIP/math.sqrt(2)
def top_pts():
    A = (O, O); B = (O+LEG, O); C = (O, O+LEG)
    return [(O+10, O), (O+10, O-FL), (O+LEG-10, O-FL), (O+LEG-10, O), B, (B[0]+nn, B[1]+nn), (C[0]+nn, C[1]+nn), C,
            (O, O+LEG-10), (O-FL, O+LEG-10), (O-FL, O+10), (O, O+10), A]
def top_holes():
    h = [(O+a, O-FL/2) for a in HOLES_AT] + [(O-FL/2, O+a) for a in HOLES_AT]; return h
def gus_pts(): return [(0, 0), (GL, 0), (0, DROP)]
def perim(p): return sum(math.dist(p[i], p[(i+1) % len(p)]) for i in range(len(p)))
TOPW = LEG+FL+nn; TOPH = TOPW                          # bbox 242.1 square
PARTS = {'P1': ('Top plate with front fold and wall flanges (flat)', 'لوح الرف بالثنية الأمامية وزعانف الحائط (مسطح)', 2, 'top', (TOPW, TOPH), perim(top_pts())+4*math.pi*HOLE_D),
         'P2': ('Gusset plate', 'لوح التدعيم المثلث', 2, 'gus', (GL, DROP), perim(gus_pts()))}
TOTAL_CUT = sum(v[2]*v[5] for v in PARTS.values())
x2 = GAP+TOPW+GAP
NEST = [('P1', GAP, GAP), ('P1', x2, GAP), ('P2', GAP, GAP+TOPH+GAP), ('P2', GAP+GL+GAP, GAP+TOPH+GAP)]
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
    d.layers.add('CUT', color=7); d.layers.add('SHEET', color=3); return d
def add_part(msp, key, ox, oy):
    if key == 'P1':
        msp.add_lwpolyline([(ox+x, oy+y) for x, y in top_pts()], close=True, dxfattribs={'layer': 'CUT'})
        for hx, hy in top_holes(): msp.add_circle((ox+hx, oy+hy), HOLE_D/2, dxfattribs={'layer': 'CUT'})
    else: msp.add_lwpolyline([(ox+x, oy+y) for x, y in gus_pts()], close=True, dxfattribs={'layer': 'CUT'})
FN = {'P1': 'top-plate', 'P2': 'gusset'}
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


STAMP = 'Approved by Sabry 12 Nov 2026. Production review pending. Not engineered'; STAMP_AR = 'معتمد من سبري ١٢ نوفمبر ٢٠٢٦. بانتظار مراجعة التصنيع. غير مهندس'
AR = ' direction="rtl"'
def frame(n, N, title_en, title_ar, scale):
    s = rect(5, 5, 410, 287, .5) + rect(7, 7, 406, 283, .2)
    X, Y, Wd = 228, 247, 185
    s += rect(X, Y, Wd, 41, .4, fill='#fff')
    s += line(X, Y+9, X+Wd, Y+9, .25) + line(X, Y+20, X+Wd, Y+20, .25) + line(X, Y+31, X+Wd, Y+31, .25) + line(X+92, Y+9, X+92, Y+41, .25)
    s += bi(X+2, Y+4, f'{PN}   Corner shelf, triangular (pair)', 'رف زاوية مثلث (زوج)', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  {LEG} x {LEG} x {OH} mm each', 'المقاس لكل رف', 88, 2.1) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, 'MATERIAL  Stainless sheet 2 mm (proposal)', 'الخامة: ستانلس ٢ مم (مقترح)', 88, 2.1) + bi(X+94, Y+25, 'FINISH  Brushed (proposal)', 'التشطيب: مبشور (مقترح)', 88, 2.1)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, '#2f6b45', '#fff')
    s += t(X+Wd/2, Y-8.6, STAMP, 2.5, 700, 'middle', '#2f6b45') + t(X+Wd/2, Y-3.8, STAMP_AR, 2.5, 700, 'middle', '#2f6b45')
    s += t(10, 14, title_en, 4.2, 700) + t(410, 14, title_ar, 4.2, 700, 'end', extra=' direction="rtl"')
    return s
def sheet(n, N, title_en, title_ar, scale, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, N, title_en, title_ar, scale)}{body}</svg>'
N = 5; S = .4
# ================= SHEET 1: views =================
# PLAN: corner at top-left of the plan (walls along the left and top edges); x right, y down
oxp, oyp = 30, 40
def px(x): return oxp + x*S
def py(y): return oyp + y*S
b = t(22, 30, 'PLAN (top, true shape)', 2.8, 600) + t(205, 34, 'المسقط الأفقي', 2.6, 500, 'end', extra=AR)
plan_top = [(0, 0), (LEG, 0), (LEG+nn, nn), (nn, LEG+nn), (0, LEG)]
b += poly([(px(x), py(y)) for x, y in [(0, 0), (LEG, 0), (0, LEG)]], .45, INK, '#e6e6e4')
b += poly([(px(x), py(y)) for x, y in [(LEG, 0), (LEG+nn, nn), (nn, LEG+nn), (0, LEG)]], .3, INK, '#cfcfcc')     # folded front edge seen from above
b += line(px(0), py(0), px(LEG/2), py(LEG/2), .25, HID, '1.5 1')                                                    # gusset below, hidden
b += rect(px(0)-1.5, py(0), 1.5, LEG*S, .3, '#999', '#ddd') + rect(px(0), py(0)-1.5, LEG*S, 1.5, .3, '#999', '#ddd')  # walls
b += t(px(LEG/2), py(0)-3, 'WALL / حائط', 2, 400, 'middle', HID)
b += dim_h(px(0), px(LEG), py(0)-9, f'{LEG}', ext=py(0)-1.5) + dim_v(px(0)-9, py(0), py(LEG), f'{LEG}', ext=px(0)-1.5)
mx, my = (px(LEG)+px(0))/2, (py(0)+py(LEG))/2
b += t(mx+8, my-3, f'front edge {HYP:.1f}', 2.3, 500, fill=DIM) + t(mx+8, my+.5, 'الحافة الأمامية', 2.2, 400, 'start', DIM, extra=AR)
b += t(px(LEG/2)-4, py(LEG/2)+12, 'gusset below (dashed), along the corner bisector', 2.0, 400, fill=HID)
b += t(px(LEG/2)-4, py(LEG/2)+15, f'{GL:.1f} long', 2.0, 400, fill=HID)
b += t(px(8), py(LEG*.28), '90°', 2.4, 500, fill=DIM)
# FRONT ELEVATION (looking at the corner along the bisector)
ox, oz = 275, 62
def fx(x): return ox + x*S
def fz(z): return oz + z*S   # z downward from top face
b += t(215, 30, 'FRONT ELEVATION (looking into the corner)', 2.8, 600) + t(410, 34, 'الواجهة الأمامية (نحو الركن)', 2.6, 500, 'end', extra=AR)
half = HYP/2
b += rect(fx(-half), fz(0), HYP*S, T*S, .45, INK, '#d8d8d5') + rect(fx(-half), fz(T), HYP*S, LIP*S, .35, INK, '#cfcfcc')
b += rect(fx(-T/2), fz(T), T*S, DROP*S, .4, INK, '#bdbdb9')
b += dim_h(fx(-half), fx(half), fz(0)-5, f'{HYP:.1f}', ext=fz(0)) 
b += dim_v(fx(half)+8, fz(0), fz(OH), f'{OH}', ext=fx(half)) + dim_v(fx(half)+16, fz(T), fz(OH), f'{DROP}', ext=fx(half))
b += dim_v(fx(-half)-8, fz(T), fz(T+LIP), f'{LIP}', ext=fx(-half)) + t(fx(-half)-12, fz(T)+LIP*S+5, 'fold', 2, 400, 'end', DIM)
b += t(fx(0)+4, fz(T+DROP/2), 'gusset edge-on', 2.0, 400, fill=HID) + t(fx(0)+4, fz(T+DROP/2)+3, 'لوح التدعيم من الجانب', 2.0, 400, fill=HID)
b += balloon(fx(-half)+10, fz(0)-12, 1) + balloon(fx(0)+16, fz(T+DROP*.8), 2)
# SIDE ELEVATION (looking along one wall)
ox2 = 235; oz2 = 150
def sx(x): return ox2 + x*S
def sz(z): return oz2 + z*S
b += t(215, 138, 'SIDE ELEVATION (looking along a wall)', 2.8, 600) + t(410, 142, 'منظر جانبي (بمحاذاة الحائط)', 2.6, 500, 'end', extra=AR)
b += rect(sx(0), sz(0), LEG*S, T*S, .45, INK, '#d8d8d5') + rect(sx(0), sz(T), LEG*S, LIP*S, .3, INK, '#cfcfcc')
b += poly([(sx(0), sz(T)), (sx(GL/math.sqrt(2)), sz(T)), (sx(0), sz(T+DROP))], .4, INK, '#bdbdb9')
b += rect(sx(0)-1.5, sz(-5), 1.5, (OH+10)*S, .3, '#999', '#ddd') + t(sx(0)-4, sz(OH/2), 'WALL / حائط', 2, 400, 'end', HID)
b += dim_h(sx(0), sx(LEG), sz(OH)+8, f'{LEG}', ext=sz(OH)) + dim_v(sx(LEG)+8, sz(0), sz(OH), f'{OH}', ext=sx(LEG))
b += dim_h(sx(0), sx(GL/math.sqrt(2)), sz(T)-6 if False else sz(T+DROP)+3, f'{GL/math.sqrt(2):.1f}', ext=None)
b += t(sx(118), sz(T+DROP*.5), 'gusset: vertical edge in the corner, 150 deep', 2.0, 400, fill=HID) + t(sx(118), sz(T+DROP*.5)+3, 'الحافة الرأسية في الركن', 2.0, 400, fill=HID)
# reference photo + notes
b += t(22, 160, 'REFERENCE PHOTO (Sabry, 12 Nov; maker unknown, device on the shelf is not ours)', 2.3, 600) + t(205, 164, 'صورة مرجعية (الجهاز ليس لنا)', 2.3, 500, 'end', extra=AR)
b += f'<image href="{datauri(PHOTO)}" x="22" y="166" width="64" height="74" preserveAspectRatio="xMidYMid slice"/>' + rect(22, 166, 64, 74, .2, HID)
for i, ln in enumerate(['Shape inferred from one photo, approximate:', 'flat triangular top that fits the corner, a deep', 'triangular gusset below it, crisp front edge, no', 'visible fixings. Drawn as objekt\'s own design.', 'The shelf-top device in the photo is not drawn.']):
    b += t(92, 172+i*3.6, ln, 2.0, 400, fill=HID)
b += t(205, 172, 'الشكل مقدّر من صورة واحدة، تقريبي', 2.0, 400, 'end', HID, extra=AR)
b += t(22, 262, 'Colourways: bare brushed stainless (proposal). No paint colour; objekt palette not used on exposed metal.', 2.0, 400, fill=HID)
b += t(22, 266, 'ألوان: ستانلس مبشور بدون دهان (مقترح).', 2.0, 400, fill=HID)
b += t(22, 276, f'Leg 220 x 220 is Sabry\'s (production-book caption "2pc 22x22CM"). Thickness 2, fold {LIP}, gusset drop {DROP}, flange {FL}, screws, pair: PROPOSALS,', 2.0, 400, fill=HID)
b += t(22, 279.5, f'not costed, Production to confirm. Overall height {OH} = top plate {T} + gusset {DROP} below it.  المقاسات عدا ٢٢٠ مقترحة، يؤكدها التصنيع.', 2.0, 400, fill=HID)
sh1 = sheet(1, N, 'VIEWS', 'المناظير', '1:2.5', b)

# ================= SHEET 2: flat patterns =================
S2 = .5
b = t(10, 22, 'Flat patterns at 1:2, bend allowance NOT applied (Production adds it). Fold lines dashed.', 2.3, 400, fill=HID) + t(410, 22, 'الأنماط المسطحة، بدون سماحية الثني (يضيفها التصنيع). خطوط الثني متقطعة.', 2.3, 400, 'end', HID)
x1, y1 = 40, 45
def fx1(x): return x1 + x*S2
def fy1(y): return y1 + (TOPH-y)*S2           # math y-up -> svg y-down
b += poly([(fx1(x), fy1(y)) for x, y in top_pts()], .4, INK, FILL)
for hx, hy in top_holes(): b += f'<circle cx="{fx1(hx):.2f}" cy="{fy1(hy):.2f}" r="{HOLE_D/2*S2:.2f}" fill="#fff" stroke="{INK}" stroke-width=".3"/>'
b += line(fx1(O+10), fy1(O), fx1(O+LEG-10), fy1(O), .25, DIM, '2 1') + line(fx1(O), fy1(O+10), fx1(O), fy1(O+LEG-10), .25, DIM, '2 1')
b += line(fx1(O+LEG), fy1(O), fx1(O), fy1(O+LEG), .25, DIM, '2 1')
b += dim_h(fx1(O), fx1(O+LEG), fy1(O-FL)+14, f'{LEG}', ext=fy1(O-FL)) + dim_v(fx1(O-FL)-6, fy1(O+LEG), fy1(O), f'{LEG}', ext=fx1(O-FL))
b += dim_h(fx1(O+HOLES_AT[0]), fx1(O+HOLES_AT[1]), fy1(O-FL)+7, f'{HOLES_AT[1]-HOLES_AT[0]}', ext=fy1(O-FL/2)) 
b += dim_h(fx1(O), fx1(O+HOLES_AT[0]), fy1(O-FL)+7, f'{HOLES_AT[0]}', ext=fy1(O-FL/2))
b += dim_v(fx1(O-FL)-14, fy1(O), fy1(O-FL), f'{FL}', ext=fx1(O-FL)) 
b += t(fx1(O+LEG*.55), fy1(O+LEG*.25), f'fold line, front edge {HYP:.1f}', 2.0, 400, fill=DIM) + t(fx1(O+LEG*.55), fy1(O+LEG*.25)+3, f'ثنية {LIP} مم', 2.0, 400, fill=DIM)
b += t(x1, y1-4, f'1  TOP PLATE, flat, {PARTS["P1"][2]} off (one per shelf)', 2.4, 600) + t(x1+TOPW*S2, y1-4, 'لوح الرف، عدد ٢', 2.4, 600, 'end', extra=AR) + balloon(x1-20, y1+TOPH*S2/2, 1)
x3, y3 = 250, 60
def fx3(x): return x3 + x*S2
def fy3(y): return y3 + (DROP-y)*S2
b += poly([(fx3(x), fy3(y)) for x, y in gus_pts()], .4, INK, FILL)
b += dim_h(fx3(0), fx3(GL), fy3(0)+7, f'{GL:.1f}', ext=fy3(0)) + dim_v(fx3(0)-6, fy3(DROP), fy3(0), f'{DROP}', ext=fx3(0))
b += t(fx3(GL*.4), fy3(DROP*.35)-1, f'{GH:.1f}', 2.3, 500, fill=DIM)
b += t(x3, y3-6, '2  GUSSET PLATE, 2 off (one per shelf)', 2.4, 600) + t(x3+GL*S2+30, y3-6, 'لوح التدعيم، عدد ٢', 2.4, 600, 'end', extra=AR) + balloon(x3-10, y3+DROP*S2/2, 2)
dx, dy = 22, 200
b += t(dx, dy, 'DATA  mm', 2.4, 600) + t(224, dy, 'بيانات', 2.4, 600, 'end', extra=AR)
rows = [('Part', 'Qty (pair)', 'Flat size (bbox)', 'Outline each'), ('1 Top plate', '2', f'{TOPW:.1f} x {TOPH:.1f}, 4 holes dia {HOLE_D}', f'{PARTS["P1"][5]:.0f}'), ('2 Gusset', '2', f'{GL:.1f} x {DROP}', f'{PARTS["P2"][5]:.0f}')]
for i, r_ in enumerate(rows):
    yy = dy+5+i*4.2
    for xx, v in zip((dx, dx+30, dx+55, dx+135), r_): b += t(xx, yy, v, 2.1, 600 if i == 0 else 400)
for i, ln in enumerate([f'Gusset top edge {GL:.1f} = {LEG} / sqrt 2 (half the front edge); vertical edge {DROP}; welded to the underside of the top plate, vertical edge in the wall corner.',
                        f'Wall flanges {FL} fold down; two dia {HOLE_D} holes on each at {HOLES_AT[0]} and {HOLES_AT[1]} from the corner. Screws and plugs: bought-in, by Production.',
                        f'Corner relief 10 mm at the flange ends so the two flanges do not touch. Front fold {LIP} down along the {HYP:.1f} edge.',
                        'Thickness 2 mm is a proposal. Bend allowance, welding, blending and brushing direction: Production.']):
    b += t(dx, dy+22+i*3.8, ln, 2.0)
b += t(410, dy+22, 'سماكة ٢ مم مقترحة. سماحية الثني واللحام والتنعيم واتجاه البشر من التصنيع.', 2.0, 400, 'end', extra=AR)
sh2 = sheet(2, N, 'PART SHEET', 'ورقة القطع', '1:2', b)

# ================= SHEET 3: assembly =================
SC = .6
def P(x, y, z): return 40+88*SC + (x*.9 - y*.4)*SC, 55 + (x*.25 + y*.45 + z)*SC   # z down
def pl(pts3, fill, sw=.35): return poly([P(*q) for q in pts3], sw, INK, fill)
b = t(10, 22, 'EXPLODED VIEW (proposed assembly; Production decides jigs, welds and fixings)', 2.5, 600) + t(410, 22, 'منظر مفكك (تجميع مقترح، والتصنيع يقرر القوالب واللحام)', 2.5, 600, 'end', extra=AR)
EXG = 60
gb = [(0, 0, T+EXG), (GL/math.sqrt(2), GL/math.sqrt(2), T+EXG), (GL/math.sqrt(2), GL/math.sqrt(2), T+EXG), (0, 0, T+EXG+DROP)]
b += pl([(0, 0, T+EXG), (GL/math.sqrt(2), GL/math.sqrt(2), T+EXG), (0, 0, T+EXG+DROP)], '#bdbdb9')
for q in [(0, 0, T), (GL/math.sqrt(2), GL/math.sqrt(2), T)]:
    (ax, ay), (bx, by) = P(*q), P(q[0], q[1], q[2]+EXG); b += line(ax, ay, bx, by, .2, HID, '1 1')
b += pl([(0, 0, 0), (LEG, 0, 0), (0, LEG, 0)], '#d8d8d5', .45)
b += pl([(LEG, 0, 0), (LEG+nn, nn, 0), (nn, LEG+nn, 0), (0, LEG, 0)], '#cfcfcc')
b += pl([(LEG, 0, 0), (0, LEG, 0), (0, LEG, LIP), (LEG, 0, LIP)], '#c4c4c0')
b += pl([(10, 0, 0), (LEG-10, 0, 0), (LEG-10, 0, FL), (10, 0, FL)], '#bdbdb9') + pl([(0, 10, 0), (0, LEG-10, 0), (0, LEG-10, FL), (0, 10, FL)], '#bdbdb9')
ax, ay = P(LEG*.3, LEG*.3, 0); b += balloon(ax, ay-12, 1)
ax, ay = P(0, 0, T+EXG+DROP*.6); b += balloon(ax-8, ay, 2)
ax, ay = P(LEG/2, 0, FL); b += balloon(ax+10, ay+4, 3)
b += t(22, 262, 'Wall fixings (3): 4 screws and plugs per shelf, through the flanges, for the wall type (Production / installer). Heads sit under the top plate, hidden from above.', 2.0, 400, fill=HID)
b += t(224, 266, 'التثبيت بالحائط: ٤ مسامير وفيشر لكل رف عبر الزعانف، حسب نوع الحائط.', 2.0, 400, 'end', HID, extra=AR)
sx0 = 245
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end', extra=AR)
steps = [('Cut parts 1 and 2 from the DXF files; deburr.', 'قص القطعتين ١ و٢ من ملفات DXF وتنعيم الحواف.'),
         ('Fold the front edge and the two wall flanges of the top plate (1).', 'ثني الحافة الأمامية وزعنفتي الحائط في لوح الرف (١).'),
         ('Weld the gusset (2) under the top plate, vertical edge in the corner; blend the weld.', 'لحام لوح التدعيم (٢) تحت لوح الرف مع الركن وتنعيم اللحام.'),
         ('Brush the finish in one direction on all visible faces.', 'بشر السطح في اتجاه واحد على كل الوجوه الظاهرة.'),
         ('Fix to the wall through the flanges (3); two screws per wall side. Make two shelves for the pair.', 'التثبيت بالحائط عبر الزعانف (٣). صنع رفين للزوج.')]
for i, (en, ar) in enumerate(steps):
    yy = 48 + i*17
    b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 2.2) + t(410, yy+5, ar, 2.2, 400, 'end', extra=AR)
sh3 = sheet(3, N, 'ASSEMBLY', 'التجميع', 'n/a', b)

# ================= SHEET 4: cutting layout =================
S4 = .1
b = t(10, 22, f'CUTTING LAYOUT for one PAIR on an assumed sheet {SHEET_L} x {SHEET_W} x {T} (proposal, Production to confirm).', 2.4, 600) + t(410, 22, 'مخطط القص لزوج على لوح مفترض، يؤكده التصنيع', 2.4, 600, 'end', extra=AR)
ox4, oy4 = 30, 40
b += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6') + t(ox4, oy4-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for k, x, y in NEST:
    w, h = size(k)
    pts = top_pts() if k == 'P1' else gus_pts()
    b += poly([(ox4+(x+px_)*S4, oy4+(y+h-py_)*S4) for px_, py_ in pts], .3, INK, FILL)
    b += t(ox4+(x+w/2)*S4, oy4+(y+h/2)*S4+1, k[1], 3.4, 600, 'middle', '#555')
b += dim_h(ox4, ox4+SHEET_L*S4, oy4+SHEET_W*S4+7, f'{SHEET_L}', ext=oy4+SHEET_W*S4) + dim_v(ox4-6, oy4, oy4+SHEET_W*S4, f'{SHEET_W}', ext=ox4)
b += t(30, 195, f'Parts nested with {GAP} mm spacing in one corner: about {USED_X:.0f} x {USED_Y:.0f} mm used. No offcut is claimed.', 2.3)
b += t(30, 200, f'Total cutting length, 2 top plates (with holes) + 2 gussets: {TOTAL_CUT/1000:.2f} m ({TOTAL_CUT:.0f} mm), outlines only.', 2.5, 600)
b += t(410, 195, 'الأجزاء مرتبة بمسافة ١٠ مم. لا يُدّعى أي هالك.', 2.3, 400, 'end', extra=AR) + t(410, 200, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.5, 600, 'end', extra=AR)
sh4 = sheet(4, N, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)

# ================= SHEET 5: BOM and notes =================
b = t(10, 28, 'BILL OF MATERIALS (for one PAIR = 2 shelves)', 2.8, 600) + t(410, 28, 'قائمة المواد (لزوج = رفان)', 2.8, 600, 'end', extra=AR)
b += rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Top plate with front fold and flanges', 'لوح الرف بالثنية والزعانف', '2', 'Stainless sheet 2 mm, brushed (proposal)'),
       ('2', 'Gusset plate', 'لوح التدعيم', '2', 'Stainless sheet 2 mm, brushed (proposal)'),
       ('3', 'Wall screw and plug', 'مسمار وفيشر للحائط', '8 (4 per shelf)', 'Bought-in; for the wall type, by Production')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*7
    b += line(10, yy+2.2, 410, yy+2.2, .15, HID) + t(12, yy, n_, 2.4) + t(24, yy, en, 2.4) + t(140, yy, ar, 2.4, 400, 'end', extra=AR) + t(150, yy, q, 2.4) + t(215, yy, m_, 2.4)
b += t(10, 80, 'NOTES', 2.8, 600) + t(410, 80, 'ملاحظات', 2.8, 600, 'end', extra=AR)
notes = [('Leg length 220 x 220 mm is Sabry\'s size (the production-book caption reads "2pc 22x22CM"), taken as the two straight edges that run along the walls. Front edge about 311 mm.', 'الضلعان ٢٢٠ × ٢٢٠ مم (مقاس سبري) على الحائطين، والحافة الأمامية حوالي ٣١١ مم.'),
         ('Proposals, not costed, Production to confirm: stainless sheet 2 mm, brushed; front fold 10 mm; gusset drop 150 mm (overall height 152); wall flanges 15 mm with 4 holes dia 5 per shelf; sold as a pair.', 'مقترحات غير مسعرة يؤكدها التصنيع: ستانلس ٢ مم مبشور، ثنية ١٠ مم، تدعيم ١٥٠ مم، زعانف ١٥ مم، زوج.'),
         ('Shape inferred from one photo of unknown maker: flat triangular top, a deep triangular gusset under it with its vertical edge in the wall corner, crisp edge, no visible fixings. Drawn as objekt\'s own design. The device on the shelf is not ours and not drawn.', 'الشكل مقدّر من صورة واحدة، ومرسوم كتصميم خاص بأوبجيكت. الجهاز على الرف ليس لنا.'),
         ('Hidden fixing: the screws pass through the folded flanges against the wall and are covered by the top plate from above. Wall type and plugs are not known: Production / installer to decide.', 'التثبيت مخفي: المسامير عبر الزعانف ومغطاة بلوح الرف من أعلى.'),
         ('Finish: exposed brushed stainless, no paint (proposal). Stainless grade, brushing direction and welding / blending method are Production\'s to decide.', 'التشطيب: ستانلس مبشور بدون دهان (مقترح). النوع واتجاه البشر واللحام من التصنيع.'),
         ('Material, thickness, bend allowance, tolerances, sheet size, joints and finish details are Production\'s to decide.', 'الخامة والسماكة والسماحيات واللحام وتفاصيل التشطيب يقررها التصنيع.'),
         ('No structural claims, stress figures, load figures, costs or prices on this drawing. Not engineered. A stated shelf load is not claimed until Production tests it. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا حمل مذكور ولا تكاليف. الصياغة العربية مسودة.')]
for i, (en, ar) in enumerate(notes):
    yy = 89 + i*13
    b += t(12, yy, f'{i+1}.', 2.4, 600) + t(18, yy, en, 2.2) + t(410, yy+5, ar, 2.2, 400, 'end', extra=AR)
sh5 = sheet(5, N, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)

for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1):
    open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('outlines (mm):', {k: round(v[5]) for k, v in PARTS.items()}, 'total', round(TOTAL_CUT), 'nest', MSG, 'used', round(USED_X), round(USED_Y))
