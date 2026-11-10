"""OBJ-177 bench, rev 1: drawing set (A3, EN/AR), DXF profiles and 3D print files.

Run:  python3 make_obj177_rev1.py            (from this folder)
Needs: numpy pillow scikit-image trimesh manifold3d fast-simplification ezdxf pymupdf,
       and node with playwright + chromium for the SVG to PDF step.
Output: venture/drawings/OBJ-177/

Moulded product (print the pattern, then mould): no flat patterns, no cutting layout.
Overall and cushion sizes come from the supplied tear sheet. Everything else is
estimated from the tear sheet line drawings and the photos. Nothing here is engineered.
"""
import base64, io, json, os, subprocess, sys, zipfile
from multiprocessing import Pool
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import obj177_model as M

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "venture", "drawings", "OBJ-177")
PRINT = os.path.join(OUT, "print")
CACHE = os.environ.get("OBJ177_CACHE", os.path.join(HERE, "_cache_obj177"))
PID, REV, DATE = "OBJ-177", "1", "10 Nov 2026"
PRE = f"{PID}_rev{REV}_"
STAMP_EN = "DRAFT, not approved, not engineered"
STAMP_AR = "مسودة، غير معتمدة، بدون مراجعة هندسية"
CHOC, OLIVE = "#4A2A1B", "#5B5A3E"
SEG_X = [-M.L / 2 - 2, -M.L / 4, 0.0, M.L / 4, M.L / 2 + 2]      # 4 print segments along the length
DOWELS = [(-170.0, 291.0), (0.0, 291.0), (170.0, 291.0)]          # (y, z) on each joint face
DOWEL_D, DOWEL_DEPTH = 8.2, 20.0


# ----------------------------------------------------------------- fields
def both_sdf(x, y, z):
    return np.minimum(M.frame_sdf(x, y, z), M.cushion_sdf(x, y, z))


def exploded_sdf(x, y, z, gap=110.0):
    out = np.full(np.shape(x), 1e9)
    for i in range(4):
        s = (i - 1.5) * gap
        a, b = SEG_X[i] + s, SEG_X[i + 1] + s
        d = np.maximum(M.frame_sdf(x - s, y, z), np.maximum(a - x, x - b))
        out = np.minimum(out, d)
    return out


def colour_fn(p):
    f = M.frame_sdf(p[:, 0], p[:, 1], p[:, 2]); c = M.cushion_sdf(p[:, 0], p[:, 1], p[:, 2])
    col = np.where((c < f)[:, None], np.array([[0.50, 0.50, 0.33]]), np.array([[0.42, 0.25, 0.16]]))
    return col


GREY = (0.66, 0.66, 0.66)
VIEWS = {  # name: (field, eye, up, width mm, height mm, centre, px per mm, base)
    "front": ("both", (0, -1, 0), (0, 0, 1), 1900, 460, (0, 0, 210), 1.15, GREY),
    "end": ("both", (1, 0, 0), (0, 0, 1), 760, 460, (0, 0, 210), 1.15, GREY),
    "plan": ("both", (0, 0, 1), (0, 1, 0), 1900, 760, (0, 0, 200), 1.15, GREY),
    "planframe": ("frame", (0, 0, 1), (0, 1, 0), 1900, 760, (0, 0, 200), 1.15, GREY),
    "iso": ("both", (1.0, -1.3, 0.75), (0, 0, 1), 2100, 1100, (0, 0, 190), 0.95, "colour"),
    "corner": ("frame", (0.25, -1, 0.12), (0, 0, 1), 640, 470, (760, -250, 215), 2.2, GREY),
    "under": ("frame", (0.9, -1.1, -0.75), (0, 0, 1), 2100, 1200, (0, 0, 190), 0.75, GREY),
    "exploded": ("exploded", (1.0, -1.3, 0.75), (0, 0, 1), 2400, 1230, (0, 0, 190), 0.8, GREY),
}
FIELDS = {"both": both_sdf, "frame": M.frame_sdf, "exploded": exploded_sdf}


def view_basis(name):
    _, eye, up, w, h, c, ppm, _ = VIEWS[name]
    d = -np.asarray(eye, float); d /= np.linalg.norm(d)
    r = np.cross(d, up); r /= np.linalg.norm(r)
    u = np.cross(r, d)
    return r, u, np.asarray(c, float), w, h


def render_view(name):
    path = os.path.join(CACHE, name + ".png")
    if os.path.exists(path):
        return name
    fld, eye, up, w, h, c, ppm, base = VIEWS[name]
    img, hit, _ = M.render(FIELDS[fld], eye, up, w, h, c, px_per_mm=ppm, base=colour_fn if base == "colour" else base)
    # dark outline around the silhouette
    e = np.zeros_like(hit)
    e[1:-1, 1:-1] = hit[1:-1, 1:-1] & ~(hit[:-2, 1:-1] & hit[2:, 1:-1] & hit[1:-1, :-2] & hit[1:-1, 2:])
    img[e] = (0.1, 0.1, 0.1)
    Image.fromarray((img * 255).astype("uint8")).save(path)
    return name


# ----------------------------------------------------------------- measurements from the model
def probe():
    z = np.linspace(-5, 430, 8701)

    def col(x, y):
        d = M.frame_sdf(np.full_like(z, x), np.full_like(z, y), z)
        i = np.nonzero(d < 0)[0]
        return (z[i.min()], z[i.max()]) if len(i) else (None, None)

    m = {}
    m["tray"] = col(0, 0)[1]
    m["under"] = col(0, 0)[0]
    m["rim"] = max(col(0, yy)[1] for yy in np.arange(252, 276, 0.5))
    m["beam_top"] = col(843, 0)[1]
    m["beam_under"] = col(843, 0)[0]
    m["frame_top"] = max(col(xx, yy)[1] for xx in np.arange(826, 866, 2.0) for yy in np.arange(232, 262, 2.0))
    y = np.linspace(200, 320, 2401)
    d = M.frame_sdf(np.zeros_like(y), y, np.full_like(y, 298.0))
    m["rail_w"] = 2 * y[np.nonzero(d < 0)[0].max()]
    x = np.linspace(760, 930, 3401)
    d = M.frame_sdf(x, np.zeros_like(x), np.full_like(x, 333.0))
    i = np.nonzero(d < 0)[0]
    m["beam_out"] = x[i.max()]
    return m


