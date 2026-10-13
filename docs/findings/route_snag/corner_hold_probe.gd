extends SceneTree
## Is the wall's end where warehouse_yard_001 seed_9206's guards are held a place that holds ANY body? (roadmap 242)
##
##   godot --headless --path <a copy of the lot's staged evaluation> -s res://corner_hold_probe.gd
##
## Laser Tag 0.31.0's guards stand there 14 times in 25 runs: centre (1.50, 16.87), 0.35 m west of the face
## building b1's west wall turns at x 1.85, the face made of two boxes -- `ext_col_0_W_seg0` (z 14.85 to
## 16.85) and the corner block `ext_col_0_S_seg22` (z 16.85 to 17.15) -- whose seam, z 16.85, is under the
## guard. Five of the fourteen moved nothing with a velocity pointing away from the wall
## (`docs/findings/stoop_breadth/enemy_stop_residue_0310.out.txt`).
##
## This loads the lot's `level.tscn`, frees every body in it but the level's, and puts a fresh capsule of the
## contract's size (radius 0.35, height 1.8, origin at the feet, colliding with the world layer only) at the
## guard's place. From the same start each time it drives the capsule with `move_and_slide` at 4 m/s for 20
## physics frames, in each of ten directions, and prints how far it went. It does that five ways:
##   both      the level as built
##   no_seg22  the corner block's shape disabled
##   no_seg0   the wall segment's shape disabled
##   two_boxes both disabled, and two BoxShape3D at the same extents, the seam kept: whether the shapes'
##             kind matters (the level's are convex hulls, `-convcolonly`)
##   one_box   both disabled, and one box standing where the two stood (x 1.85 to 2.15, z 14.85 to 17.15)
## and, as THE CONTROL, the same capsule started 0.30 m further west, touching nothing, in the level as built:
## it must go the full distance in every direction that leads away from the wall, or the probe cannot see a
## free body. It prints what it measured and stops.

const START := Vector3(1.500122, 0.016944, 16.87095)
const SPEED := 4.0
const FRAMES := 20
## the plan directions tried: the eight compass headings, the held guards' own velocity after the slide
## (keep-to-the-mesh's correction, (-0.752, 3.809)), and their path's heading, (0.303, 0.953)
const HEADINGS := {
	"+x": Vector2(1, 0), "-x": Vector2(-1, 0), "+z": Vector2(0, 1), "-z": Vector2(0, -1),
	"+x+z": Vector2(1, 1), "-x+z": Vector2(-1, 1), "+x-z": Vector2(1, -1), "-x-z": Vector2(-1, -1),
	"held velocity": Vector2(-0.752, 3.809), "path heading": Vector2(0.303, 0.953),
}

var _level: Node = null
## `-- --scale=4` runs at the grader's step (`run_map_eval.gd` sets `Engine.time_scale` 4: 1/15 s);
## `-- --vy=-6.5` starts each drive falling at that speed, as four of the five held guards were
var _scale: float = 1.0
var _vy: float = 0.0


func _initialize() -> void:
	_main.call_deferred()


## The shape under building b1's collider `name` -- b1 only: another building can carry the same names.
func _find(name: String) -> CollisionShape3D:
	var b1: Node = _level.find_child("b1", true, false)
	if b1 == null:
		return null
	for n in b1.find_children("*", "CollisionShape3D", true, false):
		var p: Node = (n as Node).get_parent()
		if p != null and String(p.name) == name:
			return n as CollisionShape3D
	return null


## A StaticBody3D on the world layer holding one box from `lo` to `hi`, world coordinates.
func _box(lo: Vector3, hi: Vector3) -> StaticBody3D:
	var sb := StaticBody3D.new()
	sb.collision_layer = 1
	var cs := CollisionShape3D.new()
	var b := BoxShape3D.new()
	b.size = hi - lo
	cs.shape = b
	sb.add_child(cs)
	root.add_child(sb)
	sb.global_position = (lo + hi) * 0.5
	return sb


