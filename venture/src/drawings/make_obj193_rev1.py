"""OBJ-193: low coffee table, thick rounded-rectangle top on four fat cylindrical legs. Production drawing set, REV 1 (DRAFT), MOULDED GRP.
Rev 0 (welded steel) is in superseded-rev0: Sabry thought the table is not metal (12 Nov), so it is redrawn as moulded GRP, painted Duco gloss.
Run: python3 make_obj193_rev1.py <repo root>   Then make_pdf.js for the PDF.
ALL sizes, wall thickness, split lines, construction and finish are PROPOSALS (not costed, Production to confirm). Shape estimated by eye from one render of
unknown source (reference only, drawn as objekt's own design). The lamp in the photo is not part of the product. Moulded product: no flat patterns, no cutting layout;
DXF files are plan outlines and profiles (leg and cap half-profiles: x = radius, y = height). Arabic wording is a draft and needs a technical reader. No costs, no structural claims."""
import sys, os, math, base64, io, textwrap
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-193'; os.makedirs(OUT, exist_ok=True)
PHOTO = ROOT + '/images/OBJ-193.jpg'
REV = 1; DATE = '12 Nov 2026'; PN = 'OBJ-193'
L, W, H = 1100, 800, 350
WALL = 4                          # GRP laminate wall, proposal
R = 175                  # corner radius = leg radius: the legs sit flush at the corners, concentric with the arcs (Sabry, 12 Nov)
SLAB = 110; SKIRT_H = 100; REV_H = 10; REV_IN = 6
LEG_D, LEG_H, PAD = 350, 240, 10
SHELL_H = LEG_H - PAD
INSET = 0                                                   # leg surface flush with the slab edge
LX = [INSET + LEG_D/2, L - INSET - LEG_D/2]
LY = [INSET + LEG_D/2, W - INSET - LEG_D/2]
CAP_D = LEG_D - 2*WALL; CAP_T = 6                          # bottom cap, 6 mm GRP disc
PCD = 190; HOLE = 9; MP = 220                              # bolt circle, bolt hole, bonded pad 160 x 160
ZS0 = LEG_H; ZS1 = H
P3W, P3H, R3 = L-2*REV_IN, W-2*REV_IN, R-REV_IN
def holes_bolt(): return [(PCD/2*math.cos(math.radians(a)), PCD/2*math.sin(math.radians(a))) for a in (45, 135, 225, 315)]
def perim_rr(w, h, r): return 2*(w-2*r) + 2*(h-2*r) + 2*math.pi*r
def rr_area(w, h, r): return w*h - (4-math.pi)*r*r
DENS = 1.6e-6                                              # kg/mm3, 1.6 g/cm3 laminate, ASSUMED
A_UP = rr_area(L, W, R) + perim_rr(L, W, R)*SKIRT_H
A_LO = rr_area(P3W, P3H, R3) + perim_rr(P3W, P3H, R3)*REV_H
A_LEG = 4*(math.pi*(LEG_D/2)**2 + math.pi*LEG_D*SHELL_H)
A_CAP = 4*math.pi*(CAP_D/2)**2
KG_SLAB = (A_UP + A_LO)*WALL*DENS; KG_LEGS = (A_LEG*WALL + A_CAP*CAP_T)*DENS; KG = KG_SLAB + KG_LEGS
BUL = math.tan(math.radians(90)/4)
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); return d
def rr_poly(msp, wd, ht, r, ox=0, oy=0):
    pts = [(r, 0, 0), (wd-r, 0, BUL), (wd, r, 0), (wd, ht-r, BUL), (wd-r, ht, 0), (r, ht, BUL), (0, ht-r, 0), (0, r, BUL)]
    msp.add_lwpolyline([(ox+x, oy+y, 0, 0, b) for x, y, b in pts], format='xyseb', close=True, dxfattribs={'layer': 'CUT'})
