r"""level_factory 0.37.0 (amendment) -- the 656 tests nobody was running.

    python patches\patch_lf_037c.py --check
    python patches\patch_lf_037c.py
    python patches\patch_lf_037c.py --selftest
    python patches\patch_lf_037c.py --revert

Run from the FACTORY ROOT. Apply AFTER patch_lf_037b.py.

THE PROCESS FAILURE FIRST, BECAUSE IT IS THE BIGGER ONE

Four releases -- 0.34.0, 0.35.0, 0.36.0, 0.37.0 -- each reported "still
green" against `tests/service` and `tests/integration`: 28 tests. The unit
suite is 656, and nothing in this arc ran it. `tests/unit/test_fanout.py`
has been failing since 0.35.0 and said so to nobody.

Every selftest from here runs `tests/unit` whole. A subset that is described
as the suite is the same instrument failure this release is about, one level
up: a green reading that covers less than it appears to.

THREE FAILURES, AND THEY ARE NOT THE SAME KIND

1. test_fanout.py::test_placement_stages_fan_out_and_libraries_do_not

       assert len(_stages(plan, stage)) == 1, stage
       AssertionError: lux_apply  --  0 == 1

   MINE, from 0.35.0. Its `_plan` helper asks for `layers={LAYER_ART}` and
   then asserts `lux_apply` is planned once. That was true when LAYER_ART
   meant "and Lux"; the layer set it requests is what changed. 0.35.0
   updated four such assertions in `test_planner_graph.py` and missed this
   file entirely, because I looked in the file I already knew about instead
   of asking which tests mention the stage I was moving.

   `grep -rn lux_apply level_factory/tests` would have found it in one
   command, and is what the CHANGELOG for 0.35.0 should have recorded doing.

2. test_closure_export.py::test_export_pure_shell_drops_presentation
3. test_closure_export.py::test_export_zip_is_deterministic

   NOT mine, and not wrong exactly. Both build a handoff whose only scene is
   `mission.tscn` -- and `write_entry_scene` OVERWRITES `mission.tscn` with
   its stub, so after the export there is nothing left to instance. The
   fixtures have always described a package that opens to nothing; before
   0.37.0 nothing objected.

   They gain a `site.tscn`, which is what a real handoff-based package has
   underneath it and what 0.37.0b now guarantees for pure-shell. Neither test
   is weakened: one still asserts Lux's files are dropped, the other still
   asserts the zip is deterministic.

   That these two fixtures produced empty packages for as long as they have
   existed is the same finding as lot_demo_001's art-unlit export, in
   miniature, and it is why the guard belongs in `write_entry_scene` rather
   than in any one mode.

WHAT IS STILL UNMEASURED

Whether `tests/unit` has other failures behind these three. 656 tests ran
once, at 3 failed / 653 passed, and that reading is from the run that
produced this patch -- not from a green one. The selftest here runs the whole
suite and reports the count, so the next claim about it is a measurement.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

FANOUT = "level_factory/tests/unit/test_fanout.py"
CLOSURE_TEST = "level_factory/tests/unit/test_closure_export.py"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_037c"

EDITS: list[tuple[str, str, str]] = [
    # --------------------------------------------------- 0.35.0's other file
    (FANOUT,
     "from packages.pipeline.planner import LAYER_ART, plan_mission\n",

     "from packages.pipeline.planner import LAYER_ART, LAYER_LIGHT, plan_mission\n"),

    (FANOUT,
     "def _plan(brief: MissionBrief):\n"
     "    plan = plan_mission(brief, seed_base=SEED_BASE, layers={LAYER_ART})\n"
     "    return plan_mission(brief, seed_base=SEED_BASE, layers={LAYER_ART},\n"
     "                        selected_candidate=plan.candidate_ids[0])\n",

     "def _plan(brief: MissionBrief):\n"
     "    # ART + LIGHT since 0.35.0. `lux_apply` moved behind its own layer,\n"
     "    # and this file asserts it is planned exactly once -- so it has to ask\n"
     "    # for the layer that plans it. 0.35.0 updated the same assertions in\n"
     "    # test_planner_graph.py and missed this file, which then failed\n"
     "    # unnoticed through three releases because nothing ran tests/unit.\n"
     "    layers = {LAYER_ART, LAYER_LIGHT}\n"
     "    plan = plan_mission(brief, seed_base=SEED_BASE, layers=layers)\n"
     "    return plan_mission(brief, seed_base=SEED_BASE, layers=layers,\n"
     "                        selected_candidate=plan.candidate_ids[0])\n"),

    # ------------------------------------------ the two hollow-package fixtures
    (CLOSURE_TEST,
     "def test_export_pure_shell_drops_presentation(tmp_path):\n"
     "    handoff = tmp_path / \"handoff\"\n"
     "    handoff.mkdir()\n"
     '    (handoff / "mission.tscn").write_text("[gd_scene]\\n")\n'
     '    (handoff / "gameplay_anchors.json").write_text("{}")\n',

     "def test_export_pure_shell_drops_presentation(tmp_path):\n"
     "    handoff = tmp_path / \"handoff\"\n"
     "    handoff.mkdir()\n"
     '    (handoff / "mission.tscn").write_text("[gd_scene]\\n")\n'
     "    # THE PACKAGE NEEDS SOMETHING TO OPEN. `write_entry_scene` overwrites\n"
     "    # mission.tscn with its own stub, so a handoff whose only scene is\n"
     "    # mission.tscn exports to a package that instances nothing -- which\n"
     "    # this fixture did from the day it was written, and which 0.37.0's\n"
     "    # guard now refuses. A real handoff-based package has the site\n"
     "    # underneath it; 0.37.0b makes that true for pure-shell.\n"
     '    (handoff / "site.tscn").write_text("[gd_scene]\\n")\n'
     '    (handoff / "gameplay_anchors.json").write_text("{}")\n'),

    (CLOSURE_TEST,
     "def test_export_zip_is_deterministic(tmp_path):\n"
     "    handoff = tmp_path / \"handoff\"\n"
     "    handoff.mkdir()\n"
     '    (handoff / "mission.tscn").write_text("[gd_scene]\\n")\n',

     "def test_export_zip_is_deterministic(tmp_path):\n"
     "    handoff = tmp_path / \"handoff\"\n"
     "    handoff.mkdir()\n"
     '    (handoff / "mission.tscn").write_text("[gd_scene]\\n")\n'
     "    # Same reason as above: the entry stub replaces mission.tscn, so\n"
     "    # without this the package has nothing to instance. What this test\n"
     "    # asserts -- that the zip is deterministic -- is unchanged.\n"
     '    (handoff / "site.tscn").write_text("[gd_scene]\\n")\n'),

    (CHANGELOG,
     "Whether it is still right is unmeasured.\n",

     "Whether it is still right is unmeasured.\n"
     "\n"
     "AMENDED AGAIN -- THE 656 TESTS NOBODY WAS RUNNING\n"
     "\n"
     "0.34.0, 0.35.0, 0.36.0 and 0.37.0 each reported \"still green\" against\n"
     "`tests/service` and `tests/integration`: 28 tests. `tests/unit` is 656,\n"
     "and nothing in this arc ran it. `test_fanout.py` had been failing since\n"
     "0.35.0 and said so to nobody. Every selftest from here runs `tests/unit`\n"
     "whole -- a subset described as the suite is this release's own subject,\n"
     "one level up.\n"
     "\n"
     "test_fanout.py's `_plan` asked for `layers={LAYER_ART}` and asserted\n"
     "`lux_apply` is planned once. 0.35.0 fixed exactly that in\n"
     "test_planner_graph.py and missed this file, because the search was \"the\n"
     "file I know about\" rather than `grep -rn lux_apply tests`.\n"
     "\n"
     "The two closure fixtures build a handoff whose only scene is\n"
     "`mission.tscn` -- which `write_entry_scene` overwrites with its stub, so\n"
     "they have described a package that opens to nothing since the day they\n"
     "were written. They gain a `site.tscn`. Neither assertion is weakened.\n"
     "That is lot_demo_001's empty art-unlit package in miniature, and it is\n"
     "why the guard lives in `write_entry_scene` rather than in a mode.\n"),
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
    import re
    import subprocess
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = (root / "level_factory").resolve()

    def run(*paths):
        return subprocess.run([sys.executable, "-m", "pytest", *paths],
                              cwd=str(lf), capture_output=True, text=True)

    # THE WHOLE SUITE. Not a subset described as the suite.
    print("  tests/unit -- ALL of it, which nothing in this arc had run --")
    r = run("tests/unit")
    tail = (r.stdout + r.stderr).strip().splitlines()
    for line in tail[-6:]:
        print(f"       {line}")
    check("THE UNIT SUITE IS GREEN", r.returncode == 0)

    # Say the number. "green" without a count is how 28 stood in for 656.
    m = re.search(r"(\d+) passed", r.stdout + r.stderr)
    if m:
        print(f"       {m.group(1)} tests passed")
        check("and it is the whole suite, not a corner of it",
              int(m.group(1)) > 500)
    else:
        check("the run reported a count", False)

    print()
    print("  service + integration -- ~2.5 min --")
    r2 = run("tests/service", "tests/integration")
    for line in (r2.stdout + r2.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("STILL GREEN", r2.returncode == 0)

    fan = (root / FANOUT).read_text(encoding="utf-8")
    check("test_fanout asks for the layer that plans lux_apply",
          "layers = {LAYER_ART, LAYER_LIGHT}" in fan)

    ct = (root / CLOSURE_TEST).read_text(encoding="utf-8")
    check("both closure fixtures give the package something to open",
          ct.count('(handoff / "site.tscn").write_text') == 2)

    # The search that would have caught it in 0.35.0, run now.
    hits = sorted(
        p.relative_to(lf).as_posix()
        for p in (lf / "tests").rglob("*.py")
        if "lux_apply" in p.read_text(encoding="utf-8", errors="replace"))
    print()
    print("  files mentioning lux_apply (the grep 0.35.0 should have run):")
    for h in hits:
        print(f"       {h}")

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check("the entry names the process failure, not just the three tests",
          "656" in flat and "nothing in this arc ran it" in flat)

    print()
    print("  the suite is the suite"
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
        for rel in (FANOUT, CLOSURE_TEST, CHANGELOG):
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
        print("    python patches\\patch_lf_037c.py --selftest")
        print()
        print("  That selftest runs tests/unit WHOLE. It is slower and it is")
        print("  the point.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
