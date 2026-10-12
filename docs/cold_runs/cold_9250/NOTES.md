# Cold run 9250 -- the legs profiled

**What it tested:** nothing new; the tools as in 9249, the legs run under
cProfile (`PROFILE_LEGS=1`, the drive's switch from 9249) to see where the
shell and art legs spend time that no job's `duration=` covers.
restaurant_row_001 on 9245's lot and seeds.

**Result: 0 interventions, 0 tool files changed; baked on its first
attempt.** seed_9104 picked as before; findings 122 -> 122. The profiles
are beside the run's journal (`_runs/cold/cold_9250/{shell,art,export}.prof`),
not in this record.

**Under the switch the legs' exit codes read 0:** cProfile swallows a
script's `SystemExit`, so the art leg's usual `exit 1` (the pipeline waiting
at an approval gate) printed `exit 0`. The drive gates each leg on its own
output lines, never on these codes, so nothing here depended on them; the
switch should still carry the code through, and does not yet.

## The art leg's critical path (the workspace index's own start and finish per job)

    jobs                         class          window (s from the leg's first job)
    patina apply and dressing    python_cpu       0 ->  35   (4 at a time)
    clutter, fixtures, kits,     blender         32 -> 146   (one at a time: kits 61.5 s,
      roof props, dressing                                    dressing 24.2, fixtures 11.0)
    presentation_compose         python_cpu     146 -> 210   (one job, 16 commands in turn)
    themed site, surface         python_cpu,    212 -> 252   (22.5 s before lux_apply)
      dressing, lux_apply        godot

**REFUTED, KEPT:** 9249's note read the compose job's 63.7 s against "its
command, 1.6 s". `job.log` holds only the last of its sixteen commands; the
63.7 s is the sixteen buildings composed one after another.

## What the profile adds

Inside each job, before the cache is even asked, the scheduler runs the
job's advisories, its validation, a git probe of the tool's repository, the
hashing of its inputs and its whole plan -- and a plan for Laser Tag, the
walk tests or Lux STAGES a Godot project:

    cumulative s   what
          29.8     `sdk.probe`, 89 calls: 180 `git` processes reading each tool's commit
          27.9     Laser Tag's `plan_commands`, 3 calls -- in the art leg, for jobs
                   that then report "cache" (17.6 s of it `_body_overrides`)
          27.1     Lux's `plan_commands`, 4 calls (the fixture gates and the apply)
           9.9     the walk tests' `plan_commands`, 3 calls, also "cache"
          ~30      collision hulls and ground contact in the validations
          ~19      `hash_json`

## What it says to cut, in order

1. **Blender one at a time** (`blender` 1, TDD 19.2's default, never
   measured): about 100 s of the leg. Level Factory 0.184.0 lets a run set
   `LF_CONCURRENCY=blender=3`; cold run 9251 measures it.
2. **The compose job's sixteen commands in turn**: 64 s.
3. **Work done for a cache hit**: the staging and the probe, before the cache
   is asked.

## What is evidence of what

- The windows: each job's `started_at` and `finished_at` in the workspace
  index; `duration=` in `job.log` only for single-command jobs.
- The profile's cumulative times are summed across worker threads, so they
  rank costs; they are not wall time.
