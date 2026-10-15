extends Node
## A WORK LIGHT FOR THE WALK COPY, off by default and toggled with L.
##
## The walker, 2026-10-14: "a tool to make the area brighter for checking
## things so its not too dark and you get mistaken... just for visual checks".
## The flashlight (F) is a hand torch: one beam, and the rest stays as dark as
## the level ships it. This is the other instrument -- the whole view lit
## flat enough to tell what is THERE, which way a monitor faces, whether a
## step exists, in any room at any hour. It is `look_shots.py --inspect
## studio`'s light carried by the walker's camera: a white key over the
## camera's shoulder with no shadow, a flat white ambient, and the level's fog,
## glow, colour adjustment, tonemap and Lux's grade set aside, so the night
## grade cannot hide the check.
##
## WHILE IT IS ON, NOTHING ON SCREEN IS THE LEVEL'S LOOK, and a banner across
## the top of the frame says so, so a screenshot taken in this light carries
## its own warning. Pressing L again puts every value it touched back as it
## found it. The level's own lamps stay on underneath: brighter is the point.
##
## Walk copies only, debug builds only. The package ships no player and no
## work light; `tools/walk_export.py` copies this in as `_walk_work_light.gd`.
## Proven headless by `tools/walk_work_light_selftest.gd`.

## Equal to look_shots.gd's STUDIO_KEY_ENERGY, STUDIO_KEY_TILT_DEG and
## STUDIO_AMBIENT, so a check walked in this light and a frame shot with
## `--inspect studio` show one light. CHOSEN, not derived: legible on the grey
## and brown of a greybox office and on a street at once.
const KEY_ENERGY := 1.2
const KEY_TILT_DEG := Vector3(-35.0, -25.0, 0.0)
const AMBIENT := 0.5
const BANNER := "WORK LIGHT (L) -- for checking what is there. Nothing on screen is the level's look."
## Every Environment value the light changes, read before and written back after.
const PROPS := ["fog_enabled", "volumetric_fog_enabled", "glow_enabled", "adjustment_enabled",
	"tonemap_mode", "tonemap_exposure", "ambient_light_source", "ambient_light_color",
	"ambient_light_energy", "ambient_light_sky_contribution"]

var _on: bool = false
var _key: DirectionalLight3D = null
var _banner: CanvasLayer = null
var _saved: Array = []
var _hidden_layers: Array = []


func _ready() -> void:
	if not OS.is_debug_build():
		queue_free()
		return
	_banner = CanvasLayer.new()
	_banner.name = &"WorkLightBanner"
	_banner.layer = 120
	_banner.visible = false
	add_child(_banner)
	var label := Label.new()
	label.text = BANNER
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", 20)
	label.add_theme_color_override("font_color", Color(1.0, 0.85, 0.25))
	label.add_theme_color_override("font_outline_color", Color(0.0, 0.0, 0.0))
	label.add_theme_constant_override("outline_size", 6)
	_banner.add_child(label)
	label.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	label.offset_top = 8.0
	print("[walk_work_light] L toggles a work light: a shadowless light over "
		+ "your shoulder and a flat ambient, for checking what is there in a "
		+ "dark room. While it is on, nothing on screen is the level's look.")


func _unhandled_input(event: InputEvent) -> void:
	var k: InputEventKey = event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if k.keycode == KEY_L:
		set_on(not _on)


func is_on() -> bool:
	return _on


## Turn the work light on or off. Off puts back every value on did change.
func set_on(on: bool) -> void:
	if on == _on:
		return
	if on:
		var cam: Camera3D = get_viewport().get_camera_3d()
		if cam == null:
			push_warning("[walk_work_light] no current camera; no work light")
			return
		_key = DirectionalLight3D.new()
		_key.name = &"WalkWorkLightKey"
		_key.shadow_enabled = false
		_key.light_energy = KEY_ENERGY
		_key.light_bake_mode = Light3D.BAKE_DISABLED
		cam.add_child(_key)
		_key.rotation_degrees = KEY_TILT_DEG
		_saved = []
		for e in _environments():
			var env: Environment = e
			_saved.append({"env": env, "values": _read(env)})
			_apply(env)
		# Lux's grade only: the debug overlay and the HUD stay on screen
		_hidden_layers = []
		for n in get_tree().root.find_children("*", "CanvasLayer", true, false):
			var layer: CanvasLayer = n
			if layer.visible and layer != _banner and _under_lux_root(layer):
				layer.visible = false
				_hidden_layers.append(layer)
		_banner.visible = true
	else:
		if is_instance_valid(_key):
			_key.queue_free()
		_key = null
		for s in _saved:
			var d: Dictionary = s
			_write(d["env"], d["values"])
		_saved = []
		for l in _hidden_layers:
			if is_instance_valid(l):
				var layer: CanvasLayer = l
				layer.visible = true
		_hidden_layers = []
		_banner.visible = false
	_on = on
	print("[walk_work_light] " + ("ON -- nothing on screen is the level's look" if on else "OFF"))


func _process(_delta: float) -> void:
	# again every frame while on: Lux may set its environment back
	if _on:
		for s in _saved:
			var d: Dictionary = s
			_apply(d["env"])


## Every Environment drawing this viewport, once each: each WorldEnvironment's,
## the camera's own, and the world's.
func _environments() -> Array:
	var envs: Array = []
	for n in get_tree().root.find_children("*", "WorldEnvironment", true, false):
		var we: WorldEnvironment = n as WorldEnvironment
		if we != null and we.environment != null and not envs.has(we.environment):
			envs.append(we.environment)
	var cam: Camera3D = get_viewport().get_camera_3d()
	if cam != null and cam.environment != null and not envs.has(cam.environment):
		envs.append(cam.environment)
	var world: World3D = get_viewport().find_world_3d()
	if world != null and world.environment != null and not envs.has(world.environment):
		envs.append(world.environment)
	return envs


func _read(env: Environment) -> Dictionary:
	var out: Dictionary = {}
	for p in PROPS:
		out[p] = env.get(p)
	return out


func _write(env: Environment, values: Dictionary) -> void:
	for p in values:
		env.set(p, values[p])


func _apply(env: Environment) -> void:
	env.fog_enabled = false
	env.volumetric_fog_enabled = false
	env.glow_enabled = false
	env.adjustment_enabled = false
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.tonemap_exposure = 1.0
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(1.0, 1.0, 1.0)
	env.ambient_light_energy = AMBIENT
	env.ambient_light_sky_contribution = 0.0


func _under_lux_root(node: Node) -> bool:
	var p: Node = node
	while p != null:
		if p.is_in_group(&"lux_root"):
			return true
		p = p.get_parent()
	return false
