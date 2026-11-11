"""OBJ-003 coffee table, rev 4: drawing set (A3, EN/AR) + DXF, 1000 mm wide, 380 mm high, round discs.

Rev 2: discs are untrimmed egg shapes (ellipses, no flat foot), taller table.
Rev 3: Sabry set 380 mm overall height and 320 mm disc width (11 Nov 2026).
Rev 4: table 1000 mm wide, discs are full circles (no egg shape, no flat foot): disc diameter = overall height.
Overall height can be overridden with OBJ003_H (mm).

Source numbers: Sabry's model ratios (workspace record, 2 Nov 2026): top diameter 130.06,
top height 40.00, disc total height 46.39 (cap 6.40 above the top). The cap is scaled so the top is 1000 mm.
Everything else (top thickness, disc width and shape, disc position and orientation) is an
ESTIMATE from the reference photo and is labelled as such on the sheets.

Run: python3 make_obj003_rev4.py     Needs: numpy ezdxf pymupdf pillow, node + playwright.
Output: venture/drawings/OBJ-003/
"""
import base64, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_obj177_rev1 as H          # drawing helpers only (txt, bi, line, hdim, vdim, table, ...)

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "venture", "drawings", "OBJ-003")
PID, REV, DATE = "OBJ-003", "4", "11 Nov 2026"
PRE = f"{PID}_rev{REV}_"
STAMP_EN, STAMP_AR = H.STAMP_EN, H.STAMP_AR
INK = H.INK

# ---------------------------------------------------------------- geometry (mm)
K = 1000.0 / 130.06                       # model units to mm
DIA = 1000.0
H_DISC = float(os.environ.get("OBJ003_H", "380"))   # overall height incl. caps (Sabry, 11 Nov 2026)
CAP = 6.40 * K                           # cap above the top, kept from Sabry's model ratio   39.4
TOP_Z = H_DISC - CAP                     # top surface above floor
T = 3.0                                  # plate thickness (proposed, Production decides)
Z_UNDER = TOP_Z - T
W_DISC = H_DISC                          # full circle: the disc is as wide as it is tall (Sabry: no egg shape)
A_E = W_DISC / 2                         # half width
B_E = H_DISC / 2                         # half height (= A_E, a circle)
ZC = B_E                                 # centre height; the bottom touches the floor at one point
RHO = 295.0                              # ESTIMATE: disc centre radius from table centre (outer edge 15 mm inside the rim)
ANG = [90.0, 210.0, 330.0]               # discs at 120 deg
def ar_num(txt):
    return str(txt).translate(str.maketrans('0123456789.', '٠١٢٣٤٥٦٧٨٩٫'))


def chord(z):
    """Disc width at height z (circle)."""
    return 2 * A_E * math.sqrt(max(0.0, 1 - ((z - ZC) / B_E) ** 2))


SLOT_L = chord(Z_UNDER)                  # slot length = disc width at the underside of the top
CAP_W = chord(TOP_Z)                     # cap width at the top surface


