extends SceneTree

## WHAT AN UNNAMED COLLIDER IS. `walkable_edge.gd`'s owner table carried
## `GreyboxBase/@StaticBody3D@19803` on cold run 9317's package: a static body
## Godot named itself, standing 1.05 m up in both mission buildings. This
## instantiates the package's main scene, finds every body whose name starts
## with "@", and prints its parent, its shapes and each shape's extent, so the
## thing can be named. Prints and stops.
##
##   godot --headless --path <pkg> --script res://body_names.gd


func _initialize() -> void:
	_run()


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _run() -> void:
	await process_frame
	var main_scene: String = String(ProjectSettings.get_setting("application/run/main_scene", ""))
	var packed: PackedScene = load(main_scene) as PackedScene
	var scene: Node = packed.instantiate()
	root.add_child(scene)
	for i in range(5):
		await process_frame
	var nodes: Array = []
	_walk(scene, nodes)
	var found: int = 0
	for n in nodes:
		if not (n is StaticBody3D) or not String(n.name).begins_with("@"):
			continue
		found += 1
		var body: StaticBody3D = n as StaticBody3D
		print("[body] %s  parent %s (%s)" % [body.get_path(), body.get_parent().name, body.get_parent().get_class()])
		for c in body.get_children():
			var cs: CollisionShape3D = c as CollisionShape3D
			if cs == null:
				print("   child %s (%s)" % [c.name, c.get_class()])
				continue
			var shape: Shape3D = cs.shape
			var desc: String = shape.get_class() if shape != null else "no shape"
			if shape is BoxShape3D:
				desc += " size %s" % [(shape as BoxShape3D).size]
			elif shape is ConvexPolygonShape3D:
				var pts: PackedVector3Array = (shape as ConvexPolygonShape3D).points
				var lo := Vector3(1e9, 1e9, 1e9)
				var hi := Vector3(-1e9, -1e9, -1e9)
				for p in pts:
					lo = lo.min(p)
					hi = hi.max(p)
				desc += " %d points, local extent %s .. %s" % [pts.size(), lo, hi]
			print("   shape %s at world %s: %s" % [cs.name, cs.global_transform.origin, desc])
		var sib: Array = []
		for s in body.get_parent().get_children():
			if s != body and (s.global_transform.origin - body.global_transform.origin).length() < 0.5:
				sib.append(s.name)
		print("   nodes within 0.5 m under the same parent: %s" % [sib])
	print("[body] %d unnamed static bodies" % found)
	quit(0)
