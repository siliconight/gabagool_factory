"""Deli Counter 0.206.0: ceiling rows laid to the room's work plane, on the ceiling's grid.

Roadmap 229, the walker's ask of 2026-10-10: indoor light fixtures should "not always be in a
perfect line, so it looks a little less robotic". Every room had one fluorescent row at its
centre along its longer axis (513 of 513 shipped rows, `docs/findings/fixture_rows/`). Now a room
takes as many rows across its width as its work plane asks (WOOD's rule, rows at most 1.5 x the
work-surface-to-lamp height apart), each row's line on the ceiling's 0.6 m tile or 0.4 m joist
pitch, and a home's room one fixture at its centre; the bulbs below grade are untouched.

Anchored edits, every file pinned by hash, every anchor once, nothing written until all match:
- `lights.py`: the constants after `_FIXTURE_GAP`, the helpers (`_work_plane`, `_ceiling_pitch`,
  `_snap`, `_rows_for_room`) before `_row_for_bounds`, `_colinear_shift` taking the row's own
  `line`, the report's `rows_laid`, and the room loop laying its rows (the old block is read from
  `dc_fixture_rows/lights_rows_old.py.txt`, cut from the file, so it cannot be mistyped);
- `deli_counter.py`: the build line says how many rows were laid;
- `docs/LIGHT_MANIFEST.md`: the derived-row paragraph;
- `test_lights_voids.py`, `test_lights_partitions.py`: their rooms narrowed to one row, the
  partition report gaining `rows_laid`.
New file, refused if it exists: `test_fixture_rows.py`. CHANGELOG and VERSION from
`dc_fixture_rows/CHANGELOG_0.206.0.md`. Then, chained:

    python patches/patch_dc_fixture_rows.py --suite-pending && cd deli_counter && python -m pytest -q

and `python build.py --all` for the library; `--draft` applies to a `DC_ROOT` copy.
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_fixture_rows"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

#: sha256[:16] of each file as read on 2026-10-10 for this patch (Deli Counter 0.205.0)
SHA = {"lights.py": "7d42ba7f98146bb0", "deli_counter.py": "ef26e373fb6a70d7",
       "test_lights_voids.py": "a537c7bde3fa0a64",
       "test_lights_partitions.py": "82c9887addce4594",
       "test_storefront_reach.py": "cf7eb35afe1ae170",
       "test_storefront_spill.py": "af97143ebfb1d227",
       "test_club_rooms.py": "75df0446105b0e65",
       "docs/LIGHT_MANIFEST.md": "4a09eef2bb0f9cf8"}


def _read(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


# --- lights.py ---------------------------------------------------------
GAP_OLD = "_FIXTURE_DEPTH = 0.3\n_FIXTURE_GAP = _CEILING_GAP\n"
ROW_FN = "def _row_for_bounds(bounds):\n"
CS_OLD = "def _colinear_shift(bounds, rot, walls, clear):\n"
CS_NEW = "def _colinear_shift(bounds, rot, walls, clear, line=None):\n"
CS_BODY_OLD = (
    "    not a lighting one.\n"
    "    \"\"\"\n"
    "    minx, miny, maxx, maxy = bounds\n"
    "    along_x = abs(rot) < 45.0\n"
    "    if along_x:\n"
    "        perp, lo, hi, a0, a1 = (miny + maxy) / 2.0, miny, maxy, minx, maxx\n"
    "    else:\n"
    "        perp, lo, hi, a0, a1 = (minx + maxx) / 2.0, minx, maxx, miny, maxy\n")
CS_BODY_NEW = (
    "    not a lighting one. ``line`` (0.206.0) is the row's own perpendicular\n"
    "    coordinate when it is not the room's centre.\n"
    "    \"\"\"\n"
    "    minx, miny, maxx, maxy = bounds\n"
    "    along_x = abs(rot) < 45.0\n"
    "    if along_x:\n"
    "        perp, lo, hi, a0, a1 = (miny + maxy) / 2.0, miny, maxy, minx, maxx\n"
    "    else:\n"
    "        perp, lo, hi, a0, a1 = (minx + maxx) / 2.0, minx, maxx, miny, maxy\n"
    "    if line is not None:\n"
    "        perp = line\n")
REP_OLD = "    rep.setdefault(\"counter_accents\", 0)\n"
REP_NEW = REP_OLD + "    rep.setdefault(\"rows_laid\", 0)\n"
ROWS_START = "        rot, count, spacing = _row_for_bounds(bounds)\n"
ROWS_END_MARK = "\"id\": base_id if len(runs) == 1 else"

# --- deli_counter.py ---------------------------------------------------
PRINT_OLD = "          f\"{_report.get('rows_shifted', 0)} row(s) moved off a wall; \"\n"
PRINT_NEW = PRINT_OLD + "          f\"{_report.get('rows_laid', 0)} row(s) laid to the work; \"\n"

# --- docs/LIGHT_MANIFEST.md --------------------------------------------
DOC_OLD = (
    "- **One `fluorescent` row per room** \u2014 at the room center, mounted just below\n"
    "  the ceiling (`center.z + story_height`), running along the room's longer\n"
    "  axis, fixture count scaled to the room's length. `reacts_to_alarm: true`.\n")
DOC_NEW = (
    "- **`fluorescent` rows per room, laid to the work (0.206.0)** \u2014 along the\n"
    "  room's longer axis, mounted just below the ceiling, and across it as many\n"
    "  as the room's work plane asks: rows at most 1.5 x the height from the work\n"
    "  surface to the lamp apart (a desk in an office, a counter on a sales\n"
    "  floor, the floor elsewhere), each row's line on the ceiling's 0.6 m tile\n"
    "  or 0.4 m joist pitch from the building's origin, held to 3 rows and 12\n"
    "  lamps a room; a home's room gets one fixture at its centre. The first row\n"
    "  keeps the id `<room>_ceiling`, further rows `<room>_ceiling_r<k>`.\n"
    "  `reacts_to_alarm: true`.\n")

# --- the tests that assumed one row a room ------------------------------
VOIDS_OLD = (
    "# The room from the measured case: 24 m wide on story 0, row along x.\n"
    "OFFICE = {\"id\": \"manager_office\", \"story\": 0, \"bounds\": [-15.0, 4.0, 0.0, 9.0],\n"
    "          \"center\": [-7.5, 6.5, 0.0]}\n")
VOIDS_NEW = (
    "# The room from the measured case: 24 m wide on story 0, row along x. Since\n"
    "# 0.206.0 a 5 m deep office takes two rows over its desks; this slice of it,\n"
    "# 3.4 m deep, keeps the one row the argument below is about.\n"
    "OFFICE = {\"id\": \"manager_office\", \"story\": 0, \"bounds\": [-15.0, 4.0, 0.0, 7.4],\n"
    "          \"center\": [-7.5, 5.7, 0.0]}\n")
PART_OLD = (
    "#: the hospital lobby: x longer, row along x at y = -7.5, count 5, spacing 8\n"
    "LOBBY = {\"id\": \"lobby\", \"story\": 0, \"bounds\": [-20.0, -15.0, 20.0, 0.0],\n"
    "         \"role\": \"safe_room\", \"center\": [0.0, -7.5, 0.0]}\n")
PART_NEW = (
    "#: the hospital lobby: x longer, row along x, count 5, spacing 8. Since\n"
    "#: 0.206.0 the 15 m deep lobby takes three rows across; this 4.5 m slice of\n"
    "#: it keeps the one row, with the same five lamps at the same x.\n"
    "LOBBY = {\"id\": \"lobby\", \"story\": 0, \"bounds\": [-20.0, -4.5, 20.0, 0.0],\n"
    "         \"role\": \"safe_room\", \"center\": [0.0, -2.25, 0.0]}\n")
PART_REP_OLD = (
    "    assert rep == {\"rows_shifted\": 0, \"nudged\": 2, \"dropped\": 0, \"club_rooms\": 0,\n"
    "                   \"tv_screens\": 0, \"back_bars\": 0, \"storefront_rows\": 0,\n"
    "                   \"storefront_spills\": 0, \"counter_accents\": 0}\n")
PART_REP_NEW = (
    "    assert rep == {\"rows_shifted\": 0, \"nudged\": 2, \"dropped\": 0, \"club_rooms\": 0,\n"
    "                   \"tv_screens\": 0, \"back_bars\": 0, \"storefront_rows\": 0,\n"
    "                   \"storefront_spills\": 0, \"counter_accents\": 0, \"rows_laid\": 1}\n")
# gas_station_a02's 23 x 12 sales floor over its counters takes three rows at y -9.0, -4.8 and
# -1.2 (the tile grid), and the 9 x 12 food service two at x 9.0 and 13.8: each row's reach is
# its own, and the spill carries the room's farthest.
REACH_OLD_1 = (
    "def test_a_row_parallel_to_its_storefront_reaches_across_the_room():\n"
    "    row = _rows([SALES], SOUTH_GLASS)[\"sales_floor\"]\n"
    "    assert row[\"type\"] == \"fluorescent\"\n"
    "    assert row[\"reach\"] == 6.0          # the row at y -5, the glass at -11\n")
REACH_NEW_1 = (
    "def _all_rows(rooms, storefronts):\n"
    "    \"\"\"Every ceiling row of each room, in order (0.206.0 lays more than one).\"\"\"\n"
    "    out = {}\n"
    "    for a in lights.derive_light_anchors(rooms, [], 4.2, cap_thick=_cap, wall_thick=0.3,\n"
    "                                         storefronts=storefronts):\n"
    "        if a[\"type\"] in (\"fluorescent\", \"pendant\"):\n"
    "            out.setdefault(a[\"room\"], []).append(a)\n"
    "    return out\n"
    "\n"
    "\n"
    "def test_a_row_parallel_to_its_storefront_reaches_across_the_room():\n"
    "    # 0.206.0 lays the 12 m deep sales floor in three rows over its counters, at y -9.0,\n"
    "    # -4.8 and -1.2 (the tile grid); each reaches the glass at -11 from its own line\n"
    "    rows = _all_rows([SALES], SOUTH_GLASS)[\"sales_floor\"]\n"
    "    assert [a[\"type\"] for a in rows] == [\"fluorescent\"] * 3\n"
    "    assert [a[\"reach\"] for a in rows] == [2.0, 6.2, 9.8]\n")
REACH_OLD_2 = (
    "    assert _rows([food], south)[\"food_service\"][\"reach\"] == 2.0\n"
    "    # the largest of the glass lines it faces\n"
    "    assert _rows([food], south + east)[\"food_service\"][\"reach\"] == 4.5\n")
REACH_NEW_2 = (
    "    # two rows across the 9 m room since 0.206.0, at x 9.0 and 13.8: both reach the south\n"
    "    # glass from their lamp at y -9, and the east glass at x 16 from their own line\n"
    "    assert [a[\"reach\"] for a in _all_rows([food], south)[\"food_service\"]] == [2.0, 2.0]\n"
    "    # the largest of the glass lines each faces\n"
    "    assert [a[\"reach\"] for a in _all_rows([food], south + east)[\"food_service\"]] == [7.0, 2.2]\n")
REACH_OLD_3 = (
    "def test_the_gas_stations_sales_floor_reaches_its_glass():\n"
    "    a = {x[\"id\"]: x for x in _lights(\"gas_station_a02\")}\n"
    "    assert a[\"sales_floor_ceiling\"][\"reach\"] == 6.0\n")
REACH_NEW_3 = (
    "def test_the_gas_stations_sales_floor_reaches_its_glass():\n"
    "    # three rows since 0.206.0, each reaching the glass from its own line; the built\n"
    "    # manifest (`build.py --all`) agrees with the pure case above to the centimetre\n"
    "    a = {x[\"id\"]: x for x in _lights(\"gas_station_a02\")}\n"
    "    assert [a[k][\"reach\"] for k in (\"sales_floor_ceiling\", \"sales_floor_ceiling_r1\",\n"
    "                                    \"sales_floor_ceiling_r2\")] == [2.0, 6.2, 9.8]\n")
SPILL_OLD_1 = "    row = next(x for x in a if x[\"id\"] == \"sales_floor_ceiling\")\n"
SPILL_NEW_1 = (
    "    rows = [x for x in a if x[\"type\"] == \"fluorescent\" and x[\"room\"] == \"sales_floor\"]\n"
    "    row = rows[0]\n"
    "    # the spill carries the room's FARTHEST row's reach (0.206.0: three rows at 2.0, 6.2, 9.8 m)\n"
    "    reach = max(x[\"reach\"] for x in rows)\n")
SPILL_OLD_2 = "        assert s[\"drop\"] == row[\"drop\"] and s[\"reach\"] == row[\"reach\"]\n"
SPILL_NEW_2 = "        assert s[\"drop\"] == row[\"drop\"] and s[\"reach\"] == reach\n"
CLUB_OLD_1 = (
    "    types = collections.Counter(a[\"type\"] for a in n[\"anchors\"])\n"
    "    assert types == {\"fluorescent\": 1, \"neon\": 1, \"room_ambient\": 1}, types\n"
    "    ids = [a[\"id\"] for a in n[\"anchors\"]]\n"
    "    # the room's ceiling light first and its box last, as every reader assumes\n"
    "    assert ids == [\"bullpen_ceiling\", \"wall_tv_r00000001_1_screen\", \"bullpen_ambient\"], ids\n")
CLUB_NEW_1 = (
    "    types = collections.Counter(a[\"type\"] for a in n[\"anchors\"])\n"
    "    # three rows over the 20 x 12 bullpen since 0.206.0\n"
    "    assert types == {\"fluorescent\": 3, \"neon\": 1, \"room_ambient\": 1}, types\n"
    "    ids = [a[\"id\"] for a in n[\"anchors\"]]\n"
    "    # the room's ceiling lights first and its box last, as every reader assumes\n"
    "    assert ids == [\"bullpen_ceiling\", \"bullpen_ceiling_r1\", \"bullpen_ceiling_r2\",\n"
    "                   \"wall_tv_r00000001_1_screen\", \"bullpen_ambient\"], ids\n")
CLUB_OLD_2 = (
    "    types = collections.Counter(a[\"type\"] for a in n[\"anchors\"])\n"
    "    assert types == {\"fluorescent\": 1, \"room_ambient\": 1}, types\n")
CLUB_NEW_2 = (
    "    types = collections.Counter(a[\"type\"] for a in n[\"anchors\"])\n"
    "    assert types == {\"fluorescent\": 3, \"room_ambient\": 1}, types   # three rows since 0.206.0\n")


def _rows_block():
    """The room loop's row block as cut from 0.205.0's lights.py, from the row derivation
    through the anchor's id line, and the text that replaces it."""
    old = _read("lights_rows_old.py.txt")
    i = old.index(ROWS_START)
    j = old.index(ROWS_END_MARK)
    j = old.index("\n", j) + 1
    block = old[i:j]
    assert block.count("\n") == 38, block.count("\n")
    new = _read("lights_rows_new.py.txt")
    assert new.startswith("        # THE ROWS (0.206.0") and new.endswith("                \"id\": rid,\n")
    return block, new


