extends SceneTree
## The walk copy's asset flags (`walk_asset_flags.gd`), proven headless, 2026-10-19 (factory roadmap 253).
##
##     a project holding this file and walk_asset_flags.gd as res://_walk_asset_flags.gd, then
##     godot --headless --path <that project> -s res://walk_asset_flags_selftest.gd
##
## Exit 0 = every check held. Exit 1 = a check failed. Exit 2 = could not run.
##
## Builds what a walk copy's view is made of: a camera, a Zoo module instanced over Deli Counter's greybox -- a
## mesh under a node whose `scene_file_path` is `res://lot/deli_a01/art/zoo/<module>.glb`, nearer the camera --
## and a greybox collider behind it under the building's `res://lot/deli_a01/site.tscn`. Presses G and checks the
## record names the MODULE the eye sees, not the collider the physics ray meets; hides the mesh, presses P and
## checks the collider stands in, said as `how: physics`. An echo and a release must write nothing.
##
## And what a flag leaves on screen (the walker, 2026-10-19): each thing flagged is boxed, green for good and red for
## needs love, and the box is held off its bounds. The box goes round the module when the pick is under a model (the
## GLB the module came from), and round the node picked when it is under a scene: the building's collider, and a kerb
## in the level's own scene -- `res://presentation/lux.applied.tscn`, where a walk copy's site lives, with a second
## piece 30 m off that a box round the level would take in -- which the banner names by its path, not the level's
## file. A second flag of one asset repaints its box and adds none; a pick along a line that meets only a box finds
## nothing, beside its control, that the line does meet the box; a mesh round the whole level, its faces 450 m off as
## Lux's horizon glow's are, is never picked, and a press at the open sky boxes nothing; the boxes outlast the banner;
## and the banner hangs from the foot of the screen in its verdict's colour.

const SUBJECT := "res://_walk_asset_flags.gd"
const FLAGS := "res://asset_flags.jsonl"
const MODULE := "res://lot/deli_a01/art/zoo/prop_bench_delco_1997_01_w180.glb"
const BUILDING := "res://lot/deli_a01/site.tscn"
const SITE := "res://presentation/lux.applied.tscn"
## What each box must ring, worked by hand from the sizes and places the scene below is built with.
const BENCH := AABB(Vector3(-0.5, -0.5, -5.5), Vector3(1, 1, 1))
const SLAB := AABB(Vector3(-2, -2, -8.5), Vector3(4, 4, 1))
const KERB := AABB(Vector3(5.5, -0.1, -0.5), Vector3(1, 0.2, 1))

var _fails: int = 0
var _consts: Dictionary = {}


func _initialize() -> void:
	_main()


func _check(label: String, ok: bool) -> void:
	if not ok:
		_fails += 1
	print("%s  %s" % ["ok  " if ok else "FAIL", label])


