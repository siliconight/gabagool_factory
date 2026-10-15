extends Node
## Scratch probe, autoloaded into a SCRATCH walk copy only: the work light in a real level, headless.
## Waits for the level, reads every Environment, presses L, reads again, presses L, reads again; prints what it
## measured and quits. Names no cause.

const PROPS := ["fog_enabled", "glow_enabled", "adjustment_enabled", "tonemap_mode", "tonemap_exposure",
	"ambient_light_source", "ambient_light_energy"]


func _envs() -> Array:
	var envs: Array = []
	for n in get_tree().root.find_children("*", "WorldEnvironment", true, false):
		var we: WorldEnvironment = n as WorldEnvironment
		if we != null and we.environment != null and not envs.has(we.environment):
			envs.append(we.environment)
	var world: World3D = get_viewport().find_world_3d()
	if world != null and world.environment != null and not envs.has(world.environment):
		envs.append(world.environment)
	return envs


func _snap() -> Array:
	var out: Array = []
	for e in _envs():
		var env: Environment = e
		var d: Dictionary = {}
		for p in PROPS:
			d[p] = env.get(p)
		out.append(d)
	return out


func _press() -> void:
	var ev := InputEventKey.new()
	ev.keycode = KEY_L
	ev.pressed = true
	get_viewport().push_input(ev)


func _ready() -> void:
	for _i in range(120):
		await get_tree().process_frame
	var wl: Node = get_tree().root.find_child("WalkWorkLight", true, false)
	print("PROBE work light node: ", wl != null)
	var cam: Camera3D = get_viewport().get_camera_3d()
	print("PROBE current camera: ", cam.get_path() if cam != null else "none")
	print("PROBE environments: ", _envs().size())
	var before: Array = _snap()
	print("PROBE before: ", JSON.stringify(before))
	_press()
	for _i in range(5):
		await get_tree().process_frame
	print("PROBE on: ", wl.call("is_on") if wl != null else "no node")
	var key_found: bool = false
	if cam != null:
		for c in cam.get_children():
			if c is DirectionalLight3D and String(c.name) == "WalkWorkLightKey":
				key_found = true
	print("PROBE key light under the camera: ", key_found)
	print("PROBE while on: ", JSON.stringify(_snap()))
	_press()
	for _i in range(5):
		await get_tree().process_frame
	print("PROBE off: ", not bool(wl.call("is_on")) if wl != null else "no node")
	var after: Array = _snap()
	print("PROBE after: ", JSON.stringify(after))
	print("PROBE restored exactly: ", JSON.stringify(after) == JSON.stringify(before))
	get_tree().quit()
