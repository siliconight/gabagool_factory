"""Render a building shell and its dressing from across the street and from
above, under Blender's workbench -- shapes and textures, not the game's
lighting. Run by `preflight_roof.py`:

    blender --background --python render_roof.py -- <shell.glb> <dressing.glb> <out prefix>

Both GLBs import into Blender's Z-up frame, which is Deli Counter's spec
frame: the front of a rowhome Empty is its S face, at -y. The street view
stands an eye at 1.6 m, 14 m out from that face -- across the road, where a
player stands -- looking up at the SHELL's roofline (measured before the
dressing is imported, so a mast cannot lift the aim); the second view is from
above the front corner. Writes <out prefix>_street.png and _above.png.
"""
import math
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
shell, dressing, prefix = argv[0], argv[1], argv[2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=shell)
body = [o for o in bpy.context.scene.objects if o.type == "MESH"]
zs = [(o.matrix_world @ v.co).z for o in body for v in o.data.vertices]
ys = [(o.matrix_world @ v.co).y for o in body for v in o.data.vertices]
top, front = max(zs), min(ys)
bpy.ops.import_scene.gltf(filepath=dressing)
n = sum(1 for o in bpy.context.scene.objects if o.type == "MESH")
print(f"[render] shell {len(body)} meshes, with dressing {n}; shell top z {top:.2f}, front y {front:.2f}")

scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "TEXTURE"
scene.display.shading.show_cavity = True
scene.render.resolution_x, scene.render.resolution_y = 1280, 720
world = bpy.data.worlds.new("w")
scene.world = world
world.color = (0.05, 0.06, 0.09)

cam_data = bpy.data.cameras.new("cam")
cam_data.angle = math.radians(65.0)
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam


def shoot(loc, look_at, name):
    cam.location = loc
    d = [look_at[i] - loc[i] for i in range(3)]
    yaw = math.atan2(d[1], d[0]) - math.pi / 2.0
    pitch = math.atan2(d[2], math.hypot(d[0], d[1]))
    cam.rotation_euler = (math.pi / 2.0 + pitch, 0.0, yaw)
    scene.render.filepath = f"{prefix}_{name}.png"
    bpy.ops.render.render(write_still=True)
    print(f"[render] wrote {scene.render.filepath}")


shoot((0.0, front - 14.0, 1.6), (0.0, front, top - 1.0), "street")
shoot((-9.0, front - 9.0, top + 7.0), (0.0, front + 3.0, top), "above")
