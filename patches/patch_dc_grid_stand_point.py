"""HELD, NOT APPLIED (2026-10-06). The re-snap this replaces is what a level's
own bake does.
- A register marker inside its counter lands on the counter top at some grid
  origins and on the floor at others. In a level the objective's
  reachability then depends on where the building happens to land.
- So 0.189.0's sweep is reporting a real hazard, not an artefact. Testing
  the base bake's standing place would make the gate stop seeing it.
- Roadmap 189's third item removes the ambiguity at the source: the markers
  move onto the floor beside the counter. After that, this patch and the
  re-snap would agree for those shells.
- Kept, re-versioned for 0.191.0 and dry-run clean against 0.190.0, for the
  day the gate needs to separate a floor neck from a marker's placement.

Deli Counter 0.191.0, the gate half: the grid sweep tests a marker where
the base bake stood it, instead of snapping it afresh at every origin.

Found 2026-10-06 by the route-walking neck finder (roadmap 189,
`docs/findings/stairwell_on_one_grid_in_four/necks.txt` at the factory root).
In nine shells the passing origin's route survives intact at the failing one;
what changes is the polygon the MARKER snaps to.
- The register markers of cr_deli, night_deli, corner_deli_heist_01 and
  fuel_stop_heist stand inside their counters, and land on a counter top at
  some origins and the floor at others.
- 0.189.0's sweep re-ran `_check_markers` per origin, so it reported that as
  a fragile connection.

Now `_check_markers` records where each marker and the spawn stood: the
closest point `_snap` found, which it now returns. The sweep re-finds those
same points at every origin, within GRID_STAND_TOL_M, and asks whether they
connect. A neck in the floor still fails. A marker hopping between a counter
top and the floor no longer does. `_check_markers` loses the `loud`
parameter 0.189.0 gave it: nothing calls it twice any more.

    python patch_dc_grid_stand_point.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
GD = DC / "godot" / "addon" / "deli_counter" / "nav_gate.gd"
TEST = DC / "test_navgate_grid.py"

CONST_OLD = '''# Margin round the geometry's bounds for a swept bake, so moving the origin
# never crops a wall out of it.
const GRID_PAD_M := 2.0
'''
CONST_NEW = '''# Margin round the geometry's bounds for a swept bake, so moving the origin
# never crops a wall out of it.
const GRID_PAD_M := 2.0
# How far the same standing place may move between two bakes and still be
# re-found (0.191.0): a cell height up or down and a contour's simplification
# sideways are a few cells. A counter top is at least 0.6 m above the floor
# beside it, and the clerk's side of a 0.9 m counter at least that far across,
# so neither is ever re-found as the same place.
const GRID_STAND_TOL_M := 0.5
'''

SNAP_OLD = '''			var q := _closest_on_tri(p, a, b, c)
			if q.y - p.y > max_above:
				continue
			var d := p.distance_to(q)
			if d < best_d:
				best_d = d
				best = i
	return {"poly": best, "dist": best_d}
'''
SNAP_NEW = '''			var q := _closest_on_tri(p, a, b, c)
			if q.y - p.y > max_above:
				continue
			var d := p.distance_to(q)
			if d < best_d:
				best_d = d
				best = i
				best_q = q
	# `point` is where on that polygon: the place a body stands, which the grid
	# sweep re-finds at every origin (0.191.0).
	return {"poly": best, "dist": best_d, "point": best_q}
'''
SNAP_DECL_OLD = '''	## `max_above` skips surfaces standing higher than that above `p`.
	var verts := nm.get_vertices()
	var best := -1
	var best_d := INF
'''
SNAP_DECL_NEW = '''	## `max_above` skips surfaces standing higher than that above `p`.
	var verts := nm.get_vertices()
	var best := -1
	var best_d := INF
	var best_q := p
'''

SIG_OLD = '''func _check_markers(gp: Variant, nm: NavigationMesh, graph: Array,
		loud: bool = true) -> Dictionary:
'''
SIG_NEW = '''func _check_markers(gp: Variant, nm: NavigationMesh, graph: Array) -> Dictionary:
'''

ROW_OLD = '''		detail.append({"name": mname, "type": t,
					   "x": float(m.get("x", 0.0)),
					   "y": float(m.get("y", 0.0)),
					   "snap": snappedf(hit["dist"], 0.01),
					   "reachable": reached})
'''
ROW_NEW = '''		var stood: Vector3 = hit["point"]
		detail.append({"name": mname, "type": t,
					   "x": float(m.get("x", 0.0)),
					   "y": float(m.get("y", 0.0)),
					   "snap": snappedf(hit["dist"], 0.01),
					   "reachable": reached,
					   # where it stood, Godot frame: the grid sweep's question
					   "stand": [stood.x, stood.y, stood.z]})
'''

PRINT_OLD = '''	if loud:
		print("[nav-check] %d/%d markers reachable by a nav agent from the spawn" % [reachable, checked])
		if not unreachable.is_empty():
			print("[nav-check] UNREACHABLE: %s" % ", ".join(unreachable))
	return {"checked": checked, "reachable": reachable,
			"unreachable": unreachable, "detail": detail}
'''
PRINT_NEW = '''	print("[nav-check] %d/%d markers reachable by a nav agent from the spawn" % [reachable, checked])
	if not unreachable.is_empty():
		print("[nav-check] UNREACHABLE: %s" % ", ".join(unreachable))
	var spawn_stood: Vector3 = s_hit["point"]
	return {"checked": checked, "reachable": reachable,
			"unreachable": unreachable, "detail": detail,
			"spawn_stand": [spawn_stood.x, spawn_stood.y, spawn_stood.z]}
'''

DOC_OLD = '''	## snapped within SNAP_MAX and joined in the polygon graph -- and the
	## marker test is _check_markers' own. Reports; decides nothing. Where a
	## list is mixed, nav_gate.py scopes it into `navigable`.
'''
DOC_NEW = '''	## snapped within SNAP_MAX and joined in the polygon graph. A marker the
	## base bake reached is asked about the PLACE it stood there, re-found at
	## each origin within GRID_STAND_TOL_M and joined to the spawn's own place:
	## re-snapping the marker let a register inside its counter land on the
	## counter top at some origins and the floor at others (0.191.0). Reports;
	## decides nothing. Where a list is mixed, nav_gate.py scopes it into
	## `navigable`.
'''

LOOP_OLD = '''		var mk := _check_markers(gp, nm, graph, false)
		for row in mk.get("detail", []):
			var mname: String = row["name"]
			if not marker_grid.has(mname):
				marker_grid[mname] = []
			marker_grid[mname].append(bool(row["reachable"]))
'''
LOOP_NEW = '''		var mk_now: Dictionary = result["markers"]
		var s_poly := -1
		if mk_now.has("spawn_stand"):
			var sa: Array = mk_now["spawn_stand"]
			var s_hit := _snap(nm, Vector3(float(sa[0]), float(sa[1]), float(sa[2])))
			if float(s_hit["dist"]) <= GRID_STAND_TOL_M:
				s_poly = s_hit["poly"]
		for row in mk_now.get("detail", []):
			var mname: String = row["name"]
			if not marker_grid.has(mname):
				marker_grid[mname] = []
			var reached := false
			if bool(row["reachable"]) and s_poly >= 0 and row.has("stand"):
				var ma: Array = row["stand"]
				var m_hit := _snap(nm, Vector3(float(ma[0]), float(ma[1]), float(ma[2])))
				reached = float(m_hit["dist"]) <= GRID_STAND_TOL_M \\
					and _connected(graph, s_poly, m_hit["poly"])
			marker_grid[mname].append(reached)
'''

TEST_OLD = '''    assert "filter_baking_aabb" in body
    assert "CELL_SIZE" in body and "CELL_HEIGHT" in body
    assert "_check_markers(gp, nm, graph, false)" in body
'''
TEST_NEW = '''    assert "filter_baking_aabb" in body
    assert "CELL_SIZE" in body and "CELL_HEIGHT" in body


def test_the_sweep_asks_about_the_place_a_marker_stood():
    """0.191.0: a marker is re-found where the base bake stood it, not snapped
    afresh -- a register inside its counter landed on the counter top at some
    origins and the floor at others (roadmap 189's neck finder). Read as
    source."""
    src = open(GD, encoding="utf-8").read()
    body = src[src.index("func _grid_sweep"):]
    body = body[:body.index("\\nfunc ", 1)]
    assert "_check_markers(" not in body
    assert '"spawn_stand"' in body and '"stand"' in body
    assert "GRID_STAND_TOL_M" in body
    snap = src[src.index("func _snap("):]
    snap = snap[:snap.index("\\nfunc ", 1)]
    assert '"point": best_q' in snap
'''

EDITS = {
    TEST: [(TEST_OLD, TEST_NEW)],
    GD: [(CONST_OLD, CONST_NEW), (SNAP_DECL_OLD, SNAP_DECL_NEW), (SNAP_OLD, SNAP_NEW),
         (SIG_OLD, SIG_NEW), (ROW_OLD, ROW_NEW), (PRINT_OLD, PRINT_NEW),
         (DOC_OLD, DOC_NEW), (LOOP_OLD, LOOP_NEW)],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path.name}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
