extends SceneTree
## THE ORDER PROBE (2026-10-12): `patches/lux_street_shadow_fade/street_shadow_fade_selftest.gd.txt`
## with a far reading taken FIRST, before any near render, and one again at the end. Run it in a
## copy of Lux with `patches/patch_lux_street_shadow_fade.py`'s edits drafted in (`--draft` with
## LUX_ROOT, before the patch was refuted) and imported, from that copy's tools/:
##
##     godot --rendering-method gl_compatibility --path <copy> -s res://tools/fade_order_probe.gd
##
## Its output is `fade_order_probe.out.txt`: far first 0.499 (no shadow: the fade works when the
## map was never drawn), far after the near reads 0.000 (the near map, still sampled). It
## measures and stops; what that means is in this folder's README.
## A street light's shadow stops at a distance from the camera (0.76.0).
##
##     godot --rendering-method gl_compatibility --path lux -s res://tools/street_shadow_fade_selftest.gd
##
## Opens a window (it reads frames; headless draws nothing), measures, and
## quits itself. Exit 0 = every case behaved. Exit 1 = a case failed. Exit 2
## = could not run.
##
## What this holds:
##
##   * the loader's `streetlight` branch gives a pole's lamp Godot's distance
##     fade: its SHADOW ends `STREET_SHADOW_FADE_M` from the camera, fading
##     over `SHADOW_FADE_LENGTH_M`, and the light itself never fades
##     (`LIGHT_FADE_NEVER_M`);
##   * a wall pack keeps no fade: its shadow stops its own wall's wash;
##   * in a frame, on the renderer packages ship on: a slab a metre under a
##     shadowed lamp blacks the pool seen from about 12 m and does not from
##     about 44 m; with the fade off it blacks the pool from both, so the
##     fade -- not the far camera -- is what lifts it, and the far camera can
##     see a shadow at all.
##
## What it cannot hold, and `docs/findings/pole_line/` in the factory does:
## what the fade saves in a level (draws at Level Factory's stations).

const LOADER := "res://addons/lux/runtime/lux_light_loader.gd"
const MOUNT := 7.5

var _fails: int = 0


func _initialize() -> void:
	_main.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _check(label: String, got: Variant, want: Variant) -> void:
	var ok: bool = str(got) == str(want)
	if not ok:
		_fails += 1
	print("  %s %s: %s%s" % ["ok  " if ok else "FAIL", label, str(got),
		"" if ok else "   (wanted %s)" % str(want)])


func _near(label: String, got: float, want: float, tol: float) -> void:
	var ok := absf(got - want) <= tol
	if not ok:
		_fails += 1
	print("  %s %s: %.4f%s" % ["ok  " if ok else "FAIL", label, got,
		"" if ok else "   (wanted %.4f +/- %.4f)" % [want, tol]])


func _lamp(rig: Node) -> SpotLight3D:
	for c in rig.get_children():
		if c is SpotLight3D:
			return c
	return null


func _band(img: Image) -> float:
	var w: int = img.get_width()
	var h: int = img.get_height()
	var s: float = 0.0
	var n: int = 0
	for y in range(int(h * 0.50), int(h * 0.70), 2):
		for x in range(int(w * 0.3), int(w * 0.7), 2):
			s += img.get_pixel(x, y).get_luminance()
			n += 1
	return s / float(n)


func _read() -> float:
	# a shadow map settles into its atlas slot over tens of frames
	# (LuxStreetlightRig.POLE_SHADOW_BIAS says how long): wait it out
	for _i in range(40):
		await process_frame
	return _band(root.get_viewport().get_texture().get_image())


