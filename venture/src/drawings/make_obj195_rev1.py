"""OBJ-195 side table (library item, 1 photo), rev 1 APPROVED: drawing set (A3, EN/AR) + DXF.

Overall 420 W x 420 D x 550 H mm are Sabry's (42 x 42 x 55 cm). Everything else is estimated from one photo:
a square box top (420 x 420 x 185) sitting on a smaller square block base (320 x 320 x 365), centred.
Proposed build: 3 mm sheet, hollow. Production decides everything; moulded or lacquered is also possible.

Run: python3 make_obj195_rev1.py     Needs: numpy ezdxf pymupdf pillow, node + playwright.
Output: venture/drawings/OBJ-195/
"""
import base64, math, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_obj177_rev1 as H
import make_obj194_rev4 as M          # shared projection and shading helpers only

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "venture", "drawings", "OBJ-195")
PID, REV, DATE = "OBJ-195", "1", "11 Nov 2026"
PRE = f"{PID}_rev{REV}_"
APPROVED = True                          # Sabry approved rev 1 on 11 Nov 2026
if APPROVED:
    STAMP_EN = "Approved by Sabry 11 Nov 2026. Production review pending. Not engineered"
    STAMP_AR = "معتمد من صبري ١١ نوفمبر ٢٠٢٦. مراجعة الإنتاج قيد الانتظار. بدون مراجعة هندسية"
else:
    STAMP_EN, STAMP_AR = H.STAMP_EN, H.STAMP_AR
STAMP_COL = "#1d6b3a" if APPROVED else "#b3261e"
STAMP_BG = "#f0f8f2" if APPROVED else "#fff4f2"
INK = H.INK
T = 3.0

W = D = 420.0                 # given
HT = 550.0                    # given
BOXH = 185.0                  # estimate: box top, from the photo
BASEH = HT - BOXH             # 365
BW = 320.0                    # estimate: base block, square, centred
OFF = (W - BW) / 2            # 50 overhang each side
BOX_POLY = [(0, 0), (W, 0), (W, D), (0, D)]
BASE_POLY = [(OFF, OFF), (OFF + BW, OFF), (OFF + BW, OFF + BW), (OFF, OFF + BW)]


def ar_num(t):
    return str(t).translate(str.maketrans('0123456789.', '٠١٢٣٤٥٦٧٨٩٫'))


def parts():
    return [
        ("P1_top_plate", "Top plate", 1, "poly", BOX_POLY),
        ("P2_box_bottom_plate", "Box bottom plate", 1, "poly", BOX_POLY),
        ("P3_box_band", "Box band", 1, "band", (4 * W, BOXH, [W, 2 * W, 3 * W])),
        ("P4_base_band", "Base band", 1, "band", (4 * BW, BASEH, [BW, 2 * BW, 3 * BW])),
        ("P5_base_cap", "Base cap plate", 1, "poly", [(0, 0), (BW, 0), (BW, BW), (0, BW)]),
    ]


def nest_layout():
    return {"P3_box_band": [(10, 10, False)], "P4_base_band": [(10, 225, False)],
            "P1_top_plate": [(10, 620, False)], "P2_box_bottom_plate": [(460, 620, False)], "P5_base_cap": [(910, 620, False)]}


def part_pts(kind, data, x, y, vert=False):
    if kind == "poly":
        return [(x + a, y + b) for a, b in data]
    w, h, _ = data
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def cut_lengths():
    tot = 0.0; out = {}
    for key, name, qty, kind, data in parts():
        pts = part_pts(kind, data, 0, 0)
        per = M.perimeter(pts); out[key] = per * qty; tot += per * qty
    out["total"] = tot
    return out


def write_dxf():
    import ezdxf
    def new():
        d = ezdxf.new("R2010"); d.units = 4
        d.layers.add("CUT", color=7); d.layers.add("BEND", color=5, linetype="DASHED"); d.layers.add("NOTE", color=8)
        return d
    def put(m, kind, data, x, y):
        m.add_lwpolyline(part_pts(kind, data, x, y), close=True, dxfattribs={"layer": "CUT"})
        if kind == "band":
            for f in data[2]:
                m.add_line((x + f, y), (x + f, y + data[1]), dxfattribs={"layer": "BEND"})
    for key, name, qty, kind, data in parts():
        d = new(); put(d.modelspace(), kind, data, 0, 0)
        d.modelspace().add_text(f"{PID} rev {REV} {key} x{qty}. mm. 3 mm sheet (proposed). Sizes estimated from one photo. {'APPROVED' if APPROVED else 'DRAFT'}.",
                                dxfattribs={"layer": "NOTE", "height": 8}).set_placement((0, -30))
        d.saveas(os.path.join(OUT, PRE + key + ".dxf"))
    d = new(); d.layers.add("SHEET", color=1); m = d.modelspace()
    m.add_lwpolyline([(0, 0), (2500, 0), (2500, 1250), (0, 1250)], close=True, dxfattribs={"layer": "SHEET"})
    for key, name, qty, kind, data in parts():
        for (x, y, v) in nest_layout()[key]: put(m, kind, data, x, y)
    d.saveas(os.path.join(OUT, PRE + "nest_1250x2500.dxf"))


