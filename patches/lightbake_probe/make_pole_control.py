"""The bake probe's pole control: does a lamp inside a closed pole bake to
nothing, and does the same lamp moved out of the pole bake its pool?

    python make_pole_control.py <dir> <lamp x> <lamp y>

A 20 m grey plane, a closed 6 m shaft (radius 0.06, 8 sides, lightmap UVs)
standing at x 0 whose cap is 5 mm under y 6.0 -- Zoo's streetlight at a
slot, where Lux's mount is the lens point 5 mm above the shaft's cap -- and
one static spot pointing down at (<lamp x>, <lamp y>, 0), the streetlight
rig's own numbers. Lux 0.64.0 put the lamp at (0, 5.9): on the axis, 9.5 cm
below the cap, inside the shaft. Same plugin as the site.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SCENE = """[gd_scene load_steps=4 format=3]

[sub_resource type="PlaneMesh" id="plane"]
add_uv2 = true
size = Vector2(20, 20)

[sub_resource type="CylinderMesh" id="shaft"]
add_uv2 = true
top_radius = 0.06
bottom_radius = 0.06
height = 5.995
radial_segments = 8

[sub_resource type="StandardMaterial3D" id="grey"]
albedo_color = Color(0.6, 0.6, 0.6, 1)

[node name="Bake" type="Node3D"]

[node name="Ground" type="MeshInstance3D" parent="."]
mesh = SubResource("plane")
surface_material_override/0 = SubResource("grey")

[node name="Shaft" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2.9975, 0)
mesh = SubResource("shaft")
surface_material_override/0 = SubResource("grey")

[node name="Lamp" type="SpotLight3D" parent="."]
transform = Transform3D(1, 0, 0, 0, -4.371139e-08, 1, 0, -1, -4.371139e-08, {x}, {y}, 0)
light_energy = 19.2
spot_range = 14.0
spot_angle = 55.0
spot_angle_attenuation = 1.2
shadow_enabled = true
light_bake_mode = 1

[node name="Lightmap" type="LightmapGI" parent="."]
quality = 0
bounces = 2
max_texture_size = 2048
environment_mode = 0
"""


def main():
    d, x, y = sys.argv[1], sys.argv[2], sys.argv[3]
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "addons", "bake_probe"))
    open(os.path.join(d, "project.godot"), "w", encoding="utf-8", newline="\n").write(
        'config_version=5\n\n[application]\n\nconfig/name="pole_control"\nconfig/features=PackedStringArray("4.7")\n\n'
        '[rendering]\n\nrenderer/rendering_method="forward_plus"\n\n'
        '[editor_plugins]\n\nenabled=PackedStringArray("res://addons/bake_probe/plugin.cfg")\n')
    open(os.path.join(d, "bake.tscn"), "w", encoding="utf-8", newline="\n").write(SCENE.format(x=x, y=y))
    shutil.copy(os.path.join(HERE, "bake_plugin.gd"), os.path.join(d, "addons", "bake_probe", "bake_plugin.gd"))
    open(os.path.join(d, "addons", "bake_probe", "plugin.cfg"), "w", encoding="utf-8", newline="\n").write(
        '[plugin]\n\nname="bake_probe"\ndescription="Bakes bake.tscn and quits."\n'
        'author="factory"\nversion="1"\nscript="bake_plugin.gd"\n')
    print("POLE CONTROL", d, "lamp at", x, y)


if __name__ == "__main__":
    main()
