extends SceneTree
## Roadmap 222: does the streetlight selftest's cap control fail for the gap it asks a shadow map to
## see? A probe, not a test: it measures and quits.
##
##     godot --rendering-method gl_compatibility --path <a Lux checkout> -s res://tools/shadow_gap_probe.gd
##
## The selftest stands a 0.06 m shaft whose cap is 5 mm under the lens point and holds that an
## on-axis lamp at the lens point, shadowed at bias 0.03, blacks the pool. Here the same scene is
## built and the on-axis pool is read with the cap 5 mm, 2 cm, 5 cm, 10 cm and 30 cm under the
## lamp, at biases 0.0, 0.01, 0.03 and 0.1, against the unshadowed pool. Luma is the frame's
## band the selftest reads, 0..1. Opens a window (headless draws nothing) and quits itself.

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
	lamp.position = Vector3(0.0, rr.mount_height, 0.0)       # on the axis, at the lens point
	print("PROBE lamp world y %.4f, spot_range %.2f, angle %.1f, normal_bias %.3f, opacity %.2f" % [
		lamp.global_position.y, lamp.spot_range, lamp.spot_angle, lamp.shadow_normal_bias,
		lamp.shadow_opacity])
	print("PROBE driver: %s / %s" % [RenderingServer.get_video_adapter_name(),
		RenderingServer.get_video_adapter_api_version()])
	for gap: float in [0.005, 0.02, 0.05, 0.1, 0.3]:
		var cap: float = mount - gap
		cm.height = cap
		shaft.position = Vector3(0.0, cap * 0.5, 0.0)
		lamp.shadow_enabled = false
		var unshadowed: float = await _read()
		lamp.shadow_enabled = true
		var row: String = "PROBE gap %.3f m  unshadowed %.3f" % [gap, unshadowed]
		for bias: float in [0.0, 0.01, 0.03, 0.1]:
			lamp.shadow_bias = bias
			var got: float = await _read()
			row += "  bias %.2f -> %.3f" % [bias, got]
		print(row)
	quit(0)
