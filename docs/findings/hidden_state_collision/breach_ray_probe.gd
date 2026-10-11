extends SceneTree
## Does a hidden interactive state still collide? (roadmap 175)
##
##     godot --headless --path <package> --script <abs path>/breach_ray_probe.gd -- res://lot/deli_a01/site.tscn
##
## Instantiates the named building scene, waits for physics, and for every node whose name ends in
## `_breached` (Deli Counter's hidden sibling of an intact breach wall, `visible = false`) prints:
## its visibility; every CollisionObject3D under it with its layer and mask; and what a ray hits
## when cast through the node's origin along its local Z, from 1.5 m off either side, with the
## full mask -- the collider's node path, and whether it belongs to the hidden state. Godot frame,
## metres. It prints what it measured and stops.

var _scene_path := ""


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	_scene_path = args[0] if args.size() > 0 else "res://lot/deli_a01/site.tscn"
	_run.call_deferred()


func _bodies(n: Node, out: Array) -> void:
	if n is CollisionObject3D:
		out.append(n)
	for c in n.get_children():
		_bodies(c, out)


func _owner_state(n: Node) -> String:
	var p := n
	while p != null:
		if String(p.name).ends_with("_breached"):
			return String(p.name)
		p = p.get_parent()
	return ""


func _run() -> void:
	var packed := load(_scene_path) as PackedScene
	if packed == null:
		print("[breach] cannot load %s" % _scene_path)
		_exit(2)
		return
	var root := packed.instantiate()
	get_root().add_child(root)
	for _i in 4:
		await physics_frame
	var space := (root as Node3D).get_world_3d().direct_space_state
	var hidden: Array = []
	for n in root.get_children():
		if String(n.name).ends_with("_breached"):
			hidden.append(n)
	print("[breach] %s: %d hidden breached state(s)" % [_scene_path, hidden.size()])
	var hits_hidden := 0
	for n in hidden:
		var node := n as Node3D
		var bodies: Array = []
		_bodies(node, bodies)
		var desc := []
		for b in bodies:
			var co := b as CollisionObject3D
			desc.append("%s layer %d mask %d" % [String(co.name), co.collision_layer, co.collision_mask])
		var origin: Vector3 = node.global_transform.origin + Vector3(0.0, 1.2, 0.0)
		var axis: Vector3 = node.global_transform.basis.z.normalized()
		var verdicts := []
		for side in [1.0, -1.0]:
			var from: Vector3 = origin + axis * 1.5 * side
			var q := PhysicsRayQueryParameters3D.create(from, origin - axis * 1.5 * side)
			q.collision_mask = 0xFFFFFFFF
			var hit := space.intersect_ray(q)
			if hit.is_empty():
				verdicts.append("side %+d: nothing" % int(side))
			else:
				var col := hit["collider"] as Node
				var mine := _owner_state(col) != ""
				if mine:
					hits_hidden += 1
				verdicts.append("side %+d: %s%s" % [int(side), String(root.get_path_to(col)), " (THE HIDDEN STATE)" if mine else ""])
		print("[breach]   %s visible=%s bodies [%s] | %s" % [String(node.name), str(node.visible), ", ".join(desc), "; ".join(verdicts)])
	print("[breach] rays that hit a hidden state: %d of %d" % [hits_hidden, hidden.size() * 2])
	_exit(0)


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())
