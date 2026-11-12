"""OBJ-193: low coffee table, thick rounded-rectangle top on four fat cylindrical legs. Production drawing set, REV 0 (DRAFT).
Run: python3 make_obj193_rev0.py <repo root>   Then make_pdf.js for the PDF.
ALL sizes, thicknesses, the construction and the finish are PROPOSALS (not costed, Production to confirm), set by the product brief on 12 Nov 2026.
Shape is estimated by eye from one render of unknown source (reference only, drawn as objekt's own design). The lamp in the photo is not part of the product.
Arabic wording is a draft and needs a technical reader. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-193'; os.makedirs(OUT, exist_ok=True)
PHOTO = ROOT + '/images/OBJ-193.jpg'
REV = 0; DATE = '12 Nov 2026'; PN = 'OBJ-193'
L, W, H = 1100, 800, 350          # overall, proposal
T, T3 = 2, 3                      # sheet thickness: shells and top, caps and mount plates (proposal)
R = 120                           # top corner radius (proposal)
SLAB = 110; SKIRT_H = 100; REV_H = 10; REV_IN = 6        # slab thickness, upper skirt, reveal band height, reveal set-back
LEG_D, LEG_H, PAD = 250, 240, 10                          # leg diameter, leg height incl. levelling pad, pad height (nominal)
SHELL_H = LEG_H - PAD                                      # 230 rolled shell
INSET = 120                                                # leg surface set in from the slab edge
LX = [INSET + LEG_D/2, L - INSET - LEG_D/2]                # leg centres along length: 245, 855
LY = [INSET + LEG_D/2, W - INSET - LEG_D/2]                # along depth: 245, 555
CAP_D = LEG_D - 2*T                                        # 246
PCD = 140; HOLE = 9; BOLT = 'M8'
ZS0 = LEG_H; ZS1 = H                                       # slab 240 to 350
BUL = math.tan(math.radians(90)/4)
def perim_rr(w, h, r): return 2*(w-2*r) + 2*(h-2*r) + 2*math.pi*r
P1W, P1H = L, W
P3W, P3H, R3 = L-2*REV_IN, W-2*REV_IN, R-REV_IN
P2L = perim_rr(L, W, R)/2; P4L = perim_rr(P3W, P3H, R3)/2
P5L = math.pi*(LEG_D-T)
MP = 160
def holes_bolt(): return [(PCD/2*math.cos(math.radians(a)), PCD/2*math.sin(math.radians(a))) for a in (45, 135, 225, 315)]
def holes_bot(): return [(100*math.cos(math.radians(a)), 100*math.sin(math.radians(a))) for a in (90, 210, 330)]
# key: (EN, AR, qty, kind, (w, h) bounding box, thickness, outline length each incl. holes)
PARTS = {'P1': ('Top plate', 'لوح السطح', 1, 'rr', (P1W, P1H), T, perim_rr(P1W, P1H, R)),
         'P2': ('Skirt band (half)', 'شريط الإطار (نصف)', 2, 'rect', (round(P2L), SKIRT_H), T, 2*(round(P2L)+SKIRT_H)),
         'P3': ('Base plate', 'لوح القاعدة', 1, 'rr3', (P3W, P3H), T, perim_rr(P3W, P3H, R3) + 16*math.pi*HOLE),
         'P4': ('Reveal band (half)', 'شريط الفاصل (نصف)', 2, 'rect', (round(P4L), REV_H), T, 2*(round(P4L)+REV_H)),
         'P5': ('Leg shell (rolled)', 'جسم الرجل (مدرفل)', 4, 'rect', (round(P5L), SHELL_H), T, 2*(round(P5L)+SHELL_H)),
         'P6': ('Leg top cap', 'غطاء الرجل العلوي', 4, 'capt', (CAP_D, CAP_D), T3, math.pi*CAP_D + 4*math.pi*HOLE),
         'P7': ('Leg bottom cap (removable)', 'غطاء الرجل السفلي (قابل للفك)', 4, 'capb', (CAP_D, CAP_D), T3, math.pi*CAP_D + math.pi*11 + 3*math.pi*5.5),
         'P8': ('Slab mount plate', 'لوح تثبيت الرجل', 4, 'mp', (MP, MP), T3, 4*MP + 4*math.pi*HOLE)}
TOTAL_CUT = sum(v[2]*v[6] for v in PARTS.values())
SHEET_L, SHEET_W, GAP = 2500, 1250, 10
# nesting: sheet name -> thickness, list of (part, x, y)
NESTS = {'A': (2, [('P1', GAP, GAP), ('P3', GAP+L+GAP, GAP), ('P2', GAP, GAP+W+GAP), ('P2', GAP, GAP+W+GAP+SKIRT_H+GAP),
                   ('P4', GAP, GAP+W+GAP+2*(SKIRT_H+GAP)), ('P4', GAP, GAP+W+GAP+2*(SKIRT_H+GAP)+REV_H+GAP)]),
         'B': (2, [('P5', GAP, GAP+i*(SHELL_H+GAP)) for i in range(4)]),
         'C': (3, [('P6', GAP+i*(CAP_D+GAP), GAP) for i in range(4)] + [('P7', GAP+i*(CAP_D+GAP), GAP+CAP_D+GAP) for i in range(4)]
                  + [('P8', GAP+i*(MP+GAP), GAP+2*(CAP_D+GAP)) for i in range(4)])}
def size(k): return PARTS[k][4]
def nest_ok(items):
    r = [(k, x, y, x+size(k)[0], y+size(k)[1]) for k, x, y in items]
    for k, x0, y0, x1, y1 in r:
        if x0 < 0 or y0 < 0 or x1 > SHEET_L or y1 > SHEET_W: return False, f'{k} outside sheet'
    for i in range(len(r)):
        for j in range(i+1, len(r)):
            a, b = r[i], r[j]
            if not (a[3]+GAP-1e-6 <= b[1] or b[3]+GAP-1e-6 <= a[1] or a[4]+GAP-1e-6 <= b[2] or b[4]+GAP-1e-6 <= a[2]): return False, f'{a[0]} / {b[0]} spacing'
    return True, 'ok'
for nm, (th, items) in NESTS.items():
    ok, msg = nest_ok(items); assert ok, (nm, msg)
# every part quantity must be nested exactly
for k, v in PARTS.items():
    n = sum(1 for _, (_, it) in NESTS.items() for kk, _, _ in it if kk == k); assert n == v[2], (k, n, v[2])
# weight of the steel parts, 7.85 g/cm3, flat areas (corner losses included), before stiffeners, fixings, filler and paint
def rr_area(w, h, r): return w*h - (4-math.pi)*r*r
A2 = rr_area(P1W, P1H, R) + rr_area(P3W, P3H, R3) + 2*round(P2L)*SKIRT_H + 2*round(P4L)*REV_H + 4*round(P5L)*SHELL_H
A3 = 8*math.pi*(CAP_D/2)**2 + 4*MP*MP
KG = (A2*T + A3*T3)*7.85e-6
KG_SLAB = (rr_area(P1W, P1H, R)*T + rr_area(P3W, P3H, R3)*T + 2*round(P2L)*SKIRT_H*T + 2*round(P4L)*REV_H*T + 4*MP*MP*T3)*7.85e-6
KG_LEGS = KG - KG_SLAB
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); d.layers.add('SHEET', color=3); return d
def add_part(msp, key, ox, oy):
    kind, (w, h) = PARTS[key][3], PARTS[key][4]
    A = {'layer': 'CUT'}
    def rr(wd, ht, r):
        pts = [(r, 0, 0), (wd-r, 0, BUL), (wd, r, 0), (wd, ht-r, BUL), (wd-r, ht, 0), (r, ht, BUL), (0, ht-r, 0), (0, r, BUL)]
        msp.add_lwpolyline([(ox+x, oy+y, 0, 0, b) for x, y, b in pts], format='xyseb', close=True, dxfattribs=A)
    if kind in ('rect', 'mp'):
        msp.add_lwpolyline([(ox, oy), (ox+w, oy), (ox+w, oy+h), (ox, oy+h)], close=True, dxfattribs=A)
    elif kind == 'rr': rr(P1W, P1H, R)
    elif kind == 'rr3':
        rr(P3W, P3H, R3)
        for lx in LX:
            for ly in LY:
                for hx, hy in holes_bolt(): msp.add_circle((ox+lx-REV_IN+hx, oy+ly-REV_IN+hy), HOLE/2, dxfattribs=A)
    if kind in ('capt', 'capb'): msp.add_circle((ox+w/2, oy+h/2), CAP_D/2, dxfattribs=A)
    cx, cy = ox+w/2, oy+h/2
    if kind in ('capt', 'mp'):
        for hx, hy in holes_bolt(): msp.add_circle((cx+hx, cy+hy), HOLE/2, dxfattribs=A)
    if kind == 'capb':
        msp.add_circle((cx, cy), 5.5, dxfattribs=A)
        for hx, hy in holes_bot(): msp.add_circle((cx+hx, cy+hy), 2.75, dxfattribs=A)
FN = {'P1': 'top-plate', 'P2': 'skirt-band', 'P3': 'base-plate', 'P4': 'reveal-band', 'P5': 'leg-shell', 'P6': 'leg-top-cap', 'P7': 'leg-bottom-cap', 'P8': 'mount-plate'}
for k in PARTS:
    doc = new_doc(); add_part(doc.modelspace(), k, 0, 0); doc.saveas(f'{OUT}/{PN}_rev{REV}_{k}_{FN[k]}.dxf')
for nm, (th, items) in NESTS.items():
    doc = new_doc(); m = doc.modelspace()
    m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
    for k, x, y in items: add_part(m, k, x, y)
    doc.saveas(f'{OUT}/{PN}_rev{REV}_nest{nm}_{th}mm_{SHEET_L}x{SHEET_W}.dxf')

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
COLS = [('Oxblood', '#5A1F25', 'عنابي داكن', 'proposed, nearest palette colour to the photo'), ('Chocolate', '#4A2A1B', 'بني شوكولاتة', 'alternative, colour still unconfirmed')]
def frame(n, N, title_en, title_ar, scale):
    s = rect(5, 5, 410, 287, .5) + rect(7, 7, 406, 283, .2)
    X, Y, Wd = 228, 247, 185
    s += rect(X, Y, Wd, 41, .4, fill='#fff')
    s += line(X, Y+9, X+Wd, Y+9, .25) + line(X, Y+20, X+Wd, Y+20, .25) + line(X, Y+31, X+Wd, Y+31, .25) + line(X+92, Y+9, X+92, Y+41, .25)
    s += bi(X+2, Y+4, f'{PN}   Low coffee table, four cylinder legs', 'طاولة قهوة منخفضة بأربع أرجل أسطوانية', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  {L} x {W} x {H} mm (proposal)', 'المقاس الكلي (مقترح)', 88, 2.1) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, 'MATERIAL  Sheet steel 2 and 3 mm (proposal)', 'الخامة: صاج ٢ و٣ مم (مقترح)', 88, 2.1) + bi(X+94, Y+25, 'FINISH  Duco, gloss (proposal, to confirm)', 'التشطيب: دوكو لامع (مقترح)', 88, 2.1)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, '#b3261e', '#fff')
    s += t(X+Wd/2, Y-8.6, STAMP, 2.9, 700, 'middle', '#b3261e') + t(X+Wd/2, Y-3.8, STAMP_AR, 2.9, 700, 'middle', '#b3261e')
    s += t(10, 14, title_en, 4.2, 700) + t(410, 14, title_ar, 4.2, 700, 'end', extra=' direction="rtl"')
    return s
def sheet(n, N, title_en, title_ar, scale, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, N, title_en, title_ar, scale)}{body}</svg>'
AR = ' direction="rtl"'
N = 5; S = .13
def rr_pts(w, h, r, ox=0, oy=0, n=10):
    p = []
    for cx, cy, a0 in ((w-r, r, -90), (w-r, h-r, 0), (r, h-r, 90), (r, r, 180)):
        for i in range(n+1):
            a = math.radians(a0 + 90*i/n); p.append((ox+cx+r*math.cos(a), oy+cy+r*math.sin(a)))
    return p
def ell_pts(cx, cy, rad, n=28): return [(cx+rad*math.cos(2*math.pi*i/n), cy+rad*math.sin(2*math.pi*i/n)) for i in range(n)]
# ================= SHEET 1: views =================
ox, oy = 26, 80
def fx(x): return ox + x*S
def fz(z): return oy - z*S
b = t(22, 24, 'FRONT ELEVATION', 2.8, 600) + t(202, 28, 'الواجهة الأمامية', 2.6, 500, 'end', extra=AR)
for cx_ in LX:
    b += rect(fx(cx_-LEG_D/2), fz(LEG_H), LEG_D*S, SHELL_H*S, .4, INK, '#9a7f86') + rect(fx(cx_-30), fz(PAD), 60*S, PAD*S, .3, INK, '#555')
b += rect(fx(REV_IN), fz(ZS0+REV_H), (L-2*REV_IN)*S, REV_H*S, .35, INK, '#6f4a52') + rect(fx(0), fz(H), L*S, SKIRT_H*S, .45, INK, '#b58f98')
b += dim_h(fx(0), fx(L), fz(0)+12, f'{L}', ext=fz(0)) + t(fx(L/2), fz(0)+17, 'OVERALL LENGTH / الطول الكلي', 2, 400, 'middle', DIM)
b += dim_h(fx(LX[0]-LEG_D/2), fx(LX[0]+LEG_D/2), fz(0)+5, f'Ø{LEG_D}', ext=fz(0))
b += dim_h(fx(0), fx(INSET), fz(H)-4, f'{INSET}', ext=fz(H))
b += dim_v(fx(0)-8, fz(H), fz(0), f'{H}', ext=fx(0))
b += dim_v(fx(L)+8, fz(H), fz(ZS0), f'{SLAB}', ext=fx(L)) + dim_v(fx(L)+8, fz(ZS0), fz(0), f'{LEG_H}', ext=fx(L))
b += t(fx(L/2), fz(H)+SKIRT_H*S/2+1, 'skirt, 100 high (upper box)', 2.1, 400, 'middle', '#fff') 
b += t(fx(L/2), fz(ZS0+REV_H)-.4+REV_H*S+2.8, '', 2)
b += t(fx(L/2)+0, fz(ZS0)+3.6+REV_H*S-5.4, '', 2)
b += t(fx(400), fz(ZS0)+4.2, 'reveal band, 10 high, set back 6 (shadow line)', 1.9, 400, fill=DIM)
b += balloon(fx(L/2), fz(H)-5, 2) + balloon(fx(LX[0]), fz(120), 5) + balloon(fx(LX[1])+3, fz(PAD/2)+0.6, 9)
b += t(fx(LX[1]+LEG_D/2)+2, fz(130), 'back legs hidden,', 1.9, 400, fill=HID) + t(fx(LX[1]+LEG_D/2)+2, fz(130)+2.6, 'same positions', 1.9, 400, fill=HID)
# side elevation
ox_s = 235
def sx(y): return ox_s + y*S
b += t(ox_s-2, 24, 'SIDE ELEVATION', 2.8, 600) + t(ox_s+112, 28, 'منظر جانبي', 2.6, 500, 'end', extra=AR)
for cy_ in LY:
    b += rect(sx(cy_-LEG_D/2), fz(LEG_H), LEG_D*S, SHELL_H*S, .4, INK, '#9a7f86') + rect(sx(cy_-30), fz(PAD), 60*S, PAD*S, .3, INK, '#555')
b += rect(sx(REV_IN), fz(ZS0+REV_H), (W-2*REV_IN)*S, REV_H*S, .35, INK, '#6f4a52') + rect(sx(0), fz(H), W*S, SKIRT_H*S, .45, INK, '#b58f98')
b += dim_h(sx(0), sx(W), fz(0)+12, f'{W}', ext=fz(0)) + t(sx(W/2), fz(0)+17, 'OVERALL DEPTH / العمق الكلي', 2, 400, 'middle', DIM)
b += dim_h(sx(LY[0]+LEG_D/2), sx(LY[1]-LEG_D/2), fz(0)+5, f'{LY[1]-LY[0]-LEG_D:.0f}', ext=fz(0)) 
b += dim_v(sx(W)+7, fz(H), fz(ZS0), f'{SLAB}', ext=sx(W))
# plan
oxp, oyp = 26, 106
def px(x): return oxp + x*S
def py(y): return oyp + y*S
b += t(22, 100, 'PLAN', 2.8, 600) + t(202, 100, 'المسقط الأفقي', 2.6, 500, 'end', extra=AR)
b += poly([(px(x), py(y)) for x, y in rr_pts(L, W, R)], .45, INK, '#e7dde0')
b += poly([(px(REV_IN+x), py(REV_IN+y)) for x, y in rr_pts(P3W, P3H, R3)], .2, HID, 'none', '1 .7')
for cx_ in LX:
    for cy_ in LY: b += f'<circle cx="{px(cx_):.2f}" cy="{py(cy_):.2f}" r="{LEG_D/2*S:.2f}" fill="none" stroke="{HID}" stroke-width=".25" stroke-dasharray="1.2 .8"/>' + line(px(cx_)-1.5, py(cy_), px(cx_)+1.5, py(cy_), .15, HID) + line(px(cx_), py(cy_)-1.5, px(cx_), py(cy_)+1.5, .15, HID)
b += dim_h(px(0), px(L), py(W)+7, f'{L}', ext=py(W)) + dim_v(px(0)-6, py(0), py(W), f'{W}', ext=px(0))
b += dim_h(px(LX[0]), px(LX[1]), py(0)-3.5, f'{LX[1]-LX[0]:.0f}', ext=py(LY[0])) + dim_v(px(L)+6, py(LY[0]), py(LY[1]), f'{LY[1]-LY[0]:.0f}', ext=px(LX[1]))
b += t(px(LX[0]+LEG_D/2)+1, py(LY[0])-LEG_D/2*S-1, f'R{R}', 2.2, 500, fill=DIM) if False else ''
b += t(px(L/2), py(W/2)+1, 'legs shown dashed (below the top)', 2.1, 400, 'middle', '#555') + t(px(L/2), py(W/2)+4.2, 'الأرجل بخط متقطع (أسفل السطح)', 2.1, 400, 'middle', '#555', extra=AR)
b += t(px(L)+10, py(60)+1, f'corner R{R}', 2.2, 500, fill=DIM) + t(px(L)+10, py(60)+4, f'legs set in {INSET} from the edges', 2.0, 400, fill=DIM)
# reference photo
b += t(235, 108, 'REFERENCE PHOTO (not ours; render, source unknown)', 2.3, 600) + t(410, 112, 'صورة مرجعية (ليست لنا، المصدر مجهول)', 2.3, 500, 'end', extra=AR)
b += f'<image href="{datauri(PHOTO)}" x="235" y="116" width="100" height="72.4" preserveAspectRatio="xMidYMid slice"/>' + rect(235, 116, 100, 72.4, .2, HID)
for i, ln in enumerate(['Shape estimated by eye from the', 'photo, approximate. The lamp with the', 'marble base is NOT part of the', 'product and is not drawn.']): b += t(340, 122+i*3.2, ln, 2.0, 400, fill=HID)
b += t(410, 140, 'المصباح في الصورة ليس جزءاً من المنتج.', 2.0, 400, 'end', HID, extra=AR)
cy0 = 232
b += t(22, cy0-6, 'COLOURWAYS (names from the objekt colour guide; proposal, Sabry to approve)', 2.5, 600) + t(215, cy0-2.5, 'الألوان', 2.4, 500, 'end', extra=AR)
for i, (nm, hx, ar, why) in enumerate(COLS):
    yy = cy0 + i*9
    b += rect(22, yy-3.5, 12, 6, .25, INK, hx) + t(38, yy, f'{nm}  {hx}  ({why})', 2.4, 600) + t(38, yy+3, f'Duco · {nm} · Gloss', 2.1, 400, fill=HID) + t(215, yy+1.5, ar, 2.3, 400, 'end', extra=AR)
b += t(22, 253, 'Paint system and gloss to be confirmed; paint codes to follow. Duco can be tinted in the workshop; confirm against a physical sample.', 1.9, 400, fill=HID)
b += t(22, 281, f'All sizes, thicknesses and the construction are PROPOSALS (not costed, Production to confirm). Shape estimated from a render.  المقاسات والسماكات والتصنيع مقترحة.', 2.0, 400, fill=HID)
b += t(22, 285, f'Leg height 240 includes a 10 mm levelling pad (adjustable). Slab 110 = skirt 100 + reveal band 10.  ارتفاع الرجل ٢٤٠ شاملاً قاعدة الضبط.', 2.0, 400, fill=HID)
sh1 = sheet(1, N, 'VIEWS', 'المناظير', '1:7.7', b)

# ================= SHEET 2: flat patterns =================
b = t(10, 22, 'Flat patterns. Big plates and shell at 1:10, caps and mount plate at 1:5. Thickness: 2 mm (1 to 5), 3 mm (6 to 8). All proposals.', 2.2, 400, fill=HID) + t(410, 22, 'الأنماط المسطحة. السماكات مقترحة ويقررها التصنيع.', 2.2, 400, 'end', HID)
S2 = .1
x1, y1 = 34, 40
b += poly([(x1+x*S2, y1+(P1H-y)*S2) for x, y in rr_pts(P1W, P1H, R)], .4, INK, FILL) + dim_h(x1, x1+P1W*S2, y1+P1H*S2+6, f'{P1W}', ext=y1+P1H*S2) + dim_v(x1-5, y1, y1+P1H*S2, f'{P1H}', ext=x1)
b += t(x1+R*S2*0.5, y1+P1H*S2+11, f'corner R{R}', 2.1, 500, fill=DIM) + t(x1, y1-2, '1  TOP PLATE, 1 off', 2.4, 600) + t(x1+P1W*S2, y1-2, 'لوح السطح، عدد ١', 2.4, 600, 'end', extra=AR) + balloon(x1-12, y1+P1H*S2/2, 1)
x3 = 160
b += poly([(x3+x*S2, y1+(P3H-y)*S2) for x, y in rr_pts(P3W, P3H, R3)], .4, INK, FILL) + dim_h(x3, x3+P3W*S2, y1+P3H*S2+6, f'{P3W}', ext=y1+P3H*S2) + dim_v(x3-5, y1, y1+P3H*S2, f'{P3H}', ext=x3)
for lx in LX:
    for ly in LY:
        for hx, hy in holes_bolt(): b += f'<circle cx="{x3+(lx-REV_IN+hx)*S2:.2f}" cy="{y1+(P3H-(ly-REV_IN+hy))*S2:.2f}" r="{HOLE/2*S2+.35:.2f}" fill="#fff" stroke="{INK}" stroke-width=".2"/>'
b += t(x3, y1-2, '3  BASE PLATE, 1 off, 16 holes Ø9', 2.4, 600) + t(x3+P3W*S2, y1-2, 'لوح القاعدة، عدد ١', 2.4, 600, 'end', extra=AR) + balloon(x3-12, y1+P3H*S2/2, 3)
y2 = 138
b += rect(x1, y2, round(P2L)*S2, SKIRT_H*S2, .4, INK, FILL) + dim_h(x1, x1+round(P2L)*S2, y2+SKIRT_H*S2+6, f'{round(P2L)}', ext=y2+SKIRT_H*S2) + dim_v(x1-5, y2, y2+SKIRT_H*S2, f'{SKIRT_H}', ext=x1)
b += t(x1, y2-2, '2  SKIRT BAND, 2 off (halves; rolled to the corner radii)', 2.4, 600) + t(x1+round(P2L)*S2, y2-2, 'شريط الإطار، عدد ٢', 2.4, 600, 'end', extra=AR) + balloon(x1-12, y2+SKIRT_H*S2/2, 2)
y4 = 164
b += rect(x1, y4, round(P4L)*S2, REV_H*S2, .4, INK, FILL) + dim_h(x1, x1+round(P4L)*S2, y4+REV_H*S2+6, f'{round(P4L)}', ext=y4+REV_H*S2) + t(x1+round(P4L)*S2+3, y4+REV_H*S2, f'{REV_H}', 2.2, 500, fill=DIM)
b += t(x1, y4-2, '4  REVEAL BAND, 2 off (halves, 10 wide strip)', 2.4, 600) + t(x1+round(P4L)*S2, y4-2, 'شريط الفاصل، عدد ٢', 2.4, 600, 'end', extra=AR) + balloon(x1-12, y4+REV_H*S2/2, 4)
x5, y5 = 290, 40
b += rect(x5, y5, round(P5L)*S2, SHELL_H*S2, .4, INK, FILL) + dim_h(x5, x5+round(P5L)*S2, y5+SHELL_H*S2+6, f'{round(P5L)}', ext=y5+SHELL_H*S2) + dim_v(x5-5, y5, y5+SHELL_H*S2, f'{SHELL_H}', ext=x5)
b += t(x5, y5-2, '5  LEG SHELL, 4 off', 2.4, 600) + t(x5+round(P5L)*S2, y5-2, 'جسم الرجل، عدد ٤', 2.4, 600, 'end', extra=AR) + balloon(x5-12, y5+SHELL_H*S2/2, 5)
b += t(x5, y5+SHELL_H*S2+11, f'Rolled to Ø{LEG_D}, one seam. Length = π x ({LEG_D} - {T}) = {P5L:.0f}.', 2.0)
S4_ = .2
x6, y6 = 285, 90
b += f'<circle cx="{x6+CAP_D*S4_/2:.2f}" cy="{y6+CAP_D*S4_/2:.2f}" r="{CAP_D*S4_/2:.2f}" fill="{FILL}" stroke="{INK}" stroke-width=".4"/>'
for hx, hy in holes_bolt(): b += f'<circle cx="{x6+CAP_D*S4_/2+hx*S4_:.2f}" cy="{y6+CAP_D*S4_/2-hy*S4_:.2f}" r="{HOLE/2*S4_+.4:.2f}" fill="#fff" stroke="{INK}" stroke-width=".25"/>'
b += dim_h(x6, x6+CAP_D*S4_, y6+CAP_D*S4_+6, f'Ø{CAP_D}', ext=y6+CAP_D*S4_) + t(x6, y6-2, '6  LEG TOP CAP, 4 off', 2.4, 600) + balloon(x6-5, y6+CAP_D*S4_/2, 6)
b += t(x6, y6+CAP_D*S4_+11, f'4 holes Ø{HOLE} on PCD {PCD}, at 45°', 2.0)
x7 = 345
b += f'<circle cx="{x7+CAP_D*S4_/2:.2f}" cy="{y6+CAP_D*S4_/2:.2f}" r="{CAP_D*S4_/2:.2f}" fill="{FILL}" stroke="{INK}" stroke-width=".4"/>' + f'<circle cx="{x7+CAP_D*S4_/2:.2f}" cy="{y6+CAP_D*S4_/2:.2f}" r="{5.5*S4_+.3:.2f}" fill="#fff" stroke="{INK}" stroke-width=".25"/>'
for hx, hy in holes_bot(): b += f'<circle cx="{x7+CAP_D*S4_/2+hx*S4_:.2f}" cy="{y6+CAP_D*S4_/2-hy*S4_:.2f}" r="{2.75*S4_+.25:.2f}" fill="#fff" stroke="{INK}" stroke-width=".25"/>'
b += dim_h(x7, x7+CAP_D*S4_, y6+CAP_D*S4_+6, f'Ø{CAP_D}', ext=y6+CAP_D*S4_) + t(x7, y6-2, '7  BOTTOM CAP, 4 off', 2.4, 600) + balloon(x7-5, y6+CAP_D*S4_/2, 7)
b += t(x7, y6+CAP_D*S4_+11, 'centre Ø11 (M10 weld nut), 3 x Ø5.5 on PCD 200', 2.0)
x8 = 285; y8 = 158
b += rect(x8, y8, MP*S4_, MP*S4_, .4, INK, FILL)
for hx, hy in holes_bolt(): b += f'<circle cx="{x8+MP*S4_/2+hx*S4_:.2f}" cy="{y8+MP*S4_/2-hy*S4_:.2f}" r="{HOLE/2*S4_+.4:.2f}" fill="#fff" stroke="{INK}" stroke-width=".25"/>'
b += dim_h(x8, x8+MP*S4_, y8+MP*S4_+6, f'{MP}', ext=y8+MP*S4_) + t(x8, y8-2, '8  MOUNT PLATE, 4 off', 2.4, 600) + balloon(x8-5, y8+MP*S4_/2, 8)
b += t(x8, y8+MP*S4_+11, f'4 x Ø{HOLE}, PCD {PCD}', 2.0)
dx, dy = 22, 178
b += t(dx, dy, 'DATA  mm', 2.4, 600) + t(224, dy, 'بيانات', 2.4, 600, 'end', extra=AR)
rows = [('Part', 'Qty', 'Thk', 'Size', 'Cut length each')]
for k, v in PARTS.items():
    sz = f'{v[4][0]} x {v[4][1]}' if v[3] not in ('capt', 'capb') else f'Ø{CAP_D}'
    rows.append((f'{k[1]}  {v[0]}', str(v[2]), str(v[5]), sz, f'{v[6]:.0f}'))
for i, r_ in enumerate(rows):
    yy = dy+5+i*3.9
    for xx, v in zip((dx, dx+56, dx+68, dx+80, dx+112), r_): b += t(xx, yy, v, 2.0, 600 if i == 0 else 400)
for i, ln in enumerate([f'Total cutting length of all parts: {TOTAL_CUT/1000:.1f} m (outlines and holes). Reveal band is a thin strip; Production may fold a lip instead.',
                        f'Skirt and reveal bands: half-length each ({round(P2L)} and {round(P4L)}), joined at the straight sides. Developed lengths are approximate; bend allowance is Production\'s.',
                        'Base plate holes: 4 per leg on PCD 140 at each leg centre (16 in all). Mount plate (8) welded on the inside, M8 weld nuts over the holes.',
                        'Thickness 2 / 3 mm, joints, stiffening inside the box and corner forming are Production\'s to decide.']):
    b += t(dx, dy+5+len(rows)*3.9+4+i*3.6, ln, 1.9)
b += t(410, dy+4, 'سماكة الصاج ٢ و٣ مم مقترحة. التقوية الداخلية واللحام من التصنيع.', 2.0, 400, 'end', extra=AR)
sh2 = sheet(2, N, 'PART SHEET', 'ورقة القطع', '1:10 / 1:5', b)

# ================= SHEET 3: assembly =================
SC = .13; KK = .5; AA = math.radians(35)
def P(x, y, z): return 30 + (x + KK*y*math.cos(AA))*SC, 200 - (z + KK*y*math.sin(AA))*SC
def hull(pts):
    pts = sorted(set(pts))
    def cr(o, a, b_): return (a[0]-o[0])*(b_[1]-o[1]) - (a[1]-o[1])*(b_[0]-o[0])
    lo = []
    for q in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0: lo.pop()
        lo.append(q)
    up = []
    for q in reversed(pts):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0: up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]
def solid(outline_xy, z0, z1, fill, sw=.35):
    """prism of a convex outline: hull of bottom and top outlines, then the top face on top"""
    allp = [P(x, y, z0) for x, y in outline_xy] + [P(x, y, z1) for x, y in outline_xy]
    return poly(hull(allp), sw, INK, fill) + poly([P(x, y, z1) for x, y in outline_xy], .25, INK, fill if fill == 'none' else '#d8d4cb')
LIFT = 120
b = t(10, 22, 'EXPLODED VIEW (proposed assembly; Production decides jigs, welds and fixings)', 2.5, 600) + t(410, 22, 'منظر مفكك (تجميع مقترح، والتصنيع يقرر القوالب واللحام)', 2.5, 600, 'end', extra=AR)
def leg(cx_, cy_):
    s = solid(ell_pts(cx_, cy_, LEG_D/2), PAD, LEG_H, '#9a7f86')
    s += solid(ell_pts(cx_, cy_, CAP_D/2), -45, -42, '#bbb', .25)
    s += solid(ell_pts(cx_, cy_, 30), -78, -68, '#666', .25)
    return s
for cy_ in (LY[1], LY[0]):
    if cy_ == LY[1]:
        for cx_ in LX: b += leg(cx_, cy_)
b += solid(rr_pts(L, W, R, 0, 0), ZS0+LIFT, ZS1+LIFT, '#b58f98')
for cx_ in LX: b += leg(cx_, LY[0])
for cx_ in LX:
    for cy_ in LY:
        for hx, hy in holes_bolt()[:1]:
            (ax, ay), (bx, by) = P(cx_+hx, cy_+hy, LEG_H), P(cx_+hx, cy_+hy, ZS0+LIFT); b += line(ax, ay, bx, by, .2, HID, '1 1')
ax, ay = P(L/2, 0, ZS1+LIFT); b += balloon(ax, ay-5, 2)
ax, ay = P(LX[0], LY[0]-LEG_D/2, 120); b += balloon(ax-LEG_D/2*SC-6, ay, 5)
ax, ay = P(LX[1], LY[0], -45); b += balloon(ax+LEG_D/2*SC+4, ay, 7)
ax, ay = P(LX[1], LY[0], -73); b += balloon(ax+10, ay+2, 9)
b += t(22, 226, 'Items 1 to 4: the slab is a box, top plate and skirt above, base plate and reveal band below. Mount plates (8) are welded inside it.', 1.9, 400, fill=HID)
b += t(22, 230, 'Item 5 shell, 6 top cap (welded in), 7 bottom cap (removable, three M5 screws), 9 levelling pad. Bolts (10) go up from inside the leg.', 1.9, 400, fill=HID)
b += t(22, 234, 'Bought-in: levelling pads, M8 bolts and washers, M8 weld nuts, M5 screws. Sizes proposed; Production chooses types.', 1.9, 400, fill=HID)
b += t(224, 240, 'المشتريات: قواعد الضبط، براغي M8، صواميل لحام، براغي M5. الأنواع يحددها التصنيع.', 1.9, 400, 'end', HID, extra=AR)
sx0 = 245
b += t(sx0, 36, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 36, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end', extra=AR)
steps = [('Cut parts 1 to 8 from the DXF files; roll the leg shells and the bands; deburr.', 'قص القطع ١ إلى ٨، ثم لف الأجسام والأشرطة وتنعيم الحواف.'),
         ('Weld each leg: shell, top cap, mount plate parts; weld the slab box; grind welds and fill.', 'لحام الأرجل وصندوق السطح وصنفرة اللحام والمعجون.'),
         ('Duco gloss in the chosen colour on the slab and the legs, separately.', 'دهان الدوكو اللامع على السطح والأرجل كل على حدة.'),
         ('Fit the levelling pads (9) and the bottom caps (7) loose; ship in two parts.', 'تركيب قواعد الضبط والأغطية السفلية، والشحن على جزأين.'),
         ('Remove a bottom cap, bolt the leg up into the slab with four M8 (10), refit the cap.', 'فك الغطاء السفلي وتثبيت الرجل بأربعة براغي M8 ثم إعادة الغطاء.'),
         ('Stand the table on the floor and level it with the four pads.', 'وضع الطاولة على الأرض وضبط الاستواء.')]
for i, (en, ar) in enumerate(steps):
    yy = 44 + i*10.5
    b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 2.0) + t(410, yy+4, ar, 2.0, 400, 'end', extra=AR)
# section through a leg
SC2 = .36; cxs = 327; z0y = 224
def zs(z): return z0y - z*SC2
b += t(sx0, 114, 'SECTION THROUGH A LEG (schematic, wall thicknesses exaggerated)', 2.2, 600) + t(410, 118, 'مقطع في الرجل (تخطيطي، السماكات مبالغ فيها)', 2.1, 500, 'end', extra=AR)
b += rect(cxs-LEG_D*SC2/2, zs(LEG_H), 1.3, SHELL_H*SC2, .3, INK, '#9a7f86') + rect(cxs+LEG_D*SC2/2-1.3, zs(LEG_H), 1.3, SHELL_H*SC2, .3, INK, '#9a7f86')          # shell walls
b += rect(cxs-CAP_D*SC2/2, zs(LEG_H)+0.0, CAP_D*SC2, 1.8, .3, INK, '#666')                                                                                           # top cap
b += rect(cxs-CAP_D*SC2/2, zs(PAD+3), CAP_D*SC2, 1.8, .3, INK, '#666', '1 .6')                                                                                       # bottom cap
b += rect(cxs-30*SC2, zs(PAD), 60*SC2, PAD*SC2, .3, INK, '#555')                                                                                                     # pad
b += rect(cxs-LEG_D*SC2/2-6, zs(ZS0)-1.3, LEG_D*SC2+12, 1.3, .3, INK, '#b58f98')                                                                                     # base plate
b += rect(cxs-MP*SC2/2, zs(ZS0)-1.3-1.8, MP*SC2, 1.8, .3, INK, '#888')                                                                                               # mount plate
for sgn in (-1, 1):
    bx_ = cxs + sgn*PCD/2*0.7071*SC2*0+sgn*PCD/2*SC2*0.7071
    b += line(bx_, zs(PAD+14), bx_, zs(ZS0)-5, .5, DIM) + rect(bx_-1.6, zs(ZS0)-1.3-1.8-2.2, 3.2, 2.2, .25, DIM, '#fff')
b += line(cxs-LEG_D*SC2/2-6, zs(ZS0)-1.3-1.8, cxs+LEG_D*SC2/2+6, zs(ZS0)-1.3-1.8, .12, HID, '1 1')
def lead(x, y, tx, ty, n, lab): return line(x, y, tx, ty, .15, HID) + balloon(tx, ty, n) + t(tx+5 if tx > x else tx-5, ty+1, lab, 1.9, 400, 'start' if tx > x else 'end', INK)
b += lead(cxs+LEG_D*SC2/2+4, zs(ZS0)-.6, cxs+LEG_D*SC2/2+14, zs(ZS0)-8, 3, 'base plate')
b += lead(cxs+MP*SC2/2, zs(ZS0)-2.5, cxs+LEG_D*SC2/2+14, zs(ZS0)-15, 8, 'mount plate')
b += lead(cxs+LEG_D*SC2/2-.6, zs(120), cxs+LEG_D*SC2/2+14, zs(150), 5, 'leg shell')
b += lead(cxs+LEG_D*SC2/2-4, zs(LEG_H)+1.2, cxs+LEG_D*SC2/2+14, zs(215), 6, 'top cap')
b += lead(cxs-LEG_D*SC2/2+8, zs(PAD+3)+.9, cxs-LEG_D*SC2/2-14, zs(75), 7, 'bottom cap')
b += lead(cxs-20, zs(PAD/2), cxs-LEG_D*SC2/2-14, zs(30), 9, 'pad')
b += lead(cxs-PCD*SC2/2*0.7071, zs(150), cxs-LEG_D*SC2/2-14, zs(190), 10, 'M8 bolt')
b += t(sx0, 232, 'Fixing detail is a proposal; Production decides.', 1.9, 400, fill=HID) if False else ''
sh3 = sheet(3, N, 'ASSEMBLY', 'التجميع', 'n/a', b)

# ================= SHEET 4: cutting layouts =================
S4 = .05
b = t(10, 22, f'CUTTING LAYOUTS on three assumed sheets {SHEET_L} x {SHEET_W} (proposal, to be confirmed by Production). All parts nested; spacing {GAP} mm.', 2.3, 600) + t(410, 22, 'مخططات القص على ثلاثة ألواح مفترضة، يؤكدها التصنيع', 2.3, 600, 'end', extra=AR)
def shape_svg(k, x, y, ox4, oy4):
    kind, (w, h) = PARTS[k][3], PARTS[k][4]
    if kind in ('rect', 'mp'): return rect(ox4+x*S4, oy4+y*S4, w*S4, h*S4, .3, INK, FILL)
    if kind in ('rr', 'rr3'): return poly([(ox4+(x+px_)*S4, oy4+(y+h-py_)*S4) for px_, py_ in rr_pts(w, h, R if kind == 'rr' else R3)], .3, INK, FILL)
    return f'<circle cx="{ox4+(x+w/2)*S4:.2f}" cy="{oy4+(y+h/2)*S4:.2f}" r="{w/2*S4:.2f}" fill="{FILL}" stroke="{INK}" stroke-width=".3"/>'
cut_by = {}
for si, (nm, (th, items)) in enumerate(NESTS.items()):
    ox4, oy4 = 30, 34 + si*72
    b += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6') + t(ox4, oy4-2, f'SHEET {nm}: {SHEET_L} x {SHEET_W} x {th} mm', 2.2, 600, fill='#2f6b45')
    for k, x, y in items:
        b += shape_svg(k, x, y, ox4, oy4)
        kind, (w, h) = PARTS[k][3], PARTS[k][4]
        b += t(ox4+(x+w/2)*S4, oy4+(y+h/2)*S4+(1.2 if h*S4 > 4 else -1), k[1], 2.6 if h*S4 > 4 else 1.8, 600, 'middle', '#555')
    cl = sum(PARTS[k][6] for k, _, _ in items); cut_by[nm] = cl
    ux = max(x+size(k)[0] for k, x, y in items); uy = max(y+size(k)[1] for k, x, y in items)
    b += t(165, oy4+8, f'Sheet {nm} ({th} mm): {len(items)} parts, about {ux:.0f} x {uy:.0f} mm used.', 2.3)
    b += t(165, oy4+13, f'Cutting length on this sheet: {cl/1000:.1f} m (outlines and holes).', 2.3, 600)
    b += t(410, oy4+12, f'لوح {nm}: طول القص {cl/1000:.1f} متر', 2.3, 600, 'end', extra=AR)
b += t(165, 78, 'A: top plate, base plate, 2 skirt halves, 2 reveal halves.   B: 4 leg shells.   C: 4 top caps, 4 bottom caps, 4 mount plates (3 mm).', 2.0, 400, fill=HID)
b += t(165, 160, 'Parts are laid out in one corner of each sheet; no offcut is claimed. Sheet A needs the full length (the two big plates side by side).', 2.0, 400, fill=HID)
b += t(165, 232, f'Total cutting length of all parts: {TOTAL_CUT/1000:.1f} m.   إجمالي طول القص: {TOTAL_CUT/1000:.1f} متر', 2.6, 600)
sh4 = sheet(4, N, 'CUTTING LAYOUT', 'مخطط القص', '1:20', b)

# ================= SHEET 5: BOM and notes =================
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + t(410, 28, 'قائمة المواد', 2.8, 600, 'end', extra=AR)
b += rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [(str(i+1), PARTS[f'P{i+1}'][0], PARTS[f'P{i+1}'][1], str(PARTS[f'P{i+1}'][2]), f'Sheet steel {PARTS[f"P{i+1}"][5]} mm (proposal)') for i in range(8)]
bom += [('9', 'Levelling pad, M10, Ø60, adjustable', 'قاعدة ضبط M10', '4', 'Bought-in; nominal 10 mm high (proposal)'), ('10', 'M8 bolt and washer', 'برغي M8 وحلقة', '16', 'Bought-in'),
        ('11', 'M8 weld nut', 'صامولة لحام M8', '16', 'Bought-in'), ('12', 'M5 screw with captive nut or tab', 'برغي M5', '12', 'Bought-in; fixing by Production')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*6
    b += line(10, yy+2.0, 410, yy+2.0, .15, HID) + t(12, yy, n_, 2.3) + t(24, yy, en, 2.3) + t(140, yy, ar, 2.3, 400, 'end', extra=AR) + t(150, yy, q, 2.3) + t(215, yy, m_, 2.3)
b += t(10, 120, 'NOTES', 2.8, 600) + t(410, 120, 'ملاحظات', 2.8, 600, 'end', extra=AR)
notes = [(f'Overall {L} x {W} x {H} mm, sheet thicknesses 2 and 3 mm, corner radius {R} mm, leg Ø{LEG_D} x {LEG_H} mm (incl. 10 mm pad) set in {INSET} mm, and the whole construction are proposals, not costed. Production to confirm.', 'المقاسات والسماكات والتصنيع مقترحة وغير مُسعّرة. يؤكدها التصنيع.'),
         ('The shape is estimated by eye from one render of unknown source (not ours): a thick rounded-rectangle top with a visible reveal line under it, on four fat cylindrical legs. Drawn as objekt\'s own design. The lamp in the photo is not part of the product.', 'الشكل مقدّر من صورة واحدة مجهولة المصدر ومرسوم كتصميم خاص بأوبجيكت. المصباح ليس جزءاً من المنتج.'),
         (f'Colour and finish (proposal): Duco · Oxblood #5A1F25 · Gloss; Chocolate #4A2A1B is the alternative (colour unconfirmed). Paint system and gloss to be confirmed; codes to follow.', 'اللون والتشطيب (مقترح): دوكو، عنابي داكن، لامع. البديل بني شوكولاتة.'),
         ('Gloss Duco on a large welded steel top shows every weld mark, dent and wave. Production to decide plate thickness (2 mm is a guess; 3 mm may be needed for the top plate), inside stiffening, filler and the number of sanding and coating coats. Painter capacity is not known to us.', 'اللامع يُظهر كل لحام وانبعاج. سماكة السطح والتقوية والمعجون وعدد الطبقات يقررها التصنيع. سعة الدهان غير معروفة لنا.'),
         (f'Weight, calculated from the proposed sizes (not weighed): about {KG:.0f} kg of steel parts (slab {KG_SLAB:.0f} kg, four legs {KG_LEGS:.0f} kg) before inside stiffening, fixings, filler and paint. Ships in two parts: slab {L} x {W} x {SLAB}, and legs bolted up from inside.', f'الوزن محسوب من المقاسات المقترحة (غير موزون): حوالي {KG:.0f} كجم صلب قبل التقوية والتثبيت والدهان.'),
         ('The slab is a closed box. Reveal: the lower 10 mm band is set back 6 mm under the skirt, giving the shadow line. Bolts go up from inside each leg (bottom cap removable) into M8 weld nuts on the mount plates. The fixing and access method are proposals.', 'السطح صندوق مغلق. خط الفاصل بتراجع ٦ مم. التثبيت بالبراغي من داخل الرجل مقترح.'),
         ('Front-to-back, the clear gap between the legs is only 60 mm with these sizes (800 - 2 x 120 - 2 x 250). The photo may show a wider gap: Sabry to check the proportion on the render.', 'المسافة بين الأرجل من الأمام للخلف ٦٠ مم فقط بهذه المقاسات. سبري يراجع النسبة.'),
         ('Material, thickness, bend allowance, tolerances, sheet size, joints, welding and finish details are Production\'s to decide.', 'الخامة والسماكة والسماحيات واللحام وتفاصيل التشطيب يقررها التصنيع.'),
         ('No structural claims, stress figures, load figures, costs or prices on this drawing. Not engineered. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا تكاليف ولا أسعار. الصياغة العربية مسودة.'),
         ('Product number OBJ-193 was the next free number; Sabry can override.', 'رقم المنتج التالي المتاح؛ يمكن لسبري تغييره.')]
import textwrap
yy = 128
for i, (en, ar) in enumerate(notes):
    lines = textwrap.wrap(en, 150)
    b += t(12, yy, f'{i+1}.', 2.2, 600)
    for j, ln in enumerate(lines): b += t(18, yy+j*3.4, ln, 2.0)
    b += t(410, yy, ar, 2.0, 400, 'end', extra=AR)
    yy += max(len(lines)*3.4, 3.4) + 3.6
assert yy < 232, yy
sh5 = sheet(5, N, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)

for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1):
    open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('cut length per part (mm):', {k: round(v[6]) for k, v in PARTS.items()}, 'total', round(TOTAL_CUT))
print('weight kg', round(KG, 1), 'slab', round(KG_SLAB, 1), 'legs', round(KG_LEGS, 1), 'cut per sheet', {k: round(v) for k, v in cut_by.items()}, 'end y notes', round(yy))