# ----------------------------------------------------------------- outlines (silhouettes and sections)
def contours(field2d, a0, b0, step):
    from skimage import measure
    out = []
    for c in measure.find_contours(field2d, 0.0):
        pts = np.column_stack([a0 + c[:, 0] * step, b0 + c[:, 1] * step])
        if len(pts) > 8:
            out.append(pts[::2] if len(pts) > 400 else pts)
    return out


def build_outlines(step=2.0):
    bounds = ((-930, 930), (-356, 356), (-10, 420))
    vf, (xs, ys, zs) = M.grid(M.frame_sdf, step, bounds)
    vc, _ = M.grid(M.cushion_sdf, step, bounds)
    ix0 = int(np.argmin(np.abs(xs))); iy0 = int(np.argmin(np.abs(ys))); ixl = int(np.argmin(np.abs(xs - 843)))
    o = {}
    o["plan"] = contours(vf.min(2), xs[0], ys[0], step)
    o["plan_cushion"] = contours(vc.min(2), xs[0], ys[0], step)
    o["front"] = contours(vf.min(1), xs[0], zs[0], step)
    o["front_cushion"] = contours(vc.min(1), xs[0], zs[0], step)
    o["end"] = contours(vf.min(0), ys[0], zs[0], step)
    o["end_cushion"] = contours(vc.min(0), ys[0], zs[0], step)
    o["secA"] = contours(vf[ix0], ys[0], zs[0], step)            # cross-section at mid length (y, z)
    o["secA_cushion"] = contours(vc[ix0], ys[0], zs[0], step)
    o["secB"] = contours(vf[:, iy0], xs[0], zs[0], step)         # long section on the centreline (x, z)
    o["secB_cushion"] = contours(vc[:, iy0], xs[0], zs[0], step)
    o["secC"] = contours(vf[ixl], ys[0], zs[0], step)            # cross-section through the end beam and legs
    return o, vf, (xs, ys, zs)


def write_dxf(name, layers, note):
    import ezdxf
    doc = ezdxf.new("R2010"); doc.units = 4  # mm
    msp = doc.modelspace()
    for lname, (polys, colour) in layers.items():
        doc.layers.add(lname, color=colour)
        for p in polys:
            msp.add_lwpolyline([tuple(map(float, q)) for q in p], close=True, dxfattribs={"layer": lname})
    doc.layers.add("NOTE", color=8)
    msp.add_text(note, dxfattribs={"layer": "NOTE", "height": 8}).set_placement((0, -40))
    path = os.path.join(OUT, PRE + name + ".dxf")
    doc.saveas(path)
    return path


# ----------------------------------------------------------------- meshes and print files
def build_meshes():
    import trimesh, manifold3d as mf, fast_simplification
    bounds = ((-930, 930), (-356, 356), (-10, 420))
    raw = M.mesh_from(M.frame_sdf, 2.5, bounds)
    v, f = fast_simplification.simplify(raw.vertices.astype(np.float32), raw.faces, target_count=260000)
    frame = trimesh.Trimesh(v, f, process=True)

    def to_mf(m):
        return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))

    def to_tm(man):
        me = man.to_mesh()
        return trimesh.Trimesh(np.asarray(me.vert_properties)[:, :3], np.asarray(me.tri_verts), process=True)

    solid = to_mf(frame)
    assert solid.status() == mf.Error.NoError and solid.volume() > 0, solid.status()
    full = to_tm(solid)
    info = {"full": dict(tris=len(full.faces), watertight=bool(full.is_watertight), volume_l=solid.volume() / 1e6,
                         area_m2=solid.surface_area() / 1e6, bbox=(full.bounds[1] - full.bounds[0]).round(1).tolist())}
    full.export(os.path.join(PRINT, PRE + "frame_full.stl"))
    # dowel holes across each joint, then split
    holes = None
    for xj in SEG_X[1:-1]:
        for (yy, zz) in DOWELS:
            c = mf.Manifold.cylinder(2 * DOWEL_DEPTH, DOWEL_D / 2, DOWEL_D / 2, 48).rotate((0, 90, 0)).translate((xj - DOWEL_DEPTH, yy, zz))
            holes = c if holes is None else holes + c
    drilled = solid - holes
    segs = []
    for i in range(4):
        a, b = SEG_X[i], SEG_X[i + 1]
        box = mf.Manifold.cube((b - a, 800, 500)).translate((a, -400, -40))
        part = drilled ^ box
        tm = to_tm(part)
        name = f"print_P{i + 1}"
        tm.export(os.path.join(PRINT, PRE + name + ".stl"))
        segs.append(dict(name=name, tris=len(tm.faces), watertight=bool(tm.is_watertight), volume_l=part.volume() / 1e6,
                         bbox=(tm.bounds[1] - tm.bounds[0]).round(1).tolist(), pieces=len(part.decompose())))
    info["segments"] = segs
    cush = M.mesh_from(M.cushion_sdf, 3.0, ((-810, 810), (-256, 256), (310, 416)))
    v, f = fast_simplification.simplify(cush.vertices.astype(np.float32), cush.faces, target_count=40000)
    cman = to_mf(trimesh.Trimesh(v, f, process=True))
    assert cman.status() == mf.Error.NoError, cman.status()
    cm = to_tm(cman)
    cm.export(os.path.join(PRINT, PRE + "cushion_reference_not_for_print.stl"))
    info["cushion"] = dict(bbox=(cm.bounds[1] - cm.bounds[0]).round(1).tolist(), watertight=bool(cm.is_watertight))
    return info


