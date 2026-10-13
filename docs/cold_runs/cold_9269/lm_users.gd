extends SceneTree
## Writes a baked LightmapGIData's users one a line -- the node path, the sub-instance, the rect the
## atlas gave it (`uv_scale`: x y w h) and its slice -- so two bakes of one level can be compared:
## did the atlas put the same mesh in the same place? `lm_users.py` compares two such dumps.
##
## The data's own textures are not loaded (a .lmbake names its .exr by res:// path, and this runs in
## an empty scratch project): missing dependencies are allowed, and only `user_data` is read.
##
##   godot --headless --path <empty scratch project> -s <this> -- <bake.lmbake> <out.txt>


func _init() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 2:
		printerr("usage: -- <bake.lmbake> <out.txt>")
		quit(2)
		return
	ResourceLoader.set_abort_on_missing_resources(false)
	var data := ResourceLoader.load(args[0], "", ResourceLoader.CACHE_MODE_IGNORE) as LightmapGIData
	if data == null:
		printerr("not a LightmapGIData: " + args[0])
		quit(1)
		return
	var raw: Variant = data.get("user_data")
	if typeof(raw) != TYPE_ARRAY:
		printerr("user_data is not an Array here (type %d): nothing to dump" % typeof(raw))
		quit(1)
		return
	var users: Array = raw
	if users.size() % 4 != 0:
		printerr("user_data holds %d values, not four a user" % users.size())
		quit(1)
		return
	var f := FileAccess.open(args[1], FileAccess.WRITE)
	for i in range(0, users.size(), 4):
		var rect: Rect2 = users[i + 1]
		var line := "%s\t%d\t%.6f %.6f %.6f %.6f\t%d" % [str(users[i]), int(users[i + 3]), rect.position.x, rect.position.y, rect.size.x, rect.size.y, int(users[i + 2])]
		f.store_line(line)
	f.close()
	print("users: %d -> %s" % [users.size() / 4, args[1]])
	quit(0)
