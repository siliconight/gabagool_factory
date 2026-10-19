"""Deli Counter 0.231.0: a store's video poker cabinet may stand against the partition it backs onto (roadmap 196).

THE REFUSALS, ATTRIBUTED (`patches/dc_store_cabinets/why_rule.py`, tracing which `return False` of `_seed_clear`
each candidate reached, on 0.230.0's library). The four stores 0.228.0 left short -- fuel_stop_heist and
pawn_shop_a01 at none, pharmacy_a01 and stop_n_go at one -- were refused by two rules: the 0.9 m spread off other
volumes (12 to 37 a room) and the metre-off-a-partition line rule (24 to 48 a room), with 2 at a door's approach
and 3 at a ladder. The line rule keeps every piece's CENTRE 1.0 m off every partition's line, so it refuses every
slot a held partition wall offers: a cabinet backed against one stands its centre about half a metre off it. It
is roadmap 196's other residue, "a partition is still unfurnished". The door rule (`_seed_clear_doors`, 1.5 m
plus the piece's half from every partition opening) is separate.

THE CALL, made 2026-10-19 and meant to be changed -- one dial on one piece: `backs_on_partitions`, on for
`video_poker_store` alone. Placed by `_place_fixture` against a wall, such a piece is not asked the line rule for
the one partition whose centreline IS the room edge it backs onto (`_seed_clear(backed_on=(axis, pos))`); every
other partition, the door rule and every other rule still apply. Every other wall piece keeps the metre.

SIMULATED BEFORE WRITING (`patches/dc_store_cabinets/partition_sim.py`: the same edits in a scratch copy, the
library stripped and refurnished in memory): 26 specs change. fuel_stop_heist 0 -> 2, pharmacy_a01 1 -> 2,
stop_n_go 1 -> 2, pawn_shop_a01 0 -> 1 -- 30 of 31 stores at two. Nine of the fifteen fillers 0.228.0 displaced
come back (+5 file cabinets, +4 vending), because a cabinet now finds a partition before it needs a filler's
slot; poster boards net +2; twelve buildings' cabinets move with their counts unchanged.

What it changes (anchored; the file pinned by hash; nothing written on a miss; LF-safe):
  * level_design.py -- `_piece(backs_on_partitions=)`; the cabinet's dial; `_seed_clear(backed_on=)`; and
    `_place_fixture` passes the edge for a piece with the dial.
  * test_cabinet_partitions.py (new, 4; 3 fail on 0.230.0), on fixtures kept beside it as the library is before
    the change (pharmacy_a01, fuel_stop_heist).
  * test_store_cabinets.py -- its filler test asks with the partition dial off: the displacement path it proves
    is unchanged, and deli_a01 with the dial on needs fewer fillers.
  * VERSION 0.230.0 -> 0.231.0, CHANGELOG.

AFTER APPLYING: `python migrate_furnish_recipes.py`, then `python build.py --all` (level_design.py is a geometry
source since 0.229.0), the suite, and the commit.

    python patches/patch_dc_cabinet_partitions.py --tests   # the test file and its fixtures (prove it fails first)
    python patches/patch_dc_cabinet_partitions.py           # everything; the tests again when they are this patch's
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
LD = DC / "level_design.py"
LD_SHA = "8fa3d0c789fa2a77"
TSC = DC / "test_store_cabinets.py"
FIXTURES = ("pharmacy_a01", "fuel_stop_heist")

EDITS = [
    ("_piece's signature",
     '''           displaces=None, most_building=None):
    return {"name": name, "sizes": tuple(sizes), "where": where,
''', '''           displaces=None, most_building=None, backs_on_partitions=False):
    return {"name": name, "sizes": tuple(sizes), "where": where,
            # a wall piece that may stand against the PARTITION it backs onto
            # (0.231.0; `_seed_clear`'s `backed_on`, passed by `_place_fixture`)
            "backs_on_partitions": backs_on_partitions,
'''),
    ("the cabinet's comment",
     '''    # building holds two, the walker's count. Both are dials, a call made
    # 2026-10-19 and meant to be changed.
''', '''    # building holds two, the walker's count. Both are dials, a call made
    # 2026-10-19 and meant to be changed. And it may back onto a PARTITION
    # (0.231.0): `_seed_clear` keeps every piece's centre a metre off every
    # partition's line, which refused every slot a partition wall offers; the
    # one partition behind the cabinet is not asked, every other rule is --
    # a third dial, the same call.
'''),
    ("the cabinet's dials",
     '''           displaces=("cabinet_file", "vending"), most_building=2),
''', '''           displaces=("cabinet_file", "vending"), most_building=2,
           backs_on_partitions=True),
'''),
    ("_seed_clear's signature",
     '''def _seed_clear(spec, room, px, py, placed, half=0.0, above=None,
                below=None, over_openings=False, corridor=False):
''', '''def _seed_clear(spec, room, px, py, placed, half=0.0, above=None,
                below=None, over_openings=False, corridor=False, backed_on=None):
'''),
    ("_seed_clear's docstring end",
     '''    Opt-in, because furnish's callers stand furniture against walls on
    purpose and answer to their own rules."""
