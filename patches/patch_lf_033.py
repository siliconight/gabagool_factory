r"""level_factory 0.33.0 -- a bake that published nothing, and a test that could not see it.

    python patches\patch_lf_033.py --check
    python patches\patch_lf_033.py
    python patches\patch_lf_033.py --selftest
    python patches\patch_lf_033.py --revert

Run from the FACTORY ROOT.

WHAT WAS FAILING

0.32.0 repaired collection, so `tests/service` and `tests/integration` ran for
the first time in weeks. Nine tests failed. They are ONE failure:

    bank_block_001.presentation_compose              failed

with eight downstream absences. `themed_site_assemble`, `lux_apply` and
`dispatch_handoff` never ran, so the facade reported PLANNED nodes, the
dashboard stayed `pending`, no `mission.tscn` appeared, and `review` said
"no presentation previews".

`diagnostics bank_block_001.presentation_compose` names the cause exactly:

    failure_class: input_validation_error
    message: dressing_glb for the mission shell: no '*_dressing.glb' in
             ...jobs\bank_block_001.zoo_dressing_build\out -- the job that
             bakes it reported success without publishing one

THE CAUSE IS THE TEST FIXTURE, NOT THE PRODUCT

`tests/fixtures/repos/zoo/tools/zoo_cli.py`, the `--dress` branch, wrote its
index and no geometry:

    idx = out / f"{bid}_dressing.built.json"
    idx.write_text(...)          # and nothing else

Its own `--fixtures` branch, twenty lines above, has always written both:

    idx.write_text(...)
    (out / f"{scope}_fixtures.glb").write_bytes(b"glTF-zoo-fixtures-stub")

which is why `lux_fixture_gate succeeded` in the same run this broke. Real
Zoo's `--dress` publishes geometry -- `build_dressing` returns
`res["files"]["glb"]` and the CLI prints it. The guard in
`adapters/presentation` is right; the stub was one line short.

THE GUARD IS NOT NEW. `dressing_glb", "_dressing.glb"` appears twice in
`adapters/presentation/__init__.py.pre_032` and twice in the current file,
unchanged. 0.32.0 added `_COMPOSER_SOURCES` and `_composer_fingerprint` and
nothing else. This failure predates it; 0.32.0 only made it visible.

TWO BLIND SPOTS MADE IT SURVIVABLE, AND BOTH ARE CLOSED HERE

1. THE BAKE DID NOT DECLARE ITS GEOMETRY. `ZooAdapter.plan_commands` declared
   `expected = (f"{bid}_dressing.built.json",)` for mode `dress` -- the index
   only. The command's outputs appeared, so the job reported `succeeded`, and
   the missing `.glb` surfaced two stages later as somebody else's input
   error naming a directory upstream. A job that does not publish what the
   next stage requires has failed, and it has to fail AS ITSELF. The `.glb`
   is now declared.

   NOT CHANGED, and deliberately: the `fixtures` branch has the same shape --
   `expected = (f"{scope}_fixtures.built.json",)` with no `.glb` -- and
   `presentation_compose` requires `*_fixtures.glb` the same way. It is left
   alone because no run has failed on it and a mission with zero light
   fixtures might legitimately bake no geometry. Declaring it on a guess is
   how a working mission starts refusing. Measured and left open, not fixed
   blind.

2. THE TEST COULD NOT TELL SUCCESS FROM FAILURE. It asserted

       assert stage in r.stdout, f"missing stage {stage}"

   against a run that prints one line per job ending in a status word. The
   line `bank_block_001.presentation_compose  failed` CONTAINS
   "presentation_compose", so that assertion PASSED on the stage that broke
   the run. Six of its eight checks passed; the only two that caught anything
   were `lux_apply` and `dispatch_handoff`, and they caught it by never
   appearing at all. A stage list that goes green on a totally failed run is
   not a test. It now reads the status word.

WHAT THIS PATCH DOES NOT CLAIM

It fixes the stage that failed. It does not promise the nine go green: the
run has not reached `themed_site_assemble`, `lux_apply`, `dispatch_handoff`,
export or the portability test since roughly 2026-08-06, and anything behind
this wall is unmeasured. The selftest runs the integration test and prints
what happens rather than asserting a pass it has not earned. Expect to peel
another layer; each one is a real fix.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

STUB = "level_factory/tests/fixtures/repos/zoo/tools/zoo_cli.py"
ZOO = "level_factory/adapters/zoo/__init__.py"
TEST = "level_factory/tests/integration/test_presentation_export.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_033"

OLD_V, NEW_V = "0.32.0", "0.33.0"

EDITS: list[tuple[str, str, str]] = [
    # ---------------------------------------------------------------- stub
    (STUB,
     '        idx = out / f"{bid}_dressing.built.json"\n'
     "        idx.write_text(json.dumps(\n"
     '            {"mode": "dress", "building_id": bid, "n_fail": 0,\n'
     '             "dressing": [{"id": "curb_0", "collision": "none"}]}, sort_keys=True))\n',

     '        idx = out / f"{bid}_dressing.built.json"\n'
     "        idx.write_text(json.dumps(\n"
     '            {"mode": "dress", "building_id": bid, "n_fail": 0,\n'
     '             "dressing": [{"id": "curb_0", "collision": "none"}]}, sort_keys=True))\n'
     "        # THE GEOMETRY, which this branch never published. Real Zoo's\n"
     "        # --dress returns `res[\"files\"][\"glb\"]` and prints it;\n"
     "        # `presentation_compose` requires a `*_dressing.glb` in this\n"
     "        # job's out/. Writing the index alone made `zoo_dressing_build`\n"
     "        # report success and compose fail two stages later. The\n"
     "        # --fixtures branch above has always written its own .glb --\n"
     "        # which is why `lux_fixture_gate` passed in the same run.\n"
     '        (out / f"{bid}_dressing.glb").write_bytes(b"glTF-zoo-dressing-stub")\n'),

    # ----------------------------------------------------------- zoo adapter
    (ZOO,
     '            bid = _bid(job_spec.get("manifest_path")) or "building"\n'
     '            expected = (f"{bid}_dressing.built.json",)\n',

     '            bid = _bid(job_spec.get("manifest_path")) or "building"\n'
     "            # The .glb is DECLARED, not merely hoped for.\n"
     "            # `presentation_compose` requires a `*_dressing.glb` in this\n"
     "            # job's out/, so a bake that writes the index and no geometry\n"
     "            # has failed -- and it has to fail as ITSELF. Measured\n"
     "            # 2026-08-15: it reported `succeeded`, and compose failed for\n"
     "            # it, naming a directory two stages upstream.\n"
     '            expected = (f"{bid}_dressing.built.json",\n'
     '                        f"{bid}_dressing.glb")\n'),

    # ------------------------------------------------------------- the test
    (TEST,
     "def _cli(ws_root: Path, *args: str) -> subprocess.CompletedProcess:\n"
     "    return subprocess.run(\n"
     '        [sys.executable, str(ROOT / "apps" / "cli" / "main.py"), "-C", str(ws_root), *args],\n'
     "        capture_output=True, text=True,\n"
     "    )\n",

     "def _cli(ws_root: Path, *args: str) -> subprocess.CompletedProcess:\n"
     "    return subprocess.run(\n"
     '        [sys.executable, str(ROOT / "apps" / "cli" / "main.py"), "-C", str(ws_root), *args],\n'
     "        capture_output=True, text=True,\n"
     "    )\n"
     "\n"
     "\n"
     "def _stage_status(stdout: str, mission_id: str) -> dict:\n"
     '    """Map `<stage>[.<suffix>]` -> the status word the run printed for it.\n'
     "\n"
     "    A run prints one indented line per job, `<mission>.<stage>  <status>`,\n"
     "    where status is `succeeded`, `cache` or `failed`. Lines that do not\n"
     "    begin with the mission id -- the candidate summary, the structural\n"
     "    check total -- are not jobs and are skipped.\n"
     '    """\n'
     "    out: dict[str, str] = {}\n"
     "    for line in stdout.splitlines():\n"
     "        parts = line.split()\n"
     '        if len(parts) < 2 or not parts[0].startswith(mission_id + "."):\n'
     "            continue\n"
     "        out[parts[0][len(mission_id) + 1:]] = parts[-1]\n"
     "    return out\n"),

    (TEST,
     "    for stage in (\"pixelcoat_build\", \"zoo_kit_build\", \"patina_apply\",\n"
     "                  \"patina_dressing\", \"zoo_dressing_build\", \"presentation_compose\",\n"
     "                  \"lux_apply\", \"dispatch_handoff\"):\n"
     "        assert stage in r.stdout, f\"missing stage {stage}\"\n",

     "    # A stage NAME proves nothing. The run prints a status word at the end\n"
     "    # of each job line, so `bank_block_001.presentation_compose  failed`\n"
     "    # CONTAINS \"presentation_compose\" and satisfied `stage in r.stdout`.\n"
     "    # Measured 2026-08-15: compose failed, six of these eight assertions\n"
     "    # passed anyway, and the two that caught it did so only because their\n"
     "    # stages never ran at all. Read the STATUS the line carries.\n"
     "    status = _stage_status(r.stdout, \"bank_block_001\")\n"
     "    for stage in (\"pixelcoat_build\", \"zoo_kit_build\", \"patina_apply\",\n"
     "                  \"patina_dressing\", \"zoo_dressing_build\", \"presentation_compose\",\n"
     "                  \"lux_apply\", \"dispatch_handoff\"):\n"
     "        got = [s for jid, s in sorted(status.items())\n"
     "               if jid == stage or jid.startswith(stage + \".\")]\n"
     "        assert got, f\"missing stage {stage}\\n{r.stdout}\"\n"
     "        assert all(s in (\"succeeded\", \"cache\") for s in got), \\\n"
     "            f\"stage {stage} reported {got}\\n{r.stdout}\"\n"),
]

