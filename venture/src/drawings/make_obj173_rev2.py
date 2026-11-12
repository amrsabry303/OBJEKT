"""OBJ-173 REV 2 (DRAFT): cube 150 for a loose tapered round pot, top 100, base 65 (Sabry 12 Nov).
Run: python3 make_obj173_rev2.py <repo root>   then: NODE_PATH=<playwright> node make_pdf.js <dir> OBJ-173 2
Replaces the open-top REV 0 draft (not in git). Brief: Sabry 12 Nov 2026, "make it fit the round IKEA pot, so a circular opening from above".
Pot used for sizing: IKEA Egypt NYPON plant pot 15 cm, art. 60395616 (page figures: height 150, outside dia 170, inside dia 160, max flowerpot dia 150). TO CONFIRM by Sabry.
ALL OTHER SIZES PROPOSED, not costed, Production to confirm. Arabic is a draft."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-173'; os.makedirs(OUT, exist_ok=True)
SUP = OUT + '/superseded-rev1'
REV = 2; DATE = '12 Nov 2026'; PN = 'OBJ-173'
C, T = 150, 2                      # cube outer size, sheet thickness (proposed)
WH = C - T                         # wall height 198 (top plate sits on the walls)
POT_D, POT_H, POT_B = 100, 100, 65   # Sabry 12 Nov: top dia 100, base dia 65 (read as cm). Height ASSUMED 100 from IKEA Egypt FORENLIG 9 cm page, to confirm
OPEN_D = POT_D + 2                 # opening = pot body diameter + 2 mm clearance
SIDE_W = C - 2*T                   # left/right walls fit between front/back walls
CROSS = 2*WH + C                   # 596
SHEET_L, SHEET_W, GAP = 2500, 1250, 10

a_ = WH; m_ = T
CROSS_P = [(a_,0),(a_+C,0),(a_+C,a_),(a_+C,a_+m_),(a_+C+WH,a_+m_),(a_+C+WH,a_+C-m_),(a_+C,a_+C-m_),(a_+C,a_+C),(a_+C,a_+C+WH),(a_,a_+C+WH),(a_,a_+C),(a_,a_+C-m_),(0,a_+C-m_),(0,a_+m_),(a_,a_+m_),(a_,a_)]
def perim(p): return sum(math.dist(p[i], p[(i+1)%len(p)]) for i in range(len(p)))
TOP_P = [(0,0),(C,0),(C,C),(0,C)]
CUT_LEN = perim(CROSS_P) + perim(TOP_P) + math.pi*OPEN_D
NEST = [('cross', 10, 10), ('top', 10+CROSS+GAP, 10)]
assert 10+CROSS+GAP+C+10 <= SHEET_L and CROSS+20 <= SHEET_W
print('cross', CROSS, 'perimeter', round(perim(CROSS_P),1), 'cut length', round(CUT_LEN,1))
import glob, shutil
os.makedirs(SUP, exist_ok=True)
for f in glob.glob(OUT+'/OBJ-173_rev1_*'): shutil.move(f, SUP)
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4; d.layers.add('CUT', color=7); d.layers.add('SHEET', color=3); return d
def add_part(msp, key, ox, oy):
    if key == 'cross': msp.add_lwpolyline([(ox+x, oy+y) for x, y in CROSS_P], close=True, dxfattribs={'layer':'CUT'})
    else:
        msp.add_lwpolyline([(ox+x, oy+y) for x, y in TOP_P], close=True, dxfattribs={'layer':'CUT'})
        msp.add_circle((ox+C/2, oy+C/2), OPEN_D/2, dxfattribs={'layer':'CUT'})
for key, nm in [('cross','P1_cross_blank'),('top','P2_top_plate')]:
    d = new_doc(); add_part(d.modelspace(), key, 0, 0); d.saveas(f'{OUT}/{PN}_rev{REV}_{nm}.dxf')
d = new_doc(); mm = d.modelspace()
mm.add_lwpolyline([(0,0),(SHEET_L,0),(SHEET_L,SHEET_W),(0,SHEET_W)], close=True, dxfattribs={'layer':'SHEET'})
for k, x, y in NEST: add_part(mm, k, x, y)
d.saveas(f'{OUT}/{PN}_rev{REV}_nest_{SHEET_L}x{SHEET_W}.dxf')

FONT = "DejaVu Sans, Inter, Arial, sans-serif"
INK, DIM, HID, FILL, FILL2 = '#161616', '#2a4a7a', '#7a7a7a', '#f1efe9', '#dcd9d0'
RED = '#b3261e'
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;')
def t(x, y, s, size=2.6, w=400, anchor='start', fill=INK, extra=''):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size}" font-weight="{w}" text-anchor="{anchor}" fill="{fill}"{extra}>{esc(s)}</text>'
def ar(x, y, s, size=2.6, w=400, fill=INK): return t(x, y, s.rstrip('.'), size, w, 'end', fill)
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
    s += bi(X+2, Y+4, f'{PN}   Planter, mirror cube, round opening', 'حوض مكعب مرآة بفتحة دائرية', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  {C} x {C} x {C} mm', 'المقاس الكلي (مقترح)', 88, 2.3) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, f'MATERIAL  304 stainless, {T} mm proposed', 'الخامة: ستانلس ٣٠٤، ٢ مم مقترح', 88, 2.1) + bi(X+94, Y+25, 'FINISH  brushed stainless (approved)', 'التشطيب: ستانلس مصقول بالفرشاة', 88, 2.1)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, RED, '#fff')
    s += t(X+Wd/2, Y-8.6, 'Approved by Sabry 12 Nov 2026. Production review pending. Not engineered', 2.4, 700, 'middle', RED) + t(X+Wd/2, Y-3.8, 'معتمد من سبري ١٢ نوفمبر ٢٠٢٦. مراجعة التصنيع قيد الانتظار. غير مهندس', 2.4, 700, 'middle', RED)
    return s + t(10, 14, title_en, 4.2, 700) + ar(410, 14, title_ar, 4.2, 700)
def sheet(n, te, ta, sc, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, te, ta, sc)}{body}</svg>'
def circ(cx, cy, r, sw=.4, col=INK, fill='none', dash=None):
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + '/>'
MIR, BRU, POTF = '#e4e6e8', '#b8b8b4', '#d9d4c8'
im = Image.open(ROOT + '/images/OBJ-173_ref-sabry-12nov.jpg').convert('RGB'); im.thumbnail((520, 520))
b_ = io.BytesIO(); im.save(b_, 'JPEG', quality=72); PHOTO = 'data:image/jpeg;base64,' + base64.b64encode(b_.getvalue()).decode()

# ===== 1 views =====
S = .42; ox, oy = 25, 35
b = t(ox, oy-5, 'PLAN, 1:2.4', 2.6, 600)
b += rect(ox, oy, C*S, C*S, .5, INK, MIR) + circ(ox+C*S/2, oy+C*S/2, OPEN_D/2*S, .5, INK, '#fff')
b += circ(ox+C*S/2, oy+C*S/2, POT_D/2*S, .3, HID, 'none', '1.4 1')
b += dim_h(ox, ox+C*S, oy+C*S+7, f'{C}', ext=oy+C*S) + dim_v(ox-7, oy, oy+C*S, f'{C}', ext=ox)
b += dim_h(ox+C*S/2-OPEN_D/2*S, ox+C*S/2+OPEN_D/2*S, oy+C*S/2, f'Ø{OPEN_D}', ext=None)
b += t(ox, oy+C*S+17, f'Opening Ø{OPEN_D} = pot top Ø{POT_D} + 2 mm.', 2.1, 400, fill=HID) + t(ox, oy+C*S+20.5, f'Top plate ring left each side: {(C-OPEN_D)//2} mm.', 2.1, 400, fill=HID)
b += ar(120, oy+C*S+24, f'الفتحة Ø{OPEN_D} = قطر الأصيص {POT_D} + ٢ مم', 2.1, 400, HID)
ex, ey0 = 30, 232
b = b + ''
# section
sx0 = 135; sy0 = oy
b += t(sx0, oy-5, 'SECTION through centre, 1:2.4', 2.6, 600)  # top-left of section
b += rect(sx0, sy0, C*S, C*S, .5, INK, MIR)
b += rect(sx0+T*S, sy0+T*S, (C-2*T)*S, (C-2*T)*S, .3, INK, '#fff')
# top plate (with opening) drawn over walls
b += rect(sx0, sy0, C*S, T*S, .4, INK, '#9a9a96')
b += rect(sx0+(C-OPEN_D)/2*S, sy0-.01, OPEN_D*S, T*S+.02, 0, 'none', '#fff')
# pot hanging by rim (to confirm) or on floor: show on floor dashed
pot_top = sy0 + (C-T-POT_H)*S
b += poly([(sx0+(C-POT_D)/2*S, pot_top), (sx0+(C+POT_D)/2*S, pot_top), (sx0+(C+POT_B)/2*S, pot_top+POT_H*S), (sx0+(C-POT_B)/2*S, pot_top+POT_H*S)], .35, HID, POTF, '1.6 1')
b += t(sx0+C*S/2, pot_top+POT_H*S/2, f'pot top Ø{POT_D}, base Ø{POT_B}, H {POT_H}?', 2.2, 500, 'middle', HID) + t(sx0+C*S/2, pot_top+POT_H*S/2+4, '(bought-in, position only)', 1.9, 400, 'middle', HID)
b += dim_v(sx0+C*S+7, sy0, sy0+C*S, f'{C}', ext=sx0+C*S) + dim_h(sx0, sx0+C*S, sy0+C*S+7, f'{C}', ext=sy0+C*S)
b += dim_v(sx0-7, sy0+T*S, sy0+(C-T)*S, f'{C-2*T} inside', ext=sx0+T*S)
b += t(sx0, sy0+C*S+17, f'Walls {T} mm; top plate {T} mm on the walls.', 2.0, 400, fill=HID) + t(sx0, sy0+C*S+20.5, f'Inside height {C-2*T}. Pot {POT_H} high stands {C-2*T-POT_H} mm', 2.0, 400, fill=HID) + t(sx0, sy0+C*S+24, 'below the plate unless its rim hangs. Note 5.', 2.0, 400, fill=HID)
# front elevation
fx = 245
b += t(fx, oy-5, 'FRONT, 1:2.4 (same as side)', 2.6, 600)
b += rect(fx, oy, C*S, C*S, .5, INK, MIR) + dim_h(fx, fx+C*S, oy+C*S+7, f'{C}', ext=oy+C*S)
b += line(fx, oy+T*S, fx+C*S, oy+T*S, .2, HID, '1 1') + t(fx, oy+C*S+17, 'Dotted: top plate seam, ground flush.', 2.0, 400, fill=HID)
b += ar(410, oy-5, 'المناظر: علوي، قطاع، أمامي', 2.6, 600)
# reference + colourways
rx = 25; ih = 90*im.size[1]/im.size[0]
b += t(rx, 152, 'REFERENCE (open top, not ours)', 2.4, 600)
b += f'<image x="{rx}" y="155" width="90" height="{ih:.1f}" href="{PHOTO}"/>' + rect(rx, 155, 90, ih, .25, HID)
b += t(rx+95, 160, 'Sabry, 12 Nov. Maker unknown.', 1.9, 400, fill=HID) + t(rx+95, 164, 'Shape only; round opening is the change.', 1.9, 400, fill=HID)
b += rect(rx+95, 172, 14, 9, .3, INK, MIR) + t(rx+112, 176, 'Mirror stainless (proposed)', 2.1, 600) + rect(rx+95, 184, 14, 9, .3, INK, BRU) + t(rx+112, 188, 'Brushed stainless (alternative)', 2.1, 600)
sh1 = sheet(1, 'VIEWS', 'المناظر', '1:2.4', b)

# ===== 2 parts =====
S2 = .3; ox, oy = 25, 45
b = t(10, 24, f'ITEM 1  CROSS BLANK, flat, 1:3.3   qty 1', 2.6, 600) + ar(410, 24, 'بند ١، الشكل المفرود، العدد ١', 2.6, 600)
P = [(ox+x*S2, oy+(CROSS-y)*S2) for x, y in CROSS_P]
b += poly(P, .5, INK, FILL)
for k, (x0, y0, x1, y1) in {'b': (WH, WH, WH+C, WH+C)}.items(): b += rect(ox+x0*S2, oy+(CROSS-y1)*S2, C*S2, C*S2, .3, DIM, 'none', '2 1')
for x0, y0, x1, y1 in [(WH, WH+C, WH+C, WH+C), (WH, WH, WH+C, WH), (WH, WH, WH, WH+C), (WH+C, WH, WH+C, WH+C)]: pass
b += t(ox+(WH+C/2)*S2, oy+(CROSS-WH-C/2)*S2, 'BOTTOM', 2.6, 600, 'middle', HID) + t(ox+(WH+C/2)*S2, oy+(CROSS-WH/2)*S2+1, 'FRONT / BACK', 2.2, 600, 'middle', HID)
b += t(ox+WH/2*S2, oy+(CROSS-WH-C/2)*S2, 'SIDE', 2.2, 600, 'middle', HID) + t(ox+(WH+C+WH/2)*S2, oy+(CROSS-WH-C/2)*S2, 'SIDE', 2.2, 600, 'middle', HID)
b += t(ox+(WH+C/2)*S2, oy+(WH/2)*S2+1, 'FRONT / BACK', 2.2, 600, 'middle', HID)
b += balloon(ox+(WH+C/2)*S2+30, oy+(CROSS-WH-C/2)*S2+12, 1)
b += dim_h(ox, ox+CROSS*S2, oy+CROSS*S2+8, f'{CROSS}', ext=oy+CROSS*S2) + dim_v(ox-8, oy, oy+CROSS*S2, f'{CROSS}', ext=ox)
b += dim_h(ox+WH*S2, ox+(WH+C)*S2, oy-6, f'{C}', ext=oy) + dim_v(ox+CROSS*S2+8, oy+(CROSS-WH)*S2, oy+CROSS*S2, f'{WH}', ext=ox+(WH+C)*S2)
b += t(ox, oy+CROSS*S2+16, 'Dashed blue: fold lines (sharp folds drawn; bend allowance is Production\'s).', 2.0, 400, fill=HID) + t(ox, oy+CROSS*S2+20, f'Side flaps {SIDE_W} wide: front and back walls cover the corners.', 2.0, 400, fill=HID) + t(ox, oy+CROSS*S2+24, 'Four corners butt-welded, ground flush.', 2.0, 400, fill=HID)
# top plate
tx0, ty0, S3 = 250, 52, .4
b += t(tx0, 40, 'ITEM 2  TOP PLATE, 1:2.5   qty 1', 2.6, 600) + ar(410, 40, 'بند ٢، لوح علوي، العدد ١', 2.6, 600)
b += rect(tx0, ty0, C*S3, C*S3, .5, INK, FILL) + circ(tx0+C*S3/2, ty0+C*S3/2, OPEN_D/2*S3, .5, INK, '#fff')
b += balloon(tx0+10, ty0+10, 2) + dim_h(tx0, tx0+C*S3, ty0+C*S3+7, f'{C}', ext=ty0+C*S3) + dim_v(tx0-7, ty0, ty0+C*S3, f'{C}', ext=tx0)
b += dim_h(tx0+C*S3/2-OPEN_D/2*S3, tx0+C*S3/2+OPEN_D/2*S3, ty0+C*S3/2, f'Ø{OPEN_D}')
b += t(tx0, ty0+C*S3+15, f'Opening centred, edge deburred. Small inward rolled or flanged edge: only if Production can.', 2.0, 400, fill=HID)
rows = [('Cross blank', f'{CROSS} x {CROSS} x {T}'), ('Cross cut length', f'{perim(CROSS_P):.0f} mm'), ('Top plate', f'{C} x {C} x {T}'), ('Opening', f'Ø{OPEN_D} (pot top Ø{POT_D} + 2)'), ('Top plate cut length', f'{perim(TOP_P)+math.pi*OPEN_D:.0f} mm'), ('Welds', '4 corner seams + top plate seam'), ('Cube outer', f'{C} x {C} x {C}')]
b += t(tx0, 150, 'DATA', 2.6, 600) + ar(410, 150, 'بيانات', 2.6, 600)
for i, (k, v) in enumerate(rows):
    yy = 158 + i*6.2
    b += line(tx0, yy+2, 410, yy+2, .15, HID) + t(tx0+1, yy, k, 2.2) + t(408, yy, v, 2.2, 600, 'end')
sh2 = sheet(2, 'PART SHEET', 'ورقة الأجزاء', '1:3.3', b)

# ===== 3 assembly =====
S4 = .45; ox, oy = 40, 100
b = t(10, 24, 'EXPLODED SECTION, 1:2.2', 2.6, 600) + ar(410, 24, 'قطاع مفكك', 2.6, 600)
body_y = oy + 20
b += rect(ox, body_y, C*S4, (C-T)*S4, .5, INK, MIR) + rect(ox+T*S4, body_y+0, (C-2*T)*S4, (C-2*T)*S4, .3, INK, '#fff')
b += balloon(ox-8, body_y+60, 1) + t(ox-4, body_y+C*S4+8, '', 2)
tp_y = oy - 10
b += rect(ox, tp_y, C*S4, T*S4+1, .4, INK, '#9a9a96') + balloon(ox-8, tp_y+1, 2)
b += circ(ox+C*S4/2, tp_y-9, 0, 0)
b += line(ox+C*S4/2, tp_y+3, ox+C*S4/2, body_y-2, .2, DIM, '1.5 1')
pot_y = oy - 62
b += rect(ox+(C-POT_D)/2*S4, pot_y, POT_D*S4, POT_H*S4*0.0+POT_H*S4*0.0+POT_H*S4*0.0+1, 0, 'none', 'none') 
b += poly([(ox+(C-POT_D)/2*S4, pot_y), (ox+(C+POT_D)/2*S4, pot_y), (ox+(C+POT_B)/2*S4, pot_y+POT_H*S4*.7), (ox+(C-POT_B)/2*S4, pot_y+POT_H*S4*.7)], .35, HID, POTF, '1.6 1') + t(ox+C*S4/2, pot_y+POT_H*S4*.35, 'pot (loose, bought in)', 2.0, 500, 'middle', HID)
b += balloon(ox-8, pot_y+10, 3)
b += t(ox, body_y+C*S4+12, 'Item 1 folded (open top), item 2 welded on, item 3 dropped through the opening.', 2.0, 400, fill=HID)
b += ar(215, body_y+C*S4+16.5, 'يُطوى البند ١، يُلحم البند ٢، ثم يوضع الأصيص.', 2.0, 400, HID)
sx0 = 238
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + ar(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600)
steps = [('Cut item 1 and item 2, deburr, including the opening edge.', 'قص البندين ١ و٢ وإزالة الحواف الحادة بما فيها حافة الفتحة.'),
         ('Fold item 1 on the four fold lines into an open box.', 'طي البند ١ على خطوط الطي إلى صندوق مفتوح.'),
         ('Weld the four corner seams, grind flush.', 'لحام الحروف الأربعة الركنية وصنفرتها.'),
         ('Place item 2 on the walls, weld the seam all round, grind flush.', 'وضع اللوح العلوي ولحام محيطه وصنفرته.'),
         ('Polish all faces (mirror or brushed). Item 3, the pot, is not part of the cube.', 'تلميع كل الأوجه. الأصيص ليس جزءاً من المكعب.')]
for i, (en, a) in enumerate(steps):
    yy = 48 + i*17
    b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 2.2) + ar(410, yy+5, a, 2.2)
b += t(sx0, 140, 'Weld method, jigs, order and grinding are Production\'s. The cube has no drain hole: the pot drains', 2.1, 400, fill=HID)
b += t(sx0, 144.5, 'into the cube. Water collecting in the cube is for the customer to empty; to confirm with Sabry.', 2.1, 400, fill=HID)
sh3 = sheet(3, 'ASSEMBLY', 'التجميع', '1:2.2', b)

# ===== 4 nest =====
S5 = .1; ox, oy = 30, 40
b = t(10, 22, f'CUTTING LAYOUT on an assumed sheet {SHEET_L} x {SHEET_W} x {T}. Assumed, to be confirmed by Production.', 2.4, 600) + ar(410, 22, 'مخطط القص على لوح مفترض', 2.4, 600)
b += rect(ox, oy, SHEET_L*S5, SHEET_W*S5, .5, '#2f6b45', '#fbfaf6') + t(ox, oy-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for k, x, y in NEST:
    pts = CROSS_P if k == 'cross' else TOP_P
    b += poly([(ox+(x+px)*S5, oy+(SHEET_W-(y+py))*S5) for px, py in pts], .3, INK, FILL)
    if k == 'top': b += circ(ox+(x+C/2)*S5, oy+(SHEET_W-(y+C/2))*S5, OPEN_D/2*S5, .3, INK, '#fbfaf6')
    b += t(ox+(x+(CROSS if k=='cross' else C)/2)*S5, oy+(SHEET_W-(y+(CROSS if k=='cross' else C)/2))*S5+(1 if k=='cross' else -3), '1' if k=='cross' else '2', 3.4, 600, 'middle', '#555')
b += dim_h(ox, ox+SHEET_L*S5, oy+SHEET_W*S5+7, f'{SHEET_L}', ext=oy+SHEET_W*S5) + dim_v(ox-6, oy, oy+SHEET_W*S5, f'{SHEET_W}', ext=ox)
b += t(30, 195, f'Item 1 and item 2 nested with {GAP} mm spacing. They use about {10+CROSS+GAP+C+10} x {CROSS+20} mm of the sheet. No offcut is claimed.', 2.3)
b += t(30, 200, f'Total cutting length (both parts, with the opening): {CUT_LEN/1000:.2f} m ({CUT_LEN:.0f} mm).', 2.5, 600)
b += ar(410, 195, 'جزءان بمسافة ١٠ مم. لا يُدّعى أي هالك.', 2.3) + ar(410, 200, f'إجمالي طول القص: {CUT_LEN/1000:.2f} متر', 2.5, 600)
sh4 = sheet(4, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)

# ===== 5 BOM and notes =====
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + ar(410, 28, 'قائمة المواد', 2.8, 600) + rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Cross blank, folded', 'قطعة مفرودة تُطوى', '1', f'304 stainless sheet {T} mm (proposed), mirror or brushed'),
       ('2', f'Top plate with Ø{OPEN_D} opening', 'لوح علوي بفتحة دائرية', '1', f'304 stainless sheet {T} mm (proposed), mirror or brushed'),
       ('3', f'Tapered round pot, top Ø{POT_D}, base Ø{POT_B}, loose (bought in, not supplied)', 'أصيص دائري (غير مرفق)', '1', 'Sabry\'s IKEA pot (article to confirm)')]
for i, (n_, en, a, q, mat) in enumerate(bom):
    yy = 44 + i*7
    b += line(10, yy+2.2, 410, yy+2.2, .15, HID) + t(12, yy, n_, 2.4) + t(24, yy, en, 2.3) + ar(148, yy, a, 2.2) + t(150, yy, q, 2.4) + t(215, yy, mat, 2.2)
b += t(10, 72, 'NOTES', 2.8, 600) + ar(410, 72, 'ملاحظات', 2.8, 600)
notes = [(f'ALL SIZES EXCEPT THE POT DIAMETERS ARE PROPOSED, not costed, Production to confirm: cube {C}, sheet {T} mm. Pot top Ø{POT_D} and base Ø{POT_B} are from Sabry (12 Nov, read as cm). Pot height {POT_H} is ASSUMED from the IKEA Egypt FORENLIG 9 cm page (10 cm high) and must be confirmed.', 'المقاسات مقترحة عدا الأصيص.'),
         (f'Opening Ø{OPEN_D} = pot top Ø{POT_D} + 2 mm. Real pots vary: Production measures a bought pot before cutting.', 'تُقاس عينة أصيص فعلية قبل القص.'),
         ('Shape traced from the reference photo (open top) with one change from Sabry: a round opening in a closed top plate. Drawn as exact otherwise.', 'الشكل من الصورة المرجعية مع فتحة دائرية.'),
         ('No drain hole. The pot is loose and drains into the cube (Sabry\'s brief). Production decides any weld seal.', 'بلا ثقب تصريف؛ الأصيص منفصل.'),
         (f'Depth of the pot: the cube is {C-2*T} mm inside, the pot is {POT_H}. If the pot rim stands proud of the body it can hang on the top plate; if not, it stands on the floor {C-2*T-POT_H} mm down, or on a loose riser. Production to test with a real pot.', 'عمق الأصيص يُختبر بأصيص فعلي.'),
         ('Finish proposed: mirror all faces. Polishers are few, so mirror pieces are capped; brushed is the alternative. Sabry chooses.', 'المرآة محدودة بعدد المصقلين؛ الفرشاة بديل.'),
         ('No structural claims, stress figures, costs or prices. Not engineered. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا أسعار. الصياغة العربية مسودة.')]
for i, (en, a) in enumerate(notes):
    yy = 80 + i*17
    words = en.split(); lines_, cur = [], ''
    for w in words:
        if len(cur)+len(w) > 175: lines_.append(cur); cur = w
        else: cur = (cur+' '+w).strip()
    lines_.append(cur)
    b += t(12, yy, f'{i+1}.', 2.4, 600)
    for j, l in enumerate(lines_): b += t(18, yy+j*4, l, 2.2)
    b += ar(410, yy+len(lines_)*4, a, 2.2)
sh5 = sheet(5, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)
for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1): open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('written')
