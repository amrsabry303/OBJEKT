"""OBJ-177 bench, rev 1: geometry (signed distance field), mesh and ray-traced views.

Units mm. x = length, y = depth, z = height, origin at floor centre.
Sizes: overall and cushion sizes are from the supplied tear sheet (Riva bench);
everything else is estimated from the tear sheet line drawings and the photos.
Needs: numpy, scikit-image, trimesh, manifold3d, fast-simplification.
"""
import numpy as np

# ---- sizes from the tear sheet (inches converted) ----
L, D, H = 1828.8, 685.8, 406.4            # overall
CL, CD, CH = 1595.0, 488.0, 84.0          # cushion (62.8 x 19.2 x 3.3 in)
C_RC, C_RE = 81.0, 64.0                   # cushion plan corner R3.2 in, end edge R2.5 in

# ---- estimated from the drawings and photos ----
FOOT_R = 92.5                             # foot radius at floor
FX, FY = L / 2 - FOOT_R - 1.0, D / 2 - FOOT_R + 0.2   # foot centre (blend adds about 1 mm)
TOPX, TOPY, TOPZ, TOP_R = 846.0, 246.0, 334.0, 44.0   # leg cone top sphere
HOOD_T = 17.0                             # hood thickness over the cone
SLAB_HW, SLAB_Z0, SLAB_Z1, SLAB_R = 281.0, 262.0, 334.0, 30.0
TRAY_Z = H - CH                           # cushion seat level, 322.4
REC_CLEAR = 6.0
BEAM_X, BEAM_Z, BEAM_R = 843.0, 333.0, 57.0


def smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def smax(a, b, k):
    return -smin(-a, -b, k)


def round_cone(x, y, z, a, b, r1, r2):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ba = b - a
    l2 = ba @ ba
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    px, py, pz = x - a[0], y - a[1], z - a[2]
    yy = px * ba[0] + py * ba[1] + pz * ba[2]
    zz = yy - l2
    x2 = (px * l2 - ba[0] * yy) ** 2 + (py * l2 - ba[1] * yy) ** 2 + (pz * l2 - ba[2] * yy) ** 2
    y2 = yy * yy * l2
    z2 = zz * zz * l2
    k = np.sign(rr) * rr * rr * x2
    d1 = np.sqrt(x2 + z2) * il2 - r2
    d2 = np.sqrt(x2 + y2) * il2 - r1
    d3 = (np.sqrt(x2 * a2 * il2) + yy * rr) * il2 - r1
    return np.where(np.sign(zz) * a2 * z2 > k, d1, np.where(np.sign(yy) * a2 * y2 < k, d2, d3))


def rbox(x, y, z, c, h, r):
    qx = np.abs(x - c[0]) - (h[0] - r)
    qy = np.abs(y - c[1]) - (h[1] - r)
    qz = np.abs(z - c[2]) - (h[2] - r)
    out = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2 + np.maximum(qz, 0) ** 2)
    return out + np.minimum(np.maximum(qx, np.maximum(qy, qz)), 0) - r


def rrect2(x, y, hx, hy, r):
    qx = np.abs(x) - (hx - r); qy = np.abs(y) - (hy - r)
    return np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0) - r


def frame_sdf(x, y, z):
    """Frame (the 'bone'): tray, rails, end beams, hoods, cone legs. Symmetric in x and y."""
    ax, ay = np.abs(x), np.abs(y)
    A = (FX, FY, 0.0); B = (TOPX, TOPY, TOPZ)
    cone = round_cone(ax, ay, z, A, B, FOOT_R, TOP_R)
    # hood: the tube draped over the top of the cone. Its skin fades into the cone lower down,
    # and an arch window on the long-side face shows the cone (the crease seen in the photos).
    fade = np.clip((z - 130.0) / 150.0, 0, 1); fade = fade * fade * (3 - 2 * fade)
    hood = round_cone(ax, ay, z, A, B, FOOT_R + HOOD_T, TOP_R + HOOD_T) + HOOD_T * (1 - fade)
    t = np.clip(z / TOPZ, 0, 1.2)
    cx = FX + (TOPX - FX) * t
    cy = FY + (TOPY - FY) * t
    arch = ((ax - cx) / 50.0) ** 2 + (z - 222.0) / 106.0 - 1.0     # <0 inside the arch
    win = smax(arch * 38.0, (cy + 6.0) - ay, 8.0)
    hood = smax(hood, -win, 9.0)
    leg = smin(cone, hood, 5.0)
    # tray slab with rounded (tube-like) long edges
    zc = (SLAB_Z0 + SLAB_Z1) / 2
    slab = rbox(ax, ay, z, (0, 0, zc), (BEAM_X, SLAB_HW, (SLAB_Z1 - SLAB_Z0) / 2), SLAB_R)
    # end beam: a tube between the two hoods
    beam = np.sqrt((ax - BEAM_X) ** 2 + (z - BEAM_Z) ** 2 + np.maximum(ay - TOPY, 0) ** 2) - BEAM_R
    # neck: the rail swells and rises into the hood
    neck = round_cone(ax, ay, z, (640.0, SLAB_HW - 31.0, zc), (TOPX - 6, TOPY, TOPZ + 6), 30.0, 52.0)
    body = smin(slab, beam, 34.0)
    body = smin(body, neck, 22.0)
    body = smin(body, leg, 26.0)
    # cushion recess
    rec = np.maximum(rrect2(x, y, CL / 2 + REC_CLEAR, CD / 2 + REC_CLEAR, C_RC + REC_CLEAR), TRAY_Z - z)
    body = smax(body, -rec, 10.0)
    # shallow groove between the rail tube and the upper lip (fades out before the necks)
    gf = np.clip((620.0 - ax) / 160.0, 0, 1)
    g = np.sqrt((ay - (SLAB_HW + 1.5)) ** 2 + (z - 318.0) ** 2) - 5.0 + 9.0 * (1 - gf)
    body = smax(body, -g, 5.0)
    # floor
    body = smax(body, -z, 6.0)
    return body


