extends SceneTree
## A digest of every mesh's lightmap UVs in the site, to tell whether a
## fresh import reproduces the unwrap the lightmap was baked against.
##     godot --headless --path <package> --script uv2_hash.gd
## Prints one line per source with the count of meshes and a digest of their
## UV2 arrays, and a total digest.


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _walk(n: Node, out: Array) -> void:
	if n is MeshInstance3D and (n as MeshInstance3D).mesh is ArrayMesh:
		out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _run() -> void:
	var packed: PackedScene = load("res://presentation/lux.applied.tscn")
	var site: Node = packed.instantiate()
	root.add_child(site)
	await process_frame
	var meshes: Array = []
	_walk(site, meshes)
	var total := HashingContext.new()
	total.start(HashingContext.HASH_SHA256)
	var n_uv2: int = 0
	var seen: Dictionary = {}
	for mi in meshes:
		var m: ArrayMesh = (mi as MeshInstance3D).mesh
		var key: String = m.resource_path if m.resource_path != "" else str(mi.get_path())
		if seen.has(key):
			continue
		seen[key] = true
		for s in range(m.get_surface_count()):
			if not (m.surface_get_format(s) & Mesh.ARRAY_FORMAT_TEX_UV2):
				continue
			var uv2: PackedVector2Array = m.surface_get_arrays(s)[Mesh.ARRAY_TEX_UV2]
			total.update(key.to_utf8_buffer())
			total.update(uv2.to_byte_array())
			n_uv2 += 1
	print("UV2HASH surfaces with uv2 %d over %d distinct meshes; digest %s" % [n_uv2, seen.size(), total.finish().hex_encode()])
	_exit(0)
