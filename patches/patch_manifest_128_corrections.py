#!/usr/bin/env python3
"""factory.manifest.json: three claims in the certification record are false.

The manifest is the document that gets trusted hardest, because its whole
premise is `these tool versions were verified TOGETHER`. Its PINS are current.
Its PROSE is three releases stale, and stale prose in a certification record
does not read as old -- it reads as current.

1. It says lot's own unit suite is RED on a clean tree, 328 passed / 8 FAILED,
   and lists the three defects. MEASURED 2026-08-18 on a clean tree at Lot
   0.44.0 (git 0028666, 0 dirty): 336 passed, 0 failed. All three were fixed,
   across Lot 0.42.0 / 0.43.0 / 0.44.0. The manifest already PINS lot 0.44.0
   -- so the file contradicts itself, pin against prose.

2. It lists roadmap 50 as KNOWN OPEN inside a package this set produces. It
   was fixed in level_factory 0.40.0, which is the version this set pins.

3. It says the closure scan's `ok: true` is not yet evidence that the art
   resolves, because whether it reads the scene's `res://` references is
   UNMEASURED. It is measured: `closure.py` globs every file under the
   mission root and does not walk a reference graph at all.

WHAT THIS PATCH DOES NOT DO: bump `factory_version`. Correcting prose is not
re-certifying, no pipeline was re-run for it, and the selftest asserts the
version and every tool pin come out byte-identical. It also does not move the
level_factory pin to 0.41.0 -- 0.41.0 is tagged and has never been executed by
a Godot process. That is recorded in the tool note instead of hidden.

Corrections are marked as corrections and carry their date, the same way the
roadmap names its own wrong mechanisms rather than quietly rewriting them.

Usage:
    pwsh> python patch_manifest_128_corrections.py --check
    pwsh> python patch_manifest_128_corrections.py
    pwsh> python patch_manifest_128_corrections.py --selftest
    pwsh> python patch_manifest_128_corrections.py --revert
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "factory.manifest.json"
TAG = "pre_128corr"

# NOTE: these strings live inside a JSON string literal on one line. Nothing
# below may contain a double quote, a backslash or a newline, or the file
# stops being JSON. The selftest re-parses to prove it did not happen.

R1_OLD = (
    "lot's own unit suite is RED on a clean tree and predates this set -- 328 "
    "passed, 8 FAILED; six of the eight are one defect "
    "(`opening_engagement_is_fair` is handed a spawn POINT where it wants a "
    "crew PATH, site_spawns.py:470, so `math.dist(candidate, p)` raises on a "
    "float), plus one cover assertion (Enemy_5 sees the crew spawn down 51.9 m "
    "of open ground) and one rounding tolerance. Also not run:"
)
R1_NEW = (
    "CORRECTED 2026-08-18 -- THIS SET SAID lot's own unit suite was RED on a "
    "clean tree, 328 passed and 8 FAILED. That has not been true since Lot "
    "0.42.0. MEASURED 2026-08-18 on a clean tree at Lot 0.44.0, git 0028666, "
    "0 dirty files: 336 passed, 0 failed, 4.21 s. The three defects were "
    "fixed, not muted. 0.42.0 stopped `assemble` planning cover from a crew "
    "spawn the scene does not ship -- it planned from -70.0, 30.0 while "
    "`write_walk_scene` cleared to -60.5, 30.0 and shipped that, so from "
    "inside a building almost every sightline read as already broken and the "
    "planner reported open_lines 0 for a map it had never correctly measured. "
    "0.43.0 removed the second `place_enemies` call, which is why there had "
    "been two different Enemy_5s. 0.44.0 took enemy-to-enemy pairs off the "
    "opening cover budget. AND THE THIRD ONE WAS MISDESCRIBED HERE: the 18.5 m "
    "plan-versus-scene gap was not a rounding tolerance and was not filed as "
    "one -- the scene carried its plan exactly, 0 of 18 coordinate pairs "
    "failing, and the test held a route the tool never uses. The lot pin below "
    "was already 0.44.0; only this prose was stale, so the file has been "
    "contradicting itself, pin against paragraph. Also not run:"
)

R2_OLD = (
    "WHAT IS KNOWN OPEN inside a package this set produces: roadmap 50 -- "
    "`resource_manifest.json` records `mission.tscn` at 16,246 bytes when the "
    "file beside it is 688, and lists 14 files where the package holds 56. And "
    "the export closure scan reports `missing_resource_count: 0` while the "
    "scene it just counted carries 34 `res://` references that appear in none "
    "of its numbers; whether it reads them is UNMEASURED, so `ok: true` above "
    "is evidence that the three scenes chain and is not yet evidence that the "
    "art resolves."
)
R2_NEW = (
    "CORRECTED 2026-08-18 -- BOTH entries this set listed as KNOWN OPEN inside "
    "a package it produces are closed, and were already closed when this text "
    "was last written. Roadmap 50 -- `resource_manifest.json` recording "
    "`mission.tscn` at 16,246 bytes when the file beside it is 688, and "
    "listing 14 files where the package holds 56 -- was fixed in level_factory "
    "0.40.0, the version pinned below: the stale file joins the skip set the "
    "handoff copy already uses, so a package ships one manifest and it is the "
    "current one. And the closure-scan caveat is ANSWERED rather than open: "
    "`closure.py` globs every file under the mission root with "
    "`mission_root.rglob` and does not walk a reference graph at all, so its "
    "counters see the art whether or not a scene points at it, and `ok: true` "
    "IS evidence that the art resolves. NOTHING is currently listed as known "
    "open inside a package this set produces. That is a statement about what "
    "has been measured. It is not a claim that nothing is wrong."
)

R3_OLD = (
    "it was tagged on 2026-08-16 and sat UNCERTIFIED until factory-v1.26.0."
)
R3_NEW = R3_OLD + (
    " 0.41.0 IS TAGGED AND IS NOT IN THIS SET: it reads the applied Lux preset "
    "off LuxRoot rather than echoing the --preset argument back into "
    "lux.quality.json, adds preset_applied, and raises LUX_PRESET_NOT_APPLIED "
    "when the two disagree. No Godot process has ever executed it, so the pin "
    "stays at 0.40.0 until a lit run certifies it."
)

EDITS = [
    ("lot's suite is green, not red", R1_OLD, R1_NEW),
    ("both known-open entries are closed", R2_OLD, R2_NEW),
    ("0.41.0 is tagged and outside this set", R3_OLD, R3_NEW),
]

FORBIDDEN = ('"', "\\", "\n", "\r", "\t")


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:8].upper()


def _stamp(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    return f"{p.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


def _guard_replacements() -> None:
    """A double quote or a backslash in any replacement turns a valid manifest
    into a parse error, and this file is read by tooling that will not say so
    politely. Checked before the file is opened, not after it is written."""
    for label, _old, new in EDITS:
        bad = [c for c in FORBIDDEN if c in new]
        if bad:
            raise SystemExit(
                f"REFUSING: replacement for '{label}' contains {bad!r}, which "
                f"cannot appear raw inside a JSON string literal.")


def _require() -> None:
    if not MANIFEST.is_file():
        sys.exit(f"REFUSING: not found: {MANIFEST}")


def _plan(text: str) -> str:
    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(
                f"REFUSING: anchor for '{label}' occurs {n} times, expected 1.")
        text = text.replace(old, new, 1)
        print(f"  ok  {label}")
    return text


def _pins(doc: dict) -> dict:
    return {k: (v.get("version"), v.get("tag"))
            for k, v in doc.get("tools", {}).items()}


def cmd_check() -> int:
    _require()
    _guard_replacements()
    print("   ", _stamp(MANIFEST))
    t = MANIFEST.read_text(encoding="utf-8")
    if "CORRECTED 2026-08-18" in t:
        print("\nALREADY APPLIED.")
        return 0
    print()
    _plan(t)
    doc = json.loads(t)
    print(f"\nfactory_version {doc['factory_version']} -- NOT bumped; "
          f"a prose correction is not a re-certification")
    print(f"{len(_pins(doc))} tool pins -- all left byte-identical")
    return 0


def cmd_apply() -> int:
    _require()
    _guard_replacements()
    src = MANIFEST.read_text(encoding="utf-8")
    if "CORRECTED 2026-08-18" in src:
        print("ALREADY APPLIED; nothing to do.")
        return 0
    before = json.loads(src)
    out = _plan(src)
    after = json.loads(out)          # raises BEFORE anything is written

    if _pins(after) != _pins(before):
        raise SystemExit("REFUSING: a tool pin moved. This patch edits prose.")
    if after["factory_version"] != before["factory_version"]:
        raise SystemExit("REFUSING: factory_version moved.")

    (MANIFEST.parent / f"{MANIFEST.name}.{TAG}").write_bytes(MANIFEST.read_bytes())
    MANIFEST.write_text(out, encoding="utf-8", newline="")
    print("\nafter:")
    print("   ", _stamp(MANIFEST))
    print(f"\nsidecar .{TAG} written; `--revert` restores it.")
    return 0


def cmd_revert() -> int:
    side = MANIFEST.parent / f"{MANIFEST.name}.{TAG}"
    if not side.is_file():
        print("nothing to revert.")
        return 0
    MANIFEST.write_bytes(side.read_bytes())
    side.unlink()
    print(f"  restored {MANIFEST.name}")
    return 0


CHECKS = [
    ("still valid JSON", lambda t: _parses(t)),
    ("the RED-suite claim is gone",
     lambda t: "328 passed, 8 FAILED" not in t),
    ("the measured green number is present",
     lambda t: "336 passed, 0 failed, 4.21 s" in t),
    ("the 18.5 m gap is not called a tolerance",
     lambda t: "one rounding tolerance" not in t),
    ("roadmap 50 is no longer listed as known open",
     lambda t: "WHAT IS KNOWN OPEN inside a package this set produces: roadmap 50" not in t),
    ("the closure-scan caveat is answered",
     lambda t: "mission_root.rglob" in t and "is not yet evidence that the art resolves" not in t),
    ("0.41.0 is named as tagged and outside the set",
     lambda t: "0.41.0 IS TAGGED AND IS NOT IN THIS SET" in t),
]


def _parses(t: str) -> bool:
    try:
        json.loads(t)
        return True
    except json.JSONDecodeError:
        return False


def cmd_selftest() -> int:
    _require()
    t = MANIFEST.read_text(encoding="utf-8")
    side = MANIFEST.parent / f"{MANIFEST.name}.{TAG}"

    bad = []
    for name, fn in CHECKS:
        ok = fn(t)
        print(("  ok  " if ok else "  FAIL ") + name)
        if not ok:
            bad.append(name)
    if bad:
        raise SystemExit("SELFTEST FAILED: " + "; ".join(bad))

    if side.is_file():
        pre = side.read_text(encoding="utf-8")
        # `still valid JSON` is true of the pre-image BY DESIGN -- it is an
        # invariant, not a change -- so it is excluded rather than counted as
        # a check that tests nothing.
        useless = [name for name, fn in CHECKS
                   if name != "still valid JSON" and fn(pre)]
        if useless:
            raise SystemExit(
                "SELFTEST FAILED: these hold on the PRE-IMAGE too, so they "
                "test nothing: " + "; ".join(useless))
        print("  ok  every content check fails on the pre-image")

        a, b = json.loads(t), json.loads(pre)
        if _pins(a) != _pins(b):
            raise SystemExit("SELFTEST FAILED: a tool pin moved.")
        print(f"  ok  all {len(_pins(a))} tool pins byte-identical")
        if a["factory_version"] != b["factory_version"]:
            raise SystemExit("SELFTEST FAILED: factory_version moved.")
        print(f"  ok  factory_version still {a['factory_version']} "
              f"(prose correction, not re-certification)")
        moved = [k for k in set(a) | set(b) if a.get(k) != b.get(k)]
        if moved != ["description"]:
            # tools changed too, via the level_factory note
            if sorted(moved) != ["description", "tools"]:
                raise SystemExit(
                    f"SELFTEST FAILED: unexpected top-level keys changed: {moved}")
            tmoved = [k for k in a["tools"] if a["tools"][k] != b["tools"][k]]
            if tmoved != ["level_factory"]:
                raise SystemExit(
                    f"SELFTEST FAILED: unexpected tools changed: {tmoved}")
        print(f"  ok  changed keys limited to {sorted(moved)}"
              " (+ tools.level_factory.note only)")
    else:
        print("  --  no sidecar; pre-image comparison skipped")

    print("\nSELFTEST PASSED")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--revert", action="store_true")
    g.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.check:
        return cmd_check()
    if a.revert:
        return cmd_revert()
    if a.selftest:
        return cmd_selftest()
    return cmd_apply()


if __name__ == "__main__":
    raise SystemExit(main())
