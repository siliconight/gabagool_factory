"""Roadmap item 31, the light-bake probe, step 2: can a bake run unattended?

    python prepare_bake.py <prepared probe dir> <bake dir>

Copies the step-1 probe (static lightmaps set, UV2 imported) to <bake dir>,
keeping its import cache, and:

  * switches the project to Forward+, because only a RenderingDevice can
    bake (the shipped package stays GL Compatibility; step 3 renders the
    bake there);
  * marks every steady Lux rig `bake_mode = 1` (Static: direct and indirect
    baked) in `presentation/lux.applied.tscn`, and leaves the 17 failing
    fixtures' rigs alone, so a stuttering tube or a cycling pole stays live;
  * writes `bake.tscn`: the applied site and one `LightmapGI`;
  * installs and enables `addons/bake_probe`, an editor plugin that opens
    `bake.tscn`, selects the LightmapGI, presses the editor's own Bake
    Lightmaps button (Godot 4.7 exposes no script call for a bake), saves,
    writes `bake_result.json` and quits.

Prints what it changed.
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

BAKE_TSCN = """[gd_scene load_steps=2 format=3]

[ext_resource type="PackedScene" path="res://presentation/lux.applied.tscn" id="site"]

[node name="Bake" type="Node3D"]

[node name="Site" parent="." instance=ExtResource("site")]

[node name="Lightmap" type="LightmapGI" parent="."]
quality = {quality}
bounces = 2
directional = false
use_denoiser = true
max_texture_size = 4096
environment_mode = 0
"""


def main():
    src, dst = sys.argv[1], sys.argv[2]
    quality = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    pg = os.path.join(dst, "project.godot")
    text = open(pg, encoding="utf-8").read()
    text, k = re.subn(r'^renderer/rendering_method="gl_compatibility"$',
                      'renderer/rendering_method="forward_plus"', text, flags=re.M)
    assert k == 1, "renderer line"
    text += '\n[editor_plugins]\n\nenabled=PackedStringArray("res://addons/bake_probe/plugin.cfg")\n'
    open(pg, "w", encoding="utf-8", newline="\n").write(text)
    lux = os.path.join(dst, "presentation", "lux.applied.tscn")
    t = open(lux, encoding="utf-8").read()
    rig_script = re.search(r'\[ext_resource type="Script" path="res://runtime/lux/resources/lux_light_rig.gd" id="([^"]+)"\]', t).group(1)
    blocks = re.split(r"(?=^\[)", t, flags=re.M)
    marked = kept = 0
    for i, b in enumerate(blocks):
        if not b.startswith('[sub_resource type="Resource"') or f'script = ExtResource("{rig_script}")' not in b:
            continue
        if re.search(r"^failing_kind = [1-9]", b, flags=re.M):
            kept += 1
            continue
        assert "bake_mode" not in b
        blocks[i] = b.replace(f'script = ExtResource("{rig_script}")\n',
                              f'script = ExtResource("{rig_script}")\nbake_mode = 1\n', 1)
        marked += 1
    open(lux, "w", encoding="utf-8", newline="\n").write("".join(blocks))
    open(os.path.join(dst, "bake.tscn"), "w", encoding="utf-8", newline="\n").write(
        BAKE_TSCN.format(quality=quality))
    addon = os.path.join(dst, "addons", "bake_probe")
    os.makedirs(addon, exist_ok=True)
    shutil.copy(os.path.join(HERE, "bake_plugin.gd"), os.path.join(addon, "bake_plugin.gd"))
    open(os.path.join(addon, "plugin.cfg"), "w", encoding="utf-8", newline="\n").write(
        '[plugin]\n\nname="bake_probe"\ndescription="Bakes bake.tscn and quits."\n'
        'author="factory"\nversion="1"\nscript="bake_plugin.gd"\n')
    print("BAKEPREP rigs marked static:", marked, " failing rigs left live:", kept, " quality:", quality)


if __name__ == "__main__":
    main()
