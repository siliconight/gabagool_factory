extends SceneTree
## A MOCKUP, NOT PIPELINE OUTPUT: what the far side of the through road could
## be, shown on a COPY of cold run 9145's walk copy (gas_block_001, seed 9080).
## Three states, the same cameras each:
##   as_is      the plate's perimeter wall 5.4 m past the far sidewalk;
##   facades    buildings across the street, fronts to the road -- the
##              level's own themed shells stood as backdrop (a real version
##              would be facade-only shells, Lot's `blockers`);
##   vacant     a chain-link fence along the far walk and a dirt lot behind
##              it, weeds, rubble, a tree, a dumpster, flyers on the fence.
##     godot --path <mock copy> --script mock_across.gd -- <out dir> <dirt png> <gravel png>
## Plan (x, y) is Godot (x, -y). The through road is at plan y -27.65, its
## far sidewalk ends at y -35.65, the plate at y -41.

const ROAD_Y := -27.65
const FAR_WALK := -35.65
const PLATE_S := -41.0

## [name, eye (plan x, plan y, height), target (plan x, plan y, height)]
const SHOTS: Array = [
	["across_from_the_storefronts", Vector3(-10.0, -21.0, 1.7), Vector3(-10.0, -60.0, 3.0)],
	["down_the_row", Vector3(-80.0, -21.5, 1.7), Vector3(40.0, -42.0, 2.0)],
	["above_from_the_south", Vector3(0.0, -110.0, 50.0), Vector3(0.0, -20.0, 0.0)],
]


func _initialize() -> void:
	_run.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _g(p: Vector3) -> Vector3:
	return Vector3(p.x, p.z, -p.y)


func _hide_canvas(n: Node) -> void:
	if n is CanvasLayer and not String(n.name).contains("Lux"):
		(n as CanvasLayer).visible = false
	for c: Node in n.get_children():
		_hide_canvas(c)


func _tex(path: String) -> ImageTexture:
	var img := Image.load_from_file(path)
	img.generate_mipmaps()
	return ImageTexture.create_from_image(img)


func _ground(parent: Node3D, tex: Texture2D, x0: float, y0: float, x1: float, y1: float, metres: float, tint: Color) -> void:
	var mi := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(x1 - x0, y1 - y0)
	mi.mesh = pm
	var m := StandardMaterial3D.new()
	m.albedo_texture = tex
	m.albedo_color = tint
	m.uv1_triplanar = true
	m.uv1_world_triplanar = true
	m.uv1_scale = Vector3(1.0 / metres, 1.0 / metres, 1.0 / metres)
	m.roughness = 0.95
	mi.material_override = m
	mi.position = _g(Vector3((x0 + x1) / 2.0, (y0 + y1) / 2.0, 0.004))
	parent.add_child(mi)


