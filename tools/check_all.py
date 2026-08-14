"""One command that runs every guardrail and says what it could NOT check.

WHY THIS EXISTS. The checks accumulated one defect at a time and each one is
invoked differently, reports differently, and is remembered separately. That is
how a guardrail stops being respected: not by failing, but by nobody running it.
This is the single entry point, and it enforces one convention across all of them:

    exit 0   checked, clean
    exit 1   checked, found something
    exit 2   COULD NOT check

The third code is the one that matters and the one most tools omit. Four defects
in this toolchain survived because a check went quiet and quiet read as clean --
Write-Host not being pipeable, git's stderr sent to $null, walktest's inner
timeout, and a gate whose prints were indented past the filter that forwards them.
A runner that folded "could not check" into "clean" would reproduce the same
defect at the top level, so it is a separate column and a separate exit code.

WHAT IT RUNS, and what each one owns:

    steps        check_steps.py       a rise on a designed route that a body
                                      cannot walk up, read off the built .tscn
    freshness    check_freshness.py   geometry that no longer matches the spec
                                      and builder that made it, by content hash
    stairs       check_stair_pitch.py flights pitched past what a body stands on,
                                      read off each building's .glb
    gdscript     gdcheck.py           every .gd this repo owns: grammar plus
                                      the three traps a grammar cannot see.
                                      rockay-ws is skipped -- it is evidence
                                      rather than source, and it holds 342 of
                                      the tree's 446 .gd files

WHAT IT DOES NOT RUN, stated out loud rather than left to be assumed:

  * the walk sweep (library_walk.py) -- an hour, and it needs Godot
  * the pack engine check (package.py --check) -- needs a pack and Godot
  * deli_counter's and lot's pytest suites -- run those directly

Nothing here needs Blender or Godot, so it is the pass to run before those, not
instead of them.

    python check_all.py
    python check_all.py --only steps stairs
"""
import argparse
import os
import pathlib
import subprocess
import sys

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from factory_paths import factory_root                        # noqa: E402

#: TWO QUESTIONS, not one. SCRIPT_DIR finds the sibling checkers this script
#: shells out to; ROOT is the tree those checkers are pointed at. They were the
#: same directory while everything sat at the factory root, and stop being the
#: same the moment anything moves -- at which point gd_files() would scan the
#: tools directory, find a handful of .gd files instead of 104, and still print
#: `clean`.
ROOT = factory_root()

#: (key, script, args, what a non-zero exit means). Order is cheapest first so a
#: broken tree fails fast.
CHECKS = [
    ("gdscript", "gdcheck.py", ["@gd"],
     "a .gd file will not parse, or hits one of the three known traps"),
    ("freshness", "check_freshness.py", [],
     "a building's geometry no longer matches the spec or builder that made it"),
    ("stairs", "check_stair_pitch.py", [],
     "a flight is pitched past what a body can stand on"),
    ("steps", "check_steps.py", [],
     "a designed route crosses a rise a body cannot walk up"),
]

NOT_RUN = [
    ("walk sweep", "python tools\\library_walk.py --timeout 1800",
     "needs Godot; about an hour for 20 sites"),
    ("pack loads", "python lot\\package.py <spec> --walkable --check <godot>",
     "needs a built pack and Godot"),
    ("unit tests", "cd lot && python -m pytest tests -q",
     "and the same in deli_counter"),
]


#: Skipped, for two DIFFERENT reasons, kept apart because they would want
#: different answers if either changed:
#:
#:   generated  _scratch, __pycache__, dist, _runs, .godot. The
#:              `_scratch` entry replaced _bridge and _scratch_archive
#:              when those moved under it -- anything below that folder
#:              is scratch by construction, so the list cannot fall
#:              behind. `_runs` keeps its own entry because it has NOT
#:              moved: tools/factory_tidy.py still files measurements
#:              and dead sidecars into it by that name.
#:              Build output and staging copies. A finding here points at a
#:              copy, and the next reader patches a file that is not the file.
#:   evidence   rockay-ws. A mission workspace -- CLAUDE.md says read it, do
#:              not edit it. It holds 342 of the tree's 446 .gd files, so
#:              including it spent three quarters of this check raising
#:              findings nobody is permitted to act on.
#:
#: Anyone adding an entry has to say which of the two they are claiming.
SKIP_GENERATED = ("__pycache__", "_scratch" + os.sep,
                  os.sep + "dist" + os.sep, os.sep + "_runs" + os.sep,
                  ".godot")
SKIP_EVIDENCE = (os.sep + "rockay-ws" + os.sep,)

#: Windows refuses a command line over 32767 characters, and CreateProcess then
#: raises WinError 206 -- "the filename or extension is too long". Measured at
#: 70,029 characters across 446 files, so the gdscript check never launched at
#: all and printed NOT CHECKED beside three checks that had run. The budget is
#: derived from the ceiling rather than chosen as a file count, because a count
#: that is right today goes wrong the next time paths lengthen or a repo joins.
ARGV_CEILING = 32767
ARGV_BUDGET = ARGV_CEILING - 768   # room for the interpreter path and quoting


