"""Roadmap 305's far band as a HORIZON RING, on a COPY of a walk copy (never a tool repo, never a shipped walk copy).
The sky-shader form (`proto_apply.py`) reaches only the two Lux presets that name SkyMint; a level running any other
(cold run 9389's restaurant_row_001 runs `blue_hour`, a ProceduralSkyMaterial) never draws it. A ring draws under any
sky: one open cylinder, faces drawn both sides, RADIUS out from the plate's centre, the strip as its texture --
unshaded, alpha-cut, no fog of its own, no shadow, outside the bake. One mesh, one surface: one draw a level.

    python proto_ring.py <walk copy> <strip png> [radius_m]

Its rows span the strip's elevations from an eye EYE_Y high: BOTTOM_DEG to TOP_DEG (the strip's own, see
strip_proto.py). Anchored; refuses on a miss.
"""
import math
import pathlib
import shutil
import sys

W = pathlib.Path(sys.argv[1])
strip = pathlib.Path(sys.argv[2])
R = float(sys.argv[3]) if len(sys.argv) > 3 else 1500.0
assert "_scratch" in str(W.resolve()), "the prototype goes on a scratch copy only"
EYE_Y, BOTTOM_DEG, TOP_DEG = 1.7, -1.0, 8.0
y0 = EYE_Y + R * math.tan(math.radians(BOTTOM_DEG))
y1 = EYE_Y + R * math.tan(math.radians(TOP_DEG))
H, CY = y1 - y0, (y0 + y1) / 2.0

(W / "vista").mkdir(exist_ok=True)
shutil.copy2(strip, W / "vista" / "ring.png")

p = W / "_walk.tscn"
b = p.read_bytes()
crlf = b"\r\n" in b
t = b.decode("utf-8").replace("\r\n", "\n")
a1 = '[ext_resource type="Script" path="res://_walk_asset_flags.gd" id="walk_asset_flags"]\n'
a2 = '[node name="_walk" type="Node3D"]\n'
assert t.count(a1) == 1 and t.count(a2) == 1 and "VistaRing" not in t
t = t.replace(a1, a1 + '[ext_resource type="Texture2D" path="res://vista/ring.png" id="vista_ring_tex"]\n')
t = t.replace(a2, """[sub_resource type="CylinderMesh" id="VistaRingMesh"]
top_radius = %.3f
bottom_radius = %.3f
height = %.3f
radial_segments = 96
rings = 1
cap_top = false
cap_bottom = false

[sub_resource type="StandardMaterial3D" id="VistaRingMat"]
transparency = 2
alpha_scissor_threshold = 0.5
cull_mode = 2
shading_mode = 0
disable_fog = true
albedo_texture = ExtResource("vista_ring_tex")
texture_filter = 3

""" % (R, R, H) + a2)
t = t.rstrip("\n") + """

[node name="VistaRing" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, %.3f, 0)
cast_shadow = 0
gi_mode = 0
mesh = SubResource("VistaRingMesh")
material_override = SubResource("VistaRingMat")
""" % CY
p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
print("ring: radius %.0f m, y %.1f..%.1f (%.1f m tall), %s" % (R, y0, y1, H, strip.name))
