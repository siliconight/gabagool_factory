r"""level_factory 0.35.0 (amendment) -- one version, read from one file.

    python patches\patch_lf_035b.py --check
    python patches\patch_lf_035b.py
    python patches\patch_lf_035b.py --selftest
    python patches\patch_lf_035b.py --revert

Run from the FACTORY ROOT. Apply AFTER patch_lf_035.py.

WHAT FAILED

    FAIL pyproject still agrees with VERSION

0.34.0 corrected `pyproject.toml` from 0.22.0 to 0.34.0 -- eleven releases of
drift -- and added the check that caught it. 0.35.0 bumped `VERSION` to
0.35.0 and did not touch `pyproject.toml`, so the drift restarted within the
hour, at one release, in the patch immediately after the one that fixed it.

The check did its job. The lesson is about the design, not the miss: two
files carried the same fact and stayed equal only while somebody kept
remembering. That is not a thing to remember harder.

THE FIX IS TO DELETE ONE OF THE TWO

`pyproject.toml` no longer states a version. It declares the version dynamic
and points at `VERSION`:

    [project]
    dynamic = ["version"]

    [tool.setuptools.dynamic]
    version = {file = "VERSION"}

`VERSION` is what the running code already reads, so it was always the real
source; `pyproject.toml` was a copy that nothing consulted and nothing
verified. Now there is no copy. A release patch bumps one file and an
installed wheel reports what the working tree says, because they are the same
bytes.

WHY THIS AND NOT A CHECK IN EVERY PATCH

A check that both files agree has to be written into every future release
patch, and the one that forgets is the one that drifts -- which is exactly
what just happened, one patch after the check existed. Removing the second
copy cannot be forgotten.

WHAT THE SELFTEST ACTUALLY VERIFIES

Not that the text says `dynamic`. It parses the TOML, follows the `file =`
reference to whatever path it names, reads that file, and compares it to
`VERSION`. If someone later points it at a different file, or misspells the
key, or leaves a literal `version =` behind that setuptools would prefer,
the check fails on the mechanism rather than on the spelling.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

PYPROJECT = "level_factory/pyproject.toml"
CHANGELOG = "level_factory/CHANGELOG.md"
VERSION_F = "level_factory/VERSION"
SIDECAR = ".pre_035b"

EDITS: list[tuple[str, str, str]] = [
    (PYPROJECT,
     'version = "0.34.0"\n',

     'dynamic = ["version"]\n'),

    (PYPROJECT,
     "[tool.setuptools.packages.find]\n"
     'include = ["packages*", "adapters*", "apps*"]\n',

     "[tool.setuptools.packages.find]\n"
     'include = ["packages*", "adapters*", "apps*"]\n'
     "\n"
     "# ONE VERSION, AND IT LIVES IN ./VERSION. This file said 0.22.0 while\n"
     "# VERSION said 0.33.0 -- eleven releases -- because two files carried the\n"
     "# same fact and only stayed equal while somebody remembered. 0.34.0\n"
     "# corrected the number and added a check; 0.35.0 drifted again by one\n"
     "# release anyway, in the very next patch. So the copy is gone rather\n"
     "# than corrected: setuptools reads the same file the running code does.\n"
     "[tool.setuptools.dynamic]\n"
     'version = {file = "VERSION"}\n'),

    (CHANGELOG,
     "unlit package from it, so two archives from one build can be compared. Stage\n"
     "2.\n",

     "unlit package from it, so two archives from one build can be compared. Stage\n"
     "2.\n"
     "\n"
     "AMENDED, SAME VERSION -- ONE VERSION, READ FROM ONE FILE\n"
     "\n"
     "This release bumped `VERSION` and not `pyproject.toml`, so the drift\n"
     "0.34.0 had just finished correcting -- eleven releases of it -- restarted\n"
     "at one release, in the patch immediately after the one that fixed it. The\n"
     "check 0.34.0 added caught it.\n"
     "\n"
     "The correction is not another bump. `pyproject.toml` no longer states a\n"
     "version at all: it declares `dynamic = [\"version\"]` and points\n"
     "`[tool.setuptools.dynamic]` at `VERSION`, which is the file the running\n"
     "code already read. There is no second copy to disagree. A check that two\n"
     "files match has to be remembered by every future release patch, and the\n"
     "one that forgets is the one that drifts; deleting the copy cannot be\n"
     "forgotten.\n"),
]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def _as(text: str, eol: str) -> str:
    return text if eol == "\n" else text.replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        raw = p.read_bytes()
        eol = _eol(raw)
        out, done = raw.decode("utf-8"), 0
        for old, new in edits:
            old_f, new_f = _as(old, eol), _as(new, eol)
            if new_f in out:
                done += 1
                continue
            if out.count(old_f) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old_f)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old_f, new_f, 1)
        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
        data = out.encode("utf-8")
        if data == raw:
            print(f"  already applied  {rel}")
            continue
        if check:
            print(f"  would patch  {rel}  {len(raw):,} -> {len(data):,} bytes "
                  f"({len(data) - len(raw):+,})")
            continue
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        p.write_bytes(data)
        print(f"  patched      {rel}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    try:
        import tomllib
    except ModuleNotFoundError:                        # pragma: no cover
        import tomli as tomllib                        # type: ignore

    pp = root / PYPROJECT
    data = tomllib.loads(pp.read_text(encoding="utf-8"))
    project = data.get("project", {})

    check("pyproject parses as TOML", True)
    check("it no longer states a literal version",
          "version" not in project)
    check("and declares the version dynamic",
          "version" in (project.get("dynamic") or []))

    # FOLLOW THE REFERENCE. A check that the word "dynamic" appears would pass
    # on a pyproject pointing at a file that does not exist.
    dyn = (data.get("tool", {}).get("setuptools", {})
           .get("dynamic", {}).get("version", {}))
    named = dyn.get("file")
    check("the dynamic version names a file", bool(named))
    if named:
        target = pp.parent / named
        check(f"and that file exists ({named})", target.is_file())
        if target.is_file():
            declared = target.read_text(encoding="utf-8").strip()
            actual = (root / VERSION_F).read_text(encoding="utf-8").strip()
            print(f"       {named} says {declared!r}; VERSION says {actual!r}")
            check("IT IS THE SAME FILE THE RUNNING CODE READS",
                  declared == actual)
            check("and it is this release", declared == "0.35.0")

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check("the entry records the second drift",
          "restarted at one release" in flat)
    check("and says why a check was not the fix",
          "deleting the copy cannot be forgotten" in flat)

    print()
    print("  NOT VERIFIED HERE: that a BUILT wheel reports 0.35.0. That needs")
    print("  `python -m build`, and the setuptools file: directive is what is")
    print("  under test, not this repo's packaging. `pip install -e .` in a")
    print("  scratch venv is the check if you want it.")

    print()
    print("  one version, and it lives in VERSION"
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
        for rel in (PYPROJECT, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        return bad
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lf_035b.py --selftest")
        print()
        print("  patch_lf_035.py --selftest will now also pass: its pyproject")
        print("  check reads the file the version is declared FROM.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