ENTRY = """## [0.33.0] - a bake that published nothing, and a test that could not see it

0.32.0 repaired collection, so `tests/service` and `tests/integration` ran
for the first time in weeks and nine tests failed. They are ONE failure with
eight downstream absences:

    bank_block_001.presentation_compose              failed

`themed_site_assemble`, `lux_apply` and `dispatch_handoff` never ran. That is
why the facade reported PLANNED nodes, the dashboard stayed `pending`, no
`mission.tscn` appeared, and `review` said "no presentation previews".

THE CAUSE

`diagnostics bank_block_001.presentation_compose`:

    failure_class: input_validation_error
    message: dressing_glb for the mission shell: no '*_dressing.glb' in
             ...jobs/bank_block_001.zoo_dressing_build/out -- the job that
             bakes it reported success without publishing one

The test-fixture Zoo stub's `--dress` branch wrote its index and no geometry.
Its own `--fixtures` branch has always written both, which is why
`lux_fixture_gate succeeded` in the same run this broke. Real Zoo's `--dress`
publishes geometry. The guard was right; the stub was one line short.

NOT A 0.32.0 REGRESSION. `dressing_glb", "_dressing.glb"` appears twice in
`adapters/presentation/__init__.py.pre_032` and twice in the current file,
unchanged. This has been failing since the dressing guard landed around
2026-08-06 and nothing could see it, because collection was aborting.

TWO BLIND SPOTS, BOTH CLOSED

THE BAKE DID NOT DECLARE ITS GEOMETRY. `ZooAdapter.plan_commands` declared
only the index for mode `dress`. Its declared outputs appeared, so the job
reported `succeeded`, and the missing geometry surfaced two stages later as
somebody else's input error naming a directory upstream. A job that does not
publish what the next stage requires has failed, and it must fail as itself.

The `fixtures` branch has the same shape and is LEFT ALONE. No run has failed
on it, and a mission with zero light fixtures may legitimately bake no
geometry -- declaring it on a guess is how a working mission starts refusing.
Measured and left open rather than fixed blind.

THE TEST COULD NOT TELL SUCCESS FROM FAILURE. It asserted `stage in r.stdout`
against a run that prints a status word at the end of each job line, so
`bank_block_001.presentation_compose  failed` CONTAINS "presentation_compose"
and that assertion passed on the stage that broke the run. Six of its eight
checks passed. The only two that caught anything, `lux_apply` and
`dispatch_handoff`, caught it by never appearing at all. It now reads the
status word and accepts only `succeeded` or `cache`.

WHAT THIS DOES NOT CLAIM

It fixes the stage that failed. It does not promise the nine go green. The
run has not reached `themed_site_assemble`, `lux_apply`, `dispatch_handoff`,
export or the portability test since roughly 2026-08-06, and everything
behind this wall is unmeasured. The selftest runs the integration test and
prints what happens rather than asserting a pass it has not earned.
"""

