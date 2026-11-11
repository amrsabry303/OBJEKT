"""OBJ-020 coffee table (library item 'Coffee Tables ref 4'), rev 1: drawing set (A3, EN/AR) + DXF.

Reference: one lifestyle photo, no dimensions. EVERY size here is estimated from the photo
(wine glass and sofa for scale) and is labelled as such on the sheets.

Table: a hollow box top with its four plan corners cut at 45 degrees, resting on two hollow block legs.
Proposed build: 3 mm sheet. Box = top plate + bottom plate + 2 folded end bands + 2 long side plates.
Each leg = one folded band + a cap plate. Production decides everything about joints and finish.

Run: python3 make_obj020_rev1.py     Needs: numpy ezdxf pymupdf pillow, node + playwright.
Output: venture/drawings/OBJ-020/
"""
import base64, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_obj177_rev1 as H          # drawing helpers only (txt, bi, line, hdim, vdim, table, ...)

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "venture", "drawings", "OBJ-020")
PID, REV, DATE = "OBJ-020", "1", "11 Nov 2026"
PRE = f"{PID}_rev{REV}_"
STAMP_EN, STAMP_AR = H.STAMP_EN, H.STAMP_AR
INK = H.INK

# ---------------------------------------------------------------- geometry (mm), all ESTIMATED from the photo
L, D, HT = 1200.0, 600.0, 340.0        # overall length, depth, height
BOXH = 180.0                           # box height
LEGH = HT - BOXH                       # leg height 160
CB = 100.0                             # box corner cut (45 degrees, both legs of the cut)
LL, LD = 400.0, 420.0                  # leg block length (along x) and depth (along y)
CL = 60.0                              # leg corner cut
INSET = 40.0                           # leg block inset from the box end
T = 3.0                                # sheet thickness (proposed; Production decides)
LCX = L / 2 - INSET - LL / 2           # leg centre x = +-360
GAP = L - 2 * INSET - 2 * LL           # gap between legs 320


def ar_num(txt):
    return str(txt).translate(str.maketrans('0123456789.', '٠١٢٣٤٥٦٧٨٩٫'))


def octagon(w, d, c):
    return [(-w / 2 + c, -d / 2), (w / 2 - c, -d / 2), (w / 2, -d / 2 + c), (w / 2, d / 2 - c),
            (w / 2 - c, d / 2), (-w / 2 + c, d / 2), (-w / 2, d / 2 - c), (-w / 2, -d / 2 + c)]


def oct_perimeter(w, d, c):
    return 2 * (w - 2 * c) + 2 * (d - 2 * c) + 4 * c * math.sqrt(2)


BOX_OCT = octagon(L, D, CB)
LEG_OCT = octagon(LL, LD, CL)
SEG_A = L - 2 * CB                      # long side plate 1000
SEG_B = D - 2 * CB                      # end face 400
SEG_C = CB * math.sqrt(2)               # chamfer face 141.4
END_BAND = 2 * SEG_C + SEG_B            # 682.8
LEG_SEGS = [(LL - 2 * CL) / 2, CL * math.sqrt(2), LD - 2 * CL, CL * math.sqrt(2), LL - 2 * CL,
            CL * math.sqrt(2), LD - 2 * CL, CL * math.sqrt(2), (LL - 2 * CL) / 2]
LEG_BAND = sum(LEG_SEGS)                # 1499.4
LEG_FOLDS = list(np.cumsum(LEG_SEGS)[:-1])


# ---------------------------------------------------------------- 3D prisms and projections
def prism(poly, x0, y0, z0, z1):
    pts = [(x + x0, y + y0) for x, y in poly]
    faces = [("top", [(x, y, z1) for x, y in pts])]
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        faces.append(("side", [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]))
    return faces


def view_iso(p, az=35.0, el=28.0):
    a, e = math.radians(az), math.radians(el)
    x = p[0] * math.cos(a) - p[1] * math.sin(a)
    y = p[0] * math.sin(a) + p[1] * math.cos(a)
    return (x, p[2] * math.cos(e) + y * math.sin(e), y * math.cos(e) - p[2] * math.sin(e))


def to_cam(az=35.0, el=28.0):
    a, e = math.radians(az), math.radians(el)
    return (-math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e))


def normal(face):
    p0, p1, p2 = [np.array(q, float) for q in face[:3]]
    n = np.cross(p1 - p0, p2 - p0)
    return n / (np.linalg.norm(n) + 1e-9)


def poly_svg(pts2, ox, oy, s, fill, stroke=INK, w=0.3, dash=None):
    d = "M" + " L".join(f"{ox + u * s:.2f},{oy - v * s:.2f}" for u, v in pts2) + " Z"
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"{da}/>'


METAL_TOP, METAL_LIT, METAL_MID, METAL_DARK = "#d6cdbd", "#c2b6a2", "#ab9f8b", "#968a77"


