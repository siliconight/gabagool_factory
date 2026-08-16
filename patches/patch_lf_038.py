r"""Level Factory 0.38.0 -- the pool a mission draws from is a property of
the mission, not of the command that happens to be running.

    python patches\\patch_lf_038.py --check
    python patches\\patch_lf_038.py
    python patches\\patch_lf_038.py --selftest
    python patches\\patch_lf_038.py --revert

Run from the FACTORY ROOT. Roadmap item 48, question 2, answered "keyed on
the brief".

WHAT CHANGES

    apps/cli/commands/__init__.py   `_art_run` deleted (definition, call site,
                                    parameter); the narrowing at :942 becomes
                                    unconditional inside the `lot_library`
                                    branch it already sits in
    tests/unit/test_draw_is_invocation_independent.py    new
    VERSION, CHANGELOG.md           0.37.0 -> 0.38.0

WHY UNCONDITIONAL RATHER THAN A NEW CONDITION

`if themed_map or art_run:` sits inside `if library and (...)`, and `library`
IS `model.lot_library`. So "key it on the brief" and "always, here" are the
same statement, and a condition that can never be false reads as if it could.

WHAT THIS COSTS, AND IT IS NOT NOTHING

A brief that sets `lot_library` and never runs `--art` now draws from 98 of
123 shells. Missions ALREADY BUILT with `lot_library` will re-select
buildings on their next run and their existing grades stop describing them --
which is the point, since those grades already described a different level,
but it is a real re-run. Missions without `lot_library` are untouched
byte-for-byte.

THE SELFTEST RUNS THE UNIT SUITE. Not a grep for the strings this patch
inserted -- four releases in this arc reported "still green" against 28 tests
while 659 went unrun. `pyproject.toml` sets `addopts = "-q"`, so this does
NOT pass `-q` again; `-q -q` drops the count line entirely and the run looks
like a wall of dots that never reports.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

LF = "level_factory"
CMDS = f"{LF}/apps/cli/commands/__init__.py"
TESTF = f"{LF}/tests/unit/test_draw_is_invocation_independent.py"
VERSION = f"{LF}/VERSION"
CHANGELOG = f"{LF}/CHANGELOG.md"
SIDECAR = ".pre_038"

OLD_VER, NEW_VER = "0.37.0", "0.38.0"

EDITS = [
    ('    # DOES THIS RUN HAVE AN ART LAYER? Read off the planned graph rather than\n    # threaded down as a flag: `themed_site_assemble` is planned or it is not,\n    # and a parameter somebody has to remember to pass is the shape of defect\n    # this file keeps finding. It decides which pool the GREYBOX pass draws\n    # from -- see the narrowing in `_write_site_spec`, and addendum item J.\n    _art_run = any(j.stage_id == "themed_site_assemble"\n                   for j in plan.graph.jobs())\n\n',
     "    # WHICH POOL THE GREYBOX PASS DRAWS FROM used to be decided here, by\n    # reading `themed_site_assemble` off THIS INVOCATION'S planned graph.\n    # Roadmap 48 measured what that cost: `batch create` plans no art layer\n    # and drew from 123 shells, `run --art` plans one and drew from 98, and\n    # the same job at the same seed produced two different buildings -- the\n    # one every grader and the functional lock measured, and the one the\n    # package would have shipped. The decision moved into `_write_site_spec`,\n    # where it is keyed on the BRIEF (`lot_library`) and is therefore the same\n    # answer in every invocation of the mission's life. Addendum item J.\n\n"),
    ('            site_spec = _write_site_spec(\n                ws, model, deli_out, seed=seed, themed_scene=themed_scene,\n                art_run=_art_run)\n',
     '            site_spec = _write_site_spec(\n                ws, model, deli_out, seed=seed, themed_scene=themed_scene)\n'),
    ('                     *, seed: int, themed_scene: str | None = None,\n                     art_run: bool = False) -> Path:\n',
     '                     *, seed: int, themed_scene: str | None = None) -> Path:\n'),
    ('        if themed_map or art_run:\n            # The themed pool is narrower, and it must be the SAME narrowing\n            # `_lot_for_compose` applied: compose published one scene per\n            # archetype and `themed_map` is keyed on those ids. A wider pool\n            # here selects buildings that have no composed scene, `_source`\n            # finds no match, and the row stands as greybox with every stage\n            # reporting success -- the defect this file keeps finding, one\n            # layer down.\n            #\n            # NOW APPLIED TO THE GREYBOX BRANCH TOO, when the run has an art\n            # layer. The comment that used to sit here said the opposite:\n            # "NOT applied to the greybox branch. That places levels already\n            # built and graded, and re-selecting them would be different levels\n            # wearing the same grades." That protected the STABILITY of a\n            # grade, and `probe_pool_divergence.py` measured what it was\n            # stabilising -- across lot_demo_001\'s three candidates, 14 of 15\n            # building slots already carried an archetype other than the one\n            # Laser Tag graded, and 13 graded archetypes never shipped at all.\n            # One slot in the mission agreed. The thing that comment feared had\n            # already happened; keeping the wider draw preserved the\n            # consistency of a number about a level nobody receives.\n            #\n            # So: grade the pool that ships. With an art layer the themed pool\n            # is the deliverable, so the greybox pass draws from it as well.\n            # Without one the greybox IS the deliverable and this does not\n            # fire -- `art_run` is false and nothing changes.\n            before = len(complete)\n            complete = building_library.require_themed_shells(complete, count)\n            which = "themed lot" if themed_map else "graded lot (art run)"\n            print(f"[site] {which}: {len(complete)} of {before} shell(s) "\n                  f"can carry a theme -- the graded draw and the shipped draw "\n                  f"come from the same pool")\n',
     '        # THE NARROWING, AND IT IS NOT CONDITIONAL ANY MORE. Roadmap 48.\n        #\n        # The themed pool is narrower, and it must be the SAME narrowing\n        # `_lot_for_compose` applied: compose published one scene per\n        # archetype and `themed_map` is keyed on those ids. A wider pool here\n        # selects buildings that have no composed scene, `_source` finds no\n        # match, and the row stands as greybox with every stage reporting\n        # success -- the defect this file keeps finding, one layer down.\n        #\n        # IT USED TO BE GATED ON A PER-INVOCATION FLAG read off the planned\n        # graph. That gate was itself a fix: `probe_pool_divergence.py` had\n        # measured that across lot_demo_001\'s three candidates, 14 of 15\n        # building slots already carried an archetype other than the one Laser\n        # Tag graded and 13 graded archetypes never shipped at all, so the\n        # greybox branch started narrowing too -- "grade the pool that ships".\n        #\n        # It made the greybox pass and the themed pass agree WITHIN one\n        # invocation, and could not make them agree ACROSS invocations:\n        # `batch create` plans no `themed_site_assemble`, so it drew from 123\n        # shells while `run --art` drew from 98, and `batch create` is where\n        # the graders, the structural checks and the functional lock all run.\n        # Roadmap 48 caught it on unlit_probe_001 -- cr_garage graded,\n        # landmark_hall_a03 shipped, one job id, one seed -- and it was the\n        # functional lock that refused the export, because nothing else in the\n        # pipeline can see both sites.\n        #\n        # SO IT IS KEYED ON THE BRIEF. Reaching this line already means\n        # `lot_library` is set, which is also what gates the art layer, so the\n        # pool a mission draws from is now the same in every invocation of its\n        # life -- before approval, after approval, graded, shipped.\n        #\n        # THE COST, STATED: a brief that sets `lot_library` and is never run\n        # with `--art` now draws from the narrower pool as well. It buys back\n        # nothing and loses 25 of 123 shells of variety. That is the price of\n        # the draw not moving, and it is the cheaper side of the trade -- a\n        # graybox deliverable with less variety is a worse level; a graded\n        # level that is not the shipped level is not a level at all.\n        before = len(complete)\n        complete = building_library.require_themed_shells(complete, count)\n        which = "themed lot" if themed_map else "graded lot"\n        print(f"[site] {which}: {len(complete)} of {before} shell(s) "\n              f"can carry a theme -- keyed on the brief, so this is the same "\n              f"pool in every invocation")\n'),
]

TEST_SRC = '"""Roadmap 48: which buildings a mission places may not depend on WHICH\nCOMMAND is running.\n\nTHE DEFECT THIS PINS. `_write_site_spec` chooses the lot by handing a pool to\n`building_library.pick_lot`. That pool used to be narrowed only when the\nCURRENT invocation had planned a `themed_site_assemble` job -- `_art_run`,\nread off `plan.graph.jobs()`. `batch create` plans no art layer and `run\n--art` plans one, so the same mission at the same seed drew from 123 shells\nin one command and 98 in the other, and produced two different buildings.\n\nMeasured on unlit_probe_001 (2026-08-15, one workspace, seed 5017): graybox\ndrew `cr_garage`, the art pass drew `landmark_hall_a03`. Everything that\ngraded the mission -- walktest, Laser Tag, the structural checks, the\nfunctional lock -- ran under `batch create` and measured the first. The\nexport would have shipped the second. The functional lock refused it, which\nis the only reason anybody found out. Full evidence:\n`docs/findings/ITEM48_THE_DRAW_MOVED.md`.\n\nWHAT THIS TEST CHECKS, AND WHAT IT DOES NOT. It checks that the flag is gone\nand cannot come back by accident: no `art_run` parameter, no `_art_run`\nbinding, nothing threading an art-layer flag into the site spec builder. That\nis a STRUCTURAL check. It does NOT run two invocations and compare the\narchetypes they select -- that needs a workspace, Deli Counter output and a\nlibrary on disk, which is `tests/integration`\'s job. Said plainly here so\nnobody later reads a green tick as more than it is.\n\nRun:  python -m pytest tests/unit/test_draw_is_invocation_independent.py\n"""\nimport inspect\n\nfrom apps.cli import commands as cmds\n\n\ndef test_the_site_spec_builder_cannot_be_told_about_the_art_layer():\n    sig = inspect.signature(cmds._write_site_spec)\n    assert "art_run" not in sig.parameters, (\n        "the pool a mission draws from is a property of its BRIEF, not of the "\n        "command that happens to be running -- see roadmap item 48")\n\n\ndef test_no_caller_still_passes_one():\n    src = inspect.getsource(cmds)\n    assert "art_run" not in src, (\n        "a caller still threads an art-layer flag into the site spec builder")\n\n\ndef test_the_pool_is_not_decided_by_reading_the_planned_graph():\n    """The specific shape that caused it: a binding computed from\n    `plan.graph.jobs()` and then used as a POOL decision. Reading the graph\n    for other reasons is fine, so this looks for that binding by name."""\n    assert "_art_run" not in inspect.getsource(cmds)\n\n\ndef test_the_narrowing_still_happens():\n    """The other half, and the one worth being nervous about. Removing the\n    flag must not have removed the narrowing with it -- a greybox pass that\n    draws from the WIDE pool is the original defect wearing the fix\'s\n    clothes."""\n    assert "require_themed_shells" in inspect.getsource(cmds._write_site_spec)\n\n\ndef test_it_is_reached_only_when_the_brief_asks_for_a_lot():\n    """`lot_library` is the key that gates the art layer, and it is what the\n    narrowing is now keyed on. A mission without it must not reach this at\n    all, so existing single-shell missions keep their row byte-for-byte."""\n    src = inspect.getsource(cmds._write_site_spec)\n    head = src[:src.index("require_themed_shells")]\n    assert \'library = getattr(model, "lot_library", None)\' in head\n    assert "if library and" in head\n'

