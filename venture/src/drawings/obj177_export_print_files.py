import trimesh, numpy as np, glob, os, json, base64
import fast_simplification as fs
out='riva/out'; rep={}
R=trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0])  # model Y-up -> file Z-up: (x,y,z)->(x,-z,y)
whole=trimesh.load('riva/m3/OBJ-177_rev0_frame_one-piece.stl'); dy=-whole.bounds[0][1]
for f in sorted(glob.glob('riva/m3/*.stl')):
    m=trimesh.load(f); m.apply_translation([0,dy,0])
    s=None
    for keep in ((0.3,) if 'one-piece' in f else (0.45,)) + (0.6, 1.0):
        if keep<1:
            v,fc=fs.simplify(m.vertices.astype('float32'),m.faces.astype('int32'),target_reduction=1-keep); s=trimesh.Trimesh(v,fc,process=True)
        else: s=m.copy()
        if s.is_watertight: break
    pts,_=trimesh.sample.sample_surface(s,20000); _,dist,_=trimesh.proximity.closest_point(m,pts)
    s.apply_transform(R)
    name=os.path.basename(f); s.export(f'{out}/{name}')
    rep[name]=dict(faces=len(s.faces),watertight=bool(s.is_watertight),bodies=len(s.split(only_watertight=False)),max_dev_mm=round(float(dist.max()),2),MB=round(os.path.getsize(f'{out}/{name}')/1e6,1),extent_xyz_mm=(s.bounds[1]-s.bounds[0]).round(1).tolist(),volume_l=round(float(s.volume)/1e6,2),bounds=s.bounds.round(1).tolist())
    print(name,{k:rep[name][k] for k in ['faces','watertight','bodies','max_dev_mm','MB','extent_xyz_mm','volume_l']})
src=json.load(open('riva/m3/OBJ-177_rev0_print-report.json'))
# dowel check in model coords
parts=[trimesh.load(f'riva/m3/OBJ-177_rev0_print-part-{i:02d}.stl') for i in range(1,9)]
ok=0
for d in src['dowels']:
    x,y,z=d['at_mm']; off=np.array([10,0,0]) if d['plane']=='x' else np.array([0,0,10])
    p=np.array([[x,y,z]])+[off,-off]
    solid=whole.contains(p).all(); empty=not any(pp.contains(p).any() for pp in parts)
    ok+= solid and empty
print('dowels ok', ok, 'of', len(src['dowels']))
json.dump({'note':'Files are Z-up, mm, origin at the floor centre of the bench. Parts keep their position in the bench, so they line up when loaded together.','meshes':rep,'dowels_model_coords_y_up':src['dowels'],'dowel':'D8 x 44 (22 each side of the cut), hole D8.4','dowels_checked':f'{ok} of {len(src["dowels"])} sit in solid material and are open in the parts'},open(f'{out}/OBJ-177_rev0_print-report.json','w'),indent=1)
# viewer mesh
v,f=fs.simplify(whole.vertices.astype('float32'),whole.faces.astype('int32'),target_reduction=0.7); s=trimesh.Trimesh(v,f)
vv=s.vertices[s.faces].reshape(-1,3).astype('float32'); vn=s.vertex_normals[s.faces].reshape(-1,3).astype('float32')
open('geo/obj177_mesh.js','w').write('window.MESH={p:"%s",n:"%s"};'%(base64.b64encode(vv.tobytes()).decode(),base64.b64encode(vn.tobytes()).decode()))
