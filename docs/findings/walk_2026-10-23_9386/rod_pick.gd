extends SceneTree
## Finding 4, by pixels rather than bounds: draw the walker's view of the office stair from their eye, then hide each
## visible MeshInstance3D near the eye in turn and measure how much the rod's band of the frame changes. The mesh whose
## hiding moves the band most is what draws the rod. Godot world metres, Y up. Windowed (headless draws nothing);
## measures, saves the frame, prints, and quits itself. Measurements only.
##
## The pose, from the walker's screenshot overlay (`04_rod_over_stair.webp`): eye (54.6, 2.2, 1.6), the centre ray
## hitting `slab_col_2` 13.07 m off at y 6.90, so pitched up asin(4.7 / 13.07); facing -Z, up the flight. The camera is
## the walk player's: no FOV set, so Godot's 75 degrees vertical. The rod's band is where the screenshot shows it,
## rows 0.40 to 0.45 of the height and columns 0.40 to 0.66 of the width.

const EYE := Vector3(54.6, 2.2, 1.6)
const REACH := 10.0
const BAND := Rect2(0.40, 0.40, 0.26, 0.05)
const W := 1600
const H := 900


func _initialize() -> void:
	root.size = Vector2i(W, H)
	var ps: PackedScene = load("res://_walk.tscn")
	var level := ps.instantiate()
	root.add_child(level)
	_run.call_deferred()


func _band_mean(img: Image) -> PackedFloat32Array:
	var out := PackedFloat32Array()
	var x0 := int(BAND.position.x * img.get_width())
	var x1 := int((BAND.position.x + BAND.size.x) * img.get_width())
	var y0 := int(BAND.position.y * img.get_height())
	var y1 := int((BAND.position.y + BAND.size.y) * img.get_height())
	for y in range(y0, y1):
		for x in range(x0, x1, 2):
			var c: Color = img.get_pixel(x, y)
			out.append(c.r + c.g + c.b)
	return out


func _diff(a: PackedFloat32Array, b: PackedFloat32Array) -> float:
	var s := 0.0
	for i in range(mini(a.size(), b.size())):
		s += absf(a[i] - b[i])
	return s / maxf(1.0, float(a.size()))


func _frame() -> Image:
	for i in 3:
		await RenderingServer.frame_post_draw
	return root.get_texture().get_image()


func _run() -> void:
	# the player's own camera off; ours at the walker's eye
	var cam := Camera3D.new()
	cam.fov = 75.0
	root.add_child(cam)
	var pitch := asin(4.7 / 13.07)
	cam.global_position = EYE
	cam.look_at(EYE + Vector3(0.0, sin(pitch), -cos(pitch)), Vector3.UP)
	cam.make_current()
	# THE FIRST RUN SCORED AGAINST A BLACK FRAME (kept in the README): 30 frames
	# had not drawn the level, every hidden mesh "moved the band" by the same
	# 0.34 and the leader meant nothing. So: warm up longer, and REFUSE to score
	# unless the first frame has a picture in it.
	for i in 240:
		await process_frame
	var base_img: Image = await _frame()
	var lum := 0.0
	var px := 0
	for y in range(0, base_img.get_height(), 8):
		for x in range(0, base_img.get_width(), 8):
			var c: Color = base_img.get_pixel(x, y)
			lum += (c.r + c.g + c.b) / 3.0
			px += 1
	lum /= maxf(1.0, float(px))
	print("BASE mean luminance %.4f (0..1) at %dx%d" % [lum, base_img.get_width(), base_img.get_height()])
	if lum < 0.02:
		print("REFUSED: the first frame is black; nothing would be measured")
		quit(2)
		await process_frame
		await process_frame
		OS.kill(OS.get_process_id())
		return
	base_img.save_png("user://rod_pick_base.png")
	print("FRAME saved %s" % ProjectSettings.globalize_path("user://rod_pick_base.png"))
	var base := _band_mean(base_img)
	var again: Image = await _frame()
	var noise := _diff(base, _band_mean(again))
	print("NOISE band diff with nothing hidden: %.5f" % noise)
	var scores: Array = []
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if not mi.is_visible_in_tree():
			continue
		var bb: AABB = mi.global_transform * mi.get_aabb()
		if bb.grow(REACH).has_point(EYE) == false:
			continue
		mi.visible = false
		var img: Image = await _frame()
		mi.visible = true
		# against a frame drawn just before, so a slow drift (the sky's cycle) is not scored
		var ref: Image = await _frame()
		scores.append([_diff(_band_mean(ref), _band_mean(img)), str(mi.get_path()), bb])
	scores.sort_custom(func(a, b): return a[0] > b[0])
	for s in scores.slice(0, 12):
		print("HIDE %.5f %s aabb %s" % [s[0], s[1], s[2]])
	print("CANDIDATES %d" % scores.size())
	quit(0)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())
