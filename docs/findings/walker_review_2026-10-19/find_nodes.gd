extends SceneTree
## Where things stand in a walk copy: every Node3D whose name holds one of the given words, with its global
## position and, for drawn nodes, the world box of what it draws -- for aiming review cameras at real objects. A
## probe: prints what it measured and stops.
##
##   godot --headless --path <walk copy> --script res://find_nodes.gd -- <out.json> <word,word,...>
##
## Frame: Godot metres, world space, y up. Words match the node's name, case-folded. Nested matches are kept: a
## caller wants the outermost match of a kind and can drop its children by path.


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _initialize() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 2:
		print("[find] USAGE: <out.json> <word,word,...>")
		quit(2)
		return
	var words: PackedStringArray = args[1].to_lower().split(",")
	await process_frame
	var main_scene: String = String(ProjectSettings.get_setting("application/run/main_scene", ""))
	var packed: PackedScene = load(main_scene) as PackedScene
	var scene: Node = packed.instantiate()
	root.add_child(scene)
	for i in range(20):
		await process_frame
	var nodes: Array = []
	_walk(scene, nodes)
	var rows: Array = []
	for n in nodes:
		var n3: Node3D = n as Node3D
		if n3 == null:
			continue
		var nm: String = String(n3.name).to_lower()
		var hit: String = ""
		for w in words:
			if w != "" and nm.contains(w):
				hit = w
				break
		if hit == "":
			continue
		var row: Dictionary = {"word": hit, "path": str(n3.get_path()), "class": n3.get_class()}
		var p: Vector3 = n3.global_position
		row["pos"] = [snappedf(p.x, 0.001), snappedf(p.y, 0.001), snappedf(p.z, 0.001)]
		var v: VisualInstance3D = n3 as VisualInstance3D
		if v != null:
			var a: AABB = v.global_transform * v.get_aabb()
			row["box"] = [snappedf(a.position.x, 0.001), snappedf(a.position.y, 0.001), snappedf(a.position.z, 0.001),
				snappedf(a.end.x, 0.001), snappedf(a.end.y, 0.001), snappedf(a.end.z, 0.001)]
		rows.append(row)
	var fh: FileAccess = FileAccess.open(args[0], FileAccess.WRITE)
	fh.store_string(JSON.stringify({"scene": main_scene, "words": words, "rows": rows}, " "))
	fh.close()
	print("[find] %d nodes matched %s" % [rows.size(), args[1]])
	quit(0)
