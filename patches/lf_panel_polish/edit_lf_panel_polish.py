"""Level Factory 0.256.0 on a clone: three defects the walker found on the first windowed run of the authoring loop
(the factory's roadmap 318, `docs/AUTHORING_LOOP.md`). Anchored; refuses on a miss.

    python edit_lf_panel_polish.py <clone>

  1. The progress bar went backwards: it counted finished jobs over the jobs the index knew, and the index learns
     of jobs as the run reaches them. `run` now records its whole plan when it starts (`runs/<mission>.json`) and
     the progress counts this run's finished jobs against that fixed total.
  2. Whole numbers read as decimals ("revision 1.0", "Seed 9003.0"): Godot parses every JSON number as a float.
  3. The Setup tab cut every column off in a narrow dock with nothing to show the rest: each cell now carries its
     full text as a tooltip, and the readiness column is wide enough for "warning".
  4. The bar sat at 99% through the walk's last stage, which counts nothing, and read as stuck: every walk stage
     now says "Stage n of m", and a stage that cannot count puts the bar in motion (indeterminate) instead of
     leaving the last stage's number on it.

Copies tests/integration/test_run_progress.py and apps/godot/tests/test_panel_numbers.gd (+ .uid) from `src/`.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
NEW = sorted(str(p.relative_to(HERE / "src")).replace("\\", "/") for p in (HERE / "src").rglob("*") if p.is_file())
for rel in NEW:
    dst = C / rel
    assert not dst.exists(), rel
    dst.parent.mkdir(parents=True, exist_ok=True)
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


edit("apps/cli/commands/__init__.py", [
    ('''    summary = scheduler.run(plan.graph, job_specs=specs, mission_id=args.mission_id,
                            force=bool(getattr(args, "force", False)))''',
     '''    _write_run_plan(ws, args.mission_id, plan)
    summary = scheduler.run(plan.graph, job_specs=specs, mission_id=args.mission_id,
                            force=bool(getattr(args, "force", False)))'''),
    ('''def cmd_run(args) -> int:''', '''def _write_run_plan(ws, mission_id: str, plan) -> Path:
    """Record what this run is about to do: ``<workspace>/.level_factory/runs/<mission>.json`` -- every planned job
    and the moment it started (UTC, the format the index stamps ``finished_at`` in). Written once, before the first
    job is dispatched, so a reader counting progress has the whole total from the start (0.256.0: the Factory
    panel's bar counted against the jobs the index had met so far, and went backwards as it met more)."""
    import datetime as _dt
    import json as _json
    import os as _os
    path = ws.jobs_dir.parent / "runs" / f"{mission_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(_json.dumps({
        "schema": "level_factory.run_plan.v1", "mission_id": mission_id,
        "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "jobs": [j.job_id for j in plan.graph.topological_order()]}, indent=1) + "\\n", encoding="utf-8")
    _os.replace(tmp, path)
    return path


def cmd_run(args) -> int:'''),
])

edit("packages/service/layouts.py", [
    ('''def index_progress(ws: Path, mission: str, events, stage: str) -> None:
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
''', '''def index_progress(ws: Path, mission: str, events, stage: str, since: float = 0.0) -> None:
    """Report how far the running ``run`` has got: of the jobs IT PLANNED (``runs/<mission>.json``, which it writes
    before dispatching anything), how many have finished SINCE IT STARTED, read from the job index. The total is
    fixed when the run starts, so the bar only moves forward (0.256.0: it counted against the jobs the index had met
    so far, and the walker watched it go backwards). A plan written before ``since`` -- the epoch seconds this leg
    started -- is the last run's, and a job finished before the run started is the last run's: neither counts, and
    nothing is said until this run's plan exists. A read that races a writer is skipped; the next poll asks again."""
    from packages.core import states
    from packages.project_store.index import Index
    internal = ws / ".level_factory"
    record, db = internal / "runs" / ("%s.json" % mission), internal / "index.sqlite"
    try:
        if record.stat().st_mtime < since or not db.exists():
            return
        plan = json.loads(record.read_text(encoding="utf-8"))
        planned, started = set(plan["jobs"]), str(plan["started_at"])
        idx = Index(db)
        jobs = idx.jobs_for_mission(mission)
        idx.close()
    except Exception:
        return
    if planned:
        done = sum(1 for j in jobs if j.job_id in planned and j.status in states.JOB_TERMINAL
                   and str(j.finished_at or "") >= started)
        events.emit(stage, "running", "%d of %d build steps done" % (done, len(planned)),
                    progress=done / len(planned))
'''),
    ('''    def progress():
        index_progress(ws, mission, events, "layouts")
''', '''    leg_started = time.time()

    def progress():
        index_progress(ws, mission, events, "layouts", since=leg_started)
'''),
    ('''                    progress=i / len(legs) if name != "layouts" else None)
        try:
            code = leg(argv, log, cancel_file=cancel, on_poll=progress if name == "layouts" else None)''',
     '''                    progress=i / len(legs) if name != "layouts" else None)
        leg_started = time.time()
        try:
            code = leg(argv, log, cancel_file=cancel, on_poll=progress if name == "layouts" else None)'''),
])

edit("packages/service/walking.py", [
    ('''    for name, argv in legs:
        events.emit(name, "running", said[name])
