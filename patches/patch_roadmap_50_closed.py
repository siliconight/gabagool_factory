r"""Roadmap item 50 CLOSED -- fixed as level_factory 0.40.0 and confirmed.

    python patches\\patch_roadmap_50_closed.py --check
    python patches\\patch_roadmap_50_closed.py
    python patches\\patch_roadmap_50_closed.py --selftest
    python tools\\roadmap_status.py --write

ONE EDIT: item 50's STATUS line.

WHY IT MATTERS THAT THIS RUNS

The item is fixed, shipped and tagged, and the roadmap still says OPEN. A
record that misstates the state of the thing it records is the defect this
whole file is about, and leaving it one item wrong overnight is how a reader
tomorrow re-investigates something already done.

THE STATUS ALSO CORRECTS THE FINDING, not just its state. Item 50 was written
as "the package ships a manifest that describes a different package". It ships
TWO, and the correct one was already there -- `portable_resource_manifest.json`,
58 resources, written at export time. The defect was that the stale one had
the better name.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_r50c"
OLD = '*STATUS: OPEN 2026-08-16 -- MEASURED on the same package. `resource_manifest.json` says `mission.tscn` is 16,246 bytes; the file beside it is 688. Written by Dispatch at `...388494` and overwritten by LF at `...389514`, one second later, with no rewrite of the manifest. It also lists 14 files where the package holds 56 -- no `site.tscn`, no `site_base.glb`, none of the 30 `art/` GLBs*'
NEW = "*STATUS: CLOSED 2026-08-16 -- FIXED as level_factory 0.40.0 and confirmed on the package. The finding was not one stale manifest but TWO manifests: Dispatch's `resource_manifest.json` (`dispatch.resource_manifest.v0.2`, 17 entries, recording `mission.tscn` at 16,246 bytes beside a 688-byte file, written at `...388494` and overwritten by LF at `...389514`) and LF's own `portable_resource_manifest.json` (`level_factory.portable_manifest.v0.1`, 58 resources with sha256 and size each, including `lot/shell/site.tscn` and all 31 art/zoo GLBs, written at export time and CORRECT). The stale one had the better name, so it is the one a recipient opens. FIX: `resource_manifest.json` joins the `skip` set the handoff copy already uses -- dropped rather than regenerated, following the composed-root copy twelve lines below which already skips `portable_resource_manifest.json` because the composer writes one and LF writes its own. If a recipient contract ever needs that name, REGENERATE it there rather than un-skip it; the problem was never the file, it was the file being stale. CONFIRMED by re-export: no `resource_manifest.json` in the package, `portable_resource_manifest.json` 10,651 -> 10,485 B (one fewer file to describe), and the closure scan byte-for-byte unchanged -- `ok: true`, `issues: []`, `resource_count: 3`, every counter identical. `_METADATA_FILES` meant the scan never read either manifest for references, so nothing was depending on it*"
_CRLF = "\r\n"


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
    b = raw.decode("utf-8")
    eol = _eol(b)
    o, n = _as(OLD, eol), _as(NEW, eol)
    if n in b:
        print(f"  already applied  {ROADMAP}")
        return 0
    if b.count(o) != 1:
        print(f"REFUSING: item 50's OPEN status occurs {b.count(o)} time(s), "
              f"expected 1")
        return 1
    data = b.replace(o, n, 1).encode("utf-8")
    if check:
        print(f"  would patch  {ROADMAP}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 "
          f"{hashlib.sha256(data).hexdigest()[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    md = (root / ROADMAP).read_bytes().decode("utf-8").replace(_CRLF, "\n")
    m = "**50. The package ships a resource manifest"
    check("item 50 is there", m in md)
    if m not in md:
        print(f"\n  {bad} FAILURE(S)")
        return 1
    s = " ".join(md[:md.index(m)].rstrip().splitlines()[-1].split())
    check("item 50 is CLOSED", s.startswith("*STATUS: CLOSED 2026-08-16"))
    check("...naming the release", "level_factory 0.40.0" in s)
    check("...correcting the finding to TWO manifests",
          "not one stale manifest but TWO manifests" in s)
    check("...with both schemas and both counts",
          "dispatch.resource_manifest.v0.2" in s
          and "level_factory.portable_manifest.v0.1" in s
          and "17 entries" in s and "58 resources" in s)
    check("...and the sentence that is the actual defect",
          "The stale one had the better name" in s)
    check("...and the fix, with its precedent",
          "joins the `skip` set" in s
          and "already skips `portable_resource_manifest.json`" in s)
    check("...and what to do if a contract needs the name",
          "REGENERATE it there rather than un-skip it" in s)
    check("...and the CONFIRMATION, with the number that moved",
          "10,651 -> 10,485 B" in s and "one fewer file to describe" in s)
    check("...and the number that did NOT move",
          "closure scan byte-for-byte unchanged" in s
          and "every counter identical" in s)
    check("...and why nothing depended on it",
          "_METADATA_FILES" in s and "nothing was depending on it" in s)
    check("the old OPEN text is gone",
          "no `site_base.glb`, none of the 30" not in md)
    check("the derived table is left to roadmap_status.py",
          (root / "tools" / "roadmap_status.py").is_file())

    print()
    print("  every item this arc opened is now closed on a measurement"
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
        print("    python patches\\patch_roadmap_50_closed.py --selftest")
        print("    python tools\\roadmap_status.py --write")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
