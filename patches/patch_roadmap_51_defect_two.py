#!/usr/bin/env python3
"""Roadmap 51: defect two measured, fixed, and the framing corrected.

Item 51 files defect two as "either the search or the check is wrong, and both
readings are worth the same until somebody measures". Somebody measured. It was
NEITHER, and it was two faults stacked:

1. `assemble` never cleared the crew spawn, so the cover was planned for a crew
   standing INSIDE building `b0` while the scene shipped the cleared spawn
   9.5 m away. Fixed by `patch_lot_cover_ships_spawn.py`.
2. With that corrected the planner became honest -- `open_lines` 0 -> 1 -- and
   showed the real fault: the 12-piece opening budget went to lines sorted
   longest-first, and NONE of the twelve touched a line the crew stands on.
   Six broke enemy-to-enemy sightlines. Fixed by
   `patch_lot_cover_crew_first.py`.

The check was right the whole time and `test_site_cover.py` was never modified.

WHY THIS PATCH DOES NOT STAMP AN EXPECTED BYTE COUNT

`PIPELINE_ROADMAP.md` has been rewritten twice since it was last read here --
`patch_roadmap_51_mechanism.py` then `tools/roadmap_status.py --write`
regenerating the derived table -- so any size carried in this file would be a
guess, and a guessed stamp is worse than none: it invites the reader to trust
it. The identity is PRINTED for the record and the ANCHORS are the authority;
both anchor texts were read verbatim from the file in the session that wrote
this. Drift refuses.

AFTER APPLYING:

    python tools\\roadmap_status.py --write
    python tools\\roadmap_status.py --check

USAGE

    python patches\\patch_roadmap_51_defect_two.py --check
    python patches\\patch_roadmap_51_defect_two.py --selftest
    python patches\\patch_roadmap_51_defect_two.py
    python patches\\patch_roadmap_51_defect_two.py --revert
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r51two"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "PIPELINE_ROADMAP.md"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)


def _eol(raw: bytes) -> str:
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    if crlf and lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has mixed line endings "
                         f"({crlf} CRLF, {lf} LF).")
    if not crlf and not lf:
        raise SystemExit(f"REFUSING: {TARGET.name} has no line endings.")
    return "\r\n" if crlf else "\n"


def _n(t: str) -> str:
    return t.replace("\r\n", "\n")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


# --- anchor 1a: the STATUS line's HEAD still summarises three-minus-one.
# Replacing only the tail left "ONE STILL UNDIAGNOSED" standing at the front of
# the same sentence, which the selftest caught. The head and tail of one line
# are two edits and both have to move.
STATUS_HEAD_OLD = ("*STATUS: NARROWED 2026-08-16 -- ONE OF THREE FIXED, ONE "
                   "MECHANISM REFUTED, ONE STILL UNDIAGNOSED.")

STATUS_HEAD_NEW = ("*STATUS: CLOSED 2026-08-16 -- ALL THREE FIXED AND "
                   "RE-MEASURED. TWO of the three mechanisms this item "
                   "proposed were refuted by measurement; the third was "
                   "correct as written.")

# --- anchor 1b: the STATUS line, which currently calls defect two undiagnosed
STATUS_OLD_TAIL = (
    "Defect TWO (`test_site_cover.py`) is STILL UNDIAGNOSED; "
    "noted only that `open_span` returned exactly the full crew-to-enemy "
    "distance (51.94522232553231 on both sides of the assertion), and that "
    "the `LOT_ENEMY_SPAWN_STANDOFF` finding in the same run calls that enemy "
    "52.8 m from the crew where the test measures 51.945 -- two instruments, "
    "one distance, two answers, unresolved*"
)

STATUS_NEW_TAIL = (
    "Defect TWO is MEASURED AND FIXED, and it was neither of the two things "
    "this item offered. TWO FAULTS STACKED. First, `assemble` never cleared "
    "the crew spawn, so cover was planned for a crew standing INSIDE building "
    "`b0` at (-70.0, 30.0) while the scene shipped the cleared spawn at "
    "(-60.5, 30.0); from inside a shell almost every sightline reads as "
    "already broken, which is why `plan_cover` claimed `open_lines=0` over a "
    "map with a clear 51.9 m lane. `patch_lot_cover_ships_spawn.py`. That also "
    "settles the 52.8-versus-51.945 instrument disagreement: two different "
    "enemy sets, both numbered from zero, one placed from each spawn. Second, "
    "with the inputs corrected the planner became honest (`open_lines` 0 -> 1) "
    "and showed the real fault: the 12-piece opening budget is spent "
    "longest-first over ALL marker pairs, and none of the twelve touched a "
    "line the crew stands on -- six broke enemy-to-enemy sightlines, which "
    "describe nothing about who opens fire on the crew. Serving the crew's "
    "lines first, same budget, stable sort so longest-first survives inside "
    "each group: 3 of 12 pieces now touch the crew, all seven of its lines "
    "close, `open_lines` 0. `patch_lot_cover_crew_first.py`. "
    "`test_site_cover.py` was NOT modified -- it asserted the right contract "
    "throughout. STILL OPEN, deliberately: `assemble` and `write_walk_scene` "
    "derive the mission points twice and this only makes the two agree; "
    "enemy-to-enemy pairs still consume budget after the crew is served "
    "(excluding them outright measured 7 opening pieces and 18 total, also "
    "with 0 open lines); and cover planning is still coupled to "
    "`place_enemies`, which is awkward given enemy placement belongs to the "
    "gameplay layer and not to this pipeline*"
)

# --- anchor 2: the defect-two body, kept and superseded above
TWO_OLD = """**TWO: the cover assertion.**
"""

TWO_NEW = '''**TWO: the cover was planned for a crew standing somewhere else, and then
for the wrong lines. -- MEASURED AND FIXED 2026-08-16.**

Two faults, one behind the other. Neither is "the search" or "the check".

**FAULT ONE: cover planned for a crew the scene does not ship.** `assemble`
seated the mission points and never cleared the crew spawn, so it planned from
(-70.0, 30.0) -- the dead centre of `b0`, footprint x -78.0 .. -62.0 --
while `write_walk_scene` cleared it to (-60.5, 30.0) and shipped that. From
inside a shell the building occludes almost everything, so `plan_cover`
reported `open_lines=0`: it believed it had covered a map it had never
correctly measured. One statement in `assemble` fixes it; the shipped spawn
does not move, because `write_walk_scene` already cleared it and seat+clear is
idempotent (measured: 0.000000 m on a second application).

This also disposes of the 52.8-versus-51.945 disagreement recorded above. Two
`place_enemies` calls fire inside one `assemble` -- `lot.py:1874` for the cover
plan and `lot.py:1257` for the scene -- and before the fix they returned
different six-enemy sets, both numbered from zero. There was no instrument
error. There were two different `Enemy_5`s.

**FAULT TWO: the opening budget never reached the crew.** With the inputs
corrected the planner became honest -- `open_lines` 0 -> 1 -- and the real
defect showed. `open_sightlines` returns every marker pair over the opening
range, longest first, and `plan_cover` takes twelve. On this site those twelve
were:

```
Cover_0  Extraction -> Objective     Cover_6   Enemy_0 -> Extraction
Cover_1  Enemy_5 -> Objective        Cover_7   Enemy_4 -> Objective
Cover_2  Enemy_2 -> Enemy_5   <--    Cover_8   Enemy_0 -> Enemy_5   <--
Cover_3  Enemy_3 -> Enemy_5   <--    Cover_9   Enemy_5 -> Extraction
Cover_4  Enemy_0 -> Objective        Cover_10  Enemy_4 -> Enemy_5   <--
Cover_5  Enemy_1 -> Enemy_5   <--    Cover_11  Enemy_0 -> Enemy_3   <--
```

ZERO of the twelve involve `LT_PlayerSpawn`. Six break enemy-to-enemy
sightlines -- cover so one enemy cannot see another, which says nothing about
who opens fire on the crew, since they are the same team. The crew had seven
open lines (130.5, 115.9, 106.4, 77.3, 67.8, 53.9, 51.9 m) and got none, and
`unbreakable` was 0 throughout, so a placeable spot existed the whole time.

Serving the crew's lines first fixes it on the SAME budget. The longest-first
heuristic is kept inside each group by sorting stably on one boolean:

```
                    opening pieces  touching crew  total  open_lines  test
longest first                   12              0     23           1  FAILS
crew lines first                12              3     23           0  PASSES
```

Three pieces close all seven crew lines -- "the worst line's fix usually
shortens three others" working, finally pointed at the lines that matter.

`test_site_cover.py` was NOT modified. It asserted the right contract from the
start, and the instruction in this item not to loosen or skip it was correct.

WHAT IS STILL OPEN, DELIBERATELY

- `assemble` and `write_walk_scene` still derive the mission points twice,
  independently. Fault one is fixed by making the two agree, not by making
  there be one.
- Enemy-to-enemy pairs still consume budget once the crew is served. Excluding
  them outright measured 7 opening pieces and 18 total, also with 0 open
  lines -- fewer pieces for the same result, but it is a separate decision
  about what `open_sightlines` should return at all.
- Cover planning still derives its priorities from `place_enemies`, which is
  awkward if enemy placement is leaving this pipeline for the gameplay layer.

The reading this replaces, kept because a retracted finding is cheaper to keep
than to rediscover:

**TWO: the cover assertion.**
'''

EDITS = [
    ("item 51 STATUS head: all three fixed", STATUS_HEAD_OLD, STATUS_HEAD_NEW),
    ("item 51 STATUS tail: defect two measured and fixed",
     STATUS_OLD_TAIL, STATUS_NEW_TAIL),
    ("defect two: the measured account above the original", TWO_OLD, TWO_NEW),
]


def _load():
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET} does not exist.")
    raw = TARGET.read_bytes()
    return raw, _eol(raw), _n(raw.decode("utf-8"))


def _identity(raw: bytes):
    crlf = raw.count(b"\r\n")
    lone = raw.count(b"\n") - crlf
    print(f"  {TARGET.name}")
    print(f"    bytes  : {len(raw)}   (no expected value carried -- see the "
          f"module docstring)")
    print(f"    sha256 : {_sha(raw)}")
    print(f"    eol    : {crlf} CRLF, {lone} lone LF")


def check() -> int:
    raw, _e, text = _load()
    _identity(raw)
    print()
    ok = True
    for name, old, _new in EDITS:
        n = text.count(_n(old))
        print(f"  [{'ok' if n == 1 else 'MISSING'}]  {name}  (found {n})")
        ok = ok and n == 1
    print()
    print("APPLICABLE: both anchors present exactly once." if ok
          else "NOT APPLICABLE: refusing rather than fuzzy-matching.")
    return 0 if ok else 1


def apply() -> int:
    raw, eol, text = _load()
    _identity(raw)
    for name, old, _new in EDITS:
        if text.count(_n(old)) != 1:
            raise SystemExit(f"REFUSING: anchor for {name} not present exactly "
                             f"once. Nothing written.")
    if SIDECAR.exists():
        raise SystemExit(f"REFUSING: {SIDECAR.name} exists. Use --revert.")
    shutil.copy2(TARGET, SIDECAR)
    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)
    data = out.replace("\n", eol).encode("utf-8")
    TARGET.write_bytes(data)
    print()
    print(f"  applied {len(EDITS)} edits")
    print(f"  sidecar : {SIDECAR.name}")
    print(f"  bytes   : {len(raw)} -> {len(data)}  ({len(data) - len(raw):+d})")
    print(f"  sha256  : {_sha(data)}")
    print(f"  endings : {data.count(bytes([13, 10]))} CRLF, "
          f"{data.count(bytes([10])) - data.count(bytes([13, 10]))} lone LF")
    print()
    print("  NEXT: python tools\\roadmap_status.py --write")
    print("        python tools\\roadmap_status.py --check")
    return 0


def revert() -> int:
    if not SIDECAR.exists():
        raise SystemExit(f"REFUSING: no {SIDECAR.name} to revert from.")
    before = TARGET.read_bytes()
    shutil.copy2(SIDECAR, TARGET)
    SIDECAR.unlink()
    after = TARGET.read_bytes()
    print(f"  reverted: {len(before)} -> {len(after)} bytes, sha256 {_sha(after)}")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    raw, eol, text = _load()
    ok(eol == "\r\n", "the roadmap reads as CRLF")
    ok(raw.count(b"\n") - raw.count(b"\r\n") == 0,
       "the roadmap has no lone LF before the edit")
    for name, old, _new in EDITS:
        ok(text.count(_n(old)) == 1, f"anchor present exactly once: {name}")

    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)
    ok(out != text, "the edits change the file")

    # The superseded reading is KEPT, and sits BELOW the one replacing it.
    ok(out.count("**TWO: the cover assertion.**") == 1,
       "the original heading survives exactly once (kept, not deleted)")
    ok("either the search or the check is wrong" in out,
       "the refuted body is kept verbatim")
    ok(out.index("MEASURED AND FIXED 2026-08-16")
       < out.index("**TWO: the cover assertion.**"),
       "the measured account sits ABOVE the reading it replaces")
    # SCOPED TO THE STATUS LINE, not the whole document. `roadmap_status.py
    # --write` copies status text into the DERIVED table near the top, so a
    # whole-document search finds that copy too and cannot tell "the status
    # line still says it" from "the table has not been regenerated yet". The
    # first version of this check was the whole-document form; it passed here
    # only because this sandbox had never run `roadmap_status.py`, and it FAILED
    # on a real tree for a reason that was not a defect.
    status_line = next(l for l in out.split("\n")
                       if l.startswith("*STATUS:") and "ALL THREE FIXED" in l)
    ok("STILL UNDIAGNOSED" not in status_line,
       "the STATUS LINE no longer calls defect two undiagnosed")
    stale_table = [i for i, l in enumerate(out.split("\n"), 1)
                   if l.lstrip().startswith("|") and "STILL UNDIAGNOSED" in l]
    if stale_table:
        print(f"        (note) the derived table still carries the old status "
              f"text on line(s) {stale_table} -- expected, and cleared by "
              f"`roadmap_status.py --write`, which must be run after this patch)")

    # Defect three's block must be untouched by this patch.
    ok(out.count("MECHANISM CORRECTED 2026-08-16") == 1,
       "defect three's correction is left alone")
    ok(out.count("THAT IS ROADMAP 48's FAMILY, ONE TOOL DOWN.") == 1,
       "defect three's refuted body is left alone")

    # STATUS vocabulary is a closed set.
    verbs = ("OPEN", "CLOSED", "RETRACTED", "NARROWED", "SUPERSEDED", "ANALYSIS")
    line = next(l for l in out.split("\n")
                if l.startswith("*STATUS:") and "ALL THREE FIXED" in l)
    ok(line.split()[1] in verbs, f"STATUS verb is in the vocabulary ({line.split()[1]})")
    ok(line.endswith("*"), "the STATUS line is still italic-delimited")
    ok(line.count("*STATUS:") == 1, "the STATUS line was not doubled")

    # Prove the anchor checks can fail.
    damaged = text.replace(_n(TWO_OLD), "**TWO: moved.**\n", 1)
    ok(damaged.count(_n(TWO_OLD)) == 0,
       "check() can fail: removing an anchor makes it uncountable")

    data = out.replace("\n", eol).encode("utf-8")
    lone = data.count(bytes([10])) - data.count(bytes([13, 10]))
    ok(lone == 0, f"no lone LF is written into the CRLF document (got {lone})")
    ok(data.count(bytes([13, 10])) > raw.count(b"\r\n"),
       "the CRLF count grew, as an insertion should make it")

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
