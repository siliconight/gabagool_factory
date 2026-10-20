extends SceneTree
## PROTOTYPE: AN ENTERABLE BUILDING'S STATIC MODULES MERGED PER UNIT AND MATERIAL (the factory's roadmap 266).
## Run on a COPY of an unbaked package, never on a shipped one; it rewrites the scenes it is handed.
##
##     godot --headless --path <copy> --script res://merge_buildings_proto.gd -- <report> <res://lot/<id>/site.tscn> ...
##
## `merge_empties.gd` (Level Factory 0.143.0) with `merge_census.gd`'s classes and units: a slot child that is
## `interactive`, an `opening`, `lit`, `moving`, the `GreyboxBase` or the `Dressing` is left exactly as it is; every
## other one is taken apart -- its StaticBody3D colliders copied out whole under `KitCollision`, in the root's frame,
## and each surface of its other MeshInstance3D nodes appended to the group keyed by (unit, material name, uv1 scale
## and triplanar flags, surface format). A unit is one side of one storey (`ext_<s>_<side>_*`), the roof
## (`parapet_*`, `roof*`), one partition run (`int_<s>_<k>_*`), one furnished room (`*_r<hash>_*`), or else the
## room the piece stands in, read off Deli Counter's own rooms (`rooms.json` beside the scene, which `proto_ab.py`
## writes), and failing a room a `CELL_M` cell of its storey.
##
## AND EVERY ROOM UNIT IS CUT INTO `CELL_M` CELLS of the plan, and the parapet into its four sides (v3): v2's
## rooms paired market_aisles' shelving, one mesh across a 15 x 20 m room, with 14 lights, and one parapet ring with
## 10 -- the meshes over the cap went 9 -> 11.
##
## REFUTED, kept: v1 put a piece named for no wall or room on ONE UNIT A STOREY, by its height against a guessed
## 3.5 m storey (deli_a03's is 3.3). Priced on cold run 9347's package, the storey-wide meshes it made -- the rooms'
## floors and ceilings, stair guards, authored counters -- paired with up to 14 lights against Godot's cap of 8, and
## the merged arm's meshes over the cap went from 9 to 19. Each group becomes one ArrayMesh wearing a duplicate of its first material, unwrapped for its
## lightmap at `TEXEL_M`, saved as `res://lot/<id>/merged/b<n>.res`, under one MeshInstance3D `MergedB_<n>`.
## Its report says per scene what went in and what came out; what it does not measure is what any of it costs or
## buys at run time.

const SCHEMA := "lf.merge_buildings_proto.v1"
const TEXEL_M := 0.2
const LIT_SUFFIXES: Array[String] = ["_Lens", "_Diffuser", "_Face"]
## A piece with no room: one cell this wide on its storey, so no merged mesh spans more than a room would.
const CELL_M := 6.0
## How far outside a room's bounds a piece may stand and still be that room's (a counter against a wall).
const ROOM_SLACK_M := 1.5

var _report: Dictionary = {"schema": SCHEMA, "ok": false, "error": null, "scenes": []}
var _report_path: String = ""
## `--dry` (first argument after the report): group and count, write nothing -- what a merge would make
var _dry := false


func _initialize() -> void:
	_run()


func _write() -> void:
	var f := FileAccess.open(_report_path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(_report, "  "))
		f.close()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _lit(mat: Material) -> bool:
	if mat == null:
		return false
	var nm: String = mat.resource_name
	if not nm.begins_with("M_"):
		return false
	for s in LIT_SUFFIXES:
		if nm.ends_with(s):
			return true
	return false


## Deli Counter's rooms for one building, from `rooms.json` beside its scene: {story_height, rooms: [{id,
## story, bounds [x0, y0, x1, y1]}]} in Deli Counter's frame (Blender Z-up), where a local Godot point (x, y, z)
## is (x, -z) on the plan and storey floor(y / story_height).
func _room_of(origin: Vector3, rooms: Dictionary) -> String:
	var h: float = float(rooms.get("story_height", 0.0))
	if h <= 0.0:
		return ""
	var story: int = int(floor((origin.y + 0.05) / h))
	var px: float = origin.x
	var py: float = -origin.z
	var best := ""
	var best_d := ROOM_SLACK_M
	for r in rooms.get("rooms", []):
		if int(r.get("story", -99)) != story:
			continue
		var b: Array = r.get("bounds", [])
		if b.size() != 4:
			continue
		var dx: float = maxf(maxf(float(b[0]) - px, px - float(b[2])), 0.0)
		var dy: float = maxf(maxf(float(b[1]) - py, py - float(b[3])), 0.0)
		var d: float = sqrt(dx * dx + dy * dy)
		if d < best_d or (d == 0.0 and best_d > 0.0):
			best_d = d
			best = String(r.get("id", ""))
			if d == 0.0:
				break
	var cell := "%d %d" % [int(floor(px / CELL_M)), int(floor(py / CELL_M))]
	if best != "":
		return "room %s %s" % [best, cell]
	return "cell %d %s" % [story, cell]