def poly_dxf(msp, pts): msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'CUT'})
# profiles. slab edge section: x inward from the outer edge of the skirt, y up from the underside
UPPER = [(0, REV_H), (0, SLAB), (120, SLAB), (120, SLAB-WALL), (WALL, SLAB-WALL), (WALL, REV_H)]
LOWER = [(REV_IN, 0), (REV_IN, REV_H), (REV_IN+WALL, REV_H), (REV_IN+WALL, WALL), (120, WALL), (120, 0)]
LEGP = [(LEG_D/2-WALL, 0), (LEG_D/2, 0), (LEG_D/2, SHELL_H), (0, SHELL_H), (0, SHELL_H-WALL), (LEG_D/2-WALL, SHELL_H-WALL)]
CAPP = [(0, 0), (CAP_D/2, 0), (CAP_D/2, CAP_T), (0, CAP_T)]
FILES = {'P1_upper-shell-plan': lambda m: rr_poly(m, L, W, R), 'P2_lower-shell-plan': lambda m: rr_poly(m, P3W, P3H, R3),
         'P1_P2_slab-edge-section': lambda m: (poly_dxf(m, UPPER), poly_dxf(m, LOWER)), 'P3_leg-half-profile': lambda m: poly_dxf(m, LEGP), 'P4_cap-half-profile': lambda m: poly_dxf(m, CAPP)}
for nm, fn in FILES.items():
    d = new_doc(); fn(d.modelspace()); d.saveas(f'{OUT}/{PN}_rev{REV}_{nm}.dxf')
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
    s += bi(X+2, Y+25, 'MATERIAL  Moulded GRP, 4 mm wall (proposal)', 'الخامة: فايبر جلاس مصبوب ٤ مم (مقترح)', 88, 2.1) + bi(X+94, Y+25, 'FINISH  Duco gloss on primer (proposal)', 'التشطيب: دوكو لامع (مقترح)', 88, 2.1)
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
b += dim_v(fx(0)-8, fz(H), fz(0), f'{H}', ext=fx(0))
b += dim_v(fx(L)+8, fz(H), fz(ZS0), f'{SLAB}', ext=fx(L)) + dim_v(fx(L)+8, fz(ZS0), fz(0), f'{LEG_H}', ext=fx(L))
b += t(fx(L/2), fz(H)+SKIRT_H*S/2+1, 'upper shell, skirt 100 high', 2.1, 400, 'middle', '#fff') 
b += t(fx(L/2), fz(ZS0+REV_H)-.4+REV_H*S+2.8, '', 2)
b += t(fx(L/2)+0, fz(ZS0)+3.6+REV_H*S-5.4, '', 2)
b += t(fx(L/2), fz(ZS0)+4.2, 'lower shell, 10 high,', 1.9, 400, 'middle', DIM) + t(fx(L/2), fz(ZS0)+6.8, 'set back 6 (shadow line)', 1.9, 400, 'middle', DIM)
b += balloon(fx(L/2), fz(H)-5, 1) + balloon(fx(LX[0]), fz(120), 3) + balloon(fx(LX[1])+3, fz(PAD/2)+0.6, 6)
b += t(fx(L/2), fz(130), 'back legs hidden,', 1.9, 400, 'middle', HID) + t(fx(L/2), fz(130)+2.6, 'same positions', 1.9, 400, 'middle', HID)
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
b += t(px(L)+10, py(60)+1, f'corner R{R} = leg radius', 2.2, 500, fill=DIM) + t(px(L)+10, py(60)+4, 'legs flush with the edge, concentric', 2.0, 400, fill=DIM) + t(px(L)+10, py(60)+7, 'with the corner arcs', 2.0, 400, fill=DIM)
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
b += t(22, 253, 'Duco gloss over primer on the GRP; paint system and gloss to be confirmed; paint codes to follow. Confirm the colour against a physical sample.', 1.9, 400, fill=HID)
b += t(22, 281, f'All sizes, wall thickness, split lines and construction are PROPOSALS (not costed, Production to confirm). Material: moulded GRP (Sabry, 12 Nov).  المقاسات والتصنيع مقترحة.', 2.0, 400, fill=HID)
b += t(22, 285, f'Leg height 240 includes a 10 mm levelling pad (adjustable). Slab 110 = upper shell 100 + lower shell lip 10.  ارتفاع الرجل ٢٤٠ شاملاً قاعدة الضبط.', 2.0, 400, fill=HID)
sh1 = sheet(1, N, 'VIEWS', 'المناظير', '1:7.7', b)

