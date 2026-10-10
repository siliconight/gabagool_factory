"""Roadmap 229: Deli Counter 0.206.0 and Lux 0.74.0 landed; the library's rows counted; 9229 prices them.

Replaces 229's status block and adds the landing to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_229_landed.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: OPEN 2026-10-10 -- the walker's ask, grounded and not yet built: 513 of 513 shipped "
    "fluorescent rows stand on their room's centreline along its longer axis, 303 of them at the "
    "five-lamp cap (`docs/findings/fixture_rows/`); the nine references are digested in "
    "`docs/reference/INDOOR_FIXTURE_PLACEMENT_GUIDE.md`. Owner: Deli Counter, with Zoo for the "
    "species and Lux for the rigs.*\n"
)
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- the first step is shipped and not yet seen. Deli Counter "
    "0.206.0 (`patches/patch_dc_fixture_rows.py`) lays a room's ceiling rows to its work plane "
    "(WOOD's rule: rows at most 1.5 x the work-surface-to-lamp height apart, a desk in an office, "
    "a counter on a sales floor, the floor elsewhere), each row's line on the 0.6 m tile or 0.4 m "
    "joist pitch, a home's room one fixture at its centre; the library rebuilt reads 1,156 rows "
    "where 513 stood, 1,035 off their room's centreline, 4,217 lamps against 2,083 "
    "(`docs/findings/fixture_rows/row_census_0206.txt`). Lux 0.74.0 fails one tube a ROOM across "
    "its rows. Cold run 9229 (restaurant_row_001, the level 9225 built) prices the lamps and shoots "
    "the rooms before and after. Left: the layout by use (aisles, benches, the bar), structural "
    "causes beyond the grid, the species (strip light, sconce, high-bay, exit sign), and the long "
    "hall's thinned rows. Owner: Deli Counter, with Zoo for the species and Lux for the rigs.*\n"
)
BODY_ANCHOR = (
    "Owner: Deli Counter, with Zoo for the species and Lux for the rigs.\n"
)
ADDED = (
    "\n**THE FIRST STEP, SHIPPED 2026-10-10.** Deli Counter 0.206.0 (`patches/patch_dc_fixture_rows.py`, "
    "`lights._rows_for_room`): with A the height from the work plane to the lamp and B = 1.5 A, a "
    "room W wide takes ceil(W / B - 0.3) rows across its shorter axis (the slack keeps a 4 m "
    "office under one row), the lamps along each at B, held to 3 rows and 12 lamps a room; the "
    "work plane is matched on the room's role and id with the furnish's own words (0.75 m where "
    "desks are seeded, 1.0 m where it sells or serves, the floor in a hall, a stockroom, a bay); "
    "each row's line is snapped to 0.6 m tiles over a desk or a counter and 0.4 m joists "
    "elsewhere, from the building's origin; a home's room is one fixture at its centre; the bulbs "
    "below grade are 0.205.0's. The first row keeps `<room>_ceiling`, so every authored override "
    "binds; further rows are `_r<k>`. Ten pure tests; the void, partition, storefront-reach, spill "
    "and club suites keep their arguments on rooms narrowed to one row or on every row's own "
    "reach (gas_station_a02's 12 m sales floor: three rows at y -9.0, -4.8, -1.2 reaching the glass "
    "at 2.0, 6.2 and 9.8 m, the built manifest agreeing with the pure case to the centimetre). "
    "Suite 1,378 before and after the library rebuild. Lux 0.74.0 (`patches/patch_lux_failing_room.py`): "
    "`LuxFixtureSpawner.room_of` groups the markers by the anchor's room, so a three-row sales "
    "floor stutters one tube, not three (selftest 60 ok).\n"
    "- **The census after the rebuild** (`docs/findings/fixture_rows/row_census_0206.txt`): 1,156 "
    "rows in 475 rooms, 400 rooms with more than one, 1,035 rows off the centreline and 121 on it, "
    "every row along the longer axis; lamps a row 4 x 646, 5 x 201, 3 x 124, 2 x 71, 1 x 114 -- "
    "4,217 lamps, twice 0.205.0's 2,083, which 9229 prices against 9225's package (the same "
    "level: 17 rows and 72 lamps over its three buildings before, `site_9225_before.txt`).\n"
    "- **A trade to revisit:** the room cap thins a long hall's three rows to four lamps each, so "
    "the longest rooms run 10 to 14.5 m between lamps where 0.205.0 ran 11.6 at most; a long "
    "narrow room should favour lamps along over rows across.\n"
    "- **Not yet seen.** Frames at interior stations (`tools/room_stations.py`) on 9229's package "
    "against 9225's are the evidence; the walker's eye is the gate.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + ADDED).replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**229. "), "229's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 229: the first step shipped, 9229 prices it")


if __name__ == "__main__":
    main()
