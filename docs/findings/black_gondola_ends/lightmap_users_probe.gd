extends SceneTree
## Is a mesh instance one of the LightmapGI's users? Prints and stops.
##
##     godot --headless --path <walk copy> --script res://lightmap_users_probe.gd -- <scene> <name filter> [...]
##
## For every LightmapGI in the scene: its user count, and every user path containing one of the filters. Then, for
## every MeshInstance3D whose path contains a filter, its gi_mode and whether some LightmapGI lists it. A static mesh
## no lightmap lists gets nothing from the baked lights. Draws no conclusion.


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var scene: Node = (load(args[0]) as PackedScene).instantiate()
	root.add_child(scene)
	await process_frame
	var filters: Array = Array(args.slice(1))
	var nodes: Array = []
	_walk(scene, nodes)
	var listed: Dictionary = {}
	for n in nodes:
		var lm: LightmapGI = n as LightmapGI
		if lm == null or lm.light_data == null:
			continue
		var d: LightmapGIData = lm.light_data
		var count: int = d.get_user_count()
		print("LIGHTMAP %s users %d" % [String(scene.get_path_to(lm)), count])
		for i in range(count):
			var up: String = String(d.get_user_path(i))
			var abs_path: String = String((lm.get_node_or_null(NodePath(up)) as Node).get_path()) if lm.get_node_or_null(NodePath(up)) != null else up
			listed[abs_path] = true
			for f in filters:
				if up.find(String(f)) >= 0:
					print("  user %d %s" % [i, up])
	for n in nodes:
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi == null:
			continue
		var p: String = String(mi.get_path())
		for f in filters:
			if p.find(String(f)) >= 0:
				print("MESH %s gi_mode %d listed %s" % [String(scene.get_path_to(mi)), mi.gi_mode, str(listed.has(p))])
	_exit(0)