# ================= SHEET 2: profiles and part outlines =================
b = t(10, 22, 'Part outlines and profiles. Plan outlines 1:10, edge section and cap 1:2, leg half-profile 1:4. Wall 4 mm (cap 6): proposals.', 2.2, 400, fill=HID) + t(410, 22, 'مخططات القطع والمقاطع. السماكات مقترحة ويقررها التصنيع.', 2.2, 400, 'end', HID)
S2 = .1
x1, y1 = 34, 40
b += poly([(x1+x*S2, y1+(W-y)*S2) for x, y in rr_pts(L, W, R)], .4, INK, FILL) + dim_h(x1, x1+L*S2, y1+W*S2+6, f'{L}', ext=y1+W*S2) + dim_v(x1-5, y1, y1+W*S2, f'{W}', ext=x1)
b += t(x1+R*S2*0.5, y1+W*S2+11, f'corner R{R}', 2.1, 500, fill=DIM) + t(x1, y1-2, '1  UPPER SHELL, plan outline, 1 off', 2.4, 600) + t(x1+L*S2, y1-2, 'الغلاف العلوي، عدد ١', 2.4, 600, 'end', extra=AR) + balloon(x1-12, y1+W*S2/2, 1)
x3 = 160
b += poly([(x3+x*S2, y1+(P3H-y)*S2) for x, y in rr_pts(P3W, P3H, R3)], .4, INK, FILL) + dim_h(x3, x3+P3W*S2, y1+P3H*S2+6, f'{P3W}', ext=y1+P3H*S2) + dim_v(x3-5, y1, y1+P3H*S2, f'{P3H}', ext=x3)
for lx in LX:
    for ly in LY:
        for hx, hy in holes_bolt(): b += f'<circle cx="{x3+(lx-REV_IN+hx)*S2:.2f}" cy="{y1+(P3H-(ly-REV_IN+hy))*S2:.2f}" r="{HOLE/2*S2+.35:.2f}" fill="#fff" stroke="{INK}" stroke-width=".2"/>'
