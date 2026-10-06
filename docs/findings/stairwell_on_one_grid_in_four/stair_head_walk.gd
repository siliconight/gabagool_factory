extends Node
## Walk a capsule down, then up, one stair of one building, with no step-up:
## the body Laser Tag's harness stands (agent_contract player radius 0.35,
## height 1.8, CharacterBody3D defaults, floor_max_angle 45 deg). Then do it
## again with the stair's collision ramp lowered by `lower_m` -- the control.
## Measures where the body ends; names no cause.
##
## Settings ([stair_head_walk] in project.godot): glb (res://), ramp (node
## name of the ramp's collider, e.g. "stair1ramp_0-convcolonly"), down_from
## and down_to, up_from and up_to ([x, y, z], the building's Godot frame),
## lower_m (the control's offset), seconds per walk.

const RADIUS := 0.35
const HEIGHT := 1.8
const SPEED := 2.0
const GRAVITY := 9.8


func _ready() -> void:
	await get_tree().process_frame
	var glb: String = ProjectSettings.get_setting("stair_head_walk/glb", "")
	var ramp_name: String = ProjectSettings.get_setting("stair_head_walk/ramp", "")
	var lower_m: float = float(ProjectSettings.get_setting("stair_head_walk/lower_m", 0.2))
	var seconds: float = float(ProjectSettings.get_setting("stair_head_walk/seconds", 6.0))
	var walks: Array = []
	for key in ["down", "up"]:
		var a: Array = JSON.parse_string(str(ProjectSettings.get_setting("stair_head_walk/%s_from" % key, "[]")))
		var b: Array = JSON.parse_string(str(ProjectSettings.get_setting("stair_head_walk/%s_to" % key, "[]")))
		walks.append([key, Vector3(a[0], a[1], a[2]), Vector3(b[0], b[1], b[2])])
	var out := {"glb": glb, "ramp": ramp_name, "lower_m": lower_m, "runs": []}
	for lowered in [false, true]:
		var packed: PackedScene = load(glb)
		var inst: Node3D = packed.instantiate()
		add_child(inst)
		var ramp_found := false
		for n in inst.find_children("*", "", true, false):
			if str(n.name).begins_with(ramp_name.split("-")[0]) and n is StaticBody3D:
				ramp_found = true
				if lowered:
					(n as Node3D).position.y -= lower_m
		await get_tree().physics_frame
		await get_tree().physics_frame
		for w in walks:
			var rep: Dictionary = await _walk(w[1], w[2], seconds)
			rep["walk"] = w[0]
			rep["ramp_lowered"] = lowered
			rep["ramp_found"] = ramp_found
			out["runs"].append(rep)
		inst.queue_free()
		await get_tree().physics_frame
	print("STAIR_WALK_BEGIN")
	print(JSON.stringify(out))
	print("STAIR_WALK_END")
	get_tree().quit()


func _walk(from_pt: Vector3, to_pt: Vector3, seconds: float) -> Dictionary:
	var body := CharacterBody3D.new()
	var shape := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = RADIUS
	cap.height = HEIGHT
	shape.shape = cap
	shape.position.y = HEIGHT * 0.5
	body.add_child(shape)
	add_child(body)
	body.global_position = from_pt + Vector3(0, 0.05, 0)
	await get_tree().physics_frame
	var dir := Vector3(to_pt.x - from_pt.x, 0.0, to_pt.z - from_pt.z).normalized()
	var t := 0.0
	var dt := 1.0 / float(Engine.physics_ticks_per_second)
	var best := body.global_position.distance_to(to_pt)
	while t < seconds:
		var v := dir * SPEED
		v.y = body.velocity.y - GRAVITY * dt if not body.is_on_floor() else 0.0
		body.velocity = v
		body.move_and_slide()
		best = minf(best, body.global_position.distance_to(to_pt))
		if body.global_position.distance_to(to_pt) < 0.4:
			break
		await get_tree().physics_frame
		t += dt
	var end := body.global_position
	body.queue_free()
	return {"from": [from_pt.x, from_pt.y, from_pt.z], "to": [to_pt.x, to_pt.y, to_pt.z],
			"end": [snappedf(end.x, 0.01), snappedf(end.y, 0.01), snappedf(end.z, 0.01)],
			"closest_m": snappedf(best, 0.01), "seconds": snappedf(t, 0.01),
			"arrived": end.distance_to(to_pt) < 0.4}
