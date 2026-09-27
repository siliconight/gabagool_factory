extends Node
## A FLASHLIGHT FOR THE WALK COPY, off by default and toggled with F.
##
## The walker, on cold run 9086's night package: "its so dark I cant find my
## way outside of this building". A level you cannot navigate is a finding and
## this does not make it stop being one -- which is why the light starts OFF
## and says so in the console.
##
## `walk_export.py` has carried `--headlamp` since it was written, and its own
## help explains why it is not the answer here: "OFF by default: the package's
## own lighting is part of what you are here to judge, and a headlamp hides a
## level that ships dark." An always-on lamp trades one problem for the
## opposite one. A TOGGLE keeps both: press F to get out of a black room,
## press F again to judge it.
##
## Walk copies only. The package ships no player and therefore no flashlight;
## the real one belongs to the game runtime, whose character this stands in
## for.

## A 1990s hand torch, not a film light: a warm-white incandescent beam, tight
## enough to be a beam and wide enough to walk by.
const ENERGY := 4.0
const RANGE_M := 18.0
const CONE_DEG := 26.0
const COLOR := Color(1.0, 0.94, 0.82)
## The lamp sits at the eye and a hair forward, so its own cone never clips
## the camera's near plane.
const FORWARD := 0.15

var _lamp: SpotLight3D = null
var _on: bool = false


func _ready() -> void:
	var cam: Camera3D = _find_camera(get_tree().current_scene)
	if cam == null:
		push_warning("[walk_flashlight] no Camera3D found; no flashlight")
		return
	_lamp = SpotLight3D.new()
	_lamp.name = &"WalkFlashlight"
	_lamp.light_color = COLOR
	_lamp.light_energy = ENERGY
	_lamp.spot_range = RANGE_M
	_lamp.spot_angle = CONE_DEG
	_lamp.spot_angle_attenuation = 1.1
	_lamp.spot_attenuation = 1.4
	_lamp.shadow_enabled = false
	_lamp.light_bake_mode = Light3D.BAKE_DISABLED
	_lamp.position = Vector3(0.0, 0.0, -FORWARD)
	_lamp.visible = false
	cam.add_child(_lamp)
	print("[walk_flashlight] F toggles a flashlight. It starts OFF on purpose: "
		+ "a level too dark to walk IS a finding, and a lamp that is always on "
		+ "hides it.")


func _find_camera(n: Node) -> Camera3D:
	if n == null:
		return null
	var c: Camera3D = n as Camera3D
	if c != null:
		return c
	for child in n.get_children():
		var found: Camera3D = _find_camera(child)
		if found != null:
			return found
	return null


func _unhandled_input(event: InputEvent) -> void:
	if _lamp == null:
		return
	var k: InputEventKey = event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if k.keycode == KEY_F:
		_on = not _on
		_lamp.visible = _on
		print("[walk_flashlight] %s" % ("ON" if _on else "OFF"))
