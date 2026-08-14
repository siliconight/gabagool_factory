r"""Let the root-anchored scripts find the factory from anywhere.

    python patch_root_resolution.py --check
    python patch_root_resolution.py
    python patch_root_resolution.py --selftest   (run it AFTER applying)
    python patch_root_resolution.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

WHAT BLOCKS A TIDY ROOT. Eleven scripts open with

    ROOT = Path(__file__).resolve().parent
    sys.path.insert(0, str(ROOT / "level_factory"))

which means each one finds the factory by SITTING IN IT. `factory_map.py`
says so in its own docstring -- "the file must SIT there". So they cannot
move to `tools/` or `patches/` with everything else, and the root cannot get
down to folders while eleven scripts are pinned to it by their first line.

WHAT THIS CHANGES. Each gets a four-line resolver that walks UP looking for
`factory.manifest.json`:

    def _factory_root() -> Path:
        here = Path(__file__).resolve()
        for base in (here.parent, *here.parents):
            if (base / "factory.manifest.json").is_file():
                return base
        return here.parent

Behaviour at the root is identical -- the first candidate it tests is its own
directory, which is where the manifest is. From `tools/` or `patches/` it
finds the root one or two levels up. Nothing else in any file moves.

WHY THE MANIFEST IS THE MARKER. It is the one file that defines this place:
`README.md` calls it the authority on the certified set, `verify-manifest`
reads it, and it exists in no tool repo. `.git` would match every tool repo;
`level_factory/` would break the moment someone checked out the tools
elsewhere.

FIVE SCRIPTS ARE NOT TOUCHED BECAUSE THEY ALREADY DO THIS.
`probe_reach.py` and `probe_sightlines.py` call `_lf_root()`, which walks
`(start, *start.parents)`. `module_extents.py` searches `here.parents` AND
`Path.cwd()`. `test_mirror_agreement.py` walks `(here.parent, *here.parents)`.
`patch_lf_walkable_site.py` mentions `__file__` only inside code it EMITS
into another file. All five can move today; the tidy script was refusing them
on a keyword rather than on what they do.

THE ANCHOR IS NEWLINE-DELIMITED ON PURPOSE. `patch_lf_source_library.py` and
`patch_map_derived.py` carry whole source files inside string literals, and
those literals contain the same assignment written with escaped `\n`. A plain
substring match finds three occurrences in one file and would rewrite the
wrong one -- the embedded copy, silently, inside a patch that then writes it
into a tool repo. Requiring real newlines on both sides finds exactly one.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SIDECAR = ".pre_rootres"

TARGETS = [
    "factory_map.py",
    "library_census.py",
    "library_themed_fit.py",
    "marker_scope_census.py",
    "patch_dc_roof_voids.py",
    "patch_lf_source_library.py",
    "patch_map_derived.py",
    "patch_zoo_roof_plate.py",
    "probe_pool_divergence.py",
    "roadmap_status.py",
    "unpatch_lf_themed_selection.py",
]

OLD = "ROOT = Path(__file__).resolve().parent"

NEW = '''def _factory_root() -> Path:
    """The directory holding `factory.manifest.json`, found by walking up.

    Was `Path(__file__).resolve().parent`, which required this file to sit AT
    the factory root and kept eleven scripts pinned there. Walking up means it
    works from `tools/`, `patches/` or anywhere else, and still returns the
    root when it IS the root -- the first candidate tested is its own
    directory.

    The manifest is the marker because it is the one file that defines this
    place and exists in no tool repo. `.git` would match every tool repo.
    """
    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        if (base / "factory.manifest.json").is_file():
            return base
    return here.parent


ROOT = _factory_root()'''

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _delimited(body: str, eol: str) -> tuple[str, int]:
    """The assignment as a whole line -- see the module docstring."""
    anchor = eol + OLD + eol
    return anchor, body.count(anchor)


def _apply(path: Path, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)

    if "def _factory_root()" in body:
        print(f"  already applied  {path.name}")
        return 0

    anchor, count = _delimited(body, eol)
    if count != 1:
        loose = body.count(OLD)
        print(f"REFUSING: {path.name} -- expected 1 whole-line occurrence, "
              f"found {count} ({loose} including embedded copies).")
        return 1

    out = body.replace(anchor, eol + _as(NEW, eol) + eol, 1)
    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- would leave {bare} bare LF line(s).")
        return 1
    try:
        compile(out, str(path), "exec")
    except SyntaxError as exc:
        print(f"REFUSING: {path.name} -- does not parse after the edit: {exc}")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    side = path.with_suffix(path.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    """Prove each patched script resolves the root from a subdirectory."""
    import shutil
    import subprocess
    import tempfile

    bad = 0
    probe = (
        "import sys\n"
        "from pathlib import Path\n"
        "src = Path(sys.argv[1]).read_text(encoding='utf-8')\n"
        "ns = {'__file__': sys.argv[2], 'Path': Path, 'sys': sys}\n"
        "start = src.index('def _factory_root')\n"
        "end = src.index('ROOT = _factory_root()') + len('ROOT = _factory_root()')\n"
        "exec(compile(src[start:end], 'frag', 'exec'), ns)\n"
        "print(ns['ROOT'])\n"
    )
    tmp = Path(tempfile.mkdtemp())
    try:
        fake = tmp / "factory"
        (fake / "tools").mkdir(parents=True)
        (fake / "factory.manifest.json").write_text("{}", encoding="utf-8")
        pf = tmp / "probe.py"
        pf.write_text(probe, encoding="utf-8")

        for name in TARGETS:
            p = root / name
            if not p.is_file():
                print(f"  skip {name} (not here -- already moved?)")
                continue
            if "def _factory_root()" not in p.read_text(encoding="utf-8"):
                print(f"  FAIL {name} has no resolver -- not applied")
                bad += 1
                continue
            # pretend the script lives in tools/ inside the fake factory
            r = subprocess.run(
                [sys.executable, str(pf), str(p),
                 str(fake / "tools" / name)],
                capture_output=True, text=True)
            got = r.stdout.strip()
            ok = got == str(fake)
            bad += 0 if ok else 1
            print(f"  {'ok  ' if ok else 'FAIL'} {name:<32} from tools/ -> "
                  f"{got or r.stderr.strip()[:60]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("  every patched script finds the root from a subdirectory"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for name in TARGETS:
            p = root / name
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {name}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {name}")
        return bad

    check = "--check" in argv
    rc = 0
    missing = 0
    for name in TARGETS:
        p = root / name
        if not p.is_file():
            print(f"  not here     {name}")
            missing += 1
            continue
        rc |= _apply(p, check=check)
    if missing:
        print(f"\n  {missing} target(s) absent -- already moved, or this is "
              f"not the root they were at.")
    if not check and not rc:
        print("\n  now they can move. Re-run: python factory_tidy.py")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
