"""Level Factory 0.246.0 on a clone, the panel's half: Generate layouts, a progress bar, Stop, the layouts with
their states, the recommendation, and Use this layout on the Level tab; `cancel()` on the client. Run after
`edit_lf_layouts.py`. Anchored; refuses on a miss.

    python edit_lf_layouts_panel.py <clone>
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
ADDON = C / "apps" / "godot" / "addons" / "gabagool_factory"


def edit(path, edits):
    t = path.read_bytes().decode("utf-8")
    assert "\r\n" not in t
    for old, new in edits:
        assert t.count(old) == 1, (path.name, t.count(old), old[:80])
        t = t.replace(old, new)
    path.write_bytes(t.encode("utf-8"))
    print("edited", path.name, len(edits))


edit(ADDON / "service_client.gd", [
    ('''## Is an operation in flight?
func is_running() -> bool:
	return _running
''', '''## Is an operation in flight?
func is_running() -> bool:
	return _running


## Ask the running operation to stop: protocol v1's `cancel` file in its run directory. The operation ends its
## processes and finishes with a `cancelled` error result; `finished` still fires once. Returns false when nothing
## is running.
func cancel() -> bool:
	if not _running or run_dir == "":
		return false
	var f := FileAccess.open(run_dir.path_join("cancel"), FileAccess.WRITE)
	if f == null:
		return false
	f.store_string("cancelled from the panel")
	f.close()
	return true
'''),
])

edit(ADDON / "level_panel.gd", [
    ('''var _queue: Array = []
var _pending: Callable
''', '''var _queue: Array = []
var _pending: Callable
## The last layouts the factory returned for this design ({} before a build).
var layouts: Dictionary = {}
var _generate: Button
var _stop: Button
var _progress: ProgressBar
var _build_status: Label
var _recommendation: Label
var _layouts: Tree
var _use: Button
'''),
    ('''	client.finished.connect(_on_finished)
	_build()
''', '''	client.finished.connect(_on_finished)
	client.event_received.connect(_on_event)
	_build()
'''),
    ('''	_form.set_column_title(2, "What it does")
	_form.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_form)
''', '''	_form.set_column_title(2, "What it does")
	_form.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_form)

	# LAYOUTS (increment 4, roadmap 314): generate, watch, stop, choose
	var build_row := HBoxContainer.new()
	_generate = Button.new()
	_generate.text = "Generate layouts"
	_generate.pressed.connect(generate_layouts)
	build_row.add_child(_generate)
	_stop = Button.new()
	_stop.text = "Stop"
	_stop.disabled = true
	_stop.pressed.connect(stop)
	build_row.add_child(_stop)
	_progress = ProgressBar.new()
	_progress.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_progress.max_value = 1.0
	_progress.step = 0.001
	build_row.add_child(_progress)
	add_child(build_row)
	_build_status = Label.new()
	_build_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_build_status)
	_recommendation = Label.new()
	_recommendation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_recommendation)
	_layouts = Tree.new()
	_layouts.columns = 3
	_layouts.hide_root = true
	_layouts.column_titles_visible = true
	_layouts.set_column_title(0, "Layout")
	_layouts.set_column_title(1, "State")
	_layouts.set_column_title(2, "Why")
	_layouts.custom_minimum_size = Vector2(0, 110)
	add_child(_layouts)
	_use = Button.new()
	_use.text = "Use this layout"
	_use.disabled = true
	_use.pressed.connect(use_layout)
	add_child(_use)
'''),
    ('''func _on_finished(result: Dictionary) -> void:
	var done := _pending
	_pending = Callable()
''', '''## Generate the open design's layouts (`generate_layouts`); progress shows as it runs, Stop ends it.
func generate_layouts() -> void:
	if design_path == "":
		_info.text = "Open or start a level first."
		return
	layouts = {}
	_layouts.clear()
	_recommendation.text = ""
	_progress.value = 0.0
	_generate.disabled = true
	_stop.disabled = false
	_use.disabled = true
	_build_status.text = "Generating layouts. This runs the whole graybox pipeline and takes several minutes."
	_call("generate_layouts", {"path": design_path}, show_layouts)


## Ask the running build to stop.
func stop() -> void:
	if client.cancel():
		_build_status.text = "Stopping..."


## Record the selected layout as the designer's choice (`choose_layout`).
func use_layout() -> void:
	var item := _layouts.get_selected()
	if item == null:
		_build_status.text = "Select a layout first."
		return
	_call("choose_layout", {"path": design_path, "candidate": item.get_metadata(0)}, _on_chosen)


## Fill the layouts list from a `generate_layouts` answer.
func show_layouts(data: Dictionary) -> void:
	layouts = data
	_layouts.clear()
	var root := _layouts.create_item()
	var recommended: String = data.get("recommended", "")
	for c in data.get("candidates", []):
		var row: Dictionary = c
		var item := _layouts.create_item(root)
		item.set_text(0, "Seed %s" % str(row.get("seed", "?")))
		item.set_metadata(0, row.get("candidate_id", ""))
		var state: String = row.get("state", "?")
		item.set_text(1, state)
		item.set_custom_color(1, LAYOUT_COLOURS.get(state, Color.WHITE))
		var why: Array = row.get("out_for", [])
		var majors := int(row.get("major_findings", 0))
		var said: String = "no major findings"
		if not why.is_empty():
			said = "fails: %s" % ", ".join(why)
		elif majors > 0:
			said = "%d major finding(s)" % majors
		item.set_text(2, said)
		item.set_tooltip_text(2, str(row.get("summary", "")))
		if row.get("candidate_id", "") == recommended and not data.get("every_out", false):
			item.select(0)
	_recommendation.text = str(data.get("recommendation", ""))
	_use.disabled = data.get("candidates", []).is_empty()
	_build_status.text = "%d layouts." % data.get("candidates", []).size()


func _on_chosen(data: Dictionary) -> void:
	var chosen: Dictionary = data.get("chosen", {})
	_build_status.text = "Using seed %s. Choosing records your choice; it does not sign off the layout's quality." \\
		% str(chosen.get("seed", "?"))


func _on_event(event: Dictionary) -> void:
	if event.get("operation", "") != "generate_layouts":
		return
	var msg: String = event.get("message", "")
	if msg != "":
		_build_status.text = msg
	if event.has("progress"):
		_progress.value = float(event["progress"])


func _on_finished(result: Dictionary) -> void:
	var done := _pending
	_pending = Callable()
	_generate.disabled = false
	_stop.disabled = true
'''),
    ('''const SUPPORT_COLOURS := {"supported": Color(0.45, 0.8, 0.45), "conditional": Color(0.95, 0.75, 0.3),
	"intent": Color(0.65, 0.65, 0.7)}
''', '''const SUPPORT_COLOURS := {"supported": Color(0.45, 0.8, 0.45), "conditional": Color(0.95, 0.75, 0.3),
	"intent": Color(0.65, 0.65, 0.7)}
const LAYOUT_COLOURS := {"valid": Color(0.45, 0.8, 0.45), "needs attention": Color(0.95, 0.75, 0.3),
	"failed": Color(0.95, 0.35, 0.35), "not checked": Color(0.65, 0.65, 0.7)}
'''),
])

test = C / "apps" / "godot" / "tests" / "test_level_layouts.gd"
assert not test.exists()
shutil.copyfile(HERE / "src" / "apps" / "godot" / "tests" / "test_level_layouts.gd", test)
print("wrote", test.name)
