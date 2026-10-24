extends SceneTree
## Finding 2: what a walk copy's LightmapGIData exposes -- its properties, its user entry for one mesh path, and its
## lightmap textures' sizes. The first step to reading a wall's texels; prints and stops. Headless.
##
##     godot --headless --path <walk copy> --script res://lm_props.gd -- <mesh path substring>

var _frame := 0
var _needle := "MergedR_1"


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() >= 1:
		_needle = args[0]
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _process(_d: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	for n in root.find_children("*", "LightmapGI", true, false):
		var lm: LightmapGI = n
		var data: LightmapGIData = lm.light_data
		if data == null:
			print("LIGHTMAPGI %s: no light_data" % lm.get_path())
			continue
		print("LIGHTMAPGI %s data %s" % [lm.get_path(), data.resource_path])
		for p in data.get_property_list():
			var nm: String = p["name"]
			var v: Variant = data.get(nm)
			var desc: String = type_string(typeof(v))
			if v is Array:
				desc += " size %d" % (v as Array).size()
			print("  PROP %s %s" % [nm, desc])
		print("  users %d" % data.get_user_count())
		for i in data.get_user_count():
			var up: String = str(data.get_user_path(i))
			if up.find(_needle) >= 0:
				print("  USER %d %s" % [i, up])
		var ud: Variant = data.get("user_data")
		if ud is Array:
			var arr: Array = ud
			for k in range(0, arr.size()):
				if str(arr[k]).find(_needle) >= 0:
					print("  USER_DATA[%d..%d] %s" % [k, mini(k + 4, arr.size() - 1), str(arr.slice(k, k + 5))])
		var texs: Variant = data.get("lightmap_textures")
		if texs is Array:
			for t in (texs as Array):
				var tl: TextureLayered = t
				if tl != null:
					print("  TEXTURE %s %dx%d layers %d format %d" % [tl.resource_path, tl.get_width(), tl.get_height(), tl.get_layers(), tl.get_format()])
	_exit(0)
	return true