def shade(n, cam):
    light = np.array([-0.5, -0.6, 0.65]); light /= np.linalg.norm(light)
    v = float(np.dot(n, light))
    if n[2] > 0.9:
        return METAL_TOP
    return METAL_LIT if v > 0.25 else (METAL_MID if v > -0.15 else METAL_DARK)


def draw_iso(ox, oy, s, lift=0.0, exploded=False):
    cam = np.array(to_cam())
    svg = ""
    legs = []
    for sgn in (-1, 1):
        legs.append(prism(LEG_OCT, sgn * LCX, 0, 0, LEGH))
    box = prism(BOX_OCT, 0, 0, LEGH + lift, HT + lift)
    groups = legs + [box]
    for fa in groups:
        vis = [(f, view_iso(np.mean(np.array(f[1]), axis=0))) for f in fa if float(np.dot(normal(f[1]), cam)) > 0.02]
        vis.sort(key=lambda t: -t[1][2])
        for f, _ in vis:
            svg += poly_svg([view_iso(q)[:2] for q in f[1]], ox, oy, s, shade(normal(f[1]), cam))
    return svg


def draw_front(ox, oy, s):
    """Front elevation, looking along +y. oy = floor line."""
    svg = ""
    for sgn in (-1, 1):
        x0, x1 = sgn * LCX - LL / 2, sgn * LCX + LL / 2
        svg += poly_svg([(x0, 0), (x1, 0), (x1, LEGH), (x0, LEGH)], ox, oy, s, METAL_MID)
        for xx in (x0 + CL, x1 - CL):
            svg += H.line(ox + xx * s, oy, ox + xx * s, oy - LEGH * s, 0.2)
    svg += poly_svg([(-L / 2, LEGH), (L / 2, LEGH), (L / 2, HT), (-L / 2, HT)], ox, oy, s, METAL_LIT)
    for xx in (-L / 2 + CB, L / 2 - CB):
        svg += H.line(ox + xx * s, oy - LEGH * s, ox + xx * s, oy - HT * s, 0.2)
    return svg


def draw_end(ox, oy, s):
    """End elevation, looking along -x (the right-hand end)."""
    svg = ""
    svg += poly_svg([(-LD / 2, 0), (LD / 2, 0), (LD / 2, LEGH), (-LD / 2, LEGH)], ox, oy, s, METAL_MID)
    for yy in (-LD / 2 + CL, LD / 2 - CL):
        svg += H.line(ox + yy * s, oy, ox + yy * s, oy - LEGH * s, 0.2)
    svg += poly_svg([(-D / 2, LEGH), (D / 2, LEGH), (D / 2, HT), (-D / 2, HT)], ox, oy, s, METAL_LIT)
    for yy in (-D / 2 + CB, D / 2 - CB):
        svg += H.line(ox + yy * s, oy - LEGH * s, ox + yy * s, oy - HT * s, 0.2)
    return svg


# ---------------------------------------------------------------- sheet frame
def sheet(n, total, t_en, t_ar, scale, body, logo):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm" font-family="{H.FONT}">'
    s += '<rect width="420" height="297" fill="#fff"/>'
    s += f'<rect x="7" y="7" width="406" height="283" fill="none" stroke="{INK}" stroke-width="0.35"/>'
    s += H.image(11, 10.5, 22, 14, logo)
    s += H.txt(38, 17, f"{PID}  Coffee table", 5, bold=True) + H.txt(38, 22.5, t_en, 3.2, fill="#444")
    s += H.txt(409, 17, f"طاولة قهوة  {PID}", 5, "start", True, ar=True) + H.txt(409, 22.5, t_ar, 3.2, "start", False, "#444", ar=True)
    s += H.line(7, 27, 413, 27, 0.25)
    s += body
    bx, by, bw, bh = 263, 253, 150, 37
    s += f'<rect x="{bx}" y="{by - 11}" width="{bw}" height="11" fill="#fff4f2" stroke="#b3261e" stroke-width="0.4"/>'
    s += H.txt(bx + 3, by - 6.3, STAMP_EN, 2.9, bold=True, fill="#b3261e") + H.txt(bx + bw - 3, by - 2.2, STAMP_AR, 2.7, "start", False, "#b3261e", ar=True)
    s += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#fff" stroke="{INK}" stroke-width="0.35"/>'
    cells = [("PRODUCT / المنتج", f"{PID} Coffee table (name to follow)", 0, 0, 75), ("SIZE / المقاس", "A3", 75, 0, 25),
             ("SCALE / المقياس", scale, 100, 0, 25), ("UNITS / الوحدات", "mm", 125, 0, 25),
             ("MATERIAL / الخامة", "Steel sheet 3 mm, laser cut and folded (proposed)", 0, 12.3, 75),
             ("DATE / التاريخ", DATE, 75, 12.3, 25), ("SHEET / لوحة", f"{n} / {total}", 100, 12.3, 25), ("REV / مراجعة", REV, 125, 12.3, 25),
             ("FINISH / التشطيب", "Brushed metal, tone as the photo (to be confirmed)", 0, 24.6, 100),
             ("DRAWN / رسم", "objekt", 100, 24.6, 50)]
    for lab, val, cx, cy, cw in cells:
        s += f'<rect x="{bx + cx}" y="{by + cy}" width="{cw}" height="12.3" fill="none" stroke="{INK}" stroke-width="0.15"/>'
        s += H.txt(bx + cx + 1.3, by + cy + 3.6, lab, 1.9, fill="#666") + H.txt(bx + cx + 1.3, by + cy + 9.2, val, 2.5 if len(val) < 30 else 2.0, bold=True)
    return s + "</svg>"


