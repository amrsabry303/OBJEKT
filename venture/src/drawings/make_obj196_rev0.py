"""OBJ-196: plant stand, flat round base disc, two vertical plates, round top disc, shelf disc. Production drawing set, REV 0 (DRAFT).
Run: python3 make_obj196_rev0.py <repo root>   Then: NODE_PATH=<playwright> node make_pdf.js <dir> OBJ-196 0
Reference: images/OBJ-196.jpg (stainless) plus a second angle Sabry sent in the session (blue, not stored in the repo). Third-party, maker unknown; drawn as objekt's own design.
READING OF THE REFERENCE (inferred, to confirm): the two plates are parallel with a narrow gap, OFFSET from the disc centre (photo 2: gap about 0.26 D off centre).
The near plate carries the big segment of the base disc and of the top disc; the far plate the small segment. The pot stands on a shelf and goes through a round hole in the top disc.
Every size is a PROPOSAL, not costed, Production to confirm. Pot sizes from size-charts.com 4 L pot (rim 20 cm, base 15.5 cm, height 16.5 cm). Arabic is a draft. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-196'; os.makedirs(OUT, exist_ok=True)
PHOTO = ROOT + '/images/OBJ-196.jpg'
REV = 0; DATE = '12 Nov 2026'; PN = 'OBJ-196'
D, R, H, T = 300, 150, 400, 2          # disc diameter, radius, height to top face of top disc, sheet
POT_RIM, POT_BASE, POT_H = 200, 155, 165   # reference pot (size-charts.com 4 L), NOT part of the product
RH = 102                               # hole radius in top disc = pot rim 100 + 2 clearance
GAP = 22; XF_IN = RH + 2               # far plate inner face x = 104
XF = XF_IN + T/2                       # far plate mid x = 105
XN = XF_IN - GAP - T/2                 # near plate mid x = 81
ZS = 280                               # shelf top height; pot rim then at 445 = 45 above the top disc
RS = 88                                # shelf radius (pot base 77.5 + 10)
WH = math.sqrt(RH**2 - XN**2); WHD = round(2*WH)   # window half width in near plate (about 62)
CH_N = 2*math.sqrt(R**2 - XN**2); CH_F = 2*math.sqrt(R**2 - XF**2)
DN, DF = round(XN + R), round(R - XF)
SH_HW = math.sqrt(RS**2 - (XN-T/2)**2) # shelf neck half width at the plate face
TAB = 20                               # shelf tab, folds down against the plate
HOLE_D = 5.5; TIE = [(-95, 60), (95, 60), (-95, 340), (95, 340)]   # tie spacer holes (y, z)
SHEET_L, SHEET_W, GP = 2500, 1250, 10
def seg(x0, n=60):
    """half chord of the disc at x"""
    return math.sqrt(max(R*R - x0*x0, 0))
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
    s += bi(X+2, Y+4, f'{PN}   Planter, plant stand, disc base and two plates', 'حامل نباتات بقاعدة دائرية ولوحين', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, f'SIZE  Ø{D} x {H} mm (proposal)', 'المقاس الكلي (مقترح)', 88, 2.1) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, 'MATERIAL  Stainless sheet 2 mm (proposal), folded', 'الخامة: ستانلس ٢ مم (مقترح)، ثني', 88, 2.0) + bi(X+94, Y+25, 'FINISH  Brushed stainless (no paint)', 'التشطيب: ستانلس مبروش', 88, 2.1)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, '#b3261e', '#fff')
    s += t(X+Wd/2, Y-8.6, STAMP, 2.9, 700, 'middle', '#b3261e') + t(X+Wd/2, Y-3.8, STAMP_AR, 2.9, 700, 'middle', '#b3261e')
    s += t(10, 14, title_en, 4.2, 700) + t(410, 14, title_ar, 4.2, 700, 'end', extra=' direction="rtl"')
    return s
def sheet(n, N, title_en, title_ar, scale, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, N, title_en, title_ar, scale)}{body}</svg>'
AR = ' direction="rtl"'
# ---------------- flat patterns, frame X = along the part (v), Y = across (u + half width) ----------------
def arc_pts(f, a0, a1, n=48): return [f(a0 + (a1-a0)*i/n) for i in range(n+1)]
def outer_near():
    L = DN + 400 + DN; UC = 150
    left = [(v, UC - seg(-R + v)) for v in [DN*i/40 for i in range(41)]]            # base flange, v 0..231
    left += [(DN, UC - CH_N/2), (DN+400, UC - CH_N/2)]
    left += [(DN+400+d, UC - seg(XN - d)) for d in [DN*i/40 for i in range(41)]]
    right = [(v, UC + h) for v, h in [(x, UC - y) for x, y in left]]
    right = [(v, 2*UC - y) for v, y in left]
    return left + right[::-1], L, UC
def hole_near():
    UC = 150; z0 = DN
    pts = [(z0+ZS, UC-WH), (z0+400, UC-WH)]
    a0 = math.acos(XN/RH)
    pts += [(z0+400 + (XN - RH*math.cos(a)), UC + RH*math.sin(a)*(-1)) for a in [a0 + (math.pi - a0)*i/48 for i in range(49)]]
    pts += [(z0+400 + (XN - RH*math.cos(a)), UC + RH*math.sin(a)) for a in [math.pi - (math.pi - a0)*i/48 for i in range(49)]]
    pts += [(z0+400, UC+WH), (z0+ZS, UC+WH)]
    return pts
def outer_far():
    UC = CH_F/2
    left = [(v, UC - seg(R - v)) for v in [DF*i/20 for i in range(21)]]
    left += [(DF, UC - CH_F/2), (DF+400, UC - CH_F/2)]
    left += [(DF+400+d, UC - seg(XF + d)) for d in [DF*i/20 for i in range(21)]]
    right = [(v, 2*UC - y) for v, y in left]
    return left + right[::-1], DF+400+DF, UC
def shelf_pts():
    xm = XN - T/2; a = math.acos(xm/RS)
    pts = [(RS + RS*math.cos(th), RS + RS*math.sin(th)) for th in [a + (2*math.pi - 2*a)*i/80 for i in range(81)]]
    return pts, (RS + xm, RS - SH_HW), (RS + xm + TAB, RS + SH_HW)
OUT_N, LN, UCN = outer_near(); HOLE_N = hole_near()
OUT_F, LF, UCF = outer_far()
SH, TB0, TB1 = shelf_pts()
def tie_holes(zoff, uc): return [(zoff + z, uc + y) for y, z in TIE]
def plen(pts, closed=True): return sum(math.dist(pts[i], pts[(i+1) % len(pts)]) for i in range(len(pts) if closed else len(pts)-1))
LEN_N = plen(OUT_N) + plen(HOLE_N) + 4*math.pi*HOLE_D
LEN_F = plen(OUT_F) + 4*math.pi*HOLE_D
SH_OUT = SH + [(TB1[0], TB1[1]), (TB1[0], TB0[1])]    # outline incl. tab, tab at +x
# rebuild shelf outline properly: arc then tab rectangle between the two arc end points
xm = XN - T/2; a_ = math.acos(xm/RS)
arc = [(RS + RS*math.cos(th), RS + RS*math.sin(th)) for th in [a_ + (2*math.pi - 2*a_)*i/80 for i in range(81)]]
SH_OUT = arc + [(RS + xm + TAB, arc[-1][1]), (RS + xm + TAB, arc[0][1])]
LEN_S = plen(SH_OUT)
TOTAL_CUT = LEN_N + LEN_F + LEN_S
PARTS = {'P1': ('near-plate-with-flanges', OUT_N, [HOLE_N] + [], LN, 2*UCN, [DN, DN+400]),
         'P2': ('far-plate-with-flanges', OUT_F, [], LF, 2*UCF, [DF, DF+400]),
         'P3': ('shelf', SH_OUT, [], 2*RS + TAB + 0, 2*RS, [])}
BB = {'P1': (LN, 2*UCN), 'P2': (LF, 2*UCF), 'P3': (max(p[0] for p in SH_OUT), 2*RS)}
NEST = [('P1', GP, GP), ('P2', GP + LN + GP, GP), ('P3', GP + LN + GP, GP + 2*UCF + GP)]
for k, x, y in NEST: assert x + BB[k][0] <= SHEET_L and y + BB[k][1] <= SHEET_W
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); d.layers.add('FOLD', color=5); d.layers.add('SHEET', color=3); return d
def add_part(msp, k, ox, oy):
    fn, outl, holes, L_, W_, folds = PARTS[k]
    msp.add_lwpolyline([(ox+p[0], oy+p[1]) for p in outl], close=True, dxfattribs={'layer': 'CUT'})
    if k == 'P1':
        msp.add_lwpolyline([(ox+p[0], oy+p[1]) for p in HOLE_N], close=True, dxfattribs={'layer': 'CUT'})
        for v, u in tie_holes(DN, UCN): msp.add_circle((ox+v, oy+u), HOLE_D/2, dxfattribs={'layer': 'CUT'})
    if k == 'P2':
        for v, u in tie_holes(DF, UCF): msp.add_circle((ox+v, oy+u), HOLE_D/2, dxfattribs={'layer': 'CUT'})
    if k in ('P1', 'P2'):
        for f in folds:
            hw = CH_N/2 if k == 'P1' else CH_F/2
            uc = UCN if k == 'P1' else UCF
            msp.add_line((ox+f, oy+uc-hw), (ox+f, oy+uc+hw), dxfattribs={'layer': 'FOLD'})
    if k == 'P3':
        msp.add_line((ox+RS+xm, oy+arc[0][1]), (ox+RS+xm, oy+arc[-1][1]), dxfattribs={'layer': 'FOLD'})
for k in PARTS:
    doc = new_doc(); add_part(doc.modelspace(), k, 0, 0); doc.saveas(f'{OUT}/{PN}_rev{REV}_{k}_{PARTS[k][0]}.dxf')
doc = new_doc(); m = doc.modelspace()
m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
for k, x, y in NEST: add_part(m, k, x, y)
doc.saveas(f'{OUT}/{PN}_rev{REV}_nest_{SHEET_L}x{SHEET_W}.dxf')

N = 5
def circ(cx, cy, r): return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="#fff" stroke="{INK}" stroke-width=".35"/>'
def pl(pts, sw=.35, fill=FILL, dash=None, col=INK): return poly(pts, sw, col, fill, dash)
# ================= SHEET 1: views =================
S = .27; oz = 215
def X0(cx): return cx
b = t(24, 26, 'FRONT (looking along the plates)', 2.6, 600) + t(130, 29.5, 'الأمامي (بمحاذاة اللوحين)', 2.4, 500, 'end', extra=AR)
cx = 80                                           # disc centre x on sheet
def zz(z): return oz - z*S
# base disc, top disc, plates, shelf, pot (dashed)
b += rect(cx-R*S, zz(0)-T*S*1.6, D*S, T*S*1.6, .4, INK, '#d9dbdc')
b += rect(cx-R*S, zz(H)-T*S*1.6+T*S*1.6-T*S*1.6, D*S, T*S*1.6, .4, INK, '#d9dbdc')
b += rect(cx+(XN-T/2)*S, zz(H), T*S, H*S, .35, INK, '#c9cbcd') + rect(cx+(XF-T/2)*S, zz(H), T*S, H*S, .35, INK, '#c9cbcd')
b += rect(cx-(RS-0)*S, zz(ZS)-T*S*1.6, (RS+XN-T/2)*S, T*S*1.6, .35, INK, '#c9cbcd')
potpts = [(cx-POT_RIM/2*S, zz(ZS+POT_H)), (cx+POT_RIM/2*S, zz(ZS+POT_H)), (cx+POT_BASE/2*S, zz(ZS)), (cx-POT_BASE/2*S, zz(ZS))]
b += pl(potpts, .3, 'none', '1.4 .9', HID)
b += t(cx-POT_RIM/2*S, zz(ZS+POT_H)-1.5, 'pot (not ours)', 1.8, 400, fill=HID)
b += dim_v(cx-R*S-8, zz(H), zz(0), f'{H}', ext=cx-R*S) + dim_h(cx-R*S, cx+R*S, zz(0)+7, f'Ø{D}', ext=zz(0))
b += dim_v(cx+R*S+9, zz(ZS), zz(0), f'{ZS} shelf', ext=cx+RS*S) if False else ''
b += dim_h(cx+(XN+T/2)*S, cx+(XF-T/2)*S, zz(H)-6, f'gap {GAP}', ext=zz(H))
b += balloon(cx+XF*S+12, zz(150), 2) + balloon(cx+XN*S-10, zz(150), 1) + balloon(cx-RS*S+4, zz(ZS)-6, 3)
# side
sx = 205
b += t(sx-30, 26, 'SIDE (from the near plate, -x)', 2.6, 600) + t(sx+75, 29.5, 'الجانبي', 2.4, 500, 'end', extra=AR)
b += rect(sx-CH_N/2*S, zz(H), CH_N*S, H*S, .4, INK, '#d9dbdc')
b += rect(sx-WH*S, zz(H), WH*2*S, (H-ZS)*S, .35, INK, '#fff')
b += rect(sx-R*S, zz(0)-T*S*1.6, D*S, T*S*1.6, .4, INK, '#c0c3c5') + rect(sx-R*S, zz(H)-T*S*1.6, D*S, T*S*1.6, .4, INK, '#c0c3c5')
b += pl([(sx-SH_HW*S, zz(ZS)), (sx+SH_HW*S, zz(ZS)), (sx+SH_HW*S, zz(ZS-TAB)), (sx-SH_HW*S, zz(ZS-TAB))], .3, '#b8bbbd')
b += dim_h(sx-CH_N/2*S, sx+CH_N/2*S, zz(H)-5, f'{CH_N:.0f}', ext=zz(H)) + dim_h(sx-WH*S, sx+WH*S, zz(H)+(H-ZS)*S/2*0+ -0.0 + 14, f'{WHD}', ext=zz(H)) if False else dim_h(sx-CH_N/2*S, sx+CH_N/2*S, zz(H)-5, f'{CH_N:.0f}', ext=zz(H))
b += t(sx+WH*S+2, zz(H)+(H-ZS)*S/2+1, f'window {WHD} wide, from {ZS} up', 1.9, 400, fill=HID)
# plan
px, py = 325, 90
b += t(px-30, 26, 'PLAN', 2.6, 600) + t(px+30, 29.5, 'المسقط الأفقي', 2.4, 500, 'end', extra=AR)
P_ = .27
pcx, pcy = px, py
b += circ(pcx, pcy, R*P_)
b += circ(pcx, pcy, RH*P_) + f'<circle cx="{pcx}" cy="{pcy}" r="{RS*P_:.2f}" fill="none" stroke="{HID}" stroke-width=".25" stroke-dasharray="1.2 .8"/>'
b += rect(pcx+(XN-T/2)*P_, pcy-CH_N/2*P_, T*P_, CH_N*P_, .3, INK, '#c9cbcd') + rect(pcx+(XF-T/2)*P_, pcy-CH_F/2*P_, T*P_, CH_F*P_, .3, INK, '#c9cbcd')
b += dim_h(pcx-R*P_, pcx+R*P_, pcy+R*P_+8, f'Ø{D}', ext=pcy+R*P_) + dim_h(pcx-RH*P_, pcx+RH*P_, pcy-R*P_-5, f'hole Ø{2*RH}', ext=pcy-RH*P_)
b += t(px-44, pcy+R*P_+17, f'Plates at x = {XN:.0f} and {XF:.0f} from the disc centre (offset); dashed = shelf Ø{2*RS}.', 1.9, 400, fill=HID)
# photo
b += t(24, 240, 'REFERENCE PHOTO (third-party, maker unknown; second angle seen in session)', 2.1, 600) + t(215, 244, 'صورة مرجعية (ليست لنا)', 2.1, 500, 'end', extra=AR)
b += f'<image href="{datauri(PHOTO, 300)}" x="300" y="170" width="42" height="56" preserveAspectRatio="xMidYMid slice"/>' + rect(300, 170, 42, 56, .2, HID)
b += t(346, 176, 'Photo shows brushed stainless.', 1.9, 400, fill=HID) + t(346, 179, 'Plates read as offset; shape inferred.', 1.9, 400, fill=HID) + t(346, 182, 'The pot is not part of objekt.', 1.9, 400, fill=HID)
b += t(24, 252, 'FINISH: brushed stainless (objekt guide: exposed metal). No paint, no colourways.  التشطيب: ستانلس مبروش بدون دهان.', 1.9, 400, fill=HID)
b += t(24, 256, f'All sizes are a PROPOSAL, not costed, Production to confirm. Disc Ø{D}, height {H} (photo proportion), pot hole Ø{2*RH} for the 4 L pot class (rim {POT_RIM}, base {POT_BASE}, height {POT_H}).  المقاسات مقترحة ويؤكدها التصنيع.', 1.9, 400, fill=HID)
sh1 = sheet(1, N, 'VIEWS', 'المناظير', '1:3.7', b)
# ================= SHEET 2: flat patterns =================
S2 = .21
def fp(pts, ox, oy): return [(ox+p[0]*S2, oy+p[1]*S2) for p in pts]
b = t(10, 22, 'Flat patterns at 1:4.8, outside dimensions, bend allowance not applied (Production). Red dash-dot = fold. Same frame as the DXF files.', 2.2, 400, fill=HID) + t(410, 22, 'الأنماط المسطحة، الأبعاد الخارجية، وسماحية الثني من التصنيع.', 2.2, 400, 'end', HID, extra=AR)
o1x, o1y = 14, 36
b += pl(fp(OUT_N, o1x, o1y), .4) + pl(fp(HOLE_N, o1x, o1y), .35, '#fff')
for f in (DN, DN+400): b += line(o1x+f*S2, o1y+(UCN-CH_N/2)*S2-2, o1x+f*S2, o1y+(UCN+CH_N/2)*S2+2, .25, '#b3261e', '3 1 .6 1')
for v, u in tie_holes(DN, UCN): b += circ(o1x+v*S2, o1y+u*S2, HOLE_D/2*S2+.4)
b += t(o1x, o1y-4, '1  NEAR PLATE WITH BASE AND TOP FLANGES, 1 off', 2.4, 600) + t(o1x+LN*S2, o1y-8, 'اللوح القريب بجناحي القاع والسطح، عدد ١', 2.4, 600, 'end', extra=AR)
b += dim_h(o1x, o1x+LN*S2, o1y+2*UCN*S2+9, f'{LN:.0f} developed ({DN:.0f} + {H} + {DN:.0f})', ext=o1y+2*UCN*S2) + dim_v(o1x-6, o1y, o1y+2*UCN*S2, '300', ext=o1x)
b += dim_h(o1x+(DN+ZS)*S2, o1x+(DN+H)*S2, o1y-1, f'{H-ZS}', ext=o1y+(UCN-WH)*S2) if False else ''
b += t(o1x+(DN+ZS)*S2, o1y+UCN*S2-4, f'window {WHD} x {H-ZS}', 1.8, 400, fill=HID) + t(o1x+(DN+400)*S2+3, o1y+UCN*S2-4, f'Ø{2*RH} hole opens to the fold', 1.8, 400, fill=HID)
o2x, o2y = 14, 128
b += pl(fp(OUT_F, o2x, o2y), .4)
for f in (DF, DF+400): b += line(o2x+f*S2, o2y+(UCF-CH_F/2)*S2-2, o2x+f*S2, o2y+(UCF+CH_F/2)*S2+2, .25, '#b3261e', '3 1 .6 1')
for v, u in tie_holes(DF, UCF): b += circ(o2x+v*S2, o2y+u*S2, HOLE_D/2*S2+.4)
b += t(o2x, o2y-4, '2  FAR PLATE WITH BASE AND TOP FLANGES, 1 off', 2.4, 600) + t(o2x+LF*S2+40, o2y-8, 'اللوح البعيد بجناحيه، عدد ١', 2.4, 600, 'end', extra=AR)
b += dim_h(o2x, o2x+LF*S2, o2y+2*UCF*S2+9, f'{LF:.0f} developed ({DF} + {H} + {DF})', ext=o2y+2*UCF*S2) + dim_v(o2x-6, o2y, o2y+2*UCF*S2, f'{2*UCF:.0f}', ext=o2x)
o3x, o3y = 150, 128
b += pl(fp(SH_OUT, o3x, o3y), .4) + line(o3x+(RS+xm)*S2, o3y+arc[0][1]*S2-2, o3x+(RS+xm)*S2, o3y+arc[-1][1]*S2+2, .25, '#b3261e', '3 1 .6 1')
b += t(o3x, o3y-4, '3  SHELF, 1 off', 2.4, 600) + t(o3x+60, o3y-8, 'الرف، عدد ١', 2.4, 600, 'end', extra=AR)
b += dim_h(o3x, o3x+2*RS*S2, o3y+2*RS*S2+7, f'Ø{2*RS} (cut at x = {xm:.0f})', ext=o3y+2*RS*S2) + t(o3x+(RS+xm+3)*S2, o3y+RS*S2+1, f'tab {TAB} folds down', 1.8, 400, fill=HID)
dx, dy = 235, 36
b += t(dx, dy, 'DATA  mm', 2.4, 600) + t(410, dy, 'بيانات', 2.4, 600, 'end', extra=AR)
rows = [('Disc diameter (base and top)', f'{D}'), ('Height to top face of top disc', f'{H}'), ('Sheet thickness (proposal)', f'{T}'),
        ('Pot hole diameter in top disc', f'{2*RH}'), ('Plate positions from disc centre', f'near {XN:.0f}, far {XF:.0f} (mid plane)'),
        ('Gap between plates', f'{GAP}'), ('Shelf height (top face) / diameter', f'{ZS} / {2*RS}'), ('Flange depth near / far', f'{DN:.0f} / {DF}'),
        ('Near plate window', f'{WHD} wide, from {ZS} to {H}'), ('Tie spacer holes', f'4 each plate, Ø{HOLE_D}, at y +-95, z 60 and 340')]
for i, (a_, b_) in enumerate(rows):
    yy = dy+5+i*4.4; b += line(dx, yy+1.4, 410, yy+1.4, .12, HID) + t(dx, yy, a_, 2.0, 400) + t(dx+70, yy, b_, 2.0, 600)
nts = [f'Both plates and both flange pairs fold the same way: flanges point away from the gap.', f'Near plate window leaves 2 side legs of {(CH_N-2*WH)/2:.0f} mm; the pot passes the plate plane there.',
       f'Shelf (3): cut disc with a {TAB} mm tab, tab folds down and is joined to the near plate face under the window. Joint method is Production\'s.',
       'Plates are tied across the gap by 4 spacers (Ø10 tube, 22 long, bolt or weld): bought-in, not drawn in detail.']
for i, ln in enumerate(nts): b += t(dx, dy+55+i*4, ln, 1.8)
b += t(410, dy+73, 'الأجنحة تتجه بعيداً عن الفتحة. الرف بلسان مثني للأسفل. اللوحان مربوطان بأربع قطع تباعد.', 1.8, 400, 'end', extra=AR)
sh2 = sheet(2, N, 'PART SHEET', 'ورقة القطع', '1:4.8', b)
# ================= SHEET 3: assembly =================
b = t(10, 22, 'EXPLODED VIEW, front, parts lifted apart (proposed assembly; Production decides jigs, welds and fixings)', 2.4, 600) + t(410, 22, 'منظر مفكك (تجميع مقترح، والتصنيع يقرر)', 2.4, 600, 'end', extra=AR)
SA = .26; oz3 = 235; c3 = 90
def z3(z): return oz3 - z*SA
# near part C-section side view: plate at x=XN, base flange to -x, top flange to -x
def part_side(cx_, xp, sign, label, ln):
    s = rect(cx_+xp*SA, z3(H), T*SA, H*SA, .35, INK, '#c9cbcd')
    s += rect(cx_+(xp-sign*(DN if sign > 0 else DF))*SA if sign > 0 else cx_+xp*SA, z3(0)-T*SA*1.6, (DN if sign > 0 else DF)*SA, T*SA*1.6, .35, INK, '#d9dbdc')
    return s
b += part_side(c3, XN, 1, 'N', 1) 
# near: flanges extend -x from XN (width DN)
b += rect(c3+(XN-DN)*SA, z3(0)-T*SA*1.6, DN*SA, T*SA*1.6, .35, INK, '#d9dbdc') + rect(c3+(XN-DN)*SA, z3(H)-T*SA*1.6, DN*SA, T*SA*1.6, .35, INK, '#d9dbdc')
b += rect(c3+XN*SA, z3(H), T*SA, H*SA, .35, INK, '#c9cbcd')
# far part moved +x by 70
fx = c3 + 70
b += rect(fx+XF*SA, z3(0)-T*SA*1.6, DF*SA, T*SA*1.6, .35, INK, '#d9dbdc') + rect(fx+XF*SA, z3(H)-T*SA*1.6, DF*SA, T*SA*1.6, .35, INK, '#d9dbdc') + rect(fx+XF*SA, z3(H), T*SA, H*SA, .35, INK, '#c9cbcd')
# shelf lifted 90
b += rect(c3-RS*SA, z3(ZS+90)-T*SA*1.6, (RS+XN-T/2)*SA, T*SA*1.6, .35, INK, '#c9cbcd') + rect(c3+(XN-T/2)*SA-T*SA, z3(ZS+90), T*SA, TAB*SA, .3, INK, '#c9cbcd')
(ax, ay) = (c3+(XN-T/2)*SA, z3(ZS+90)); (bx_, by_) = (c3+(XN-T/2)*SA, z3(ZS))
b += line(ax, ay+TAB*SA, bx_, by_, .2, HID, '1 1')
for (zz_) in (60, 340): b += line(c3+(XN+T)*SA, z3(zz_), fx+XF*SA, z3(zz_), .2, DIM, '1 1') + rect(c3+(XN+T)*SA+.5, z3(zz_)-1.3, (GAP-2*0)*SA*1.0, 2.6, .3, INK, '#e6e2d8')
b += balloon(c3+XN*SA-12, z3(200), 1) + balloon(fx+XF*SA+14, z3(200), 2) + balloon(c3-20, z3(ZS+90), 3) + balloon(c3+XN*SA+8*SA+3, z3(60)+8, 4)
b += t(24, 262, 'Items: 1 near plate, 2 far plate, 3 shelf, 4 tie spacers (4 off). The pot and the plant are not part of objekt.  الأصناف: ١ اللوح القريب، ٢ البعيد، ٣ الرف، ٤ قطع التباعد.', 1.9, 400, fill=HID)
sx0 = 245
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end', extra=AR)
steps = [('Laser cut parts 1, 2 and 3 from the DXF files; deburr all edges.', 'قص القطع ١ و٢ و٣ بالليزر وتنعيم الحواف.'),
         ('Fold parts 1 and 2 at the two fold lines each: flanges away from the gap.', 'ثني القطعتين ١ و٢ عند خطي الثني، الأجنحة بعيداً عن الفتحة.'),
         ('Fold the shelf tab (3) down; join the tab to the near plate under the window at height 280.', 'ثني لسان الرف (٣) للأسفل وتثبيته باللوح القريب عند الارتفاع ٢٨٠.'),
         ('Set the 22 mm gap with the four spacers (4); fix by bolt or weld (Production).', 'ضبط الفتحة ٢٢ مم بأربع قطع تباعد وتثبيتها.'),
         ('Brush to one grain along the long axis; deburr the hole edge. Check the stand sits flat on the floor.', 'تبريش في اتجاه واحد وتنعيم حافة الفتحة والتأكد من ثبات القاعدة.')]
for i, (en, ar) in enumerate(steps):
    yy = 48 + i*17; b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 1.9) + t(410, yy+5, ar, 1.9, 400, 'end', extra=AR)
sh3 = sheet(3, N, 'ASSEMBLY', 'التجميع', 'n/a', b)
# ================= SHEET 4: cutting layout =================
S4 = .1
b = t(10, 22, f'CUTTING LAYOUT on an assumed sheet {SHEET_L} x {SHEET_W} x {T} (proposal, to be confirmed by Production).', 2.4, 600) + t(410, 22, 'مخطط القص على لوح مفترض، يؤكده التصنيع', 2.4, 600, 'end', extra=AR)
ox4, oy4 = 30, 40
b += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6') + t(ox4, oy4-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for k, x, y in NEST:
    outl = PARTS[k][1]; b += pl([(ox4+(x+p[0])*S4, oy4+(y+p[1])*S4) for p in outl], .3)
    if k == 'P1': b += pl([(ox4+(x+p[0])*S4, oy4+(y+p[1])*S4) for p in HOLE_N], .3, '#fff')
    b += t(ox4+(x+BB[k][0]/2)*S4, oy4+(y+BB[k][1]/2)*S4+1, k[1], 3.4, 600, 'middle', '#555')
b += dim_h(ox4, ox4+SHEET_L*S4, oy4+SHEET_W*S4+7, f'{SHEET_L}', ext=oy4+SHEET_W*S4) + dim_v(ox4-6, oy4, oy4+SHEET_W*S4, f'{SHEET_W}', ext=ox4)
b += t(30, 195, f'Three parts, {GP} mm spacing, one corner of the sheet. No offcut is claimed. Part 1 is 862 long developed and 300 wide.', 2.3)
b += t(30, 200, f'Total cutting length: {TOTAL_CUT/1000:.2f} m ({TOTAL_CUT:.0f} mm): P1 {LEN_N:.0f} + P2 {LEN_F:.0f} + P3 {LEN_S:.0f}.', 2.5, 600)
b += t(410, 195, 'ثلاث قطع بمسافة ١٠ مم. لا يُدّعى أي هالك.', 2.3, 400, 'end', extra=AR) + t(410, 200, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.5, 600, 'end', extra=AR)
sh4 = sheet(4, N, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)
# ================= SHEET 5: BOM and notes =================
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + t(410, 28, 'قائمة المواد', 2.8, 600, 'end', extra=AR)
b += rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Near plate with flanges (window)', 'اللوح القريب بالجناحين', '1', 'Stainless sheet 2 mm (proposal)'), ('2', 'Far plate with flanges', 'اللوح البعيد', '1', 'Stainless sheet 2 mm (proposal)'),
       ('3', 'Shelf with tab', 'الرف بلسان', '1', 'Stainless sheet 2 mm (proposal)'), ('4', 'Tie spacer Ø10 x 22 + fixing', 'قطعة تباعد وتثبيت', '4', 'Stainless, bought-in or turned (Production)')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*7
    b += line(10, yy+2.2, 410, yy+2.2, .15, HID) + t(12, yy, n_, 2.4) + t(24, yy, en, 2.4) + t(140, yy, ar, 2.4, 400, 'end', extra=AR) + t(150, yy, q, 2.4) + t(215, yy, m_, 2.4)
b += t(10, 80, 'NOTES', 2.8, 600) + t(410, 80, 'ملاحظات', 2.8, 600, 'end', extra=AR)
nts = [('Reference: third-party photos (maker unknown). Drawn as objekt\'s own design. Plates read as offset from the disc centre; the gap and offset are inferred and need Sabry\'s confirmation.', 'المرجع صور لصانع مجهول. مرسوم كتصميم خاص. موضع اللوحين مستنتج ويحتاج تأكيد سبري.'),
       (f'Pot (not ours): 4 L class, rim {POT_RIM}, base {POT_BASE}, height {POT_H} (size-charts.com 4 L pot: 20 cm rim, 15.5 cm base, 16.5 cm high). Hole Ø{2*RH} lets the rim through; shelf Ø{2*RS} carries the base. Pots of 19 to 22 cm rim: Production to confirm the hole.', 'الأصيص ليس من منتجنا. الفتحة ٢٠٤ مم والرف ١٧٦ مم.'),
       ('Height, disc diameter, 2 mm sheet, gap 22, shelf height 280 and all sizes are a PROPOSAL, not costed, Production to confirm.', 'كل المقاسات مقترحة ويؤكدها التصنيع.'),
       ('Shelf joint: the shelf carries the pot on a short tab (about 73 x 20) against the near plate. Production to say whether a larger joint, a thicker shelf or a support is needed. No load figure is given.', 'وصلة الرف: التصنيع يحدد إن كانت تحتاج دعماً. لا أرقام أحمال.'),
       ('Stability: equal base and top diameter, so a downward push on the top disc cannot tip it. Side push and the pot weight are Production\'s to test; heavier base or ballast is proposed to confirm. Levelling not needed.', 'الثبات: قطر القاعدة والسطح متساويان. الاختبار من التصنيع.'),
       ('Finish: brushed stainless, no paint (objekt guide: exposed metal, brushed). Brushing direction and weld finish by Production.', 'التشطيب: ستانلس مبروش بدون دهان.'),
       ('Material, thickness, bend allowance, tolerances, sheet size, joints, welding and finish details are Production\'s to decide.', 'الخامة والسماكة والسماحيات واللحام يقررها التصنيع.'),
       ('No structural claims, stress or load figures, costs or prices. Not engineered. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا تكاليف. الصياغة العربية مسودة.')]
for i, (en, ar) in enumerate(nts):
    yy = 89 + i*13; b += t(12, yy, f'{i+1}.', 2.4, 600) + t(18, yy, en, 2.0) + t(410, yy+5, ar, 2.0, 400, 'end', extra=AR)
sh5 = sheet(5, N, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)
for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1):
    open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('WH', WH, 'XN', XN, 'XF', XF, 'CH', round(CH_N), round(CH_F), 'DN', round(DN), 'shelf neck', round(2*SH_HW), 'L', round(LN), 'cut', round(TOTAL_CUT))
