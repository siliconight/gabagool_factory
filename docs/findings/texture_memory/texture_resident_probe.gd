extends SceneTree
## WHAT the texture memory is, not only how much (roadmap 238). `texture_mem_probe.gd` read one total;
## the census beside it inferred where it goes from the package's files, counting every image as resident
## -- the sky's 140 included -- and the lightmap as nothing (Pillow cannot open `bake.exr`, so it is a row
## of 0 x 0). SkyMint loads two skyboxes, the day's and the night's (`skymint.gd`, `_assign_textures`), so
## the inference and the code disagree; this measures which is right.
##
## Opens a window -- a headless run allocates no texture -- loads the package's scene and waits FRAMES
## frames, then takes the engine's own monitor at each of four states, waiting FRAMES between them:
##   loaded    the scene as shipped
##   no_lmap   every LightmapGI freed
##   no_sky    every WorldEnvironment's sky taken away as well (`environment.sky = null`) and every
##             SkyMint-like node freed
##   no_scene  the whole scene freed
##   no_patlas the window's positional shadow atlas set to 0 (`Viewport.positional_shadow_atlas_size`)
##   no_datlas the directional shadow atlas set to 256 (`RenderingServer.directional_shadow_atlas_set_size`)
## Each drop is what the thing released held, by the renderer's own accounting (compressed formats at
## their compressed size). What is left at `no_scene` is the engine's and the window's, not the level's;
## the two atlas steps ask how much of that the shadow maps a level's lights asked for are.
## `-- --empty` loads no scene at all and reads the monitor after FRAMES frames: the window's own floor.
## At `loaded` and at `no_scene` it also lists which of the package's image files the resource cache
## holds (`ResourceLoader.has_cached`), by top folder -- a cached texture is a loaded one -- and every
## LightmapGI's textures by size and layers. Prints what it measured and quits; it never stops on a
## dialog: a scene that does not load prints so and quits.
##
##     godot --path <imported package copy> -s res://texture_resident_probe.gd

const SCENE := "res://mission.tscn"
const FRAMES := 90
const IMAGE_EXTS := ["png", "webp", "jpg", "jpeg", "tga", "exr", "hdr", "ktx2"]

var _scene: Node = null
var _frames := 0
var _phase := 0
var _images: PackedStringArray = []


func _walk(dir_path: String) -> void:
	var d := DirAccess.open(dir_path)
	if d == null:
		return
	for f in d.get_files():
		var ext := f.get_extension().to_lower()
		if ext in IMAGE_EXTS:
			_images.append(dir_path.path_join(f))
	for sub in d.get_directories():
		if sub.begins_with("."):
			continue
		_walk(dir_path.path_join(sub))


func _mib(v: float) -> String:
	return "%.1f MiB" % (v / 1048576.0)


func _monitor(label: String) -> float:
	var tex := Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)
	var buf := Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED)
	var fmt := "[resident] %-9s texture %s, buffers %s"
	print(fmt % [label, _mib(tex), _mib(buf)])
	return tex


func _cached_by_folder(label: String) -> void:
	var counts := {}
	var held := 0
	for p in _images:
		if ResourceLoader.has_cached(p):
			held += 1
			var rel := p.trim_prefix("res://")
			var top := rel.get_slice("/", 0)
			if top == "runtime" and rel.get_slice_count("/") > 2:
				top = rel.get_slice("/", 0) + "/" + rel.get_slice("/", 1) + "/" + rel.get_slice("/", 2)
			counts[top] = int(counts.get(top, 0)) + 1
	var fmt := "[resident] %-9s %d of %d image files cached: %s"
	print(fmt % [label, held, _images.size(), str(counts)])


func _lightmaps() -> void:
	for n in _scene.find_children("*", "LightmapGI", true, false):
		var lm := n as LightmapGI
		if lm == null or lm.light_data == null:
			continue
		var texs: Array = lm.light_data.lightmap_textures
		for t in texs:
			var tl := t as TextureLayered
			if tl == null:
				continue
			var fmt := "[resident] lightmap  %s: %d x %d x %d layers, format %d, path %s"
			print(fmt % [lm.name, tl.get_width(), tl.get_height(), tl.get_layers(), tl.get_format(),
				tl.resource_path])


func _initialize() -> void:
	_walk("res://")
	var fmt := "[resident] window positional shadow atlas %d, directional shadow size %d (project setting)"
	print(fmt % [root.positional_shadow_atlas_size,
		int(ProjectSettings.get_setting("rendering/lights_and_shadows/directional_shadow/size", -1))])
	if "--empty" in OS.get_cmdline_user_args():
		_phase = 9
		print("[resident] --empty: no scene; waiting %d frames" % FRAMES)
		return
	var packed: PackedScene = load(SCENE)
	if packed == null:
		print("[resident] FAILED to load %s" % SCENE)
		quit(2)
		return
	_scene = packed.instantiate()
	root.add_child(_scene)
	print("[resident] scene %s; %d image files under res://; waiting %d frames a state" % [
		SCENE, _images.size(), FRAMES])


func _process(_delta: float) -> bool:
	_frames += 1
	if _frames < FRAMES:
		return false
	_frames = 0
	if _phase == 0:
		_monitor("loaded")
		_cached_by_folder("loaded")
		_lightmaps()
		for n in _scene.find_children("*", "LightmapGI", true, false):
			n.queue_free()
	elif _phase == 1:
		_monitor("no_lmap")
		for n in _scene.find_children("*", "WorldEnvironment", true, false):
			var we := n as WorldEnvironment
			if we != null and we.environment != null:
				we.environment.sky = null
		for n in _scene.find_children("*", "", true, false):
			if n.get_script() != null and String(n.get_script().resource_path).get_file() == "skymint.gd":
				n.queue_free()
	elif _phase == 2:
		_monitor("no_sky")
		_scene.queue_free()
		_scene = null
	elif _phase == 3:
		_monitor("no_scene")
		_cached_by_folder("no_scene")
		root.positional_shadow_atlas_size = 0
	elif _phase == 4:
		_monitor("no_patlas")
		RenderingServer.directional_shadow_atlas_set_size(256, true)
	elif _phase == 5:
		_monitor("no_datlas")
		quit(0)
		return true
	else:
		_monitor("empty")
		quit(0)
		return true
	_phase += 1
	return false
