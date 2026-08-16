r"""Roadmap 49b -- the cause is found, and the first draft of item 49 was wrong.

    python patches\\patch_roadmap_49b.py --check
    python patches\\patch_roadmap_49b.py
    python patches\\patch_roadmap_49b.py --selftest
    python patches\\patch_roadmap_49b.py --revert

Run from the FACTORY ROOT, AFTER patch_roadmap_49.py. Then:

    python tools\\roadmap_status.py --write

ONE EDIT: item 49's STATUS line and body, replaced whole.

WHAT CHANGED, AND WHY IT IS A REPLACEMENT RATHER THAN AN ADDENDUM

The first draft said the composed scene "is never staged" and led with the
possibility that the lot was drawing this pipeline's own output as a source
archetype. Both are wrong, and they are wrong in the title as well as the
body, so appending a correction would leave a heading that lies and a table
row derived from it that lies too.

    staging          WORKS -- themed_site_assemble/out/lot/shell/site.tscn,
                     47,460 B, with site_base.glb and art/ beside it
    the export       FLATTENS that directory to the package root; root files
                     carry byte-identical sizes AND mtimes to their originals
    the loss         lot/shell/site.tscn collides on basename with the site's
                     own site.tscn, so the 47 KB building scene is dropped and
                     the 5,567 B site scene survives

THE REFUTED HYPOTHESIS IS KEPT, in its own section at the end. It was
reasonable, its evidence was real (`assets/lot.glb` and `assets/shell.glb`
ship at one sha256), and `tools/probe_lot_own_output.py` exists because of it.
A reader who trips over that duplicate hash next month should find out here
that it has been chased already, rather than chase it again.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r49b"

OLD_BLOCK = '*STATUS: OPEN 2026-08-16 -- MEASURED on unlit_probe_001 after item 48 was fixed. 56 files ship, 7,158,515 bytes; the entry scene reaches TWO of them. `site.tscn`\'s only `ext_resource` is `lot/shell/site.tscn`, which is not in the package, so the 30 Zoo GLBs, the dressing and the fixtures are all orphaned. IDENTICAL in `portable-godot` and `art-unlit`, which acquits `--unlit`. Found by the export closure scan on its first run against a varied lot -- exactly what item 47 said would happen*\r\n\r\n**49. The composed scene the site points at is never staged, and 54 of 56\r\nshipped files are unreachable from the entry.**\r\n`unlit_probe_001` exported for the first time on 2026-08-16, item 48\'s fix\r\nhaving removed the functional-lock refusal that had been stopping it earlier.\r\nBoth modes then failed the same way:\r\n\r\n```\r\nEXPORT_CLOSURE_BROKEN: 0 unresolved res:// reference(s), 0 misrooted,\r\n                       1 unresolved relative, 0 absolute path(s)\r\n  site.tscn: relative ext_resource resolves to nothing: lot/shell/site.tscn (from ./)\r\n  resource_count: 2\r\n```\r\n\r\n`site.tscn` carries exactly one `ext_resource`:\r\n\r\n```\r\n[ext_resource type="PackedScene" path="lot/shell/site.tscn" id="b1"]\r\n```\r\n\r\nThere is no `lot/` directory in the package at all. The walk is\r\n`mission.tscn` -> `site.tscn` -> nothing, two resources deep, in a 56-file\r\n7.2 MB package.\r\n\r\n**`_write_site_spec` promises that path and something else has to keep it.**\r\n\r\n```python\r\ndef _source(entry):\r\n    aid = str(entry["id"])\r\n    scene = (themed_map or {}).get(entry["id"])\r\n    if scene:\r\n        staged_packages[aid] = str(Path(scene).parent)\r\n        return {"scene": f"lot/{aid}/site.tscn"}\r\n    staged_glbs[aid] = str(entry["glb"])\r\n    return {"glb": f"buildings/{aid}.glb"}\r\n```\r\n\r\nThe spec names `lot/<aid>/site.tscn` and records the source directory in\r\n`staged_packages`. The composed scene\'s whole DIRECTORY is the unit -- its\r\nown comment says so, because `site.tscn` is useless without the\r\n`site_base.glb` and `art/` beside it. Whoever consumes `staged_packages` is\r\nwhere this ends, and it is one export away from being known.\r\n\r\n**BEFORE ANY OF THAT, THE ARCHETYPE IS CALLED `shell`.** Not\r\n`landmark_hall_a03`, not `cr_garage` -- `shell`. And in\r\n`resource_manifest.json`:\r\n\r\n```\r\nassets/lot.glb    sha256:a929d7d2...  242,176 bytes\r\nassets/shell.glb  sha256:a929d7d2...  242,176 bytes\r\n```\r\n\r\nThe same file twice, and that hash is the `shell.glb` the fingerprints\r\nrecord. So the lot\'s one building is the mission\'s OWN SHELL, drawn back out\r\nof `deli_counter/build` as though it were a source archetype. That directory\r\nis both the source and the sink -- the site builder already prints eleven\r\nentries it excluded for exactly this reason, and `shell` was not among them.\r\nWhether the narrower 98-shell pool now reaches the pipeline\'s own output is\r\nthe FIRST question here, because if it does, the missing `lot/shell/`\r\ndirectory is a symptom and staging it would ship the wrong thing correctly.\r\n\r\n**Two failures are possible and they want different fixes.** Either the\r\nstaging step never ran for this lot, or it ran and the export dropped what it\r\nstaged. The export\'s mode logic is the obvious suspect and is exonerated by\r\nthe A/B: `portable-godot` and `art-unlit` produce byte-identical packages\r\nhere -- 56 files, 7,158,515 bytes, zero files differing -- because Lux never\r\nran on this mission and there was nothing to subtract. Whatever drops the\r\ndirectory drops it in both.\r\n\r\n'
NEW_BLOCK = '*STATUS: OPEN 2026-08-16 -- CAUSE FOUND, and it is not what the first draft of this item said. Staging WORKS: `themed_site_assemble`\'s out dir holds `lot/shell/site.tscn` (47,460 B) with `site_base.glb` and the whole `art/` tree beside it. The EXPORT flattens that directory to the package root -- root `site_base.glb` and every `art/**` file carry byte-identical sizes AND mtimes to their `lot/shell/` originals -- while `site.tscn` still references `lot/shell/site.tscn`. And `lot/shell/site.tscn` collides on basename with the site\'s own `site.tscn`, so flattening drops the 47 KB building scene and keeps the 5,567 B site scene. 56 files ship, the entry reaches 2. IDENTICAL in `portable-godot` and `art-unlit`, which acquits `--unlit`. The archetype-pool hypothesis is REFUTED by `tools/probe_lot_own_output.py`*\n\n**49. The export flattens the composed building\'s directory, and a basename\ncollision eats the building.**\n`unlit_probe_001` exported for the first time on 2026-08-16, item 48\'s fix\nhaving removed the functional-lock refusal that had been stopping it. Both\nmodes then failed the same way:\n\n```\nEXPORT_CLOSURE_BROKEN: 0 unresolved res:// reference(s), 0 misrooted,\n                       1 unresolved relative, 0 absolute path(s)\n  site.tscn: relative ext_resource resolves to nothing: lot/shell/site.tscn (from ./)\n  resource_count: 2\n```\n\n`site.tscn` carries exactly one `ext_resource`, and it is the whole level:\n\n```\n[ext_resource type="PackedScene" path="lot/shell/site.tscn" id="b1"]\n```\n\n**Everything upstream did its job.** `_write_site_spec`\'s single-shell branch\nrecords the staging entry and names the path:\n\n```python\nif themed_scene and not themed_map:\n    staged_packages["shell"] = str(Path(themed_scene).parent)\n    source = {"scene": "lot/shell/site.tscn"}\n```\n\n`"shell"` is a hardcoded literal on that branch, NOT a library archetype id.\nIt is written to `packages.json` beside the spec, the Lot adapter plans a\nstaging command against `staging_manifest_path`, and\n`packages/staging/site_packages.py` delivers the directory. It arrived:\n\n```\nthemed_site_assemble/out/site.tscn                    5,567\nthemed_site_assemble/out/lot/shell/site.tscn         47,460\nthemed_site_assemble/out/lot/shell/site_base.glb    255,352\nthemed_site_assemble/out/lot/shell/art/zoo/*.glb     30 files\n```\n\n**The export flattened it.** In the package:\n\n```\nsite.tscn        5,567   mtime ...387527   == the SITE scene\nsite_base.glb  255,352   mtime ...382990   == lot/shell/site_base.glb\nart/zoo/*.glb            mtimes identical  == lot/shell/art/zoo/*\nlot/                     ABSENT\n```\n\nIdentical sizes and identical mtimes, one directory level up. The contents of\n`lot/shell/` were copied to the package ROOT while `site.tscn` kept\nreferencing `lot/shell/site.tscn`.\n\n**And the collision is why exactly one file is missing.**\n`lot/shell/site.tscn` and the site\'s own `site.tscn` share a basename. Flatten\nthe directory and they land on the same path. The 5,567 B site scene is what\nsurvives; the 47,460 B composed building -- the one file that references all\n30 Zoo GLBs -- does not ship at all. Its dependencies do. That is why 54 of 56\nfiles are orphans rather than absent: the export shipped the leaves and lost\nthe branch.\n\nThe namespacing directory existed precisely to keep those two `site.tscn`\napart, and removing it is what let them collide.\n\n**This is the same machinery roadmap 42 has outstanding work on** -- the\ninterior re-rooting, `lot/<building>/` -> `sites/<building>/` and dropping\n`assets/lot.glb`. `assets/lot.glb` and `assets/shell.glb` shipping at the same\nsha256 `a929d7d2...`, 242,176 bytes each, is that machinery too.\n\n**The fix is a choice, not a repair.** Either the composed package keeps its\ndirectory in the export and nothing needs rewriting, or the flatten stays and\n`site.tscn`\'s reference is rewritten to match -- with a rule for the basename\ncollision, since `site.tscn` is a name both Lot and the composer use. Doing\nneither is the current behaviour and it is the one that ships silently.\n\nWHAT THIS ITEM SAID FIRST, AND WHY IT IS WRONG\n\nThe first draft led with a different hypothesis: that the archetype is called\n`shell`, that `deli_counter/build` is both the source and the sink, and that\nthe narrowed 98-shell pool might be drawing this pipeline\'s own output back\nout as a source archetype -- in which case staging `lot/shell/` would ship the\nwrong thing correctly.\n\n`tools/probe_lot_own_output.py` was written to test exactly that, and refuted\nit. On the real library: `shell`, `site`, `site_base` and `lot` are not in it\nat all; `source_exclusion` catches the eleven it claims to (two facades, nine\n`lf_` ids) and nothing slips past. The `shell` in `lot/shell/` is a literal on\na code branch, not an id from a directory listing.\n\nIt is kept here rather than deleted because the hypothesis was reasonable, the\nevidence for it (`assets/lot.glb` and `assets/shell.glb` at one hash) was\nreal, and a reader who notices that duplicate later should find out here that\nit has already been chased. The same probe reproduced item 48\'s divergence\nfrom the library alone -- seed 5017, wide pool `cr_garage`, themed pool\n`landmark_hall_a03` -- which is independent confirmation of that item from a\ndirection the fingerprints could not reach.\n\n'

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

    o, n = _as(OLD_BLOCK, eol), _as(NEW_BLOCK, eol)
    if n in body:
        print(f"  already applied  {ROADMAP}")
        return 0
    if o not in body:
        print("REFUSING: item 49's original block is not in the file "
              "byte-for-byte. Either patch_roadmap_49.py has not run, or 49 "
              "has been edited since -- in which case this replacement would "
              "silently discard that edit.")
        return 1
    if body.count(o) != 1:
        print(f"REFUSING: item 49's block occurs {body.count(o)} times")
        return 1

    out = body.replace(o, n, 1)
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

    m49 = "**49. The export flattens the composed building's directory"
    check("item 49 has the corrected title", m49 in md)
    if m49 not in md:
        print(f"\n  {bad} FAILURE(S) -- run the patch first")
        return 1
    # SCOPED PAST THE DERIVED TABLE, deliberately. `roadmap_status.py --write`
    # runs AFTER this selftest, so the generated block still carries the old
    # title at this moment and an unscoped search would fail on a block this
    # patch does not own. The table has its own checker: `--check` exits 1 when
    # it drifts, which is the right instrument for it.
    _body_only = md.split("<!-- END GENERATED -->", 1)[-1]
    check("...and the wrong one is gone from the prose",
          "is never staged" not in _body_only)
    check("...while the derived table still shows it, pending --write",
          "is never staged" in md.split("<!-- END GENERATED -->", 1)[0]
          or "is never staged" not in md)

    i49 = md.index(m49)
    s49 = md[:i49].rstrip().splitlines()[-1]
    check("the STATUS says the cause is found",
          s49.startswith("*STATUS: OPEN 2026-08-16 -- CAUSE FOUND"))
    check("...and says staging WORKS, reversing the first claim",
          "Staging WORKS" in s49)
    check("...and names the collision as the reason ONE file is lost",
          "collides on basename" in s49)
    check("...and records the refutation and what did it",
          "REFUTED by `tools/probe_lot_own_output.py`" in s49)

    body = md[i49:md.index("**50. The package ships", i49)]
    flat = " ".join(body.split())

    check("it shows the staged tree that proves staging ran",
          "themed_site_assemble/out/lot/shell/site.tscn" in body
          and "47,460" in body)
    check("it shows the flattened package beside it",
          "mtime ...387527" in body and "mtime ...382990" in body
          and "lot/                     ABSENT" in body)
    check("it rests the flatten claim on mtimes, not on inference",
          "Identical sizes and identical mtimes" in flat)
    check("it quotes the branch that hardcodes the name",
          'staged_packages["shell"] = str(Path(themed_scene).parent)' in body
          and "hardcoded literal on that branch" in flat)
    check("it names the staging chain end to end",
          "packages.json" in body and "staging_manifest_path" in body
          and "packages/staging/site_packages.py" in body)
    check("it explains why 54 files are ORPHANS rather than absent",
          "shipped the leaves and lost the branch" in flat)
    check("it ties the flatten to roadmap 42's outstanding work",
          "roadmap 42" in body and "sites/<building>/" in body)
    check("it states the fix as a choice and names the current default",
          "The fix is a choice, not a repair" in body
          and "Doing neither is the current behaviour" in flat)

    check("the refuted hypothesis is kept, not deleted",
          "WHAT THIS ITEM SAID FIRST, AND WHY IT IS WRONG" in body)
    check("...with what refuted it and on what evidence",
          "probe_lot_own_output.py" in body
          and "two facades, nine" in flat)
    check("...and says why it is kept rather than removed",
          "should find out here" in flat)
    check("...and records the probe's independent confirmation of item 48",
          "wide pool `cr_garage`, themed pool `landmark_hall_a03`" in flat)

    check("item 50 survived the replacement",
          "**50. The package ships a resource manifest" in md)
    nums = [int(x) for x in re.findall(r"^\*\*(\d+)\. ", md, re.M)]
    check("the numbering is still contiguous through 50",
          nums[-3:] == [48, 49, 50])
    check("every fenced block in 49 is closed", body.count("```") % 2 == 0)
    check("49 still ends with a blank line before 50's status",
          body.endswith("\n\n"))
    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  the cause is named, and the wrong guess is kept where it can be read"
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
        print("    python patches\\patch_roadmap_49b.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
