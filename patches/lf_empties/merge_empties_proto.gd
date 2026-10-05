extends SceneTree
## PROTOTYPE, MEASUREMENT ONLY: every Empty's kit modules merged into one mesh
## per SIDE per material, to price the merge before any tool is changed.
##
##     godot --headless --path <imported package COPY> --script res://merge_empties_proto.gd
##
## For each `res://lot/gs_empty_*/site.tscn` (read off cold run 9162's
## package: a `site` root, `GreyboxBase` -- the collision base -- one child per
## slot named for its slot id and instancing a kit module GLB, and `Dressing`):
##   * every slot child whose name gives a side -- `ext_<storey>_<N|E|S|W>_*`,
##     `parapet_<N|E|S|W>_*`, `roof_*` (side R) -- is taken apart: its
##     StaticBody3D colliders are copied out whole under a `KitCollision` node,
##     in the root's frame, and every surface of its MeshInstance3D nodes is
##     appended (SurfaceTool.append_from, in the root's frame) to the group
##     keyed by (side, material name, uv1 scale and triplanar flags, surface
##     format) -- each module GLB imports its own material instances, so the
##     name is the identity and the flags keep visually different ones apart;
##   * the slot child is removed, and one MeshInstance3D a group is added,
##     named `Merged<side>_<n>`, wearing the group's first material;
##   * the scene is saved back over itself.
## GreyboxBase and Dressing are left alone. The baked lightmap no longer finds
## the merged surfaces (its users are node paths), so they draw without it:
## the copy measures submission cost, not the look.
## Prints per scene what it took in and put out, and refuses a scene in which
## it found no side to merge.

func _initialize() -> void:
	_run()


func _side(slot_name: String) -> String:
	var parts: PackedStringArray = slot_name.split("_")
	if slot_name.begins_with("roof"):
		return "R"
	if slot_name.begins_with("parapet_") and parts.size() > 1:
		return parts[1]
	if slot_name.begins_with("ext_") and parts.size() > 2 and parts[2] in ["N", "E", "S", "W"]:
		return parts[2]
	return ""


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _key(side: String, mat: Material, fmt: int) -> String:
	var k: String = "%s|%s|%d" % [side, (mat.resource_name if mat != null else "<none>"), fmt]
	var bm: BaseMaterial3D = mat as BaseMaterial3D
	if bm != null:
		k += "|%s|%s|%s" % [str(bm.uv1_scale), str(bm.uv1_triplanar), str(bm.uv1_world_triplanar)]
	return k


func _merge_scene(path: String) -> String:
	var packed: PackedScene = load(path) as PackedScene
	if packed == null:
		return "cannot load"
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
	var meshes_in: int = 0
	var surfaces_in: int = 0
	var bodies: int = 0
	var gone: Array = []
	for child in scene.get_children():
		var side: String = _side(String(child.name))
		if side == "":
			continue
		var nodes: Array = []
		_walk(child, nodes)
		for n in nodes:
			var body: StaticBody3D = n as StaticBody3D
			if body != null:
				var copy: StaticBody3D = body.duplicate() as StaticBody3D
				collision.add_child(copy)
				copy.transform = inv * body.global_transform
				copy.owner = scene
				for d in copy.get_children():
					d.owner = scene
				bodies += 1
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
			meshes_in += 1
			var xf: Transform3D = inv * mi.global_transform
			for s in range(mi.mesh.get_surface_count()):
				var mat: Material = mi.get_active_material(s)
				var fmt: int = (mi.mesh as ArrayMesh).surface_get_format(s) if mi.mesh is ArrayMesh else 0
				var key: String = _key(side, mat, fmt)
				if not tools.has(key):
					var st := SurfaceTool.new()
					tools[key] = st
					mats[key] = mat
				(tools[key] as SurfaceTool).append_from(mi.mesh, s, xf)
				surfaces_in += 1
		gone.append(child)
	if tools.is_empty():
		scene.queue_free()
		return "REFUSED: no side to merge"
	for g in gone:
		scene.remove_child(g)
		(g as Node).queue_free()
	var k: int = 0
	var keys: Array = tools.keys()
	keys.sort()
	for key in keys:
		var st: SurfaceTool = tools[key]
		var am: ArrayMesh = st.commit()
		var out := MeshInstance3D.new()
		out.name = "Merged%s_%d" % [String(key).split("|")[0], k]
		out.mesh = am
		out.set_surface_override_material(0, mats[key])
		scene.add_child(out)
		out.owner = scene
		k += 1
	# the root was instantiated FROM this path; packed with it set, the saved
	# scene would inherit from itself
	scene.scene_file_path = ""
	var repacked := PackedScene.new()
	var err: int = repacked.pack(scene)
	if err != OK:
		return "pack failed %d" % err
	err = ResourceSaver.save(repacked, path)
	scene.queue_free()
	if err != OK:
		return "save failed %d" % err
	return "%d meshes, %d surfaces in -> %d merged meshes; %d colliders kept" % [meshes_in, surfaces_in, k, bodies]


func _run() -> void:
	await process_frame
	var dir: DirAccess = DirAccess.open("res://lot")
	if dir == null:
		print("PROTO no res://lot")
		quit(2)
		return
	var done: int = 0
	for d in dir.get_directories():
		if not String(d).begins_with("gs_empty_"):
			continue
		var path: String = "res://lot/%s/site.tscn" % d
		var said: String = await _merge_scene(path)
		print("PROTO %s: %s" % [d, said])
		if said.contains("meshes"):
			done += 1
	print("PROTO merged %d Empty scene(s)" % done)
	quit(0 if done > 0 else 2)