''', '''    for i, (name, argv) in enumerate(legs):
        events.emit(name, "running", "Stage %d of %d: %s" % (i + 1, len(legs), said[name]))
'''),
    ('''        poll = (lambda: layouts.index_progress(ws, mission, events, "art")) if name == "art" else None
''', '''        poll = ((lambda since=time.time(): layouts.index_progress(ws, mission, events, "art", since=since))
                if name == "art" else None)
'''),
])

P = "apps/godot/addons/gabagool_factory/level_panel.gd"
edit(P, [
    ('''		item.set_text(0, "Seed %s" % str(row.get("seed", "?")))''',
     '''		item.set_text(0, "Seed %s" % whole(row.get("seed", "?")))'''),
    ('''	_plan_note.text = "Seed %s. %s" % [str(row.get("seed", "?")), str(layouts.get("plan_key", ""))]''',
     '''	_plan_note.text = "Seed %s. %s" % [whole(row.get("seed", "?")), str(layouts.get("plan_key", ""))]'''),
    ('''		% str(chosen.get("seed", "?"))''', '''		% whole(chosen.get("seed", "?"))'''),
    ('''		var label := "%s (revision %s)" % [row.get("name", "?"), str(row.get("revision", "?"))]''',
     '''		var label := "%s (revision %s)" % [row.get("name", "?"), whole(row.get("revision", "?"))]'''),
    ('''	var text := "%s -- revision %s, from %s. Saved at %s." % [design.get("name", "?"), str(design.get("revision", "?")),''',
     '''	var text := "%s -- revision %s, from %s. Saved at %s." % [design.get("name", "?"), whole(design.get("revision", "?")),'''),
    ('''			str(built.get("design_revision", "?"))]''', '''			whole(built.get("design_revision", "?"))]'''),
    ('''		_export_status.text = "Last export, revision %s: %s%s" % [str(exported.get("design_revision", "?")),''',
     '''		_export_status.text = "Last export, revision %s: %s%s" % [whole(exported.get("design_revision", "?")),'''),
    ('''			% str(design.get("revision"))
''', '''			% whole(design.get("revision"))
'''),
    ('''		_walk_status.text = "Saved revision %s. Nothing to rebuild: it records intent." % str(design.get("revision"))''',
     '''		_walk_status.text = "Saved revision %s. Nothing to rebuild: it records intent." % whole(design.get("revision"))'''),
    ('''			% [str(design.get("revision")), ", ".join(rebuilds)]''',
     '''			% [whole(design.get("revision")), ", ".join(rebuilds)]'''),
    ('''	if event.has("progress"):
		_progress.value = float(event["progress"])
''', '''	if event.has("progress"):
		_progress.indeterminate = false
		_progress.value = float(event["progress"])
	elif event.get("status", "") == "running":
		# a stage that cannot count shows motion, never the last stage's number (0.256.0: 99% read as stuck)
		_progress.indeterminate = true
'''),
    ('''func _on_finished(result: Dictionary) -> void:
	var done := _pending
''', '''func _on_finished(result: Dictionary) -> void:
	_progress.indeterminate = false
	var done := _pending
'''),
    ('''## Show the selected layout's plan:''', '''## A number as people write it: Godot reads every JSON number as a float, so a revision or a seed arrives as 1.0
## or 9003.0 (0.256.0). Whole numbers lose the ".0"; anything else is shown as it is.
static func whole(value: Variant) -> String:
	if value is float and is_equal_approx(value, roundf(value)):
		return str(int(value))
	return str(value)


## Show the selected layout's plan:'''),
])

edit("apps/godot/addons/gabagool_factory/factory_dock.gd", [
    ('''	_checks.set_column_custom_minimum_width(0, 70)
''', '''	_checks.set_column_custom_minimum_width(0, 84)          # room for "warning" (0.256.0: it read "warnin")
'''),
    ('''		item.set_text(0, readiness)
		item.set_custom_color(0, COLOURS.get(readiness, Color.WHITE))
		item.set_text(1, check.get("label", check.get("name", "")))
		item.set_tooltip_text(1, check.get("technical", ""))
		var fix: Variant = check.get("fix")
		item.set_text(2, fix if fix is String else "")
''', '''		item.set_text(0, readiness)
		item.set_custom_color(0, COLOURS.get(readiness, Color.WHITE))
		var label: String = str(check.get("label", check.get("name", "")))
		item.set_text(1, label)
		var fix: Variant = check.get("fix")
		item.set_text(2, fix if fix is String else "")
		# a narrow dock cuts every column off: each cell's whole text is its tooltip (0.256.0)
		item.set_tooltip_text(0, readiness)
		var technical: String = str(check.get("technical", ""))
		item.set_tooltip_text(1, label + ("\\n" + technical if technical != "" else ""))
		item.set_tooltip_text(2, fix if fix is String else "")
'''),
])
