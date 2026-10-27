"""Does a polished floor read as the comps' shiny floor, before any generator is changed? Copies of the walked preview,
one change each through an autoload, shot at the walker's supermarket station.

    python docs/findings/shiny_floor/gloss_arms.py

The walker, 2026-10-26: "shiny floor, bright lights, isles, glowing freezer section, stacked high"
(docs/reference/GROCERY_STORE_COMPS.md: pale VCT polished until it mirrors each fluorescent run as a streak).
`floor_material_probe.gd` read the supermarket's floor as `M_Skin_tile_delco_1997`, roughness 1.0 times
`vct_floor_beige_roughness_*.png` (Pixelcoat's profile: base 0.35), under the room's ReflectionProbe at intensity 1.0,
interior, box projection OFF, updated once.

ARMS (each a copy of the walked preview; the autoload `gloss_arm.gd` changes the loaded scene, nothing is re-baked):
  shipped      the preview as walked -- the control, shot in place
  noop         a copy with the autoload doing nothing -- proves the copy and the autoload change no pixel
  box          every ReflectionProbe's box projection on
  rough12      every VCT floor material: roughness texture dropped, roughness 0.12
  rough12_box  both

Prints each arm's frame mean and p50 and writes the frames; draws no conclusion. Copies are deleted once shot.
Writes `gloss_arms.out.json` beside itself.
"""
import json
import pathlib
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[2]
SRC = F / "levels" / "restaurant_row" / "workspace" / ".level_factory" / "preview" / "restaurant_row_001_walk"
WORK = F / "_scratch" / "shiny_floor"
STATIONS = ["walker_sales:24.4,1.6,-6.8,0.0,1.2,-6.8", "sales_low:20.0,1.0,-12.0,0.0,0.2,-12.0"]
ARMS = {"noop": "", "box": "box", "rough12": "rough", "rough12_box": "rough box"}

AUTOLOAD = '''extends Node
## gloss_arms.py's arm: %(what)r. Changes the scene as it loads; nothing is saved.

const WHAT := %(what)r


func _ready() -> void:
	get_tree().node_added.connect(_on_added)


func _on_added(n: Node) -> void:
	if "box" in WHAT and n is ReflectionProbe:
		(n as ReflectionProbe).box_projection = true
	var mi: MeshInstance3D = n as MeshInstance3D
	if "rough" in WHAT and mi != null and mi.mesh != null:
		for s in range(mi.mesh.get_surface_count()):
			var m: BaseMaterial3D = mi.get_active_material(s) as BaseMaterial3D
			if m != null and m.roughness_texture != null and m.roughness_texture.resource_path.find("vct_floor") >= 0:
				var c: BaseMaterial3D = m.duplicate() as BaseMaterial3D
				c.roughness_texture = null
				c.roughness = 0.12
				mi.set_surface_override_material(s, c)
'''

sys.path.insert(0, str(F / "tools"))
import look_shots  # noqa: E402


def shoot(project, out):
    r = look_shots.shoot(str(project), str(out), stations=STATIONS, timeout=900)
    return {s["name"]: {"mean": round(s["mean"], 1), "p50": s["p50"], "png": s.get("png") or s.get("path")}
            for s in r.get("shots", []) if s.get("name") in ("walker_sales", "sales_low")}


results = {"shipped": shoot(SRC, WORK / "shots_shipped")}
print("shipped", results["shipped"], flush=True)
for arm, what in ARMS.items():
    dest = WORK / ("copy_" + arm)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SRC, dest)
    (dest / "gloss_arm.gd").write_text(AUTOLOAD % {"what": what}, encoding="utf-8")
    proj = dest / "project.godot"
    text = proj.read_text(encoding="utf-8")
    entry = 'GlossArm="*res://gloss_arm.gd"\n'
    if "[autoload]" in text:
        text = text.replace("[autoload]\n", "[autoload]\n\n" + entry, 1)
    else:
        text = text.rstrip("\n") + "\n\n[autoload]\n\n" + entry
    proj.write_text(text, encoding="utf-8")
    results[arm] = shoot(dest, WORK / ("shots_" + arm))
    print(arm, results[arm], flush=True)
    shutil.rmtree(dest, ignore_errors=True)
(HERE / "gloss_arms.out.json").write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
