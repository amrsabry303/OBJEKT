"""OBJ-020 coffee table (library item 'Coffee Tables ref 4'), rev 2: drawing set (A3, EN/AR) + DXF.

Rev 2 (11 Nov 2026): Sabry gave the overall size, 1000 W x 600 D x 300 H mm, and two clearer photos.
The shape is read from the photos and is APPROXIMATE (traced by eye, not measured): an irregular
polygon top with a slight crease in the front face, on two block legs, in a two-tone finish
(brushed silver top, bronze sides and legs). Everything except the three overall sizes is estimated.

Proposed build: 3 mm sheet, hollow box and hollow legs. Production decides everything about joints and finish.

Run: python3 make_obj020_rev2.py     Needs: numpy ezdxf pymupdf pillow, node + playwright.
Output: venture/drawings/OBJ-020/
"""
import base64, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_obj177_rev1 as H          # drawing helpers only (txt, bi, line, hdim, vdim, table, ...)

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "venture", "drawings", "OBJ-020")
PID, REV, DATE = "OBJ-020", "2", "11 Nov 2026"
PRE = f"{PID}_rev{REV}_"
STAMP_EN, STAMP_AR = H.STAMP_EN, H.STAMP_AR
INK = H.INK

# ---------------------------------------------------------------- geometry (mm)
L, D, HT = 1000.0, 600.0, 300.0         # overall: GIVEN by Sabry (100 x 60 x 30 cm)
BOXH = 165.0                            # box height, estimated from the photos
LEGH = HT - BOXH                        # leg height 135
T = 3.0                                 # sheet thickness (proposed; Production decides)
# top outline, counter-clockwise from the front-left corner, y = 0 at the front. ESTIMATED from the photos.
BOX_POLY = [(0, 25), (490, 0), (935, 20), (1000, 130), (1000, 470), (930, 600), (190, 600), (25, 325)]
# legs, ESTIMATED: A is a plain block, B has its two right corners cut
LEG_A = [(50, 60), (260, 60), (260, 330), (50, 330)]
_B = [(-95, -165), (45, -165), (95, -115), (95, 115), (45, 165), (-95, 165)]
LEG_B = [(x + 865, y + 245) for x, y in _B]


def ar_num(txt):
    return str(txt).translate(str.maketrans('0123456789.', '٠١٢٣٤٥٦٧٨٩٫'))


def edges(poly):
    return [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]


def elen(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def perimeter(poly):
    return sum(elen(a, b) for a, b in edges(poly))


def area_poly(poly):
    return 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))))


def norm(poly):
    mx = min(p[0] for p in poly); my = min(p[1] for p in poly)
    return [(x - mx, y - my) for x, y in poly]


BOX_E = [elen(a, b) for a, b in edges(BOX_POLY)]          # 8 edge lengths
# band strips of the box wall (each strip is folded at the corners between its edges)
B_FRONT = BOX_E[0] + BOX_E[1] + BOX_E[2]                  # front crease plane + plane + chamfer  (2 folds)
B_RIGHT = BOX_E[3] + BOX_E[4]                             # right end + back-right chamfer       (1 fold)
B_BACK = BOX_E[5]                                         # back plate                          (flat)
B_LEFT = BOX_E[6] + BOX_E[7]                              # left chamfer + left end              (1 fold)
LEGA_E = [elen(a, b) for a, b in edges(LEG_A)]
LEGB_E = [elen(a, b) for a, b in edges(LEG_B)]


def leg_segments(poly, start_mid_edge):
    """Band segments for a leg with the seam in the middle of edge start_mid_edge: half, the rest, then the other half."""
    el = [elen(a, b) for a, b in edges(poly)]
    n = len(el)
    segs = [el[start_mid_edge] / 2]
    for k in range(1, n):
        segs.append(el[(start_mid_edge + k) % n])
    segs.append(el[start_mid_edge] / 2)
    return segs


LEGA_SEGS = leg_segments(LEG_A, 0)      # seam in the middle of the front face
LEGB_SEGS = leg_segments(LEG_B, 5)      # seam in the middle of the left (long) face


def folds_of(segs):
    return list(np.cumsum(segs)[:-1])


# ---------------------------------------------------------------- 3D prisms and projections
def prism(poly, z0, z1):
    faces = [("top", [(x, y, z1) for x, y in poly])]
    for a, b in edges(poly):
        faces.append(("side", [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]))
    return faces


