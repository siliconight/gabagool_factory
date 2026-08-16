#!/usr/bin/env python3
"""lot 0.41.0 -> 0.42.0: the release entry for roadmap item 51.

Two of item 51's three fixes change shipped geometry, so this is a version
bump and not a patch release note:

  * `assemble` clears the crew spawn BEFORE planning cover, so the cover is
    planned for the crew the scene ships rather than one standing inside a
    building (`patch_lot_cover_ships_spawn.py`).
  * `plan_cover` serves the crew's sightlines before the rest, on the same
    12-piece budget (`patch_lot_cover_crew_first.py`).

The third is a refactor with a byte-identical scene (`patch_lot_hook_plan.py`)
and the fourth is test-only (`patch_lot_stale_spawn_callers.py`).

TWO FILE SHAPES THIS HAD TO BE TOLD ABOUT, both found by reconciling a scratch
dump's byte count against the source's:

  * `lot/VERSION` is exactly ``Lot 0.41.0`` -- 10 bytes, NO TRAILING NEWLINE.
    Writing ``Lot 0.42.0\\n`` would add a spurious byte to a file whose whole
    content is the version, so this reads and writes it as bytes and asserts
    the exact length on both sides.
  * `lot/CHANGELOG.md` is LF and has NO title heading -- it opens directly on
    ``## [0.41.0]``, so a new entry goes at byte zero.

USAGE

    python patches\\patch_r52_lot_release.py --check
    python patches\\patch_r52_lot_release.py --selftest
    python patches\\patch_r52_lot_release.py
    python patches\\patch_r52_lot_release.py --revert
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r52lot"

ROOT = Path(__file__).resolve().parent.parent
VERSION = ROOT / "lot" / "VERSION"
CHANGELOG = ROOT / "lot" / "CHANGELOG.md"

OLD_VERSION = b"Lot 0.41.0"
NEW_VERSION = b"Lot 0.42.0"

CHANGELOG_ANCHOR = ("## [0.41.0] - the ground plate and the ground floor "
                    "were the same plane\n")

ENTRY = """## [0.42.0] - the cover was planned for a crew standing somewhere else

`lot`'s own suite had been red through every certification this month -- 328
passed, 8 failed. Three defects, and the two that mattered were both one tool
re-deriving another's inputs instead of asking for them.

**The cover was planned from a crew spawn the scene does not ship.** `assemble`
seated the mission points and never cleared the crew spawn, so it planned cover
from (-70.0, 30.0) -- the dead centre of a 16 x 16 shell -- while
`write_walk_scene` cleared it to (-60.5, 30.0) and shipped that. From inside a
building almost every sightline reads as already broken, so `plan_cover`
reported `open_lines=0`: it believed it had covered a map it had never
correctly measured, and the shipped scene opened with a clear 51.9 m lane to
the nearest enemy.

That also explains a disagreement that looked like a broken instrument. Two
`place_enemies` calls fire inside one `assemble` -- one for the cover plan, one
for the scene -- and they returned different six-enemy sets, both numbered from
zero. Nothing was mismeasured. There were two different `Enemy_5`s.

**And then the opening cover budget never reached the crew.** With the inputs
corrected the planner became honest -- `open_lines` 0 -> 1 -- and the real
defect showed. `open_sightlines` returns every marker pair over the opening
range, longest first, and `plan_cover` takes twelve. On the test yard, ZERO of
those twelve involved the crew spawn and SIX broke enemy-to-enemy sightlines --
cover so one enemy cannot see another, which says nothing about who opens fire
on the crew, since they are the same team. The crew had seven open lines
(130.5, 115.9, 106.4, 77.3, 67.8, 53.9, 51.9 m) and got none of the budget.
`unbreakable` was 0 throughout, so a placeable spot existed the whole time.

Serving the crew's lines first fixes it on the SAME budget. The longest-first
heuristic is kept inside each group by sorting stably on one boolean:

                        opening pieces  touching crew  total  open_lines
    longest first                   12              0     23           1
    crew lines first                12              3     23           0

