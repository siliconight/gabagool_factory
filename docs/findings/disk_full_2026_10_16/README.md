# The disk filled, 2026-10-16: what was measured, what the walker retired, what it was not

**What happened.** At 08:20 C: read 466 GB used, 0 free. Cold run 9319 (the package proof for the declared-drop
links) died at its art stage with `drive exit 2`; two scratch files failed to write with ENOSPC. The run is
void (`docs/cold_runs/cold_9319/NOTES.md`) and re-staged as 9320.

**What the factory held** (measured while the disk was full, slowly):

    _runs/                 16 GB   775 entries, 7 from July, 59 August, 549 September, 160 October
                                   (the largest: demo_fallback_2026-10-14 870 MB, moon_trial 672 MB, day_lamps_9214
                                   559 MB, perf_inner 464 MB, seven walk_export_* at 265-311 MB each)
    workspaces/            62 GB measured mid-retire; ~110 workspaces before it: 79 cold-run (about 1 GB each:
                           cold-9318-ws 1,020 MB), 29 named A/B arms and demos (rockay-ws 504 MB)
    _scratch/             2.4 GB
    deli_counter/build/   157 MB
    Godot's own caches     3.8 GB (Roaming) + 0.8 GB (Local); the user Temp folder 1.1 GB -- not the factory's,
                           not touched

So the factory's regenerable output was on the order of 100 GB of the 466, and the retire tool's own rules found
0.6 GB of it: `tools/factory_retire.py` keeps a cold-run workspace whenever a file under docs/ names it, and the
records name them literally on purpose (the memory rule "name workspaces literally in records", so a BUILT name
cannot let the retire take an arm a finding still reads). A name in a record was never meant to pin a gigabyte,
but the rule cannot tell a name that still reads the workspace from a name that merely cites it.

**What the walker approved** (asked, two of four options): the 67 cold-run workspaces whose record is pushed,
beyond the newest four (9180 .. 9310; kept 9314, 9316, 9317, 9318) -- regenerable from `docs/cold_runs/cold_N/`
-- and the 615 `_runs/` entries last touched before October (perf copies, A/B arms and probes whose JSON records
are in docs/). NOT the 29 named workspaces, not rockay-ws. `retire_approved.py` is the rule as a script, dry-run
by default; `retired_paths.txt` is the exact list it removed, each by its literal absolute path, refusing
anything outside workspaces/ or _runs/.

**What it did** (2026-10-16 08:47-09:10): removed 682 paths -- 67 cold-run workspaces and 615 `_runs/`
entries -- and C: went from 447 MB free to 54 GB free. The 9315 workspace (0.6 GB) went first, by
`tools/factory_retire.py`'s own rule. On 2026-10-18 cold run 9321's own clean job took cold-9316-ws and
cold-9317-ws (2.4 GB) by that tool's pushed-runs rule, once 9318 to 9321 made them older than the newest four.

**What it got wrong.** It had no tracked-file guard, and `_runs/attic/` held one tracked file
(`_runs/attic/test_themed_selection.py.pending`), against the retire tool's rule that nothing git tracks is
ever touched. Restored from git on 2026-10-18. `retire_approved.py` now keeps any path that is a tracked file
or holds one, proven in planning by moving its date cutoff past every entry: `_runs/attic` and
`_runs/measurements` stay. It also no longer rewrites `retired_paths.txt` on a dry run; that list is the record
of the 682.

**What it was not.** The other ~350 GB of C: are outside this factory and were not measured here. The walker
knows. Between the retire's end and 2026-10-18 free space fell from 54 GB to 46 GB, and none of the 8 GB is in
the factory's scratch, the test runner's temp (7.6 MB) or the user's Temp folder (1.0 GB): unattributed,
outside the factory.

**For the retire tool (a policy call, queued):** a `--pushed-only` mode that retires any cold-run workspace whose
record is pushed regardless of mentions, which is the rule the walker approved by hand today, would have kept
the disk from filling. It is not changed here because it is the walker's standing rule to change.
