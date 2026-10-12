"""Run `python -m level_factory <args>` under cProfile, keep the profile, and exit with the leg's code.

`cold_drive.sh`'s `PROFILE_LEGS=1` switch ran `python -m cProfile -o <file> -m level_factory`, and
cProfile's own runner swallows a script's SystemExit: cold run 9250's art leg, which exits 1 while
the pipeline waits at an approval gate, printed `exit 0`. The drive gates on each leg's output
lines, so nothing depended on it -- but a switch that changes what a run reports is not a probe.
This keeps the code.

    python tools/cold_drive/profile_leg.py <profile file> <level_factory args...>
"""
import cProfile
import os
import runpy
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def main():
    out, args = sys.argv[1], sys.argv[2:]
    sys.path.insert(0, ROOT)          # `level_factory` itself, as `python -m` finds it from the root
    sys.argv = ["level_factory"] + args
    prof = cProfile.Profile()
    code = 0
    try:
        prof.runcall(runpy.run_module, "level_factory", run_name="__main__", alter_sys=True)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    finally:
        prof.dump_stats(out)
    sys.exit(code)


if __name__ == "__main__":
    main()
