"""Deli Counter 0.189.0, the gate half: the nav gate bakes each shell again at
eight voxel-grid origins, and an interior marker or a stair that connects at
only some of them is reported -- and makes the shell not navigable, which is
what Level Factory's themed-lot selection reads.

Found 2026-10-06 (roadmap 189, `docs/findings/stairwell_on_one_grid_in_four/`):
deli_a03's objective upstairs joins the ground floor at 8 of 32 grid origins,
the gate baked one and passed it, and cold run 9185 lost two candidates of
three when the site's grid fell on the other side.

    python patch_dc_grid_sweep.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

GD_CONST_OLD = '''var MARKER_MAX_ABOVE := 0.3 + AGENT_MAX_CLIMB

var _exit_code := 0
'''
GD_CONST_NEW = '''var MARKER_MAX_ABOVE := 0.3 + AGENT_MAX_CLIMB

# THE GRID SWEEP (0.189.0). A navmesh's voxel grid starts at the corner of
# whatever is baked, so one building baked alone and the same building
# standing in a site sit on different grids -- and a connection that passes
# through a neck a few cells wide holds on some and not others. Measured
# 2026-10-06 (roadmap 189): deli_a03's objective upstairs joins its ground
# floor at 8 of 32 origins; this gate baked one, at its own bounds, and that
# one connected. Cold run 9185's site fell on another and lost two candidates.
#
# So the same parsed geometry is baked again at eight origins inside one cell:
# eight distinct X and Z phases, four Y phases. Fractions of a cell, not
# metres, so they follow agent_contract.json when the cell size changes.
const GRID_FRACTIONS := [[0.0, 0.0, 0.0], [0.5, 0.5, 0.25], [0.25, 0.0, 0.75],
	[0.75, 0.5, 0.5], [0.125, 0.25, 0.375], [0.625, 0.75, 0.125],
	[0.375, 0.25, 0.875], [0.875, 0.75, 0.625]]
# Margin round the geometry's bounds for a swept bake, so moving the origin
# never crops a wall out of it.
const GRID_PAD_M := 2.0

var _exit_code := 0
'''

GD_CALL_OLD = '''	# -- markers: the documented F5 check, headless (secondary, warn-only) ---
	result["markers"] = _check_markers(gp, nm, graph)
'''
GD_CALL_NEW = '''	# -- markers: the documented F5 check, headless (secondary, warn-only) ---
	result["markers"] = _check_markers(gp, nm, graph)

	# -- the grid sweep: does any of it depend on where the grid falls? ------
	_grid_sweep(gp, src, result)
'''

GD_SIG_OLD = '''func _check_markers(gp: Variant, nm: NavigationMesh, graph: Array) -> Dictionary:
'''
GD_SIG_NEW = '''func _check_markers(gp: Variant, nm: NavigationMesh, graph: Array,
		loud: bool = true) -> Dictionary:
'''

GD_PRINT_OLD = '''	print("[nav-check] %d/%d markers reachable by a nav agent from the spawn" % [reachable, checked])
	if not unreachable.is_empty():
		print("[nav-check] UNREACHABLE: %s" % ", ".join(unreachable))
'''
GD_PRINT_NEW = '''	if loud:
		print("[nav-check] %d/%d markers reachable by a nav agent from the spawn" % [reachable, checked])
		if not unreachable.is_empty():
			print("[nav-check] UNREACHABLE: %s" % ", ".join(unreachable))
'''

GD_FUNC_ANCHOR = '''func _to_godot(p: Array) -> Vector3:
'''
GD_FUNC_NEW = '''func _grid_sweep(gp: Variant, src: NavigationMeshSourceGeometryData3D,
		result: Dictionary) -> void:
	## Bake `src` again at every GRID_FRACTIONS origin and write, beside each
	## traversable stair and each checked marker, the list of origins at which
	## it connected (`grid`). The stair test is the main loop's -- both ends
	## snapped within SNAP_MAX and joined in the polygon graph -- and the
	## marker test is _check_markers' own. Reports; decides nothing. Where a
	## list is mixed, nav_gate.py scopes it into `navigable`.
	var bounds: AABB = src.get_bounds()
	var pad := Vector3(GRID_PAD_M, GRID_PAD_M, GRID_PAD_M)
	var systems: Array = gp.get("stair_systems", [])
	var stair_grid := {}
	var marker_grid := {}
	var polys: Array = []
	for f in GRID_FRACTIONS:
		var fr: Array = f
		var nm := NavigationMesh.new()
		nm.agent_radius = AGENT_RADIUS
		nm.agent_height = AGENT_HEIGHT
		nm.agent_max_climb = AGENT_MAX_CLIMB
		nm.agent_max_slope = AGENT_MAX_SLOPE
		nm.cell_size = CELL_SIZE
		nm.cell_height = CELL_HEIGHT
		nm.filter_baking_aabb = AABB(bounds.position - pad + Vector3(
			float(fr[0]) * CELL_SIZE, float(fr[1]) * CELL_HEIGHT,
			float(fr[2]) * CELL_SIZE), bounds.size + pad * 2.0)
		NavigationServer3D.bake_from_source_geometry_data(nm, src)
		polys.append(nm.get_polygon_count())
		var graph := _poly_graph(nm)
		for sysd in systems:
			if sysd.get("role") == "decorative_nontraversable":
				continue
			var eps: Variant = sysd.get("nav_endpoints")
			if eps == null or eps.get("lower") == null or eps.get("upper") == null:
				continue
			var lo_hit := _snap(nm, _to_godot(eps["lower"]))
			var hi_hit := _snap(nm, _to_godot(eps["upper"]))
			var ok: bool = lo_hit["dist"] <= SNAP_MAX and hi_hit["dist"] <= SNAP_MAX \\
				and _connected(graph, lo_hit["poly"], hi_hit["poly"])
			var sid := str(sysd.get("id", "?"))
			if not stair_grid.has(sid):
				stair_grid[sid] = []
			stair_grid[sid].append(ok)
		var mk := _check_markers(gp, nm, graph, false)
		for row in mk.get("detail", []):
			var mname: String = row["name"]
			if not marker_grid.has(mname):
				marker_grid[mname] = []
			marker_grid[mname].append(bool(row["reachable"]))
	var fragile_stairs: Array = []
	for rep in result["stairs"]:
		var sid := str(rep.get("id", "?"))
		if stair_grid.has(sid):
			rep["grid"] = stair_grid[sid]
			if stair_grid[sid].has(false) and stair_grid[sid].has(true):
				fragile_stairs.append(sid)
	var fragile_markers: Array = []
	var mk_base: Dictionary = result["markers"]
	for row in mk_base.get("detail", []):
		var mname: String = row["name"]
		if marker_grid.has(mname):
			row["grid"] = marker_grid[mname]
			if marker_grid[mname].has(false) and marker_grid[mname].has(true):
				fragile_markers.append(mname)
	result["grid"] = {"origins": GRID_FRACTIONS.size(), "fractions": GRID_FRACTIONS,
					  "cell": [CELL_SIZE, CELL_HEIGHT], "pad_m": GRID_PAD_M,
					  "polys": polys, "fragile_stairs": fragile_stairs,
					  "fragile_markers": fragile_markers}
	print("[nav-gate] grid: %d origins, polys %s; connects at only some: stairs %s, markers %s"
		% [GRID_FRACTIONS.size(), str(polys), str(fragile_stairs), str(fragile_markers)])


func _to_godot(p: Array) -> Vector3:
'''

PY_SIG_OLD = '''def scope_markers(markers, footprint, stairs_ok=True):
'''
PY_SIG_NEW = '''def scope_markers(markers, footprint, stairs_ok=True, stairs_grid_ok=True):
'''

PY_UNREACHED_OLD = '''    unreached = [r for r in interior if not r.get("reachable")]
'''
PY_UNREACHED_NEW = '''    unreached = [r for r in interior if not r.get("reachable")]
    # REACHED HERE, BUT NOT WHEREVER THE GRID FALLS (0.189.0). `grid` is the
    # gate's sweep: the same marker at eight more voxel-grid origins. A marker
    # this bake reached and some of those did not is one a level reaches or
    # not by where the shell lands -- deli_a03's objective, 2026-10-06. Kept
    # out of `interior_unreachable`, whose string format other tools parse.
    fragile = [r for r in interior if r.get("reachable")
               and isinstance(r.get("grid"), list) and not all(r["grid"])]
    markers["interior_grid_fragile"] = [
        "%s (%d/%d grid origins)" % (r.get("name", "?"),
                                     sum(1 for g in r["grid"] if g), len(r["grid"]))
        for r in fragile]
'''

PY_STAIRS_OLD = '''    if not stairs_ok:
        return markers, False, (
            "a stair is not traversable, so this shell cannot be walked "
            "whatever its markers say" + tail)
'''
PY_STAIRS_NEW = '''    if not stairs_ok:
        return markers, False, (
            "a stair is not traversable, so this shell cannot be walked "
            "whatever its markers say" + tail)
    if not stairs_grid_ok:
        return markers, False, (
            "a stair traverses at only some voxel-grid origins, so whether a "
            "level can climb it depends on where the shell lands" + tail)
'''

PY_DECIDE_OLD = '''    if unreached:
        return markers, False, (
            "%d of %d interior marker(s) unreachable from spawn: %s"
            % (len(unreached), len(interior),
               ", ".join(markers["interior_unreachable"][:4])) + tail)
    return markers, True, (
'''
PY_DECIDE_NEW = '''    if unreached:
        return markers, False, (
            "%d of %d interior marker(s) unreachable from spawn: %s"
            % (len(unreached), len(interior),
               ", ".join(markers["interior_unreachable"][:4])) + tail)
    if fragile:
        return markers, False, (
            "%d of %d interior marker(s) reachable from spawn at only some "
            "voxel-grid origins, so whether a level reaches them depends on "
            "where the shell lands: %s"
            % (len(fragile), len(interior),
               ", ".join(markers["interior_grid_fragile"][:4])) + tail)
    return markers, True, (
'''

PY_CALL_OLD = '''        scoped, navigable, why = scope_markers(
            result["markers"], footprint,
            stairs_ok=bool(result.get("stairs_ok", result.get("ok", False))))
'''
PY_CALL_NEW = '''        scoped, navigable, why = scope_markers(
            result["markers"], footprint,
            stairs_ok=bool(result.get("stairs_ok", result.get("ok", False))),
            stairs_grid_ok=not grid_fragile_stairs(result))
'''

PY_HELPER_ANCHOR = '''#: Marker types the gate asks about. Mirrors the list in `nav_gate.gd`
'''
PY_HELPER_NEW = '''def grid_fragile_stairs(result):
    """Ids of the stairs the gate's grid sweep found connected at some origins
    and not others. A result written before 0.189.0 has no `grid` and answers
    none, which is what it measured."""
    out = []
    for st in result.get("stairs") or []:
        g = st.get("grid")
        if isinstance(g, list) and any(g) and not all(g):
            out.append(st.get("id", "?"))
    return out


#: Marker types the gate asks about. Mirrors the list in `nav_gate.gd`
'''

PY_VERDICT_OLD = '''    for st in result.get("stairs", []):
        lines.append(f"stair {st.get('id')}: {st.get('status')} "
                     f"({st.get('detail', '')})")
'''
PY_VERDICT_NEW = '''    for st in result.get("stairs", []):
        lines.append(f"stair {st.get('id')}: {st.get('status')} "
                     f"({st.get('detail', '')})")
        g = st.get("grid")
        if isinstance(g, list) and any(g) and not all(g):
            lines.append(f"  grid: traverses at {sum(1 for x in g if x)} of "
                         f"{len(g)} voxel-grid origins")
'''

PY_VERDICT2_OLD = '''        for d in mk.get("exterior_deferred", []):
            lines.append(f"  deferred to site scope: {d.get('name')} "
                         f"(snap {d.get('snap')}m, outside the footprint)")
'''
PY_VERDICT2_NEW = '''        for d in mk.get("exterior_deferred", []):
            lines.append(f"  deferred to site scope: {d.get('name')} "
                         f"(snap {d.get('snap')}m, outside the footprint)")
        for u in mk.get("interior_grid_fragile", []):
            lines.append(f"  interior, reached at only some grid origins: {u}")
'''

EDITS = {
    DC / "godot/addon/deli_counter/nav_gate.gd": [
        (GD_CONST_OLD, GD_CONST_NEW), (GD_CALL_OLD, GD_CALL_NEW),
        (GD_SIG_OLD, GD_SIG_NEW), (GD_PRINT_OLD, GD_PRINT_NEW),
        (GD_FUNC_ANCHOR, GD_FUNC_NEW)],
    DC / "nav_gate.py": [
        (PY_SIG_OLD, PY_SIG_NEW), (PY_UNREACHED_OLD, PY_UNREACHED_NEW),
        (PY_STAIRS_OLD, PY_STAIRS_NEW), (PY_DECIDE_OLD, PY_DECIDE_NEW),
        (PY_CALL_OLD, PY_CALL_NEW), (PY_HELPER_ANCHOR, PY_HELPER_NEW),
        (PY_VERDICT_OLD, PY_VERDICT_NEW), (PY_VERDICT2_OLD, PY_VERDICT2_NEW)],
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
