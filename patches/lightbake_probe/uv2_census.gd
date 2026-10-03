extends SceneTree
## Roadmap item 31, the light-bake probe: after import, which mesh instances
## in the site carry a second UV set, and which do not. Run headless in a
## prepared copy:
##     godot --headless --path <probe dir> --script uv2_census.gd
## Prints, per source (a model file or the site's inline primitives), the
## instances with UV2 and without, the GI mode they carry, and the
## lightmap size hint Godot computed. Prints what it measured and stops.


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _source(mi: MeshInstance3D) -> String:
	var n: Node = mi
	while n != null:
		if n.scene_file_path != "" and n != mi:
			return n.scene_file_path.get_file()
		n = n.get_parent()
	return "(inline)"


func _walk(n: Node, out: Array) -> void:
	if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
		out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _run() -> void:
	var packed: PackedScene = load("res://site.tscn")
	if packed == null:
		print("UV2 CANNOT LOAD site.tscn")
		_exit(2)
		return
	var site: Node = packed.instantiate()
	root.add_child(site)
	await process_frame
	var meshes: Array = []
	_walk(site, meshes)
	var by: Dictionary = {}
	var with_total: int = 0
	var without_total: int = 0
	var static_total: int = 0
	var texels: int = 0
	for mi in meshes:
		var m: Mesh = (mi as MeshInstance3D).mesh
		var uv2: bool = false
		if m is PrimitiveMesh:
			uv2 = (m as PrimitiveMesh).add_uv2
		else:
			for s in range(m.get_surface_count()):
				if m.surface_get_format(s) & Mesh.ARRAY_FORMAT_TEX_UV2:
					uv2 = true
		var key: String = _source(mi)
		if not by.has(key):
			by[key] = [0, 0, 0]
		if uv2:
			by[key][0] += 1
			with_total += 1
		else:
			by[key][1] += 1
			without_total += 1
		if (mi as GeometryInstance3D).gi_mode == GeometryInstance3D.GI_MODE_STATIC:
			static_total += 1
			by[key][2] += 1
		if m is ArrayMesh and uv2:
			var hint: Vector2i = (m as ArrayMesh).lightmap_size_hint
			texels += hint.x * hint.y
	var keys: Array = by.keys()
	keys.sort()
	for k in keys:
		print("UV2 %-70s with %4d  without %4d  gi static %4d" % [k, by[k][0], by[k][1], by[k][2]])
	print("UV2 mesh instances %d: with UV2 %d, without %d; gi_mode static %d" % [meshes.size(), with_total, without_total, static_total])
	print("UV2 lightmap size hints on the imported meshes, summed: %d texels (%.1f megatexels)" % [texels, texels / 1.0e6])
	print("UV2 done")
	_exit(0)
