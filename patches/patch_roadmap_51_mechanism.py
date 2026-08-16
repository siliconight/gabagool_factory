#!/usr/bin/env python3
"""Roadmap 51: defect one closed, defect three's mechanism refuted and replaced.

Item 51 files defect three as "THE ONE THAT MATTERS MOST: the scene does not
carry the position the planner chose", in roadmap 48's family. Measured on
2026-08-16, that is not the mechanism. The scene carries its own plan exactly;
the TEST held a plan of a route the tool never uses.

This patch does two things to `PIPELINE_ROADMAP.md`:

1. Rewrites item 51's STATUS line -- defect one FIXED and re-measured, defect
   three's mechanism corrected, defect two still undiagnosed.
2. Inserts the corrected account ABOVE the original defect-three text, and
   marks the original as refuted while KEEPING it. Per the repo's own rule, a
   retracted finding is cheaper to keep than to rediscover -- and this one's
   two warnings (do not widen the bound, do not skip the test) were correct and
   are the reason the defect stayed findable at all.

The original text is not deleted, edited or reflowed. Only a heading marker and
a preceding block are added.

`PIPELINE_ROADMAP.md` is CRLF (4,391 CRLF, 0 lone LF at the read this was
written against) and `_eol` is keyed off the file, not off an anchor.

AFTER APPLYING, the derived status table must be regenerated:

    python tools\\roadmap_status.py --write
    python tools\\roadmap_status.py --check

USAGE

    python patches\\patch_roadmap_51_mechanism.py --check
    python patches\\patch_roadmap_51_mechanism.py --selftest
    python patches\\patch_roadmap_51_mechanism.py
    python patches\\patch_roadmap_51_mechanism.py --revert
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

TAG = "r51mech"

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "PIPELINE_ROADMAP.md"
SIDECAR = TARGET.with_name(TARGET.name + ".pre_" + TAG)

EXPECT_BYTES = 265566


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


# ---------------------------------------------------------------------------
STATUS_OLD = (
    "*STATUS: OPEN 2026-08-16 -- MEASURED. `lot` 0.41.0, clean tree (`git "
    "status --short` and `git stash list` both empty), so these predate "
    "tonight's level_factory work and are not caused by it: 328 passed, 8 "
    "FAILED in 4.26s. THREE defects, not eight: six tests are one arity bug "
    "at `site_spawns.py:470`, one is a cover assertion, one is a plan-versus-"
    "scene position disagreement of 18.5 m that is wearing a tolerance "
    "assertion's clothes*"
)

STATUS_NEW = (
    "*STATUS: NARROWED 2026-08-16 -- ONE OF THREE FIXED, ONE MECHANISM "
    "REFUTED, ONE STILL UNDIAGNOSED. Defect ONE (six stale callers) is FIXED "
    "and re-measured: `patch_lot_stale_spawn_callers.py` gives the four "
    "geometry assertions a one-point path at six call sites and derives the "
    "two read-backs' window from the route with `crew_reaction_path`, the way "
    "`place_enemies` does at `site_spawns.py:803` -- a read-back on `[spawn]` "
    "would ask an easier question than the search and pass exactly the maps "
    "the search had been too generous about. The predicate was NOT touched; "
    "its refusal to default `crew_path` worked as designed and only the "
    "follow-through was missing. Suite 328 passed / 8 failed -> 334 passed / "
    "2 failed. Defect THREE's MECHANISM IS REFUTED and rewritten below: it is "
    "not 48's family and the scene is not losing the plan. "
    "`_lasertag_hook_nodes` seats the hooks and clears the crew spawn before "
    "planning, and the test planned from the RAW route -- on BAIE_DORE, whose "
    "crew spawn is the dead centre of a 44 x 44 shell, `clear_crew_spawn` "
    "moves it 23.5 m and takes all six enemies with it. Planned from the same "
    "`pos` the scene was written from, 0 of 18 coordinate pairs fail at "
    "abs_tol=1e-3. Defect TWO (`test_site_cover.py`) is STILL UNDIAGNOSED; "
    "noted only that `open_span` returned exactly the full crew-to-enemy "
    "distance (51.94522232553231 on both sides of the assertion), and that "
    "the `LOT_ENEMY_SPAWN_STANDOFF` finding in the same run calls that enemy "
    "52.8 m from the crew where the test measures 51.945 -- two instruments, "
    "one distance, two answers, unresolved*"
)

INSERT_ANCHOR = (
    "**THREE, AND THE ONE THAT MATTERS MOST: the scene does not carry the "
    "position\nthe planner chose.**\n"
)

INSERT_NEW = """**THREE: the scene DOES carry the position the planner chose. The TEST was
holding a different plan. -- MECHANISM CORRECTED 2026-08-16, measured.**

`_lasertag_hook_nodes` does not plan against the positions it is handed. It
seats the nav hooks onto floor, clears the crew spawn off the wall it is
standing against, and spreads the enemies along the route THOSE TWO STEPS
produce (`lot.py:1242-1253`). The test planned from the raw dict instead:

```python
planned = site_spawns.place_enemies(BAIE_DORE, route()).positions
```

On `BAIE_DORE` the crew spawn (51.0, -5.0) is the dead centre of `b1`, a
44 x 44 shell at (51, -5). `clear_crew_spawn` moves it to (51.0, 18.5) --
23.5 m -- and `seat_destinations` drops the objective from z 0.9 to 0.0. The
route's first point moves, so every enemy spread along it moves too. All six
disagree, not only the pair the assertion reached first:

```
 i    planned x (test)   product x (scene)
 0           19.242160           37.734968     <- the assertion's pair
 1           64.683855           36.919915
 2           69.055220           48.119216
 3           73.426585           65.310451
 4           88.003898           82.593142
 5          107.547001           99.869736
```

