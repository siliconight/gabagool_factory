"""Edit a Level Factory clone for 0.261.0: the light bake asks the level's Lux (>= 0.80.0) to lend its static
fluorescent lamps their bake range before Bake is pressed, and gives it back before the save. Run from the clone's root.
Asserts every anchor once; refuses on a miss."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


edit("assets/godot/light_bake_plugin.gd", [
('''var _fill: Node = null
var _fill_count: int = -1
''',
'''var _fill: Node = null
var _fill_count: int = -1
## THE ROWS' BAKE RANGE (0.261.0). Lux >= 0.80.0 lets a static fluorescent
## lamp bake further than it claims live (`LuxLightLoader.stretch_bake_ranges`):
## a lamp's live range is the realtime claim it makes on every dynamic object,
## every player included, and its lightmap makes none. Lent after the scene
## opens and before Bake is pressed, given back before the save, beside the
## fill. `_lent_count` is -1 when the level's Lux has no such call.
var _lent: Array = []
var _lent_count: int = -1
'''),
('''## The level's Lux loader sits beside its LuxRoot's script, in a package
## (`res://runtime/lux/runtime/`) and in Lux's own repo alike. Its
## `add_bake_fills` lays the fill under `root` and returns the container.
func _lay_room_fill(root: Node) -> Node:
	if root == null:
		return null
	for n in root.get_tree().get_nodes_in_group(&"lux_root"):
		if n != root and not root.is_ancestor_of(n):
			continue
		var s: Script = n.get_script()
		if s == null:
			continue
		var path := s.resource_path.get_base_dir().path_join("lux_light_loader.gd")
		if not ResourceLoader.exists(path):
			continue
		var loader: Script = load(path)
		if loader == null or not loader.has_method("add_bake_fills"):
			return null
		var fill: Node = loader.call("add_bake_fills", root)
		_fill_count = fill.get_child_count() if fill != null else 0
		print("BAKE room fills: ", _fill_count)
		return fill
	return null
''',
'''## The level's Lux loader sits beside its LuxRoot's script, in a package
## (`res://runtime/lux/runtime/`) and in Lux's own repo alike; null when the
## scene has no LuxRoot under `root`.
func _lux_loader(root: Node) -> Script:
	if root == null:
		return null
	for n in root.get_tree().get_nodes_in_group(&"lux_root"):
		if n != root and not root.is_ancestor_of(n):
			continue
		var s: Script = n.get_script()
		if s == null:
			continue
		var path := s.resource_path.get_base_dir().path_join("lux_light_loader.gd")
		if not ResourceLoader.exists(path):
			continue
		return load(path)
	return null


## Its `add_bake_fills` lays the fill under `root` and returns the container.
func _lay_room_fill(root: Node) -> Node:
	var loader: Script = _lux_loader(root)
	if loader == null or not loader.has_method("add_bake_fills"):
		return null
	var fill: Node = loader.call("add_bake_fills", root)
	_fill_count = fill.get_child_count() if fill != null else 0
	print("BAKE room fills: ", _fill_count)
	return fill


## Its `stretch_bake_ranges` lends the static lamps their bake range and
## returns what to give back (0.261.0).
func _lend_bake_ranges(root: Node) -> void:
	var loader: Script = _lux_loader(root)
	if loader == null or not loader.has_method("stretch_bake_ranges"):
		return
	_lent = loader.call("stretch_bake_ranges", root)
	_lent_count = _lent.size()
	print("BAKE ranges lent: ", _lent_count)


func _give_back_bake_ranges() -> void:
	var loader: Script = _lux_loader(EditorInterface.get_edited_scene_root())
	if loader != null and loader.has_method("restore_bake_ranges"):
		loader.call("restore_bake_ranges", _lent)
	_lent = []
'''),
('''			_fill = _lay_room_fill(EditorInterface.get_edited_scene_root())
''',
'''			_fill = _lay_room_fill(EditorInterface.get_edited_scene_root())
			_lend_bake_ranges(EditorInterface.get_edited_scene_root())
'''),
('''			_free_room_fill()
			_busy = true
			EditorInterface.save_scene()''',
'''			_free_room_fill()
			_give_back_bake_ranges()
			_busy = true
			EditorInterface.save_scene()'''),
('''				"room_fills": _fill_count,
''',
'''				"room_fills": _fill_count,
				"bake_ranges_lent": _lent_count,
'''),
])

edit("packages/exporting/light_bake.py", [
('''        report["room_fills"] = (result or {}).get("room_fills")
''',
'''        report["room_fills"] = (result or {}).get("room_fills")
        # 0.261.0: the static lamps Lux lent a bake range, -1 when its Lux has none
        report["bake_ranges_lent"] = (result or {}).get("bake_ranges_lent")
'''),
('''               "no room floor (the level's Lux lays none)" if fills in (None, -1)
               else "%d room fill(s)" % fills,''',
'''               ("no room floor (the level's Lux lays none)" if fills in (None, -1)
                else "%d room fill(s)" % fills)
               + ("" if report["bake_ranges_lent"] in (None, -1)
                  else ", %d lamp(s) lent a bake range" % report["bake_ranges_lent"]),'''),
])

edit("tests/unit/test_light_bake.py", [
('''    free = src.find("_free_room_fill()\\n\\t\\t\\t_busy = true\\n\\t\\t\\tEditorInterface.save_scene()")
    assert '"add_bake_fills"' in src, "the plugin never asks Lux for the rooms' floor"
    assert 0 <= lay < press, "the floor must be laid before Bake is pressed"
    assert free > press, "the floor must be freed after the bake and before the save"
''',
'''    # by ORDER, not adjacency (0.261.0 gives the rows' range back between the
    # two): freed after Bake is pressed and before the scene is saved
    free = src.find("\\t\\t\\t_free_room_fill()\\n")
    save = src.find("EditorInterface.save_scene()")
    assert '"add_bake_fills"' in src, "the plugin never asks Lux for the rooms' floor"
    assert 0 <= lay < press, "the floor must be laid before Bake is pressed"
    assert press < free < save, "the floor must be freed after the bake and before the save"
'''),
('''    assert any("30 room fill(s)" in s for s in said), said
''',
'''    assert any("30 room fill(s)" in s for s in said), said


def test_the_bake_lends_the_rows_their_bake_range_and_gives_it_back_before_it_saves():
    """THE ROWS' BAKE RANGE (0.261.0). Lux >= 0.80.0 lets a static lamp bake
    further than it claims live (`stretch_bake_ranges`, `restore_bake_ranges`):
    lent before Bake is pressed, given back before the save, counted in the
    result. Read off the plugin's source, as the floor is."""
    src = LB.PLUGIN_SCRIPT.read_text(encoding="utf-8")
    lend = src.find("_lend_bake_ranges(EditorInterface.get_edited_scene_root())")
    press = src.find("b.pressed.emit()")
    back = src.find("\\t\\t\\t_give_back_bake_ranges()\\n")
    save = src.find("EditorInterface.save_scene()")
    assert '"stretch_bake_ranges"' in src and '"restore_bake_ranges"' in src
    assert 0 <= lend < press, "the range must be lent before Bake is pressed"
    assert press < back < save, "the range must be given back after the bake and before the save"
    assert '"bake_ranges_lent": _lent_count' in src, "the result must say how many lamps were lent one"


