"""Does the light bake reproduce an interior lamp's own light?

    python fixture_control.py <dir> [--godot EXE]

A 20 x 12 m grey floor (albedo 0.5, Lambert, no specular, UV2 by
`add_uv2`) and nothing else -- no walls, no ceiling, no hardware, so there
is nothing for a lamp to hide inside and nothing to bounce from but the
floor itself. On it, two downward spots with Lux's own numbers as the walk
copy of cold run 9190 ships them (presentation/lux.applied.tscn):

  Lamp_fluorescent  Fluorescent (baked): 2.65 m (anchor 2.9, mount -0.25),
                    energy 3.7 (1.0 x Blue Hour's fluorescent scale 3.7),
                    range 4.0, attenuation 2.0, cone 89, rim 0.125
  Lamp_bare_bulb    Bare Bulb (baked): 2.3 m, energy 1.3, range 3.5,
                    attenuation 1.0 (the rig's default), cone 89, rim 0.125

Baked by Level Factory's own plugin and settings (light_bake.py: quality 0,
2 bounces, 4096, environment off, denoiser on), then shot twice in GL
Compatibility by fixture_shoot.gd: with the lightmap, and with the
LightmapGI freed so the same static lamps light the floor in real time.
Prints what the frames measured; the ratio is the reader's.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

FACTORY = Path(r"C:\Projects\gabagool_studios\gabagool_factory")
sys.path.insert(0, str(FACTORY / "level_factory"))
from packages.exporting import light_bake as LB   # noqa: E402

HERE = Path(__file__).resolve().parent
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
BEGIN, END = "<<<FIXTURE_SHOOT_JSON", "FIXTURE_SHOOT_JSON>>>"

SCENE = """[gd_scene load_steps=3 format=3]

[sub_resource type="PlaneMesh" id="floor"]
add_uv2 = true
size = Vector2(20, 12)

[sub_resource type="StandardMaterial3D" id="grey"]
diffuse_mode = 1
specular_mode = 2
albedo_color = Color(0.5, 0.5, 0.5, 1)
roughness = 1.0

[node name="Bake" type="Node3D"]

[node name="Floor" type="MeshInstance3D" parent="."]
mesh = SubResource("floor")
surface_material_override/0 = SubResource("grey")

[node name="Lamp_fluorescent" type="SpotLight3D" parent="."]
transform = Transform3D(1, 0, 0, 0, -4.371139e-08, 1, 0, -1, -4.371139e-08, -4, 2.65, 0)
light_color = Color(0.965, 0.8739275, 0.64569217, 1)
light_energy = 3.7
light_bake_mode = 1
spot_range = 4.0
spot_attenuation = 2.0
spot_angle = 89.0
spot_angle_attenuation = 0.125

[node name="Lamp_bare_bulb" type="SpotLight3D" parent="."]
transform = Transform3D(1, 0, 0, 0, -4.371139e-08, 1, 0, -1, -4.371139e-08, 4, 2.3, 0)
light_color = Color(1, 0.6538038, 0.34276664, 1)
light_energy = 1.3
light_bake_mode = 1
spot_range = 3.5
spot_attenuation = 1.0
spot_angle = 89.0
spot_angle_attenuation = 0.125

[node name="Lightmap" type="LightmapGI" parent="."]
quality = {quality}
bounces = {bounces}
directional = false
use_denoiser = true
max_texture_size = {max_texture}
environment_mode = 0
"""


def build(d: Path) -> None:
    if d.exists():
        shutil.rmtree(d)
    (d / LB.PLUGIN_DIR).mkdir(parents=True)
    (d / "project.godot").write_text(
        'config_version=5\n\n[application]\n\nconfig/name="fixture_control"\n'
        'config/features=PackedStringArray("4.7")\n\n[rendering]\n\n'
        'renderer/rendering_method="forward_plus"\n\n[editor_plugins]\n\n'
        'enabled=PackedStringArray("res://%s/plugin.cfg")\n' % LB.PLUGIN_DIR,
        encoding="utf-8", newline="\n")
    (d / "bake.tscn").write_text(SCENE.format(quality=LB.QUALITY, bounces=LB.BOUNCES,
                                              max_texture=LB.MAX_TEXTURE), encoding="utf-8", newline="\n")
    shutil.copy(LB.PLUGIN_SCRIPT, d / LB.PLUGIN_DIR / "light_bake_plugin.gd")
    (d / LB.PLUGIN_DIR / "plugin.cfg").write_text(
        '[plugin]\n\nname="lf_light_bake"\ndescription="Bakes bake.tscn and quits."\n'
        'author="level_factory"\nversion="1"\nscript="light_bake_plugin.gd"\n',
        encoding="utf-8", newline="\n")
    shutil.copy(HERE / "fixture_shoot.gd", d / "fixture_shoot.gd")


def shoot(d: Path, godot: str, mode: str) -> list:
    cmd = [godot, "--path", str(d), "--rendering-method", "gl_compatibility",
           "--resolution", "400x400", "--script", "res://fixture_shoot.gd", "--",
           mode, str(d / "shot").replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    out = (r.stdout or "") + (r.stderr or "")
    m = re.search(re.escape(BEGIN) + r"\s*(.*?)\s*" + re.escape(END), out, re.S)
    if m is None:
        raise SystemExit("no result fence from the %s shot; Godot exited %s:\n%s"
                         % (mode, r.returncode, "\n".join(out.splitlines()[-20:])))
    rows = json.loads(m.group(1))
    if isinstance(rows, dict):
        raise SystemExit("the %s shot refused: %s" % (mode, rows))
    return rows


def main(argv):
    d = Path(argv[0]).resolve()
    godot = argv[argv.index("--godot") + 1] if "--godot" in argv else GODOT
    build(d)
    subprocess.run([godot, "--headless", "--path", str(d), "--import"],
                   capture_output=True, text=True, timeout=600)
    code, took = LB._run([godot, "--editor", "--path", str(d), "--resolution", "1280x720"],
                         LB.EDITOR_TIMEOUT_S)
    res = d / LB.RESULT
    result = json.loads(res.read_text(encoding="utf-8")) if res.exists() else None
    print("bake: editor exit %s after %.0f s; %s" % (code, took, result))
    if not result or not result.get("ok"):
        raise SystemExit("the control did not bake")
    rows = shoot(d, godot, "baked") + shoot(d, godot, "unbaked")
    print("%-18s %-8s %8s %10s %8s" % ("lamp", "mode", "centre", "one metre", "frame"))
    for r in sorted(rows, key=lambda r: (r["lamp"], r["mode"])):
        print("%-18s %-8s %8.2f %10.2f %8.2f" % (r["lamp"], r["mode"], r["centre"], r["one_metre"], r["frame"]))
    (d / "fixture_control.json").write_text(json.dumps({"bake": result, "shots": rows}, indent=1),
                                            encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