`37.73496811511527` through `_v3`'s `{:g}` is `37.735`, the number in the
traceback. Recomputed from the same `pos` the scene was written from, **0 of
18 coordinate pairs fail at `abs_tol=1e-3`**. Nothing else was behind it.

So this is defect ONE's family, not 48's: a stale caller reproducing the
tool's pipeline with inputs the tool does not use. The ordering hypothesis
below is refuted directly -- reordering can only produce numbers that are IN
the planned set, and 37.735 is not any planned coordinate on any axis.

WHY IT DRIFTED, AND WHAT WAS DONE ABOUT IT. Because `_lasertag_hook_nodes`
returned only the scene body, the one question worth asking of it -- are the
positions in the scene the positions that were planned -- could be asked ONLY
by re-running its derivation by hand. The test's copy of that sequence went
stale, and a third preprocessing step would have desynced it again. The
derivation now lives in `_lasertag_hook_plan`, which returns the resolved
positions, route and enemies; `_lasertag_hook_nodes` calls it and writes the
same body (asserted byte-identical, not assumed). The test asks the tool which
plan it used. `patch_lot_hook_plan.py`.

Noted while reading and NOT a defect: `lot.py:1409-1414` seats and clears
`pos` and then hands it to `_lasertag_hook_nodes`, which does both again.
Measured idempotent on this site with `solids=None` -- the crew spawn moves
0.000000 m on the second application. Untested on sites with a collision
reading.

WHAT THE ORIGINAL READING GOT RIGHT. Both of its warnings were correct and are
why this stayed findable: widening the bound or skipping the test would have
buried a genuine input mismatch. What it got wrong was the mechanism, by
comparing two artefacts without first establishing they came from the same
build -- the failure `CLAUDE.md` rule 1 names. It is kept below in full,
because a retracted finding is cheaper to keep than to rediscover.

REFUTED 2026-08-16 -- the reading the block above replaces:

**THREE, AND THE ONE THAT MATTERS MOST: the scene does not carry the position
the planner chose.**
"""


EDITS = [
    ("item 51 STATUS line", STATUS_OLD, STATUS_NEW),
    ("defect three: corrected account above the refuted one",
     INSERT_ANCHOR, INSERT_NEW),
]


def _load():
    if not TARGET.exists():
        raise SystemExit(f"REFUSING: {TARGET} does not exist.")
    raw = TARGET.read_bytes()
    return raw, _eol(raw), _n(raw.decode("utf-8"))


def _identity(raw: bytes):
    mark = "" if len(raw) == EXPECT_BYTES else "   <-- not the size this was read against"
    print(f"  {TARGET.name}")
    print(f"    bytes  : {len(raw)}   (expected {EXPECT_BYTES}){mark}")
    print(f"    sha256 : {_sha(raw)}")
    crlf = raw.count(b"\r\n")
    lone = raw.count(b"\n") - crlf
    print(f"    eol    : {'CRLF' if crlf and not lone else 'LF' if lone and not crlf else 'MIXED'} "
          f"({crlf} CRLF, {lone} lone LF)")


def check() -> int:
    raw, _eol_, text = _load()
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
    ok(len(raw) == EXPECT_BYTES, f"target is {EXPECT_BYTES} bytes (got {len(raw)})")
    ok(eol == "\r\n", "the roadmap reads as CRLF")
    ok(raw.count(b"\n") - raw.count(b"\r\n") == 0,
       "the roadmap has no lone LF before the edit")

    for name, old, _new in EDITS:
        ok(text.count(_n(old)) == 1, f"anchor present exactly once: {name}")

    out = text
    for _name, old, new in EDITS:
        out = out.replace(_n(old), _n(new), 1)
    ok(out != text, "the edits change the file")

    # The original defect-three text is KEPT, not replaced.
    ok(out.count("**THREE, AND THE ONE THAT MATTERS MOST: the scene does not "
                 "carry the position\nthe planner chose.**") == 1,
       "the original heading survives exactly once (kept, not deleted)")
    ok("THAT IS ROADMAP 48's FAMILY, ONE TOOL DOWN." in out,
       "the refuted body is kept verbatim")
    ok("Do not fix the tolerance. Do not skip the test." in out,
       "the original's WHAT NOT TO DO is kept")
    ok(out.count("REFUTED 2026-08-16 -- the reading the block above replaces:") == 1,
       "the refutation marker is added exactly once")
    ok(out.index("MECHANISM CORRECTED 2026-08-16")
       < out.index("THAT IS ROADMAP 48's FAMILY"),
       "the correction sits ABOVE the reading it replaces")

    # STATUS vocabulary is a closed set; a verb outside it is not derivable.
    verbs = ("OPEN", "CLOSED", "RETRACTED", "NARROWED", "SUPERSEDED", "ANALYSIS")
    line = next(l for l in out.split("\n") if l.startswith("*STATUS:")
                and "ONE OF THREE FIXED" in l)
    ok(line.split()[1] in verbs, f"STATUS verb is in the vocabulary ({line.split()[1]})")
    ok(line.endswith("*"), "the STATUS line is still italic-delimited")
    ok("OPEN 2026-08-16 -- MEASURED. `lot` 0.41.0" not in out,
       "the superseded STATUS line is gone")

    # Prove the anchor checks can fail.
    damaged = text.replace(_n(STATUS_OLD), "*STATUS: MOVED*", 1)
    ok(damaged.count(_n(STATUS_OLD)) == 0,
       "check() can fail: removing the STATUS anchor makes it uncountable")

    # Line endings survive the round trip -- this is the one that has actually
    # gone wrong in this repo, writing 81 bare LF into a CRLF document.
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
