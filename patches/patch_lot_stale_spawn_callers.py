#!/usr/bin/env python3
"""Roadmap 51, defect one: six stale callers of `opening_engagement_is_fair`.

WHAT IS WRONG

`site_spawns.opening_engagement_is_fair(candidate, crew_path, occluders)` was
changed to judge the STRETCH OF ROUTE the crew covers in its first second
rather than the spawn TILE it starts on. Six tests still pass a single 2-tuple
spawn point where a sequence of points is wanted; bound to `crew_path` it
iterates to floats and `site_spawns.py:475` raises

    TypeError: 'float' object is not iterable

THE PREDICATE IS NOT THE DEFECT AND IS NOT TOUCHED. Its docstring states the
refusal was deliberate:

    `crew_path` is required rather than defaulted to ``[spawn]``. A default
    would leave both existing callers testing the old thing while this code sat
    unreached, which is precisely the failure this patch exists to correct one
    instance of.

The refusal worked. The follow-through never happened. This is the
follow-through.

WHAT IT DOES, AND WHY THE TWO KINDS OF CALLER ARE FIXED DIFFERENTLY

Four of the six are unit assertions about the predicate's own geometry -- an
enemy at 23 m in the open, the same enemy behind a rect, 40 m, the range
itself. They are asking about the distance and occlusion branches with the crew
held still, so they get a one-point path, `[(0.0, 0.0)]`. That is the same
degenerate case `crew_reaction_path` documents ("a caller with nowhere to walk
gets the old single-point behaviour without a second code path"), and it is the
honest shape for a test whose subject is the branch and not the window.

The other two run `place_enemies` and read the written positions back. Those
MUST use the window the SEARCH used, which is `crew_reaction_path(route)` --
`site_spawns.py:803`. A read-back that asked `[spawn]` would ask an easier
question than the search did and would report a clean opening on exactly the
maps the search had just been too generous about. That is not a hypothetical
risk invented here; it is the failure `_opening_findings` names in its own
docstring, and it is why a helper mirroring the product's own derivation is
added rather than the spawn being wrapped in a list six times.

Verified before writing: `lot/site_spawns.py` 53,893 B sha256 619F4C3C..., and
`sight_occluders(site_spec, solids=None)` returns `footprints(site_spec,
margin=0.0)` -- the same rects both read-back tests already build, so the
occluder sets agree and only the window changes.

USAGE

    python patches\patch_r51_stale_spawn_callers.py --check
    python patches\patch_r51_stale_spawn_callers.py --selftest
    python patches\patch_r51_stale_spawn_callers.py
    python patches\patch_r51_stale_spawn_callers.py --revert
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r51callers"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "lot" / "tests" / "test_site_spawns.py"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)

#: The size and digest the anchors below were read against. A mismatch is not
#: fatal by itself -- the anchors decide -- but it is printed so a stale device
#: read is visible rather than inferred from a confusing failure later.
EXPECT_BYTES = 25773
EXPECT_SHA = "6A2DB68441F8FA3EC4ED96AA0F9C4B0F8F78672AC9AFFD6502C7E22BB8DC06AD"


# ---------------------------------------------------------------------------
# line endings, keyed off the FILE
# ---------------------------------------------------------------------------
def _eol(raw: bytes) -> str:
    """The file's line ending, or a refusal.

    Keyed off the file's own bytes, never off an anchor: an anchor that happens
    to be one line contains no ending at all and answers LF for a CRLF
    document, which has already written 81 bare LF lines into a CRLF file in
    this repo. Read as bytes, because `Path.read_text` normalises endings and a
    check written on top of it reports every file as LF.
    """
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    if crlf and lf:
        raise SystemExit(
            f"REFUSING: {TARGET.name} has mixed line endings "
            f"({crlf} CRLF, {lf} LF). Normalise it first; this patch will not "
            f"guess which the next line wants.")
    if not crlf and not lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has no line endings at all.")
    return "\r\n" if crlf else "\n"


def _n(text: str) -> str:
    """Anchors are written LF; compare against the file in the same currency."""
    return text.replace("\r\n", "\n")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


# ---------------------------------------------------------------------------
# the edits
# ---------------------------------------------------------------------------
HELPER = '''

def crew_path(positions):
    """The window the opening is judged over, derived the way the search does.

    `opening_engagement_is_fair` takes the stretch of route the crew covers in
    its first second, not the tile it starts on, and `place_enemies` builds
    that with `crew_reaction_path` off the same route it spreads the enemies
    along. A read-back that passed `[spawn]` instead would ask an easier
    question than the search did, and would therefore report a clean opening on
    exactly the maps the search had just been too generous about -- which is
    the one class of defect these read-back tests exist to catch.
    """
    return site_spawns.crew_reaction_path(
        [positions[k] for k in ("spawn", "objective", "extraction")])
'''

#: (name, old, new). Every one is asserted present before any is written.
EDITS = [
    ("helper: crew_path, mirroring place_enemies",
     '''def route(spawn=(51.0, -5.0, 0.0), objective=(35.0, -17.0, 0.9),
          extraction=(117.0, -16.0, 0.0)):
    return {"spawn": spawn, "objective": objective, "extraction": extraction}
''',
     '''def route(spawn=(51.0, -5.0, 0.0), objective=(35.0, -17.0, 0.9),
          extraction=(117.0, -16.0, 0.0)):
    return {"spawn": spawn, "objective": objective, "extraction": extraction}
''' + HELPER),

    ("test_an_enemy_down_an_open_street_inside_sight_range_is_not_fair",
     "        (23.0, 0.0), (0.0, 0.0), [])\n",
     "        (23.0, 0.0), [(0.0, 0.0)], [])\n"),

    ("test_the_same_enemy_behind_a_building_is_fair",
     "        (23.0, 0.0), (0.0, 0.0), [(10.0, -5.0, 14.0, 5.0)])\n",
     "        (23.0, 0.0), [(0.0, 0.0)], [(10.0, -5.0, 14.0, 5.0)])\n"),

    ("test_and_so_is_one_further_off_than_either_side_can_open_fire",
     """        (40.0, 0.0), (0.0, 0.0), [])
    assert site_spawns.opening_engagement_is_fair(
        (52.0, 0.0), (0.0, 0.0), [])
