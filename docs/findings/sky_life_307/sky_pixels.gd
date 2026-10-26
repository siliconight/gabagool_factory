extends SceneTree
# Windowed, in a BARE scene: a Camera3D at EYE looking at TARGET and copies of a walk copy's SkyBirds and SkyPlane
# nodes, nothing else. (A first version moved the walk's own camera, and the walk's warm-up sweep drives a camera of
# its own for some 560 frames: it read 0 for a plain box too, and is refuted.) After FRAMES frames it counts the
# frame's pixels unlike the clear colour (any channel more than 0.08 from it), then the same with a plain BoxMesh
# MeshInstance3D at TARGET, 4 m, for a control that the count can move. Measurements only.

const FRAMES := 20
const EYE := Vector3(7.9, 1.7, 16.7)
var target := Vector3(7.9, 30.0, -30.0)
var _n := 0
var _stage := 0
var _world: Node3D
var _cam: Camera3D

func _init() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 3:
		target = Vector3(float(args[0]), float(args[1]), float(args[2]))
	var ps: PackedScene = load("res://_walk.tscn")
	var walk: Node = ps.instantiate()
	_world = Node3D.new()
	root.add_child(_world)
	for n in ["SkyBirds", "SkyPlane"]:
		var g: Node = walk.get_node(n)
		var copy: Node = g.duplicate()
		_world.add_child(copy)
	walk.free()
	RenderingServer.set_default_clear_color(Color(0, 0, 0))
	_cam = Camera3D.new()
	_world.add_child(_cam)
	_cam.far = 4000.0
	_cam.current = true

func _count() -> int:
	var img: Image = root.get_texture().get_image()
	var c := 0
	for y in range(0, img.get_height(), 2):
		for x in range(0, img.get_width(), 2):
			var p: Color = img.get_pixel(x, y)
			if p.r > 0.08 or p.g > 0.08 or p.b > 0.08:
				c += 1
	return c

func _process(_d: float) -> bool:
	_cam.global_position = EYE
	_cam.look_at(target)
	_n += 1
	if _n == FRAMES:
		if _stage == 0:
			print("sky nodes alone, target %s: %d lit pixel(s) of every 4th" % [str(target), _count()])
			var mi := MeshInstance3D.new()
			var bx := BoxMesh.new()
			bx.size = Vector3(4, 4, 4)
			mi.mesh = bx
			_world.add_child(mi)
			mi.global_position = target
		else:
			print("plus a plain 4 m box at the target: %d" % _count())
			quit()
		_stage += 1
		_n = 0
	return false
