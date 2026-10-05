# Cold run 9163 -- STOPPED in the shell leg: the disk was full. Not a result.

gas_block_001, seed 9080. The stack:
- Deli Counter 0.186.0: an Empty's door is shut to a ray (roadmap 183).
- Patina 0.29.1: no gutter on an Empty's party wall (roadmap 184).

**What happened.** The shell leg stopped at 16:39 with `STOPPED: shell leg`.
- **The driver** printed no `candidates:` line, so its `blockers open: 0`
  check failed.
- **The workspace's job index** (`index.sqlite`, read-only) still had
  `laser_tag_evaluate` for seed 9181 as RUNNING, with no exit code. Seed
  9282 had no laser-tag or walk job recorded.
- **That job's log** ends `exit=0, duration=984.17s`. Its `lasertag.report.json`
  and `.csv` are **0 bytes**: created, never written.
- **C: had 0.14 GB free.**

**This is not the stack's doing.**
- **Seed 9181's evaluation looks as it did before:** 984 s and 1,667
  "player stuck", against 956 to 985 s and 1,549 to 1,649 in cold runs 9160
  to 9162.
- **The run never reached** the art, export and walk legs where either
  change would show.

**What filled the disk.** This session's own measurement copies: 42 package
copies in `_runs/perf_inner/`, each with its import cache, at 230 to 290 MB,
plus three experiment packages.
- **Removed**, keeping every report beside them (`<tag>.json`,
  `<tag>.log`), which is what the committed price files were computed from.
- **The 75 older copies** from earlier sessions are untouched.
- **10.7 GB free** afterwards.
- **Still for the walker:** the drive holds 454 of 465 GB, and each cold-run
  workspace keeps about 0.6 to 0.75 GB.

`--end` was run and recorded 0 interventions. The run is incomplete, so that
zero is evidence of nothing.

**The same stack runs again as cold run 9164.**