b += t(x3, y1-2, '2  LOWER SHELL, plan outline, 1 off', 2.4, 600) + t(x3+P3W*S2, y1-2, 'الغلاف السفلي، عدد ١', 2.4, 600, 'end', extra=AR) + balloon(x3-12, y1+P3H*S2/2, 2)
b += t(x3, y1+P3H*S2+11, f'16 bolt holes Ø{HOLE} (4 per leg, PCD {PCD}), drilled after the pads are bonded. Set-back {REV_IN} from the upper shell.', 1.9)
# edge section 1:2
S5 = .5; xs, ys = 290, 52
def ex(x): return xs + x*S5
def ey(y): return ys + (SLAB-y)*S5
b += t(xs, ys-9, 'SLAB EDGE SECTION, 1:2 (items 1, 2)', 2.4, 600) + t(410, ys-9, 'مقطع حافة السطح', 2.3, 600, 'end', extra=AR)
b += poly([(ex(x), ey(y)) for x, y in UPPER], .4, INK, '#b58f98') + poly([(ex(x), ey(y)) for x, y in LOWER], .4, INK, '#6f4a52')
b += dim_v(ex(0)-5, ey(SLAB), ey(0), f'{SLAB}', ext=ex(0)) + dim_v(ex(0)-11, ey(SLAB), ey(REV_H), f'{SKIRT_H}', ext=ex(0)) + dim_h(ex(0), ex(REV_IN), ey(0)+5, f'{REV_IN}', ext=ey(0))
b += t(ex(0)+34, ey(SLAB)+14, f'wall {WALL}', 2.0, 400, 'middle', DIM) + t(ex(124), ey(REV_H/2)+1, f'lower shell, lip {REV_H}', 2.0, 400, fill=DIM)
b += t(ex(124), ey(SLAB/2+10), 'joint at 10: bonded overlap (not drawn);', 1.9, 400, fill=HID) + t(ex(124), ey(SLAB/2+10)+3, 'upper shell skirt over lower shell lip', 1.9, 400, fill=HID)
# leg half-profile 1:4
S4_ = .25; xl, yl = 295, 128
def lxp(x): return xl + x*S4_
def lyp(y): return yl + (SHELL_H-y)*S4_
b += t(xl, yl-9, '3  LEG CUP, half-profile 1:4, 4 off', 2.4, 600) + t(410, yl-9, 'الرجل، مقطع نصفي، عدد ٤', 2.3, 600, 'end', extra=AR) + balloon(xl-8, yl+SHELL_H*S4_/2, 3)
b += poly([(lxp(x), lyp(y)) for x, y in LEGP], .4, INK, '#9a7f86') + line(lxp(0), lyp(0)-2, lxp(0), lyp(SHELL_H)-2, .15, HID, '3 1 .6 1')
b += dim_v(lxp(LEG_D/2)+5, lyp(SHELL_H), lyp(0), f'{SHELL_H}', ext=lxp(LEG_D/2)) + dim_h(lxp(0), lxp(LEG_D/2), lyp(0)+6, f'R{LEG_D//2}', ext=lyp(0))
b += t(lxp(0)+2, lyp(0)+13, f'wall {WALL}; top closed (integral); DXF x = radius, y = height', 1.9)
xc, yc = 360, 150
b += t(xc, yc-9, '4  BOTTOM CAP', 2.4, 600) + balloon(xc-7, yc+2, 4)
b += poly([(xc+x*.25, yc+(CAP_T-y)*.25) for x, y in CAPP], .4, INK, '#bbb') + dim_h(xc, xc+CAP_D/2*.25, yc+8, f'R{CAP_D//2}', ext=yc+CAP_T*.25) + t(xc, yc+13, f'{CAP_T} thick, 4 off; half-profile 1:4', 1.9)
b += t(xc, yc+17, 'centre insert M10, 3 x M5 fixings', 1.9)
dx, dy = 22, 148
b += t(dx, dy, 'DATA  mm', 2.4, 600) + t(224, dy, 'بيانات', 2.4, 600, 'end', extra=AR)
rows = [('Part', 'Qty', 'Wall', 'Size', 'Method'), ('1 Upper shell', '1', str(WALL), f'{L} x {W}, skirt {SKIRT_H}', 'female mould'), ('2 Lower shell', '1', str(WALL), f'{P3W} x {P3H}, lip {REV_H}', 'female mould'),
        ('3 Leg cup', '4', str(WALL), f'Ø{LEG_D} x {SHELL_H}', 'split mould'), ('4 Bottom cap', '4', str(CAP_T), f'Ø{CAP_D}', 'flat / shallow mould'), ('5 Bonded pad', '4', '6', f'{MP} x {MP}', 'GRP or ply (Production)')]
for i, r_ in enumerate(rows):
    yy = dy+5+i*3.9
    for xx, v in zip((dx, dx+40, dx+52, dx+66, dx+120), r_): b += t(xx, yy, v, 2.0, 600 if i == 0 else 400)
for i, ln in enumerate(['Plan outlines are the visible outlines of the finished shells (DXF: plan outline, layer CUT). Section and half-profile DXFs are profiles, not cut files.',
                        'Wall thickness, lay-up, resin, any core, and the bonded joint and pads are Production\'s. Vertical walls need draft or split moulds: see sheet 4.',
                        'Pads (5) carry the M8 inserts; Production decides pad material, insert type and how far the pads spread the load (no claim made).']):
    b += t(dx, dy+5+len(rows)*3.9+4+i*3.6, ln, 1.9)
