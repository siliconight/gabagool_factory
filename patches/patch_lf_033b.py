r"""level_factory 0.33.0 (amendment) -- the second wall is our own export rename.

    python patches\patch_lf_033b.py --check
    python patches\patch_lf_033b.py
    python patches\patch_lf_033b.py --selftest
    python patches\patch_lf_033b.py --revert

Run from the FACTORY ROOT. Apply AFTER patch_lf_033.py.

WHAT 0.33.0 PROVED

The presentation chain runs. With the strict status check in place -- which
accepts only `succeeded` or `cache` -- all eight stages passed:

    pixelcoat_build  zoo_kit_build  patina_apply  patina_dressing
    zoo_dressing_build  presentation_compose  lux_apply  dispatch_handoff

and the three assertions behind them passed too: the composed
`presentation/site.tscn`, and Lux's `lux.applied.tscn` and `lux.quality.json`.
Both export commands returned 0. `lux_apply` and `dispatch_handoff` had not
run since roughly 2026-08-06.

THE NEXT WALL, AND IT IS OURS

    tests/integration/test_presentation_export.py:136: AssertionError
    assert (exports / "bank_block_001.portable-godot" / "HANDOFF.md").exists()

That name is gone. 0.26.0 and 0.27.0 renamed both artifacts, on purpose, and
docs/EXPORT_NAMING.md says why there are three names rather than one:

    build directory   LF_<mission>.<profile>/     keeps the profile, so
                                                  portable-godot and pure-shell
                                                  coexist in one workspace
    interior folder   LF_<mission>/               stable, so a recipient's
                                                  res:// paths survive a re-export
    archive           LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip

The test was written on 2026-07-24 and still expects the pre-rename spelling.
This is not a regression; it is a test that has not run since we renamed the
thing it checks.

HOW THE TWO ASSERTIONS ARE REWRITTEN

The DIRECTORY is spelled out literally, `LF_bank_block_001.portable-godot`.
It would be easy to import `export_build_dir_name` and assert the code agrees
with itself, and that assertion would pass no matter what the function did.
A test states the expected name; it does not ask the code what the name is.

The ARCHIVE cannot be spelled literally -- it carries the seed, a UTC instant
and the factory version -- so it is matched by shape,
`LF_bank_block_001_s*_f*_pure-shell.zip`, and exactly one must match. The
glob encodes the parts the name promises to carry.

THE HANDOFF.md ASSERTION IS DELIBERATELY LOOSE, FOR NOW

A folder export builds `LF_<mission>.<profile>/`, and the archive rewrites
its members under `LF_<mission>/`. Whether the FOLDER export also nests an
interior directory has not been observed -- the pytest tmp workspace is gone
by the time anyone looks. So this searches the package for `HANDOFF.md`
rather than asserting a path, and on failure PRINTS THE ACTUAL TREE, so the
next iteration needs no extra run. Tighten it to an exact path once the
layout has been seen. Recorded here rather than guessed at.

TWO DEFECTS IN 0.33.0'S OWN SELFTEST, FIXED HERE

1. `plan_commands` was handed `repository` and `work_dir` in the JOB SPEC.
   `ZooAdapter.plan_commands` reads both from the CONTEXT, so it raised
   `KeyError('repository')`, `declared` fell back to `()`, and the two checks
   that were supposed to prove the `.glb` is now declared reported FAIL for a
   reason that had nothing to do with the edit. The edit was correct; the
   check was calling it wrong.

2. `ran` was decided by reading pytest's prose. `"1 failed" in output`
   missed a `-x` run ending at `!!! stopping !!!` with no count line; the
   replacement, `"passed" in output`, then missed a PASSING run under `-q`,
   whose entire output is `.` and `[100%]`. It reported FAIL on the same run
   whose return code printed "IT PASSES END TO END" four lines later.

   It now reads the RETURN CODE, which pytest documents: 0 passed, 1 failed,
   2 interrupted, 3 internal, 4 usage, 5 nothing collected. Only 0 and 1
   mean the test ran. Two text detectors were wrong about output the process
   had already summarised in an integer.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TEST = "level_factory/tests/integration/test_presentation_export.py"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_033b"

#: The shape the archive name promises. Kept here AND in the test on purpose:
#: the selftest cross-checks this against a name `export_archive_name`
#: actually produces, so a drift in either one is caught.
ARCHIVE_GLOB = "LF_bank_block_001_s*_f*_pure-shell.zip"

EDITS: list[tuple[str, str, str]] = [
    (TEST,
     '    exports = root / ".level_factory" / "exports"\n'
     '    assert (exports / "bank_block_001.portable-godot" / "HANDOFF.md").exists()\n'
     '    assert (exports / "bank_block_001.zip").exists()\n',

     '    exports = root / ".level_factory" / "exports"\n'
     "    # 0.26.0/0.27.0 renamed both of these on purpose -- see\n"
     "    # docs/EXPORT_NAMING.md for why there are three names and not one.\n"
     "    # The build directory KEEPS the profile so two modes can coexist in\n"
     "    # one workspace; it is spelled out literally here rather than\n"
     "    # imported from `export_build_dir_name`, because a test that asks\n"
     "    # the code for the name it expects passes whatever the code does.\n"
     '    build_dir = exports / "LF_bank_block_001.portable-godot"\n'
     "    assert build_dir.is_dir(), (\n"
     '        f"no build dir; exports/ holds "\n'
     "        f\"{sorted(p.name for p in exports.glob('*'))}\")\n"
     "    # Loose ON PURPOSE, and tight enough to fail: the archive rewrites\n"
     "    # its members under an interior `LF_<mission>/` and it has not been\n"
     "    # observed whether a FOLDER export nests one too. Search, and print\n"
     "    # the real tree when it is not there.\n"
     '    handoffs = sorted(p.relative_to(build_dir).as_posix()\n'
     '                      for p in build_dir.rglob("HANDOFF.md"))\n'
     "    assert handoffs, (\n"
     '        f"no HANDOFF.md in {build_dir.name}; it holds "\n'
     "        f\"{sorted(p.relative_to(build_dir).as_posix() for p in build_dir.rglob('*'))}\")\n"
     "    # The archive is fully qualified -- seed, UTC instant, factory\n"
     "    # version -- so it cannot be spelled literally. Match the shape, and\n"
     "    # require exactly one: two would mean an export did not replace its\n"
     "    # predecessor, which is the failure the old single name hid.\n"
     '    zips = sorted(p.name for p in exports.glob(\n'
     '        "LF_bank_block_001_s*_f*_pure-shell.zip"))\n'
     "    assert len(zips) == 1, (\n"
     '        f"expected exactly one pure-shell archive, got {zips}; "\n'
     "        f\"exports/ holds {sorted(p.name for p in exports.glob('*'))}\")\n"),

    (CHANGELOG,
     "prints what happens rather than asserting a pass it has not earned.\n",

     "prints what happens rather than asserting a pass it has not earned.\n"
     "\n"
     "AMENDED, SAME VERSION -- WHAT THE FIX UNCOVERED\n"
     "\n"
     "The presentation chain runs. Under the strict status check all eight\n"
     "stages reported `succeeded` or `cache`, including `lux_apply` and\n"
     "`dispatch_handoff`, which had not run since roughly 2026-08-06, and\n"
     "both export commands returned 0.\n"
     "\n"
     "The next wall is our own rename. The test still expected\n"
     "`exports/bank_block_001.portable-godot/HANDOFF.md` and\n"
     "`exports/bank_block_001.zip`; 0.26.0 and 0.27.0 replaced both with the\n"
     "three names in docs/EXPORT_NAMING.md. Written 2026-07-24, it has not\n"
     "run since we renamed the thing it checks.\n"
     "\n"
     "The directory is now spelled out literally rather than imported from\n"
     "`export_build_dir_name` -- a test that asks the code for the name it\n"
     "expects passes whatever the code does. The archive carries a seed, a\n"
     "UTC instant and the factory version, so it is matched by shape and\n"
     "exactly one must match. The `HANDOFF.md` assertion searches the package\n"
     "instead of asserting a path, and prints the real tree when it fails,\n"
     "because whether a folder export nests an interior `LF_<mission>/` has\n"
     "not been observed. Loose on purpose, and recorded as such.\n"),
]

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        body = raw.decode("utf-8")
        if body.count(_CRLF):
            print(f"REFUSING: {rel} has CRLF line endings; these anchors are LF")
            return 1
        out, done = body, 0
        for old, new in edits:
            if new in out:
                done += 1
                continue
            if out.count(old) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old, new, 1)
        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
        # Only Python is compiled. 0.33.0's _apply ran compile() over every
        # edited file because all of them happened to be .py; this one edits
        # a CHANGELOG too, and markdown does not parse as Python.
        if p.suffix == ".py":
            try:
                compile(out, str(p), "exec")
            except SyntaxError as exc:
                print(f"REFUSING: {rel} -- does not parse after the edit: {exc}")
                return 1
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
    import fnmatch
    import importlib
    import json
    import subprocess
    import tempfile
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = (root / "level_factory").resolve()
    if str(lf) not in sys.path:
        sys.path.insert(0, str(lf))
    src = (root / TEST).read_text(encoding="utf-8")

    # ---- 1. THE OLD NAMES ARE GONE. ----------------------------------------
    check("the pre-rename build dir is no longer expected",
          '"bank_block_001.portable-godot"' not in src)
    check("the pre-rename archive name is no longer expected",
          '"bank_block_001.zip"' not in src)
    # Comments stripped first. The comment this patch inserts NAMES
    # `export_build_dir_name` in order to explain why it is not used, so a
    # search over the whole file finds the word and fails on the prose that
    # justifies the edit. Read the CODE.
    code = "\n".join(ln for ln in src.splitlines()
                     if not ln.strip().startswith("#"))
    check("the new build dir is spelled out, not imported",
          '"LF_bank_block_001.portable-godot"' in code
          and "export_build_dir_name" not in code)

    # ---- 2. THE GLOB MATCHES A NAME THE CODE ACTUALLY PRODUCES. ------------
    # Not a string check. `export_archive_name` is asked for a real name and
    # the test's pattern is matched against it.
    ids = importlib.import_module("packages.core.ids")
    importlib.reload(ids)
    real = ids.export_archive_name(
        "bank_block_001", profile_mode="pure-shell", seed=1997,
        built_utc="2026-08-15T10:18:09+00:00", factory_version="1.22.0")
    print(f"       a real archive name: {real}")
    check("THE TEST'S GLOB MATCHES A REAL export_archive_name OUTPUT",
          fnmatch.fnmatch(real, ARCHIVE_GLOB))
    check("and the test file carries that same glob",
          ARCHIVE_GLOB in src)
    check("the OLD literal would NOT have matched it -- why this had to change",
          not fnmatch.fnmatch(real, "bank_block_001.zip"))
    check("an unknown seed and factory version still match the shape",
          fnmatch.fnmatch(
              ids.export_archive_name("bank_block_001",
                                      profile_mode="pure-shell",
                                      built_utc="2026-08-15T10:18:09+00:00"),
              ARCHIVE_GLOB))
    check("a portable-godot archive does NOT match the pure-shell glob",
          not fnmatch.fnmatch(
              ids.export_archive_name("bank_block_001",
                                      profile_mode="portable-godot", seed=1997,
                                      built_utc="2026-08-15T10:18:09+00:00",
                                      factory_version="1.22.0"),
              ARCHIVE_GLOB))
    check("the build dir the code makes agrees with the literal in the test",
          ids.export_build_dir_name("bank_block_001", "portable-godot")
          == "LF_bank_block_001.portable-godot")

    # ---- 3. 0.33.0's SELFTEST BUG 1: the context, not the spec. ------------
    try:
        za = importlib.import_module("adapters.zoo")
        importlib.reload(za)
    except Exception as exc:                           # noqa: BLE001
        za = None
        print(f"       adapters.zoo did not import: {exc!r}")
    check("adapters.zoo imports", za is not None)
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        (work / "tools").mkdir()
        man = work / "b1.patina.dressing.json"
        man.write_text(json.dumps({"schema": "patina-dressing/1",
                                   "building_id": "b1"}), encoding="utf-8")
        # repository and work_dir live in the CONTEXT. 0.33.0 put them in the
        # job spec and got KeyError('repository') -- a FAIL that said nothing
        # about the edit it was checking.
        ctx = {"repository": str(work), "work_dir": str(work / "out"),
               "python_executable": sys.executable,
               "blender_executable": sys.executable}
        declared: tuple = ()
        if za is not None:
            cmds = za.ZooAdapter().plan_commands({"mode": "dress",
                                                  "manifest_path": str(man)},
                                                 ctx)
            declared = tuple(str(d) for d in cmds[0].expected_outputs)
        print(f"       declared: {declared}")
        check("mode=dress DECLARES the .glb -- 0.33.0's real edit, checked right",
              any(d.endswith("_dressing.glb") for d in declared))
        check("and still declares its index",
              any(d.endswith("_dressing.built.json") for d in declared))

    # ---- 4. 0.33.0's SELFTEST BUG 2: what counts as "the test ran". --------
    # ASK THE PROCESS, DO NOT READ ITS PROSE. pytest documents its exit
    # codes: 0 all passed, 1 tests failed, 2 interrupted, 3 internal error,
    # 4 usage error, 5 nothing collected. Only 0 and 1 mean the test ran.
    #
    # Two text detectors were tried before this and both were wrong. `"1
    # failed" in out` missed a `-x` run that ends at `!!! stopping !!!` with
    # no count line; `"passed" in out` then missed a PASSING run under `-q`,
    # whose whole output is `.` and `[100%]`. That second one reported FAIL
    # on the same run whose return code printed "IT PASSES END TO END" four
    # lines later -- the check disagreeing with the process it had just run.
    def _ran(rc: int) -> bool:
        return rc in (0, 1)

    check("a failing run counts as having run", _ran(1))
    check("a passing run counts as having run", _ran(0))
    check("a collection error (4) does not", not _ran(4))
    check("nothing collected (5) does not", not _ran(5))
    check("an interrupted session (2) does not", not _ran(2))

    # ---- 5. THE TEST. Reported, not asserted. ------------------------------
    print()
    print("  running the integration test --")
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/integration/test_presentation_export.py"
         "::test_presentation_export_and_portability", "-x", "-q"],
        cwd=str(lf), capture_output=True, text=True,
    )
    combined = r.stdout + r.stderr
    for line in combined.strip().splitlines()[-8:]:
        print(f"       {line}")
    check("the test actually RAN", _ran(r.returncode))
    check("the export-name wall is gone (no 'bank_block_001.portable-godot')",
          _ran(r.returncode)
          and "bank_block_001.portable-godot" not in combined)

    print()
    if r.returncode == 0:
        print("  IT PASSES END TO END. Locked shell -> art pass -> Lux ->")
        print("  Dispatch -> export -> portability, for the first time since")
        print("  roughly 2026-08-06.")
    else:
        print("  STILL FAILING, AND NOT ASSERTED EITHER WAY. Read the tail.")
        print("  What remains behind this point -- portability-test, the clean")
        print("  project instantiation -- has not run in weeks and is")
        print("  unmeasured. A third wall is a discovery, not a regression.")

    print()
    print("  NOT VERIFIED HERE: the eight other failures in tests/service and")
    print("  tests/integration, whether a FOLDER export nests an interior")
    print("  LF_<mission>/, and the `fixtures` branch's undeclared .glb.")
    print("    python -m pytest level_factory\\tests\\service "
          "level_factory\\tests\\integration -q")

    print()
    print("  the test expects the names we actually ship"
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
        for rel in (TEST, CHANGELOG):
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
        print("    python patches\\patch_lf_033b.py --selftest")
        print()
        print("  0.33.0 fixed the stage. This fixes the test's idea of what")
        print("  an export is called. Neither is the last wall until the")
        print("  suite says so.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
