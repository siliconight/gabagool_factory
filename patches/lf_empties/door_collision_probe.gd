extends SceneTree
## Does anything stop a body walking into an Empty through its front door?
##
##     godot --headless --path <package> --script res://door_collision_probe.gd -- <lot scene> <door x> <front z>
##
## Loads one Empty's scene (`res://lot/<id>/site.tscn`) on its own, at the
## origin, and lets physics settle. Then, in that scene's frame (Godot Y-up,
## metres, the Empty's front facing +z as Deli Counter's S wall exports):
##   * casts rays straight at the front, from z = <front z> + 2 toward -z,
##     at 1.0 m and 2.0 m above the ground, every 0.1 m across x from -3.5 to
##     +3.5, and prints how deep each one gets before it hits anything --
##     a wall stops it at the face, an open doorway lets it through;
##   * sweeps a capsule (radius 0.4, height 1.8, the walk body's) from
##     <front z> + 1.5 toward -z at x = <door x> and prints how far it gets.
## Prints what it measured and quits; names no cause.


func _initialize() -> void:
	_run()


func _run() -> void:
	var t0: int = Time.get_ticks_msec()
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 3:
		print("PROBE usage: <lot scene> <door x> <front z>")
		quit(2)
		return
	var scene_path: String = args[0]
	var door_x: float = float(args[1])
	var front_z: float = float(args[2])
	var packed: PackedScene = load(scene_path) as PackedScene
	if packed == null:
		print("PROBE cannot load %s" % scene_path)
		quit(2)
		return
	var root3: Node3D = Node3D.new()
	root.add_child(root3)
	root3.add_child(packed.instantiate())
	for i in range(10):
		await physics_frame
	var space: PhysicsDirectSpaceState3D = root3.get_world_3d().direct_space_state
	for h in [1.0, 2.0]:
		var line: String = "PROBE rays at %.1f m:" % h
		var x: float = -3.5
		while x <= 3.5001:
			var from := Vector3(x, h, front_z + 2.0)
			var to := Vector3(x, h, front_z - 8.0)
			var hit: Dictionary = space.intersect_ray(PhysicsRayQueryParameters3D.create(from, to))
			var depth: float = 99.0
			if not hit.is_empty():
				depth = front_z - float((hit["position"] as Vector3).z)
			line += " %.1f:%s" % [x, ("open" if hit.is_empty() else "%.2f" % depth)]
			x += 0.1
		print(line)
	var shape := CapsuleShape3D.new()
	shape.radius = 0.4
	shape.height = 1.8
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = shape
	q.transform = Transform3D(Basis(), Vector3(door_x, 0.95, front_z + 1.5))
	q.motion = Vector3(0.0, 0.0, -4.0)
	var frac: PackedFloat32Array = space.cast_motion(q)
	print("PROBE capsule at x %.2f from z %.2f toward -z: safe fraction %.3f of 4.0 m -> stops at z %.2f (front %.2f)"
		% [door_x, front_z + 1.5, frac[0], front_z + 1.5 - 4.0 * frac[0], front_z])
	print("PROBE done in %d ms" % (Time.get_ticks_msec() - t0))
	quit(0)