def _edits():
    constants = _read("lights_constants.py.txt")
    assert constants.startswith("_FIXTURE_GAP = _CEILING_GAP\n")
    helper = _read("lights_helper.py.txt")
    assert helper.endswith("\n\n\n"), "the helper must end in two blank lines"
    block, new = _rows_block()
    # (old, new, how many times old stands in the file)
    return {
        "lights.py": [
            (GAP_OLD, "_FIXTURE_DEPTH = 0.3\n" + constants, 1),
            (ROW_FN, helper + ROW_FN, 1),
            (CS_OLD, CS_NEW, 1),
            (CS_BODY_OLD, CS_BODY_NEW, 1),
            (REP_OLD, REP_NEW, 1),
            (block, new, 1)],
        "deli_counter.py": [(PRINT_OLD, PRINT_NEW, 1)],
        "docs/LIGHT_MANIFEST.md": [(DOC_OLD, DOC_NEW, 1)],
        "test_lights_voids.py": [(VOIDS_OLD, VOIDS_NEW, 1)],
        "test_lights_partitions.py": [(PART_OLD, PART_NEW, 1), (PART_REP_OLD, PART_REP_NEW, 1)],
        "test_storefront_reach.py": [(REACH_OLD_1, REACH_NEW_1, 1), (REACH_OLD_2, REACH_NEW_2, 1),
                                     (REACH_OLD_3, REACH_NEW_3, 1)],
        "test_storefront_spill.py": [(SPILL_OLD_1, SPILL_NEW_1, 1), (SPILL_OLD_2, SPILL_NEW_2, 1)],
        "test_club_rooms.py": [(CLUB_OLD_1, CLUB_NEW_1, 1), (CLUB_OLD_2, CLUB_NEW_2, 1)],
    }


