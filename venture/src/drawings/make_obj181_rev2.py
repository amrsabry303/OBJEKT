"""OBJ-181 console (library item, 4 photos), rev 2 DRAFT: drawing set (A3, EN/AR) + DXF.

Overall 1200 W x 450 D x 750 H mm are Sabry's (120 x 45 x 75 cm). Everything else is estimated from the three photos.
Same language as OBJ-020: a thick box top with a shallow crease in the middle of the long faces and a V end, and two block legs
whose V ends step inside the top's V. Proposed build: 3 mm sheet, hollow box and hollow legs. Production decides everything.
Moulded or lacquered is also possible: the photos do not say. Drawn as sheet because that is the proposal route used for OBJ-020.

Run: python3 make_obj181_rev2.py     Needs: numpy ezdxf pymupdf pillow, node + playwright.
Output: venture/drawings/OBJ-181/
"""
import base64, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_obj177_rev1 as H          # drawing helpers only (txt, bi, line, hdim, vdim, table, ...)

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "venture", "drawings", "OBJ-181")
PID, REV, DATE = "OBJ-181", "2", "11 Nov 2026"
PRE = f"{PID}_rev{REV}_"
APPROVED = False
if APPROVED:
    STAMP_EN = "Approved by Sabry 11 Nov 2026. Production review pending. Not engineered"
    STAMP_AR = "معتمد من صبري ١١ نوفمبر ٢٠٢٦. مراجعة الإنتاج قيد الانتظار. بدون مراجعة هندسية"
else:
    STAMP_EN, STAMP_AR = H.STAMP_EN, H.STAMP_AR
STAMP_COL = "#1d6b3a" if APPROVED else "#b3261e"
STAMP_BG = "#f0f8f2" if APPROVED else "#fff4f2"
INK = H.INK

# ---------------------------------------------------------------- geometry (mm)


