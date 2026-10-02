extends SceneTree
## Scratch probe for Lux 0.62.0's failing fixtures, on a copy of a walk
## export with the new Lux dropped in. Loads the mission, re-spawns the
## fixture lights so the spawner chooses the failing ones, lists them, then
## watches one stuttering tube and one pole it makes cycle: lamp energy and
## lens emission every frame for a while, and a frame of the tube at its
## brightest and its dimmest. Windowed, drives itself, quits itself. Prints
## what it measured and stops.

const OUT: String = "C:/Projects/gabagool_studios/gabagool_factory/docs/findings/failing_fixtures"
const WATCH_S: float = 24.0


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _rigs(n: Node, out: Array) -> void:
	if n is LuxFluorescentRig or n is LuxStreetlightRig:
		out.append(n)
	for c in n.get_children():
		_rigs(c, out)


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(OUT)
	change_scene_to_file("res://mission.tscn")
	var steady: int = 0
	var waited: int = 0
	while steady < 30 and waited < 6000:
		await process_frame
		waited += 1
		steady = steady + 1 if is_equal_approx(root.get_viewport().scaling_3d_scale, 1.0) else 0
	print("FAIL warm-up waited ", waited)
	var scene: Node = current_scene
	var res: Dictionary = LuxFixtureSpawner.spawn(scene)
	print("FAIL respawn: ", res.get("msg"))
	await process_frame
	await process_frame
	var rigs: Array = []
	_rigs(scene, rigs)
	var failing: Array = []
	var kinds: Dictionary = {}
	for r in rigs:
		var lr: LuxLightRig = r.get("rig")
		if lr != null and lr.failing_kind != LuxFailing.NONE:
			failing.append(r)
			kinds[lr.failing_kind] = int(kinds.get(lr.failing_kind, 0)) + 1
	print("FAIL rigs=", rigs.size(), " failing=", failing.size(), " kinds=", kinds)
	var bound: int = 0
	for r in failing:
		bound += (r.get("_lenses") as Array).size()
	print("FAIL lenses bound=", bound)
	# one stuttering tube
	var tube: Node3D = null
	for r in failing:
		if (r.get("rig") as LuxLightRig).failing_kind == LuxFailing.STUTTER and not (r.get("_lenses") as Array).is_empty():
			tube = r
			break
	# one pole made to cycle, by hand, as the loader would at export
	var pole: Node3D = null
	for r in rigs:
		if r is LuxStreetlightRig:
			var lr: LuxLightRig = r.get("rig")
			lr.failing_kind = LuxFailing.CYCLING
			lr.failing_seed = 12345
			r.call("_bind_lenses")
			r.set_process(true)
			pole = r
			break
	print("FAIL tube=", tube != null, " pole=", pole != null, " pole lenses=",
		(pole.get("_lenses") as Array).size() if pole != null else -1)
	if tube == null:
		_exit(2)
		return
	var lamp: Light3D = tube.get_child(0) as Light3D
	var lens: Array = (tube.get("_lenses") as Array)[0]
	var cam: Camera3D = Camera3D.new()
	cam.fov = 45.0
	root.add_child(cam)
	cam.make_current()
	var mi: MeshInstance3D = lens[0]
	var box: AABB = mi.global_transform * mi.get_aabb()
	var mid: Vector3 = box.get_center()
	cam.look_at_from_position(mid + Vector3(0.9, -1.4, 0.9), mid, Vector3.UP)
	for _i in range(10):
		await process_frame
	var t0: float = Time.get_ticks_msec() / 1000.0
	var e_min: float = 1e9
	var e_max: float = 0.0
	var drops: int = 0
	var was_low: bool = false
	var frames: int = 0
	var base_e: float = 1.0
	var bright: Image = null
	var dim: Image = null
	var pole_min: float = 1e9
	var pole_max: float = 0.0
	var pole_lamp: Light3D = pole.get_child(0) as Light3D if pole != null else null
	while Time.get_ticks_msec() / 1000.0 - t0 < WATCH_S:
		await process_frame
		frames += 1
		var e: float = lamp.light_energy
		var em: float = (lens[2] as BaseMaterial3D).emission_energy_multiplier
		if frames == 1:
			base_e = e
			print("FAIL tube base energy=", e, " lens base emission=", float(lens[3]))
		# against the lamp's own first-frame energy: the rig's `energy` is scaled
		# by the preset before it reaches the lamp (2.2 became 6.0 here)
		var low: bool = e < 0.9 * base_e
		if low and not was_low:
			drops += 1
			if dim == null:
				dim = root.get_viewport().get_texture().get_image()
		was_low = low
		e_min = minf(e_min, e)
		e_max = maxf(e_max, e)
		if bright == null and frames == 5:
			bright = root.get_viewport().get_texture().get_image()
		if frames % 60 == 0:
			print("FAIL t=%.1f tube energy=%.3f lens=%.3f pole energy=%s" % [Time.get_ticks_msec() / 1000.0 - t0, e, em,
				str(pole_lamp.light_energy) if pole_lamp != null else "-"])
		if pole_lamp != null:
			pole_min = minf(pole_min, pole_lamp.light_energy)
			pole_max = maxf(pole_max, pole_lamp.light_energy)
	print("FAIL watched ", frames, " frames over ", WATCH_S, " s: tube energy min=", e_min, " max=", e_max,
		" drops=", drops, " | pole energy min=", pole_min, " max=", pole_max)
	if bright != null:
		bright.save_png(OUT + "/tube_bright.png")
	if dim != null:
		dim.save_png(OUT + "/tube_dim.png")
	print("FAIL done")
	_exit(0)