func _body() -> CharacterBody3D:
	var body := CharacterBody3D.new()
	body.collision_layer = 0
	body.collision_mask = 1
	var cs := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = 0.35
	cap.height = 1.8
	cs.shape = cap
	cs.position.y = 0.9
	body.add_child(cs)
	return body


## Drive a fresh capsule from `start` along `heading` for FRAMES frames; the plan distance it went.
func _drive(start: Vector3, heading: Vector2) -> float:
	var body := _body()
	root.add_child(body)
	body.global_position = start
	var dir := Vector3(heading.x, 0.0, heading.y).normalized()
	await physics_frame
	body.velocity.y = _vy
	for i in FRAMES:
		body.velocity.x = dir.x * SPEED
		body.velocity.z = dir.z * SPEED
		if not body.is_on_floor():
			body.velocity.y -= 9.8 * _scale / float(Engine.physics_ticks_per_second)
		body.move_and_slide()
		await physics_frame
	var p: Vector3 = body.global_position
	body.free()
	return Vector2(p.x - start.x, p.z - start.z).length()


func _row(label: String, start: Vector3) -> void:
	var cells: Array[String] = []
	for key: String in HEADINGS:
		var went: float = await _drive(start, HEADINGS[key])
		cells.append("%s %.3f" % [key, went])
	print("  %-10s %s" % [label, ", ".join(cells)])


func _main() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--scale="):
			_scale = float(a.get_slice("=", 1))
		elif a.begins_with("--vy="):
			_vy = float(a.get_slice("=", 1))
	Engine.time_scale = _scale
	print("time_scale %.1f, starting fall speed %.2f m/s" % [_scale, _vy])
	var scene: PackedScene = load("res://level.tscn")
	_level = scene.instantiate()
	root.add_child(_level)
	for i in 3:
		await physics_frame
	# nothing moves in the level but the probe's capsule
	for n in _level.find_children("*", "CharacterBody3D", true, false):
		(n as Node).queue_free()
	await physics_frame
	var seg22 := _find("ext_col_0_S_seg22")
	var seg0 := _find("ext_col_0_W_seg0")
	if seg22 == null or seg0 == null:
		print("UNKNOWN SHAPE: ext_col_0_S_seg22 %s, ext_col_0_W_seg0 %s" % [str(seg22), str(seg0)])
		quit(2)
		return
	print("physics ticks per second %d, %d frames at %.1f m/s: the full distance is %.3f m" % [
		Engine.physics_ticks_per_second, FRAMES, SPEED, SPEED * FRAMES * _scale / float(Engine.physics_ticks_per_second)])
	for cs: CollisionShape3D in [seg22, seg0]:
		var box := cs.shape as BoxShape3D
		print("  %s: %s, centre %s, size %s" % [cs.get_parent().name, cs.shape.get_class(),
			str(cs.global_position), str(box.size) if box != null else "-"])
	print("plan distance moved from the held guards' place, by heading:")
	await _row("both", START)
	seg22.disabled = true
	await physics_frame
	await _row("no_seg22", START)
	seg22.disabled = false
	seg0.disabled = true
	await physics_frame
	await _row("no_seg0", START)
	seg22.disabled = true
	# the same two extents as boxes, the seam kept: separates the seam from the shapes' kind
	var a := _box(Vector3(1.85, 0.0, 14.85), Vector3(2.15, 4.3, 16.85))
	var c := _box(Vector3(1.85, 0.0, 16.85), Vector3(2.15, 4.3, 17.15))
	await physics_frame
	await _row("two_boxes", START)
	a.free()
	c.free()
	var one := _box(Vector3(1.85, 0.0, 14.85), Vector3(2.15, 4.3, 17.15))
	await physics_frame
	await _row("one_box", START)
	one.free()
	seg22.disabled = false
	seg0.disabled = false
	await physics_frame
	print("THE CONTROL, 0.30 m further west, touching nothing:")
	await _row("both", START + Vector3(-0.30, 0.0, 0.0))
	quit(0)