# ---------------------------------------------------------------- DXF
PARTS = [  # key, name, qty
    ("P1_top_plate", "Top plate", 1), ("P2_bottom_plate", "Bottom plate", 1), ("P3_end_band", "End band", 2),
    ("P4_long_side", "Long side plate", 2), ("P5_leg_band", "Leg band", 2), ("P6_leg_cap", "Leg cap plate", 2)]


def write_dxf():
    import ezdxf
    def new():
        d = ezdxf.new("R2010"); d.units = 4
        d.layers.add("CUT", color=7); d.layers.add("BEND", color=5, linetype="DASHED"); d.layers.add("NOTE", color=8)
        return d
    def poly(msp, pts, ox, oy):
        msp.add_lwpolyline([(ox + x, oy + y) for x, y in pts], close=True, dxfattribs={"layer": "CUT"})
    def rect_pts(w, h): return [(0, 0), (w, 0), (w, h), (0, h)]
    def band(msp, w, h, folds, ox, oy, vertical=False):
        if vertical:
            msp.add_lwpolyline([(ox, oy), (ox + h, oy), (ox + h, oy + w), (ox, oy + w)], close=True, dxfattribs={"layer": "CUT"})
            for f in folds:
                msp.add_line((ox, oy + f), (ox + h, oy + f), dxfattribs={"layer": "BEND"})
        else:
            msp.add_lwpolyline([(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)], close=True, dxfattribs={"layer": "CUT"})
            for f in folds:
                msp.add_line((ox + f, oy), (ox + f, oy + h), dxfattribs={"layer": "BEND"})
    files = []
    e_folds = [SEG_C, SEG_C + SEG_B]
    items = {
        "P1_top_plate": lambda m: poly(m, BOX_OCT, L / 2, D / 2),
        "P2_bottom_plate": lambda m: poly(m, BOX_OCT, L / 2, D / 2),
        "P3_end_band": lambda m: band(m, END_BAND, BOXH, e_folds, 0, 0),
        "P4_long_side": lambda m: poly(m, rect_pts(SEG_A, BOXH), 0, 0),
        "P5_leg_band": lambda m: band(m, LEG_BAND, LEGH, LEG_FOLDS, 0, 0),
        "P6_leg_cap": lambda m: poly(m, LEG_OCT, LL / 2, LD / 2),
    }
    for key, fn in items.items():
        d = new(); fn(d.modelspace())
        d.modelspace().add_text(f"{PID} rev {REV} {key}. mm. 3 mm sheet (proposed). Sizes estimated from a photo. DRAFT.",
                                dxfattribs={"layer": "NOTE", "height": 8}).set_placement((0, -30))
        p = os.path.join(OUT, PRE + key + ".dxf"); d.saveas(p); files.append(p)
    # nested sheets
    nests = nest_layout()
    for i, parts in enumerate(nests):
        d = new(); d.layers.add("SHEET", color=1); m = d.modelspace()
        m.add_lwpolyline([(0, 0), (2500, 0), (2500, 1250), (0, 1250)], close=True, dxfattribs={"layer": "SHEET"})
        for kind, x, y, vert in parts:
            if kind == "oct_box": poly(m, BOX_OCT, x + L / 2, y + D / 2)
            elif kind == "oct_leg": poly(m, LEG_OCT, x + LL / 2, y + LD / 2)
            elif kind == "long": poly(m, rect_pts(SEG_A, BOXH), x, y)
            elif kind == "end": band(m, END_BAND, BOXH, e_folds, x, y, vertical=vert)
            elif kind == "legband": band(m, LEG_BAND, LEGH, LEG_FOLDS, x, y)
        p = os.path.join(OUT, PRE + f"nest_{i + 1}_1250x2500.dxf"); d.saveas(p); files.append(p)
    return files