func _unit(name: String, origin: Vector3, rooms: Dictionary) -> String:
	var parts: PackedStringArray = name.split("_")
	if name.begins_with("ext_") and parts.size() > 2:
		return "ext %s %s" % [parts[1], parts[2]]
	if name.begins_with("int_") and parts.size() > 2:
		return "int %s %s" % [parts[1], parts[2]]
	if name.begins_with("parapet_") and parts.size() > 1:
		return "roof %s" % parts[1]
	if name.begins_with("roof"):
		return "roof"
	for p in parts:
		if p.length() == 9 and p.begins_with("r") and p.substr(1).is_valid_hex_number(false):
			return "room %s %d %d" % [p, int(floor(origin.x / CELL_M)), int(floor(-origin.z / CELL_M))]
	return _room_of(origin, rooms)


func _key(unit: String, mat: Material, fmt: int) -> String:
	var k: String = "%s|%s|%d" % [unit, (mat.resource_name if mat != null else "<none>"), fmt]
	var bm: BaseMaterial3D = mat as BaseMaterial3D
	if bm != null:
		k += "|%s|%s|%s" % [str(bm.uv1_scale), str(bm.uv1_triplanar), str(bm.uv1_world_triplanar)]
	return k


func _static(child: Node, nodes: Array) -> bool:
	var name := String(child.name)
	if name == "GreyboxBase" or name == "Dressing" or name == "KitCollision" or name.begins_with("Merged"):
		return false
	if child.has_meta("interactive_id") or name.find("_open") >= 0:
		return false
	for n in nodes:
		if n is AnimationPlayer or (n as Node).get_script() != null:
			return false
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi != null and mi.mesh != null:
			for s in range(mi.mesh.get_surface_count()):
				if _lit(mi.get_active_material(s)):
					return false
	return true


