"""Deli Counter 0.228.0: a store's video poker cabinet takes a filler's wall when none is free -- two a store.

THE REGRESSION (factory roadmap 196's open line). Deli Counter 0.202.0 made `_wall_slots` offer a slot only where a
built wall holds the piece, which put deli_a01's ATM and poster boards back on real walls -- and dropped every
fixture no held wall could take. The six delis lost 18 of their 20 video poker cabinets, against the walker's two a
store. Measured 2026-10-19 across the library (the session's `poker_census.py`): of 31 buildings whose rooms ask
for `video_poker_store`, 16 hold two, 6 hold one and 9 hold none -- four delis, four pawn shops and a fuel stop.

WHY, replayed in deli_a01 (`poker_why.py`): both rooms that ask -- `customer_floor` and `market_aisles` -- are
offered held wall slots (7 and 11), and `_seed_clear` refuses every one (58 and 67 draws): the held walls are
already stood with shelf runs, vending, file cabinets and the service counter, and the rest are partitions, which
`_seed_clear` keeps a metre off because interior doors are there. A fixture is placed after the room's wall run,
so it meets a full wall.

THE RULE, a call made 2026-10-19 under the walker's standing instruction to make decisions that can be changed
later -- two dials on the piece:
  * `displaces=("cabinet_file", "vending")`: a cabinet with no free wall takes the slot of a filler in its own room,
    a file cabinet first (an office piece on a shop floor), then a vending machine. The cabinet still passes every
    test of its own, its stool's included, in whatever slot it lands; a filler is put back when the retry fails.
  * `most_building=2`: two a store, the walker's count, across the building's rooms (`most` stays two a room).

MEASURED after the library's strip and refurnish (`migrate_furnish_recipes.py`; the census beside this patch,
patches/dc_store_cabinets/census.out.txt): 11 specs change, +18 cabinets with their 18 stools, 9 file cabinets
and 6 vending machines displaced. Of the 31 buildings that ask, 27 hold two, 2 hold one and 2 hold none --
fuel_stop_heist and pawn_shop_a01 at none, pharmacy_a01 and stop_n_go at one -- whose rooms hold no filler a
cabinet and its stool fit. A store's poster boards come after its cabinets in the recipe's fixtures, so they
meet different walls: corner_deli_heist_01 (3 -> 2), cr_deli, deli_a01 and night_deli (2 -> 1 each) lose one,
convenience_store_a01 (1 -> 2) gains one. Every store keeps a board; the dial, if the walker wants boards first,
is the recipe's order.

REFUTED, kept above the result that replaced it. The first version of this patch shipped its own migration,
`migrate_store_cabinets.py`, running `place_fixtures(spec, keys={"video_poker_store"})` over the library and
nothing else: +15 cabinets, 9 vending and 5 file cabinets displaced (migrate_targeted.out.txt beside this
patch, and `poker_simulate.py` before it). It left the library no fixed point of furnish, and three tests said
so -- test_wall_backing, test_club_fixtures and test_deli_window, each with its
`test_the_library_is_a_fixed_point_of_furnish` (suite_targeted.out.txt: 3 failed, 1573 passed). A fresh furnish
places the cabinet before the poster boards, as the recipe orders them; the targeted pass had placed it after. A
library this repo refurnishes must be what refurnishing makes, so the migration is the strip and refurnish every
furnishing change here uses, and this patch writes none of its own.

What it changes (anchored; the file pinned by hash; nothing written on a miss; LF-safe):
  * level_design.py -- `_piece(displaces=, most_building=)`; the store cabinet's two dials; `place_fixtures(spec,
    keys=None)` honours the building cap and falls back to `_displace_for`; `_displace_for` (new).
  * test_store_cabinets.py (new): deli_a01 reaches two by displacing fillers, its stools with them; deli_a02 stops
    at two; a store already at two is untouched; `keys` limits the pass; the dials are recorded. Its fixtures
    (tests_fixtures/store_cabinets/) are the library's deli_a01 and deli_a02 as they were before the change.
  * VERSION 0.227.0 -> 0.228.0, CHANGELOG.

AFTER APPLYING: `python migrate_furnish_recipes.py`, then `python build.py --all`, the suite, and the commit (the
pre-commit gate refuses until the built shells are newer than the code).

    python patches/patch_dc_store_cabinets.py --tests   # the test file and its fixtures only (prove it fails first)
    python patches/patch_dc_store_cabinets.py           # everything; the tests again when they are this patch's
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
LD = DC / "level_design.py"
LD_SHA = "e8dd5e7fbd0fb5ee"
FIXTURES = ("deli_a01", "deli_a02")

PIECE_OLD = r'''           rooms=None, distinct=False, solo=False, lift_steps=None):
    return {"name": name, "sizes": tuple(sizes), "where": where,
'''
PIECE_NEW = r'''           rooms=None, distinct=False, solo=False, lift_steps=None,
           displaces=None, most_building=None):
    return {"name": name, "sizes": tuple(sizes), "where": where,
'''
PIECE_TAIL_OLD = r'''            "lift_steps": tuple(lift_steps) if lift_steps else None}
'''
PIECE_TAIL_NEW = r'''            "lift_steps": tuple(lift_steps) if lift_steps else None,
            # a fixture with no free wall may take a filler's (0.228.0,
            # `_displace_for`), and a building holds at most so many of it
            "displaces": tuple(displaces) if displaces else (),
            "most_building": most_building}
'''

CAB_OLD = r'''    _piece("video_poker_store", ((0.65, 0.65, 1.75),), "wall", front=True, most=2,
           variants=4, seats=("stool", 1, 1), off_glass=True,
           rooms=("sales", "retail", "shop", "customer", "market", "showroom", "stall")),
'''
CAB_NEW = r'''    # TWO A STORE, AND A FILLER'S WALL WHEN NONE IS FREE (0.228.0, the factory's
    # roadmap 196). 0.202.0 offered a wall slot only where a built wall holds
    # the piece and dropped every fixture no held wall took: the six delis
    # lost 18 of their 20 cabinets. A store's walls are stood before its
    # fixtures, so a cabinet now takes a file cabinet's slot, then a vending
    # machine's, in its own room -- passing every test of its own in it -- and a
    # building holds two, the walker's count. Both are dials, a call made
    # 2026-10-19 and meant to be changed.
    _piece("video_poker_store", ((0.65, 0.65, 1.75),), "wall", front=True, most=2,
           variants=4, seats=("stool", 1, 1), off_glass=True,
           rooms=("sales", "retail", "shop", "customer", "market", "showroom", "stall"),
           displaces=("cabinet_file", "vending"), most_building=2),
'''

PF_OLD = r'''def place_fixtures(spec):
    """Every room's FIXTURES (a recipe's ``fixtures``), where a room has none
    yet: one of each, two of a piece whose ``most_big`` area the room
    reaches. Idempotent and deterministic; reads nothing but the spec.
    Returns the number of volumes placed."""
    building = club_building_id(spec)
'''
PF_NEW = r'''def place_fixtures(spec, keys=None):
    """Every room's FIXTURES (a recipe's ``fixtures``), where a room has none
    yet: one of each, two of a piece whose ``most_big`` area the room
    reaches. Idempotent and deterministic; reads nothing but the spec.
    Returns the number of volumes placed.

    ``keys`` (0.228.0) limits the pass to those pieces, so a caller can place
    one kind and nothing else (test_store_cabinets.py does). A piece with
    ``most_building`` stops when the building holds that many; one with
    ``displaces`` that finds no free wall takes a filler's (`_displace_for`)."""
    building = club_building_id(spec)
