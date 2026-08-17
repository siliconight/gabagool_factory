#!/usr/bin/env python3
"""Roadmap 3: CLOSED. The enemies are placed once and threaded through.

Item 3 asked for "place once, thread the result through, or assert the two
agree". `patch_lot_place_once.py` took the first: `place_enemies` runs ONCE, in
`assemble`, and the result is handed down through `write_walk_scene` ->
`_lasertag_hook_nodes` -> `_lasertag_hook_plan`. There is no second call left
to drift.

VERIFIED ON THE ARTIFACT, NOT THE FIXTURE. The selftest proved byte-identical
scene bodies on `BAIE_DORE`, which licenses nothing about a real mission. So
`lot_demo_001` was re-run and its three navqa scenes hashed against the
pre-threading run:

    5017  e9177e9be4c3d78ad4634aad99517473e25c29fb95bd156f6c55d09023a8af23
    5118  25bdce90e97acfade19b9b0f5554df3b4c374ab56bc7d23daaa5bba831a644e7
    5219  b3bd2815f3f57a735014d0adde87237ba128339d468357485ee694b8b4f6f773

All three identical, and seed_5219's cover_plan unchanged at `placed 16,
route_open 14, unbreakable 0, pinches 0`. `laser_tag_evaluate` cache-hit on all
three, which is the correct answer when the inputs did not move.

The anchor is the NARROWED status line written earlier today by
`patch_roadmap_03_narrowed.py`, so it was authored and verified in this
session. No byte count is carried: the roadmap has been rewritten eight times
today. The identity is printed and drift refuses.

USAGE

    python patches\\patch_roadmap_03_closed.py --check
    python patches\\patch_roadmap_03_closed.py --selftest
    python patches\\patch_roadmap_03_closed.py
    python patches\\patch_roadmap_03_closed.py --revert

AFTER APPLYING:

    python tools\\roadmap_status.py --write
    python tools\\roadmap_status.py --check
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r53item3closed"

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


OLD = (
    "*STATUS: NARROWED 2026-08-16 -- THE DIVERGENCE IS FIXED; THE REMEDY THIS "
    "ITEM ASKED FOR IS NOT. Measured during item 51, on the `test_site_cover` "
    "yard: the two calls returned different six-enemy sets inside one "
    "`assemble` -- the reporter gave (-16.000, 31.500) ... (-30.000, 64.500) "
    "and the writer gave (-8.332, 43.500) ... (-31.357, -13.000) -- and the "
    "cover plan was built from the first while the walk scene shipped the "
    "second, so every level's cover was planned against enemies it does not "
    "contain. `patch_lot_cover_ships_spawn.py` makes `assemble` clear the crew "
    "spawn before planning; `tools/probe_r51_cover_enemies.py` then reports "
    "`in_positions SAME, positions SAME` and the two sets identical. THE "
    "MECHANISM NAMED BELOW IS NOT THE ONE MEASURED: this item blames a second "
    "`seat_destinations` pass, and the entire 9.5 m difference was "
    "`clear_crew_spawn`, which `patch_lot_crew_spawn_clearance.py` added on "
    "2026-08-15 -- AFTER this item was written, so the item was right for its "
    "time and a second cause landed on top of it. The two call sites are "
    "`lot.py:1874` and `lot.py:1257` as measured; this item's `1337` and `975` "
    "are the same two sites before the file grew. STILL OPEN, and it is this "
    "item's actual prescription: the enemies are still placed TWICE and "
    "NOTHING ASSERTS the two agree -- they agree by determinism from identical "
    "inputs, which is precisely the \"same inputs, same answer\" claim this "
    "item calls untested, restored rather than removed. Either place once and "
    "thread the result through, or add the assertion. Item 51 recorded this "
    "gap in its own entry without recognising it as this item*"
)

NEW = (
    "*STATUS: CLOSED 2026-08-16 -- PLACED ONCE AND THREADED THROUGH, which is "
    "the first of the two remedies this item names. `place_enemies` now runs "
    "once, in `assemble`, before the site report closes; the result is handed "
    "down through `write_walk_scene` -> `_lasertag_hook_nodes` -> "
    "`_lasertag_hook_plan`, which places only when `enemies=None` so the "
    "standalone test callers are unaffected. The assertion this item offers as "
    "its alternative was deliberately NOT taken: an assertion detects a "
    "disagreement after the fact, and there is now no second call to disagree. "
    "`patch_lot_place_once.py`. THE ORDERING CONSTRAINT THAT JUSTIFIED THE "
    "SECOND CALL IS INTACT -- `lot.py`'s comment says the walk scene is written "
    "after the report closes and a placement Lot could not honour has to travel "
    "with the site rather than sit in a .tscn nobody diffs; the placement still "
    "happens in `assemble`, and only the RE-placement is gone. VERIFIED ON THE "
    "ARTIFACT: the selftest proves byte-identical scene bodies on `BAIE_DORE` "
    "and counts place_enemies calls (1 standalone, 0 when threaded), but a "
    "fixture licenses nothing about a mission, so `lot_demo_001` was re-run and "
    "all three navqa scenes hashed identical to the pre-threading run -- "
    "e9177e9b (5017), 25bdce90 (5118), b3bd2815 (5219) -- with seed_5219's "
    "cover_plan unchanged at placed 16 / route_open 14 / unbreakable 0 / "
    "pinches 0, and `laser_tag_evaluate` correctly cache-hitting on all three. "
    "WHAT THIS ITEM'S HISTORY IS WORTH KEEPING FOR: it was OPEN with an "
    "explicit status line re-confirmed on 2026-08-12, it named both call sites, "
    "and an item-51 investigation on 2026-08-16 re-derived its entire content "
    "as a new finding without searching for it. The roadmap already knew. "
    "NOTED, NOT FIXED: `walktest_navqa` re-executed on all three candidates "
    "despite byte-identical input while `laser_tag_evaluate` cached -- same "
    "unchanged upstream, two different answers. Wasted work rather than wrong "
    "output, and another face of item 39's unpopulated "
    "`upstream_artifact_hashes`*"
)

EDITS = [("item 3: NARROWED -> CLOSED", OLD, NEW)]


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
    n = text.count(_n(OLD))
    print(f"  [{'ok' if n == 1 else 'MISSING'}]  item 3's NARROWED status "
          f"(found {n})")
    print()
    print("APPLICABLE." if n == 1
          else "NOT APPLICABLE: refusing rather than fuzzy-matching.")
    return 0 if n == 1 else 1


def apply() -> int:
    raw, eol, text = _load()
    _identity(raw)
    if text.count(_n(OLD)) != 1:
        raise SystemExit("REFUSING: item 3's NARROWED status is not present "
                         "exactly once. Nothing written.")
    if SIDECAR.exists():
        raise SystemExit(f"REFUSING: {SIDECAR.name} exists. Use --revert.")
    shutil.copy2(TARGET, SIDECAR)
    out = text.replace(_n(OLD), _n(NEW), 1)
    data = out.replace("\n", eol).encode("utf-8") if eol != "\n" else out.encode("utf-8")
    TARGET.write_bytes(data)
    print()
    print(f"  {len(raw)} -> {len(data)} B  ({len(data) - len(raw):+d})")
    print(f"  sha256 {_sha(data)}")
    print(f"  endings: {data.count(bytes([13, 10]))} CRLF, "
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
    ok(eol == "\n", "the roadmap is LF")
    ok(text.count(_n(OLD)) == 1, "item 3's NARROWED status is present once")

    # It must be item 3's, not some other item's -- verified by position.
    i = text.index(_n(OLD))
    after_it = text[i + len(_n(OLD)):].lstrip("\n")
    ok(after_it.startswith("**3. Lot places enemies twice"),
       f"and it sits directly above item 3 (next is {after_it[:40]!r})")

    out = text.replace(_n(OLD), _n(NEW), 1)
    ok(out != text, "the edit changes the file")

    j = out.index(_n(NEW))
    ok(out[j + len(_n(NEW)):].lstrip("\n").startswith("**3. Lot places enemies"),
       "the new status is still directly above item 3")
    ok(_n(NEW).startswith("*STATUS: CLOSED 2026-08-16"), "verb is CLOSED")
    ok(_n(NEW).endswith("*"), "italic-delimited")
    ok(_n(NEW).count("*STATUS:") == 1, "one status line, not two")
    ok("\n" not in _n(NEW), "it is a single line, as the format requires")
    ok(out.count("*STATUS:") == text.count("*STATUS:"),
       f"the number of status lines is unchanged "
       f"({text.count('*STATUS:')}) -- replaced, not added")

    # Item 3's own body must survive untouched.
    ok("**3. Lot places enemies twice, and nothing checks the two agree.**"
       in out, "item 3's heading survives")
    # Whitespace-normalised: the prescription wraps as "...through, or\nassert
    # the two agree." A naive search says item 3 lost its own sentence. Third
    # time this trap has fired today; each time the check caught it and each
    # time I wrote the naive form first.
    flat_out = " ".join(out.split())
    ok("Place once, thread the result through, or assert the two agree."
       in flat_out,
       "and its prescription, which this discharges, is still readable")
    ok("Place once, thread the result through, or assert the two agree."
       not in out,
       "...and it really does wrap, so the naive form would have been wrong")

    # The claims in the status have to be the measured ones.
    for v in ("e9177e9b", "25bdce90", "b3bd2815", "placed 16",
              "route_open 14", "unbreakable 0", "pinches 0",
              "patch_lot_place_once.py"):
        ok(v in _n(NEW), f"records the measured value {v!r}")
    ok("re-derived its entire content as a new finding without searching"
       in _n(NEW),
       "the process failure is recorded, not quietly dropped")
    ok("NOTED, NOT FIXED" in _n(NEW),
       "the walktest re-execution is carried rather than buried")

    damaged = text.replace(_n(OLD), "*STATUS: MOVED*", 1)
    ok(damaged.count(_n(OLD)) == 0,
       "check() can fail: removing the anchor makes it uncountable")

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
