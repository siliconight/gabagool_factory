"""Level Factory 0.256.0 on a clone, after `edit_lf_panel_polish.py`: the walker's fifth and sixth findings on the
first windowed run (the factory's roadmap 318). Anchored; refuses on a miss.

    python edit_lf_panel_resume.py <clone>

  5. The panel restarted while a walk was running (11:16, 2026-10-26) and lost it: the walk went on, its result
     landed in a run directory nobody watched, and Stop went to another run. The client now records the operation
     it starts (`user://factory_runs/current_<owner>.json`) and the Level tab re-attaches to it when it loads: a
     run still going is followed to its result, one that finished meanwhile is shown once.
  6. Nothing on the tab opened a walk already built: "Open the last walk" launches the preview the last walk record
     names, without building it again.

Copies apps/godot/tests/test_panel_resume.gd (+ .uid) from `src_resume/`.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for p in sorted((HERE / "src_resume").rglob("*")):
    if p.is_file():
        rel = str(p.relative_to(HERE / "src_resume")).replace("\\", "/")
        assert not (C / rel).exists(), rel
        shutil.copyfile(p, C / rel)
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


edit("apps/godot/addons/gabagool_factory/service_client.gd", [
    ('''var run_dir: String = ""
''', '''var run_dir: String = ""
## When set, the operation this client starts is recorded in `user://factory_runs/current_<record_name>.json` until
## it finishes, so a panel that restarts can `resume()` it (0.256.0). Empty records nothing.
var record_name: String = ""
## A resumed run was started by another instance of the panel: Godot can only ask after processes it started
## itself, so a resumed run is followed by its result file alone.
var _resumed: bool = false
'''),
    ('''	_events_offset = 0
	_partial = ""
	_exited_at = -1.0
	_running = true
	_timer.start()
	return ""
''', '''	_events_offset = 0
	_partial = ""
	_exited_at = -1.0
	_running = true
	_resumed = false
	_record({"run_dir": run_dir, "operation": operation, "started": Time.get_datetime_string_from_system()})
	_timer.start()
	return ""


func _record_path() -> String:
	return ProjectSettings.globalize_path("user://factory_runs").path_join("current_%s.json" % record_name)


func _record(data: Dictionary) -> void:
	if record_name == "":
		return
	var f := FileAccess.open(_record_path(), FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(data))
		f.close()


## Re-attach to the operation an earlier instance of this panel started and did not see finish. Returns its
## operation name ("" when there is none): `finished` then fires once, with its result -- at once when it finished
## while nobody watched, else when it does. Stop still reaches it through its cancel file.
func resume() -> String:
	if _running or record_name == "" or not FileAccess.file_exists(_record_path()):
		return ""
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(_record_path()))
	if not (parsed is Dictionary) or not DirAccess.dir_exists_absolute(str(parsed.get("run_dir", ""))):
		DirAccess.remove_absolute(_record_path())
		return ""
	run_dir = str(parsed["run_dir"])
	_pid = -1
	_events_offset = 0
	_partial = ""
	_exited_at = -1.0
	_running = true
	_resumed = true
	_timer.start()
	return str(parsed.get("operation", ""))
'''),
    ('''	if not OS.is_process_running(_pid):
		var now''', '''	if not _resumed and not OS.is_process_running(_pid):
		var now'''),
    ('''func _finish(result: Dictionary) -> void:
	_read_events()
	_timer.stop()
	_running = false
''', '''func _finish(result: Dictionary) -> void:
	_read_events()
	_timer.stop()
	_running = false
	_resumed = false
	if record_name != "" and FileAccess.file_exists(_record_path()):
		DirAccess.remove_absolute(_record_path())
'''),
])

edit("apps/godot/addons/gabagool_factory/level_panel.gd", [
    ('''	client = ServiceClient.new()
	add_child(client)
''', '''	client = ServiceClient.new()
	client.record_name = "level"
	add_child(client)
'''),
    ('''var walk_result: Dictionary = {}
''', '''var walk_result: Dictionary = {}
var _open_walk: Button
'''),
    ('''	_walk.pressed.connect(walk_level)
	add_child(_walk)
''', '''	_walk.pressed.connect(walk_level)
	add_child(_walk)
	# open the walk already built, without building it again (0.256.0)
	_open_walk = Button.new()
	_open_walk.text = "Open the last walk"
	_open_walk.visible = false
	_open_walk.pressed.connect(open_last_walk)
	add_child(_open_walk)
'''),
    ('''	var last := _setting(SETTING_LAST)
	if last != "":
		open_design(last)
''', '''	var last := _setting(SETTING_LAST)
	if last != "":
		open_design(last)
	# an operation an earlier panel started and did not see finish: re-attach once the quick loads are done
	_queue.append(["__resume__", {}, Callable()])
	_next()
'''),
    ('''	var item: Array = _queue.pop_front()
	_pending = item[2]
''', '''	var item: Array = _queue.pop_front()
	if item[0] == "__resume__":
		_resume()
		return
	_pending = item[2]
'''),
    ('''## Show a `walk_level` answer and, unless turned off, open the preview.
func show_walk(data: Dictionary) -> void:
	walk_result = data
''', '''## Re-attach to an operation an earlier panel started (`ServiceClient.resume`), routing its answer where it would
## have gone and saying so meanwhile.
func _resume() -> void:
	var operation: String = client.resume()          # client is a Node: annotate, never infer
	var handlers := {"walk_level": show_walk, "generate_layouts": show_layouts, "export_level": show_export,
		"choose_layout": _on_chosen}
	if operation == "":
		_next()
		return
	_pending = handlers.get(operation, Callable())
	_stop.disabled = false
	if operation == "walk_level" or operation == "generate_layouts":
		_walk.disabled = true
		_generate.disabled = true
	var said := "Still running from before the panel restarted: %s. It carries on; Stop still stops it." % operation
	if operation == "walk_level":
		_walk_status.text = said
	else:
		_build_status.text = said


## Open the preview the last walk built (`walk_result`), without building it again.
func open_last_walk() -> void:
	var command := preview_command(walk_result)
	if command.is_empty():
		_walk_status.text = "No walk to open yet: walk the level first."
		return
	if launch_previews and OS.create_process(command[0], command[1]) <= 0:
		_walk_status.text = "Godot could not be started from %s." % command[0]


## Show a `walk_level` answer and, unless turned off, open the preview.
func show_walk(data: Dictionary) -> void:
	walk_result = data
	_open_walk.visible = not preview_command(data).is_empty()
'''),
    ('''	var walked: Variant = standing.get("walk")
	if walked is Dictionary:
''', '''	var walked: Variant = standing.get("walk")
	_open_walk.visible = false
	if walked is Dictionary:
		walk_result = walked
		_open_walk.visible = not preview_command(walked).is_empty()
'''),
])
