r"""Read the freshness rule from the tool that owns it, do not restate it.

    python patch_lf_freshness_sources.py --check
    python patch_lf_freshness_sources.py
    python patch_lf_freshness_sources.py --revert
    python patch_lf_freshness_sources.py --probe <build_dir>

Run from the FACTORY ROOT. Applies on top of `patch_lf_library_freshness.py`.

`stale_shells` compares every shell against the newest `*.py` beside the build
directory. `deli_counter/build_freshness.py` -- which owns this question --
compares against a named tuple instead:

    GEOMETRY_SOURCES = (
        "deli_counter.py",      # the builder itself
        "stairwell.py", "stair_core.py", "stair_place.py",
        "floorplan.py", "floors.py", "wallruns.py", "roofs.py",
        "ladder.py", "ladder_geom.py", "ladder_place.py", ...
    )

The difference is not cosmetic. Measured 2026-08-12, minutes apart on the same
library: the owning tool said **"138 shell(s) newer than deli_counter.py -- up
to date"** while this one said **7.2 days behind**, because `check.py` had just
been edited. `check.py` builds no geometry. A gate that cries stale when a
patch script lands is one somebody stops reading, which is the failure this
whole thread has been about.

So READ the tuple rather than copy it. A mirrored list in another repo is two
copies of one rule, and `Building._cap_thick` states the objection in this
codebase's own words: *"One rule, one place, because both wall emitters need it
and two copies drift."* Parsed with `ast.literal_eval` off the assignment, no
import and no subprocess across the repo boundary.

AND IT REFUSES TO GUESS. If `build_freshness.py` is absent, or the tuple is not
there in a readable shape, `stale_shells` returns nothing rather than falling
back to "every .py". A freshness check that reports fresh -- or cries wolf --
because it could not find the rule is worse than one that says nothing, and
this module's docstring already commits to that direction.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

LIB = Path("level_factory/packages/pipeline/building_library.py")
SIDECAR = ".pre_freshsrc"


OLD = '''    build = Path(build_dir)
    src = build.parent
    if not build.is_dir() or not src.is_dir():
        return [], 0.0
    try:
        newest = max((p.stat().st_mtime for p in src.glob("*.py")), default=0.0)
        if not newest:
            return [], 0.0
        gaps = [(p.name, newest - p.stat().st_mtime)
                for p in sorted(build.glob("*.glb"))
                if p.stat().st_mtime < newest]
    except OSError:
        return [], 0.0
    worst = max((g for _n, g in gaps), default=0.0) / 86400.0
    return [n for n, _g in gaps], worst'''

NEW = '''    build = Path(build_dir)
    src = build.parent
    if not build.is_dir() or not src.is_dir():
        return [], 0.0
    sources = _geometry_sources(src)
    if not sources:
        return [], 0.0
    try:
        newest = max((p.stat().st_mtime for p in sources), default=0.0)
        if not newest:
            return [], 0.0
        gaps = [(p.name, newest - p.stat().st_mtime)
                for p in sorted(build.glob("*.glb"))
                if p.stat().st_mtime < newest]
    except OSError:
        return [], 0.0
    worst = max((g for _n, g in gaps), default=0.0) / 86400.0
    return [n for n, _g in gaps], worst'''


OLD_HDR = '''def stale_shells(build_dir) -> tuple[list[str], float]:'''

NEW_HDR = '''def _geometry_sources(src: Path) -> list[Path]:
    """The files `build_freshness.py` compares against, READ from it.

    That tool owns the freshness rule and names the geometry modules in a
    `GEOMETRY_SOURCES` tuple. Copying the list here would be two copies of one
    rule in two repos -- the objection `Building._cap_thick` states as "one
    rule, one place, because both wall emitters need it and two copies drift".
    So it is parsed out of the assignment, with no import and no subprocess
    across the boundary.

    Comparing against every `*.py` instead is not close enough. Measured
    2026-08-12, minutes apart on one library: the owning tool said "138
    shell(s) newer than deli_counter.py -- up to date" while a newest-of-all-py
    rule said 7.2 days behind, because `check.py` had just been edited and
    `check.py` builds no geometry.

    Returns [] when the tool or the tuple cannot be found. A check that cries
    stale because it could not locate the rule gets ignored, and one that
    reports fresh for the same reason is worse -- both are worse than silence.
    """
    tool = src / "build_freshness.py"
    if not tool.is_file():
        return []
    try:
        text = tool.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    m = re.search(r"^GEOMETRY_SOURCES\\s*=\\s*(\\([^)]*\\))", text, re.M)
    if not m:
        return []
    try:
        import ast
        names = ast.literal_eval(m.group(1))
    except (ValueError, SyntaxError):
        return []
    if isinstance(names, str):
        names = (names,)
    return [src / n for n in names if isinstance(n, str) and (src / n).is_file()]


def stale_shells(build_dir) -> tuple[list[str], float]:'''


EDITS = {LIB: ((OLD_HDR, NEW_HDR), (OLD, NEW))}

_CRLF = "\r\n"


def probe(build_dir: Path) -> int:
    import ast
    import re as _re
    build = Path(build_dir)
    src = build.parent
    tool = src / "build_freshness.py"
    print(f"probing {build}")
    if not tool.is_file():
        print(f"  no build_freshness.py beside it -- no opinion")
        return 1
    m = _re.search(r"^GEOMETRY_SOURCES\s*=\s*(\([^)]*\))",
                   tool.read_text(encoding="utf-8"), _re.M)
    if not m:
        print("  GEOMETRY_SOURCES not found in build_freshness.py -- no opinion")
        return 1
    names = ast.literal_eval(m.group(1))
    present = [src / n for n in names if (src / n).is_file()]
    print(f"  rule read from build_freshness.py: {len(names)} named, "
          f"{len(present)} present")
    newest = max(present, key=lambda p: p.stat().st_mtime, default=None)
    if newest is None:
        print("  none of them exist -- no opinion")
        return 1
    t = newest.stat().st_mtime
    glbs = sorted(build.glob("*.glb"))
    gaps = [(p.name, (t - p.stat().st_mtime) / 86400.0)
            for p in glbs if p.stat().st_mtime < t]
    print(f"  newest geometry source: {newest.name}")
    print(f"  {len(glbs)} shell(s), {len(gaps)} stale")
    for n, d in sorted(gaps, key=lambda x: -x[1])[:10]:
        print(f"    {d:5.1f} days behind  {n}")
    if len(gaps) > 10:
        print(f"    ... and {len(gaps) - 10} more")
    if not gaps:
        print("  up to date")
    return 0


def _eol(body: str) -> str:
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
            print(f"  anchor starts: {old.splitlines()[0].strip()[:70]!r}")
            print(f"  apply patch_lf_library_freshness.py first")
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
        print(f"REFUSING: {path.name} -- the patched file does not parse: {exc}")
        return 1
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
    if "--probe" in argv:
        i = argv.index("--probe")
        if i + 1 >= len(argv):
            raise SystemExit("--probe wants a Deli Counter build directory")
        return probe(Path(argv[i + 1]))

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
