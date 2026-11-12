"""OBJ-196: plant stand, flat round base disc, two vertical plates, round top disc, shelf disc. Production drawing set, REV 1 (DRAFT).
Run: python3 make_obj196_rev1.py <repo root>   Then: NODE_PATH=<playwright> node make_pdf.js <dir> OBJ-196 1
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
REV = 1; DATE = '12 Nov 2026'; PN = 'OBJ-196'
D, R, H, T = 300, 150, 400, 2          # disc diameter, radius, height to top face of top disc, sheet
POT_RIM, POT_BASE, POT_H = 200, 155, 165   # reference pot (size-charts.com 4 L), NOT part of the product
RH = 102                               # hole radius in top disc = pot rim 100 + 2 clearance
GAP = 22; XP = GAP/2 + T/2             # plate mid plane at +-12 from the centre; gap centred
ZS = 280                               # shelf top height; pot rim then at 445 = 45 above the top disc
RS = 88                                # shelf radius (pot base 77.5 + 10)
WH = math.sqrt(RH**2 - XP**2); WHD = round(2*WH)    # window half width in each plate (about 101)
CH = 2*math.sqrt(R**2 - XP**2)         # plate width = chord at the plate (about 299)
DEP = round(R - XP)                    # flange depth 138
LEG = (CH - 2*WH)/2
SH_HW = math.sqrt(RS**2 - (XP+T/2)**2) # half shelf neck width
TAB = 20
HOLE_D = 5.5; TIE = [(-125, 60), (125, 60), (-125, 340), (125, 340)]   # tie spacer holes (y, z), in the leg strips
SHEET_L, SHEET_W, GP = 2500, 1250, 10
def seg(x0): return math.sqrt(max(R*R - x0*x0, 0))
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
UC = 150
def outer():
    left = [(v, UC - seg(R - v)) for v in [DEP*i/40 for i in range(41)]]            # base flange; v=0 is the free edge at x=R
    left += [(DEP, UC - CH/2), (DEP+H, UC - CH/2)]
    left += [(DEP+H+d, UC - seg(XP + d)) for d in [DEP*i/40 for i in range(41)]]
    right = [(v, 2*UC - y) for v, y in left]
    return left + right[::-1]
SHD = RS - (XP + T/2)                                   # shelf flange depth (75): from the plate outer face to the shelf edge
def sh_hw(d): return math.sqrt(max(RS*RS - (XP + T/2 + d)**2, 0))
SHN = sh_hw(0)                                          # shelf neck half width at the bend (about 87)
def hole():
    """window + top-flange bite + the shelf flange as a peninsula standing in the window"""
    a0 = math.acos(XP/RH); n = 48
    pts = [(DEP+ZS, UC-SHN)]                                                 # sill, left of the shelf neck
    pts += [(DEP+ZS, UC-WH)]
    pts += [(DEP+H, UC-WH)]
    pts += [(DEP+H + (RH*math.cos(a) - XP), UC - RH*math.sin(a)) for a in [a0 - a0*i/n for i in range(n+1)]]
    pts += [(DEP+H + (RH*math.cos(a) - XP), UC + RH*math.sin(a)) for a in [a0*i/n for i in range(n+1)]]
    pts += [(DEP+H, UC+WH), (DEP+ZS, UC+WH), (DEP+ZS, UC+SHN)]
    pts += [(DEP+ZS+d, UC + sh_hw(d)) for d in [SHD*i/40 for i in range(41)]]
    pts += [(DEP+ZS+d, UC - sh_hw(d)) for d in [SHD*(40-i)/40 for i in range(41)]]
    return pts
OUT_P = outer(); HOLE_P = hole(); LP = DEP + H + DEP
def plen(pts): return sum(math.dist(pts[i], pts[(i+1) % len(pts)]) for i in range(len(pts)))
LEN_P = plen(OUT_P) + plen(HOLE_P) + 4*math.pi*HOLE_D
TOTAL_CUT = 2*LEN_P
NEST = [('P1', GP, GP), ('P1', GP, GP + 300 + GP)]
BB = (LP, 300)
for k, x, y in NEST: assert x + BB[0] <= SHEET_L and y + BB[1] <= SHEET_W
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4
    d.layers.add('CUT', color=7); d.layers.add('FOLD', color=5); d.layers.add('SHEET', color=3); return d
def add_part(msp, ox, oy):
    msp.add_lwpolyline([(ox+p[0], oy+p[1]) for p in OUT_P], close=True, dxfattribs={'layer': 'CUT'})
    msp.add_lwpolyline([(ox+p[0], oy+p[1]) for p in HOLE_P], close=True, dxfattribs={'layer': 'CUT'})
    for y, z in TIE: msp.add_circle((ox+DEP+z, oy+UC+y), HOLE_D/2, dxfattribs={'layer': 'CUT'})
    for f in (DEP, DEP+H): msp.add_line((ox+f, oy+UC-CH/2), (ox+f, oy+UC+CH/2), dxfattribs={'layer': 'FOLD'})
    msp.add_line((ox+DEP+ZS, oy+UC-SHN), (ox+DEP+ZS, oy+UC+SHN), dxfattribs={'layer': 'FOLD'})
doc = new_doc(); add_part(doc.modelspace(), 0, 0); doc.saveas(f'{OUT}/{PN}_rev{REV}_P1_plate-with-flanges.dxf')
doc = new_doc(); m = doc.modelspace()
m.add_lwpolyline([(0, 0), (SHEET_L, 0), (SHEET_L, SHEET_W), (0, SHEET_W)], close=True, dxfattribs={'layer': 'SHEET'})
for k, x, y in NEST: add_part(m, x, y)
doc.saveas(f'{OUT}/{PN}_rev{REV}_nest_{SHEET_L}x{SHEET_W}.dxf')

N = 5
def circ(cx, cy, r): return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="#fff" stroke="{INK}" stroke-width=".35"/>'
def pl(pts, sw=.35, fill=FILL, dash=None, col=INK): return poly(pts, sw, col, fill, dash)
S = .27; oz = 215
def zz(z): return oz - z*S
# ================= SHEET 1: views =================
b = t(24, 26, 'FRONT (looking along the plates)', 2.6, 600) + t(130, 29.5, 'الأمامي (بمحاذاة اللوحين)', 2.4, 500, 'end', extra=AR)
cx = 80
b += rect(cx-R*S, zz(0)-T*S*1.6, D*S, T*S*1.6, .4, INK, '#d9dbdc') + rect(cx-R*S, zz(H)-T*S*1.6, D*S, T*S*1.6, .4, INK, '#d9dbdc')
for sgn in (1, -1):
    b += rect(cx+(sgn*XP-T/2)*S, zz(H), T*S, H*S, .35, INK, '#c9cbcd')
    x0 = sgn*(XP+T/2); x1 = sgn*RS
    b += rect(min(cx+x0*S, cx+x1*S), zz(ZS)-T*S*1.6, abs(x1-x0)*S, T*S*1.6, .35, INK, '#c9cbcd')
potpts = [(cx-POT_RIM/2*S, zz(ZS+POT_H)), (cx+POT_RIM/2*S, zz(ZS+POT_H)), (cx+POT_BASE/2*S, zz(ZS)), (cx-POT_BASE/2*S, zz(ZS))]
b += pl(potpts, .3, 'none', '1.4 .9', HID) + t(cx-POT_RIM/2*S, zz(ZS+POT_H)-1.5, 'pot (not ours)', 1.8, 400, fill=HID)
b += dim_v(cx-R*S-8, zz(H), zz(0), f'{H}', ext=cx-R*S) + dim_h(cx-R*S, cx+R*S, zz(0)+7, f'Ø{D}', ext=zz(0))
b += dim_h(cx-GAP/2*S, cx+GAP/2*S, zz(H)-6, f'gap {GAP}', ext=zz(H))
b += dim_v(cx+R*S+8, zz(ZS), zz(0), f'{ZS}', ext=cx+RS*S) + balloon(cx+XP*S+14, zz(120), 1) + balloon(cx-XP*S-14, zz(120), 1) + balloon(cx+RS*S-6, zz(ZS)-6, 2)
sx = 205
b += t(sx-30, 26, 'SIDE (face of one plate)', 2.6, 600) + t(sx+75, 29.5, 'الجانبي', 2.4, 500, 'end', extra=AR)
b += rect(sx-CH/2*S, zz(H), CH*S, H*S, .4, INK, '#d9dbdc') + rect(sx-WH*S, zz(H), WH*2*S, (H-ZS)*S, .35, INK, '#fff')
b += rect(sx-R*S, zz(0)-T*S*1.6, D*S, T*S*1.6, .4, INK, '#c0c3c5') + rect(sx-R*S, zz(H)-T*S*1.6, D*S, T*S*1.6, .4, INK, '#c0c3c5')
b += dim_h(sx-CH/2*S, sx+CH/2*S, zz(H)-5, f'{CH:.0f}', ext=zz(H)) + t(sx-WH*S, zz(H)+(H-ZS)*S/2, f'window {WHD} wide, {H-ZS} high', 1.9, 400, fill=HID)
b += t(sx-WH*S, zz(H)+(H-ZS)*S/2+4, f'legs {LEG:.0f} each side', 1.9, 400, fill=HID)
px, py = 325, 90; P_ = .27
b += t(px-30, 26, 'PLAN', 2.6, 600) + t(px+30, 29.5, 'المسقط الأفقي', 2.4, 500, 'end', extra=AR)
b += circ(px, py, R*P_) + circ(px, py, RH*P_) + circ(px, py, POT_BASE/2*P_) + f'<circle cx="{px}" cy="{py}" r="{RS*P_:.2f}" fill="none" stroke="{HID}" stroke-width=".25" stroke-dasharray="1.2 .8"/>'
for sgn in (1, -1): b += rect(px+(sgn*XP-T/2)*P_, py-CH/2*P_, T*P_, CH*P_, .3, INK, '#c9cbcd')
b += dim_h(px-R*P_, px+R*P_, py+R*P_+8, f'Ø{D}', ext=py+R*P_) + dim_h(px-RH*P_, px+RH*P_, py-R*P_-5, f'hole Ø{2*RH}', ext=py-RH*P_)
b += t(px-44, py+R*P_+17, f'Plates at x = +-{XP:.0f} (gap {GAP} centred); shelf flanges Ø{2*RS} fold outward.', 1.9, 400, fill=HID)
b += t(300, 166, 'REFERENCE PHOTO (third-party, maker unknown)', 2.1, 600) + t(410, 166, 'صورة مرجعية (ليست لنا)', 2.1, 500, 'end', extra=AR)
b += f'<image href="{datauri(PHOTO, 300)}" x="300" y="170" width="42" height="56" preserveAspectRatio="xMidYMid slice"/>' + rect(300, 170, 42, 56, .2, HID)
b += t(346, 176, 'Photo shows brushed stainless.', 1.9, 400, fill=HID) + t(346, 179, 'Centred gap, mirrored halves (Sabry).', 1.9, 400, fill=HID) + t(346, 182, 'The pot is not part of objekt.', 1.9, 400, fill=HID)
b += t(24, 252, 'FINISH: brushed stainless (objekt guide: exposed metal). No paint, no colourways.  التشطيب: ستانلس مبروش بدون دهان.', 1.9, 400, fill=HID)
b += t(24, 256, f'All sizes are a PROPOSAL, not costed, Production to confirm. Disc Ø{D}, height {H}, pot hole Ø{2*RH} for the 4 L pot class (rim {POT_RIM}, base {POT_BASE}, height {POT_H}).  المقاسات مقترحة ويؤكدها التصنيع.', 1.9, 400, fill=HID)
sh1 = sheet(1, N, 'VIEWS', 'المناظير', '1:3.7', b)
# ================= SHEET 2: flat pattern =================
S2 = .3
def fp(pts, ox, oy): return [(ox+p[0]*S2, oy+p[1]*S2) for p in pts]
o1x, o1y = 14, 45
b = t(10, 22, 'Flat pattern at 1:2.4, outside dimensions, bend allowance not applied (Production). Red dash-dot = fold. Same frame as the DXF files.', 2.2, 400, fill=HID) + t(410, 22, 'النمط المسطح، الأبعاد الخارجية، وسماحية الثني من التصنيع.', 2.2, 400, 'end', HID, extra=AR)
b += pl(fp(OUT_P, o1x, o1y), .4) + pl(fp(HOLE_P, o1x, o1y), .35, '#fff')
for f in (DEP, DEP+H): b += line(o1x+f*S2, o1y+(UC-CH/2)*S2-2, o1x+f*S2, o1y+(UC+CH/2)*S2+2, .25, '#b3261e', '3 1 .6 1')
b += line(o1x+(DEP+ZS)*S2, o1y+(UC-SHN)*S2, o1x+(DEP+ZS)*S2, o1y+(UC+SHN)*S2, .25, '#b3261e', '3 1 .6 1')
for y, z in TIE: b += circ(o1x+(DEP+z)*S2, o1y+(UC+y)*S2, HOLE_D/2*S2+.4)
b += t(o1x, o1y-4, '1  PLATE WITH BASE FLANGE, TOP FLANGE AND SHELF FLANGE, 2 off (identical; one turned 180 degrees)', 2.4, 600) + t(o1x+LP*S2, o1y-8, 'اللوح بجناح القاع والسطح والرف، عدد ٢ (متطابقان)', 2.4, 600, 'end', extra=AR)
b += dim_h(o1x, o1x+LP*S2, o1y+300*S2+9, f'{LP} developed ({DEP} + {H} + {DEP})', ext=o1y+300*S2) + dim_v(o1x-6, o1y, o1y+300*S2, '300', ext=o1x)
b += dim_h(o1x+DEP*S2, o1x+(DEP+H)*S2, o1y+300*S2+17, f'{H} plate height', ext=o1y+300*S2) if False else ''
b += t(o1x+(DEP+ZS+10)*S2, o1y+UC*S2+1.5, f'shelf flange folds out of the window (Ø{2*RS})', 1.8, 400, fill=HID)
dx, dy = 235, 80
b += t(dx, dy, 'DATA  mm', 2.4, 600) + t(410, dy, 'بيانات', 2.4, 600, 'end', extra=AR)
rows = [('Disc diameter (base and top)', f'{D}'), ('Height to top face of top disc', f'{H}'), ('Sheet thickness (proposal)', f'{T}'), ('Gap between plates (centred)', f'{GAP}'),
        ('Plate mid planes from centre', f'+-{XP:.0f}'), ('Pot hole diameter in top disc', f'{2*RH}'), ('Shelf height (top face) / diameter', f'{ZS} / {2*RS}'),
        ('Flange depth (base, top)', f'{DEP}'), ('Plate window', f'{WHD} wide, from {ZS} to {H}'), ('Leg strip each side', f'{LEG:.0f}'), ('Tie spacer holes', f'4 each plate, Ø{HOLE_D}, y +-125, z 60, 340')]
for i, (a_, b_) in enumerate(rows):
    yy = dy+5+i*4.4; b += line(dx, yy+1.4, 410, yy+1.4, .12, HID) + t(dx, yy, a_, 2.0, 400) + t(dx+70, yy, b_, 2.0, 600)
nts = ['The two plates are the same part: turn one 180 degrees about the vertical axis. Flanges point away from the gap.', f'The shelf flange is bent from the window sill (height {ZS}); the pot base rests on both shelf flanges, with a {GAP} mm slot between them.',
       'Plates are tied across the gap by 4 spacers (Ø10 tube, 22 long, bolt or weld): bought-in, not drawn in detail.']
for i, ln in enumerate(nts): b += t(dx, dy+60+i*4, ln, 1.8)
b += t(410, dy+74, 'اللوحان متطابقان، أحدهما مدار ١٨٠ درجة. جناح الرف مثني من عتبة الفتحة. أربع قطع تباعد.', 1.8, 400, 'end', extra=AR)
sh2 = sheet(2, N, 'PART SHEET', 'ورقة القطع', '1:2.4', b)
# ================= SHEET 3: assembly =================
SA = .26; oz3 = 235; c3 = 105
def z3(z): return oz3 - z*SA
b = t(10, 22, 'EXPLODED VIEW, front, plates moved apart (proposed assembly; Production decides jigs, welds and fixings)', 2.4, 600) + t(410, 22, 'منظر مفكك (تجميع مقترح، والتصنيع يقرر)', 2.4, 600, 'end', extra=AR)
for sgn, off in ((-1, -35), (1, 35)):
    px_ = c3 + off + sgn*XP*SA*0
    xp = sgn*XP
    b += rect(px_+(xp-T/2)*SA, z3(H), T*SA, H*SA, .35, INK, '#c9cbcd')
    b += rect(px_+((xp-T/2) if sgn > 0 else xp-DEP)*SA if False else px_+((xp+T/2) if sgn > 0 else xp-T/2-DEP)*SA, z3(0)-T*SA*1.6, DEP*SA, T*SA*1.6, .35, INK, '#d9dbdc')
    b += rect(px_+((xp+T/2) if sgn > 0 else xp-T/2-DEP)*SA, z3(H)-T*SA*1.6, DEP*SA, T*SA*1.6, .35, INK, '#d9dbdc')
    b += rect(px_+((xp+T/2) if sgn > 0 else xp-T/2-SHD)*SA, z3(ZS)-T*SA*1.6, SHD*SA, T*SA*1.6, .35, INK, '#c9cbcd')
    b += balloon(px_+xp*SA+(14 if sgn > 0 else -14), z3(150), 1)
for zz_ in (60, 340): b += line(c3-35+XP*SA, z3(zz_), c3+35-XP*SA, z3(zz_), .2, DIM, '1 1') + rect(c3-10, z3(zz_)-1.3, 20, 2.6, .3, INK, '#e6e2d8')
b += balloon(c3, z3(60)+8, 2)
b += t(24, 262, 'Items: 1 plate (2 off, identical), 2 tie spacer (4 off). The pot and the plant are not part of objekt.  الأصناف: ١ اللوح (عدد ٢ متطابقان)، ٢ قطعة التباعد (٤).', 1.9, 400, fill=HID)
sx0 = 245
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end', extra=AR)
steps = [('Laser cut two plates (1) from the DXF file; deburr all edges.', 'قص لوحين (١) بالليزر وتنعيم الحواف.'),
         ('Fold each plate at the three fold lines: base flange, top flange, shelf flange (all away from the gap).', 'ثني كل لوح عند خطوط الثني الثلاثة، الأجنحة بعيداً عن الفتحة.'),
         ('Stand the two plates facing each other with a 22 mm gap (one turned 180 degrees).', 'وضع اللوحين متقابلين بفتحة ٢٢ مم (أحدهما مدار ١٨٠ درجة).'),
         ('Fix the four spacers (2) through the leg strips by bolt or weld (Production).', 'تثبيت قطع التباعد الأربع في الأرجل بمسمار أو لحام.'),
         ('Brush to one grain; deburr the hole edge. Check the stand sits flat on the floor.', 'تبريش في اتجاه واحد وتنعيم حافة الفتحة والتأكد من ثبات القاعدة.')]
for i, (en, ar) in enumerate(steps):
    yy = 48 + i*17; b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 1.9) + t(410, yy+5, ar, 1.9, 400, 'end', extra=AR)
sh3 = sheet(3, N, 'ASSEMBLY', 'التجميع', 'n/a', b)
# ================= SHEET 4: cutting layout =================
S4 = .1
b = t(10, 22, f'CUTTING LAYOUT on an assumed sheet {SHEET_L} x {SHEET_W} x {T} (proposal, to be confirmed by Production).', 2.4, 600) + t(410, 22, 'مخطط القص على لوح مفترض، يؤكده التصنيع', 2.4, 600, 'end', extra=AR)
ox4, oy4 = 30, 40
b += rect(ox4, oy4, SHEET_L*S4, SHEET_W*S4, .5, '#2f6b45', '#fbfaf6') + t(ox4, oy4-2, f'SHEET {SHEET_L} x {SHEET_W}', 2.2, 600, fill='#2f6b45')
for k, x, y in NEST:
    b += pl([(ox4+(x+p[0])*S4, oy4+(y+p[1])*S4) for p in OUT_P], .3) + pl([(ox4+(x+p[0])*S4, oy4+(y+p[1])*S4) for p in HOLE_P], .3, '#fff')
    b += t(ox4+(x+60)*S4, oy4+(y+150)*S4+1, '1', 3.4, 600, 'middle', '#555')
b += dim_h(ox4, ox4+SHEET_L*S4, oy4+SHEET_W*S4+7, f'{SHEET_L}', ext=oy4+SHEET_W*S4) + dim_v(ox4-6, oy4, oy4+SHEET_W*S4, f'{SHEET_W}', ext=ox4)
b += t(30, 195, f'Two identical parts, {GP} mm spacing, one corner of the sheet. No offcut is claimed. Each part is {LP} long developed and 300 wide.', 2.3)
b += t(30, 200, f'Total cutting length: {TOTAL_CUT/1000:.2f} m ({TOTAL_CUT:.0f} mm): 2 x {LEN_P:.0f}.', 2.5, 600)
b += t(410, 195, 'قطعتان متطابقتان بمسافة ١٠ مم. لا يُدّعى أي هالك.', 2.3, 400, 'end', extra=AR) + t(410, 200, f'إجمالي طول القص: {TOTAL_CUT/1000:.2f} متر', 2.5, 600, 'end', extra=AR)
sh4 = sheet(4, N, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)
# ================= SHEET 5: BOM and notes =================
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + t(410, 28, 'قائمة المواد', 2.8, 600, 'end', extra=AR)
b += rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Plate with base, top and shelf flanges', 'اللوح بثلاثة أجنحة', '2', 'Stainless sheet 2 mm (proposal), identical'), ('2', 'Tie spacer Ø10 x 22 + fixing', 'قطعة تباعد وتثبيت', '4', 'Stainless, bought-in or turned (Production)')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*7
    b += line(10, yy+2.2, 410, yy+2.2, .15, HID) + t(12, yy, n_, 2.4) + t(24, yy, en, 2.4) + t(140, yy, ar, 2.4, 400, 'end', extra=AR) + t(150, yy, q, 2.4) + t(215, yy, m_, 2.4)
b += t(10, 70, 'NOTES', 2.8, 600) + t(410, 70, 'ملاحظات', 2.8, 600, 'end', extra=AR)
nts = [('Reference: third-party photos (maker unknown). Drawn as objekt\'s own design. Layout (Sabry, 12 Nov): gap in the centre, two mirrored halves; rev 0 had off-centre plates and is superseded.', 'المرجع صور لصانع مجهول. التصميم: فتحة في المنتصف ونصفان متماثلان (سبري).'),
       (f'Pot (not ours): 4 L class, rim {POT_RIM}, base {POT_BASE}, height {POT_H} (size-charts.com 4 L pot: 20 cm rim, 15.5 cm base, 16.5 cm high). Hole Ø{2*RH}; the pot passes both plate windows and stands on the two shelf flanges (Ø{2*RS}). 19 to 22 cm rims: Production to confirm the hole.', 'الأصيص ليس من منتجنا. الفتحة ٢٠٤ مم. جناحا الرف قطرهما ١٧٦ مم.'),
       ('Disc, height, 2 mm sheet, gap 22, shelf height 280 and all sizes are a PROPOSAL, not costed, Production to confirm.', 'كل المقاسات مقترحة ويؤكدها التصنيع.'),
       (f'Each plate is a frame of two {LEG:.0f} mm leg strips plus the sill. Production to say if that holds the pot and soil, or if thicker sheet, a cross tie or a heavier shelf bend is needed. No load figure is given.', 'كل لوح له ساقان ضيقتان. التصنيع يحدد إن كانت كافية. لا أرقام أحمال.'),
       ('Stability: equal base and top diameter, so a downward push on the top disc cannot tip it. Side push and pot weight are Production\'s to test; heavier base or ballast to confirm. Levelling not needed.', 'الثبات: قطر القاعدة والسطح متساويان. الاختبار من التصنيع.'),
       ('Finish: brushed stainless, no paint (objekt guide: exposed metal, brushed). Brushing direction and weld finish by Production.', 'التشطيب: ستانلس مبروش بدون دهان.'),
       ('Material, thickness, bend allowance, tolerances, sheet size, joints, welding and finish details are Production\'s to decide.', 'الخامة والسماكة والسماحيات واللحام يقررها التصنيع.'),
       ('No structural claims, stress or load figures, costs or prices. Not engineered. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا تكاليف. الصياغة العربية مسودة.')]
for i, (en, ar) in enumerate(nts):
    yy = 79 + i*13; b += t(12, yy, f'{i+1}.', 2.4, 600) + t(18, yy, en, 2.0) + t(410, yy+5, ar, 2.0, 400, 'end', extra=AR)
sh5 = sheet(5, N, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)
for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1):
    open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('WH', round(WH,1), 'CH', round(CH), 'DEP', DEP, 'LEG', round(LEG), 'SHN', round(SHN), 'L', LP, 'cut', round(TOTAL_CUT))
