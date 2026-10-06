"""Lot 0.97.2, second half: `_vertical_access` samples the anchor's column
height by height, keeping the old concession's window.

`patch_lot_vertical_access.py` asked for the navmesh point closest to a
vertical segment over and under the anchor. Proven on cold run 9185's
seed_9003 (a copy of its staged walk test), it made `home->proxy_2` and
`proxy_1->proxy_2` agree -- the goal -- but it FAILED `proxy_2->proxy_3`.
That leg is a drop from the deli's upstairs south edge, (-56.0, 3.6, 17.8),
to the street 2.7 m out and 3.3 m down, and the old concession passed it on
both 9179 and 9185. A segment's closest point is the street under its own
foot every time, so the upstairs edge 2.7 m away was never considered.
Stricter than the rule it replaced, and not on purpose.

Now each height from 1.5 m to VERTICAL_REACH_M above and below the anchor is
asked for its nearest navmesh point. A point counts if it lies within the old
window, 1.5 x SNAP_MAX across and more than 1 m up or down, and a strict
route from the start reaches it. That is what Godot's fallback returns when
it works, decided without it.

    python patch_lot_vertical_access_column.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GD = ROOT / "lot" / "godot" / "addons" / "heist_nav_qa" / "nav_qa_director.gd"
TEST = ROOT / "lot" / "tests" / "test_nav_qa_vertical_access.py"

LOOP_OLD = '''	for dir in [-1.0, 1.0]:
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
'''
LOOP_NEW = '''	#
	# Asked HEIGHT BY HEIGHT, nearest first, keeping the old concession's
	# window (1.5 x SNAP_MAX across, more than 1 m up or down). One closest
	# point to the whole column found the floor under the anchor's own foot
	# every time, and so failed a drop from a ledge 2.7 m out that the old
	# rule passed -- 9185 seed_9003's proxy_2->proxy_3.
	var dy := 1.0 + STAND_STEP_M
	while dy <= VERTICAL_REACH_M:
		for dir in [-1.0, 1.0]:
			var sgn: float = dir
			var c := NavigationServer3D.map_get_closest_point(
				map, target + Vector3(0.0, sgn * dy, 0.0))
			# map_get_closest_point answers Vector3.ZERO when it has nothing.
			if c == Vector3.ZERO and target.distance_to(Vector3.ZERO) > STAND_STEP_M:
				continue
			if Vector2(c.x - target.x, c.z - target.z).length() > SNAP_MAX * 1.5:
				continue
			if absf(c.y - target.y) <= 1.0:
				continue
			if _reaches(map, from_pt, c, true):
				return c
		dy += STAND_STEP_M
	return null
'''

TEST_OLD = '''    # asked of the anchor: navmesh straight under and over it ...
    assert "map_get_closest_point_to_segment" in body
    assert "VERTICAL_REACH_M" in body
'''
TEST_NEW = '''    # asked of the anchor: its column, height by height, within the reach ...
    assert "map_get_closest_point(" in body
    assert "while dy <= VERTICAL_REACH_M" in body
    # ... inside the old concession's window, so a drop off a ledge beside the
    # anchor still counts (9185 seed_9003, proxy_2->proxy_3) ...
    assert "SNAP_MAX * 1.5" in body and "<= 1.0" in body
'''

EDITS = {GD: [(LOOP_OLD, LOOP_NEW)], TEST: [(TEST_OLD, TEST_NEW)]}


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