def draw_iso(ox, oy, s, lift=0.0):
    cam = np.array(M.to_cam()); svg = ""
    for fa in (M.prism(BASE_POLY, 0, BASEH), M.prism(BOX_POLY, BASEH + lift, HT + lift)):
        vis = [(f, M.view_iso(np.mean(np.array(f[1]), axis=0))) for f in fa if float(np.dot(M.normal(f[1]), cam)) > 0.02]
        vis.sort(key=lambda t: -t[1][2])
        for f, _ in vis:
            svg += M.poly_svg([M.view_iso(q)[:2] for q in f[1]], ox, oy, s, M.shade(M.normal(f[1])))
    return svg


def draw_front(ox, oy, s):
    svg = M.poly_svg([(OFF, 0), (OFF + BW, 0), (OFF + BW, BASEH), (OFF, BASEH)], ox, oy, s, M.BRZ_MID)
    svg += M.poly_svg([(0, BASEH), (W, BASEH), (W, HT), (0, HT)], ox, oy, s, M.BRZ_LIT)
    return svg + M.poly_svg([(0, HT), (W, HT), (W, HT + 0.01), (0, HT + 0.01)], ox, oy, s, M.SILVER, w=1.1)


def sheet(n, total, t_en, t_ar, scale, body, logo):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm" font-family="{H.FONT}">'
    s += '<rect width="420" height="297" fill="#fff"/>'
    s += f'<rect x="7" y="7" width="406" height="283" fill="none" stroke="{INK}" stroke-width="0.35"/>'
    s += H.image(11, 10.5, 22, 14, logo)
    s += H.txt(38, 17, f"{PID}  Side table", 5, bold=True) + H.txt(38, 22.5, t_en, 3.2, fill="#444")
    s += H.txt(409, 17, f"طاولة جانبية  {PID}", 5, "start", True, ar=True) + H.txt(409, 22.5, t_ar, 3.2, "start", False, "#444", ar=True)
    s += H.line(7, 27, 413, 27, 0.25)
    s += body
    bx, by, bw, bh = 263, 253, 150, 37
    s += f'<rect x="{bx}" y="{by - 11}" width="{bw}" height="11" fill="{STAMP_BG}" stroke="{STAMP_COL}" stroke-width="0.4"/>'
    s += H.txt(bx + 3, by - 6.3, STAMP_EN, 2.7, bold=True, fill=STAMP_COL) + H.txt(bx + bw - 3, by - 2.2, STAMP_AR, 2.5, "start", False, STAMP_COL, ar=True)
    s += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#fff" stroke="{INK}" stroke-width="0.35"/>'
    cells = [("PRODUCT / المنتج", f"{PID} Side table (name to follow)", 0, 0, 75), ("SIZE / المقاس", "A3", 75, 0, 25),
             ("SCALE / المقياس", scale, 100, 0, 25), ("UNITS / الوحدات", "mm", 125, 0, 25),
             ("MATERIAL / الخامة", "Steel sheet 3 mm, laser cut and folded (proposed)", 0, 12.3, 75),
             ("DATE / التاريخ", DATE, 75, 12.3, 25), ("SHEET / لوحة", f"{n} / {total}", 100, 12.3, 25), ("REV / مراجعة", REV, 125, 12.3, 25),
             ("FINISH / التشطيب", "Satin taupe-brown all over (to be confirmed)", 0, 24.6, 100), ("DRAWN / رسم", "objekt", 100, 24.6, 50)]
    for lab, val, cx, cy, cw in cells:
        s += f'<rect x="{bx + cx}" y="{by + cy}" width="{cw}" height="12.3" fill="none" stroke="{INK}" stroke-width="0.15"/>'
        s += H.txt(bx + cx + 1.3, by + cy + 3.6, lab, 1.9, fill="#666") + H.txt(bx + cx + 1.3, by + cy + 9.2, val, 2.5 if len(val) < 30 else 1.9, bold=True)
    return s + "</svg>"


