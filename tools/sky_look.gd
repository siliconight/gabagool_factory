extends SceneTree
## DIAL CHECK for the sky-shader A/B copies: does this copy's sky actually
## draw? One frame from a camera pitched 35 degrees up at a fixed spot,
## saved beside the package, with the mean luminance of its upper half
## printed. A copy whose shader failed to compile draws no sky and reads
## dark; a copy whose shader compiled draws the same sky the baseline does.
## Says what it measured and stops. Windowed, because a shader compiles on
## a GPU. Takes one argument after `--`: a label for the output file.

const W := 1280
const H := 720
const WATCHDOG_SEC := 180.0


func _initialize() -> void:
	_run()
	_watchdog()


func _watchdog() -> void:
	var t0: int = Time.get_ticks_msec()
	while true:
		await process_frame
		if Time.get_ticks_msec() - t0 > int(WATCHDOG_SEC * 1000.0):
			print("[look] WATCHDOG: quitting")
			_exit(2)
			return


func _run() -> void:
	var label: String = "x"
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() > 0:
		label = args[0]
	DisplayServer.window_set_size(Vector2i(W, H))
	var ps: PackedScene = load("res://mission.tscn")
	change_scene_to_packed(ps)
	await process_frame
	await process_frame
	var cam := Camera3D.new()
	cam.name = "SkyLookCam"
	current_scene.add_child(cam)
	cam.global_position = Vector3(0.5, 3.0, 0.6)
	cam.rotation_degrees = Vector3(35.0, 0.0, 0.0)
	cam.current = true
	# poll for a lit frame rather than trusting a fixed settle
	var lum: float = 0.0
	for i in range(240):
		await process_frame
		if i % 20 == 19:
			lum = _upper_lum()
			if lum > 0.01:
				break
	for i in range(30):
		await process_frame
	lum = _upper_lum()
	var img: Image = root.get_texture().get_image()
	var path: String = "res://_sky_look_%s.png" % label
	img.save_png(path)
	print("[look] %s: upper-half mean luminance %.4f, saved %s" % [label, lum, path])
	_exit(0)


func _upper_lum() -> float:
	var img: Image = root.get_texture().get_image()
	var s: float = 0.0
	var n: int = 0
	for x in range(0, W, 16):
		for y in range(0, H / 2, 16):
			var c: Color = img.get_pixel(x, y)
			s += 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b
			n += 1
	return s / float(n)


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())
