"""Deli Counter 0.231.1: two video poker cabinets in one room are two different machines (roadmap 196).

SEEN IN COLD RUN 9326's PACKAGE. deli_a01's two cabinets both instance `prop_video_poker_delco_1997_07_..._n1`:
0.231.0 stood them both in the customer floor, and a fixture's variant is its name's crc32 modulo the species'
count (`_make_volume`), so `video_poker_store_r7070a315_9` and `_10` drew the same machine. Across the library, 6 of
the 30 rooms holding two cabinets show one machine twice -- all six delis (`corner_deli_heist_01`, `cr_deli`,
`deli_a01` to `deli_a03`, `night_deli`), whose customer floors share the tag and the two names.

THE DIAL THAT ALREADY EXISTS: `distinct` (0.163.0), which `_distinct_variant` honours by moving a piece off any
variant its room's same-size pieces already show and refusing a spot only when every variant is taken -- four
here, two a room at most, so it moves a variant and never a placement. The poster runs have used it since 0.163.0.
A call, made 2026-10-19 and meant to be changed: the store's cabinet is `distinct`.

What it changes (anchored; the file pinned by hash; nothing written on a miss; LF-safe):
  * level_design.py -- `video_poker_store` takes `distinct=True`.
  * test_cabinet_variants.py (new, 2; both fail on 0.231.0): no library room holds two cabinets on one variant;
    the dial is recorded.
  * VERSION 0.231.0 -> 0.231.1, CHANGELOG.

AFTER APPLYING: `python migrate_furnish_recipes.py` (only the six delis' second cabinets should change, and only
their `variant`), then `python build.py --all`, the suite, and the commit.

    python patches/patch_dc_cabinet_variants.py --tests   # the test file only (prove it fails first)
    python patches/patch_dc_cabinet_variants.py           # everything; the test again when it is this patch's
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
LD = DC / "level_design.py"
LD_SHA = "9dbb640eadde2713"

OLD = '''           displaces=("cabinet_file", "vending"), most_building=2,
           backs_on_partitions=True),
'''
NEW = '''           displaces=("cabinet_file", "vending"), most_building=2,
           backs_on_partitions=True,
           # two in one room are two machines (0.231.1): a variant is the
           # name's crc32, and the six delis' customer floors drew one twice
           distinct=True),
'''

TEST = r'''"""Two video poker cabinets in one room are two different machines (0.231.1, the factory's roadmap 196).

A fixture's variant is its name's crc32 modulo the species' count, so two cabinets in one room can draw the same
machine: cold run 9326 showed deli_a01's customer floor with one machine twice, and the library held six such
rooms, all delis. The cabinet is now `distinct`, which moves a variant off the one its room already shows and never
moves a placement. This reads the library as it is.

Run: python -m pytest -q test_cabinet_variants.py
"""
import collections
import glob
import json
import re
from pathlib import Path

import level_design as L

HERE = Path(__file__).resolve().parent
KEY = "video_poker_store"
NAME = re.compile(r"^%s_(r[0-9a-f]{8})_\d+$" % KEY)


def test_no_room_holds_one_machine_twice():
    clashes = []
    for path in sorted(glob.glob(str(HERE / "specs" / "*.json"))):
        if Path(path).name.startswith("lf_"):
            continue
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
        by_room = collections.defaultdict(list)
        for v in spec.get("volumes") or []:
            m = NAME.match(str(v.get("name", "")))
            if m:
                by_room[m.group(1)].append(int(v.get("variant", 0) or 0))
        clashes += [(Path(path).name, tag, vs) for tag, vs in by_room.items() if len(set(vs)) < len(vs)]
    assert clashes == []


def test_the_cabinet_is_distinct():
    assert L._PIECES[KEY]["distinct"] is True
'''

CHANGELOG = '''## [0.231.1] - two video poker cabinets in one room are two different machines

**Seen in the factory's cold run 9326 (roadmap 196).** deli_a01's two cabinets, both in the customer floor since
0.231.0, instanced one machine twice: a fixture's variant is its name's crc32 modulo the species' count, and
`video_poker_store_r7070a315_9` and `_10` drew the same one. Across the library, 6 of the 30 rooms holding two
cabinets showed one machine twice -- all six delis, whose customer floors share the tag and the names.

### Changed
- `video_poker_store` is `distinct` (0.163.0's dial, which the poster runs use): `_distinct_variant` moves a
  variant off the one its room already shows, and refuses a spot only when every variant is taken -- four here, two
  a room at most -- so no placement moves. A call, made 2026-10-19 and meant to be changed.

### Added
- `test_cabinet_variants.py` (2, both fail on 0.231.0).

'''


def _test_plan():
    p = DC / "test_cabinet_variants.py"
    if p.exists():
        assert p.read_bytes() == TEST.encode("utf-8"), f"{p.name} exists and is not this patch's"
    return p


def write_tests(p=None):
    p = p or _test_plan()
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote deli_counter/test_cabinet_variants.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    raw = LD.read_bytes()
    assert b"\r\n" not in raw, "level_design.py is LF"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == LD_SHA, ("level_design.py is not the file this patch read", got)
    text = raw.decode("utf-8")
    assert text.count(OLD) == 1, ("the cabinet's dials", text.count(OLD))
    text = text.replace(OLD, NEW)
    v = DC / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Deli Counter 0.231.0", v.read_text(encoding="utf-8")
    cl = DC / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    ctext = rawc.decode("utf-8")
    assert ctext.startswith("## [0.231.0]"), ctext[:40]
    plan = _test_plan()
    LD.write_bytes(text.encode("utf-8"))
    v.write_text("Deli Counter 0.231.1", encoding="utf-8")
    cl.write_bytes((CHANGELOG.replace("\n", eol) + ctext).encode("utf-8"))
    write_tests(plan)
    print("Deli Counter 0.231.1 applied: the cabinet is distinct, test, VERSION, CHANGELOG -- now "
          "migrate_furnish_recipes.py, build.py --all")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
