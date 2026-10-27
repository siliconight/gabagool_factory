"""The walker's floor, with a plain VCT in place of the checker: one copy of a walk preview, its VCT material's albedo
swapped at load for a re-tuned Pixelcoat profile's and polished, shot at the walker's station beside the copy as it
was.

    python docs/findings/shiny_floor/vct_arm.py <walk copy> <albedo png> <tag>

The walker, 2026-10-26, on `frames/01_floor_40_lamps_shipped_vs_polished.png`: "better, it wouldn't be this tile
pattern though..." and "but the finish/shine looks right". The profile is `vct_plain.json` beside this file, rendered
with `pixelcoat proc-pack`; the arm drops the roughness texture for roughness 0.12, as `gloss_arms.py`'s `rough12`.
Writes the frames under `_scratch/vct_<tag>/` and `vct_arm_<tag>.out.json` beside itself; draws no conclusion.
"""
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[2]
SRC, PNG, TAG = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
WORK = F / "_scratch" / ("vct_" + TAG)
STATIONS = ["walker_sales:24.4,1.6,-6.8,0.0,1.2,-6.8", "to_cooler:3.5,1.6,13.0,3.5,1.2,-8.0"]

AUTOLOAD = '''extends Node
## vct_arm.py: the VCT floor's albedo swapped for res://vct_plain_albedo.png and polished, as the scene loads.

var _tex: Texture2D


func _ready() -> void:
	_tex = ImageTexture.create_from_image(Image.load_from_file("res://vct_plain_albedo.png"))
	get_tree().node_added.connect(_on_added)


func _on_added(n: Node) -> void:
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi == null or mi.mesh == null:
		return
	for s in range(mi.mesh.get_surface_count()):
		var m: BaseMaterial3D = mi.get_active_material(s) as BaseMaterial3D
		if m != null and m.roughness_texture != null and m.roughness_texture.resource_path.find("vct_floor") >= 0:
			var c: BaseMaterial3D = m.duplicate() as BaseMaterial3D
			c.albedo_texture = _tex
			c.roughness_texture = null
			c.roughness = 0.12
			mi.set_surface_override_material(s, c)
'''

sys.path.insert(0, str(F / "tools"))
import look_shots  # noqa: E402

results = {}
r = look_shots.shoot(str(SRC), str(WORK / "shots_shipped"), stations=STATIONS, timeout=900)
results["shipped"] = {s["name"]: [round(s["mean"], 1), s["p50"], s.get("png")] for s in r.get("shots", [])
                      if s["name"] in ("walker_sales", "to_cooler")}
dest = WORK / "copy"
if dest.exists():
    shutil.rmtree(dest)
shutil.copytree(SRC, dest)
shutil.copy2(PNG, dest / "vct_plain_albedo.png")
(dest / "vct_arm.gd").write_text(AUTOLOAD, encoding="utf-8")
proj = dest / "project.godot"
text = proj.read_text(encoding="utf-8")
entry = 'VctArm="*res://vct_arm.gd"\n'
text = (text.replace("[autoload]\n", "[autoload]\n\n" + entry, 1) if "[autoload]" in text
        else text.rstrip("\n") + "\n\n[autoload]\n\n" + entry)
proj.write_text(text, encoding="utf-8")
r = look_shots.shoot(str(dest), str(WORK / "shots_vct"), stations=STATIONS, timeout=900)
results["vct_plain"] = {s["name"]: [round(s["mean"], 1), s["p50"], s.get("png")] for s in r.get("shots", [])
                        if s["name"] in ("walker_sales", "to_cooler")}
shutil.rmtree(dest, ignore_errors=True)
print(json.dumps(results, indent=1))
(HERE / ("vct_arm_%s.out.json" % TAG)).write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
