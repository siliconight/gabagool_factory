extends SceneTree
## WHAT DOES LEVEL FACTORY'S BUILDING MERGE REMOVE THAT IT DOES NOT CARRY? (the factory's install test 11's walk:
## "walk bot: no ladder_area3d in scene; traversal vacuous")
##
##     godot --headless --path <an UNMERGED package> --script res://merge_drop_census.gd -- <out.json> <scene> [...]
##
## For each building scene (`res://lot/<id>/site.tscn`): instantiates it and waits a frame, as the merge does, then
## takes every top-level child that Level Factory 0.226.2's `_mergeable` would take apart (copied below as it
## stands) and sorts each node of its subtree:
##   * CARRIED -- a StaticBody3D and everything under it (the merge copies the body whole under `KitCollision`), and
##     any other MeshInstance3D (its surfaces go into the merged meshes);
##   * DROPPED -- everything else, removed with the child.
## Dropped nodes are counted by exact class (`get_class()`), and any that carries a group not starting "_" (Godot's
## own groups do) or any metadata is listed. Then, for two candidate rules, the children each would keep whole and
## the mesh surfaces those children hold -- surfaces a kept child no longer gives the merge:
##   * rule A: a CollisionObject3D that is not a StaticBody3D, or a node in a group not starting "_";
##   * rule W: a dropped node whose class is not exactly Node3D, or that is in such a group or carries metadata.
## It also counts the bare empties it drops below a slot's own root by name (digits dropped) -- a marker with no
## group or metadata would hide there -- and lists any MeshInstance3D it carries that has a group or metadata,
## which the merged mesh does not keep. It prints what it counted and stops.

const FIXTURE_SUFFIXES: Array[String] = ["_Lens", "_Diffuser"]
const FLAGGED_CAP := 400

var _out := ""


func _initialize() -> void:
	_run()


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


# Level Factory 0.226.2's, verbatim
func _fixture(mat: Material) -> bool:
	if mat == null or not mat.resource_name.begins_with("M_"):
		return false
	for s in FIXTURE_SUFFIXES:
		if mat.resource_name.ends_with(s):
			return true
	return false


# Level Factory 0.226.2's, verbatim
func _mergeable(child: Node, nodes: Array) -> bool:
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
				var m: Material = mi.get_active_material(s)
				if m is ShaderMaterial or _fixture(m):
					return false
	return true


func _own_groups(n: Node) -> Array:
	var out: Array = []
	for g in n.get_groups():
		if not String(g).begins_with("_"):
			out.append(String(g))
	return out


func _under_body(n: Node, child: Node) -> bool:
	var p: Node = n
	while p != null:
		if p is StaticBody3D:
			return true
		if p == child:
			return false
		p = p.get_parent()
	return false


func _surfaces(nodes: Array, child: Node) -> int:
	var k: int = 0
	for n in nodes:
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi != null and mi.mesh != null and not _under_body(mi, child):
			k += mi.mesh.get_surface_count()
	return k


