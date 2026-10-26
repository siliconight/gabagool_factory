"""Level Factory 0.248.0 on a clone: change a level's settings and see the change in the next walk (the factory's
roadmap 316, increment 6 of `docs/AUTHORING_LOOP.md`). Anchored; refuses on a miss.

    python edit_lf_revise.py <clone>

Edits packages/service/design.py (`update_design`, `rebuilds_between`), packages/service/layouts.py
(`write_request`, `latest_layout_record`), packages/service/walking.py (re-import the current revision; refuse when
the layouts are stale), packages/service/operations.py (`update_design`), and the Level tab (an editable form, Save,
Undo). Copies tests/service/test_revise.py and apps/godot/tests/test_level_edit.gd from `src/`.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("tests/service/test_revise.py", "apps/godot/tests/test_level_edit.gd"):
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


edit("packages/service/design.py", [
    ('''def free_folder(root: Path, slug: str) -> Path:''', '''def update_design(doc: dict, expected_revision, choices: dict | None = None, intent: dict | None = None,
                  name: str | None = None) -> dict:
    """``doc`` changed by ``choices``, ``intent`` and ``name``, as revision + 1. ``expected_revision`` is the revision
    the caller edited: when the saved design has moved since, the change is refused (``conflict``) rather than laid
    over somebody else's. Every value is checked against the template's catalog; an unchanged value is allowed and a
    change that changes nothing is refused (``nothing_changed``), so a revision always records a difference."""
    if isinstance(expected_revision, bool) or expected_revision != doc.get("revision"):
        raise DesignError("conflict", "this level was saved as revision %s since revision %s was opened; open it again"
                          % (doc.get("revision"), expected_revision))
    controls = _controls(doc["template"])
    new = json.loads(json.dumps(doc))
    for given, part, kinds in ((choices or {}, "choices", ("supported", "conditional")),
                               (intent or {}, "intent", ("intent",))):
        for key, value in given.items():
            c = controls.get(key)
            if c is None or c["support"] not in kinds:
                raise DesignError("unknown_control", "%s is not a %s control of %s" % (
                    key, "choice" if part == "choices" else "intent", doc["template"]))
            new[part][key] = check_value(c, value)
    if name is not None:
        if not isinstance(name, str) or not name.strip():
            raise DesignError("bad_choice", "a level needs a name")
        new["name"] = name.strip()
    if (new["choices"], new["intent"], new["name"]) == (doc["choices"], doc["intent"], doc["name"]):
        raise DesignError("nothing_changed", "nothing to save: every value is what revision %d says" % doc["revision"])
    new["revision"] = doc["revision"] + 1
    new["updated_at"] = _now()
    return new


def rebuilds_between(old: dict, new: dict) -> list[str]:
    """What a change from ``old`` to ``new`` makes the pipeline rebuild: the `rebuilds` words of every control whose
    value moved (layout, lighting, backdrop, art), sorted. Intent rebuilds nothing."""
    controls = _controls(new["template"])
    words = set()
    for key, value in new["choices"].items():
        if old["choices"].get(key) != value and controls.get(key, {}).get("rebuilds"):
            words.add(controls[key]["rebuilds"])
    return sorted(words)


def free_folder(root: Path, slug: str) -> Path:'''),
])

edit("packages/service/layouts.py", [
    ('''def _design_folder(path: str) -> tuple[Path, dict]:''', '''def write_request(folder: Path, doc: dict) -> tuple[Path, dict]:
    """Write the batch and the brief derived from ``doc`` into ``folder/request/``: what the pipeline imports, and the
    record of what it was asked. Returns the batch's path and the brief."""
    brief = design_mod.brief_from_design(doc)
    t = design_mod.template(doc["template"])
    batch = {"schema": "level_factory.batch.v0.1", "batch_id": doc["slug"], "name": doc["name"],
             "seed_base": int(t["batch"]["seed_base"]), "theme_family": t["batch"]["theme_family"],
             "missions": [brief["mission_id"]]}
    batch_path = _write_json(folder / "request" / "batch.json", batch)
    _write_json(folder / "request" / "briefs" / ("%s.json" % brief["mission_id"]), brief)
    return batch_path, brief