func _press(key: Key, pressed: bool, echo: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = key
	ev.pressed = pressed
	ev.echo = echo
	root.push_input(ev)


func _lines() -> Array:
	if not FileAccess.file_exists(FLAGS):
		return []
	var out: Array = []
	for ln in FileAccess.get_file_as_string(FLAGS).split("\n", false):
		out.append(JSON.parse_string(ln))
	return out


## The boxes the handler has drawn this session.
func _boxes(flags: Node) -> Array:
	var holder: Node = flags.get_node_or_null(^"AssetFlagOutlines")
	return [] if holder == null else holder.get_children()


## The box drawn round `target`, or null.
func _box_for(flags: Node, target: Node) -> MeshInstance3D:
	for b in _boxes(flags):
		var n: Node = b
		if n.get_meta(&"target", NodePath()) == target.get_path():
			return n as MeshInstance3D
	return null


func _color(box: MeshInstance3D) -> Color:
	if box == null or not (box.material_override is ShaderMaterial):
		return Color.BLACK
	var m: ShaderMaterial = box.material_override as ShaderMaterial
	var c: Color = m.get_shader_parameter(&"color")
	return c


func _green(c: Color) -> bool:
	return c.g > 0.6 and c.r < 0.5 and c.b < 0.5


func _red(c: Color) -> bool:
	return c.r > 0.8 and c.g < 0.4 and c.b < 0.4


## True when `box` rings `inner`: its bounds grown by the handler's pad and half an edge's thickness, to float error.
func _rings(box: MeshInstance3D, inner: AABB) -> bool:
	if box == null or box.mesh == null:
		return false
	var grow: float = float(_consts.get("OUTLINE_PAD_M", NAN)) + 0.5 * float(_consts.get("OUTLINE_EDGE_M", NAN))
	var want: AABB = inner.grow(grow)
	var got: AABB = box.global_transform * box.mesh.get_aabb()
	return got.position.is_equal_approx(want.position) and got.size.is_equal_approx(want.size)


func _main() -> void:
	if not ResourceLoader.exists(SUBJECT):
		print("could not run: no %s in this project" % SUBJECT)
		quit(2)
		return
	_consts = (load(SUBJECT) as GDScript).get_script_constant_map()
	if FileAccess.file_exists(FLAGS):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(FLAGS))
	var scene := Node3D.new()
	scene.name = &"Scene"
	root.add_child(scene)
	current_scene = scene
	var cam := Camera3D.new()
	scene.add_child(cam)
	cam.current = true
	# the building, as a walk copy instances it, with its greybox collider 8 m ahead
	var bldg := Node3D.new()
	bldg.name = &"b0"
	bldg.scene_file_path = BUILDING
	scene.add_child(bldg)
	var body := StaticBody3D.new()
	body.name = &"slab_col_1"
	bldg.add_child(body)
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(4, 4, 1)
	shape.shape = box
	body.add_child(shape)
	body.position = Vector3(0, 0, -8)
	# the Zoo module over it, 5 m ahead: what the eye sees
	var module := Node3D.new()
	module.name = &"prop_bench"
	module.scene_file_path = MODULE
	bldg.add_child(module)
	var mi := MeshInstance3D.new()
	mi.name = &"bench"
	var bm := BoxMesh.new()
	bm.size = Vector3(1, 1, 1)
	mi.mesh = bm
	module.add_child(mi)
	mi.position = Vector3(0, 0, -5)
	# the level's own scene, as a walk copy instances it, with a kerb 6 m to the camera's right, a second piece of it
	# 30 m beyond, which a box round the whole level would take in, and a mesh round all of it with its faces 450 m
	# off, as Lux's horizon glow is
	var site := Node3D.new()
	site.name = &"Site"
	site.scene_file_path = SITE
	scene.add_child(site)
	var slab_mesh := BoxMesh.new()
	slab_mesh.size = Vector3(1, 0.2, 1)
	var kerb := MeshInstance3D.new()
	kerb.name = &"kerb"
	kerb.mesh = slab_mesh
	site.add_child(kerb)
	kerb.position = Vector3(6, 0, 0)
	var far_piece := MeshInstance3D.new()
	far_piece.name = &"far_piece"
	far_piece.mesh = slab_mesh
	site.add_child(far_piece)
	far_piece.position = Vector3(36, 0, 0)
	var horizon := MeshInstance3D.new()
	horizon.name = &"horizon"
	var hm := BoxMesh.new()
	hm.size = Vector3(900, 900, 900)
	horizon.mesh = hm
	site.add_child(horizon)
	var flags: Node = (load(SUBJECT) as GDScript).new()
	flags.name = &"WalkAssetFlags"
	scene.add_child(flags)
	await physics_frame
	await physics_frame
	await process_frame

	_press(KEY_G, true, false)
	await process_frame
	var recs: Array = _lines()
	_check("G writes one record", recs.size() == 1)
	if recs.size() >= 1:
		var r: Dictionary = recs[0]
		_check("the verdict is good", String(r.get("verdict")) == "good")
		_check("picked by render, not physics", String(r.get("how")) == "render")
		_check("the asset is the module the eye sees", String(r.get("asset")) == "prop_bench_delco_1997_01_w180")
		_check("its file is the module's GLB", String(r.get("asset_file")) == MODULE)
		_check("the building is deli_a01", String(r.get("building")) == "deli_a01")
		_check("the point is the mesh's near face", absf(float(r.get("distance_m", 0.0)) - 4.5) < 0.01)
		_check("the collider is recorded beside it", String(r.get("collider")).ends_with("slab_col_1"))
	_check("G boxes the module", _boxes(flags).size() == 1 and _box_for(flags, module) != null)
	_check("in green", _green(_color(_box_for(flags, module))))
	_check("round the module's bounds, held off them", _rings(_box_for(flags, module), BENCH))

	_press(KEY_G, true, true)
	_press(KEY_G, false, false)
	await process_frame
	_check("an echo and a release write nothing", _lines().size() == 1)
	_check("and draw nothing", _boxes(flags).size() == 1)

	mi.visible = false
	await process_frame
	_press(KEY_P, true, false)
	await process_frame
	recs = _lines()
	_check("P writes a second record", recs.size() == 2)
	if recs.size() >= 2:
		var r2: Dictionary = recs[1]
		_check("the verdict is needs_love", String(r2.get("verdict")) == "needs_love")
		_check("with the mesh hidden the collider stands in", String(r2.get("how")) == "physics")
		_check("and names its building's scene", String(r2.get("asset_file")) == BUILDING)
		_check("the building is still deli_a01", String(r2.get("building")) == "deli_a01")
	_check("P boxes the collider itself, the building being a scene and not a model", _boxes(flags).size() == 2
		and _box_for(flags, body) != null and _box_for(flags, bldg) == null)
	_check("in red", _red(_color(_box_for(flags, body))))
	_check("round its shape, nothing under it being drawn", _rings(_box_for(flags, body), SLAB))

	mi.visible = true
	await process_frame
	_press(KEY_P, true, false)
	await process_frame
	recs = _lines()
	_check("P on the module writes a third record", recs.size() == 3)
	if recs.size() >= 3:
		var r3: Dictionary = recs[2]
		_check("needs_love, picked by render", String(r3.get("verdict")) == "needs_love"
			and String(r3.get("how")) == "render")
	_check("and repaints the module's box rather than adding one", _boxes(flags).size() == 2)
	_check("red now", _red(_color(_box_for(flags, module))))
	_check("still round the module", _rings(_box_for(flags, module), BENCH))

	cam.look_at(kerb.global_position, Vector3.UP)
	await process_frame
	_press(KEY_P, true, false)
	await process_frame
	recs = _lines()
	_check("P on the kerb writes a fourth record", recs.size() == 4)
	if recs.size() >= 4:
		var r4: Dictionary = recs[3]
		_check("which names the layer, as it always has", String(r4.get("asset_file")) == SITE)
	_check("the kerb is boxed itself, not the level", _rings(_box_for(flags, kerb), KERB)
		and _box_for(flags, site) == null)
	_check("in red", _red(_color(_box_for(flags, kerb))))
	_check("three boxes now", _boxes(flags).size() == 3)
	var shown: Label = flags.get("_label")
	_check("the banner names the kerb by its path, not the level's file", shown != null
		and shown.text.contains("kerb") and not shown.text.contains("lux.applied"))

	# a line from the camera's place to the module box's lower front edge passes under the bench and meets nothing
	# else in the scene: the box is all a pick along it could find
	var pad: float = float(_consts.get("OUTLINE_PAD_M", NAN))
	var dir: Vector3 = Vector3(0.0, BENCH.position.y - pad, BENCH.end.z + pad).normalized()
	var mbox: MeshInstance3D = _box_for(flags, module)
	_check("control: that line meets the box", mbox != null
		and float(flags.call("_triangle_t", mbox, Vector3.ZERO, dir)) < INF)
	var hit: Dictionary = flags.call("_render_hit", Vector3.ZERO, dir)
	_check("and a pick along it takes no box for an asset, nor the mesh 450 m off", hit.is_empty())

	# the open sky: nothing within reach but the mesh round the level, whose faces are 450 m off
	cam.look_at(Vector3(0, 50, -1), Vector3.UP)
	await process_frame
	_check("control: the line up meets the mesh round the level, out of reach", float(flags.call("_triangle_t",
		horizon, Vector3.ZERO, Vector3(0, 50, -1).normalized())) > float(_consts.get("RAY_LENGTH", INF)))
	_press(KEY_P, true, false)
	await process_frame
	recs = _lines()
	_check("P at the open sky writes a fifth record", recs.size() == 5)
	if recs.size() >= 5:
		var r5: Dictionary = recs[4]
		_check("which names nothing", String(r5.get("how")) == "none" and String(r5.get("node")) == "")
	_check("and boxes nothing", _boxes(flags).size() == 3)
	_check("the banner says nothing was in reach", shown != null and shown.text.contains("nothing within"))

	await create_timer(float(_consts.get("BANNER_SECS", 3.0)) + 0.5).timeout
	var banner: CanvasLayer = flags.get("_banner")
	_check("the banner goes after its seconds", banner != null and not banner.visible)
	_check("and the boxes stay", _boxes(flags).size() == 3)
	var label: Label = flags.get("_label")
	_check("the banner hangs from the foot of the screen, clear of F3's panels at the top", label != null
		and label.anchor_top == 1.0 and label.anchor_bottom == 1.0)
	_check("in the last verdict's colour", label != null and _red(label.get_theme_color(&"font_color")))

	DirAccess.remove_absolute(ProjectSettings.globalize_path(FLAGS))
	print("selftest: %d check(s) failed" % _fails)
	quit(1 if _fails > 0 else 0)
