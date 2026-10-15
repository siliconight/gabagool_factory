extends SceneTree
## The walk copy's work light (`walk_work_light.gd`), proven headless, 2026-10-14.
##
##     a project holding this file and walk_work_light.gd as res://_walk_work_light.gd, then
##     godot --headless --path <that project> -s res://walk_work_light_selftest.gd
##
## Exit 0 = every check held. Exit 1 = a check failed. Exit 2 = could not run.
##
## Builds a camera, a WorldEnvironment graded like a night -- fog, glow, a
## colour adjustment, a filmic tonemap at 0.3, ambient from the sky -- a
## CanvasLayer under a `lux_root` node standing in for Lux's grade, and one
## outside it standing in for the debug overlay. Presses L through the
## viewport and checks what the light changed; sets a value back the way Lux
## may and checks the light re-asserts it; presses L again and checks every
## value is back as it was found. A key release and an echo must do nothing.

const SUBJECT := "res://_walk_work_light.gd"

var _fails: int = 0


func _initialize() -> void:
	_main()


func _check(label: String, ok: bool) -> void:
	if not ok:
		_fails += 1
	print("%s  %s" % ["ok  " if ok else "FAIL", label])


func _press(key: Key, pressed: bool, echo: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = key
	ev.pressed = pressed
	ev.echo = echo
	root.push_input(ev)


func _key_light(cam: Camera3D) -> DirectionalLight3D:
	for c in cam.get_children():
		var d: DirectionalLight3D = c as DirectionalLight3D
		if d != null and not d.is_queued_for_deletion():
			return d
	return null


func _main() -> void:
	if not ResourceLoader.exists(SUBJECT):
		print("could not run: no %s in this project" % SUBJECT)
		quit(2)
		return
	var scene := Node3D.new()
	scene.name = &"Scene"
	root.add_child(scene)
	current_scene = scene
	var cam := Camera3D.new()
	scene.add_child(cam)
	cam.current = true
	var env := Environment.new()
	env.fog_enabled = true
	env.glow_enabled = true
	env.adjustment_enabled = true
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 0.3
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_color = Color(0.2, 0.25, 0.4)
	env.ambient_light_energy = 0.2
	env.ambient_light_sky_contribution = 1.0
	var we := WorldEnvironment.new()
	we.environment = env
	scene.add_child(we)
	var lux := Node.new()
	lux.add_to_group(&"lux_root")
	scene.add_child(lux)
	var grade := CanvasLayer.new()
	lux.add_child(grade)
	var overlay := CanvasLayer.new()
	scene.add_child(overlay)
	var light: Node = (load(SUBJECT) as GDScript).new()
	scene.add_child(light)
	await process_frame

	_check("starts off", not bool(light.call("is_on")))
	_check("no key light before L", _key_light(cam) == null)
	_press(KEY_L, false, false)
	_press(KEY_L, true, true)
	await process_frame
	_check("a release and an echo do nothing", not bool(light.call("is_on")))

	_press(KEY_L, true, false)
	await process_frame
	_check("L turns it on", bool(light.call("is_on")))
	var key: DirectionalLight3D = _key_light(cam)
	_check("a key light rides on the camera", key != null)
	if key != null:
		_check("the key casts no shadow", not key.shadow_enabled)
		_check("the key is look_shots' studio energy", is_equal_approx(key.light_energy, 1.2))
		_check("the key is never baked", key.light_bake_mode == Light3D.BAKE_DISABLED)
	_check("fog off", not env.fog_enabled)
	_check("glow off", not env.glow_enabled)
	_check("colour adjustment off", not env.adjustment_enabled)
	_check("tonemap linear", env.tonemap_mode == Environment.TONE_MAPPER_LINEAR)
	_check("exposure 1", is_equal_approx(env.tonemap_exposure, 1.0))
	_check("ambient a flat colour", env.ambient_light_source == Environment.AMBIENT_SOURCE_COLOR)
	_check("ambient white at 0.5", env.ambient_light_color == Color(1, 1, 1)
		and is_equal_approx(env.ambient_light_energy, 0.5))
	_check("Lux's grade hidden", not grade.visible)
	_check("the overlay left on screen", overlay.visible)
	var banner: CanvasLayer = light.get_node_or_null("WorkLightBanner") as CanvasLayer
	_check("the banner is up", banner != null and banner.visible)

	# the way Lux may set its environment back while the light is on
	env.tonemap_exposure = 0.3
	env.fog_enabled = true
	await process_frame
	_check("re-asserted after Lux sets exposure back", is_equal_approx(env.tonemap_exposure, 1.0))
	_check("re-asserted after Lux turns fog back on", not env.fog_enabled)

	_press(KEY_L, true, false)
	await process_frame
	_check("L again turns it off", not bool(light.call("is_on")))
	_check("the key light is gone", _key_light(cam) == null)
	_check("fog back on", env.fog_enabled)
	_check("glow back on", env.glow_enabled)
	_check("colour adjustment back on", env.adjustment_enabled)
	_check("tonemap back to filmic", env.tonemap_mode == Environment.TONE_MAPPER_FILMIC)
	_check("exposure back to 0.3", is_equal_approx(env.tonemap_exposure, 0.3))
	_check("ambient back to the sky", env.ambient_light_source == Environment.AMBIENT_SOURCE_SKY)
	_check("ambient colour and energy back", env.ambient_light_color == Color(0.2, 0.25, 0.4)
		and is_equal_approx(env.ambient_light_energy, 0.2))
	_check("sky contribution back", is_equal_approx(env.ambient_light_sky_contribution, 1.0))
	_check("Lux's grade back on screen", grade.visible)
	_check("the banner is down", banner != null and not banner.visible)

	print("selftest: %d failed" % _fails)
	quit(1 if _fails > 0 else 0)
