"""Deli Counter 0.205.0: every window of a strip club hangs a drape, and draws no window light.

Roadmap 219, the walker's note 2, walking club_block_014 on 2026-10-09: "the windows in any 'den
of sin' building should have curtains or drapes or blinds So people outside can't see in, and you
keep the streetlight light out of the club". Zoo 1.91.0 draws `window_drape`; this hangs it.

Anchored edits, every file pinned by hash, every anchor once, nothing written until all match:
- `level_design.py`: the rule (`plan_den_drapes`, `drape_den_windows`, `_is_drape`) before
  `dress_club_rooms`, and `furnish` calling it after `dress_club_rooms`; `_hung` beside
  `_HUNG_MIN`, which the five clearance checks that read `_HUNG_MIN` now ask (four `if`, one
  `elif`, each count asserted), and `_room_volume_count` leaving a drape out of the count --
  furnish never sees a drape, and the library stays a fixed point of it;
- `lights.py`: `_drapes_window` before `derive_light_anchors`, and its window loop skipping a
  draped window after counting it;
- `prop_species.py`: `window_drape` routed to Zoo's species, after `window_sign`.
New files, refused if they exist: `migrate_den_drapes.py`, `test_den_drapes.py`.
CHANGELOG and VERSION from `dc_den_drapes/CHANGELOG_0.205.0.md`. Then, chained:

    python patch_dc_den_drapes.py --suite-pending && python migrate_den_drapes.py && python build.py --all
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_den_drapes"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

#: sha256[:16] of each file as read on 2026-10-09 for this patch
SHA = {"level_design.py": "b692a56346b87f6e", "lights.py": "8ae64558cdaf6b8d",
       "prop_species.py": "21e9abfbd6284563"}


def _read(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


LD_ANCHOR = ("        _declare_material(spec, mat, _PROP_ACOUSTIC[mat])\n"
             "    return mat\n\n\n"
             "def dress_club_rooms(spec):\n")
FURNISH_OLD = "    dress_club_rooms(spec)\n    dress_card_shop_rooms(spec)\n"
FURNISH_NEW = ("    dress_club_rooms(spec)\n"
               "    # a den's windows drawn shut (0.205.0), before any piece is appended\n"
               "    drape_den_windows(spec)\n"
               "    dress_card_shop_rooms(spec)\n")
LIGHTS_FN = "def derive_light_anchors(rooms, openings, story_height, *, cap_thick,\n"
LIGHTS_LOOP_OLD = ("    win_n = {}\n"
                   "    for o in openings or []:\n"
                   "        if o.get(\"kind\") != \"window\":\n"
                   "            continue\n"
                   "        wall = o.get(\"wall\") or \"win\"\n"
                   "        win_n[wall] = win_n.get(wall, 0) + 1\n")
#: FURNISH NEVER SEES A DRAPE. The suite's first run failed four fixed-point
#: tests: re-furnished with its drape present, strip_club_a01's club room was
#: re-drawn (a piece fewer, fourteen named differently) and strip_club_a03's
#: upstairs room gained a chair. A drape's foot is 1.3 to 1.7 m up, under
#: `_HUNG_MIN`, so it was counted as a piece the room held and cleared as a
#: floor piece by `_seed_clear`'s 0.9 m. `_hung` takes it out of the five
#: clearance checks that read `_HUNG_MIN`, and `_room_volume_count` out of
#: the count.
HUNG_MIN = "_HUNG_MIN = 1.8\n"
HUNG_FN = (HUNG_MIN + "\n\n"
           "def _hung(v, floor):\n"
           "    \"\"\"Over the furniture, not among it: a collision-free volume whose foot\n"
           "    is `_HUNG_MIN` over ``floor``, or a den's drape (0.205.0, `_is_drape`),\n"
           "    hung against its window from 1.3 to 1.7 m up, whose span a wall piece\n"
           "    already keeps off (`_clear_of_openings`).\"\"\"\n"
           "    if v.get(\"collision\") != \"none\":\n"
           "        return False\n"
           "    if _is_drape(v):\n"
           "        return True\n"
           "    return float(v.get(\"z\", 0.0)) - float(v.get(\"size_z\", 0.0)) / 2.0 - floor >= _HUNG_MIN\n")
IF_SITE = ("        if v.get(\"collision\") == \"none\" and vz - vh / 2.0 - floor >= _HUNG_MIN:\n"
           "            continue\n")
ELIF_SITE = ("        elif v.get(\"collision\") == \"none\" and vz - vh / 2.0 - floor >= _HUNG_MIN:\n"
             "            continue\n")
COUNT_OLD = ("        if v.get(\"collision\") == \"none\" and v.get(\"form\") == \"window\":\n"
             "            continue\n")
COUNT_NEW = (COUNT_OLD
             + "        # A DEN'S DRAPE stands on no floor either (0.205.0): hung across its\n"
             "        # window from 1.3 to 1.7 m up, under the headroom line, and counted\n"
             "        # it re-drew strip_club_a01's club room -- the window sign's defect a\n"
             "        # fourth time. Not a rule by foot height: furnish's own wall pieces,\n"
             "        # 683 across the library, count toward the target today, and such a\n"
             "        # rule would refurnish the library.\n"
             "        if _is_drape(v):\n"
             "            continue\n")
ROW_OLD = "    ((\"window_sign\",), \"neon_sign\"),\n"
ROW_NEW = (ROW_OLD
           + "    # a den's drawn drape (0.205.0, `level_design.DRAPE_NAME`): Zoo's\n"
           "    # `window_drape` (>= 1.91.0)\n"
           "    ((\"window_drape\",), \"window_drape\"),\n")


def _edits():
    block = _read("level_design_block.py.txt")
    assert block.endswith("\n\n\n"), "the block must end in two blank lines"
    helper = _read("lights_helper.py.txt")
    assert helper.endswith("\n\n\n"), "the helper must end in two blank lines"
    # (old, new, how many times old stands in the file)
    return {
        "level_design.py": [
            (LD_ANCHOR, LD_ANCHOR.replace("def dress_club_rooms(spec):\n",
                                          block + "def dress_club_rooms(spec):\n"), 1),
            (FURNISH_OLD, FURNISH_NEW, 1),
            (HUNG_MIN, HUNG_FN, 1),
            (IF_SITE, "        if _hung(v, floor):\n            continue\n", 4),
            (ELIF_SITE, "        elif _hung(v, floor):\n            continue\n", 1),
            (COUNT_OLD, COUNT_NEW, 1)],
        "lights.py": [(LIGHTS_FN, helper + LIGHTS_FN, 1),
                      (LIGHTS_LOOP_OLD, _read("lights_loop_new.py.txt"), 1)],
        "prop_species.py": [(ROW_OLD, ROW_NEW, 1)],
    }


NEW = {"migrate_den_drapes.py": "migrate_den_drapes.py", "test_den_drapes.py": "test_den_drapes.py"}
CHANGELOG_HEAD = "## [0.204.1] - a quarter of the rowhome roofs carry an antenna or a dish\n"


def _stage():
    staged = {}
    for rel, pairs in _edits().items():
        p = DC / rel
        d = p.read_bytes()
        got = hashlib.sha256(d).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        assert b"\r" not in d, (rel, "has CR; this patch writes LF")
        t = d.decode("utf-8")
        assert "DRAPE_NAME" not in t, (rel, "already applied")
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
    assert v == b"Deli Counter 0.204.1", repr(v)
    staged = _stage()
    entry = _read("CHANGELOG_0.205.0.md")
    assert entry.startswith("## [0.205.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
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
    (DC / "VERSION").write_bytes(b"Deli Counter 0.205.0")
    print("Deli Counter 0.204.1 -> 0.205.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