# ----------------------------------------------------------------- SVG helpers
FONT = "DejaVu Sans, Arial, sans-serif"
INK = "#1b1b1b"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=2.6, anchor="start", bold=False, fill=INK, ar=False):
    extra = ' direction="rtl" unicode-bidi="plaintext"' if ar else ""
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"'
            f'{" font-weight=\"bold\"" if bold else ""}{extra}>{esc(s)}</text>')


def bi(x, y, en, ar, size=2.6, anchor="start", bold=False, fill=INK):
    """English line with the Arabic line directly under it."""
    flip = {"start": "end", "end": "start", "middle": "middle"}[anchor]   # rtl text: 'end' is its left edge
    return txt(x, y, en, size, anchor, bold, fill) + txt(x, y + size * 1.3, ar, size, flip, False, "#444", ar=True)


def line(x1, y1, x2, y2, w=0.18, col=INK, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{col}" stroke-width="{w}"{d}/>'


def hdim(x1, x2, y, label, off=0, size=2.4):
    s = line(x1, y, x2, y, 0.13) + line(x1, y - 1.5, x1, y + 1.5, 0.13) + line(x2, y - 1.5, x2, y + 1.5, 0.13)
    w = len(label) * size * 0.62 + 1.5
    xm = (x1 + x2) / 2 + off
    s += f'<rect x="{xm - w / 2:.2f}" y="{y - size * 0.75:.2f}" width="{w:.2f}" height="{size * 1.4:.2f}" fill="#fff"/>'
    return s + txt(xm, y + size * 0.35, label, size, "middle")


def vdim(x, y1, y2, label, size=2.4, side=1):
    s = line(x, y1, x, y2, 0.13) + line(x - 1.5, y1, x + 1.5, y1, 0.13) + line(x - 1.5, y2, x + 1.5, y2, 0.13)
    return s + txt(x + side * 1.5, (y1 + y2) / 2 + size * 0.35, label, size, "start" if side > 0 else "end")


def balloon(x, y, n, tx, ty):
    return (line(x, y, tx, ty, 0.15) + f'<circle cx="{tx}" cy="{ty}" r="0.5" fill="{INK}"/>'
            f'<circle cx="{x}" cy="{y}" r="3" fill="#fff" stroke="{INK}" stroke-width="0.25"/>' + txt(x, y + 1, n, 2.8, "middle", True))


def img_uri(path, max_px=None, fmt="JPEG"):
    im = Image.open(path).convert("RGB")
    if max_px and max(im.size) > max_px:
        k = max_px / max(im.size); im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, fmt, quality=88)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(b.getvalue()).decode()


def image(x, y, w, h, uri, clip=False):
    par = "xMidYMid slice" if clip else "xMidYMid meet"
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="{par}" href="{uri}"/>'


def poly_path(polys, sx, sy, s, flipy=True, fill="none", stroke=INK, w=0.3, x0=0, y0=0, clipx=None):
    """World (a, b) to sheet: X = sx + (a - x0) * s ; Y = sy - (b - y0) * s."""
    d = ""
    for p in polys:
        if clipx:
            p = np.column_stack([np.clip(p[:, 0], clipx[0], clipx[1]), p[:, 1]])
        X = sx + (p[:, 0] - x0) * s; Y = sy - (p[:, 1] - y0) * s
        d += "M" + " L".join(f"{a:.2f},{b:.2f}" for a, b in zip(X, Y)) + " Z "
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" fill-rule="evenodd" stroke-linejoin="round"/>'


def table(x, y, colw, rows, rh=6.4, size=2.3, head=True):
    s = ""
    W = sum(colw)
    for i, r in enumerate(rows):
        yy = y + i * rh
        if head and i == 0:
            s += f'<rect x="{x}" y="{yy}" width="{W}" height="{rh}" fill="#ececec"/>'
        s += line(x, yy, x + W, yy, 0.13)
        cx = x
        for j, cell in enumerate(r):
            if isinstance(cell, tuple) and cell[0] == "swatch":
                s += f'<rect x="{cx + 1.2}" y="{yy + 1.2}" width="{colw[j] - 2.4}" height="{rh - 2.4}" fill="{cell[1]}" stroke="#555" stroke-width="0.1"/>'
            elif isinstance(cell, tuple):
                s += txt(cx + 1.2, yy + rh * 0.42, cell[0], size, bold=(head and i == 0))
                s += txt(cx + 1.2, yy + rh * 0.86, cell[1], size * 0.95, "end", fill="#444", ar=True)
            else:
                s += txt(cx + 1.2, yy + rh * 0.62, cell, size, bold=(head and i == 0))
            cx += colw[j]
    yy = y + len(rows) * rh
    s += line(x, yy, x + W, yy, 0.13)
    cx = x
    for wv in colw + [0]:
        s += line(cx, y, cx, yy, 0.13); cx += wv
    return s