CHANGELOG_ENTRY = '## [0.38.0] - the pool a mission draws from is a property of the mission\n\n`unlit_probe_001`, one fresh workspace, one candidate, seed 5017, run once\nfrom empty. `lot_assemble.candidate.seed_5017` succeeded twice and produced\ntwo different sites.\n\n    batch create                    123 shells -> cr_garage\n    run --art --unlit --gameplay     98 shells -> landmark_hall_a03\n\n    graybox   17 openings, 178 colliders, 12 markers\n    art       13 openings, 176 colliders,  7 markers\n    shell.glb sha256:a929d7d2... in BOTH -- same lot, different building\n\nEverything that graded the mission ran under `batch create` and measured\n`cr_garage`: walktest nav QA, Laser Tag, the structural checks, and the\nfunctional lock. The package would have shipped `landmark_hall_a03`.\n\nTHE MECHANISM WAS ONE BOOLEAN\n\n    commands/__init__.py:238   _art_run = any(j.stage_id == "themed_site_assemble"\n                                              for j in plan.graph.jobs())\n    commands/__init__.py:942   if themed_map or art_run:   # narrow 123 -> 98\n\n`_art_run` described THE INVOCATION, not the mission. `batch create` plans no\nart layer; `run --art` plans one.\n\nAND THE GATE IT SAT IN WAS ITSELF A FIX\n\nThe greybox branch started narrowing because `probe_pool_divergence.py` had\nmeasured that on lot_demo_001, 14 of 15 building slots already carried an\narchetype other than the one Laser Tag graded and 13 graded archetypes never\nshipped at all. "Grade the pool that ships" was the right goal. It made the\ntwo passes agree within one invocation and could not make them agree across\ninvocations -- so the divergence moved from inside a run to between the run\nthat grades and the run that ships, where only the functional lock stands.\n\nTHE FIX\n\nThe narrowing is keyed on the BRIEF. Reaching that line already means\n`lot_library` is set, which is also what gates the art layer, so the pool is\nnow the same in every invocation of a mission\'s life. `art_run` is gone from\nthe signature, the call site and the module.\n\nTHE COST, STATED: a brief that sets `lot_library` and never runs `--art` now\ndraws from the narrower pool too -- 98 of 123 shells. Missions without\n`lot_library` are untouched byte-for-byte.\n\nWHAT THIS DOES NOT DO. Missions already built with `lot_library` will\nre-select buildings on their next run, and their existing grades stop\ndescribing them. That is the point -- those grades already described a\ndifferent level -- but it is not free, and `--force` is what re-runs it.\nWhether the draw may move behind `candidate_selected` AT ALL is roadmap item\n48 question 1 and is still open.\n\nEvidence, in the repo because `_runs/` is gitignored:\n`docs/findings/ITEM48_THE_DRAW_MOVED.md`.\n\n'

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(body: str) -> str:
    """KEYED OFF THE FILE, never off an anchor."""
    crlf = body.count(_CRLF)
    return _CRLF if crlf > (body.count("\n") - crlf) else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _write(p: Path, raw: bytes, data: bytes, *, check: bool, label: str) -> None:
    if check:
        print(f"  would patch  {label}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})")
        return
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file() and raw:
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {label}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")


