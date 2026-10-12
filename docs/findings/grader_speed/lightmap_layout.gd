extends SceneTree
## Prints a baked lightmap's layout: for each user -- a lightmapped mesh, by node path and
## sub-instance -- the atlas slice it was given and its rectangle on that slice, in the slice's
## normalised coordinates. One `LM_USER` line a user and an `LM_USERS` total, so two bakes'
## layouts can be compared mesh by mesh (lightmap_compare.py --layout). Measures and prints; names
## no cause. Run in the package, headless:
##   godot --headless --path <package> -s <this file> -- res://bake.lmbake


func _init() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var data: LightmapGIData = load(args[0]) as LightmapGIData
	if data == null:
		print("LM_USERS unreadable ", args[0])
		quit()
		return
	var ud: Array = data.get("user_data")
	var n: int = 0
	var i: int = 0
	while i + 3 < ud.size():
		var r: Rect2 = ud[i + 1]
		print("LM_USER\t", str(ud[i]), "\t", ud[i + 3], "\t", ud[i + 2], "\t",
			r.position.x, "\t", r.position.y, "\t", r.size.x, "\t", r.size.y)
		n += 1
		i += 4
	print("LM_USERS ", n, " of user_data ", ud.size())
	quit()