def latest_layout_record(folder: Path) -> dict | None:
    """The newest ``builds/revision_<n>.json`` -- the last generation -- or None."""
    best = None
    for p in (folder / "builds").glob("revision_*.json"):
        stem = p.name[len("revision_"):-len(".json")]
        if stem.isdigit() and (best is None or int(stem) > best[0]):
            best = (int(stem), p)
    return json.loads(best[1].read_text(encoding="utf-8")) if best else None


def _design_folder(path: str) -> tuple[Path, dict]:'''),
    ('''    brief = design_mod.brief_from_design(doc)
    mission = brief["mission_id"]
    t = design_mod.template(doc["template"])
    batch = {"schema": "level_factory.batch.v0.1", "batch_id": doc["slug"], "name": doc["name"],
             "seed_base": int(t["batch"]["seed_base"]), "theme_family": t["batch"]["theme_family"],
             "missions": [mission]}
    request = folder / "request"
    batch_path = _write_json(request / "batch.json", batch)
    _write_json(request / "briefs" / ("%s.json" % mission), brief)
''', '''    batch_path, brief = write_request(folder, doc)
    mission = brief["mission_id"]
'''),
])

edit("packages/service/walking.py", [
    ('''    chosen = _selected(ws, mission)
    if not chosen:
        raise layouts.LayoutError("no_choice", "choose a layout first")
    log = run_dir / "legs.log"
    cancel = run_dir / "cancel"
    legs = [("brief", ''', '''    chosen = _selected(ws, mission)
    if not chosen:
        raise layouts.LayoutError("no_choice", "choose a layout first")
    # THE LAYOUTS MUST BE OF THIS REVISION (0.248.0): a control that rebuilds the layout -- streets, how many to
    # generate -- changed since they were generated means the chosen layout belongs to the old design
    last = layouts.latest_layout_record(folder)
    if last is not None:
        stale = [c["label"] for c in design_mod.capabilities(doc["template"])
                 if c.get("rebuilds") == "layout" and last["brief"].get(c["key"]) !=
                 design_mod.brief_from_design(doc).get(c["key"])]
        if stale:
            raise layouts.LayoutError("needs_new_layouts", "%s changed since these layouts were generated: generate "
                                      "layouts again, then choose one" % ", ".join(stale))
    # AND THE BRIEF THAT BUILDS IS THIS REVISION'S: re-written and re-imported before the art leg
    batch_path, _brief = layouts.write_request(folder, doc)
    log = run_dir / "legs.log"
    cancel = run_dir / "cancel"
    legs = [("import", ["-C", str(ws), "batch", "create", str(batch_path)]),
            ("brief", '''),
    ('''    said = {"brief": "Recording the brief", "lock": "Locking the chosen layout",''',
     '''    said = {"import": "Reading revision %d of the level" % doc["revision"], "brief": "Recording the brief",
            "lock": "Locking the chosen layout",'''),
])

edit("apps/godot/tests/test_level_panel.gd", [
    ('''	_check(time_row.size() == 1 and time_row[0].get_text(1) == "Evening", "Time of day shows the template's Evening")''',
     '''	# 0.248.0: a choice is a drop-down -- its text every option's label, the range the chosen one's index
	var shown := ""
	if time_row.size() == 1:
		var labels: PackedStringArray = time_row[0].get_text(1).split(",")
		shown = labels[int(time_row[0].get_range(1))]
	_check(shown == "Evening", "Time of day shows the template's Evening: %s" % shown)'''),
])

edit("tests/service/test_walking.py", [
    ('''    assert [a[2] for a in calls] == ["approve", "approve", "run", "walk"]
    assert calls[0][3:5] == ["walker_001", "brief_approved"] and calls[1][4] == "functional_shell_locked"''',
     '''    # 0.248.0: the walk re-imports the current revision's brief first
    assert calls[0][2:4] == ["batch", "create"]
    calls = calls[1:]
    assert [a[2] for a in calls] == ["approve", "approve", "run", "walk"]
    assert calls[0][3:5] == ["walker_001", "brief_approved"] and calls[1][4] == "functional_shell_locked"'''),
])

edit("packages/service/operations.py", [
    ('''def walk_level(arguments: dict, events) -> dict:''', '''def update_design(arguments: dict, events) -> dict:
    """Save a change to the design at ``path`` as its next revision. Arguments: ``path``, ``revision`` (the one the
    change was made to: a design saved since is a ``conflict``), and any of ``choices``, ``intent``, ``name``.
    Returns the new design and ``rebuilds`` -- what the change makes the pipeline rebuild (layout, lighting, backdrop,
    art) -- so the panel can say whether a walk or new layouts come next."""
    _no_unknown(arguments, {"path", "revision", "choices", "intent", "name"})
    from packages.service import design
    for part in ("choices", "intent"):
        if not isinstance(arguments.get(part, {}), dict):
            raise RequestError("bad_argument", "%s must be an object" % part)
    try:
        got = design.read_design(Path(_text(arguments, "path")))
        if got["problems"]:
            raise RequestError("design_unusable", "; ".join(got["problems"]))
        old = got["design"]
        new = design.update_design(old, arguments.get("revision"), arguments.get("choices"),
                                   arguments.get("intent"), arguments.get("name"))
        path = design.write_design(Path(got["path"]).parent, new)
    except design.DesignError as exc:
        raise _design_error(exc) from None
    rebuilds = design.rebuilds_between(old, new)
    events.emit("design", "ok", "Saved revision %d" % new["revision"])
    return {"design": new, "path": str(path), "rebuilds": rebuilds, "problems": [], "unknown_fields": [],
            "brief": design.brief_from_design(new)}


def walk_level(arguments: dict, events) -> dict:'''),
    ('''    "walk_level": walk_level,
}''', '''    "walk_level": walk_level,
    "update_design": update_design,
}'''),
])

edit("apps/godot/addons/gabagool_factory/level_panel.gd", [
    ('''var _walk: Button
var _walk_status: Label
''', '''var _walk: Button
var _walk_status: Label
var _save: Button
var _undo: Button
## The controls the form shows, as `describe_template` returned them.
var _controls: Array = []
## The design as it was before the last save, for Undo ({} when there is nothing to undo).
var _before_save: Dictionary = {}
'''),
    ('''	_form.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_form)
''', '''	_form.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_form)

	# EDIT (increment 6, roadmap 316): the form's values are editable; Save makes the next revision
	var edit_row := HBoxContainer.new()
	_save = Button.new()
	_save.text = "Save changes"
	_save.pressed.connect(save_changes)
	edit_row.add_child(_save)
	_undo = Button.new()
	_undo.text = "Undo last save"
	_undo.disabled = true
	_undo.pressed.connect(undo_last_save)
	edit_row.add_child(_undo)
	add_child(edit_row)
'''),
    ('''		var value: Variant = design.get("name", "") if key == "name" else choices.get(key, intent.get(key, ""))
		item.set_text(1, _shown(control, value))
''', '''		var value: Variant = design.get("name", "") if key == "name" else choices.get(key, intent.get(key, ""))
		_editable(item, control, value)
'''),
    ('''func _on_controls(data: Dictionary) -> void:
	_form.clear()''', '''func _on_controls(data: Dictionary) -> void:
	_controls = data.get("controls", [])
	_form.clear()'''),
    ('''## A control's value as the form shows it: an option's label, yes/no, a list joined.''', '''## Make the form's value cell for `control` editable: a choice as a drop-down of its options' labels, a whole
## number as a spin range, yes/no as a check box, a list as words joined by commas, text as text.
func _editable(item: TreeItem, control: Dictionary, value: Variant) -> void:
	var kind: String = control.get("type", "text")
	item.set_metadata(1, control.get("key", ""))
	item.set_editable(1, true)
	if kind == "choice":
		var labels: PackedStringArray = PackedStringArray()
		var index := 0
		var options: Array = control.get("options", [])
		for i in range(options.size()):
			var option: Dictionary = options[i]
			labels.append(str(option.get("label", option.get("value"))).replace(",", ";"))
			if option.get("value") == value:
				index = i
		item.set_cell_mode(1, TreeItem.CELL_MODE_RANGE)
		item.set_text(1, ",".join(labels))
		item.set_range(1, index)
	elif kind == "integer":
		item.set_cell_mode(1, TreeItem.CELL_MODE_RANGE)
		item.set_range_config(1, float(control.get("min", 0)), float(control.get("max", 100)), 1.0)
		item.set_range(1, float(value))
	elif kind == "boolean":
		item.set_cell_mode(1, TreeItem.CELL_MODE_CHECK)
		item.set_checked(1, bool(value))
		item.set_text(1, "yes")
	else:
		item.set_cell_mode(1, TreeItem.CELL_MODE_STRING)
		item.set_text(1, _shown(control, value))


## The form's values as `update_design` takes them: {"choices", "intent", "name"}.
func form_values() -> Dictionary:
	var choices := {}
	var intent := {}
	var level_name := ""
	var root_item := _form.get_root()
	var rows: Array = root_item.get_children() if root_item != null else []
	for i in range(mini(rows.size(), _controls.size())):
		var item: TreeItem = rows[i]
		var control: Dictionary = _controls[i]
		var key: String = control.get("key", "")
		var kind: String = control.get("type", "text")
		var value: Variant
		if kind == "choice":
			var options: Array = control.get("options", [])
			var option: Dictionary = options[clampi(int(item.get_range(1)), 0, options.size() - 1)]
			value = option.get("value")
		elif kind == "integer":
			value = int(item.get_range(1))
		elif kind == "boolean":
			value = item.is_checked(1)
		elif kind == "list":
			var words: Array = []
			for w in item.get_text(1).split(","):
				if w.strip_edges() != "":
					words.append(w.strip_edges())
			value = words
		else:
			value = item.get_text(1)
		if key == "name":
			level_name = str(value)
		elif control.get("support", "") == "intent":
			intent[key] = value
		else:
			choices[key] = value
	return {"choices": choices, "intent": intent, "name": level_name}


## Save the form as the design's next revision (`update_design`).
func save_changes() -> void:
	if design_path == "" or design.is_empty():
		_info.text = "Open or start a level first."
		return
	var values := form_values()
	# the snapshot rides with the request and is kept only when the save lands
	_call("update_design", {"path": design_path, "revision": design.get("revision"), "choices": values["choices"],
		"intent": values["intent"], "name": values["name"]}, _on_saved.bind(design.duplicate(true)))


## Save the values from before the last save, as a new revision: history is never rewritten.
func undo_last_save() -> void:
	if _before_save.is_empty():
		return
	var back := _before_save
	_call("update_design", {"path": design_path, "revision": design.get("revision"),
		"choices": back.get("choices", {}), "intent": back.get("intent", {}), "name": back.get("name", "")},
		_on_saved.bind({}))


func _on_saved(data: Dictionary, before: Dictionary) -> void:
	_before_save = before
	_on_design(data)
	_undo.disabled = _before_save.is_empty()
	var rebuilds: Array = data.get("rebuilds", [])
	if rebuilds.has("layout"):
		_walk_status.text = "Saved revision %s. This change makes new layouts: generate layouts again, then choose one." \\
			% str(design.get("revision"))
	elif rebuilds.is_empty():
		_walk_status.text = "Saved revision %s. Nothing to rebuild: it records intent." % str(design.get("revision"))
	else:
		_walk_status.text = "Saved revision %s. Walk the level to see it (rebuilds the %s)." \\
			% [str(design.get("revision")), ", ".join(rebuilds)]


## A control's value as the form shows it: an option's label, yes/no, a list joined.'''),
])