func _main() -> void:
	print("street shadow fade selftest")
	var loader: Script = load(LOADER)
	if loader == null:
		print("  FAIL could not load the loader")
		_exit(2)
		return
	var world := Node3D.new()
	root.add_child(world)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color.BLACK
	e.ambient_light_source = Environment.AMBIENT_SOURCE_DISABLED
	env.environment = e
	world.add_child(env)
	var grey := StandardMaterial3D.new()
	grey.albedo_color = Color(0.6, 0.6, 0.6)
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(120.0, 120.0)
	ground.mesh = pm
	ground.material_override = grey
	world.add_child(ground)
	# a pole line's lamp, built by the loader's own streetlight branch
	var rig: Node3D = loader.rig_for_anchor({"id": "site_pole_t", "type": "streetlight",
		"pos": [0.0, 0.0, MOUNT], "rot_y": 0.0})
	var rr: LuxLightRig = rig.get("rig")
	rr.shadows_enabled = true                  # what the shadow budget gives the first poles
	rr.failing_kind = LuxFailing.NONE          # a steady lamp, whatever its id hashes to
	world.add_child(rig)
	rig.position = Vector3(0.0, MOUNT, 0.0)
	for _i in range(20):
		await process_frame
	var lamp: SpotLight3D = _lamp(rig)
	if lamp == null:
		print("  FAIL the rig built no lamp")
		_exit(2)
		return
	_check("the pole's lamp fades by distance", lamp.distance_fade_enabled, true)
	_near("...its shadow ending STREET_SHADOW_FADE_M from the camera", lamp.distance_fade_shadow,
		LuxStreetlightRig.STREET_SHADOW_FADE_M, 1e-6)
	_near("...over SHADOW_FADE_LENGTH_M", lamp.distance_fade_length,
		LuxStreetlightRig.SHADOW_FADE_LENGTH_M, 1e-6)
	_near("...and the light itself not before LIGHT_FADE_NEVER_M", lamp.distance_fade_begin,
		LuxStreetlightRig.LIGHT_FADE_NEVER_M, 1e-6)
	# a slab a metre under the lamp: its shadow is the pool's whole middle
	var slab := MeshInstance3D.new()
	var sm := BoxMesh.new()
	sm.size = Vector3(3.0, 0.05, 3.0)
	slab.mesh = sm
	slab.material_override = grey
	world.add_child(slab)
	slab.position = Vector3(0.0, MOUNT - 1.0, 0.0)
	var cam := Camera3D.new()
	cam.fov = 60.0
	world.add_child(cam)
	cam.make_current()
	var near_eye := Vector3(10.0, 1.6, 0.0)
	var far_eye := Vector3(44.0, 12.0, 0.0)
	var at := Vector3(0.0, 0.3, 0.0)
	var light_at: Vector3 = lamp.global_position
	# ORDER PROBE: far first, before any near render
	cam.fov = 14.0
	cam.look_at_from_position(far_eye, at, Vector3.UP)
	var far_first: float = await _read()
	print("  ORDER PROBE far first, fade on: %.3f" % far_first)
	# NEAR: inside the fade, the shadow drawn
	cam.fov = 60.0
	cam.look_at_from_position(near_eye, at, Vector3.UP)
	var near_fade: float = await _read()
	lamp.shadow_enabled = false
	var near_open: float = await _read()
	lamp.shadow_enabled = true
	lamp.distance_fade_enabled = false
	var near_nofade: float = await _read()
	lamp.distance_fade_enabled = true
	# FAR: past the fade and its length, a narrow lens so the pool fills the band
	cam.fov = 14.0
	cam.look_at_from_position(far_eye, at, Vector3.UP)
	var far_fade: float = await _read()
	lamp.shadow_enabled = false
	var far_open: float = await _read()
	lamp.shadow_enabled = true
	lamp.distance_fade_enabled = false
	var far_nofade: float = await _read()
	lamp.distance_fade_enabled = true
	var far_again: float = await _read()
	print("  ORDER PROBE far again after the toggles, fade on: %.3f" % far_again)
	print("  camera to lamp: near %.1f m, far %.1f m (the shadow ends at %.1f + %.1f)" % [
		near_eye.distance_to(light_at), far_eye.distance_to(light_at),
		LuxStreetlightRig.STREET_SHADOW_FADE_M, LuxStreetlightRig.SHADOW_FADE_LENGTH_M])
	print("  the pool under the slab:  near  faded %.3f  no fade %.3f  unshadowed %.3f" % [
		near_fade, near_nofade, near_open])
	print("                            far   faded %.3f  no fade %.3f  unshadowed %.3f" % [
		far_fade, far_nofade, far_open])
	_check("the near camera stands inside the fade",
		near_eye.distance_to(light_at) < LuxStreetlightRig.STREET_SHADOW_FADE_M, true)
	_check("the far camera stands past the fade and its length",
		far_eye.distance_to(light_at) > LuxStreetlightRig.STREET_SHADOW_FADE_M
		+ LuxStreetlightRig.SHADOW_FADE_LENGTH_M, true)
	_check("the unshadowed pool is lit from both", near_open > 0.05 and far_open > 0.05, true)
	_check("control: with no fade the slab blacks the pool from near", near_nofade < near_open * 0.1, true)
	_check("control: with no fade the slab blacks the pool from far", far_nofade < far_open * 0.1, true)
	_check("near, the fade keeps the shadow", near_fade < near_open * 0.1, true)
	_check("far, the fade ends the shadow: the pool keeps 0.8 of its unshadowed self",
		far_fade >= far_open * 0.8, true)
	# a wall pack keeps no fade: its shadow stops its own wall's wash
	var wp: Node3D = loader.rig_for_anchor({"id": "Spawned_wall_pack_t", "type": "wall_pack",
		"pos": [0.0, 0.0, 2.5], "rot_y": 0.0})
	world.add_child(wp)
	await process_frame
	var wl: SpotLight3D = _lamp(wp)
	if wl == null:
		print("  FAIL the wall pack built no lamp")
		_exit(2)
		return
	_check("a wall pack's lamp does not fade", wl.distance_fade_enabled, false)
	print("%s (%d failed)" % ["PASS" if _fails == 0 else "FAIL", _fails])
	_exit(0 if _fails == 0 else 1)
