extends SceneTree
# Scout window prototype (roadmap 295): the walker's "1990s palm pilot...but with a little more backlight and color",
# a window a game opens at runtime showing the level's buildings and their 3D schematics. Built in code, reads a
# package's buildings.json, turns the selected building's scout model. Saves frames and quits.
# Args after --: <buildings.json> <models dir> <out prefix>

const LCD := Color(0.56, 0.68, 0.53)
const LCD_GLOW := Color(0.78, 0.95, 0.82)
const INK := Color(0.08, 0.12, 0.08)
const INK_SOFT := Color(0.20, 0.28, 0.19)
const PLASTIC := Color(0.29, 0.31, 0.29)
const ACCENTS := {"SCORE": Color(1.00, 0.22, 0.22), "SAFE/CAM": Color(0.80, 0.55, 1.00), "ENTRY": Color(1.00, 0.55, 0.20), "STAIRS": Color(1.00, 0.85, 0.35),
		"LADDER": Color(0.55, 1.00, 0.75), "HOLE": Color(1.00, 0.40, 0.70), "WINDOW": Color(0.45, 0.85, 0.95)}

const SCREEN := """
shader_type canvas_item;
uniform vec4 lcd : source_color;
uniform vec4 glow : source_color;
void fragment() {
	float d = distance(UV, vec2(0.55, 0.42));
	vec3 c = mix(glow.rgb, lcd.rgb, smoothstep(0.0, 0.8, d));
	vec2 px = fract(FRAGCOORD.xy / 3.0);
	float grid = min(step(0.8, px.x) + step(0.8, px.y), 1.0);
	c *= 1.0 - 0.07 * grid;
	COLOR = vec4(c, 1.0);
}
"""
const BODY := """
shader_type spatial;
void fragment() {
	ALBEDO = COLOR.rgb;
	ROUGHNESS = 0.9;
	EMISSION = COLOR.rgb * (1.0 - COLOR.a) * 2.4;
}
"""

var models_dir: String
var prefix: String
var names: Array = []
var pivot: Node3D
var cam: Camera3D
var list_box: VBoxContainer
var title: Label
var subtitle: Label
var radius: float = 10.0


func _initialize() -> void:
	var a: PackedStringArray = OS.get_cmdline_user_args()
	var idx: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(a[0]))
	models_dir = a[1]
	prefix = a[2]
	for e in idx["buildings"]:
		var id: String = e["id"]
		if e["kind"] == "building" and not names.has(id):
			names.append(id)
	_build_ui()
	_run.call_deferred()


func _box(bg: Color, radius_px: int, border: Color, border_px: int) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.set_corner_radius_all(radius_px)
	s.border_color = border
	s.set_border_width_all(border_px)
	return s


func _label(text: String, size: int, color: Color, shadow: bool) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	if shadow:
		# a hard one-pixel offset in a lit tone under the ink: the walker's "duplicate layer offset", LCD-sized
		l.add_theme_color_override("font_shadow_color", Color(LCD_GLOW.r, LCD_GLOW.g, LCD_GLOW.b, 0.85))
		l.add_theme_constant_override("shadow_offset_x", 1)
		l.add_theme_constant_override("shadow_offset_y", 1)
	return l


