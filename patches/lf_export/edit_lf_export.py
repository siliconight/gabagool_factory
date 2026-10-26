"""Level Factory 0.249.0 on a clone: export a level as a snapshot from the panel (the factory's roadmap 317, increment 7
of `docs/AUTHORING_LOOP.md`). Anchored; refuses on a miss.

    python edit_lf_export.py <clone>

Copies packages/service/exporting.py, tests/service/test_exporting.py and apps/godot/tests/test_level_export.gd from
`src/`; adds the `export_level` operation and the Level tab's Export.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("packages/service/exporting.py", "tests/service/test_exporting.py", "apps/godot/tests/test_level_export.gd"):
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


edit("packages/service/operations.py", [
    ('''def walk_level(arguments: dict, events) -> dict:''', '''def export_level(arguments: dict, events) -> dict:
    """Export the walked level as a snapshot (`packages.service.exporting.export`): arguments ``path`` (the design)
    and ``destination`` (a new or empty folder). Refuses when the current revision was not walked. Returns the
    snapshot's folder and its checklist -- complete, portable, baked, renderer, findings left."""
    _no_unknown(arguments, {"path", "destination"})
    from packages.service import exporting, layouts
    try:
        return exporting.export(_text(arguments, "path"), _text(arguments, "destination"), events,
                                Path(events.path).parent)
    except (layouts.LayoutError, ValueError) as exc:
        raise RequestError(getattr(exc, "code", "design_unusable"), str(exc)) from None


def walk_level(arguments: dict, events) -> dict:'''),
    ('''    "update_design": update_design,
}''', '''    "update_design": update_design,
    "export_level": export_level,
}'''),
])

edit("apps/godot/addons/gabagool_factory/level_panel.gd", [
    ('''var _save: Button
var _undo: Button
''', '''var _save: Button
var _undo: Button
var _export: Button
var _export_status: Label
var _checklist: Tree
var _export_dialog: FileDialog
## The last snapshot the factory exported ({} before one).
var export_result: Dictionary = {}
'''),
    ('''	_walk_status = Label.new()
	_walk_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_walk_status)
''', '''	_walk_status = Label.new()
	_walk_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_walk_status)

	# EXPORT (increment 7, roadmap 317): a snapshot of what was walked, into a new folder
	_export = Button.new()
	_export.text = "Export..."
	_export.tooltip_text = "Copies the level you walked into a new folder you choose, with a checklist. " \\
		+ "Later walks and builds never touch it."
	_export.pressed.connect(_pick_export_folder)
	add_child(_export)
	_export_status = Label.new()
	_export_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_export_status)
	_checklist = Tree.new()
	_checklist.columns = 3
	_checklist.hide_root = true
	_checklist.custom_minimum_size = Vector2(0, 100)
	add_child(_checklist)
	_export_dialog = FileDialog.new()
	_export_dialog.access = FileDialog.ACCESS_FILESYSTEM
	_export_dialog.file_mode = FileDialog.FILE_MODE_OPEN_DIR
	_export_dialog.title = "Choose a new, empty folder for the snapshot"
	_export_dialog.dir_selected.connect(export_level)
	add_child(_export_dialog)
'''),
    ('''## The executable and arguments that open a walk preview, or [] when no Godot is recorded.''',
     '''func _pick_export_folder() -> void:
	if design_path == "":
		_info.text = "Open or start a level first."
		return
	_export_dialog.popup_centered_ratio(0.6)


## Export the walked level as a snapshot into `destination` (`export_level`).
func export_level(destination: String) -> void:
	_export_status.text = "Exporting to %s..." % destination
	_call("export_level", {"path": design_path, "destination": destination}, show_export)


## Show an `export_level` answer: where the snapshot is and its checklist.
func show_export(data: Dictionary) -> void:
	export_result = data
	_checklist.clear()
	var root := _checklist.create_item()
	var problems := 0
	for row in data.get("checklist", []):
		var line: Dictionary = row
		var item := _checklist.create_item(root)
		var state: String = line.get("state", "unknown")
		item.set_text(0, state)
		item.set_custom_color(0, EXPORT_COLOURS.get(state, Color.WHITE))
		item.set_text(1, str(line.get("item", "")))
		item.set_text(2, str(line.get("detail", "")))
		if state != "ok":
			problems += 1
	var said := "Exported to %s." % str(data.get("snapshot", "?"))
	if problems > 0:
		said += " %d item(s) on the checklist are not ok: read them before you ship it." % problems
	_export_status.text = said


## The executable and arguments that open a walk preview, or [] when no Godot is recorded.'''),
    ('''const LAYOUT_COLOURS := {''', '''const EXPORT_COLOURS := {"ok": Color(0.45, 0.8, 0.45), "problem": Color(0.95, 0.35, 0.35),
	"unknown": Color(0.95, 0.75, 0.3)}
const LAYOUT_COLOURS := {'''),
])
