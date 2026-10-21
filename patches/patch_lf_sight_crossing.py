"""Level Factory 0.229.0 (the factory's roadmap 289): the sightline advisory sights from the evaluator's eye.

`packages/validation/sightlines.py` sighted from a 1.4 m eye -- Laser Tag's bot before 0.20.0 -- so it crossed at 1.2
m and called solids both sides see over cover, where Laser Tag, Lot and the agent contract all cross at 1.3. The eye is
1.6 now, and `test_sightlines` asks this module's heights what `lasertag_contract.check_sight_drift` asks Lot's.

What this writes, every target pinned by its hash and refused on a mismatch, nothing written until every file has
been worked out: `packages/validation/sightlines.py` and `tests/unit/test_sightlines.py` (anchored hunks); VERSION;
the CHANGELOG entry, prepended. Generated from a proven clone (`patches/lf_sight_crossing/gen_lf_sight_crossing.py`),
dry-run on a fresh clone to the clone's every byte, a second run refused (`patches/lf_sight_crossing/dry_run_*.out.txt`).

    python patches/patch_lf_sight_crossing.py
    cd level_factory && python -m pytest -q > out.txt 2>&1; echo "exit=$?"
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
PINS = {'packages/validation/sightlines.py': '1acfd3afaf9a7ee7', 'tests/unit/test_sightlines.py': '4facd1c2181aed06'}
EDITS = {'packages/validation/sightlines.py': [('lines 44-48', "#: Eye heights, from the Laser Tag scripts. ``LT_BotPlayerController`` sights\n#: from ``body.global_position + Vector3.UP * 1.4``; the enemy sights from its\n#: ``Marker3D_Eye``, and both aim at ``LT_LineOfSightTester.CHEST_OFFSET``,\n#: which is 1.0 m above the target's origin.\nEYE_HEIGHT = 1.4\n", "#: Eye heights: where Laser Tag sights each side from, and the height both aim\n#: at. Since Laser Tag 0.20.0 the crew and the enemy sight from the scenario's\n#: ``player_eye_height_m`` and ``enemy_eye_height_m`` -- 1.6 m both, the agent\n#: contract's ``crew_sight_height_m`` and ``enemy_sight_height_m`` -- and aim at\n#: ``LT_LineOfSightTester.CHEST_OFFSET``, 1.0 m above the target's origin (the\n#: contract's ``aim_height_m``). Until Level Factory 0.229.0 this read 1.4, the\n#: bot's old probe, so the advisory crossed at 1.2 m and named solids both sides\n#: see over as cover (the factory's roadmap 289); the check Lot's copies answer\n#: to, `lasertag_contract.check_sight_drift`, now asks this one too\n#: (`test_sightlines`).\nEYE_HEIGHT = 1.6\n")], 'tests/unit/test_sightlines.py': [('lines 70-71', '    sightline runs from an eye at 1.4 m to a chest at 1.0 m and passes a metre\n    above it the whole way.\n', '    sightline runs from an eye at 1.6 m to a chest at 1.0 m and passes at least\n    0.6 m above it the whole way.\n'), ('lines 134-134', '    that line descends from 1.4 m to 1.0 m -- and never touches the incoming\n', '    that line descends from 1.6 m to 1.0 m -- and never touches the incoming\n'), ('lines 153-153', '    assert MIN_COVER_HEIGHT == 1.2\n', '    assert MIN_COVER_HEIGHT == 1.3        # 1.2 until 0.229.0, from a stale 1.4 m eye\n'), ('lines 258-258', '    assert open_sightlines({}, [], limit=45.0) == []\n', '    assert open_sightlines({}, [], limit=45.0) == []\n\n\ndef test_the_advisory_s_heights_are_the_shipped_evaluator_s():\n    """The check Lot\'s copies answer to (`lasertag_contract.check_sight_drift`, roadmap 131), asked of this module\'s.\n\n    Until 0.229.0 the advisory sighted from a 1.4 m eye -- the bot\'s probe before Laser Tag 0.20.0 moved both sides\n    to the scenario\'s 1.6 -- so it crossed at 1.2 m and named solids both sides see over as cover, while Lot\'s copies\n    were held to 1.6 by this same check (the factory\'s roadmap 289). Skipped when the Laser Tag sibling is absent,\n    as Lot\'s is: it has to run against the evaluator as it stands, not a fixture."""\n    import pytest\n    from packages.validation import lasertag_contract as lt\n    from packages.validation.sightlines import CHEST_HEIGHT, EYE_HEIGHT\n    from tests.siblings import not_found, sibling_repo\n    lasertag = sibling_repo("lasertag", marker="addons/laser_tag_tool")\n    if lasertag is None:\n        pytest.skip(not_found("lasertag", marker="addons/laser_tag_tool"))\n    assert lt.check_sight_drift(EYE_HEIGHT, CHEST_HEIGHT, lt.read_engagement_from(lasertag),\n                                who="Level Factory\'s sightline advisory") == []\n')]}
NEW_FILES = {}
CHANGELOG = "## [0.229.0] - the sightline advisory sights from the evaluator's eye\n\n**The factory's roadmap 289.** `packages/validation/sightlines.py` sighted from `EYE_HEIGHT = 1.4` -- the crew bot's\nprobe before Laser Tag 0.20.0 moved both sides to the scenario's `player_eye_height_m` and `enemy_eye_height_m`, 1.6 m\neach -- at a 1.0 m chest, so its `MIN_COVER_HEIGHT` was 1.2, and the advisory the Laser Tag adapter gives through\n`tactical.py` counted a 1.2 to 1.3 m solid as breaking a line both sides see over. Lot's copies, held to Laser Tag's\nby `lasertag_contract.check_sight_drift` since roadmap 131, carry 1.6 and 1.3, and the agent contract crosses at\n`cover_break_height_m`, 1.3: two instruments for one question, and this was the wrong one. Found by the read-only pass\nover the walker's lived-in levels guide (the factory's `docs/findings/guides_2026-10-21/lived_in.md`).\n\n### Changed\n- **`EYE_HEIGHT` 1.4 -> 1.6**, Laser Tag's and the contract's; `MIN_COVER_HEIGHT`, derived, 1.2 -> 1.3. The\n  constant's comment says where the number comes from and what it read before.\n\n### Tests\n- **test_sightlines.py**: `test_the_advisory_s_heights_are_the_shipped_evaluator_s` (new) asks this module's heights\n  what `check_sight_drift` asks Lot's, against the Laser Tag checkout beside it, and is skipped when that is absent,\n  as Lot's is. On 0.228.0 it fails on behaviour -- a 1.4 m eye against Laser Tag's 1.6, a 1.2 m crossing against 1.3\n  -- and so does `test_on_flat_ground_the_shortest_workable_cover_works_at_one_spot_only`, which pinned the old 1.2\n  and pins 1.3 now. Two docstrings that walked a line down from 1.4 m walk it from 1.6.\n\n"
OLD_VERSION, NEW_VERSION = '0.228.0', '0.229.0'


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (LF / name).read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: level_factory/%s has mixed line endings (%d CRLF of %d); nothing written"
                         % (name, crlf, lf))
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if _sha(text.encode("utf-8")) != PINS[name]:
        raise SystemExit("REFUSED: level_factory/%s is %s, not the %s this patch was written against; nothing "
                         "written" % (name, _sha(text.encode("utf-8")), PINS[name]))
    return text, crlf > 0


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: level_factory/%s: the anchor at %s is there %d times; nothing written"
                                 % (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\n", "\r\n") if crlf else text
    for name in NEW_FILES:
        if (LF / name).exists():
            raise SystemExit("REFUSED: level_factory/%s exists already; nothing written" % name)
    v = LF / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %r, not %s; nothing written" % (v.read_text(), OLD_VERSION))
    cl = LF / "CHANGELOG.md"
    craw = cl.read_bytes()
    if b"\r\n" in craw or not craw.startswith(b"## [" + OLD_VERSION.encode() + b"]"):
        raise SystemExit("REFUSED: CHANGELOG.md is not LF opening on %s; nothing written" % OLD_VERSION)
    for name, text in out.items():
        (LF / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (LF / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes(CHANGELOG.encode("utf-8") + craw)
    print("Level Factory %s applied: %d files edited, %d written, VERSION, CHANGELOG. Now, in level_factory/: the "
          "suite" % (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
