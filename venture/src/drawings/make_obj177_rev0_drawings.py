"""OBJ-177 bench, REV 0: drawing set (SVG sheets, PDF, DXF outlines).

Reads the frame solid written by make_obj177_rev0_model.py (_vol.npy, Y-up, mm)
and draws views and sections from it, so the drawing and the print files agree.

Run: python make_obj177_rev0_drawings.py <model_dir> <images_dir> <out_dir>
images_dir holds iso_lacquer.png, iso_grey.png, photo0.png, photo1.png.
"""
import base64
import json
import sys
from pathlib import Path

import ezdxf
import numpy as np
from skimage import measure

sys.path.insert(0, str(Path(__file__).parent))
import make_obj177_rev0_model as M  # noqa: E402

REV = "REV 0"
DATE = "10.11.2026"
STAMP_EN = "DRAFT, not approved, not engineered"
STAMP_AR = "مسودة، غير معتمدة، غير مُصمَّمة هندسيًا"
TITLE_EN = "OBJ-177  BENCH, MOULDED FRAME, UPHOLSTERED SEAT"
TITLE_AR = "مقعد طويل، هيكل مصبوب، مقعد منجد"
N_SHEETS = 5


# ---------------- geometry from the solid ----------------
def load(model_dir):
    vol = np.load(Path(model_dir) / "_vol.npy")
    meta = json.load(open(Path(model_dir) / "_vol.json"))
    lo, vox = np.array(meta["lo"]), meta["vox"]
    return vol, lo, vox


def contours2d(a, lo_u, lo_v, vox, level=0.0, min_len=8):
    out = []
    for c in measure.find_contours(a, level):
        if len(c) < min_len:
            continue
        u = lo_u + c[:, 0] * vox
        v = lo_v + c[:, 1] * vox
        out.append(np.stack([u, v], 1))
    return out


def views(vol, lo, vox):
    """Return dict of outline lists in mm. Front: (x, y). Side: (z, y). Plan: (x, z)."""
    V = {}
    V["front"] = contours2d(vol.min(axis=2), lo[0], lo[1], vox)
    V["side"] = contours2d(vol.min(axis=0).T, lo[2], lo[1], vox)          # rows z, cols y
    V["plan"] = contours2d(vol.min(axis=1), lo[0], lo[2], vox)
    ix = lambda x: int(round((x - lo[0]) / vox))
    iy = lambda y: int(round((y - lo[1]) / vox))
    iz = lambda z: int(round((z - lo[2]) / vox))
    V["sec_mid"] = contours2d(vol[ix(0)].T, lo[2], lo[1], vox)            # A-A at x = 0 (z, y)
    V["sec_end"] = contours2d(vol[ix(M.hood_apex()[0])].T, lo[2], lo[1], vox)     # B-B through the end bar
    V["sec_long"] = contours2d(vol[:, :, iz(M.FOOT_Z)], lo[0], lo[1], vox)  # C-C through two legs (x, y)
    V["foot"] = contours2d(vol[:, iy(4), :], lo[0], lo[2], vox)          # footprint at 4 mm (x, z)
    V["leg300"] = contours2d(vol[:, iy(240), :], lo[0], lo[2], vox)      # legs at 240 mm high (x, z)
    return V


def bbox(cs):
    a = np.concatenate(cs)
    return a.min(0), a.max(0)


