"""OBJ-075: floor planter, ONE design in THREE sizes (S, M, L). Production drawing set, REV 1 (approved by Sabry 12 Nov 2026).
Run: python3 make_obj075_rev1.py <repo root>   then: NODE_PATH=<playwright> node make_pdf.js <dir> OBJ-075 1
Reference: images/OBJ-075_ref-sabry-12nov.jpg (two polished stainless cylinder planters, maker unknown, reference only).
Rev 0 (11 Nov) was a pair, A D300 x 390 and B D240 x 290; replaced by Sabry's 12 Nov brief: one pot in three sizes.
ALL SIZES ARE PROPOSED (not costed, Production to confirm). Liner sizes come from public nursery pages listed in plan/OBJ-075-sizes-note.md.
No costs, no structural claims. Arabic is a draft."""
import sys, os, math, base64, io
from PIL import Image
import ezdxf
ROOT = sys.argv[1] if len(sys.argv) > 1 else '/home/user/OBJEKT'
OUT = ROOT + '/venture/drawings/OBJ-075'; os.makedirs(OUT, exist_ok=True)
REV = 1; DATE = '12 Nov 2026'; PN = 'OBJ-075'
T = 2; RING_H = 12; RING_SET = 20      # sheet thickness; foot ring height; ring OD = body OD - 20
SHEET_L, SHEET_W, GAP = 2500, 1250, 10
RHO = 7.9e-6                              # kg per mm3, 304 (7.9 g/cm3, two of three sources; one gives 7.93)
SIZES = {  # name: (outer diameter, overall height incl. foot ring, liner text, liner top dia max)
    'S': dict(D=300, H=360, liner='10 L: D280 x 225 (7 L: D250 x 200)', ld=280),
    'M': dict(D=400, H=500, liner='20 L: D355 x 325, 25 L: D385 x 350', ld=385),
    'L': dict(D=520, H=650, liner='40 L: D500 x 450 (50 L D500 x 390)', ld=500)}
LINER_H = {'S': 225, 'M': 350, 'L': 450}
for k, s in SIZES.items():
    D, H = s['D'], s['H']
    s['WH'] = H - RING_H                                   # wall height
    s['WL'] = math.pi*(D-T)                                # wall blank length, neutral axis
    s['BD'] = D - 2*T                                      # base disc dia = wall inner dia
    s['RD'] = D - RING_SET                                 # ring outer dia
    s['RL'] = math.pi*(s['RD']-T)                          # ring strip length
    s['ID'] = D - 2*T
    s['clr'] = s['ID'] - s['ld']
    s['wt'] = (s['WL']*s['WH'] + math.pi*(s['BD']/2)**2 + s['RL']*RING_H)*T*RHO
    s['ratio'] = H/D
    s['riser'] = s['WH'] - 25 - LINER_H[k]
    wl, wh, bd, rl = s['WL'], s['WH'], s['BD'], s['RL']
    s['nest'] = [(GAP, GAP, wl, wh), (GAP, GAP+wh+GAP, rl, RING_H), (GAP+wl+GAP, GAP, bd, bd)]
    assert GAP+wl+GAP+bd <= SHEET_L-GAP and GAP+wh+GAP+RING_H <= SHEET_W-GAP and GAP+bd <= SHEET_W-GAP and rl <= SHEET_L-2*GAP, k
    print(k, 'wall', round(wl, 1), 'x', wh, 'base', bd, 'ring', round(rl, 1), 'ID', s['ID'], 'clear', s['clr'], 'kg', round(s['wt'], 1), 'ratio', round(s['ratio'], 2), 'riser', s['riser'])

# ---- DXF (mm, outline on layer CUT) ----
def new_doc():
    d = ezdxf.new('R2010'); d.units = 4; d.layers.add('CUT', color=7); d.layers.add('SHEET', color=3); return d