NEW = {"test_fixture_rows.py": "test_fixture_rows.py"}
CHANGELOG_HEAD = "## [0.205.0] - a den's windows are drawn shut\n"


def _stage():
    staged = {}
    for rel, pairs in _edits().items():
        p = DC / rel
        d = p.read_bytes()
        got = hashlib.sha256(d).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        assert b"\r" not in d, (rel, "has CR; this patch writes LF")
        t = d.decode("utf-8")
        assert "_rows_for_room" not in t and "rows_laid" not in t, (rel, "already applied")
        for old, new, times in pairs:
            n = t.count(old)
            assert n == times, (rel, n, times, old[:70])
            t = t.replace(old, new)
        staged[p] = t.encode("utf-8")
    for rel, src in NEW.items():
        p = DC / rel
        assert not p.exists(), (rel, "already exists")
        staged[p] = _read(src).encode("utf-8")
    return staged


def main():
    if DRAFT and not os.environ.get("DC_ROOT"):
        sys.exit("refusing: --draft is for a DC_ROOT copy, never the repo")
    v = (DC / "VERSION").read_bytes()
    assert v == b"Deli Counter 0.205.0", repr(v)
    staged = _stage()
    entry = _read("CHANGELOG_0.206.0.md")
    assert entry.startswith("## [0.206.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "").replace("RESULT_CENSUS", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r" not in data, "CHANGELOG.md is not LF"
    text = data.decode("utf-8")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # Every anchor and hash matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).encode("utf-8"))
    (DC / "VERSION").write_bytes(b"Deli Counter 0.206.0")
    print("Deli Counter 0.205.0 -> 0.206.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
