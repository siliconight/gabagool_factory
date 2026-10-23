"""Level Factory 0.236.1 drafts (argv: <drafts dir>): a building in the screen's list is clicked to show it. The
walker: "(also clicking on the buttons in the screen should change the buildings)". The screen is drawn off-screen and
shown as a texture -- over the game, or on the game's own handheld -- so a click never reaches its controls by itself:
`click(screen_pos)` takes a point in the screen's own pixels, and the overlay maps the mouse to it. Anchored."""
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


edit("assets/godot/scout/scout_window.gd", [
    ("""var _overlay: CanvasLayer
""", """var _overlay: CanvasLayer
var _shown: TextureRect           # the screen as the overlay shows it
var _rows: Array = []             # [{id, node}] each listed building's row; its rect is in the screen's own pixels
"""),
    ("""func turn(degrees: float) -> void:""",
     """func click(screen_pos: Vector2) -> bool:
	\"\"\"A click at ``screen_pos``, in the screen's own pixels (0..screen_size): on a building's row, show it. For a
	game whose handheld shows `get_screen_texture()` on a mesh -- turn the hit's UV into pixels (uv * screen_size)
	and pass it here. Returns whether the click landed on something.\"\"\"
	for r in _rows:
		# the row's own laid-out rect: inside the screen's viewport, global is the screen's pixels
		if is_instance_valid(r["node"]) and (r["node"] as Control).get_global_rect().has_point(screen_pos):
			select(String(r["id"]))
			return true
	return false


func turn(degrees: float) -> void:"""),
    ("""	var shown := TextureRect.new()
	shown.texture = _screen.get_texture()
	shown.set_anchors_preset(Control.PRESET_CENTER)
	shown.position = -Vector2(w, h) * 0.5
	shown.size = Vector2(w, h)
	_overlay.add_child(shown)""",
     """	_shown = TextureRect.new()
	_shown.texture = _screen.get_texture()
	_shown.set_anchors_preset(Control.PRESET_CENTER)
	_shown.position = -Vector2(w, h) * 0.5
	_shown.size = Vector2(w, h)
	_overlay.add_child(_shown)"""),
    ("""	_list.add_child(_label("BUILDINGS", 15, INK_SOFT, false))
	for j in range(_entries.size()):""",
     """	_list.add_child(_label("BUILDINGS", 15, INK_SOFT, false))
	_rows.clear()
	for j in range(_entries.size()):"""),
    ("""		row.add_child(_label("  %s %s" % [">" if sel else " ", shown_name], 15, LCD_GLOW if sel else INK, false))
		_list.add_child(row)""",
     """		row.add_child(_label("  %s %s" % [">" if sel else " ", shown_name], 15, LCD_GLOW if sel else INK, false))
		_list.add_child(row)
		_rows.append({"id": String(_entries[j]["id"]), "node": row})"""),
    ("""	elif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		_dragging = (event as InputEventMouseButton).pressed
		if _dragging:
			_spin = 0.0""",
     """	elif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT \\
			and (event as InputEventMouseButton).pressed and _overlay.visible \\
			and click(_to_screen((event as InputEventMouseButton).position)):
		pass                         # a row clicked in the overlay: it shows that building, and no drag starts
	elif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		_dragging = (event as InputEventMouseButton).pressed
		if _dragging:
			_spin = 0.0"""),
    ("""func _wheel(event: InputEvent, button: MouseButton) -> bool:""",
     """func _to_screen(viewport_pos: Vector2) -> Vector2:
	\"\"\"A point of the game's viewport, as the overlay shows the screen, in the screen's own pixels.\"\"\"
	var r: Rect2 = _shown.get_global_rect()
	return (viewport_pos - r.position) * Vector2(screen_size) / r.size


func _wheel(event: InputEvent, button: MouseButton) -> bool:"""),
])

edit("assets/godot/scout/README.md", [
    ("""scout.close()                                  # stop drawing; costs nothing until opened again""",
     """scout.click(uv * Vector2(scout.screen_size))   # a click on the game's handheld, in the screen's pixels:
                                               #   on a building's row it shows it (returns whether it hit)
scout.close()                                  # stop drawing; costs nothing until opened again"""),
    ("""While open it reads its own input -- left/right the building;""",
     """While open it reads its own input -- a click on a building in the list (in the overlay; on a handheld, pass the
click in with `click`), left/right the building;"""),
])
print("drafts edited")