def sheet(n, total, title_en, title_ar, scale, body, logo):
    s = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 297" width="420mm" height="297mm" font-family="{FONT}">'
    s += '<rect width="420" height="297" fill="#fff"/>'
    s += f'<rect x="7" y="7" width="406" height="283" fill="none" stroke="{INK}" stroke-width="0.35"/>'
    s += image(11, 10.5, 22, 14, logo)
    s += txt(38, 17, f"{PID}  Bench", 5, bold=True) + txt(38, 22.5, title_en, 3.2, fill="#444")
    s += txt(409, 17, f"مقعد  {PID}", 5, "start", True, ar=True) + txt(409, 22.5, title_ar, 3.2, "start", False, "#444", ar=True)
    s += line(7, 27, 413, 27, 0.25)
    s += body
    # status stamp and title block
    bx, by, bw, bh = 263, 253, 150, 37
    s += f'<rect x="{bx}" y="{by - 11}" width="{bw}" height="11" fill="#fff4f2" stroke="#b3261e" stroke-width="0.4"/>'
    s += txt(bx + 3, by - 6.3, STAMP_EN, 2.9, bold=True, fill="#b3261e") + txt(bx + bw - 3, by - 2.2, STAMP_AR, 2.7, "start", False, "#b3261e", ar=True)
    s += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#fff" stroke="{INK}" stroke-width="0.35"/>'
    cells = [("PRODUCT / المنتج", f"{PID} Bench (name to follow)", 0, 0, 75), ("SIZE / المقاس", "A3", 75, 0, 25),
             ("SCALE / المقياس", scale, 100, 0, 25), ("UNITS / الوحدات", "mm", 125, 0, 25),
             ("MATERIAL / الخامة", "Moulded frame from a 3D printed pattern (proposed)", 0, 12.3, 75),
             ("DATE / التاريخ", DATE, 75, 12.3, 25), ("SHEET / لوحة", f"{n} / {total}", 100, 12.3, 25), ("REV / مراجعة", REV, 125, 12.3, 25),
             ("FINISH / التشطيب", "Duco · Chocolate · Gloss (to be confirmed) + upholstered cushion", 0, 24.6, 100),
             ("DRAWN / رسم", "objekt", 100, 24.6, 50)]
    for lab, val, cx, cy, cw in cells:
        s += f'<rect x="{bx + cx}" y="{by + cy}" width="{cw}" height="12.3" fill="none" stroke="{INK}" stroke-width="0.15"/>'
        s += txt(bx + cx + 1.3, by + cy + 3.6, lab, 1.9, fill="#666") + txt(bx + cx + 1.3, by + cy + 9.2, val, 2.5 if len(val) < 30 else 2.05, bold=True)
    return s + "</svg>"


# ----------------------------------------------------------------- sheets
def placed(name, x, y, w):
    """Place a rendered view; returns svg and a world->sheet projector."""
    r, u, c, vw, vh = view_basis(name)
    k = w / vw
    h = vh * k
    uri = img_uri(os.path.join(CACHE, name + ".png"), 2400)

    def proj(p):
        q = np.asarray(p, float) - c
        return x + w / 2 + (q @ r) * k, y + h / 2 - (q @ u) * k
    return image(x, y, w, h, uri), proj, k, h


