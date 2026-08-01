"""Put a configured LuxRoot into a walk scene, so F6 is the only click left.

WHY THIS IS SCRIPTABLE AT ALL. Lux's quick start says to add the node, open the
dock, pick a preset and hit Apply. The dock is convenience, not a requirement:

    lux_root.gd:37   @export var apply_on_ready: bool = true
    lux_root.gd:90   func _ready():  ... if apply_on_ready: apply_preset(start)

A LuxRoot carrying an `active_preset` applies itself when the scene runs. So the
whole editor dance reduces to three lines of .tscn.

WHAT IT WIRES, and why each one.

  script          res://addons/lux/runtime/lux_root.gd -- @tool, class_name
                  LuxRoot, extends Node3D. Referenced by script path rather than
                  by `type="LuxRoot"`, because the global class cache may not be
                  populated the first time the project opens.

  active_preset   one of the nine .tres in addons/lux/presets. Nine ship, not
                  the five the README names.

  sun_light       NodePath to the scene's existing Sun. Without this,
                  _resolve_sun_link falls through auto_find_skymint (no SkyMint
                  here) to "the preset's static sun", and Lux adds its own
                  directional light beside Lot's -- two suns, double-lit. Lot's
                  walk scenes always emit a `Sun` DirectionalLight3D, and
                  pointing Lux at it is what the README calls Sun Link.

WHAT IT DELIBERATELY DOES NOT TOUCH. The existing WorldEnvironment stays.
lux_environment.ensure_world_environment() reuses one when the level already has
it -- its own comment says so -- and only creates a LuxWorldEnvironment when
none is found. Removing Lot's would be work for no gain and would lose whatever
Lot set on it.

Idempotent: refuses politely if a LuxRoot is already in the scene. Asserts the
addon and the preset are actually present in the project, because a scene that
references a missing script fails to open with a less obvious error than "the
file is not there".

    python tools\\lux_inject.py <project_dir> [--preset blue_hour] [--scene X.tscn]
"""
import argparse
import pathlib
import re
import sys

SCRIPT_RES = "res://addons/lux/runtime/lux_root.gd"
PRESET_DIR = "addons/lux/presets"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", help="the Godot project folder cater wrote")
    ap.add_argument("--preset", default="delco_summer_afternoon",
                    help="preset stem in addons/lux/presets (default: %(default)s)")
    ap.add_argument("--scene", default=None,
                    help="walk scene name; default is the single *_walk.tscn")
    ap.add_argument("--node-name", default="Lux")
    args = ap.parse_args()

    proj = pathlib.Path(args.project).resolve()
    if not (proj / "project.godot").is_file():
        raise SystemExit(f"no project.godot in {proj} -- that is not a Godot "
                         f"project. Nothing written.")

    addon = proj / "addons" / "lux" / "runtime" / "lux_root.gd"
    if not addon.is_file():
        raise SystemExit(f"missing {addon}.\n  Copy addons\\lux into the project "
                         f"first (scripts\\lux_dress.ps1 does it).\n  A scene "
                         f"pointing at a script that is not there will not open.")

    preset = proj / PRESET_DIR / f"{args.preset}.tres"
    if not preset.is_file():
        have = sorted(p.stem for p in (proj / PRESET_DIR).glob("*.tres"))
        raise SystemExit(f"no preset {args.preset!r}. Available:\n    "
                         + "\n    ".join(have))

    if args.scene:
        scene = proj / args.scene
    else:
        walks = sorted(proj.glob("*_walk.tscn"))
        if len(walks) != 1:
            raise SystemExit(f"expected exactly one *_walk.tscn in {proj}, found "
                             f"{len(walks)}: {[w.name for w in walks]}. "
                             f"Pass --scene.")
        scene = walks[0]

    src = scene.read_text(encoding="utf-8")
    if SCRIPT_RES in src:
        print(f"  {scene.name}: already has a LuxRoot")
        return 0

    m = re.search(r'^\[gd_scene([^\]]*)\]', src, re.M)
    if not m:
        raise SystemExit(f"{scene.name} has no [gd_scene] header -- not a scene "
                         f"file this script understands. Nothing written.")

    # load_steps counts ext+sub resources; two are being added. Godot uses it to
    # size the loader, so leaving it short is not free.
    header = m.group(0)
    ls = re.search(r'load_steps=(\d+)', header)
    if ls:
        new_header = header.replace(f"load_steps={ls.group(1)}",
                                    f"load_steps={int(ls.group(1)) + 2}")
    else:
        new_header = header  # no count declared; Godot copes
    src = src.replace(header, new_header, 1)

    # ext_resource lines must precede the nodes; put them after the last one
    # already there, or straight after the header if the scene has none.
    ext = list(re.finditer(r'^\[ext_resource[^\]]*\]\n', src, re.M))
    inject = (f'[ext_resource type="Script" path="{SCRIPT_RES}" id="luxroot"]\n'
              f'[ext_resource type="Resource" '
              f'path="res://{PRESET_DIR}/{args.preset}.tres" id="luxpreset"]\n')
    at = ext[-1].end() if ext else src.index("\n", m.start()) + 1
    src = src[:at] + inject + src[at:]

    # A Node-typed export is only resolved by Godot's scene loader when the
    # [node] header names it in node_paths. The loader builds its set of
    # node-path properties SOLELY from that field; a property missing from it is
    # assigned literally, so `sun_light = NodePath("../Sun")` becomes a NodePath
    # written into a DirectionalLight3D-typed property. GDScript rejects the
    # type and drops it SILENTLY -- no error, no warning -- so sun_light is null
    # through _ready and ensure_sun() manufactures a LuxSun beside Lot's.
    # Measured on 4.7.stable with this exact block: 2 directional lights without
    # the field, 1 with it. It is also why the editor's re-save of a scene
    # injected the old way drops the sun_light line -- it was never set.
    has_sun = re.search(r'^\[node name="Sun" type="DirectionalLight3D"', src, re.M)
    node_paths = ' node_paths=PackedStringArray("sun_light")' if has_sun else ''
    node = (f'\n[node name="{args.node_name}" type="Node3D" parent="."'
            f'{node_paths}]\n'
            f'script = ExtResource("luxroot")\n'
            f'active_preset = ExtResource("luxpreset")\n')
    if has_sun:
        node += 'sun_light = NodePath("../Sun")\n'
    src = src.rstrip("\n") + "\n" + node

    backup = scene.with_suffix(".tscn.pre_lux")
    if not backup.exists():
        backup.write_text(scene.read_text(encoding="utf-8"), encoding="utf-8")
    scene.write_text(src, encoding="utf-8")

    print(f"  {scene.name}: LuxRoot added")
    print(f"    preset      {args.preset}")
    print(f"    sun_light   " + ("../Sun (Sun Link -- Lux drives Lot's existing "
                                 "sun rather than adding one)"
                                 if has_sun else
                                 "unset -- no Sun node found, Lux will use the "
                                 "preset's own"))
    print(f"    environment left alone; Lux reuses the existing WorldEnvironment")
    print(f"    previous scene kept at {backup.name}")
    lights = sorted(proj.glob("*.site.lights.json"))
    if lights:
        print(f"\n  {lights[0].name} is present, so lux_light_loader has anchors "
              f"to spawn from.")
    else:
        print(f"\n  No *.site.lights.json here -- the look will apply but the "
              f"site's own\n  light anchors will not be spawned (roadmap item 19).")
    print(f"\n  Open the project and press F6 on {scene.name}. No dock needed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
