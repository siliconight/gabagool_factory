extends SceneTree
## A digest of every imported model in a project, as Godot loads it: for each .glb and .obj, the
## md5 of a description of what loads -- every node's path, class and transform (to 1e-4), and for
## each mesh its surfaces' primitive, vertex and index counts, whether it carries a second UV set,
## and its material's name and albedo texture path. Two imports of the same files that load the
## same thing print the same digest, whatever bytes their cache holds.
##
##   godot --headless --path <project> -s <this file>
##
## Prints `DIGEST <res path> <md5>` a line, then `DIGESTS <count> unloadable=<count>`. Measures and
## prints; names no cause.

var _unloadable: int = 0


func _initialize() -> void:
	var files: Array[String] = []
	_collect("res://", files)
	files.sort()
	for f in files:
		var res: Resource = ResourceLoader.load(f, "", ResourceLoader.CACHE_MODE_IGNORE)
		if res == null:
			_unloadable += 1
			print("DIGEST %s UNLOADABLE" % f)
			continue
		var text: String = ""
		if res is PackedScene:
			var root: Node = (res as PackedScene).instantiate()
			text = _describe(root, root)
			root.free()
		elif res is Mesh:
			text = _mesh_text(res as Mesh)
		else:
			text = res.get_class()
		print("DIGEST %s %s" % [f, text.md5_text()])
	print("DIGESTS %d unloadable=%d" % [files.size(), _unloadable])
	quit(0)


func _collect(dir_path: String, out: Array[String]) -> void:
	var d: DirAccess = DirAccess.open(dir_path)
	if d == null:
		return
	for sub in d.get_directories():
		if sub.begins_with("."):
			continue
		_collect(dir_path.path_join(sub), out)
	for f in d.get_files():
		if f.ends_with(".glb") or f.ends_with(".obj"):
			out.append(dir_path.path_join(f))


func _describe(n: Node, root: Node) -> String:
	var t: String = ""
	var n3: Node3D = n as Node3D
	var xf: String = ""
	if n3 != null:
		var b: Basis = n3.transform.basis
		var o: Vector3 = n3.transform.origin
		xf = "%.4f,%.4f,%.4f|%.4f,%.4f,%.4f|%.4f,%.4f,%.4f|%.4f,%.4f,%.4f" % [
			b.x.x, b.x.y, b.x.z, b.y.x, b.y.y, b.y.z, b.z.x, b.z.y, b.z.z, o.x, o.y, o.z]
	t += "%s:%s:%s\n" % [String(root.get_path_to(n)), n.get_class(), xf]
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		t += _mesh_text(mi.mesh)
	for c in n.get_children():
		t += _describe(c, root)
	return t


func _mesh_text(m: Mesh) -> String:
	var t: String = ""
	for s in range(m.get_surface_count()):
		var arrays: Array = m.surface_get_arrays(s)
		var verts: int = 0
		var idx: int = 0
		var uv2: bool = false
		if arrays.size() > Mesh.ARRAY_VERTEX and arrays[Mesh.ARRAY_VERTEX] != null:
			verts = (arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array).size()
		if arrays.size() > Mesh.ARRAY_INDEX and arrays[Mesh.ARRAY_INDEX] != null:
			idx = (arrays[Mesh.ARRAY_INDEX] as PackedInt32Array).size()
		if arrays.size() > Mesh.ARRAY_TEX_UV2 and arrays[Mesh.ARRAY_TEX_UV2] != null:
			uv2 = true
		var mat: Material = m.surface_get_material(s)
		var mname: String = ""
		var tex: String = ""
		if mat != null:
			mname = mat.resource_name
			var bm: BaseMaterial3D = mat as BaseMaterial3D
			if bm != null and bm.albedo_texture != null:
				# An embedded texture's path ends in a sub-resource id an import may
				# generate; the file it lives in and its size are what loaded.
				tex = "%s %dx%d" % [bm.albedo_texture.resource_path.get_slice("::", 0),
					bm.albedo_texture.get_width(), bm.albedo_texture.get_height()]
		t += "  s%d p%d v%d i%d uv2=%s m=%s tex=%s\n" % [
			s, int(m.surface_get_primitive_type(s)), verts, idx, str(uv2), mname, tex]
	return t