sh2 = sheet(2, N, 'PROFILES AND PART OUTLINES', 'المقاطع ومخططات القطع', '1:10 / 1:4 / 1:2', b)
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
b = t(10, 22, 'EXPLODED VIEW (proposed assembly; Production decides moulds, bonding and fixings)', 2.5, 600) + t(410, 22, 'منظر مفكك (تجميع مقترح، والتصنيع يقرر القوالب واللصق والتثبيت)', 2.5, 600, 'end', extra=AR)
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
ax, ay = P(L/2, 0, ZS1+LIFT); b += balloon(ax, ay-5, 1)
ax, ay = P(LX[0], LY[0]-LEG_D/2, 120); b += balloon(ax-LEG_D/2*SC-6, ay, 3)
ax, ay = P(LX[1], LY[0], -45); b += balloon(ax+LEG_D/2*SC+4, ay, 4)
ax, ay = P(LX[1], LY[0], -73); b += balloon(ax+10, ay+2, 6)
b += t(22, 226, 'Items 1, 2: the slab is two moulded shells bonded together; the 6 mm set-back at the joint is the shadow line. Bonded pads (5) sit inside it.', 1.9, 400, fill=HID)
b += t(22, 230, 'Item 3 leg cup (top is part of the moulding), 4 bottom cap (removable, three M5 screws), 6 levelling pad. Bolts (7) go up from inside the leg.', 1.9, 400, fill=HID)
b += t(22, 234, 'Bought-in: levelling pads, M8 bolts and washers, M8 threaded inserts, M5 screws. Sizes proposed; Production chooses types.', 1.9, 400, fill=HID)
b += t(224, 240, 'المشتريات: قواعد الضبط، براغي M8، قطع تسنين، براغي M5. الأنواع يحددها التصنيع.', 1.9, 400, 'end', HID, extra=AR)
sx0 = 245
b += t(sx0, 36, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 36, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end', extra=AR)
steps = [('Make the patterns (3D printed or CNC foam, faired and polished) for the two shells, the leg cup and the cap; make the moulds.', 'عمل النماذج (طباعة ثلاثية الأبعاد أو فوم) ثم القوالب.'),
         ('Gelcoat and laminate the two shells, four leg cups and four caps; demould, trim.', 'طلاء الجل ثم التصفيح للغلافين والأرجل والأغطية، ثم الفك والتشذيب.'),
         ('Bond the pads (5) with M8 inserts into the lower shell; bond the two shells; fair the joint.', 'لصق الألواح بالقطع المسننة في الغلاف السفلي، ثم لصق الغلافين وتسوية الوصلة.'),
         ('Fill, prime, Duco gloss in the chosen colour; polish. Slab and legs separately.', 'معجون وبرايمر ودوكو لامع ثم تلميع، السطح والأرجل كل على حدة.'),
         ('Fit pads (6) and bottom caps (4) loose; ship in two parts. At site: bolt each leg up with four M8 (7).', 'تركيب القواعد والأغطية، والشحن جزأين. في الموقع: تثبيت كل رجل بأربعة براغي M8.'),
         ('Stand the table on the floor and level it with the four pads.', 'وضع الطاولة على الأرض وضبط الاستواء.')]
for i, (en, ar) in enumerate(steps):
    yy = 44 + i*10.5
    b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 2.0) + t(410, yy+4, ar, 2.0, 400, 'end', extra=AR)