def build_sheets(m, info, logo, ref1, ref2):
    L, D, H = M.L, M.D, M.H
    sheets = []
    # ---------------- sheet 1: views
    b = ""
    s1 = 0.1
    b += bi(20, 34, "FRONT ELEVATION  1:10", "المسقط الأمامي", 2.8, bold=True)
    im, pf, k, h = placed("front", 20, 40, 190)
    b += im
    xa, _ = pf((-L / 2, 0, 0)); xb, yb = pf((L / 2, 0, 0)); _, yt = pf((0, 0, H))
    b += hdim(xa, xb, yb + 6, f"{L:.0f}  (72 in)")
    b += vdim(xb + 5, yt, yb, f"{H:.0f}")
    _, yu = pf((0, 0, m["under"]))
    b += vdim(115, yu, yb, f"{m['under']:.0f} clear, est.", 2.2)
    bx, by2 = pf((300, 0, 298)); b += balloon(bx + 12, by2 - 14, "1", bx, by2)
    cxp, cyp = pf((-300, 0, 380)); b += balloon(cxp - 10, cyp - 10, "2", cxp, cyp)
    b += bi(20, 102, "PLAN  1:10", "المسقط الأفقي", 2.8, bold=True)
    im, pp, k, h = placed("plan", 20, 106, 190)
    b += im
    xa, ya = pp((L / 2, -D / 2, 0)); _, yb_ = pp((L / 2, D / 2, 0))
    b += vdim(xa + 5, yb_, ya, f"{D:.0f}  (27 in)")
    ca, cy0 = pp((-M.CL / 2, 0, 0)); cb, _ = pp((M.CL / 2, 0, 0))
    b += hdim(ca, cb, cy0 + 8, f"cushion {M.CL:.0f}")
    ccx, cya = pp((250, -M.CD / 2, 0)); _, cyb = pp((250, M.CD / 2, 0))
    b += vdim(ccx, cyb, cya, f"{M.CD:.0f}", 2.2)
    b += bi(232, 34, "END ELEVATION  1:10", "المسقط الجانبي", 2.8, bold=True)
    im, pe, k, h = placed("end", 232, 40, 76)
    b += im
    ea, eyb = pe((0, -D / 2, 0)); eb, _ = pe((0, D / 2, 0)); _, eyt = pe((0, 0, H))
    b += hdim(ea, eb, eyb + 6, f"{D:.0f}")
    b += vdim(eb + 4, eyt, eyb, f"{H:.0f}  (16 in)")
    ra, ry = pe((0, -m["rail_w"] / 2, 300)); rb, _ = pe((0, m["rail_w"] / 2, 300))
    b += bi(326, 50, "Overall height is taken to the", "الارتفاع الكلي حتى أعلى الوسادة", 2.2)
    b += txt(326, 56.5, f"top of the cushion. Frame top {m['frame_top']:.0f} est.", 2.2)
    b += bi(232, 102, "VIEW (colour as the reference: gloss brown, olive green seat)", "منظور (اللون كما في المرجع: بني لامع ووسادة زيتية)", 2.6, bold=True)
    im, pi, k, h = placed("iso", 226, 108, 184)
    b += im
    # reference images
    b += bi(20, 190, "REFERENCE (supplied tear sheet images)", "المرجع (صور من ورقة المواصفات المرسلة)", 2.6, bold=True)
    b += image(20, 196, 46, 46, ref1, True) + image(69, 196, 46, 46, ref2, True)
    b += txt(20, 246.5, "Source: Riva bench tear sheet, Carlyle Collective. Reference only.", 2.0, fill="#555")
    # colourways
    b += bi(124, 190, "COLOURWAY", "الألوان", 2.6, bold=True)
    rows = [[("Item", "البند"), "", ("Colour", "اللون"), ("Finish", "التشطيب")],
            [("1 Frame", "الهيكل"), ("swatch", CHOC), ("Chocolate #4A2A1B", "بني شوكولاتة"), ("Duco · Gloss, to be confirmed", "دوكو لامع، يؤكَّد لاحقاً")],
            [("2 Cushion", "الوسادة"), ("swatch", OLIVE), ("Olive green, as reference", "أخضر زيتي كما في المرجع"), ("Fabric to be chosen by Sabry", "القماش يختاره صبري")]]
    b += table(124, 196, [24, 10, 46, 52], rows, 8.2)
    b += txt(124, 226, "Hex is a screen approximation. Paint code (CAPCI) to follow. Olive is not an objekt paint colour: fabric only.", 2.0, fill="#555")
    b += bi(20, 256, "Sizes: overall and cushion sizes are from the tear sheet. All other sizes are estimated from the", "المقاسات الكلية ومقاسات الوسادة من ورقة المواصفات. باقي المقاسات تقديرية من الرسومات والصور.", 2.3)
    b += txt(20, 265.5, "tear sheet line drawings and photos, and are for Production to confirm on the pattern.", 2.3)
    b += bi(20, 272, "1 Frame (moulded)   2 Seat cushion (upholstered, loose in the tray)", "١ الهيكل (مصبوب)   ٢ وسادة المقعد (منجّدة، توضع في الحوض)", 2.3)
    sheets.append(("views", sheet(1, 4, "Views and overall sizes", "المساقط والمقاسات الكلية", "1:10", b, logo)))

    # ---------------- sheet 2: frame details
    o = OUTL
    b = ""
    sc = 0.25
    b += bi(20, 34, "SECTION A-A  mid length  1:4", "قطاع أ-أ عند منتصف الطول", 2.8, bold=True)
    X0, Y0 = 95, 89                      # sheet position of world (y=0, z=250)
    b += poly_path(o["secA"], X0, Y0, sc, fill="#d9d9d9", y0=250)
    b += poly_path(o["secA_cushion"], X0, Y0, sc, fill="none", stroke="#777", w=0.2, y0=250)
    zy = lambda z: Y0 - (z - 250) * sc
    b += hdim(X0 - m["rail_w"] / 2 * sc, X0 + m["rail_w"] / 2 * sc, zy(250) + 3, f"{m['rail_w']:.0f} est.")
    rw = (M.CD / 2 + M.REC_CLEAR) * sc
    b += hdim(X0 - rw, X0 + rw, zy(432), f"tray {M.CD + 2 * M.REC_CLEAR:.0f} (cushion {M.CD:.0f} + 6 each side)", size=2.2)
    xr = X0 + m["rail_w"] / 2 * sc + 5
    b += vdim(xr, zy(m["rim"]), zy(m["under"]), f"{m['rim'] - m['under']:.0f} est.", 2.2)
    b += txt(X0, zy(m["tray"]) + 4.2, f"tray floor {m['tray']:.0f} above the floor · underside {m['under']:.0f} · lip {m['rim']:.0f}", 2.1, "middle")
    b += bi(X0 - 20, zy(380), "cushion (outline)", "الوسادة", 2.0, fill="#666")

    b += bi(20, 100, "SECTION B-B  centreline, one end  1:4", "قطاع ب-ب على المحور، أحد الطرفين", 2.8, bold=True)
    X1, Y1 = 22, 212                     # world (x=600, z=0)
    clip = (600, 940)
    b += poly_path(o["secB"], X1, Y1, sc, fill="#d9d9d9", x0=600, clipx=clip)
    b += poly_path(o["secB_cushion"], X1, Y1, sc, stroke="#777", w=0.2, x0=600, clipx=clip)
    b += line(X1, Y1, X1 + 90, Y1, 0.15, "#555")
    wx = lambda x: X1 + (x - 600) * sc
    wz = lambda z: Y1 - z * sc
    b += vdim(wx(m["beam_out"]) + 5, wz(m["beam_top"]), wz(0), f"{m['beam_top']:.0f} est.", 2.2)
    b += vdim(wx(843), wz(m["beam_under"]), wz(0), f"{m['beam_under']:.0f}", 2.2, -1)
    b += hdim(wx(600), wx(L / 2), wz(0) + 5, f"to end of bench: feet at {L / 2:.0f} from centre", size=2.1)
    b += bi(wx(630), wz(200), "End beam: tube about", "عارضة الطرف: أنبوب قطره", 2.1)
    b += txt(wx(630), wz(200) + 6.2, f"Ø{2 * M.BEAM_R:.0f}, est.", 2.1)

    s5 = 0.2
    b += bi(118, 100, "SECTION C-C  through end beam and legs  1:5", "قطاع ج-ج عبر عارضة الطرف والأرجل", 2.8, bold=True)
    X2, Y2 = 186, 200                    # world y=0 at X2
    b += poly_path(o["secC"], X2, Y2, s5, fill="#d9d9d9")
    b += line(X2 - 72, Y2, X2 + 72, Y2, 0.15, "#555")
    b += line(X2, Y2 + 2, X2, Y2 - 86, 0.12, "#777", "4 1 1 1")
    b += hdim(X2 - M.FY * s5, X2 + M.FY * s5, Y2 + 5, f"leg centres {2 * M.FY:.0f} est.", size=2.2)
    b += hdim(X2 - D / 2 * s5, X2 + D / 2 * s5, Y2 + 11, f"{D:.0f}", size=2.2)
    b += txt(X2 + M.FY * s5, Y2 - 3, f"foot Ø{2 * M.FOOT_R:.0f} est.", 2.0, "middle")
    b += txt(X2, Y2 + 17, f"Along the length: leg centres {2 * M.FX:.0f} est.", 2.1, "middle")

    b += bi(262, 34, "CORNER DETAIL (model view)", "تفصيلة الركن (من النموذج)", 2.8, bold=True)
    im, pc, k, h = placed("corner", 262, 40, 147)
    b += im
    calls = [((500, -281, 318), "Groove between rail tube and lip", "مجرى بين القضيب والحافة"),
             ((560, -265, 333), "Lip holds the cushion", "حافة تثبت الوسادة"),
             ((720, -262, 300), "Neck: the rail swells and rises", "العنق: القضيب يتسع ويرتفع"),
             ((M.TOPX - 25, -M.TOPY - 50, 345), "Hood: the tube drapes over the cone", "الغطاء: الأنبوب ينسدل فوق المخروط"),
             ((M.FX + 2, -(M.FY + 52), 262), "Arch window: the cone shows", "فتحة قوسية يظهر منها المخروط"),
             ((M.FX - 30, -(M.FY + 80), 60), "Cone leg, foot Ø185 est.", "رجل مخروطية")]
    for i, (wp, en, ar) in enumerate(calls):
        px, py = pc(wp)
        tx, ty = 266, 96 + i * 9.4
        ex = tx + len(en) * 1.22 + 1.5
        b += line(ex, ty - 0.8, px, py, 0.15) + f'<circle cx="{px:.2f}" cy="{py:.2f}" r="0.55" fill="{INK}"/>'
        b += bi(tx, ty, en, ar, 2.2)
    b += bi(262, 158, "UNDERSIDE (model view)", "المنظر السفلي (من النموذج)", 2.8, bold=True)
    im, pu, k, h = placed("under", 262, 163, 108)
    b += im
    rows = [[("DATA (from the model)", "بيانات من النموذج"), ""],
            [("Frame volume, solid", "حجم الهيكل مصمت"), f"{info['full']['volume_l']:.1f} L"],
            [("Frame surface area", "مساحة سطح الهيكل"), f"{info['full']['area_m2']:.2f} m²"],
            [("Frame top above floor", "أعلى الهيكل"), f"{m['frame_top']:.0f} mm"],
            [("Tray floor above floor", "أرضية الحوض"), f"{m['tray']:.0f} mm"]]
    b += table(20, 228, [70, 32], rows, 6.6, 2.1)
    b += bi(130, 234, "All sizes on this sheet are estimated from the reference and", "كل مقاسات هذه اللوحة تقديرية من المرجع وتُراجع على النموذج قبل عمل القالب.", 2.3)
    b += txt(130, 243.5, "are to be checked on the pattern before a mould is made.", 2.3)
    b += txt(130, 249.5, "Blend radii and crease depth are approximate; see the STL for the surface.", 2.3)
    sheets.append(("frame-details", sheet(2, 4, "Frame sections and details", "قطاعات وتفاصيل الهيكل", "1:4", b, logo)))

    # ---------------- sheet 3: pattern, print and mould
    b = ""
    b += bi(20, 34, "PRINT SPLIT (plan, frame only)  1:10", "تقسيم الطباعة (مسقط أفقي للهيكل فقط)", 2.8, bold=True)
    im, pp, k, h = placed("planframe", 20, 40, 190)
    b += im
    for i, xj in enumerate(SEG_X[1:-1]):
        xs_, ya = pp((xj, -D / 2 - 25, 0)); _, yb_ = pp((xj, D / 2 + 25, 0))
        b += line(xs_, ya, xs_, yb_, 0.35, "#b3261e", "3 1.2")
        for (yy, zz) in DOWELS:
            dx_, dy_ = pp((xj, yy, 0)); b += f'<circle cx="{dx_:.2f}" cy="{dy_:.2f}" r="0.9" fill="#b3261e"/>'
    for i in range(4):
        a_ = max(SEG_X[i], -L / 2); b_ = min(SEG_X[i + 1], L / 2)
        xm, ym = pp(((a_ + b_) / 2, 0, 0))
        b += txt(xm, ym + 1.5, f"P{i + 1}", 6, "middle", True, "#b3261e")
        xa, yd = pp((a_, -D / 2, 0)); xb, _ = pp((b_, -D / 2, 0))
        b += hdim(xa, xb, yd + 6, f"{b_ - a_:.1f}", size=2.2)
    b += bi(20, 126, "Red dots: Ø8 dowel holes, 20 deep in each face, 3 per joint, to line the pieces up.", "النقاط الحمراء: ثقوب خوابير قطر ٨ وعمق ٢٠ في كل وجه، ٣ لكل وصلة، لضبط تطابق القطع.", 2.3)
    b += bi(20, 140, "PIECES APART (model view)", "القطع منفصلة (من النموذج)", 2.8, bold=True)
    im, px_, k, h = placed("exploded", 20, 146, 188)
    b += im

    b += bi(226, 34, "JOINT FACE (section A-A)  1:4", "وجه الوصلة (قطاع أ-أ)", 2.8, bold=True)
    X0, Y0 = 318, 74
    b += poly_path(o["secA"], X0, Y0, sc, fill="#e6e6e6", y0=250)
    for (yy, zz) in DOWELS:
        cx_, cy_ = X0 + yy * sc, Y0 - (zz - 250) * sc
        b += f'<circle cx="{cx_:.2f}" cy="{cy_:.2f}" r="{DOWEL_D / 2 * sc:.2f}" fill="#fff" stroke="#b3261e" stroke-width="0.3"/>'
    b += hdim(X0 - 170 * sc, X0, Y0 + 6, "170", size=2.1) + hdim(X0, X0 + 170 * sc, Y0 + 6, "170", size=2.1)
    b += txt(X0, Y0 + 13, f"Dowel holes Ø{DOWEL_D} x {DOWEL_DEPTH:.0f} deep, centres {DOWELS[0][1]:.0f} above the floor", 2.1, "middle")

    b += bi(226, 96, "3D PRINT FILES (STL, mm, 1:1, solid)", "ملفات الطباعة ثلاثية الأبعاد", 2.8, bold=True)
    rows = [[("File", "الملف"), ("Size L x D x H", "المقاس"), ("Volume", "الحجم")]]
    rows.append([PRE + "frame_full.stl", " x ".join(f"{v:.0f}" for v in info["full"]["bbox"]), f"{info['full']['volume_l']:.1f} L"])
    for sg in info["segments"]:
        rows.append([PRE + sg["name"] + ".stl", " x ".join(f"{v:.0f}" for v in sg["bbox"]), f"{sg['volume_l']:.1f} L"])
    rows.append([PRE + "cushion_reference…stl", " x ".join(f"{v:.0f}" for v in info["cushion"]["bbox"]), "not printed"])
    b += table(226, 102, [96, 56, 30], rows, 5.6, 2.1)
    y0 = 148
    b += bi(226, y0, "PROPOSED SEQUENCE (Production decides)", "تسلسل مقترح (القرار للإنتاج)", 2.8, bold=True)
    steps = [("Print P1 to P4, or the full frame in one if the printer allows.", "طباعة القطع من P1 إلى P4، أو الهيكل كاملاً إن سمحت الطابعة."),
             ("Dowel and bond the pieces on a flat table. Check length 1829 and the diagonals.", "تجميع القطع بالخوابير واللصق على سطح مستوٍ ومراجعة الطول والأقطار."),
             ("Fill the joints, prime and sand the pattern to a gloss-ready surface.", "معجنة الوصلات ثم برايمر وصنفرة حتى سطح جاهز للّمعة."),
             ("Make the mould from the pattern. Split lines and release are Production's call.", "عمل القالب من النموذج. خطوط الفصل وطريقة الفك يحددها الإنتاج."),
             ("Mould the frame. Material, wall build-up and any inner core are Production's.", "صب الهيكل. الخامة وسماكة الجدار وأي حشو داخلي يحددها الإنتاج."),
             ("Trim, prepare and paint: Duco, Chocolate, gloss (to be confirmed).", "تشذيب وتجهيز ودهان: دوكو، بني شوكولاتة، لامع (يؤكَّد)."),
             ("Make the cushion to 1595 x 488 x 84 and seat it in the tray.", "تنجيد الوسادة بمقاس 1595 × 488 × 84 ووضعها في الحوض.")]
    for i, (en, ar) in enumerate(steps):
        yy = y0 + 9 + i * 10.4
        b += txt(226, yy, f"{i + 1}.", 2.4, bold=True) + bi(232, yy, en, ar, 2.3)
    b += bi(20, 256, "The pattern is drawn at finished size. No allowance is included for shrinkage, filler or paint build.", "النموذج مرسوم بالمقاس النهائي دون أي سماح للانكماش أو المعجون أو سماكة الدهان.", 2.3)
    b += bi(20, 268, "The split assumes a build length of about 460 mm. Tell us the printer's build size and we re-split.", "التقسيم يفترض طول طباعة حوالي ٤٦٠ مم. أرسلوا مقاس الطابعة لنعيد التقسيم.", 2.3)
    sheets.append(("pattern-print", sheet(3, 4, "Pattern, 3D print split and proposed sequence", "النموذج وتقسيم الطباعة والتسلسل المقترح", "1:10", b, logo)))

    # ---------------- sheet 4: BOM and notes
    b = ""
    b += bi(20, 34, "BILL OF MATERIALS", "قائمة المكونات", 2.8, bold=True)
    rows = [[("Item", "بند"), ("Part", "الجزء"), ("Qty", "العدد"), ("Material / process", "الخامة / الطريقة"), ("Size", "المقاس"), ("Finish", "التشطيب")],
            ["1", ("Frame", "الهيكل"), "1", ("Moulded in one piece from a 3D printed pattern (proposed)", "يُصب قطعة واحدة من نموذج مطبوع (مقترح)"),
             f"{M.L:.0f} x {M.D:.0f} x {m['frame_top']:.0f} est.", ("Duco · Chocolate · Gloss, to be confirmed", "دوكو، بني شوكولاتة، لامع، يؤكَّد")],
            ["2", ("Seat cushion", "وسادة المقعد"), "1", ("Upholstered foam pad; build by Production's upholstery", "وسادة إسفنج منجّدة؛ التنفيذ لقسم التنجيد"),
             f"{M.CL:.0f} x {M.CD:.0f} x {M.CH:.0f}", ("Fabric to be chosen. Tear sheet states 3 yards", "القماش يُحدَّد. المرجع يذكر ٣ ياردات")],
            ["3", ("Pattern (tooling)", "النموذج (عدة)"), "1 set", ("3D printed, 4 pieces P1 to P4, doweled and bonded", "مطبوع، ٤ قطع، خوابير ولصق"),
             "as STL files", ("Filled, primed, sanded", "معجون وبرايمر وصنفرة")],
            ["4", ("Dowels (tooling)", "خوابير (عدة)"), "9", ("Ø8 x 40 pins for the pattern joints", "خوابير قطر ٨ × ٤٠ لوصلات النموذج"), "Ø8 x 40", "-"],
            ["5", ("Floor glides", "قواعد أرضية"), "4", ("Not shown on the reference. Production to propose", "غير ظاهرة في المرجع. يقترحها الإنتاج"), "to follow", "-"]]
    b += table(20, 40, [12, 40, 14, 130, 62, 132], rows, 8.6, 2.2)
    notes = [
        ("Reference: Riva bench, Carlyle Collective (tear sheet supplied by Sabry). Drawn exact to the reference by Sabry's standing rule.", "المرجع: مقعد ريفا من كارلايل كوليكتيف (ورقة مواصفات أرسلها صبري). مرسوم مطابقاً للمرجع."),
        ("Overall 1829 x 686 x 406 and cushion 1595 x 488 x 84 are from the tear sheet (72 x 27 x 16 in; 62.8 x 19.2 x 3.3 in).", "المقاسات الكلية ومقاسات الوسادة مأخوذة من ورقة المواصفات."),
        ("All other sizes and every curve are estimated from the tear sheet line drawings and photos. The STL is the shape; check it against the photos.", "باقي المقاسات وكل الانحناءات تقديرية من الرسومات والصور. ملف STL هو المرجع للشكل."),
        ("Height 406 is taken to the top of the cushion. The tear sheet does not say which point it measures.", "الارتفاع ٤٠٦ حتى أعلى الوسادة. ورقة المواصفات لا تحدد نقطة القياس."),
        ("Colours as the first set of reference photos: gloss brown frame, olive green seat. The bronze photos were used for shape only.", "الألوان كما في صور المرجع الأولى: هيكل بني لامع ووسادة زيتية. صور البرونز استُخدمت للشكل فقط."),
        ("The arch window and the crease under the hood are undercuts for a one-piece mould. Production decides the mould split.", "الفتحة القوسية والثنية تحت الغطاء مناطق تعشيق في القالب. الإنتاج يحدد تقسيم القالب."),
        ("We propose; Production decides material, wall build-up, tolerances, mould, fixings, glides and finish details.", "نحن نقترح، والإنتاج يحدد الخامة والسماكات والتفاوتات والقالب والتثبيت والتشطيب."),
        ("No structural claim is made. Seat load, leg strength and the long span have not been checked.", "لا توجد أي ادعاءات إنشائية. لم تُراجع الأحمال أو قوة الأرجل أو البحر الطويل."),
        ("Paint system and gloss level to be confirmed; CAPCI code to follow. No costs or prices are on this drawing.", "نظام الدهان ودرجة اللمعة يؤكَّدان لاحقاً. لا توجد أسعار أو تكاليف في هذه اللوحات."),
        ("Arabic wording is a draft and needs a technical reader before it goes to the factory.", "الصياغة العربية مسودة وتحتاج مراجعة فنية قبل الإرسال للمصنع."),
    ]
    b += bi(20, 108, "NOTES", "ملاحظات", 2.8, bold=True)
    for i, (en, ar) in enumerate(notes):
        yy = 117 + i * 12.2
        b += txt(20, yy, f"{i + 1}.", 2.4, bold=True) + txt(27, yy, en, 2.4)
        b += txt(409, yy + 4.6, ar, 2.4, "start", False, "#444", ar=True)
    sheets.append(("bom-notes", sheet(4, 4, "Bill of materials and notes", "قائمة المكونات والملاحظات", "-", b, logo)))
    return sheets


