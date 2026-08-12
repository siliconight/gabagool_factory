r"""Let the closure scan see ext_resource paths that are not res:// at all.

    python patch_lf_closure_relative.py --check
    python patch_lf_closure_relative.py
    python patch_lf_closure_relative.py --revert
    python patch_lf_closure_relative.py --probe <export_dir>

Run from the FACTORY ROOT (the directory holding `level_factory/`).

THE BLIND SPOT. `scan_closure` finds references with `res://([^"\')\s]+)`. A
reference that never says `res://` is not matched, not counted, and not
reported -- the scan has no opinion about it in either direction.

The graybox site is written that way. `lot.write_godot_scene(portable=True)`
emits ext_resource paths RELATIVE to the scene file, deliberately, so the scene
plus its siblings form a drop-anywhere folder. Measured on
lot_demo_001.portable-godot: the root `site.tscn` names five buildings as
`path="buildings/<name>.glb"`, and the scan's `resource_count: 38` counts the
file while saying nothing at all about the five.

WHAT THIS DOES NOT DECIDE. Whether Godot resolves a relative ext_resource path
against the scene's own directory is a question about the engine, and this
patch does not answer it from memory. It reports the COUNT of relative
references so the number stops being invisible, and it fails only on one that
resolves to nothing or escapes the package -- broken under either reading of
the engine, and therefore safe to call a defect without knowing which reading
is right.

If the count is non-zero and you want the engine's actual answer, the
portability test is the instrument that has it: it opens the package in a clean
project, and a dropped building shows up there.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

TARGET = Path("level_factory/packages/exporting/closure.py")
SIDECAR = ".pre_relative"


# ---------------------------------------------------------------- probe ----

_PROBE_EXT = re.compile(r'^\[ext_resource[^\]]*path="([^"]+)"', re.M)


def probe(export_dir: Path) -> int:
    if not export_dir.is_dir():
        print(f"not a directory: {export_dir}")
        return 1
    print(f"probing {export_dir}")
    root = export_dir.resolve()
    seen = broken = 0
    for f in sorted(export_dir.rglob("*")):
        if not (f.is_file() and f.suffix in (".tscn", ".tres")):
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel_f = f.relative_to(export_dir).as_posix()
        for m in _PROBE_EXT.finditer(text):
            p = m.group(1)
            if "://" in p:
                continue
            seen += 1
            target = (f.parent / p).resolve()
            inside = target.is_relative_to(root)
            state = ("ESCAPES the package" if not inside
                     else "resolves" if target.exists()
                     else "resolves to NOTHING")
            if state != "resolves":
                broken += 1
            print(f"  {rel_f}: path=\"{p}\"  -> {state}")
            if inside:
                print(f"      as res://"
                      f"{target.relative_to(root).as_posix()}")
    print()
    print(f"  {seen} relative ext_resource path(s), {broken} broken")
    if seen and not broken:
        print("  all resolve against their own scene's directory; whether the "
              "ENGINE\n  reads them that way is the portability test's "
              "question, not this one's")
    return 0


# ---------------------------------------------------------------- edits ----

OLD_RE = '''_RES_REF = re.compile(r'res://([^"\\')\\s]+)')'''

NEW_RE = '''_RES_REF = re.compile(r'res://([^"\\')\\s]+)')
#: An ext_resource's path, whatever scheme it uses -- including none.
_EXT_PATH = re.compile(r'^\\[ext_resource[^\\]]*path="([^"]+)"', re.M)'''


OLD_FIELDS = '''    misrooted_resource_count: int = 0
    required_plugin_count: int = 0'''

NEW_FIELDS = '''    misrooted_resource_count: int = 0
    #: ext_resource paths carrying no scheme at all -- neither res:// nor
    #: uid://. `lot.write_godot_scene(portable=True)` emits these on purpose,
    #: relative to the scene file, so a scene and its siblings form a
    #: drop-anywhere folder. Reported as a COUNT because the scan used to have
    #: no opinion about them in either direction: the res:// regex never
    #: matched them, so five buildings named from the graybox site.tscn were
    #: neither resolved nor reported, in a verdict that said `ok: true`.
    relative_reference_count: int = 0
    #: Of those, the ones that resolve to nothing, or out of the package. A
    #: relative path is broken under EVERY reading of how the engine treats
    #: it, which is why this one counts against `ok` and the bare count above
    #: does not.
    unresolved_relative_count: int = 0
    required_plugin_count: int = 0'''


OLD_OK = '''                and self.misrooted_resource_count == 0
                and self.external_reference_count == 0'''

NEW_OK = '''                and self.misrooted_resource_count == 0
                and self.unresolved_relative_count == 0
                and self.external_reference_count == 0'''


OLD_DICT = '''            "misrooted_resource_count": self.misrooted_resource_count,'''

NEW_DICT = '''            "misrooted_resource_count": self.misrooted_resource_count,
            "relative_reference_count": self.relative_reference_count,
            "unresolved_relative_count": self.unresolved_relative_count,'''


OLD_SCAN = '''        low = text.lower()
        if f.name not in _METADATA_FILES:'''

NEW_SCAN = '''        # Scheme-less ext_resource paths. Godot's text loader is documented
        # to take a relative ext_resource path as relative to the scene file's
        # own directory, and that is the only reading under which these were
        # ever intended to work -- so resolve them that way and report what
        # comes back. A path that resolves to nothing, or climbs out of the
        # package, is broken under any reading; that is the only case this
        # calls a defect. The bare count is reported without judgement so the
        # number is visible instead of absent.
        if f.suffix in (".tscn", ".tres"):
            root_abs = mission_root.resolve()
            for m in _EXT_PATH.finditer(text):
                p = m.group(1)
                if "://" in p:
                    continue
                result.relative_reference_count += 1
                try:
                    target = (f.parent / p).resolve()
                    inside = target.is_relative_to(root_abs)
                except (OSError, ValueError):
                    target, inside = None, False
                here = f.parent.relative_to(mission_root).as_posix() or "."
                if target is None or not inside:
                    result.unresolved_relative_count += 1
                    result.issues.append(
                        f"{f.name}: relative ext_resource leaves the package: "
                        f"{p} (from {here}/)")
                elif not target.exists():
                    result.unresolved_relative_count += 1
                    result.issues.append(
                        f"{f.name}: relative ext_resource resolves to nothing: "
                        f"{p} (from {here}/)")

        low = text.lower()
        if f.name not in _METADATA_FILES:'''


EDITS = {TARGET: ((OLD_RE, NEW_RE), (OLD_FIELDS, NEW_FIELDS), (OLD_OK, NEW_OK),
                  (OLD_DICT, NEW_DICT), (OLD_SCAN, NEW_SCAN))}

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