_CRLF = "\r\n"

#: A real excerpt of `run --target presentation` stdout, captured 2026-08-15
#: from pytest-254. The parser is tested against THIS, not against a string I
#: wrote to make it pass.
_MEASURED_STDOUT = (
    "  bank_block_001.deli_generate.candidate.seed_1997 cache\n"
    "  bank_block_001.lot_assemble.candidate.seed_1997  cache\n"
    "  bank_block_001.patina_apply                      succeeded\n"
    "  bank_block_001.pixelcoat_build                   succeeded\n"
    "  bank_block_001.patina_dressing                   succeeded\n"
    "  bank_block_001.zoo_fixtures_build                succeeded\n"
    "  bank_block_001.zoo_kit_build                     succeeded\n"
    "  bank_block_001.zoo_dressing_build                succeeded\n"
    "  bank_block_001.presentation_compose              failed\n"
    "  bank_block_001.lux_fixture_gate                  succeeded\n"
    "\n"
    "candidates: 3 built, all distinct\n"
    "  1 candidate(s) eliminated (the rest carried on): "
    "bank_block_001.candidate.seed_1997\n"
    "  1 blocker(s) belong to eliminated candidate(s) and do not block the "
    "mission\n"
    "\n"
    "Structural checks passed  (blockers open: 0, total findings: 7)\n"
)


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

    vp, cp = root / VERSION_F, root / CHANGELOG
    vbody = vp.read_text(encoding="utf-8")
    cbody = cp.read_text(encoding="utf-8")
    if NEW_V in vbody and f"## [{NEW_V}]" in cbody:
        print("  already applied  VERSION + CHANGELOG")
        return 0
    if OLD_V not in vbody:
        print(f"REFUSING: {VERSION_F} does not say {OLD_V}")
        return 1
    if check:
        print(f"  would bump   VERSION  {OLD_V} -> {NEW_V}")
        print(f"  would prepend CHANGELOG.md  +{len(ENTRY) + 1:,} bytes")
        return 0
    for q, txt in ((vp, vbody), (cp, cbody)):
        side = q.with_suffix(q.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(txt.encode("utf-8"))
    vp.write_bytes(vbody.replace(OLD_V, NEW_V, 1).encode("utf-8"))
    cp.write_bytes((ENTRY + "\n" + cbody).encode("utf-8"))
    print(f"  bumped       VERSION  {OLD_V} -> {NEW_V}")
    print("  prepended    CHANGELOG.md")
    return 0


def selftest(root: Path) -> int:
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

    # ---- 1. THE STUB IS RUN, not read. -------------------------------------
    # The whole failure was a green check over an artifact nobody opened.
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        man = work / "b1.patina.dressing.json"
        man.write_text(json.dumps({
            "schema": "patina-dressing/1", "building_id": "b1",
            "covers": [],
        }), encoding="utf-8")
        outdir = work / "out"
        stub = root / STUB
        r = subprocess.run(
            [sys.executable, str(stub), "--dress", str(man),
             "--out", str(outdir)],
            capture_output=True, text=True,
        )
        check("the stub's --dress branch exits 0", r.returncode == 0)
        produced = sorted(p.name for p in outdir.glob("*")) if outdir.is_dir() else []
        check("IT PUBLISHES A *_dressing.glb -- the missing artifact",
              any(n.endswith("_dressing.glb") for n in produced))
        check("and still writes its index",
              any(n.endswith("_dressing.built.json") for n in produced))
        check("named for the building, as compose resolves it",
              "b1_dressing.glb" in produced)
        if not produced:
            print("       (out/ is empty)")
        else:
            print(f"       produced: {', '.join(produced)}")

    # ---- 2. THE BAKE DECLARES ITS GEOMETRY. --------------------------------
    try:
        za = importlib.import_module("adapters.zoo")
        importlib.reload(za)
    except Exception as exc:                           # noqa: BLE001
        za = None
        print(f"       adapters.zoo did not import: {exc!r}")
    check("adapters.zoo imports", za is not None)
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        man = work / "b1.patina.dressing.json"
        man.write_text(json.dumps({"schema": "patina-dressing/1",
                                   "building_id": "b1"}), encoding="utf-8")
        spec = {"mode": "dress", "manifest_path": str(man),
                "work_dir": str(work / "out"), "repository": str(work),
                "blender_executable": sys.executable}
        declared: tuple = ()
        if za is not None:
            try:
                cmds = za.ZooAdapter().plan_commands(spec, {})
                declared = tuple(cmds[0].expected_outputs) if cmds else ()
            except Exception as exc:                   # noqa: BLE001
                print(f"       plan_commands raised: {exc!r}")
        check("mode=dress DECLARES the .glb, so the bake fails as itself",
              any(str(d).endswith("_dressing.glb") for d in declared))
        check("and still declares its index",
              any(str(d).endswith("_dressing.built.json") for d in declared))
        print(f"       declared: {declared}")

    # ---- 3. THE PARSER, AGAINST REAL MEASURED STDOUT. ----------------------
    src = (root / TEST).read_text(encoding="utf-8")
    ns: dict = {}
    start = src.index("def _stage_status(")
    end = src.index("\ndef ", start + 1)
    exec(compile(src[start:end], "<_stage_status>", "exec"), ns)   # noqa: S102
    status = ns["_stage_status"](_MEASURED_STDOUT, "bank_block_001")

    check("it reads presentation_compose as FAILED",
          status.get("presentation_compose") == "failed")
    check("and zoo_dressing_build as succeeded -- the lie it told",
          status.get("zoo_dressing_build") == "succeeded")
    check("and a cache hit as cache",
          status.get("deli_generate.candidate.seed_1997") == "cache")
    check("the candidate-summary lines are not mistaken for jobs",
          not any(k.startswith("candidate") for k in status))
    check("lux_apply is genuinely absent, not defaulted",
          "lux_apply" not in status)

    # The point of the whole edit: the OLD assertion passed on this stdout.
    check("THE OLD ASSERTION PASSED ON THIS EXACT RUN",
          "presentation_compose" in _MEASURED_STDOUT)
    check("AND THE NEW ONE DOES NOT",
          status.get("presentation_compose") not in ("succeeded", "cache"))

    # ---- 4. VERSION + CHANGELOG. -------------------------------------------
    v = (root / VERSION_F).read_text(encoding="utf-8")
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check(f"VERSION is {NEW_V}", NEW_V in v)
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    check("the entry names the failed stage",
          "presentation_compose" in flat)
    check("and says it is not a 0.32.0 regression",
          "NOT A 0.32.0 REGRESSION" in flat)
    check("and records the fixtures branch left open on purpose",
          "left open rather than fixed blind" in flat)
    check("and refuses to promise the nine go green",
          "does not promise the nine go green" in flat)

    # ---- 5. THE TEST ITSELF. Reported, not asserted. -----------------------
    print()
    print("  running the integration test this was found in --")
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/integration/test_presentation_export.py"
         "::test_presentation_export_and_portability", "-x", "-q"],
        cwd=str(lf), capture_output=True, text=True,
    )
    combined = r.stdout + r.stderr
    for line in combined.strip().splitlines()[-6:]:
        print(f"       {line}")
    # A collection error contains no assertion text either, so "the old
    # failure is gone" is TRUE of a test that never ran. That is the exact
    # shape of the bug this patch is about; it does not get to live in the
    # patch that fixes it. The run has to have happened first.
    ran = ("1 passed" in combined) or ("1 failed" in combined)
    check("the test actually RAN -- a collection error is not a pass", ran)
    check("the OLD failure is gone (no 'missing stage lux_apply')",
          ran and "missing stage lux_apply" not in combined)
    if r.returncode:
        print()
        print("  THE TEST STILL FAILS, AND THAT IS NOT ASSERTED EITHER WAY.")
        print("  Everything behind presentation_compose -- themed_site_assemble,")
        print("  lux_apply, dispatch_handoff, export, portability -- has not run")
        print("  since ~2026-08-06. A second wall here is expected, not a")
        print("  regression. Read the tail above and peel the next one.")
    else:
        print()
        print("  the test passes end to end.")

    print()
    print("  NOT VERIFIED HERE: the other eight failures in tests/service and")
    print("  tests/integration, and the `fixtures` branch's undeclared .glb.")
    print("  Run the full suite to measure them:")
    print("    python -m pytest level_factory\\tests\\service "
          "level_factory\\tests\\integration -q")

    print()
    print("  the bake publishes what the next stage requires, and the test can"
          " see it"
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
        for rel in (STUB, ZOO, TEST, VERSION_F, CHANGELOG):
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
        print("    python patches\\patch_lf_033.py --selftest")
        print("    python -m pytest level_factory\\tests\\service "
              "level_factory\\tests\\integration -q")
        print()
        print("  THE SECOND COMMAND IS THE POINT. Nine tests failed on one")
        print("  stage; this fixes that stage. Whatever it uncovers behind it")
        print("  has not run since ~2026-08-06 and is unmeasured.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
