"""Level Factory 0.236.0, applied to a CLONE (<repo>) from the drafts (<drafts>, edited by edit_window_focus.py): the
scout window focuses a floor, tilts, carries a flick and turns itself alone; the walk copy's F6 caller holds the
player while it is open. Anchored; refuses on a miss; keeps line endings."""
import pathlib
import shutil
import sys

R, D = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


for rel in ("assets/godot/scout/scout_window.gd", "assets/godot/scout/README.md"):
    assert (R / rel).is_file(), rel
    shutil.copyfile(D / rel, R / rel)

edit("assets/godot/debug_overlay.gd", [
    ("""func _toggle_scout() -> void:
	if not ResourceLoader.exists("res://scout/scout_window.gd"):
		return
	if _scout == null:
		_scout = (load("res://scout/scout_window.gd") as GDScript).new()
		add_child(_scout)
	if _scout.call("is_open"):
		_scout.call("close")
		Input.mouse_mode = _scout_mouse
	else:
		_scout_mouse = Input.mouse_mode
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		_scout.call("open", true)


var _scout_mouse: int = Input.MOUSE_MODE_VISIBLE
""",
     """func _toggle_scout() -> void:
	if not ResourceLoader.exists("res://scout/scout_window.gd"):
		return
	if _scout == null:
		_scout = (load("res://scout/scout_window.gd") as GDScript).new()
		add_child(_scout)
		# the window closes itself on cancel too: give the player back whichever way it closes
		_scout.connect("closed", _scout_closed)
	if _scout.call("is_open"):
		_scout.call("close")
	else:
		_scout_mouse = Input.mouse_mode
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		_hold_player(true)
		_scout.call("open", true)


# THE PLAYER IS HELD WHILE IT IS OPEN (0.236.0). The walker, trying it: up and down did nothing -- the walk player
# polls the arrow keys for itself, and recaptures the mouse on any click, so it walked and grabbed the drag while the
# window had them. A gameplay layer holds its player while the handheld is up; so does this stand-in.
var _scout_mouse: int = Input.MOUSE_MODE_VISIBLE
var _held: Node


func _hold_player(hold: bool) -> void:
	if hold:
		_held = _find_player(get_tree().current_scene)
		if _held != null:
			_held.process_mode = Node.PROCESS_MODE_DISABLED
	elif _held != null and is_instance_valid(_held):
		_held.process_mode = Node.PROCESS_MODE_INHERIT
		_held = null


func _find_player(n: Node) -> Node:
	if n == null:
		return null
	if n is CharacterBody3D:
		return n
	for c in n.get_children():
		var hit: Node = _find_player(c)
		if hit != null:
			return hit
	return null


func _scout_closed() -> void:
	_hold_player(false)
	Input.mouse_mode = _scout_mouse
"""),
])

edit("tests/unit/test_scout_window.py", [
    ("""SEAM = ("open", "close", "is_open", "buildings", "get_screen_texture", "select", "set_points", "turn",
        "set_spread")""",
     """SEAM = ("open", "close", "is_open", "buildings", "get_screen_texture", "select", "set_points", "turn",
        "set_spread", "tilt", "focus", "focused")"""),
    ("""    ov = (LF / "assets" / "godot" / "debug_overlay.gd").read_text(encoding="utf-8")
    assert "KEY_F6" in ov and 'res://scout/scout_window.gd' in ov and '"open", true' in ov
    assert "OS.is_debug_build()" in ov""",
     """    ov = (LF / "assets" / "godot" / "debug_overlay.gd").read_text(encoding="utf-8")
    assert "KEY_F6" in ov and 'res://scout/scout_window.gd' in ov and '"open", true' in ov
    assert "OS.is_debug_build()" in ov
    # 0.236.0: it holds the player while the window is open, and gives it back on the window's own close
    assert "PROCESS_MODE_DISABLED" in ov and 'connect("closed"' in ov


def test_up_and_down_focus_a_floor_and_a_drag_turns_and_tilts():
    \"\"\"0.236.0, the walker: "the up and down isn't working? also is there a way to prioritize the view to focus on
    where you are as you rotate it so there isn't corners that just stay covered". Up and down step the focus through
    the floors, the floors above it hidden and the ones below dimmed; a drag turns and tilts it and leaves a spin; it
    turns itself when left alone.\"\"\"
    gd = (SW.SOURCE / "scout_window.gd").read_text(encoding="utf-8")
    keys = gd[gd.index("func _unhandled_input"):]
    assert 'is_action_pressed("ui_down")' in keys and 'is_action_pressed("ui_up")' in keys
    assert "focus(" in keys[keys.index('"ui_down"'):] and "set_spread" not in keys
    assert "mi.visible = _focus < 0 or k <= _focus" in gd and "_dim_mat if (_focus >= 0 and k < _focus)" in gd
    assert "tilt(rel.y" in keys and "_spin = " in keys
    assert "auto_turn and _idle > IDLE_S" in gd"""),
])

v = R / "VERSION"
assert v.read_bytes() == b"0.235.0", v.read_bytes()
v.write_bytes(b"0.236.0")
print("edited", R)
