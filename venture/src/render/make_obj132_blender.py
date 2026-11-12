"""OBJ-132 rev 0 (approved by Sabry 12 Nov 2026): set of three wall plates, built in Blender from the drawing.
All sizes in mm from the drawing (scene scale 0.001, 1 unit = 1 m). Wall plane is y=0, the room is at -y, z is up.
Usage: python make_obj132_blender.py OUTDIR grey
Grey model only (one matt grey, soft light). Model files and views stay out of git while the repo is public."""
import sys, math, bpy
from mathutils import Vector

out = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "grey"
S = 0.001
PW, PH, T = 300.0, 330.0, 2.0          # face plate
WIN, GAP = 130.0, 60.0                 # window dia (centred), gap between plates
FRD, INSET = 13.0, 10.0                # frame strip height behind the plate, inset from the edge
STAND = FRD + T                        # 15 mm off the wall
HW, HH, HTOP = 274.0, 40.0, 14.0       # hanger plate, top edge 14 below the plate top
KX, KHEAD, KSLOT, KSH = 75.0, 9.0, 12.0, 5.0
DISC, DISC_T, RING_OD, RING_ID, PCD, STUDD = 150.0, 3.0, 176.0, 136.0, 160.0, 3.0
ZHANG = 5.0                            # hanger rear face off the wall
TOP = 2055.0                           # top of the stack, mm above the floor (centre of the stack 1500, proposal)

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

def box(name, x0, x1, y0, y1, z0, z1):
    bpy.ops.mesh.primitive_cube_add()
    o = bpy.context.active_object; o.name = name
    o.scale = ((x1 - x0) / 2 * S, (y1 - y0) / 2 * S, (z1 - z0) / 2 * S)
    o.location = ((x0 + x1) / 2 * S, (y0 + y1) / 2 * S, (z0 + z1) / 2 * S)
    bpy.ops.object.transform_apply(scale=True)
    return o

def cyl(name, r, y0, y1, x, z, verts=128):
    """cylinder with its axis along y, from y0 to y1"""
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r * S, depth=abs(y1 - y0) * S,
                                        location=(x * S, (y0 + y1) / 2 * S, z * S), rotation=(math.pi / 2, 0, 0))
    o = bpy.context.active_object; o.name = name
    return o

def cut(target, tool):
    m = target.modifiers.new("cut", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = tool
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier="cut")
    bpy.data.objects.remove(tool, do_unlink=True)

def join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join(); j = bpy.context.active_object; j.name = name
    return j

plates, parts_by_plate = [], []
for i in range(3):
    zt = TOP - i * (PH + GAP); zc = zt - PH / 2
    face = box(f"face{i+1}", -PW / 2, PW / 2, -STAND, -FRD, zt - PH, zt)
    cut(face, cyl("w", WIN / 2, -STAND - 5, -FRD + 5, 0, zc))
    # frame: two long strips (full height) and two short strips butted between them, all 2 thick, 13 high, set 10 in
    fx0, fx1, fz0, fz1 = -PW / 2 + INSET, PW / 2 - INSET, zt - PH + INSET, zt - INSET
    fr = [box("fl", fx0, fx0 + T, -FRD, 0, fz0, fz1), box("fr", fx1 - T, fx1, -FRD, 0, fz0, fz1),
          box("ft", fx0 + T, fx1 - T, -FRD, 0, fz1 - T, fz1), box("fb", fx0 + T, fx1 - T, -FRD, 0, fz0, fz0 + T)]
    # hanger plate with two keyholes (head hole 9, slot up 12, 5 wide)
    hz1 = zt - HTOP; hz0 = hz1 - HH
    hg = box("hanger", -HW / 2, HW / 2, -ZHANG - T, -ZHANG, hz0, hz1)
    for sx in (-KX, KX):
        hole_z = hz0 + 14
        cut(hg, cyl("kh", KHEAD / 2, -ZHANG - T - 3, -ZHANG + 3, sx, hole_z, 48))
        slot = box("ks", sx - KSH / 2, sx + KSH / 2, -ZHANG - T - 3, -ZHANG + 3, hole_z, hole_z + KSLOT)
        cut(hg, slot)
        cut(hg, cyl("kt", KSH / 2, -ZHANG - T - 3, -ZHANG + 3, sx, hole_z + KSLOT, 48))
    disc = cyl("disc", DISC / 2, -FRD, -FRD + DISC_T, 0, zc, 128)
    ring = cyl("ring", RING_OD / 2, -FRD + DISC_T, -FRD + DISC_T + T, 0, zc, 128)
    cut(ring, cyl("ri", RING_ID / 2, -FRD, -FRD + 10, 0, zc, 128))
    studs = []
    for a in (90, 210, 330):
        sx = PCD / 2 * math.cos(math.radians(a)); sz = zc + PCD / 2 * math.sin(math.radians(a))
        studs.append(cyl("st", STUDD / 2, -FRD, -FRD + 7, sx, sz, 24))
        cut(ring, cyl("rh", 1.7, -FRD, -FRD + 10, sx, sz, 24))
    parts_by_plate.append((face, fr, hg, disc, ring, studs))

