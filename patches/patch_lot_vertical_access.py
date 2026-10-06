"""Lot 0.97.2: the walk test decides ladder or drop access from the navmesh it
can see, never from where Godot's path to an unreachable target stops.

Cold run 9185 (roadmap 189): `_prove_path` passed an unreachable anchor as
"VERTICAL access" when the path Godot returned for it ended directly under
the anchor. For an unreachable target Godot 4.7 falls back to the nearest
point it reached -- and that fallback can fail inside the engine ("It's not
expect to not find the most reachable polygons",
nav_mesh_queries_3d.cpp:404), returning a path that stops beside the START.
The same anchor in the same navmesh then passed from `proxy_1` and failed
from `home`. 9179 passed deli_a03's objective and 9185 failed it, on
identical islands.

`_vertical_access` asks the question directly: is there standing room on
another storey straight under or over the anchor, within a ladder's reach,
that a strict route from the start reaches? Both `_prove_path` and the
non-strict `_reaches` use it. The answer no longer depends on the start's
position or on an engine fallback.

    python patch_lot_vertical_access.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GD = ROOT / "lot" / "godot" / "addons" / "heist_nav_qa" / "nav_qa_director.gd"

CONST_OLD = '''const STAND_DIRS := 12
'''
CONST_NEW = '''const STAND_DIRS := 12
# How far above or below an anchor a ladder or a drop can be the way in: the
# library's longest ladder (8.0 m, measured 2026-10-06 over
# deli_counter/build/*.gameplay.json) and one storey band. Further than that,
# the floor found is not one a ladder joins to this anchor.
const VERTICAL_REACH_M := 8.0 + STOREY_BAND
'''

REACHES_OLD = '''	if strict:
		return false
	var h_gap := Vector2(pe.x - to_snapped.x, pe.z - to_snapped.z).length()
	var v_gap := absf(pe.y - to_snapped.y)
	return h_gap <= SNAP_MAX * 1.5 and v_gap > 1.0
'''
REACHES_NEW = '''	if strict:
		return false
	return _vertical_access(map, from_snapped, to_snapped) != null
'''

PROVE_OLD = '''		var pe := path[path.size() - 1]
		var h_gap := Vector2(pe.x - sb.x, pe.z - sb.z).length()
		var v_gap := absf(pe.y - sb.y)
		if h_gap <= SNAP_MAX * 1.5 and v_gap > 1.0:
			# walkable route reaches directly below/above the anchor; the
			# remaining gap is pure vertical = ladder/drop access. That
			# traversal is game code (climb volumes), gated by Deli
			# Counter's ladder checks -- report as intel, don't fail.
			return {"leg": label, "ok": true, "vertical_access": true,
					"stand_offset_m": snappedf(far, 0.01),
					"detail": "walkable to (%.1f, %.1f, %.1f); %.1f m VERTICAL access (ladder/drop) to anchor at (%.1f, %.1f, %.1f)"
					% [pe.x, pe.y, pe.z, v_gap, sb.x, sb.y, sb.z]}
'''
PROVE_NEW = '''		var pe := path[path.size() - 1]
		# A walkable route to standing room directly below or above the
		# anchor; the remaining gap is pure vertical = ladder/drop access.
		# That traversal is game code (climb volumes), gated by Deli
		# Counter's ladder checks -- report as intel, don't fail. Decided by
		# _vertical_access, never by where `path` stopped (Lot 0.97.2).
		var va: Variant = _vertical_access(map, sa, sb)
		if va != null:
			var vv: Vector3 = va
			return {"leg": label, "ok": true, "vertical_access": true,
					"stand_offset_m": snappedf(far, 0.01),
					"detail": "walkable to (%.1f, %.1f, %.1f); %.1f m VERTICAL access (ladder/drop) to anchor at (%.1f, %.1f, %.1f)"
					% [vv.x, vv.y, vv.z, absf(vv.y - sb.y), sb.x, sb.y, sb.z]}
'''

FUNC_ANCHOR = '''func _anchor_reachability(map: RID, home: Vector3, proxies: Array) -> Array:
'''
FUNC_NEW = '''func _vertical_access(map: RID, from_pt: Vector3, target: Vector3) -> Variant:
	## Standing room on another storey straight under or over `target`, within
	## VERTICAL_REACH_M, that a strict route from `from_pt` reaches -- or null.
	##
	## THIS USED TO BE READ OFF THE END OF THE PATH TO `target`. For an
	## unreachable target Godot returns a path to the nearest point it reached,
	## and in 4.7 that fallback can fail inside the engine ("It's not expect to
	## not find the most reachable polygons", nav_mesh_queries_3d.cpp:404) and
	## return a path that stops beside the start. Cold run 9185: deli_a03's
	## objective passed from proxy_1 and failed from home, in one navmesh, and
	## 9179 had passed it from both (roadmap 189). The question is about the
	## anchor, so it is asked of the anchor.
	for dir in [-1.0, 1.0]:
		var sgn: float = dir
		var c := NavigationServer3D.map_get_closest_point_to_segment(
			map, target + Vector3(0.0, sgn * 1.0, 0.0),
			target + Vector3(0.0, sgn * VERTICAL_REACH_M, 0.0), false)
		# map_get_closest_point* answers Vector3.ZERO when it has nothing to say.
		if c == Vector3.ZERO and target.distance_to(Vector3.ZERO) > STAND_STEP_M:
			continue
		if Vector2(c.x - target.x, c.z - target.z).length() > SNAP_MAX * 1.5:
			continue
		if absf(c.y - target.y) <= 1.0:
			continue
		if _reaches(map, from_pt, c, true):
			return c
	return null


func _anchor_reachability(map: RID, home: Vector3, proxies: Array) -> Array:
'''

EDITS = {GD: [(CONST_OLD, CONST_NEW), (REACHES_OLD, REACHES_NEW),
              (PROVE_OLD, PROVE_NEW), (FUNC_ANCHOR, FUNC_NEW)]}


def main():
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
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
