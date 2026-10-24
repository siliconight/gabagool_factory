extends SceneTree
## Finding 2: the baked lightmap itself along one wall. For X from x0 to x1 in STEP at height Y on the wall plane
## WALL_Z, the triangle of the named mesh that holds the point (facing +Z or -Z), its UV2 interpolated, mapped into
## the atlas by the LightmapGIData user entry (rect P + uv2 * S, slice), and the texel read there (nearest, no
## filtering): its atlas pixel and its RGB. A step in these numbers at a module joint is a step the bake wrote; no
## step means the band is made after the lightmap. Headless: reads data, draws nothing. Measurements only.
## Frame: Godot world, metres; RGB as stored (linear, the bake's units).
##
##     godot --headless --path <walk copy> --script res://lm_wall_profile.gd -- <mesh path end> <wall_z> <y> <x0> <x1> <step>

const TOL := 0.05

var _frame := 0
var _mesh_end := "b1/MergedR_1"
var _wall_z := -6.34
var _y := 1.6
var _x0 := -11.0
var _x1 := 5.0
var _step := 0.05


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 6:
		_mesh_end = args[0]
		_wall_z = float(args[1])
		_y = float(args[2])
		_x0 = float(args[3])
		_x1 = float(args[4])
		_step = float(args[5])
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _bary(p: Vector2, a: Vector2, b: Vector2, c: Vector2) -> Vector3:
	var v0: Vector2 = b - a
	var v1: Vector2 = c - a
	var v2: Vector2 = p - a
	var d: float = v0.x * v1.y - v1.x * v0.y
	if absf(d) < 1e-12:
		return Vector3(-1, -1, -1)
	var v: float = (v2.x * v1.y - v1.x * v2.y) / d
	var w: float = (v0.x * v2.y - v2.x * v0.y) / d
	return Vector3(1.0 - v - w, v, w)


func _process(_d: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	var lms: Array = root.find_children("*", "LightmapGI", true, false)
	if lms.size() != 1:
		print("EXPECTED ONE LightmapGI, found %d: nothing measured" % lms.size())
		_exit(2)
		return true
	var lm: LightmapGI = lms[0]
	var data: LightmapGIData = lm.light_data
	var ud: Array = data.get("user_data")
	var rect := Rect2()
	var slice := -1
	var found_user := false
	for k in range(0, ud.size(), 4):
		if str(ud[k]).ends_with(_mesh_end):
			rect = ud[k + 1]
			slice = int(ud[k + 2])
			found_user = true
			break
	if not found_user:
		print("NO LIGHTMAP USER ENDING %s: nothing measured" % _mesh_end)
		_exit(2)
		return true
	# Headless holds no texture pixels (the dummy renderer), so read the bake's own EXR -- the file the layered
	# texture is imported from -- and cut the slice out of it the way its .import says it is stacked.
	var exr_path := ProjectSettings.globalize_path("res://bake.exr")
	var cfg := ConfigFile.new()
	if cfg.load("res://bake.exr.import") != OK:
		print("NO res://bake.exr.import: nothing measured")
		_exit(2)
		return true
	var sv: int = int(cfg.get_value("params", "slices/vertical", 0))
	var sh: int = int(cfg.get_value("params", "slices/horizontal", 0))
	var whole: Image = Image.load_from_file(exr_path)
	if whole == null or sv < 1 or sh != 1:
		print("BAKE EXR unreadable or not stacked one across (vertical %d horizontal %d): nothing measured" % [sv, sh])
		_exit(2)
		return true
	var slice_h: int = whole.get_height() / sv
	var img: Image = whole.get_region(Rect2i(0, slice * slice_h, whole.get_width(), slice_h))
	var src := "res://bake.exr %dx%d, %d slices stacked vertically, slice %d at rows %d..%d" % [whole.get_width(), whole.get_height(), sv, slice, slice * slice_h, (slice + 1) * slice_h - 1]
	print("LIGHTMAP %s slice %d image %dx%d format %d user rect %s" % [src, slice, img.get_width(), img.get_height(), img.get_format(), str(rect)])
	var mi: MeshInstance3D = null
	for n in root.find_children("*", "MeshInstance3D", true, false):
		if str((n as Node).get_path()).ends_with(_mesh_end):
			mi = n
	if mi == null:
		print("NO MESH ENDING %s: nothing measured" % _mesh_end)
		_exit(2)
		return true
	var xf: Transform3D = mi.global_transform
	var tris: Array = []
	var am: ArrayMesh = mi.mesh
	for s in am.get_surface_count():
		var arr: Array = am.surface_get_arrays(s)
		var verts: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
		var uv2: PackedVector2Array = arr[Mesh.ARRAY_TEX_UV2]
		var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX] if arr[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
		if idx.size() == 0:
			for i in verts.size():
				idx.append(i)
		for t in range(0, idx.size(), 3):
			var a: Vector3 = xf * verts[idx[t]]
			var b: Vector3 = xf * verts[idx[t + 1]]
			var c: Vector3 = xf * verts[idx[t + 2]]
			var cr: Vector3 = (b - a).cross(c - a)
			if cr.length() < 1e-9 or absf(cr.normalized().z) < 0.95:
				continue
			if absf((a.z + b.z + c.z) / 3.0 - _wall_z) > TOL:
				continue
			tris.append([Vector2(a.x, a.y), Vector2(b.x, b.y), Vector2(c.x, c.y), uv2[idx[t]], uv2[idx[t + 1]], uv2[idx[t + 2]]])
	print("PROFILE mesh %s wall z %.3f y %.3f x %.2f..%.2f step %.3f, %d wall triangles" % [mi.get_path(), _wall_z, _y, _x0, _x1, _step, tris.size()])
	var x := _x0
	while x <= _x1 + 1e-9:
		var p := Vector2(x, _y)
		var hit := false
		for tr in tris:
			var bc: Vector3 = _bary(p, tr[0], tr[1], tr[2])
			if bc.x < -1e-6 or bc.y < -1e-6 or bc.z < -1e-6:
				continue
			var u2: Vector2 = (tr[3] as Vector2) * bc.x + (tr[4] as Vector2) * bc.y + (tr[5] as Vector2) * bc.z
			var at: Vector2 = rect.position + u2 * rect.size
			var px: int = clampi(int(at.x * img.get_width()), 0, img.get_width() - 1)
			var py: int = clampi(int(at.y * img.get_height()), 0, img.get_height() - 1)
			var col: Color = img.get_pixel(px, py)
			print("x %7.3f uv2 (%.4f,%.4f) texel (%d,%d) rgb %.4f %.4f %.4f lum %.4f" % [x, u2.x, u2.y, px, py, col.r, col.g, col.b, 0.2126 * col.r + 0.7152 * col.g + 0.0722 * col.b])
			hit = true
			break
		if not hit:
			print("x %7.3f no wall triangle" % x)
		x += _step
	_exit(0)
	return true
