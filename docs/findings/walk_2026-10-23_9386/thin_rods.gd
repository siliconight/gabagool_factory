extends SceneTree
## Every visible VisualInstance3D shaped like a rod -- two world AABB sides under THIN, the third over LONG -- in the
## whole scene, `near` when it meets a box round the office's stairwell (the walker's finding 4, cold run 9386's walk copy). Godot world metres, Y up.
## Prints measurements only: path, class, AABB, whether a CollisionObject3D sits among its ancestors or children.

const THIN := 0.1
const LONG := 1.0
## the walker stood at (54.6, 2.2, 1.6) looking down the stair; a 12 m box round it
const BOX_MIN := Vector3(46.0, -1.0, -6.0)
const BOX_MAX := Vector3(64.0, 8.0, 10.0)

var _frame := 0


func _initialize() -> void:
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())


func _has_collision(n: Node) -> bool:
	var p: Node = n
	while p != null:
		if p is CollisionObject3D:
			return true
		p = p.get_parent()
	for c in n.find_children("*", "CollisionShape3D", true, false):
		return true
	return false


func _process(_d: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	var box := AABB(BOX_MIN, BOX_MAX - BOX_MIN)
	for n in root.find_children("*", "VisualInstance3D", true, false):
		var v: VisualInstance3D = n
		if not v.is_visible_in_tree():
			continue
		var bb: AABB = v.global_transform * v.get_aabb()
		var s: Vector3 = bb.size
		var dims: Array[float] = [s.x, s.y, s.z]
		dims.sort()
		if dims[0] < THIN and dims[1] < THIN and dims[2] > LONG:
			print("ROD near=%s %s class=%s pos=%s size=%s collision=%s" % [
				box.intersects(bb), v.get_path(), v.get_class(), bb.position, s, _has_collision(v)])
	quit()
	return true