def _apply(root: Path, *, check: bool) -> int:
    p = root / CMDS
    if not p.is_file():
        print(f"REFUSING: {CMDS} is not here -- run from the factory root")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)

    out = body
    done = 0
    for old, new in EDITS:
        o, n = _as(old, eol), _as(new, eol)
        if n in out:
            done += 1
        elif out.count(o) == 1:
            out = out.replace(o, n, 1)
        else:
            print(f"REFUSING: an anchor occurs {out.count(o)} time(s), "
                  f"expected 1:\n    {old.strip().splitlines()[0][:72]}")
            return 1
    if done and done != len(EDITS):
        print(f"REFUSING: {done} of {len(EDITS)} edits are already present "
              f"-- {CMDS} is half-patched. Revert or fix by hand.")
        return 1

    # The whole point of this patch is a name that no longer exists.
    if not done and "art_run" in out:
        print("REFUSING: `art_run` still appears after the edits -- there is "
              "a caller this patch does not know about")
        return 1

    if done == len(EDITS):
        print(f"  already applied  {CMDS}")
    else:
        _write(p, raw, out.encode("utf-8"), check=check, label=CMDS)

    # -- the test ------------------------------------------------------
    t = root / TESTF
    if t.is_file() and t.read_bytes().decode("utf-8").replace(_CRLF, "\n") \
            == TEST_SRC:
        print(f"  already there    {TESTF}")
    elif check:
        print(f"  would create {TESTF}  {len(TEST_SRC.encode()):,} bytes")
    else:
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_bytes(TEST_SRC.encode("utf-8"))
        print(f"  created      {TESTF}  "
              f"{len(TEST_SRC.encode()):,} bytes")

    # -- VERSION -------------------------------------------------------
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

    # -- CHANGELOG -----------------------------------------------------
    c = root / CHANGELOG
    craw = c.read_bytes()
    cbody = craw.decode("utf-8")
    ceol = _eol(cbody)
    head = _as(f"## [{OLD_VER}] - ", ceol)
    if _as(f"## [{NEW_VER}] - ", ceol) in cbody:
        print(f"  already has {NEW_VER}  {CHANGELOG}")
    elif cbody.count(head) != 1:
        print(f"REFUSING: {CHANGELOG} has {cbody.count(head)} "
              f"'## [{OLD_VER}] - ' headings, expected 1")
        return 1
    else:
        cnew = cbody.replace(head, _as(CHANGELOG_ENTRY, ceol) + head, 1)
        _write(c, craw, cnew.encode("utf-8"), check=check, label=CHANGELOG)

    return 0