def view_iso(p, az=-35.0, el=28.0):
    a, e = math.radians(az), math.radians(el)
    x = p[0] * math.cos(a) - p[1] * math.sin(a)
    y = p[0] * math.sin(a) + p[1] * math.cos(a)
    return (x, p[2] * math.cos(e) + y * math.sin(e), y * math.cos(e) - p[2] * math.sin(e))


def to_cam(az=-35.0, el=28.0):
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


SILVER = "#d9d6cf"                                       # brushed silver top
BRZ_LIT, BRZ_MID, BRZ_DARK = "#a08a6c", "#8a7458", "#746049"   # bronze sides and legs


def shade(n):
    if n[2] > 0.9:
        return SILVER
    light = np.array([-0.5, -0.6, 0.65]); light /= np.linalg.norm(light)
    v = float(np.dot(n, light))
    return BRZ_LIT if v > 0.25 else (BRZ_MID if v > -0.15 else BRZ_DARK)


def draw_iso(ox, oy, s, lift=0.0):
    cam = np.array(to_cam())
    svg = ""
    groups = [prism(LEG_A, 0, LEGH), prism(LEG_B, 0, LEGH), prism(BOX_POLY, LEGH + lift, HT + lift)]
    for fa in groups:
        vis = [(f, view_iso(np.mean(np.array(f[1]), axis=0))) for f in fa if float(np.dot(normal(f[1]), cam)) > 0.02]
        vis.sort(key=lambda t: -t[1][2])
        for f, _ in vis:
            svg += poly_svg([view_iso(q)[:2] for q in f[1]], ox, oy, s, shade(normal(f[1])))
    return svg


def draw_front(ox, oy, s):
    """Front elevation, looking along +y; oy = floor line."""
    svg = ""
    for x0, x1, lines in ((50, 260, ()), (770, 960, (910,))):
        svg += poly_svg([(x0, 0), (x1, 0), (x1, LEGH), (x0, LEGH)], ox, oy, s, BRZ_MID)
        for xx in lines:
            svg += H.line(ox + xx * s, oy, ox + xx * s, oy - LEGH * s, 0.2)
    svg += poly_svg([(0, LEGH), (L, LEGH), (L, HT), (0, HT)], ox, oy, s, BRZ_LIT)
    for xx in (490, 935):
        svg += H.line(ox + xx * s, oy - LEGH * s, ox + xx * s, oy - HT * s, 0.2)
    svg += poly_svg([(0, HT), (L, HT), (L, HT + 0.01), (0, HT + 0.01)], ox, oy, s, SILVER, w=1.1)
    return svg


def draw_end(ox, oy, s):
    """End elevation, looking along -x (from the right-hand end); u = y."""
    svg = ""
    svg += poly_svg([(60, 0), (330, 0), (330, LEGH), (60, LEGH)], ox, oy, s, BRZ_DARK)
    svg += poly_svg([(80, 0), (410, 0), (410, LEGH), (80, LEGH)], ox, oy, s, BRZ_MID)
    for yy in (130, 360):
        svg += H.line(ox + yy * s, oy, ox + yy * s, oy - LEGH * s, 0.2)
    svg += poly_svg([(0, LEGH), (D, LEGH), (D, HT), (0, HT)], ox, oy, s, BRZ_LIT)
    for yy in (20, 130, 470):
        svg += H.line(ox + yy * s, oy - LEGH * s, ox + yy * s, oy - HT * s, 0.2)
    svg += poly_svg([(0, HT), (D, HT), (D, HT + 0.01), (0, HT + 0.01)], ox, oy, s, SILVER, w=1.1)
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
             ("FINISH / التشطيب", "Top brushed silver, sides and legs bronze (to be confirmed)", 0, 24.6, 100),
             ("DRAWN / رسم", "objekt", 100, 24.6, 50)]
    for lab, val, cx, cy, cw in cells:
        s += f'<rect x="{bx + cx}" y="{by + cy}" width="{cw}" height="12.3" fill="none" stroke="{INK}" stroke-width="0.15"/>'
        s += H.txt(bx + cx + 1.3, by + cy + 3.6, lab, 1.9, fill="#666") + H.txt(bx + cx + 1.3, by + cy + 9.2, val, 2.5 if len(val) < 30 else 1.9, bold=True)
    return s + "</svg>"