'''

PF_LOOP_OLD = r'''        for key in fixtures:
            only = _PIECES[key]["rooms"]
            if only and not tokens & only:
                continue
            if _PIECES[key]["solo"] and any(
                    str(v.get("name", "")).startswith(key + "_") for v in spec.get("volumes") or []):
                continue
            for k in range(fixture_limit(key, area)):
                have = sum(1 for stem, _s, _v in _room_names(spec, rtag) if stem == key)
                if have > k:
                    continue
                if _place_fixture(spec, room, key, k, building) is None:
                    break
                added += 1
    return added
'''
PF_LOOP_NEW = r'''        for key in fixtures:
            if keys is not None and key not in keys:
                continue
            only = _PIECES[key]["rooms"]
            if only and not tokens & only:
                continue
            if _PIECES[key]["solo"] and any(
                    str(v.get("name", "")).startswith(key + "_") for v in spec.get("volumes") or []):
                continue
            cap = _PIECES[key]["most_building"]
            for k in range(fixture_limit(key, area)):
                have = sum(1 for stem, _s, _v in _room_names(spec, rtag) if stem == key)
                if have > k:
                    continue
                if cap is not None and sum(
                        1 for v in spec.get("volumes") or []
                        if str(v.get("name", "")).startswith(key + "_r")) >= cap:
                    break
                got = _place_fixture(spec, room, key, k, building)
                if got is None and _PIECES[key]["displaces"]:
                    got = _displace_for(spec, room, key, k, building)
                if got is None:
                    break
                added += 1
    return added