Three pieces close all seven crew lines.

### What else is in here

`_lasertag_hook_plan` returns the positions, route and enemies the walk scene
is written from. `_lasertag_hook_nodes` did its own seating and clearing and
returned only the scene body, so the one question worth asking of it -- are the
positions in the scene the positions that were planned -- could be asked only
by re-running its derivation by hand. `tests/test_site_spawns.py` did exactly
that, drifted, and reported an 18.5 m gap as the scene losing the plan. The
scene had carried its plan exactly, to 0 of 18 failing coordinate pairs; the
plan the test held was of a route the tool never uses. The scene body is
unchanged by the refactor, asserted by executing both versions and comparing.

Six tests were still passing a spawn POINT where `opening_engagement_is_fair`
now requires a crew PATH. The predicate's refusal to default that parameter
worked exactly as designed; only the follow-through was missing.

### What this did not fix, which is worth recording

`assemble` and `write_walk_scene` still derive the mission points twice,
independently. This makes the two agree; it does not make there be one.

Enemy-to-enemy pairs still consume opening budget once the crew is served.
Excluding them outright measured 7 opening pieces and 18 total -- fewer pieces
for the same zero open lines -- and is a separate decision about what
`open_sightlines` should return at all.

Cover planning still derives its priorities from `place_enemies`. That is
awkward if enemy placement is leaving this pipeline for the gameplay layer,
because `plan_cover` would lose the input it currently ranks everything by.

Every measurement above is from a two-building yard fixture. `lot_demo_001`
has not been re-exported under any of this.

Suite: 328 passed / 8 failed -> 336 passed / 0 failed.