# section through a leg
SC2 = .26; cxs = 327; z0y = 224
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
b += lead(cxs+LEG_D*SC2/2+4, zs(ZS0)-.6, cxs+LEG_D*SC2/2+14, zs(ZS0)-8, 2, 'lower shell')
b += lead(cxs+MP*SC2/2, zs(ZS0)-2.5, cxs+LEG_D*SC2/2+14, zs(ZS0)-15, 5, 'bonded pad')
b += lead(cxs+LEG_D*SC2/2-.6, zs(120), cxs+LEG_D*SC2/2+14, zs(150), 3, 'leg cup')
b += lead(cxs+LEG_D*SC2/2-4, zs(LEG_H)+1.2, cxs+LEG_D*SC2/2+14, zs(215), 3, 'leg top')
b += lead(cxs-LEG_D*SC2/2+8, zs(PAD+3)+.9, cxs-LEG_D*SC2/2-14, zs(75), 4, 'bottom cap')
b += lead(cxs-20, zs(PAD/2), cxs-LEG_D*SC2/2-14, zs(30), 6, 'pad')
b += lead(cxs-PCD*SC2/2*0.7071, zs(150), cxs-LEG_D*SC2/2-14, zs(190), 7, 'M8 bolt')
b += t(sx0, 232, 'Fixing detail is a proposal; Production decides.', 1.9, 400, fill=HID) if False else ''
sh3 = sheet(3, N, 'ASSEMBLY', 'التجميع', 'n/a', b)

# ================= SHEET 4: patterns and moulds =================
def mould_cell(x0, y0, title_en, title_ar, cav_depth, note_en, note_ar, flange=50):
    s = t(x0, y0-8, title_en, 2.4, 600) + t(x0+185, y0-8, title_ar, 2.3, 600, 'end', extra=AR)
    cw = 60; bw = flange+cw; bh = cav_depth*.5 + 12
    s += rect(x0, y0, bw, bh, .4, INK, '#cfcac0')
    cy_top = y0 + 12 - 0  # cavity top edge is the mould face
    s += rect(x0+flange, y0, cw, cav_depth*.5, .3, INK, '#fff')
    s += f'<polyline points="{x0+flange:.2f},{y0:.2f} {x0+flange:.2f},{y0+cav_depth*.5:.2f} {x0+bw:.2f},{y0+cav_depth*.5:.2f}" fill="none" stroke="#b3261e" stroke-width="1.2"/>'
    s += t(x0, y0+bh+5, note_en, 1.9) + t(x0+185, y0+bh+9, note_ar, 1.9, 400, 'end', extra=AR)
    return s
b = t(10, 22, 'PATTERNS AND MOULDS (proposed; Production decides split lines, draft, flanges and lay-up)', 2.4, 600) + t(410, 22, 'النماذج والقوالب (مقترح، والتصنيع يقرر خطوط الفصل والميل)', 2.4, 600, 'end', extra=AR)
# A: upper shell, female mould, A-surface (gloss) against the mould
x0, y0 = 22, 45
b += mould_cell(x0, y0, 'MOULD A: upper shell (1), female, edge section 1:2', 'القالب أ: الغلاف العلوي', SKIRT_H, 'Visible top and skirt are formed against the mould (red = laminate, thickness exaggerated). Flange 100 around (guess).', 'السطح الظاهر يتشكل على القالب. الشفة ١٠٠ مم (تخمين).')
x0b = 218
b += mould_cell(x0b, y0, 'MOULD B: lower shell (2), female, edge section 1:2', 'القالب ب: الغلاف السفلي', REV_H, 'Shallow mould: base with a 10 mm lip, set back 6 from the upper shell. Holes drilled after bonding.', 'قالب ضحل: القاعدة بحافة ١٠ مم. الثقوب بعد اللصق.')
# C: leg cup, split mould
x0c, y0c = 22, 135
b += t(x0c, y0c-8, 'MOULD C: leg cup (3), split in two halves, 1:5', 2.4, 600) + t(x0c+190, y0c-8, 'القالب ج: الرجل، نصفان', 2.3, 600, 'end', extra=AR)
S5_ = .15
b += rect(x0c, y0c, 90, 46, .4, INK, '#cfcac0') + rect(x0c+16, y0c+3, LEG_D*S5_, SHELL_H*S5_, .3, INK, '#fff') + line(x0c+16+LEG_D*S5_/2, y0c-3, x0c+16+LEG_D*S5_/2, y0c+49, .25, '#b3261e', '3 1 .6 1')
b += t(x0c+100, y0c+8, 'One mould, four legs. Parting line', 1.9) + t(x0c+100, y0c+11.5, f'down the side: it shows on a gloss', 1.9) + t(x0c+100, y0c+15, 'leg and must be faired out.', 1.9)
b += t(x0c+100, y0c+22, 'Closed top moulded in the cup. Open', 1.9) + t(x0c+100, y0c+25.5, 'bottom for bolting from inside.', 1.9)
b += t(x0c+190, y0c+40, 'خط الفصل على جانب الرجل ويحتاج تسوية.', 1.9, 400, 'end', extra=AR)
# D: cap
x0d, y0d = 225, 135
b += t(x0d, y0d-8, 'MOULD D: bottom cap (4) and bonded pad (5)', 2.4, 600) + t(x0d+185, y0d-8, 'القالب د: الغطاء السفلي واللوح', 2.3, 600, 'end', extra=AR)
b += f'<circle cx="{x0d+30:.2f}" cy="{y0d+32:.2f}" r="{CAP_D*S5_/2:.2f}" fill="#cfcac0" stroke="{INK}" stroke-width=".4"/>' + rect(x0d+68, y0d+14, MP*S5_, MP*S5_, .4, INK, '#cfcac0')
b += t(x0d+112, y0d+12, 'Flat discs and pads: cut from a moulded flat', 1.9) + t(x0d+112, y0d+15.5, 'sheet or a shallow mould. Production decides.', 1.9)
# patterns
b += t(22, 207, 'PATTERNS', 2.5, 600) + t(410, 207, 'النماذج', 2.5, 600, 'end', extra=AR)
for i, ln in enumerate(['Pattern per mould, made by large-format 3D printing in sections or CNC foam, then faired, primed and polished. The pattern surface sets the gloss of the finished part.',
                        'Gloss shows every flaw in the pattern and mould. Production decides fairing, mould polishing, number of coats and who paints; painter capacity is not known to us.',
                        'Vertical walls (skirt, legs) need draft or split moulds so the part can come out. Drawn here at 90 degrees as the design intent; draft angle and split lines are Production\'s.']):
    b += t(22, 212+i*3.8, ln, 1.9)
