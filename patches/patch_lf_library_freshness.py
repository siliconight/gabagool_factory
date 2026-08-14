r"""Say it at the point of USE: this library is older than the code.

    python patch_lf_library_freshness.py --check
    python patch_lf_library_freshness.py
    python patch_lf_library_freshness.py --revert
    python patch_lf_library_freshness.py --probe <build_dir>

Run from the FACTORY ROOT (the directory holding `level_factory/`).

A Level Factory run already prints three lines of library health, right after
`building_library.index()` returns:

    [site] 4 archetype(s) excluded from the lot for a missing manifest: ...
    [site] 11 entr(y/ies) in ...\deli_counter\build are not source archetypes
    [site] themed lot: 97 of 123 shell(s) can carry a theme

On 2026-08-12 all three printed, and **every shell in that library was 4.2 days
behind the code that builds it.** Nothing said so. The run completed, the
export scanned clean, the engine passed it, a human walked it -- and a ladder
climbed into a solid roof because Zoo dressed a roof slot baked three days
before the slot could express a hole.

`deli_counter/build_freshness.py` owns this question and answers it well. It
was written on 2026-08-05 for exactly this failure, and `check.py` has now been
wired to run it (`patch_dc_check_freshness.py`). But `check.py` is a gate
somebody runs deliberately before committing. **Level Factory reads that
library on every single run and never asked.** That is where the four days
actually went.

So this adds a fourth line beside the other three -- the consumer's cheap guard
at the point of use, pointing at the tool that owns the answer. It does not
block: a stale library is the *caller's* to rebuild, LF cannot rebuild it, and
a run that refuses without being able to fix anything is a run that gets
`--force`d. It is loud, it is specific, and it names both commands.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

LIB = Path("level_factory/packages/pipeline/building_library.py")
COMMANDS = Path("level_factory/apps/cli/commands/__init__.py")
SIDECAR = ".pre_libfresh"


OLD_FUNC = '''def art_incomplete(lot: list[dict]) -> list[dict]:'''

NEW_FUNC = '''def stale_shells(build_dir) -> tuple[list[str], float]:
    """``(names, worst_gap_days)`` for shells older than the code building them.

    THE CONSUMER'S GUARD, NOT THE AUTHORITY. `deli_counter/build_freshness.py`
    owns this question, was written for it on 2026-08-05 after `nav_gate --all`
    graded ten stairs across seven fossil shells, and names every stale file
    with `--list`. This is the cheap version at the point of USE, because a
    Level Factory run reads this library every time and printed three lines
    about its health on 2026-08-12 while every shell in it was 4.2 days behind.

    Deli Counter's sources sit one directory up from its `build/`, which is the
    same relationship `build_freshness.py` assumes. If that stops being true
    this returns nothing rather than guessing, because a freshness check that
    reports "fresh" because it looked in the wrong place is worse than none.

    mtime, with the caveat the owning tool records: a fresh clone or a checkout
    that rewrites sources marks everything stale, asking for a rebuild that was
    not needed -- the safe direction. The unsafe direction needs a source
    written with an OLDER timestamp than the build, which git does not do in
    normal use.
    """
    build = Path(build_dir)
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
    return [n for n, _g in gaps], worst


def art_incomplete(lot: list[dict]) -> list[dict]:'''


OLD_PRINT = '''        if themed_map:
            # The themed pool is narrower, and it must be the SAME narrowing'''

NEW_PRINT = '''        # THE FOURTH LINE, and the one that was missing. The three above
        # describe what the library CONTAINS; this one describes whether any of
        # it is current. On 2026-08-12 all three printed over a library 4.2
        # days behind its code, and every gate downstream -- nav, walk, Laser
        # Tag, the export, a human's eyes -- graded geometry Deli Counter no
        # longer produces.
        #
        # Reported, not enforced. LF cannot rebuild somebody else's library,
        # and a gate that blocks without being able to fix anything is a gate
        # that gets worked around. Both commands are named so the next line
        # after this one is the fix.
        stale, worst_days = building_library.stale_shells(library)
        if stale:
            print(f"[site] STALE LIBRARY: {len(stale)} shell(s) in {library} "
                  f"are older than the code that builds them (worst "
                  f"{worst_days:.1f} days). Every gate below is grading "
                  f"geometry this code no longer produces.")
            print(f"[site]   name them:  python build_freshness.py --list"
                  f"   (in Deli Counter)")
            print(f"[site]   rebuild:    python build.py --all")

        if themed_map:
            # The themed pool is narrower, and it must be the SAME narrowing'''


EDITS = {LIB: ((OLD_FUNC, NEW_FUNC),), COMMANDS: ((OLD_PRINT, NEW_PRINT),)}

_CRLF = "\r\n"


def probe(build_dir: Path) -> int:
    """The same comparison, standalone, before anything is applied."""
    build = Path(build_dir)
    src = build.parent
    if not build.is_dir():
        print(f"not a directory: {build}")
        return 1
    newest_p = max(src.glob("*.py"), key=lambda p: p.stat().st_mtime,
                   default=None)
    if newest_p is None:
        print(f"no *.py beside {build} -- nothing to compare against")
        return 1
    newest = newest_p.stat().st_mtime
    glbs = sorted(build.glob("*.glb"))
    gaps = [(p.name, (newest - p.stat().st_mtime) / 86400.0)
            for p in glbs if p.stat().st_mtime < newest]
    print(f"probing {build}")
    print(f"  newest source: {newest_p.name}")
    print(f"  {len(glbs)} shell(s), {len(gaps)} stale")
    for n, d in sorted(gaps, key=lambda x: -x[1])[:10]:
        print(f"    {d:5.1f} days behind  {n}")
    if len(gaps) > 10:
        print(f"    ... and {len(gaps) - 10} more")
    return 0


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
            print(f"  anchor starts: {old.splitlines()[0].strip()[:70]!r}")
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
