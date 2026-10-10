extends SceneTree
## A traffic signal's lenses through Level Factory 0.165.0's import: which lens each head
## shows at three moments of the 60 s cycle. Windowed (headless draws nothing), quits itself.
##
##   godot --path <this project> --script res://probe.gd
##
## Prints, per lens surface, the material class and its window; then, per moment, each lens's
## brightness at its own pixels and which lens is brightest, per head. Saves frame_<t>.png.

const MOMENTS: Array = [8.0, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0, 31.5, 32.0, 32.5, 33.0,
	33.5, 34.0, 34.5, 35.0, 35.5, 36.0, 36.5, 37.0, 37.5, 38.0, 38.5, 39.0, 39.5, 40.0, 40.5,
	41.0, 41.5, 42.0, 47.0]
## Each lens's centre in the frame, read off frame_08/35/47 of the first run (the camera
## does not move): near head x 249, mast head x 788; red, amber, green rows.
const LENS_PX: Dictionary = {"near": [249, [349, 391, 433]], "mast": [788, [282, 324, 366]]}
var _t: float = 0.0
var _next: int = 0
var _cam: Camera3D = null


func _initialize() -> void:
	var ps: PackedScene = load("res://signal.glb") as PackedScene
	if ps == null:
		print("PROBE no signal.glb scene")
		quit(2)
		return
	var sig: Node3D = ps.instantiate() as Node3D
	root.add_child(sig)
	_report_lenses(sig)
	var env: WorldEnvironment = WorldEnvironment.new()
	var e: Environment = Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.05, 0.06, 0.08)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.35, 0.35, 0.38)
	e.ambient_light_energy = 0.6
	env.environment = e
	root.add_child(env)
	var sun: DirectionalLight3D = DirectionalLight3D.new()
	sun.light_energy = 0.5
	sun.rotation_degrees = Vector3(-40.0, 20.0, 0.0)
	root.add_child(sun)
	_cam = Camera3D.new()
	_cam.fov = 50.0
	root.add_child(_cam)
	# a camera looks down -Z by default, which is at the heads from here
	_cam.position = Vector3(2.45, 1.95, 6.2)


func _report_lenses(n: Node) -> void:
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null and String(mi.name).contains("Lens"):
		for i in range(mi.mesh.get_surface_count()):
			var m: Material = mi.mesh.surface_get_material(i)
			var line: String = "PROBE lens %s surface %d: %s %s" % [mi.name, i, m.get_class(), m.resource_name]
			var sm: ShaderMaterial = m as ShaderMaterial
			if sm != null:
				line += " window %.1f-%.1f s, energy %.2f" % [float(sm.get_shader_parameter("lit_from_s")),
					float(sm.get_shader_parameter("lit_to_s")), float(sm.get_shader_parameter("energy"))]
			print(line)
	for c in n.get_children():
		_report_lenses(c)


func _process(delta: float) -> bool:
	_t += delta
	if _next < MOMENTS.size() and _t >= float(MOMENTS[_next]):
		_capture(float(MOMENTS[_next]))
		_next += 1
	return _next >= MOMENTS.size()


func _capture(at: float) -> void:
	var img: Image = root.get_texture().get_image()
	img.save_png("res://frame_%04.1f.png" % [at])
	var line: String = "PROBE t %4.1f s:" % [at]
	for head in ["near", "mast"]:
		var spec: Array = LENS_PX[head]
		var x: int = int(spec[0])
		var rows: Array = spec[1]
		var vals: Array = []
		for y in rows:
			vals.append(_mean_max(img, x, int(y)))
		var names: Array = ["red", "amber", "green"]
		var best: int = 0
		for k in range(3):
			if float(vals[k]) > float(vals[best]):
				best = k
		line += "  %s %s (red %.2f amber %.2f green %.2f)" % [head, names[best], vals[0], vals[1], vals[2]]
	print(line)


## The mean over a 5 x 5 box of each pixel's brightest channel.
func _mean_max(img: Image, x: int, y: int) -> float:
	var s: float = 0.0
	for dy in range(-2, 3):
		for dx in range(-2, 3):
			var c: Color = img.get_pixel(x + dx, y + dy)
			s += maxf(c.r, maxf(c.g, c.b))
	return s / 25.0