def _displace_for(spec, room, key, k, building):
    """A fixture with no free wall takes a filler's (0.228.0): each of the
    piece's ``displaces`` stems in order, that stem's pieces in this room
    newest first, one at a time -- the filler is lifted, the fixture is
    placed by `_place_fixture` with every test it always had, and the filler
    is put back exactly where it was when the fixture still finds no spot.
    Returns the fixture's volume, or None with the spec as it was."""
    rtag = _room_tag(room)
    for stem in _PIECES[key]["displaces"]:
        fillers = sorted((t for t in _room_names(spec, rtag) if t[0] == stem),
                         key=lambda t: -t[1])
        for _stem, _seq, vol in fillers:
            vols = spec["volumes"]
            i = vols.index(vol)
            vols.pop(i)
            got = _place_fixture(spec, room, key, k, building)
            if got is not None:
                return got
            vols.insert(i, vol)
    return None
'''

TEST = r'''"""Two video poker cabinets a store, and a filler's wall when none is free (0.228.0, the factory's roadmap 196).

0.202.0 dropped every fixture no held wall could take, and the six delis lost 18 of their 20 cabinets: in
deli_a01 both selling rooms are offered held wall slots and `_seed_clear` refuses every one, because the walls are
already stood. Now a cabinet takes a file cabinet's slot, then a vending machine's, in its own room, and a building
holds two. These run `place_fixtures` on copies of library specs as they were before the migration
(`tests_fixtures/store_cabinets/`, kept so the test does not change when the library does).

Run: python -m pytest -q test_store_cabinets.py
"""
import copy
import json
from pathlib import Path

import level_design as L

HERE = Path(__file__).resolve().parent
FIX = HERE / "tests_fixtures" / "store_cabinets"
KEY = "video_poker_store"


def _spec(name):
    return json.loads((FIX / (name + ".json")).read_text(encoding="utf-8"))


def _count(spec, stem):
    return sum(1 for v in spec.get("volumes") or [] if str(v.get("name", "")).startswith(stem + "_r"))


def test_deli_a01_reaches_two_by_taking_fillers():
    spec = _spec("deli_a01")
    assert _count(spec, KEY) == 0
    fillers = _count(spec, "cabinet_file") + _count(spec, "vending")
    L.place_fixtures(spec, keys={KEY})
    assert _count(spec, KEY) == 2
    assert _count(spec, "cabinet_file") + _count(spec, "vending") == fillers - 2
    # each cabinet brings its stool, named `bar_stool_<room tag>_<seq>_1` beside the cabinet's `<key>_<tag>_<seq>`
    names = {str(v["name"]) for v in spec["volumes"]}
    for v in spec["volumes"]:
        n = str(v["name"])
        if n.startswith(KEY + "_r"):
            assert L._SEAT_PIECES["stool"] + n[len(KEY):] + "_1" in names, n


def test_deli_a02_stops_at_two():
    spec = _spec("deli_a02")
    assert _count(spec, KEY) == 1
    L.place_fixtures(spec, keys={KEY})
    assert _count(spec, KEY) == 2


def test_a_store_already_at_two_is_untouched():
    spec = _spec("deli_a02")
    L.place_fixtures(spec, keys={KEY})
    again = copy.deepcopy(spec)
    L.place_fixtures(again, keys={KEY})
    assert again == spec


def test_keys_limits_the_pass_to_its_pieces():
    spec = _spec("deli_a01")
    before = {v["name"] for v in spec["volumes"]}
    L.place_fixtures(spec, keys={KEY})
    new = {v["name"] for v in spec["volumes"]} - before
    # the cabinets and the stools they bring, and nothing else
    stool = L._SEAT_PIECES["stool"] + "_r"
    assert any(n.startswith(KEY + "_r") for n in new), new
    assert all(n.startswith(KEY + "_r") or n.startswith(stool) for n in new), new


def test_the_dials_are_recorded():
    p = L._PIECES[KEY]
    assert p["displaces"] == ("cabinet_file", "vending") and p["most_building"] == 2
    assert L._PIECES["video_poker_bar"]["displaces"] == () and L._PIECES["video_poker_bar"]["most_building"] is None
'''

CHANGELOG = '''## [0.228.0] - two video poker cabinets a store, and a filler's wall when none is free

**The factory's roadmap 196, its open line.** 0.202.0 made `_wall_slots` offer a slot only where a built wall holds
the piece, and dropped every fixture no held wall could take. The six delis lost 18 of their 20 video poker
cabinets, against the walker's two a store. Across the library, 31 buildings' rooms ask for `video_poker_store`;
16 held two, 6 one and 9 none. In deli_a01 both selling rooms are offered held wall slots, 7 and 11, and
`_seed_clear` refuses every one: the held walls are already stood with shelf runs, vending, file cabinets and the
service counter, and the rest are partitions, kept a metre off for their doors.