def rect_(m, x, y, w, h, layer='CUT'): m.add_lwpolyline([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], close=True, dxfattribs={'layer': layer})
for k, s in SIZES.items():
    for nm, kind in [('wall', 0), ('base', 1), ('ring', 2)]:
        d = new_doc(); m = d.modelspace()
        if kind == 0: rect_(m, 0, 0, s['WL'], s['WH'])
        elif kind == 1: m.add_circle((s['BD']/2, s['BD']/2), s['BD']/2, dxfattribs={'layer': 'CUT'})
        else: rect_(m, 0, 0, s['RL'], RING_H)
        d.saveas(f'{OUT}/{PN}_rev{REV}_{k}_{nm}.dxf')
    d = new_doc(); m = d.modelspace(); rect_(m, 0, 0, SHEET_L, SHEET_W, 'SHEET')
    (x0, y0, w0, h0), (x1, y1, w1, h1), (x2, y2, w2, h2) = s['nest']
    rect_(m, x0, y0, w0, h0); rect_(m, x1, y1, w1, h1); m.add_circle((x2+w2/2, y2+h2/2), w2/2, dxfattribs={'layer': 'CUT'})
    d.saveas(f'{OUT}/{PN}_rev{REV}_{k}_nest_{SHEET_L}x{SHEET_W}.dxf')

# ---- SVG helpers ----
FONT = "DejaVu Sans, Inter, Arial, sans-serif"
INK, DIM, HID, FILL, FILL2 = '#161616', '#2a4a7a', '#7a7a7a', '#f1efe9', '#dcd9d0'
RED = '#b3261e'
def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;')
def t(x, y, s, size=2.6, w=400, anchor='start', fill=INK, extra=''):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="{FONT}" font-size="{size}" font-weight="{w}" text-anchor="{anchor}" fill="{fill}"{extra}>{esc(s)}</text>'
def ar(x, y, s, size=2.6, w=400, fill=INK): return t(x, y, s, size, w, 'end', fill)
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

import textwrap
N = 5
def wrap(x, y, s, n=118, size=2.2, lh=3.8, fill=INK, w=400, arabic=False, xr=410):
    out = ''
    for i, ln in enumerate(textwrap.wrap(s, n)):
        out += (ar(xr, y+i*lh, ln, size, w, fill) if arabic else t(x, y+i*lh, ln, size, w, fill=fill))
    return out
def frame(n, title_en, title_ar, scale):
    s = rect(5, 5, 410, 287, .5) + rect(7, 7, 406, 283, .2)
    X, Y, Wd = 228, 247, 185
    s += rect(X, Y, Wd, 41, .4, fill='#fff')
    s += line(X, Y+9, X+Wd, Y+9, .25) + line(X, Y+20, X+Wd, Y+20, .25) + line(X, Y+31, X+Wd, Y+31, .25) + line(X+92, Y+9, X+92, Y+41, .25)
    s += bi(X+2, Y+4, f'{PN}   Floor planter, 3 sizes S M L', 'أصيص أرضي بثلاثة مقاسات', Wd-4, 2.6, 600)
    s += bi(X+2, Y+14, 'SIZE  D300x360 / D400x500 / D520x650', 'المقاسات (مقترحة)', 88, 2.1) + bi(X+94, Y+14, f'SCALE  {scale}   UNITS  mm', 'المقياس والوحدة', 88, 2.3)
    s += bi(X+2, Y+25, 'MATERIAL  304 stainless sheet 2 mm, proposed', 'الخامة: ستانلس ٣٠٤، ٢ مم مقترح', 88, 2.0) + bi(X+94, Y+25, 'FINISH  brushed (mirror optional)', 'التشطيب: فرشاة، مرآة اختياري', 88, 2.0)
    s += bi(X+2, Y+36, f'DATE  {DATE}      SHEET {n} / {N}', 'التاريخ، الورقة', 88, 2.3) + bi(X+94, Y+36, f'REV  {REV}', 'المراجعة', 88, 2.3)
    s += rect(X, Y-14, Wd, 12, .5, '#2f6b45', '#fff')
    s += t(X+Wd/2, Y-8.6, 'Approved by Sabry 12 Nov 2026. Production review pending.', 2.5, 700, 'middle', '#2f6b45') + t(X+Wd/2, Y-4.2, 'Not engineered. معتمد من سبري، مراجعة التصنيع قيد الانتظار', 2.5, 700, 'middle', '#2f6b45')
    return s + t(10, 14, title_en, 4.2, 700) + ar(410, 14, title_ar, 4.2, 700)