def nest_layout():
    """(kind, x, y, vertical) with lower-left corners in mm on a 2500 x 1250 sheet. 10 mm edge margin, 30 mm part spacing."""
    a = [("oct_box", 10, 640, False), ("oct_box", 10, 10, False),
         ("long", 1240, 1060, False), ("long", 1240, 850, False),
         ("oct_leg", 1240, 400, False), ("oct_leg", 1670, 400, False),
         ("end", 2100, 10, True), ("end", 2310, 10, True)]
    b = [("legband", 10, 10, False), ("legband", 10, 200, False)]
    return [a, b]


def cut_lengths():
    plates = 2 * oct_perimeter(L, D, CB)
    longs = 2 * 2 * (SEG_A + BOXH)
    ends = 2 * 2 * (END_BAND + BOXH)
    legbands = 2 * 2 * (LEG_BAND + LEGH)
    caps = 2 * oct_perimeter(LL, LD, CL)
    return dict(plates=plates, longs=longs, ends=ends, legbands=legbands, caps=caps,
                total=plates + longs + ends + legbands + caps)


# ---------------------------------------------------------------- sheets
def flat_part(b, ox, oy, s, w, h, label_en, label_ar, qty, folds=None, pts=None, dims=True):
    """Draw a flat pattern at scale s with its lower-left corner at sheet (ox, oy_top)."""
    if pts is None:
        pts = [(0, 0), (w, 0), (w, h), (0, h)]
    P = [(ox + x * s, oy + (h - y) * s) for x, y in pts]
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in P) + " Z"
    b += f'<path d="{d}" fill="#ece8df" stroke="{INK}" stroke-width="0.35"/>'
    for f in (folds or []):
        b += H.line(ox + f * s, oy - 2, ox + f * s, oy + h * s + 2, 0.2, "#2255aa", "5 1.2 1 1.2")
    return b


