extends SceneTree
## Scratch probe: the failing fixtures AS A SHIPPED LEVEL CARRIES THEM. Loads
## a walk export as it is -- no respawn, nothing made by hand -- lists the
## rigs whose packed resource says they fail, counts the lenses each bound at
## ready, then watches one stuttering tube and one cycling pole and saves
## frames. Windowed, drives itself, quits itself. Prints what it measured.

const OUT: String = "C:/Projects/gabagool_studios/gabagool_factory/docs/cold_runs/cold_9139/frames"
const TUBE_WATCH_S: float = 30.0
const POLE_WATCH_S: float = 80.0


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


func _hide_canvas(n: Node) -> void:
	if n is CanvasLayer and not String(n.name).contains("Lux"):
		(n as CanvasLayer).visible = false
	for c in n.get_children():
		_hide_canvas(c)


func _lamp(rig: Node) -> Light3D:
	for c in rig.get_children():
		if c is Light3D:
			return c
	return null


func _save(label: String) -> void:
	root.get_viewport().get_texture().get_image().save_png("%s/%s.png" % [OUT, label])


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(OUT)
	change_scene_to_file("res://_walk.tscn")
	for _i in range(30):
		await process_frame
	var steady: int = 0
	var waited: int = 0
	while steady < 30 and waited < 6000:
		await process_frame
		waited += 1
		steady = steady + 1 if is_equal_approx(root.get_viewport().scaling_3d_scale, 1.0) else 0
	print("LEVEL warm-up waited ", waited, " frames")
	if steady < 30:
		print("LEVEL CANNOT SHOOT: the warm-up never finished")
		_exit(2)
		return
	_hide_canvas(root)
	var rigs: Array = []
	_rigs(root, rigs)
	var failing: Array = []
	var kinds: Dictionary = {}
	var bound: Dictionary = {}
	var hum: int = 0
	for r in rigs:
		var lr: LuxLightRig = r.get("rig")
		if lr == null:
			continue
		if lr.flicker_amount > 0.0:
			hum += 1
		if lr.failing_kind != LuxFailing.NONE:
			failing.append(r)
			kinds[lr.failing_kind] = int(kinds.get(lr.failing_kind, 0)) + 1
			bound[lr.failing_kind] = int(bound.get(lr.failing_kind, 0)) + (r.get("_lenses") as Array).size()
	print("LEVEL rigs=", rigs.size(), " failing=", failing.size(), " kinds=", kinds,
		" lenses bound by kind=", bound, " rigs still humming (flicker_amount>0)=", hum)
	for r in failing:
		var lr: LuxLightRig = r.get("rig")
		print("LEVEL   ", r.name, " kind=", lr.failing_kind, " seed=", lr.failing_seed,
			" lenses=", (r.get("_lenses") as Array).size(), " owner=", r.owner.name if r.owner != null else "null",
			" at ", r.global_position)
	var tube: Node3D = null
	var pole: Node3D = null
	for r in failing:
		var lr: LuxLightRig = r.get("rig")
		if tube == null and lr.failing_kind == LuxFailing.STUTTER and r is LuxFluorescentRig:
			tube = r
		if pole == null and lr.failing_kind == LuxFailing.CYCLING and r is LuxStreetlightRig:
			pole = r
	print("LEVEL tube=", tube != null, " pole=", pole != null)
	var cam: Camera3D = Camera3D.new()
	cam.fov = 50.0
	root.add_child(cam)
	cam.make_current()
	if tube != null:
		var lamp: Light3D = _lamp(tube)
		var mid: Vector3 = lamp.global_position
		# from below and to the side, as a person under it would look up
		cam.look_at_from_position(mid + Vector3(1.2, -1.6, 1.0), mid + Vector3(0.0, 0.1, 0.0), Vector3.UP)
		for _i in range(10):
			await process_frame
		var base: float = lamp.light_energy
		var e_min: float = 1e9
		var drops: int = 0
		var was_low: bool = false
		var dim_saved: bool = false
		var t0: float = Time.get_ticks_msec() / 1000.0
		_save("failing_tube_full")
		while Time.get_ticks_msec() / 1000.0 - t0 < TUBE_WATCH_S:
			await process_frame
			var e: float = lamp.light_energy
			e_min = minf(e_min, e)
			var low: bool = e < 0.9 * base
			if low and not was_low:
				drops += 1
				if not dim_saved:
					_save("failing_tube_drop")
					dim_saved = true
			was_low = low
		print("LEVEL tube ", tube.name, ": base energy=", base, " min=", e_min, " drops in ", TUBE_WATCH_S, " s=", drops,
			" lens emission now=", ((tube.get("_lenses") as Array)[0][2] as BaseMaterial3D).emission_energy_multiplier
			if not (tube.get("_lenses") as Array).is_empty() else -1.0)
	if pole != null:
		var lamp: Light3D = _lamp(pole)
		var head: Vector3 = lamp.global_position
		# from the road, 9 m off, at eye height, the lamp head in the top of frame
		var from: Vector3 = Vector3(head.x + 7.0, 1.7, head.z + 6.0)
		cam.look_at_from_position(from, Vector3(head.x, head.y - 1.5, head.z), Vector3.UP)
		for _i in range(10):
			await process_frame
		var e_max: float = 0.0
		var e_min: float = 1e9
		var dark_saved: bool = false
		var lit_saved: bool = false
		var restrike_saved: bool = false
		var was_dark: bool = false
		var t0: float = Time.get_ticks_msec() / 1000.0
		while Time.get_ticks_msec() / 1000.0 - t0 < POLE_WATCH_S:
			await process_frame
			var e: float = lamp.light_energy
			e_max = maxf(e_max, e)
			e_min = minf(e_min, e)
			var lr: LuxLightRig = pole.get("rig")
			var dark: bool = e <= 0.001
			if not lit_saved and e >= 0.98 * lr.energy:
				_save("failing_pole_lit")
				lit_saved = true
			if dark and not dark_saved:
				_save("failing_pole_dark")
				dark_saved = true
			if was_dark and not dark and not restrike_saved:
				_save("failing_pole_restrike")
				restrike_saved = true
			was_dark = dark
		print("LEVEL pole ", pole.name, ": rig energy=", (pole.get("rig") as LuxLightRig).energy,
			" seen min=", e_min, " max=", e_max, " in ", POLE_WATCH_S, " s; frames lit=", lit_saved,
			" dark=", dark_saved, " restrike=", restrike_saved,
			" lenses=", (pole.get("_lenses") as Array).size())
	print("LEVEL done")
	_exit(0)
