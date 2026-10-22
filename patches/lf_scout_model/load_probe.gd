extends SceneTree
# Does a game load a package's scout models as a game would? (roadmap 295) Run headless in the walk copy:
#   godot --headless --path <walk copy> --script <this> -- <res:// path> [<res:// path> ...]
# For each: GLTFDocument.append_from_file on the file as the package carries it (kept, never imported), then
# generate_scene; prints its storey nodes, meshes and triangles. Prints measurements only, then quits.


func _initialize() -> void:
	for p in OS.get_cmdline_user_args():
		var doc := GLTFDocument.new()
		var state := GLTFState.new()
		var err: int = doc.append_from_file(ProjectSettings.globalize_path(p), state)
		if err != OK:
			print("%s: append_from_file error %d" % [p, err])
			continue
		var scene: Node = doc.generate_scene(state)
		var meshes: Array = []
		_collect(scene, meshes)
		var tris: int = 0
		var names: PackedStringArray = []
		for mi in meshes:
			var m: Mesh = (mi as MeshInstance3D).mesh
			names.append(String(mi.name))
			for s in range(m.get_surface_count()):
				var arr: Array = m.surface_get_arrays(s)
				var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX]
				tris += idx.size() / 3
		print("%s: loaded, %d mesh(es) %s, %d triangles" % [p, meshes.size(), ", ".join(names), tris])
		scene.free()
	quit(0)


func _collect(n: Node, out: Array) -> void:
	if n is MeshInstance3D:
		out.append(n)
	for c in n.get_children():
		_collect(c, out)
