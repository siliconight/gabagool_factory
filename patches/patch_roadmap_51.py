r"""Roadmap item 51 -- lot's suite, red through four certifications.

    python patches\\patch_roadmap_51.py --check
    python patches\\patch_roadmap_51.py
    python patches\\patch_roadmap_51.py --selftest
    python tools\\roadmap_status.py --write

Written from a run on a CLEAN checkout of lot 0.41.0 -- `git status --short`
and `git stash list` both empty -- so it says out loud that none of this is
fallout from level_factory 0.38.0-0.40.0.

THE ITEM'S JOB IS TO STOP ONE OF THE THREE BEING MISFILED

`test_the_walk_scene_carries_the_placed_positions` fails with
`(37.735, 19.242160304653307)` under an `abs_tol=1e-3` assertion whose
comment is about rounding. It reads like a precision problem and is not one:
the two numbers are 18.5 m apart. Filed as a tolerance it gets "fixed" by
widening the bound, and the finding -- the scene not carrying the position
the planner chose -- disappears. The item says so in the words `must not be
filed as one`, and ends with WHAT NOT TO DO.

NO CODE IS READ HERE and the item says which readings are still open: for the
arity bug, whether the caller or the signature is wrong; for the cover
assertion, whether the search or the check is. Six callers agreeing is weak
evidence, not proof, and it is labelled as weak.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r51"
ANCHOR = "\n### Not to be worked on\n"
INSERT = '*STATUS: OPEN 2026-08-16 -- MEASURED. `lot` 0.41.0, clean tree (`git status --short` and `git stash list` both empty), so these predate tonight\'s level_factory work and are not caused by it: 328 passed, 8 FAILED in 4.26s. THREE defects, not eight: six tests are one arity bug at `site_spawns.py:470`, one is a cover assertion, one is a plan-versus-scene position disagreement of 18.5 m that is wearing a tolerance assertion\'s clothes*\n\n**51. `lot`\'s own suite has been red through every certification this month,\nand one of the three defects is a level that is not the level that was\nplanned.**\nRun on 2026-08-16 against a clean checkout of `lot` 0.41.0, so none of this\nis fallout from level_factory 0.38.0-0.40.0:\n\n```\n8 failed, 328 passed in 4.26s\n```\n\n**ONE: the arity bug, six tests.** `tests/test_site_spawns.py:345` calls the\npredicate with three positional arguments:\n\n```python\nassert site_spawns.opening_engagement_is_fair(\n    point[:2], spawn, occluders), (...)\n```\n\nand `site_spawns.py:470` iterates the second one:\n\n```python\nif all(math.dist(candidate, p) >= reach for p in crew_path):\n```\n\n`spawn` is `SEED_5320_ROUTE["spawn"][:2]`, a single 2-tuple. Bound to\n`crew_path` it iterates to floats, and `math.dist(candidate, 37.7)` raises\n`TypeError: \'float\' object is not iterable`. A spawn POINT is arriving where\na crew PATH is wanted. Six red lines, one fix:\n\n```\ntest_an_enemy_down_an_open_street_inside_sight_range_is_not_fair\ntest_the_same_enemy_behind_a_building_is_fair\ntest_and_so_is_one_further_off_than_either_side_can_open_fire\ntest_the_sight_range_itself_is_not_a_standoff\ntest_no_enemy_can_shoot_the_crew_before_it_has_moved\ntest_the_written_positions_are_read_back_and_not_taken_on_trust\n```\n\nWhich of the two sides is wrong is NOT established here. The caller may be\npassing the wrong thing, or the signature may have gained a parameter without\nits callers. Six tests agreeing on the same call shape is weak evidence for\nthe caller, and the function\'s own docstring is the thing to read first.\n\n**TWO: the cover assertion.**\n\n```\ntest_site_cover.py::test_the_cover_that_was_planned_is_in_the_scene_that_gets_shipped\nAssertionError: Enemy_5 still sees the crew spawn down 51.9 m of open ground\n               in the scene that shipped\n```\n\nThat test exists because a search whose model of cover is wrong passes every\ncandidate on the way in and still writes a map that opens with a shot -- the\ncheck the search cannot perform on itself. It is currently failing, which\nmeans either the search or the check is wrong, and both readings are worth\nthe same until somebody measures.\n\n**THREE, AND THE ONE THAT MATTERS MOST: the scene does not carry the position\nthe planner chose.**\n\n```\ntest_site_spawns.py:461  test_the_walk_scene_carries_the_placed_positions\n    for got, want in zip((gx, gy, gz), (sx, sz + 1.0, -sy)):\n        assert math.isclose(got, want, abs_tol=1e-3), (got, want)\nAssertionError: (37.735, 19.242160304653307)\n```\n\n**This is not a tolerance failure and must not be filed as one.** 37.735\nagainst 19.242 is 18.5 m apart; no `abs_tol` closes that. The test\'s comment\nis about surviving two roundings in the same direction, which is what makes\nthe assertion LOOK like a precision check and is exactly how this would get\nwritten off. The pairing is an axis remap -- site `(x, y, z)` to Godot\n`(x, z + lift, -y)` -- and the first pair, `gx` against `sx`, is the one that\nfails. An ordering difference, or a remap applied twice, produces a gap of\nthat size; a rounding never does.\n\nIts docstring states the stake: *"The scene is the artifact Laser Tag reads;\nthe plan is only useful if it is what got written."* It asserts\n`len(written) == len(planned) == 6` and both sides pass that, so six enemies\nwere written and six were planned -- they are just not in the same places.\n\n**THAT IS ROADMAP 48\'s FAMILY, ONE TOOL DOWN.** 48 was the graded site not\nbeing the shipped site. This is the planned SPAWN not being the shipped\nspawn, inside the tool that does the placing, caught by a test written for\nprecisely that and red long enough that four certifications have shipped over\nit. `factory-v1.25.0` records the 8 failures but not this reading of them.\n\nWHAT NOT TO DO\n\nDo not fix the tolerance. Do not skip the test. The assertion is correct and\nthe number it prints is the finding.\n\n'
_CRLF = "\r\n"


def _eol(b: str) -> str:
    c = b.count(_CRLF)
    return _CRLF if c > (b.count("\n") - c) else "\n"


def _as(t: str, eol: str) -> str:
    return t.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    p = root / ROADMAP
    if not p.is_file():
        print(f"REFUSING: {ROADMAP} is not here")
        return 1
    raw = p.read_bytes()
    b = raw.decode("utf-8")
    eol = _eol(b)
    if _as("**51. `lot`'s own suite has been red", eol) in b:
        print(f"  already applied  {ROADMAP}")
        return 0
    a = _as(ANCHOR, eol)
    if b.count(a) != 1:
        print(f"REFUSING: the closing heading occurs {b.count(a)} time(s)")
        return 1
    out = b.replace(a, _as("\n" + INSERT + "### Not to be worked on\n", eol), 1)
    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {ROADMAP}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 "
          f"{hashlib.sha256(data).hexdigest()[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    md = (root / ROADMAP).read_bytes().decode("utf-8").replace(_CRLF, "\n")
    m = "**51. `lot`'s own suite has been red"
    check("item 51 is present", m in md)
    if m not in md:
        print(f"\n  {bad} FAILURE(S)")
        return 1
    i = md.index(m)
    s = " ".join(md[:i].rstrip().splitlines()[-1].split())
    body = md[i:md.index("### Not to be worked on", i)]
    flat = " ".join(body.split())

    check("the STATUS says the tree was clean, so this is not our fallout",
          "clean tree" in s and "predate tonight's level_factory work" in s)
    check("...and gives the count", "328 passed, 8 FAILED in 4.26s" in s)
    check("...and says three defects, not eight",
          "THREE defects, not eight" in s)

    check("the arity bug quotes both sides",
          "opening_engagement_is_fair(" in body
          and "for p in crew_path" in body
          and "site_spawns.py:470" in body)
    check("...and names all six tests",
          all(t in body for t in (
              "test_an_enemy_down_an_open_street_inside_sight_range_is_not_fair",
              "test_the_same_enemy_behind_a_building_is_fair",
              "test_and_so_is_one_further_off_than_either_side_can_open_fire",
              "test_the_sight_range_itself_is_not_a_standoff",
              "test_no_enemy_can_shoot_the_crew_before_it_has_moved",
              "test_the_written_positions_are_read_back_and_not_taken_on_trust")))
    check("...and leaves open which side is wrong",
          "Which of the two sides is wrong is NOT established here" in flat
          and "weak evidence" in flat)

    check("the cover failure is quoted verbatim",
          "Enemy_5 still sees the crew spawn down 51.9 m of open ground"
          in body)
    check("...and both readings are left equally open",
          "both readings are worth the same until somebody measures" in flat)

    check("the third failure is quoted with its numbers",
          "(37.735, 19.242160304653307)" in body
          and "abs_tol=1e-3" in body)
    check("...and is explicitly NOT a tolerance failure",
          "This is not a tolerance failure and must not be filed as one"
          in flat and "18.5 m apart" in flat)
    check("...and explains why it LOOKS like one",
          "is exactly how this would get written off" in flat)
    check("...and names the remap that makes the pairing legible",
          "(x, z + lift, -y)" in body)
    check("...and that the counts agree while the places do not",
          "six enemies were written and six were planned" in flat)
    check("...and ties it to roadmap 48's family",
          "ROADMAP 48's FAMILY, ONE TOOL DOWN" in body)
    check("it ends with what not to do",
          "Do not fix the tolerance. Do not skip the test." in flat)

    nums = [int(x) for x in re.findall(r"^\*\*(\d+)\. ", md, re.M)]
    check("the numbering is contiguous through 51", nums[-3:] == [49, 50, 51])
    check("every fenced block in 51 is closed", body.count("```") % 2 == 0)
    check("it ends with a blank line", body.endswith("\n\n"))
    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  three defects, written down before anyone reads the code"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        p = root / ROADMAP
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {ROADMAP}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {ROADMAP}")
        return 0
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_roadmap_51.py --selftest")
        print("    python tools\\roadmap_status.py --write")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
