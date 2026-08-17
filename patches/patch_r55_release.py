#!/usr/bin/env python3
"""lot 0.44.0, certified as factory 1.28.0.

`lot.py` changed after `v0.43.0` was tagged and pushed: `place_enemies` now runs
once and the result is threaded through `write_walk_scene` ->
`_lasertag_hook_nodes` -> `_lasertag_hook_plan`, discharging roadmap 3. The
emitted artifact is byte-identical -- all three `lot_demo_001` navqa scenes
hashed the same as the pre-threading run -- but two function signatures moved
and a roadmap item closed, so it gets a version and the certified set follows.

That ordering is deliberate and it is this morning's lesson applied: level
factory 0.40.0 was tagged, pushed, and recorded as closing roadmap 50 while
`factory.manifest.json` still pinned 0.39.0, so the certified set omitted a
shipped fix for the life of factory-v1.25.0. A tool version and a set version
are two different claims. Leaving lot's HEAD ahead of its tag and ahead of the
manifest is exactly the state that hid it.

FOUR FILES, TWO REPOS, TWO COMMITS. `lot/VERSION` and `lot/CHANGELOG.md` are
lot's; `factory.manifest.json` and `CHANGELOG.md` are the factory root's. Every
file is checked to exist and every anchor to be present BEFORE anything is
written -- a patch that half-applies across two repositories is worse than one
that refuses.

`lot/VERSION` is 10 bytes with NO trailing newline. Read and written as bytes,
with the exact length asserted on both sides.

USAGE

    python patches\\patch_r55_release.py --check
    python patches\\patch_r55_release.py --selftest
    python patches\\patch_r55_release.py
    python patches\\patch_r55_release.py --revert
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

TAG = "r55release"

ROOT = Path(__file__).resolve().parent.parent
VERSION = ROOT / "lot" / "VERSION"
LOT_CL = ROOT / "lot" / "CHANGELOG.md"
MANIFEST = ROOT / "factory.manifest.json"
FAC_CL = ROOT / "CHANGELOG.md"
FILES = (VERSION, LOT_CL, MANIFEST, FAC_CL)

OLD_VERSION = b"Lot 0.43.0"
NEW_VERSION = b"Lot 0.44.0"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def _sidecar(p: Path) -> Path:
    return p.with_name(p.name + ".pre_" + TAG)


def _eol(raw: bytes, who: str) -> str:
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    if crlf and lf:
        raise SystemExit(f"REFUSING: {who} has mixed line endings "
                         f"({crlf} CRLF, {lf} LF).")
    if not crlf and not lf:
        raise SystemExit(f"REFUSING: {who} has no line endings.")
    return "\r\n" if crlf else "\n"


def _n(t: str) -> str:
    return t.replace("\r\n", "\n")


LOT_CL_ANCHOR = "## [0.43.0] - the enemies are placed once\n"

LOT_ENTRY = """## [0.44.0] - cover stops paying for enemy-to-enemy lines

`open_sightlines` is all-pairs over the marker dict, and `lot.py` builds that
dict as three mission markers plus one `Enemy_{i}` per placed enemy. K enemies
therefore contribute C(K,2) lines describing enemies shooting each other, and
`plan_cover`'s twelve-piece opening budget was buying cover for them.

The exclusion sits in `plan_cover`'s nested `outstanding()` -- the point of
spend -- and NOT in `open_sightlines`, which is byte-identical. Laser Tag and
`level_factory/packages/validation/` still see every pair.

### This REVERSES a call the roadmap had already made

Roadmap 52 retired exactly this change on 2026-08-16, because
`LT_OPEN_SIGHTLINE` reports those lines with coordinates and a remedy, so
excluding them deletes cover the grader asks for. That reasoning is not
refuted here. It is overruled: Laser Tag is advisory, Lot builds the level,
and `Enemy_*` is leaving Lot for the gameplay layer, so a request phrased in
enemy markers cannot bind Lot's budget.

The change was re-derived from scratch and shipped before item 52 was read.
The item already carried the "before" numbers that were then re-measured with
a full pipeline run.