def gd_files():
    """Every .gd this repo owns -- see SKIP_GENERATED and SKIP_EVIDENCE."""
    out = []
    for p in ROOT.rglob("*.gd"):
        s = str(p)
        if any(part in s for part in SKIP_GENERATED + SKIP_EVIDENCE):
            continue
        out.append(str(p))
    return sorted(out)


def batched(base, files):
    """`files` split so no single command line approaches ARGV_CEILING.

    Returns a list of file-lists to append to `base`, never empty, so a caller
    can loop over it unconditionally.
    """
    room = ARGV_BUDGET - sum(len(x) + 1 for x in base)
    groups, cur, used = [], [], 0
    for f in files:
        if cur and used + len(f) + 1 > room:
            groups.append(cur)
            cur, used = [], 0
        cur.append(f)
        used += len(f) + 1
    if cur:
        groups.append(cur)
    return groups or [[]]


def run(key, script, args):
    """(state, exit_code, first_meaningful_line). state is ok / found / cannot."""
    # SIBLING, not subject. ROOT is the tree being checked; the checkers live
    # beside this file. Identical answers until something moved.
    path = SCRIPT_DIR / script
    if not path.exists():
        return "cannot", None, (f"{script} is not beside check_all.py "
                                f"(looked in {SCRIPT_DIR})")
    base = [sys.executable, str(path)]
    plain = [a for a in args if a != "@gd"]
    if "@gd" in args:
        files = gd_files()
        if not files:
            return "cannot", None, "no .gd files found to check"
        groups = batched(base + plain, files)
    else:
        groups = [[]]

    outs, codes = [], []
    for g in groups:
        try:
            r = subprocess.run(base + plain + g, capture_output=True,
                               text=True, cwd=str(ROOT))
        except OSError as e:
            return "cannot", None, f"{type(e).__name__}: {e}"
        outs.append((r.stdout or "") + (r.stderr or ""))
        codes.append(r.returncode)
    out = "".join(outs)
    tail = [l.strip() for l in out.splitlines() if l.strip()]
    # Worst wins. A batch that could not check makes the whole row "could not
    # check"; a batch with findings makes it "found"; and a clean batch never
    # upgrades a dirty one. Reading only the last exit code would let a clean
    # final batch report success over an earlier failure, which is precisely
    # the substitution this runner exists to stop at the top level.
    if 2 in codes:
        state, code = "cannot", 2
    elif any(c != 0 for c in codes):
        state, code = "found", next(c for c in codes if c != 0)
    else:
        state, code = "ok", 0
    if len(groups) > 1:
        tail.append(f"checked in {len(groups)} batches "
                    f"({sum(len(g) for g in groups)} files)")
    # the most useful line to surface: the summary if there is one, else the last
    summary = ""
    for l in reversed(tail):
        if any(w in l.lower() for w in ("every ", "no ", "clean", "site(s)",
                                        "building(s)", "transition", "walkable",
                                        "parses")):
            summary = l
            break
    return state, code, (summary or (tail[-1] if tail else ""))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", nargs="*", default=None,
                    help="run only these checks: "
                         + ", ".join(k for k, _s, _a, _w in CHECKS))
    ap.add_argument("--verbose", action="store_true",
                    help="show each check's full output")
    args = ap.parse_args()

    todo = [c for c in CHECKS if not args.only or c[0] in set(args.only)]
    if not todo:
        print(f"no checks named {args.only}")
        return 2

    results = []
    for key, script, argv, means in todo:
        state, code, line = run(key, script, argv)
        results.append((key, state, code, line, means))
        if args.verbose:
            print(f"\n=========== {key} ===========")
            # Batched here too. This path had the same unbounded argv and would
            # have failed the same way, quietly, since its result was discarded.
            _base = [sys.executable, str(SCRIPT_DIR / script)]
            _groups = batched(_base, gd_files()) if argv == ["@gd"] else [[]]
            for _g in _groups:
                subprocess.run(_base + _g, cwd=str(ROOT))

    width = max(len(k) for k, *_ in results) + 2
    print(f"  {'check':<{width}}{'result':<10}{'exit':>5}   detail")
    print("  " + "-" * (width + 60))
    for key, state, code, line, _means in results:
        label = {"ok": "clean", "found": "FINDINGS",
                 "cannot": "NOT CHECKED"}[state]
        print(f"  {key:<{width}}{label:<10}{'' if code is None else code:>5}"
              f"   {line[:70]}")

    found = [r for r in results if r[1] == "found"]
    cannot = [r for r in results if r[1] == "cannot"]

    print()
    for key, _s, _c, _l, means in found:
        print(f"  {key}: {means}")
        print(f"    python {dict((k, s) for k, s, _a, _w in CHECKS)[key]}")
    for key, _s, _c, line, _m in cannot:
        print(f"  {key}: NOT CHECKED -- {line}")
    if cannot:
        print("    A check that did not run is not a check that passed.")

    print("\n  Not run here, and not covered by the result above:")
    for name, cmd, why in NOT_RUN:
        print(f"    {name:<12}{cmd}")
        print(f"    {'':<12}({why})")

    if found:
        return 1
    return 2 if cannot else 0


if __name__ == "__main__":
    raise SystemExit(main())
