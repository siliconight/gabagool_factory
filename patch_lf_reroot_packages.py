r"""Reroot references of a package staged into a subdirectory of another root.

    python patch_lf_reroot_packages.py --probe <export_dir>   # measure first
    python patch_lf_reroot_packages.py --check
    python patch_lf_reroot_packages.py
    python patch_lf_reroot_packages.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

THE DEFECT. `res://x` is `<project root>/x` exactly -- no search path, no
walking up. Deli Counter stages each themed building as its OWN res:// root, so
`lot/<archetype>/site.tscn` names its modules `res://art/zoo/wall.glb` and its
shell `res://site_base.glb`. Copying that package into a SUBDIRECTORY of the
export root does not move the references with it, and nothing downstream
rewrites them.

Measured on lot_demo_001.portable-godot, from the export's own directory tree:

  * `mission.tscn` instances `presentation/lux.applied.tscn` and nothing else.
  * `lux.applied.tscn` names five `res://lot/<archetype>/site.tscn`. All five
    resolve.
  * Each of those five names ~26 resources rooted at ITS OWN package: 25 under
    `art/zoo`, `art/fixtures`, `art/dressing`, plus `site_base.glb`. The export
    root has NO `art/` directory, so the 25 dangle and Godot drops them
    silently.
  * `res://site_base.glb` DOES resolve at the export root -- to the SITE's base
    mesh (255,344 bytes), not the building's (108,368). It is not missing and
    not misrooted by the scan's definition. It loads the wrong geometry, in
    five buildings, and no check in the toolchain has anything to say about it.

That is the floating white plates and the empty sky.

THE FIX. A file that is not at the export root may have been written against a
res:// root that is now one of its own ancestors. Ask the disk which: walk from
the file's directory upward and take the DEEPEST ancestor under which strictly
more of its references resolve than resolve at the export root. Rewrite only
the references that actually resolve there. No ancestor beats the root -> the
file is left alone.

This is a search, not a convention. It never assumes `lot/<id>` is a package
boundary; it concludes it, from files that exist. A package with no rerootable
references produces no edit.

Ordered BEFORE the bare-ref repair, deliberately. That pass rewrites a
root-level `res://<name>` to `res://assets/<name>` whenever a bundled asset
shares the basename -- which for `res://site_base.glb` in a building scene
would point five buildings at the site's bundled base, the same wrong mesh by
another route. The specific, evidence-backed fix goes first; the basename
fallback keeps whatever it is still needed for.

--probe runs the identical decision against a real export WITHOUT writing
anything and WITHOUT needing the patch applied, because a rewriter that has
not been read out loud against a real tree is a guess.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

TARGET = Path("level_factory/packages/exporting/localize.py")
SIDECAR = ".pre_reroot"


# ---------------------------------------------------------------- probe ----
# A standalone copy of the decision the patch installs. Deliberately NOT
# imported from the repo: the point of --probe is to measure BEFORE the edit.

_PROBE_REF = re.compile(r'res://([^"\')\s]+)')
_PROBE_SUFFIXES = {".tscn", ".tres", ".gd"}


def _choose_root(export_dir: Path, f: Path, refs: list[str]):
    """(root_rel, resolved_there, resolved_at_export_root) or None."""
    at_root = sum(1 for r in refs if (export_dir / r).exists())
    if at_root == len(refs):
        return None
    cand = f.parent.relative_to(export_dir)
    while True:
        if cand == Path("."):
            return None
        n = sum(1 for r in refs if (export_dir / cand / r).exists())
        if n > at_root:
            return cand.as_posix(), n, at_root
        cand = cand.parent


def probe(export_dir: Path) -> int:
    if not export_dir.is_dir():
        print(f"not a directory: {export_dir}")
        return 1
    print(f"probing {export_dir}")
    total_files = total_refs = 0
    shadowed: list[str] = []
    for f in sorted(export_dir.rglob("*")):
        if not (f.is_file() and f.suffix in _PROBE_SUFFIXES):
            continue
        if f.parent == export_dir:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        refs = sorted(set(_PROBE_REF.findall(text)))
        if not refs:
            continue
        chosen = _choose_root(export_dir, f, refs)
        if chosen is None:
            continue
        root_rel, n, at_root = chosen
        rel = f.relative_to(export_dir).as_posix()
        movable = [r for r in refs
                   if (export_dir / root_rel / r).exists()
                   and not r.startswith(root_rel + "/")]
        total_files += 1
        total_refs += len(movable)
        print(f"  {rel}")
        print(f"      root -> res://{root_rel}/   "
              f"({n} of {len(refs)} refs resolve there, "
              f"{at_root} at the export root)")
        print(f"      would rewrite {len(movable)} reference(s)")
        for r in movable:
            if (export_dir / r).exists():
                shadowed.append(f"{rel}: res://{r}")
                print(f"        SHADOWED  res://{r}")
                print(f"                  resolves at the export root to a "
                      f"DIFFERENT file")
    print()
    print(f"  {total_files} file(s), {total_refs} reference(s) to reroot")
    if shadowed:
        print(f"  {len(shadowed)} of them currently resolve to the WRONG file "
              f"instead of dangling:")
        for s in shadowed:
            print(f"    {s}")
    else:
        print("  none of them currently resolve to a wrong file")
    return 0


# ---------------------------------------------------------------- edits ----

OLD_FIELD = '''    repaired_bare_refs: list[str] = field(default_factory=list)
    entry_scene: str | None = None'''

NEW_FIELD = '''    repaired_bare_refs: list[str] = field(default_factory=list)
    rerooted_refs: list[str] = field(default_factory=list)
    entry_scene: str | None = None'''


OLD_DICT = '''            "repaired_bare_refs": sorted(self.repaired_bare_refs),
            "entry_scene": self.entry_scene,'''

NEW_DICT = '''            "repaired_bare_refs": sorted(self.repaired_bare_refs),
            "rerooted_refs": sorted(self.rerooted_refs),
            "entry_scene": self.entry_scene,'''


OLD_FUNC = '''def localize_export(export_dir: Path, *, addon_sources: dict[str, Path],'''

NEW_FUNC = '''#: Any res:// reference in a text resource.
_RES_REF = re.compile(r'res://([^"\\')\\s]+)')


def _reroot_subpackages(export_dir: Path, report: LocalizeReport) -> None:
    """Reroot a package that was staged as its own res:// root.

    `res://x` is `<project root>/x` exactly. Deli Counter stages each themed
    building as its own res:// root, so `lot/<archetype>/site.tscn` names its
    modules `res://art/zoo/wall.glb` and its shell `res://site_base.glb`.
    Copying that package into a subdirectory of the export root does not move
    the references with it.

    Measured on lot_demo_001.portable-godot: five building scenes, 25 dangling
    art references each -- and a 26th, `res://site_base.glb`, which RESOLVES,
    to the site's 255 KB base mesh instead of the building's 108 KB one. Not
    missing, not misrooted, not detectable by any closure category: five
    buildings quietly standing the wrong geometry.

    So ask the disk which root the file was written against, rather than
    assuming `lot/<id>` is a package boundary: walk from the file's directory
    upward, take the DEEPEST ancestor under which strictly more of its
    references resolve than resolve at the export root, and rewrite only the
    references that actually resolve there. No ancestor wins -> no edit. A
    file already at the export root is already at its own root and is skipped.
    """
    for f in sorted(export_dir.rglob("*")):
        if not (f.is_file() and f.suffix in _TEXT_SUFFIXES):
            continue
        if f.parent == export_dir:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        refs = sorted(set(_RES_REF.findall(text)))
        if not refs:
            continue
        at_root = sum(1 for r in refs if (export_dir / r).exists())
        if at_root == len(refs):
            continue

        root_rel = None
        cand = f.parent.relative_to(export_dir)
        while cand != Path("."):
            if sum(1 for r in refs if (export_dir / cand / r).exists()) > at_root:
                root_rel = cand.as_posix()
                break
            cand = cand.parent
        if root_rel is None:
            continue

        new = text
        moved = 0
        for r in refs:
            if r.startswith(root_rel + "/"):
                continue
            if not (export_dir / root_rel / r).exists():
                continue
            # The lookahead is what keeps `.../wall_w30.glb` from matching
            # inside `.../wall_w300.glb`: a reference always ends at a quote,
            # whitespace or a closing paren.
            new = re.sub(r'res://' + re.escape(r) + r'(?=["\\'\\s)])',
                         f'res://{root_rel}/{r}', new)
            moved += 1
        if moved and new != text:
            f.write_text(new, encoding="utf-8")
            report.rerooted_refs.append(
                f"{f.relative_to(export_dir).as_posix()}: {moved} ref(s) -> "
                f"res://{root_rel}/")


def localize_export(export_dir: Path, *, addon_sources: dict[str, Path],'''


OLD_CALL = '''    # Repair dangling bare res://<file> refs to their bundled assets/ copy.'''

NEW_CALL = '''    # Reroot packages staged as their own res:// root (building packages under
    # lot/<archetype>/). BEFORE the bare-ref repair below, which would rewrite
    # a building's `res://site_base.glb` to `res://assets/site_base.glb` on a
    # basename match and point it at the SITE's base -- the same wrong mesh by
    # another route. Evidence-backed rewrite first; basename fallback after.
    _reroot_subpackages(export_dir, report)

    # Repair dangling bare res://<file> refs to their bundled assets/ copy.'''


EDITS = {TARGET: ((OLD_FIELD, NEW_FIELD), (OLD_DICT, NEW_DICT),
                  (OLD_FUNC, NEW_FUNC), (OLD_CALL, NEW_CALL))}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor.

    A single-line anchor contains no newline at all, so an anchor-derived test
    reports LF for a CRLF document and inserts mixed endings. That is not
    hypothetical: it happened, in `patch_claude_md_verification.py`, 81 lines
    of it.
    """
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
              f"bytes ({len(data) - len(raw):+,})  eol "
              f"{'CRLF' if eol == _CRLF else 'LF'}")
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
