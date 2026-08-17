#!/usr/bin/env python3
"""Roadmap 52: lot_demo_001 re-measured. And item 9 gets a status line.

TWO EDITS.

ITEM 52 IS NEW. `lot_demo_001` had not been re-exported since Lot 0.33.0 -- the
provenance receipt on its cached assemble said so, `evaluated_utc
2026-08-13T23:20:57`, `tool_version "Lot 0.33.0"`. Every number the roadmap
holds about that mission came from nine minor versions back. It has now been
re-run under level_factory 0.40.0 and lot 0.42.0, all stages executing rather
than cache-hitting, and the artifacts are stamped (`tool_version "Lot 0.42.0"`,
`repository_commit df848df`).

The entry records what was measured, and -- the part worth the item -- a change
that was tried, measured and REJECTED, with the reason. `route_open: 14` looks
like a defect, is not one, and the next reader will otherwise spend the same
hour discovering that. It cost one.

ITEM 9 GETS A STATUS LINE. It is one of the 25 unclassified items and infers
CLOSED from its own prose "Closed 2026-07-28 as Lot 0.28.0". Its stated
residual -- "Lot still cannot answer 'is this anchor over anything?' offline"
-- now has a SECOND measured instance, and the roadmap's `library_walk.py`
passage already attributed the first to it. NARROWED with both.

The `*STATUS: NARROWED 2026-08-14 ...*` line at the END of item 9's block
belongs to item 10, per the one-line-above convention. This adds item 9's own,
above its heading, and the selftest asserts item 10's is untouched.

NO EXPECTED BYTE COUNT IS CARRIED. The roadmap has been rewritten seven times
today. Anchors were read this session from a dump that reconstructed to delta
zero at 272,806 B; the identity is printed and drift refuses.

USAGE

    python patches\\patch_roadmap_52_lot_demo.py --check
    python patches\\patch_roadmap_52_lot_demo.py --selftest
    python patches\\patch_roadmap_52_lot_demo.py
    python patches\\patch_roadmap_52_lot_demo.py --revert

AFTER APPLYING:

    python tools\\roadmap_status.py --write
    python tools\\roadmap_status.py --check
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r53item52"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "PIPELINE_ROADMAP.md"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


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


# --- edit 1: item 9's own status line, above its heading --------------------
ITEM9_ANCHOR = "**9. Lot emits nav-QA anchors nothing checks.**"

ITEM9_STATUS = (
    "*STATUS: NARROWED 2026-08-16 -- the residual this item names for itself, "
    "\"Lot still cannot answer 'is this anchor over anything?' offline\", now "
    "has TWO measured instances and they agree. `ref_pvp` on 2026-08-14: an "
    "objective marker 3.60 m above the site ground plane, `library_walk.py` "
    "the blocked site of 20, walkers finishing 15 of 15 legs with 0 stuck. "
    "`lot_demo_001` candidate seed_5219 on 2026-08-16 under lot 0.42.0: the "
    "same finding at 6.00 m, `walktest_navqa` PASS with every bot "
    "`targets_reached 1/1`. Both are `LOT_DESTINATION_ABOVE_FLOOR`, both have "
    "clean walkers, and NEITHER is a navmesh defect -- Lot leaves the marker "
    "where it was put because it cannot read what is under it offline, and "
    "Laser Tag then cannot path to it and reports TRAVERSAL at 0%. The gap is "
    "unchanged and unbuilt; what is new is that it now has a second instance "
    "and a second site, so it is a class rather than one odd map. "
    "`site_cover.pinches()` remains the template this item names. See item 52*"
)

# --- edit 2: item 52, before the closing sections ---------------------------
TAIL_ANCHOR = """WHAT NOT TO DO

Do not fix the tolerance. Do not skip the test. The assertion is correct and
the number it prints is the finding.

