"""Level Factory 0.247.0 on a clone: walk a level's chosen layout from the panel (the factory's roadmap 315, increment 5
of `docs/AUTHORING_LOOP.md`). Anchored; refuses on a miss.

    python edit_lf_walk.py <clone>

Copies packages/service/walking.py, tests/service/test_walking.py and apps/godot/tests/test_level_walk.gd from `src/`
beside this script; lifts the job-index progress into `layouts.index_progress`; adds the `walk_level` operation and
the Level tab's Walk level. VERSION and CHANGELOG are the generator's.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("packages/service/walking.py", "tests/service/test_walking.py", "apps/godot/tests/test_level_walk.gd"):
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
    ('''def _design_folder(path: str) -> tuple[Path, dict]:''',
     '''def index_progress(ws: Path, mission: str, events, stage: str) -> None:
    """Report how many of the mission's planned jobs have finished, read from the workspace's job index. A read
    that races the writer is skipped; the next poll asks again."""
    from packages.core import states
    from packages.project_store.index import Index
    db = ws / ".level_factory" / "index.sqlite"
    if not db.exists():
        return
    try:
        idx = Index(db)
        jobs = idx.jobs_for_mission(mission)
        idx.close()
    except Exception:
        return
    if jobs:
        finished = sum(1 for j in jobs if j.status in states.JOB_TERMINAL)
        events.emit(stage, "running", "%d of %d steps done" % (finished, len(jobs)), progress=finished / len(jobs))


def _design_folder(path: str) -> tuple[Path, dict]:'''),
    ('''    def progress():
        from packages.core import states
        from packages.project_store.index import Index
        db = ws / ".level_factory" / "index.sqlite"
        if not db.exists():
            return
        try:
            idx = Index(db)
            jobs = idx.jobs_for_mission(mission)
            idx.close()
        except Exception:  # a read racing the writer: the next poll asks again
            return
        if jobs:
            finished = sum(1 for j in jobs if j.status in states.JOB_TERMINAL)
            events.emit("layouts", "running", "%d of %d steps done" % (finished, len(jobs)),
                        progress=finished / len(jobs))
''', '''    def progress():
        index_progress(ws, mission, events, "layouts")
'''),
])

edit("packages/service/operations.py", [
    ('''OPERATIONS = {''', '''def walk_level(arguments: dict, events) -> dict:
    """Build the walk preview of the design at ``path``'s chosen layout (`packages.service.walking.walk`): the brief
    and shell-lock gates recorded as the panel's automatic steps, the art and gameplay leg, then the preview with its
    traversal self-check. Returns the preview's folder and the Godot to open it with, named by design revision and
    layout. Opens no window."""
    _no_unknown(arguments, {"path"})
    from packages.service import layouts, walking
    try:
        return walking.walk(_text(arguments, "path"), events, Path(events.path).parent)
    except (layouts.LayoutError, ValueError) as exc:
        raise RequestError(getattr(exc, "code", "design_unusable"), str(exc)) from None


OPERATIONS = {'''),
    ('''    "choose_layout": choose_layout,
}''', '''    "choose_layout": choose_layout,
    "walk_level": walk_level,
}'''),
])

edit("apps/godot/addons/gabagool_factory/level_panel.gd", [
    ('''var _layouts: Tree
var _use: Button
''', '''var _layouts: Tree
var _use: Button
var _walk: Button
var _walk_status: Label
## Open the preview's window when a walk is ready. A test turns it off.
var launch_previews: bool = true
## The last walk the factory built for this design ({} before one).
var walk_result: Dictionary = {}
'''),
    ('''	_use.pressed.connect(use_layout)
	add_child(_use)
''', '''	_use.pressed.connect(use_layout)
	add_child(_use)

	# WALK (increment 5, roadmap 315)
	_walk = Button.new()
	_walk.text = "Walk level"
	_walk.pressed.connect(walk_level)
	add_child(_walk)
	_walk_status = Label.new()
	_walk_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(_walk_status)
'''),
    ('''## Ask the running build to stop.
func stop() -> void:''', '''## Build the chosen layout's walk preview (`walk_level`) and open it.
func walk_level() -> void:
	if design_path == "":
		_info.text = "Open or start a level first."
		return
	_walk.disabled = true
	_generate.disabled = true
	_stop.disabled = false
	_progress.value = 0.0
	_walk_status.text = "Building the walk: dressing, lighting and a self-check. This takes several minutes."
	_call("walk_level", {"path": design_path}, show_walk)


## Show a `walk_level` answer and, unless turned off, open the preview.
func show_walk(data: Dictionary) -> void:
	walk_result = data
	var check: String = str(data.get("self_check", ""))
	var said := "Walking %s." % str(data.get("label", "?"))
	if check == "findings":
		said += " Its self-check found something: walk it and see."
	elif check == "passed":
		said += " Its self-check passed."
	var command := preview_command(data)
	if command.is_empty():
		said += " Godot is not recorded for this level's workspace; open %s in Godot." % str(data.get("preview", ""))
	elif launch_previews:
		var pid := OS.create_process(command[0], command[1])
		if pid <= 0:
			said += " Godot could not be started from %s." % command[0]
	_walk_status.text = said


## The executable and arguments that open a walk preview, or [] when no Godot is recorded.
static func preview_command(data: Dictionary) -> Array:
	var godot := str(data.get("godot", ""))
	var preview := str(data.get("preview", ""))
	if godot == "" or preview == "":
		return []
	return [godot, PackedStringArray(["--path", preview])]


## Ask the running build to stop.
func stop() -> void:'''),
    ('''	_generate.disabled = false
	_stop.disabled = true
''', '''	_generate.disabled = false
	_stop.disabled = true
	_walk.disabled = false
'''),
    ('''func _on_event(event: Dictionary) -> void:
	if event.get("operation", "") != "generate_layouts":
		return
	var msg: String = event.get("message", "")
	if msg != "":
		_build_status.text = msg
''', '''func _on_event(event: Dictionary) -> void:
	var operation: String = event.get("operation", "")
	if operation != "generate_layouts" and operation != "walk_level":
		return
	var msg: String = event.get("message", "")
	if msg != "":
		if operation == "generate_layouts":
			_build_status.text = msg
		else:
			_walk_status.text = msg
'''),
])
