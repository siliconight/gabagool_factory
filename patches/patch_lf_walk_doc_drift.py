r"""Correct three docstrings the walk-the-export change left behind.

    python patch_lf_walk_doc_drift.py --check
    python patch_lf_walk_doc_drift.py
    python patch_lf_walk_doc_drift.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

`patch_lf_walk_the_export.py` made `cmd_walk` run `export_mission` and wrap the
`mission.tscn` that comes out of it. Three descriptions still say it wraps the
composed themed level:

  * `apps/cli/main.py`          -- the `walk` subcommand's --help text
  * `packages/preview/walk_preview.py` -- the module docstring
  * `apps/cli/commands/__init__.py`    -- `cmd_walk`'s docstring

The inline comment INSIDE cmd_walk ("WALK WHAT SHIPS") already describes the
new behaviour correctly, which is the tell: the change was explained where it
was made and nowhere else. `--help` is the one a person reads first and the
only one that was wrong in a way that changes what you expect to see.

Each still contains a true claim worth keeping -- the preview PROJECT is not
exported, and the deliverable still carries no player. That distinction is the
whole point of the module, so it is sharpened rather than deleted: the project
is not exported; what it instances now is the export.

Docstrings only. No behaviour changes.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

MAIN = Path("level_factory/apps/cli/main.py")
PREVIEW = Path("level_factory/packages/preview/walk_preview.py")
COMMANDS = Path("level_factory/apps/cli/commands/__init__.py")
SIDECAR = ".pre_walkdoc"


OLD_HELP = '''    sp = sub.add_parser("walk", help="build a dev-only first-person walk preview "
                                     "of the composed themed level (never exported)")'''

NEW_HELP = '''    sp = sub.add_parser("walk", help="build a dev-only first-person walk preview "
                                     "that wraps the portable export (the "
                                     "preview project itself is never exported)")'''


OLD_MODULE = '''"""Build a throwaway first-person WALK PREVIEW project that wraps a composed
themed level so you can walk it and make refinements.'''

NEW_MODULE = '''"""Build a throwaway first-person WALK PREVIEW project that wraps the portable
export of a mission so you can walk it and make refinements.'''


OLD_PARA = '''So we never bake the player into the package. Instead this builder makes a
SEPARATE, clearly dev-only project that INSTANCES the same content scene and adds
LF's dependency-free walk controller at a spawn marker. It's never exported (the
deliverable stays pure content); it exists purely for local iteration.'''

NEW_PARA = '''So we never bake the player into the package. Instead this builder makes a
SEPARATE, clearly dev-only project that INSTANCES the deliverable and adds LF's
dependency-free walk controller at a spawn marker. The PREVIEW PROJECT is never
exported (the deliverable stays pure content); it exists purely for local
iteration.

What it instances is the PORTABLE EXPORT, not the job outputs. ``cmd_walk``
runs ``export_mission`` first and wraps the ``mission.tscn`` that comes out of
it, so what you walk is the package a stranger receives -- localized,
addon-free and closure-scanned. Walking the job outputs meant walking a level
that renders only with the Lux checkout on disk, which is the definition of an
instrument that escaped.'''


OLD_CMD = '''    """Build (and optionally open) a DEV-ONLY first-person walk preview that
    wraps the composed themed level so you can walk it and make refinements.

    This is deliberately NOT part of the drop-in package: the package is content
    a stranger instances into their own project, so it stays project-agnostic. A
    player needs its own project, so the preview is a separate, throwaway project
    that instances the same content scene and adds LF's dependency-free player. It
    is never exported.
    """'''

NEW_CMD = '''    """Build (and optionally open) a DEV-ONLY first-person walk preview that
    wraps the mission's PORTABLE EXPORT so you can walk it and make refinements.

    This is deliberately NOT part of the drop-in package: the package is content
    a stranger instances into their own project, so it stays project-agnostic. A
    player needs its own project, so the preview is a separate, throwaway project
    that instances the export's `mission.tscn` and adds LF's dependency-free
    player. The preview project is never exported.

    It wraps the EXPORT rather than the job outputs so that what gets walked is
    what gets shipped -- see the WALK WHAT SHIPS note below.
    """'''


EDITS = {
    MAIN: ((OLD_HELP, NEW_HELP),),
    PREVIEW: ((OLD_MODULE, NEW_MODULE), (OLD_PARA, NEW_PARA)),
    COMMANDS: ((OLD_CMD, NEW_CMD),),
}

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