""",
     """        (40.0, 0.0), [(0.0, 0.0)], [])
    assert site_spawns.opening_engagement_is_fair(
        (52.0, 0.0), [(0.0, 0.0)], [])
"""),

    ("test_the_sight_range_itself_is_not_a_standoff",
     """        (site_spawns.OPENING_RANGE, 0.0), (0.0, 0.0), [])
    assert site_spawns.opening_engagement_is_fair(
        (site_spawns.OPENING_RANGE + site_spawns.OPENING_CLEARANCE, 0.0),
        (0.0, 0.0), [])
""",
     """        (site_spawns.OPENING_RANGE, 0.0), [(0.0, 0.0)], [])
    assert site_spawns.opening_engagement_is_fair(
        (site_spawns.OPENING_RANGE + site_spawns.OPENING_CLEARANCE, 0.0),
        [(0.0, 0.0)], [])
"""),

    ("test_no_enemy_can_shoot_the_crew_before_it_has_moved",
     """    plan = site_spawns.place_enemies(BAIE_DORE, route())
    spawn = route()["spawn"][:2]
    occluders = site_spawns.footprints(BAIE_DORE, margin=0.0)
    assert len(plan.positions) == 6
    for i, (x, y, _z) in enumerate(plan.positions):
        assert site_spawns.opening_engagement_is_fair((x, y), spawn, occluders), (
""",
     """    plan = site_spawns.place_enemies(BAIE_DORE, route())
    spawn = route()["spawn"][:2]
    # The window the search used, not the tile. `spawn` is kept because the
    # failure message measures distance from it.
    path = crew_path(route())
    occluders = site_spawns.footprints(BAIE_DORE, margin=0.0)
    assert len(plan.positions) == 6
    for i, (x, y, _z) in enumerate(plan.positions):
        assert site_spawns.opening_engagement_is_fair((x, y), path, occluders), (
"""),

    ("test_the_written_positions_are_read_back_and_not_taken_on_trust",
     """    plan = site_spawns.place_enemies(SEED_5320, SEED_5320_ROUTE)
    spawn = SEED_5320_ROUTE["spawn"][:2]
    occluders = site_spawns.footprints(SEED_5320, margin=0.0)
    assert plan.positions
    for i, point in enumerate(plan.positions):
        assert site_spawns.opening_engagement_is_fair(
            point[:2], spawn, occluders), (
""",
     """    plan = site_spawns.place_enemies(SEED_5320, SEED_5320_ROUTE)
    spawn = SEED_5320_ROUTE["spawn"][:2]
    # Same window the search judged these candidates against, so this reads
    # back the question that was asked rather than an easier one.
    path = crew_path(SEED_5320_ROUTE)
    occluders = site_spawns.footprints(SEED_5320, margin=0.0)
    assert plan.positions
    for i, point in enumerate(plan.positions):
        assert site_spawns.opening_engagement_is_fair(
            point[:2], path, occluders), (
"""),
]


# ---------------------------------------------------------------------------
def _load():
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET} does not exist.")
    raw = TARGET.read_bytes()
    return raw, _eol(raw), _n(raw.decode("utf-8"))


def _report_identity(raw: bytes) -> None:
    got_sha = _sha(raw)
    flag = "" if len(raw) == EXPECT_BYTES else "   <-- NOT the size this was read against"
    print(f"  {TARGET.relative_to(ROOT)}")
    print(f"    bytes  : {len(raw)}   (expected {EXPECT_BYTES}){flag}")
    print(f"    sha256 : {got_sha}")
    if got_sha != EXPECT_SHA:
        print(f"    expected {EXPECT_SHA}")
        print("    NOTE: digest differs from the read these anchors were written "
              "against. The anchors below decide; this line only makes a stale "
              "or moved file visible.")


def check() -> int:
    """Every anchor present exactly once, or say which is not."""
    raw, eol, text = _load()
    _report_identity(raw)
    print(f"    eol    : {'CRLF' if eol == chr(13) + chr(10) else 'LF'}")
    print()
    ok = True
    for name, old, _new in EDITS:
        n = text.count(_n(old))
        if n == 1:
            print(f"  [ok]      {name}")
        else:
            ok = False
            print(f"  [MISSING] {name}  -- anchor found {n} times, wanted 1")
    print()
    if ok:
        print("APPLICABLE: all 7 anchors present exactly once.")
        return 0
    print("NOT APPLICABLE: refusing rather than fuzzy-matching.")
    return 1


def apply() -> int:
    raw, eol, text = _load()
    _report_identity(raw)

    # Check every anchor BEFORE writing any of them. A patch that half-applies
    # and then raises is worse than one that refuses.
    for name, old, _new in EDITS:
        if text.count(_n(old)) != 1:
            raise SystemExit(
                f"REFUSING: anchor for {name} is not present exactly once. "
                f"Nothing has been written. Run --check.")

    if SIDECAR.exists():
        raise SystemExit(
            f"REFUSING: {SIDECAR.name} already exists -- this patch looks "
            f"applied. Use --revert first.")
    shutil.copy2(TARGET, SIDECAR)

    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)

    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
    TARGET.write_bytes(data)

    print()
    print(f"  applied 7 edits")
    print(f"  sidecar : {SIDECAR.name}")
    print(f"  bytes   : {len(raw)} -> {len(data)}  ({len(data) - len(raw):+d})")
    print(f"  sha256  : {_sha(data)}")
    return 0


def revert() -> int:
    if not SIDECAR.exists():
        raise SystemExit(f"REFUSING: no {SIDECAR.name} to revert from.")
    before = TARGET.read_bytes()
    shutil.copy2(SIDECAR, TARGET)
    SIDECAR.unlink()
    after = TARGET.read_bytes()
    print(f"  reverted: {len(before)} -> {len(after)} bytes")
    print(f"  sha256  : {_sha(after)}")
    return 0


def selftest() -> int:
    """Prove the edits say what they claim, and prove the checks can FAIL.

    A selftest that only confirms the happy path has learned nothing. Each
    positive below is paired with a negative that removes the evidence and
    asserts the check notices.
    """
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    raw, eol, text = _load()

    # -- identity ---------------------------------------------------------
    ok(len(raw) == EXPECT_BYTES,
       f"target is {EXPECT_BYTES} bytes (got {len(raw)})")
    ok(_sha(raw) == EXPECT_SHA, "target sha256 matches the read")

    # -- _eol is keyed off the file, and refuses a mixed one ---------------
    ok(_eol(b"a\nb\n") == "\n", "_eol: an LF file reads as LF")
    ok(_eol(b"a\r\nb\r\n") == "\r\n", "_eol: a CRLF file reads as CRLF")
    mixed_refused = False
    try:
        _eol(b"a\r\nb\n")
    except SystemExit:
        mixed_refused = True
    ok(mixed_refused, "_eol: a MIXED file is refused rather than guessed")
    # The trap this rule exists for: a one-line anchor contains no ending, so
    # anything keyed off the anchor answers LF whatever the file is.
    one_line_anchor = "        (23.0, 0.0), (0.0, 0.0), [])"
    ok("\n" not in one_line_anchor,
       "_eol: the trap is real -- an anchor here carries no line ending at all")

    # -- anchors ----------------------------------------------------------
    for name, old, _new in EDITS:
        ok(text.count(_n(old)) == 1, f"anchor present exactly once: {name}")

    # -- the anchors are not already-patched text -------------------------
    ok("def crew_path(positions):" not in text,
       "target is not already patched (no crew_path helper)")

    # -- check() can fail -------------------------------------------------
    # Remove the evidence and confirm the anchor check notices, rather than
    # trusting that it would.
    damaged = text.replace(_n(EDITS[1][1]), "        (23.0, 0.0), MOVED, [])\n", 1)
    ok(damaged.count(_n(EDITS[1][1])) == 0,
       "check() can fail: removing one anchor makes it uncountable")

    # -- what the edits actually change -----------------------------------
    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)

    ok(out != text, "the edits change the file")
    ok(out.count("def crew_path(positions):") == 1,
       "exactly one crew_path helper is added")
    # Counted on the CALL, not on the bare name: the helper's own docstring
    # mentions `crew_reaction_path` in prose as well, so a bare-name count says
    # 2 and means nothing.
    ok(out.count("site_spawns.crew_reaction_path(") == 1,
       "the helper derives the window with one crew_reaction_path call")

    # SIX call sites across FOUR tests, and the two numbers are not
    # interchangeable -- `test_and_so_is_one_further_off...` and
    # `test_the_sight_range_itself...` each assert twice. Asserting 4 here
    # passed for a count that was really 6 and would have gone on passing if
    # two of the edits had silently stopped applying.
    ok(text.count("[(0.0, 0.0)]") == 0 and out.count("[(0.0, 0.0)]") == 6,
       "the geometry assertions gain a one-point path at 6 call sites (0 -> 6)")
    ok(text.count("crew_path(route())") == 0
       and out.count("crew_path(route())") == 1,
       "the BAIE_DORE read-back derives its window from the route")
    ok(text.count("crew_path(SEED_5320_ROUTE)") == 0
       and out.count("crew_path(SEED_5320_ROUTE)") == 1,
       "the SEED_5320 read-back derives its window from the route")

    # No bare `spawn` is left standing in a predicate call. Whitespace-
    # normalised, because two of these calls span a line break in the source
    # and a naive substring search would find neither.
    flat = " ".join(out.split())
    ok("opening_engagement_is_fair( point[:2], spawn," not in flat
       and "opening_engagement_is_fair((x, y), spawn," not in flat,
       "no predicate call is left taking the spawn POINT")
    # ...and prove that search can find something, or it has proven nothing.
    flat_in = " ".join(text.split())
    ok("opening_engagement_is_fair( point[:2], spawn," in flat_in
       and "opening_engagement_is_fair((x, y), spawn," in flat_in,
       "that search CAN fire -- it finds both calls in the unpatched file")

    # -- the predicate itself is untouched --------------------------------
    ok(len(EDITS) == 7 and all("site_spawns.py" not in e[1] for e in EDITS),
       "no edit targets site_spawns.py -- the predicate is not touched")

    # -- the result is still valid python ---------------------------------
    try:
        compile(out, str(TARGET), "exec")
        ok(True, "the patched file compiles")
    except SyntaxError as exc:
        ok(False, f"the patched file compiles ({exc})")

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s)")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("SELFTEST PASSED")
    return 0


def main(argv) -> int:
    arg = argv[1] if len(argv) > 1 else ""
    if arg == "--check":
        return check()
    if arg == "--selftest":
        return selftest()
    if arg == "--revert":
        return revert()
    if arg == "":
        return apply()
    raise SystemExit(f"unknown argument {arg!r}; "
                     f"use --check, --selftest, --revert, or no argument")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