def _pytest(root: Path, *args: str) -> tuple[int, str]:
    """Run pytest in level_factory and return (rc, tail).

    RETURN CODE, not text. Two text detectors have already been wrong in this
    arc -- one matched a collection error as a pass. 0 = all passed,
    1 = tests failed, 5 = no tests collected (which is a FAILURE here, not a
    pass: it is what a broken import looks like).
    """
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        cwd=str(root / LF), capture_output=True, text=True)
    tail = (proc.stdout or "")[-1400:] + (proc.stderr or "")[-600:]
    return proc.returncode, tail


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    src = (root / CMDS).read_bytes().decode("utf-8")
    check("`art_run` is gone from the module entirely",
          "art_run" not in src)
    check("...including the binding read off the planned graph",
          "_art_run" not in src)
    check("the narrowing survived the flag's removal",
          "require_themed_shells" in src)
    check("it still sits inside the lot_library branch",
          src.index('library = getattr(model, "lot_library", None)')
          < src.index("require_themed_shells"))
    check("the site spec builder's signature lost the parameter",
          "themed_scene: str | None = None) -> Path:" in src)
    check("the module still compiles",
          _compiles(root / CMDS))

    check("the new test exists", (root / TESTF).is_file())
    check("...and says what it does NOT check",
          "It does NOT run two invocations"
          in (root / TESTF).read_text(encoding="utf-8"))

    check(f"VERSION is {NEW_VER}",
          (root / VERSION).read_text(encoding="utf-8").strip() == NEW_VER)
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check(f"CHANGELOG leads with {NEW_VER}",
          cl.lstrip().startswith(f"## [{NEW_VER}]"))
    check("...and states the cost rather than only the fix",
          "THE COST, STATED" in cl and "98 of 123 shells" in cl)
    check("...and points at the preserved evidence",
          "docs/findings/ITEM48_THE_DRAW_MOVED.md" in cl)

    print()
    print("  running the new test file")
    rc, tail = _pytest(root, "tests/unit/test_draw_is_invocation_independent.py")
    check(f"the new tests pass (pytest rc={rc})", rc == 0)
    if rc != 0:
        print(tail)

    print()
    print("  running tests/unit WHOLE -- 659 of them went unrun for four")
    print("  releases in this arc while 28 were reported as 'still green'")
    rc2, tail2 = _pytest(root, "tests/unit")
    check(f"tests/unit passes (pytest rc={rc2})", rc2 == 0)
    if rc2 != 0:
        print(tail2)

    print()
    print("  the draw is a property of the brief now"
          if not bad else f"  {bad} FAILURE(S)")
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
        for rel in (CMDS, CHANGELOG):
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
        print("    python patches\\patch_lf_038.py --selftest")
        print()
        print("  then the suites the selftest does not run:")
        print("    cd level_factory && python -m pytest tests")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