**The rule, a call made 2026-10-19 and meant to be changed, as two dials on the piece:**
- `displaces=("cabinet_file", "vending")`: a cabinet with no free wall takes a filler's slot in its own room, a file
  cabinet first, then a vending machine, passing every test of its own and its stool's. A filler is put back when
  the retry fails.
- `most_building=2`: two a store, across the building's rooms. `most` stays two a room.

### Added
- `_displace_for`, and `place_fixtures(spec, keys=None)`, which places only the pieces it names.
- `test_store_cabinets.py` (5, which fail on 0.227.0), on fixtures kept beside it as the library was before.

### Changed
- The library, stripped and refurnished with `migrate_furnish_recipes.py`: 11 specs, +18 cabinets and their 18
  stools, 9 file cabinets and 6 vending machines displaced. 27 of the 31 stores hold two. fuel_stop_heist and
  pawn_shop_a01 stay at none, and pharmacy_a01 and stop_n_go at one: their rooms hold no filler that a cabinet and
  its stool fit in.
- A store's poster boards come after its cabinets in the recipe, so they meet different walls. corner_deli_heist_01,
  cr_deli, deli_a01 and night_deli each lose one, and convenience_store_a01 gains one; every store keeps a board.
- Rebuilt with `build.py --all`; the suite after the rebuild: 1576 passed, 2 skipped.

### Refuted, kept
- A migration that placed the cabinets alone, `place_fixtures(spec, keys={"video_poker_store"})` over the library,
  left it no fixed point of furnish: test_wall_backing, test_club_fixtures and test_deli_window each failed theirs.
  A fresh furnish places the cabinet before the poster boards, and the targeted pass had placed it after. The
  migration is the strip and refurnish every furnishing change here uses.

'''


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _tests_plan():
    """What `write_tests` writes, refusing anything already there that is not this patch's: the test file is
    this patch's TEST, and each fixture is the library's spec as it stands, so `--tests` then the full apply
    (the documented order) writes the same bytes twice and a stale or foreign copy is refused."""
    p = DC / "test_store_cabinets.py"
    if p.exists():
        assert p.read_bytes() == TEST.encode("utf-8"), f"{p.name} exists and is not this patch's"
    fix = DC / "tests_fixtures" / "store_cabinets"
    writes = {}
    for name in FIXTURES:
        b = (DC / "specs" / (name + ".json")).read_bytes()
        f = fix / (name + ".json")
        if f.exists():
            assert f.read_bytes() == b, f"{f.name} exists and is not the library's {name}"
        writes[f] = b
    return p, fix, writes


def write_tests(plan=None):
    p, fix, writes = plan or _tests_plan()
    p.write_text(TEST, encoding="utf-8", newline="\n")
    fix.mkdir(parents=True, exist_ok=True)
    for f, b in writes.items():
        f.write_bytes(b)
    print("wrote deli_counter/test_store_cabinets.py and its fixtures (%s as the library has them)"
          % ", ".join(FIXTURES))


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    raw = LD.read_bytes()
    assert b"\r\n" not in raw, "level_design.py is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == LD_SHA, ("level_design.py is not the file this patch read", got)
    text = raw.decode("utf-8")
    assert "_displace_for" not in text, "already applied"
    text = _once(text, PIECE_OLD, PIECE_NEW, "_piece's signature")
    text = _once(text, PIECE_TAIL_OLD, PIECE_TAIL_NEW, "_piece's return")
    text = _once(text, CAB_OLD, CAB_NEW, "the store cabinet")
    text = _once(text, PF_OLD, PF_NEW, "place_fixtures' head")
    text = _once(text, PF_LOOP_OLD, PF_LOOP_NEW, "place_fixtures' loop")
    v = DC / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Deli Counter 0.227.0", v.read_text(encoding="utf-8")
    cl = DC / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    ctext = rawc.decode("utf-8")
    assert ctext.startswith("## [0.227.0]"), ctext[:40]
    plan = _tests_plan()
    LD.write_bytes(text.encode("utf-8"))
    v.write_text("Deli Counter 0.228.0", encoding="utf-8")
    cl.write_bytes((CHANGELOG.replace("\n", eol) + ctext).encode("utf-8"))
    write_tests(plan)
    print("Deli Counter 0.228.0 applied: _displace_for, the cabinet's dials, test, VERSION, CHANGELOG -- now "
          "migrate_furnish_recipes.py, build.py --all")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
