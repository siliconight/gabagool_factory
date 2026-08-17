#!/usr/bin/env python3
"""lot 0.43.0, certified as factory 1.27.0.

`lot.py` changed after `v0.42.0` was tagged and pushed: `place_enemies` now runs
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

    python patches\\patch_r53_release.py --check
    python patches\\patch_r53_release.py --selftest
    python patches\\patch_r53_release.py
    python patches\\patch_r53_release.py --revert
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

TAG = "r53release"

ROOT = Path(__file__).resolve().parent.parent
VERSION = ROOT / "lot" / "VERSION"
LOT_CL = ROOT / "lot" / "CHANGELOG.md"
MANIFEST = ROOT / "factory.manifest.json"
FAC_CL = ROOT / "CHANGELOG.md"
FILES = (VERSION, LOT_CL, MANIFEST, FAC_CL)

OLD_VERSION = b"Lot 0.42.0"
NEW_VERSION = b"Lot 0.43.0"


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


LOT_CL_ANCHOR = ("## [0.42.0] - the cover was planned for a crew standing "
                 "somewhere else\n")

LOT_ENTRY = """## [0.43.0] - the enemies are placed once

Roadmap 3 -- "Lot places enemies twice, and nothing checks the two agree" --
asked for one of two things: place once and thread the result through, or
assert the two agree. Neither had been done. 0.42.0 made the two calls agree by
handing them identical inputs, which restored the "same inputs, same answer"
claim the item calls untested rather than removing it.

`place_enemies` now runs ONCE, in `assemble`, before the site report closes.
The result is handed down through `write_walk_scene` -> `_lasertag_hook_nodes`
-> `_lasertag_hook_plan`, which places only when `enemies=None` so the
standalone callers behave as they always have. There is no second call left to
drift, which is a stronger guarantee than an assertion that a drift occurred.

The ordering constraint that justified the second placement is intact.
`lot.py`'s own comment says the walk scene is written after the report closes,
and a placement Lot could not honour has to travel with the site rather than
sit in a `.tscn` nobody diffs. The placement still happens in `assemble`. Only
the re-placement is gone.

### Verified on the artifact, not the fixture

A fixture licenses nothing about a mission. `lot_demo_001` was re-run under
this build and its three navqa scenes hashed against the pre-threading run:

    5017  e9177e9be4c3d78ad4634aad99517473e25c29fb95bd156f6c55d09023a8af23
    5118  25bdce90e97acfade19b9b0f5554df3b4c374ab56bc7d23daaa5bba831a644e7
    5219  b3bd2815f3f57a735014d0adde87237ba128339d468357485ee694b8b4f6f773

