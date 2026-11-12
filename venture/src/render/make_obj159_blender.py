"""OBJ-159 rev 8 (approved by Sabry 12 Nov 2026) built in Blender from the drawing. Computer render of the drawing, not AI.
All dimensions in mm, scene scale 0.001 (1 Blender unit = 1 m). x width, y depth (front at y = 0, camera in front at negative y), z height.
Usage: python make_obj159_blender.py OUTDIR [grey|steel]
Detail shots only (cut-outs, floor pads, shelf ends and screws), as the project rule says; heroes stay on Magnific.
Wood shelf options are not drawn yet, so only the brushed stainless version exists."""
import sys, math, bpy
from mathutils import Vector
out = sys.argv[1]; mode = sys.argv[2] if len(sys.argv) > 2 else 'grey'
S = 0.001
IN = 25.4
OH, OW, OD = 74*IN, 34*IN, 14*IN
TP, TS, FL = 4.0, 3.0, 1.25*IN
NSH, NCUT = 6, 5
TOPF, BOTF = OH - 25, 25 + FL
PITCH = (TOPF - BOTF)/(NSH-1)
SHELF = [TOPF - PITCH*k for k in range(NSH)]
SLOT_OFF = FL + (PITCH - FL)/2
R = 125.0
HOLE_U = [80.0, OD - 80.0]; DROP = 15.0
PAD_W, STEP = 40.0, 3.0

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

def box(name, x0, x1, y0, y1, z0, z1):
    bpy.ops.mesh.primitive_cube_add()
    o = bpy.context.active_object; o.name = name
    o.scale = ((x1-x0)/2*S, (y1-y0)/2*S, (z1-z0)/2*S)
    o.location = ((x0+x1)/2*S, (y0+y1)/2*S, (z0+z1)/2*S)
    bpy.ops.object.transform_apply(scale=True)
    return o
def cyl_x(name, x0, x1, y, z, r, verts=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r*S, depth=(x1-x0)*S, location=((x0+x1)/2*S, y*S, z*S), rotation=(0, math.pi/2, 0))
    o = bpy.context.active_object; o.name = name
    return o
def diff(target, cutters):
    for c in cutters:
        m = target.modifiers.new('cut', 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = c; m.solver = 'EXACT'
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier='cut')
        bpy.data.objects.remove(c, do_unlink=True)
def bevel(o, w):
    m = o.modifiers.new('bevel', 'BEVEL'); m.width = w*S; m.segments = 2; m.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier='bevel')

plates, shelves, screws = [], [], []
for side, (x0, x1) in enumerate([(0, TP), (OW-TP, OW)]):
    p = box(f'plate{side}', x0, x1, 0, OD, 0, OH)
    cut = []
    for k in range(NCUT): cut.append(cyl_x('c', x0-1, x1+1, OD/2, SHELF[k]-SLOT_OFF, R, 160))
    for z in SHELF:
        for u in HOLE_U: cut.append(cyl_x('h', x0-1, x1+1, u, z-DROP, 3.25, 32))
    # bottom edge: 3 mm step between two 40 mm pads
    cut.append(box('step', x0-1, x1+1, PAD_W, OD-PAD_W, -1, STEP))
    diff(p, cut)
    bevel(p, 0.3)
    plates.append(p)
    for z in SHELF:
        for u in HOLE_U:
            xs = (x0-3, x0) if side == 0 else (x1, x1+3)
            screws.append(cyl_x('screw', xs[0], xs[1], u, z-DROP, 5.5, 48))
for i, h in enumerate(SHELF):
    xl, xr = TP, OW-TP
    parts = [box('top', xl, xr, 0, OD, h-TS, h), box('ff', xl, xr, 0, TS, h-FL, h), box('rf', xl, xr, OD-TS, OD, h-FL, h),
             box('lf', xl, xl+TS, 1.5, OD-1.5, h-FL, h), box('rf2', xr-TS, xr, 1.5, OD-1.5, h-FL, h)]
    bpy.ops.object.select_all(action='DESELECT')
    for q in parts: q.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join()
    s = bpy.context.active_object; s.name = f'shelf{i}'; bevel(s, 0.3); shelves.append(s)
