extends SceneTree
## Roadmap 222, second probe: is the first read after `shadow_enabled = true` the stale one?
## A probe, not a test: it measures and quits.
##
##     godot --rendering-method gl_compatibility --path <a Lux checkout> -s res://tools/shadow_gap_probe2.gd
##
## The first probe read each gap's biases in one order, 0.00 first, and only the first read after
## switching the shadow back on came back unshadowed at the 5 mm and 20 mm gaps. The selftest's
## on-axis control is also the first read after switching it back on. Here, per gap: off, read;
## on at bias 0.03, read twice with nothing changed; bias 0.00, read twice; bias 0.03, read once.
## Luma is the frame's band the selftest reads, 0..1. Opens a window and quits itself.

const LOADER := "res://addons/lux/runtime/lux_light_loader.gd"


func _initialize() -> void:
	_main.call_deferred()


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
	for _i in range(8):
		await process_frame
	return _band(root.get_viewport().get_texture().get_image())


func _main() -> void:
	var loader: Script = load(LOADER)
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
	pm.size = Vector2(40.0, 40.0)
	ground.mesh = pm
	ground.material_override = grey
	world.add_child(ground)
	var mount: float = 6.0
	var shaft := MeshInstance3D.new()
	var cm := CylinderMesh.new()
	cm.top_radius = 0.06
	cm.bottom_radius = 0.06
	shaft.mesh = cm
	shaft.material_override = grey
	world.add_child(shaft)
	var cam := Camera3D.new()
	cam.fov = 60.0
	world.add_child(cam)
	cam.make_current()
	cam.look_at_from_position(Vector3(9.0, 1.6, 0.0), Vector3(0.0, 0.3, 0.0), Vector3.UP)
	var rig: Node3D = loader.rig_for_anchor({"id": "site_lamp_t", "type": "streetlight",
		"pos": [0.0, 0.0, mount], "rot_y": 0.0})
	var rr: LuxLightRig = rig.get("rig")
	rr.shadows_enabled = true
	world.add_child(rig)
	rig.position = Vector3(0.0, mount, 0.0)
	for _i in range(20):
		await process_frame
	var lamp: SpotLight3D = null
	for c in rig.get_children():
		if c is SpotLight3D:
			lamp = c
	if lamp == null:
		print("PROBE no lamp")
		quit(2)
		return
	lamp.position = Vector3(0.0, rr.mount_height, 0.0)
	for gap: float in [0.005, 0.02, 0.05]:
		var cap: float = mount - gap
		cm.height = cap
		shaft.position = Vector3(0.0, cap * 0.5, 0.0)
		lamp.shadow_enabled = false
		var off: float = await _read()
		lamp.shadow_enabled = true
		lamp.shadow_bias = 0.03
		var a1: float = await _read()
		var a2: float = await _read()
		lamp.shadow_bias = 0.0
		var b1: float = await _read()
		var b2: float = await _read()
		lamp.shadow_bias = 0.03
		var c1: float = await _read()
		print("PROBE gap %.3f  off %.3f | on, bias 0.03: %.3f then %.3f | bias 0.00: %.3f then %.3f | bias 0.03 again: %.3f" % [
			gap, off, a1, a2, b1, b2, c1])
	quit(0)
