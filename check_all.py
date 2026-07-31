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
    gdscript     gdcheck.py           every .gd in the tree: grammar plus the
                                      three traps a grammar cannot see

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

ROOT = pathlib.Path(__file__).resolve().parent

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
    ("walk sweep", "python library_walk.py --timeout 1800",
     "needs Godot; about an hour for 20 sites"),
    ("pack loads", "python lot\\package.py <spec> --walkable --check <godot>",
     "needs a built pack and Godot"),
    ("unit tests", "cd lot && python -m pytest tests -q",
     "and the same in deli_counter"),
]


def gd_files():
    """Every .gd in the tree, minus scratch and editor backups."""
    out = []
    for p in ROOT.rglob("*.gd"):
        s = str(p)
        if any(part in s for part in ("_bridge", "__pycache__", "_scratch_archive",
                                      os.sep + "dist" + os.sep,
                                      os.sep + "_runs" + os.sep, ".godot")):
            continue
        out.append(str(p))
    return sorted(out)


def run(key, script, args):
    """(state, exit_code, first_meaningful_line). state is ok / found / cannot."""
    path = ROOT / script
    if not path.exists():
        return "cannot", None, f"{script} is not at the factory root"
    argv = [sys.executable, str(path)]
    for a in args:
        if a == "@gd":
            files = gd_files()
            if not files:
                return "cannot", None, "no .gd files found to check"
            argv += files
        else:
            argv.append(a)
    try:
        r = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT))
    except OSError as e:
        return "cannot", None, f"{type(e).__name__}: {e}"
    out = (r.stdout or "") + (r.stderr or "")
    tail = [l.strip() for l in out.splitlines() if l.strip()]
    if r.returncode == 0:
        state = "ok"
    elif r.returncode == 2:
        state = "cannot"
    else:
        state = "found"
    # the most useful line to surface: the summary if there is one, else the last
    summary = ""
    for l in reversed(tail):
        if any(w in l.lower() for w in ("every ", "no ", "clean", "site(s)",
                                        "building(s)", "transition", "walkable",
                                        "parses")):
            summary = l
            break
    return state, r.returncode, (summary or (tail[-1] if tail else ""))


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
            r = subprocess.run([sys.executable, str(ROOT / script)]
                               + ([] if argv != ["@gd"] else gd_files()),
                               cwd=str(ROOT))

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
