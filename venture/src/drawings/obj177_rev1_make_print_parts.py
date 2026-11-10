"""Split the cushion-free frame into print parts with dowel holes; export GLB (m, Y-up) and STL (mm, Z-up)."""
import trimesh, numpy as np, json, os
OUT = 'glb/out'; os.makedirs(OUT, exist_ok=True)
f = trimesh.load('glb/frame_no-cushion_mm_yup.stl')
SY, SZ = 322.0 / 372.0, 686.0 / f.bounds[1][2] / 2 if False else 0.9491
RAIL_Z, RAIL_Y = 252 * SZ, 335 * SY          # rail centre line (model sections, scaled)
TUBE_X, TUBE_Y = 803.0, 373 * SY             # end tube centre line
PANEL_Y = 322 - 8                            # middle of the 16 mm seat panel
X_CUTS = [-1000, -457, 0, 457, 1000]; Z_CUTS = [-500, 0, 500]
dowels = []                                  # (axis, x, y, z, diameter)
for xc in X_CUTS[1:-1]:
    for sz in (-1, 1):
        dowels.append(('x', xc, RAIL_Y, sz * RAIL_Z, 8.0))
        dowels.append(('x', xc, PANEL_Y, sz * 130.0, 6.0))
for sx in (-1, 1):
    dowels.append(('z', sx * TUBE_X, TUBE_Y, 0.0, 8.0))
for xx in (-680, -230, 230, 680):
    dowels.append(('z', xx, PANEL_Y, 0.0, 6.0))
holes = []
for ax, x, y, z, dia in dowels:
    c = trimesh.creation.cylinder(radius=dia / 2 + 0.2, height=44, sections=32)
    if ax == 'x':
        c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    c.apply_translation([x, y, z]); holes.append(c)
ok = int(sum(f.contains([[x + (10 if a == 'x' else 0), y, z + (10 if a == 'z' else 0)], [x - (10 if a == 'x' else 0), y, z - (10 if a == 'z' else 0)]]).all() for a, x, y, z, d in dowels))
print('dowels in solid material:', ok, 'of', len(dowels))
R = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])       # Y-up -> Z-up for print files
rep = {}
def save(m, name):
    z = m.copy(); z.apply_transform(R); z.export(f'{OUT}/{name}')
    rep[name] = dict(extent_xyz_mm=(z.bounds[1] - z.bounds[0]).round(1).tolist(), watertight=bool(z.is_watertight),
                     bodies=len(z.split(only_watertight=False)), volume_l=round(float(z.volume) / 1e6, 2),
                     MB=round(os.path.getsize(f'{OUT}/{name}') / 1e6, 1))
save(f, 'OBJ-177_rev1_frame_one-piece.stl')
n = 0
for i in range(4):
    for j in range(2):
        n += 1
        b = trimesh.creation.box(extents=[X_CUTS[i + 1] - X_CUTS[i], 1000, Z_CUTS[j + 1] - Z_CUTS[j]])
        b.apply_translation([(X_CUTS[i] + X_CUTS[i + 1]) / 2, 300, (Z_CUTS[j] + Z_CUTS[j + 1]) / 2])
        p = trimesh.boolean.intersection([f, b], engine='manifold')
        p = trimesh.boolean.difference([p] + holes, engine='manifold')
        save(p, f'OBJ-177_rev1_print-part-{n:02d}.stl')
# GLB for viewing: metres, Y-up, frame only
g = f.copy(); g.apply_scale(0.001); g.export(f'{OUT}/OBJ-177_rev1_frame_no-cushion.glb')
rep['OBJ-177_rev1_frame_no-cushion.glb'] = dict(MB=round(os.path.getsize(f'{OUT}/OBJ-177_rev1_frame_no-cushion.glb') / 1e6, 1), units='m, Y-up')
json.dump({'source': "Sabry's model b0c0bf78-bench_3d_model.glb, cushion removed, scaled to the tear sheet",
           'scale_xyz': [1.0, round(SY, 4), SZ], 'files': rep,
           'dowels': [dict(axis=a, at_mm_yup=[round(x, 1), round(y, 1), round(z, 1)], diameter=d, length=44, hole=d + 0.4) for a, x, y, z, d in dowels],
           'dowels_checked': f'{ok} of {len(dowels)} in solid material'}, open(f'{OUT}/OBJ-177_rev1_print-report.json', 'w'), indent=1)
for k, v in rep.items(): print(k, v)