All three identical. `seed_5219`'s cover plan unchanged at `placed 16,
route_open 14, unbreakable 0, pinches 0`, and `laser_tag_evaluate` cache-hit on
all three candidates -- the correct answer when the inputs did not move.

Suite: 336 passed / 0 failed.

### What this did not change, which is worth recording

`walktest_navqa` re-executed on all three candidates despite byte-identical
input, while `laser_tag_evaluate` cached. Same unchanged upstream, two
different answers. Wasted work rather than wrong output, and another face of
roadmap 39's `upstream_artifact_hashes` -- a field in the build fingerprint
that nothing populates.

"""

FAC_CL_ANCHOR = "## [factory-v1.26.0] - 2026-08-16\n"

FAC_ENTRY = """## [factory-v1.27.0] - 2026-08-16

lot 0.42.0 -> 0.43.0. The other nine tools are unchanged from factory-v1.26.0.

WHY A SET VERSION FOR A BYTE-IDENTICAL ARTIFACT

Because a tool version and a set version are two different claims, and this
project learned that the expensive way earlier today. level_factory 0.40.0 was
tagged, pushed, and recorded in the roadmap as closing item 50 while
`factory.manifest.json` still pinned 0.39.0 -- so for the life of
factory-v1.25.0 the certified set omitted a fix the roadmap called closed.
Nobody noticed because nothing compares the two.

lot 0.43.0 emits the same bytes as 0.42.0 on every scene measured. It still
gets a set version, because the alternative is lot's HEAD sitting ahead of its
tag and ahead of the manifest, which is precisely the state that hid 0.40.0.

WHAT LOT 0.43.0 CHANGES

The enemies are placed once. `place_enemies` ran twice inside one `assemble` --
once for the site report, once for the scene writer -- and the two were kept in
agreement by hand. Roadmap 3 had described this since before this month and had
been re-confirmed on 2026-08-12. The result of the first placement is now
threaded down to the writer, so there is no second call to disagree.

Verified against the artifact rather than a fixture: all three `lot_demo_001`
navqa scenes byte-identical to the pre-threading run, cover plan unchanged,
`laser_tag_evaluate` correctly cache-hitting. `lot`'s suite 336 passed / 0
failed.

"""

MANIFEST_EDITS = [
    ('"lot": {\n      "version": "0.42.0",\n      "tag": "v0.42.0",',
     '"lot": {\n      "version": "0.43.0",\n      "tag": "v0.43.0",'),
    ('"factory_version": "1.26.0",', '"factory_version": "1.27.0",'),
    ("0.42.0 plans cover for the crew spawn the scene actually ships and "
     "serves the crew's sightlines before the rest of the map's.",
     "0.42.0 plans cover for the crew spawn the scene actually ships and "
     "serves the crew's sightlines before the rest of the map's. 0.43.0 places "
     "the enemies ONCE and threads the result to the scene writer instead of "
     "placing again -- roadmap 3, open since before 2026-08-12; the emitted "
     "scenes are byte-identical."),
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
        problems.append("lot/CHANGELOG.md does not open on the 0.42.0 heading")
    if "## [0.43.0]" in lot_cl:
        problems.append("lot/CHANGELOG.md already carries a 0.43.0 entry")
    for old, _new in MANIFEST_EDITS:
        if man.count(old) != 1:
            problems.append(f"manifest anchor found {man.count(old)}x: "
                            f"{old[:52]!r}")
    if fac_cl.count(FAC_CL_ANCHOR) != 1:
        problems.append(f"factory changelog anchor found "
                        f"{fac_cl.count(FAC_CL_ANCHOR)}x")
    if "## [factory-v1.27.0]" in fac_cl:
        problems.append("CHANGELOG.md already carries a factory-v1.27.0 entry")
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
    assert parsed["factory_version"] == "1.27.0"
    assert parsed["tools"]["lot"]["version"] == "0.43.0"

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
    print("    git -C lot commit -m \"0.43.0: the enemies are placed once\"")
    print("    git -C lot tag v0.43.0")
    print("    git add -A")
    print("    git commit -m \"factory-v1.27.0: certify lot 0.43.0\"")
    print("    git tag factory-v1.27.0")
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
    ok(parsed["factory_version"] == "1.27.0", "factory_version -> 1.27.0")
    ok(parsed["tools"]["lot"]["version"] == "0.43.0"
       and parsed["tools"]["lot"]["tag"] == "v0.43.0", "lot -> 0.43.0 / v0.43.0")
    moved = [k for k in before["tools"]
             if before["tools"][k]["version"] != parsed["tools"][k]["version"]]
    ok(moved == ["lot"], f"exactly one tool moves: {moved}")
    ok(len(parsed["tools"]) == len(before["tools"]) == 10, "no tool added or lost")
    ok(parsed["tools"]["lot"]["note"].endswith("byte-identical."),
       "lot's note is extended, not replaced")
    ok("roadmap 3" in parsed["tools"]["lot"]["note"],
       "and it names the item this discharges")

    # -- changelogs --------------------------------------------------------
    lot_out = LOT_ENTRY + lot_cl
    ok(lot_out.startswith("## [0.43.0]"), "lot entry lands at byte zero")
    ok(lot_out.count("## [0.43.0]") == 1 and lot_out.count("## [0.42.0]") == 1,
       "one 0.43.0 heading, 0.42.0 survives")
    import re
    heads = re.findall(r"^## \[([0-9.]+)\] - (.+)$", lot_out, flags=re.M)
    ok(heads[0][0] == "0.43.0" and heads[1][0] == "0.42.0",
       f"newest first: {heads[0][0]} then {heads[1][0]}")
    ok(not re.match(r"^\d{4}-\d{2}-\d{2}", heads[0][1]),
       "no date in lot's heading, matching the file's convention")

    fac_out = fac_cl.replace(FAC_CL_ANCHOR, FAC_ENTRY + FAC_CL_ANCHOR, 1)
    ok(fac_out.count("## [factory-v1.27.0]") == 1, "one 1.27.0 heading")
    ok(fac_out.index("factory-v1.27.0") < fac_out.index("factory-v1.26.0"),
       "newest first")
    ok(fac_out.startswith("# Factory Changelog"), "the title is not displaced")

    # -- the claims have to be the measured ones ---------------------------
    for val in ("e9177e9be4c3d78ad4634aad99517473e25c29fb95bd156f6c55d09023a8af23",
                "route_open 14", "336 passed"):
        ok(val in LOT_ENTRY, f"lot entry records {val[:24]!r}")
    ok("byte-identical" in FAC_ENTRY and "0.40.0" in FAC_ENTRY,
       "the factory entry says why a byte-identical change still gets a set "
       "version, citing the 0.40.0 gap")
    ok("walktest_navqa" in LOT_ENTRY,
       "the unexplained re-execution is carried, not dropped")

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