for o in plates + shelves + screws:
    bpy.context.view_layer.objects.active = o; o.select_set(True)
bpy.ops.object.shade_smooth()
for o in plates + shelves + screws:
    o.modifiers.new('es', 'EDGE_SPLIT')

def mat_steel(name, streak_scale):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.72, 0.72, 0.73, 1); b.inputs['Metallic'].default_value = 1.0
    b.inputs['Anisotropic'].default_value = 0.6
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = streak_scale
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40; nz.inputs['Detail'].default_value = 8
    ramp = nt.nodes.new('ShaderNodeMapRange'); ramp.inputs['To Min'].default_value = 0.22; ramp.inputs['To Max'].default_value = 0.38
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Value']); nt.links.new(ramp.outputs['Result'], b.inputs['Roughness'])
    return m
def mat_flat(name, color, rough, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = color; b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m
if mode == 'grey':
    g = mat_flat('grey', (0.45, 0.45, 0.45, 1), 0.75)
    for o in plates + shelves + screws: o.data.materials.append(g)
else:
    mv = mat_steel('steel_vertical', (400, 400, 1)); mh = mat_steel('steel_horizontal', (1, 400, 400))
    for o in plates: o.data.materials.append(mv)          # brush vertical on the plates
    for o in shelves + screws: o.data.materials.append(mh)  # brush along the length on the shelves

bpy.ops.mesh.primitive_plane_add(size=12, location=(OW/2*S, OD/2*S, 0))
floor = bpy.context.active_object; floor.name = 'floor'
floor.data.materials.append(mat_flat('floor', (0.30, 0.30, 0.30, 1) if mode == 'grey' else (0.55, 0.52, 0.48, 1), 0.9))
world = bpy.data.worlds.new('w'); scn.world = world; world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.85, 0.85, 0.85, 1) if mode == 'grey' else (0.82, 0.80, 0.76, 1); bg.inputs['Strength'].default_value = 0.30
def area(name, loc, size, energy, tgt=(0.43, 0.18, 0.9)):
    bpy.ops.object.light_add(type='AREA', location=loc)
    l = bpy.context.active_object; l.name = name; l.data.size = size; l.data.energy = energy
    l.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
import os
K = float(os.environ.get('LIGHT', '1.0'))
area('key', (-1.6, -2.0, 2.2), 2.2, 55*K); area('fill', (2.2, -1.6, 1.2), 2.0, 18*K); area('rim', (0.4, 2.4, 1.8), 1.6, 26*K)
cam_data = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cam_data); scn.collection.objects.link(cam); scn.camera = cam
def shoot(name, loc, tgt, lens=50, size=None):
    size = size or (int(os.environ.get('W', '1400')), int(os.environ.get('H', '1000')))
    scn.render.resolution_x, scn.render.resolution_y = size
    cam_data.lens = lens; cam.location = Vector(loc)*S
    cam.rotation_euler = (Vector(tgt)*S - Vector(loc)*S).to_track_quat('-Z', 'Y').to_euler()
    scn.render.filepath = f'{out}/OBJ-159_{mode}_{name}.png'
    bpy.ops.render.render(write_still=True)
scn.render.engine = 'CYCLES'; scn.cycles.device = 'CPU'; scn.cycles.samples = int(os.environ.get('SAMPLES', '48')); scn.cycles.use_denoising = True
scn.view_settings.view_transform = 'Standard' if mode == 'grey' else 'AgX'
z2 = SHELF[3]
shoot('detail_cutouts', (-900, -1500, 560), (80, 120, 560), lens=60)
shoot('detail_floor-pads', (-350, -420, 160), (60, 80, 30), lens=45)
shoot('detail_shelf-end', (-520, -520, z2-30), (0, 60, z2-130), lens=60)
