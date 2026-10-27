"""Are the supermarket's black gondola ends the light bake? One copy of the walker's walk preview whose LuxLighting
nodes have their baked lighting switched off once the scene is up (`LuxLighting.set_baked_lighting(false)`: the
lightmap cleared, every static rig light made dynamic), shot beside the preview as it is.

    python docs/findings/black_gondola_ends/unbaked_arm.py

Seen in the walker's rebuilt level (2026-10-27, `docs/findings/walk_2026-10-26_panel/frames/08_*`, `09_*`): the
gondolas' end panels and the checkout counter render pitch black from the aisle heads. `floor_material_probe.gd` at
the end of `gondola_aisle_2` read `MergedR_150`, `M_Skin_metal_painted_delco_1997_ffffff`; Zoo's `snack_gondola`
paints its end panels steel at 0.72 grey, so the black is not the albedo. Writes frames under
`_scratch/black_ends/` and `unbaked_arm.out.json` beside itself; draws no conclusion.
"""
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[2]
SRC = F / "levels" / "restaurant_row" / "workspace" / ".level_factory" / "preview" / "restaurant_row_001_walk"
WORK = F / "_scratch" / "black_ends"
STATIONS = ["to_cooler:3.5,1.6,13.0,3.5,1.2,-8.0", "aisle_heads:-8.0,1.6,14.5,6.0,2.6,4.0"]

AUTOLOAD = '''extends Node
## unbaked_arm.py: every LuxLighting's baked lighting off once the scene is up; nothing is saved.


func _ready() -> void:
	for i in range(30):
		await get_tree().process_frame
	_walk(get_tree().root)


func _walk(n: Node) -> void:
	if n.has_method("set_baked_lighting"):
		n.call("set_baked_lighting", false)
	for c in n.get_children():
		_walk(c)
'''

sys.path.insert(0, str(F / "tools"))
import look_shots  # noqa: E402

out = {}
r = look_shots.shoot(str(SRC), str(WORK / "shots_baked"), stations=STATIONS, timeout=900)
out["baked"] = {s["name"]: [round(s["mean"], 1), s["p50"], s.get("png")] for s in r.get("shots", [])
                if s["name"] in ("to_cooler", "aisle_heads")}
dest = WORK / "copy"
if dest.exists():
    shutil.rmtree(dest)
shutil.copytree(SRC, dest)
(dest / "unbaked_arm.gd").write_text(AUTOLOAD, encoding="utf-8")
proj = dest / "project.godot"
text = proj.read_text(encoding="utf-8")
entry = 'UnbakedArm="*res://unbaked_arm.gd"\n'
text = (text.replace("[autoload]\n", "[autoload]\n\n" + entry, 1) if "[autoload]" in text
        else text.rstrip("\n") + "\n\n[autoload]\n\n" + entry)
proj.write_text(text, encoding="utf-8")
r = look_shots.shoot(str(dest), str(WORK / "shots_unbaked"), stations=STATIONS, timeout=900)
out["unbaked"] = {s["name"]: [round(s["mean"], 1), s["p50"], s.get("png")] for s in r.get("shots", [])
                  if s["name"] in ("to_cooler", "aisle_heads")}
shutil.rmtree(dest, ignore_errors=True)
print(json.dumps({k: {n: v[:2] for n, v in d.items()} for k, d in out.items()}))
(HERE / "unbaked_arm.out.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