''', '''    Opt-in, because furnish's callers stand furniture against walls on
    purpose and answer to their own rules.

    `backed_on` (0.231.0, the factory's roadmap 196), ``(axis, pos)`` of the
    room edge a wall piece backs onto: the partition whose centreline IS that
    edge is not asked the metre-off-a-partition rule, which refused every slot
    a held partition wall offers -- a piece backed against one stands its
    centre about half a metre off it. Every other partition, the door-approach
    rule and every other rule still apply. Only a piece with
    ``backs_on_partitions`` passes it (`_place_fixture`)."""
'''),
    ("the partition rule",
     '''        if p.get("story", 0) != story:
            continue
        if p["axis"] == "Y":
            cy = max(p["start"], min(py, p["end"]))
''', '''        if p.get("story", 0) != story:
            continue
        # the partition the piece backs onto (0.231.0, `backed_on`)
        if backed_on is not None and p["axis"] == backed_on[0] \\
                and abs(float(p["pos"]) - backed_on[1]) < 0.05:
            continue
        if p["axis"] == "Y":
            cy = max(p["start"], min(py, p["end"]))
'''),
    ("_place_fixture's call",
     '''        if not _seed_clear(spec, room, qx, qy, [], half=half, above=above,
                           below=below,
                           over_openings=hangs_over_openings(spec, story,
                                                             above)):
            continue
''', '''        # THE EDGE A WALL PIECE BACKS ONTO (0.231.0), for a piece that may
        # stand against a partition: the slot's front bearing names it -- N
        # from the room's south edge, E from its west, and so on round.
        backed_on = None
        if p["backs_on_partitions"] and front is not None:
            bx0, by0, bx1, by1 = room["bounds"]
            backed_on = {0.0: ("X", by0), 180.0: ("X", by1),
                         90.0: ("Y", bx0), 270.0: ("Y", bx1)}.get(float(front))
        if not _seed_clear(spec, room, qx, qy, [], half=half, above=above,
                           below=below,
                           over_openings=hangs_over_openings(spec, story,
                                                             above),
                           backed_on=backed_on):
            continue
'''),
]

TSC_OLD = '''def test_deli_a01_reaches_two_by_taking_fillers():
    spec = _spec("deli_a01")
'''
TSC_NEW = '''def test_deli_a01_reaches_two_by_taking_fillers(monkeypatch):
    # the displacement path, asked with the partition dial off: since 0.231.0 this cabinet may back onto a
    # partition, and deli_a01 then needs fewer fillers (test_cabinet_partitions.py)
    monkeypatch.setitem(L._PIECES[KEY], "backs_on_partitions", False)
    spec = _spec("deli_a01")
'''

TEST = r'''"""A store's video poker cabinet may stand against the partition it backs onto (0.231.0, the factory's roadmap 196).

`_seed_clear` keeps every piece's centre a metre off every partition's line, which refused every slot a held
partition wall offers -- a cabinet backed against one stands its centre about half a metre off it -- and left four
stores short of the walker's two. The cabinet's `backs_on_partitions` dial exempts the one partition behind it;
every other partition and every other rule still apply. These run `place_fixtures` on copies of library specs as
they were before the change (`tests_fixtures/cabinet_partitions/`), and read the library as it is after.

