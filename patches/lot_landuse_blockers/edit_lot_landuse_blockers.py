"""Lot 0.130.0 on a CLONE (<repo>): the land-use census counts a street's Empties (`blockers`) as built land (the
walker's walk of cold run 9386, finding 7). Anchored; refuses on a miss.

    python edit_lot_landuse_blockers.py <repo>
"""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("site_landuse.py", [
    ("""  * ``building``  -- a building's rotated footprint (`site_extent.
    rotated_footprint`);""",
     """  * ``building``  -- a building's rotated footprint (`site_extent.
    rotated_footprint`), and an EMPTY's: a `blockers` entry, its `size_x` by
    `size_y` (0.130.0);"""),
    ("""    for b in site_spec.get("buildings", []) or []:
        r = site_extent.rotated_footprint(b)
        if r is not None:
            buildings[b["id"]] = r
            _paint(grid, rect, r, lambda x, y: True, "building")""",
     """    for b in site_spec.get("buildings", []) or []:
        r = site_extent.rotated_footprint(b)
        if r is not None:
            buildings[b["id"]] = r
            _paint(grid, rect, r, lambda x, y: True, "building")
    # AN EMPTY IS BUILT LAND (0.130.0). The walker, walking cold run 9386, of
    # broad ground round restaurant_row_001: "this empty space goes against
    # the doc i sent you about the value of urban land". Measuring it found
    # this census wrong first: a street's Empties are the spec's `blockers`,
    # never painted, so a row of 26 rowhomes read as remainder -- 58.4 %
    # where 47.7 % is unclaimed (the factory's
    # `docs/findings/walk_2026-10-23_9386/landuse/`). Painted as building
    # land here, after the buildings and before the ground, so a cell takes
    # its first use as before. Not in `buildings`: separation and the
    # building line stay about the buildings a mission enters, as before.
    for bl in site_spec.get("blockers", []) or []:
        if "size_x" not in bl or "size_y" not in bl:
            continue
        r = site_extent.rotated_footprint(dict(bl, footprint=[bl["size_x"], bl["size_y"]]))
        if r is not None:
            _paint(grid, rect, r, lambda x, y: True, "building")"""),
])

TEST = '''"""The census counts an Empty as built land (0.130.0): a `blockers` entry's footprint is `building`, not remainder.
The walker, walking cold run 9386: "this empty space goes against the doc i sent you about the value of urban land"
-- and restaurant_row_001's 26 rowhomes had read as remainder. FAILS ON 0.129.0."""
import site_landuse


def _spec(blockers):
    return {"ground": {"size_x": 40, "size_y": 20}, "buildings": [], "roads": [], "paths": [],
            "blockers": blockers}


def _as_building(bl):
    """The same footprint as a mission's building: what the census has always measured a building's land as, its
    0.5 m cells included at the edges."""
    s = _spec([])
    s["buildings"] = [{"id": "b0", "at": bl["at"], "rot": bl["rot"], "footprint": [bl["size_x"], bl["size_y"]]}]
    return site_landuse.census(s)


def test_an_empty_is_building_land_not_remainder():
    bl = {"id": "e0", "at": [5.0, 0.0], "rot": 180, "size_x": 6.0, "size_y": 12.0}
    bare = site_landuse.census(_spec([]))
    one = site_landuse.census(_spec([bl]))
    assert bare["ok"] and one["ok"], (bare, one)
    assert bare["areas"]["building"] == 0.0
    assert one["areas"]["building"] == _as_building(bl)["areas"]["building"] > 0.0, one["areas"]
    assert one["areas"]["remainder"] == bare["areas"]["remainder"] - one["areas"]["building"]


def test_an_empty_turned_a_quarter_is_measured_turned():
    bl = {"id": "e0", "at": [0.0, 0.0], "rot": 90, "size_x": 6.0, "size_y": 12.0}
    assert site_landuse.census(_spec([bl]))["areas"]["building"] == _as_building(bl)["areas"]["building"]


def test_an_empty_is_not_a_building_the_mission_enters():
    c = site_landuse.census(_spec([{"id": "e0", "at": [5.0, 0.0], "rot": 0, "size_x": 6.0, "size_y": 12.0}]))
    assert c["nearest_building_gap"] == {}, c["nearest_building_gap"]
'''
(R / "tests" / "test_landuse_blockers.py").write_text(TEST, encoding="utf-8", newline="\n")
print("site_landuse paints blockers as building; tests/test_landuse_blockers.py")
