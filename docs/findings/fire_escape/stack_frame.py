"""Inside Blender: a fire escape stacked as a walk-up stands it, framed from the sidewalk (roadmaps 156 and 241).

    blender -b --factory-startup --python docs/findings/fire_escape/stack_frame.py -- <zoo root> <out.png> [view]

Builds Zoo's `fire_escape` forms with Zoo's own `prim_mesh`, one storey a box, as Deli Counter is to stand them on a
five-storey walk-up with 3.1 m storeys: flights `a`, `b`, `a` from the second floor's level, the top landing (`top_b`,
where the last flight comes up) on the fifth, and the drop ladder under the lowest landing's hatch, its foot 2.2 m
over the sidewalk. Behind it a brick-red wall with the bay's windows dark; a ground. Workbench, studio light, object
colour: it shows form, not the shipped look. Views: `street` (from the far curb, 1.7 m up, default) or `near`
(3 m out, under the drop). Prints the stack's parts and triangles. It names no verdict.
"""
import math
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
ZOO, OUT = argv[0], argv[1]
VIEW = argv[2] if len(argv) > 2 else "street"
sys.path.insert(0, ZOO)

import bpy  # noqa: E402

from zoo_keeper.bpylayer import prim_mesh  # noqa: E402
from zoo_keeper.core import fire_escape_forms as F  # noqa: E402

STOREY, FLOORS, W, D = 3.1, 5, 2.8, 1.2
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection


class _Streams:
    def stream(self, name):
        import random
        return random.Random(name)


def _mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1.0)
    return m


STEEL = _mat("steel", (0.05, 0.05, 0.055))
BRICK = _mat("brick", (0.42, 0.16, 0.11))
GLASS = _mat("glass", (0.03, 0.04, 0.05))
GROUND = _mat("ground", (0.35, 0.35, 0.33))


def place(form, w, d, h, centre):
    got = F.plan(w, d, h, form)
    plan = {"dimensions": {"width": w, "depth": d, "height": h}, "material": "metal_painted", "color": [0.05] * 3,
            "bevel": 0.0, "wear": 0.0}
    objs = prim_mesh.build(got["prims"], col, plan, _Streams().stream("wear"),
                           {F.MAT: ("M_FireEscape", [0.05, 0.05, 0.055], "metal_painted")}, texel=1.2)
    for o in objs:
        o.location = centre
        o.data.materials.clear()
        o.data.materials.append(STEEL)
    return got["facts"]["tris"]


def box(name, centre, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=centre)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    o.data.materials.append(mat)
    return o


# the stack, in the module frame: X along the wall, the wall at +Y (y = D / 2), Z up; Blender's frame is the same
tris, parts = 0, []
seq = ["flight_a", "flight_b", "flight_a"]
for i, form in enumerate(seq):
    z0 = (i + 1) * STOREY
    tris += place(form, W, D, STOREY, (0.0, 0.0, z0 + STOREY / 2))
    parts.append((form, round(z0, 2)))
top_form = "top_b" if seq[-1] == "flight_a" else "top_a"
th = round(F.FRAME + F.GUARD_H + F.POST_PROUD, 4)
z0 = (len(seq) + 1) * STOREY
tris += place(top_form, W, D, th, (0.0, 0.0, z0 + th / 2))
parts.append((top_form, round(z0, 2)))
# the drop under the lowest landing's hatch: `a`'s hatch is at -X, in the stair band
yb0, yb1 = F._band(D)
dx = -W / 2 + (F.FRAME + F.HATCH) / 2
dh = 0.9
tris += place("drop", 0.45, 0.05, dh, (dx, (yb0 + yb1) / 2, STOREY + F.SINK - dh / 2))
parts.append(("drop", round(STOREY - dh, 2)))

# the wall behind, its face at y = D / 2, five storeys and a parapet; the bay's windows dark
wall_t = 0.3
box("wall", (0.0, D / 2 + wall_t / 2, (FLOORS * STOREY + 1.0) / 2), (16.0, wall_t, FLOORS * STOREY + 1.0), BRICK)
for f in range(FLOORS):
    for bx in (-3.2, 0.0, 3.2):
        box("window_%d_%g" % (f, bx), (bx, D / 2 - 0.01, f * STOREY + 0.9 + 0.75), (1.0, 0.04, 1.5), GLASS)
box("ground", (0.0, -6.0, -0.05), (30.0, 20.0, 0.1), GROUND)

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
col.objects.link(cam)
scene.camera = cam
if VIEW == "near":
    cam.location = (2.5, -3.0, 1.6)
    target = (-0.6, 0.0, 4.5)
    cam_data.lens = 18
else:
    cam.location = (4.0, -14.0, 1.7)
    target = (0.0, 0.0, 7.0)
    cam_data.lens = 26
dx_, dy_, dz_ = (target[0] - cam.location[0], target[1] - cam.location[1], target[2] - cam.location[2])
cam.rotation_euler = (math.atan2(math.hypot(dx_, dy_), -dz_), 0.0, math.atan2(dy_, dx_) - math.pi / 2)

scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.render.resolution_x, scene.render.resolution_y = 1100, 1400
scene.render.filepath = os.path.abspath(OUT)
bpy.ops.render.render(write_still=True)
print("STACK parts %s, %d tris; frame %s (%s)" % (parts, tris, OUT, VIEW))
