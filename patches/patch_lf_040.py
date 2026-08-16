r"""Level Factory 0.40.0 -- roadmap 50: one resource manifest per package.

    python patches\\patch_lf_040.py --check
    python patches\\patch_lf_040.py
    python patches\\patch_lf_040.py --selftest
    python patches\\patch_lf_040.py --revert

Run from the FACTORY ROOT.

    packages/exporting/export.py   `resource_manifest.json` joins the skip set
                                   the handoff copy already uses
    tests/unit/test_one_resource_manifest.py   new
    VERSION, CHANGELOG.md          0.39.0 -> 0.40.0

VERIFY ON THE PACKAGE, all jobs cached, seconds:

    $ws = "workspaces\\unlit-3b-ws"
    python level_factory\\apps\\cli\\main.py -C $ws export unlit_probe_001 --mode art-unlit --format folder

AFTER: no `resource_manifest.json` in the export root;
`portable_resource_manifest.json` still there with 58 resources. The closure
scan must stay `ok: true` -- `_METADATA_FILES` means the scan never read
either manifest for references, so removing one should not move it, and if it
does move, something else was reading that file.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

LF = "level_factory"
EXPORT = f"{LF}/packages/exporting/export.py"
TESTF = f"{LF}/tests/unit/test_one_resource_manifest.py"
VERSION = f"{LF}/VERSION"
CHANGELOG = f"{LF}/CHANGELOG.md"
SIDECAR = ".pre_040"
OLD_VER, NEW_VER = "0.39.0", "0.40.0"
SOURCE_SHA = "472ffb7e6c177f33"

OLD = '    skip: set[str] = set()\n    if not ships_lux(profile.mode):\n        skip |= _PRESENTATION_FILES\n    if not profile.include_validation:\n        skip |= {"validation"}\n'
NEW = '    skip: set[str] = set()\n    if not ships_lux(profile.mode):\n        skip |= _PRESENTATION_FILES\n    if not profile.include_validation:\n        skip |= {"validation"}\n    # DISPATCH\'S MANIFEST IS NOT THIS PACKAGE\'S MANIFEST. Roadmap 50.\n    #\n    # `resource_manifest.json` is `dispatch.resource_manifest.v0.2`, written\n    # by the handoff stage to describe the handoff. The export then copies\n    # that directory in, overwrites `mission.tscn` with its own portable\n    # entry, adds the composed building and its art, and writes\n    # `portable_resource_manifest.json` -- so by the time the package is\n    # finished, Dispatch\'s file describes something that no longer exists.\n    #\n    # Measured on unlit_probe_001, 2026-08-16, art-unlit:\n    #\n    #     resource_manifest.json           17 entries, mission.tscn 16,246 B\n    #     mission.tscn on disk                                          688 B\n    #     portable_resource_manifest.json  58 resources, sha256 + size each,\n    #                                      including lot/shell/site.tscn and\n    #                                      all 31 art/zoo GLBs\n    #\n    # Two manifests, and the stale one has the better name. A recipient\n    # checking what they received opens `resource_manifest.json` first.\n    #\n    # DROPPED RATHER THAN REGENERATED, and the precedent is twelve lines\n    # below: the composed-root copy already skips\n    # `portable_resource_manifest.json` for exactly this reason -- the\n    # composer writes one, LF writes its own, and shipping both would be two\n    # answers to one question. This is that rule applied to the other\n    # manifest and the other producer.\n    #\n    # IF A RECIPIENT CONTRACT EVER REQUIRES THE NAME `resource_manifest.json`,\n    # the fix is to REGENERATE it here rather than to un-skip it. The problem\n    # was never the file; it was the file being stale.\n    skip |= {"resource_manifest.json"}\n'
TEST_SRC = '"""Roadmap 50: a package carries one resource manifest, and it is current.\n\n`resource_manifest.json` is `dispatch.resource_manifest.v0.2`, written by the\nhandoff stage about the handoff. `export_mission` copies that directory in,\nthen overwrites `mission.tscn` with its own portable entry and adds the\ncomposed building and its art -- so Dispatch\'s file ends up describing a\npackage that does not exist. Measured on unlit_probe_001, 2026-08-16: it\nrecorded `mission.tscn` at 16,246 bytes beside a 688-byte file, and listed 17\nentries for a 56-file package, while `portable_resource_manifest.json` beside\nit carried all 58 resources with a sha256 and size each.\n\nTwo manifests, and the stale one has the more authoritative name.\n\nRun:  python -m pytest tests/unit/test_one_resource_manifest.py\n"""\nimport inspect\n\nfrom packages.exporting import export as E\n\n\ndef test_the_handoff_copy_skips_dispatch_manifest():\n    src = inspect.getsource(E.export_mission)\n    head = src[:src.index("_copy_tree(base_dir")]\n    assert \'skip |= {"resource_manifest.json"}\' in head, (\n        "the handoff directory is copied with `skip`, so the exclusion has to "\n        "be in the set BEFORE that copy runs")\n\n\ndef test_it_is_dropped_not_merely_renamed():\n    """A rename would leave two manifests with one confusing name each."""\n    src = inspect.getsource(E.export_mission)\n    assert "resource_manifest.json" not in src.split(\n        \'skip |= {"resource_manifest.json"}\')[1].split("_copy_tree(base_dir")[0]\n\n\ndef test_the_precedent_it_follows_is_still_there():\n    """The composed-root copy skips the composer\'s own portable manifest for\n    the same reason. If that ever goes away this exclusion is orphaned and\n    somebody should notice here."""\n    src = inspect.getsource(E.export_mission)\n    assert \'"portable_resource_manifest.json"\' in src\n\n\ndef test_copy_tree_honours_a_basename_skip(tmp_path):\n    """The mechanism itself, not just the spelling -- `skip` matches\n    basenames, so a file of that name is dropped wherever it sits."""\n    src = tmp_path / "src"\n    (src / "nested").mkdir(parents=True)\n    (src / "resource_manifest.json").write_text("{}")\n    (src / "nested" / "resource_manifest.json").write_text("{}")\n    (src / "keep.json").write_text("{}")\n    dst = tmp_path / "dst"\n    E._copy_tree(src, dst, skip={"resource_manifest.json"})\n    landed = sorted(p.relative_to(dst).as_posix()\n                    for p in dst.rglob("*") if p.is_file())\n    assert landed == ["keep.json"], landed\n'
CHANGELOG_ENTRY = "## [0.40.0] - one resource manifest per package, and it is the current one\n\nA package shipped two. `resource_manifest.json` is\n`dispatch.resource_manifest.v0.2`, written by the handoff stage about the\nhandoff; `export_mission` copies that directory in, overwrites `mission.tscn`\nwith its own portable entry, adds the composed building and its art, and\nwrites `portable_resource_manifest.json`. By the time the package is\nfinished, Dispatch's file describes something that no longer exists.\n\nMeasured on unlit_probe_001, 2026-08-16, art-unlit:\n\n    resource_manifest.json           17 entries; mission.tscn at 16,246 bytes\n    mission.tscn on disk                                             688 bytes\n    portable_resource_manifest.json  58 resources, sha256 + size each,\n                                     including lot/shell/site.tscn and all\n                                     31 art/zoo GLBs\n\nThe mtimes said which way round it happened without needing anybody's memory:\nthe manifest was written at ...388494 and `mission.tscn` at ...389514, one\nsecond later. A recipient verifying the package against its own manifest\nfails on the first file -- and the stale one has the better name, so it is\nthe one they open.\n\nTHE FIX\n\n`resource_manifest.json` joins the `skip` set the handoff copy already uses.\nDropped rather than regenerated, following the precedent twelve lines below\nit: the composed-root copy already skips `portable_resource_manifest.json`\nbecause the composer writes one and LF writes its own, and two answers to one\nquestion is the defect. If a recipient contract ever requires that exact\nname, the fix is to regenerate it there rather than un-skip it -- the problem\nwas never the file, it was the file being stale.\n\nRoadmap item 50.\n\n"