import bmesh
def fix_normals(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(o.data); bm.free()
# one matt grey for everything
g = bpy.data.materials.new("grey"); g.use_nodes = True
b = g.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1); b.inputs["Metallic"].default_value = 0.0; b.inputs["Roughness"].default_value = 0.8
allobjs = []
for p in parts_by_plate:
    for o in [p[0], *p[1], p[2], p[3], p[4], *p[5]]: allobjs.append(o)
for o in allobjs:
    fix_normals(o); o.data.materials.clear(); o.data.materials.append(g)
    for pl in o.data.polygons: pl.material_index = 0
f1 = parts_by_plate[0][0]
print('face1 mats', [m.name if m else None for m in f1.data.materials], 'wall mats', [m.name for m in wall.data.materials] if False else '', 'face1 normals y mean', sum(poly.normal.y for poly in f1.data.polygons) / len(f1.data.polygons), 'verts', len(f1.data.vertices))
wall = box("wall", -1.3 / S, 1.3 / S, 0, 60, 500, 2700)
wall.data.materials.append(g)

world = bpy.data.worlds.new("w"); scn.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (0.85, 0.85, 0.85, 1); bg.inputs["Strength"].default_value = 0.3

def area(name, loc, target, size, energy):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.active_object; l.name = name; l.data.size = size; l.data.energy = energy
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
CEN = (0, 0, 1.5)
area("key", (-1.6, -2.2, 2.6), CEN, 2.0, 55)
area("fill", (1.8, -1.8, 1.6), CEN, 2.0, 16)
area("top", (0, -1.0, 3.0), CEN, 2.0, 18)

cam_data = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_data); scn.collection.objects.link(cam); scn.camera = cam
scn.render.engine = "CYCLES"; scn.cycles.device = "CPU"; scn.cycles.samples = 48; scn.cycles.use_denoising = True
scn.view_settings.view_transform = "Standard"

def shoot(name, loc, tgt, lens=60, ortho=None, res=(800, 1200)):
    scn.render.resolution_x, scn.render.resolution_y = res
    cam_data.type = "ORTHO" if ortho else "PERSP"
    if ortho: cam_data.ortho_scale = ortho
    cam_data.lens = lens
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = f"{out}/OBJ-132_{mode}_{name}.png"
    bpy.ops.render.render(write_still=True)

z1 = TOP * S
zmid = 1.5
import sys as _s
if len(_s.argv) > 3 and _s.argv[3] == "dbg": raise SystemExit
shoot("front", (0, -4, zmid), (0, 0, zmid), ortho=1.35)
shoot("three-quarter", (-1.25, -2.1, 1.75), (0, 0, zmid), lens=55)
shoot("side", (4, -0.0075, z1 - 0.12), (0, -0.0075, z1 - 0.12), ortho=0.38, res=(900, 700))
shoot("window-detail", (-0.35, -0.5, z1 - 0.2), (0, -0.01, z1 - PH * S / 2), lens=70, res=(900, 900))
# rear view: wall removed, only the top plate, to show frame, hanger plate, ring and disc
bpy.data.objects.remove(wall, do_unlink=True)
for i, p in enumerate(parts_by_plate):
    if i > 0:
        for o in [p[0], *p[1], p[2], p[3], p[4], *p[5]]: bpy.data.objects.remove(o, do_unlink=True)
zc1 = (TOP - PH / 2) * S
shoot("rear-top-plate", (0.4, 0.55, zc1 + 0.18), (0, -0.008, zc1), lens=55, res=(900, 900))
