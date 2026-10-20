extends SceneTree
## HOW MANY SURFACES WOULD AN ENTERABLE BUILDING SUBMIT IF ITS STATIC MODULES WERE MERGED PER UNIT AND MATERIAL?
## (the factory's roadmap 266)
##
##     godot --headless --path <a copy of a package> --script res://merge_census.gd -- --out FILE <id> [<id> ...]
##
## Reads `res://lot/<id>/site.tscn` for each building named -- Deli Counter's composed scene: a root, its
## `GreyboxBase`, one child per slot instancing a kit module, `Dressing` -- and sorts every slot child into what a
## merge could not touch and what it could, counting the surfaces of each (a MeshInstance3D's surfaces, not those
## of a collider's own meshes). What a merge must leave alone, and why:
##   * `interactive`: a child carrying `interactive_id` meta -- a door, a breachable wall, a hatch: its states swap.
##   * `opening`: a `*_open<n>` slot -- a window's pane may be glass, sorted per mesh; left for a later cut.
##   * `lit`: a module wearing a Lux lit-face material (`M_*_Lens`, `_Diffuser`, `_Face`) -- Lux binds them, and a
##     failing fixture's flicker must stay its own.
##   * `moving`: a subtree holding an AnimationPlayer or any node with a script.
##   * `base`, `dressing`: the collision base, and the covers (merged per side already, roadmap 180).
## Everything else is `static` and is counted under the unit a merge would give it:
##   * `ext_<storey>_<side>_*` -> one unit a side a storey; `parapet_<side>_*` and `roof_*` -> the roof;
##   * `int_<storey>_<k>_*` -> one unit a partition run;
##   * a furnished piece, named `<kind>_r<room hash>_<n>` by `level_design.furnish` -> one unit a room;
##   * anything else -> one unit a storey, the storey read off its height (`STOREY_M`).
## Within a unit a merge keys surfaces as `merge_empties.gd` does: material name, uv1 scale and triplanar flags,
## surface format. The KEYS a building's static surfaces fall into are what its merged meshes would number.
##
## It prints what it counted and stops; whether to merge, and at what unit, is the reply's to argue. It does not
## count draws -- a surface submits only in view and unoccluded, and shadow passes submit again.

const LIT_SUFFIXES: Array[String] = ["_Lens", "_Diffuser", "_Face"]
## Deli Counter's storey height for the buildings that use its default; a piece named for no wall or room is put
## on the storey its origin stands in. Only the unit's NAME comes from it, never what is merged.
const STOREY_M := 3.5

var _out := ""
var _ids: Array = []
var _rows: Array = []


func _initialize() -> void:
	_run()


func _run() -> void:
	await process_frame
	var args := OS.get_cmdline_user_args()
	var i := 0
	while i < args.size():
		if args[i] == "--out" and i + 1 < args.size():
			_out = args[i + 1]
			i += 2
			continue
		_ids.append(args[i])
		i += 1
	for id in _ids:
		_rows.append(await _census(String(id)))
	var f := FileAccess.open(_out, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify({"schema": "lf.merge_census_266.v1", "buildings": _rows}, "  "))
		f.close()
	_exit(0)


## The shipped probes' exit (docs/COMMANDS.md): quit, two frames, then the kill a modal cannot stop.
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


func _unit(name: String, origin: Vector3) -> String:
	var parts: PackedStringArray = name.split("_")
	if name.begins_with("ext_") and parts.size() > 2:
		return "ext %s %s" % [parts[1], parts[2]]
	if name.begins_with("int_") and parts.size() > 2:
		return "int %s %s" % [parts[1], parts[2]]
	if name.begins_with("parapet_") or name.begins_with("roof"):
		return "roof"
	for p in parts:
		if p.length() == 9 and p.begins_with("r") and p.substr(1).is_valid_hex_number(false):
			return "room %s" % p
	return "storey %d" % int(floor(origin.y / STOREY_M))


