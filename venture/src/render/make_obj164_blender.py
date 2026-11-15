"""OBJ-164 corner shelf (pair; one shelf modelled) built in Blender from drawing rev 0
(rev 1 DRAFT, not yet approved).
All dimensions in mm, scene scale 0.001 (1 Blender unit = 1 m). Corner of the two walls at the origin,
wall A in the plane y=0 (runs along +x), wall B in the plane x=0 (runs along +y), z up.
REV 1 (draft, 15 Nov 2026; replaces rev 0): one triangle sheet bent 90 degrees along K-L. Horizontal top right triangle
220 x 220, 2 mm; vertical triangular plate 220 x 150 flat on wall B (vertical edge in the corner); 15 mm flange on the right leg. Overall height 152.
Usage: python make_obj164_blender.py OUTDIR [grey|steel]
The walls are plain context planes, not part of the product. Output stays out of git (venture/models/).
"""
import sys, math, bpy, bmesh
from mathutils import Vector

out = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "grey"
S = 0.001
LEG, T, LIP, FL, DROP = 220.0, 2.0, 10.0, 15.0, 150.0
GL = LEG / math.sqrt(2)
Z_UNDER = DROP            # underside of the top plate; gusset bottom at z = 0
R2 = math.sqrt(2)

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene


def prism(name, base, ext):
    """base: list of 3D points (mm) of a planar polygon, ext: extrusion vector (mm)."""
    me = bpy.data.meshes.new(name)
    n = len(base)
    ev = Vector(ext)
    verts = [Vector(p) * S for p in base] + [(Vector(p) + ev) * S for p in base]
    faces = [list(range(n))[::-1], [i + n for i in range(n)]]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, j + n, i + n])
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    scn.collection.objects.link(o)
    return o


def box(name, x0, x1, y0, y1, z0, z1):
    return prism(name, [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], (0, 0, z1 - z0))


parts = []
zt = Z_UNDER
# rev 1 (Sabry, 15 Nov 2026): one triangle sheet bent 90 degrees along K-L.
# horizontal top K-R-L (K = wall corner at the origin, R on wall A, L on wall B), 2 mm, underside at z = 150
parts.append(prism("top_plate", [(0, 0, zt), (LEG, 0, zt), (0, LEG, zt)], (0, 0, T)))
# vertical plate K-L-P flat on wall B (plane x = 0): top edge K-L = 220, vertical edge K-P = 150 in the corner, sloped edge L-P
parts.append(prism("wall_plate", [(0, 0, zt), (0, LEG, zt), (0, 0, 0)], (T, 0, 0)))
# 15 mm flange on the right leg K-R, against wall A, 200 long, hidden under the top
parts.append(box("flange_a", 10, LEG - 10, 0, T, zt - FL, zt))

bpy.ops.object.select_all(action="DESELECT")
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
shelf = bpy.context.active_object
shelf.name = "OBJ-164_shelf"
bev = shelf.modifiers.new("bevel", "BEVEL")
bev.width = 0.2 * S; bev.segments = 2; bev.limit_method = "ANGLE"
bpy.ops.object.modifier_apply(modifier="bevel")
for poly in shelf.data.polygons:
    poly.use_smooth = False


def mat(name, color, metallic=0.0, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    return m


if mode == "grey":
    shelf.data.materials.append(mat("grey", (0.45, 0.45, 0.45, 1), 0.0, 0.75))
else:
    m = bpy.data.materials.new("brushed_steel")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.72, 0.72, 0.73, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Anisotropic"].default_value = 0.6
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1, 400, 1)
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 40; nz.inputs["Detail"].default_value = 8
    ramp = nt.nodes.new("ShaderNodeMapRange"); ramp.inputs["To Min"].default_value = 0.22; ramp.inputs["To Max"].default_value = 0.38
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Value"]); nt.links.new(ramp.outputs["Result"], b.inputs["Roughness"])
    shelf.data.materials.append(m)

# walls: plain context planes behind the shelf (not part of the product)
wallm = mat("wall", (0.60, 0.60, 0.60, 1) if mode == "grey" else (0.90, 0.88, 0.84, 1), 0.0, 0.95)
for w in (box("wall_a", -20, 420, -20, 0, -60, 300), box("wall_b", -20, 0, 0, 420, -60, 300)):
    w.data.materials.append(wallm)

world = bpy.data.worlds.new("w"); scn.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.85, 0.85, 0.85, 1); bg.inputs["Strength"].default_value = 0.2


def area(name, loc, size, energy):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.active_object; l.name = name
    l.data.size = size; l.data.energy = energy
    l.rotation_euler = (Vector((0.07, 0.07, 0.08)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


area("key", (0.8, 0.2, 0.9), 0.9, 5)
area("fill", (0.2, 0.9, 0.5), 0.9, 2.5)
area("front", (0.8, 0.8, 0.5), 1.0, 3)

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data); scn.collection.objects.link(cam); scn.camera = cam
tgt = Vector((0.07, 0.07, 0.10))


def shoot(name, loc, lens=60, ortho=0.0, target=None):
    cam_data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam_data.ortho_scale = ortho
    cam_data.lens = lens
    cam.location = loc
    t = target if target is not None else tgt
    cam.rotation_euler = (t - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = f"{out}/OBJ-164_{mode}_{name}.png"
    bpy.ops.render.render(write_still=True)


scn.render.engine = "CYCLES"
scn.cycles.device = "CPU"
scn.cycles.samples = 32
scn.cycles.use_denoising = True
scn.render.resolution_x = 900
scn.render.resolution_y = 1100
scn.view_settings.view_transform = "Standard" if mode == "grey" else "AgX"

shoot("front", (1.1, 1.1, 0.10), lens=120, ortho=0.5)                 # along the corner diagonal
shoot("left-wall", (1.2, 0.11, 0.10), lens=120, ortho=0.5, target=Vector((0.0, 0.11, 0.10)))   # plate in true shape
shoot("right-wall", (0.11, 1.2, 0.10), lens=120, ortho=0.5, target=Vector((0.11, 0.0, 0.10)))   # plate edge-on, flange side
shoot("three-quarter", (0.50, 0.60, 0.30), lens=45)
shoot("underside", (0.30, 0.28, -0.12), lens=35, target=Vector((0.06, 0.06, 0.06)))   # plate and flange from below
