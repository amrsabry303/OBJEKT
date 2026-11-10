"""OBJ-177 bench, REV 0: frame model for 3D printing (print, then mould).

Shape follows the supplied tear sheet (Riva bench, Carlyle Collective) and its
photos. Overall 1829 x 686 x 406 mm and the cushion 1595 x 488 x 84 mm are from
the tear sheet; every other size is traced from the scaled drawings and photos
and is approximate.

Axes: x = length, y = up, z = depth. Origin: floor, centre of the bench. mm.

Run: python make_obj177_rev0_model.py <out_dir> [voxel_mm]
Needs numpy, scikit-image, trimesh.
"""
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from skimage import measure

# ---- key sizes (mm) ----
# From the tear sheet: overall 1829 x 686 x 406 (length and depth taken at the feet),
# cushion 1595 x 488 x 84, cushion corner R81. Everything else traced from its scaled
# elevations and plan, approximate (+-10 mm).
L, D, H = 1829.0, 686.0, 406.0
CUSH_L, CUSH_D, CUSH_T, CUSH_R = 1595.0, 488.0, 84.0, 81.0
SEAT_TOP = H - CUSH_T                     # 322: top of the seat tray; the cushion sits on it
TRAY_T = 20.0                             # seat tray thickness (proposal)
TRAY_IN_L, TRAY_IN_D = 1609.0, 511.0      # inner opening of the rim (traced)
FOOT_RX, FOOT_RZ = 95.0, 95.0             # cone foot radius at the floor (190 round); overall 1829 x 686 at the feet
FOOT_X = L / 2 - FOOT_RX                  # foot centre, 95 in from each end
FOOT_Z = D / 2 - FOOT_RZ                  # foot centre, 95 in from each long edge
LEG_TOP_Y = 300.0
LEG_TOP_RX, LEG_TOP_RZ = 54.0, 52.0       # leg at 300 high (about 108 x 104), runs into the top bar
SIDE_Z0, SIDE_Z1 = TRAY_IN_D / 2, 279.0   # side rim: inner face / outer face
SIDE_Y0, SIDE_Y1 = 263.0, 332.0           # side rim underside / top (10 above the tray)
DOWEL_D, DOWEL_DEPTH = 8.0, 22.0          # print-part alignment dowels (each side of a cut)


def sdf_round_box(p, c, half, r):
    q = np.abs(p - c) - (np.asarray(half) - r)
    return np.linalg.norm(np.maximum(q, 0), axis=-1) + np.minimum(np.max(q, axis=-1), 0) - r


def sdf_capsule(p, a, b, r):
    pa, ba = p - a, np.asarray(b) - a
    h = np.clip((pa @ ba) / (ba @ ba), 0, 1)[..., None]
    return np.linalg.norm(pa - ba * h, axis=-1) - r


def sdf_cone(p, a, b, ra, rb):
    """Rounded-cone (capped cone with spherical ends) from a (radius ra) to b (radius rb)."""
    ba = np.asarray(b, float) - a
    l2 = ba @ ba
    pa = p - a
    t = (pa @ ba) / l2
    tc = np.clip(t, 0, 1)
    r = ra + (rb - ra) * tc
    axisd = np.linalg.norm(pa - ba * tc[..., None], axis=-1)
    return axisd - r


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


# Ends, from Sabry's sharper photos (10 Nov): each leg is a separate bell-shaped cone; the
# slim side rail sweeps up into a hood that arches over the top of the cone and runs down
# its outer face; a round bar across the depth joins the two hoods at the top.
CONE_FOOT_R, CONE_TOP_R = 95.0, 46.0      # cone radius at the floor (about 190) / at its rounded top (about half)
CONE_TOP_Y = 336.0                        # centre of the rounded top; top of the cone about 382, under the hood
HOOD_R = 40.0                             # hood tube radius over the cone (about 80 round)
RAIL_R = 34.0                             # side rail tube radius (about 68 round)
HOOD_Z = 262.0                            # hood and side-rail centre line across the depth
HOOD_P0 = (600.0, 298.0)                  # hood starts from the side rail (x, y)
HOOD_C = (950.0, 440.0)                   # control point of the arch over the cone
HOOD_P2 = (872.0, 255.0)                  # arch comes down on the outer face of the cone
HOOD_P3 = (868.0, 150.0)                  # and fades into the cone
BAR_R = 42.0                              # round bar across the depth at the top of the hoods
K_CONE, K_HOOD, K_BAR = 14.0, 30.0, 26.0  # blend radii: tight crease at the cone, softer elsewhere


