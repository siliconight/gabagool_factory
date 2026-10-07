"""Deli Counter 0.196.0: the nav gate asks whether an entrance reaches each stair.

    python patch_dc_navgate_entries.py

Anchored on godot/addon/deli_counter/nav_gate.gd and nav_gate.py as read
2026-10-06; every anchor must match exactly once or nothing is written.

WHY. A stair whose two ends join is a stair, not a route. deli_a01's up-stair
passed this gate in every build while two crate stacks cut its foot off from
the stairwell's door, and the whole upper storey with it (cold runs 9187 and
9188; Deli Counter 0.195.0; `docs/findings/deli_a01_upper_storey_9188/` at
the factory root). Each storey-0 exterior door and garage is now snapped a
step inside, and each stair reports `from_entry`. REPORTED, NOT GATED, like
`navigable`: the exit code is unchanged and the library's population test
freezes the set.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GD = ROOT / "deli_counter" / "godot" / "addon" / "deli_counter" / "nav_gate.gd"
PY = ROOT / "deli_counter" / "nav_gate.py"

GD_EDITS = []

# 1. the constant, beside the other bake-scope constants
GD_EDITS.append((
    '''# Margin round the geometry's bounds for a swept bake, so moving the origin
# never crops a wall out of it.
const GRID_PAD_M := 2.0
''',
    '''# Margin round the geometry's bounds for a swept bake, so moving the origin
# never crops a wall out of it.
const GRID_PAD_M := 2.0

# AN ENTRANCE IS SNAPPED A STEP INSIDE ITS DOOR (0.196.0). 1.0 m along the
# wall's inward normal is past the wall's erosion (half a wall, 0.15-0.175 m,
# plus the 0.4 m bake radius) and inside the 1.5 m approach no seeded piece
# may stand in (`level_design._seed_clear_doors`), so it lands on the floor
# a body walks in on rather than on the door's own threshold.
const ENTRY_IN := 1.0
'''))

# 2. the entrances, before the stair loop
GD_EDITS.append((
    '''	# -- stairs: prove lower <-> upper --------------------------------------
	var failures := 0
''',
    '''	# -- entrances: snapped once, asked of every stair below (0.196.0) -------
	# A stair whose two ends join is a stair, not a route. deli_a01's up-stair
	# passed the stair check in every build while two crate stacks cut its foot
	# off from the stairwell's door, and its whole upper storey with it (cold
	# runs 9187 and 9188; Deli Counter 0.195.0). Each stair now also reports
	# `from_entry`: is either end on an island an entrance is on. REPORTED, NOT
	# GATED, like `navigable` -- nav_gate.py prints it and the library's
	# population test freezes the set, so the exit code is unchanged.
	var entry_islands := {}
	var entry_rows := []
	for e in _entry_points(gp):
		var ed: Dictionary = e
		var ehit := _snap(nm, _to_godot([ed["x"], ed["y"], ed["z"]]), MARKER_MAX_ABOVE)
		var eisl := -1
		if ehit["dist"] <= SNAP_MAX:
			eisl = _island_of(islands, ehit["poly"])
			entry_islands[eisl] = true
		entry_rows.append({"tag": ed["tag"], "kind": ed["kind"],
						   "x": ed["x"], "y": ed["y"],
						   "snap": snappedf(ehit["dist"], 0.01), "island": eisl})

	# -- stairs: prove lower <-> upper --------------------------------------
	var failures := 0
'''))

# 3. each stair's from_entry, before it is appended
GD_EDITS.append((
    '''			failures += 1
		result["stairs"].append(rep)
		print("[nav-gate] stair %s: %s -- %s" % [rep["id"], rep["status"], rep["detail"]])
''',
    '''			failures += 1
		# An entrance reaches the stair when either end is on an island an
		# entrance is on. Null when no entrance snapped, or an end is off the
		# mesh: nothing measured, so nothing claimed.
		if entry_islands.is_empty() or rep["status"] == "off_navmesh":
			rep["from_entry"] = null
		else:
			rep["from_entry"] = entry_islands.has(_island_of(islands, lo_hit["poly"])) \\
				or entry_islands.has(_island_of(islands, hi_hit["poly"]))
		result["stairs"].append(rep)
		print("[nav-gate] stair %s: %s -- %s" % [rep["id"], rep["status"], rep["detail"]])
'''))

# 4. the summary, before the markers
GD_EDITS.append((
    '''	# -- markers: the documented F5 check, headless (secondary, warn-only) ---
	result["markers"] = _check_markers(gp, nm, graph)
''',
    '''	var judged := 0
	var unreached := []
	for srep in result["stairs"]:
		var sd: Dictionary = srep
		if not sd.has("from_entry") or sd["from_entry"] == null:
			continue
		judged += 1
		if not bool(sd["from_entry"]):
			unreached.append(str(sd.get("id", "?")))
	var snapped := 0
	for row in entry_rows:
		var rd: Dictionary = row
		if int(rd["island"]) >= 0:
			snapped += 1
	result["entries"] = {"points": entry_rows, "snapped": snapped,
						 "stairs_judged": judged, "stairs_unreached": unreached}
	var not_line := ""
	if not unreached.is_empty():
		not_line = " -- NOT: " + ", ".join(unreached)
	print("[nav-gate] entrances: %d of %d snapped; stairs an entrance reaches: %d/%d%s"
		% [snapped, entry_rows.size(), judged - unreached.size(), judged, not_line])

	# -- markers: the documented F5 check, headless (secondary, warn-only) ---
	result["markers"] = _check_markers(gp, nm, graph)
'''))

# 5. the helper, after _to_godot
GD_EDITS.append((
    '''func _to_godot(p: Array) -> Vector3:
	# level space (x, y_north, z_up) -> Godot (x, z_up, -y_north)
	return Vector3(p[0], p[2], -p[1])
''',
    '''func _to_godot(p: Array) -> Vector3:
	# level space (x, y_north, z_up) -> Godot (x, z_up, -y_north)
	return Vector3(p[0], p[2], -p[1])


func _entry_points(gp: Variant) -> Array:
	## Each storey-0 exterior door and garage in gameplay.json, ENTRY_IN m
	## inside its wall at the storey's level, in LEVEL space (x, y_north,
	## z_up) -- the space the openings and markers are written in. The side
	## is the third field of the wall's name (`ext_0_S`); a name without one
	## is skipped rather than guessed at.
	var out := []
	var inward := {"N": [0.0, -1.0], "S": [0.0, 1.0], "E": [-1.0, 0.0], "W": [1.0, 0.0]}
	for o in gp.get("openings", []):
		var od: Dictionary = o
		var kind := str(od.get("kind", ""))
		var wall := str(od.get("wall", ""))
		if not (kind in ["door", "garage"]) or not wall.begins_with("ext_0_"):
			continue
		var parts := wall.split("_")
		if parts.size() < 3 or not inward.has(parts[2]):
			continue
		var n: Array = inward[parts[2]]
		out.append({"tag": str(od.get("tag", "")), "kind": kind,
					"x": float(od.get("x", 0.0)) + float(n[0]) * ENTRY_IN,
					"y": float(od.get("y", 0.0)) + float(n[1]) * ENTRY_IN,
					"z": 0.0})
	return out
'''))

PY_EDITS = [(
    '''    mk = result.get("markers") or {}
    if mk.get("checked"):
''',
    '''    # 0.196.0: does an entrance reach each stair? A stair whose ends join can
    # still be cut off from every door -- deli_a01's was, in cold runs 9187
    # and 9188 -- so the gate snaps each storey-0 exterior door a step inside
    # and asks. Reported here, frozen by test_navgate_population; the
    # returned `ok` is unchanged.
    ent = result.get("entries")
    if isinstance(ent, dict):
        judged = ent.get("stairs_judged", 0)
        unreached = ent.get("stairs_unreached") or []
        lines.append(f"entrances: {ent.get('snapped', 0)} of "
                     f"{len(ent.get('points') or [])} snapped; stairs an "
                     f"entrance reaches: {judged - len(unreached)}/{judged}")
        for sid in unreached:
            lines.append(f"  no entrance reaches stair {sid}")
    else:
        lines.append("entrances: UNJUDGED -- this result predates the "
                     "entrance check (0.196.0)")
    mk = result.get("markers") or {}
    if mk.get("checked"):
'''
)]


def _apply(path, edits):
    data = path.read_bytes()
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    assert not (crlf and lf), "mixed endings in %s; refusing" % path
    eol = "\r\n" if crlf else "\n"
    text = data.decode("utf-8").replace(eol, "\n")
    for old, _new in edits:
        n = text.count(old)
        assert n == 1, "%s: anchor found %d times, not once: %r" % (path.name, n, old[:70])
    for old, new in edits:
        text = text.replace(old, new)
    return text.replace("\n", eol).encode("utf-8")


def main():
    gd = _apply(GD, GD_EDITS)
    py = _apply(PY, PY_EDITS)
    GD.write_bytes(gd)
    PY.write_bytes(py)
    print("nav_gate.gd: %d edits; nav_gate.py: %d edit" % (len(GD_EDITS), len(PY_EDITS)))


if __name__ == "__main__":
    main()