# ---------------------------------------------------------------- parts, nesting, DXF
def parts():
    """key, name, qty, kind, data. 'poly' = flat polygon (origin at its lower-left); 'band' = (length, height, folds)."""
    return [
        ("P1_top_plate", "Top plate", 1, "poly", norm(BOX_POLY)),
        ("P2_bottom_plate", "Bottom plate", 1, "poly", norm(BOX_POLY)),
        ("P3_front_band", "Front band", 1, "band", (B_FRONT, BOXH, [BOX_E[0], BOX_E[0] + BOX_E[1]])),
        ("P4_right_band", "Right end band", 1, "band", (B_RIGHT, BOXH, [BOX_E[3]])),
        ("P5_back_plate", "Back plate", 1, "band", (B_BACK, BOXH, [])),
        ("P6_left_band", "Left end band", 1, "band", (B_LEFT, BOXH, [BOX_E[6]])),
        ("P7_legA_band", "Leg A band", 1, "band", (sum(LEGA_SEGS), LEGH, folds_of(LEGA_SEGS))),
        ("P8_legA_cap", "Leg A cap plate", 1, "poly", norm(LEG_A)),
        ("P9_legB_band", "Leg B band", 1, "band", (sum(LEGB_SEGS), LEGH, folds_of(LEGB_SEGS))),
        ("P10_legB_cap", "Leg B cap plate", 1, "poly", norm(LEG_B)),
    ]


def nest_layout():
    """key -> (x, y, vertical) lower-left corner in mm on one 2500 x 1250 sheet; 10 mm margin, 30 mm spacing."""
    return {
        "P1_top_plate": (10, 640, False), "P2_bottom_plate": (10, 10, False),
        "P3_front_band": (1040, 1075, False), "P5_back_plate": (1040, 880, False),
        "P6_left_band": (1040, 685, False), "P4_right_band": (1040, 490, False),
        "P8_legA_cap": (1040, 190, False), "P10_legB_cap": (1280, 130, False),
        "P7_legA_band": (1810, 10, True), "P9_legB_band": (1975, 10, True),
    }


