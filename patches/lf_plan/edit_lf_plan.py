"""Level Factory 0.250.0 on a clone: each layout's top-down plan, drawn from the build that made it, on the Level tab
(the factory's roadmap 314). Anchored; refuses on a miss.

    python edit_lf_plan.py <clone>

Copies packages/service/plan_image.py, tests/service/test_plan_image.py and apps/godot/tests/test_level_plan.gd from
`src/`; `generate` draws every layout's plan; the Level tab shows the selected layout's.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("packages/service/plan_image.py", "tests/service/test_plan_image.py", "apps/godot/tests/test_level_plan.gd"):
    dst = C / rel
    assert not dst.exists(), rel
    shutil.copyfile(HERE / "src" / rel, dst)
    print("wrote", rel)


def edit(rel, edits):
    p = C / rel
    t = p.read_bytes().decode("utf-8")
    assert "\r\n" not in t
    for old, new in edits:
        assert t.count(old) == 1, (rel, t.count(old), old[:80])
        t = t.replace(old, new)
    p.write_bytes(t.encode("utf-8"))
    print("edited", rel, len(edits))


edit("packages/service/layouts.py", [
    ('''        raise LayoutError("no_layouts", "no layouts came out of the build: %s (output in %s)" % (exc, log)) from None
    record = _write_json(''', '''        raise LayoutError("no_layouts", "no layouts came out of the build: %s (output in %s)" % (exc, log)) from None
    # each layout's plan, from its own build, kept with this revision's record (0.250.0, roadmap 314)
    from packages.service import plan_image
    plan_image.write_plans(ws / ".level_factory", mission, result["candidates"],
                           folder / "builds" / "plans" / ("revision_%d" % doc["revision"]))
    result["plan_key"] = plan_image.KEY
    record = _write_json('''),
])

edit("apps/godot/addons/gabagool_factory/level_panel.gd", [
    ('''var _layouts: Tree
''', '''var _layouts: Tree
var _plan: TextureRect
var _plan_note: Label
'''),
    ('''	_layouts.custom_minimum_size = Vector2(0, 110)
	add_child(_layouts)
''', '''	_layouts.custom_minimum_size = Vector2(0, 110)
	_layouts.item_selected.connect(_show_plan)
	add_child(_layouts)
	# each layout's top-down plan, drawn from its own build (0.250.0, roadmap 314)
	_plan = TextureRect.new()
	_plan.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_plan.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_plan.custom_minimum_size = Vector2(0, 200)
	add_child(_plan)
	_plan_note = Label.new()
	_plan_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_plan_note)
'''),
    ('''		item.set_metadata(0, row.get("candidate_id", ""))
''', '''		item.set_metadata(0, row.get("candidate_id", ""))
		item.set_metadata(1, row)
'''),
    ('''	_use.disabled = data.get("candidates", []).is_empty()
	_build_status.text = "%d layouts." % data.get("candidates", []).size()
''', '''	_use.disabled = data.get("candidates", []).is_empty()
	_build_status.text = "%d layouts." % data.get("candidates", []).size()
	_show_plan()


## Show the selected layout's plan: the SVG `generate_layouts` drew from that layout's own build, or why there is none.
func _show_plan() -> void:
	_plan.texture = null
	var item := _layouts.get_selected()
	if item == null:
		_plan_note.text = "Select a layout to see its plan."
		return
	var row: Dictionary = item.get_metadata(1)
	var path: String = str(row.get("plan", "")) if row.get("plan") != null else ""
	if path == "":
		_plan_note.text = "No plan for this layout: %s" % str(row.get("plan_problem", "none was drawn"))
		return
	var image := Image.new()
	var err := image.load_svg_from_string(FileAccess.get_file_as_string(path), 1.0)
	if err != OK:
		_plan_note.text = "The plan at %s cannot be shown (error %d)." % [path, err]
		return
	_plan.texture = ImageTexture.create_from_image(image)
	_plan_note.text = "Seed %s. %s" % [str(row.get("seed", "?")), str(layouts.get("plan_key", ""))]
'''),
])
