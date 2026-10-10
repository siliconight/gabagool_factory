extends SceneTree
## Roadmap 220: which drawn thing IS the bar on the door sign -- found by hiding things and looking.
##
##   godot --path <walk project> --script <this file> -- EX,EY,EZ TX,TY,TZ BX,BY0,BY1,BZ OUT_DIR
##
## Windowed, GL Compatibility, the walked level itself (`_walk.tscn`). Waits out the level's
## warm-up, then stands a camera at eye E looking at T (Godot metres, Y up) and measures the bar:
## the strip of screen that the world segment from (BX, BY0, BZ) to (BX, BY1, BZ) projects to,
## 3 px either side of it, against the face 12 px to its left and right at the same rows -- mean
## Rec.709 luma of each, 0-255.
##
## It then hides, one at a time, every VisualInstance3D whose world AABB comes within 2 m of the
## bar, renders, measures the same strip, and shows it again. A hide that brings the strip to
## the face's level names the thing that draws the bar. A strip that never moves says the bar is
## drawn by something that is not one of those nodes.
##
## Saves `baseline.png` and one crop per hide that moved the strip by more than 10 into OUT_DIR,
## prints every measurement, and quits. It names no cause.

var _eye := Vector3.ZERO
var _target := Vector3.ZERO
var _b0 := Vector3.ZERO
var _b1 := Vector3.ZERO
var _out: String = ""
var _cam: Camera3D = null
var _frame: int = 0
var _phase: int = 0
var _cands: Array = []
var _idx: int = -1
var _wait: int = 0
var _base: Array = []


func _v3(s: String) -> Vector3:
	var p: PackedStringArray = s.split(",")
	return Vector3(float(p[0]), float(p[1]), float(p[2]))


func _initialize() -> void:
	var a: PackedStringArray = OS.get_cmdline_user_args()
	if a.size() < 4:
		print("SEEK usage: -- EX,EY,EZ TX,TY,TZ BX,BY0,BY1,BZ OUT_DIR")
		quit(2)
		return
	_eye = _v3(a[0])
	_target = _v3(a[1])
	var b: PackedStringArray = a[2].split(",")
	_b0 = Vector3(float(b[0]), float(b[1]), float(b[3]))
	_b1 = Vector3(float(b[0]), float(b[2]), float(b[3]))
	_out = a[3]
	DirAccess.make_dir_recursive_absolute(_out)
	var ps: PackedScene = load("res://_walk.tscn") as PackedScene
	if ps == null:
		print("SEEK no _walk.tscn")
		quit(2)
		return
	root.add_child(ps.instantiate())


## Mean luma of the columns [x0, x1) over rows [y0, y1) of `img`.
func _luma(img: Image, x0: int, x1: int, y0: int, y1: int) -> float:
	var s: float = 0.0
	var n: int = 0
	for y in range(maxi(y0, 0), mini(y1, img.get_height())):
		for x in range(maxi(x0, 0), mini(x1, img.get_width())):
			var c: Color = img.get_pixel(x, y)
			s += 255.0 * (0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b)
			n += 1
	return s / float(maxi(n, 1))


## [bar, face] lumas of the current frame.
func _measure(img: Image) -> Array:
	var p0: Vector2 = _cam.unproject_position(_b0)
	var p1: Vector2 = _cam.unproject_position(_b1)
	var cx: int = int(round((p0.x + p1.x) * 0.5))
	var ya: int = int(minf(p0.y, p1.y))
	var yb: int = int(maxf(p0.y, p1.y))
	var bar: float = _luma(img, cx - 3, cx + 4, ya, yb)
	var face: float = 0.5 * (_luma(img, cx - 15, cx - 9, ya, yb) + _luma(img, cx + 10, cx + 16, ya, yb))
	return [bar, face, cx, ya, yb]


func _process(_delta: float) -> bool:
	_frame += 1
	if _phase == 0:
		if _frame < 320:
			return false
		_cam = Camera3D.new()
		_cam.fov = 40.0
		root.add_child(_cam)
		_cam.global_position = _eye
		_cam.look_at(_target, Vector3.UP)
		_cam.make_current()
		var mid: Vector3 = (_b0 + _b1) * 0.5
		for n in root.find_children("*", "VisualInstance3D", true, false):
			var vi: VisualInstance3D = n as VisualInstance3D
			if vi == null or not vi.is_visible_in_tree() or vi is Light3D:
				continue
			var wb: AABB = vi.global_transform * vi.get_aabb()
			if wb.grow(2.0).has_point(mid):
				_cands.append(vi)
		print("SEEK %d candidates within 2 m of the bar" % _cands.size())
		_phase = 1
		_wait = 12
		return false
	if _wait > 0:
		_wait -= 1
		return false
	var img: Image = root.get_texture().get_image()
	var m: Array = _measure(img)
	if _idx < 0:
		_base = m
		img.save_png(_out.path_join("baseline.png"))
		print("SEEK baseline bar %.1f face %.1f at x %d rows %d-%d" % [m[0], m[1], m[2], m[3], m[4]])
	else:
		var vi: VisualInstance3D = _cands[_idx]
		vi.visible = true
		var moved: float = float(_base[0]) - float(m[0])
		print("SEEK hid %s (%s): bar %.1f face %.1f, the bar moved %.1f" % [
			str(vi.get_path()), vi.get_class(), m[0], m[1], moved])
		if absf(moved) > 10.0:
			var cx: int = int(m[2])
			var crop: Image = img.get_region(Rect2i(cx - 160, int(m[3]) - 90, 320, 180))
			crop.save_png(_out.path_join("hid_%d.png" % _idx))
	_idx += 1
	if _idx >= _cands.size():
		print("SEEK done")
		return true
	(_cands[_idx] as VisualInstance3D).visible = false
	_wait = 4
	return false
