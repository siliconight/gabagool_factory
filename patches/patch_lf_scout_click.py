"""Level Factory 0.236.1 (the factory's roadmap 295): a building is clicked in the scout window's list -- in the
overlay by the mouse, on a game's own handheld through `click(screen_pos)`, the screen's pixels.

What this writes, every target pinned by its hash and refused on a mismatch, nothing written until every file has been
worked out: `assets/godot/scout/scout_window.gd`, `assets/godot/scout/README.md` and `tests/unit/test_scout_window.py`
(anchored hunks); VERSION; the CHANGELOG entry, prepended. Generated from a proven clone
(`patches/lf_scout_click/gen_lf_scout_click.py`), dry-run on a fresh clone to the clone's every byte, a second run
refused (`patches/lf_scout_click/dry_run_*.out.txt`).

    python patches/patch_lf_scout_click.py
    cd level_factory && python -m pytest -q
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
PINS = {'assets/godot/scout/scout_window.gd': '1e4991f46fd532aa', 'assets/godot/scout/README.md': 'cc1ab7a9db8d7e6a', 'tests/unit/test_scout_window.py': '3090e923a7f770d4'}
EDITS = {'assets/godot/scout/scout_window.gd': [('lines 98-99', 'var _overlay: CanvasLayer\nvar _screen: SubViewport\n', "var _overlay: CanvasLayer\nvar _shown: TextureRect           # the screen as the overlay shows it\nvar _rows: Array = []             # [{id, node}] each listed building's row; its rect is in the screen's own pixels\nvar _screen: SubViewport\n"), ('lines 183-184', '\t\t_show()\n\n', '\t\t_show()\n\n\nfunc click(screen_pos: Vector2) -> bool:\n\t"""A click at ``screen_pos``, in the screen\'s own pixels (0..screen_size): on a building\'s row, show it. For a\n\tgame whose handheld shows `get_screen_texture()` on a mesh -- turn the hit\'s UV into pixels (uv * screen_size)\n\tand pass it here. Returns whether the click landed on something."""\n\tfor r in _rows:\n\t\t# the row\'s own laid-out rect: inside the screen\'s viewport, global is the screen\'s pixels\n\t\tif is_instance_valid(r["node"]) and (r["node"] as Control).get_global_rect().has_point(screen_pos):\n\t\t\tselect(String(r["id"]))\n\t\t\treturn true\n\treturn false\n\n'), ('lines 343-348', '\tvar shown := TextureRect.new()\n\tshown.texture = _screen.get_texture()\n\tshown.set_anchors_preset(Control.PRESET_CENTER)\n\tshown.position = -Vector2(w, h) * 0.5\n\tshown.size = Vector2(w, h)\n\t_overlay.add_child(shown)\n', '\t_shown = TextureRect.new()\n\t_shown.texture = _screen.get_texture()\n\t_shown.set_anchors_preset(Control.PRESET_CENTER)\n\t_shown.position = -Vector2(w, h) * 0.5\n\t_shown.size = Vector2(w, h)\n\t_overlay.add_child(_shown)\n'), ('lines 356-357', '\t_list.add_child(_label("BUILDINGS", 15, INK_SOFT, false))\n\tfor j in range(_entries.size()):\n', '\t_list.add_child(_label("BUILDINGS", 15, INK_SOFT, false))\n\t_rows.clear()\n\tfor j in range(_entries.size()):\n'), ('lines 363-364', '\t\t_list.add_child(row)\n\tif _model != null:\n', '\t\t_list.add_child(row)\n\t\t_rows.append({"id": String(_entries[j]["id"]), "node": row})\n\tif _model != null:\n'), ('lines 480-481', '\nfunc _wheel(event: InputEvent, button: MouseButton) -> bool:\n', '\nfunc _to_screen(viewport_pos: Vector2) -> Vector2:\n\t"""A point of the game\'s viewport, as the overlay shows the screen, in the screen\'s own pixels."""\n\tvar r: Rect2 = _shown.get_global_rect()\n\treturn (viewport_pos - r.position) * Vector2(screen_size) / r.size\n\n\nfunc _wheel(event: InputEvent, button: MouseButton) -> bool:\n'), ('lines 502-503', '\t\tfocus(-1 if (_focus < 0 or _focus >= n - 1) else _focus + 1)\n\telif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:\n', '\t\tfocus(-1 if (_focus < 0 or _focus >= n - 1) else _focus + 1)\n\telif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT \\\n\t\t\tand (event as InputEventMouseButton).pressed and _overlay.visible \\\n\t\t\tand click(_to_screen((event as InputEventMouseButton).position)):\n\t\tpass                         # a row clicked in the overlay: it shows that building, and no drag starts\n\telif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:\n')], 'assets/godot/scout/README.md': [('lines 26-27', '])\nscout.close()                                  # stop drawing; costs nothing until opened again\n', "])\nscout.click(uv * Vector2(scout.screen_size))   # a click on the game's handheld, in the screen's pixels:\n                                               #   on a building's row it shows it (returns whether it hit)\nscout.close()                                  # stop drawing; costs nothing until opened again\n"), ('lines 33-33', 'While open it reads its own input -- left/right the building; up/down the floor in focus (the floors above it step\n', 'While open it reads its own input -- a click on a building in the list (in the overlay; on a handheld, pass the\nclick in with `click`), left/right the building; up/down the floor in focus (the floors above it step\n')], 'tests/unit/test_scout_window.py': [('lines 18-18', '        "set_spread", "tilt", "focus", "focused")\n', '        "set_spread", "tilt", "focus", "focused", "click")\n'), ('lines 63-64', '\ndef test_up_and_down_focus_a_floor_and_a_drag_turns_and_tilts():\n', '\ndef test_a_click_on_a_buildings_row_shows_it():\n    """0.236.1, the walker: "(also clicking on the buttons in the screen should change the buildings)". The screen is\n    drawn off-screen and shown as a texture, so a click reaches it only by being mapped: `click` takes the screen\'s\n    own pixels and asks each row for its laid-out rect -- never a layout guessed from spacing -- and the overlay maps\n    the mouse to those pixels; a click on a row selects and starts no drag."""\n    gd = (SW.SOURCE / "scout_window.gd").read_text(encoding="utf-8")\n    body = gd[gd.index("func click("):gd.index("func turn(")]\n    assert "get_global_rect().has_point(screen_pos)" in body and "select(" in body\n    keys = gd[gd.index("func _unhandled_input"):]\n    assert "click(_to_screen(" in keys and keys.index("click(_to_screen(") < keys.index("_dragging = ")\n    to_screen = gd[gd.index("func _to_screen("):gd.index("func _wheel(")]\n    assert "_shown.get_global_rect()" in to_screen and "screen_size" in to_screen\n\n\ndef test_up_and_down_focus_a_floor_and_a_drag_turns_and_tilts():\n')]}
NEW_FILES = {}
CHANGELOG = '## [0.236.1] - a building is clicked in the scout window\'s list\n\n**The factory\'s roadmap 295.** The walker: "(also clicking on the buttons in the screen should change the\nbuildings)".\n\n### Added\n- **`click(screen_pos)`**: a click in the screen\'s own pixels; on a building\'s row it shows that building, and it\n  says whether it hit. The screen is drawn off-screen and shown as a texture -- over the game, or on the game\'s own\n  handheld -- so a click never reaches its controls by itself: a game whose handheld shows `get_screen_texture()` on\n  a mesh turns the hit\'s UV into pixels and passes them here. Each row is asked for its own laid-out rect, never a\n  layout guessed from the list\'s spacing. In the overlay the window maps the mouse itself, and a click on a row starts\n  no drag. Driven both ways (`patches/lf_scout_click/drive_click.gd`): `click` on the office\'s row selects it and on\n  empty screen hits nothing; a mouse press on the overlay\'s pharmacy row selects it, no drag begun.\n\n### Tests\n- `test_scout_window.py`: the seam carries `click`; it reads each row\'s laid-out rect and selects; the overlay maps\n  the mouse before any drag begins. On 0.236.0 the seam test fails on behaviour (no `click`), the click test on the\n  new name it reads.\n\n'
OLD_VERSION, NEW_VERSION = '0.236.0', '0.236.1'


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (LF / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: level_factory/%s has mixed line endings (%d CRLF of %d); nothing written"
                         % (name, crlf, lf))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text.encode("utf-8")) != PINS[name]:
        raise SystemExit("REFUSED: level_factory/%s is %s, not the %s this patch was written against; nothing "
                         "written" % (name, _sha(text.encode("utf-8")), PINS[name]))
    return text, crlf > 0


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: level_factory/%s: the anchor at %s is there %d times; nothing written"
                                 % (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (LF / name).exists():
            raise SystemExit("REFUSED: level_factory/%s exists already; nothing written" % name)
    v = LF / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %r, not %s; nothing written" % (v.read_text(), OLD_VERSION))
    cl = LF / "CHANGELOG.md"
    craw = cl.read_bytes()
    if b"\r\n" in craw or not craw.startswith(b"## [" + OLD_VERSION.encode() + b"]"):
        raise SystemExit("REFUSED: CHANGELOG.md is not LF opening on %s; nothing written" % OLD_VERSION)
    for name, text in out.items():
        (LF / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (LF / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes(CHANGELOG.encode("utf-8") + craw)
    print("Level Factory %s applied: %d files edited, %d written, VERSION, CHANGELOG. Now, in level_factory/: the "
          "suite" % (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