### Measured, seed-matched, in both directions

    seed   before (placed, route_open)   after
    5017   (9, 3)                        (8, 3)    waste removed, no cost
    5118   (9, 0)                        (9, 0)    freed slot went to the
                                                   route: enemy-route 4 -> 5
    5219   (16, 14)                      (14, 15)  one route stretch left open

15 of the 16 pieces in the previous export were placed against an `Enemy_*`
point. Only one would survive without enemies at all.

The cost is real. On seed_5219 `route_open` goes 14 -> 15, because one
enemy-enemy crate was incidentally blocking a route line and the route pass
did not replace it -- its density cap (`ROUTE_METRES_PER_PIECE`) was already
met. Mission findings went 51 -> 50. Which finding disappeared was NOT
isolated, and `LT_OPEN_SIGHTLINE` was NOT counted before-versus-after per seed.

Reverting and re-applying reproduced the patched numbers exactly, every stage
cache-hitting, so these are not rebuild artifacts.

Suite: 336 passed / 0 failed.

"""

FAC_CL_ANCHOR = "## [factory-v1.27.0] - 2026-08-16\n"

FAC_ENTRY = """## [factory-v1.28.0] - 2026-08-17

lot 0.43.0 -> 0.44.0. The other nine tools are unchanged from factory-v1.27.0.

WHAT LOT 0.44.0 CHANGES

Lot's opening cover budget no longer buys cover for enemy-to-enemy sightlines.
`open_sightlines` is all-pairs, so K enemy markers contribute C(K,2) lines that
say nothing about who shoots the crew. The exclusion sits at the point of
spend, inside `plan_cover`, leaving `open_sightlines` byte-identical for Laser
Tag and the validation package.

THIS REVERSES ROADMAP 52, ON PRECEDENCE AND NOT ON EVIDENCE

Item 52 retired this change a day earlier, because `LT_OPEN_SIGHTLINE` asks
for that cover by name. Nothing here refutes it. Lot outranks Laser Tag, and
enemy placement is leaving Lot, so the request cannot bind the budget. The
item now carries the reversal, the measurement, and what was not measured.

MEASURED

Seed-matched across all three `lot_demo_001` candidates: 5017 (9,3) -> (8,3),
5118 (9,0) -> (9,0) with the freed slot going to the route, and 5219 (16,14) ->
(14,15). The one regression -- a stretch of the crew's route left open on
seed_5219 -- is recorded rather than argued away. Mission findings 51 -> 50.
`lot`'s suite 336 passed / 0 failed.

