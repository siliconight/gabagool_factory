extends SceneTree
## Do a rowhome Empty's railings (Deli Counter 0.212.0) keep the contract body on its stoop, and leave the
## way up as it was? Cold run 9273's package is the subject; 9272's (the same stoop, no railings) is the
## control that the instrument can see a body leave the stoop at all.
##
## Four arms, each in its own copy of the Empty's scene from the package, 40 m apart along x. Each is a
## CharacterBody3D capsule of the contract's player (radius 0.35 m, height 1.8 m, walk 4.0 m/s;
## `deli_counter/agent_contract.json`), floor_max_angle 45 deg and nothing else set, driven for 3 s:
##   up        from the sidewalk straight at the front door along -z: onto the landing, as in 9271 and 9272
##   off_w     from the landing's middle along -x: the level railing's way
##   off_e     from the landing's middle along +x
##   flight_w  standing on the ramp halfway up the flight, along -x: the flight railing's way
## The stoop as Deli Counter 0.211.0 placed it (Godot frame, metres, the Empty unturned, its door at
## x = <door x>): the facade at z 6.15, the landing to z 7.05 with its top at y 0.5334, the ramp's foot
## at z 7.888. A body's feet are its centre less half its height. Prints what it measured: where each
## body ended, how far it moved the way it was driven, the lowest and highest its feet stood, and -- read
## on the first physics frame, after the tree is ready (cold run 9271's retraction) -- every `stoop_rail*`
## node the first copy loaded and where it stands.
##
##   godot --headless --path <package copy> -s res://rail_walk.gd -- <res:// Empty scene> <door x> <out.txt>

const RADIUS := 0.35
const HEIGHT := 1.8
const SPEED := 4.0
const FRAMES := 180
const GAP := 40.0
const LANDING_Y := 0.5334
const LANDING_Z := 6.6
const HEAD_Z := 7.05
const FOOT_Z := 7.888
const FLIGHT_Z := 7.3

var _bodies: Array[CharacterBody3D] = []
var _names: PackedStringArray = []
var _dirs: Array[Vector3] = []
var _starts: Array[Vector3] = []
var _low: PackedFloat64Array = []
var _high: PackedFloat64Array = []
var _houses: Array[Node3D] = []
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


func _walker(parent: Node3D, pos: Vector3, dir: Vector3, label: String) -> void:
	var body := CharacterBody3D.new()
	var shape := CollisionShape3D.new()
	var cap := CapsuleShape3D.new()
	cap.radius = RADIUS
	cap.height = HEIGHT
	shape.shape = cap
	body.add_child(shape)
	body.floor_max_angle = deg_to_rad(45.0)
	body.position = pos
	parent.add_child(body)
	_bodies.append(body)
	_names.append(label)
	_dirs.append(dir)
	_starts.append(pos)
	_low.append(1.0e9)
	_high.append(-1.0e9)


func _ramp_top(z: float) -> float:
	return LANDING_Y * (FOOT_Z - z) / (FOOT_Z - HEAD_Z)


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
	for k in range(4):
		var house := packed.instantiate() as Node3D
		house.position = Vector3(GAP * k, 0.0, 0.0)
		root.add_child(house)
		_houses.append(house)
	var stand := HEIGHT / 2.0 + 0.02
	_walker(root, Vector3(door_x, stand, 10.0), Vector3(0.0, 0.0, -1.0), "up")
	_walker(root, Vector3(GAP + door_x, LANDING_Y + stand, LANDING_Z), Vector3(-1.0, 0.0, 0.0), "off_w")
	_walker(root, Vector3(GAP * 2.0 + door_x, LANDING_Y + stand, LANDING_Z), Vector3(1.0, 0.0, 0.0), "off_e")
	_walker(root, Vector3(GAP * 3.0 + door_x, _ramp_top(FLIGHT_Z) + stand + 0.03, FLIGHT_Z),
		Vector3(-1.0, 0.0, 0.0), "flight_w")


func _physics_process(delta: float) -> bool:
	if _bodies.is_empty():
		return false
	_frame += 1
	if _frame == 1:
		var first := _houses[0]
		for n in first.find_children("stoop_rail*", "", true, false):
			var n3 := n as Node3D
			if n3 != null:
				var fmt := "loaded %s (%s) at %s rot %s"
				_log.append(fmt % [str(first.get_path_to(n3)), n3.get_class(), str(n3.global_position),
					str(n3.global_rotation_degrees)])
	for i in range(_bodies.size()):
		var b := _bodies[i]
		var v := b.velocity
		v.x = _dirs[i].x * SPEED
		v.z = _dirs[i].z * SPEED
		if b.is_on_floor():
			v.y = 0.0
		else:
			v.y -= 9.8 * delta
		b.velocity = v
		b.move_and_slide()
		var feet := b.global_position.y - HEIGHT / 2.0
		_low[i] = minf(_low[i], feet)
		_high[i] = maxf(_high[i], feet)
	if _frame >= FRAMES:
		for i in range(_bodies.size()):
			var b := _bodies[i]
			var p := b.global_position
			var moved := (p - _starts[i]).dot(_dirs[i])
			var fmt := "%-8s start (%8.3f, %6.3f)  end (%8.3f, %6.3f)  moved %7.3f  feet lowest %6.3f highest %6.3f end %6.3f  on floor %s"
			_log.append(fmt % [_names[i], _starts[i].x, _starts[i].z, p.x, p.z, moved, _low[i], _high[i],
				p.y - HEIGHT / 2.0, str(b.is_on_floor())])
		var f := FileAccess.open(_out, FileAccess.WRITE)
		for line in _log:
			f.store_line(line)
			print(line)
		f.close()
		quit(0)
	return false
