"""The bake probe's control: the smallest scene a LightmapGI bakes -- a
plane and a box with lightmap UVs, one static omni -- in a Forward+
project with the same `bake_probe` plugin. If this does not bake, the
instrument is wrong, not the site.

    python make_control.py <dir>
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SCENE = """[gd_scene load_steps=4 format=3]

[sub_resource type="PlaneMesh" id="plane"]
add_uv2 = true
size = Vector2(20, 20)

[sub_resource type="BoxMesh" id="box"]
add_uv2 = true
size = Vector3(2, 2, 2)

[sub_resource type="StandardMaterial3D" id="grey"]
albedo_color = Color(0.6, 0.6, 0.6, 1)

[node name="Bake" type="Node3D"]

[node name="Ground" type="MeshInstance3D" parent="."]
mesh = SubResource("plane")
surface_material_override/0 = SubResource("grey")

[node name="Box" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0)
mesh = SubResource("box")
surface_material_override/0 = SubResource("grey")

[node name="Lamp" type="OmniLight3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 3, 4, 2)
light_energy = 4.0
omni_range = 12.0
light_bake_mode = 1

[node name="Lightmap" type="LightmapGI" parent="."]
quality = 0
bounces = 2
max_texture_size = 2048
environment_mode = 0
"""


def main():
    d = sys.argv[1]
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "addons", "bake_probe"))
    open(os.path.join(d, "project.godot"), "w", encoding="utf-8", newline="\n").write(
        'config_version=5\n\n[application]\n\nconfig/name="bake_control"\nconfig/features=PackedStringArray("4.7")\n\n'
        '[rendering]\n\nrenderer/rendering_method="forward_plus"\n\n'
        '[editor_plugins]\n\nenabled=PackedStringArray("res://addons/bake_probe/plugin.cfg")\n')
    open(os.path.join(d, "bake.tscn"), "w", encoding="utf-8", newline="\n").write(SCENE)
    shutil.copy(os.path.join(HERE, "bake_plugin.gd"), os.path.join(d, "addons", "bake_probe", "bake_plugin.gd"))
    open(os.path.join(d, "addons", "bake_probe", "plugin.cfg"), "w", encoding="utf-8", newline="\n").write(
        '[plugin]\n\nname="bake_probe"\ndescription="Bakes bake.tscn and quits."\n'
        'author="factory"\nversion="1"\nscript="bake_plugin.gd"\n')
    print("CONTROL written", d)


if __name__ == "__main__":
    main()