def ccw(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return list(poly) if a > 0 else list(poly)[::-1]


L, D, HT = 1200.0, 450.0, 750.0         # overall: GIVEN by Sabry (120 x 45 x 75 cm)
BOXH = 165.0                            # box height, estimated from the photos (about 22 % of the height)
LEGH = HT - BOXH                        # leg height 585
T = 3.0                                 # sheet thickness (proposed; Production decides)
# top outline, counter-clockwise from the front crease, y = 0 at the front. Symmetric about x = 600 and y = 225:
# a shallow crease (30 deep) in the middle of the front and back faces, and a V point at each end (45 in).
CR, VA = 30.0, 45.0
BOX_POLY = [(600, 0), (L - VA, CR), (L, D / 2), (L - VA, D - CR), (600, D), (VA, D - CR), (0, D / 2), (VA, CR)]
# legs: each has the same V end as the table, its V faces parallel to the table's and stepped INS inside, a flat front,
# back and inner end. ESTIMATED from the 3/4 photo: 340 across (Sabry, front photo), 340 deep, front 55 behind the table front.
INS = 50.0
LY0, LY1 = 55.0, 395.0                                   # leg front and back (y)
LW = 340.0                                               # leg width incl. the V end
_VX = 39.0                                               # x run of the V face from the point to the corner
LEG_R = ccw([(L - INS, D / 2), (L - INS - _VX, LY1), (L - INS - LW, LY1), (L - INS - LW, LY0), (L - INS - _VX, LY0)])
LEG_L = ccw([(L - x, y) for x, y in LEG_R])


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


def ccw(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return list(poly) if a > 0 else list(poly)[::-1]


def norm(poly):
    mx = min(p[0] for p in poly); my = min(p[1] for p in poly)
    return [(x - mx, y - my) for x, y in poly]


BOX_E = [elen(a, b) for a, b in edges(BOX_POLY)]          # 8 edge lengths
FRONT_BAND = BOX_E[7] + BOX_E[0]                          # front-right plane + front-left plane (1 fold at the crease)
END_BAND = BOX_E[1] + BOX_E[2]                            # two end facets (1 fold at the point)


def leg_segments(poly, start_mid_edge):
    """Band segments for a leg with the seam in the middle of edge start_mid_edge."""
    el = [elen(a, b) for a, b in edges(poly)]
    n = len(el)
    segs = [el[start_mid_edge] / 2]
    for k in range(1, n):
        segs.append(el[(start_mid_edge + k) % n])
    segs.append(el[start_mid_edge] / 2)
    return segs


LEG_SEGS = leg_segments(LEG_L, max(range(len(LEG_L)), key=lambda k: elen(*edges(LEG_L)[k])))   # seam in the middle of the inner face
LEG_BAND = sum(LEG_SEGS)


def leg_turns():
    pts = LEG_L
    out = []
    for i in range(len(pts)):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
        d1 = math.atan2(b[1] - a[1], b[0] - a[0]); d2 = math.atan2(c[1] - b[1], c[0] - b[0])
        out.append(abs((math.degrees(d2 - d1) + 180) % 360 - 180))
    return out


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


SILVER = "#b8a891"                                       # top face, lighter taupe
BRZ_LIT, BRZ_MID, BRZ_DARK = "#9a8872", "#80705c", "#675848"   # taupe sides and legs


def shade(n):
    if n[2] > 0.9:
        return SILVER
    light = np.array([-0.5, -0.6, 0.65]); light /= np.linalg.norm(light)
    v = float(np.dot(n, light))
    return BRZ_LIT if v > 0.25 else (BRZ_MID if v > -0.15 else BRZ_DARK)


def draw_iso(ox, oy, s, lift=0.0):
    cam = np.array(to_cam())
    svg = ""
    groups = [prism(LEG_L, 0, LEGH), prism(LEG_R, 0, LEGH), prism(BOX_POLY, LEGH + lift, HT + lift)]
    for fa in groups:
        vis = [(f, view_iso(np.mean(np.array(f[1]), axis=0))) for f in fa if float(np.dot(normal(f[1]), cam)) > 0.02]
        vis.sort(key=lambda t: -t[1][2])
        for f, _ in vis:
            svg += poly_svg([view_iso(q)[:2] for q in f[1]], ox, oy, s, shade(normal(f[1])))
    return svg


def draw_front(ox, oy, s):
    """Front elevation, looking along +y; oy = floor line."""
    svg = ""
    for x0, x1, lines in ((INS, INS + LW, (INS + _VX,)), (L - INS - LW, L - INS, (L - INS - _VX,))):
        svg += poly_svg([(x0, 0), (x1, 0), (x1, LEGH), (x0, LEGH)], ox, oy, s, BRZ_MID)
        for xx in lines:
            svg += H.line(ox + xx * s, oy, ox + xx * s, oy - LEGH * s, 0.2)
    svg += poly_svg([(0, LEGH), (L, LEGH), (L, HT), (0, HT)], ox, oy, s, BRZ_LIT)
    for xx in (VA, 600, L - VA):
        svg += H.line(ox + xx * s, oy - LEGH * s, ox + xx * s, oy - HT * s, 0.2)
    svg += poly_svg([(0, HT), (L, HT), (L, HT + 0.01), (0, HT + 0.01)], ox, oy, s, SILVER, w=1.1)
    return svg


def draw_end(ox, oy, s):
    """End elevation, looking along -x (from the right-hand end); u = y."""
    svg = ""
    svg += poly_svg([(LY0, 0), (LY1, 0), (LY1, LEGH), (LY0, LEGH)], ox, oy, s, BRZ_MID)
    svg += H.line(ox + D / 2 * s, oy, ox + D / 2 * s, oy - LEGH * s, 0.2)
    svg += poly_svg([(0, LEGH), (D, LEGH), (D, HT), (0, HT)], ox, oy, s, BRZ_LIT)
    for yy in (CR, D / 2, D - CR):
        svg += H.line(ox + yy * s, oy - LEGH * s, ox + yy * s, oy - HT * s, 0.2)
    svg += poly_svg([(0, HT), (D, HT), (D, HT + 0.01), (0, HT + 0.01)], ox, oy, s, SILVER, w=1.1)
    return svg


# ---------------------------------------------------------------- sheet frame
def sheet(n, total, t_en, t_ar, scale, body, logo):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm" font-family="{H.FONT}">'
    s += '<rect width="420" height="297" fill="#fff"/>'
    s += f'<rect x="7" y="7" width="406" height="283" fill="none" stroke="{INK}" stroke-width="0.35"/>'
    s += H.image(11, 10.5, 22, 14, logo)
    s += H.txt(38, 17, f"{PID}  Console", 5, bold=True) + H.txt(38, 22.5, t_en, 3.2, fill="#444")
    s += H.txt(409, 17, f"كونسول  {PID}", 5, "start", True, ar=True) + H.txt(409, 22.5, t_ar, 3.2, "start", False, "#444", ar=True)
    s += H.line(7, 27, 413, 27, 0.25)
    s += body
    bx, by, bw, bh = 263, 253, 150, 37
    s += f'<rect x="{bx}" y="{by - 11}" width="{bw}" height="11" fill="{STAMP_BG}" stroke="{STAMP_COL}" stroke-width="0.4"/>'
    s += H.txt(bx + 3, by - 6.3, STAMP_EN, 2.7, bold=True, fill=STAMP_COL) + H.txt(bx + bw - 3, by - 2.2, STAMP_AR, 2.5, "start", False, STAMP_COL, ar=True)
    s += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#fff" stroke="{INK}" stroke-width="0.35"/>'
    cells = [("PRODUCT / المنتج", f"{PID} Console (name to follow)", 0, 0, 75), ("SIZE / المقاس", "A3", 75, 0, 25),
             ("SCALE / المقياس", scale, 100, 0, 25), ("UNITS / الوحدات", "mm", 125, 0, 25),
             ("MATERIAL / الخامة", "Steel sheet 3 mm, laser cut and folded (proposed)", 0, 12.3, 75),
             ("DATE / التاريخ", DATE, 75, 12.3, 25), ("SHEET / لوحة", f"{n} / {total}", 100, 12.3, 25), ("REV / مراجعة", REV, 125, 12.3, 25),
             ("FINISH / التشطيب", "Satin taupe-brown all over (to be confirmed)", 0, 24.6, 100),
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
        ("P3_side_band", "Side band (front and back)", 2, "band", (FRONT_BAND, BOXH, [BOX_E[7]])),
        ("P4_end_band", "End band", 2, "band", (END_BAND, BOXH, [BOX_E[1]])),
        ("P5_leg_band", "Leg band", 2, "band", (LEG_BAND, LEGH, folds_of(LEG_SEGS))),
        ("P6_leg_cap", "Leg cap plate", 2, "poly", norm(LEG_L)),
    ]


def nest_layout():
    """key -> list of (sheet, x, y, vertical), lower-left corners in mm on assumed 2500 x 1250 sheets; 10 mm margin, 30 mm spacing."""
    return {
        "P5_leg_band": [(1, 10, 10, False), (1, 10, 625, False)],
        "P3_side_band": [(1, 1335, 10, False), (2, 10, 970, False)],
        "P4_end_band": [(1, 1335, 205, False), (1, 1775, 205, False)],
        "P6_leg_cap": [(1, 1335, 400, False), (1, 1710, 400, False)],
        "P1_top_plate": [(2, 10, 10, False)], "P2_bottom_plate": [(2, 10, 490, False)],
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
        d.modelspace().add_text(f"{PID} rev {REV} {key} x{qty}. mm. 3 mm sheet (proposed). Shape read from photos, approximate. DRAFT.",
                                dxfattribs={"layer": "NOTE", "height": 8}).set_placement((0, -30))
        p = os.path.join(OUT, PRE + key + ".dxf"); d.saveas(p); files.append(p)
    nl = nest_layout()
    for sh in (1, 2):
        d = new(); d.layers.add("SHEET", color=1); m = d.modelspace()
        m.add_lwpolyline([(0, 0), (2500, 0), (2500, 1250), (0, 1250)], close=True, dxfattribs={"layer": "SHEET"})
        for key, name, qty, kind, data in parts():
            for (sn, x, y, vert) in nl[key]:
                if sn == sh: put(m, kind, data, x, y, vert)
        p = os.path.join(OUT, PRE + f"nest{sh}_1250x2500.dxf"); d.saveas(p); files.append(p)
    return files


# ---------------------------------------------------------------- sheets
def build(logo, ref):
    sheets = []
    cl = cut_lengths()
    nl = nest_layout()
    # ---- sheet 1: views
    s = 1 / 10
    b = ""
    b += H.bi(20, 34, "FRONT ELEVATION  1:10", "المسقط الأمامي", 2.8, bold=True)
    ox, oy = 40, 118
    b += draw_front(ox, oy, s)
    b += H.hdim(ox, ox + L * s, oy + 8, f"{L:.0f}")
    b += H.vdim(ox + L * s + 6, oy - HT * s, oy, f"{HT:.0f}")
    b += H.vdim(ox - 6, oy - LEGH * s, oy, f"{LEGH:.0f} est.", side=-1)
    b += H.balloon(ox + 25, oy - HT * s - 10, "1", ox + 300 * s, oy - (LEGH + BOXH * 0.6) * s)
    b += H.balloon(ox + 100, oy - HT * s - 10, "2", ox + 150 * s, oy - LEGH * 0.5 * s)
    b += H.bi(20, 138, "PLAN  1:10", "المسقط الأفقي", 2.8, bold=True)
    px, py = 40, 148
    b += poly_svg([(x, D - y) for x, y in BOX_POLY], px, py + D * s, s, SILVER)
    for lg in (LEG_L, LEG_R):
        b += poly_svg([(x, D - y) for x, y in lg], px, py + D * s, s, "none", "#777", 0.2, "3 1.2")
    b += H.line(px + 600 * s, py - 4, px + 600 * s, py + D * s + 4, 0.1, "#888", "4 1 1 1")
    b += H.line(px - 4, py + D / 2 * s, px + L * s + 4, py + D / 2 * s, 0.1, "#888", "4 1 1 1")
    b += H.hdim(px, px + L * s, py + D * s + 8, f"{L:.0f}")
    b += H.vdim(px + L * s + 6, py, py + D * s, f"{D:.0f}")
    b += H.txt(px, py + D * s + 17, "front edge at the bottom; legs under the top: dashed; symmetric about both centre lines (assumed)", 2.0, fill="#555")
    b += H.bi(190, 34, "END ELEVATION  1:10 (from the right)", "المسقط الجانبي (من اليمين)", 2.8, bold=True)
    sx = 200
    b += draw_end(sx, oy, s)
    b += H.hdim(sx, sx + D * s, oy + 8, f"{D:.0f}")
    b += H.bi(190, 138, "VIEW", "منظور", 2.8, bold=True)
    b += draw_iso(262, 212, 0.075)
    b += H.bi(330, 34, "REFERENCE (photo, third party)", "المرجع (صورة من طرف ثالث)", 2.1, bold=True)
    b += H.image(330, 40, 80, 80, ref, True) + H.txt(330, 124, "Reference only. Not our piece.", 1.9, fill="#555")
    rows = [[("Part", "الجزء"), ("", ""), ("Finish (from the photos)", "التشطيب (من الصور)"), ("Note", "ملاحظة")],
            [("1 Box and 2 Legs", "الصندوق والأرجل"), ("swatch", "#80705c"), ("Taupe-brown, smooth satin", "بني رمادي، ساتان ناعم"), ("one colour all over, to confirm", "لون واحد، للتأكيد")],
            [("Photo 21 variant", "نسخة الصورة ٢١"), ("swatch", "#b3a58f"), ("Brushed metal, champagne", "معدن مصنفر شامبانيا"), ("seen in one photo only", "في صورة واحدة فقط")]]
    b += H.bi(20, 232, "FINISH", "التشطيب", 2.6, bold=True)
    b += H.table(20, 238, [28, 10, 52, 50], rows, 7.0, 1.9)
    b += H.txt(20, 268, "Hex is only a screen guess from the photos. Not an objekt paint colour: to be chosen from brand/COLOURS-FINISHES.md.", 1.8, fill="#555")
    b += H.bi(20, 276, "1 Box  2 Leg block (2 off, mirrored)", "١ الصندوق   ٢ كتلة رجل (٢، متناظرتان)", 2.3)
    b += H.bi(20, 283, "1200 x 450 x 750 are Sabry's sizes. The shape is read from photos: approximate.", "١٢٠٠ × ٤٥٠ × ٧٥٠ مقاسات صبري. الشكل من الصور: تقريبي.", 2.1)
    sheets.append(("views", sheet(1, 4, "Views and overall sizes", "المساقط والمقاسات", "1:10", b, logo)))

    # ---- sheet 2: parts at 1:10
    b = ""
    sp = 1 / 10
    b += H.bi(20, 34, "P1 TOP PLATE (1) and P2 BOTTOM PLATE (1), same outline  1:10", "ل١ لوح علوي (١) ول٢ لوح سفلي (١)، نفس الشكل", 2.6, bold=True)
    x0, y0 = 22, 44
    P = [(x0 + x * sp, y0 + (D - y) * sp) for x, y in BOX_POLY]
    b += f'<path d="M{" L".join(f"{x:.2f},{y:.2f}" for x, y in P)} Z" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
    for i, (a, c) in enumerate(edges(BOX_POLY)):
        mx, my = (a[0] + c[0]) / 2, (a[1] + c[1]) / 2
        px_, py_ = x0 + mx * sp, y0 + (D - my) * sp
        cx, cy = x0 + 600 * sp, y0 + D / 2 * sp
        vx, vy = cx - px_, cy - py_; ln = math.hypot(vx, vy)
        b += H.txt(px_ + vx / ln * 4, py_ + vy / ln * 4 + 0.7, f"{elen(a, c):.1f}".rstrip('0').rstrip('.'), 1.9, "middle", fill="#333")
    b += H.hdim(x0, x0 + L * sp, y0 + D * sp + 7, f"{L:.0f}")
    b += H.vdim(x0 + L * sp + 6, y0, y0 + D * sp, f"{D:.0f}")
    b += H.txt(x0, y0 + D * sp + 15, "Corner points (x, y from the lower-left): " + " ".join(f"({x:.0f},{y:.0f})" for x, y in BOX_POLY), 1.8, fill="#444")
    b += H.txt(x0, y0 + D * sp + 19, "8 sides, symmetric about both centre lines (assumed). Read from the photos, rounded. Edge lengths inside the outline.", 1.7, fill="#444")
    xb = 175
    b += H.bi(xb, 34, "P6 LEG CAP PLATE (2)  1:10", "ل٦ غطاء الرجل (٢)", 2.2, bold=True)
    LB = norm(LEG_L)
    wB, hB = max(p[0] for p in LB), max(p[1] for p in LB)
    P = [(xb + x * sp, 48 + (hB - y) * sp) for x, y in LB]
    b += f'<path d="M{" L".join(f"{x:.2f},{y:.2f}" for x, y in P)} Z" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
    b += H.hdim(xb, xb + wB * sp, 48 + hB * sp + 6, f"{wB:.0f}", size=1.9)
    b += H.vdim(xb + wB * sp + 4, 48, 48 + hB * sp, f"{hB:.0f}", size=1.9)
    b += H.txt(xb, 48 + hB * sp + 14, "V end like the table, 50 in; flat inner end", 1.8, fill="#555")
    def band(xp, yp, label_en, label_ar, w, h, folds):
        r = ""
        r += H.bi(xp - 2, yp - 11, label_en, label_ar, 2.1, bold=True)
        r += f'<rect x="{xp}" y="{yp}" width="{w * sp:.2f}" height="{h * sp:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
        for f in folds:
            r += H.line(xp + f * sp, yp - 2, xp + f * sp, yp + h * sp + 2, 0.2, "#2255aa", "5 1.2 1 1.2")
        pos = [0.0] + list(folds) + [w]
        for a, c in zip(pos[:-1], pos[1:]):
            r += H.txt(xp + (a + c) / 2 * sp, yp + h * sp / 2 + 0.7, f"{c - a:.1f}".rstrip('0').rstrip('.'), 1.8, "middle")
        r += H.hdim(xp, xp + w * sp, yp + h * sp + 5, f"{w:.1f} x {h:.0f}", size=1.9)
        return r
    b += band(22, 135, "P3 SIDE BAND (2: front and back), 1 fold  1:10", "ل٣ شريط جانبي (٢: أمامي وخلفي)، ثنية واحدة", FRONT_BAND, BOXH, [BOX_E[7]])
    b += band(200, 135, "P4 END BAND (2), 1 fold  1:10", "ل٤ شريط طرفي (٢)، ثنية واحدة", END_BAND, BOXH, [BOX_E[1]])
    b += band(22, 180, "P5 LEG BAND (2), 5 folds  1:10", "ل٥ شريط الرجل (٢)، ٥ ثنيات", LEG_BAND, LEGH, folds_of(LEG_SEGS))
    ta = 2 * math.degrees(math.atan2(CR, 600 - VA))
    b += H.txt(22, 255, "Blue dash-dot = fold. Turn angles: P3 at the crease " + f"{ta:.1f}°; P4 at the end point " + f"{2 * math.degrees(math.atan2(VA, D / 2 - CR)):.1f}°;", 1.8, fill="#555")
    b += H.txt(22, 259, "P5 turns " + "°, ".join(f"{t:.0f}" for t in leg_turns()) + "°. Leg band seam in the middle of the inner face.", 1.8, fill="#555")
    rows = [[("DATA", "بيانات"), ""],
            [("Overall W x D x H (given)", "العرض × العمق × الارتفاع (معطى)"), f"{L:.0f} x {D:.0f} x {HT:.0f}"],
            [("Box height / leg height (est.)", "ارتفاع الصندوق / الرجل (تقدير)"), f"{BOXH:.0f} / {LEGH:.0f}"],
            [("Leg block (est., 2 mirrored)", "كتلة الرجل (تقدير، ٢ متناظرتان)"), f"{LW:.0f} x {LY1 - LY0:.0f}, V end"],
            [("Leg set in from the table points", "بعد الرجل عن رأس الطاولة"), f"{INS:.0f}"],
            [("Leg front behind the table front", "الرجل خلف حافة الطاولة الأمامية"), f"{LY0:.0f}"],
            [("Sheet thickness (proposed)", "سماكة الصاج (مقترحة)"), f"{T:.0f}"]]
    b += H.table(290, 60, [60, 52], rows, 6.2, 1.9)
    sheets.append(("parts", sheet(2, 4, "Parts: flat patterns", "القطع: الأشكال المسطحة", "1:10", b, logo)))

    # ---- sheet 3: assembly and cutting
    b = ""
    b += H.bi(20, 34, "EXPLODED VIEW  1:12", "منظور مفكوك", 2.8, bold=True)
    b += draw_iso(70, 112, 0.07, lift=200.0)
    b += H.bi(215, 34, "PROPOSED SEQUENCE (Production decides)", "تسلسل مقترح (القرار للإنتاج)", 2.8, bold=True)
    steps = [("Laser cut P1 to P6 from 3 mm sheet. Fold P3 and P4 (1 fold each) and P5 (5 folds) at the blue lines.", "قص الليزر للقطع من ل١ إلى ل٦ من صاج ٣ مم. ثني ل٣ ول٤ (ثنية لكل منهما) ول٥ (٥ ثنيات) عند الخطوط الزرقاء."),
             ("Weld each leg: the band closes at its seam, then its cap plate on top. The two legs are mirror images.", "لحام كل رجل: يُقفل الشريط عند وصلته ثم غطاؤه العلوي. الرجلان متناظرتان."),
             ("Build the box: bottom plate, the 2 side bands and 2 end bands round it, then the top plate.", "تجميع الصندوق: اللوح السفلي، الشريطان الجانبيان والشريطان الطرفيان حوله، ثم اللوح العلوي."),
             ("Fix each leg under its end, 50 in from the point, its V faces parallel to the table's V faces (dashed outlines on the plan).", "تثبيت كل رجل أسفل الطرف على بعد ٥٠ من الرأس بحيث تتوازى أوجه V مع أوجه V للطاولة (الخطوط المتقطعة)."),
             ("Dress the seams, then finish. Glides if wanted.", "تنعيم الوصلات ثم التشطيب. قواعد أرضية إن لزم.")]
    for i, (en, ar) in enumerate(steps):
        yy = 44 + i * 17
        b += H.txt(215, yy, f"{i + 1}.", 2.4, bold=True) + H.bi(221, yy, en, ar, 2.1)
    ns = 1 / 20; ny = 162
    b += H.bi(20, 148, "CUTTING LAYOUT  1:20  (two assumed sheets, 1250 x 2500 x 3)", "توزيع القص (لوحان مفترضان ١٢٥٠ × ٢٥٠٠ × ٣)", 2.6, bold=True)
    for sh, nx in ((1, 20), (2, 160)):
        b += H.txt(nx, ny - 2, f"SHEET {sh} / لوح {sh}", 2.0, bold=True)
        b += f'<rect x="{nx}" y="{ny}" width="{2500 * ns:.2f}" height="{1250 * ns:.2f}" fill="#fafafa" stroke="{INK}" stroke-width="0.3"/>'
        for key, name, qty, kind, data in parts():
            for (sn, x, y, vert) in nl[key]:
                if sn != sh: continue
                pts = part_pts(kind, data, x, y, vert)
                d = "M" + " L".join(f"{nx + px_ * ns:.2f},{ny + (1250 - py_) * ns:.2f}" for px_, py_ in pts) + " Z"
                b += f'<path d="{d}" fill="#e6e2d8" stroke="{INK}" stroke-width="0.3"/>'
                cxm = sum(p[0] for p in pts) / len(pts); cym = sum(p[1] for p in pts) / len(pts)
                b += H.txt(nx + cxm * ns, ny + (1250 - cym) * ns + 1, key.split("_")[0], 2.0, "middle", fill="#333")
        b += H.hdim(nx, nx + 2500 * ns, ny + 1250 * ns + 6, "2500", size=1.8)
    b += H.txt(20, 242, f"Total cutting length {cl['total'] / 1000:.1f} m on two assumed sheets. Part spacing 30 mm, edge margin 10 mm (assumed).", 2.3, bold=True)
    b += H.txt(20, 248, "Sheet 2 is about half empty and sheet 1 has room: a larger sheet (for example 1500 x 3000) may do it on one. Sheet size and nesting are Production's.", 2.0, fill="#555")
    sheets.append(("assembly-cutting", sheet(3, 4, "Assembly and cutting layout", "التركيب وتوزيع القص", "1:12 / 1:20", b, logo)))

    # ---- sheet 4: BOM and notes
    b = ""
    b += H.bi(20, 34, "BILL OF MATERIALS", "قائمة المكونات", 2.8, bold=True)
    def row(k, en, ar, qty, proc_en, proc_ar, size, fin_en, fin_ar):
        return [k, (en, ar), str(qty), (proc_en, proc_ar), size, (fin_en, fin_ar)]
    lsz = f"{LW:.0f} x {LY1 - LY0:.0f}, V end"
    rows = [[("Item", "بند"), ("Part", "الجزء"), ("Qty", "العدد"), ("Material / process", "الخامة / الطريقة"), ("Size", "المقاس"), ("Finish (to confirm)", "التشطيب (للتأكيد)")],
            row("P1", "Top plate", "لوح علوي", 1, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", f"{L:.0f} x {D:.0f}", "Satin taupe", "ساتان بني رمادي"),
            row("P2", "Bottom plate", "لوح سفلي", 1, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", f"{L:.0f} x {D:.0f}", "-", "-"),
            row("P3", "Side band (front, back)", "شريط جانبي (أمامي، خلفي)", 2, "Steel sheet 3, cut, folded once", "صاج ٣ مم، قص وثني مرة", f"{FRONT_BAND:.1f} x {BOXH:.0f}", "Satin taupe", "ساتان بني رمادي"),
            row("P4", "End band", "شريط طرفي", 2, "Steel sheet 3, cut, folded once", "صاج ٣ مم، قص وثني مرة", f"{END_BAND:.1f} x {BOXH:.0f}", "Satin taupe", "ساتان بني رمادي"),
            row("P5", "Leg band", "شريط الرجل", 2, "Steel sheet 3, cut, folded 5 times", "صاج ٣ مم، قص وثني ٥ مرات", f"{LEG_BAND:.0f} x {LEGH:.0f}", "Satin taupe", "ساتان بني رمادي"),
            row("P6", "Leg cap plate", "غطاء الرجل", 2, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", lsz, "Satin taupe", "ساتان بني رمادي"),
            row("G", "Floor glides", "قواعد أرضية", "-", "Barely visible in the photos. Production to propose", "بالكاد ظاهرة في الصور. يقترحها الإنتاج", "to follow", "-", "-")]
    b += H.table(20, 40, [10, 40, 12, 100, 52, 48], rows, 7.4, 2.0)
    notes = [
        ("Overall 1200 W x 450 D x 750 H (120 x 45 x 75 cm) are Sabry's sizes (11 Nov 2026). Everything else is estimated from four photos.", "المقاسات الكلية ١٢٠٠ × ٤٥٠ × ٧٥٠ (١٢٠ × ٤٥ × ٧٥ سم) من صبري (١١ نوفمبر ٢٠٢٦). الباقي تقدير من أربع صور."),
        ("Rev 2 draft, not approved. Legs widened from 280 to 340 across (Sabry, front photo, rev 1 superseded). Same design language as OBJ-020.", "المراجعة ٢ مسودة غير معتمدة. عرض الرجل زاد من ٢٨٠ إلى ٣٤٠ (صبري، الصورة الأمامية؛ المراجعة ١ أُلغيت). نفس لغة التصميم لـ OBJ-020."),
        ("Reference: library item OBJ-181, photos 1 to 4 (third party, not our piece). Drawn exact to the reference by Sabry's standing rule.", "المرجع: عنصر المكتبة OBJ-181، الصور ١ إلى ٤ (طرف ثالث). مرسوم مطابقاً للمرجع حسب قاعدة صبري."),
        (f"Top outline: 8 sides. Crease {CR:.0f} deep in the middle of the front and back faces (back assumed like the front), and a V point at each end, corners {VA:.0f} in.", f"شكل السطح: ٨ أضلاع. ثنية بعمق {ar_num(f'{CR:.0f}')} في منتصف الأمامي والخلفي (الخلفي مفترض كالأمامي) وطرف V عند كل نهاية، الزوايا {ar_num(f'{VA:.0f}')} للداخل."),
        (f"Box height {BOXH:.0f} and leg height {LEGH:.0f} are estimates. Each leg: {LW:.0f} wide, {LY1 - LY0:.0f} deep, V end stepped {INS:.0f} inside the table's V, front {LY0:.0f} behind the table front, flat inner end; mirrored (estimate).", f"ارتفاع الصندوق {ar_num(f'{BOXH:.0f}')} والرجل {ar_num(f'{LEGH:.0f}')} تقديريان. الرجل: عرض {ar_num(f'{LW:.0f}')}، عمق {ar_num(f'{LY1 - LY0:.0f}')}، طرف V مزاح {ar_num(f'{INS:.0f}')} داخل V الطاولة، والواجهة خلف حافة الطاولة {ar_num(f'{LY0:.0f}')}؛ متناظرتان (تقدير)."),
        ("Build proposed in 3 mm sheet: hollow box and hollow legs, crisp corners as in the photos. The photos could also be a moulded or lacquered piece: Production decides the process.", "التنفيذ المقترح من صاج ٣ مم: صندوق ورجلان مجوفان بزوايا حادة. قد تكون القطعة مصبوبة أو مطلية: الإنتاج يقرر الطريقة."),
        ("Finish as the photos: smooth satin taupe-brown all over (one photo shows a champagne brushed metal). Material and method are Production's. Hex is a screen guess.", "التشطيب كما في الصور: ساتان بني رمادي ناعم (صورة واحدة بمعدن شامبانيا مصنفر). الخامة والطريقة للإنتاج. الرمز تقدير من الشاشة."),
        ("Leg underside is left open on the drawing. Closing it, bracing and weight are Production's. No structural claim is made.", "أسفل الرجل مفتوح في الرسم. التقفيل والتدعيم والوزن للإنتاج. لا توجد ادعاءات إنشائية."),
        ("We propose; Production decides sheet size and thickness, tolerances, joints, glides and finish. No costs or prices are on this drawing.", "نحن نقترح، والإنتاج يحدد مقاس الصاج وسماكته والتفاوتات والوصلات والقواعد والتشطيب. لا أسعار هنا."),
        ("Arabic wording is a draft and needs a technical reader before it goes to the factory.", "الصياغة العربية مسودة وتحتاج مراجعة فنية قبل الإرسال للمصنع."),
    ]
    b += H.bi(20, 122, "NOTES", "ملاحظات", 2.8, bold=True)
    for i, (en, ar) in enumerate(notes):
        yy = 131 + i * 10.0
        b += H.txt(20, yy, f"{i + 1}.", 2.1, bold=True) + H.txt(27, yy, en, 2.1)
        b += H.txt(409, yy + 4.2, ar, 2.1, "start", False, "#444", ar=True)
    sheets.append(("bom-notes", sheet(4, 4, "Bill of materials and notes", "قائمة المكونات والملاحظات", "-", b, logo)))
    return sheets


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = "data:image/svg+xml;base64," + base64.b64encode(open(os.path.join(ROOT, "brand", "objekt-logo.svg"), "rb").read()).decode()
    ref = H.img_uri(os.path.join(ROOT, "images", "OBJ-181.jpg"), 800)
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
    print("edges", [round(e, 1) for e in BOX_E], "side band", round(FRONT_BAND, 1), "end band", round(END_BAND, 1), "leg band", round(LEG_BAND, 1))
    print({k: round(v, 1) for k, v in cl.items()})


if __name__ == "__main__":
    main()