def disc_profile(n=160):
    """(s, z): s across the disc width from its centre line, z up from the floor. Closed circle, bottom at z=0."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        pts.append((A_E * math.sin(t), ZC - B_E * math.cos(t)))
    return pts


def disc3d(theta_deg, prof=None):
    th = math.radians(theta_deg); c, s_ = math.cos(th), math.sin(th)
    prof = prof or disc_profile()
    return [((RHO + s) * c, (RHO + s) * s_, z) for s, z in prof]


def clip_z(poly, zc, keep_below):
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        ia = a[2] <= zc if keep_below else a[2] >= zc
        ib = b[2] <= zc if keep_below else b[2] >= zc
        if ia:
            out.append(a)
        if ia != ib:
            t = (zc - a[2]) / (b[2] - a[2])
            out.append(tuple(a[k] + t * (b[k] - a[k]) for k in range(3)))
    return out


# ---------------------------------------------------------------- projections
def view_front(p):  return (p[0], p[2], p[1])            # u, up, depth (bigger = farther)
def view_side(p):   return (p[1], p[2], -p[0])           # seen from +x


def view_iso(p, az=35.0, el=28.0):
    a, e = math.radians(az), math.radians(el)
    x = p[0] * math.cos(a) - p[1] * math.sin(a)
    y = p[0] * math.sin(a) + p[1] * math.cos(a)
    return (x, p[2] * math.cos(e) + y * math.sin(e), y * math.cos(e) - p[2] * math.sin(e))


def poly_svg(pts2, ox, oy, s, fill="#e4e4e4", stroke=INK, w=0.3, dash=None):
    d = "M" + " L".join(f"{ox + u * s:.2f},{oy - v * s:.2f}" for u, v in pts2) + " Z"
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"{da}/>'


def plate_poly(z, n=96, r=DIA / 2):
    return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), z) for i in range(n)]


def draw_elevation(view, ox, oy, s):
    """Elevation, painter order by depth. oy = floor line on the sheet."""
    items = []
    for th in ANG:
        full = disc3d(th)
        cx = np.mean([view(p)[0] for p in full]); dep = np.mean([view(p)[2] for p in full])
        items.append((dep, "disc", full))
    items.sort(key=lambda t: -t[0])
    svg = ""
    for _, _, poly in items:
        svg += poly_svg([view(p)[:2] for p in poly], ox, oy, s, fill="#ececec")
    us = [view(p)[0] for p in plate_poly(TOP_Z)]
    u0, u1 = min(us), max(us)
    svg += poly_svg([(u0, Z_UNDER), (u1, Z_UNDER), (u1, TOP_Z), (u0, TOP_Z)], ox, oy, s, fill="#cfcfcf")
    return svg


def draw_iso(ox, oy, s, lift=0.0):
    """lift = 0: assembled (discs clipped at the underside of the top, caps over the top).
    lift > 0: exploded, discs stay where they are and the top plate is lifted and drawn last."""
    def pr(p): return view_iso(p)
    svg = ""
    if lift > 0:
        discs = [disc3d(th) for th in ANG]
        discs.sort(key=lambda p: -np.mean([pr(q)[2] for q in p]))
        for poly in discs:
            svg += poly_svg([pr(q)[:2] for q in poly], ox, oy, s, fill="#d9d9d9")
        caps = []
    else:
        lows, caps = [], []
        for th in ANG:
            full = disc3d(th)
            lows.append(clip_z(full, Z_UNDER, True)); caps.append(clip_z(full, Z_UNDER, False))
        lows.sort(key=lambda p: -np.mean([pr(q)[2] for q in p]))
        for poly in lows:
            svg += poly_svg([pr(q)[:2] for q in poly], ox, oy, s, fill="#d9d9d9")
    top = plate_poly(TOP_Z + lift); bot = plate_poly(Z_UNDER + lift)
    svg += poly_svg([pr(q)[:2] for q in bot], ox, oy, s, fill="#bdbdbd", w=0.25)
    for i in range(len(top)):
        j = (i + 1) % len(top)
        if pr(top[i])[2] < 0 or pr(top[j])[2] < 0:
            quad = [pr(top[i])[:2], pr(top[j])[:2], pr(bot[j])[:2], pr(bot[i])[:2]]
            svg += poly_svg(quad, ox, oy, s, fill="#bdbdbd", stroke="#bdbdbd", w=0.15)
    svg += poly_svg([pr(q)[:2] for q in top], ox, oy, s, fill="#f2f2f2")
    for c in caps:
        svg += poly_svg([pr(q)[:2] for q in c], ox, oy, s, fill="#e2e2e2")
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
             ("MATERIAL / الخامة", "Steel sheet 3 mm, laser cut (proposed)", 0, 12.3, 75),
             ("DATE / التاريخ", DATE, 75, 12.3, 25), ("SHEET / لوحة", f"{n} / {total}", 100, 12.3, 25), ("REV / مراجعة", REV, 125, 12.3, 25),
             ("FINISH / التشطيب", "Powder coat · matte, colour to be confirmed", 0, 24.6, 100),
             ("DRAWN / رسم", "objekt", 100, 24.6, 50)]
    for lab, val, cx, cy, cw in cells:
        s += f'<rect x="{bx + cx}" y="{by + cy}" width="{cw}" height="12.3" fill="none" stroke="{INK}" stroke-width="0.15"/>'
        s += H.txt(bx + cx + 1.3, by + cy + 3.6, lab, 1.9, fill="#666") + H.txt(bx + cx + 1.3, by + cy + 9.2, val, 2.5 if len(val) < 30 else 2.05, bold=True)
    return s + "</svg>"


# ---------------------------------------------------------------- DXF
def write_dxf():
    import ezdxf
    def new():
        d = ezdxf.new("R2010"); d.units = 4; d.layers.add("CUT", color=7); d.layers.add("NOTE", color=8); return d
    def top_into(msp, cx, cy):
        msp.add_circle((cx, cy), DIA / 2, dxfattribs={"layer": "CUT"})
        for th in ANG:
            t = math.radians(th); c, s_ = math.cos(t), math.sin(t)
            hl, hw = SLOT_L / 2, T / 2
            pts = [(-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw)]
            P = [(cx + RHO * c + u * c - v * s_, cy + RHO * s_ + u * s_ + v * c) for u, v in pts]
            msp.add_lwpolyline(P, close=True, dxfattribs={"layer": "CUT"})
    def disc_into(msp, x0, y0):
        """round disc with its lowest point on y0, centre at x0 + A_E."""
        msp.add_circle((x0 + A_E, y0 + B_E), A_E, dxfattribs={"layer": "CUT"})
    files = []
    d = new(); top_into(d.modelspace(), 0, 0); p = os.path.join(OUT, PRE + "top.dxf"); d.saveas(p); files.append(p)
    d = new(); disc_into(d.modelspace(), 0, 0); p = os.path.join(OUT, PRE + "disc_x3.dxf"); d.saveas(p); files.append(p)
    d = new(); m = d.modelspace(); d.layers.add("SHEET", color=1)
    m.add_lwpolyline([(0, 0), (2500, 0), (2500, 1250), (0, 1250)], close=True, dxfattribs={"layer": "SHEET"})
    top_into(m, 510, 510)
    for i in range(3):
        disc_into(m, 1040 + i * (W_DISC + 30), 20)
    p = os.path.join(OUT, PRE + "nest_1250x2500.dxf"); d.saveas(p); files.append(p)
    return files


def ellipse_perimeter(a, b):
    h = ((a - b) / (a + b)) ** 2
    return math.pi * (a + b) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))


def cut_lengths():
    top = math.pi * DIA + 3 * 2 * (SLOT_L + T)
    disc = ellipse_perimeter(A_E, B_E)
    return top, disc, top + 3 * disc


# ---------------------------------------------------------------- sheets
def build(logo, ref):
    sheets = []
    topL, discL, totL = cut_lengths()
    s = 1 / 8
    h = 80 * 5 / 6 * 0 + DIA / 2 * s          # plate radius on the sheet
    # ---- sheet 1
    b = ""
    b += H.bi(20, 34, "FRONT ELEVATION  1:8", "المسقط الأمامي", 2.8, bold=True)
    ox, oy = 95, 104
    b += draw_elevation(view_front, ox, oy, s)
    b += H.hdim(ox - h, ox + h, oy + 8, f"{DIA:.0f}")
    b += H.vdim(ox + h + 6, oy - H_DISC * s, oy, f"{H_DISC:.0f}")
    b += H.vdim(ox - h - 6, oy - TOP_Z * s, oy, f"{TOP_Z:.0f}", side=-1)
    b += H.txt(ox + h + 9, oy - H_DISC * s + 1.5, f"cap {CAP:.0f}", 2.0)
    b += H.balloon(ox + h + 36, oy - TOP_Z * s + 12, "1", ox + h - 8, oy - TOP_Z * s)
    b += H.balloon(ox + h + 36, oy - 8, "2", ox + 46, oy - 8)
    b += H.bi(20, 126, "PLAN  1:8", "المسقط الأفقي", 2.8, bold=True)
    px, py = 95, 188
    b += f'<circle cx="{px}" cy="{py}" r="{h:.2f}" fill="#f2f2f2" stroke="{INK}" stroke-width="0.3"/>'
    for th in ANG:
        poly = [(x, y) for x, y, z in disc3d(th)]
        b += H.poly_path([np.array(poly)], px, py, s, fill="none", stroke="#888", w=0.2)
        t = math.radians(th)
        b += f'<g transform="translate({px + RHO * math.cos(t) * s:.2f},{py - RHO * math.sin(t) * s:.2f}) rotate({-th:.1f})"><rect x="{-SLOT_L / 2 * s:.2f}" y="-1.0" width="{SLOT_L * s:.2f}" height="2.0" fill="#d9d9d9" stroke="{INK}" stroke-width="0.25"/></g>'
    b += H.line(px - h - 4, py, px + h + 4, py, 0.1, "#888", "4 1 1 1") + H.line(px, py - h - 4, px, py + h + 4, 0.1, "#888", "4 1 1 1")
    b += H.hdim(px - h, px + h, py + h + 8, f"Ø{DIA:.0f}")
    b += H.txt(px + 30, py + h - 4, "discs stand on the slot lines", 2.0, fill="#555")
    b += H.bi(205, 34, "SIDE ELEVATION  1:8", "المسقط الجانبي", 2.8, bold=True)
    sx = 270
    b += draw_elevation(view_side, sx, oy, s)
    b += H.hdim(sx - h, sx + h, oy + 8, f"{DIA:.0f}")
    b += H.bi(205, 126, "VIEW", "منظور", 2.8, bold=True)
    b += draw_iso(262, 188, 0.105)
    b += H.bi(340, 126, "REFERENCE (photo, third party)", "المرجع (صورة من طرف ثالث)", 2.1, bold=True)
    b += H.image(340, 133, 68, 57, ref, True) + H.txt(340, 194, "Reference only. Not our piece.", 1.9, fill="#555")
    rows = [[("Colour", "اللون"), "", ("Hex", "الرمز"), ("Source", "المصدر")],
            ["Bone", ("swatch", "#E9E4D8"), "#E9E4D8", ("Book colour", "لون الكتاب")],
            ["Clay", ("swatch", "#A8553A"), "#A8553A", ("Book colour", "لون الكتاب")],
            ["Carbon", ("swatch", "#222222"), "#222222", ("Book colour", "لون الكتاب")],
            ["Oxblood", ("swatch", "#5A1F25"), "#5A1F25", ("In the renders. To confirm", "في التصاميم. للتأكيد")]]
    b += H.bi(205, 204, "COLOURWAYS", "الألوان", 2.6, bold=True)
    b += H.table(205, 211, [22, 10, 24, 52], rows, 5.2, 2.0)
    b += H.txt(205, 241, "Powder coat, matte, to be confirmed. Hex is a screen", 1.9, fill="#555")
    b += H.txt(205, 244.5, "approximation. CAPCI code to follow.", 1.9, fill="#555")
    b += H.bi(20, 276, "1 Top plate   2 Disc (3 off)", "١ لوح السطح   ٢ قرص (٣ قطع)", 2.4)
    b += H.bi(110, 276, "Width 1000 and overall height 380 are Sabry's sizes. Discs are full circles.", "العرض ١٠٠٠ والارتفاع الكلي ٣٨٠ بطلب صبري. الأقراص دوائر كاملة.", 2.2)
    sheets.append(("views", sheet(1, 4, "Views and overall sizes, 1000 wide", "المساقط والمقاسات، عرض ١٠٠٠", "1:8", b, logo)))
    s = 1 / 7
    rt = DIA / 2 * s

    # ---- sheet 2: parts
    b = ""
    b += H.bi(20, 34, "TOP PLATE  1:7", "لوح السطح", 2.8, bold=True)
    tx, ty = 100, 120
    b += f'<circle cx="{tx}" cy="{ty}" r="{DIA / 2 * s}" fill="#f6f6f6" stroke="{INK}" stroke-width="0.4"/>'
    for th in ANG:
        t = math.radians(th)
        cxs, cys = tx + RHO * math.cos(t) * s, ty - RHO * math.sin(t) * s
        b += f'<g transform="translate({cxs:.2f},{cys:.2f}) rotate({-th:.1f})"><rect x="{-SLOT_L / 2 * s:.2f}" y="-0.8" width="{SLOT_L * s:.2f}" height="1.6" fill="#fff" stroke="{INK}" stroke-width="0.3"/></g>'
        b += H.line(tx, ty, tx + (rt + 4) * math.cos(t), ty - (rt + 4) * math.sin(t), 0.1, "#888", "4 1 1 1")
    b += H.hdim(tx - rt, tx + rt, ty + rt + 8, f"Ø{DIA:.0f}")
    b += H.txt(tx + 6, ty - 18, "120°", 2.2) + H.txt(tx - 5, ty + 28, "120°", 2.2)
    b += H.txt(tx + 4, ty - 4, f"ρ {RHO:.0f} est.", 2.1, fill="#555")
    b += H.bi(20, 222, "3 slots, each", "٣ فتحات، كل منها", 2.4, bold=True)
    b += H.txt(20, 233, f"{SLOT_L:.1f} long x {T:.1f} wide, centred at radius {RHO:.0f} on the", 2.3)
    b += H.txt(20, 238.5, "radial line (est.). Length = disc width at the underside of the top.", 2.3)
    b += H.txt(20, 244, "Clearance for the weld or fit is Production's.", 2.3)
    b += H.bi(205, 34, "DISC  1:2.5   (3 off)", "القرص (٣ قطع)", 2.8, bold=True)
    s2 = 0.4
    dx0, dy0 = 305, 208                      # foot line on the sheet, disc centre x
    prof = disc_profile()
    d = "M" + " L".join(f"{dx0 + sv * s2:.2f},{dy0 - z * s2:.2f}" for sv, z in prof) + " Z"
    b += f'<path d="{d}" fill="#ececec" stroke="{INK}" stroke-width="0.4"/>'
    b += H.line(dx0 - 85, dy0 - Z_UNDER * s2, dx0 + 85, dy0 - Z_UNDER * s2, 0.12, "#b3261e", "4 1.5")
    b += H.line(dx0 - 85, dy0 - TOP_Z * s2, dx0 + 85, dy0 - TOP_Z * s2, 0.12, "#b3261e", "4 1.5")
    b += H.txt(dx0 + 87, dy0 - TOP_Z * s2 - 0.6, f"top {TOP_Z:.0f}", 1.9, fill="#b3261e")
    b += H.txt(dx0 + 87, dy0 - Z_UNDER * s2 + 3.2, f"under {Z_UNDER:.0f}", 1.9, fill="#b3261e")
    b += H.hdim(dx0 - A_E * s2, dx0 + A_E * s2, dy0 + 8, f"Ø{W_DISC:.0f}")
    b += H.vdim(dx0 - A_E * s2 - 6, dy0 - H_DISC * s2, dy0, f"{H_DISC:.1f}", side=-1)
    b += H.hdim(dx0 - SLOT_L / 2 * s2, dx0 + SLOT_L / 2 * s2, dy0 - Z_UNDER * s2 - 8, f"{SLOT_L:.1f}", size=2.1)
    b += H.hdim(dx0 - CAP_W / 2 * s2, dx0 + CAP_W / 2 * s2, dy0 - H_DISC * s2 - 8, f"cap {CAP_W:.0f}", size=2.1)
    b += H.vdim(dx0 + A_E * s2 + 6, dy0 - H_DISC * s2, dy0 - TOP_Z * s2, f"{CAP:.1f}", size=2.1)
    b += H.bi(262, 226, "A full circle, no flat foot. The disc seats in its slot where", "دائرة كاملة بلا قاعدة مسطحة. يستقر القرص في فتحته حيث يساوي عرضه الفتحة.", 2.0)
    b += H.txt(262, 232, "it is as wide as the slot, so the top rests on the disc.", 2.0)
    rows = [[("DATA", "بيانات"), ""],
            [("Top Ø / height of top surface", "قطر السطح / ارتفاعه"), f"{DIA:.0f} / {TOP_Z:.1f}"],
            [("Disc height (total) / cap above top", "ارتفاع القرص / البارز"), f"{H_DISC:.1f} / {CAP:.1f}"],
            [("Plate thickness (proposed)", "سماكة اللوح (مقترحة)"), f"{T:.0f}"],
            [("Cut length: top / disc", "طول القص: سطح / قرص"), f"{topL / 1000:.2f} m / {discL / 1000:.2f} m"],
            [("Overall height (Sabry)", "الارتفاع الكلي (صبري)"), f"{H_DISC:.0f}"]]
    b += H.table(124, 218, [64, 36], rows, 5.6, 2.0)
    sheets.append(("parts", sheet(2, 4, "Parts: top plate and disc", "القطع: لوح السطح والقرص", "1:7 / 1:2.5", b, logo)))

    # ---- sheet 3: assembly and cutting
    b = ""
    b += H.bi(20, 34, "EXPLODED VIEW  1:10", "منظور مفكوك", 2.8, bold=True)
    b += draw_iso(110, 142, 0.1, lift=320.0)
    for th in ANG:
        t = math.radians(th); p0 = (RHO * math.cos(t), RHO * math.sin(t), Z_UNDER)
        a = view_iso((p0[0], p0[1], H_DISC + 4)); b_ = view_iso((p0[0], p0[1], Z_UNDER + 320))
        b += H.line(110 + a[0] * 0.1, 142 - a[1] * 0.1, 110 + b_[0] * 0.1, 142 - b_[1] * 0.1, 0.12, "#555", "2 1.5")
    b += H.bi(215, 34, "PROPOSED SEQUENCE (Production decides)", "تسلسل مقترح (القرار للإنتاج)", 2.8, bold=True)
    steps = [("Laser cut the top plate with 3 slots, and 3 discs.", "قص الليزر للوح السطح بثلاث فتحات وثلاثة أقراص."),
             ("Clean edges. Check each disc against its slot.", "تنظيف الحواف. مطابقة كل قرص مع فتحته."),
             ("Lay the top upside down. Pass each disc up through its slot from below until it seats.", "قلب اللوح. تمرير كل قرص من أسفل حتى يستقر."),
             (f"Set the 120° spacing and the cap height {CAP:.1f}. Fix (weld or other: Production's).", f"ضبط ١٢٠° وارتفاع البارز {ar_num(f'{CAP:.1f}')} ثم التثبيت (اللحام أو غيره: للإنتاج)."),
             ("Finish the joints, then powder coat, matte. Fit floor glides if wanted.", "تشطيب الوصلات ثم دهان بودرة مطفي. إضافة قواعد أرضية إن لزم.")]
    for i, (en, ar) in enumerate(steps):
        yy = 44 + i * 13.5
        b += H.txt(215, yy, f"{i + 1}.", 2.4, bold=True) + H.bi(221, yy, en, ar, 2.2)
    b += H.bi(20, 166, "CUTTING LAYOUT  1:14  (assumed sheet 1250 x 2500 x 3)", "توزيع القص (لوح مفترض ١٢٥٠ × ٢٥٠٠ × ٣)", 2.8, bold=True)
    ns = 1 / 14; nx, ny = 22, 176
    b += f'<rect x="{nx}" y="{ny}" width="{2500 * ns}" height="{1250 * ns}" fill="#fafafa" stroke="{INK}" stroke-width="0.3"/>'
    b += f'<circle cx="{nx + 510 * ns}" cy="{ny + 1250 * ns - 510 * ns}" r="{DIA / 2 * ns}" fill="#e6e6e6" stroke="{INK}" stroke-width="0.3"/>'
    for i in range(3):
        x0 = 1040 + i * (W_DISC + 30)
        pr = disc_profile()
        d = "M" + " L".join(f"{nx + (x0 + A_E + sv) * ns:.2f},{ny + 1250 * ns - (20 + z) * ns:.2f}" for sv, z in pr) + " Z"
        b += f'<path d="{d}" fill="#e6e6e6" stroke="{INK}" stroke-width="0.3"/>'
    b += H.hdim(nx, nx + 2500 * ns, ny + 1250 * ns + 6, "2500", size=2.1)
    b += H.vdim(nx + 2500 * ns + 4, ny, ny + 1250 * ns, "1250", size=2.1)
    b += H.txt(nx + 1100 * ns, ny + 1250 * ns - 900 * ns, f"Total cutting length {totL / 1000:.2f} m", 2.4, bold=True)
    b += H.txt(nx + 1100 * ns, ny + 1250 * ns - 900 * ns + 5, f"Part spacing 30 mm, edge margin 10 mm (assumed).", 2.0, fill="#555")
    sheets.append(("assembly-cutting", sheet(3, 4, "Assembly and cutting layout", "التركيب وتوزيع القص", "1:10 / 1:14", b, logo)))

    # ---- sheet 4: BOM and notes
    b = ""
    b += H.bi(20, 34, "BILL OF MATERIALS", "قائمة المكونات", 2.8, bold=True)
    rows = [[("Item", "بند"), ("Part", "الجزء"), ("Qty", "العدد"), ("Material / process", "الخامة / الطريقة"), ("Size", "المقاس"), ("Finish", "التشطيب")],
            ["1", ("Top plate", "لوح السطح"), "1", ("Steel sheet 3, laser cut, 3 slots (proposed)", "صاج ٣ مم قص ليزر، ٣ فتحات (مقترح)"), f"Ø{DIA:.0f} x {T:.0f}", ("Powder coat, matte, to confirm", "بودرة مطفي، للتأكيد")],
            ["2", ("Disc", "قرص"), "3", ("Steel sheet 3, laser cut (proposed)", "صاج ٣ مم قص ليزر (مقترح)"), f"Ø{H_DISC:.0f} x {T:.0f}", ("Powder coat, matte, to confirm", "بودرة مطفي، للتأكيد")],
            ["3", ("Floor glides", "قواعد أرضية"), "3", ("Not in the reference. Production to propose", "ليست في المرجع. يقترحها الإنتاج"), "to follow", "-"]]
    b += H.table(20, 40, [12, 40, 14, 120, 68, 132], rows, 8.6, 2.2)
    notes = [
        ("Overall width 1000 (1 m) and overall height 380 are Sabry's sizes (11 Nov 2026). The earlier book size (Ø900 x 380) is replaced.", "العرض الكلي ١٠٠٠ (متر) والارتفاع الكلي ٣٨٠ بطلب صبري (١١ نوفمبر ٢٠٢٦). يحل محل مقاس الكتاب السابق."),
        (f"The cap above the top is {CAP:.1f}, from Sabry's model ratio (6.40 on a top of 130.06, scaled to 1000). The discs are full circles, so the disc diameter equals the overall height ({H_DISC:.0f}). A 320 disc width was asked for earlier and dropped.", f"البارز فوق السطح {ar_num(f'{CAP:.1f}')} من نسبة نموذج صبري. الأقراص دوائر كاملة فقطرها يساوي الارتفاع الكلي ({ar_num(f'{H_DISC:.0f}')}). عرض ٣٢٠ المطلوب سابقاً أُلغي."),
        (f"ESTIMATED from the reference photo: disc position (radius {RHO:.0f}), disc direction (radial) and top thickness.", "تقديرية من صورة المرجع: موضع القرص واتجاهه (شعاعي) وسماكة السطح."),
        ("Sabry's own cut sheet and model were not available for this revision. Replace the estimates when they are.", "لم يتوفر ملف القص ونموذج صبري لهذه المراجعة. تُستبدل التقديرات عند توفره."),
        ("The photo shows half-disc caps; Sabry's model has full discs passing through slots. This drawing follows his model.", "الصورة تُظهر أنصاف أقراص، ونموذج صبري أقراص كاملة من فتحات. الرسم يتبع نموذجه."),
        ("A prototype exists (built, in painting, 27 Oct). Check this drawing against it before Production relies on it.", "يوجد نموذج أولي (مبني، قيد الدهان). تُراجع اللوحة عليه قبل الاعتماد."),
        ("We propose; Production decides thickness, tolerances, joint method, welding, glides and finish details.", "نحن نقترح، والإنتاج يحدد السماكة والتفاوتات والوصلات واللحام والتشطيب."),
        ("No structural claim is made. A 3 mm top over this span has not been checked.", "لا توجد ادعاءات إنشائية. لم يُراجع لوح ٣ مم على هذا البحر."),
        ("Colours Bone, Clay, Carbon are the book colours; Oxblood is used in the renders. Paint system and gloss to be confirmed. No costs or prices here.", "الألوان عاجي وطيني وفحمي من الكتاب والعنابي في التصاميم. الدهان يؤكد لاحقاً. لا أسعار هنا."),
        ("Arabic wording is a draft and needs a technical reader before it goes to the factory.", "الصياغة العربية مسودة وتحتاج مراجعة فنية قبل الإرسال للمصنع."),
    ]
    b += H.bi(20, 98, "NOTES", "ملاحظات", 2.8, bold=True)
    for i, (en, ar) in enumerate(notes):
        yy = 107 + i * 12.6
        b += H.txt(20, yy, f"{i + 1}.", 2.4, bold=True) + H.txt(27, yy, en, 2.4)
        b += H.txt(409, yy + 4.6, ar, 2.4, "start", False, "#444", ar=True)
    sheets.append(("bom-notes", sheet(4, 4, "Bill of materials and notes", "قائمة المكونات والملاحظات", "-", b, logo)))
    return sheets


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = "data:image/svg+xml;base64," + base64.b64encode(open(os.path.join(ROOT, "brand", "objekt-logo.svg"), "rb").read()).decode()
    ref = H.img_uri(os.path.join(ROOT, "images", "OBJ-003.jpg"), 700)
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
    t, d_, tot = cut_lengths()
    print(f"K={K:.4f} top_z={TOP_Z:.2f} H={H_DISC:.2f} cap={CAP:.2f} zc={ZC:.2f} slot={SLOT_L:.1f} capw={CAP_W:.1f} cut top={t:.0f} disc={d_:.0f} total={tot:.0f}")


if __name__ == "__main__":
    main()
