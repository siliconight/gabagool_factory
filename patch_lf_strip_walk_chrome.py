r"""Strip the walk scene's player scripts when the walk scene itself is stripped.

    python patch_lf_strip_walk_chrome.py --check
    python patch_lf_strip_walk_chrome.py
    python patch_lf_strip_walk_chrome.py --revert
    python patch_lf_strip_walk_chrome.py --probe <export_dir>

Run from the FACTORY ROOT (the directory holding `level_factory/`).

Measured on lot_demo_001 --mode pure-shell: `lot_player.gd` (10,878 bytes) and
`lot_site_walk.gd` both shipped, and NOTHING in the package references either.
`site.tscn` names only the five buildings; `mission.tscn` loads only
`site.tscn`. They were referenced by the walk scene, `strip_walk` deleted that
scene, and the two scripts it was the sole referrer of stayed behind.

A player controller riding along in a package whose own mode is documented as
"functional geometry + collision + anchors only". ENGINE_GATES is pointed about
the direction of that mistake -- a QA harness "may not grow into a player
controller" -- and a player controller may not commute into a shell either.
Closure scanning cannot see it: an unreferenced file breaks nothing, it just
should not be there.

NOT ADDED TO `_QA_HARNESS_FILES`, and the difference matters. That list is
stripped UNCONDITIONALLY because nothing may ever ask for a QA harness. These
two ARE asked for: `lot.py` emits the walk scene with
`ext_resource ... lot_site_walk.gd` and `... lot_player.gd`, so an
`--include-walk` export needs them. Stripping them unconditionally would leave
that profile's walk scene naming two scripts that are gone -- and with
CLOSURE_ENFORCED now True, that is not a warning any more, it is a failed
export. So they go only when the scene that referenced them goes.

AND ONLY IF NOTHING ELSE NAMES THEM. Deleting by basename across the whole tree
without checking is the `skip`-vs-`skip_rel` mistake in a new costume: that one
matched `site.tscn` everywhere and took all six, breaking five buildings. Each
candidate here is checked against every surviving text resource first. A false
positive keeps a file that could have gone, which is the harmless direction.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

TARGET = Path("level_factory/packages/exporting/localize.py")
SIDECAR = ".pre_walkchrome"

_CANDIDATES = ("lot_player.gd", "lot_site_walk.gd")
_PROBE_SUFFIXES = {".tscn", ".tres", ".gd"}


def probe(export_dir: Path) -> int:
    """Who, if anyone, references these files in a real export."""
    if not export_dir.is_dir():
        print(f"not a directory: {export_dir}")
        return 1
    print(f"probing {export_dir}")
    for name in _CANDIDATES:
        found = sorted(export_dir.rglob(name))
        if not found:
            print(f"  {name}: not in this package")
            continue
        for target in found:
            rel = target.relative_to(export_dir).as_posix()
            refs = []
            for f in sorted(export_dir.rglob("*")):
                if not (f.is_file() and f.suffix in _PROBE_SUFFIXES):
                    continue
                if f == target:
                    continue
                try:
                    if name in f.read_text(encoding="utf-8"):
                        refs.append(f.relative_to(export_dir).as_posix())
                except (OSError, UnicodeDecodeError):
                    continue
            size = target.stat().st_size
            if refs:
                print(f"  {rel} ({size:,} bytes) KEPT, referenced by:")
                for r in refs:
                    print(f"      {r}")
            else:
                print(f"  {rel} ({size:,} bytes) would be STRIPPED, "
                      f"referenced by nothing")
    return 0


OLD_CONST = '''_QA_HARNESS_FILES = ("site_navqa.tscn", "lot_navqa_setup.gd",
                     "mp_smoke.gd", "mp_smoke_node.gd")'''

NEW_CONST = '''_QA_HARNESS_FILES = ("site_navqa.tscn", "lot_navqa_setup.gd",
                     "mp_smoke.gd", "mp_smoke_node.gd")

#: Dev-only walk chrome. Kept apart from `_QA_HARNESS_FILES` on purpose: that
#: list goes unconditionally because nothing may ask for a QA harness, while
#: these two ARE asked for when a profile says include_walk -- `lot.py` emits
#: the walk scene naming both. So they go only alongside the walk scene, and
#: only when nothing else still references them.
#:
#: Measured on lot_demo_001 --mode pure-shell: both shipped, referenced by
#: nothing, in a package documented as functional geometry + collision +
#: anchors only. Closure scanning cannot catch this -- an unreferenced file
#: resolves fine, it simply has no business being in a deliverable.
_WALK_CHROME_FILES = ("lot_player.gd", "lot_site_walk.gd")


def _still_referenced(export_dir: Path, target: Path) -> bool:
    """Does any surviving text resource name this file?

    Matched by BASENAME and deliberately wide: a reference can arrive as
    ``res://lot_player.gd``, as a bare relative ``lot_player.gd``, or inside a
    preload in a .gd. Erring wide keeps a file that could have gone, which
    costs bytes; erring narrow deletes a script a scene still needs, which
    costs a package -- and with CLOSURE_ENFORCED True, an export.
    """
    for f in sorted(export_dir.rglob("*")):
        if not (f.is_file() and f.suffix in _TEXT_SUFFIXES) or f == target:
            continue
        try:
            if target.name in f.read_text(encoding="utf-8"):
                return True
        except (OSError, UnicodeDecodeError):
            continue
    return False'''


OLD_STRIP = '''    for name in _QA_HARNESS_FILES:
        for stray in sorted(export_dir.rglob(name)):
            report.stripped_scenes.append(
                stray.relative_to(export_dir).as_posix())
            stray.unlink()
'''

NEW_STRIP = '''    for name in _QA_HARNESS_FILES:
        for stray in sorted(export_dir.rglob(name)):
            report.stripped_scenes.append(
                stray.relative_to(export_dir).as_posix())
            stray.unlink()

    # The walk scene was the only thing naming its player and setup scripts,
    # so deleting the scene orphaned them and they shipped anyway. Runs AFTER
    # both strips above, so that anything already deleted cannot count as a
    # referrer and keep a file alive on the strength of a scene that is gone.
    if strip_walk:
        for name in _WALK_CHROME_FILES:
            for stray in sorted(export_dir.rglob(name)):
                if _still_referenced(export_dir, stray):
                    continue
                report.stripped_scenes.append(
                    stray.relative_to(export_dir).as_posix())
                stray.unlink()
'''


EDITS = {TARGET: ((OLD_CONST, NEW_CONST), (OLD_STRIP, NEW_STRIP))}

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
    if "--probe" in argv:
        i = argv.index("--probe")
        if i + 1 >= len(argv):
            raise SystemExit("--probe wants an export directory")
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