def build(logo, ref):
    sheets = []
    cl = cut_lengths()
    # ---- sheet 1: views
    s = 1 / 8
    b = ""
    b += H.bi(20, 34, "FRONT ELEVATION  1:8", "المسقط الأمامي", 2.8, bold=True)
    ox, oy = 95, 100
    b += draw_front(ox, oy, s)
    b += H.hdim(ox - L / 2 * s, ox + L / 2 * s, oy + 8, f"{L:.0f} est.")
    b += H.vdim(ox + L / 2 * s + 6, oy - HT * s, oy, f"{HT:.0f}")
    b += H.vdim(ox - L / 2 * s - 6, oy - LEGH * s, oy, f"{LEGH:.0f}", side=-1)
    b += H.balloon(ox - 40, oy - HT * s - 12, "1", ox - 30, oy - (LEGH + BOXH * 0.8) * s)
    b += H.balloon(ox + 40, oy - HT * s - 12, "2", ox + (LCX + 60) * s, oy - LEGH * 0.5 * s)
    b += H.bi(20, 120, "PLAN  1:8", "المسقط الأفقي", 2.8, bold=True)
    px, py = 95, 166
    b += poly_svg([(x, y) for x, y in BOX_OCT], px, py, s, METAL_TOP)
    for sgn in (-1, 1):
        b += poly_svg([(x + sgn * LCX, y) for x, y in LEG_OCT], px, py, s, "none", "#777", 0.2, "3 1.2")
    b += H.line(px - L / 2 * s - 5, py, px + L / 2 * s + 5, py, 0.1, "#888", "4 1 1 1") + H.line(px, py - D / 2 * s - 5, px, py + D / 2 * s + 5, 0.1, "#888", "4 1 1 1")
    b += H.hdim(px - L / 2 * s, px + L / 2 * s, py + D / 2 * s + 8, f"{L:.0f} est.")
    b += H.vdim(px + L / 2 * s + 6, py - D / 2 * s, py + D / 2 * s, f"{D:.0f} est.")
    b += H.txt(px - 60, py + D / 2 * s + 15, "legs under the top: dashed", 2.0, fill="#555")
    b += H.bi(215, 34, "END ELEVATION  1:8", "المسقط الجانبي", 2.8, bold=True)
    sx = 262
    b += draw_end(sx, oy, s)
    b += H.hdim(sx - D / 2 * s, sx + D / 2 * s, oy + 8, f"{D:.0f}")
    b += H.vdim(sx + D / 2 * s + 6, oy - HT * s, oy, f"{HT:.0f}")
    b += H.bi(215, 122, "VIEW", "منظور", 2.8, bold=True)
    b += draw_iso(262, 212, 0.095)
    b += H.bi(335, 122, "REFERENCE (photo, third party)", "المرجع (صورة من طرف ثالث)", 2.1, bold=True)
    b += H.image(335, 128, 74, 92, ref, True) + H.txt(335, 224, "Reference only. Not our piece.", 1.9, fill="#555")
    rows = [[("Item", "البند"), ("Finish", "التشطيب"), ("Note", "ملاحظة")],
            [("1 Box (top)", "الصندوق"), ("Brushed metal, champagne-bronze tone", "معدن مصنفر بدرجة شمبانيا-برونز"), ("tone from the photo", "الدرجة من الصورة")],
            [("2 Legs (2)", "الأرجل (٢)"), ("Same finish as the box", "نفس تشطيب الصندوق"), ("to be confirmed", "للتأكيد")]]
    b += H.bi(20, 224, "FINISH", "التشطيب", 2.6, bold=True)
    b += H.table(20, 230, [28, 74, 40], rows, 7.0, 2.0)
    b += H.txt(20, 255, "No painted colour chosen. Method (brushed stainless, PVD or other) is Production's.", 1.9, fill="#555")
    b += H.bi(20, 266, "1 Box  2 Leg block (2 off)", "١ الصندوق   ٢ كتلة رجل (٢)", 2.4)
    b += H.bi(20, 277, "ALL sizes are estimated from the photo. No dimensions came with it.", "كل المقاسات تقديرية من الصورة. لم تصل أي أبعاد معها.", 2.3)
    sheets.append(("views", sheet(1, 4, "Views and overall sizes (estimated)", "المساقط والمقاسات (تقديرية)", "1:8", b, logo)))

    # ---- sheet 2: parts at 1:7
    b = ""
    s7 = 1 / 7
    b += H.bi(20, 34, "P1 TOP PLATE (1) and P2 BOTTOM PLATE (1), same outline  1:7", "ل١ لوح علوي (١) ول٢ لوح سفلي (١)، نفس الشكل", 2.6, bold=True)
    x0, y0 = 22, 44
    P = [(x0 + (x + L / 2) * s7, y0 + (D / 2 - y) * s7) for x, y in BOX_OCT]
    b += f'<path d="M{" L".join(f"{x:.2f},{y:.2f}" for x, y in P)} Z" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
    b += H.hdim(x0, x0 + L * s7, y0 + D * s7 + 7, f"{L:.0f}")
    b += H.vdim(x0 + L * s7 + 6, y0, y0 + D * s7, f"{D:.0f}")
    b += H.hdim(x0, x0 + CB * s7, y0 - 3, f"{CB:.0f}", size=2.0)
    b += H.txt(x0 + 62, y0 + 42, f"corner cuts {CB:.0f} x {CB:.0f}, 45°", 2.1, fill="#555")
    b += H.bi(240, 34, "P6 LEG CAP PLATE (2)  1:7", "ل٦ لوح علوي للرجل (٢)", 2.6, bold=True)
    x1, y1 = 262, 48
    P = [(x1 + (x + LL / 2) * s7, y1 + (LD / 2 - y) * s7) for x, y in LEG_OCT]
    b += f'<path d="M{" L".join(f"{x:.2f},{y:.2f}" for x, y in P)} Z" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
    b += H.hdim(x1, x1 + LL * s7, y1 + LD * s7 + 7, f"{LL:.0f}")
    b += H.vdim(x1 + LL * s7 + 6, y1, y1 + LD * s7, f"{LD:.0f}")
    b += H.hdim(x1, x1 + CL * s7, y1 - 3, f"{CL:.0f}", size=2.0)
    # bands and plates
    y2 = 168
    b += H.bi(20, y2 - 12, "P4 LONG SIDE PLATE (2)  1:7", "ل٤ لوح جانبي طويل (٢)", 2.6, bold=True)
    b += f'<rect x="22" y="{y2}" width="{SEG_A * s7:.2f}" height="{BOXH * s7:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
    b += H.hdim(22, 22 + SEG_A * s7, y2 + BOXH * s7 + 6, f"{SEG_A:.0f}")
    b += H.vdim(22 + SEG_A * s7 + 5, y2, y2 + BOXH * s7, f"{BOXH:.0f}")
    xe = 180
    b += H.bi(xe - 2, y2 - 12, "P3 END BAND (2), folded twice  1:7", "ل٣ شريط طرفي (٢)، يُثنى مرتين", 2.6, bold=True)
    b += f'<rect x="{xe}" y="{y2}" width="{END_BAND * s7:.2f}" height="{BOXH * s7:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
    for f in (SEG_C, SEG_C + SEG_B):
        b += H.line(xe + f * s7, y2 - 2, xe + f * s7, y2 + BOXH * s7 + 2, 0.2, "#2255aa", "5 1.2 1 1.2")
    b += H.hdim(xe, xe + SEG_C * s7, y2 + BOXH * s7 + 6, f"{SEG_C:.1f}", size=1.9)
    b += H.hdim(xe + SEG_C * s7, xe + (SEG_C + SEG_B) * s7, y2 + BOXH * s7 + 6, f"{SEG_B:.0f}", size=1.9)
    b += H.hdim(xe + (SEG_C + SEG_B) * s7, xe + END_BAND * s7, y2 + BOXH * s7 + 6, f"{SEG_C:.1f}", size=1.9)
    b += H.txt(xe, y2 + BOXH * s7 + 14, f"total {END_BAND:.1f}, folds 135° (blue dash-dot)", 2.0, fill="#555")
    y3 = 228
    b += H.bi(20, y3 - 12, "P5 LEG BAND (2), eight folds  1:7", "ل٥ شريط الرجل (٢)، ثماني ثنيات", 2.6, bold=True)
    b += f'<rect x="22" y="{y3}" width="{LEG_BAND * s7:.2f}" height="{LEGH * s7:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
    pos = 22
    for i, seg in enumerate(LEG_SEGS):
        if i:
            b += H.line(pos, y3 - 2, pos, y3 + LEGH * s7 + 2, 0.2, "#2255aa", "5 1.2 1 1.2")
        b += H.txt(pos + seg * s7 / 2, y3 + LEGH * s7 / 2 + 0.8, f"{seg:.0f}" if abs(seg - round(seg)) < 0.05 else f"{seg:.1f}", 1.8, "middle")
        pos += seg * s7
    b += H.hdim(22, 22 + LEG_BAND * s7, y3 + LEGH * s7 + 6, f"{LEG_BAND:.1f}  (height {LEGH:.0f})", size=2.0)
    b += H.txt(22, y3 + LEGH * s7 + 13, "Seam at the middle of a long face. Folds 135° (blue dash-dot).", 2.0, fill="#555")
    rows = [[("DATA", "بيانات"), ""],
            [("Overall L x D x H (estimated)", "الطول × العمق × الارتفاع (تقديري)"), f"{L:.0f} x {D:.0f} x {HT:.0f}"],
            [("Box height / leg height", "ارتفاع الصندوق / الرجل"), f"{BOXH:.0f} / {LEGH:.0f}"],
            [("Leg block L x D, set in", "كتلة الرجل، البعد عن الطرف"), f"{LL:.0f} x {LD:.0f}, {INSET:.0f}"],
            [("Gap between legs", "المسافة بين الرجلين"), f"{GAP:.0f}"],
            [("Sheet thickness (proposed)", "سماكة الصاج (مقترحة)"), f"{T:.0f}"]]
    b += H.table(300, 150, [60, 48], rows, 6.2, 1.9)
    sheets.append(("parts", sheet(2, 4, "Parts: flat patterns", "القطع: الأشكال المسطحة", "1:7", b, logo)))

    # ---- sheet 3: assembly and cutting
    b = ""
    b += H.bi(20, 34, "EXPLODED VIEW  1:11", "منظور مفكوك", 2.8, bold=True)
    b += draw_iso(100, 112, 0.09, lift=220.0)
    for sgn in (-1, 1):
        a = view_iso((sgn * LCX, 0, LEGH + 4)); b2 = view_iso((sgn * LCX, 0, LEGH + 220))
        b += H.line(100 + a[0] * 0.09, 112 - a[1] * 0.09, 100 + b2[0] * 0.09, 112 - b2[1] * 0.09, 0.12, "#555", "2 1.5")
    b += H.bi(215, 34, "PROPOSED SEQUENCE (Production decides)", "تسلسل مقترح (القرار للإنتاج)", 2.8, bold=True)
    steps = [("Laser cut P1 to P6 from 3 mm sheet. Fold P3 (2 folds) and P5 (8 folds).", "قص الليزر للقطع ل١ حتى ل٦ من صاج ٣ مم. ثني ل٣ (ثنيتان) ول٥ (٨ ثنيات)."),
             ("Weld each leg: the band closes at its seam, then the cap plate on top.", "لحام كل رجل: يُقفل الشريط عند وصلته ثم لوح العلوي."),
             ("Build the box: bottom plate, 2 long sides, 2 end bands, then the top plate.", "تجميع الصندوق: اللوح السفلي، الجانبان الطويلان، الشريطان الطرفيان، ثم اللوح العلوي."),
             ("Set the legs 40 in from each end and fix them to the box underside.", "ضبط الرجلين على بعد ٤٠ من كل طرف وتثبيتهما أسفل الصندوق."),
             ("Dress the seams, brush the finish, fit glides if wanted.", "تنعيم الوصلات، التفريش، وإضافة قواعد أرضية إن لزم.")]
    for i, (en, ar) in enumerate(steps):
        yy = 44 + i * 17
        b += H.txt(215, yy, f"{i + 1}.", 2.4, bold=True) + H.bi(221, yy, en, ar, 2.1)
    ns = 1 / 16
    for k, parts in enumerate(nest_layout()):
        nx, ny = 20 + k * 195, 156
        b += H.bi(nx, 142, f"CUTTING SHEET {k + 1}  1:16  (assumed 1250 x 2500 x 3)", f"لوح القص {k + 1} (مفترض ١٢٥٠ × ٢٥٠٠ × ٣)", 2.4, bold=True)
        b += f'<rect x="{nx}" y="{ny}" width="{2500 * ns:.2f}" height="{1250 * ns:.2f}" fill="#fafafa" stroke="{INK}" stroke-width="0.3"/>'
        for kind, x, y, vert in parts:
            if kind == "oct_box": pts = [(x + L / 2 + px_, y + D / 2 + py_) for px_, py_ in BOX_OCT]
            elif kind == "oct_leg": pts = [(x + LL / 2 + px_, y + LD / 2 + py_) for px_, py_ in LEG_OCT]
            elif kind == "long": pts = [(x, y), (x + SEG_A, y), (x + SEG_A, y + BOXH), (x, y + BOXH)]
            elif kind == "end":
                pts = [(x, y), (x + BOXH, y), (x + BOXH, y + END_BAND), (x, y + END_BAND)]
            else: pts = [(x, y), (x + LEG_BAND, y), (x + LEG_BAND, y + LEGH), (x, y + LEGH)]
            d = "M" + " L".join(f"{nx + px_ * ns:.2f},{ny + (1250 - py_) * ns:.2f}" for px_, py_ in pts) + " Z"
            b += f'<path d="{d}" fill="#e6e2d8" stroke="{INK}" stroke-width="0.3"/>'
        b += H.hdim(nx, nx + 2500 * ns, ny + 1250 * ns + 6, "2500", size=2.0)
    b += H.txt(20, 250, f"Total cutting length {cl['total'] / 1000:.1f} m on 2 sheets. Part spacing 30 mm, edge margin 10 mm (assumed).", 2.3, bold=True)
    b += H.txt(20, 256, "Sheet 2 has room left over. Sheet size is Production's.", 2.0, fill="#555")
    sheets.append(("assembly-cutting", sheet(3, 4, "Assembly and cutting layout", "التركيب وتوزيع القص", "1:11 / 1:16", b, logo)))

    # ---- sheet 4: BOM and notes
    b = ""
    b += H.bi(20, 34, "BILL OF MATERIALS", "قائمة المكونات", 2.8, bold=True)
    rows = [[("Item", "بند"), ("Part", "الجزء"), ("Qty", "العدد"), ("Material / process", "الخامة / الطريقة"), ("Size", "المقاس"), ("Finish", "التشطيب")],
            ["P1", ("Top plate", "لوح علوي"), "1", ("Steel sheet 3, laser cut (proposed)", "صاج ٣ مم قص ليزر (مقترح)"), f"{L:.0f} x {D:.0f}, cuts {CB:.0f}", ("Brushed, to confirm", "مصنفر، للتأكيد")],
            ["P2", ("Bottom plate", "لوح سفلي"), "1", ("Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر"), f"{L:.0f} x {D:.0f}, cuts {CB:.0f}", "-"],
            ["P3", ("End band", "شريط طرفي"), "2", ("Steel sheet 3, cut and folded twice", "صاج ٣ مم، قص وثني مرتين"), f"{END_BAND:.1f} x {BOXH:.0f}", ("Brushed, to confirm", "مصنفر، للتأكيد")],
            ["P4", ("Long side plate", "لوح جانبي طويل"), "2", ("Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر"), f"{SEG_A:.0f} x {BOXH:.0f}", ("Brushed, to confirm", "مصنفر، للتأكيد")],
            ["P5", ("Leg band", "شريط الرجل"), "2", ("Steel sheet 3, cut and folded 8 times", "صاج ٣ مم، قص وثني ٨ مرات"), f"{LEG_BAND:.1f} x {LEGH:.0f}", ("Brushed, to confirm", "مصنفر، للتأكيد")],
            ["P6", ("Leg cap plate", "لوح علوي للرجل"), "2", ("Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر"), f"{LL:.0f} x {LD:.0f}, cuts {CL:.0f}", "-"],
            ["G", ("Floor glides", "قواعد أرضية"), "to follow", ("Not visible in the photo. Production to propose", "غير ظاهرة في الصورة. يقترحها الإنتاج"), "to follow", "-"]]
    b += H.table(20, 40, [10, 36, 14, 110, 60, 62], rows, 8.0, 2.1)
    notes = [
        ("Reference: one lifestyle photo (library item 'Coffee Tables ref 4'). Drawn exact to the reference by Sabry's standing rule.", "المرجع: صورة واحدة (عنصر المكتبة). مرسوم مطابقاً للمرجع حسب قاعدة صبري."),
        ("No dimensions came with the photo. Every size is estimated from it, using the wine glass and the sofa for scale. Sabry to confirm.", "لم تصل أبعاد مع الصورة. كل المقاسات تقديرية بمقارنة الكأس والكنبة. يؤكدها صبري."),
        (f"Estimated overall {L:.0f} x {D:.0f} x {HT:.0f}. Box height {BOXH:.0f}, corner cuts {CB:.0f}. Two leg blocks {LL:.0f} x {LD:.0f}, {LEGH:.0f} high, {INSET:.0f} in from each end.", f"التقدير الكلي {ar_num(f'{L:.0f}')} × {ar_num(f'{D:.0f}')} × {ar_num(f'{HT:.0f}')}. ارتفاع الصندوق {ar_num(f'{BOXH:.0f}')}، قطع الأركان {ar_num(f'{CB:.0f}')}."),
        ("The photo shows only the near leg in full and part of the far one. The drawing assumes two identical, symmetric legs.", "الصورة تُظهر الرجل القريبة كاملة وجزءاً من البعيدة. الرسم يفترض رجلين متطابقتين."),
        ("Build proposed in 3 mm sheet: hollow box and hollow legs, crisp corners as in the photo. Production decides folds, welds and seam finishing.", "التنفيذ المقترح من صاج ٣ مم: صندوق ورجلان مجوفان بزوايا حادة. الإنتاج يقرر الثني واللحام والتشطيب."),
        ("Finish: brushed metal in a warm champagne-bronze tone, as the photo. Material (stainless or other) and method are Production's. No painted colour chosen.", "التشطيب: معدن مصنفر بدرجة شمبانيا-برونز كما في الصورة. الخامة والطريقة يحددها الإنتاج."),
        ("Leg underside is left open on the drawing. Closing it, bracing and weight are Production's. No structural claim is made.", "أسفل الرجل مفتوح في الرسم. التقفيل والتدعيم والوزن للإنتاج. لا توجد ادعاءات إنشائية."),
        ("We propose; Production decides sheet size and thickness, tolerances, joints, glides and finish details.", "نحن نقترح، والإنتاج يحدد مقاس الصاج وسماكته والتفاوتات والوصلات والقواعد والتشطيب."),
        ("Cutting layout uses an assumed 1250 x 2500 x 3 sheet, 2 sheets. No costs or prices are on this drawing.", "توزيع القص على لوح مفترض ١٢٥٠ × ٢٥٠٠ × ٣، لوحان. لا أسعار أو تكاليف هنا."),
        ("Arabic wording is a draft and needs a technical reader before it goes to the factory.", "الصياغة العربية مسودة وتحتاج مراجعة فنية قبل الإرسال للمصنع."),
    ]
    b += H.bi(20, 112, "NOTES", "ملاحظات", 2.8, bold=True)
    for i, (en, ar) in enumerate(notes):
        yy = 121 + i * 12.0
        b += H.txt(20, yy, f"{i + 1}.", 2.3, bold=True) + H.txt(27, yy, en, 2.3)
        b += H.txt(409, yy + 4.6, ar, 2.3, "start", False, "#444", ar=True)
    sheets.append(("bom-notes", sheet(4, 4, "Bill of materials and notes", "قائمة المكونات والملاحظات", "-", b, logo)))
    return sheets


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = "data:image/svg+xml;base64," + base64.b64encode(open(os.path.join(ROOT, "brand", "objekt-logo.svg"), "rb").read()).decode()
    ref = H.img_uri(os.path.join(ROOT, "images", "OBJ-020.jpg"), 800)
    svgs = []
    for i, (name, svg) in enumerate(build(logo, ref)):
        p = os.path.join(OUT, f"{PRE}sheet{i + 1}_{name}.svg"); open(p, "w", encoding="utf-8").write(svg); svgs.append(p)
    js = os.path.join(OUT, "_topdf.js")
    open(js, "w").write("""
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
for(const f of process.argv.slice(2)){const svg=fs.readFileSync(f,'utf8');
await p.setContent('<html><body style="margin:0">'+svg+'</body></html>');
await p.pdf({path:f.replace('.svg','.pdf'),width:'420mm',height:'297mm',printBackground:true,pageRanges:'1'});}
await b.close();})();""")
    subprocess.run(["node", js] + svgs, check=True, env={**os.environ, "NODE_PATH": subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()})
    os.remove(js)
    import fitz
    doc = fitz.open()
    for s_ in svgs:
        pp = s_.replace(".svg", ".pdf"); d = fitz.open(pp); doc.insert_pdf(d); d.close(); os.remove(pp)
    doc.save(os.path.join(OUT, PRE + "drawings.pdf"), deflate=True, garbage=4); doc.close()
    write_dxf()
    cl = cut_lengths()
    print({k: round(v, 1) for k, v in cl.items()}, "end band", round(END_BAND, 1), "leg band", round(LEG_BAND, 1), "gap", GAP)


if __name__ == "__main__":
    main()
