"""Level Factory 0.236.0 drafts (argv: <drafts dir>, the folder holding assets/godot/scout/): the scout window focuses a
floor, tilts, carries a flick and turns itself when left alone. The walker, trying it: "the up and down isn't
working? also is there a way to prioritize the view to focus on where you are as you rotate it so there isn't
corners that just stay covered as you rotate it?" -- and asked for vertical tilt, a turn that keeps spinning after
the drag lets go, and a slow automatic turn. Anchored; refuses on a miss."""
import pathlib
import sys

D = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = D / rel
    t = p.read_text(encoding="utf-8")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_text(t, encoding="utf-8", newline="\n")


W = "assets/godot/scout/scout_window.gd"
edit(W, [
    ("""## While open it takes its own input: left/right (ui_left/ui_right) the building, up/down (ui_up/ui_down) the floors
## apart or together, a mouse drag turns it, ui_cancel closes it. A caller that wants its own controls turns that
## off with `handle_input = false` and calls `select`, `turn` and `set_spread`.""",
     """## While open it takes its own input: left/right (ui_left/ui_right) the building; up/down (ui_up/ui_down) the floor
## it focuses -- the floors above it step aside, the ones below dim, the view centres on it, so no corner of it stays
## covered as it turns (0.236.0) -- and past the top the whole building again; a mouse drag turns it and tilts it, a
## flick keeps it turning, and left alone it turns itself slowly; ui_cancel closes it. A caller that wants its own
## controls turns that off with `handle_input = false` and calls `select`, `focus`, `turn`, `tilt` and
## `set_spread`."""),
    ("""## Whether the window reads the keyboard and mouse itself while open.
@export var handle_input: bool = true
""",
     """## Whether the window reads the keyboard and mouse itself while open.
@export var handle_input: bool = true
## Whether, left alone, it turns itself slowly.
@export var auto_turn: bool = true
"""),
    ("""## How far apart the storeys stand when spread, metres.
const SPREAD_M := 6.0
""",
     """## How far apart the storeys stand when spread, metres.
const SPREAD_M := 6.0
## The slow turn when it is left alone, degrees a second, and how long alone first, seconds.
const AUTO_TURN_DPS := 10.0
const IDLE_S := 3.0
## How far the view tilts: from nearly overhead to nearly level, degrees above the horizon.
const PITCH_MIN := 12.0
const PITCH_MAX := 80.0
## How quickly a flick's turn dies away, per second.
const SPIN_DAMP := 2.5
## How much a floor under the focused one is dimmed.
const DIM := 0.4
"""),
    ("""uniform float pulse = 0.0;
void fragment() {
	ALBEDO = COLOR.rgb;""",
     """uniform float pulse = 0.0;
uniform float dim = 1.0;
void fragment() {
	ALBEDO = COLOR.rgb * dim;"""),
    ("""var _yaw: float = 35.0
var _spread: float = 1.0""",
     """var _yaw: float = 35.0
var _pitch: float = 36.0
var _spin: float = 0.0            # degrees a second, what a flick left behind
var _idle: float = 0.0            # seconds since the player last touched it
var _focus: int = -1              # the floor in focus, by order from the lowest; -1 the whole building
var _spread: float = 1.0"""),
    ("""var _body_mat: ShaderMaterial
var _point_mat: ShaderMaterial
""",
     """var _body_mat: ShaderMaterial
var _dim_mat: ShaderMaterial
var _point_mat: ShaderMaterial
"""),
    ("""func turn(degrees: float) -> void:
	_yaw = fmod(_yaw + degrees, 360.0)
	_aim()
""",
     """func turn(degrees: float) -> void:
	_yaw = fmod(_yaw + degrees, 360.0)
	_aim()


func tilt(degrees: float) -> void:
	\"\"\"Raise the view towards overhead (positive) or lower it towards level, within PITCH_MIN..PITCH_MAX.\"\"\"
	_pitch = clampf(_pitch + degrees, PITCH_MIN, PITCH_MAX)
	_aim()


func focus(floor_index: int) -> void:
	\"\"\"Focus one floor, by order from the lowest (0), -1 the whole building: the floors above it step aside, the
	ones below dim, the view centres on it.\"\"\"
	_focus = clampi(floor_index, -1, _floors.size() - 1)
	_place_floors()


func focused() -> int:
	return _focus
"""),
    ("""	_body_mat = _shader_mat(BODY_SHADER)
	_point_mat = _shader_mat(BODY_SHADER)""",
     """	_body_mat = _shader_mat(BODY_SHADER)
	_dim_mat = _shader_mat(BODY_SHADER)
	_dim_mat.set_shader_parameter("dim", DIM)
	_point_mat = _shader_mat(BODY_SHADER)"""),
    ("""	_floors.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return float(a["y"]) < float(b["y"]))
	if _points_override.has(id):""",
     """	_floors.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return float(a["y"]) < float(b["y"]))
	_focus = -1
	if _points_override.has(id):"""),
    ("""	_place_floors()
	_note.text = "%d FLOOR(S)  -  DRAG TO TURN  -  UP/DOWN FOR FLOORS" % _floors.size()
""",
     """	_place_floors()
"""),
    ("""func _place_floors() -> void:
	if _model == null or _floors.is_empty():
		return
	var box := AABB()
	for k in range(_floors.size()):
		var mi: MeshInstance3D = _floors[k]["node"]
		mi.position.y = float(_floors[k]["y"]) + k * SPREAD_M * _spread
		var b: AABB = mi.transform * mi.get_aabb()
		box = b if k == 0 else box.merge(b)
	_model.position = -box.get_center()
	_radius = box.size.length() * 0.5
	_aim()""",
     """func _place_floors() -> void:
	if _model == null or _floors.is_empty():
		return
	# FOCUS (0.236.0): the floors above the focused one step aside -- hidden, their points with them -- and the ones
	# below dim, so turning shows every side of the focused floor with nothing standing over it; the view frames it
	var box := AABB()
	var first: bool = true
	for k in range(_floors.size()):
		var mi: MeshInstance3D = _floors[k]["node"]
		mi.position.y = float(_floors[k]["y"]) + k * SPREAD_M * _spread
		mi.visible = _focus < 0 or k <= _focus
		mi.material_override = _dim_mat if (_focus >= 0 and k < _focus) else _body_mat
		if _focus >= 0 and k != _focus:
			continue
		var b: AABB = mi.transform * mi.get_aabb()
		box = b if first else box.merge(b)
		first = false
	_model.position = -box.get_center()
	_radius = maxf(box.size.length() * 0.5, 4.0)
	var where: String = "WHOLE BUILDING" if _focus < 0 else "FLOOR %d OF %d" % [_focus + 1, _floors.size()]
	_note.text = "%s  -  DRAG TO TURN AND TILT  -  UP/DOWN: FLOOR" % where
	_aim()"""),
    ("""	var r: float = deg_to_rad(_yaw)
	var el: float = deg_to_rad(36.0)
	var d: float = _radius / sin(deg_to_rad(_cam.fov * 0.5))""",
     """	var r: float = deg_to_rad(_yaw)
	var el: float = deg_to_rad(_pitch)
	var d: float = _radius / sin(deg_to_rad(_cam.fov * 0.5))"""),
    ("""func _unhandled_input(event: InputEvent) -> void:
	if not _open or not handle_input or _entries.is_empty():
		return
	if event.is_action_pressed("ui_cancel"):
		close()
	elif event.is_action_pressed("ui_right"):
		select(String(_entries[(_index + 1) % _entries.size()]["id"]))
	elif event.is_action_pressed("ui_left"):
		select(String(_entries[(_index - 1 + _entries.size()) % _entries.size()]["id"]))
	elif event.is_action_pressed("ui_up"):
		set_spread(_spread + 0.25)
	elif event.is_action_pressed("ui_down"):
		set_spread(_spread - 0.25)
	elif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		_dragging = (event as InputEventMouseButton).pressed
	elif event is InputEventMouseMotion and _dragging:
		turn((event as InputEventMouseMotion).relative.x * 0.4)
	else:
		return
	get_viewport().set_input_as_handled()""",
     """func _process(delta: float) -> void:
	if not _open or _cam == null:
		return
	_idle += delta
	if _dragging:
		return
	# a flick keeps turning and dies away; left alone, it turns itself slowly
	if absf(_spin) > 0.5:
		turn(_spin * delta)
		_spin *= exp(-SPIN_DAMP * delta)
	elif auto_turn and _idle > IDLE_S:
		turn(AUTO_TURN_DPS * delta)


func _unhandled_input(event: InputEvent) -> void:
	if not _open or not handle_input or _entries.is_empty():
		return
	var n: int = _floors.size()
	if event.is_action_pressed("ui_cancel"):
		close()
	elif event.is_action_pressed("ui_right"):
		select(String(_entries[(_index + 1) % _entries.size()]["id"]))
	elif event.is_action_pressed("ui_left"):
		select(String(_entries[(_index - 1 + _entries.size()) % _entries.size()]["id"]))
	elif event.is_action_pressed("ui_down"):
		# down through the building: the whole of it, then the top floor, then each one below
		focus(n - 1 if _focus < 0 else maxi(_focus - 1, 0))
	elif event.is_action_pressed("ui_up"):
		# up through it, and past the top floor the whole building again
		focus(-1 if (_focus < 0 or _focus >= n - 1) else _focus + 1)
	elif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		_dragging = (event as InputEventMouseButton).pressed
		if _dragging:
			_spin = 0.0
	elif event is InputEventMouseMotion and _dragging:
		var rel: Vector2 = (event as InputEventMouseMotion).relative
		turn(rel.x * 0.4)
		tilt(rel.y * 0.25)
		# what the turn would carry on at if let go now: this motion's degrees over a frame's time
		_spin = rel.x * 0.4 / maxf(get_process_delta_time(), 1.0 / 240.0)
	else:
		return
	_idle = 0.0
	get_viewport().set_input_as_handled()"""),
])

edit("assets/godot/scout/README.md", [
    ("""scout.turn(45.0)                               # degrees""",
     """scout.turn(45.0)                               # degrees
scout.tilt(-10.0)                              # towards level (+ towards overhead), degrees
scout.focus(1)                                 # one floor, by order from the lowest; -1 the whole building
scout.focused()                                # which"""),
    ("""While open it reads its own input -- left/right the building, up/down the floors, a mouse drag turns it, cancel
closes it. Set `handle_input = false` to drive it from the game's own controls.""",
     """While open it reads its own input -- left/right the building; up/down the floor in focus (the floors above it step
aside, the ones below dim, the view centres on it; past the top, the whole building); a mouse drag turns and tilts
it, a flick keeps it turning; left alone it turns itself slowly (`auto_turn`); cancel closes it. Set
`handle_input = false` to drive it from the game's own controls. The caller holds its own player while it is open:
the window takes its input events, not keys a player script polls."""),
])
print("drafts edited")
