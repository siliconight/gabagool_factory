r"""factory-v1.25.0 -- the first certified set that produces a package
which opens.

    python patches\\patch_manifest_125.py --check
    python patches\\patch_manifest_125.py
    python patches\\patch_manifest_125.py --selftest
    python patches\\patch_manifest_125.py --revert

Run from the FACTORY ROOT.

    factory.manifest.json   factory_version 1.24.0 -> 1.25.0
                            level_factory   0.37.0 -> 0.39.0 (+ tag)
                            description     re-certified, 2026-08-14 demoted
                                            to PRIOR CERTIFICATION
    CHANGELOG.md            factory-v1.25.0 entry

ONLY level_factory MOVES. The other nine were already pinned at the versions
the 3b run used -- deli_counter 0.89.0, lot 0.41.0, lux 0.16.0, patina
0.19.0, pixelcoat 0.12.0, zoo 0.36.0, dispatch 0.3.1, pipeline 0.6.0,
laser_tag 0.8.0 -- so this is a genuine lockstep bump of one tool and not a
re-pin of ten.

`doctor` REPORTING DRIFT IS NOT THIS FILE. Its "drift vs certified 0.75.0
(grounded)" compares against `packages/tools/contracts.py`'s GROUNDED, a
different source from this manifest, and the two disagreeing is its own open
question. Nothing here touches it.

THE DESCRIPTION SAYS WHAT WAS NOT RUN, AT LENGTH, ON PURPOSE

lot's suite is RED -- 328 passed, 8 failed, on a clean tree. A certified set
that did not say so would be the same defect this arc has spent itself on. It
also records that `ok: true` from the closure scan is evidence the three
scenes chain and is NOT yet evidence that the art resolves, because the scan
never mentions the 34 `res://` references in the scene it counted.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
CHANGELOG = "CHANGELOG.md"
SIDECAR = ".pre_125"

OLD_FACTORY, NEW_FACTORY = "1.24.0", "1.25.0"
OLD_LF, NEW_LF = "0.37.0", "0.39.0"

OLD_DESC = 'The certified lockstep set: these tool versions were verified TOGETHER. Re-certified 2026-08-14, on the art layer. What was run: the mission re-ran end to end and graded its three candidates 40 / 55 / 60, selecting lot_demo_001.candidate.seed_5219; check_all reports gdscript, stairs and steps clean; the portable package opened in a clean Godot project with zero plugins, zero autoloads and zero external references, 18.6 MB across 212 entries; four deli_counter shell fixes were engine-confirmed, taking nav_gate from 7 of 135 shells failing to 3. What was NOT run and is therefore not covered by this set: the walk sweep (library_walk, needs Godot, about an hour for 20 sites), the pack load check, and the lot and deli_counter unit suites. What is known failing: check_all freshness reports 57 buildings whose geometry no longer matches the spec or builder that made them, and three demo shells -- cbp, night_pawn and primos_pizza -- still fail nav_gate; none of the three is in the lot_demo_001 draw, and cbp fails on a first floor fragmented across 63 islands rather than on the stair geometry the other fixes addressed. '
NEW_DESC = "The certified lockstep set: these tool versions were verified TOGETHER. Re-certified 2026-08-16, on the first package this pipeline has produced that opens. WHAT WAS RUN: unlit_probe_001, built COLD from an empty workspace through Blender 5.1.1 and headless Godot 4.7 (tools/run_3b_unlit.ps1) -- one mission, one candidate, seed 5017, ONE building, `--art --unlit --gameplay`. Structural checks passed, 0 blockers, 22 findings. `lot_assemble`, `walktest_navqa` and `laser_tag_evaluate` all report `cache` on the art pass, which is the evidence for roadmap 48: the graded site IS the shipped site, established by fingerprint rather than by inspection. Exported in BOTH `portable-godot` and `art-unlit`: export_closure_scan `ok: true`, `issues: []`, `unresolved_relative_count: 0`, a 56-file package whose entry reaches `lot/shell/site.tscn` (48,004 B) and the 31 GLBs beside it, with no duplicate copy at the root. Level Factory's suite: 823 passed, 11 skipped, 0 failed. WHAT WAS NOT RUN, and is therefore NOT covered by this set: lot's own unit suite is RED on a clean tree and predates this set -- 328 passed, 8 FAILED; six of the eight are one defect (`opening_engagement_is_fair` is handed a spawn POINT where it wants a crew PATH, site_spawns.py:470, so `math.dist(candidate, p)` raises on a float), plus one cover assertion (Enemy_5 sees the crew spawn down 51.9 m of open ground) and one rounding tolerance. Also not run: the walk sweep (library_walk), the pack load check, deli_counter's suite, the real_tools suite, and lot_demo_001 has NOT been re-exported since level_factory 0.39.0 -- the five-building shape is the one this release's fix deliberately leaves untouched, and nothing has re-measured it. WHAT IS KNOWN OPEN inside a package this set produces: roadmap 50 -- `resource_manifest.json` records `mission.tscn` at 16,246 bytes when the file beside it is 688, and lists 14 files where the package holds 56. And the export closure scan reports `missing_resource_count: 0` while the scene it just counted carries 34 `res://` references that appear in none of its numbers; whether it reads them is UNMEASURED, so `ok: true` above is evidence that the three scenes chain and is not yet evidence that the art resolves. PRIOR CERTIFICATION, 2026-08-14: What was run: the mission re-ran end to end and graded its three candidates 40 / 55 / 60, selecting lot_demo_001.candidate.seed_5219; check_all reports gdscript, stairs and steps clean; the portable package opened in a clean Godot project with zero plugins, zero autoloads and zero external references, 18.6 MB across 212 entries; four deli_counter shell fixes were engine-confirmed, taking nav_gate from 7 of 135 shells failing to 3. What was NOT run and is therefore not covered by this set: the walk sweep (library_walk, needs Godot, about an hour for 20 sites), the pack load check, and the lot and deli_counter unit suites. What is known failing: check_all freshness reports 57 buildings whose geometry no longer matches the spec or builder that made them, and three demo shells -- cbp, night_pawn and primos_pizza -- still fail nav_gate; none of the three is in the lot_demo_001 draw, and cbp fails on a first floor fragmented across 63 islands rather than on the stair geometry the other fixes addressed. "
CHANGELOG_ENTRY = "## [factory-v1.25.0] - 2026-08-16\n\nlevel_factory 0.37.0 -> 0.39.0. The other nine tools are unchanged from\nfactory-v1.24.0.\n\nWHAT THE SET NOW DOES THAT IT DID NOT\n\nIt produces a package that opens. On a single-shell mission it never has --\n`export_mission` step 2.5 has been overwriting the root `site.tscn` with the\nassembly scene since 0.37.0, and the assembly names `lot/<id>/site.tscn`, a\ndirectory the export did not carry. Both `portable-godot` and `art-unlit`\nshipped 56 files whose entry reached two of them. Roadmap 49, fixed in\n0.39.0.\n\nAnd the buildings a mission places no longer depend on which command is\nrunning. `_art_run` was read off the invocation's planned graph, so `batch\ncreate` drew from 123 shells and `run --art` drew from 98 -- same job id,\nsame seed, two different buildings, with every grader and the functional lock\nmeasuring the first and the package shipping the second. Roadmap 48, fixed in\n0.38.0. The lock caught it, which is the only reason anybody found out.\n\nWHAT WAS RUN\n\nunlit_probe_001, cold from an empty workspace, Blender 5.1.1 and headless\nGodot 4.7. `lot_assemble`, `walktest_navqa` and `laser_tag_evaluate` all\nreport `cache` on the art pass -- the graded site IS the shipped site, by\nfingerprint. Export closure `ok: true` in both modes. LF suite 823/11/0.\n\nWHAT WAS NOT RUN\n\nlot's suite is RED and predates this set: 328 passed, 8 failed, six of them\none arity defect in `opening_engagement_is_fair`. The walk sweep, the pack\nload check, deli_counter's suite and the real_tools suite were not run.\nlot_demo_001 has not been re-exported since 0.39.0 -- the five-building shape\nis the one 0.39.0 deliberately leaves untouched, and nothing has re-measured\nit.\n\nWHAT IS KNOWN OPEN\n\nRoadmap 50: the package ships a `resource_manifest.json` describing a\ndifferent package. And the closure scan's `missing_resource_count: 0` sits\nbeside a scene carrying 34 `res://` references the scan's numbers never\nmention -- unmeasured, and recorded as a question rather than a finding.\n\n"

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(body: str) -> str:
    crlf = body.count(_CRLF)
    return _CRLF if crlf > (body.count("\n") - crlf) else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    missing = [r for r in (MANIFEST, CHANGELOG) if not (root / r).is_file()]
    if missing:
        print("REFUSING: not here -- run from the factory root: "
              + ", ".join(missing))
        return 1

    p = root / MANIFEST
    raw = p.read_bytes()
    m = json.loads(raw.decode("utf-8"))

    # EDITED AS JSON, not as text. The manifest is machine-written (the
    # version tools read and rewrite it), so a text patch would fight
    # whatever formatting those produce; the anchors that matter here are
    # VALUES, and json.loads finds them wherever they sit.
    fv, lf = m.get("factory_version"), m["tools"]["level_factory"]
    done = fv == NEW_FACTORY and lf["version"] == NEW_LF
    if not done:
        if fv != OLD_FACTORY:
            print(f"REFUSING: factory_version is {fv!r}, expected "
                  f"{OLD_FACTORY!r}")
            return 1
        if lf["version"] != OLD_LF or lf.get("tag") != f"v{OLD_LF}":
            print(f"REFUSING: level_factory is {lf['version']!r} / "
                  f"{lf.get('tag')!r}, expected {OLD_LF!r} / v{OLD_LF}")
            return 1
        if m.get("description", "")[:len(OLD_DESC)] != OLD_DESC:
            print("REFUSING: the description does not open with the 1.24.0 "
                  "certification text -- it has been edited since, and this "
                  "would discard that edit")
            return 1
        m["factory_version"] = NEW_FACTORY
        lf["version"] = NEW_LF
        lf["tag"] = f"v{NEW_LF}"
        m["description"] = NEW_DESC + m["description"][len(OLD_DESC):]

    if done:
        print(f"  already applied  {MANIFEST}")
    else:
        data = (json.dumps(m, indent=2, ensure_ascii=False) + "\n").encode()
        if check:
            print(f"  would patch  {MANIFEST}  {len(raw):,} -> {len(data):,} "
                  f"bytes ({len(data) - len(raw):+,})")
        else:
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                side.write_bytes(raw)
            p.write_bytes(data)
            print(f"  patched      {MANIFEST}  {len(raw):,} -> {len(data):,} "
                  f"bytes ({len(data) - len(raw):+,})  sha256 "
                  f"{_sha(data)[:16]}")

    c = root / CHANGELOG
    craw = c.read_bytes()
    cbody = craw.decode("utf-8")
    ceol = _eol(cbody)
    head = _as(f"## [factory-v{OLD_FACTORY}] - ", ceol)
    if _as(f"## [factory-v{NEW_FACTORY}] - ", ceol) in cbody:
        print(f"  already has {NEW_FACTORY}  {CHANGELOG}")
    elif cbody.count(head) != 1:
        print(f"REFUSING: {CHANGELOG} has {cbody.count(head)} "
              f"'## [factory-v{OLD_FACTORY}] - ' headings, expected 1")
        return 1
    else:
        cnew = cbody.replace(head, _as(CHANGELOG_ENTRY, ceol) + head, 1)
        if check:
            print(f"  would patch  {CHANGELOG}  {len(craw):,} -> "
                  f"{len(cnew.encode()):,} bytes")
        else:
            side = c.with_suffix(c.suffix + SIDECAR)
            if not side.is_file():
                side.write_bytes(craw)
            c.write_bytes(cnew.encode("utf-8"))
            print(f"  patched      {CHANGELOG}  {len(craw):,} -> "
                  f"{len(cnew.encode()):,} bytes")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    m = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    check(f"factory_version is {NEW_FACTORY}",
          m.get("factory_version") == NEW_FACTORY)
    lf = m["tools"]["level_factory"]
    check(f"level_factory is {NEW_LF} and tagged v{NEW_LF}",
          lf["version"] == NEW_LF and lf["tag"] == f"v{NEW_LF}")
    check("the other nine tools are untouched",
          {k: v["version"] for k, v in m["tools"].items()
            if k != "level_factory"}
          == {"deli_counter": "0.89.0", "dispatch": "0.3.1",
              "laser_tag": "0.8.0", "lot": "0.41.0", "lux": "0.16.0",
              "patina": "0.19.0", "pipeline": "0.6.0",
              "pixelcoat": "0.12.0", "zoo": "0.36.0"})
    check("every tool's tag matches its version",
          all(v["tag"] == "v" + v["version"] for v in m["tools"].values()))

    d = " ".join(m.get("description", "").split())
    check("the description is re-certified 2026-08-16",
          d.startswith("The certified lockstep set: these tool versions were "
                       "verified TOGETHER. Re-certified 2026-08-16"))
    check("...and says what was RUN, cold, through the real tools",
          "built COLD from an empty workspace" in d
          and "Blender 5.1.1 and headless Godot 4.7" in d)
    check("...citing the cache hits that close roadmap 48",
          "all report `cache` on the art pass" in d)
    check("...and the closure result in BOTH modes",
          "BOTH `portable-godot` and `art-unlit`" in d
          and "`unresolved_relative_count: 0`" in d)
    check("...and LF's suite count",
          "823 passed, 11 skipped, 0 failed" in d)
    check("it says lot's suite is RED, with the number",
          "328 passed, 8 FAILED" in d)
    check("...and what the eight actually are",
          "spawn POINT where it wants a crew PATH" in d
          and "site_spawns.py:470" in d)
    check("it names what was NOT run",
          "library_walk" in d and "the real_tools suite" in d
          and "lot_demo_001 has NOT been re-exported" in d)
    check("...including that the five-building shape is unmeasured",
          "the five-building shape is the one this release's fix "
          "deliberately leaves untouched" in d)
    check("it names what is known open INSIDE the package",
          "roadmap 50" in d and "16,246 bytes when the file beside it is 688"
          in d)
    check("...and does not let `ok: true` claim more than it proves",
          "is not yet evidence that the art resolves" in d)
    check("the 2026-08-14 certification is demoted, not deleted",
          "PRIOR CERTIFICATION, 2026-08-14:" in d
          and "graded its three candidates 40 / 55 / 60" in d)
    check("...and the 2026-07-28 one is still there under it",
          "PRIOR CERTIFICATION, 2026-07-28:" in d)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check(f"CHANGELOG leads with factory-v{NEW_FACTORY}",
          cl.split("## [")[1].startswith(f"factory-v{NEW_FACTORY}]"))
    clf = " ".join(cl.split())
    check("...and says only level_factory moved",
          "The other nine tools are unchanged from factory-v1.24.0" in clf)
    check("...and credits the lock for catching item 48",
          "The lock caught it, which is the only reason anybody found out"
          in clf)
    check("...and carries the same NOT-RUN list",
          "lot's suite is RED and predates this set" in clf)

    print()
    print("  certified, and honest about what it does not cover"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / MANIFEST).is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        rc = 0
        for rel in (MANIFEST, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if side.is_file():
                p.write_bytes(side.read_bytes())
                print(f"  reverted     {rel}")
            else:
                print(f"  no sidecar for {rel}")
                rc = 1
        return rc
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_manifest_125.py --selftest")
        print()
        print("  then tag the factory repo:")
        print("    git tag factory-v1.25.0")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