"""

ITEM52 = '''
*STATUS: CLOSED 2026-08-16 -- MEASURED on the mission it was overdue for. All stages EXECUTED rather than cache-hit, because `tool_version` is folded into the build fingerprint and the cached receipt said `Lot 0.33.0` -- so every earlier number for this mission came from nine minor versions back. Cover verified at five buildings with a real collision reading: `LOT_SIGHTLINE_OPEN` on NONE of three candidates, `unbreakable 0`, `pinches 0`. One change was tried and REJECTED on measurement, and the reason is the useful part of this item*

**52. `lot_demo_001` re-measured, and the route exposure it reports is the
design working rather than failing.**
Re-run 2026-08-16 under level_factory 0.40.0 and lot 0.42.0, the first numbers
on this mission since Lot 0.33.0. Its cached assemble receipt
(`fingerprint.last.json`) read `evaluated_utc 2026-08-13T23:20:57`,
`tool_version "Lot 0.33.0"` -- so the 45/100 and `route_completion_rate: 0.0`
this roadmap carries were produced nine minor versions back. The new artifacts
are stamped: `tool_version "Lot 0.42.0"`, `repository_commit df848df`.

`lot_assemble`, `walktest_navqa` and `laser_tag_evaluate` all EXECUTED on all
three candidates. That confirms item 39's claim that `tool_version` is folded
into the fingerprint, on a real mission -- a tool upgrade does invalidate a
workspace.

**WHAT THE COVER WORK DID AT FIVE BUILDINGS.** Item 51's fixes had only ever
been measured on `test_site_cover`'s two-building yard with no collision
reading. On the real mission, with 959 colliders and 1,029 surfaces:

```
LOT_SIGHTLINE_OPEN   fired on NONE of the three candidates
seed_5219 cover_plan  placed 16 (5 opening + 11 route)
                      route_open 14   unbreakable 0   pinches 0
```

The opening pass closed every marker sightline with FIVE of its twelve pieces.
Crew-first ordering holds at scale.

**AND LASER TAG ASKS FOR ENEMY-TO-ENEMY COVER BY NAME.** Item 51's entry left
"exclude enemy-to-enemy pairs from the opening budget" standing as a live
alternative, on the reasoning that such a line says nothing about who shoots
the crew. It is not an alternative. `LT_OPEN_SIGHTLINE` reports those lines
with coordinates and a remedy -- *"Enemy_2 and Enemy_5 see each other across
108.1 m of open ground, past the 45 m at which Laser Tag opens fire; fix: cover
near (19.0, 36.3) would break it"* -- three of them on seed_5219 alone.
Excluding those pairs would delete cover the grader requests. Retired.

**THE CHANGE THAT WAS TRIED AND REJECTED.** `route_open: 14` reads like a
defect. The opening pass had left SEVEN of its twelve unspent while the route
pass exhausted all eleven of its own, so the obvious move is to carry the
leftover down. It was written, and it worked on a constructed case -- route
pieces 4 -> 10, route_open 14 -> 2, opening untouched, pinches 0.

It is wrong, and `tests/test_lot.py::test_route_budget_scales_with_the_route_
and_is_reported_when_short` says so: it asserts the route budget is exactly
`ceil(route_length / ROUTE_METRES_PER_PIECE)`, and the carry made it 4 where
the test wants 1. **The test is right.** Its docstring -- *"A flat twelve is
generous on a 40 m approach and nothing on a 250 m one"* -- is arguing that the
allowance must be a scaled CAP, and `plan_cover`'s own comment says what the
cap is for: *"a producer that placed one per line would litter the street with
crates."* Carrying up to twelve flat pieces onto a deliberately scaled cap
pushes the route pass toward one-piece-per-open-line, which is the behaviour
the cap exists to prevent. The mitigation offered for it -- that extra pieces
only land on genuinely exposed lines -- is not a mitigation, it IS the failure
mode.

So the 14 is not a cover-budget defect. The route runs ~270 m past SIX enemies
each with a 45 m envelope; the exposed-stretch count is a function of enemy
density against route length. The cap stops Lot answering an enemy-density
problem by filling the street, and `LOT_ROUTE_EXPOSED` reports the remainder
honestly, which is exactly what the second half of that test demands.

WHAT NOT TO DO

Do not raise the route budget to make `route_open` smaller. Do not carry the
opening's leftover. Both were tried on 2026-08-16 and the suite refused them
for a stated reason. If route exposure is to come down, the lever is enemy
placement -- which is leaving this pipeline for the gameplay layer -- or a
different notion of what the route pass is for, not more pieces.

**WHAT IS ADVISORY HERE AND WHAT IS NOT.** Lot makes the level; Laser Tag
grades it. Its numbers are recorded because they are evidence, not because they
are gates: seed_5017 FAIL 40 over 25 runs with 4% traversal, seed_5118 0% and
the route never completed, seed_5219 16%, overexposure 45-69%, player-stuck
861 / 3,663 / 718. `LT_ROUTE_NEVER_COMPLETED` names its own instrument --
*"walktest_navqa walks the same spine on the baked navmesh with no combat in
it, and says which leg failed. Read that first."* It was read: **PASS**, every
bot `targets_reached 1/1` on all four legs. The map is walkable. Laser Tag's
own text attributes the failure to the crew halting on contact, which is
downstream's model of combat and out of scope under this file's boundary.

The one Lot-side finding in that set is `LT_DESTINATION_ABOVE_FLOOR` on
seed_5219 -- an objective marker 6.00 m above the ground plane -- and that is
item 9's residual gap, second instance. Not new, and not a navmesh defect.

'''

EDITS = [
    ("item 9: add its own status line", ITEM9_ANCHOR,
     ITEM9_STATUS + "\n\n" + ITEM9_ANCHOR),
    ("item 52: the lot_demo_001 re-measurement", TAIL_ANCHOR,
     TAIL_ANCHOR + ITEM52),
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
    print(f"    bytes  : {len(raw)}   (no expected value carried)")
    print(f"    sha256 : {_sha(raw)}")
    print(f"    endings: {crlf} CRLF, {lone} lone LF")


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
    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
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
    print(f"  reverted: {len(before)} -> {len(after)} B, sha256 {_sha(after)}")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    raw, eol, text = _load()
    ok(eol == "\n", "the roadmap is LF (it is, since f2713e9 and the "
                    "roadmap_status fix)")
    for name, old, _new in EDITS:
        ok(text.count(_n(old)) == 1, f"anchor present exactly once: {name}")

    # Item 9 must NOT already have a status line above it, or this adds a
    # second and `roadmap_status.py` reads whichever it finds first. This is
    # the mistake the item-3 patch made on its first draft.
    i = text.index(ITEM9_ANCHOR)
    above = text[:i].rstrip("\n").split("\n")[-1]
    ok(not above.startswith("*STATUS:"),
       f"item 9 has no status line above it yet (line above is {above[:44]!r})")
    # ...and the NARROWED line inside its block belongs to item 10.
    nine = text[i:text.index("**10. ", i)]
    ok("*STATUS: NARROWED 2026-08-14" in nine,
       "item 10's status line sits at the end of item 9's block, as expected")

    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)
    ok(out != text, "the edits change the file")

    # -- item 9 -----------------------------------------------------------
    j = out.index(ITEM9_ANCHOR)
    above2 = out[:j].rstrip("\n").split("\n")[-1]
    ok(above2.startswith("*STATUS: NARROWED 2026-08-16"),
       "item 9's new status sits directly above its heading")
    ok(above2.endswith("*"), "it is italic-delimited")
    ok(above2.split()[1] in ("OPEN", "CLOSED", "RETRACTED", "NARROWED",
                             "SUPERSEDED", "ANALYSIS"),
       f"verb in vocabulary ({above2.split()[1]})")
    nine2 = out[j:out.index("**10. ", j)]
    ok("*STATUS: NARROWED 2026-08-14" in nine2,
       "item 10's status line is UNTOUCHED by adding item 9's")
    # UNCHANGED, not ==1: four items carry a `NARROWED 2026-08-14` status
    # (9's neighbour 10, plus 42, 46 and 47). Asserting uniqueness of a shared
    # date stamp was wrong about the document, not about the edit -- the same
    # shape of error as every other count in this session that was written
    # before it was measured.
    probe = "*STATUS: NARROWED 2026-08-14"
    ok(out.count(probe) == text.count(probe) == 4,
       f"the four 2026-08-14 NARROWED lines are untouched "
       f"({text.count(probe)} -> {out.count(probe)})")

    # -- item 52 ----------------------------------------------------------
    ok(out.count("**52. `lot_demo_001` re-measured") == 1, "one item 52")
    ok(out.index("**51.") < out.index("**52."), "52 follows 51")
    ok(out.index("**52.") < out.index("### Not to be worked on"),
       "52 sits before the closing sections")
    fifty2 = out[out.index("*STATUS: CLOSED 2026-08-16 -- MEASURED on the "
                           "mission"):out.index("**52.")]
    ok(fifty2.strip().endswith("*"), "item 52's status line is closed with *")
    ok(fifty2.strip().count("*STATUS:") == 1, "and is a single status line")

    # -- the measured numbers must be the ones that were measured ---------
    for v in ("Lot 0.33.0", "Lot 0.42.0", "df848df", "placed 16",
              "route_open 14", "unbreakable 0", "pinches 0", "108.1 m",
              "3.60 m", "6.00 m", "861 / 3,663 / 718"):
        ok(v in out, f"records the measured value {v!r}")
    # The rejected change must be recorded as rejected, not as an option.
    ok("Do not carry the\nopening's leftover" in out,
       "the rejected change is recorded under WHAT NOT TO DO")
    ok("It is not an alternative" in out,
       "the enemy-to-enemy exclusion is retired, not left live")

    # -- prove a check can fail -------------------------------------------
    damaged = text.replace(ITEM9_ANCHOR, "**9. moved**", 1)
    ok(damaged.count(ITEM9_ANCHOR) == 0,
       "check() can fail: removing item 9's heading makes it uncountable")

    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
    lone = data.count(bytes([10])) - data.count(bytes([13, 10]))
    ok(data.count(bytes([13, 10])) == 0 and lone > 0,
       f"the written file stays LF ({lone} LF, 0 CRLF)")

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
