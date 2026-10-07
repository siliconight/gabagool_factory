extends SceneTree
## Shoot the fixture control's floor under each lamp, baked or not, and print
## what the 8-bit frame measured. Launched by fixture_control.py:
##
##     godot --path <control> --rendering-method gl_compatibility \
##         --script res://fixture_shoot.gd -- <baked|unbaked> <out prefix>
##
## Frame: Godot metres, y up; each camera 1.2 m over the floor straight under
## its lamp, looking down, 90 degree vertical field, 400 x 400 window. Luma
## is Rec.709 on the sRGB bytes that reached the frame (tonemap linear,
## exposure 1, no ambient, black sky) -- a measurement of the picture, not of
## light. Prints between fences and quits itself.

const SETTLE := 40
const BEGIN := "<<<FIXTURE_SHOOT_JSON"
const END := "FIXTURE_SHOOT_JSON>>>"

var _mode := "baked"
var _prefix := "shot"
var _cams: Array = []
var _i := 0
var _frames := 0
var _out: Array = []


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 2:
		_mode = args[0]
		_prefix = args[1]
	root.size = Vector2i(400, 400)
	var scene := (load("res://bake.tscn") as PackedScene).instantiate()
	root.add_child(scene)
	if _mode == "unbaked":
		var lm := scene.get_node_or_null("Lightmap")
		if lm != null:
			lm.free()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0, 0, 0)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_DISABLED
	env.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	var we := WorldEnvironment.new()
	we.environment = env
	root.add_child(we)
	# THE LAMP'S OWN position, not global_position. In `_initialize` the tree
	# is not running yet, so `global_position` errors "!is_inside_tree()" and
	# returns the identity: the first run stood both cameras at x 0, between
	# the pools, and read 0.00 unbaked and a faint rim baked -- an instrument
	# fault that looked like a finding. The bake scene's root is at the
	# identity, so a lamp's local position is its world position.
	for n in scene.find_children("Lamp_*", "Light3D", true, false):
		var l := n as Light3D
		var cam := Camera3D.new()
		cam.fov = 90.0
		cam.position = Vector3(l.position.x, 1.2, l.position.z)
		cam.rotation_degrees = Vector3(-90.0, 0.0, 0.0)
		root.add_child(cam)
		_cams.append([String(l.name), cam])
	if _cams.is_empty():
		print(BEGIN)
		print(JSON.stringify({"error": "no Lamp_* lights in bake.tscn"}))
		print(END)
		quit(1)
		return
	(_cams[0][1] as Camera3D).current = true


func _luma(img: Image, x0: int, y0: int, x1: int, y1: int) -> float:
	var s := 0.0
	for y in range(y0, y1):
		for x in range(x0, x1):
			var c := img.get_pixel(x, y)
			s += 0.2126 * c.r8 + 0.7152 * c.g8 + 0.0722 * c.b8
	return s / float((x1 - x0) * (y1 - y0))


func _process(_delta: float) -> bool:
	_frames += 1
	if _frames < SETTLE:
		return false
	var img := root.get_texture().get_image()
	var w := img.get_width()
	var h := img.get_height()
	var name: String = _cams[_i][0]
	var png := "%s_%s_%s.png" % [_prefix, _mode, name]
	img.save_png(png)
	# centre: the 40 x 40 px under the lamp (+-0.12 m of floor). one_metre:
	# a 40 x 40 px window centred 1.0 m out along +x -- at 1.2 m and a 90
	# degree field, 200 px span 1.2 m, so 1.0 m is 167 px off centre.
	var off := int(round(1.0 * (h / 2) / 1.2))
	var cam: Camera3D = _cams[_i][1]
	_out.append({"lamp": name, "mode": _mode, "png": png,
		"camera": [snappedf(cam.global_position.x, 0.01), snappedf(cam.global_position.y, 0.01),
			snappedf(cam.global_position.z, 0.01)],
		"current": cam.is_current(),
		"centre": snappedf(_luma(img, w / 2 - 20, h / 2 - 20, w / 2 + 20, h / 2 + 20), 0.01),
		"one_metre": snappedf(_luma(img, w / 2 + off - 20, h / 2 - 20, w / 2 + off + 20, h / 2 + 20), 0.01),
		"frame": snappedf(_luma(img, 0, 0, w, h), 0.01)})
	_i += 1
	if _i >= _cams.size():
		print(BEGIN)
		print(JSON.stringify(_out))
		print(END)
		quit()
		return true
	(_cams[_i][1] as Camera3D).current = true
	_frames = 0
	return false
