"""OBJ-166 plinth, square box, two heights: drawing set rev 1 (A3, EN/AR) + DXF.  DRAFT, not approved.

Rev 1 (11 Nov 2026), Sabry: the short version is now 700 high (rev 0 had 850), and the finishes are brushed stainless or mirror
polish (rev 0 had Carbon matte or brushed stainless). Footprint 220 x 220 is Sabry's, unchanged. The build is unchanged from rev 0:
one 3 mm blank folded into a square tube with a butt seam, a top and a bottom plate, four turned feet. Rev 0 (approved 1 Nov 2026,
1000 and 850 high) is in the Drive folder and is superseded by this revision once Sabry approves it.

Run: python3 make_obj166_rev1.py     Needs: numpy ezdxf pymupdf pillow, node + playwright.   Output: venture/drawings/OBJ-166/
"""
import base64, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_obj177_rev1 as H
import make_obj194_rev4 as M          # shared helpers only (poly_svg, prism, view_iso, shade, perimeter)

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "venture", "drawings", "OBJ-166")
PID, REV, DATE = "OBJ-166", "1", "11 Nov 2026"
PRE = f"{PID}_rev{REV}_"
APPROVED = False
if APPROVED:
    STAMP_EN = "Approved by Sabry. Production review pending. Not engineered"
    STAMP_AR = "معتمد من صبري. مراجعة الإنتاج قيد الانتظار. بدون مراجعة هندسية"
else:
    STAMP_EN, STAMP_AR = H.STAMP_EN, H.STAMP_AR
STAMP_COL = "#1d6b3a" if APPROVED else "#b3261e"
STAMP_BG = "#f0f8f2" if APPROVED else "#fff4f2"
INK = H.INK

W = D = 220.0                    # Sabry's footprint
T = 3.0                          # sheet thickness (rev 0, proposed)
PL = W - 2 * T                   # plate 214
FOOT_H, FOOT_D, FOOT_IN = 5.0, 16.0, 22.0
HOLE_D, HOLE_SP = 6.5, W - 2 * FOOT_IN          # 6.5 and 176
FACES = (214.0, 208.0, 208.0, 211.0)            # face widths from rev 0
BA = 6.6                                        # bend allowance per bend, rev 0 (inside r 3, K 0.4)
BLANK_W = sum(FACES) + 3 * BA                   # 860.8
FOLDS = [FACES[0] + BA / 2, FACES[0] + BA + FACES[1] + BA / 2, FACES[0] + BA + FACES[1] + BA + FACES[2] + BA / 2]
SIZES = [("H1", 1000.0), ("H2", 700.0)]         # overall heights, floor to top, feet included
FIN = [("S", "Brushed stainless", "#A7ACB1", "ستانلس مصنفر"), ("M", "Mirror polish", "#DCE0E4", "ستانلس مرآة")]


def blank_len(h): return h - FOOT_H


def ar_num(t): return str(t).translate(str.maketrans('0123456789.', '٠١٢٣٤٥٦٧٨٩٫'))


def parts(h):
    return [("body", "Body blank", 1, "rect", (BLANK_W, blank_len(h))), ("top", "Top plate", 1, "rect", (PL, PL)),
            ("bottom", "Bottom plate", 1, "rectholes", (PL, PL))]