def sheet(n, te, ta, sc, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm"><rect width="420" height="297" fill="#fff"/>{frame(n, te, ta, sc)}{body}</svg>'
im = Image.open(ROOT + '/images/OBJ-075_ref-sabry-12nov.jpg').convert('RGB'); im.thumbnail((520, 900))
b_ = io.BytesIO(); im.save(b_, 'JPEG', quality=72); PHOTO = 'data:image/jpeg;base64,' + base64.b64encode(b_.getvalue()).decode()
STEEL, STEEL2 = '#c9cbcc', '#e6e8e9'
KEYS = ['S', 'M', 'L']

# ===== SHEET 1: views =====
S = .2; base = 205
b = t(10, 24, 'FRONT ELEVATION, 1:5, three sizes (one design)', 2.6, 600) + ar(225, 24, 'منظر أمامي، ثلاثة مقاسات بتصميم واحد', 2.6, 600)
xs = {'S': 22, 'M': 98, 'L': 190}
for k in KEYS:
    s = SIZES[k]; x = xs[k]; D, H, WH = s['D'], s['H'], s['WH']
    b += rect(x, base-WH*S-RING_H*S, D*S, WH*S, .45, INK, STEEL) + rect(x+(RING_SET/2)*S, base-RING_H*S, (D-RING_SET)*S, RING_H*S, .4, INK, STEEL2)
    b += rect(x+D*S*.62, base-WH*S-RING_H*S, D*S*.05, WH*S, 0, INK, '#ffffff66')
    b += line(x-6, base, x+D*S+6, base, .3, HID)
    b += dim_v(x-5, base-H*S, base, f'{H}', ext=x) + dim_h(x, x+D*S, base+7, f'D {D}', ext=base)
    b += t(x+D*S/2, base-H*S-4, f'{k}', 4, 700, 'middle') + t(x+D*S/2, base+14, f'H/D {s["ratio"]:.2f}', 2.0, 400, 'middle', HID)
# plans 1:10
b += t(10, 232, 'PLAN, 1:12   (red mark = longitudinal weld, ground flush; dashed = loose liner)', 2.4, 600)
pcx = {'S': 38, 'M': 100, 'L': 172}; pcy = 256
for k in KEYS:
    s = SIZES[k]; cx = pcx[k]; r = s['D']/24
    b += f'<circle cx="{cx}" cy="{pcy}" r="{r:.2f}" fill="{STEEL}" stroke="{INK}" stroke-width=".4"/><circle cx="{cx}" cy="{pcy}" r="{s["ID"]/24:.2f}" fill="{STEEL2}" stroke="{INK}" stroke-width=".25"/>'
    b += f'<circle cx="{cx}" cy="{pcy}" r="{s["ld"]/24:.2f}" fill="none" stroke="{HID}" stroke-width=".3" stroke-dasharray="1.4 1"/>'
    b += line(cx, pcy-r-1.2, cx, pcy-r+2.2, .8, RED) + t(cx, pcy+r+5, f'{k}  D{s["D"]}', 2.3, 600, 'middle')
b += t(10, 284, 'Same design in three sizes. No drain hole. Liner sizes are public nursery pot sizes, see sheet 5.', 2.0, 400, fill=HID)
# photo + ratio note
rx = 300; ih = 105*im.size[1]/im.size[0]
b += t(rx, 22, 'REFERENCE (idea only, maker unknown)', 2.3, 600) + ar(410, 22, 'المرجع (للفكرة فقط)', 2.3, 600)
b += f'<image x="{rx}" y="25" width="105" height="{ih:.1f}" href="{PHOTO}"/>' + rect(rx, 25, 105, ih, .25, HID)
b += wrap(rx, 25+ih+4, 'Two polished stainless cylinders, the smaller on a shallow foot ring. Height to diameter in the photo is about 1.25 to 1.3 (read by eye). Ours: 1.20 / 1.25 / 1.25.', 52, 1.9, 3.4, HID)
sh1 = sheet(1, 'VIEWS', 'المناظر', '1:5 / 1:12', b)

# ===== SHEET 2: flat patterns =====
S2 = .075; b = t(10, 24, 'FLAT PATTERNS, about 1:13, per size (quantity 1 of each part per planter)', 2.6, 600) + ar(410, 24, 'الأشكال المفرودة لكل مقاس', 2.6, 600)
rows = {'S': 34, 'M': 86, 'L': 152}
for k in KEYS:
    s = SIZES[k]; y0 = rows[k]; wl, wh = s['WL'], s['WH']
    b += t(10, y0-2, f'SIZE {k}', 2.6, 700)
    b += rect(14, y0+4, wl*S2, wh*S2, .45, INK, STEEL) + balloon(14+wl*S2/2, y0+4+wh*S2/2, 1)
    b += dim_h(14, 14+wl*S2, y0+4+wh*S2+6, f'{wl:.0f}  (= pi x {s["D"]-T})', ext=y0+4+wh*S2) + dim_v(11, y0+4, y0+4+wh*S2, f'{wh}', ext=14)
    ry = y0+4+wh*S2+12
    b += rect(14, ry, s['RL']*S2, RING_H*S2, .35, INK, STEEL2) + balloon(14+s['RL']*S2+5, ry+.6, 3) + t(14, ry+4.6, f'{s["RL"]:.0f} x {RING_H}', 2.0, 400, fill=DIM)
    bcx = 207; bcy = y0+4+s['BD']*S2/2 - (s['BD']*S2/2-wh*S2/2 if wh*S2 < s['BD']*S2 else 0)
    bcy = y0+4+max(wh*S2, s['BD']*S2)/2
    b += f'<circle cx="{bcx}" cy="{bcy:.2f}" r="{s["BD"]*S2/2:.2f}" fill="{STEEL}" stroke="{INK}" stroke-width=".45"/>' + balloon(bcx, bcy, 2) + t(bcx, bcy+s['BD']*S2/2+4, f'D {s["BD"]}', 2.2, 500, 'middle', DIM)
    ty = y0+2
    for i, (kk, v) in enumerate([('1 Wall, rolled', f'{wl:.0f} x {wh} x {T}'), ('2 Base disc', f'D{s["BD"]} x {T}'), ('3 Foot ring strip', f'{s["RL"]:.0f} x {RING_H} x {T}'), ('Ring outer dia', f'D{s["RD"]} (body D{s["D"]})'), ('Inner dia of wall', f'D{s["ID"]}'), ('Weight, steel only', f'about {s["wt"]:.1f} kg')]):
        b += t(240, ty+i*5.4, kk, 2.2) + t(408, ty+i*5.4, v, 2.2, 600, 'end') + line(240, ty+i*5.4+1.6, 410, ty+i*5.4+1.6, .12, HID)
b += wrap(10, 234, f'Wall blank = pi x (outer D - {T}) long, neutral axis, before weld preparation. Base disc = wall inner diameter, welded inside the wall bottom, flush with the wall edge. Foot ring is a rolled strip welded under the base disc, set in 10 mm all round. Weights use 7.9 g/cm3 for 304 (a public datasheet; another gives 7.93), steel only, about, no liner, no soil.', 118, 2.0, 3.6, HID)
b += ar(225, 252, 'الوزن تقريبي للصلب فقط بكثافة ٧٫٩؛ الفرد = ط × (القطر الخارجي − ٢)؛ القاعدة ملحومة داخل الجدار وحلقة القاعدة تحتها.', 2.0, 400, HID)
# تقريبي للصلب فقط بكثافة ٧٫٩. الفرد = ط × (القطر الخارجي − ٢). قاعدة داخلية ملحومة وحلقة قاعدة تحتها.', 118, 2.0, 3.6, HID, arabic=False)
sh2 = sheet(2, 'PART SHEET', 'ورقة الأجزاء', '1:13', b)

# ===== SHEET 3: section, joint, sequence =====
b = t(10, 24, 'SECTION through size M, 1:4 (liner dashed, riser and rim gap are Production to confirm)', 2.6, 600) + ar(410, 24, 'مقطع للمقاس M', 2.6, 600)
s = SIZES['M']; S3 = .25; cx = 75; top = 40; Hs = s['H']*S3; yb = top+Hs
D, WH = s['D'], s['WH']; x0, x1 = cx-D*S3/2, cx+D*S3/2
b += rect(x0, top, T*S3*4, WH*S3, .4, INK, '#8a8d90') + rect(x1-T*S3*4, top, T*S3*4, WH*S3, .4, INK, '#8a8d90')   # walls (drawn 4x thick for legibility)
b += rect(x0, yb-RING_H*S3-T*S3*4, D*S3, T*S3*4, .4, INK, '#8a8d90')                                           # base plate
b += rect(cx-s['RD']*S3/2, yb-RING_H*S3, s['RD']*S3, RING_H*S3, .35, INK, STEEL2)                               # ring
lh = LINER_H['M']*S3; lx = s['ld']*S3/2; ry_ = SIZES['M']['riser']*S3
liner_top = top+25*S3
b += rect(cx-lx, liner_top, 2*lx, lh, .3, HID, 'none', '1.4 1') + rect(cx-lx+6, yb-RING_H*S3-T*S3*4-ry_, 2*lx-12, ry_, .25, HID, '#eeeeee')
b += t(cx, liner_top+lh/2, 'loose liner', 2.3, 400, 'middle', HID) + t(cx, yb-RING_H*S3-T*S3*4-ry_/2+1, f'riser about {s["riser"]}', 2.0, 400, 'middle', HID)
b += dim_v(x1+6, top, yb, f'{s["H"]}', ext=x1) + dim_h(x0, x1, yb+7, f'D {D}', ext=yb) + dim_v(x1+14, top, liner_top, '25', ext=x1)
b += t(cx, top-4, 'Wall thickness drawn 4x for legibility (2 mm).', 1.9, 400, 'middle', HID)
dx, dy = 150, 150; D4 = 3.2
b += t(150, 36, 'JOINT DETAIL, wall / base / foot ring, 3.2:1', 2.4, 600)
wx, wy = 160, 50
b += rect(wx, wy, T*D4, 46, .4, INK, '#8a8d90') + rect(wx+T*D4, wy+46-T*D4, 40, T*D4, .4, INK, '#8a8d90') + rect(wx+10*D4, wy+46, T*D4, RING_H*D4, .4, INK, STEEL2)
b += line(wx-6, wy+46+RING_H*D4, wx+60, wy+46+RING_H*D4, .3, HID, '2 1')
b += poly([(wx+T*D4, wy+46-T*D4), (wx+T*D4+5, wy+46-T*D4), (wx+T*D4, wy+46-T*D4-5)], .3, RED, '#f6d6d3') + t(wx+T*D4+8, wy+46-T*D4-3, 'weld, base to wall (inside)', 2.0, 400, fill=RED)
b += t(wx+T*D4+4, wy+46+RING_H*D4+7, 'weld, foot ring to base (underside)', 2.0, 400, fill=RED)
b += dim_h(wx, wx+10*D4, wy+46+RING_H*D4+12, '10 set in', ext=wy+46+RING_H*D4) + dim_v(wx+10*D4+T*D4+8, wy+46, wy+46+RING_H*D4, f'{RING_H}', ext=wx+10*D4+T*D4)
b += t(150, 128, 'Wall closed by one longitudinal weld, ground flush. Base welded inside; no drain hole.', 2.0, 400, fill=HID)
sx0 = 238
b += t(sx0, 38, 'ASSEMBLY SEQUENCE (proposed)', 2.6, 600) + ar(410, 38, 'تسلسل التجميع (مقترح)', 2.6, 600)
steps = [('Cut wall, base disc and ring strip (items 1, 2, 3).', 'قص الجدار والقاعدة وشريط الحلقة.'),
         ('Roll the wall and the ring strip. Weld the longitudinal seams, grind flush.', 'لف الجدار والحلقة وحام اللحام الطولي وسوّه.'),
         ('Weld the base disc inside the wall bottom, flush with the edge.', 'حام القاعدة داخل أسفل الجدار.'),
         ('Weld the foot ring under the base, set in 10 mm all round.', 'حام حلقة القاعدة تحتها بإزاحة ١٠ مم.'),
         ('Brush or polish. Stand the loose liner on a riser, rim 25 mm under the planter rim.', 'اللمسة النهائية ثم وضع الأصيص الداخلي على رافع.')]
for i, (en, a) in enumerate(steps):
    yy = 48 + i*19
    b += balloon(sx0+3, yy-1, i+1) + wrap(sx0+9, yy, en, 62, 2.2, 3.8) + ar(410, yy+8, a, 2.2)
sh3 = sheet(3, 'SECTION AND ASSEMBLY', 'المقطع والتجميع', '1:4 / 3.2:1', b)

# ===== SHEET 4: cutting layouts =====
S4 = .05; b = t(10, 22, f'CUTTING LAYOUT per size on an assumed sheet {SHEET_L} x {SHEET_W} x {T}, 1:20. Assumed, Production to confirm.', 2.4, 600) + ar(410, 22, 'مخطط القص لكل مقاس على لوح مفترض', 2.4, 600)
for i, k in enumerate(KEYS):
    s = SIZES[k]; oy = 34 + i*72; ox = 14
    b += rect(ox, oy, SHEET_L*S4, SHEET_W*S4, .4, '#2f6b45', '#fbfaf6') + t(ox, oy-1.5, f'SIZE {k}', 2.4, 700)
    (x0, y0_, w0, h0), (x1, y1, w1, h1), (x2, y2, w2, h2) = s['nest']
    b += rect(ox+x0*S4, oy+y0_*S4, w0*S4, h0*S4, .3, INK, STEEL) + t(ox+(x0+w0/2)*S4, oy+(y0_+h0/2)*S4+1, '1', 3, 600, 'middle')
    b += rect(ox+x1*S4, oy+y1*S4, w1*S4, h1*S4, .3, INK, STEEL2) + t(ox+(x1+w1)*S4+2, oy+(y1+h1)*S4, '3', 2.4, 600)
    b += f'<circle cx="{ox+(x2+w2/2)*S4:.2f}" cy="{oy+(y2+h2/2)*S4:.2f}" r="{w2*S4/2:.2f}" fill="{STEEL}" stroke="{INK}" stroke-width=".3"/>' + t(ox+(x2+w2/2)*S4, oy+(y2+h2/2)*S4+1, '2', 3, 600, 'middle')
    cut = 2*(s['WL']+s['WH']) + math.pi*s['BD'] + 2*(s['RL']+RING_H)
    s['cut'] = cut
    b += wrap(160, oy+6, f'Size {k}: parts 1, 2, 3 on one sheet, {GAP} mm spacing, grain along the length. One planter per sheet used here; no offcut or yield is claimed.', 62, 2.2, 3.8)
    b += t(160, oy+20, f'Total cutting length {cut/1000:.2f} m.   Used width {GAP+s["WH"]+GAP+RING_H:.0f} of {SHEET_W}, length {GAP+s["WL"]+GAP+s["BD"]:.0f} of {SHEET_L}.', 2.3, 600)
sh4 = sheet(4, 'CUTTING LAYOUT', 'مخطط القص', '1:20', b)

# ===== SHEET 5: BOM, sizes, notes =====
b = t(10, 28, 'BILL OF MATERIALS (per planter)', 2.8, 600) + ar(410, 28, 'قائمة المواد', 2.8, 600) + rect(10, 31, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 24, 150, 190], ['ITEM', 'PART / الجزء', 'QTY', 'MATERIAL / الخامة']): b += t(x, 36, s_, 2.3, 600)
for i, (a1, a2, a3) in enumerate([('1', 'Wall, flat, rolled, one seam welded', '304 stainless sheet 2 mm (proposed)'), ('2', 'Base disc', '304 stainless sheet 2 mm (proposed)'), ('3', 'Foot ring strip, rolled and welded', '304 stainless sheet 2 mm (proposed)')]):
    yy = 44 + i*6
    b += t(12, yy, a1, 2.3) + t(24, yy, a2, 2.3) + t(150, yy, '1', 2.3) + t(190, yy, a3, 2.3) + line(10, yy+1.8, 410, yy+1.8, .12, HID)