_CRLF = "\r\n"


def _sha(d: bytes) -> str:
    return hashlib.sha256(d).hexdigest()


def _eol(b: str) -> str:
    c = b.count(_CRLF)
    return _CRLF if c > (b.count("\n") - c) else "\n"


def _as(t: str, eol: str) -> str:
    return t.replace(_CRLF, "\n").replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    missing = [r for r in (EXPORT, VERSION, CHANGELOG)
               if not (root / r).is_file()]
    if missing:
        print("REFUSING: not here -- run from the factory root: "
              + ", ".join(missing))
        return 1

    p = root / EXPORT
    raw = p.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)
    if _sha(raw)[:16] != SOURCE_SHA:
        print(f"  NOTE: {EXPORT} is sha256 {_sha(raw)[:16]}, written against "
              f"{SOURCE_SHA}. The anchor decides.")

    o, n = _as(OLD, eol), _as(NEW, eol)
    if n in body:
        print(f"  already applied  {EXPORT}")
    elif body.count(o) != 1:
        print(f"REFUSING: the skip-set anchor occurs {body.count(o)} time(s), "
              f"expected 1")
        return 1
    else:
        data = body.replace(o, n, 1).encode("utf-8")
        # THE POINT OF THE PATCH, CHECKED BEFORE IT IS WRITTEN: the exclusion
        # has to be in the set BEFORE the handoff copy runs, not merely
        # somewhere in the function.
        txt = data.decode("utf-8")
        if 'skip |= {"resource_manifest.json"}' not in \
                txt[:txt.index("_copy_tree(base_dir")]:
            print("REFUSING: the exclusion did not land before "
                  "`_copy_tree(base_dir` -- the copy would still carry it")
            return 1
        if check:
            print(f"  would patch  {EXPORT}  {len(raw):,} -> {len(data):,} "
                  f"bytes ({len(data) - len(raw):+,})")
        else:
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                side.write_bytes(raw)
            p.write_bytes(data)
            print(f"  patched      {EXPORT}  {len(raw):,} -> {len(data):,} "
                  f"bytes ({len(data) - len(raw):+,})  sha256 "
                  f"{_sha(data)[:16]}")

    t = root / TESTF
    if t.is_file() and t.read_text(encoding="utf-8").replace(_CRLF, "\n") \
            == TEST_SRC:
        print(f"  already there    {TESTF}")
    elif check:
        print(f"  would create {TESTF}  {len(TEST_SRC.encode()):,} bytes")
    else:
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_bytes(TEST_SRC.encode("utf-8"))
        print(f"  created      {TESTF}  {len(TEST_SRC.encode()):,} bytes")

    v = root / VERSION
    cur = v.read_bytes().decode("utf-8").strip()
    if cur == NEW_VER:
        print(f"  already {NEW_VER}     {VERSION}")
    elif cur != OLD_VER:
        print(f"REFUSING: {VERSION} is {cur!r}, expected {OLD_VER!r}")
        return 1
    elif check:
        print(f"  would bump   {VERSION}  {OLD_VER} -> {NEW_VER}")
    else:
        v.write_bytes(NEW_VER.encode("utf-8"))
        print(f"  bumped       {VERSION}  {OLD_VER} -> {NEW_VER}")

    c = root / CHANGELOG
    craw = c.read_bytes()
    cb = craw.decode("utf-8")
    ceol = _eol(cb)
    head = _as(f"## [{OLD_VER}] - ", ceol)
    if _as(f"## [{NEW_VER}] - ", ceol) in cb:
        print(f"  already has {NEW_VER}  {CHANGELOG}")
    elif cb.count(head) != 1:
        print(f"REFUSING: {CHANGELOG} has {cb.count(head)} "
              f"'## [{OLD_VER}] - ' headings, expected 1")
        return 1
    else:
        cn = cb.replace(head, _as(CHANGELOG_ENTRY, ceol) + head, 1)
        if check:
            print(f"  would patch  {CHANGELOG}  {len(craw):,} -> "
                  f"{len(cn.encode()):,} bytes")
        else:
            side = c.with_suffix(c.suffix + SIDECAR)
            if not side.is_file():
                side.write_bytes(craw)
            c.write_bytes(cn.encode("utf-8"))
            print(f"  patched      {CHANGELOG}  {len(craw):,} -> "
                  f"{len(cn.encode()):,} bytes")
    return 0


