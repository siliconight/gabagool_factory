# Cold run 4 — `bank_block_001`, seed_base 8001, VARIED LOT

**Begun** 2026-09-05 09:05:01 · **Ended** 09:23:29 · 18 min 28 s · 2394 source
files hashed across 10 tools
**Journal / snapshots:** `_runs/cold/cold_8001/`
**Brief:** `docs/cold_runs/cold_8001/` (seed_base 8001 → seeds 8001 / 8102 / 8203)

## Result

```
interventions NOTED in the journal      0
tool source files CHANGED on disk       3
  attributed to the pipeline, NOT counted   3
  UNATTRIBUTED, counted                     0
retries (same command re-run)           0
observations (looked, did not touch)    1

INTERVENTIONS: 0
```

**And a gated package came out.** `export ... --mode portable-godot` exited 0.
This is the first cold run to answer item 17's question with a yes.

| run | seed_base | interventions | retries | outcome |
|---|---|---|---|---|
| cold_7001 | 7001 | 0 | 1 | exported — verdict rested on a gate later found broken (item 71) |
| cold_7002 | 7002 | 1 | 1 | blocked — brief named a Pixelcoat profile that does not exist (item 72) |
| cold_7003 | 7003 | 1 | 0 | blocked at export — functional lock refused it (item 73) |
| **cold_8001** | **8001** | **0** | **0** | **EXPORTED, gate-clean** |

## The versions this is a measurement of

    deli_counter 0.103.1   level_factory 0.55.0   lot 0.51.0
    lux 0.29.0             zoo 0.54.0             patina 0.21.0
    pixelcoat 0.16.0       lasertag 0.9.0         dispatch 0.4.2
    pipeline 0.6.0

Three of those had never been exercised by a cold run: **deli_counter 0.103.1**
(item 73), **level_factory 0.54.0** (item 69) and **0.55.0** (the export's
engine declaration).

## What was different about this run, and it is the point

**`lot_library` was set.** No previous cold run set it, so every
interventions-per-level figure this repo has quoted was measured on a site of
one building repeated (roadmap 37). The brief is otherwise identical to
cold_7003's, field for field.

Each candidate drew three DISTINCT archetypes, and different sets between
candidates:

    seed_8001   deli_a01, freight_terminal_a03, brewery_a01
    seed_8102   depot_a01, stadium_a02, train_yard_a03
    seed_8203   freight_terminal_a03, construction_site_a01, pawn_shop_a02

The shipped package carries three per-building directories — `depot_a01`,
`stadium_a02`, `train_yard_a03` — with its 33 interactives distributed across
all three (9 / 11 / 13). Roadmap 37's founding measurement was "1
`ext_resource`, 4 instances". **A varied THEMED lot has now been built end to
end, which had never happened.**

## Why the export was not refused this time

Cold run 3 died here, and the mechanism was found and fixed before this run
rather than after it (deli_counter 0.103.1, roadmap 73).

`specs/CATALOG.md` is TRACKED, `new_level.py` refreshed it after every spec
write, and it indexed the `lf_*` transients. Level Factory folds a tool repo's
dirty-TRACKED-file hash into the build fingerprint. So one `deli_generate` job
changed Deli Counter's revision mid-run, later jobs cache-missed — including
jobs the functional lock had just fingerprinted — the re-runs moved the
gameplay-anchor and interactive registries, and `verify_no_drift` refused the
export.

MEASURED THIS RUN, at the lock and again after the art pass:

    DC   a31cda2c9ac4d90693ec0106f6088409985ac2da   (unchanged)
    LOT  98834b1b3d04d14e8e0cc7ee643aad809e5c3ee5   (unchanged)

No `+dirty` suffix at either point. And the art run's own log shows the
consequence directly:

    deli_generate.candidate.seed_8102   cache
    lot_assemble.candidate.seed_8102    cache

In cold_7003 those two RE-RAN, 1.3 s and 6.6 s after the lock. Here they
cache-hit. `specs/CATALOG.md` does not appear in this run's changed-file list
at all; under the old behaviour it would have been a fourth changed file.

## The package

`workspaces/cold-8001-ws/.level_factory/exports/LF_bank_block_001.portable-godot`
— 156 files, 17 MB.

```
config_version=5
config/name="bank_block_001 (shell)"
config/features=PackedStringArray("4.7")
run/main_scene="res://mission.tscn"
```

`config/features` is there because level_factory 0.55.0 put it there. Measured
before that fix: 0 of 4 shipped exports declared it, while every one of their
manifests recorded `godot_version: 4.7` — so the package asserted a version it
never told the engine, and Godot drops such a folder to the Project Manager
instead of opening the level. **This is the first export that will open.**

Handoff artifacts present: `gameplay_anchors.json`, `interactives.json`,
`proposed_beat_graph.json`, `runtime_ownership_requirements.json`,
`mission_manifest.json`, `portable_resource_manifest.json`.

## The three changed files, and why none counted

    deli_counter/specs/lf_bank_block_001_8001.json
    deli_counter/specs/lf_bank_block_001_8102.json
    deli_counter/specs/lf_bank_block_001_8203.json

One DC spec per candidate, which is exactly what Level Factory is expected to
write. Item 70's attribution table named all three with reasons and left zero
unattributed. These are the files roadmap 98 notes are written into a tool repo
by another tool — the boundary is still there; it just no longer costs a count.

## The one observation

An operator shell-quoting error: a Windows path passed through a bash heredoc
turned `\b` into a backspace, so `batch create` exited 5 before reaching the
pipeline. Re-invoked with forward slashes. Recorded rather than quietly
retried — it is not a pipeline retry, because no pipeline work was attempted,
and it counts toward nothing. It is in the journal so the number is not
flattering itself.

## Candidate selection — a decision, not an intervention

`seed_8102`, chosen on the graybox findings:

* `seed_8203` — objective marker 3.20 m above the ground plane
  (`LOT_DESTINATION_ABOVE_FLOOR`), reads as sealed from the crew spawn
  (`LT_SEAL_UNVERIFIED`, `LT_ROUTE_NEVER_COMPLETED`).
* `seed_8001` — `WALKTEST_ANCHOR_ISOLATED`: `proxy_2` snapped onto the navmesh
  but sits on a 1-polygon cluster while the main network has 12.
* `seed_8102` — neither. Its two majors are `LT_MAP_TRAVERSAL` (0% route
  completion) and `LT_NO_SURVIVABLE_OPENING`, both Laser Tag combat-model
  findings, which the standing rules classify as information for a human at
  selection rather than map defects. Most cover of the three: 14 pieces, 9 on
  route.

## What this run does NOT establish

* **The vocabulary was not cold.** Archetype, theme, site shape and route shape
  were all seen by cold runs 2 and 3. What was cold: the geometry, the seeds,
  and the varied lot. Quote the number with that limitation attached.
* **Nobody has walked it.** The package is gate-clean and it opens; that is
  "works", not "good" (roadmap 18). `LT_MAP_TRAVERSAL` is 0% on all three
  candidates, as it has been on every evaluation ever run.
* **One run.** Item 17 is explicit: "Repeat on several specs before believing
  either result." This is one spec, with a vocabulary the tools have seen.
* The three shells of roadmap 98 still keep `check.py` red in Deli Counter, so
  DC commits still need `--no-verify`. That is unrelated to this run and did
  not touch it.
