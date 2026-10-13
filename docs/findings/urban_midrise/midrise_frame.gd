extends SceneTree
## Deli Counter 0.213.0's mid-rise Empties stood in a row as a street wall, a rowhome Empty at its end for scale
## (roadmap 241). The shells as Deli Counter builds them -- greybox, before any theme -- so this shows
## massing, height and the window rhythm, not the look a level gives them.
##
##   godot --path <a project holding the GLBs, imported> -s res://midrise_frame.gd
##
## Windowed (headless draws nothing); it saves two frames beside itself and quits. Each shell is placed by
## its own meshes' bounds, touching the one before, its long side on the street. The shells' greybox
## materials (`gb_wall`, `gb_window`, `gb_ceiling`, `gb_threshold`) are near-white, which hid the windows,
## so each piece is TINTED BY ITS NODE NAME: a window's `_pane` dark, a door's `_leaf` wood, every other
## exterior piece -- the wall runs and each opening's `_sill` and `_lintel`, which wear the window's greybox
## material -- in a colour for the wall kind its family table gives that block (`WALLS`), the roof grey. An
## illustration of which piece is which, not any theme's look.

#: each block's wall kind, from Deli Counter's `presets.EMPTY_MIDRISES` and `EMPTY_ROWHOMES`
const WALLS := {"gs_empty_rowhome_a": "brick_orange", "gs_midrise_a": "brick_brown", "gs_midrise_b": "brick",
	"gs_midrise_c": "brick_orange", "gs_midrise_d": "stone_ext", "gs_midrise_e": "brick_brown",
	"gs_midrise_f": "brick"}
const WALL_TINT := {"brick": Color(0.55, 0.27, 0.22), "brick_brown": Color(0.42, 0.28, 0.22),
	"brick_orange": Color(0.62, 0.4, 0.26), "stone_ext": Color(0.62, 0.6, 0.55)}
const PANE := Color(0.16, 0.2, 0.26)
const LEAF := Color(0.35, 0.22, 0.13)
const OTHER := Color(0.55, 0.55, 0.56)

const NAMES := ["gs_empty_rowhome_a", "gs_midrise_a", "gs_midrise_b", "gs_midrise_c",
	"gs_midrise_d", "gs_midrise_e", "gs_midrise_f"]


func _initialize() -> void:
	_main.call_deferred()


func _bounds(n: Node) -> AABB:
	var box := AABB()
	var first := true
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh == null:
			continue
		var b: AABB = mi.global_transform * mi.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box


func _tint(n: Node, wall: Color) -> void:
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.mesh == null:
			continue
		var piece := String(mi.name)
		var col := OTHER
		if piece.ends_with("_pane"):
			col = PANE
		elif piece.ends_with("_leaf"):
			col = LEAF
		elif piece.begins_with("ext_") or piece.begins_with("parapet"):
			col = wall
		var mat := StandardMaterial3D.new()
		mat.albedo_color = col
		mi.material_override = mat


func _shot(cam: Camera3D, path: String) -> void:
	cam.make_current()
	for i in 12:
		await process_frame
	var img: Image = root.get_texture().get_image()
	img.save_png(path)
	print("[frame] %s (%d x %d)" % [ProjectSettings.globalize_path(path), img.get_width(), img.get_height()])


func _main() -> void:
	DisplayServer.window_set_size(Vector2i(1600, 900))
	root.size = Vector2i(1600, 900)
	var world := Node3D.new()
	root.add_child(world)
	var we := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.62, 0.70, 0.82)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.75, 0.75, 0.8)
	env.ambient_light_energy = 0.55
	we.environment = env
	world.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-42.0, -35.0, 0.0)
	sun.light_energy = 0.9
	sun.shadow_enabled = true
	world.add_child(sun)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(400.0, 400.0)
	ground.mesh = plane
	var gm := StandardMaterial3D.new()
	gm.albedo_color = Color(0.36, 0.36, 0.37)
	ground.material_override = gm
	world.add_child(ground)
	var x := 0.0
	var tallest := 0.0
	var depth_max := 0.0
	for n: String in NAMES:
		var ps: PackedScene = load("res://%s.glb" % n)
		if ps == null:
			print("[frame] REFUSED: %s did not load" % n)
			quit(2)
			return
		var inst: Node3D = ps.instantiate()
		world.add_child(inst)
		_tint(inst, WALL_TINT[WALLS[n]])
		await process_frame
		var b := _bounds(inst)
		# its long side along x: a shell deeper than wide is turned a quarter
		if b.size.z > b.size.x and not n.begins_with("gs_empty"):
			inst.rotation_degrees.y = 90.0
			await process_frame
			b = _bounds(inst)
		inst.position += Vector3(x - b.position.x, -b.position.y, -b.position.z - b.size.z)
		x += b.size.x
		tallest = maxf(tallest, b.size.y)
		depth_max = maxf(depth_max, b.size.z)
		print("[frame] %-20s %.1f m wide, %.1f m tall, %.1f m deep" % [n, b.size.x, b.size.y, b.size.z])
	var street := Camera3D.new()
	street.fov = 70.0
	world.add_child(street)
	street.position = Vector3(x * 0.05, 1.7, 30.0)
	street.look_at(Vector3(x * 0.6, tallest * 0.4, -depth_max * 0.5))
	var high := Camera3D.new()
	high.fov = 55.0
	world.add_child(high)
	high.position = Vector3(x * 0.5, tallest * 0.9, x * 0.9)
	high.look_at(Vector3(x * 0.5, tallest * 0.35, -depth_max * 0.5))
	await _shot(street, "res://midrise_street.png")
	await _shot(high, "res://midrise_high.png")
	quit(0)
