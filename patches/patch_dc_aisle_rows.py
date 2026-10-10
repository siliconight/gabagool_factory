"""Deli Counter 0.207.0: ceiling rows over the aisles, between the shelf runs (roadmap 229, step 2).

Anchored edits in `lights.py` (the constants, `_rows_for_room` replaced and `_lanes_for_room`
added from `dc_aisle_rows/lights_rows_new.py.txt`, the room loop and the report), one in
`deli_counter.py` (the manifest line), eight tests appended to `test_fixture_rows.py`, the
partition test's report dict given the new count and the gas station's storefront reach test
asserting the shape rather than three pinned numbers; each file pinned by hash and each anchor
asserted once, nothing written on a miss; the file's own line
endings kept. CHANGELOG and VERSION from `dc_aisle_rows/CHANGELOG_0.207.0.md`. Then, chained:

    python patches/patch_dc_aisle_rows.py --suite-pending && cd deli_counter && python -m pytest -q

and `python build.py --all` for the library; `--draft` applies to a `DC_ROOT` copy.
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_aisle_rows"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv
SHA = {"lights.py": "5d5235fc80c9b77b", "test_fixture_rows.py": "86565578d5c84445",
       "deli_counter.py": "8ce639cb9ccc8168", "test_lights_partitions.py": "8dcef3220c15ffc2",
       "test_storefront_reach.py": "2ce94fb056e98975"}

# the gas station's library test pinned three reach values from a sales floor laid across;
# the built floor is laid to its gondolas now, so it asserts the shape instead
REACH_OLD = (
    '    # three rows since 0.206.0, each reaching the glass from its own line; the built\n'
    '    # manifest (`build.py --all`) agrees with the pure case above to the centimetre\n'
    '    a = {x["id"]: x for x in _lights("gas_station_a02")}\n'
    '    assert [a[k]["reach"] for k in ("sales_floor_ceiling", "sales_floor_ceiling_r1",\n'
    '                                    "sales_floor_ceiling_r2")] == [2.0, 6.2, 9.8]\n'
)
REACH_NEW = (
    '    # since 0.207.0 the built sales floor is laid to its gondolas and the cap\'s trade\n'
    '    # (the pure case above has no shelves and keeps its three rows), so the shape is\n'
    '    # asserted: every row reaches the glass from its own line, the nearer the shorter,\n'
    '    # and the first row keeps the original id\n'
    '    a = {x["id"]: x for x in _lights("gas_station_a02")}\n'
    '    rows = sorted((x["pos"][1], x["reach"]) for x in a.values()\n'
    '                  if x["type"] == "fluorescent" and x.get("room") == "sales_floor")\n'
    '    assert len(rows) >= 2 and "sales_floor_ceiling" in a\n'
    '    assert all(r > 0.0 for _y, r in rows)\n'
    '    assert [r for _y, r in rows] == sorted(r for _y, r in rows)\n'
)
VERSION_WAS, VERSION = b"Deli Counter 0.206.1", b"Deli Counter 0.207.0"
CHANGELOG_HEAD = "## [0.206.1] - a home's room in any building takes the home rule\n"

HOME_OLD = "_HOME_WORDS = (\"apartment\", \"hideout\", \"bedroom\", \"living\", \"flat\", \"bedsit\")\n"
HOME_NEW = HOME_OLD + (
    "#: ROWS OVER THE AISLES (0.207.0, roadmap 229). In a room organised by its\n"
    "#: shelving -- a selling floor's gondolas, a stockroom's or a warehouse's\n"
    "#: racks -- the ceiling is laid to the AISLES between the runs, not across\n"
    "#: the room: a fixture over a gondola lights its top shelf and leaves the\n"
    "#: aisle beside it to spill. The room's shelf volumes (`_SHELF_WORDS` on the\n"
    "#: volume's name, standing on the floor) are projected across the room's\n"
    "#: long axis, the spans merged, and every gap at least an aisle wide\n"
    "#: (`level_design.island_aisle_width`, the contract's door width, 1.25 m) is\n"
    "#: a LANE; each lane takes WOOD's rows within its own width, so the open\n"
    "#: band beside one wall run is still lit as a floor (`_lanes_for_room`,\n"
    "#: `_rows_for_room`). Only in a room whose words say it sells or stores\n"
    "#: (`_AISLE_ROOM_WORDS`): an office with a shelf unit against the wall keeps\n"
    "#: its tile grid, which is what an office is. Counted over the furnished\n"
    "#: library before the change (`docs/findings/fixture_rows/aisle_census.py`):\n"
    "#: 514 of 702 rooms carry a shelf volume, 293 of them with two or more lanes.\n"
    "_SHELF_WORDS = (\"shelf\", \"gondola\", \"rack\", \"pack_wall\")\n"
    "_AISLE_ROOM_WORDS = (\"sales\", \"retail\", \"shop_floor\", \"aisle\", \"market\", \"store\",\n"
    "                     \"stock\", \"storage\", \"ware\", \"parts\", \"supply\", \"cellar\", \"bond\")\n"
    "#: The aisle's width when `level_design` cannot be asked: the contract's\n"
    "#: `clearances.min_door_width_m`, the number `island_aisle_width` returns.\n"
    "_AISLE_MIN_FALLBACK = 1.25\n"
    "#: A shelf stands on the floor; a sign hung over an aisle does not.\n"
    "_SHELF_FOOT_MAX = 0.5\n"
    "#: A merged shelf span wider than this is a FIELD of islands, not a run: the\n"
    "#: deepest run in `level_design._PIECES` is 0.6 m and a twin island, two\n"
    "#: backs meeting, 1.2 m (`level_design.island_depth`); the furnish stands a\n"
    "#: selling room's islands down its middle band at shuffled positions along\n"
    "#: it, and their spans overlap into a band 2 to 10 m wide (66 of the 98\n"
    "#: shelved selling and storage rooms in the library; 32 have runs). A row\n"
    "#: kept off such a band leaves the middle of the floor dark, so past this\n"
    "#: the room is laid across as before.\n"
    "_SHELF_SPAN_MAX = 2.0\n")
REP_OLD = "    rep.setdefault(\"rows_laid\", 0)\n"
REP_NEW = REP_OLD + "    rep.setdefault(\"rows_over_aisles\", 0)\n"
TRY_OLD = (
    "        bar_aisle = level_design.bar_aisle_width()\n"
    "    except Exception:                                    # noqa: BLE001\n"
    "        bar_aisle = None\n")
TRY_NEW = (
    "        bar_aisle = level_design.bar_aisle_width()\n"
    "        aisle_min = level_design.island_aisle_width()\n"
    "    except Exception:                                    # noqa: BLE001\n"
    "        bar_aisle = None\n"
    "        aisle_min = _AISLE_MIN_FALLBACK\n")
LOOP_OLD = (
    "            home = _home_room(r, residence)\n"
    "            rows = _rows_for_room(bounds, ceiling_z, c[2],\n"
    "                                  _work_plane(r, home), home)\n"
    "            rep[\"rows_laid\"] += len(rows)\n")
LOOP_NEW = (
    "            home = _home_room(r, residence)\n"
    "            # over the aisles between the room's shelf runs when it has them\n"
    "            # (0.207.0, `_lanes_for_room`); a home's room has no aisles\n"
    "            lanes = None if home else _lanes_for_room(r, bounds, c[2], in_room, aisle_min)\n"
    "            rows = _rows_for_room(bounds, ceiling_z, c[2],\n"
    "                                  _work_plane(r, home), home, lanes=lanes)\n"
    "            if lanes:\n"
    "                rep[\"rows_over_aisles\"] += 1\n"
    "            rep[\"rows_laid\"] += len(rows)\n")
LINE_OLD = "          f\"{_report.get('rows_laid', 0)} row(s) laid to the work; \"\n"
LINE_NEW = ("          f\"{_report.get('rows_laid', 0)} row(s) laid to the work, \"\n"
            "          f\"{_report.get('rows_over_aisles', 0)} room(s) over their aisles; \"\n")
TEST_TAIL = "    assert len(_rows(_derive([office]), \"upper_office\")) == 3\n"
# the partition test asserts the whole report dict, as it did for 0.206.0's `rows_laid`
PART_OLD = '                   "storefront_spills": 0, "counter_accents": 0, "rows_laid": 1}\n'
PART_NEW = ('                   "storefront_spills": 0, "counter_accents": 0, "rows_laid": 1,\n'
            '                   "rows_over_aisles": 0}\n')


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = DC / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def main():
    if DRAFT and not os.environ.get("DC_ROOT"):
        sys.exit("refusing: --draft is for a DC_ROOT copy, never the repo")
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.207.0.md")
    assert entry.startswith("## [0.207.0] - "), entry[:40]
    if not DRAFT and not SUITE_PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    rows_old, rows_new = _src("lights_rows_old.py.txt"), _src("lights_rows_new.py.txt")
    assert rows_old.startswith("def _rows_for_room(") and rows_new.startswith("def _rows_for_room(")
    assert "def _lanes_for_room(" in rows_new and rows_new.endswith("\n\n\n")

    lp, l_eol, lights = _read("lights.py")
    assert "_lanes_for_room" not in lights, "already applied"
    lights = _once(lights, HOME_OLD, HOME_NEW, "the home words")
    lights = _once(lights, rows_old, rows_new, "_rows_for_room")
    assert lights.count("def _row_for_bounds(") == 1
    lights = _once(lights, REP_OLD, REP_NEW, "the report default")
    lights = _once(lights, TRY_OLD, TRY_NEW, "the aisle try")
    lights = _once(lights, LOOP_OLD, LOOP_NEW, "the room loop")

    dp, d_eol, dc = _read("deli_counter.py")
    dc = _once(dc, LINE_OLD, LINE_NEW, "the manifest line")

    tp, t_eol, tests = _read("test_fixture_rows.py")
    assert tests.endswith(TEST_TAIL), tests[-120:]
    tests = tests + _src("test_aisle_rows.py.txt")

    pp, p_eol, part = _read("test_lights_partitions.py")
    part = _once(part, PART_OLD, PART_NEW, "the partition report")

    sp, s_eol, reach = _read("test_storefront_reach.py")
    reach = _once(reach, REACH_OLD, REACH_NEW, "the gas station's reach")

    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # Every pin and anchor matched: now write.
    lp.write_bytes(lights.replace("\n", l_eol.decode()).encode("utf-8"))
    dp.write_bytes(dc.replace("\n", d_eol.decode()).encode("utf-8"))
    tp.write_bytes(tests.replace("\n", t_eol.decode()).encode("utf-8"))
    pp.write_bytes(part.replace("\n", p_eol.decode()).encode("utf-8"))
    sp.write_bytes(reach.replace("\n", s_eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (DC / "VERSION").write_bytes(VERSION)
    print("Deli Counter 0.206.1 -> 0.207.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