func _census(path: String) -> Dictionary:
	var row: Dictionary = {"scene": path, "children": 0, "merged_02262": 0, "dropped_by_class": {},
		"flagged_count": 0, "flagged": [], "rule_a": {"kept": [], "surfaces": 0},
		"rule_w": {"kept": [], "surfaces": 0}, "empties_by_name": {}, "carried_meshes": 0,
		"carried_meshes_flagged": [], "error": null}
	var packed: PackedScene = load(path) as PackedScene
	if packed == null:
		row["error"] = "cannot load"
		return row
	var scene: Node3D = packed.instantiate() as Node3D
	if scene == null:
		row["error"] = "root is not a Node3D"
		return row
	root.add_child(scene)
	await process_frame
	var by_class: Dictionary = row["dropped_by_class"]
	for child in scene.get_children():
		row["children"] = int(row["children"]) + 1
		var nodes: Array = []
		_walk(child, nodes)
		if not _mergeable(child, nodes):
			continue
		row["merged_02262"] = int(row["merged_02262"]) + 1
		var keep_a: bool = false
		var keep_w: bool = false
		for n in nodes:
			var node: Node = n as Node
			var groups: Array = _own_groups(node)
			if node is CollisionObject3D and not (node is StaticBody3D):
				keep_a = true
			if not groups.is_empty():
				keep_a = true
			if _under_body(node, child):
				continue
			if node is MeshInstance3D and (node as MeshInstance3D).mesh != null:
				row["carried_meshes"] = int(row["carried_meshes"]) + 1
				if not groups.is_empty() or not node.get_meta_list().is_empty():
					(row["carried_meshes_flagged"] as Array).append({"child": String(child.name),
						"path": String(child.get_path_to(node)), "groups": groups,
						"meta": str(node.get_meta_list())})
				continue
			var cls: String = node.get_class()
			by_class[cls] = int(by_class.get(cls, 0)) + 1
			var metas: Array = []
			for m in node.get_meta_list():
				metas.append(String(m))
			if cls != "Node3D" or not groups.is_empty() or not metas.is_empty():
				keep_w = true
			elif node != child:
				# a bare empty below the slot's own root: its name, digits dropped, is all it carries
				var stem: String = String(node.name).rstrip("0123456789_-.")
				var en: Dictionary = row["empties_by_name"]
				en[stem] = int(en.get(stem, 0)) + 1
			if not groups.is_empty() or not metas.is_empty() or cls != "Node3D":
				row["flagged_count"] = int(row["flagged_count"]) + 1
				if (row["flagged"] as Array).size() < FLAGGED_CAP:
					(row["flagged"] as Array).append({"child": String(child.name),
						"path": String(child.get_path_to(node)), "class": cls, "groups": groups, "meta": metas})
		if keep_a:
			(row["rule_a"]["kept"] as Array).append(String(child.name))
			row["rule_a"]["surfaces"] = int(row["rule_a"]["surfaces"]) + _surfaces(nodes, child)
		if keep_w:
			(row["rule_w"]["kept"] as Array).append(String(child.name))
			row["rule_w"]["surfaces"] = int(row["rule_w"]["surfaces"]) + _surfaces(nodes, child)
	scene.queue_free()
	return row


func _run() -> void:
	await process_frame
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 2:
		print("usage: <out.json> <scene> [...]")
		quit(2)
		return
	_out = args[0]
	var rows: Array = []
	for i in range(1, args.size()):
		var row: Dictionary = await _census(args[i])
		rows.append(row)
		if row["error"] != null:
			print("[census] %s: %s" % [args[i], row["error"]])
			continue
		var classes: PackedStringArray = []
		var keys: Array = (row["dropped_by_class"] as Dictionary).keys()
		keys.sort()
		for c in keys:
			classes.append("%s %d" % [c, int(row["dropped_by_class"][c])])
		# joined BEFORE the format: `%` binds tighter than `+`
		var fmt: String = ("[census] %s: %d children, %d merged by 0.226.2; dropped %s; flagged %d; "
			+ "rule A keeps %d (%d surfaces) %s; rule W keeps %d (%d surfaces) %s")
		print(fmt % [args[i], row["children"], row["merged_02262"], ", ".join(classes), row["flagged_count"],
			(row["rule_a"]["kept"] as Array).size(), row["rule_a"]["surfaces"], str(row["rule_a"]["kept"]),
			(row["rule_w"]["kept"] as Array).size(), row["rule_w"]["surfaces"], str(row["rule_w"]["kept"])])
		var empties: PackedStringArray = []
		var en: Dictionary = row["empties_by_name"]
		var stems: Array = en.keys()
		stems.sort()
		for s in stems:
			empties.append("%s %d" % [s, int(en[s])])
		print("[census]     bare empties below a slot's root: %s" % ", ".join(empties))
		print("[census]     meshes carried %d, of them with a group or metadata %d" % [row["carried_meshes"],
			(row["carried_meshes_flagged"] as Array).size()])
	var f := FileAccess.open(_out, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify({"schema": "merge_drop_census.v1", "scenes": rows}, "  "))
		f.close()
	quit(0)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())
