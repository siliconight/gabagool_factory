extends SceneTree
## Print every user a package's LightmapGIData names, one path a line, then the count.
##
##   godot --headless --path <package> -s <this file>
##
## Loads res://bake.lmbake with the cache ignored. The package ships no import cache, so the
## lightmap's texture may not load; the user list is the resource's own data and does not need
## it. Measures and prints; names no cause.


func _initialize() -> void:
	var data: LightmapGIData = ResourceLoader.load(
		"res://bake.lmbake", "", ResourceLoader.CACHE_MODE_IGNORE) as LightmapGIData
	if data == null:
		print("LIGHTMAP_USERS unreadable")
		quit(1)
		return
	var n: int = data.get_user_count()
	for i in range(n):
		print("USER %s" % String(data.get_user_path(i)))
	print("LIGHTMAP_USERS %d" % n)
	quit(0)
