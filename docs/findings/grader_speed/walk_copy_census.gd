extends SceneTree
## Load the content a walk copy's level loads and count what came in: scenes, nodes, mesh
## instances, mesh instances with no mesh, lights, and the lightmap's user count. Measures and
## prints one line; names no cause.
##
##   godot --headless --path <walk copy> -s <this file>
##
## REFUTED, KEPT: the first version instantiated `res://_walk.tscn` and counted 1,380 nodes, 0
## meshes and 0 lights in every copy. `mission.tscn` loads its content in `_ready`, and a scene
## instantiated outside the tree never runs it, so that census counted the frame and could not
## have told a copy with every model from one with none. This one reads the paths the entry
## script loads (`load('res://....tscn')` in `mission.tscn`) and instantiates each.


func _initialize() -> void:
	var text: String = FileAccess.get_file_as_string("res://mission.tscn")
	var re: RegEx = RegEx.new()
	re.compile("load\\('(res://[^']+\\.tscn)'\\)")
	var counts: Dictionary = {"scenes": 0, "unloadable": 0, "nodes": 0, "meshes": 0,
		"empty_meshes": 0, "lights": 0, "lightmap_users": -1}
	for m in re.search_all(text):
		var path: String = (m as RegExMatch).get_string(1)
		var packed: PackedScene = ResourceLoader.load(
			path, "", ResourceLoader.CACHE_MODE_IGNORE) as PackedScene
		if packed == null:
			counts["unloadable"] = int(counts["unloadable"]) + 1
			continue
		counts["scenes"] = int(counts["scenes"]) + 1
		var root: Node = packed.instantiate()
		_count(root, counts)
		root.free()
	print("WALK_COPY scenes=%d unloadable=%d nodes=%d meshes=%d empty_meshes=%d lights=%d lightmap_users=%d"
		% [int(counts["scenes"]), int(counts["unloadable"]), int(counts["nodes"]),
			int(counts["meshes"]), int(counts["empty_meshes"]), int(counts["lights"]),
			int(counts["lightmap_users"])])
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
