extends SceneTree
## What stands where restaurant_row_001 seed_9104's enemies stop (the stoop breadth's one "found on the way").
##
## Laser Tag's report for that lot, in cold runs 9271 to 9274 and in the breadth's `stoop` arm, carries three
## EnemyStuck events at two points, the same to the centimetre in two runs: LT_Enemy_02 at (-2.05, 0.02,
## 12.24) at t 9.07 in runs 10 and 15, and LT_Enemy_04 at (-2.75, 0.02, 12.24) at t 15.07 in run 10.
## Laser Tag's position is a body's FEET (its origin), Godot metres, y up.
##
## Loads the staged evaluation level (`level.tscn`) headless, waits for the physics space, and at each point:
##   - every collider a capsule of the contract's player size (radius R, height H, standing on the point)
##     overlaps, and every one an inflated capsule (R + PAD) overlaps -- what the body touches, and what is
##     within PAD of it;
##   - eight rays at waist height (0.9 m), every 45 degrees from +x, to MAX_RAY: the nearest solid each way,
##     its name and its distance from the point.
## Collider names are the node path of the CollisionObject3D under the level. Prints what it measured and quits.
##
##     godot --headless --path <imported staging copy> -s res://enemy_pin_probe.gd

const POINTS := [Vector3(-2.05, 0.02, 12.24), Vector3(-2.75, 0.02, 12.24)]
const R := 0.35
const H := 1.8
const PAD := 0.3
const MAX_RAY := 6.0
const WAIT := 10

var _frames := 0
var _level: Node = null


func _initialize() -> void:
	var packed := load("res://level.tscn") as PackedScene
	if packed == null:
		print("[pin] FAILED to load res://level.tscn")
		quit(2)
		return
	_level = packed.instantiate()
	root.add_child(_level)


func _name_of(obj: Object) -> String:
	var n := obj as Node
	if n == null:
		return str(obj)
	return str(_level.get_path_to(n))


func _overlaps(space: PhysicsDirectSpaceState3D, feet: Vector3, radius: float) -> PackedStringArray:
	var cap := CapsuleShape3D.new()
	cap.radius = radius
	cap.height = H
	var q := PhysicsShapeQueryParameters3D.new()
	q.shape = cap
	q.transform = Transform3D(Basis(), feet + Vector3(0.0, H / 2.0 + 0.01, 0.0))
	var out: PackedStringArray = []
	for hit in space.intersect_shape(q, 64):
		var nm := _name_of(hit["collider"])
		if not out.has(nm):
			out.append(nm)
	return out


func _physics_process(_delta: float) -> bool:
	_frames += 1
	if _frames < WAIT:
		return false
	var space := (_level as Node3D).get_world_3d().direct_space_state
	for p in POINTS:
		var feet: Vector3 = p
		print("[pin] point %s" % str(feet))
		var touch := _overlaps(space, feet, R)
		var near := _overlaps(space, feet, R + PAD)
		print("[pin]   a %.2f m capsule overlaps %d: %s" % [R, touch.size(), ", ".join(touch)])
		print("[pin]   a %.2f m capsule overlaps %d: %s" % [R + PAD, near.size(), ", ".join(near)])
		for k in range(8):
			var a := deg_to_rad(45.0 * k)
			var dir := Vector3(cos(a), 0.0, sin(a))
			var from := feet + Vector3(0.0, 0.9, 0.0)
			var rq := PhysicsRayQueryParameters3D.create(from, from + dir * MAX_RAY)
			var hit := space.intersect_ray(rq)
			if hit.is_empty():
				print("[pin]   ray %3d deg: nothing within %.1f m" % [45 * k, MAX_RAY])
			else:
				var hp: Vector3 = hit["position"]
				print("[pin]   ray %3d deg: %.2f m to %s" % [45 * k, from.distance_to(hp), _name_of(hit["collider"])])
	quit(0)
	return true