def main():
    global OUTL
    os.makedirs(OUT, exist_ok=True); os.makedirs(PRINT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
    with Pool(4) as p:
        p.map(render_view, list(VIEWS), chunksize=1)
    ipath = os.path.join(CACHE, "info.json")
    if os.path.exists(ipath) and not os.environ.get("OBJ177_REMESH"):
        info = json.load(open(ipath))
    else:
        info = build_meshes(); json.dump(info, open(ipath, "w"), indent=1)
    m = probe()
    OUTL, vf, axes = build_outlines()
    note = f"{PID} rev {REV} {DATE}. DRAFT, not engineered. mm. Sizes estimated from the reference except overall and cushion sizes."
    write_dxf("plan_outline", {"PROFILE": (OUTL["plan"], 7), "CUSHION": (OUTL["plan_cushion"], 3)}, note)
    write_dxf("front_elevation", {"PROFILE": (OUTL["front"], 7), "CUSHION": (OUTL["front_cushion"], 3)}, note)
    write_dxf("end_elevation", {"PROFILE": (OUTL["end"], 7), "CUSHION": (OUTL["end_cushion"], 3)}, note)
    write_dxf("section_AA_mid", {"PROFILE": (OUTL["secA"], 7), "CUSHION": (OUTL["secA_cushion"], 3)}, note)
    write_dxf("section_BB_centreline", {"PROFILE": (OUTL["secB"], 7), "CUSHION": (OUTL["secB_cushion"], 3)}, note)
    write_dxf("section_CC_legs", {"PROFILE": (OUTL["secC"], 7)}, note)
    logo = "data:image/svg+xml;base64," + base64.b64encode(open(os.path.join(ROOT, "brand", "objekt-logo.svg"), "rb").read()).decode()
    ref1 = img_uri(os.path.join(ROOT, "images", "OBJ-177.jpg"), 700)
    ref2 = img_uri(os.path.join(OUT, "reference", "OBJ-177_reference_low-angle.jpg"), 700)
    sheets = build_sheets(m, info, logo, ref1, ref2)
    svgs = []
    for i, (name, svg) in enumerate(sheets):
        pth = os.path.join(OUT, f"{PRE}sheet{i + 1}_{name}.svg")
        open(pth, "w", encoding="utf-8").write(svg); svgs.append(pth)
    js = os.path.join(CACHE, "topdf.js")
    open(js, "w").write("""
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage();
for(const f of process.argv.slice(2)){const svg=fs.readFileSync(f,'utf8');
await p.setContent('<html><body style="margin:0">'+svg+'</body></html>');
await p.pdf({path:f.replace('.svg','.pdf'),width:'420mm',height:'297mm',printBackground:true,pageRanges:'1'});}
await b.close();})();""")
    subprocess.run(["node", js] + svgs, check=True, env={**os.environ, "NODE_PATH": subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()})
    import fitz
    doc = fitz.open()
    for s in svgs:
        pp = s.replace(".svg", ".pdf"); d = fitz.open(pp); doc.insert_pdf(d); d.close(); os.remove(pp)
    doc.save(os.path.join(OUT, PRE + "drawings.pdf"), deflate=True, garbage=4); doc.close()
    with zipfile.ZipFile(os.path.join(OUT, PRE + "print-files.zip"), "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for fn in sorted(os.listdir(PRINT)):
            if fn.endswith(".stl"):
                z.write(os.path.join(PRINT, fn), fn)
    print(json.dumps({"measure": {k: round(float(v), 1) for k, v in m.items()}, "info": info}, indent=1))


if __name__ == "__main__":
    main()
