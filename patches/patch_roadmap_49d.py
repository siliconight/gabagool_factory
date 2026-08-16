r"""Roadmap 49 CLOSED, and the closure scan's coverage carried.

    python patches\\patch_roadmap_49d.py --check
    python patches\\patch_roadmap_49d.py
    python patches\\patch_roadmap_49d.py --selftest
    python tools\\roadmap_status.py --write

TWO EDITS

1. Item 49's STATUS: OPEN -> CLOSED. Fixed as level_factory 0.39.0 and proven
   by re-exporting from the cached 3b workspace -- `ok: false` with the entry
   reaching 2 of 56 files, then `ok: true` with `issues: []` in BOTH modes.
2. A new carried note: the closure scan reports `missing_resource_count: 0`
   while the scene it just counted carries 34 `res://` references that appear
   in none of its numbers.

WHY 2 IS A NOTE AND NOT AN ITEM

Because it is not yet measured. The obvious test does not work -- renaming a
GLB inside the export directory and re-exporting proves nothing, since
`export_mission` rmtree's the directory and rebuilds from source before the
scan runs, so the file is back before anybody looks. That was tried; it is
recorded so nobody tries it twice. A real test runs the scan against a
mutated COPY of a finished package, and that needs `closure.py`'s API rather
than a guess at it.

Writing it down as an open question rather than as a finding is the honest
shape for something nobody has measured, which is what the ANALYSIS
vocabulary elsewhere in this file exists for.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r49d"

OLD_STATUS = "*STATUS: OPEN 2026-08-16 -- CAUSE FOUND, third reading, this one against a hash-verified file (`export.py` 31,675 B, sha256 5303E3D0...). `export_mission` step 2.5, added in level_factory 0.37.0, copies `themed_site_assemble/out/site.tscn` over the package root and copies NOTHING ELSE from that job. For a SINGLE-SHELL mission that overwrites the composer's inlined, self-sufficient building with an assembly scene whose one `ext_resource` is `lot/shell/site.tscn` -- a directory `site_packages.py` built in the job's out dir and the export never carries. A VARIED lot is unaffected: the composer writes `lot/<archetype>/` inside `composed_root`, so `_copy_tree` brings it. 0.37.0 was measured on five-building lot_demo_001, which is why nothing caught it. IDENTICAL in `portable-godot` and `art-unlit`, which acquits `--unlit`*"
NEW_STATUS = "*STATUS: CLOSED 2026-08-16 -- FIXED as level_factory 0.39.0 and proven on the package. `_assembly_building_dir` reads the assembly scene and returns `lot/<id>` when it names exactly one such package AND the composed root has no `lot/` of its own; the composed root is copied THERE instead of to the package root, and the composer's own `site.tscn` stops being skipped because under `lot/<id>/` it IS the building. A varied lot hits neither condition and is untouched. Re-exported from the cached 3b workspace: BEFORE `ok: false`, `site.tscn: relative ext_resource resolves to nothing: lot/shell/site.tscn`, entry reaching 2 of 56 files; AFTER `ok: true`, `issues: []`, `unresolved_relative_count: 0`, in BOTH `portable-godot` and `art-unlit`, with `lot/shell/site.tscn` 48,004 B and its 31 GLBs beside it and NO duplicate copy at the root. The export also reached artifacts it had never written before -- `project.godot`, `LF_MANIFEST.json`, `export_profile.json`, `output_layers.json`, `portable_resource_manifest.json` -- because it had never got past the closure gate on this mission. tests/unit green. CAUSE, from a hash-verified read (`export.py` 31,675 B, sha256 5303E3D0...): `export_mission` step 2.5, added in 0.37.0, copied the assembly scene over the package root and nothing else from that job, so on a SINGLE-SHELL mission a self-sufficient inlined scene was replaced by one naming `lot/<id>/`. 0.37.0 was measured on five-building lot_demo_001, which is why nothing caught it. `--unlit` acquitted: both modes failed and both now pass*"
SMALLER = '**The export closure scan may not read the scenes it counts.** After roadmap\n49 closed, `lot/shell/site.tscn` in the shipped package carries 34\n`res://lot/shell/...` references -- `site_base.glb` and 31 art GLBs -- and the\nscan reports `resource_count: 3`, `relative_reference_count: 1`,\n`absolute_path_count: 0` and `missing_resource_count: 0`. Those 34 appear in\nnone of its numbers. Either it resolved them and does not count them, or it\nnever read them and the zero is a pass over files it did not check. The\nprecedent points the wrong way: 0.37.0 recorded `resource_count: 6` for a\n180-file five-building package, which is the count of SCENES in the chain and\nnothing else. Not settled by the obvious test -- renaming a GLB inside the\nexport directory and re-exporting proves nothing, because `export_mission`\ndoes `shutil.rmtree(export_dir)` and rebuilds from source before scanning, so\nthe file is back before the scan runs. It wants the scan run against a\nmutated COPY of a finished package. If the blind spot is real, the guard that\ncaught item 49 cannot see one level below where it looked.\n\n'
ANCHOR_SMALL = "### Smaller, carried\n\n**`probe_unlit_ab.py`'s manifest section reads nothing"

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(body: str) -> str:
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

    out = body
    already = 0

    o, n = _as(OLD_STATUS, eol), _as(NEW_STATUS, eol)
    if n in out:
        already += 1
    elif out.count(o) == 1:
        out = out.replace(o, n, 1)
    else:
        print(f"REFUSING: item 49's OPEN status occurs {out.count(o)} time(s), "
              f"expected 1 -- run patch_roadmap_49c.py first")
        return 1

    a = _as(ANCHOR_SMALL, eol)
    if _as("**The export closure scan may not read the scenes it counts.**",
           eol) in out:
        already += 1
    elif out.count(a) == 1:
        out = out.replace(
            a, _as("### Smaller, carried\n\n" + SMALLER
                   + "**`probe_unlit_ab.py`'s manifest section reads nothing",
                   eol), 1)
    else:
        print(f"REFUSING: the 'Smaller, carried' anchor occurs {out.count(a)} "
              f"time(s), expected 1")
        return 1

    if already == 2:
        print(f"  already applied  {ROADMAP}")
        return 0
    if already:
        print("REFUSING: one of two edits is already present -- part-patched")
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

    m49 = "**49. Step 2.5 replaces a self-contained root scene"
    check("item 49 is there", m49 in md)
    if m49 not in md:
        print(f"\n  {bad} FAILURE(S) -- run patch_roadmap_49c.py first")
        return 1
    s49 = md[:md.index(m49)].rstrip().splitlines()[-1]

    check("item 49 is CLOSED", s49.startswith("*STATUS: CLOSED 2026-08-16"))
    check("...naming the release that fixed it",
          "level_factory 0.39.0" in s49)
    check("...and the BEFORE measurement",
          "entry reaching 2 of 56 files" in s49
          and "resolves to nothing: lot/shell/site.tscn" in s49)
    check("...and the AFTER measurement, in both modes",
          "`ok: true`" in s49 and "`unresolved_relative_count: 0`" in s49
          and "BOTH `portable-godot` and `art-unlit`" in s49)
    check("...and that nothing duplicated at the root",
          "NO duplicate copy" in s49)
    # STRICT CONJUNCTION on the flattened line. Written first as
    # `A and B or C`, where B tested for a newline inside a line that has
    # none -- so B was always False and the whole check collapsed to C,
    # quietly dropping the LF_MANIFEST.json requirement. Second time tonight
    # for this exact precedence mistake, which is why it is written down here
    # rather than just fixed.
    _s = " ".join(s49.split())
    check("...and the artifacts the export had never reached",
          "LF_MANIFEST.json" in _s
          and "never got past the closure gate" in _s)
    check("...and still cites the hash-verified read for the cause",
          "sha256 5303E3D0" in s49)
    check("...and acquits --unlit on the strongest evidence: both, then both",
          "both modes failed and both now pass" in s49)

    check("the closure-scan question is carried",
          "**The export closure scan may not read the scenes it counts.**"
          in md)
    small = md[md.index("**The export closure scan may not read"):]
    small = small[:small.index("**`probe_unlit_ab.py`")]
    sflat = " ".join(small.split())
    check("...with the numbers that raise it",
          "`resource_count: 3`" in small and "34" in small
          and "`missing_resource_count: 0`" in small)
    check("...and both readings left open, not one asserted",
          "Either it resolved them and does not count them, or it never read"
          in sflat)
    check("...and the precedent that points one way",
          "`resource_count: 6` for a 180-file" in sflat)
    check("...and why the obvious test does not work",
          "shutil.rmtree(export_dir)" in small
          and "the file is back before the scan runs" in sflat)
    check("...and what a real test would be",
          "mutated COPY of a finished package" in sflat)

    nums = [int(x) for x in re.findall(r"^\*\*(\d+)\. ", md, re.M)]
    check("the numbering is untouched", nums[-3:] == [48, 49, 50])
    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  49 closed on a measurement, and the next question written down"
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
        print("    python patches\\patch_roadmap_49d.py --selftest")
        print("    python tools\\roadmap_status.py --write")
        print("    python tools\\roadmap_status.py --check")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
