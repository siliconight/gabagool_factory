r"""Roadmap items 49 and 50, and item 48 CLOSED.

    python patches\\patch_roadmap_49.py --check
    python patches\\patch_roadmap_49.py
    python patches\\patch_roadmap_49.py --selftest
    python patches\\patch_roadmap_49.py --revert

Run from the FACTORY ROOT. Then:

    python tools\\roadmap_status.py --write

FOUR EDITS, ONE FILE

1. Item 48's STATUS becomes CLOSED. Fixed in level_factory 0.38.0 (tag
   fe428551) and re-measured on a cold workspace: three `cache` hits where
   there were three re-runs, and no lock refusal.
2. Item 49 -- the composed scene the site spec points at is never staged, so
   54 of 56 shipped files are unreachable from the entry.
3. Item 50 -- the package ships a resource manifest describing a different
   package.
4. `probe_unlit_ab.py`'s vacuous manifest check joins "Smaller, carried".

WHY 49 AND 50 ARE SEPARATE ITEMS

They were found in the same minute and they are not the same defect. 49 is a
file that should be in the package and is not. 50 is a file that IS in the
package and lies about it. One is a staging step; the other is a boundary
between two tools that both write `mission.tscn`. Merging them would produce
an item whose fix is two fixes.

WHY THE PROBE'S DEFECT IS WRITTEN DOWN AT ALL

It is mine, it is small, and it is the exact family this arc has been about:
a check that reported `ok` about a file it never opened. Leaving it out
because it is embarrassing is how the other six survived.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r49"

STATUS_48_OLD = '*STATUS: OPEN 2026-08-15 -- MEASURED on unlit_probe_001'
STATUS_48_NEW = "*STATUS: CLOSED 2026-08-16 -- FIXED and re-measured on a cold workspace. level_factory 0.38.0 keys the narrowing on the brief instead of on the invocation's planned graph; `art_run` is gone from the signature, the call site and the module. Re-running `tools/run_3b_unlit.ps1` from empty, through Blender and headless Godot: `lot_assemble`, `walktest_navqa` and `laser_tag_evaluate` all report `cache` on the art pass -- the art run produced a byte-identical site spec, so the assemble did not re-execute and neither did the graders. The graded site IS the shipped site, established by the fingerprint cache rather than by anyone comparing two files. `[site] graded lot: 98 of 123 ... keyed on the brief` now prints identically in both invocations, and the functional lock does not fire. Suite 823 passed / 11 skipped / 0 failed. Question 1 -- whether the draw may move behind `candidate_selected` at all -- is NOT answered by this and is carried into item 49's neighbourhood. ORIGINALLY MEASURED on unlit_probe_001"

ANCHOR_END = "\n### Not to be worked on\n"
ANCHOR_SMALL = '### Smaller, carried\n\n**`MIGRATIONS.md` indexes one run rather than a directory.**'

INSERT_49 = '*STATUS: OPEN 2026-08-16 -- MEASURED on unlit_probe_001 after item 48 was fixed. 56 files ship, 7,158,515 bytes; the entry scene reaches TWO of them. `site.tscn`\'s only `ext_resource` is `lot/shell/site.tscn`, which is not in the package, so the 30 Zoo GLBs, the dressing and the fixtures are all orphaned. IDENTICAL in `portable-godot` and `art-unlit`, which acquits `--unlit`. Found by the export closure scan on its first run against a varied lot -- exactly what item 47 said would happen*\n\n**49. The composed scene the site points at is never staged, and 54 of 56\nshipped files are unreachable from the entry.**\n`unlit_probe_001` exported for the first time on 2026-08-16, item 48\'s fix\nhaving removed the functional-lock refusal that had been stopping it earlier.\nBoth modes then failed the same way:\n\n```\nEXPORT_CLOSURE_BROKEN: 0 unresolved res:// reference(s), 0 misrooted,\n                       1 unresolved relative, 0 absolute path(s)\n  site.tscn: relative ext_resource resolves to nothing: lot/shell/site.tscn (from ./)\n  resource_count: 2\n```\n\n`site.tscn` carries exactly one `ext_resource`:\n\n```\n[ext_resource type="PackedScene" path="lot/shell/site.tscn" id="b1"]\n```\n\nThere is no `lot/` directory in the package at all. The walk is\n`mission.tscn` -> `site.tscn` -> nothing, two resources deep, in a 56-file\n7.2 MB package.\n\n**`_write_site_spec` promises that path and something else has to keep it.**\n\n```python\ndef _source(entry):\n    aid = str(entry["id"])\n    scene = (themed_map or {}).get(entry["id"])\n    if scene:\n        staged_packages[aid] = str(Path(scene).parent)\n        return {"scene": f"lot/{aid}/site.tscn"}\n    staged_glbs[aid] = str(entry["glb"])\n    return {"glb": f"buildings/{aid}.glb"}\n```\n\nThe spec names `lot/<aid>/site.tscn` and records the source directory in\n`staged_packages`. The composed scene\'s whole DIRECTORY is the unit -- its\nown comment says so, because `site.tscn` is useless without the\n`site_base.glb` and `art/` beside it. Whoever consumes `staged_packages` is\nwhere this ends, and it is one export away from being known.\n\n**BEFORE ANY OF THAT, THE ARCHETYPE IS CALLED `shell`.** Not\n`landmark_hall_a03`, not `cr_garage` -- `shell`. And in\n`resource_manifest.json`:\n\n```\nassets/lot.glb    sha256:a929d7d2...  242,176 bytes\nassets/shell.glb  sha256:a929d7d2...  242,176 bytes\n```\n\nThe same file twice, and that hash is the `shell.glb` the fingerprints\nrecord. So the lot\'s one building is the mission\'s OWN SHELL, drawn back out\nof `deli_counter/build` as though it were a source archetype. That directory\nis both the source and the sink -- the site builder already prints eleven\nentries it excluded for exactly this reason, and `shell` was not among them.\nWhether the narrower 98-shell pool now reaches the pipeline\'s own output is\nthe FIRST question here, because if it does, the missing `lot/shell/`\ndirectory is a symptom and staging it would ship the wrong thing correctly.\n\n**Two failures are possible and they want different fixes.** Either the\nstaging step never ran for this lot, or it ran and the export dropped what it\nstaged. The export\'s mode logic is the obvious suspect and is exonerated by\nthe A/B: `portable-godot` and `art-unlit` produce byte-identical packages\nhere -- 56 files, 7,158,515 bytes, zero files differing -- because Lux never\nran on this mission and there was nothing to subtract. Whatever drops the\ndirectory drops it in both.\n\n'
INSERT_50 = '*STATUS: OPEN 2026-08-16 -- MEASURED on the same package. `resource_manifest.json` says `mission.tscn` is 16,246 bytes; the file beside it is 688. Written by Dispatch at `...388494` and overwritten by LF at `...389514`, one second later, with no rewrite of the manifest. It also lists 14 files where the package holds 56 -- no `site.tscn`, no `site_base.glb`, none of the 30 `art/` GLBs*\n\n**50. The package ships a resource manifest that describes a different\npackage.**\n`dispatch.resource_manifest.v0.2`, in the export root, next to the files it\nis wrong about:\n\n```\nresource_manifest.json:  mission.tscn   16,246 bytes  sha256:35165b8d...\non disk:                 mission.tscn      688 bytes\n```\n\nThe mtimes say what happened without needing anybody\'s memory:\n`resource_manifest.json` was written at `...388494` and `mission.tscn` at\n`...389514`. Dispatch wrote a manifest describing ITS entry scene; Level\nFactory then replaced the entry scene with its own 688-byte portable one and\nleft the manifest alone. A consumer verifying the package against its own\nmanifest fails on the first file.\n\n**And it is not only stale, it is short.** The manifest lists 14 files. The\npackage holds 56. `site.tscn`, `site_base.glb` and all 30 `art/` GLBs are\nabsent from it -- which means a recipient checking "did I receive everything"\nagainst this file would conclude yes while holding a package whose art is\nundescribed.\n\nThis is the same boundary as the discarded 65,493-byte Dispatch\n`mission.tscn` already on the smaller list: two tools write the same\nartifact, the second wins, and the first tool\'s account of the package\nsurvives it. The manifest is either Dispatch\'s to own and LF must not\noverwrite what it describes, or it is a package-level artifact and belongs\ndownstream of every writer. It is currently neither.\n\n'
SMALLER = "**`probe_unlit_ab.py`'s manifest section reads nothing and reports `ok` for\nit.** Run against the 3b packages it printed `profile=None layers=None\npackage_dir=None archive=None` for both, then `ok the unlit manifest does not\nclaim the light layer` -- a pass derived from a file it never opened. It looks\nfor `LF_MANIFEST.json`, which only an ARCHIVE export writes; a `--format\nfolder` export has no such file. Three of its four LOOK lines come from the\nsame absence. This is the defect the probe was written to find, in the probe,\nand its manifest output should not be read until it either locates the folder\nexport's manifest or says out loud that it found none.\n\n"

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(body: str) -> str:
    """KEYED OFF THE FILE, never off an anchor."""
    crlf = body.count(_CRLF)
    return _CRLF if crlf > (body.count("\n") - crlf) else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    p = root / ROADMAP
    if not p.is_file():
        print(f"REFUSING: {ROADMAP} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)

    if _as("**48. The same job and the same seed draw", eol) not in body:
        print("REFUSING: item 48 is not in the file -- run "
              "patches\\patch_roadmap_48.py and 48b first")
        return 1

    out = body
    already = 0

    o, n = _as(STATUS_48_OLD, eol), _as(STATUS_48_NEW, eol)
    if n in out:
        already += 1
    elif out.count(o) == 1:
        out = out.replace(o, n, 1)
    else:
        print(f"REFUSING: item 48's OPEN status head occurs {out.count(o)} "
              f"time(s), expected 1")
        return 1

    anchor = _as(ANCHOR_END, eol)
    if _as("**49. The composed scene the site points at", eol) in out:
        already += 1
    elif out.count(anchor) == 1:
        out = out.replace(
            anchor,
            _as("\n" + INSERT_49 + INSERT_50 + "### Not to be worked on\n",
                eol), 1)
    else:
        print(f"REFUSING: the closing heading occurs {out.count(anchor)} "
              f"time(s), expected 1")
        return 1

    small = _as(ANCHOR_SMALL, eol)
    if _as("**`probe_unlit_ab.py`'s manifest section reads nothing", eol) \
            in out:
        already += 1
    elif out.count(small) == 1:
        out = out.replace(
            small,
            _as("### Smaller, carried\n\n" + SMALLER
                + "**`MIGRATIONS.md` indexes one run rather than a "
                  "directory.**", eol), 1)
    else:
        print(f"REFUSING: the 'Smaller, carried' anchor occurs "
              f"{out.count(small)} time(s), expected 1")
        return 1

    if already == 3:
        print(f"  already applied  {ROADMAP}")
        return 0
    if already:
        print(f"REFUSING: {already} of 3 edits are already present -- the "
              f"file is part-patched. Revert or fix by hand.")
        return 1

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
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import re
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    disk = (root / ROADMAP).read_bytes().decode("utf-8")
    check("the file's line endings are preserved",
          disk.count(_CRLF) > 0 or "\r" not in disk)
    md = disk.replace(_CRLF, "\n")

    m48 = "**48. The same job and the same seed draw"
    check("item 48 is still there", m48 in md)
    if m48 not in md:
        print(f"\n  {bad} FAILURE(S) -- run patch_roadmap_48.py first")
        return 1
    s48 = md[:md.index(m48)].rstrip().splitlines()[-1]
    check("item 48 is CLOSED", s48.startswith("*STATUS: CLOSED 2026-08-16"))
    check("...on the evidence that actually closes it, the cache hits",
          "`cache` on the art pass" in s48
          and "walktest_navqa" in s48 and "laser_tag_evaluate" in s48)
    check("...and names the release that did it",
          "level_factory 0.38.0" in s48)
    check("...and does NOT claim question 1 is answered",
          "is NOT answered by this" in s48)
    check("...and keeps the original measurement rather than erasing it",
          "ORIGINALLY MEASURED on unlit_probe_001" in s48)

    m49 = "**49. The composed scene the site points at"
    check("item 49 is present", m49 in md)
    if m49 not in md:
        print(f"\n  {bad} FAILURE(S)")
        return 1
    i49 = md.index(m49)
    s49 = md[:i49].rstrip().splitlines()[-1]
    check("49 carries a STATUS line",
          s49.startswith("*STATUS: OPEN 2026-08-16"))
    b49 = md[i49:md.index("**50. The package ships", i49)]
    f49 = " ".join(b49.split())
    check("49 quotes the closure scan verbatim",
          "relative ext_resource resolves to nothing: lot/shell/site.tscn"
          in b49 and "resource_count: 2" in b49)
    check("49 gives the package size the scan is silent about",
          "56" in b49 and "7,158,515" in b49)
    check("49 quotes the code that promises the path",
          "staged_packages[aid]" in b49
          and "lot/{aid}/site.tscn" in b49)
    check("49 raises the `shell` archetype BEFORE the staging fix",
          "THE ARCHETYPE IS CALLED `shell`" in b49)
    check("...with the duplicate-hash evidence for it",
          "a929d7d2" in b49 and b49.count("242,176") == 2)
    check("...and says why that must be settled first",
          "staging it would ship the wrong thing correctly" in f49)
    check("49 records the A/B that acquits --unlit",
          "byte-identical" in f49 and "zero files differing" in f49)

    m50 = "**50. The package ships a resource manifest"
    check("item 50 is present", m50 in md)
    i50 = md.index(m50)
    s50 = md[:i50].rstrip().splitlines()[-1]
    check("50 carries a STATUS line",
          s50.startswith("*STATUS: OPEN 2026-08-16"))
    b50 = md[i50:md.index("### Not to be worked on", i50)]
    f50 = " ".join(b50.split())
    check("50 gives both sizes of the same file",
          "16,246 bytes" in b50 and "688 bytes" in b50)
    check("...and the mtimes that establish the order",
          "...388494" in b50 and "...389514" in b50)
    check("...and that the manifest is short as well as stale",
          "lists 14 files" in f50 and "package holds 56" in f50)
    check("50 states the boundary rather than picking a fix",
          "It is currently neither" in f50)

    check("the probe's own defect is written down",
          "**`probe_unlit_ab.py`'s manifest section reads nothing" in md)
    check("...with the tell -- a pass from a file it never opened",
          "a pass derived from a file it never opened" in " ".join(md.split()))
    check("...and it sits in Smaller/carried, not as an item",
          md.index("probe_unlit_ab.py`'s manifest section")
          > md.index("### Smaller, carried"))

    nums = [int(x) for x in re.findall(r"^\*\*(\d+)\. ", md, re.M)]
    check("the numbering is contiguous through 50", nums[-3:] == [48, 49, 50])
    check("every fenced block in 49 and 50 is closed",
          b49.count("```") % 2 == 0 and b50.count("```") % 2 == 0)
    check("both items end with a blank line before what follows",
          b49.endswith("\n\n") and b50.endswith("\n\n"))
    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  three findings from one export, written the night they were made"
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
        print("    python patches\\patch_roadmap_49.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