b += t(10, 66, 'SIZE LADDER (proposal, not costed, Production to confirm)', 2.8, 600) + ar(410, 66, 'سلم المقاسات', 2.8, 600) + rect(10, 69, 400, 7, .3, INK, '#e9e5dc')
for x, s_ in zip([12, 28, 62, 92, 112, 215, 265, 322], ['SIZE', 'D x H', 'H/D', 'inner D', 'standard liner it takes (top diameter x height)', 'clearance', 'weight, about', 'sheet blank']): b += t(x, 74, s_, 2.0, 600)
for i, k in enumerate(KEYS):
    s = SIZES[k]; yy = 82 + i*6
    b += t(12, yy, k, 2.3, 700) + t(28, yy, f'{s["D"]} x {s["H"]}', 2.3) + t(62, yy, f'{s["ratio"]:.2f}', 2.3) + t(92, yy, f'{s["ID"]}', 2.3) + t(112, yy, s['liner'], 2.1) + t(215, yy, f'{s["clr"]:.0f} mm', 2.3) + t(265, yy, f'{s["wt"]:.1f} kg', 2.3) + t(322, yy, f'{s["WL"]:.0f} x {s["WH"]}', 2.3) + line(10, yy+1.8, 410, yy+1.8, .12, HID)
b += t(10, 108, 'NOTES', 2.8, 600) + ar(410, 108, 'ملاحظات', 2.8, 600)
notes = ['ALL SIZES ARE PROPOSED, not costed, Production to confirm. Sabry asked for "this pot in 3 sizes" and to check the industry sizes (12 Nov 2026). Liner sizes and ladder reasons are in plan/OBJ-075-sizes-note.md with the public pages they come from.',
         'Shape drawn exactly from one reference photo: plain rolled cylinder, flat top edge, low foot ring (visible on the smaller one in the photo; proposed here on all three). Maker unknown, reference only. Nothing of its marks is used.',
         'Loose inner liner, no drain hole (earlier decision for OBJ-173 and OBJ-075). The liner stands on a riser so its rim sits about 25 mm under the planter rim; riser sizes in the section are arithmetic, the riser is not designed. Production to confirm.',
         'Material 304 stainless, 2 mm, one longitudinal weld ground flush, base welded inside, no structural claims, stress figures, costs or prices. Wall thickness, weld method, tolerances, rolling limits and sheet size are Production\'s to decide.',
         'Finish: brushed stainless (recommended for launch) or mirror stainless as in the photo. A ground weld on a mirror finish is hard to hide; mirror needs the few skilled polishers, Production to confirm slots.',
         'Weight check, size L: about 20 kg steel only. Wall blank 1627 x 638 fits a 1250 x 2500 sheet with base and ring on the same sheet (sheet 4). Size M blank is 1250 long: same sheet, run along the 2500 length.',
         'Arabic wording is a draft for a technical reader.']
yy = 116
for i, n_ in enumerate(notes):
    b += t(12, yy, f'{i+1}.', 2.3, 600) + wrap(18, yy, n_, 130, 2.1, 3.7)
    yy += 3.7*len(textwrap.wrap(n_, 130)) + 3
sh5 = sheet(5, 'BILL OF MATERIALS, SIZES AND NOTES', 'المواد والمقاسات والملاحظات', 'n/a', b)
for i, s_ in enumerate([sh1, sh2, sh3, sh4, sh5], 1): open(f'{OUT}/{PN}_rev{REV}_sheet{i}.svg', 'w').write(s_)
print('written')