def sdf_cone_leg(p, sx, sz):
    foot = np.array([sx * FOOT_X, -30.0, sz * FOOT_Z])
    top = np.array([sx * (FOOT_X + 4), CONE_TOP_Y, sz * (HOOD_Z - 10)])
    return sdf_cone(p, foot, top, CONE_FOOT_R + 6, CONE_TOP_R)


def hood_points(sx, n=14):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * HOOD_P0[0] + 2 * (1 - t) * t * HOOD_C[0] + t * t * HOOD_P2[0]
        y = (1 - t) ** 2 * HOOD_P0[1] + 2 * (1 - t) * t * HOOD_C[1] + t * t * HOOD_P2[1]
        pts.append((sx * x, y))
    pts.append((sx * HOOD_P3[0], HOOD_P3[1]))
    return pts


def sdf_hood(p, sx, sz):
    pts = hood_points(sx)
    d = None
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        t = min(1.0, (abs(x0) - HOOD_P0[0]) / 120.0)
        r = (RAIL_R + (HOOD_R - RAIL_R) * t) if y1 > 200 else HOOD_R - 8
        c = sdf_capsule(p, np.array([x0, y0, sz * HOOD_Z]), np.array([x1, y1, sz * HOOD_Z]), r)
        d = c if d is None else np.minimum(d, c)
    return d


def hood_apex():
    pts = hood_points(1, 200)
    return max(pts, key=lambda q: q[1])


def frame_sdf(p):
    d = None
    ax, ay = hood_apex()
    for sx in (-1, 1):
        bar = sdf_capsule(p, np.array([sx * ax, ay + HOOD_R - BAR_R, -HOOD_Z]),
                          np.array([sx * ax, ay + HOOD_R - BAR_R, HOOD_Z]), BAR_R)
        end = bar
        for sz in (-1, 1):
            end = smin(end, sdf_hood(p, sx, sz), K_BAR)
        for sz in (-1, 1):
            end = smin(end, sdf_cone_leg(p, sx, sz), K_CONE)
        d = end if d is None else np.minimum(d, end)
    for sz in (-1, 1):
        # side rail: round tube along the length, same line as the hoods
        # runs on into the inner face of each cone; the blend gives the downward sweep under it
        side = sdf_capsule(p, np.array([-(FOOT_X - 20), HOOD_P0[1], sz * HOOD_Z]),
                           np.array([FOOT_X - 20, HOOD_P0[1], sz * HOOD_Z]), RAIL_R)
        d = smin(d, side, 48.0)
    tray = sdf_round_box(p, np.array([0, SEAT_TOP - TRAY_T / 2, 0]),
                         [hood_apex()[0] - 10, TRAY_T / 2, SIDE_Z0 + 5], 8.0)
    d = smin(d, tray, 8.0)
    # seat recess: flat tray top where the cushion sits, inside the rim
    pocket = sdf_round_box(p, np.array([0, SEAT_TOP + 100, 0]),
                           [TRAY_IN_L / 2, 100, TRAY_IN_D / 2], 30.0)
    d = np.maximum(d, -pocket)
    d = -smin(-d, p[..., 1] + 3.0, 12.0)   # about R12 round on the bottom edge of each foot
    d = np.maximum(d, -p[..., 1])          # flat feet on the floor (y = 0)
    # keep inside the tear-sheet envelope: blends must not bulge past 1829 x 686
    d = np.maximum(d, np.abs(p[..., 0]) - L / 2)
    d = np.maximum(d, np.abs(p[..., 2]) - D / 2)
    return d


def eval_grid(fn, lo, hi, vox):
    xs = np.arange(lo[0], hi[0] + vox, vox)
    ys = np.arange(lo[1], hi[1] + vox, vox)
    zs = np.arange(lo[2], hi[2] + vox, vox)
    vol = np.empty((len(xs), len(ys), len(zs)), np.float32)
    Y, Z = np.meshgrid(ys, zs, indexing="ij")
    for i, x in enumerate(xs):
        P = np.stack([np.full_like(Y, x), Y, Z], -1)
        vol[i] = fn(P)
    return vol, (xs, ys, zs)