sh4 = sheet(4, N, 'PATTERNS AND MOULDS', 'النماذج والقوالب', '1:2 / 1:5', b)

# ================= SHEET 5: BOM and notes =================
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + t(410, 28, 'قائمة المواد', 2.8, 600, 'end', extra=AR)
b += rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Upper shell (top and skirt)', 'الغلاف العلوي', '1', f'Moulded GRP, {WALL} mm wall (proposal)'), ('2', 'Lower shell (base and lip)', 'الغلاف السفلي', '1', f'Moulded GRP, {WALL} mm wall (proposal)'),
       ('3', 'Leg cup, top closed', 'الرجل، قمة مغلقة', '4', f'Moulded GRP, {WALL} mm wall (proposal)'), ('4', 'Leg bottom cap (removable)', 'الغطاء السفلي', '4', f'GRP, {CAP_T} mm (proposal)'),
       ('5', 'Bonded pad with 4 M8 threaded inserts', 'لوح مثبت مع ٤ قطع مسننة', '4', 'GRP or plywood 6 mm, 160 x 160 (Production)'),
       ('6', 'Levelling pad, M10, Ø60, adjustable', 'قاعدة ضبط M10', '4', 'Bought-in; nominal 10 mm high (proposal)'), ('7', 'M8 bolt and washer', 'برغي M8 وحلقة', '16', 'Bought-in'),
       ('8', 'M5 screw with insert (bottom cap)', 'برغي M5', '12', 'Bought-in; fixing by Production'), ('9', 'Structural adhesive, GRP overlap, primer, Duco', 'لاصق وبرايمر ودوكو', 'as needed', 'By Production; Duco gloss')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*6
    b += line(10, yy+2.0, 410, yy+2.0, .15, HID) + t(12, yy, n_, 2.3) + t(24, yy, en, 2.3) + t(140, yy, ar, 2.3, 400, 'end', extra=AR) + t(150, yy, q, 2.3) + t(215, yy, m_, 2.3)