func _chain_link() -> ImageTexture:
	var n := 64
	var img := Image.create(n, n, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var wire := Color(0.62, 0.64, 0.62, 1.0)
	for i in range(n):
		for k in [0, 16, 32, 48]:
			img.set_pixel(i, (i + k) % n, wire)
			img.set_pixel(i, (n - 1 - i + k) % n, wire)
	return ImageTexture.create_from_image(img)


func _fence(parent: Node3D, x0: float, x1: float, y: float) -> void:
	var h := 1.85
	var steel := StandardMaterial3D.new()
	steel.albedo_color = Color(0.45, 0.46, 0.45)
	steel.metallic = 0.6
	steel.roughness = 0.5
	var panel := MeshInstance3D.new()
	var qm := QuadMesh.new()
	qm.size = Vector2(x1 - x0, h)
	panel.mesh = qm
	var m := StandardMaterial3D.new()
	m.albedo_texture = _chain_link()
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	m.alpha_scissor_threshold = 0.5
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	m.uv1_scale = Vector3((x1 - x0) / 0.6, h / 0.6, 1.0)
	panel.material_override = m
	panel.position = _g(Vector3((x0 + x1) / 2.0, y, h / 2.0))
	parent.add_child(panel)
	var rail := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(x1 - x0, 0.05, 0.05)
	rail.mesh = bm
	rail.material_override = steel
	rail.position = _g(Vector3((x0 + x1) / 2.0, y, h))
	parent.add_child(rail)
	var x := x0
	while x <= x1 + 0.01:
		var post := MeshInstance3D.new()
		var cm := CylinderMesh.new()
		cm.top_radius = 0.035
		cm.bottom_radius = 0.035
		cm.height = h + 0.08
		post.mesh = cm
		post.material_override = steel
		post.position = _g(Vector3(x, y, (h + 0.08) / 2.0))
		parent.add_child(post)
		x += 3.0


func _place(parent: Node3D, scene_path: String, x: float, y: float, yaw_deg: float) -> void:
	var ps: PackedScene = load(scene_path)
	if ps == null:
		print("MOCK missing ", scene_path)
		return
	var n: Node3D = ps.instantiate()
	n.position = _g(Vector3(x, y, 0.0))
	n.rotation = Vector3(0.0, deg_to_rad(yaw_deg), 0.0)
	parent.add_child(n)


func _scatter(parent: Node3D, mesh_path: String, count: int, x0: float, y0: float, x1: float, y1: float, rseed: int, scale: float) -> void:
	var mesh: Mesh = load(mesh_path)
	if mesh == null:
		print("MOCK missing ", mesh_path)
		return
	var rng := RandomNumberGenerator.new()
	rng.seed = rseed
	for i in range(count):
		var mi := MeshInstance3D.new()
		mi.mesh = mesh
		mi.position = _g(Vector3(rng.randf_range(x0, x1), rng.randf_range(y0, y1), 0.0))
		mi.rotation.y = rng.randf_range(0.0, TAU)
		var s := scale * rng.randf_range(0.7, 1.5)
		mi.scale = Vector3(s, s, s)
		parent.add_child(mi)


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 3:
		print("MOCK needs <out dir> <dirt png> <gravel png>")
		_exit(2)
		return
	change_scene_to_file("res://_walk.tscn")
	for _i in range(30):
		await process_frame
	var steady: int = 0
	var waited: int = 0
	while steady < 30 and waited < 6000:
		await process_frame
		waited += 1
		steady = steady + 1 if is_equal_approx(root.get_viewport().scaling_3d_scale, 1.0) else 0
	_hide_canvas(root)
	var wall: Node3D = root.find_child("perim_S", true, false) as Node3D
	if wall == null:
		print("MOCK no perim_S")
		_exit(2)
		return
	var site: Node3D = wall.get_parent() as Node3D
	var dirt := _tex(args[1])
	var gravel := _tex(args[2])

	# FACADES: the level's own shells across the street, fronts to the road
	# (yaw 180), each street edge 2 m off the far walk; asphalt behind them.
	var facades := Node3D.new()
	site.add_child(facades)
	_ground(facades, gravel, -95.0, -120.0, 95.0, PLATE_S, 3.0, Color(0.42, 0.42, 0.44))
	var line := FAR_WALK - 2.0
	_place(facades, "res://lot/bank_tower_a02/site.tscn", -62.0, line - 14.2, 180.0)
	_place(facades, "res://lot/gas_station_a03/site.tscn", -14.0, line - 8.2, 180.0)
	_place(facades, "res://lot/freight_terminal_a01/site.tscn", 45.0, line - 16.2, 180.0)

	# VACANT: a chain-link fence 1 m behind the far walk, dirt behind it,
	# weeds, rubble and litter, a tree, a dumpster, flyers on the fence.
	var vacant := Node3D.new()
	site.add_child(vacant)
	_ground(vacant, dirt, -95.0, -120.0, 95.0, FAR_WALK - 0.05, 4.0, Color(1, 1, 1))
	_fence(vacant, -90.0, 90.0, FAR_WALK - 1.0)
	_scatter(vacant, "res://dressing/weed_tuft.res", 900, -90.0, -100.0, 90.0, FAR_WALK - 1.5, 7, 1.6)
	_scatter(vacant, "res://dressing/rubble_frag.res", 260, -90.0, -100.0, 90.0, FAR_WALK - 1.5, 11, 2.2)
	_scatter(vacant, "res://dressing/litter_scrap.res", 200, -90.0, -60.0, 90.0, FAR_WALK - 1.2, 13, 1.2)
	_place(vacant, "res://cover/prop_red_maple_delco_1997_01_w400_d400_h600.glb", -40.0, -55.0, 30.0)
	_place(vacant, "res://cover/prop_pin_oak_delco_1997_01_w400_d400_h650.glb", 35.0, -70.0, 0.0)
	_place(vacant, "res://cover/prop_dumpster_delco_1997_01_w183_d110_h130_n3.glb", 10.0, -44.0, 170.0)
	_place(vacant, "res://cover/prop_poster_wall_delco_1997_01_w300_d1_h81_falley.glb", -22.0, FAR_WALK - 1.05, 180.0)

	var cam := Camera3D.new()
	cam.fov = 65.0
	root.add_child(cam)
	cam.make_current()
	var fill := DirectionalLight3D.new()
	fill.light_energy = 0.6
	root.add_child(fill)
	fill.rotation_degrees = Vector3(-55.0, 200.0, 0.0)
	for state in ["as_is", "facades", "vacant"]:
		wall.visible = state == "as_is"
		facades.visible = state == "facades"
		vacant.visible = state == "vacant"
		for s in SHOTS:
			cam.look_at_from_position(_g(s[1]), _g(s[2]), Vector3.UP)
			for _i in range(12):
				await process_frame
			var path: String = "%s/%s_%s.png" % [args[0], state, String(s[0])]
			root.get_viewport().get_texture().get_image().save_png(path)
			print("MOCK wrote ", path)
	print("MOCK done")
	_exit(0)
