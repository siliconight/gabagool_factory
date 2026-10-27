"""Which mesh is the black block at a supermarket gondola's end? Copies of the walker's walk preview, each with ONE
merged mesh painted an unshaded flat colour by an autoload, shot at the station that shows the block.

    python docs/findings/black_gondola_ends/paint_arm.py

`ray_probe.out.txt`: a ray from (3.5, 1.6, 13.0) through the block enters `Level/Bake/Site/b1/MergedR_150` (the
gondola's painted steel, 5,544 verts) at 2.99 m and `MergedR_152` (its snack bags, 25,064 verts) at 3.03 m. Whichever
arm turns the block its colour owns it. Writes frames under `_scratch/black_ends_paint/` and `paint_arm.out.json`;
draws no conclusion.
"""
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[2]
SRC = F / "levels" / "restaurant_row" / "workspace" / ".level_factory" / "preview" / "restaurant_row_001_walk"
WORK = F / "_scratch" / "black_ends_paint"
STATIONS = ["to_cooler:3.5,1.6,13.0,3.5,1.2,-8.0"]
ARMS = {"steel_red": ("Level/Bake/Site/b1/MergedR_150", "Color(1, 0, 0)"),
        "bags_green": ("Level/Bake/Site/b1/MergedR_152", "Color(0, 1, 0)"),
        # its OWN material, unshaded: albedo texture x vertex colour with no light at all
        "steel_own_unshaded": ("Level/Bake/Site/b1/MergedR_150", "OWN")}
if len(sys.argv) > 1:
    ARMS = {k: v for k, v in ARMS.items() if k in sys.argv[1:]}

AUTOLOAD = '''extends Node
## paint_arm.py: %(path)s painted an unshaded flat %(col)s once the scene is up; nothing is saved.


func _ready() -> void:
	for i in range(20):
		await get_tree().process_frame
	var mi: MeshInstance3D = _find(get_tree().root)
	if mi == null:
		push_error("paint_arm: no %(path)s")
		return
	var m: StandardMaterial3D
	if "%(col)s" == "OWN":
		m = (mi.get_active_material(0) as StandardMaterial3D).duplicate() as StandardMaterial3D
	else:
		m = StandardMaterial3D.new()
		m.albedo_color = Color.html("%(col)s") if "%(col)s".begins_with("#") else %(colexpr)s
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mi.material_override = m


func _find(n: Node) -> MeshInstance3D:
	var p: String = String(n.get_path())
	if p.ends_with("%(path)s") and n is MeshInstance3D:
		return n as MeshInstance3D
	for c in n.get_children():
		var got: MeshInstance3D = _find(c)
		if got != null:
			return got
	return null
'''

sys.path.insert(0, str(F / "tools"))
import look_shots  # noqa: E402

out = {}
for arm, (path, col) in ARMS.items():
    dest = WORK / ("copy_" + arm)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SRC, dest)
    (dest / "paint_arm.gd").write_text(AUTOLOAD % {"path": path, "col": col,
                                                    "colexpr": "Color(1, 1, 1)" if col == "OWN" else col},
                                       encoding="utf-8")
    proj = dest / "project.godot"
    text = proj.read_text(encoding="utf-8")
    entry = 'PaintArm="*res://paint_arm.gd"\n'
    text = (text.replace("[autoload]\n", "[autoload]\n\n" + entry, 1) if "[autoload]" in text
            else text.rstrip("\n") + "\n\n[autoload]\n\n" + entry)
    proj.write_text(text, encoding="utf-8")
    r = look_shots.shoot(str(dest), str(WORK / ("shots_" + arm)), stations=STATIONS, timeout=900)
    out[arm] = {s["name"]: [round(s["mean"], 1), s["p50"], s.get("png")] for s in r.get("shots", [])
                if s["name"] == "to_cooler"}
    shutil.rmtree(dest, ignore_errors=True)
print(json.dumps({k: {n: v[:2] for n, v in d.items()} for k, d in out.items()}))
(HERE / ("paint_arm%s.out.json" % ("_" + "_".join(sys.argv[1:]) if len(sys.argv) > 1 else ""))).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
