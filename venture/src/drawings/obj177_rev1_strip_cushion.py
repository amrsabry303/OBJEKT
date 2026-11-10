"""Remove the cushion from Sabry's bench model (b0c0bf78-bench_3d_model.glb) and scale the frame
to the tear sheet. Model units: mm after scaling the GLB by 1829 (it was normalised to 1 m long).
Everything above the seat line is cushion, except the two end tubes and the four corner hoods,
which are protected. End tubes fitted from the model's own sections."""
import trimesh, numpy as np
SEAT_Y = 372.0                       # cushion meets the frame here (before scaling)
TUBE_X, TUBE_Y, TUBE_R = 803.0, 373.0, 80.0   # end tubes across the depth (fitted: r 67-79)
HOOD_X, HOOD_Z = 745.0, 240.0        # corner zones (hoods over the cones) kept as modelled
m = trimesh.load('glb/user_main_mm.stl')
cut = trimesh.creation.box(extents=[2000, 600, 1000]); cut.apply_translation([0, SEAT_Y + 300, 0])
keep = []
for sx in (-1, 1):
    t = trimesh.creation.cylinder(radius=TUBE_R, height=1000, sections=128)   # along z
    t.apply_translation([sx * TUBE_X, TUBE_Y, 0]); keep.append(t)
    for sz in (-1, 1):
        b = trimesh.creation.box(extents=[400, 600, 400])
        b.apply_translation([sx * (HOOD_X + 200), SEAT_Y + 300, sz * (HOOD_Z + 200)]); keep.append(b)
cut = trimesh.boolean.difference([cut] + keep, engine='manifold')
f = trimesh.boolean.difference([m, cut], engine='manifold')
# the cushion's underside left a thin, wavy layer (about 10 mm, holes in places): replace it with
# a flat seat panel 16 mm thick after scaling, top at the seat line, running into rails and end tubes
PANEL_T = 16.0 / (322.0 / SEAT_Y)
panel = trimesh.creation.box(extents=[2 * 790, PANEL_T, 2 * 275])
panel.apply_translation([0, SEAT_Y - PANEL_T / 2, 0])
f = trimesh.boolean.union([f, panel], engine='manifold')
parts = f.split(only_watertight=False)
big = max(abs(p.volume) for p in parts)
f = trimesh.util.concatenate([p for p in parts if abs(p.volume) > 0.01 * big]) if len(parts) > 1 else f
print('bodies', len(parts), 'watertight', f.is_watertight)
ext = f.bounds[1] - f.bounds[0]
sx = 1829.0 / ext[0]; sz = 686.0 / ext[2]; sy = 322.0 / SEAT_Y      # seat at 322 = 406 - 84 cushion
f.apply_transform(np.diag([sx, sy, sz, 1.0]))
f.apply_translation([-(f.bounds[0][0] + f.bounds[1][0]) / 2, -f.bounds[0][1], -(f.bounds[0][2] + f.bounds[1][2]) / 2])
print('scale x %.4f y %.4f z %.4f' % (sx, sy, sz))
print('frame extent mm', (f.bounds[1] - f.bounds[0]).round(1).tolist(), 'watertight', f.is_watertight, 'volume L', round(f.volume / 1e6, 2))
f.export('glb/frame_no-cushion_mm_yup.stl')