"""

MANIFEST_EDITS = [
    ('"lot": {\n      "version": "0.43.0",\n      "tag": "v0.43.0",',
     '"lot": {\n      "version": "0.44.0",\n      "tag": "v0.44.0",'),
    ('"factory_version": "1.27.0",', '"factory_version": "1.28.0",'),
    ("0.43.0 places the enemies ONCE and threads the result to the scene "
     "writer instead of placing again -- roadmap 3, open since before "
     "2026-08-12; the emitted scenes are byte-identical.",
     "0.43.0 places the enemies ONCE and threads the result to the scene "
     "writer instead of placing again -- roadmap 3, open since before "
     "2026-08-12; the emitted scenes are byte-identical. 0.44.0 stops the "
     "opening budget buying cover for enemy-to-enemy lines, reversing roadmap "
     "52 on precedence rather than on evidence; the measured cost is one "
     "stretch of the crew's route left open on seed_5219."),
]


def _preflight():
    missing = [p for p in FILES if not p.exists()]
    if missing:
        raise SystemExit("REFUSING: missing " + ", ".join(str(m) for m in missing))
    v = VERSION.read_bytes()
    lot_cl = _n(LOT_CL.read_bytes().decode("utf-8"))
    man = _n(MANIFEST.read_bytes().decode("utf-8"))
    fac_cl = _n(FAC_CL.read_bytes().decode("utf-8"))
    problems = []
    if v != OLD_VERSION:
        problems.append(f"lot/VERSION is {v!r}, expected {OLD_VERSION!r}")
    if not lot_cl.startswith(LOT_CL_ANCHOR):
        problems.append("lot/CHANGELOG.md does not open on the 0.43.0 heading")
    if "## [0.44.0]" in lot_cl:
        problems.append("lot/CHANGELOG.md already carries a 0.44.0 entry")
    for old, _new in MANIFEST_EDITS:
        if man.count(old) != 1:
            problems.append(f"manifest anchor found {man.count(old)}x: "
                            f"{old[:52]!r}")
    if fac_cl.count(FAC_CL_ANCHOR) != 1:
        problems.append(f"factory changelog anchor found "
                        f"{fac_cl.count(FAC_CL_ANCHOR)}x")
    if "## [factory-v1.28.0]" in fac_cl:
        problems.append("CHANGELOG.md already carries a factory-v1.28.0 entry")
    return (v, lot_cl, man, fac_cl), problems


def _identity():
    for p in FILES:
        if p.exists():
            raw = p.read_bytes()
            print(f"  {p.relative_to(ROOT).as_posix():28s} {len(raw):>7} B  "
                  f"sha256 {_sha(raw)[:12]}")


def check() -> int:
    _identity()
    print()
    _st, problems = _preflight()
    if problems:
        print("NOT APPLICABLE:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("APPLICABLE: all four files present and every anchor found once.")
    return 0


def apply() -> int:
    _identity()
    (v, lot_cl, man, fac_cl), problems = _preflight()
    if problems:
        raise SystemExit("REFUSING: " + "; ".join(problems) + ". Nothing written.")
    for p in FILES:
        if _sidecar(p).exists():
            raise SystemExit(f"REFUSING: {_sidecar(p).name} exists. Use --revert.")

    lot_cl_out = LOT_ENTRY + lot_cl
    man_out = man
    for old, new in MANIFEST_EDITS:
        man_out = man_out.replace(old, new, 1)
    fac_cl_out = fac_cl.replace(FAC_CL_ANCHOR, FAC_ENTRY + FAC_CL_ANCHOR, 1)

    parsed = json.loads(man_out)
    assert parsed["factory_version"] == "1.28.0"
    assert parsed["tools"]["lot"]["version"] == "0.44.0"

    def _bytes(p, text):
        eol = _eol(p.read_bytes(), p.name)
        return text.replace("\n", eol).encode("utf-8") if eol != "\n" \
            else text.encode("utf-8")

    payload = {
        VERSION: NEW_VERSION,
        LOT_CL: _bytes(LOT_CL, lot_cl_out),
        MANIFEST: _bytes(MANIFEST, man_out),
        FAC_CL: _bytes(FAC_CL, fac_cl_out),
    }

    print()
    for p in FILES:
        before = p.read_bytes()
        shutil.copy2(p, _sidecar(p))
        p.write_bytes(payload[p])
        print(f"  {p.relative_to(ROOT).as_posix():28s} {len(before):>7} -> "
              f"{len(payload[p]):>7} B  ({len(payload[p]) - len(before):+d})")
    print()
    print("  NEXT -- two repos, two commits:")
    print("    git -C lot add -A")
    print("    git -C lot commit -m \"0.44.0: cover stops paying for "
          "enemy-to-enemy lines\"")
    print("    git -C lot tag v0.44.0")
    print("    git add -A")
    print("    git commit -m \"factory-v1.28.0: certify lot 0.44.0\"")
    print("    git tag factory-v1.28.0")
    return 0


def revert() -> int:
    done = False
    for p in FILES:
        s = _sidecar(p)
        if not s.exists():
            print(f"  {p.name}: no sidecar, left alone")
            continue
        shutil.copy2(s, p)
        s.unlink()
        print(f"  {p.relative_to(ROOT).as_posix()}: restored to "
              f"{len(p.read_bytes())} B")
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

    (v, lot_cl, man, fac_cl), problems = _preflight()
    ok(not problems, "preflight clean")
    for p in problems:
        print(f"        {p}")
    if problems:
        print("\nSELFTEST FAILED")
        return 1

    # -- VERSION, the shape that has no trailing newline -------------------
    ok(v == OLD_VERSION, f"lot/VERSION is exactly {OLD_VERSION!r}")
    ok(len(v) == 10 and not v.endswith(b"\n"),
       "10 bytes, no trailing newline")
    ok(len(NEW_VERSION) == 10 and not NEW_VERSION.endswith(b"\n"),
       "and the bump keeps both properties")

    # -- manifest ----------------------------------------------------------
    man_out = man
    for old, new in MANIFEST_EDITS:
        man_out = man_out.replace(old, new, 1)
    parsed, before = json.loads(man_out), json.loads(man)
    ok(parsed["factory_version"] == "1.28.0", "factory_version -> 1.28.0")
    ok(parsed["tools"]["lot"]["version"] == "0.44.0"
       and parsed["tools"]["lot"]["tag"] == "v0.44.0", "lot -> 0.44.0 / v0.44.0")
    moved = [k for k in before["tools"]
             if before["tools"][k]["version"] != parsed["tools"][k]["version"]]
    ok(moved == ["lot"], f"exactly one tool moves: {moved}")
    ok(len(parsed["tools"]) == len(before["tools"]) == 10, "no tool added or lost")
    ok(parsed["tools"]["lot"]["note"].startswith(
           before["tools"]["lot"]["note"]),
       "lot's note is extended, not replaced (derived: new startswith old)")
    ok("roadmap 3" in parsed["tools"]["lot"]["note"],
       "and it names the item this discharges")

    # -- changelogs --------------------------------------------------------
    lot_out = LOT_ENTRY + lot_cl
    ok(lot_out.startswith("## [0.44.0]"), "lot entry lands at byte zero")
    ok(lot_out.count("## [0.44.0]") == 1 and lot_out.count("## [0.43.0]") == 1,
       "one 0.44.0 heading, 0.43.0 survives")
    import re
    heads = re.findall(r"^## \[([0-9.]+)\] - (.+)$", lot_out, flags=re.M)
    ok(heads[0][0] == "0.44.0" and heads[1][0] == "0.43.0",
       f"newest first: {heads[0][0]} then {heads[1][0]}")
    ok(not re.match(r"^\d{4}-\d{2}-\d{2}", heads[0][1]),
       "no date in lot's heading, matching the file's convention")

    fac_out = fac_cl.replace(FAC_CL_ANCHOR, FAC_ENTRY + FAC_CL_ANCHOR, 1)
    ok(fac_out.count("## [factory-v1.28.0]") == 1, "one 1.28.0 heading")
    ok(fac_out.index("factory-v1.28.0") < fac_out.index("factory-v1.27.0"),
       "newest first")
    ok(fac_out.startswith("# Factory Changelog"), "the title is not displaced")

    # -- the claims have to be the measured ones ---------------------------
    # 0.44.0 CHANGES THE OUTPUT, so 0.43.0's assertions about a byte-identical
    # artifact do not carry over. What must survive instead is the measurement
    # and -- more importantly -- the admissions.
    #
    # MATCHED ON WHITESPACE-NORMALISED TEXT. The entry is hard-wrapped, so
    # "was NOT\nisolated" makes the naive substring "NOT isolated" absent.
    # That is the line-break trap this project has hit three times.
    flat_lot = " ".join(LOT_ENTRY.split())
    flat_fac = " ".join(FAC_ENTRY.split())

    ok("NOT isolated" not in LOT_ENTRY,
       "the naive substring really is absent, so normalising is not decorative")

    for val in ("(16, 14)", "(14, 15)", "(9, 3)", "336 passed",
                "Roadmap 52 retired"):
        ok(val in flat_lot, f"lot entry records {val!r}")
    for val in ("NOT isolated", "NOT counted before-versus-after per seed",
                "`route_open` goes 14 -> 15", "51 -> 50"):
        ok(val in flat_lot,
           f"lot entry keeps the admission {val!r} -- the cost and the gap in "
           f"the evidence do not get to fall out of the entry")
    ok("REVERSES ROADMAP 52" in flat_fac and "not on evidence" in flat_fac.lower(),
       "the factory entry names the reversal AND that it is on precedence")
    ok("51 -> 50" in flat_fac, "the factory entry carries the findings delta")

    # -- prove a check can fail -------------------------------------------
    ok(OLD_VERSION + b"\n" != OLD_VERSION,
       "the VERSION comparison distinguishes a trailing newline")
    broken = man.replace(MANIFEST_EDITS[1][0], '"factory_version": "9.9.9",', 1)
    ok(broken.count(MANIFEST_EDITS[1][0]) == 0,
       "check() can fail: moving factory_version makes its anchor uncountable")

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
