"""Roadmap 307's sky life on a COPY of a walk copy (never a tool repo, never a shipped walk copy): a flock
(`birds.gdshader`, one MultiMesh of BIRDS quads) and an airliner on an approach track (`airliner.gdshader`, one
MultiMesh of seven unit boxes). Two draws a level, whatever the number of birds; no script, no per-frame CPU.

    python proto_sky.py <walk copy> <centre x,z> [pin [bearing_deg]]

`pin` holds both clocks for proof frames: the flock mid-crossing and the airliner at its track's nearest point, both
on one bearing (degrees from +X toward +Z; 270 is north, -Z; default 300). Without it they run on the clock.
Anchored; refuses on a miss.
"""
import pathlib
import shutil
import sys

W = pathlib.Path(sys.argv[1])
cx, cz = (float(v) for v in sys.argv[2].split(","))
PIN = len(sys.argv) > 3 and sys.argv[3] == "pin"
BEARING = float(sys.argv[4]) if len(sys.argv) > 4 else 300.0
assert "_scratch" in str(W.resolve()), "the prototype goes on a scratch copy only"
HERE = pathlib.Path(__file__).resolve().parent
BIRDS = 30

(W / "sky_life").mkdir(exist_ok=True)
for n in ("birds.gdshader", "airliner.gdshader"):
    shutil.copy2(HERE / n, W / "sky_life" / n)


def row(s, o, c):
    sx, sy, sz = s
    ox, oy, oz = o
    return [sx, 0, 0, ox, 0, sy, 0, oy, 0, 0, sz, oz] + list(c)


BODY = (0.82, 0.83, 0.86, 1.0)
parts = [
    row((3.8, 3.8, 38.0), (0, 0, 0), BODY),             # fuselage, nose at -Z
    row((34.0, 0.5, 5.5), (0, -0.8, 1.0), BODY),        # wing
    row((12.0, 0.4, 3.0), (0, 0.5, 17.0), BODY),        # tailplane
    row((0.4, 6.0, 4.5), (0, 4.0, 17.0), BODY),         # fin
    row((0.8, 0.8, 0.8), (-17.0, -0.8, 1.0), (1.0, 0.1, 0.1, 2.0)),   # port nav, red
    row((0.8, 0.8, 0.8), (17.0, -0.8, 1.0), (0.1, 1.0, 0.2, 3.0)),    # starboard nav, green
    row((0.8, 0.8, 0.8), (0, 7.0, 18.0), (1.0, 1.0, 1.0, 4.0)),       # tail strobe
]
plane_buf = ", ".join("%g" % v for r in parts for v in r)
bird_buf = ", ".join("%g" % v for _ in range(BIRDS) for v in row((1, 1, 1), (0, 0, 0), (0, 0, 0, 0)))

pin_b = "shader_parameter/pin_phase = 0.175\nshader_parameter/pin_angle_deg = %g\n" % BEARING if PIN else ""
# nearest point: u = 0.5, s = 0.5 * track / speed = 33.33 s of a 180 s period
pin_a = "shader_parameter/pin_phase = 0.18518\nshader_parameter/pin_angle_deg = %g\n" % BEARING if PIN else ""

p = W / "_walk.tscn"
b = p.read_bytes()
crlf = b"\r\n" in b
t = b.decode("utf-8").replace("\r\n", "\n")
a1 = '[ext_resource type="Script" path="res://_walk_asset_flags.gd" id="walk_asset_flags"]\n'
a2 = '[node name="_walk" type="Node3D"]\n'
assert t.count(a1) == 1 and t.count(a2) == 1 and "SkyBirds" not in t
t = t.replace(a1, a1 + '[ext_resource type="Shader" path="res://sky_life/birds.gdshader" id="sky_birds_sh"]\n'
              '[ext_resource type="Shader" path="res://sky_life/airliner.gdshader" id="sky_plane_sh"]\n')
t = t.replace(a2, """[sub_resource type="QuadMesh" id="SkyBirdQuad"]
size = Vector2(1, 0.28)
subdivide_width = 1
orientation = 1

[sub_resource type="MultiMesh" id="SkyBirdsMM"]
transform_format = 1
use_custom_data = true
custom_aabb = AABB(-4000, -600, -4000, 8000, 4000, 8000)
instance_count = %d
mesh = SubResource("SkyBirdQuad")
buffer = PackedFloat32Array(%s)

[sub_resource type="ShaderMaterial" id="SkyBirdsMat"]
shader = ExtResource("sky_birds_sh")
shader_parameter/centre = Vector3(%g, 0, %g)
%s
[sub_resource type="BoxMesh" id="SkyPlaneBox"]

[sub_resource type="MultiMesh" id="SkyPlaneMM"]
transform_format = 1
use_custom_data = true
custom_aabb = AABB(-4000, -600, -4000, 8000, 4000, 8000)
instance_count = %d
mesh = SubResource("SkyPlaneBox")
buffer = PackedFloat32Array(%s)

[sub_resource type="ShaderMaterial" id="SkyPlaneMat"]
shader = ExtResource("sky_plane_sh")
shader_parameter/centre = Vector3(%g, 0, %g)
%s
""" % (BIRDS, bird_buf, cx, cz, pin_b, len(parts), plane_buf, cx, cz, pin_a) + a2)
t = t.rstrip("\n") + """

[node name="SkyBirds" type="MultiMeshInstance3D" parent="."]
cast_shadow = 0
gi_mode = 0
ignore_occlusion_culling = true
custom_aabb = AABB(-4000, -600, -4000, 8000, 4000, 8000)
material_override = SubResource("SkyBirdsMat")
multimesh = SubResource("SkyBirdsMM")

[node name="SkyPlane" type="MultiMeshInstance3D" parent="."]
cast_shadow = 0
gi_mode = 0
ignore_occlusion_culling = true
custom_aabb = AABB(-4000, -600, -4000, 8000, 4000, 8000)
material_override = SubResource("SkyPlaneMat")
multimesh = SubResource("SkyPlaneMM")
"""
p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
print("sky life: %d birds, %d aircraft parts, centre %g,%g, %s" % (BIRDS, len(parts), cx, cz,
                                                                    "pinned" if PIN else "on the clock"))