def part_pts(kind, data, x, y, vert):
    if kind == "poly":
        return [(x + a, y + b) for a, b in data]
    w, h, _ = data
    return [(x, y), (x + h, y), (x + h, y + w), (x, y + w)] if vert else [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def cut_lengths():
    out = {}
    tot = 0.0
    for key, name, qty, kind, data in parts():
        pts = part_pts(kind, data, 0, 0, False)
        per = perimeter(pts) if kind == "poly" else 2 * (data[0] + data[1])
        out[key] = per * qty; tot += per * qty
    out["total"] = tot
    return out


def write_dxf():
    import ezdxf
    def new():
        d = ezdxf.new("R2010"); d.units = 4
        d.layers.add("CUT", color=7); d.layers.add("BEND", color=5, linetype="DASHED"); d.layers.add("NOTE", color=8)
        return d
    def put(m, kind, data, x, y, vert):
        m.add_lwpolyline(part_pts(kind, data, x, y, vert), close=True, dxfattribs={"layer": "CUT"})
        if kind == "band":
            for f in data[2]:
                if vert: m.add_line((x, y + f), (x + data[1], y + f), dxfattribs={"layer": "BEND"})
                else: m.add_line((x + f, y), (x + f, y + data[1]), dxfattribs={"layer": "BEND"})
    files = []
    for key, name, qty, kind, data in parts():
        d = new(); put(d.modelspace(), kind, data, 0, 0, False)
        d.modelspace().add_text(f"{PID} rev {REV} {key} x{qty}. mm. 3 mm sheet (proposed). Shape traced from photos, approximate. DRAFT.",
                                dxfattribs={"layer": "NOTE", "height": 8}).set_placement((0, -30))
        p = os.path.join(OUT, PRE + key + ".dxf"); d.saveas(p); files.append(p)
    d = new(); d.layers.add("SHEET", color=1); m = d.modelspace()
    m.add_lwpolyline([(0, 0), (2500, 0), (2500, 1250), (0, 1250)], close=True, dxfattribs={"layer": "SHEET"})
    nl = nest_layout()
    for key, name, qty, kind, data in parts():
        x, y, vert = nl[key]; put(m, kind, data, x, y, vert)
    p = os.path.join(OUT, PRE + "nest_1250x2500.dxf"); d.saveas(p); files.append(p)
    return files


# ---------------------------------------------------------------- sheets
def build(logo, ref):
    sheets = []
    cl = cut_lengths()
    # ---- sheet 1: views
    s = 1 / 8
    b = ""
    b += H.bi(20, 34, "FRONT ELEVATION  1:8", "المسقط الأمامي", 2.8, bold=True)
    ox, oy = 40, 100
    b += draw_front(ox, oy, s)
    b += H.hdim(ox, ox + L * s, oy + 8, f"{L:.0f}")
    b += H.vdim(ox + L * s + 6, oy - HT * s, oy, f"{HT:.0f}")
    b += H.vdim(ox - 6, oy - LEGH * s, oy, f"{LEGH:.0f} est.", side=-1)
    b += H.balloon(ox + 20, oy - HT * s - 12, "1", ox + 40 * s * 3, oy - (LEGH + BOXH * 0.6) * s)
    b += H.balloon(ox + 100, oy - HT * s - 12, "2", ox + 865 * s, oy - LEGH * 0.5 * s)
    b += H.bi(20, 120, "PLAN  1:8", "المسقط الأفقي", 2.8, bold=True)
    px, py = 40, 135
    b += poly_svg([(x, D - y) for x, y in BOX_POLY], px, py + D * s, s, SILVER)
    for lg in (LEG_A, LEG_B):
        b += poly_svg([(x, D - y) for x, y in lg], px, py + D * s, s, "none", "#777", 0.2, "3 1.2")
    b += H.hdim(px, px + L * s, py + D * s + 8, f"{L:.0f}")
    b += H.vdim(px + L * s + 6, py, py + D * s, f"{D:.0f}")
    b += H.txt(px, py + D * s + 17, "front edge at the bottom; legs under the top: dashed", 2.0, fill="#555")
    b += H.bi(190, 34, "END ELEVATION  1:8 (from the right)", "المسقط الجانبي (من اليمين)", 2.8, bold=True)
    sx = 195
    b += draw_end(sx, oy, s)
    b += H.hdim(sx, sx + D * s, oy + 8, f"{D:.0f}")
    b += H.bi(190, 120, "VIEW", "منظور", 2.8, bold=True)
    b += draw_iso(268, 205, 0.1)
    b += H.bi(330, 34, "REFERENCE (photos, third party)", "المرجع (صور من طرف ثالث)", 2.1, bold=True)
    b += H.image(330, 40, 80, 80, ref, True) + H.txt(330, 124, "Reference only. Not our piece.", 1.9, fill="#555")
    rows = [[("Part", "الجزء"), ("", ""), ("Finish (from the photos)", "التشطيب (من الصور)"), ("Note", "ملاحظة")],
            [("1 Top face", "الوجه العلوي"), ("swatch", "#d9d6cf"), ("Brushed silver metal", "معدن فضي مصنفر"), ("to be confirmed", "للتأكيد")],
            [("1 Box sides", "جوانب الصندوق"), ("swatch", "#8a7458"), ("Bronze-brown, satin", "برونزي بني، ساتان"), ("not an objekt paint colour", "ليس لون دهان objekt")],
            [("2 Legs (2)", "الأرجل (٢)"), ("swatch", "#8a7458"), ("Same as the box sides", "كجوانب الصندوق"), ("method is Production's", "الطريقة للإنتاج")]]
    b += H.bi(20, 224, "FINISH", "التشطيب", 2.6, bold=True)
    b += H.table(20, 230, [24, 10, 56, 50], rows, 7.0, 1.9)
    b += H.txt(150, 262, "Hex is only a screen guess from the photos.", 1.8, fill="#555")
    b += H.bi(20, 270, "1 Box  2 Leg block (2 off)", "١ الصندوق   ٢ كتلة رجل (٢)", 2.3)
    b += H.bi(85, 270, "1000 x 600 x 300 are Sabry's sizes. The shape is traced from photos: approximate.", "١٠٠٠ × ٦٠٠ × ٣٠٠ مقاسات صبري. الشكل مرسوم من الصور: تقريبي.", 2.1)
    sheets.append(("views", sheet(1, 4, "Views and overall sizes", "المساقط والمقاسات", "1:8", b, logo)))

    # ---- sheet 2: parts at 1:7
    b = ""
    s7 = 1 / 7
    b += H.bi(20, 34, "P1 TOP PLATE (1) and P2 BOTTOM PLATE (1), same outline  1:7", "ل١ لوح علوي (١) ول٢ لوح سفلي (١)، نفس الشكل", 2.6, bold=True)
    x0, y0 = 22, 44
    P = [(x0 + x * s7, y0 + (D - y) * s7) for x, y in BOX_POLY]
    b += f'<path d="M{" L".join(f"{x:.2f},{y:.2f}" for x, y in P)} Z" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
    for i, (a, c) in enumerate(edges(BOX_POLY)):
        mx, my = (a[0] + c[0]) / 2, (a[1] + c[1]) / 2
        px_, py_ = x0 + mx * s7, y0 + (D - my) * s7
        # push the label inward a little
        cx, cy = x0 + 500 * s7, y0 + 300 * s7
        vx, vy = cx - px_, cy - py_; ln = math.hypot(vx, vy)
        b += H.txt(px_ + vx / ln * 4, py_ + vy / ln * 4 + 0.7, f"{elen(a, c):.0f}", 1.9, "middle", fill="#333")
    b += H.hdim(x0, x0 + L * s7, y0 + D * s7 + 7, f"{L:.0f}")
    b += H.vdim(x0 + L * s7 + 6, y0, y0 + D * s7, f"{D:.0f}")
    b += H.txt(x0, y0 + D * s7 + 15, "Corner points (x, y from the lower-left): " + "  ".join(f"({x:.0f},{y:.0f})" for x, y in BOX_POLY), 1.8, fill="#444")
    b += H.txt(x0, y0 + D * s7 + 19, "Edge lengths shown inside the outline. Outline traced from the photos: approximate.", 1.8, fill="#444")
    xa = 190
    b += H.bi(xa, 34, "P8 LEG A CAP (1)", "ل٨ غطاء الرجل أ (١)", 2.4, bold=True)
    for key, name, qty, kind, data in parts():
        if key == "P8_legA_cap":
            w_, h_ = max(p[0] for p in data), max(p[1] for p in data)
            b += f'<rect x="{xa}" y="48" width="{w_ * s7:.2f}" height="{h_ * s7:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
            b += H.hdim(xa, xa + w_ * s7, 48 + h_ * s7 + 6, f"{w_:.0f}", size=1.9)
            b += H.vdim(xa + w_ * s7 + 4, 48, 48 + h_ * s7, f"{h_:.0f}", size=1.9)
    xb = 245
    b += H.bi(xb, 34, "P10 LEG B CAP (1)", "ل١٠ غطاء الرجل ب (١)", 2.4, bold=True)
    LB = norm(LEG_B)
    wB, hB = max(p[0] for p in LB), max(p[1] for p in LB)
    P = [(xb + x * s7, 48 + (hB - y) * s7) for x, y in LB]
    b += f'<path d="M{" L".join(f"{x:.2f},{y:.2f}" for x, y in P)} Z" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
    b += H.hdim(xb, xb + wB * s7, 48 + hB * s7 + 6, f"{wB:.0f}", size=1.9)
    b += H.vdim(xb + wB * s7 + 4, 48, 48 + hB * s7, f"{hB:.0f}", size=1.9)
    b += H.txt(xb, 48 + hB * s7 + 14, "two corners cut 50 x 50", 1.8, fill="#555")
    # bands
    def band(xp, yp, label_en, label_ar, w, h, folds, segs=None, note=None):
        r = ""
        r += H.bi(xp - 2, yp - 11, label_en, label_ar, 2.1, bold=True)
        r += f'<rect x="{xp}" y="{yp}" width="{w * s7:.2f}" height="{h * s7:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
        for f in folds:
            r += H.line(xp + f * s7, yp - 2, xp + f * s7, yp + h * s7 + 2, 0.2, "#2255aa", "5 1.2 1 1.2")
        pos = [0.0] + list(folds) + [w]
        for a, c in zip(pos[:-1], pos[1:]):
            r += H.txt(xp + (a + c) / 2 * s7, yp + h * s7 / 2 + 0.7, f"{c - a:.0f}", 1.8, "middle")
        r += H.hdim(xp, xp + w * s7, yp + h * s7 + 5, f"{w:.1f} x {h:.0f}", size=1.9)
        return r
    b += band(22, 165, "P3 FRONT BAND (1), 2 folds  1:7", "ل٣ شريط أمامي (١)، ثنيتان", B_FRONT, BOXH, [BOX_E[0], BOX_E[0] + BOX_E[1]])
    b += band(190, 165, "P4 RIGHT BAND (1), 1 fold", "ل٤ شريط أيمن (١)", B_RIGHT, BOXH, [BOX_E[3]])
    b += band(270, 165, "P5 BACK PLATE (1)", "ل٥ لوح خلفي (١)", B_BACK, BOXH, [])
    b += band(22, 212, "P6 LEFT BAND (1), 1 fold", "ل٦ شريط أيسر (١)", B_LEFT, BOXH, [BOX_E[6]])
    b += band(130, 212, "P7 LEG A BAND (1), 4 folds", "ل٧ شريط الرجل أ (١)", sum(LEGA_SEGS), LEGH, folds_of(LEGA_SEGS))
    b += band(22, 254, "P9 LEG B BAND (1), 6 folds", "ل٩ شريط الرجل ب (١)", sum(LEGB_SEGS), LEGH, folds_of(LEGB_SEGS))
    b += H.txt(172, 262, "Blue dash-dot = fold.", 1.8, fill="#555") + H.txt(172, 266, "Seams in the middle of a long face.", 1.8, fill="#555")
    rows = [[("DATA", "بيانات"), ""],
            [("Overall W x D x H (given)", "العرض × العمق × الارتفاع (معطى)"), f"{L:.0f} x {D:.0f} x {HT:.0f}"],
            [("Box height / leg height (est.)", "ارتفاع الصندوق / الرجل (تقدير)"), f"{BOXH:.0f} / {LEGH:.0f}"],
            [("Leg A block (est.)", "كتلة الرجل أ (تقدير)"), "210 x 270"],
            [("Leg B block (est.)", "كتلة الرجل ب (تقدير)"), "190 x 330"],
            [("Sheet thickness (proposed)", "سماكة الصاج (مقترحة)"), f"{T:.0f}"]]
    b += H.table(300, 60, [58, 52], rows, 6.2, 1.9)
    sheets.append(("parts", sheet(2, 4, "Parts: flat patterns", "القطع: الأشكال المسطحة", "1:7", b, logo)))

    # ---- sheet 3: assembly and cutting
    b = ""
    b += H.bi(20, 34, "EXPLODED VIEW  1:10", "منظور مفكوك", 2.8, bold=True)
    b += draw_iso(60, 118, 0.1, lift=200.0)
    b += H.bi(215, 34, "PROPOSED SEQUENCE (Production decides)", "تسلسل مقترح (القرار للإنتاج)", 2.8, bold=True)
    steps = [("Laser cut P1 to P10 from 3 mm sheet. Fold P3, P4, P6, P7, P9 at the blue lines.", "قص الليزر للقطع من ل١ إلى ل١٠ من صاج ٣ مم. ثني ل٣ ول٤ ول٦ ول٧ ول٩ عند الخطوط الزرقاء."),
             ("Weld each leg: the band closes at its seam, then its cap plate on top.", "لحام كل رجل: يُقفل الشريط عند وصلته ثم غطاؤه العلوي."),
             ("Build the box: bottom plate, the four band and plate pieces round it, then the top plate.", "تجميع الصندوق: اللوح السفلي، القطع الأربع حوله، ثم اللوح العلوي."),
             ("Fix the legs to the box underside as on the plan (dashed outlines).", "تثبيت الرجلين أسفل الصندوق كما في المسقط الأفقي (الخطوط المتقطعة)."),
             ("Dress the seams, then finish: brushed top, bronze sides and legs. Glides if wanted.", "تنعيم الوصلات ثم التشطيب: سطح مصنفر وجوانب وأرجل برونزية. قواعد أرضية إن لزم.")]
    for i, (en, ar) in enumerate(steps):
        yy = 44 + i * 17
        b += H.txt(215, yy, f"{i + 1}.", 2.4, bold=True) + H.bi(221, yy, en, ar, 2.1)
    ns = 1 / 14; nx, ny = 20, 158
    b += H.bi(nx, 142, "CUTTING LAYOUT  1:14  (assumed sheet 1250 x 2500 x 3)", "توزيع القص (لوح مفترض ١٢٥٠ × ٢٥٠٠ × ٣)", 2.6, bold=True)
    b += f'<rect x="{nx}" y="{ny}" width="{2500 * ns:.2f}" height="{1250 * ns:.2f}" fill="#fafafa" stroke="{INK}" stroke-width="0.3"/>'
    nl = nest_layout()
    for key, name, qty, kind, data in parts():
        x, y, vert = nl[key]
        pts = part_pts(kind, data, x, y, vert)
        d = "M" + " L".join(f"{nx + px_ * ns:.2f},{ny + (1250 - py_) * ns:.2f}" for px_, py_ in pts) + " Z"
        b += f'<path d="{d}" fill="#e6e2d8" stroke="{INK}" stroke-width="0.3"/>'
        cxm = sum(p[0] for p in pts) / len(pts); cym = sum(p[1] for p in pts) / len(pts)
        b += H.txt(nx + cxm * ns, ny + (1250 - cym) * ns + 1, key.split("_")[0], 2.2, "middle", fill="#333")
    b += H.hdim(nx, nx + 2500 * ns, ny + 1250 * ns + 6, "2500", size=2.0)
    b += H.vdim(nx + 2500 * ns + 4, ny, ny + 1250 * ns, "1250", size=2.0)
    b += H.txt(20, 262, f"Total cutting length {cl['total'] / 1000:.1f} m on one assumed sheet. Part spacing 30 mm, edge margin 10 mm (assumed).", 2.3, bold=True)
    b += H.txt(20, 268, "Sheet size and nesting are Production's.", 2.0, fill="#555")
    sheets.append(("assembly-cutting", sheet(3, 4, "Assembly and cutting layout", "التركيب وتوزيع القص", "1:10 / 1:14", b, logo)))

    # ---- sheet 4: BOM and notes
    b = ""
    b += H.bi(20, 34, "BILL OF MATERIALS", "قائمة المكونات", 2.8, bold=True)
    def row(k, en, ar, qty, proc_en, proc_ar, size, fin_en="Brushed silver" , fin_ar="فضي مصنفر"):
        return [k, (en, ar), str(qty), (proc_en, proc_ar), size, (fin_en, fin_ar)]
    rows = [[("Item", "بند"), ("Part", "الجزء"), ("Qty", "العدد"), ("Material / process", "الخامة / الطريقة"), ("Size", "المقاس"), ("Finish (to confirm)", "التشطيب (للتأكيد)")],
            row("P1", "Top plate", "لوح علوي", 1, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", f"{L:.0f} x {D:.0f}"),
            row("P2", "Bottom plate", "لوح سفلي", 1, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", f"{L:.0f} x {D:.0f}", "-", "-"),
            row("P3", "Front band", "شريط أمامي", 1, "Steel sheet 3, cut, folded twice", "صاج ٣ مم، قص وثني مرتين", f"{B_FRONT:.1f} x {BOXH:.0f}", "Bronze", "برونزي"),
            row("P4", "Right end band", "شريط أيمن", 1, "Steel sheet 3, cut, folded once", "صاج ٣ مم، قص وثني مرة", f"{B_RIGHT:.1f} x {BOXH:.0f}", "Bronze", "برونزي"),
            row("P5", "Back plate", "لوح خلفي", 1, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", f"{B_BACK:.0f} x {BOXH:.0f}", "Bronze", "برونزي"),
            row("P6", "Left end band", "شريط أيسر", 1, "Steel sheet 3, cut, folded once", "صاج ٣ مم، قص وثني مرة", f"{B_LEFT:.1f} x {BOXH:.0f}", "Bronze", "برونزي"),
            row("P7", "Leg A band", "شريط الرجل أ", 1, "Steel sheet 3, cut, folded 4 times", "صاج ٣ مم، قص وثني ٤ مرات", f"{sum(LEGA_SEGS):.0f} x {LEGH:.0f}", "Bronze", "برونزي"),
            row("P8", "Leg A cap plate", "غطاء الرجل أ", 1, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", "210 x 270", "Bronze", "برونزي"),
            row("P9", "Leg B band", "شريط الرجل ب", 1, "Steel sheet 3, cut, folded 6 times", "صاج ٣ مم، قص وثني ٦ مرات", f"{sum(LEGB_SEGS):.1f} x {LEGH:.0f}", "Bronze", "برونزي"),
            row("P10", "Leg B cap plate", "غطاء الرجل ب", 1, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", "190 x 330", "Bronze", "برونزي"),
            row("G", "Floor glides", "قواعد أرضية", "-", "Not visible in the photos. Production to propose", "غير ظاهرة في الصور. يقترحها الإنتاج", "to follow", "-", "-")]
    b += H.table(20, 40, [10, 36, 12, 100, 52, 50], rows, 7.2, 2.0)
    notes = [
        ("Overall 1000 W x 600 D x 300 H (100 x 60 x 30 cm) are Sabry's sizes (11 Nov 2026). Everything else is estimated from two photos.", "المقاسات الكلية ١٠٠٠ × ٦٠٠ × ٣٠٠ (١٠٠ × ٦٠ × ٣٠ سم) من صبري (١١ نوفمبر ٢٠٢٦). الباقي تقدير من صورتين."),
        ("Reference: library item 'Coffee Tables ref 4', photos 2 and 3. Drawn exact to the reference by Sabry's standing rule.", "المرجع: عنصر المكتبة، الصورتان ٢ و٣. مرسوم مطابقاً للمرجع حسب قاعدة صبري."),
        ("The top outline is an irregular polygon with the left end narrower and a slight crease in the front face. Corner points are traced by eye: approximate.", "شكل السطح مضلع غير منتظم، الطرف الأيسر أضيق، وفي الواجهة الأمامية ثنية خفيفة. النقاط مرسومة بالعين: تقريبية."),
        (f"Box height {BOXH:.0f} and leg height {LEGH:.0f} are estimates. Leg A (210 x 270) and leg B (190 x 330, two corners cut) positions are estimates.", f"ارتفاع الصندوق {ar_num(f'{BOXH:.0f}')} والرجل {ar_num(f'{LEGH:.0f}')} تقديريان. مواضع الرجلين ومقاساتهما تقديرية."),
        ("Build proposed in 3 mm sheet: hollow box and hollow legs, crisp corners as in the photos. Production decides folds, welds and seams.", "التنفيذ المقترح من صاج ٣ مم: صندوق ورجلان مجوفان بزوايا حادة. الإنتاج يقرر الثني واللحام والوصلات."),
        ("Finish as the photos: brushed silver top, bronze-brown satin sides and legs. Material and method (stainless, plated, painted) are Production's. Hex is a screen guess.", "التشطيب كما في الصور: سطح فضي مصنفر وجوانب وأرجل برونزية. الخامة والطريقة للإنتاج. الرمز تقدير من الشاشة."),
        ("Leg underside is left open on the drawing. Closing it, bracing and weight are Production's. No structural claim is made.", "أسفل الرجل مفتوح في الرسم. التقفيل والتدعيم والوزن للإنتاج. لا توجد ادعاءات إنشائية."),
        ("We propose; Production decides sheet size and thickness, tolerances, joints, glides and finish details.", "نحن نقترح، والإنتاج يحدد مقاس الصاج وسماكته والتفاوتات والوصلات والقواعد والتشطيب."),
        ("Cutting layout uses an assumed 1250 x 2500 x 3 sheet. No costs or prices are on this drawing.", "توزيع القص على لوح مفترض ١٢٥٠ × ٢٥٠٠ × ٣. لا أسعار أو تكاليف هنا."),
        ("Arabic wording is a draft and needs a technical reader before it goes to the factory.", "الصياغة العربية مسودة وتحتاج مراجعة فنية قبل الإرسال للمصنع."),
    ]
    b += H.bi(20, 142, "NOTES", "ملاحظات", 2.8, bold=True)
    for i, (en, ar) in enumerate(notes):
        yy = 150 + i * 9.0
        b += H.txt(20, yy, f"{i + 1}.", 2.1, bold=True) + H.txt(27, yy, en, 2.1)
        b += H.txt(409, yy + 4.0, ar, 2.1, "start", False, "#444", ar=True)
    sheets.append(("bom-notes", sheet(4, 4, "Bill of materials and notes", "قائمة المكونات والملاحظات", "-", b, logo)))
    return sheets


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = "data:image/svg+xml;base64," + base64.b64encode(open(os.path.join(ROOT, "brand", "objekt-logo.svg"), "rb").read()).decode()
    ref = H.img_uri(os.path.join(ROOT, "images", "OBJ-020_2.jpg"), 800)
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
    print("edges", [round(e, 1) for e in BOX_E], "perimeter", round(perimeter(BOX_POLY), 1))
    print({k: round(v, 1) for k, v in cl.items()})


if __name__ == "__main__":
    main()