def cushion_sdf(x, y, z):
    """Seat cushion, reference only (upholstery, not printed)."""
    d2 = rrect2(x, y, CL / 2, CD / 2, C_RC)
    crown = 6.0 * (1 - (x / (CL / 2)) ** 2) * (1 - (y / (CD / 2)) ** 2)
    top = z - (H - 6.0 + np.clip(crown, 0, 6))
    d = smax(d2, top, C_RE * 0.9)
    return smax(d, (TRAY_Z + 0.5) - z, 6.0)


def grid(fn, step, bounds):
    (x0, x1), (y0, y1), (z0, z1) = bounds
    xs = np.arange(x0, x1 + step, step, dtype=np.float32)
    ys = np.arange(y0, y1 + step, step, dtype=np.float32)
    zs = np.arange(z0, z1 + step, step, dtype=np.float32)
    out = np.empty((len(xs), len(ys), len(zs)), np.float32)
    Y, Z = np.meshgrid(ys, zs, indexing="ij")
    for i, xv in enumerate(xs):
        out[i] = fn(np.full_like(Y, xv), Y, Z)
    return out, (xs, ys, zs)


def mesh_from(fn, step, bounds):
    """Marching cubes on one quarter is not used: the field is already symmetric."""
    from skimage import measure
    import trimesh
    vol, (xs, ys, zs) = grid(fn, step, bounds)
    v, f, _, _ = measure.marching_cubes(vol, 0.0, spacing=(step, step, step))
    v += np.array([xs[0], ys[0], zs[0]])
    m = trimesh.Trimesh(v, f, process=True)
    return m


def render(fn, eye_dir, up, width_mm, height_mm, centre, px_per_mm=1.0, base=(0.62, 0.62, 0.62), ground=True):
    """Orthographic sphere-traced shaded view. Returns float RGB image and hit mask."""
    d = -np.asarray(eye_dir, float); d /= np.linalg.norm(d)
    r = np.cross(d, up); r /= np.linalg.norm(r)
    u = np.cross(r, d)
    W, Hh = int(width_mm * px_per_mm), int(height_mm * px_per_mm)
    sx = (np.arange(W) + 0.5) / px_per_mm - width_mm / 2
    sy = height_mm / 2 - (np.arange(Hh) + 0.5) / px_per_mm
    SX, SY = np.meshgrid(sx, sy)
    o = np.asarray(centre, float)[None, None, :] + SX[..., None] * r + SY[..., None] * u - d * 2500.0
    tt = np.zeros((Hh, W))
    alive = np.ones((Hh, W), bool)
    hit = np.zeros((Hh, W), bool)
    for _ in range(220):
        idx = np.nonzero(alive)
        if len(idx[0]) == 0:
            break
        p = o[idx] + tt[idx][:, None] * d
        dist = fn(p[:, 0], p[:, 1], p[:, 2])
        h = dist < 0.15
        hit[idx[0][h], idx[1][h]] = True
        tt[idx] += np.where(h, 0, np.maximum(dist * 0.6, 0.1))
        far = tt[idx] > 5000
        alive[idx[0][h | far], idx[1][h | far]] = False
    img = np.ones((Hh, W, 3))
    idx = np.nonzero(hit)
    p = o[idx] + tt[idx][:, None] * d
    e = 0.6
    n = np.stack([fn(p[:, 0] + e, p[:, 1], p[:, 2]) - fn(p[:, 0] - e, p[:, 1], p[:, 2]),
                  fn(p[:, 0], p[:, 1] + e, p[:, 2]) - fn(p[:, 0], p[:, 1] - e, p[:, 2]),
                  fn(p[:, 0], p[:, 1], p[:, 2] + e) - fn(p[:, 0], p[:, 1], p[:, 2] - e)], 1)
    n /= np.linalg.norm(n, axis=1)[:, None] + 1e-9
    lite = (-d * 0.55 + u * 0.7 + r * -0.45); lite /= np.linalg.norm(lite)
    lam = 0.72 * np.clip(n @ lite, 0, 1) + 0.28 * np.clip(n @ -d, 0, 1)
    rim = 1 - np.clip(n @ -d, 0, 1)
    hv = lite - d; hv /= np.linalg.norm(hv)
    spec = np.clip(n @ hv, 0, 1) ** 40
    sh = 0.30 + 0.70 * lam - 0.30 * rim ** 2.5
    bc = base(p) if callable(base) else np.asarray(base)[None, :]
    col = np.clip(sh[:, None] * bc + 0.35 * spec[:, None], 0, 1)
    img[idx] = col
    return img, hit, tt
