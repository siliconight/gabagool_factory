extends SceneTree
## Does the contract body, with NO step-up code, walk up a rowhome Empty's stoop (Deli Counter 0.211.0)?
##
## Four arms in one world, 40 m apart along x, each a CharacterBody3D capsule of the contract's player
## (radius 0.35 m, height 1.8 m, walk 4.0 m/s; `deli_counter/agent_contract.json`), floor_max_angle 45
## deg and nothing else set, driven straight at the house's front door along -z for 3 s:
##   stoop  the Empty's scene from the package, its stoop in front of its door
##   flat   nothing in the way: the drive moves a body 12 m, so a stop elsewhere is the geometry's
##   block  a solid box the stoop's visual size (no ramp): the instrument must see a body stopped
##   riser  one 7 in (0.1778 m) step the same size: above the 0.1025 m unassisted step, so stopped too
## Frame: Godot's, metres; a body's feet are its centre less half its height. Prints what it measured.
##
## RETRACTED, KEPT (cold run 9271): its "loaded" lines read `global_position` in `_initialize`, before the
## scene is inside the tree, and so print the origin for every node; they place nothing. Read them in the
## first `_physics_process` before relying on them. The arms' numbers are read there and stand.
##
##   godot --headless --path <package copy> -s res://stoop_walk.gd -- <res:// Empty scene> <door x> <out.txt>

const RADIUS := 0.35
const HEIGHT := 1.8
const SPEED := 4.0
const FRAMES := 180
const GAP := 40.0

var _bodies: Array = []
var _names: Array = []
var _best: Array = []
var _frame := 0
var _out := ""
var _log: PackedStringArray = []


func _box(parent: Node3D, pos: Vector3, size: Vector3) -> void:
	var body := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	body.add_child(shape)
	body.position = pos
	parent.add_child(body)


func _walker(parent: Node3D, x: float, name: String) -> void:
	var body := CharacterBody3D.new()
	var shape := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = RADIUS
	cap.height = HEIGHT
	shape.shape = cap
	body.add_child(shape)
	body.floor_max_angle = deg_to_rad(45.0)
	body.position = Vector3(x, HEIGHT / 2.0 + 0.02, 10.0)
	parent.add_child(body)
	_bodies.append(body)
	_names.append(name)
	_best.append(-1.0)


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 3:
		printerr("usage: -- <res:// Empty scene> <door x> <out.txt>")
		quit(2)
		return
	_out = args[2]
	var door_x := float(args[1])
	var root := Node3D.new()
	get_root().add_child(root)
	# the ground: grade at y = 0 under every arm
	_box(root, Vector3(GAP * 1.5, -0.5, 0.0), Vector3(GAP * 5.0, 1.0, 60.0))
	var packed := load(args[0]) as PackedScene
	if packed == null:
		printerr("not a scene: " + args[0])
		quit(1)
		return
	var house := packed.instantiate() as Node3D
	root.add_child(house)
	# the stoop's own colliders, as loaded, so the arms below stand where it stands
	for n in house.find_children("stoop*", "", true, false):
		var n3 := n as Node3D
		if n3 != null:
			_log.append("loaded %s at %s rot %s" % [n3.name, str(n3.global_position), str(n3.global_rotation_degrees)])
	# the controls: the stoop's visual box (0.9 m landing + two 0.2794 m treads, 0.5334 m high), and one riser
	var depth := 0.9 + 2.0 * 0.2794
	_box(root, Vector3(GAP * 2.0 + door_x, 0.5334 / 2.0, 6.15 + depth / 2.0), Vector3(1.5, 0.5334, depth))
	_box(root, Vector3(GAP * 3.0 + door_x, 0.1778 / 2.0, 6.15 + depth / 2.0), Vector3(1.5, 0.1778, depth))
	_walker(root, door_x, "stoop")
	_walker(root, GAP + door_x, "flat")
	_walker(root, GAP * 2.0 + door_x, "block")
	_walker(root, GAP * 3.0 + door_x, "riser")


func _physics_process(delta: float) -> bool:
	if _bodies.is_empty():
		return false
	_frame += 1
	for i in range(_bodies.size()):
		var b := _bodies[i] as CharacterBody3D
		var v := b.velocity
		v.x = 0.0
		v.z = -SPEED
		if b.is_on_floor():
			v.y = 0.0
		else:
			v.y -= 9.8 * delta
		b.velocity = v
		b.move_and_slide()
		var feet := b.global_position.y - HEIGHT / 2.0
		if feet > float(_best[i]):
			_best[i] = feet
	if _frame >= FRAMES:
		for i in range(_bodies.size()):
			var b := _bodies[i] as CharacterBody3D
			var feet := b.global_position.y - HEIGHT / 2.0
			var line := "%-6s start z 10.000  end z %7.3f  feet %6.3f (highest %6.3f)  on floor %s" % [_names[i], b.global_position.z, feet, float(_best[i]), str(b.is_on_floor())]
			_log.append(line)
		var f := FileAccess.open(_out, FileAccess.WRITE)
		for line in _log:
			f.store_line(line)
			print(line)
		f.close()
		quit(0)
	return false
