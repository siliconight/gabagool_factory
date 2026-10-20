extends SceneTree
## WHICH MESHES DOES A SHIPPED LEVEL DRAW AS SEPARATE NODES, AND HOW MANY TIMES EACH?
##
##     godot --headless --path <a copy of a package> --script res://instancing_census.gd -- --out FILE
##
## The walker, 2026-10-19, with Godot 4.7's MultiMesh page: "Are we doing this intelligently?" --
## "at a high level if we are using it for our total pipeline". A MultiMesh draws ONE mesh many
## times in one submission; a MeshInstance3D is a submission per surface whenever it is in view,
## however many other nodes share its mesh. So the question has a measurable form: of the surfaces
## a shipped level can submit, how many belong to meshes that several nodes share -- the pool a
## MultiMesh could fold -- and what are they: lightmapped static geometry, which a MultiMesh may not
## carry (the 4.7 docs name MeshInstance3D as what LightmapGI bakes and say nothing of MultiMesh),
## or unbaked props.
##
## WHAT IT READS: the package's own entry, `mission.tscn`, instanced and given two frames, so the
## baked level, the dressing layer and the backdrop it loads are all in the tree. Every
## MeshInstance3D is grouped by the identity of its Mesh resource (one imported GLB instanced ten
## times shares its meshes), and each group records its node count, surfaces, triangles, how many
## of its nodes bake (`gi_mode` static) and cast shadows, and which branch of the level they stand
## in. MultiMeshInstance3D nodes are listed with their instance counts.
##
## WHAT IT DOES NOT: count draws. A surface submits only when its node is in view and survives
## occlusion, and shadow passes submit again; `level_factory/tools/draw_attrib.gd` measures draws
## at stations, windowed. This is the POOL those draws come from. It prints what it counted and
## stops; whether a group should become a MultiMesh is the reply's to argue.

var _out := ""
var _frames := 0
var _mission: Node = null


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var i := args.find("--out")
	if i >= 0 and i + 1 < args.size():
		_out = args[i + 1]
	var packed := load("res://mission.tscn") as PackedScene
	_mission = packed.instantiate()
	root.add_child(_mission)


func _process(_delta: float) -> bool:
	_frames += 1
	if _frames < 3:
		return false
	_census()
	return true


func _category(n: Node) -> String:
	var p := str(_mission.get_path_to(n)).to_lower()
	if p.find("dressing") >= 0:
		return "dressing"
	if p.find("backdrop") >= 0:
		return "backdrop"
	var parts := p.split("/")
	for part in parts:
		var s := str(part)
		if s.begins_with("cover"):
			return "cover"
		if s.begins_with("blocker"):
			return "blocker"
		if s.begins_with("hung"):
			return "hung"
		if s.length() >= 2 and s.begins_with("b") and s.substr(1, 1).is_valid_int():
			return "building"
	return "site"