func _build_ui() -> void:
	var ui := Control.new()
	ui.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.add_child(ui)
	var desk := ColorRect.new()
	desk.color = Color(0.10, 0.11, 0.12)
	desk.set_anchors_preset(Control.PRESET_FULL_RECT)
	ui.add_child(desk)
	# the device: chunky plastic, a soft layered drop shadow, a bevel
	var device := Panel.new()
	var dbox := _box(PLASTIC, 34, Color(0.18, 0.19, 0.18), 5)
	dbox.shadow_color = Color(0, 0, 0, 0.45)
	dbox.shadow_size = 28
	dbox.shadow_offset = Vector2(12, 16)
	device.add_theme_stylebox_override("panel", dbox)
	device.position = Vector2(90, 40)
	device.size = Vector2(1100, 880)
	ui.add_child(device)
	var brand := _label("GABAGOOL  SCOUT", 18, Color(0.72, 0.74, 0.70), false)
	brand.position = Vector2(60, 22)
	device.add_child(brand)
	# the screen: a backlit LCD with its pixel grid, set into a dark bezel
	var bezel := Panel.new()
	bezel.add_theme_stylebox_override("panel", _box(Color(0.12, 0.14, 0.12), 14, Color(0.07, 0.08, 0.07), 3))
	bezel.position = Vector2(50, 60)
	bezel.size = Vector2(1000, 700)
	device.add_child(bezel)
	var screen := ColorRect.new()
	var sm := ShaderMaterial.new()
	sm.shader = Shader.new()
	sm.shader.code = SCREEN
	sm.set_shader_parameter("lcd", LCD)
	sm.set_shader_parameter("glow", LCD_GLOW)
	screen.material = sm
	screen.position = Vector2(18, 18)
	screen.size = Vector2(964, 664)
	bezel.add_child(screen)
	# header: inverse bar, as the handhelds drew a title
	var bar := ColorRect.new()
	bar.color = INK
	bar.position = Vector2(0, 0)
	bar.size = Vector2(964, 40)
	screen.add_child(bar)
	var head := _label(" SCOUT  -  RESTAURANT ROW", 20, LCD_GLOW, false)
	head.position = Vector2(8, 6)
	screen.add_child(head)
	# the list of buildings
	list_box = VBoxContainer.new()
	list_box.position = Vector2(16, 58)
	list_box.size = Vector2(250, 400)
	list_box.add_theme_constant_override("separation", 6)
	screen.add_child(list_box)
	list_box.add_child(_label("BUILDINGS", 15, INK_SOFT, false))
	# the 3D schematic, in a world of its own, its background the LCD
	var svc := SubViewportContainer.new()
	svc.stretch = true
	svc.position = Vector2(280, 52)
	svc.size = Vector2(668, 520)
	screen.add_child(svc)
	var sv := SubViewport.new()
	sv.own_world_3d = true
	sv.transparent_bg = true
	sv.msaa_3d = Viewport.MSAA_4X
	svc.add_child(sv)
	var world := Node3D.new()
	sv.add_child(world)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_CLEAR_COLOR
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(1, 1, 1)
	e.ambient_light_energy = 0.55
	env.environment = e
	world.add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, -35, 0)
	sun.light_energy = 0.6
	sun.shadow_enabled = true
	world.add_child(sun)
	pivot = Node3D.new()
	world.add_child(pivot)
	cam = Camera3D.new()
	cam.fov = 30.0
	world.add_child(cam)
	title = _label("", 22, INK, true)
	title.position = Vector2(290, 566)
	screen.add_child(title)
	subtitle = _label("", 14, INK_SOFT, false)
	subtitle.position = Vector2(290, 596)
	screen.add_child(subtitle)
	# the legend: what lights up, in its own colour on an ink chip
	var leg := HBoxContainer.new()
	leg.position = Vector2(16, 636)
	leg.add_theme_constant_override("separation", 6)
	screen.add_child(leg)
	for k in ACCENTS:
		var chip := PanelContainer.new()
		chip.add_theme_stylebox_override("panel", _box(INK, 4, INK, 0))
		var l := _label(" %s " % k, 11, ACCENTS[k], false)
		chip.add_child(l)
		leg.add_child(chip)
	# the handheld's hard buttons
	for i in range(4):
		var b := Panel.new()
		b.add_theme_stylebox_override("panel", _box(Color(0.22, 0.24, 0.22), 26, Color(0.14, 0.15, 0.14), 3))
		b.position = Vector2(170 + i * 210, 790)
		b.size = Vector2(52, 52)
		device.add_child(b)


func _show(i: int) -> void:
	for c in pivot.get_children():
		c.free()
	for c in list_box.get_children().slice(1):
		c.free()
	for j in range(names.size()):
		var row := PanelContainer.new()
		var sel: bool = j == i
		row.add_theme_stylebox_override("panel", _box(INK if sel else Color(0, 0, 0, 0), 3, INK_SOFT, 0 if sel else 1))
		row.add_child(_label("  %s %s" % [">" if sel else " ", String(names[j]).to_upper().replace("_", " ")], 15,
				LCD_GLOW if sel else INK, false))
		list_box.add_child(row)
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	if doc.append_from_file("%s/%s_palm.glb" % [models_dir, names[i]], state) != OK:
		return
	var model: Node = doc.generate_scene(state)
	pivot.add_child(model)
	var mat := ShaderMaterial.new()
	mat.shader = Shader.new()
	mat.shader.code = BODY
	var ms: Array = []
	_collect(model, ms)
	for n in ms:
		(n as MeshInstance3D).material_override = mat
	# the storeys are the meshes named storey_<n>; a storey's points ride under it as its child
	var floors: Array = ms.filter(func(n: Node) -> bool: return not String(n.name).ends_with("_points"))
	floors.sort_custom(func(x: Node3D, y: Node3D) -> bool: return x.position.y < y.position.y)
	var box := AABB()
	var k: int = 0
	for n in floors:
		var mi: MeshInstance3D = n as MeshInstance3D
		mi.position.y += k * 6.0
		var b: AABB = mi.transform * mi.get_aabb()
		box = b if k == 0 else box.merge(b)
		k += 1
	model.position = -box.get_center()
	radius = box.size.length() * 0.5
	title.text = String(names[i]).to_upper().replace("_", " ")
	subtitle.text = "%d FLOOR(S)  -  DRAG TO TURN  -  UP/DOWN FOR FLOORS" % floors.size()


func _collect(n: Node, out: Array) -> void:
	if n is MeshInstance3D:
		out.append(n)
	for c in n.get_children():
		_collect(c, out)


func _aim(az: float) -> void:
	var r: float = deg_to_rad(az)
	var el: float = deg_to_rad(36.0)
	var d: float = radius / sin(deg_to_rad(cam.fov * 0.5)) * 1.0
	cam.position = Vector3(cos(r) * cos(el), sin(el), sin(r) * cos(el)) * d
	cam.look_at(Vector3.ZERO, Vector3.UP)


func _run() -> void:
	var shots: Array = [[0, 35.0], [0, 215.0], [2, 60.0], [1, 35.0]]
	for s in shots:
		_show(int(s[0]))
		_aim(float(s[1]))
		for f in range(20):
			await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("%s_%s_az%03d.png" % [prefix, names[int(s[0])], int(s[1])])
	print("draws %d" % RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME))
	quit(0)
