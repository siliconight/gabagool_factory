r"""The closure-scan question, answered -- and the answer is that it is sound.

    python patches\\patch_roadmap_scan_answered.py --check
    python patches\\patch_roadmap_scan_answered.py
    python patches\\patch_roadmap_scan_answered.py --selftest
    python tools\\roadmap_status.py --write

ONE EDIT: the carried note added by patch_roadmap_49d.py is replaced with the
answer, read out of `closure.py` (12,146 B, sha256 1467E73D...).

WHAT THE ANSWER IS

`scan_closure` globs every file with a scanned suffix and reads it; it does
not walk a graph from the entry. So the 34 `res://` references inside
`lot/shell/site.tscn` WERE each checked against a `present` set built from
`rglob("*")` over the whole package. `resource_count` is a count of scene and
script FILES, not of resources reached. The green tick means what it says.

WHY THE NOTE IS REPLACED RATHER THAN DELETED

Two things in it are worth keeping. The obvious test does not work, and
somebody will try it again in six months. And the scan has been wrong about
this exact class before -- its own comment records a suffix-matching line that
certified lot_demo_001 while five building scenes each dangled 33 references.
That is roadmap 49's defect one layer up.

WHAT IS NOT DONE HERE

factory-v1.25.0's description says this was UNMEASURED. That was true when it
was certified and the tag is pushed. It stays. The next certification can say
it was measured; a shipped record does not get edited to look better than it
was, which is the same rule that kept two wrong mechanisms inside item 49.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_scanans"

OLD = '**The export closure scan may not read the scenes it counts.** After roadmap\n49 closed, `lot/shell/site.tscn` in the shipped package carries 34\n`res://lot/shell/...` references -- `site_base.glb` and 31 art GLBs -- and the\nscan reports `resource_count: 3`, `relative_reference_count: 1`,\n`absolute_path_count: 0` and `missing_resource_count: 0`. Those 34 appear in\nnone of its numbers. Either it resolved them and does not count them, or it\nnever read them and the zero is a pass over files it did not check. The\nprecedent points the wrong way: 0.37.0 recorded `resource_count: 6` for a\n180-file five-building package, which is the count of SCENES in the chain and\nnothing else. Not settled by the obvious test -- renaming a GLB inside the\nexport directory and re-exporting proves nothing, because `export_mission`\ndoes `shutil.rmtree(export_dir)` and rebuilds from source before scanning, so\nthe file is back before the scan runs. It wants the scan run against a\nmutated COPY of a finished package. If the blind spot is real, the guard that\ncaught item 49 cannot see one level below where it looked.\n\n'
NEW = '**The export closure scan reads what it counts -- asked, and answered.**\nRaised on 2026-08-16 because `lot/shell/site.tscn` carries 34\n`res://lot/shell/...` references while the scan reported `resource_count: 3`\nand `missing_resource_count: 0`, and those 34 appeared in none of its\nnumbers. Read out of `closure.py` (12,146 B, sha256 1467E73D...): the scan\ndoes NOT walk a reference graph from the entry. It globs every file whose\nsuffix is in `_SCANNED_SUFFIXES`, reads each one\'s text, and checks every\n`res://` it finds against `present` -- a set built from `rglob("*")` over the\nwhole package, GLBs included. So `lot/shell/site.tscn` was opened and all 34\nwere checked. `resource_count` is a count of scene and script FILES present,\nnot of resources reached; 3 is `mission.tscn`, `site.tscn` and\n`lot/shell/site.tscn`. `ok: true` does mean the art resolves.\n\nRecorded rather than deleted for two reasons. The obvious test does NOT work\n-- renaming a GLB inside the export directory and re-exporting proves\nnothing, because `export_mission` does `shutil.rmtree(export_dir)` and\nrebuilds from source before scanning, so the file is back before anybody\nlooks; that was tried on 2026-08-16 and the rename-back failed because the\nrebuild had already replaced it. And the scan has been wrong about precisely\nthis before: its own comment records `any(pr.endswith(rel) for pr in\npresent)` certifying lot_demo_001 at `ok: true, 0 missing` while five\nbuilding scenes each dangled 33 references, "floors and a staircase in an\nempty sky". That is roadmap 49\'s defect one layer up, which is why\n`misrooted_resource_count` is a separate counter and why it reading 0 is\nworth as much as the missing count reading 0.\n\nfactory-v1.25.0\'s description says this was UNMEASURED. It was, at the moment\nthat set was certified. It is measured now, and the next certification can\nsay so; a pushed tag does not get rewritten to look better than it was.\n\n'

_CRLF = "\r\n"


def _sha(d: bytes) -> str:
    return hashlib.sha256(d).hexdigest()


def _eol(b: str) -> str:
    c = b.count(_CRLF)
    return _CRLF if c > (b.count("\n") - c) else "\n"


def _as(t: str, eol: str) -> str:
    return t.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    p = root / ROADMAP
    if not p.is_file():
        print(f"REFUSING: {ROADMAP} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)
    o, n = _as(OLD, eol), _as(NEW, eol)
    if n in body:
        print(f"  already applied  {ROADMAP}")
        return 0
    if body.count(o) != 1:
        print(f"REFUSING: the carried note occurs {body.count(o)} time(s), "
              f"expected 1 -- run patch_roadmap_49d.py first, or it has been "
              f"edited since")
        return 1
    data = body.replace(o, n, 1).encode("utf-8")
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
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    md = (root / ROADMAP).read_bytes().decode("utf-8").replace(_CRLF, "\n")
    head = "**The export closure scan reads what it counts -- asked, and answered.**"
    check("the answer is in the file", head in md)
    if head not in md:
        print(f"\n  {bad} FAILURE(S)")
        return 1
    seg = md[md.index(head):]
    seg = seg[:seg.index("**`probe_unlit_ab.py`")]
    flat = " ".join(seg.split())

    check("the open question is gone",
          "may not read the scenes it counts" not in md)
    check("it cites the file it was read from, with a hash",
          "12,146 B, sha256 1467E73D" in seg)
    check("it says HOW the scan works, not just that it is fine",
          "globs every file whose suffix is in `_SCANNED_SUFFIXES`" in flat
          and "does NOT walk a reference graph from the entry" in flat)
    check("...and that `present` covers GLBs too",
          'rglob("*")` over the whole package, GLBs included' in flat)
    check("...and what resource_count actually counts",
          "count of scene and script FILES present, not of resources reached"
          in flat)
    check("it states the conclusion plainly",
          "`ok: true` does mean the art resolves." in flat)
    check("it keeps why the obvious test fails",
          "shutil.rmtree(export_dir)" in seg
          and "the rename-back failed because the rebuild had already "
              "replaced it" in flat)
    check("it keeps the precedent where this scan WAS wrong",
          "floors and a staircase in an empty sky" in flat
          and "misrooted_resource_count" in seg)
    check("it refuses to rewrite the shipped certification",
          "a pushed tag does not get rewritten to look better than it was"
          in flat)

    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  asked, answered, and the reason it was worth asking kept"
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
        print("    python patches\\patch_roadmap_scan_answered.py --selftest")
        print("    python tools\\roadmap_status.py --write")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
