"""Level Factory 0.251.0 on a clone: a reopened level shows where it stands -- its layouts and plans, the chosen one,
the last walk and the last export, each saying whether it is of the design as it is now (the factory's roadmap 318:
save and reopen). Anchored; refuses on a miss.

    python edit_lf_standing.py <clone>

Copies packages/service/standing.py, tests/service/test_standing.py and apps/godot/tests/test_level_reopen.gd from
`src/`; `open_design` returns the standing; the build record keeps the recommendation and the plans' key; the Level
tab fills from the standing on every open, clearing the last level's first.
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
for rel in ("packages/service/standing.py", "tests/service/test_standing.py", "apps/godot/tests/test_level_reopen.gd"):
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
    ('''                          "recommended": result["recommended"], "every_out": result["every_out"],
''', '''                          "recommended": result["recommended"], "every_out": result["every_out"],
                          "recommendation": result["recommendation"], "plan_key": result["plan_key"],
'''),
])

edit("packages/service/operations.py", [
    ('''    got["brief"] = design.brief_from_design(got["design"]) if not got["problems"] else None
''', '''    got["brief"] = design.brief_from_design(got["design"]) if not got["problems"] else None
    # where it stands: layouts, choice, last walk and export, read from the records beside it (0.251.0)
    if not got["problems"]:
        from packages.service import standing
        got["standing"] = standing.standing(Path(got["path"]).parent, got["design"])
'''),
])

edit("apps/godot/addons/gabagool_factory/level_panel.gd", [
    ('''	_call("describe_template", {"template": design.get("template", "")}, _on_controls)
''', '''	_call("describe_template", {"template": design.get("template", "")}, _on_controls)
	show_standing(data.get("standing", {}))


## Show where an opened level stands (`open_design`'s ``standing``): its layouts and the chosen one, the last walk and
## the last export, each saying when the level has changed since. Clears what the last level showed first, so a level
## opened after another never shows the other's layouts.
func show_standing(standing: Dictionary) -> void:
	layouts = {}
	walk_result = {}
	export_result = {}
	_layouts.clear()
	_recommendation.text = ""
	_build_status.text = ""
	_use.disabled = true
	_plan.texture = null
	_plan_note.text = ""
	_walk_status.text = ""
	_export_status.text = ""
	_checklist.clear()
	var revision := int(design.get("revision", 0))
	var built: Variant = standing.get("layouts")
	if built is Dictionary:
		show_layouts(built)
		var said := "%d layouts, generated for revision %s." % [built.get("candidates", []).size(),
			str(built.get("design_revision", "?"))]
		var chosen: String = str(standing.get("chosen", "")) if standing.get("chosen") != null else ""
		for row in _layouts.get_root().get_children():
			var item: TreeItem = row
			if chosen != "" and item.get_metadata(0) == chosen:
				item.select(0)
				said += " Using seed %s, chosen earlier." % chosen.get_slice("_", chosen.get_slice_count("_") - 1)
		var stale: Array = standing.get("layouts_stale", [])
		if not stale.is_empty():
			said += " %s changed since they were generated: generate layouts again." % ", ".join(stale)
		_build_status.text = said
		_show_plan()
	var walked: Variant = standing.get("walk")
	if walked is Dictionary:
		_walk_status.text = "Last walked: %s." % str(walked.get("label", "?"))
		if not walked.get("current", false):
			_walk_status.text += " The level has changed since: walk it to see revision %d." % revision
	var exported: Variant = standing.get("export")
	if exported is Dictionary:
		show_export(exported)
		var when := "" if exported.get("current", false) else " The level has changed since that export."
		if not exported.get("snapshot_present", true):
			when += " That folder is no longer there."
		_export_status.text = "Last export, revision %s: %s%s" % [str(exported.get("design_revision", "?")),
			_export_status.text, when]
	var problems: Array = standing.get("problems", [])
	if not problems.is_empty():
		_build_status.text += " Not read: %s" % "; ".join(problems)
'''),
])
