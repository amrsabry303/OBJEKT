"""OBJ-173 rev 2 (approved 12 Nov 2026) built in Blender from the drawing.
All dimensions in mm, scene scale 0.001 (1 Blender unit = 1 m).
Usage: python obj173_blender.py OUTDIR [grey|steel]
"""
import sys, math, bpy, bmesh
from mathutils import Vector

out = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "grey"
S = 0.001
W = 150.0      # outer cube
T = 2.0        # sheet
OPEN_D = 102.0 # opening
POT_TOP, POT_BASE, POT_H = 100.0, 65.0, 100.0  # bought-in pot, position only

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene


def box(name, x0, x1, y0, y1, z0, z1):
    bpy.ops.mesh.primitive_cube_add()
    o = bpy.context.active_object
    o.name = name
    o.scale = ((x1 - x0) / 2 * S, (y1 - y0) / 2 * S, (z1 - z0) / 2 * S)
    o.location = ((x0 + x1) / 2 * S, (y0 + y1) / 2 * S, (z0 + z1) / 2 * S)
    bpy.ops.object.transform_apply(scale=True)
    return o


h = W / 2
parts = []
parts.append(box("bottom", -h, h, -h, h, 0, T))
parts.append(box("wall_front", -h, h, -h, -h + T, T, W - T))
parts.append(box("wall_back", -h, h, h - T, h, T, W - T))
parts.append(box("wall_left", -h, -h + T, -h + T, h - T, T, W - T))
parts.append(box("wall_right", h - T, h, -(h - T), (h - T), T, W - T))

top = box("top_plate", -h, h, -h, h, W - T, W)
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=OPEN_D / 2 * S, depth=(T * 3) * S,
                                    location=(0, 0, (W - T / 2) * S))
cut = bpy.context.active_object
mod = top.modifiers.new("hole", "BOOLEAN")
mod.operation = "DIFFERENCE"
mod.object = cut
bpy.context.view_layer.objects.active = top
bpy.ops.object.modifier_apply(modifier="hole")
bpy.data.objects.remove(cut, do_unlink=True)
parts.append(top)

# the cube is one welded part: join and bevel the outer edges very slightly (ground weld)
bpy.ops.object.select_all(action="DESELECT")
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
cube = bpy.context.active_object
cube.name = "OBJ-173_cube"
bev = cube.modifiers.new("bevel", "BEVEL")
bev.width = 0.25 * S
bev.segments = 2
bev.limit_method = "ANGLE"
bpy.ops.object.modifier_apply(modifier="bevel")
bpy.ops.object.shade_smooth()
cube.data.polygons.foreach_set("use_smooth", [False] * len(cube.data.polygons))
cube.modifiers.new("edgesplit", "EDGE_SPLIT")

# pot (position only, bought-in)
bpy.ops.mesh.primitive_cone_add(vertices=96, radius1=POT_BASE / 2 * S, radius2=POT_TOP / 2 * S,
                                depth=POT_H * S, location=(0, 0, (T + POT_H / 2) * S))
pot = bpy.context.active_object
pot.name = "pot_position_only"
bpy.ops.object.shade_smooth()

# materials
def mat(name, color, metallic=0.0, rough=0.6, aniso=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    if aniso:
        b.inputs["Anisotropic"].default_value = aniso
    return m

if mode == "grey":
    g = mat("grey", (0.45, 0.45, 0.45, 1), 0.0, 0.75)
    cube.data.materials.append(g)
    pot.data.materials.append(mat("potgrey", (0.55, 0.55, 0.55, 1), 0.0, 0.8))
else:
    # brushed stainless: metallic, anisotropic, fine streak noise
    m = bpy.data.materials.new("brushed_steel")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.72, 0.72, 0.73, 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = 0.30
    b.inputs["Anisotropic"].default_value = 0.6
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1, 400, 1)  # streaks along X
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 40
    nz.inputs["Detail"].default_value = 8
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["To Min"].default_value = 0.22
    ramp.inputs["To Max"].default_value = 0.38
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Value"])
    nt.links.new(ramp.outputs["Result"], b.inputs["Roughness"])
    cube.data.materials.append(m)
    pot.data.materials.append(mat("pot", (0.85, 0.83, 0.78, 1), 0.0, 0.6))

# floor + studio
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "floor"
floor.data.materials.append(mat("floor", (0.30, 0.30, 0.30, 1) if mode == "grey" else (0.55, 0.52, 0.48, 1), 0.0, 0.9))

world = bpy.data.worlds.new("w")
scn.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.85, 0.85, 0.85, 1) if mode == "grey" else (0.82, 0.80, 0.76, 1)
bg.inputs["Strength"].default_value = 0.25

def area(name, loc, size, energy):
    bpy.ops.object.light_add(type="AREA", location=loc)
    l = bpy.context.active_object
    l.name = name
    l.data.size = size
    l.data.energy = energy
    direction = Vector((0, 0, 0.07)) - Vector(loc)
    l.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return l

area("key", (-0.7, -0.8, 0.9), 0.9, 18)
area("fill", (0.9, -0.5, 0.5), 0.9, 6)
area("rim", (0.3, 0.9, 0.8), 0.7, 9)

# camera
cam_data = bpy.data.cameras.new("cam")
cam_data.lens = 70
cam = bpy.data.objects.new("cam", cam_data)
scn.collection.objects.link(cam)
scn.camera = cam
tgt = Vector((0, 0, 0.065))

def shoot(name, loc, lens=70, ortho=False):
    cam_data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam_data.ortho_scale = 0.26
    cam_data.lens = lens
    cam.location = loc
    cam.rotation_euler = (tgt - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = f"{out}/OBJ-173_{mode}_{name}.png"
    bpy.ops.render.render(write_still=True)

scn.render.engine = "CYCLES"
scn.cycles.device = "CPU"
scn.cycles.samples = 32
scn.cycles.use_denoising = True
scn.render.resolution_x = 800
scn.render.resolution_y = 800
scn.view_settings.view_transform = "Standard" if mode == "grey" else "AgX"

d = 0.9
pass
pass
shoot("three-quarter", (-0.5, -0.62, 0.42), lens=65)
pass
