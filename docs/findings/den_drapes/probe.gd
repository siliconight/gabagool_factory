extends SceneTree
## Zoo 1.91.0's window_drape, framed twice and quit: from the room under a warm, low club light,
## and from the street (its back, through where the glass is) under a cool streetlight.
## Windowed, GL Compatibility; saves room.png and street.png beside this file.
##
##   godot --path <this project> --script res://probe.gd

var _frame: int = 0
var _cam: Camera3D = null
var _warm: OmniLight3D = null
var _cool: OmniLight3D = null


func _initialize() -> void:
	var ps: PackedScene = load("res://drape.glb") as PackedScene
	if ps == null:
		print("PROBE no drape.glb scene")
		quit(2)
		return
	root.add_child(ps.instantiate())
	var env: WorldEnvironment = WorldEnvironment.new()
	var e: Environment = Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.03, 0.03, 0.04)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.25, 0.22, 0.24)
	e.ambient_light_energy = 0.35
	env.environment = e
	root.add_child(env)
	_warm = OmniLight3D.new()
	_warm.light_color = Color(1.0, 0.55, 0.42)
	_warm.light_energy = 2.2
	_warm.omni_range = 4.0
	_warm.position = Vector3(0.7, 0.5, 1.3)
	root.add_child(_warm)
	_cool = OmniLight3D.new()
	_cool.light_color = Color(0.72, 0.84, 1.0)
	_cool.light_energy = 2.2
	_cool.omni_range = 5.0
	_cool.position = Vector3(-0.9, 1.0, -1.6)
	_cool.visible = false
	root.add_child(_cool)
	_cam = Camera3D.new()
	_cam.fov = 50.0
	_cam.position = Vector3(0.0, 0.0, 2.4)
	root.add_child(_cam)


func _process(_delta: float) -> bool:
	_frame += 1
	if _frame == 30:
		root.get_texture().get_image().save_png("res://room.png")
		print("PROBE saved room.png")
		# the street side: turn round to the back, swap the light
		_cam.position = Vector3(0.0, 0.0, -2.4)
		_cam.rotation_degrees = Vector3(0.0, 180.0, 0.0)
		_warm.visible = false
		_cool.visible = true
	elif _frame == 60:
		root.get_texture().get_image().save_png("res://street.png")
		print("PROBE saved street.png")
		return true
	return false
