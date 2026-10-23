extends SceneTree
## Ladder probe for deli_a03 ladder 0 (b0) in a COPY of walk_9383.
## Frame: Godot world metres, Y up. "feet" = CharacterBody3D origin (capsule
## shape sits 0.9 above it); "eye" = origin + 1.6 (the overlay's "pos").
## Prints measurements only.

const LADDER_BASE := Vector3(-43.0, 0.0, 9.49)
## the body's start: inside the through-hole footprint, off round coordinates
const START := Vector3(-43.0031, 0.0, 9.1123)

var _frame := 0
var _walk: Node
var _player: CharacterBody3D
var _phase := 0
var _t := 0.0
var _max_feet := -100.0
var _arm := ""
var _trace: Array[String] = []


func _initialize() -> void:
	var ps: PackedScene = load("res://_walk.tscn")
	_walk = ps.instantiate()
	root.add_child(_walk)
	_player = _walk.get_node("Player") as CharacterBody3D
	var dc: String = OS.get_environment("PROBE_ARM")
	_arm = dc if dc != "" else "as_shipped"


func _near(p: Vector3) -> bool:
	return Vector2(p.x - LADDER_BASE.x, p.z - LADDER_BASE.z).length() < 2.0


func _report_volumes() -> void:
	for grp in ["ladder", "ladder_area3d", "hatch"]:
		for n in get_nodes_in_group(grp):
			if not (n is Node3D) or not _near((n as Node3D).global_position):
				continue
			var line := "group=%s node=%s type=%s pos=%s" % [grp, n.get_path(), n.get_class(), (n as Node3D).global_position]
			if n is Area3D:
				for c in n.get_children():
					if c is CollisionShape3D and (c as CollisionShape3D).shape is BoxShape3D:
						var cs := c as CollisionShape3D
						var sz: Vector3 = (cs.shape as BoxShape3D).size
						var ctr: Vector3 = cs.global_position
						line += " box_centre=%s size=%s y_range=[%.3f, %.3f]" % [ctr, sz, ctr.y - sz.y * 0.5, ctr.y + sz.y * 0.5]
			print("VOL ", line)


func _report_rays() -> void:
	var space := _player.get_world_3d().direct_space_state
	# down-rays across the hole's footprint and just outside it (hole: world x
	# -43.65..-42.35, z 8.39..9.69 by ladder_geom.through_hole)
	var xs := [-44.003, -43.703, -43.403, -43.003, -42.603, -42.303, -42.003]
	var zs := [8.093, 8.493, 8.793, 9.113, 9.493, 9.793, 10.193]
	for x in xs:
		var row := "RAY x=%.3f" % x
		for z in zs:
			var q := PhysicsRayQueryParameters3D.create(Vector3(x, 9.013, z), Vector3(x, -1.0, z))
			q.collide_with_areas = false
			var hit := space.intersect_ray(q)
			var y := "none"
			if not hit.is_empty():
				y = "%.3f(%s)" % [hit["position"].y, (hit["collider"] as Node).name]
			row += " z%.3f:%s" % [z, y]
		print(row)


func _report_capsule() -> void:
	var space := _player.get_world_3d().direct_space_state
	var cap := CapsuleShape3D.new()
	cap.radius = 0.35
	cap.height = 1.8
	var feet := 3.313
	while feet < 7.4:
		var q := PhysicsShapeQueryParameters3D.new()
		q.shape = cap
		q.transform = Transform3D(Basis(), START + Vector3(0, feet + 0.9, 0))
		q.collide_with_areas = false
		q.exclude = [_player.get_rid()]
		var res := space.intersect_shape(q, 16)
		var names: Array[String] = []
		for r in res:
			names.append(String((r["collider"] as Node).name))
		var areas := 0
		var qa := PhysicsShapeQueryParameters3D.new()
		qa.shape = cap
		qa.transform = q.transform
		qa.collide_with_areas = true
		qa.collide_with_bodies = false
		var ra := space.intersect_shape(qa, 16)
		var an: Array[String] = []
		for r in ra:
			var c := r["collider"] as Node
			if c.is_in_group("ladder") or c.is_in_group("ladder_area3d"):
				an.append(String(c.name))
		print("CAP feet=%.3f solids=%s ladder_areas=%s" % [feet, names, an])
		feet += 0.25


func _physics_process(delta: float) -> bool:
	_frame += 1
	if _phase == 0:
		if _frame == 30:
			if _arm == "dc_area_in_group":
				for n in get_nodes_in_group("ladder_area3d"):
					n.add_to_group("ladder")
				print("ARM dc_area_in_group: ladder_area3d volumes joined group ladder")
			_report_volumes()
			_report_rays()
			_report_capsule()
			_player.global_position = START + Vector3(0, 3.313, 0)
			_player.velocity = Vector3.ZERO
			_player.set("_yaw", PI)
			_player.rotation.y = PI
			var cam := _player.get_node("Camera") as Camera3D
			cam.rotation.x = 1.2
			var ev := InputEventKey.new()
			ev.keycode = KEY_W
			ev.physical_keycode = KEY_W
			ev.pressed = true
			Input.parse_input_event(ev)
			_phase = 1
		return false
	if _phase == 1:
		_t += delta
		var feet := _player.global_position.y
		_max_feet = maxf(_max_feet, feet)
		if _frame % 15 == 0:
			_trace.append("t=%.2f feet=%.3f eye=%.3f on_ladder=%s x=%.3f z=%.3f" % [_t, feet, feet + 1.6, _player.call("_current_ladder") != null, _player.global_position.x, _player.global_position.z])
		if _t > 6.0:
			for l in _trace:
				print("CLIMB ", l)
			print("CLIMB arm=%s max_feet=%.3f (roof top at local 6.6)" % [_arm, _max_feet])
			_phase = 2
			quit(0)
	return false