func _key(unit: String, mat: Material, fmt: int) -> String:
	var k: String = "%s|%s|%d" % [unit, (mat.resource_name if mat != null else "<none>"), fmt]
	var bm: BaseMaterial3D = mat as BaseMaterial3D
	if bm != null:
		k += "|%s|%s|%s" % [str(bm.uv1_scale), str(bm.uv1_triplanar), str(bm.uv1_world_triplanar)]
	return k


func _census(id: String) -> Dictionary:
	var path := "res://lot/%s/site.tscn" % id
	var row: Dictionary = {"id": id, "error": null, "surfaces": {}, "slots": {}, "keys": 0, "units": {},
		"static_surfaces": 0}
	var packed: PackedScene = load(path) as PackedScene
	if packed == null:
		row["error"] = "cannot load " + path
		return row
	var scene: Node3D = packed.instantiate() as Node3D
	root.add_child(scene)
	# A FRAME FIRST. The first version read every slot's transform straight after add_child, inside _initialize,
	# and got the identity: every piece named for no wall or room fell on storey 0, and deli_a03's 56 storey keys
	# counted as 25 (the prototype, which waits a frame, found the 56 merging them).
	await process_frame
	var inv: Transform3D = scene.global_transform.affine_inverse()
	var keys: Dictionary = {}
	var units: Dictionary = {}
	for child in scene.get_children():
		var name := String(child.name)
		var nodes: Array = []
		_walk(child, nodes)
		var cls := "static"
		if name == "GreyboxBase":
			cls = "base"
		elif name == "Dressing":
			cls = "dressing"
		elif (child as Node).has_meta("interactive_id"):
			cls = "interactive"
		elif name.find("_open") >= 0:
			cls = "opening"
		else:
			for n in nodes:
				if n is AnimationPlayer or ((n as Node).get_script() != null):
					cls = "moving"
					break
		var meshes: Array = []
		for n in nodes:
			var mi: MeshInstance3D = n as MeshInstance3D
			if mi == null or mi.mesh == null:
				continue
			var under_body := false
			var p: Node = mi.get_parent()
			while p != null and p != child:
				if p is StaticBody3D:
					under_body = true
				p = p.get_parent()
			if not under_body:
				meshes.append(mi)
		if cls == "static":
			for mi in meshes:
				for s in range((mi as MeshInstance3D).mesh.get_surface_count()):
					if _lit((mi as MeshInstance3D).get_active_material(s)):
						cls = "lit"
		var count := 0
		for mi in meshes:
			count += (mi as MeshInstance3D).mesh.get_surface_count()
		row["surfaces"][cls] = int(row["surfaces"].get(cls, 0)) + count
		row["slots"][cls] = int(row["slots"].get(cls, 0)) + 1
		if cls != "static":
			continue
		var origin: Vector3 = (inv * (child as Node3D).global_transform).origin if child is Node3D else Vector3.ZERO
		var unit := _unit(name, origin)
		for mi in meshes:
			var m := mi as MeshInstance3D
			for s in range(m.mesh.get_surface_count()):
				var fmt: int = (m.mesh as ArrayMesh).surface_get_format(s) if m.mesh is ArrayMesh else 0
				keys[_key(unit, m.get_active_material(s), fmt)] = true
				row["static_surfaces"] = int(row["static_surfaces"]) + 1
		units[unit.split(" ")[0]] = int(units.get(unit.split(" ")[0], 0)) + count
	row["keys"] = keys.size()
	row["units"] = units
	var by_kind: Dictionary = {}
	for k in keys:
		var kind: String = String(k).split("|")[0].split(" ")[0]
		by_kind[kind] = int(by_kind.get(kind, 0)) + 1
	row["keys_by_unit_kind"] = by_kind
	scene.queue_free()
	print("[merge_census] %s: surfaces %s; static %d in %d keys %s" % [id, JSON.stringify(row["surfaces"]),
		row["static_surfaces"], row["keys"], JSON.stringify(by_kind)])
	return row