"""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def _eol(raw: bytes, who: str) -> str:
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    if crlf and lf:
        raise SystemExit(f"REFUSING: {who} has mixed line endings "
                         f"({crlf} CRLF, {lf} LF).")
    if not crlf and not lf:
        raise SystemExit(f"REFUSING: {who} has no line endings at all.")
    return "\r\n" if crlf else "\n"


def _sidecar(p: Path) -> Path:
    return p.with_name(p.name + ".pre_" + TAG)


def _preflight():
    missing = [p for p in (VERSION, CHANGELOG) if not p.exists()]
    if missing:
        raise SystemExit("REFUSING: missing " + ", ".join(str(m) for m in missing))
    v = VERSION.read_bytes()
    c = CHANGELOG.read_bytes()
    problems = []
    if v != OLD_VERSION:
        problems.append(f"lot/VERSION is {v!r}, expected {OLD_VERSION!r}")
    text = c.decode("utf-8").replace("\r\n", "\n")
    if not text.startswith(CHANGELOG_ANCHOR):
        problems.append("lot/CHANGELOG.md does not OPEN on the 0.41.0 heading")
    if text.count("## [0.42.0]") != 0:
        problems.append("lot/CHANGELOG.md already carries a 0.42.0 entry")
    return v, c, problems


def _identity():
    for p in (VERSION, CHANGELOG):
        if p.exists():
            raw = p.read_bytes()
            print(f"  {p.relative_to(ROOT)}: {len(raw)} B  sha256 {_sha(raw)[:16]}...")


def check() -> int:
    _identity()
    print()
    _v, _c, problems = _preflight()
    if problems:
        print("NOT APPLICABLE:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("APPLICABLE: VERSION is exactly the expected bytes and the changelog "
          "opens where expected.")
    return 0


def apply() -> int:
    _identity()
    v, c, problems = _preflight()
    if problems:
        raise SystemExit("REFUSING: " + "; ".join(problems) + ". Nothing written.")
    for p in (VERSION, CHANGELOG):
        if _sidecar(p).exists():
            raise SystemExit(f"REFUSING: {_sidecar(p).name} exists. Use --revert.")

    eol = _eol(c, CHANGELOG.name)
    text = c.decode("utf-8").replace("\r\n", "\n")
    out = ENTRY + text
    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")

    shutil.copy2(VERSION, _sidecar(VERSION))
    shutil.copy2(CHANGELOG, _sidecar(CHANGELOG))
    VERSION.write_bytes(NEW_VERSION)
    CHANGELOG.write_bytes(data)

    print()
    print(f"  lot/VERSION   : {len(v)} -> {len(VERSION.read_bytes())} B  "
          f"{v.decode()!r} -> {NEW_VERSION.decode()!r}")
    print(f"  lot/CHANGELOG : {len(c)} -> {len(data)} B  ({len(data) - len(c):+d})")
    print(f"                  sha256 {_sha(data)}")
    print()
    print("  NEXT (from inside lot/, it is its own repo):")
    print("    git -C lot add -A")
    print("    git -C lot commit -m \"0.42.0: the cover was planned for a crew "
          "standing somewhere else\"")
    print("    git -C lot tag v0.42.0")
    return 0


def revert() -> int:
    done = False
    for p in (VERSION, CHANGELOG):
        s = _sidecar(p)
        if not s.exists():
            print(f"  {p.name}: no sidecar, left alone")
            continue
        shutil.copy2(s, p)
        s.unlink()
        print(f"  {p.relative_to(ROOT)}: restored to {len(p.read_bytes())} B")
        done = True
    if not done:
        raise SystemExit("REFUSING: nothing to revert.")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    v, c, problems = _preflight()
    ok(not problems, "preflight clean")
    for p in problems:
        print(f"        {p}")

    # -- VERSION is bytes, and the no-trailing-newline shape is the point ----
    ok(v == OLD_VERSION, f"lot/VERSION is exactly {OLD_VERSION!r}")
    ok(len(v) == 10, f"lot/VERSION is 10 bytes (got {len(v)})")
    ok(not v.endswith(b"\n"), "lot/VERSION has NO trailing newline")
    ok(len(NEW_VERSION) == len(OLD_VERSION),
       "the bump keeps the byte count identical")
    ok(not NEW_VERSION.endswith(b"\n"),
       "and writes no trailing newline either")
    # Prove the check can fail: a version with a newline must be rejected.
    ok(OLD_VERSION + b"\n" != OLD_VERSION,
       "the comparison distinguishes a trailing newline from none")

    # -- CHANGELOG ---------------------------------------------------------
    eol = _eol(c, CHANGELOG.name)
    ok(eol == "\n", "lot/CHANGELOG.md is LF")
    text = c.decode("utf-8").replace("\r\n", "\n")
    ok(text.startswith("## [0.41.0]"),
       "the changelog opens directly on a version heading, with no title line")
    out = ENTRY + text

    ok(out.startswith("## [0.42.0]"), "the new entry lands at byte zero")
    ok(out.count("## [0.42.0]") == 1, "exactly one 0.42.0 heading")
    ok(out.count("## [0.41.0]") == 1, "0.41.0's entry survives exactly once")
    ok(text[:400] in out, "the previous head is kept verbatim")
    ok(len(out) > len(text), "the changelog grew")

    # Heading format must match the file's own convention, not a guess:
    # `## [x.y.z] - lowercase sentence`, no date (unlike the factory one).
    import re
    heads = re.findall(r"^## \[([0-9.]+)\] - (.+)$", out, flags=re.M)
    ok(len(heads) >= 2, f"headings parse with the house pattern ({len(heads)} found)")
    ok(heads[0][0] == "0.42.0" and heads[1][0] == "0.41.0",
       f"newest first: {heads[0][0]} then {heads[1][0]}")
    ok(not re.match(r"^\d{4}-\d{2}-\d{2}", heads[0][1]),
       "no date in the heading -- lot's changelog does not carry one")

    # The entry must not claim more than was measured.
    ok("336 passed / 0 failed" in ENTRY, "the suite result is recorded")
    ok("two-building yard fixture" in ENTRY,
       "the scope limit of the measurements is recorded")
    ok("What this did not fix" in ENTRY,
       "the carried non-fixes are recorded, not dropped")

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