def test_a_bake_reports_the_lamps_lent_a_range(tmp_path, monkeypatch):
    """What the plugin counted reaches `light_bake.json` and the export log; a
    Lux with no such call (-1) says nothing about it."""
    for lent, line in ((50, "50 lamp(s) lent a bake range"), (-1, None)):
        pkg = _package(tmp_path / str(lent))
        monkeypatch.setattr(LB, "_import", lambda d, g: True)

        def fake_editor(cmd, timeout, log_path=None, lent=lent):
            work = Path(cmd[cmd.index("--path") + 1])
            (work / LB.RESULT).write_text(json.dumps({"ok": True, "users": 12, "room_fills": 30,
                                                      "bake_ranges_lent": lent}), encoding="utf-8")
            (work / "bake.tscn").write_text("[gd_scene format=3]\\n", encoding="utf-8")
            for f in ("bake.lmbake", "bake.exr", "bake.exr.import"):
                (work / f).write_text("x", encoding="utf-8")
            return 0, 3.0
        monkeypatch.setattr(LB, "_run", fake_editor)
        said = []
        r = LB.bake(pkg, "godot.exe", log=said.append)
        assert r["ok"] is True and r["bake_ranges_lent"] == lent, r
        assert json.loads((pkg / LB.REPORT).read_text(encoding="utf-8"))["bake_ranges_lent"] == lent
        if line:
            assert any(line in s for s in said), said
        else:
            assert not any("lent a bake range" in s for s in said), said
'''),
])