func _tris(m: Mesh) -> int:
	return int(m.get_faces().size() / 3)


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _census() -> void:
	var nodes: Array = []
	_walk(_mission, nodes)
	var groups := {}
	var multis: Array = []
	var mesh_nodes := 0
	for item in nodes:
		var n := item as Node
		if n is MultiMeshInstance3D:
			var mmi := n as MultiMeshInstance3D
			var mm := mmi.multimesh
			if mm != null and mm.mesh != null:
				multis.append({"path": str(_mission.get_path_to(mmi)), "category": _category(mmi),
					"instances": mm.instance_count, "surfaces": mm.mesh.get_surface_count(),
					"mesh_tris": _tris(mm.mesh), "gi_mode": int(mmi.gi_mode)})
			continue
		if not (n is MeshInstance3D):
			continue
		var mi := n as MeshInstance3D
		if mi.mesh == null:
			continue
		mesh_nodes += 1
		var key := str(mi.mesh.get_instance_id())
		if not groups.has(key):
			var label := mi.mesh.resource_name
			if label == "":
				label = mi.mesh.resource_path.get_file()
			if label == "":
				label = str(mi.name)
			groups[key] = {"label": label, "class": mi.mesh.get_class(), "nodes": 0,
				"surfaces": mi.mesh.get_surface_count(), "tris": _tris(mi.mesh), "baked": 0,
				"shadow": 0, "categories": {}}
		var g: Dictionary = groups[key]
		g["nodes"] = int(g["nodes"]) + 1
		if mi.gi_mode == GeometryInstance3D.GI_MODE_STATIC:
			g["baked"] = int(g["baked"]) + 1
		if mi.cast_shadow != GeometryInstance3D.SHADOW_CASTING_SETTING_OFF:
			g["shadow"] = int(g["shadow"]) + 1
		var cat := _category(mi)
		var cats: Dictionary = g["categories"]
		cats[cat] = int(cats.get(cat, 0)) + 1
	var rows: Array = groups.values()
	rows.sort_custom(func(a, b): return int(a["nodes"]) * int(a["surfaces"]) > int(b["nodes"]) * int(b["surfaces"]))
	var total_surfaces := 0
	var shared_surfaces := {2: 0, 8: 0, 32: 0}
	var shared_baked := {2: 0, 8: 0, 32: 0}
	var by_cat := {}
	for r in rows:
		var row: Dictionary = r
		var s := int(row["nodes"]) * int(row["surfaces"])
		total_surfaces += s
		for k in [2, 8, 32]:
			if int(row["nodes"]) >= k:
				shared_surfaces[k] = int(shared_surfaces[k]) + s
				shared_baked[k] = int(shared_baked[k]) + int(row["baked"]) * int(row["surfaces"])
		var cats: Dictionary = row["categories"]
		for c in cats.keys():
			var cs := str(c)
			if not by_cat.has(cs):
				by_cat[cs] = {"nodes": 0, "surfaces": 0, "shared8_surfaces": 0}
			var b: Dictionary = by_cat[cs]
			b["nodes"] = int(b["nodes"]) + int(cats[c])
			b["surfaces"] = int(b["surfaces"]) + int(cats[c]) * int(row["surfaces"])
			if int(row["nodes"]) >= 8:
				b["shared8_surfaces"] = int(b["shared8_surfaces"]) + int(cats[c]) * int(row["surfaces"])
	var mm_instances := 0
	for m in multis:
		var md: Dictionary = m
		mm_instances += int(md["instances"])
	print("[census] mesh nodes %d in %d distinct meshes; surfaces (the draw pool) %d" % [mesh_nodes, rows.size(), total_surfaces])
	for k in [2, 8, 32]:
		print("[census] meshes drawn by >= %d nodes: %d surfaces (%.1f%% of the pool), %d of them baked" % [k, int(shared_surfaces[k]), 100.0 * float(int(shared_surfaces[k])) / max(1.0, float(total_surfaces)), int(shared_baked[k])])
	print("[census] MultiMeshInstance3D nodes %d carrying %d instances" % [multis.size(), mm_instances])
	for c in by_cat.keys():
		var b: Dictionary = by_cat[c]
		print("[census] %-9s nodes %5d  surfaces %5d  in meshes shared by >= 8 nodes %5d" % [str(c), int(b["nodes"]), int(b["surfaces"]), int(b["shared8_surfaces"])])
	var top := mini(30, rows.size())
	for i in range(top):
		var row: Dictionary = rows[i]
		print("[census] %4d nodes x %d surf  %6d tris  baked %4d  shadow %4d  %s  %s %s" % [int(row["nodes"]), int(row["surfaces"]), int(row["tris"]), int(row["baked"]), int(row["shadow"]), str(row["class"]), str(row["label"]).left(48), JSON.stringify(row["categories"])])
	if _out != "":
		var f := FileAccess.open(_out, FileAccess.WRITE)
		f.store_string(JSON.stringify({"mesh_nodes": mesh_nodes, "distinct_meshes": rows.size(), "surfaces": total_surfaces, "shared_surfaces": shared_surfaces, "shared_baked_surfaces": shared_baked, "by_category": by_cat, "multimeshes": multis, "groups": rows}, " "))
		f.close()
		print("[census] wrote ", _out)
