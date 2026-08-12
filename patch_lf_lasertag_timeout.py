r"""The Laser Tag job's timeout scales with the number of runs it asked for.

    python patch_lf_lasertag_timeout.py --check
    python patch_lf_lasertag_timeout.py
    python patch_lf_lasertag_timeout.py --revert

## The defect

`LaserTagAdapter.plan_commands` reads the run count from the job spec --

    runs = job_spec.get("run_count", 25)

-- and then plans the command with a flat `timeout_seconds=900`. The two are
unrelated numbers, and 900 was sized when the default was 8.

Measured 2026-08-09, `lot_demo_001` candidate 5017 at 25 runs. Every run went
its full clock, Godot was killed at 900.1 s nineteen runs in, no report was
written, and the job came back `JOB_TIMEOUT` -- for a level whose route
`walktest_navqa` walks clean (four walkers, 18/18 targets, ~875 m, verdict
PASS, zero stranded anchors). A blocked mission, on a working level, because a
ceiling did not scale with the work under it.

    (exit=3221225786, duration=900.1s, timed_out=True, cancelled=False)

`3221225786` is `STATUS_CONTROL_C_EXIT`: the scheduler's own timeout handler
killing the child with a console control event. It is not a crash and not an
interrupted terminal.

## Why the budget is not derived from the scenario

`default_laser_tag_scenario.tres` declares `max_run_time_seconds = 180.0`, and
that is the obvious number to multiply by. It is the wrong one: it is
SIMULATED time, and the harness runs the simulation faster than real time.
Nineteen runs of 180 simulated seconds cost 900 seconds of wall clock -- 47.4 s
each. Multiplying 25 by 180 would reserve 4,500 s for work that takes about
1,200.

So the per-run figure here is a measured wall-clock budget, and it says so.
Nothing pretends it was read from a contract, because it was not.

## The change

Two named budgets on the adapter, and a timeout computed from them:

    timeout = bake_wall_budget_seconds + runs * run_wall_budget_seconds

At the current 25 runs that is 120 + 1500 = 1,620 s against the observed
~1,200 s worst case. At the old 8-run default it is 600 s -- tighter than the
900 it replaces, which is the right direction: a job that hangs should be
killed sooner, not later, and the number should follow the work.

## Noted, not fixed

`run_count` is declared twice: `25` in the scenario resource and `25` again as
the default in `job_spec.get("run_count", 25)`. LF passes `--runs` on the
command line, so its value wins and the scenario's is decorative -- but the two
agree today by coincidence, not by construction. That is the same shape as
every other duplicated constant in this toolchain and belongs on the roadmap
rather than in this patch.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("level_factory") / "adapters" / "laser_tag" / "__init__.py"
SIDECAR = ".pre_lttimeout"


BUDGETS_OLD = '''    output_contract_version = "lasertag.report.0.7"'''

BUDGETS_NEW = '''    output_contract_version = "lasertag.report.0.7"

    #: Wall-clock budget for ONE evaluation run, in seconds.
    #:
    #: NOT the scenario's `max_run_time_seconds` (180.0). That is SIMULATED
    #: time and the harness runs the simulation faster than real time:
    #: measured 2026-08-09 on a level where every run went its full clock,
    #: nineteen runs cost 900 s of wall time, 47.4 s each. Multiplying the
    #: simulated figure by the run count would reserve 4,500 s for about
    #: 1,200 s of work.
    #:
    #: A run that ENDS early costs a fraction of this -- the same job took
    #: 160.85 s for 25 runs on a level whose runs wiped in 20-31 s. This has to
    #: cover the worst case, which is every run stalemating to its cap.
    run_wall_budget_seconds = 60.0

    #: Load, navmesh bake and position sampling, paid once before the first
    #: run. Roughly 20 s for a 1041-polygon bake over 34,356 source vertices;
    #: tripled, because it is paid once and a slow machine should not lose a
    #: report over it.
    bake_wall_budget_seconds = 120.0'''


TIMEOUT_OLD = '''        return [
            PlannedCommand(
                executable=godot,
                arguments=tuple(args),
                working_directory=Path(str(project)),
                expected_outputs=("lasertag.report.json", "lasertag.report.csv"),
                resource_class="godot_headless",
                timeout_seconds=900,
            )
        ]'''

TIMEOUT_NEW = '''        # Scaled by the run count, because that is the thing that varies. The
        # flat 900 s this replaces was sized for the 8-run default and became a
        # ceiling no 25-run mission could pass under: measured 2026-08-09,
        # Godot was killed nineteen runs in, the report was never written, and
        # the job reported JOB_TIMEOUT for a level `walktest_navqa` walks clean.
        #
        # A ceiling that does not follow the work is not a safety net; it is a
        # second thing to keep in sync, and it was already out of sync.
        timeout = int(self.bake_wall_budget_seconds
                      + max(1, int(runs)) * self.run_wall_budget_seconds)
        return [
            PlannedCommand(
                executable=godot,
                arguments=tuple(args),
                working_directory=Path(str(project)),
                expected_outputs=("lasertag.report.json", "lasertag.report.csv"),
                resource_class="godot_headless",
                timeout_seconds=timeout,
            )
        ]'''


EDITS = ((BUDGETS_OLD, BUDGETS_NEW), (TIMEOUT_OLD, TIMEOUT_NEW))
_CRLF = "\r\n"


def _find(body: str, anchor: str) -> tuple[str, int]:
    for candidate in (anchor, anchor.replace("\n", _CRLF)):
        count = body.count(candidate)
        if count:
            return candidate, count
    return anchor, 0


def main(argv: list[str]) -> int:
    path = Path.cwd() / TARGET
    if not path.is_file():
        raise SystemExit(f"cannot find {TARGET} -- run from the factory root")
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)

    if "--revert" in argv:
        if not side.is_file():
            print(f"no sidecar at {side.name}")
            return 2
        path.write_bytes(side.read_bytes())
        print(f"  reverted   {path.name}")
        return 0

    done = sum(1 for _o, new in EDITS if _find(body, new)[1] == 1)
    if done == len(EDITS):
        print("  already applied")
        return 0
    if done:
        print(f"REFUSING: {done} of {len(EDITS)} edits already present")
        return 1

    out = body
    for old, new in EDITS:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: expected 1 occurrence of an anchor, found "
                  f"{count}: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(
            anchor, new.replace("\n", _CRLF) if _CRLF in anchor else new, 1)
    data = out.encode("utf-8")

    if "--check" in argv:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})")
    print(f"  sha256       {hashlib.sha256(data).hexdigest()[:16]}")
    print()
    print("  25 runs -> 120 + 25*60 = 1620 s   (was a flat 900)")
    print("   8 runs -> 120 +  8*60 =  600 s   (tighter, on purpose)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
