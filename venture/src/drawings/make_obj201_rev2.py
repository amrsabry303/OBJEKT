"""OBJ-201: plant stand, flat round base disc, two vertical plates, round top disc, shelf disc. Production drawing set, REV 2 (approved by Sabry 25 Nov 2026: same geometry as rev 1, more views, separated sheets).
Run: python3 make_obj201_rev2.py <repo root>   Then: NODE_PATH=<playwright> node make_pdf.js <dir> OBJ-201 1
Reference: images/OBJ-201.jpg (stainless) plus a second angle Sabry sent in the session (blue, not stored in the repo). Third-party, maker unknown; drawn as objekt's own design.
READING OF THE REFERENCE (inferred, to confirm): the two plates are parallel with a narrow gap, OFFSET from the disc centre (photo 2: gap about 0.26 D off centre).
The near plate carries the big segment of the base disc and of the top disc; the far plate the small segment. The pot stands on a shelf and goes through a round hole in the top disc.
Every size is a PROPOSAL, not costed, Production to confirm. Pot sizes from size-charts.com 4 L pot (rim 20 cm, base 15.5 cm, height 16.5 cm). Arabic is a draft. No costs, no structural claims."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-201'; os.makedirs(OUT, exist_ok=True)
PHOTO = ROOT + '/images/OBJ-201.jpg'
REV = 2; DATE = '12 Nov 2026'; PN = 'OBJ-201'
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



STAMP = 'Approved by Sabry 25 Nov 2026. Production review pending. Not engineered'; STAMP_AR = 'معتمد من سبري ٢٥ نوفمبر ٢٠٢٦، بانتظار مراجعة التصنيع، غير مهندس'
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

N = 10
CUT = '#161616'
HATCH = '<defs><pattern id="hatch" width="1.3" height="1.3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="1.3" stroke="#161616" stroke-width=".25"/></pattern></defs>'
def circ(cx, cy, r): return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="#fff" stroke="{INK}" stroke-width=".35"/>'
def pl(pts, sw=.35, fill=FILL, dash=None, col=INK): return poly(pts, sw, col, fill, dash)
def arcp(r, a0, a1, n=60): return [(r*math.cos(a0+(a1-a0)*i/n), r*math.sin(a0+(a1-a0)*i/n)) for i in range(n+1)]
HH = math.sqrt(R*R - XP*XP)                      # half chord at the fold (about 149.5)
def seg_pts(x0, xe, sgn):
    """half disc segment: from the fold line x = sgn*x0 outward to radius R, plan outline (x,y) points, sgn=-1 N plate side (x<0), +1 F"""
    a = math.acos(x0/R)
    pts = [(R*math.cos(t_), R*math.sin(t_)) for t_ in [(-a + 2*a*i/80) for i in range(81)]]    # arc on +x side
    pts = [(x*sgn, y) for x, y in pts]
    return pts
def top_flange(sgn):
    """top flange outline in plan incl. the bite for the pot hole"""
    arc = seg_pts(XP, R, sgn)                         # from (sgn*XP,-HH) round to (sgn*XP,+HH)
    a0 = math.atan2(WH, XP)
    bite = [(sgn*RH*math.cos(a0 - 2*a0*i/60), RH*math.sin(a0 - 2*a0*i/60)) for i in range(61)]   # from (sgn*XP,+WH) to (sgn*XP,-WH) through (sgn*RH,0)
    return arc + [(sgn*XP, HH)][:0] + [(sgn*XP, WH)] + bite[1:-1] + [(sgn*XP, -WH)]
def base_flange(sgn): return seg_pts(XP, R, sgn)
def shelf_seg(sgn):
    a = math.acos(XP/RS)
    return [(sgn*RS*math.cos(t_), RS*math.sin(t_)) for t_ in [(-a + 2*a*i/60) for i in range(61)]]
# ---------- 3D iso ----------
def iso(az_deg, el_deg, ox, oy, S):
    az, el = math.radians(az_deg), math.radians(el_deg)
    def P3(x, y, z):
        xr = x*math.cos(az) - y*math.sin(az); yr = x*math.sin(az) + y*math.cos(az)
        return ox + xr*S, oy - (z*math.cos(el) + yr*math.sin(el))*S
    return P3
def part3d(sgn, dx=0):
    """list of (name, [(x,y,z)...], fill) back to front inside one plate part; sgn=-1 is N (x<0), +1 is F"""
    X = lambda x: x + dx
    out = []
    out.append(('base', [(X(x), y, 0) for x, y in base_flange(sgn)], '#d6d8da'))
    out.append(('plate', [(X(sgn*XP), y, z) for y, z in [(-HH, 0), (HH, 0), (HH, H), (WH, H), (WH, ZS), (-WH, ZS), (-WH, H), (-HH, H)]], '#c4c7ca'))
    out.append(('shelf', [(X(x), y, ZS) for x, y in shelf_seg(sgn)], '#e4e6e8'))
    out.append(('top', [(X(x), y, H) for x, y in top_flange(sgn)], '#eceeef'))
    return out
def draw_iso(P3, near_sgn, dx=0, spacers=False):
    far = -near_sgn
    s = ''
    parts = {sg: dict((n, (pts, f)) for n, pts, f in part3d(sg, dx*sg)) for sg in (-1, 1)}
    def drw(sg, n):
        pts, f = parts[sg][n]; return pl([P3(*q) for q in pts], .3, f)
    for n in ('base', 'shelf', 'top', 'plate'): s += drw(far, n) if n != 'plate' else ''
    s += drw(far, 'plate')
    if spacers:
        for yy, zz_ in [(-125, 60), (125, 60), (-125, 340), (125, 340)]:
            x0, x1 = -10, 10
            a, b, c, d = P3(x0, yy-5, zz_-5), P3(x1, yy-5, zz_-5), P3(x1, yy+5, zz_+5), P3(x0, yy+5, zz_+5)
            s += pl([P3(x0, yy-5, zz_-5), P3(x1, yy-5, zz_-5), P3(x1, yy-5, zz_+5), P3(x0, yy-5, zz_+5)], .3, '#b9bcbf') + pl([P3(x0, yy-5, zz_+5), P3(x1, yy-5, zz_+5), P3(x1, yy+5, zz_+5), P3(x0, yy+5, zz_+5)], .3, '#d4d6d8')
    s += drw(near_sgn, 'plate')
    for n in ('base', 'shelf', 'top'): s += drw(near_sgn, n)
    return s

def tt(x, y, en, ar=None, size=2.2, w=400, fill=INK, wd=0):
    s = t(x, y, en, size, w, fill=fill)
    if ar: s += t(x+wd, y+size*1.35, ar, size, w, 'end', fill, extra=AR)
    return s
def title(x, y, en, ar, wd):
    return t(x, y, en, 2.9, 700) + t(x+wd, y, ar, 2.9, 700, 'end', extra=AR)
SHEETS = [(1,'OVERVIEW','نظرة عامة'),(2,'FRONT AND SIDE VIEWS','الواجهة الأمامية والجانبية'),(3,'PLAN AND UNDERSIDE','المسقط الأفقي والقاع'),
          (4,'SECTIONS, HORIZONTAL (A, B, C)','مقاطع أفقية'),(5,'SECTIONS, VERTICAL (D, E)','مقاطع رأسية'),(6,'DETAILS','تفاصيل'),
          (7,'PART SHEET (FLAT PATTERN)','ورقة القطع'),(8,'ASSEMBLY','التجميع'),(9,'CUTTING LAYOUT','مخطط القص'),(10,'BILL OF MATERIALS AND NOTES','قائمة المواد والملاحظات')]
# ================= SHEET 1: overview =================
b = HATCH
b += title(14, 27, 'ISOMETRIC A (from the -x side)', 'منظور أيزومتري أ', 200)
b += draw_iso(iso(35, 28, 110, 200, .27), -1)
b += title(232, 27, 'ISOMETRIC B (from the +x side)', 'منظور أيزومتري ب', 178)
b += draw_iso(iso(-145, 28, 320, 112, .17), +1)
b += t(232, 33, 'Two identical plates; the second is the first turned 180 degrees. Pot and plant not shown.', 1.9, 400, fill=HID)
ix, iy = 232, 128
b += t(ix, iy, 'SHEET INDEX', 2.7, 700) + t(410, iy, 'فهرس الأوراق', 2.7, 700, 'end', extra=AR)
for i_, (k, en, ar) in enumerate(SHEETS):
    yy = iy + 5.5 + i_*4.4
    b += line(ix, yy+1.4, 410, yy+1.4, .1, HID) + t(ix, yy, f'{k:>2}   {en}', 2.0, 400 if k != 1 else 700) + t(410, yy, ar, 2.0, 400, 'end', extra=AR)
dx0, dy0 = 14, 224
b += t(dx0, dy0, 'KEY SIZES (mm, proposal, Production to confirm)', 2.5, 700) + t(205, dy0, 'المقاسات الرئيسية (مقترحة)', 2.5, 700, 'end', extra=AR)
rows = [('Overall height', f'{H}'), ('Discs (base and top)', f'Ø{D}'), ('Gap between plates (centred)', f'{GAP}'), ('Sheet', f'{T} stainless, brushed'),
        ('Pot hole in top disc', f'Ø{2*RH}'), ('Shelf flange: height / diameter', f'{ZS} / Ø{2*RS}'), ('Plate window', f'{WHD} x {H-ZS}'), ('Parts', '2 plates (identical) + 4 spacers')]
for i_, (a_, b_) in enumerate(rows):
    yy = dy0 + 5.2 + i_*4.3
    b += line(dx0, yy+1.4, 205, yy+1.4, .1, HID) + t(dx0, yy, a_, 2.0) + t(dx0+80, yy, b_, 2.0, 600)
b += f'<image href="{datauri(PHOTO, 300)}" x="14" y="262" width="17" height="22.7" preserveAspectRatio="xMidYMid slice"/>' + rect(14, 262, 17, 22.7, .2, HID)
b += t(35, 266, 'Reference photo (third-party, maker unknown). Drawn as objekt\'s own design.', 1.9, 400, fill=HID) + t(35, 270, 'REV 2 (approved 25 Nov) replaces rev 1: same geometry, more views and a separated sheet layout.', 1.9, 400, fill=HID)
b += t(35, 274, 'Finish: brushed stainless, no paint. All sizes are a proposal, not costed, Production to confirm.', 1.9, 400, fill=HID) + t(35, 278, 'المراجعة ٢ (معتمدة ٢٥ نوفمبر) تحل محل المراجعة ١: نفس الهندسة مع مناظير أكثر.', 1.9, 400, fill=HID)
sh1 = sheet(1, N, 'OVERVIEW', 'نظرة عامة', 'n/a', b)
# ================= SHEET 2: front and side =================
S2 = .42; b = ''
def FX(x, ox): return ox + x*S2
oz = 222
def Z(z): return oz - z*S2
fx = 95
b += title(14, 27, 'FRONT (looking along +y, along the plates)', 'الأمامي (بمحاذاة اللوحين)', 190)
for sg in (-1, 1):
    b += rect(FX(sg*XP-T/2, fx), Z(H), T*S2, H*S2, .3, CUT, CUT)
    x0, x1 = sg*(XP+T/2), sg*R
    b += rect(min(FX(x0, fx), FX(x1, fx)), Z(0)-T*S2, abs(x1-x0)*S2, T*S2, .3, CUT, CUT) + rect(min(FX(x0, fx), FX(x1, fx)), Z(H), abs(x1-x0)*S2, T*S2, .3, CUT, CUT)
    x1s = sg*RS
    b += rect(min(FX(x0, fx), FX(x1s, fx)), Z(ZS), abs(x1s-x0)*S2, T*S2, .3, CUT, CUT)
potpts = [(FX(-POT_RIM/2, fx), Z(ZS+POT_H)), (FX(POT_RIM/2, fx), Z(ZS+POT_H)), (FX(POT_BASE/2, fx), Z(ZS)), (FX(-POT_BASE/2, fx), Z(ZS))]
b += pl(potpts, .3, 'none', '1.6 1', HID) + t(FX(-POT_RIM/2, fx), Z(ZS+POT_H)-1.5, 'pot stand-in (not ours)', 1.8, 400, fill=HID)
b += line(fx-20, Z(0), fx+R*S2+10, Z(0), .3, INK)
b += dim_v(fx-R*S2-9, Z(H), Z(0), f'{H}', ext=fx-R*S2) + dim_v(fx+R*S2+10, Z(ZS), Z(0), f'{ZS}', ext=fx+RS*S2) + dim_h(fx-R*S2, fx+R*S2, Z(0)+7, f'Ø{D}', ext=Z(0))
b += dim_h(fx-GAP/2*S2, fx+GAP/2*S2, Z(H)-6, f'{GAP}', ext=Z(H))
b += balloon(fx-XP*S2-12, Z(200), 1) + balloon(fx+XP*S2+12, Z(200), 1)
b += t(fx-70, Z(0)+16, 'The plates are seen edge-on. The back view (from -y) is the same silhouette.', 1.9, 400, fill=HID)
for zc_, nm_ in ((200, 'A'), (340, 'B'), (279, 'C')):
    b += line(fx-R*S2-4, Z(zc_), fx+R*S2+4, Z(zc_), .3, '#b3261e', '4 1 .8 1') + t(fx-R*S2-22, Z(zc_)+1, nm_, 2.6, 700, fill='#b3261e') + t(fx+R*S2+6, Z(zc_)+1, nm_, 2.6, 700, fill='#b3261e')
b += t(fx-R*S2, Z(H)-14, 'Red dash-dot: cut planes A-A (z 200), B-B (z 340), C-C (z 279), see sheet 4.', 1.8, 400, fill='#b3261e')
sx = 300
b += title(225, 27, 'LEFT SIDE (from -x), plate face', 'الجانب الأيسر، وجه اللوح', 185)
b += rect(sx-HH*S2, Z(H), 2*HH*S2, H*S2, .4, INK, '#d9dbdc') + rect(sx-WH*S2, Z(H), 2*WH*S2, (H-ZS)*S2, .35, INK, '#fff')
b += dim_h(sx-HH*S2, sx+HH*S2, Z(H)-5, f'{CH:.0f}', ext=Z(H)) + dim_h(sx-WH*S2, sx+WH*S2, Z(ZS)-6, f'{WHD}', ext=Z(ZS)) + dim_v(sx+HH*S2+6, Z(H), Z(ZS), f'{H-ZS}', ext=sx+WH*S2) + dim_v(sx-HH*S2-6, Z(H), Z(0), f'{H}', ext=sx-HH*S2)
b += line(sx-SHN*S2, Z(ZS), sx+SHN*S2, Z(ZS), .3, '#b3261e', '3 1 .6 1') + t(sx-SHN*S2, Z(ZS)+4, f'shelf flange neck {2*SHN:.0f}', 1.9, 400, fill='#b3261e')
b += line(sx-HH*S2-1, Z(0), sx+HH*S2+1, Z(0), .4, INK)
b += t(sx-WH*S2, Z(H)+(H-ZS)*S2/2, 'window, open at the top', 1.9, 400, fill=HID) + t(225, 36, 'Right side (from +x) is the same: the second plate, turned 180 degrees.', 1.9, 400, fill=HID)
b += balloon(sx-HH*S2+10, Z(150), 1)
sh2 = sheet(2, N, 'FRONT AND SIDE VIEWS', 'الواجهة الأمامية والجانبية', '1:2', b)
# ================= SHEET 3: plan and underside =================
S3 = .52; b = HATCH
def PX(x, ox): return ox + x*S3
def PY(y, oy): return oy - y*S3
cx1, cy1 = 112, 122
b += title(14, 27, 'PLAN (looking down)', 'المسقط الأفقي', 190)
for sg in (-1, 1):
    b += pl([(PX(x, cx1), PY(y, cy1)) for x, y in top_flange(sg)], .4, '#eceeef')
    b += pl([(PX(x, cx1), PY(y, cy1)) for x, y in shelf_seg(sg)], .3, '#e0e2e4', '1.4 1')
    b += rect(PX(sg*XP-T/2, cx1), PY(HH, cy1), T*S3, (HH-WH)*S3, .3, CUT, CUT) + rect(PX(sg*XP-T/2, cx1), PY(-WH, cy1), T*S3, (HH-WH)*S3, .3, CUT, CUT)
    b += rect(PX(sg*XP-T/2, cx1), PY(WH, cy1), T*S3, 2*WH*S3, .3, CUT, 'none', '1.2 .8')
b += f'<circle cx="{cx1}" cy="{cy1}" r="{POT_RIM/2*S3:.2f}" fill="none" stroke="{HID}" stroke-width=".3" stroke-dasharray="1.6 1"/><circle cx="{cx1}" cy="{cy1}" r="{POT_BASE/2*S3:.2f}" fill="none" stroke="{HID}" stroke-width=".3" stroke-dasharray="1.6 1"/>'
b += dim_h(PX(-R, cx1), PX(R, cx1), PY(-HH, cy1)+9, f'{D}', ext=PY(-HH, cy1)) + dim_v(PX(-R, cx1)-8, PY(HH, cy1), PY(-HH, cy1), f'{2*HH:.0f}', ext=PX(-R, cx1)) + dim_h(PX(-RH, cx1), PX(RH, cx1), PY(HH, cy1)-6, f'hole Ø{2*RH}', ext=PY(WH, cy1))
b += t(PX(-R, cx1), PY(-HH, cy1)+19, 'Dashed circles: pot stand-in rim Ø200 and base Ø155 (not ours). Shelf flanges lie below the top disc.', 1.8, 400, fill=HID)
for yc_, nm_ in ((0, 'D'), (125, 'E')):
    b += line(PX(-R, cx1)-4, PY(yc_, cy1), PX(R, cx1)+4, PY(yc_, cy1), .3, '#b3261e', '4 1 .8 1') + t(PX(-R, cx1)-22, PY(yc_, cy1)+1, nm_, 2.6, 700, fill='#b3261e') + t(PX(R, cx1)+6, PY(yc_, cy1)+1, nm_, 2.6, 700, fill='#b3261e')
b += t(PX(-R, cx1), 215, 'Red dash-dot: cut planes D-D (y 0) and E-E (y 125), see sheet 5.', 1.8, 400, fill='#b3261e')
cx2, cy2 = 312, 122
b += title(222, 27, 'UNDERSIDE (looking up)', 'من الأسفل', 185)
for sg in (-1, 1):
    b += pl([(PX(x, cx2), PY(y, cy2)) for x, y in base_flange(sg)], .4, '#dcdee0')
    b += pl([(PX(x, cx2), PY(y, cy2)) for x, y in shelf_seg(sg)], .3, 'none', '1.4 1')
    b += rect(PX(sg*XP-T/2, cx2), PY(HH, cy2), T*S3, 2*HH*S3, .3, CUT, CUT)
b += dim_h(PX(-R, cx2), PX(R, cx2), PY(-HH, cy2)+9, f'{D}', ext=PY(-HH, cy2)) + dim_h(PX(-XP+T/2, cx2), PX(XP-T/2, cx2), PY(HH, cy2)-6, f'{2*XP-T:.0f} gap', ext=PY(HH, cy2))
b += t(PX(-R, cx2), PY(-HH, cy2)+19, 'The stand rests on the two base flanges. Dashed: shelf flanges above. No feet, no levelling.', 1.8, 400, fill=HID)
b += t(PX(-R, cx2), PY(-HH, cy2)+23, 'Footprint is the base flange pair; the centre strip between the plates is open to the floor.', 1.8, 400, fill=HID)
sh3 = sheet(3, N, 'PLAN AND UNDERSIDE', 'المسقط الأفقي والقاع', '1:1.8', b)

# ================= SHEET 4: horizontal sections =================
S4 = .42
def HX(x, ox): return ox + x*S4
def HY(y, oy): return oy - y*S4
def cutbar(ox, oy, x, y0, y1, w=T):          # black cut rect, x centre, y0..y1
    return rect(HX(x-w/2, ox), HY(y1, oy), w*S4, (y1-y0)*S4, .2, CUT, CUT)
b = HATCH
b += title(14, 27, 'SECTIONS A-A, B-B, C-C (cut planes are marked on sheet 2; cut material is black or hatched)', 'مقاطع أفقية', 392)
panels = [(75, 'A-A', 200, 'at height 200: through the plates below the shelf'), (205, 'B-B', 340, 'at height 340: through the window; leg strips and spacers'), (335, 'C-C', 279, 'at height 279: through the shelf flanges')]
cy = 125
for cx, nm, zc, note in panels:
    b += t(cx-60, 42, f'SECTION {nm}', 2.7, 700) + t(cx+60, 42, 'مقطع ' + nm, 2.7, 700, 'end', extra=AR)
    # beyond: base flanges
    for sg in (-1, 1):
        b += pl([(HX(x, cx), HY(y, cy)) for x, y in base_flange(sg)], .25, '#eceeef')
    if nm == 'A-A':
        for sg in (-1, 1): b += cutbar(cx, cy, sg*XP, -HH, HH)
    if nm == 'B-B':
        for sg in (-1, 1):
            b += cutbar(cx, cy, sg*XP, WH, HH) + cutbar(cx, cy, sg*XP, -HH, -WH)
        for yy in (-125, 125):
            b += rect(HX(-XP+T/2, cx), HY(yy+5, cy), (2*XP-T)*S4, 10*S4, .2, CUT, CUT)
        b += f'<circle cx="{cx}" cy="{cy}" r="{(POT_BASE/2+(POT_RIM-POT_BASE)/2*((zc-ZS)/POT_H))*S4:.2f}" fill="none" stroke="{HID}" stroke-width=".3" stroke-dasharray="1.6 1"/>'
        for sg in (-1, 1): b += pl([(HX(x, cx), HY(y, cy)) for x, y in shelf_seg(sg)], .2, 'none', '1.2 .8', HID)
    if nm == 'C-C':
        for sg in (-1, 1):
            b += cutbar(cx, cy, sg*XP, -HH, HH)
            b += f'<polygon points="' + ' '.join(f'{HX(x, cx):.2f},{HY(y, cy):.2f}' for x, y in shelf_seg(sg)) + f'" fill="url(#hatch)" stroke="{INK}" stroke-width=".4"/>'
        b += f'<circle cx="{cx}" cy="{cy}" r="{POT_BASE/2*S4:.2f}" fill="none" stroke="{HID}" stroke-width=".3" stroke-dasharray="1.6 1"/>'
    b += dim_h(HX(-R, cx), HX(R, cx), HY(-HH, cy)+8, f'{D}', ext=HY(-HH, cy))
    if nm != 'C-C': b += dim_h(HX(-XP+T/2, cx), HX(XP-T/2, cx), HY(HH, cy)-5, f'{2*XP-T:.0f}', ext=HY(HH, cy))
    if nm == 'B-B': b += dim_v(HX(R, cx)+6, HY(HH, cy), HY(WH, cy), f'{HH-WH:.0f}', ext=HX(XP, cx)) 
    if nm == 'C-C': b += dim_h(HX(-RS, cx), HX(-XP-T/2, cx), HY(-RS, cy)+17, f'{SHD:.0f} flange depth', ext=HY(0, cy)-0) if False else dim_h(HX(-RS, cx), HX(RS, cx), HY(-RS, cy)+17, f'Ø{2*RS} shelf', ext=HY(-RS, cy)+1)
    b += t(cx-62, HY(-HH, cy)+26, note, 1.9, 400, fill=HID)
b += t(14, 232, 'Plates are cut black (2 mm). Hatched area on C-C is the shelf flange metal. Below the cut plane the base flanges are seen in light grey.', 1.9, 400, fill=HID)
b += t(14, 237, 'Dashed: pot stand-in (not ours). The spacers on B-B are Ø10 tubes, 22 long, between the two plates; fixing by Production.', 1.9, 400, fill=HID)
sh4 = sheet(4, N, 'SECTIONS, HORIZONTAL (A, B, C)', 'مقاطع أفقية', '1:2.4', b)
# ================= SHEET 5: vertical sections =================
S5 = .42
def VX(x, ox): return ox + x*S5
def VZ(z): return 222 - z*S5
def vbar(ox, x0, x1, z0, z1): return rect(VX(min(x0, x1), ox), VZ(max(z0, z1)), abs(x1-x0)*S5, abs(z1-z0)*S5, .2, CUT, CUT)
b = ''
b += title(14, 27, 'SECTION D-D (cut at y = 0 on sheet 3, looking along +y)', 'مقطع د-د', 190)
ox = 95
for sg in (-1, 1):
    # beyond: leg strips, flanges at full width
    b += rect(min(VX(sg*(XP-T/2), ox), VX(sg*(XP+T/2), ox)), VZ(H), T*S5, (H-ZS)*S5, .3, INK, '#d9dbdc')
    b += rect(min(VX(sg*XP, ox), VX(sg*R, ox)), VZ(H), abs(R-XP)*S5, T*S5, .25, INK, '#e4e6e8') + rect(min(VX(sg*XP, ox), VX(sg*R, ox)), VZ(T), abs(R-XP)*S5, T*S5, .25, INK, '#e4e6e8')
for sg in (-1, 1):
    b += vbar(ox, sg*(XP-T/2), sg*(XP+T/2), 0, ZS)             # plates below sill
    b += vbar(ox, sg*(XP+T/2), sg*R, 0, T)                      # base flange
    b += vbar(ox, sg*RH, sg*R, H-T, H)                          # top flange ring
    b += vbar(ox, sg*(XP+T/2), sg*RS, ZS-T, ZS)                 # shelf flange
b += line(ox-R*S5-6, VZ(0), ox+R*S5+6, VZ(0), .4, INK)
b += dim_v(ox-R*S5-9, VZ(H), VZ(0), f'{H}', ext=ox-R*S5) + dim_h(ox-RH*S5, ox+RH*S5, VZ(H)-7, f'hole Ø{2*RH}', ext=VZ(H)) + dim_h(ox-RS*S5, ox+RS*S5, VZ(ZS)+9, f'Ø{2*RS} shelf', ext=VZ(ZS)) + dim_v(ox+R*S5+8, VZ(ZS), VZ(0), f'{ZS}', ext=ox+RS*S5)
b += t(14, 36, 'Above 280 the plates are open (window), so only the leg strips behind the cut are seen (grey).', 1.8, 400, fill=HID)
ox2 = 300
b += title(225, 27, 'SECTION E-E (cut at y = 125 on sheet 3, through a leg strip)', 'مقطع هـ-هـ', 185)
xe = math.sqrt(R*R-125*125)
for sg in (-1, 1):
    for zc in (60, 340):
        pass
    b += vbar(ox2, sg*(XP-T/2), sg*(XP+T/2), 0, 60-2.75) + vbar(ox2, sg*(XP-T/2), sg*(XP+T/2), 60+2.75, 340-2.75) + vbar(ox2, sg*(XP-T/2), sg*(XP+T/2), 340+2.75, H)
    b += vbar(ox2, sg*(XP+T/2), sg*xe, 0, T) + vbar(ox2, sg*(XP+T/2), sg*xe, H-T, H)
for zc in (60, 340):
    b += rect(VX(-XP+T/2, ox2), VZ(zc+5), (2*XP-T)*S5, 10*S5, .3, CUT, '#9a9da0')
b += line(ox2-R*S5-6, VZ(0), ox2+R*S5+6, VZ(0), .4, INK)
b += dim_v(ox2-R*S5-9, VZ(H), VZ(0), f'{H}', ext=ox2-R*S5) + dim_h(ox2-xe*S5, ox2+xe*S5, VZ(0)+8, f'{2*xe:.0f}', ext=VZ(0)) + dim_v(ox2+R*S5+8, VZ(340), VZ(60), '280 between spacers', ext=ox2+XP*S5)
b += t(225, 36, 'Spacers: Ø10 tube x 22 at height 60 and 340 (grey), through Ø5.5 holes. No shelf flange at this cut.', 1.8, 400, fill=HID)
b += balloon(ox2+XP*S5+8, VZ(200), 1) + balloon(ox2+8, VZ(60)+8, 2)
sh5 = sheet(5, N, 'SECTIONS, VERTICAL (D, E)', 'مقاطع رأسية', '1:2', b)
# ================= SHEET 6: details =================
b = ''
def panel(x, y, w, h, en, ar):
    return rect(x, y, w, h, .3, INK, 'none') + t(x+3, y+6, en, 2.6, 700) + t(x+w-3, y+6, ar, 2.6, 700, 'end', extra=AR)
cid = [0]
def clip(x, y, w, h, body):
    cid[0] += 1
    return f'<clipPath id="cp{cid[0]}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#cp{cid[0]})">{body}</g>'
PW, PH1, PH2 = 192, 100, 90
b += panel(12, 32, PW, PH1, 'DETAIL 1  SHELF FLANGE AND SILL (elevation, y = 0)  1.9:1', 'تفصيل ١ جناح الرف')
SD = 1.9
dX = lambda x: 20 + (x+100)*SD
dZ = lambda z: 118 - (z-258)*SD
body = f'<polygon points="{dX(-13):.2f},{dZ(258):.2f} {dX(-11):.2f},{dZ(258):.2f} {dX(-11):.2f},{dZ(280):.2f} {dX(-13):.2f},{dZ(280):.2f}" fill="{CUT}"/>'
body += rect(dX(-88), dZ(280), (88-13)*SD, T*SD, .2, CUT, CUT)
body += dim_h(dX(-88), dX(-13), dZ(280)-9, f'flange depth {88-13}', ext=dZ(280)) + dim_h(dX(-13), dX(-11), dZ(258)+8, '2', ext=dZ(258)) + dim_v(dX(-92), dZ(280), dZ(278), '2', ext=dX(-88))
b += clip(13, 38, PW-2, PH1-8, body)
b += t(18, 86, 'Plate (below) and shelf flange are black (cut). The plate continues down to the floor, 280 below the flange.', 1.9) + t(18, 91, f'The flange is bent out of the window sill. Neck {2*SHN:.0f} wide (plan, sheet 2); depth {88-13}; sheet 2.', 1.9)
b += t(18, 96, 'Bend radius, relief, weld or no weld: Production. The pot base (Ø155) rests on this flange and the mirrored one.', 1.9, 400, fill=HID)
b += line(dX(-13)-4, dZ(258), dX(-13)+8, dZ(258), .3, INK) + t(dX(-11)+6, dZ(258)-1, 'break', 1.7, 400, fill=HID)
b += panel(210, 32, PW, PH1, 'DETAIL 2  WINDOW EDGE AND TOP FLANGE (plan, plate N)  0.75:1', 'تفصيل ٢ حافة الفتحة')
SD2 = .75
eX = lambda x: 218 + (x+150)*SD2
eY = lambda y: 128 - (y-40)*SD2
body = pl([(eX(x), eY(y)) for x, y in top_flange(-1)], .4, '#eceeef')
body += rect(eX(-12)-1, eY(HH), T*SD2+2, (HH-WH)*SD2, .2, CUT, CUT)
body += dim_v(eX(-12)+6, eY(HH), eY(WH), f'{HH-WH:.0f}', ext=eX(-12)) + dim_h(eX(-R), eX(-RH), eY(40)-3, f'{R-RH}', ext=eY(40))
b += clip(211, 38, PW-2, PH1-8, body)
b += t(335, 60, f'hole R{RH} (Ø{2*RH})', 1.9) + t(335, 64, 'bites the flange;', 1.9) + t(335, 70, f'leg strip {HH-WH:.0f} wide;', 1.9) + t(335, 74, f'window half width {WH:.1f}', 1.9) + t(335, 78, '(full width 203);', 1.9, 400, fill=HID) + t(335, 82, 'ring outside the hole 48.', 1.9, 400, fill=HID)
b += panel(12, 138, PW, PH2, 'DETAIL 3  TIE SPACER (section at y = 125)  3:1', 'تفصيل ٣ قطعة التباعد')
SD3 = 3.0
gX = lambda x: 108 + x*SD3
gZ = lambda z: 188 - (z-60)*SD3
body = ''
for sg in (-1, 1):
    xl = gX(sg*(XP-T/2)) if sg > 0 else gX(sg*(XP+T/2))
    body += f'<rect x="{xl:.2f}" y="{gZ(73):.2f}" width="{T*SD3}" height="{(73-62.75)*SD3:.2f}" fill="{CUT}"/><rect x="{xl:.2f}" y="{gZ(57.25):.2f}" width="{T*SD3}" height="{(57.25-47)*SD3:.2f}" fill="{CUT}"/>'
body += rect(gX(-XP+T/2), gZ(65), (2*XP-T)*SD3, 10*SD3, .3, CUT, '#9a9da0')
body += line(gX(-XP-T/2-8), gZ(60), gX(XP+T/2+8), gZ(60), .2, HID, '6 1.5 1 1.5')
body += dim_h(gX(-XP+T/2), gX(XP-T/2), gZ(65)-4, f'{GAP}', ext=gZ(65)) + dim_v(gX(XP+T/2)+9, gZ(65), gZ(55), '10', ext=gX(XP-T/2)) + dim_v(gX(-XP-T/2)-8, gZ(62.75), gZ(57.25), f'Ø{HOLE_D}', ext=gX(-XP-T/2))
b += clip(13, 144, PW-2, PH2-8, body)
b += t(16, 218, f'Spacer Ø10 tube, {GAP} long, between the plates; Ø{HOLE_D} hole in each plate. Bolt, weld or tapped end: Production.', 1.8, 400, fill=HID) + t(16, 222, '4 spacers: y = +-125, heights 60 and 340.', 1.8, 400, fill=HID)
b += panel(210, 138, PW, PH2, 'DETAIL 4  BASE FOLD AND FLOOR CONTACT (section at y = 125)  3:1', 'تفصيل ٤ ثنية القاعدة')
SD4 = 3.0
hX = lambda x: 330 + x*SD4
hZ = lambda z: 200 - z*SD4
body = line(hX(-45), hZ(0), hX(8), hZ(0), .5, INK)
body += f'<polygon points="{hX(-13):.2f},{hZ(0):.2f} {hX(-11):.2f},{hZ(0):.2f} {hX(-11):.2f},{hZ(24):.2f} {hX(-13):.2f},{hZ(24):.2f}" fill="{CUT}"/>' + rect(hX(-45), hZ(T), (45-13)*SD4, T*SD4, .2, CUT, CUT)
body += dim_v(hX(-48), hZ(T), hZ(0), '2', ext=hX(-45)) + dim_h(hX(-45), hX(-13), hZ(0)+8, 'flange (ends at x = -83 at y = 125)', ext=hZ(0))
b += clip(211, 144, PW-2, PH2-8, body)
b += t(214, 214, 'The base flange lies flat on the floor; the plate rises from its inner edge. No feet, no levelling.', 1.8, 400, fill=HID) + t(214, 218, 'A flat floor is assumed. Fold radius and relief: Production.', 1.8, 400, fill=HID)
sh6 = sheet(6, N, 'DETAILS', 'تفاصيل', '1:1 to 3:1', b)
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
fl = [('Fold', 'Where (v, mm)', 'What', 'Angle'), ('1', f'{DEP}', 'base flange up from the floor line', '90, away from the gap'), ('2', f'{DEP+ZS}', f'shelf flange, neck {2*SHN:.0f} wide', '90, away from the gap'), ('3', f'{DEP+H}', 'top flange, with the pot hole', '90, away from the gap')]
b += t(235, 172, 'FOLD LIST (proposed; bend allowance and radius by Production)', 2.4, 700) + t(410, 172, 'قائمة الثنيات', 2.4, 700, 'end', extra=AR)
for i_, r_ in enumerate(fl):
    yy = 178 + i_*4.6
    b += line(235, yy+1.4, 410, yy+1.4, .1, HID)
    for xx, v_ in zip((235, 255, 285, 365), r_): b += t(xx, yy, v_, 1.9, 700 if i_ == 0 else 400)
b += t(235, 199, 'Measured along the flat pattern from the free edge of the base flange (v = 0).', 1.8, 400, fill=HID)
sh7 = sheet(7, N, 'PART SHEET (FLAT PATTERN)', 'ورقة القطع', '1:2.4', b)

# ================= SHEET 8: assembly =================
b = HATCH
b += title(14, 27, 'EXPLODED VIEW (plates pulled apart along x; proposed assembly)', 'منظر مفكك', 392)
P3e = iso(35, 28, 140, 205, .30)
b += draw_iso(P3e, -1, dx=55, spacers=True)
b += t(14, 36, 'Items: 1 plate (2 off, identical, one turned 180 degrees), 2 tie spacer (4 off). Pot and plant are not part of objekt.', 1.9, 400, fill=HID)
sx0 = 232
b += t(sx0, 46, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + t(410, 46, 'تسلسل التجميع (مقترح)', 2.6, 600, 'end', extra=AR)
steps = [('Laser cut two plates (1) from the DXF file; deburr all edges.', 'قص لوحين (١) بالليزر وتنعيم الحواف.'),
         ('Fold each plate at the three fold lines: base flange, top flange, shelf flange (all away from the gap).', 'ثني كل لوح عند خطوط الثني الثلاثة، الأجنحة بعيداً عن الفتحة.'),
         ('Stand the two plates facing each other with a 22 mm gap (one turned 180 degrees).', 'وضع اللوحين متقابلين بفتحة ٢٢ مم (أحدهما مدار ١٨٠ درجة).'),
         ('Fix the four spacers (2) through the leg strips by bolt or weld (Production).', 'تثبيت قطع التباعد الأربع في الأرجل بمسمار أو لحام.'),
         ('Brush to one grain; deburr the hole edge. Check the stand sits flat on the floor.', 'تبريش في اتجاه واحد وتنعيم حافة الفتحة والتأكد من ثبات القاعدة.')]
for i, (en, ar) in enumerate(steps):
    yy = 56 + i*17; b += balloon(sx0+3, yy-1, i+1) + t(sx0+9, yy, en, 1.9) + t(410, yy+5, ar, 1.9, 400, 'end', extra=AR)
sh8 = sheet(8, N, 'ASSEMBLY', 'التجميع', 'n/a', b)
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
sh9 = sheet(9, N, 'CUTTING LAYOUT', 'مخطط القص', '1:10', b)
# ================= SHEET 5: BOM and notes =================
b = t(10, 28, 'BILL OF MATERIALS', 2.8, 600) + t(410, 28, 'قائمة المواد', 2.8, 600, 'end', extra=AR)
b += rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 215], ['ITEM', 'PART / الجزء', 'QTY / العدد', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
bom = [('1', 'Plate with base, top and shelf flanges', 'اللوح بثلاثة أجنحة', '2', 'Stainless sheet 2 mm (proposal), identical'), ('2', 'Tie spacer Ø10 x 22 + fixing', 'قطعة تباعد وتثبيت', '4', 'Stainless, bought-in or turned (Production)')]
for i, (n_, en, ar, q, m_) in enumerate(bom):
    yy = 44 + i*7
    b += line(10, yy+2.2, 410, yy+2.2, .15, HID) + t(12, yy, n_, 2.4) + t(24, yy, en, 2.4) + t(140, yy, ar, 2.4, 400, 'end', extra=AR) + t(150, yy, q, 2.4) + t(215, yy, m_, 2.4)
b += t(10, 70, 'NOTES', 2.8, 600) + t(410, 70, 'ملاحظات', 2.8, 600, 'end', extra=AR)
nts = [('REV 2, approved by Sabry 25 Nov 2026, replaces rev 1: same geometry, with more views and separated sheets. Production review pending.', 'المراجعة ٢ معتمدة من سبري ٢٥ نوفمبر وتحل محل المراجعة ١.'),
       ('Reference: third-party photos (maker unknown). Drawn as objekt\'s own design. Layout (Sabry, 12 Nov): gap in the centre, two mirrored halves; rev 0 had off-centre plates and is superseded.', 'المرجع صور لصانع مجهول. التصميم: فتحة في المنتصف ونصفان متماثلان (سبري).'),
       (f'Pot (not ours): 4 L class, rim {POT_RIM}, base {POT_BASE}, height {POT_H} (size-charts.com 4 L pot: 20 cm rim, 15.5 cm base, 16.5 cm high). Hole Ø{2*RH}; the pot passes both plate windows and stands on the two shelf flanges (Ø{2*RS}). 19 to 22 cm rims: Production to confirm the hole.', 'الأصيص ليس من منتجنا. الفتحة ٢٠٤ مم. جناحا الرف قطرهما ١٧٦ مم.'),
       ('Disc, height, 2 mm sheet, gap 22, shelf height 280 and all sizes are a PROPOSAL, not costed, Production to confirm.', 'كل المقاسات مقترحة ويؤكدها التصنيع.'),
       (f'Each plate is a frame of two {LEG:.0f} mm leg strips plus the sill. Production to say if that holds the pot and soil, or if thicker sheet, a cross tie or a heavier shelf bend is needed. No load figure is given.', 'كل لوح له ساقان ضيقتان. التصنيع يحدد إن كانت كافية. لا أرقام أحمال.'),
       ('Stability: equal base and top diameter, so a downward push on the top disc cannot tip it. Side push and pot weight are Production\'s to test; heavier base or ballast to confirm. Levelling not needed.', 'الثبات: قطر القاعدة والسطح متساويان. الاختبار من التصنيع.'),
       ('Finish: brushed stainless, no paint (objekt guide: exposed metal, brushed). Brushing direction and weld finish by Production.', 'التشطيب: ستانلس مبروش بدون دهان.'),
       ('Material, thickness, bend allowance, tolerances, sheet size, joints, welding and finish details are Production\'s to decide.', 'الخامة والسماكة والسماحيات واللحام يقررها التصنيع.'),
       ('No structural claims, stress or load figures, costs or prices. Not engineered. Arabic wording is a draft for a technical reader.', 'لا ادعاءات إنشائية ولا تكاليف. الصياغة العربية مسودة.')]
for i, (en, ar) in enumerate(nts):
    yy = 79 + i*12; b += t(12, yy, f'{i+1}.', 2.4, 600) + t(18, yy, en, 2.0) + t(410, yy+5, ar, 2.0, 400, 'end', extra=AR)
sh10 = sheet(10, N, 'BILL OF MATERIALS AND NOTES', 'قائمة المواد والملاحظات', 'n/a', b)

for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5, sh6, sh7, sh8, sh9, sh10], 1):
    open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('rev2 sheets written', len(SHEETS))
