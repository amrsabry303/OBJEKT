"""OBJ-192: long low planter on four swivel casters. Production drawing set, REV 0 (DRAFT).
Run: python3 make_obj192_rev0.py <repo root>   Then make_pdf.js for the PDF.
Sizes: 900 x 300 x 450 overall is a PROPOSAL (Sabry: "u suggest"), not costed, Production to confirm. Colours (Carbon, Oxblood, Bone), matte powder coat,
rubber casters and subcategory Planters are Sabry's answers (12 Nov). Shape is estimated by eye from a low-resolution reference render, approximate.
Arabic wording is a draft and needs a technical reader. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-192'; os.makedirs(OUT, exist_ok=True)
PHOTO = ROOT + '/images/OBJ-192.jpg'
REV = 0; DATE = '12 Nov 2026'; PN = 'OBJ-192'
L, W, H = 900, 300, 450           # overall, proposal
T = 2                             # sheet thickness, proposal
CASTER_H = 70                     # caster overall height incl. 50 mm wheel, ASSUMED until the caster is chosen
PLATE_H = H - CASTER_H            # 380 steel height
R = 60                            # top corner radius of the end plates, from the photo, approximate
PZ0, PZ1 = 110, 320               # panel bottom / top above plate bottom (panel top = where the plate corner radius starts)
PL = L - 2*T; PH = PZ1 - PZ0      # panel 896 x 210
FL, FW = L - 2*T, W - 2*T         # floor 896 x 296
CY = [50, W-50]                   # caster positions along the depth
SHEET_L, SHEET_W, GAP = 2500, 1250, 10
BUL = math.tan(math.radians(90)/4)
def plate_pts(n=12):
    """end plate profile, origin bottom-left, x along the depth (W), y up (PLATE_H); top corners rounded R"""
    p = [(0, 0), (W, 0), (W, PLATE_H-R)]
    for i in range(1, n+1):
        a = math.radians(90*i/n); p.append((W-R+R*math.cos(a), PLATE_H-R+R*math.sin(a)))
    p.append((R, PLATE_H))
    for i in range(1, n+1):
        a = math.radians(90+90*i/n); p.append((R+R*math.cos(a), PLATE_H-R+R*math.sin(a)))
    p.append((0, PLATE_H-R)); return p
def plate_perim(): return W + 2*(PLATE_H-R) + (W-2*R) + 2*(math.pi*R/2)
PARTS = {'P1': ('End plate', 'لوح الطرف', 2, 'plate', (W, PLATE_H), plate_perim()),
         'P2': ('Front / back panel', 'اللوح الأمامي والخلفي', 2, 'rect', (PL, PH), 2*(PL+PH)),
         'P3': ('Floor plate', 'لوح القاع', 1, 'rect', (FL, FW), 2*(FL+FW))}
TOTAL_CUT = sum(v[2]*v[5] for v in PARTS.values())
NEST = [('P2', GAP, GAP), ('P2', GAP+PL+GAP, GAP), ('P3', GAP, GAP+PH+GAP), ('P1', GAP+PL+GAP, GAP+PH+GAP), ('P1', GAP+PL+GAP+W+GAP, GAP+PH+GAP)]
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
    kind, (w, h) = PARTS[key][3], PARTS[key][4]
    if kind == 'rect':
        msp.add_lwpolyline([(ox, oy), (ox+w, oy), (ox+w, oy+h), (ox, oy+h)], close=True, dxfattribs={'layer': 'CUT'})
    else:  # plate with true arcs (bulge)
        pts = [(0, 0, 0), (W, 0, 0), (W, PLATE_H-R, BUL), (W-R, PLATE_H, 0), (R, PLATE_H, BUL), (0, PLATE_H-R, 0)]
        msp.add_lwpolyline([(ox+x, oy+y, 0, 0, b) for x, y, b in pts], format='xyseb', close=True, dxfattribs={'layer': 'CUT'})
FN = {'P1': 'end-plate', 'P2': 'panel', 'P3': 'floor'}
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


Z0P = CASTER_H                       # plate bottom (absolute z)
PZA, PZB = Z0P+PZ0, Z0P+PZ1          # panel bottom / top (absolute z) = 180 / 390
STAMP = 'DRAFT, not approved, not engineered'; STAMP_AR = 'مسودة، غير معتمدة، غير مهندسة'
COLS = [('Carbon', '#222222', 'أسود فحمي'), ('Oxblood', '#5A1F25', 'عنابي داكن'), ('Bone', '#E9E4D8', 'عاجي')]
def frame(n, N, title_en, title_ar, scale):
    s = rect(5, 5, 410, 287, .5) + rect(7, 7, 406, 283, .2)
    X, Y, Wd = 228, 247, 185
    s += rect(X, Y, Wd, 41, .4, fill='#fff')
    s += line(X, Y+9, X+Wd, Y+9, .25) + line(X, Y+20, X+Wd, Y+20, .25) + line(X, Y+31, X+Wd, Y+31, .25) + line(X+92, Y+9, X+92, Y+41, .25)
    s += bi(X+2, Y+4, f'{PN}   Planter, long low trough on four casters', 'جاردينيرا طويلة منخفضة على أربع عجلات', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  {L} x {W} x {H} mm incl. casters (proposal)', 'المقاس الكلي شاملاً العجلات (مقترح)', 88, 2.1) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, 'MATERIAL  Sheet steel 2 mm (proposal), welded', 'الخامة: صاج ٢ مم (مقترح)، لحام', 88, 2.1) + bi(X+94, Y+25, 'FINISH  Powder coating, matte (Sabry)', 'التشطيب: دهان بودرة مطفي', 88, 2.1)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, '#b3261e', '#fff')
    s += t(X+Wd/2, Y-8.6, STAMP, 2.9, 700, 'middle', '#b3261e') + t(X+Wd/2, Y-3.8, STAMP_AR, 2.9, 700, 'middle', '#b3261e')
    s += t(10, 14, title_en, 4.2, 700) + t(410, 14, title_ar, 4.2, 700, 'end', extra=' direction="rtl"')
    return s
def sheet(n, N, title_en, title_ar, scale, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, N, title_en, title_ar, scale)}{body}</svg>'
AR = ' direction="rtl"'
N = 5; S = .2
# ================= SHEET 1: views =================
ox, oy = 26, 122
def fx(x): return ox + x*S
def fz(z): return oy - z*S
b = t(22, 24, 'FRONT ELEVATION', 2.8, 600) + t(202, 28, 'الواجهة الأمامية', 2.6, 500, 'end', extra=AR)
b += rect(fx(T), fz(PZB), PL*S, PH*S, .4, INK, '#c9c5bb')
b += rect(fx(0), fz(H), T*S, PLATE_H*S, .4, INK, '#8d8a82') + rect(fx(L-T), fz(H), T*S, PLATE_H*S, .4, INK, '#8d8a82')
for cx_ in (T/2, L-T/2):
    b += f'<circle cx="{fx(cx_):.2f}" cy="{fz(25):.2f}" r="{25*S:.2f}" fill="#555" stroke="{INK}" stroke-width=".3"/>' + rect(fx(cx_)-1.2, fz(CASTER_H), 2.4, (CASTER_H-50)*S, .3, INK, '#bbb')
b += dim_h(fx(0), fx(L), fz(0)+9, f'{L}', ext=fz(0)) + t(fx(L/2), fz(0)+14, 'OVERALL LENGTH / الطول الكلي', 2, 400, 'middle', DIM)
b += dim_v(fx(0)-8, fz(H), fz(0), f'{H}', ext=fx(0))
b += dim_v(fx(L)+8, fz(H), fz(CASTER_H), f'{PLATE_H}', ext=fx(L)) + dim_v(fx(L)+8, fz(CASTER_H), fz(0), f'{CASTER_H}', ext=fx(L))
b += dim_v(fx(L)+16, fz(PZB), fz(PZA), f'{PH}', ext=fx(L-T)) if False else ''
b += t(fx(L/2), fz(PZB)+PH*S/2+1, 'front panel (flat)', 2.2, 400, 'middle', '#555') + t(fx(L/2), fz(PZB)+PH*S/2+4.5, 'اللوح الأمامي (مسطح)', 2.2, 400, 'middle', '#555', extra=AR)
b += balloon(fx(L/2), fz(PZB)-5, 2) + balloon(fx(0)-3, fz(300), 1) + balloon(fx(0)+12, fz(10), 4)
# side elevation
ox_s = 250
def sx(y): return ox_s + y*S
b += t(ox_s-2, 24, 'SIDE ELEVATION (end plate)', 2.8, 600) + t(ox_s+70, 28, 'منظر جانبي (لوح الطرف)', 2.6, 500, 'end', extra=AR)
pp = plate_pts(); b += poly([(sx(x), fz(Z0P+y)) for x, y in pp], .45, INK, '#c9c5bb')
for yy_ in CY:
    b += f'<circle cx="{sx(yy_):.2f}" cy="{fz(25):.2f}" r="{25*S:.2f}" fill="#555" stroke="{INK}" stroke-width=".3"/>' + rect(sx(yy_)-2, fz(CASTER_H), 4, (CASTER_H-50)*S, .3, INK, '#bbb')
b += line(sx(T), fz(PZB), sx(W-T), fz(PZB), .15, HID, '1.2 .8') + line(sx(T), fz(PZA), sx(W-T), fz(PZA), .15, HID, '1.2 .8')
b += dim_h(sx(0), sx(W), fz(0)+9, f'{W}', ext=fz(0)) + t(sx(W/2), fz(0)+14, 'OVERALL DEPTH / العمق الكلي', 2, 400, 'middle', DIM)
b += dim_v(sx(0)-6, fz(H), fz(Z0P), f'{PLATE_H}', ext=sx(0)) + dim_v(sx(W)+6, fz(PZB), fz(PZA), f'{PH}', ext=sx(W))
b += dim_v(sx(W)+14, fz(H), fz(PZB), f'{PLATE_H-(PZB-Z0P)}', ext=sx(W)) if False else ''
b += t(sx(W/2), fz(PZA)-PH*S/2, 'panels and floor behind', 2, 400, 'middle', HID) + t(sx(W/2), fz(PZA)-PH*S/2+3, 'اللوحان والقاع خلفه', 2, 400, 'middle', HID, extra=AR)
b += t(sx(R/2), fz(H)+3, f'R{R}', 2.2, 500, 'middle', DIM)
# plan
oxp, oyp = 26, 152
def px(x): return oxp + x*S
def py(y): return oyp + y*S
b += t(22, 148, 'PLAN', 2.8, 600) + t(202, 148, 'المسقط الأفقي', 2.6, 500, 'end', extra=AR)
b += rect(px(0), py(0), L*S, W*S, .45, INK, '#e7e3da') + rect(px(T), py(T), FL*S, FW*S, .2, HID, 'none', '1 .7')
b += rect(px(0), py(0), T*S, W*S, .3, INK, '#8d8a82') + rect(px(L-T), py(0), T*S, W*S, .3, INK, '#8d8a82')
for cx_ in (T/2, L-T/2):
    for yy_ in CY: b += f'<circle cx="{px(cx_):.2f}" cy="{py(yy_):.2f}" r="{25*S:.2f}" fill="none" stroke="{HID}" stroke-width=".2" stroke-dasharray="1 .7"/>'
b += dim_h(px(0), px(L), py(W)+7, f'{L}', ext=py(W)) + dim_v(px(0)-6, py(0), py(W), f'{W}', ext=px(0))
b += t(px(L/2), py(W/2)+1, f'inner clear {FL} x {FW}', 2.2, 400, 'middle', '#555') + t(px(L/2), py(W/2)+4.5, 'المقاس الداخلي الصافي', 2.2, 400, 'middle', '#555', extra=AR)
b += t(px(L)+1.5, py(CY[0])+1, '', 2)
# reference photo
b += t(235, 142, 'REFERENCE PHOTO (not ours; low-resolution render, source unknown)', 2.3, 600) + t(410, 146, 'صورة مرجعية (ليست لنا، المصدر مجهول)', 2.3, 500, 'end', extra=AR)
b += f'<image href="{datauri(PHOTO)}" x="235" y="150" width="100" height="70.4" preserveAspectRatio="xMidYMid slice"/>' + rect(235, 150, 100, 70.4, .2, HID)
b += t(340, 156, 'Shape estimated by eye from the', 2.0, 400, fill=HID) + t(340, 159, 'photo, approximate. The photo shows', 2.0, 400, fill=HID) + t(340, 162, 'black and sage; the sage is not in the', 2.0, 400, fill=HID) + t(340, 165, 'objekt palette and is not used.', 2.0, 400, fill=HID)
# colourways
cy0 = 232
b += t(22, cy0-6, 'COLOURWAYS (Sabry, 12 Nov; names from the objekt colour guide)', 2.5, 600) + t(215, cy0-2.5, 'الألوان', 2.4, 500, 'end', extra=AR)
for i, (nm, hx, ar) in enumerate(COLS):
    yy = cy0 + i*9
    b += rect(22, yy-3.5, 12, 6, .25, INK, hx) + t(38, yy, f'{nm}  {hx}', 2.4, 600) + t(38, yy+3, f'Electrostatic powder coating · {nm} · Matte', 2.1, 400, fill=HID) + t(215, yy+1.5, ar, 2.3, 400, 'end', extra=AR)
b += t(22, 262, 'Matte powder coat: Sabry. Powder maker matches HEX with a sample; confirm against a physical sample. Paint codes to follow.', 1.9, 400, fill=HID)
b += t(22, 284, 'Overall 900 x 300 x 450 mm incl. casters is a PROPOSAL (not costed, Production to confirm). Caster height 70 mm is assumed.  المقاسات مقترحة، وارتفاع العجلة ٧٠ مم افتراضي.', 2.0, 400, fill=HID)
b += t(22, 287.5, 'Steel height 380 + casters 70 = 450. Panel top where the end-plate corner radius starts.  ارتفاع الصاج ٣٨٠ + العجلات ٧٠ = ٤٥٠.', 2.0, 400, fill=HID)
sh1 = sheet(1, N, 'VIEWS', 'المناظير', '1:5', b)

# ================= SHEET 2: flat patterns =================
S2 = .25
b = t(10, 22, 'Flat patterns at 1:4. All parts are flat sheet; edge folds, if any, are Production\'s.', 2.3, 400, fill=HID) + t(410, 22, 'الأنماط المسطحة بمقياس ١:٤. أي ثنيات للحواف يقررها التصنيع.', 2.3, 400, 'end', HID)
x1, y1 = 34, 40
b += rect(x1, y1, PL*S2, PH*S2, .4, INK, FILL) + dim_h(x1, x1+PL*S2, y1+PH*S2+6, f'{PL}', ext=y1+PH*S2) + dim_v(x1-5, y1, y1+PH*S2, f'{PH}', ext=x1)
b += t(x1, y1-2, '2  FRONT / BACK PANEL, 2 off', 2.4, 600) + t(x1+PL*S2, y1-2, 'اللوح الأمامي والخلفي، عدد ٢', 2.4, 600, 'end', extra=AR) + balloon(x1-12, y1+PH*S2/2, 2)
x2, y2 = 34, 112
b += rect(x2, y2, FL*S2, FW*S2, .4, INK, FILL) + dim_h(x2, x2+FL*S2, y2+FW*S2+6, f'{FL}', ext=y2+FW*S2) + dim_v(x2-5, y2, y2+FW*S2, f'{FW}', ext=x2)
b += t(x2, y2-2, '3  FLOOR PLATE, 1 off', 2.4, 600) + t(x2+FL*S2, y2-2, 'لوح القاع، عدد ١', 2.4, 600, 'end', extra=AR) + balloon(x2-12, y2+FW*S2/2, 3)
x3, y3 = 300, 40
b += poly([(x3+x*S2, y3+(PLATE_H-y)*S2) for x, y in plate_pts()], .4, INK, FILL)
b += dim_h(x3, x3+W*S2, y3+PLATE_H*S2+6, f'{W}', ext=y3+PLATE_H*S2) + dim_v(x3-5, y3, y3+PLATE_H*S2, f'{PLATE_H}', ext=x3)
b += dim_h(x3+R*S2, x3+(W-R)*S2, y3-4, f'{W-2*R}', ext=y3) + t(x3+(W+4)*S2, y3+R*S2*.5, f'R{R}', 2.3, 500, fill=DIM)
b += t(x3-10, y3-8, '1  END PLATE, 2 off (same part, not handed)', 2.4, 600) + t(x3+W*S2+25, y3-4.5, 'لوح الطرف، عدد ٢', 2.4, 600, 'end', extra=AR) + balloon(x3-12, y3+PLATE_H*S2/2, 1)
dx, dy = 22, 205
b += t(dx, dy, 'DATA  mm', 2.4, 600) + t(224, dy, 'بيانات', 2.4, 600, 'end', extra=AR)
rows = [('Part', 'Qty', 'Size', 'Outline length each')]
rows += [('1 End plate', '2', f'{W} x {PLATE_H}, top corners R{R}', f'{plate_perim():.0f}'), ('2 Panel', '2', f'{PL} x {PH}', f'{2*(PL+PH):.0f}'), ('3 Floor plate', '1', f'{FL} x {FW}', f'{2*(FL+FW):.0f}')]
for i, r_ in enumerate(rows):
    yy = dy+5+i*4.2
    for xx, v in zip((dx, dx+34, dx+46, dx+120), r_): b += t(xx, yy, v, 2.1, 600 if i == 0 else 400)
for i, ln in enumerate([f'Panels sit between the end plates: {L} - 2 x {T} = {PL}. Floor: {W} - 2 x {T} = {FW} wide.',
                        'Panel bottom is 110 above the plate bottom, top 320 (where the corner radius starts). Floor sits at the panel bottom.',
                        'Sheet thickness 2 mm is a proposal. Bend allowance, joints, weld method and seam sealing: Production.',
                        'Caster fixing to the plate bottom edge (flange or bracket) is not drawn: Production to decide.']):
    b += t(dx, dy+22+i*3.8, ln, 2.0)
b += t(410, dy+22, 'سماكة الصاج ٢ مم مقترحة. اللحام وتثبيت العجلات من التصنيع.', 2.0, 400, 'end', extra=AR)
sh2 = sheet(2, N, 'PART SHEET', 'ورقة القطع', '1:4', b)

# ================= SHEET 3: assembly =================
SC = .15; KK = .5; AA = math.radians(35)
def P(x, y, z): return 40 + (x + KK*y*math.cos(AA))*SC, 200 - (z + KK*y*math.sin(AA))*SC
def pl(pts3, fill, sw=.35): return poly([P(*q) for q in pts3], sw, INK, fill)
b = t(10, 22, 'EXPLODED VIEW (proposed assembly; Production decides jigs, welds and fixings)', 2.5, 600) + t(410, 22, 'منظر مفكك (تجميع مقترح، والتصنيع يقرر القوالب واللحام)', 2.5, 600, 'end', extra=AR)
EX = 90; EY = 80
yb = W-T+EY
b += pl([(T, yb, PZA), (L-T, yb, PZA), (L-T, yb, PZB), (T, yb, PZB)], '#c9c5bb')                               # back panel
b += pl([(T, 0, PZA-60), (L-T, 0, PZA-60), (L-T, W, PZA-60), (T, W, PZA-60)], '#e2ded4')                       # floor, lowered
for xp in (-EX, L-T+EX):
    b += pl([(xp, y, Z0P+z) for y, z in plate_pts()], '#a9a69d')
    for yy_ in CY:
        b += pl([(xp, yy_-3, Z0P-35), (xp, yy_+3, Z0P-35), (xp, yy_+3, Z0P-5), (xp, yy_-3, Z0P-5)], '#bbb', .25)
        cx_, cz_ = P(xp, yy_, 12); b += f'<circle cx="{cx_:.2f}" cy="{cz_:.2f}" r="{25*SC:.2f}" fill="#555" stroke="{INK}" stroke-width=".3"/>'
b += pl([(T, -EY, PZA), (L-T, -EY, PZA), (L-T, -EY, PZB), (T, -EY, PZB)], '#c9c5bb')                           # front panel
for (xa, ya, za, xb_, yb_, zb_) in [(T, -EY, PZA, T, 0, PZA), (L-T, -EY, PZA, L-T, 0, PZA), (T, 0, PZA-60, T, 0, PZA), (-EX, W/2, Z0P+150, 0, W/2, Z0P+150), (L-T+EX, W/2, Z0P+150, L-T, W/2, Z0P+150)]:
    (ax, ay), (bx, by) = P(xa, ya, za), P(xb_, yb_, zb_); b += line(ax, ay, bx, by, .2, HID, '1 1')
ax, ay = P(L/2, -EY, PZB); b += balloon(ax, ay-5, 2)
ax, ay = P(-EX, W/2, Z0P+PLATE_H); b += balloon(ax-4, ay-4, 1)
ax, ay = P(L/2, W/2, PZA-60); b += balloon(ax, ay+6, 3)
ax, ay = P(-EX, CY[0], 0); b += balloon(ax-8, ay+2, 4)
b += t(22, 262, 'Casters (4): bought-in, swivel, rubber wheel, 50 mm; two locking (proposal). Load rating: Production to decide with the supplier.', 2.0, 400, fill=HID)
b += t(22, 266, 'Inner liner (5): loose, drops into the trough; not drawn, size and material by Production.', 2.0, 400, fill=HID)
b += t(224, 270, 'العجلات: جاهزة، دوارة، مطاط ٥٠ مم، اثنتان بقفل (مقترح). السعة من التصنيع.', 2.0, 400, 'end', HID, extra=AR)
sx0 = 245
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end', extra=AR)
steps = [('Cut parts 1, 2, 3 from the DXF files; deburr the edges.', 'قص القطع ١ و٢ و٣ من ملفات DXF وتنعيم الحواف.'),
         ('Weld the floor plate (3) and the two panels (2) between the two end plates (1); seal the trough seams.', 'لحام لوح القاع (٣) واللوحين (٢) بين لوحي الطرف (١) وإحكام سد الوصلات.'),
         ('Grind welds flush. Powder coat, matte, in the chosen colour.', 'صنفرة اللحام ثم الدهان بالبودرة المطفي باللون المختار.'),
         ('Fit the four rubber swivel casters (4) under the end plates; two with locks.', 'تركيب العجلات الأربع (٤) تحت لوحي الطرف، اثنتان بقفل.'),
         ('Drop the loose inner liner (5) into the trough.', 'وضع البطانة الداخلية (٥) داخل الحوض.')]
for i, (en, ar) in enumerate(steps):
    yy = 48 + i*17
    b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 2.2) + t(410, yy+5, ar, 2.2, 400, 'end', extra=AR)
sh3 = sheet(3, N, 'ASSEMBLY', 'التجميع', 'n/a', b)

# ================= SHEET 4: cutting layout =================
S4 = .1
b = t(10, 22, f'CUTTING LAYOUT on an assumed sheet {SHEET_L} x {SHEET_W} x {T} (proposal, to be confirmed by Production).', 2.4, 600) + t(410, 22, 'مخطط القص على لوح مفترض، يؤكده التصنيع', 2.4, 600, 'end', extra=AR)
ox4, oy4 = 30, 40
b += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6') + t(ox4, oy4-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for k, x, y in NEST:
    kind, (w, h) = PARTS[k][3], PARTS[k][4]
    if kind == 'rect': b += rect(ox4+x*S4, oy4+y*S4, w*S4, h*S4, .3, INK, FILL)
    else: b += poly([(ox4+(x+px_)*S4, oy4+(y+PLATE_H-py_)*S4) for px_, py_ in plate_pts()], .3, INK, FILL)
    b += t(ox4+(x+w/2)*S4, oy4+(y+h/2)*S4+1, k[1], 3.4, 600, 'middle', '#555')
b += dim_h(ox4, ox4+SHEET_L*S4, oy4+SHEET_W*S4+7, f'{SHEET_L}', ext=oy4+SHEET_W*S4) + dim_v(ox4-6, oy4, oy4+SHEET_W*S4, f'{SHEET_W}', ext=ox4)
b += t(30, 195, f'Parts nested with {GAP} mm spacing, in one corner of the sheet: about {USED_X:.0f} x {USED_Y:.0f} mm used. No offcut is claimed.', 2.3)
b += t(30, 200, f'Total cutting length of all parts: {TOTAL_CUT/1000:.2f} m ({TOTAL_CUT:.0f} mm), outlines only.', 2.5, 600)
b += t(410, 195, 'الأجزاء مرتبة بمسافة ١٠ مم. لا يُدّعى أي هالك.', 2.3, 400, 'end', extra=AR) + t(410, 200, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.5, 600, 'end', extra=AR)
sh4 = sheet(4, N, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)

# ================= SHEET 5: BOM and notes =================
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + t(410, 28, 'قائمة المواد', 2.8, 600, 'end', extra=AR)
b += rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'End plate', 'لوح الطرف', '2', 'Sheet steel 2 mm (proposal)'), ('2', 'Front / back panel', 'اللوح الأمامي والخلفي', '2', 'Sheet steel 2 mm (proposal)'), ('3', 'Floor plate', 'لوح القاع', '1', 'Sheet steel 2 mm (proposal)'),
       ('4', 'Swivel caster, rubber wheel 50 mm', 'عجلة دوارة مطاط ٥٠ مم', '4 (2 locking)', 'Bought-in; load rating by Production'), ('5', 'Inner liner, loose', 'بطانة داخلية', '1', 'By Production; not drawn')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*7
    b += line(10, yy+2.2, 410, yy+2.2, .15, HID) + t(12, yy, n_, 2.4) + t(24, yy, en, 2.4) + t(140, yy, ar, 2.4, 400, 'end', extra=AR) + t(150, yy, q, 2.4) + t(215, yy, m_, 2.4)
b += t(10, 90, 'NOTES', 2.8, 600) + t(410, 90, 'ملاحظات', 2.8, 600, 'end', extra=AR)
notes = [('Overall 900 x 300 x 450 mm (including casters), sheet thickness 2 mm and the caster height of 70 mm are proposals, not costed. Production to confirm.', 'المقاسات وسماكة الصاج وارتفاع العجلة مقترحة. يؤكدها التصنيع.'),
         ('The shape is estimated by eye from one low-resolution render of unknown source (not ours): two end plates with rounded top corners, flat front and back panels, floor, four casters. Drawn as objekt\'s own design.', 'الشكل مقدّر من صورة واحدة منخفضة الدقة مجهولة المصدر، ومرسوم كتصميم خاص بأوبجيكت.'),
         ('Colours (Sabry): Carbon, Oxblood, Bone. Finish (Sabry): electrostatic powder coating, matte. Powder maker matches the HEX with a sample.', 'الألوان: أسود فحمي، عنابي داكن، عاجي. التشطيب: دهان بودرة مطفي.'),
         ('Drainage (proposal, same call as OBJ-173 and OBJ-075): the steel trough is sealed with no drain hole, so the floor stays dry on casters; plants sit in a loose inner liner (5) that drains. Production to confirm seam sealing and liner.', 'الصرف (مقترح): الحوض مغلق بدون فتحات، والنباتات في بطانة داخلية قابلة للصرف.'),
         ('Casters (Sabry: rubber): four swivel casters, rubber wheel, 50 mm, two with locks (proposal). Type, mounting to the plate bottom and load rating are Production\'s to decide.', 'العجلات مطاط (سبري): أربع عجلات دوارة ٥٠ مم، اثنتان بقفل (مقترح).'),
         ('Material, thickness, bend allowance, tolerances, sheet size, joints, welding and finish details are Production\'s to decide.', 'الخامة والسماكة والسماحيات واللحام وتفاصيل التشطيب يقررها التصنيع.'),
         ('No structural claims, stress figures, load figures, costs or prices on this drawing. Not engineered. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا تكاليف ولا أسعار. الصياغة العربية مسودة.'),
         ('Product number OBJ-192 was the next free number; Sabry can override.', 'رقم المنتج التالي المتاح؛ يمكن لسبري تغييره.')]
for i, (en, ar) in enumerate(notes):
    yy = 99 + i*13
    b += t(12, yy, f'{i+1}.', 2.4, 600) + t(18, yy, en, 2.2) + t(410, yy+5, ar, 2.2, 400, 'end', extra=AR)
sh5 = sheet(5, N, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)

for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1):
    open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('outlines (mm):', {k: round(v[5]) for k, v in PARTS.items()}, 'total', round(TOTAL_CUT), 'nest', MSG, 'used', USED_X, USED_Y)