Run: python -m pytest -q test_cabinet_partitions.py
"""
import glob
import json
import math
from pathlib import Path

import level_design as L

HERE = Path(__file__).resolve().parent
FIX = HERE / "tests_fixtures" / "cabinet_partitions"
KEY = "video_poker_store"


def _spec(name):
    return json.loads((FIX / (name + ".json")).read_text(encoding="utf-8"))


def _cabinets(spec):
    return [v for v in spec.get("volumes") or [] if str(v.get("name", "")).startswith(KEY + "_r")]


def _partition_distance(p, x, y):
    if p["axis"] == "Y":
        return math.hypot(x - p["pos"], y - max(p["start"], min(y, p["end"])))
    return math.hypot(x - max(p["start"], min(x, p["end"])), y - p["pos"])


def _story_of(spec, v):
    return int(round((float(v["z"]) - float(v["size_z"]) / 2.0) / float(spec["story_height"])))


def _near_partitions(spec, v):
    story = _story_of(spec, v)
    return [p for p in spec.get("partitions") or []
            if p.get("story", 0) == story and _partition_distance(p, v["x"], v["y"]) < 1.0]


def test_pharmacy_reaches_two_against_a_partition():
    spec = _spec("pharmacy_a01")
    before = {v["name"] for v in _cabinets(spec)}
    assert len(before) == 1
    L.place_fixtures(spec, keys={KEY})
    new = [v for v in _cabinets(spec) if v["name"] not in before]
    assert len(new) == 1
    # it stands where the metre refused it: within a metre of exactly one partition, the one behind it
    near = _near_partitions(spec, new[0])
    assert len(near) == 1, near
    assert _partition_distance(near[0], new[0]["x"], new[0]["y"]) < 0.7


def test_the_fuel_stop_reaches_two():
    spec = _spec("fuel_stop_heist")
    assert len(_cabinets(spec)) == 0
    L.place_fixtures(spec, keys={KEY})
    assert len(_cabinets(spec)) == 2


def test_no_cabinet_in_the_library_stands_near_a_partition_it_does_not_back_onto():
    for path in sorted(glob.glob(str(HERE / "specs" / "*.json"))):
        if Path(path).name.startswith("lf_"):
            continue
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
        for v in _cabinets(spec):
            near = _near_partitions(spec, v)
            assert len(near) <= 1, (Path(path).name, v["name"], near)
            if near:
                assert _partition_distance(near[0], v["x"], v["y"]) < 0.7, (Path(path).name, v["name"])


def test_the_dial_is_the_cabinets_alone():
    assert L._PIECES[KEY]["backs_on_partitions"] is True
    others = [k for k, p in L._PIECES.items() if k != KEY and p["backs_on_partitions"]]
    assert others == []
'''

CHANGELOG = '''## [0.231.0] - a store's video poker cabinet may stand against the partition it backs onto

**The factory's roadmap 196: the four stores 0.228.0 left short, and its other residue.** Traced on 0.230.0's
library, rule by rule (the factory's `patches/dc_store_cabinets/why_rule.py`), the short stores' candidates were
refused by two rules: the 0.9 m spread off other volumes, 12 to 37 a room, and the metre-off-a-partition line
rule, 24 to 48 a room. The line rule keeps every piece's centre 1.0 m off every partition's line, so it refuses
every slot a held partition wall offers: a cabinet backed against one stands its centre about half a metre off it.
That is the roadmap's "a partition is still unfurnished". The door rule (`_seed_clear_doors`) is separate.

**The call, made 2026-10-19 and meant to be changed:** one dial on one piece, `backs_on_partitions`, on for
`video_poker_store` alone. Placed against a wall, the cabinet is not asked the line rule for the one partition
whose centreline is the room edge it backs onto; every other partition, the door rule and every other rule still
apply. Every other wall piece keeps the metre.

### Added
- `_piece(backs_on_partitions=)`, `_seed_clear(backed_on=)`, and `_place_fixture` passing the edge, named by the
  slot's front bearing, for a piece with the dial.
- `test_cabinet_partitions.py` (4, three of which fail on 0.230.0), on fixtures kept beside it as the library was.

### Changed
- `test_store_cabinets.py`'s filler test asks with the dial off. The displacement path it proves is unchanged;
  deli_a01 with the dial on needs fewer fillers.
- The library, stripped and refurnished with `migrate_furnish_recipes.py`, as simulated beforehand
  (`partition_sim.py` beside the census): fuel_stop_heist 0 -> 2, pharmacy_a01 1 -> 2, stop_n_go 1 -> 2,
  pawn_shop_a01 0 -> 1, so 30 of 31 stores hold two. Nine of the fifteen fillers 0.228.0 displaced come back, five
  file cabinets and four vending machines, because a cabinet now finds a partition first. Poster boards net +2.

'''


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _tests_plan():
    p = DC / "test_cabinet_partitions.py"
    if p.exists():
        assert p.read_bytes() == TEST.encode("utf-8"), f"{p.name} exists and is not this patch's"
    fix = DC / "tests_fixtures" / "cabinet_partitions"
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
    print("wrote deli_counter/test_cabinet_partitions.py and its fixtures (%s as the library has them)"
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
    assert "backs_on_partitions" not in text, "already applied"
    for what, old, new in EDITS:
        text = _once(text, old, new, what)
    rawt = TSC.read_bytes()
    assert b"\r\n" not in rawt, "test_store_cabinets.py is LF"
    tsc = _once(rawt.decode("utf-8"), TSC_OLD, TSC_NEW, "the filler test")
    v = DC / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Deli Counter 0.230.0", v.read_text(encoding="utf-8")
    cl = DC / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    ctext = rawc.decode("utf-8")
    assert ctext.startswith("## [0.230.0]"), ctext[:40]
    plan = _tests_plan()
    LD.write_bytes(text.encode("utf-8"))
    TSC.write_bytes(tsc.encode("utf-8"))
    v.write_text("Deli Counter 0.231.0", encoding="utf-8")
    cl.write_bytes((CHANGELOG.replace("\n", eol) + ctext).encode("utf-8"))
    write_tests(plan)
    print("Deli Counter 0.231.0 applied: backs_on_partitions on the store cabinet, backed_on in _seed_clear, tests, "
          "VERSION, CHANGELOG -- now migrate_furnish_recipes.py, build.py --all")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