def build(logo, ref):
    sheets = []; cl = cut_lengths(); nl = nest_layout()
    # ---- sheet 1
    s = 1 / 5; b = ""
    b += H.bi(20, 34, "FRONT ELEVATION  1:5", "المسقط الأمامي", 2.8, bold=True)
    ox, oy = 52, 160
    b += draw_front(ox, oy, s)
    b += H.hdim(ox, ox + W * s, oy + 8, f"{W:.0f}")
    b += H.vdim(ox + W * s + 6, oy - HT * s, oy, f"{HT:.0f}")
    b += H.vdim(ox - 6, oy - BASEH * s, oy, f"{BASEH:.0f} est.", side=-1)
    b += H.vdim(ox - 18, oy - HT * s, oy - BASEH * s, f"{BOXH:.0f} est.", side=-1)
    b += H.hdim(ox + OFF * s, ox + (OFF + BW) * s, oy - 6, f"{BW:.0f} est.", size=2.0)
    b += H.balloon(ox + 15, oy - HT * s - 8, "1", ox + 40, oy - (BASEH + BOXH * 0.5) * s)
    b += H.balloon(ox + 70, oy - HT * s - 8, "2", ox + 60, oy - BASEH * 0.5 * s)
    b += H.bi(150, 34, "SIDE ELEVATION  1:5", "المسقط الجانبي", 2.8, bold=True)
    b += draw_front(152, oy, s)
    b += H.hdim(152, 152 + D * s, oy + 8, f"{D:.0f}")
    b += H.bi(243, 34, "PLAN  1:5", "المسقط الأفقي", 2.8, bold=True)
    px, py = 243, 44
    b += M.poly_svg([(x, D - y) for x, y in BOX_POLY], px, py + D * s, s, M.SILVER)
    b += M.poly_svg([(x, D - y) for x, y in BASE_POLY], px, py + D * s, s, "none", "#777", 0.2, "3 1.2")
    b += H.hdim(px, px + W * s, py + D * s + 8, f"{D:.0f}")
    b += H.txt(px, py + D * s + 17, "base dashed, centred under the box (assumed)", 2.0, fill="#555")
    b += H.bi(330, 34, "REFERENCE (photo, third party)", "المرجع (صورة من طرف ثالث)", 2.1, bold=True)
    b += H.image(330, 40, 80, 80, ref, True) + H.txt(330, 124, "Reference only. Not our piece.", 1.9, fill="#555")
    b += H.bi(20, 190, "VIEW", "منظور", 2.8, bold=True)
    b += M.poly_svg([(0, 0)], 0, 0, 1, "none", "none", 0) if False else ""
    b += draw_iso(100, 268, 0.075)
    rows = [[("Part", "الجزء"), ("", ""), ("Finish (from the photo)", "التشطيب (من الصورة)"), ("Note", "ملاحظة")],
            [("1 Box and 2 Base", "الصندوق والقاعدة"), ("swatch", "#80705c"), ("Taupe-brown, satin metal look", "بني رمادي، مظهر معدن ساتان"), ("one colour all over, to confirm", "لون واحد، للتأكيد")]]
    b += H.bi(170, 190, "FINISH", "التشطيب", 2.6, bold=True)
    b += H.table(170, 196, [26, 10, 50, 44], rows, 7.0, 1.9)
    b += H.txt(170, 218, "Hex is only a screen guess from the photo. Not an objekt paint colour.", 1.8, fill="#555")
    b += H.bi(170, 228, "1 Box top  2 Base block", "١ صندوق علوي   ٢ كتلة القاعدة", 2.3)
    b += H.bi(170, 236, "420 x 420 x 550 are Sabry's sizes. The rest is read from one photo: approximate.", "٤٢٠ × ٤٢٠ × ٥٥٠ مقاسات صبري. الباقي من صورة واحدة: تقريبي.", 2.1)
    sheets.append(("views", sheet(1, 4, "Views and overall sizes", "المساقط والمقاسات", "1:5", b, logo)))
    # ---- sheet 2
    b = ""; sp = 1 / 6
    def plate(x0, y0, w, h, en, ar):
        r = H.bi(x0, y0 - 10, en, ar, 2.2, bold=True)
        r += f'<rect x="{x0}" y="{y0}" width="{w * sp:.2f}" height="{h * sp:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
        r += H.hdim(x0, x0 + w * sp, y0 + h * sp + 6, f"{w:.0f}", size=1.9) + H.vdim(x0 + w * sp + 4, y0, y0 + h * sp, f"{h:.0f}", size=1.9)
        return r
    b += plate(22, 48, W, D, "P1 TOP PLATE (1)  1:6", "ل١ لوح علوي (١)")
    b += plate(120, 48, W, D, "P2 BOX BOTTOM PLATE (1)  1:6", "ل٢ لوح سفلي للصندوق (١)")
    b += plate(220, 48, BW, BW, "P5 BASE CAP PLATE (1)  1:6", "ل٥ غطاء القاعدة (١)")
    def band(xp, yp, en, ar, w, h, folds):
        r = H.bi(xp - 2, yp - 11, en, ar, 2.2, bold=True)
        r += f'<rect x="{xp}" y="{yp}" width="{w * sp:.2f}" height="{h * sp:.2f}" fill="#ece8df" stroke="{INK}" stroke-width="0.4"/>'
        for f in folds: r += H.line(xp + f * sp, yp - 2, xp + f * sp, yp + h * sp + 2, 0.2, "#2255aa", "5 1.2 1 1.2")
        pos = [0.0] + list(folds) + [w]
        for a, c in zip(pos[:-1], pos[1:]): r += H.txt(xp + (a + c) / 2 * sp, yp + h * sp / 2 + 0.7, f"{c - a:.0f}", 1.8, "middle")
        return r + H.hdim(xp, xp + w * sp, yp + h * sp + 5, f"{w:.0f} x {h:.0f}", size=1.9)
    b += band(22, 152, "P3 BOX BAND (1), 3 folds  1:6", "ل٣ شريط الصندوق (١)، ٣ ثنيات", 4 * W, BOXH, [W, 2 * W, 3 * W])
    b += band(22, 208, "P4 BASE BAND (1), 3 folds  1:6", "ل٤ شريط القاعدة (١)، ٣ ثنيات", 4 * BW, BASEH, [BW, 2 * BW, 3 * BW])
    b += H.txt(22, 283, "Blue dash-dot = fold, all 90 degrees. Each band closes at a seam at one corner (Production decides where and how).", 1.8, fill="#555")
    rows = [[("DATA", "بيانات"), ""],
            [("Overall W x D x H (given)", "العرض × العمق × الارتفاع (معطى)"), f"{W:.0f} x {D:.0f} x {HT:.0f}"],
            [("Box height / base height (est.)", "ارتفاع الصندوق / القاعدة (تقدير)"), f"{BOXH:.0f} / {BASEH:.0f}"],
            [("Base block (est., square, centred)", "كتلة القاعدة (تقدير، مربعة، بالمنتصف)"), f"{BW:.0f} x {BW:.0f}"],
            [("Box overhang each side", "بروز الصندوق من كل جهة"), f"{OFF:.0f}"],
            [("Sheet thickness (proposed)", "سماكة الصاج (مقترحة)"), f"{T:.0f}"]]
    b += H.table(300, 48, [60, 52], rows, 6.2, 1.9)
    sheets.append(("parts", sheet(2, 4, "Parts: flat patterns", "القطع: الأشكال المسطحة", "1:6", b, logo)))
    # ---- sheet 3
    b = H.bi(20, 34, "EXPLODED VIEW  1:8", "منظور مفكوك", 2.8, bold=True)
    b += draw_iso(80, 135, 0.1, lift=200.0)
    b += H.bi(215, 34, "PROPOSED SEQUENCE (Production decides)", "تسلسل مقترح (القرار للإنتاج)", 2.8, bold=True)
    steps = [("Laser cut P1 to P5 from 3 mm sheet. Fold P3 and P4 at the blue lines (3 folds each).", "قص الليزر للقطع من ل١ إلى ل٥ من صاج ٣ مم. ثني ل٣ ول٤ عند الخطوط الزرقاء (٣ ثنيات لكل منهما)."),
             ("Weld the base: the band closes at its seam, then the cap plate on top. The underside stays open.", "لحام القاعدة: يُقفل الشريط عند وصلته ثم غطاء علوي. الأسفل يبقى مفتوحاً."),
             ("Build the box: bottom plate, the band round it, then the top plate.", "تجميع الصندوق: اللوح السفلي، الشريط حوله، ثم اللوح العلوي."),
             ("Fix the box on the base, centred, 50 overhang each side (dashed outline on the plan).", "تثبيت الصندوق على القاعدة بالمنتصف وبروز ٥٠ من كل جهة (الخط المتقطع في المسقط)."),
             ("Dress the seams, then finish. Glides if wanted.", "تنعيم الوصلات ثم التشطيب. قواعد أرضية إن لزم.")]
    for i, (en, ar) in enumerate(steps):
        yy = 44 + i * 17
        b += H.txt(215, yy, f"{i + 1}.", 2.4, bold=True) + H.bi(221, yy, en, ar, 2.1)
    ns = 1 / 14; nx, ny = 20, 168
    b += H.bi(nx, 152, "CUTTING LAYOUT  1:14  (assumed sheet 1250 x 2500 x 3)", "توزيع القص (لوح مفترض ١٢٥٠ × ٢٥٠٠ × ٣)", 2.6, bold=True)
    b += f'<rect x="{nx}" y="{ny}" width="{2500 * ns:.2f}" height="{1250 * ns:.2f}" fill="#fafafa" stroke="{INK}" stroke-width="0.3"/>'
    for key, name, qty, kind, data in parts():
        for (x, y, v) in nl[key]:
            pts = part_pts(kind, data, x, y)
            d = "M" + " L".join(f"{nx + px_ * ns:.2f},{ny + (1250 - py_) * ns:.2f}" for px_, py_ in pts) + " Z"
            b += f'<path d="{d}" fill="#e6e2d8" stroke="{INK}" stroke-width="0.3"/>'
            cx = sum(p[0] for p in pts) / 4; cy = sum(p[1] for p in pts) / 4
            b += H.txt(nx + cx * ns, ny + (1250 - cy) * ns + 1, key.split("_")[0], 2.2, "middle", fill="#333")
    b += H.hdim(nx, nx + 2500 * ns, ny + 1250 * ns + 6, "2500", size=2.0) + H.vdim(nx + 2500 * ns + 4, ny, ny + 1250 * ns, "1250", size=2.0)
    b += H.txt(20, 278, f"Total cutting length {cl['total'] / 1000:.1f} m on one assumed sheet. Part spacing 30 mm, edge margin 10 mm (assumed).", 2.3, bold=True)
    b += H.txt(20, 284, "Sheet size and nesting are Production's.", 2.0, fill="#555")
    sheets.append(("assembly-cutting", sheet(3, 4, "Assembly and cutting layout", "التركيب وتوزيع القص", "1:8 / 1:14", b, logo)))
    # ---- sheet 4
    b = H.bi(20, 34, "BILL OF MATERIALS", "قائمة المكونات", 2.8, bold=True)
    def row(k, en, ar, qty, pe, pa, size, fe, fa): return [k, (en, ar), str(qty), (pe, pa), size, (fe, fa)]
    sat = ("Satin taupe", "ساتان بني رمادي")
    rows = [[("Item", "بند"), ("Part", "الجزء"), ("Qty", "العدد"), ("Material / process", "الخامة / الطريقة"), ("Size", "المقاس"), ("Finish (to confirm)", "التشطيب (للتأكيد)")],
            row("P1", "Top plate", "لوح علوي", 1, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", f"{W:.0f} x {D:.0f}", *sat),
            row("P2", "Box bottom plate", "لوح سفلي للصندوق", 1, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", f"{W:.0f} x {D:.0f}", "-", "-"),
            row("P3", "Box band", "شريط الصندوق", 1, "Steel sheet 3, cut, folded 3 times", "صاج ٣ مم، قص وثني ٣ مرات", f"{4 * W:.0f} x {BOXH:.0f}", *sat),
            row("P4", "Base band", "شريط القاعدة", 1, "Steel sheet 3, cut, folded 3 times", "صاج ٣ مم، قص وثني ٣ مرات", f"{4 * BW:.0f} x {BASEH:.0f}", *sat),
            row("P5", "Base cap plate", "غطاء القاعدة", 1, "Steel sheet 3, laser cut", "صاج ٣ مم قص ليزر", f"{BW:.0f} x {BW:.0f}", *sat),
            row("G", "Floor glides", "قواعد أرضية", "-", "Tiny feet seem to show in the photo. Production to propose", "يبدو وجود أقدام صغيرة في الصورة. يقترحها الإنتاج", "to follow", "-", "-")]
    b += H.table(20, 40, [10, 40, 12, 100, 52, 48], rows, 7.4, 2.0)
    notes = [
        ("Overall 420 W x 420 D x 550 H (42 x 42 x 55 cm) are Sabry's sizes (11 Nov 2026). Everything else is estimated from one photo.", "المقاسات الكلية ٤٢٠ × ٤٢٠ × ٥٥٠ (٤٢ × ٤٢ × ٥٥ سم) من صبري (١١ نوفمبر ٢٠٢٦). الباقي تقدير من صورة واحدة."),
        ("Rev 1, approved by Sabry 11 Nov 2026. Reference: library item OBJ-195, one photo (third party, not our piece). Drawn exact to the reference by Sabry's standing rule.", "المراجعة ١ معتمدة من صبري ١١ نوفمبر ٢٠٢٦. المرجع: عنصر المكتبة OBJ-195، صورة واحدة (طرف ثالث). مرسوم مطابقاً للمرجع حسب قاعدة صبري."),
        (f"Shape: a square box top {W:.0f} x {D:.0f} x {BOXH:.0f} on a smaller square block {BW:.0f} x {BW:.0f} x {BASEH:.0f}, centred, so the box overhangs {OFF:.0f} each side. Crisp square corners.", f"الشكل: صندوق علوي مربع {ar_num(f'{W:.0f}')} × {ar_num(f'{D:.0f}')} × {ar_num(f'{BOXH:.0f}')} على كتلة مربعة أصغر {ar_num(f'{BW:.0f}')} × {ar_num(f'{BW:.0f}')} × {ar_num(f'{BASEH:.0f}')} بالمنتصف، فيبرز الصندوق {ar_num(f'{OFF:.0f}')} من كل جهة. زوايا حادة."),
        ("The photo shows only the front and one side of the box. The base depth (320) and the centring are assumed, not seen.", "الصورة تُظهر الأمام وجانباً واحداً فقط. عمق القاعدة (٣٢٠) والمنتصف افتراضان وليسا ظاهرين."),
        ("Box height 185 and base 320 wide are estimates measured from the photo; the lamp and sofa in the photo are not part of this product.", "ارتفاع الصندوق ١٨٥ وعرض القاعدة ٣٢٠ تقديران من الصورة؛ المصباح والكنبة ليسا جزءاً من المنتج."),
        ("Build proposed in 3 mm sheet: hollow box and hollow base. The photo could also be a moulded or lacquered piece: Production decides the process.", "التنفيذ المقترح من صاج ٣ مم: صندوق وقاعدة مجوفان. قد تكون القطعة مصبوبة أو مطلية: الإنتاج يقرر الطريقة."),
        ("Finish as the photo: smooth satin taupe-brown all over. Material and method are Production's. Hex is a screen guess.", "التشطيب كما في الصورة: ساتان بني رمادي ناعم. الخامة والطريقة للإنتاج. الرمز تقدير من الشاشة."),
        ("Base underside is left open on the drawing. Closing it, bracing and weight are Production's. No structural claim is made.", "أسفل القاعدة مفتوح في الرسم. التقفيل والتدعيم والوزن للإنتاج. لا توجد ادعاءات إنشائية."),
        ("We propose; Production decides sheet size and thickness, tolerances, joints, glides and finish. No costs or prices are on this drawing.", "نحن نقترح، والإنتاج يحدد مقاس الصاج وسماكته والتفاوتات والوصلات والقواعد والتشطيب. لا أسعار هنا."),
        ("Arabic wording is a draft and needs a technical reader before it goes to the factory.", "الصياغة العربية مسودة وتحتاج مراجعة فنية قبل الإرسال للمصنع."),
    ]
    b += H.bi(20, 122, "NOTES", "ملاحظات", 2.8, bold=True)
    for i, (en, ar) in enumerate(notes):
        yy = 131 + i * 10.0
        b += H.txt(20, yy, f"{i + 1}.", 2.1, bold=True) + H.txt(27, yy, en, 2.1) + H.txt(409, yy + 4.2, ar, 2.1, "start", False, "#444", ar=True)
    sheets.append(("bom-notes", sheet(4, 4, "Bill of materials and notes", "قائمة المكونات والملاحظات", "-", b, logo)))
    return sheets


def main():
    os.makedirs(OUT, exist_ok=True)
    logo = "data:image/svg+xml;base64," + base64.b64encode(open(os.path.join(ROOT, "brand", "objekt-logo.svg"), "rb").read()).decode()
    ref = H.img_uri(os.path.join(ROOT, "images", "OBJ-195.jpg"), 800)
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
    print({k: round(v, 1) for k, v in cut_lengths().items()})


if __name__ == "__main__":
    main()
