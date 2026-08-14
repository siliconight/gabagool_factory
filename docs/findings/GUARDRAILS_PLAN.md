# Guardrails — making the checks consistent, discoverable, and binding

Status: planned, not started. Written at the end of the pass that produced
`check_steps.py`, `check_freshness.py`, `check_stair_pitch.py` and `check_all.py`,
while the reasons were still measured rather than remembered.

## The problem, stated precisely

Three different things share one directory and one naming style.

**~28 `patch_*.py` and ~10 `commit_*.ps1` at the factory root are one-shot
migrations that already ran.** They are evidence, not tools. Keep them — this pass
twice reconstructed a bridge-stale file from a backup plus the patches that
followed it, and that only worked because the patches record their exact
before-and-after text. But nothing distinguishes "run this weekly" from "this ran
once in July", so the four things you actually run are lost among fifty things you
do not.

**The checks have no common interface, except the good one already in the repo.**
`site_steps.findings()` returns dicts with `code`, `severity`, `category`,
`message`, `suggested_fix`. So do `site_ground.findings()` and
`site_cover.pinches()`. The standalone `check_*.py` scripts print tables instead,
so `check_all.py` has to scrape stdout and guess which line is the summary — a
cheap observable standing in for structured truth, which is the exact defect class
this toolchain keeps producing. `check_all.py` is a useful stopgap and the wrong
foundation.

**"Could not check" is signalled by an exit code, and exit codes get swallowed.**
By a pipe, by a wrapper, by `2>$null`. Four defects in one pass survived because a
check went quiet and quiet read as clean.

**And the one thing that actually gates a build ignores all of it.**
`library_walk`'s pass column is the walkers' verdict alone: `ballpark_block`
reported `pass 25/25` while carrying `LOT_STEP_BLOCKS_A_ROUTE`, and `ref_pvp`
still reports `pass 15/15` with an objective at 0% traversal. Until a major
finding can fail a sweep, every gate is advisory.

## Phase 1 — make the gates binding

Smallest change, largest shift in meaning: it changes what every future sweep
*says*.

`assemble()` already returns findings in its result dict (`tactical.findings`,
`steps`), and `library_walk` already reads that result. So the verdict becomes a
function of the findings rather than a second opinion:

    pass  = walkers completed  AND  no major finding  AND  nothing unchecked

Do it in this order, because the risk is real:

1. Add a column to the sweep table for major findings, **reporting only**. Run a
   full sweep. Now you know which sites would newly fail and why, without having
   changed any verdict.
2. Read that list. Any site that would newly fail is either a real defect this
   pass already measured (see *Carried measurements* below) or a gate that is
   wrong. Establish which before making it binding — a gate that fails a good
   site gets disabled by whoever is trying to ship, and then it is worse than no
   gate.
3. Make it binding.

Do not skip step 1. A verdict change that fails four sites on its first run is
indistinguishable from a broken verdict change.

## Phase 2 — findings, not printed tables

One dict shape and one function name. Resist building a framework.

    def findings(ctx) -> list[dict]
        # {"code": "LOT_...", "severity": "major"|"minor"|"info"|"unchecked",
        #  "category": "traversal"|"geometry"|"provenance"|...,
        #  "message": str, "suggested_fix": str, "where": str|None}

Two things this must get right:

**`unchecked` is a severity, not an exit code.** A gate that cannot run returns a
finding saying so, with the reason in `message`. It then flows through the same
aggregation as everything else, appears in the same report, and cannot be lost by
a pipe. It also composes: a sweep can say "17 clean, 2 blocked, 1 not checked"
instead of collapsing to one number. This is the single most important line in
this document.

**A registry, not a hardcoded list.** A `gates/` package the runner imports, so
adding a gate is adding a file. `check_all.py`'s `CHECKS` array is already the
wrong shape — it has to be edited to add a check, which means it will drift.

Convert in this order, cheapest first: `check_freshness`, `check_stair_pitch`,
`check_steps`, `gdcheck`. Each keeps its current CLI (they are in muscle memory
and in this repo's docs) and grows a `findings()` alongside; the CLI becomes a
thin formatter over it. Then `check_all.py` stops scraping stdout and imports.

## Phase 3 — migrations out of the root

Pure hygiene, no behaviour change, do it last so it never obscures a real diff.

    migrations/2026-07/patch_*.py, commit_*.ps1
    migrations/MIGRATIONS.md

`MIGRATIONS.md` records, per script: what it changed, when it ran, and the byte
counts before and after. That last column is not bookkeeping — it is what makes
reconstruction possible when the device bridge serves a file stale, which happened
to `lot.py`, `agent_contract.json`, `stairwell.py` and `PIPELINE_ROADMAP.md` in a
single session.

**Do not delete these.** They are the only record of how the current source came
to be, and they are reconstruction material.

What stays at the root: `check_all.py`, the `gates/` package, `library_walk.py`,
`rebuild_buildings.py`, `gdcheck.py`, `CLAUDE.md`.

## Carried measurements — defects found but not yet fixed

Each is measured, not suspected. Phase 1 step 2 should expect these.

**Stair pitch.** Pitch is `atan(story_height / st.run)` at `deli_counter.py:1261`,
and `st.run` is pinned near 3 m however tall the storey is, so pitch is a pure
function of storey height. 20 of 38 buildings emit flights at 45.0–51.3° against a
controller that stands on 45°; 18 are at 35.8–43.7° and walk fine. `walkup_siege`
walks; `ballpark_block` does not. Fix: lengthen `st.run` to `1.19 × H` per building
spec (about +1.3 m of shaft, needs floor space that may not exist), or split each
storey into two half-flights with a landing (~31°, no extra footprint;
`deli_counter.py:1258` and `:1303` already carry the parallel-leg and landing
machinery). Blocked in that pass: `stairwell.py` served stale over the bridge with
no `.pre_*` ancestor to reconstruct from.

**Kerbs at crossroads.** `_kerb_crossings` considered only `paths`, so where two
roads meet neither cuts the other's kerb — four raised 0.16 m strips through
`warehouse_district`'s junction, a wall across a road. `patch_kerb_junction.py` is
written and verified (single-road sites emit identical geometry; the four kerbs at
the junction each gain exactly one crossing) but **unrun**, because it moves
geometry and wants a sweep.

**Paths drawn over road carriageways.** On `walkup_siege`, `path_0` crosses
`road_0` at 30° and its 5 m band is drawn over 16.0 m of asphalt; `path_2` over
8.7 m. The lip is 0.0157 m so no traversal gate sees it — it is a design defect, a
footpath painted diagonally across a road. Rule: paths yield to roads. Emit the
path in segments that stop at each kerb, the way sidewalks now cut for paths.
**No gate measures this**, which is why it shipped invisibly.

**An unreachable objective.** `ref_pvp` reports `LOT_DESTINATION_ABOVE_FLOOR` with
`TRAVERSAL 0% completion` and still passes the sweep. Phase 1 makes this visible.

## The rule worth keeping

Every defect found by *looking at it* should leave behind a check that would have
found it without looking. Three of the four above were found by walking the level
or reading the editor viewport. That is the gap the guardrails exist to close.
