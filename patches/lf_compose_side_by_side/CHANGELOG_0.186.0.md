## [0.186.0] - A job's independent commands run side by side, and job.log keeps every command

**Why now.** Roadmap 239, the art leg. With Blender three at a time (0.185.0)
cold run 9251's art leg took 177 s, and its largest block was one job: the
compose, 64 s, its sixteen commands -- the mission's shell and one per
building -- run one after another. The buildings do not depend on each
other: each command clears and writes only its own folder under the lot's.
And the job's `job.log` held only the last building's output, because each
command rewrote it -- which a session read as the job's whole command time
(cold run 9249's note, refuted in 9250's).

**What changed.**

- `PlannedCommand.parallel` (default False, in `as_dict` only when set): a
  command that may run beside the parallel commands next to it.
- `Scheduler._run_commands` runs a job's commands: a run of consecutive
  parallel commands side by side, up to the job's class width (`python_cpu`
  4), every other command alone and in turn; results come back in plan
  order, so a failure is handled where it was before, and a command after a
  failure in turn is never started.
- `job.log` holds every command: a job of several writes each to its own
  part and joins the parts in plan order. A job of one command writes it as
  before.
- The compose adapter marks the per-building composes parallel. The mission
  shell's compose stays first and alone: Deli Counter's `build_package`
  clears its output folder before writing, and that folder holds the
  buildings'.

**Measured:** cold run 9251's compose job replayed from its workspace index, its sixteen commands into scratch folders (docs/findings/grader_speed/compose_replay_ab.py): in turn 58.3 and 58.2 s, the shell's first and alone and the fifteen buildings four at a time 25.4 s (a first run: 59.2, 58.5 and 25.5 s); 928 files in each arm, none different between the two runs in turn or between in turn and side by side, and 928 of 928 identical to the run's own compose output, its other 928 files the scheduler's provenance sidecars; the deli and the office exit 3 on Deli Counter's z-fight gate in every arm as they did in the run, advisory as before (compose_replay_ab.out.txt)

**Tests:** `tests/unit/test_commands_side_by_side.py`, seven (a command is not
parallel unless it says so; parallel commands run at once and report in plan
order; `job.log` keeps every command of a job run in turn; a job of one
command writes it as before; a width of one runs them in turn with a failure
reported in place; a caller that stops at a failure never starts what
follows; the buildings compose side by side and the shell first alone), all
failing on 0.185.0. 2,286 passed, 16 skipped, 0 failed (JUnit, 2,302 tests)