b += t(10, 106, 'NOTES', 2.8, 600) + t(410, 106, 'ملاحظات', 2.8, 600, 'end', extra=AR)
notes = [(f'Overall {L} x {W} x {H} mm, wall {WALL} mm, corner radius {R} mm, leg Ø{LEG_D} x {LEG_H} mm (incl. 10 mm pad), flush at the corners (leg radius = corner radius, concentric), and the whole construction are proposals, not costed. Production to confirm.', 'المقاسات والسماكات والتصنيع مقترحة وغير مُسعّرة. يؤكدها التصنيع.'),
         ('The shape is estimated by eye from one render of unknown source (not ours): a thick rounded-rectangle top with a visible joint line under it, on four fat cylindrical legs. Drawn as objekt\'s own design. The lamp in the photo is not part of the product.', 'الشكل مقدّر من صورة واحدة مجهولة المصدر ومرسوم كتصميم خاص بأوبجيكت. المصباح ليس جزءاً من المنتج.'),
         ('Material: moulded GRP (glass-fibre laminate), made from patterns and moulds. Changed from welded steel (rev 0, superseded) on Sabry\'s call, 12 Nov: the table in the render is probably not metal. Lay-up, resin, any core and wall thickness are Production\'s.', 'الخامة: فايبر جلاس مصبوب، بدلاً من الصلب (المراجعة ٠). التفاصيل من التصنيع.'),
         ('Colour and finish (proposal): Duco gloss over primer, Oxblood #5A1F25; Chocolate #4A2A1B is the alternative (colour unconfirmed). Paint system and gloss to be confirmed; codes to follow. Gloss shows every flaw: Production decides fairing, polishing and painter capacity, which is not known to us.', 'اللون والتشطيب (مقترح): دوكو لامع على برايمر، عنابي داكن. البديل بني شوكولاتة.'),
         (f'Weight, calculated (not weighed): about {KG:.0f} kg of laminate (slab {KG_SLAB:.0f} kg, four legs {KG_LEGS:.0f} kg), assuming {WALL} mm wall and 1.6 g/cm3, before inserts, pads, adhesive, filler, primer and paint. Density and wall are guesses. Ships in two parts: slab {L} x {W} x {SLAB}, and legs bolted up from inside.', f'الوزن محسوب (غير موزون): حوالي {KG:.0f} كجم فايبر جلاس. الكثافة والسماكة تخمين.'),
         ('The slab is two shells bonded together; the lower shell is set back 6 mm, giving the shadow line. Bolts go up from inside each leg (bottom cap removable) into M8 inserts in bonded pads. Bonding, fixing and access method are proposals.', 'السطح غلافان ملصوقان، والغلاف السفلي متراجع ٦ مم. التثبيت بالبراغي من داخل الرجل مقترح.'),
         (f'The legs sit flush at the four corners and follow the corner curve exactly: corner radius {R} = leg radius, same centre (Sabry, 12 Nov, from the render). Clear gap between legs: {LY[1]-LY[0]-LEG_D:.0f} mm front to back, {LX[1]-LX[0]-LEG_D:.0f} mm left to right. The lower shell is set back 6 mm, so each leg shows 6 mm proud of it at the corner.', 'الأرجل في الأركان تتبع انحناء السطح تماماً: نصف قطر الركن = نصف قطر الرجل.'),
         ('Material, wall thickness, draft, split lines, tolerances, joints and finish details are Production\'s to decide.', 'الخامة والسماكة والميل وخطوط الفصل والسماحيات يقررها التصنيع.'),
         ('No structural claims, stress figures, load figures, costs or prices on this drawing. Not engineered. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا تكاليف ولا أسعار. الصياغة العربية مسودة.'),
         ('Product number OBJ-193 was the next free number; Sabry can override.', 'رقم المنتج التالي المتاح؛ يمكن لسبري تغييره.')]
yy = 114
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
print('weight kg', round(KG, 1), 'slab', round(KG_SLAB, 1), 'legs', round(KG_LEGS, 1), 'notes end y', round(yy))
