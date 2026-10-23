"""Level Factory 0.236.1, applied to a CLONE (<repo>) of 0.236.0 from the drafts (<drafts>, edited by
edit_window_click.py): a building's row in the scout window's list is clicked to show it -- in the overlay by the
mouse, on a game's handheld through `click(screen_pos)`. Anchored; refuses on a miss; keeps line endings."""
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

edit("tests/unit/test_scout_window.py", [
    ("""        "set_spread", "tilt", "focus", "focused")""",
     """        "set_spread", "tilt", "focus", "focused", "click")"""),
    ("""def test_up_and_down_focus_a_floor_and_a_drag_turns_and_tilts():""",
     """def test_a_click_on_a_buildings_row_shows_it():
    \"\"\"0.236.1, the walker: "(also clicking on the buttons in the screen should change the buildings)". The screen is
    drawn off-screen and shown as a texture, so a click reaches it only by being mapped: `click` takes the screen's
    own pixels and asks each row for its laid-out rect -- never a layout guessed from spacing -- and the overlay maps
    the mouse to those pixels; a click on a row selects and starts no drag.\"\"\"
    gd = (SW.SOURCE / "scout_window.gd").read_text(encoding="utf-8")
    body = gd[gd.index("func click("):gd.index("func turn(")]
    assert "get_global_rect().has_point(screen_pos)" in body and "select(" in body
    keys = gd[gd.index("func _unhandled_input"):]
    assert "click(_to_screen(" in keys and keys.index("click(_to_screen(") < keys.index("_dragging = ")
    to_screen = gd[gd.index("func _to_screen("):gd.index("func _wheel(")]
    assert "_shown.get_global_rect()" in to_screen and "screen_size" in to_screen


def test_up_and_down_focus_a_floor_and_a_drag_turns_and_tilts():"""),
])

v = R / "VERSION"
assert v.read_bytes() == b"0.236.0", v.read_bytes()
v.write_bytes(b"0.236.1")
print("edited", R)