func _merge_scene(path: String) -> Dictionary:
	var row: Dictionary = {"scene": path, "slots_merged": 0, "meshes_in": 0, "surfaces_in": 0, "merged": 0,
		"unwrapped": 0, "colliders": 0, "error": null}
	var rooms_path: String = path.get_base_dir() + "/rooms.json"
	if not FileAccess.file_exists(rooms_path):
		row["error"] = "no rooms.json beside the scene"
		return row
	var rooms: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(rooms_path)) as Dictionary
	var packed: PackedScene = load(path) as PackedScene
	if packed == null:
		row["error"] = "cannot load"
		return row
	var scene: Node3D = packed.instantiate() as Node3D
	root.add_child(scene)
	await process_frame
	var inv: Transform3D = scene.global_transform.affine_inverse()
	var tools: Dictionary = {}
	var mats: Dictionary = {}
	var collision := Node3D.new()
	collision.name = "KitCollision"
	scene.add_child(collision)
	collision.owner = scene
	var gone: Array = []
	for child in scene.get_children():
		if child == collision:
			continue
		var nodes: Array = []
		_walk(child, nodes)
		if not _static(child, nodes):
			continue
		var origin: Vector3 = (inv * (child as Node3D).global_transform).origin if child is Node3D else Vector3.ZERO
		var unit := _unit(String(child.name), origin, rooms)
		for n in nodes:
			var body: StaticBody3D = n as StaticBody3D
			if body != null:
				var copy: StaticBody3D = body.duplicate() as StaticBody3D
				collision.add_child(copy)
				copy.transform = inv * body.global_transform
				copy.owner = scene
				var kids: Array = []
				_walk(copy, kids)
				for d in kids:
					if d != copy:
						(d as Node).owner = scene
				row["colliders"] = int(row["colliders"]) + 1
				continue
			var mi: MeshInstance3D = n as MeshInstance3D
			if mi == null or mi.mesh == null:
				continue
			var under_body: bool = false
			var p: Node = mi.get_parent()
			while p != null and p != child:
				if p is StaticBody3D:
					under_body = true
				p = p.get_parent()
			if under_body:
				continue
			row["meshes_in"] = int(row["meshes_in"]) + 1
			var xf: Transform3D = inv * mi.global_transform
			for s in range(mi.mesh.get_surface_count()):
				var mat: Material = mi.get_active_material(s)
				var fmt: int = (mi.mesh as ArrayMesh).surface_get_format(s) if mi.mesh is ArrayMesh else 0
				var key: String = _key(unit, mat, fmt)
				if not tools.has(key):
					tools[key] = SurfaceTool.new()
					mats[key] = mat
				(tools[key] as SurfaceTool).append_from(mi.mesh, s, xf)
				row["surfaces_in"] = int(row["surfaces_in"]) + 1
		gone.append(child)
		row["slots_merged"] = int(row["slots_merged"]) + 1
	var by_kind: Dictionary = {}
	for key in tools.keys():
		var kind: String = String(key).split("|")[0].split(" ")[0]
		by_kind[kind] = int(by_kind.get(kind, 0)) + 1
	row["keys_by_unit_kind"] = by_kind
	var sorted_keys: Array = tools.keys()
	sorted_keys.sort()
	row["keys"] = sorted_keys
	if _dry:
		row["merged"] = tools.size()
		scene.queue_free()
		return row
	for g in gone:
		scene.remove_child(g)
		(g as Node).queue_free()
	var dir: String = path.get_base_dir() + "/merged"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(dir))
	var keys: Array = tools.keys()
	keys.sort()
	var k: int = 0
	for key in keys:
		var am: ArrayMesh = (tools[key] as SurfaceTool).commit()
		var src: Material = mats[key]
		if src != null:
			am.surface_set_material(0, src.duplicate(true) as Material)
		if am.lightmap_unwrap(Transform3D.IDENTITY, TEXEL_M) == OK:
			row["unwrapped"] = int(row["unwrapped"]) + 1
		var mesh_path: String = "%s/b%d.res" % [dir, k]
		var err: int = ResourceSaver.save(am, mesh_path)
		if err != OK:
			scene.queue_free()
			row["error"] = "cannot save %s (%d)" % [mesh_path, err]
			return row
		var out := MeshInstance3D.new()
		out.name = "MergedB_%d" % k
		out.mesh = load(mesh_path) as ArrayMesh
		out.gi_mode = GeometryInstance3D.GI_MODE_STATIC
		scene.add_child(out)
		out.owner = scene
		k += 1
	row["merged"] = k
	scene.scene_file_path = ""
	var repacked := PackedScene.new()
	var perr: int = repacked.pack(scene)
	if perr != OK:
		scene.queue_free()
		row["error"] = "pack failed (%d)" % perr
		return row
	perr = ResourceSaver.save(repacked, path)
	scene.queue_free()
	if perr != OK:
		row["error"] = "save failed (%d)" % perr
	return row


func _run() -> void:
	await process_frame
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 2:
		_report_path = args[0] if args.size() == 1 else "user://merge_buildings_proto.json"
		_report["error"] = "usage: <report path> <scene> [...]"
		_write()
		_exit(2)
		return
	_report_path = args[0]
	var first := 1
	if args.size() > 1 and args[1] == "--dry":
		_dry = true
		first = 2
	for i in range(first, args.size()):
		var row: Dictionary = await _merge_scene(args[i])
		(_report["scenes"] as Array).append(row)
		print("[merge_buildings_proto] %s: %s" % [args[i], (row["error"] if row["error"] != null
			else "%d slots, %d meshes, %d surfaces -> %d merged (%d unwrapped), %d colliders kept"
				% [row["slots_merged"], row["meshes_in"], row["surfaces_in"], row["merged"], row["unwrapped"],
					row["colliders"]])])
	var bad: Array = (_report["scenes"] as Array).filter(func(r): return r["error"] != null)
	_report["ok"] = bad.is_empty()
	if not bad.is_empty():
		_report["error"] = "%d scene(s) failed" % bad.size()
	_write()
	_exit(0 if bad.is_empty() else 2)