def nest(h):
    """list of (key, x, y) lower-left on a 2500 x 1250 sheet: 2 plinths = 2 bodies, 2 top plates, 2 bottom plates."""
    out = [("body", 10, 10), ("body", 10 + BLANK_W + 30, 10)]
    for i, k in enumerate(("top", "top", "bottom", "bottom")):
        out.append((k, 1800 + (i % 2) * (PL + 30), 10 + (i // 2) * (PL + 30)))
    return out


def size_of(key, h): return dict((p[0], p[4]) for p in parts(h))[key]


def holes():
    a, b = (PL - HOLE_SP) / 2, (PL + HOLE_SP) / 2
    return [(a, a), (b, a), (a, b), (b, b)]


def cut_len(h):
    tot = 0.0
    for key, x, y in nest(h):
        w, l = size_of(key, h); tot += 2 * (w + l)
        if key == "bottom": tot += 4 * math.pi * HOLE_D
    return tot


def write_dxf():
    import ezdxf
    def new():
        d = ezdxf.new("R2010"); d.units = 4
        d.layers.add("CUT", color=7); d.layers.add("BEND", color=5, linetype="DASHED"); d.layers.add("NOTE", color=8)
        return d
    def put(m, key, h, x, y):
        w, l = size_of(key, h)
        m.add_lwpolyline([(x, y), (x + w, y), (x + w, y + l), (x, y + l)], close=True, dxfattribs={"layer": "CUT"})
        if key == "bottom":
            for hx, hy in holes(): m.add_circle((x + hx, y + hy), HOLE_D / 2, dxfattribs={"layer": "CUT"})
        if key == "body":
            for f in FOLDS: m.add_line((x + f, y), (x + f, y + l), dxfattribs={"layer": "BEND"})
    for tag, h in SIZES:
        for key, name, qty, kind, data in parts(h):
            d = new(); put(d.modelspace(), key, h, 0, 0)
            d.modelspace().add_text(f"{PID} rev {REV} {int(h)} high, {key} x{qty}. mm. 3 mm sheet (proposed). DRAFT.", dxfattribs={"layer": "NOTE", "height": 8}).set_placement((0, -30))
            d.saveas(os.path.join(OUT, PRE + f"{int(h)}_{key}.dxf"))
        d = new(); d.layers.add("SHEET", color=1); m = d.modelspace()
        m.add_lwpolyline([(0, 0), (2500, 0), (2500, 1250), (0, 1250)], close=True, dxfattribs={"layer": "SHEET"})
        for key, x, y in nest(h): put(m, key, h, x, y)
        d.saveas(os.path.join(OUT, PRE + f"{int(h)}_nest_1250x2500.dxf"))


SILVER_L, SILVER_M, SILVER_D = "#b9bdc2", "#a2a7ad", "#8a8f95"


def draw_front(ox, oy, s, h, fill):
    return M.poly_svg([(0, FOOT_H), (W, FOOT_H), (W, h), (0, h)], ox, oy, s, fill) + \
        "".join(M.poly_svg([(fx - 8, 0), (fx + 8, 0), (fx + 8, FOOT_H), (fx - 8, FOOT_H)], ox, oy, s, "#666", w=0.2) for fx in (FOOT_IN, W - FOOT_IN))


def draw_iso(ox, oy, s, h, lift=0.0):
    cam = np.array(M.to_cam()); svg = ""
    sq = lambda a, b: [(a, a), (b, a), (b, b), (a, b)]
    groups = [M.prism(sq(0, W), FOOT_H - lift * 0.5, h), M.prism(sq(T, W - T), h + lift, h + lift + T), M.prism(sq(T, W - T), FOOT_H - lift - T, FOOT_H - lift)]
    for fa in groups:
        vis = [(f, M.view_iso(np.mean(np.array(f[1]), axis=0))) for f in fa if float(np.dot(M.normal(f[1]), cam)) > 0.02]
        vis.sort(key=lambda t: -t[1][2])
        for f, _ in vis:
            n = M.normal(f[1]); v = float(np.dot(n, np.array([-0.5, -0.6, 0.65]) / np.linalg.norm([-0.5, -0.6, 0.65])))
            col = SILVER_L if n[2] > 0.9 else (SILVER_M if v > -0.15 else SILVER_D)
            svg += M.poly_svg([M.view_iso(q)[:2] for q in f[1]], ox, oy, s, col)
    return svg


def sheet(n, total, t_en, t_ar, scale, body, logo):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm" font-family="{H.FONT}">'
    s += '<rect width="420" height="297" fill="#fff"/>'
    s += f'<rect x="7" y="7" width="406" height="283" fill="none" stroke="{INK}" stroke-width="0.35"/>'
    s += H.image(11, 10.5, 22, 14, logo)
    s += H.txt(38, 17, f"{PID}  Plinth, square box, two heights", 5, bold=True) + H.txt(38, 22.5, t_en, 3.2, fill="#444")
    s += H.txt(409, 17, f"قاعدة عرض، صندوق مربع، ارتفاعان  {PID}", 5, "start", True, ar=True) + H.txt(409, 22.5, t_ar, 3.2, "start", False, "#444", ar=True)
    s += H.line(7, 27, 413, 27, 0.25) + body
    bx, by, bw, bh = 263, 253, 150, 37
    s += f'<rect x="{bx}" y="{by - 11}" width="{bw}" height="11" fill="{STAMP_BG}" stroke="{STAMP_COL}" stroke-width="0.4"/>'
    s += H.txt(bx + 3, by - 6.3, STAMP_EN, 2.7, bold=True, fill=STAMP_COL) + H.txt(bx + bw - 3, by - 2.2, STAMP_AR, 2.5, "start", False, STAMP_COL, ar=True)
    s += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#fff" stroke="{INK}" stroke-width="0.35"/>'
    cells = [("PRODUCT / المنتج", f"{PID} Plinth, two heights (name to follow)", 0, 0, 75), ("SIZE / المقاس", "A3", 75, 0, 25),
             ("SCALE / المقياس", scale, 100, 0, 25), ("UNITS / الوحدات", "mm", 125, 0, 25),
             ("MATERIAL / الخامة", "Stainless steel 3 mm (proposed)", 0, 12.3, 75), ("DATE / التاريخ", DATE, 75, 12.3, 25),
             ("SHEET / لوحة", f"{n} / {total}", 100, 12.3, 25), ("REV / مراجعة", REV, 125, 12.3, 25),
             ("FINISH / التشطيب", "Brushed stainless or mirror polish", 0, 24.6, 100), ("DRAWN / رسم", "objekt", 100, 24.6, 50)]
    for lab, val, cx, cy, cw in cells:
        s += f'<rect x="{bx + cx}" y="{by + cy}" width="{cw}" height="12.3" fill="none" stroke="{INK}" stroke-width="0.15"/>'
        s += H.txt(bx + cx + 1.3, by + cy + 3.6, lab, 1.9, fill="#666") + H.txt(bx + cx + 1.3, by + cy + 9.2, val, 2.5 if len(val) < 30 else 1.9, bold=True)
    return s + "</svg>"


def build(logo, ref):
    sheets = []
    # ---- sheet 1
    b = H.bi(20, 34, "FRONT ELEVATION  1:8  (the side is identical)", "المسقط الأمامي (الجانب مطابق)", 2.8, bold=True)
    s = 1 / 8; oy = 190
    for k, (tag, h) in enumerate(SIZES):
        ox = 35 + k * 62
        b += draw_front(ox, oy, s, h, SILVER_M)
        b += H.hdim(ox, ox + W * s, oy + 7, f"{W:.0f}")
        b += H.vdim(ox + W * s + 5, oy - h * s, oy, f"{h:.0f}", side=1)
    b += H.line(25, oy, 150, oy, 0.4)
    b += H.txt(35, 34 + 10, "", 2)
    b += H.bi(165, 34, "PLAN  1:4", "المسقط الأفقي", 2.8, bold=True)
    px, py = 168, 46; ps = 1 / 4
    b += M.poly_svg([(0, 0), (W, 0), (W, D), (0, D)], px, py + D * ps, ps, SILVER_L)
    for fx, fy in ((FOOT_IN, FOOT_IN), (W - FOOT_IN, FOOT_IN), (FOOT_IN, D - FOOT_IN), (W - FOOT_IN, D - FOOT_IN)):
        b += f'<circle cx="{px + fx * ps:.2f}" cy="{py + (D - fy) * ps:.2f}" r="{FOOT_D / 2 * ps:.2f}" fill="none" stroke="#777" stroke-width="0.2" stroke-dasharray="1.2 0.8"/>'
    b += H.hdim(px, px + W * ps, py + D * ps + 7, f"{W:.0f}") + H.vdim(px + W * ps + 6, py, py + D * ps, f"{D:.0f}")
    b += H.txt(px, py + D * ps + 15, "feet dashed, 22 in from each edge", 1.9, fill="#555")
    b += H.bi(250, 34, "VARIANTS (one product)", "الأنواع (منتج واحد)", 2.8, bold=True)
    rows = [[("Code", "الرمز"), ("Height", "الارتفاع"), ("Footprint", "القاعدة"), ("Finish", "التشطيب")]]
    for tag, h in SIZES:
        for ft, fn, hx, far in FIN:
            rows.append([f"166-{int(h)}-{ft}", f"{int(h)}", f"{W:.0f} x {D:.0f}", (fn, far)])
    b += H.table(250, 40, [24, 16, 26, 38], rows, 7.0, 1.9)
    b += H.bi(250, 92, "FINISHES", "التشطيب", 2.8, bold=True)
    rows = [[("Finish", "التشطيب"), ("", ""), ("Note", "ملاحظة")],
            [("Brushed stainless", "ستانلس مصنفر"), ("swatch", "#A7ACB1"), ("Stainless 3 mm, brushed along the height. No colour.", "ستانلس ٣ مم، تصنيفر بالطول")],
            [("Mirror polish", "ستانلس مرآة"), ("swatch", "#DCE0E4"), ("Stainless 3 mm, mirror polished. Needs the few skilled polishers.", "ستانلس ٣ مم، تلميع مرآة")]]
    b += H.table(250, 98, [34, 10, 90], rows, 7.0, 1.9)
    b += H.txt(250, 124, "Grade, brush grade and polish are Production's. Hex is a screen guess.", 1.8, fill="#555")
    b += H.bi(330, 140, "REFERENCE (photo, third party)", "المرجع (صورة من طرف ثالث)", 2.1, bold=True)
    b += H.image(330, 144, 56, 84, ref, True) + H.txt(330, 232, "Shape and finish as in this photo; not our piece.", 1.8, fill="#555")
    b += H.bi(20, 232, "Rev 1: the short version is 700 high (rev 0: 850). Finishes: brushed stainless or mirror (rev 0: Carbon or brushed).",
              "المراجعة ١: النسخة القصيرة ٧٠٠ (كانت ٨٥٠). التشطيب: ستانلس مصنفر أو مرآة (كان كربون أو مصنفر).", 2.1)
    b += H.bi(20, 243, "220 x 220 and the heights 1000 and 700 are Sabry's. Feet size is an estimate from his close-up photo.",
              "٢٢٠ × ٢٢٠ والارتفاعان ١٠٠٠ و٧٠٠ من صبري. حجم الأقدام تقدير من صورة قريبة.", 2.1)
    sheets.append(("views", sheet(1, 5, "Views, variants and finishes", "المساقط والأنواع والتشطيب", "1:8 / 1:4", b, logo)))
    # ---- sheet 2: parts at 1:6
    sp = 1 / 6; b = ""
    x0 = 22
    for k, (tag, h) in enumerate(SIZES):
        L = blank_len(h); xx = x0 + k * 168
        b += H.bi(xx, 34, f"ITEM 1: BODY BLANK, {int(h)} high (1:6)", f"بند ١: شريحة الصندوق، ارتفاع {ar_num(int(h))}", 2.3, bold=True)
        b += f'<rect x="{xx}" y="46" width="{BLANK_W * sp:.2f}" height="{L * sp:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
        for f in FOLDS: b += H.line(xx + f * sp, 44, xx + f * sp, 46 + L * sp + 2, 0.2, "#2255aa", "5 1.2 1 1.2")
        pos = [0.0] + [FACES[0], FACES[0] + BA + FACES[1], FACES[0] + 2 * BA + FACES[1] + FACES[2], BLANK_W]
        for a_, c_, lab in ((0, FOLDS[0], FACES[0]), (FOLDS[0], FOLDS[1], FACES[1]), (FOLDS[1], FOLDS[2], FACES[2]), (FOLDS[2], BLANK_W, FACES[3])):
            b += H.txt(xx + (a_ + c_) / 2 * sp, 46 + L * sp / 2 + 0.7, f"{lab:.0f}", 1.8, "middle")
        b += H.hdim(xx, xx + BLANK_W * sp, 46 + L * sp + 6, f"{BLANK_W:.1f}") + H.vdim(xx + BLANK_W * sp + 6, 46, 46 + L * sp, f"{L:.0f}")
    xp = 360
    b += H.bi(xp - 12, 34, "ITEM 2 TOP PLATE (1:6)", "بند ٢: لوح علوي", 2.0, bold=True)
    b += f'<rect x="{xp}" y="46" width="{PL * sp:.2f}" height="{PL * sp:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>' + H.hdim(xp, xp + PL * sp, 46 + PL * sp + 5, f"{PL:.0f}", size=1.8)
    b += H.bi(xp - 12, 98, "ITEM 3 BOTTOM PLATE (1:6)", "بند ٣: لوح سفلي", 2.0, bold=True)
    b += f'<rect x="{xp}" y="110" width="{PL * sp:.2f}" height="{PL * sp:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
    for hx, hy in holes(): b += f'<circle cx="{xp + hx * sp:.2f}" cy="{110 + hy * sp:.2f}" r="{HOLE_D / 2 * sp:.2f}" fill="#fff" stroke="{INK}" stroke-width="0.3"/>'
    b += H.hdim(xp, xp + PL * sp, 110 + PL * sp + 5, f"{PL:.0f}", size=1.8) + H.txt(xp - 12, 110 + PL * sp + 11, f"4 x Ø{HOLE_D}, spacing {HOLE_SP:.0f}", 1.8, fill="#555")
    b += H.txt(22, 232, "Blue dash-dot = bend line, 90 degrees. Bend values assume inside radius 3, K 0.4; Production confirms. The 4th corner is a butt seam:", 1.8, fill="#555")
    b += H.txt(22, 236, "face 4 stops 3 short of face 1; weld inside, grind flush. On brushed stainless the weld and grinding marks are re-brushed.", 1.8, fill="#555")
    rows = [[("DATA", "بيانات"), ""],
            [("Footprint (given)", "القاعدة (معطى)"), f"{W:.0f} x {D:.0f}"], [("Heights (given)", "الارتفاعان (معطى)"), "1000 / 700"],
            [("Blank length = height - 5", "طول الشريحة = الارتفاع - ٥"), "995 / 695"], [("Blank width", "عرض الشريحة"), f"{BLANK_W:.1f}"],
            [("Plates", "الألواح"), f"{PL:.0f} x {PL:.0f}, 3 mm"], [("Feet", "الأقدام"), f"4 x Ø{FOOT_D:.0f} x {FOOT_H:.0f}"]]
    b += H.table(190, 172, [64, 60], rows, 6.2, 1.9)
    sheets.append(("parts", sheet(2, 5, "Parts: flat patterns", "القطع: الأشكال المسطحة", "1:6", b, logo)))
    # ---- sheet 3: assembly
    b = H.bi(20, 34, "EXPLODED VIEW  1:12  (1000 version)", "منظور مفكوك (نسخة ١٠٠٠)", 2.8, bold=True)
    b += draw_iso(90, 150, 0.085, 1000.0, lift=120.0)
    b += H.bi(215, 34, "ASSEMBLY SEQUENCE (proposed)", "تسلسل التجميع (مقترح)", 2.8, bold=True)
    steps = [("Fold the blank on its three bend lines into a square tube. Hold it in a square jig, weld the butt seam, grind flush.", "ثني الشريحة على خطوط الثني الثلاثة إلى أنبوب مربع، ثم لحام الوصلة وتنعيمها."),
             ("Weld the top plate into the top of the tube, flush with the edge all round. Grind flush.", "لحام اللوح العلوي داخل أعلى الأنبوب بمحاذاة الحافة وتنعيمه."),
             ("Weld the four M6 weld nuts to the bottom plate, then weld the plate into the bottom of the tube, flush. Grind flush.", "لحام أربعة صواميل M6 باللوح السفلي ثم لحامه أسفل الأنبوب وتنعيمه."),
             ("Finish: brushed stainless, brush the four sides along the length and the top. Mirror: polish after welding.", "التشطيب: تصنفير الجوانب الأربعة بالطول والسطح، أو تلميع مرآة بعد اللحام."),
             ("Screw in the four feet after finishing. Check it stands plumb and does not rock.", "تركيب الأقدام الأربعة بعد التشطيب والتأكد من الاستواء وعدم الاهتزاز.")]
    for i, (en, ar) in enumerate(steps):
        yy = 44 + i * 17
        b += H.txt(215, yy, f"{i + 1}.", 2.4, bold=True) + H.bi(221, yy, en, ar, 2.0)
    b += H.bi(215, 140, "DETAIL F: FOOT", "تفصيل و: القدم", 2.6, bold=True)
    b += H.txt(215, 148, f"Turned foot with M6 stud, about Ø{FOOT_D:.0f} x {FOOT_H:.0f} high, {FOOT_IN:.0f} in from each outer edge, screwed into a weld nut behind", 1.9)
    b += H.txt(215, 152, "the bottom plate. It lifts the box 5 off the floor. Size, material and thread: Production. Estimated from Sabry's close-up photo.", 1.9)
    b += H.txt(215, 162, "A proposal. Jigs, tack positions, weld type and grinding are for Production.", 1.9, fill="#555")
    sheets.append(("assembly", sheet(3, 5, "Assembly", "التجميع", "1:12", b, logo)))
    # ---- sheet 4: cutting layouts
    b = H.bi(20, 34, "CUTTING LAYOUTS  1:14  (assumed sheet 1250 x 2500 x 3, one sheet makes 2 plinths)", "توزيع القص (لوح مفترض ١٢٥٠ × ٢٥٠٠ × ٣، يكفي قاعدتين)", 2.6, bold=True)
    ns = 1 / 14
    for k, (tag, h) in enumerate(SIZES):
        ny = 48 + k * 100; nx = 20
        b += H.txt(nx, ny - 3, f"{int(h)} high: 2 bodies {BLANK_W:.0f} x {blank_len(h):.0f}, 2 top plates, 2 bottom plates", 2.0, bold=True)
        b += f'<rect x="{nx}" y="{ny}" width="{2500 * ns:.2f}" height="{1250 * ns:.2f}" fill="#fafafa" stroke="{INK}" stroke-width="0.3"/>'
        for key, x, y in nest(h):
            w, l = size_of(key, h)
            b += f'<rect x="{nx + x * ns:.2f}" y="{ny + (1250 - y - l) * ns:.2f}" width="{w * ns:.2f}" height="{l * ns:.2f}" fill="#e6e2d8" stroke="{INK}" stroke-width="0.3"/>'
            b += H.txt(nx + (x + w / 2) * ns, ny + (1250 - y - l / 2) * ns + 1, {"body": "1", "top": "2", "bottom": "3"}[key], 2.2, "middle", fill="#333")
        b += H.hdim(nx, nx + 2500 * ns, ny + 1250 * ns + 5, "2500", size=1.8)
        b += H.txt(nx + 190, ny + 30, f"Cutting length {cut_len(h) / 1000:.1f} m per sheet", 2.2, bold=True)
    b += H.txt(20, 252, "Brush direction on stainless runs along the blank length. Sheet size, grain and kerf are Production's. Part spacing 30, margin 10 (assumed).", 1.9, fill="#555")
    sheets.append(("cutting", sheet(4, 5, "Cutting layouts", "توزيع القص", "1:14", b, logo)))
    # ---- sheet 5: BOM + notes
    b = H.bi(20, 34, "BILL OF MATERIALS (per plinth)", "قائمة المكونات (للقاعدة الواحدة)", 2.8, bold=True)
    rows = [[("Item", "بند"), ("Part", "الجزء"), ("Qty", "العدد"), ("Material / process", "الخامة / الطريقة"), ("Size", "المقاس")],
            ["1", ("Body blank", "شريحة الصندوق"), "1", ("Stainless 3, laser cut, 3 bends, butt seam", "ستانلس ٣ مم، قص ليزر، ٣ ثنيات"), f"{BLANK_W:.1f} x 995 (1000) / 695 (700)"],
            ["2", ("Top plate", "لوح علوي"), "1", ("Stainless 3, laser cut", "ستانلس ٣ مم"), f"{PL:.0f} x {PL:.0f}"],
            ["3", ("Bottom plate", "لوح سفلي"), "1", ("Stainless 3, laser cut, 4 holes", "ستانلس ٣ مم، ٤ ثقوب"), f"{PL:.0f} x {PL:.0f}, 4 x Ø{HOLE_D}"],
            ["4", ("Foot, turned", "قدم مخروطة"), "4", ("M6 stud; stainless or aluminium: Production", "قلاووظ M6"), f"about Ø{FOOT_D:.0f} x {FOOT_H:.0f}"],
            ["5", ("Weld nut M6", "صامولة لحام M6"), "4", ("Stainless", "ستانلس"), "M6"],
            ["6", ("Finish", "التشطيب"), "-", ("Brush finish, or mirror polish, per unit", "تصنفير أو تلميع مرآة"), "-"]]
    b += H.table(20, 40, [10, 40, 12, 100, 60], rows, 7.4, 2.0)
    notes = [("Dimensions in mm. General tolerance ±1, to be confirmed by Production.", "الأبعاد بالمليمتر. التفاوت العام ±١، يؤكده قسم الإنتاج."),
             ("Rev 1 is a DRAFT. Sizes from Sabry (11 Nov 2026): width and depth 220; overall height 1000 or 700, floor to top, feet included.", "المراجعة ١ مسودة. المقاسات من صبري: العرض والعمق ٢٢٠، الارتفاع ١٠٠٠ أو ٧٠٠ من الأرض مع الأقدام."),
             ("One product, two heights and two finishes: four variants (sheet 1). Same body, only the blank length changes: 995 or 695.", "منتج واحد بارتفاعين وتشطيبين: أربعة أنواع. نفس الجسم، يتغير طول الشريحة فقط."),
             ("Body: one blank folded on three bends into a square tube, the fourth corner a butt seam welded and ground flush. Bend values: inside radius 3, K 0.4 (rev 0).", "الجسم: شريحة واحدة بثلاث ثنيات وأنبوب مربع، والركن الرابع وصلة ملحومة ومنعمة."),
             ("Plates sit inside the tube ends, flush, welded all round. On stainless the weld and grinding marks are re-brushed or re-polished.", "الألواح داخل طرفي الأنبوب ومحاذية وملحومة، وتُعاد معالجة آثار اللحام."),
             ("Feet: four turned feet, about Ø16 x 5, 22 in from each edge, screwed in after finishing. Estimated from Sabry's close-up photo; Production confirms.", "الأقدام: أربع أقدام مخروطة وتُركب بعد التشطيب. تقدير من صورة قريبة."),
             ("Finish: brushed stainless (grade, brush grade and direction by Production) or mirror polish, which needs the few skilled polishers.", "التشطيب: ستانلس مصنفر أو تلميع مرآة، والأخير يحتاج عدداً قليلاً من المصقلين."),
             ("Stability: a 1000 high box on a 220 square footprint is tall and narrow. Tipping, weight and wall fixing are not checked and no structural claim is made. Production to advise.", "الثبات: صندوق بارتفاع ١٠٠٠ على قاعدة ٢٢٠ طويل وضيق. لم يُفحص الانقلاب ولا الوزن ولا يوجد ادعاء إنشائي."),
             ("We propose; Production decides sheet, thickness, tolerances, joints and finish. No costs or prices. Arabic wording is a draft for a technical reader.", "نحن نقترح والإنتاج يقرر. لا أسعار. الصياغة العربية مسودة.")]
    b += H.bi(20, 98, "NOTES", "ملاحظات", 2.8, bold=True)
    for i, (en, ar) in enumerate(notes):
        yy = 107 + i * 11.5
        b += H.txt(20, yy, f"{i + 1}.", 2.1, bold=True) + H.txt(27, yy, en, 2.0) + H.txt(409, yy + 4.4, ar, 2.0, "start", False, "#444", ar=True)
    sheets.append(("bom-notes", sheet(5, 5, "Bill of materials and notes", "قائمة المكونات والملاحظات", "-", b, logo)))
    return sheets


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = "data:image/svg+xml;base64," + base64.b64encode(open(os.path.join(ROOT, "brand", "objekt-logo.svg"), "rb").read()).decode()
    ref = H.img_uri(os.path.join(ROOT, "plan", "images", "OBJ-166", "OBJ-166_reference_third-party.jpg"), 800)
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
    import pymupdf
    doc = pymupdf.open()
    for s_ in svgs:
        pp = s_.replace(".svg", ".pdf"); d = pymupdf.open(pp); doc.insert_pdf(d); d.close(); os.remove(pp)
    doc.save(os.path.join(OUT, PRE + "drawings.pdf"), deflate=True, garbage=4); doc.close()
    write_dxf()
    print({int(h): round(cut_len(h) / 1000, 2) for _, h in SIZES}, "blank width", round(BLANK_W, 1), "folds", [round(f, 1) for f in FOLDS])


if __name__ == "__main__":
    main()
