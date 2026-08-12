r"""Name the FILE in a closure issue, not just its basename.

    python patch_lf_closure_issue_paths.py --check
    python patch_lf_closure_issue_paths.py
    python patch_lf_closure_issue_paths.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

Every issue `scan_closure` reports is labelled with `f.name`. A composed export
holds SIX files called `site.tscn` -- one at the root and one per building
under `lot/<archetype>/` -- so the line

    site.tscn: unresolved res://art/zoo/wall_rockay_01_w200.glb

names five possible files and identifies none of them. That is the same
ambiguity that produced four of this session's wrong calls, appearing inside
the instrument built to diagnose it.

It mattered less while the verdict was a warning nobody had to act on. With
`CLOSURE_ENFORCED` now True these strings ARE the exception body, so a report
of 132 issues across five identically-named scenes is what somebody reads at
the moment the build stops.

Every issue now carries the package-relative path:

    lot/supermarket_a01/site.tscn: MISROOTED res://art/zoo/wall_rockay_01_w200.glb
        -> present at lot/supermarket_a01/art/zoo/wall_rockay_01_w200.glb

`f.name` is KEPT where it is correct: `_METADATA_FILES` is a set of basenames
and matching it against a relative path would silently stop excluding
everything in it.

Strings only. No counter, no verdict and no control flow changes.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("level_factory/packages/exporting/closure.py")
SIDECAR = ".pre_issuepaths"


#: (anchor, replacement). Each is unique in the file; `_apply` refuses if not.
PAIRS = (
    # Bind the relative path once, right where the text is read.
    ('''        text = f.read_text(encoding="utf-8", errors="replace")''',
     '''        text = f.read_text(encoding="utf-8", errors="replace")
        # The label every issue below carries. NOT `f.name`: a composed export
        # holds six files called `site.tscn` and a basename names all of them.
        # `f.name` stays correct for the _METADATA_FILES tests, which match a
        # set of basenames.
        rel_f = f.relative_to(mission_root).as_posix()'''),

    ('''            result.issues.append(f"{f.name}: absolute path {m.group(0)[:60]}")''',
     '''            result.issues.append(f"{rel_f}: absolute path {m.group(0)[:60]}")'''),

    ('''            result.issues.append(f"{f.name}: user:// reference is not portable")''',
     '''            result.issues.append(
                f"{rel_f}: user:// reference is not portable")'''),

    ('''                    result.issues.append(f"{f.name}: unresolved res://{rel}")''',
     '''                    result.issues.append(
                        f"{rel_f}: unresolved res://{rel}")'''),

    ('''                        f"{f.name}: MISROOTED res://{rel} -> present at "''',
     '''                        f"{rel_f}: MISROOTED res://{rel} -> present at "'''),

    ('''                        f"{f.name}: relative ext_resource leaves the package: "''',
     '''                        f"{rel_f}: relative ext_resource leaves the package: "'''),

    ('''                        f"{f.name}: relative ext_resource resolves to nothing: "''',
     '''                        f"{rel_f}: relative ext_resource resolves to nothing: "'''),

    ('''                            f"{f.name}: authoring-repo path reference '{marker}'")''',
     '''                            f"{rel_f}: authoring-repo path reference "
                            f"'{marker}'")'''),
)

EDITS = {TARGET: PAIRS}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _find(body: str, anchor: str):
    candidate = _as(anchor, _eol(body))
    return candidate, body.count(candidate)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)
    eol = _eol(body)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    try:
        compile(out, str(path), "exec")
    except SyntaxError as exc:
        print(f"REFUSING: {path.name} -- the patched file does not parse: "
              f"{exc}")
        return 1
    # Nothing may still label an issue by basename.
    leftover = [ln.strip() for ln in out.splitlines()
                if "{f.name}" in ln and "issues" not in ln]
    stragglers = [ln for ln in out.splitlines() if '{f.name}:' in ln]
    if stragglers:
        print(f"REFUSING: {path.name} -- {len(stragglers)} issue label(s) still "
              f"use f.name:")
        for ln in stragglers[:5]:
            print(f"    {ln.strip()}")
        return 1
    del leftover
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