# ---------------- SVG helpers ----------------
class Sheet:
    def __init__(self, n, title_en, title_ar):
        self.n, self.parts = n, []
        self.title_en, self.title_ar = title_en, title_ar

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=2.6, anchor="start", weight=400, fill="#111", ar=False):
        fam = "'DejaVu Sans', Arial, sans-serif" if ar else "Helvetica, Arial, sans-serif"
        d = ""
        s = (str(s).replace("&", "&amp;").replace("<", "&lt;"))
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}" font-family="{fam}"{d}>{s}</text>')

    def bi(self, x, y, en, ar, size=2.6, weight=400, w=None, anchor="start"):
        """English line with the Arabic directly under it."""
        self.text(x, y, en, size, anchor, weight)
        if anchor == "start" and w:
            self.text(x + w, y + size * 1.35, ar, size * 0.95, "end", weight, ar=True)
        else:
            self.text(x, y + size * 1.35, ar, size * 0.95, anchor, weight, ar=True)

    def line(self, x1, y1, x2, y2, w=0.25, col="#111", dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{w}"{da}/>')

    def rect(self, x, y, w, h, sw=0.3, fill="none", col="#111"):
        self.add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')

    def poly(self, pts, sw=0.35, col="#111", fill="none", closed=True, dash=None):
        d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + (" Z" if closed else "")
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"{da}/>')

    def image(self, x, y, w, h, path):
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        mime = "image/png" if str(path).endswith("png") else "image/jpeg"
        self.add(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:{mime};base64,{b64}"/>')

    def svg(self):
        self.title_block()
        body = "\n".join(self.parts)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm">'
                f'<rect width="420" height="297" fill="#fff"/>{body}</svg>')

    def title_block(self):
        self.rect(5, 5, 410, 287, 0.7)
        x0, y0 = 235, 250
        self.text(413, 246, "Draft. Not approved. Not engineered. Shape and most sizes traced from the reference", 2.1, "end", 700)
        self.text(413, 249, "مسودة. غير معتمدة. الشكل ومعظم المقاسات مأخوذة من المرجع تقريبًا", 2.0, "end", 700, ar=True)
        self.rect(x0, y0, 180, 42, 0.5)
        for yy in (262, 277):
            self.line(x0, yy, 415, yy, 0.3)
        for xx in (295, 355):
            self.line(xx, 262, xx, 292, 0.3)
        self.text(238, 255, self.title_en, 2.9, weight=700)
        self.text(412, 260, self.title_ar, 2.9, "end", 700, ar=True)
        self.text(238, 260, "objekt", 2.6)
        cells = [(237, 266.2, "SIZE · المقاس", f"A3 · Sheet {self.n}/{N_SHEETS} · {REV}"),
                 (297, 266.2, "SCALE · المقياس", "as shown · كما هو موضح"),
                 (357, 266.2, "UNITS · الوحدات", "mm · مم"),
                 (237, 281.2, "MATERIAL · الخامة", "GRP on a printed pattern"),
                 (297, 281.2, "FINISH · التشطيب", "Chocolate Duco gloss (tbc)"),
                 (357, 281.2, "DATE · التاريخ", DATE)]
        for x, y, k, v in cells:
            self.text(x, y, k, 2.0, fill="#555", ar=True)
            self.text(x, y + 5.4, v, 2.3)
        self.text(237, 289.6, "فايبر جلاس على نموذج مطبوع", 2.1, ar=True)
        self.text(297, 289.6, "شوكولاتة دوكو لامع (يؤكَّد)", 2.1, ar=True)
        # status stamp
        self.rect(330, 236.5, 85, 6.5, 0.4, "#fff3cd", "#9B6835")
        self.text(372.5, 239.6, STAMP_EN, 2.1, "middle", 700, "#7a4a12")
        self.text(372.5, 242.4, STAMP_AR, 1.9, "middle", 700, "#7a4a12", ar=True)


def place(cs, sx, sy, ox, oy, flip_v=True):
    """Map mm outlines into sheet mm at scale 1:sx, origin (ox, oy) for the min corner."""
    mn, mx = bbox(cs)
    out = []
    for c in cs:
        u = ox + (c[:, 0] - mn[0]) / sx
        v = (oy + (mx[1] - c[:, 1]) / sy) if flip_v else (oy + (c[:, 1] - mn[1]) / sy)
        out.append(np.stack([u, v], 1))
    return out, mn, mx


def dim_h(S, x1, x2, y, label, off=0):
    S.line(x1, y, x2, y, 0.2)
    for x in (x1, x2):
        S.line(x, y - 1.2, x, y + 1.2, 0.2)
    S.text((x1 + x2) / 2, y - 0.8 + off, label, 2.4, "middle")


def dim_v(S, x, y1, y2, label):
    S.line(x, y1, x, y2, 0.2)
    for y in (y1, y2):
        S.line(x - 1.2, y, x + 1.2, y, 0.2)
    S.text(x + 1.5, (y1 + y2) / 2 + 0.8, label, 2.4)


def head(S, x, y, en, ar, w):
    S.text(x, y, en, 2.9, weight=700)
    S.text(x + w, y, ar, 2.8, "end", 700, ar=True)
    S.line(x, y + 1.4, x + w, y + 1.4, 0.25)


# ---------------- sheets ----------------
def sheet1(V, img):
    S = Sheet(1, TITLE_EN, TITLE_AR)
    sc = 8.0
    head(S, 12, 15, "FRONT ELEVATION  1:8", "الواجهة الأمامية ١:٨", 235)
    f, mn, mx = place(V["front"], sc, sc, 14, 22)
    for c in f:
        S.poly(c)
    # cushion (separate upholstered part), dashed
    cx0 = 14 + (M.L / 2 - M.CUSH_L / 2 - (-mn[0] - M.L / 2)) / sc
    top = 22 + (mx[1] - M.H) / sc
    seat = 22 + (mx[1] - M.SEAT_TOP) / sc
    S.rect(14 + (-M.CUSH_L / 2 - mn[0]) / sc, top, M.CUSH_L / sc, (M.H - M.SEAT_TOP) / sc, 0.3, col="#777")
    floor = 22 + mx[1] / sc
    S.line(10, floor, 255, floor, 0.2, "#777", "2,1")
    dim_h(S, 14, 14 + (mx[0] - mn[0]) / sc, floor + 9, "1829")
    dim_v(S, 14 + (mx[0] - mn[0]) / sc + 6, top, floor, "406")
    dim_v(S, 14 + (mx[0] - mn[0]) / sc + 16, seat, floor, "322 seat tray")
    S.text(14 + (mx[0] - mn[0]) / sc + 16, (seat + floor) / 2 + 4, "سطح القاعدة", 2.2, ar=True)
    # balloons
    bal = [(1, 14 + 20 / sc * 10, floor - 18, "frame"), (2, 14 + (mx[0] - mn[0]) / sc / 2, top - 3, "cushion")]
    for n, bx, by, _ in bal:
        S.add(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="2.6" fill="#fff" stroke="#111" stroke-width="0.3"/>')
        S.text(bx, by + 0.9, n, 2.6, "middle", 700)

    head(S, 12, 100, "PLAN  1:8", "المسقط الأفقي ١:٨", 235)
    p, mnp, mxp = place(V["plan"], sc, sc, 14, 106, flip_v=False)
    for c in p:
        S.poly(c)
    S.add(f'<rect x="{14 + (-M.CUSH_L/2 - mnp[0])/sc:.2f}" y="{106 + (-M.CUSH_D/2 - mnp[1])/sc:.2f}" width="{M.CUSH_L/sc:.2f}" height="{M.CUSH_D/sc:.2f}" rx="{M.CUSH_R/sc:.2f}" fill="none" stroke="#777" stroke-width="0.3" stroke-dasharray="1.5,0.8"/>')
    pw, ph = (mxp[0] - mnp[0]) / sc, (mxp[1] - mnp[1]) / sc
    dim_h(S, 14, 14 + pw, 106 + ph + 7, "1829 (at the feet)")
    dim_v(S, 14 + pw + 6, 106, 106 + ph, "686 (at the feet)")
    S.text(14 + pw / 2, 106 + ph / 2 + 1, "cushion 1595 x 488, R81 (dashed)", 2.4, "middle", fill="#555")
    S.text(14 + pw / 2, 106 + ph / 2 + 4.5, "المرتبة ١٥٩٥ × ٤٨٨، نصف قطر ٨١ (متقطع)", 2.3, "middle", fill="#555", ar=True)

    head(S, 262, 15, "SIDE ELEVATION  1:8", "الواجهة الجانبية ١:٨", 70)
    s, mns, mxs = place(V["side"], sc, sc, 268, 22)
    for c in s:
        S.poly(c)
    sw_ = (mxs[0] - mns[0]) / sc
    S.rect(268 + (-M.CUSH_D / 2 - mns[0]) / sc, 22 + (mxs[1] - M.H) / sc, M.CUSH_D / sc, (M.H - M.SEAT_TOP) / sc, 0.3, col="#777")
    sfloor = 22 + mxs[1] / sc
    S.line(264, sfloor, 340, sfloor, 0.2, "#777", "2,1")
    dim_h(S, 268, 268 + sw_, sfloor + 9, "686")

    head(S, 262, 100, "MODEL VIEW (from the print file)", "منظور من ملف الطباعة", 150)
    S.image(262, 104, 75, 75, img["iso_lacquer"])
    S.image(338, 104, 75, 75, img["iso_grey"])
    S.text(299.5, 181, "1  frame, Chocolate gloss (tbc)", 2.2, "middle")
    S.text(375.5, 181, "frame only, as printed", 2.2, "middle")

    head(S, 12, 205, "REFERENCE (supplied tear sheet, another maker; for shape only)", "المرجع (من مصمم آخر؛ للشكل فقط)", 150)
    S.image(12, 209, 34, 34, img["photo0"])
    S.image(48, 209, 34, 34, img["photo1"])
    head(S, 168, 205, "COLOURWAY", "اللون", 62)
    rows = [("Frame", "Chocolate #4A2A1B, Duco gloss", "الهيكل: شوكولاتة، دوكو لامع"),
            ("Cushion", "COM fabric; olive velvet as reference", "المرتبة: قماش العميل؛ قطيفة زيتوني"),
            ("Note", "Chocolate unconfirmed; codes to follow", "الشوكولاتة غير مؤكدة؛ الأكواد لاحقًا")]
    S.rect(86, 209, 6, 6, 0.2, "#4A2A1B")
    S.text(94, 213, "Chocolate", 2.3)
    y = 213
    for k, v, a in rows:
        S.text(168, y, f"{k}: {v}", 2.2)
        S.text(230, y + 3, a, 2.1, "end", ar=True)
        y += 8
    head(S, 12, 252, "OVERALL", "المقاسات الكلية", 210)
    ov = [("Length 1829 (72 in)", "الطول ١٨٢٩"), ("Depth 686 (27 in)", "العمق ٦٨٦"), ("Height 406 (16 in) to cushion top", "الارتفاع ٤٠٦ حتى سطح المرتبة"),
          ("Cushion 1595 x 488 x 84, R81", "المرتبة ١٥٩٥ × ٤٨٨ × ٨٤"), ("Frame top about 400", "أعلى الهيكل حوالي ٤٠٠")]
    y = 258
    for i, (e, a) in enumerate(ov):
        x = 12 + (i % 3) * 72
        if i == 3:
            y += 8
        S.text(x, y, e, 2.3)
        S.text(x + 68, y + 3.2, a, 2.1, "end", ar=True)
    S.text(12, 280, "Overall and cushion sizes from the tear sheet. All other sizes traced from its scaled drawings and photos, +-10 mm.", 2.1, fill="#555")
    S.text(222, 284, "المقاسات الكلية ومقاسات المرتبة من ورقة المرجع. باقي المقاسات تقريبية ±١٠ مم.", 2.0, "end", fill="#555", ar=True)
    return S


def sheet2(V):
    S = Sheet(2, "OBJ-177  SECTIONS AND PROFILES", "قطاعات ومقاطع")
    sc = 5.0
    head(S, 12, 15, "SECTION A-A  mid length  1:5", "قطاع أ-أ منتصف الطول ١:٥", 140)
    a, mn, mx = place(V["sec_mid"], sc, sc, 14, 24 + (M.H - bbox(V["sec_mid"])[1][1]) / sc)
    mx = mx.copy(); mx[1] = M.H
    a = [np.stack([c[:, 0], c[:, 1]], 1) for c in a]
    for c in a:
        S.poly(c, fill="#e6e6e6")
    fl = 24 + mx[1] / sc
    S.rect(14 + (-M.CUSH_D / 2 - mn[0]) / sc, 24 + (mx[1] - M.H) / sc, M.CUSH_D / sc, (M.H - M.SEAT_TOP) / sc, 0.3, col="#777")
    S.text(14 + (0 - mn[0]) / sc, 24 + (mx[1] - M.H) / sc + 9, "cushion 84", 2.3, "middle", fill="#555")
    yv = lambda yy: 24 + (mx[1] - yy) / sc
    xr = 14 + (mx[0] - mn[0]) / sc
    for k, (yy, lab) in enumerate(((332, "332 rail top"), (M.SEAT_TOP, "322 tray top"), (M.SEAT_TOP - M.TRAY_T, "302 tray underside"), (264, "264 rail underside"))):
        ty = yv(332) - 4 + k * 4.2
        S.line(xr + 1, yv(yy), xr + 6, yv(yy), 0.15, "#555"); S.line(xr + 6, yv(yy), xr + 9, ty, 0.15, "#555")
        S.text(xr + 10, ty + 0.8, lab, 2.2)
    S.text(xr + 10, yv(332) + 15, "heights from the floor", 2.1, fill="#555")
    S.text(xr + 36, yv(332) + 18.5, "الارتفاعات من الأرض", 2.0, "end", fill="#555", ar=True)
    S.text(14, yv(250) + 12, "Side rail a round tube about 68, centre 298 high. Tray 20 thick (proposal). Rail stands about 10 above the tray.", 2.2)
    S.text(140, yv(250) + 15.5, "القضيب الجانبي أنبوب حوالي ٦٨. القاعدة ٢٠ سمك (مقترح).", 2.1, "end", ar=True)

    head(S, 12, 120, "SECTION B-B  through the top bar and hoods  1:5", "قطاع ب-ب عبر العارضة العلوية ١:٥", 140)
    b, mnb, mxb = place(V["sec_end"], sc, sc, 14, 128)
    for c in b:
        S.poly(c, fill="#e6e6e6")
    yvb = lambda yy: 128 + (mxb[1] - yy) / sc
    xrb = 14 + (mxb[0] - mnb[0]) / sc
    for yy, lab in ((400, "about 400 top bar"), (314, "about 314 top bar underside"), (0, "floor")):
        S.line(xrb + 1, yvb(yy), xrb + 9, yvb(yy), 0.15, "#555")
        S.text(xrb + 10, yvb(yy) + 0.8, lab, 2.2)
    dim_h(S, 14, xrb, yvb(0) + 7, "686 at the feet")
    S.text(14, yvb(0) + 14, "Top bar about 84 round joins the two hoods; each hood arches over its cone.", 2.2)
    S.text(140, yvb(0) + 17.5, "عارضة علوية حوالي ٨٤ تربط الغطاءين؛ كل غطاء يلتف فوق المخروط.", 2.1, "end", ar=True)

    head(S, 175, 15, "SECTION C-C  through two legs  1:10", "قطاع ج-ج عبر رجلين ١:١٠", 235)
    c_, mnc, mxc = place(V["sec_long"], 10, 10, 177, 24)
    for c in c_:
        S.poly(c, fill="#e6e6e6")
    yvc = lambda yy: 24 + (mxc[1] - yy) / 10
    dim_h(S, 177, 177 + (mxc[0] - mnc[0]) / 10, yvc(0) + 7, "1829")
    S.text(177, yvc(0) + 14, "Each leg a bell cone: about 190 at the floor, rounded top about 92 wide at 382, under the hood.", 2.2)
    S.text(410, yvc(0) + 17.5, "كل رجل مخروط: حوالي ١٩٠ عند الأرض وقمة مستديرة حوالي ٩٢ على ارتفاع ٣٨٢.", 2.1, "end", ar=True)

    head(S, 175, 88, "FOOTPRINT AT THE FLOOR AND LEGS AT 240 HIGH  1:12", "مقطع الأرجل عند الأرض وعلى ارتفاع ٢٤٠ ١:١٢", 235)
    fp, mnf, mxf = place(V["foot"] + V["leg300"], 12, 12, 177, 96, flip_v=False)
    nf = len(V["foot"])
    for i, c in enumerate(fp):
        S.poly(c, 0.35 if i < nf else 0.25, "#111" if i < nf else "#777", dash=None if i < nf else "1.2,0.6")
    pw = (mxf[0] - mnf[0]) / 12
    ph = (mxf[1] - mnf[1]) / 12
    dim_h(S, 177, 177 + pw, 96 + ph + 5, "1829")
    dim_v(S, 177 + pw + 5, 96, 96 + ph, "686")
    fx = M.FOOT_X
    S.text(177, 96 + ph + 12, f"Foot centres: {fx*2:.0f} apart along the length, {M.FOOT_Z*2:.0f} across. Solid line at the floor, dashed at 240 high.", 2.2)
    S.text(410, 96 + ph + 15.5, f"مراكز الأقدام: {fx*2:.0f} بالطول و{M.FOOT_Z*2:.0f} بالعرض. الخط المتصل عند الأرض والمتقطع على ارتفاع ٢٤٠.", 2.1, "end", ar=True)

    head(S, 175, 177, "KEY SIZES", "المقاسات الأساسية", 235)
    rows = [("Overall", "1829 x 686 x 406 (tear sheet)", "الكلي"),
            ("Cushion", "1595 x 488 x 84, R81 corners (tear sheet)", "المرتبة"),
            ("Seat tray top", "322 (406 minus 84)", "سطح القاعدة"),
            ("Tray opening", "about 1609 x 511 (traced)", "فتحة القاعدة"),
            ("Side rail", "round tube about 68, 264 to 332 high (traced)", "القضيب الجانبي"),
            ("Hood", "tube about 80, rises from the rail over each cone and down its outer face", "الغطاء"),
            ("Top bar", "about 84 round, top about 400, joins the two hoods", "العارضة العلوية"),
            ("Legs", "bell cones about 190 at the floor, top about 92 at 382; centres 95 in from the ends and sides", "الأرجل"),
            ("Blends", "tight crease (R14) where the hood meets the cone; R26 to R48 elsewhere", "الانحناءات")]
    y = 183
    for k, v, a in rows:
        S.text(177, y, k, 2.2, weight=700)
        S.text(212, y, v, 2.2)
        S.text(410, y, a, 2.1, "end", ar=True)
        S.line(177, y + 1.5, 410, y + 1.5, 0.1, "#bbb")
        y += 5.4
    return S


def sheet3(V, rep):
    S = Sheet(3, "OBJ-177  3D PRINT PARTS AND PATTERN", "أجزاء الطباعة والنموذج")
    sc = 6.0
    head(S, 12, 15, "PRINT SPLIT, PLAN  1:6", "تقسيم الطباعة، مسقط ١:٦", 400)
    p, mn, mx = place(V["plan"], sc, sc, 60, 24, flip_v=False)
    for c in p:
        S.poly(c, fill="#f1ede6")
    X = lambda x: 60 + (x - mn[0]) / sc
    Z = lambda z: 24 + (z - mn[1]) / sc
    for xc in M.X_CUTS[1:-1]:
        S.line(X(xc), Z(-M.D / 2) - 3, X(xc), Z(M.D / 2) + 3, 0.4, "#c0392b", "3,1.5")
    S.line(X(-M.L / 2) - 3, Z(0), X(M.L / 2) + 3, Z(0), 0.4, "#c0392b", "3,1.5")
    n = 0
    for i in range(4):
        for j in range(2):
            n += 1
            cx = (M.X_CUTS[i] + M.X_CUTS[i + 1]) / 2
            cz = (M.Z_CUTS[j] + M.Z_CUTS[j + 1]) / 2
            S.add(f'<circle cx="{X(cx):.1f}" cy="{Z(cz):.1f}" r="3.2" fill="#fff" stroke="#c0392b" stroke-width="0.35"/>')
            S.text(X(cx), Z(cz) + 1.1, f"{n:02d}", 2.7, "middle", 700, "#c0392b")
    for d in json.load(open(rep))["dowels_model_coords_y_up"]:
        x, y, z = d["at_mm"]
        S.add(f'<circle cx="{X(x):.2f}" cy="{Z(z):.2f}" r="0.9" fill="#1E2A44"/>')
    for xc in M.X_CUTS[1:-1]:
        S.text(X(xc), Z(M.D / 2) + 7, f"cut x = {xc:.0f}", 2.2, "middle", fill="#c0392b")
    S.text(X(M.L / 2) + 5, Z(0) + 0.8, "cut z = 0", 2.2, fill="#c0392b")
    S.text(60, Z(M.D / 2) + 13, "Red dashed: print split. Blue dots: D8 dowels, 22 deep each side (holes D8.4 in the files).", 2.3)
    S.text(360, Z(M.D / 2) + 16.5, "الخط الأحمر: تقسيم الطباعة. النقاط الزرقاء: أوتاد ٨ مم بعمق ٢٢ لكل جانب.", 2.2, "end", ar=True)

    head(S, 12, 162, "PRINT FILES (STL, mm, Z up, positioned in the bench)", "ملفات الطباعة (STL، مم، المحور Z لأعلى)", 250)
    r = json.load(open(rep))["meshes"]
    y = 169
    S.text(12, y, "File", 2.3, weight=700); S.text(100, y, "Size X x Y x Z", 2.3, weight=700); S.text(160, y, "Volume", 2.3, weight=700); S.text(185, y, "Closed", 2.3, weight=700); S.text(205, y, "What", 2.3, weight=700)
    what = {"one-piece": "whole frame, for a large printer or CNC", "01": "end, one leg", "02": "end, one leg", "07": "end, one leg", "08": "end, one leg",
            "03": "rim and tray", "04": "rim and tray", "05": "rim and tray", "06": "rim and tray"}
    for name, v in r.items():
        y += 5.6
        key = "one-piece" if "one-piece" in name else name[-6:-4]
        e = v["extent_xyz_mm"]
        S.text(12, y, name, 2.2)
        S.text(100, y, f"{e[0]:.0f} x {e[1]:.0f} x {e[2]:.0f}", 2.2)
        S.text(160, y, f"{v['volume_l']:.1f} L", 2.2)
        S.text(185, y, "yes" if v["watertight"] else "NO", 2.2)
        S.text(205, y, what[key], 2.2)
    head(S, 272, 162, "PRINT AND PATTERN NOTES", "ملاحظات الطباعة والنموذج", 140)
    notes = [("Parts fit a 500 x 500 x 500 build volume (assumed).", "الأجزاء تناسب حجم طباعة ٥٠٠ مم (افتراض)."),
             ("Print hollow: walls and infill set by Production.", "الطباعة مفرغة؛ الجدار والحشو حسب الإنتاج."),
             ("Glue on dowels; fill, sand and prime to a mirror-smooth pattern.", "تُلصق بالأوتاد ثم تُعجن وتُصنفر وتُبطن."),
             ("Pattern is at finished size. Production adds any mould shrink.", "النموذج بالمقاس النهائي؛ الإنتاج يضيف الانكماش."),
             ("Legs and arches undercut: multi-part mould, split line by Production.", "الأرجل والأقواس بها تجاويف: قالب متعدد الأجزاء."),
             ("Cushion is not printed (sheet 4).", "المرتبة لا تُطبع (الورقة ٤)."),
             ]
    y = 169
    for e, a in notes:
        S.text(272, y, e, 2.15)
        S.text(412, y + 3.1, a, 2.05, "end", ar=True)
        y += 8.2
    return S


def sheet4():
    S = Sheet(4, "OBJ-177  SEAT CUSHION AND BOARD", "المرتبة ولوح القاعدة")
    sc = 5.0
    head(S, 12, 15, "CUSHION PLAN  1:5", "مسقط المرتبة ١:٥", 400)
    x0, y0 = 40, 26
    S.add(f'<rect x="{x0}" y="{y0}" width="{M.CUSH_L/sc:.2f}" height="{M.CUSH_D/sc:.2f}" rx="{M.CUSH_R/sc:.2f}" fill="#eceee4" stroke="#111" stroke-width="0.4"/>')
    bl, bd, br = 1575, 468, 71
    bx, by = x0 + (M.CUSH_L - bl) / 2 / sc, y0 + (M.CUSH_D - bd) / 2 / sc
    S.add(f'<rect x="{bx:.2f}" y="{by:.2f}" width="{bl/sc:.2f}" height="{bd/sc:.2f}" rx="{br/sc:.2f}" fill="none" stroke="#777" stroke-width="0.3" stroke-dasharray="1.5,0.8"/>')
    dim_h(S, x0, x0 + M.CUSH_L / sc, y0 + M.CUSH_D / sc + 7, "1595")
    dim_v(S, x0 + M.CUSH_L / sc + 5, y0, y0 + M.CUSH_D / sc, "488")
    S.text(x0 + 3, y0 + 4, "R81", 2.4)
    S.text(x0 + M.CUSH_L / sc / 2, y0 + M.CUSH_D / sc / 2, "dashed: base board 1575 x 468, R71, 12 plywood (proposal)", 2.4, "middle", fill="#555")
    S.text(x0 + M.CUSH_L / sc / 2, y0 + M.CUSH_D / sc / 2 + 4, "متقطع: لوح القاعدة ١٥٧٥ × ٤٦٨، خشب أبلكاش ١٢ (مقترح)", 2.3, "middle", fill="#555", ar=True)

    head(S, 12, 140, "CUSHION SECTION  1:3", "قطاع المرتبة ١:٣", 190)
    sx = 3.0
    cx, cy = 20, 150
    w, h = 488 / sx, 84 / sx
    r_top = 40 / sx
    d = (f"M{cx},{cy+h} L{cx+w},{cy+h} L{cx+w},{cy+r_top} Q{cx+w},{cy} {cx+w-r_top},{cy} "
         f"L{cx+r_top},{cy} Q{cx},{cy} {cx},{cy+r_top} Z")
    S.add(f'<path d="{d}" fill="#eceee4" stroke="#111" stroke-width="0.4"/>')
    S.rect(cx + 10 / sx, cy + h - 12 / sx, 468 / sx, 12 / sx, 0.3, "#d9c7a7")
    dim_v(S, cx + w + 4, cy, cy + h, "84")
    S.text(cx, cy + h + 7, "Foam on a 12 plywood board, covered in fabric. Top edge about R40; the tear sheet shows R2.5 in (64) at the ends.", 2.2)
    S.text(cx + 180, cy + h + 10.5, "إسفنج على لوح أبلكاش ١٢ مغطى بالقماش. الحافة العلوية حوالي ٤٠.", 2.1, "end", ar=True)
    S.text(cx, cy + h + 16, "Foam grade, layers and fixing to the frame: upholstery workshop to propose.", 2.2)
    S.text(cx + 180, cy + h + 19.5, "نوع الإسفنج وطبقاته وطريقة التثبيت: يقترحها ورشة التنجيد.", 2.1, "end", ar=True)

    head(S, 215, 140, "FABRIC", "القماش", 195)
    rows = [("Supply", "COM (customer's own material) or a chosen objekt fabric", "قماش العميل أو قماش يختاره objekt"),
            ("Reference look", "olive green velvet or hide", "قطيفة أو جلد زيتوني"),
            ("Yardage", "3 yards (2.74 m) per the tear sheet", "٣ ياردة (٢٫٧٤ م) حسب المرجع"),
            ("objekt fabric guide", "none yet; to be decided by Sabry", "لا يوجد دليل أقمشة بعد")]
    y = 148
    for k, v, a in rows:
        S.text(215, y, k, 2.3, weight=700)
        S.text(250, y, v, 2.3)
        S.text(410, y + 3.3, a, 2.2, "end", ar=True)
        y += 9
    S.text(215, y + 4, "Clearance in the tray: 7 each end, 11 each side (1609 x 511 opening).", 2.3)
    S.text(410, y + 7.5, "الخلوص داخل القاعدة: ٧ من كل طرف و١١ من كل جانب.", 2.2, "end", ar=True)
    return S


def sheet5():
    S = Sheet(5, "OBJ-177  BILL OF MATERIALS AND NOTES", "قائمة المواد والملاحظات")
    head(S, 12, 15, "BILL OF MATERIALS (per bench)", "قائمة المواد (لكل مقعد)", 396)
    bom = [("1", "Frame, one moulded piece: GRP shell from a mould taken off the printed pattern (proposal)", "1", "الهيكل قطعة واحدة مصبوبة فايبر جلاس من قالب النموذج المطبوع"),
           ("2", "Seat cushion 1595 x 488 x 84, foam on a board, fabric covered", "1", "المرتبة ١٥٩٥ × ٤٨٨ × ٨٤"),
           ("3", "Cushion base board, plywood 12, 1575 x 468, R71 (proposal)", "1", "لوح القاعدة أبلكاش ١٢"),
           ("4", "Internal reinforcement in the end bars and legs (type by Production)", "as needed", "تقوية داخلية في العوارض والأرجل"),
           ("5", "Floor glides or felt pads under the four feet (type by Production)", "4", "قواعد انزلاق أو لباد تحت الأقدام"),
           ("6", "Pattern only: 8 printed parts, 18 dowels D8 x 44, filler, primer", "1 set", "للنموذج فقط: ٨ أجزاء مطبوعة و١٨ وتد")]
    y = 24
    S.text(15, y, "ITEM", 2.4, weight=700); S.text(30, y, "DESCRIPTION", 2.4, weight=700); S.text(240, y, "QTY", 2.4, weight=700); S.text(405, y, "الوصف", 2.4, "end", 700, ar=True)
    for it, e, q, a in bom:
        y += 7.5
        S.line(12, y - 4.8, 408, y - 4.8, 0.12, "#bbb")
        S.text(15, y, it, 2.5, weight=700); S.text(30, y, e, 2.3); S.text(240, y, q, 2.3); S.text(405, y, a, 2.2, "end", ar=True)
    head(S, 12, 85, "NOTES", "ملاحظات", 396)
    notes = [
        ("Dimensions in mm. Overall 1829 x 686 x 406 and the cushion 1595 x 488 x 84 R81 are from the supplied tear sheet (Riva bench, Carlyle Collective).",
         "الأبعاد بالمليمتر. المقاسات الكلية ومقاسات المرتبة من ورقة المرجع المرفقة."),
        ("Shape and all other sizes are traced from the tear sheet's scaled drawings and photos: approximate, +-10 mm. Production measures and corrects.",
         "الشكل وباقي المقاسات مأخوذة تقريبًا من رسومات وصور المرجع ±١٠ مم. الإنتاج يراجع ويصحح."),
        ("Drawn exact to the reference by default (standing rule). The reference is another maker's product; the design is not ours. Sabry to confirm use.",
         "مرسوم مطابقًا للمرجع حسب القاعدة. المرجع منتج لمصمم آخر وليس تصميمنا؛ يؤكد سبري الاستخدام."),
        ("Process (proposal): 3D print the frame as a pattern, finish it, take a mould, lay up GRP. Wall, layup, reinforcement and mould split by Production.",
         "طريقة التصنيع (مقترح): طباعة النموذج ثم صنع القالب ثم صب الفايبر جلاس. التفاصيل حسب الإنتاج."),
        ("Finish: Chocolate (#4A2A1B, unconfirmed) Duco high gloss, as the reference's deep brown lacquer. Paint system and codes to follow.",
         "التشطيب: شوكولاتة دوكو لامع جدًا كالمرجع. نظام الدهان والأكواد لاحقًا."),
        ("Not engineered. No load, stability or strength check has been made. Production to advise on reinforcement before a prototype.",
         "غير مُصمَّم هندسيًا. لم يتم فحص التحمل أو الثبات. الإنتاج ينصح بالتقوية قبل النموذج الأولي."),
        ("Files: frame one-piece STL, 8 print-part STLs (Z up, mm), DXF outlines of views and sections, cushion board DXF, model and drawing generators.",
         "الملفات: STL للهيكل كاملًا و٨ أجزاء، DXF للمساقط والقطاعات ولوح المرتبة."),
        ("Arabic text is a draft for a technical reader to check before the factory sees it.",
         "النص العربي مسودة يراجعها فني قبل إرسالها للمصنع."),
    ]
    y = 93
    for i, (e, a) in enumerate(notes, 1):
        S.text(12, y, str(i), 2.6, weight=700); S.text(408, y, str(i), 2.6, "end", 700)
        S.text(20, y, e, 2.25)
        S.text(400, y + 3.4, a, 2.15, "end", ar=True)
        y += 10.5
    return S


def write_dxf(V, out):
    doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
    msp = doc.modelspace()
    for lay in ("FRONT", "SIDE", "PLAN", "SEC_A", "SEC_B", "SEC_C", "FOOT", "CUT", "TEXT"):
        doc.layers.add(lay)
    def add(cs, layer, dx=0, dy=0):
        for c in cs:
            msp.add_lwpolyline([(float(u + dx), float(v + dy)) for u, v in c], close=True, dxfattribs={"layer": layer})
    add(V["front"], "FRONT", 0, 0)
    add(V["side"], "SIDE", 1200, 0)
    add(V["plan"], "PLAN", 0, -900)
    msp.add_text("OBJ-177 REV 0 views, mm. Front (x,y), side (z,y) at x+1200, plan (x,z) at y-900. Traced, approximate.",
                 dxfattribs={"layer": "TEXT", "height": 20}).set_placement((-900, 500))
    doc.saveas(out / "OBJ-177_rev0_views.dxf")
    doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
    msp = doc.modelspace()
    for lay in ("SEC_A", "SEC_B", "SEC_C", "FOOT", "TEXT"):
        doc.layers.add(lay)
    add(V["sec_mid"], "SEC_A", 0, 0)
    add(V["sec_end"], "SEC_B", 900, 0)
    add(V["sec_long"], "SEC_C", 0, -700)
    add(V["foot"], "FOOT", 0, -1600)
    add(V["leg300"], "FOOT", 0, -1600)
    msp.add_text("OBJ-177 REV 0 sections, mm. A-A x=0 (z,y); B-B end bar at x+900; C-C z=242 (x,y) at y-700; feet at floor and 240 high (x,z) at y-1600.",
                 dxfattribs={"layer": "TEXT", "height": 20}).set_placement((-900, 600))
    doc.saveas(out / "OBJ-177_rev0_sections.dxf")
    doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
    msp = doc.modelspace(); doc.layers.add("CUT")
    def rrect(l, d, r):
        import math
        pts = []
        for cx, cy, a0 in ((l/2-r, d/2-r, 0), (-l/2+r, d/2-r, 90), (-l/2+r, -d/2+r, 180), (l/2-r, -d/2+r, 270)):
            for k in range(0, 91, 5):
                a = math.radians(a0 + k)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return pts
    msp.add_lwpolyline(rrect(1575, 468, 71), close=True, dxfattribs={"layer": "CUT"})
    doc.saveas(out / "OBJ-177_rev0_cushion-board.dxf")


def main(model_dir, img_dir, out_dir):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    vol, lo, vox = load(model_dir)
    V = views(vol, lo, vox)
    img = {k: Path(img_dir) / f"{k}.png" for k in ("iso_lacquer", "iso_grey", "photo0", "photo1")}
    rep = Path(out_dir) / "OBJ-177_rev0_print-report.json"
    sheets = [sheet1(V, img), sheet2(V), sheet3(V, rep), sheet4(), sheet5()]
    names = ["views", "sections", "print-parts", "cushion", "bom-notes"]
    for S, nm in zip(sheets, names):
        (out / f"OBJ-177_rev0_p{S.n}_{nm}.svg").write_text(S.svg())
    write_dxf(V, out)
    print("ok", [f"p{S.n}" for S in sheets])


if __name__ == "__main__":
    main(*sys.argv[1:4])
