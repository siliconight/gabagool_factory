r"""Roadmap 49c -- the third reading of item 49, and the first from a
hash-verified file.

    python patches\\patch_roadmap_49c.py --check
    python patches\\patch_roadmap_49c.py
    python patches\\patch_roadmap_49c.py --selftest
    python patches\\patch_roadmap_49c.py --revert

Run from the FACTORY ROOT, AFTER patch_roadmap_49.py and 49b. Then:

    python tools\\roadmap_status.py --write

THREE MECHANISMS FOR ONE DEFECT, AND WHY THAT IS THE POINT

    1st  the lot draws the pipeline's own output as a source archetype
         -> refuted by tools/probe_lot_own_output.py against the real library
    2nd  the export FLATTENS lot/shell/ and a basename collision eats it
         -> refuted by reading export_mission; the matching mtimes are two
            copy2 calls from one source, not a move
    3rd  export_mission step 2.5 (level_factory 0.37.0) overwrites the root
         site.tscn with the assembly scene and copies nothing else from that
         job, so on a SINGLE-SHELL mission a self-sufficient inlined scene is
         replaced by one naming lot/shell/, which the export never carries
         -> read out of export.py 31,675 B, sha256 5303E3D0..., stamped

The first two were written from real evidence and ahead of the code. Both are
kept in the item, named as wrong, because the item is now also a record of
how a plausible mechanism survives until somebody reads the file -- which is
this whole arc's subject, occurring in the writing of the arc.

WHAT MAKES THE THIRD DIFFERENT

It explains the mission-shape split, which neither of the others did: a
varied lot's composed root already holds `lot/<archetype>/`, so the assembly's
references have always resolved there. Only a one-building mission breaks. It
also names the release that introduced it (0.37.0, measured on five-building
lot_demo_001) and why that release was right about the problem it was fixing.

A HYPOTHESIS THAT EXPLAINS ONE CASE IS NOT DONE. A hypothesis that explains
why the OTHER case works is.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r49c"

OLD_BLOCK = '*STATUS: OPEN 2026-08-16 -- CAUSE FOUND, and it is not what the first draft of this item said. Staging WORKS: `themed_site_assemble`\'s out dir holds `lot/shell/site.tscn` (47,460 B) with `site_base.glb` and the whole `art/` tree beside it. The EXPORT flattens that directory to the package root -- root `site_base.glb` and every `art/**` file carry byte-identical sizes AND mtimes to their `lot/shell/` originals -- while `site.tscn` still references `lot/shell/site.tscn`. And `lot/shell/site.tscn` collides on basename with the site\'s own `site.tscn`, so flattening drops the 47 KB building scene and keeps the 5,567 B site scene. 56 files ship, the entry reaches 2. IDENTICAL in `portable-godot` and `art-unlit`, which acquits `--unlit`. The archetype-pool hypothesis is REFUTED by `tools/probe_lot_own_output.py`*\r\n\r\n**49. The export flattens the composed building\'s directory, and a basename\r\ncollision eats the building.**\r\n`unlit_probe_001` exported for the first time on 2026-08-16, item 48\'s fix\r\nhaving removed the functional-lock refusal that had been stopping it. Both\r\nmodes then failed the same way:\r\n\r\n```\r\nEXPORT_CLOSURE_BROKEN: 0 unresolved res:// reference(s), 0 misrooted,\r\n                       1 unresolved relative, 0 absolute path(s)\r\n  site.tscn: relative ext_resource resolves to nothing: lot/shell/site.tscn (from ./)\r\n  resource_count: 2\r\n```\r\n\r\n`site.tscn` carries exactly one `ext_resource`, and it is the whole level:\r\n\r\n```\r\n[ext_resource type="PackedScene" path="lot/shell/site.tscn" id="b1"]\r\n```\r\n\r\n**Everything upstream did its job.** `_write_site_spec`\'s single-shell branch\r\nrecords the staging entry and names the path:\r\n\r\n```python\r\nif themed_scene and not themed_map:\r\n    staged_packages["shell"] = str(Path(themed_scene).parent)\r\n    source = {"scene": "lot/shell/site.tscn"}\r\n```\r\n\r\n`"shell"` is a hardcoded literal on that branch, NOT a library archetype id.\r\nIt is written to `packages.json` beside the spec, the Lot adapter plans a\r\nstaging command against `staging_manifest_path`, and\r\n`packages/staging/site_packages.py` delivers the directory. It arrived:\r\n\r\n```\r\nthemed_site_assemble/out/site.tscn                    5,567\r\nthemed_site_assemble/out/lot/shell/site.tscn         47,460\r\nthemed_site_assemble/out/lot/shell/site_base.glb    255,352\r\nthemed_site_assemble/out/lot/shell/art/zoo/*.glb     30 files\r\n```\r\n\r\n**The export flattened it.** In the package:\r\n\r\n```\r\nsite.tscn        5,567   mtime ...387527   == the SITE scene\r\nsite_base.glb  255,352   mtime ...382990   == lot/shell/site_base.glb\r\nart/zoo/*.glb            mtimes identical  == lot/shell/art/zoo/*\r\nlot/                     ABSENT\r\n```\r\n\r\nIdentical sizes and identical mtimes, one directory level up. The contents of\r\n`lot/shell/` were copied to the package ROOT while `site.tscn` kept\r\nreferencing `lot/shell/site.tscn`.\r\n\r\n**And the collision is why exactly one file is missing.**\r\n`lot/shell/site.tscn` and the site\'s own `site.tscn` share a basename. Flatten\r\nthe directory and they land on the same path. The 5,567 B site scene is what\r\nsurvives; the 47,460 B composed building -- the one file that references all\r\n30 Zoo GLBs -- does not ship at all. Its dependencies do. That is why 54 of 56\r\nfiles are orphans rather than absent: the export shipped the leaves and lost\r\nthe branch.\r\n\r\nThe namespacing directory existed precisely to keep those two `site.tscn`\r\napart, and removing it is what let them collide.\r\n\r\n**This is the same machinery roadmap 42 has outstanding work on** -- the\r\ninterior re-rooting, `lot/<building>/` -> `sites/<building>/` and dropping\r\n`assets/lot.glb`. `assets/lot.glb` and `assets/shell.glb` shipping at the same\r\nsha256 `a929d7d2...`, 242,176 bytes each, is that machinery too.\r\n\r\n**The fix is a choice, not a repair.** Either the composed package keeps its\r\ndirectory in the export and nothing needs rewriting, or the flatten stays and\r\n`site.tscn`\'s reference is rewritten to match -- with a rule for the basename\r\ncollision, since `site.tscn` is a name both Lot and the composer use. Doing\r\nneither is the current behaviour and it is the one that ships silently.\r\n\r\nWHAT THIS ITEM SAID FIRST, AND WHY IT IS WRONG\r\n\r\nThe first draft led with a different hypothesis: that the archetype is called\r\n`shell`, that `deli_counter/build` is both the source and the sink, and that\r\nthe narrowed 98-shell pool might be drawing this pipeline\'s own output back\r\nout as a source archetype -- in which case staging `lot/shell/` would ship the\r\nwrong thing correctly.\r\n\r\n`tools/probe_lot_own_output.py` was written to test exactly that, and refuted\r\nit. On the real library: `shell`, `site`, `site_base` and `lot` are not in it\r\nat all; `source_exclusion` catches the eleven it claims to (two facades, nine\r\n`lf_` ids) and nothing slips past. The `shell` in `lot/shell/` is a literal on\r\na code branch, not an id from a directory listing.\r\n\r\nIt is kept here rather than deleted because the hypothesis was reasonable, the\r\nevidence for it (`assets/lot.glb` and `assets/shell.glb` at one hash) was\r\nreal, and a reader who notices that duplicate later should find out here that\r\nit has already been chased. The same probe reproduced item 48\'s divergence\r\nfrom the library alone -- seed 5017, wide pool `cr_garage`, themed pool\r\n`landmark_hall_a03` -- which is independent confirmation of that item from a\r\ndirection the fingerprints could not reach.\r\n\r\n'
NEW_BLOCK = '*STATUS: OPEN 2026-08-16 -- CAUSE FOUND, third reading, this one against a hash-verified file (`export.py` 31,675 B, sha256 5303E3D0...). `export_mission` step 2.5, added in level_factory 0.37.0, copies `themed_site_assemble/out/site.tscn` over the package root and copies NOTHING ELSE from that job. For a SINGLE-SHELL mission that overwrites the composer\'s inlined, self-sufficient building with an assembly scene whose one `ext_resource` is `lot/shell/site.tscn` -- a directory `site_packages.py` built in the job\'s out dir and the export never carries. A VARIED lot is unaffected: the composer writes `lot/<archetype>/` inside `composed_root`, so `_copy_tree` brings it. 0.37.0 was measured on five-building lot_demo_001, which is why nothing caught it. IDENTICAL in `portable-godot` and `art-unlit`, which acquits `--unlit`*\n\n**49. Step 2.5 replaces a self-contained root scene with one that names a\ndirectory the export never carries -- on single-shell missions only.**\n`unlit_probe_001` exported for the first time on 2026-08-16, item 48\'s fix\nhaving removed the functional-lock refusal that had been stopping it. Both\nmodes then failed the same way:\n\n```\nEXPORT_CLOSURE_BROKEN: 0 unresolved res:// reference(s), 0 misrooted,\n                       1 unresolved relative, 0 absolute path(s)\n  site.tscn: relative ext_resource resolves to nothing: lot/shell/site.tscn (from ./)\n  resource_count: 2\n```\n\nTHE CHAIN, EVERY LINK VERIFIED\n\n`_write_site_spec`\'s single-shell branch names the path and records the\nsource. `"shell"` is a hardcoded literal on that branch, NOT a library id:\n\n```python\nif themed_scene and not themed_map:\n    staged_packages["shell"] = str(Path(themed_scene).parent)\n    source = {"scene": "lot/shell/site.tscn"}\n```\n\nThat goes to `packages.json`, the Lot adapter plans a staging command against\n`staging_manifest_path`, and `packages/staging/site_packages.py` delivers.\nIt arrived -- this is on disk:\n\n```\nthemed_site_assemble/out/site.tscn                    5,567   the assembly\nthemed_site_assemble/out/lot/shell/site.tscn         47,460   the building\nthemed_site_assemble/out/lot/shell/site_base.glb    255,352\nthemed_site_assemble/out/lot/shell/art/zoo/*.glb     30 files\n```\n\nThen `export_mission` takes exactly one file out of that directory:\n\n```python\n# 2.5 THE ASSEMBLY SCENE\nif profile.mode != MODE_PURE_SHELL and themed_site_dir:\n    themed_scene = Path(themed_site_dir) / "site.tscn"\n    if themed_scene.is_file():\n        shutil.copy2(str(themed_scene), str(export_dir / "site.tscn"))\n```\n\nOne file. Not the `lot/` tree beside it that the file references.\n\nWHY ONLY SINGLE-SHELL MISSIONS\n\nStep 2 copies `composed_root` to the export ROOT. What is in a composed root\ndepends on how many buildings the mission has, and `export.py`\'s own comment\nstates both shapes:\n\n```\nA single-shell compose INLINES its geometry and its presentation scene DOES\nname `res://site.tscn`. A themed multi-building site instances five packages\nand names `res://lot/<archetype>/site.tscn` instead -- measured on\nlot_demo_001: five such refs, no `res://site.tscn`.\n```\n\nSo a varied lot\'s composed root already contains `lot/<archetype>/`, and\n`_copy_tree` carries it; the assembly\'s references resolve and always have.\nA single-shell composed root contains `site.tscn`, `site_base.glb` and `art/`\nat its TOP LEVEL -- which is why those files appear at the package root with\nmtimes matching `lot/shell/`\'s copies. They are not that directory flattened.\nThey are the same composer output, copied twice from one source by two\ndifferent steps, and `copy2` preserves mtimes.\n\n**0.37.0 introduced it, and 0.37.0 was right about the problem it fixed.**\nBefore step 2.5 the single-shell root `site.tscn` was the composer\'s inlined\nbuilding, which resolved against the `site_base.glb` and `art/` beside it and\nclosed. Step 2.5 exists because on lot_demo_001 the assembly scene reached no\npackage at all and an unlit export opened to nothing. It fixed that, on a\nfive-building mission, where the assembly\'s references were already present.\nOn a one-building mission the same copy replaces a scene that resolves with a\nscene that cannot.\n\n**THE FIX, AND IT IS A CHOICE.** Step 2.5 must carry what it names -- copy\n`themed_site_dir`\'s `lot/` subtree alongside the scene -- or the single-shell\nspec must stop routing through `lot/shell/` and reference the root directly,\nor step 2.5 must not fire when the composed root is the inlined single-shell\nshape. The first is the smallest and keeps one rule for both mission shapes.\nThe last restores the pre-0.37.0 behaviour and re-opens what 0.37.0 closed.\nDoing none of them is the current behaviour, and it ships.\n\n**And nothing tests the one-building themed export.** Every measurement in\nroadmap 47\'s stages 1-3a was taken on lot_demo_001, five buildings; 3b used\none building precisely because the point was the layer set rather than the\nscale. That choice is what surfaced this, and a fixture at each shape is what\nwould have caught it before an export did.\n\nWHAT THIS ITEM SAID FIRST, AND SECOND, AND WHY BOTH WERE WRONG\n\n**First:** that the archetype was called `shell` because the lot was drawing\nthis pipeline\'s own output back out of `deli_counter/build` as a source.\n`tools/probe_lot_own_output.py` was written to test it and refuted it: on the\nreal library `shell`, `site`, `site_base` and `lot` are not in it at all, and\n`source_exclusion` catches the eleven it claims to (two facades, nine `lf_`\nids) with nothing slipping past. The `shell` in `lot/shell/` is a literal on a\ncode branch. The evidence that suggested otherwise -- `assets/lot.glb` and\n`assets/shell.glb` shipping at one sha256, `a929d7d2...`, 242,176 bytes each\n-- is real and is roadmap 42\'s outstanding `assets/lot.glb` work, not this.\n\n**Second:** that the export FLATTENED `lot/shell/` to the root, and that a\nbasename collision between `lot/shell/site.tscn` and the site\'s own\n`site.tscn` ate the building. That was inferred from matching mtimes and it\nis wrong: nothing flattens that directory, and the matching mtimes are two\n`copy2` calls from one source. The collision is real but it is not a\ncollision -- step 2.5 overwrites deliberately, and `export.py`\'s comment says\nso in as many words.\n\nBoth were written from evidence and ahead of the code. The same probe that\nkilled the first one also reproduced item 48\'s divergence from the library\nalone -- seed 5017, wide pool `cr_garage`, themed pool `landmark_hall_a03` --\nso it earned its keep twice. The second was killed by reading\n`export_mission` out of a file stamped with its own byte count and sha256,\nwhich is now the rule for this item: a mechanism claim here cites a verified\nread or it does not go in.\n\n'

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
    if body.count(o) != 1:
        print(f"REFUSING: item 49's 49b block occurs {body.count(o)} time(s), "
              f"expected 1. Either 49b has not run, or 49 has been edited "
              f"since -- and a whole-block replacement would discard it.")
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

    m49 = "**49. Step 2.5 replaces a self-contained root scene"
    check("item 49 has the third title", m49 in md)
    if m49 not in md:
        print(f"\n  {bad} FAILURE(S) -- run the patch first")
        return 1

    # SCOPED PAST THE DERIVED TABLE: roadmap_status.py --write runs after this
    # selftest, so the generated block still carries the previous title.
    prose = md.split("<!-- END GENERATED -->", 1)[-1]
    check("...and neither earlier title survives in the prose",
          "is never staged" not in prose
          and "The export flattens the composed building" not in prose)

    i49 = md.index(m49)
    s49 = md[:i49].rstrip().splitlines()[-1]
    check("the STATUS cites a hash-verified read",
          "sha256 5303E3D0" in s49 and "31,675 B" in s49)
    check("...names step 2.5 and the release that added it",
          "step 2.5" in s49 and "0.37.0" in s49)
    check("...and states the mission-shape split",
          "SINGLE-SHELL" in s49 and "VARIED lot is unaffected" in s49)
    check("...and still acquits --unlit",
          "acquits `--unlit`" in s49)

    body = md[i49:md.index("**50. The package ships", i49)]
    flat = " ".join(body.split())

    check("it quotes the spec branch that names the path",
          'staged_packages["shell"] = str(Path(themed_scene).parent)' in body)
    check("it shows the staged tree that proves staging ran",
          "themed_site_assemble/out/lot/shell/site.tscn" in body
          and "47,460" in body)
    check("it quotes step 2.5 itself",
          'themed_scene = Path(themed_site_dir) / "site.tscn"' in body
          and "One file. Not the `lot/` tree beside it" in flat)
    check("it explains why a VARIED lot is fine",
          "already contains `lot/<archetype>/`" in flat
          and "always have" in flat)
    check("it retracts the flatten story with the mtime explanation",
          "copied twice from one source" in flat
          and "`copy2` preserves mtimes" in flat)
    check("it credits 0.37.0 rather than only blaming it",
          "0.37.0 was right about the problem it fixed" in flat)
    check("it gives three fixes and names the one that ships today",
          "THE FIX, AND IT IS A CHOICE" in body
          and "Doing none of them is the current behaviour" in flat)
    check("it names the missing test coverage",
          "nothing tests the one-building themed export" in flat)

    check("both earlier mechanisms are kept and named wrong",
          "WHAT THIS ITEM SAID FIRST, AND SECOND, AND WHY BOTH WERE WRONG"
          in body and "**First:**" in body and "**Second:**" in body)
    # PRECEDENCE. This was written `A and B or C` with C = `"reading" in flat`,
    # which is true of any prose containing the word -- so the check could not
    # fail. `and` binds tighter than `or`; the fallback swallowed the test.
    # Caught by reading the checks, which is the only thing that catches it.
    # BOTH CONJUNCTIONS, no `or` fallback. The first draft of these two was
    # `A and B or C` with C = `"reading" in flat`, true of any prose containing
    # the word, so the check could not fail. `and` binds tighter than `or` and
    # the fallback swallowed the test -- the same shape as every defect this
    # arc has been about, in a check written to guard against it.
    check("...with what refuted the first",
          "refuted it" in flat and "probe_lot_own_output.py" in body)
    check("...and what refuted the second",
          "export_mission" in body
          and "two `copy2` calls from one source" in flat)
    check("...and the rule it adopts for itself",
          "cites a verified read or it does not go in" in flat)
    check("...and the probe's independent confirmation of item 48 survives",
          "wide pool `cr_garage`, themed pool `landmark_hall_a03`" in flat)
    check("the duplicate-hash evidence is redirected to roadmap 42",
          "roadmap 42's outstanding `assets/lot.glb` work" in flat)

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
    print("  third reading, first verified one -- and the two wrong ones kept"
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
        print("    python patches\\patch_roadmap_49c.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