def _pytest(root: Path, *a: str) -> tuple[int, str]:
    pr = subprocess.run([sys.executable, "-m", "pytest", *a],
                        cwd=str(root / LF), capture_output=True, text=True)
    return pr.returncode, (pr.stdout or "")[-1500:] + (pr.stderr or "")[-500:]


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    src = (root / EXPORT).read_text(encoding="utf-8")
    check("the exclusion is in the file",
          'skip |= {"resource_manifest.json"}' in src)
    # POSITION, not presence. The handoff copy reads `skip` at line ~392; an
    # exclusion added after it would be in the file and do nothing.
    i = src.index("_copy_tree(base_dir")
    check("...and it lands BEFORE the handoff copy reads skip",
          'skip |= {"resource_manifest.json"}' in src[:i])
    check("the precedent it follows is still there",
          '"portable_resource_manifest.json"' in src)
    check("the module still compiles", _compiles(root / EXPORT))
    check("the new test exists", (root / TESTF).is_file())
    check(f"VERSION is {NEW_VER}",
          (root / VERSION).read_text(encoding="utf-8").strip() == NEW_VER)
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check(f"CHANGELOG leads with {NEW_VER}",
          cl.lstrip().startswith(f"## [{NEW_VER}]"))
    check("...with both manifests' numbers, not just the verdict",
          "17 entries" in cl and "58 resources" in cl and "16,246" in cl)
    check("...and what to do if a contract needs the name",
          "regenerate it there rather than un-skip it" in cl)

    print()
    print("  running the new tests")
    rc, tail = _pytest(root, "tests/unit/test_one_resource_manifest.py")
    check(f"the new tests pass (pytest rc={rc})", rc == 0)
    if rc:
        print(tail)
    print()
    print("  running tests/unit WHOLE")
    rc2, tail2 = _pytest(root, "tests/unit")
    check(f"tests/unit passes (pytest rc={rc2})", rc2 == 0)
    if rc2:
        print(tail2)

    print()
    if bad:
        print(f"  {bad} FAILURE(S)")
    else:
        print("  green proves the SKIP. Re-export and confirm the package has")
        print("  no resource_manifest.json and still scans ok: true.")
    return 1 if bad else 0


def _compiles(p: Path) -> bool:
    import py_compile
    import tempfile
    try:
        with tempfile.TemporaryDirectory() as d:
            py_compile.compile(str(p), cfile=str(Path(d) / "x.pyc"),
                               doraise=True)
        return True
    except Exception as exc:                      # noqa: BLE001
        print(f"       {exc}")
        return False


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        rc = 0
        for rel in (EXPORT, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if side.is_file():
                p.write_bytes(side.read_bytes())
                print(f"  reverted     {rel}")
            else:
                print(f"  no sidecar for {rel}")
                rc = 1
        (root / VERSION).write_bytes(OLD_VER.encode("utf-8"))
        print(f"  reverted     {VERSION} -> {OLD_VER}")
        t = root / TESTF
        if t.is_file():
            t.unlink()
            print(f"  removed      {TESTF}")
        return rc
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lf_040.py --selftest")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
