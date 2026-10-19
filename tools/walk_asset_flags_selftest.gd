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

const SUBJECT := "res://_walk_asset_flags.gd"
const FLAGS := "res://asset_flags.jsonl"
const MODULE := "res://lot/deli_a01/art/zoo/prop_bench_delco_1997_01_w180.glb"
const BUILDING := "res://lot/deli_a01/site.tscn"

var _fails: int = 0


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


func _main() -> void:
	if not ResourceLoader.exists(SUBJECT):
		print("could not run: no %s in this project" % SUBJECT)
		quit(2)
		return
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

	_press(KEY_G, true, true)
	_press(KEY_G, false, false)
	await process_frame
	_check("an echo and a release write nothing", _lines().size() == 1)

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

	DirAccess.remove_absolute(ProjectSettings.globalize_path(FLAGS))
	print("selftest: %d check(s) failed" % _fails)
	quit(1 if _fails > 0 else 0)