def mesh_from(vol, axes, vox):
    xs, ys, zs = axes
    v, f, _, _ = measure.marching_cubes(vol, 0.0, spacing=(vox, vox, vox), allow_degenerate=False)
    v += [xs[0], ys[0], zs[0]]
    m = trimesh.Trimesh(v, f, process=True)
    m.update_faces(m.unique_faces()); m.remove_unreferenced_vertices()
    # drop slivers where a print cut grazes a curve, then close any small opening it left
    bodies = m.split(only_watertight=False)
    if len(bodies) > 1:
        big = max(abs(b.volume) for b in bodies)
        m = trimesh.util.concatenate([b for b in bodies if abs(b.volume) > 0.01 * big])
        m.merge_vertices()
    if not m.is_watertight:
        trimesh.repair.fill_holes(m)
        trimesh.repair.fix_normals(m)
    if m.is_watertight:
        trimesh.smoothing.filter_taubin(m, iterations=4)
    return m


# ---- print split: 4 lengthwise x 2 depthwise = 8 parts, each within 500 x 500 x 500 ----
X_CUTS = [-L / 2 - 5, -457.0, 0.0, 457.0, L / 2 + 5]
Z_CUTS = [-D / 2 - 5, 0.0, D / 2 + 5]


def dowel_points():
    """Dowel centres on each cut plane, placed where the section is solid."""
    pts = []
    # x cuts at +-457 go through the side rails and the tray; x cut at 0 through rails and tray
    for xc in X_CUTS[1:-1]:
        for sz in (-1, 1):
            pts.append(("x", xc, (SIDE_Y0 + SIDE_Y1) / 2 - 10, sz * (SIDE_Z0 + SIDE_Z1) / 2))
            pts.append(("x", xc, SEAT_TOP - TRAY_T / 2, sz * (SIDE_Z0 - 110)))
    # z cut at 0 goes through the tray and both end rails
    for sx in (-1, 1):
        ax, ay = hood_apex()
        pts.append(("z", sx * ax, ay + HOOD_R - BAR_R, 0.0))
    for xx in (-680, -230, 230, 680):
        pts.append(("z", xx, SEAT_TOP - TRAY_T / 2, 0.0))
    return pts


def dowel_sdf(p, pts):
    d = np.full(p.shape[:-1], 1e9, np.float32)
    for ax, a, b, c in pts:
        if ax == "x":
            ctr = np.array([a, b, c]); u = np.array([1.0, 0, 0])
        else:
            ctr = np.array([a, b, c]); u = np.array([0, 0, 1.0])
        d = np.minimum(d, sdf_capsule(p, ctr - u * DOWEL_DEPTH, ctr + u * DOWEL_DEPTH, DOWEL_D / 2 + 0.2))
    return d


def main(out, vox=3.0):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    pad = 2 * vox
    lo = np.array([-L / 2 - pad, -pad, -D / 2 - pad]); hi = np.array([L / 2 + pad, H + pad, D / 2 + pad])
    vol, axes = eval_grid(frame_sdf, lo, hi, vox)
    whole = mesh_from(vol, axes, vox)
    whole.export(out / "OBJ-177_rev0_frame_one-piece.stl")
    np.save(out / "_vol.npy", vol); json.dump({"lo": lo.tolist(), "vox": vox}, open(out / "_vol.json", "w"))
    pts = dowel_points()
    report = {"one_piece": {"bounds": whole.bounds.tolist(), "watertight": bool(whole.is_watertight),
                            "faces": int(len(whole.faces)), "volume_l": round(whole.volume / 1e6, 2)}}
    n = 0
    for i in range(4):
        for j in range(2):
            n += 1
            blo = np.array([X_CUTS[i], -pad, Z_CUTS[j]]); bhi = np.array([X_CUTS[i + 1], H + pad, Z_CUTS[j + 1]])
            c = (blo + bhi) / 2; half = (bhi - blo) / 2

            def part(p, c=c, half=half):
                d = np.maximum(frame_sdf(p), sdf_round_box(p, c, half, 0.01))
                return np.maximum(d, -dowel_sdf(p, pts))
            plo = blo - pad; phi = bhi + pad
            v, ax = eval_grid(part, plo, phi, vox)
            m = mesh_from(v, ax, vox)
            name = f"OBJ-177_rev0_print-part-{n:02d}.stl"
            m.export(out / name)
            ext = (m.bounds[1] - m.bounds[0]).round(1).tolist()
            report[name] = {"bounds": m.bounds.round(1).tolist(), "extent_mm": ext,
                            "watertight": bool(m.is_watertight), "faces": int(len(m.faces))}
    report["dowels"] = [{"plane": a, "at_mm": [round(x, 1) for x in (b, c, d)]} for a, b, c, d in pts]
    json.dump(report, open(out / "OBJ-177_rev0_print-report.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "dowels"}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]) if len(sys.argv) > 2 else 3.0)
