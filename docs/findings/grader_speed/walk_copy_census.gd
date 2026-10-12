extends SceneTree
## Load a walk copy's scene and count what came in: nodes, mesh instances, mesh instances with no
## mesh, lights, and the lightmap's user count. Instantiated, never added to the tree, so no
## script's _ready runs. Measures and prints one line; names no cause.
##
##   godot --headless --path <walk copy> -s <this file>


func _initialize() -> void:
	var packed: PackedScene = ResourceLoader.load(
		"res://_walk.tscn", "", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
	if packed == null:
		print("WALK_COPY unloadable")
		quit(1)
		return
	var root: Node = packed.instantiate()
	var counts: Dictionary = {"nodes": 0, "meshes": 0, "empty_meshes": 0, "lights": 0, "lightmap_users": -1}
	_count(root, counts)
	print("WALK_COPY nodes=%d meshes=%d empty_meshes=%d lights=%d lightmap_users=%d"
		% [int(counts["nodes"]), int(counts["meshes"]), int(counts["empty_meshes"]),
			int(counts["lights"]), int(counts["lightmap_users"])])
	root.free()
	quit(0)


func _count(n: Node, counts: Dictionary) -> void:
	counts["nodes"] = int(counts["nodes"]) + 1
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null:
		counts["meshes"] = int(counts["meshes"]) + 1
		if mi.mesh == null:
			counts["empty_meshes"] = int(counts["empty_meshes"]) + 1
	if n is Light3D:
		counts["lights"] = int(counts["lights"]) + 1
	var lm: LightmapGI = n as LightmapGI
	if lm != null and lm.light_data != null:
		counts["lightmap_users"] = lm.light_data.get_user_count()
	for c in n.get_children():
		_count(c, counts)
