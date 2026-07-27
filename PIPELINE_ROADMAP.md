# Pipeline roadmap — engagement fairness and scene provenance

Working notes for `run <mission> --art` on `category5_baie_dore_001`
(batch `rockay_category5`, seeds 5017 / 5118 / 5219 / 5320 / 5421, four
buildings, brief `target_minutes` `[12, 20]`). This file exists so the work can
be picked up in a fresh session without replaying the investigation. Read it top
to bottom; the first two sections are the state of the world and the third is
what to do next.

For the standing shape of the system — what each repo does and OWNS, the job
DAG, where artifacts land, and the contracts — see `PIPELINE_MAP.md`. This file
assumes it, and in particular assumes its first section: the deliverable is a
level shell that must work standalone in someone else's Godot project with none
of these tools present, and **these tools are not the authority on gameplay or
networking**.

That boundary was stated plainly on 2026-07-27 and it retired a day's worth of
work in this file. Laser Tag exists to *create tests Deli Counter and Lot own*,
not to grade maps: a finding of its is a request for a guardrail upstream, and
Laser Tag going quiet is the goal rather than its score going up. Anything below
that reads as tuning a level against Laser Tag's combat model is wrong, however
it is worded.

## Standing rules

Fixes land in the tools under `gabagool_factory` — `level_factory`, `lot`,
`deli_counter`, `lasertag`, `pixelcoat`, `zoo`, `patina`, `lux`, `dispatch` —
and never in a mission workspace. `rockay-ws` is evidence, read-only; it has not
been written to and should not be.

Laser Tag is a soft gate. It grades a map, it never refuses one. Its findings
are answered by changing what gets built — chiefly by putting cover in the
ground between the crew and whatever can see them — rather than by blocking the
build. `Scheduler._advise` enforces this structurally: every advisory is forced
non-blocking and a BLOCKER is demoted to MAJOR.

That rule governs Laser Tag's *advisory* channel; findings returned from
`normalize_validation` keep their blocking flag, which is the seam a gate can
live in. But what may block there is constrained by the boundary above: only
things these tools are authoritative on — reachability, navmesh, collision,
closure. `LT_ROUTE_NEVER_COMPLETED` blocks when runs time out with the crew
alive, because that is a reachability fact. Nothing blocks on survival,
engagement distance or opening timing, because those are claims about a combat
model that ships to nobody.

Guard rails go in as the learnings arrive. The point is a repeatable pipeline
that produces game-ready assets, not a one-off good level.

## What was wrong, and what is fixed

### The engagement contract

Enemies acquire at 35 m. The crew's bot acquires at 45 m, so 45 m is the number
placement must respect — `site_spawns.OPENING_RANGE`. The crew walks at 4.5 m/s
(`LT_BotPlayerController.move_speed`); enemies walk at 4.0.

**The "and therefore fires first" that used to follow does not hold in practice**
— see "What the first honest run said". The crew's 10 m of extra sight is a
capability, not an outcome: `LT_EnemyBrain` seeks the player from frame one and
closes to a 14 m preferred distance, while `LT_BotPlayerController` walks its
route and only fires at an enemy it can currently see. The enemy is solving for
contact; the crew is solving for navigation. Measured, the enemy shoots at
~0.3 s and the crew at 6.5–8.9 s. Placement respecting 45 m is necessary and
demonstrably not sufficient.

Three defects in `lot/site_spawns.py`, all now fixed and mutation-verified:

**A — the standoff finding described the placer, not the map.** It reported the
nearest enemy *it had moved*, which on a map where the dangerous enemy was never
moved is a reassuring sentence about the wrong enemy. The finding now names the
nearest enemy on the map, by index and distance, alongside what it moved.

**B — a distance equal to the acquisition threshold was accepted as a
standoff.** It is not a standoff, it is the threshold: both sides acquire on
frame one. `OPENING_CLEARANCE = CREW_SPEED * REACTION_SECONDS` = 4.5 m of
daylight on top, so the fight starts after the crew has had a chance to move.

**C — nothing asserted the positions that were actually written.** The search
decided where an enemy could stand and the report described the search.
`_opening_findings` now reads back the emitted positions and re-asks the
fairness question of them, emitting `LOT_ENEMY_SPAWN_IN_THE_OPEN` (major) or
`LOT_ENEMY_SPAWN_CLOSE` (minor). It is deliberately redundant with the search:
the two agreeing costs microseconds, and the two disagreeing is the only class
of defect the search cannot report on itself.

### The scene that was graded could not be identified

A real defect, fixed. It was originally recorded here as the cause of the whole
metric cluster; it is not — see the correction at the end of this section. What
it actually cost was the ability to say which file a grade described.

`packages/staging/godot_project.py` copied the scene only `if
scene_src.exists()`, and ran its rewrite pass only `if (dest /
scene_res_name).exists()`. A staging directory is reused across runs. Those two
guards together meant: source missing, no copy, the previous run's `level.tscn`
still sitting there, the rewrite pass reads it, bakes hooks into it, resolves
its refs and writes it back — with the current timestamp. Godot then graded a
map from a build nobody had asked about, and every mtime on disk agreed it was
current.

Proof, seed 5320. `jobs/…lot_assemble…seed_5320/out/site_walk.tscn` holds
Enemy_0 at Godot `(53.5892, 1, -17.2715)` — 48 m from the crew spawn at
`(101, 1, -10)`. The `staging/…laser_tag_evaluate…seed_5320/level.tscn` Godot
loaded holds Enemy_0 at `(77.9785, 1, -10.6588)` — **23 m, down a clear
street**. Enemy_1 differs too; Enemies 2–5 and the crew spawn are identical.
Only the two nearest enemies differ, which is exactly the signature of an older
standoff rule. `inject_lt_hooks` is a verified no-op on that source, so the
difference cannot have been introduced at bake time.

**Corrected 2026-07-26 — the stale scene is real, but it is NOT the cause of
the metrics.** The claim that once stood here, that the whole metric cluster
followed from the stale file, does not survive the evidence now on disk.

The staged scene cited above has since been overwritten. The last run
(`index.sqlite` 21:45 UTC) re-staged correctly, because the pre-fix guards only
bite when the *source is missing*, and that run's source existed. What that run
left behind:

* `jobs/…lot_assemble…seed_5320/out/site_walk.tscn` and
  `staging/…laser_tag_evaluate…seed_5320/level.tscn` are **byte-for-byte
  identical** (6034 bytes, `Compare-Object` empty, verified by diff).
* That staged scene holds Enemy_0 at `(53.589, 1, -17.271)` — **47.96 m** from
  the crew spawn at `(101, 1, -10)`. The correct placement, not the 23 m one.
* And that run's report still reads `route_completion_rate` 0.0,
  `team_wipe_count` 25/25, `avg_time_to_first_contact` 0.21 s,
  `avg_engagement_distance` 26.97 m — the same cluster.

So a run that graded exactly the scene Lot built produced the same result. The
stale scene explained the *divergence*, never the *grades*. Both defects were
present; only one was ever load-bearing.

The method error worth remembering: the original proof compared a `site_walk.tscn`
and a `level.tscn` that came from **different runs**, and read the pair as a
single run's before/after. Two artifacts sharing a seed in the directory name do
not share a run. That is what `staging.notes.json` provenance now exists to
settle.

**Fixed:** the staged scene is deleted before anything else is decided, so a
scene this run cannot account for can never survive into a grade; and
`staging.notes.json` now records `scene_source`, `scene_source_sha256` and
`scene_staged`, so a reader holding a bad grade can answer "which file was
this?" without trusting the clock — which is precisely what the rewrite pass
changes. Five tests in `tests/unit/test_staging_scene_provenance.py`.

### Where the suites stand

Lot 257 passed. Level Factory 439 passed, 11 skipped, 0 failures — **450
collected**.

State the collected total, not just the passing count. The line once read
"433 passed, 0 failures, 11 skipped", which reads as 444 collected but meant 433
collected of which 422 passed, so adding tests looked like a regression. Passed
plus skipped equals collected, or the next person re-derives which of the three
numbers was the loose one.

Level Factory's `pyproject.toml` already sets `addopts = "-q"`. Passing `-q`
again makes it `-qq` and pytest drops the summary line entirely — the run looks
like a wall of dots that never reports a count. Lot has no such `addopts`, which
is why it prints one and LF appears not to.

### The gate that let an unplayable level through

Fixed, then fixed again for a better reason. Worth reading whole: the first
version was wrong in a way that would have blocked correct maps.

`lasertag_report.py`'s route rule had two branches and a gap. A run that timed
out with the crew alive is geometry — nothing stopped them walking except the
map — and blocked as `LT_ROUTE_NEVER_COMPLETED`. A run where every match ended
in a wipe is difficulty, which by TDD 5.5 never blocks, and reported
`LT_ROUTE_UNPROVEN` at moderate. Seed 5320 fell between: `timeout_count` 0,
`team_wipe_count` 25. The gate correctly declined to call it geometry and then
had nothing else to say, so a level no simulated crew ever traversed shipped
with every gate green.

The third branch, `LT_NO_SURVIVABLE_OPENING` (blocker, category `spawn`), closes
it: route never completed, nothing timed out, **and** the crew was fired on
inside the reaction window. Difficulty is a property of a fight the crew got to
have. The threshold is Lot's own `REACTION_SECONDS` of 1.0 — the constant
`OPENING_CLEARANCE = CREW_SPEED * REACTION_SECONDS` derives from — carried as a
documented fallback because `normalize_validation` receives report files and no
repository path. Nothing was invented.

**The first version read the wrong metric.** It used
`avg_time_to_first_contact`, which `LT_MetricsCollector.record_shot` stamps on
the first shot of a run from EITHER side — the assignment sits outside the
`shooter_is_player` branch. Lot places enemies so the crew acquires first (45 m
player sight against 35 m enemy sight), so on a map placed as intended that
figure is short BY DESIGN, and gating on it would have blocked hardest on the
maps whose opening worked. The metric the gate needs is the enemy's first shot,
which Laser Tag tracked per run and discarded at aggregation.

So Laser Tag now publishes `avg_time_to_first_enemy_shot` and
`avg_time_to_first_player_shot` (plus spread), and the gate reads the enemy
half. Two guards matter and both have tests: an absent field stands down, for
the same reason absent is not zero in `route_completion_rate`; and `_avg`
returns **-1.0** for a metric no run recorded, so the comparison is
`0.0 <= contact < REACTION_SECONDS` — without the lower bound the sentinel for
"no enemy ever fired" reads as the fastest possible opening and blocks the
quietest maps hardest.

Deliberately still permitted: a hard-but-fair map (enemy first shot 3.0 s) does
not block; a timed-out route still reports as reachability even when the opening
was also brutal, so nobody is sent to fix spawns on a level whose route is
broken. The boundary is strict — exactly `REACTION_SECONDS` is the contract met.

### The measurements were taken with the wrong ruler

Four defects, all fixed, all the same shape: something stood in for the truth it
was supposed to represent.

**The run clock ran on the render frame.** `LT_RunState.elapsed_seconds`
incremented in `_process`, while every combat event that reads it — shots,
deaths, line of sight — is produced from `_physics_process` in
`LT_BotPlayerController` and `LT_EnemyBrain`. Headless decouples the two
entirely, and `start_run()` zeroes the clock and spawns the pills in the same
call, so a shot landing before the first render frame was stamped exactly 0.0.
That is how a report came to claim first contact at 0.0 s. Now on
`_physics_process`: simulated seconds, reproducible, and `max_run_time_seconds`
is a budget of simulated time, which is what a deterministic evaluator should
always have enforced.

**Laser Tag's own findings read the both-sides metric.** `LT_ScoreCalculator`
judged `INSTANT_CONTACT` / `SLOW_CONTACT` and `OVEREXPOSED` by
`avg_time_to_first_contact`, marking down maps for the crew shooting on
schedule. Both now read the enemy's opening. `contact < 0` also split: no enemy
fire *with* shots fired is an uncontested opening (`NO_INCOMING_FIRE`, PASS),
not "combat never started", so a crew that wins is no longer scored zero.

**The build fingerprint was blind to Laser Tag.** `LaserTagAdapter.fingerprint_inputs`
described only the MAP, and the rest of a fingerprint comes from `probe()` —
`tool_version` and `repository_commit` — which Laser Tag does not publish
(`factory.manifest.json`: `"version": "unpinned"`, "no VERSION source yet").
Patching the addon and re-running therefore served the previous grade back and
reported the job as succeeded. **This is why the first `--art` re-run appeared
to do nothing**: every artifact kept its old timestamp while `index.sqlite`
advanced. The addon's sources are now hashed into the fingerprint — sources
only, `.godot/` and `.uid` excluded, keyed by path relative to the addon root
because the tree has same-named files at different depths.

**Staged sibling directories were immortal** (was item 4). `if not
dst.exists(): shutil.copytree(...)` meant the first run to stage an asset
subtree fixed it forever. Now replaced wholesale, as the addons already were.
Two tests, including one proving a module deleted upstream does not linger.

**`cater.needs_build` compared clocks** (was carried). It asked *when* a `.glb`
was built rather than *what from*, and a filesystem timestamp is one coarse
timer tick wide — ~1–4 ms on Linux, ~15.6 ms on Windows — so a spec edited in
the same tick the build finished compared EQUAL, the strict `>` answered False,
and the glb was declared current permanently. It now compares a sha256 of the
spec against a `<glb>.spec.sha256` stamp written after each build. An unstamped
glb rebuilds: we cannot say what it came from, and rebuilding costs Blender time
while trusting it costs correctness.

### The guardrails moved to the tools that build the geometry

The correction that followed from the boundary, and the shape everything after
it should take.

**`LT_NO_SURVIVABLE_OPENING` is now a non-blocking major.** It was a blocker. It
judged by the enemy's first shot landing inside a reaction window — a statement
about a combat model nobody ships — so blocking on it enforced Laser Tag's model
on Lot, which is exactly what the soft-gate rule exists to prevent. There WAS a
real gap (a broken asset shipped green); it was filled in the wrong layer. What
blocks is what these tools are authoritative on: reachability, navmesh,
collision, closure. `LT_ROUTE_NEVER_COMPLETED` still blocks, because "the crew
had the full clock, nobody killed them, and they never arrived" is a
reachability fact.

**The cover the crew looked for was never the cover Lot placed.**
`LT_CoverTestPoints` — the list `LT_BotPlayerController._on_damaged` reads — was
a hardcoded rosette 5 m around the objective, unrelated to any cover on the
site. Every measurement of "cover clustered at the objective, 69 m from spawn,
10.8–19.4 m from an enemy" was measuring that rosette, not `site_cover`'s
output. The hooks now come from `site_spec["cover"]`, which `assemble`
populates before the walk scene is written; a site with no planned cover keeps
the rosette, because an empty node reads to Laser Tag as "this map has no cover"
when the truth is "nothing was planned".

**Cover clearance is derived from the agent contract, not chosen.**
`BUILDING_CLEARANCE` was a flat 2.0 enforced against a piece's CENTRE while a
piece is 3 m wide — a 0.5 m edge gap against a bake that needs 1.2 m.
`min_passable_gap()` now applies the contract's own rule,
`2*ceil(agent_radius/cell_size)*cell_size + 2*cell_size`, reproducing its stated
1.2 m at the ratified 0.4 m radius and 0.15 m cells; `building_clearance()` adds
the half-width. A coarser bake widens it automatically. `AGENT_CONTRACT.md`
already said door width, agent radius and cell size are ONE decision — a cover
piece beside a wall is a doorway made of street furniture and nothing was
applying the rule to it.

**And Lot reads back its own geometry.** `site_cover.pinches()` measures the
emitted rectangles for lanes narrower than an agent can walk, in the shape
`_opening_findings` established: a report derived from the search cannot
disagree with the search. Reports `LOT_COVER_PINCH` (moderate, navigation).
Flush against a wall is not reported — that is a wall, solid and honest. A lane
at exactly the minimum passes, same as meeting a door width is passing.

**The pinch check was widened to the site boundary.** Cover is placed on open
ground and the edge of open ground is a wall, so `perimeter_rects()` derives the
four `perim_` walls from the ground rect and `pinches()` measures against those
as well as the buildings. Computed inside `plan_cover` rather than asked of the
caller, for the same reason the building rects are grown there. It changed
nothing on the live seeds — see item 1, which is why that item is closed rather
than open.

**Provenance recursion stopped being cosmetic.** It grew one level per run
because `collect_outputs` rglobs a reused job directory, so every run swept up
the previous run's sidecars and wrote a sidecar for each. Carried as an eyesore
at eleven deep; at seventeen the path passed Windows' MAX_PATH and the run died
with `[Errno 22]` before any stage did work. Filtered at the scheduler, so an
adapter cannot opt back in by rglobbing honestly. 1,370 existing sidecars were
cleared by hand.

**Dropped deliberately, under the boundary:** the crew bot's target memory and
threat response, the enemy-fires-at-t=0 anomaly, and anything tuned against
survival time or engagement distance. `cover_seek_max_distance` stays only
because it stopped the harness corrupting its own measurement by walking the bot
69 m into fire.

### What the first honest run said

`--art --force`, 2026-07-27. Laser Tag genuinely executed for the first time
since any of this began — 59.6 s per seed, 1080-polygon navmesh bake, 25 runs —
and `staging.notes.json` finally carries `scene_source`, `scene_source_sha256`
and `scene_staged: true`.

```
seed    enemy 1st   crew 1st    gap    survival   route   wipes
5017         0.36       8.93   8.57       11.94     0.0      25
5118         0.28       6.54   6.26        9.41     0.0      25
```

**The enemy opens fire at ~0.3 s. The crew does not shoot back for six to nine
seconds.** It then dies at 9–12 s, having returned fire for two or three of
them. `avg_time_to_first_contact` was tracking the enemy's shot all along and
nothing could tell — which is precisely what splitting the metric was for.

The gate blocked both seeds and halted the run at 5118.

**Then the cover work landed, and seed 5118 moved.** Same seed, before and after
the route-cover pass plus real cover hooks:

```
                        before      after
cover markers                4          7   (real cover, not the rosette)
avg survival             9.41 s    12.48 s
crew kills (25 runs)         2          4
player-stuck events          0         25
enemy-stuck events           0         25
score / grade          60 WARN    47 FAIL
route completion            0%         0%
```

`NO_REACTION_TIME` stopped firing — survival passed the scenario's own
`min_reasonable_survival_seconds` of 10.0. Under the boundary that is *not* the
win it looked like: it is a combat outcome. The load-bearing number is the stuck
events going 0 → 50, which is a nav failure the cover introduced, and which is
what the agent-contract clearance above was written to prevent.

**And with the clearance in, the run finally reached the seeds that had been
hiding behind the block.** Seed 5320, never evaluated before:

```
Lot   cover 6 (3 marker, 3 route)   pinches 0   route_open 0
LT    player_stuck 835   enemy_stuck 95   route 0/25
      end_reason: TIMEOUT 19, TEAM_WIPE 6   survival 14.7-180.1 s
```

Two things to take from it. `LT_ROUTE_NEVER_COMPLETED` fired as the blocker —
nineteen runs ran the full clock with the crew alive and never arrived, which is
the reachability question answered from reachability evidence, and exactly what
should stop a build. And 5320 is a completely different failure from 5118: there
the crew died in 12 s, here it survives 140 s on average and cannot reach the
objective. Same 0% completion, opposite causes. That is why the `timeout_count`
split is worth keeping.

**The guardrail passed and the runtime disagreed, which is the useful case.**
Lot reported zero pinches while the bot stuck 43-44 times per run. The check is
incomplete rather than wrong: `pinches()` measures cover against `rects`, and
`rects` is `site_spawns.footprints()` — buildings only. Perimeter walls, ground
slabs, courtyards, paths and ladder volumes from `_outdoor_nodes` are invisible
to it. See item 1.

## What to do next

**1. Cover is exonerated — the trap is somewhere else.** Closed 2026-07-27.

`site_cover.pinches()` originally measured placed cover against `rects`
(`site_spawns.footprints()` — buildings only) and reported zero while Laser Tag
counted 835 player-stuck events on a seed. It was widened to include the four
`perim_` walls `_outdoor_nodes` lays around the ground rect, computed inside
`plan_cover` from the `ground` it already receives so a caller cannot get it
wrong on Lot's behalf.

It still reports zero, on both seeds that ran:

```
              cover placed   Lot pinches   LT player-stuck   profile
seed 5017      11 (6 route)            0                25   TEAM_WIPE x25, 12.5 s
seed 5219      12 (6 route)            0               835   TIMEOUT x19, 140.4 s
```

Two rounds of cover work — route placement, agent-contract clearance, perimeter
awareness — and Lot's own read-back says the geometry it emits is clean while
the walker still sticks 33 times a run. **Whatever traps the bot is not cover**,
and that conclusion comes from Lot's offline measurement rather than from
argument. Stop looking here; the next instrument is item 2.

One number to re-check before quoting it: seed 5219's stats this run (835 stuck,
95 enemy-stuck, 140.4 s, 19 kills) are identical to seed 5320's from the
previous run, across a different seed *and* a Lot code change. Two structurally
similar sites could converge, but identical to four significant figures is the
kind of coincidence that has been wrong twice in this file.

**2. `walktest.py` into the DAG.** Every navigation conclusion in this file was
inferred from a firefight, which is the wrong instrument twice over: confounded
by combat, and asking a nav question of a gameplay simulation. `walktest.py`
path-proves the mission spine on the baked navmesh, spawns physical walkers,
fails anyone stuck over four seconds, and involves no enemies at all. On seed
5219 it would say in one run whether the route is pathable, instead of leaving
it inferred from nineteen timeouts.

Traced 2026-07-27. **Four edits, all located; none of them made yet.**

* `packages/pipeline/planner.py` — a `_STAGE_WALKTEST` job per candidate,
  `adapter_id="walktest"`, `depends_on=[lot_jid]`,
  `resource_class="godot_headless"`, expected output
  `site_navqa.walktest.json`. (Lot's stem in this pipeline is `site`, and
  `walktest.py` writes `<scene_stem>.walktest.json` beside the scene.)
* `adapters/walktest/__init__.py` — new, shaped like the Laser Tag adapter:
  stage a throwaway project with `stage_godot_project`, then run
  `python <lot_repo>/walktest.py <project> site_navqa.tscn`. Staging only needs
  the scene and its work-dir siblings — `walktest.py` syncs the `heist_nav_qa`
  addon into the project itself, from the Lot checkout, so the director is
  always the version shipped with that Lot.
* `packages/adapters/registry.py` — one line in `build_default_registry`.
* `apps/cli/commands/__init__.py` — this is the job-spec builder, dispatching
  on `job.adapter_id` (~line 223 onward). Two changes: the `elif job.adapter_id
  == "lot"` branch (~232) sets `"walkable": True` and must also set
  `"navqa": True`, or the navqa scene is never emitted — the Lot adapter has
  supported the flag all along and **nothing has ever set it**; and a new
  `elif job.adapter_id == "walktest"` branch beside the `laser_tag` one
  (~243), which is the closest working template.

**Open question before starting:** `walktest.py` finds Godot through
`$LOT_GODOT` / `$DC_GODOT` / PATH, and it is not established that
`PlannedCommand` can pass environment through to a child. If it cannot, either
the runner needs an explicit `--godot` argument or the adapter needs another way
to hand the binary over. Settle that first; it decides whether the stage works
on a machine where Godot is not on PATH, which is the machine this runs on.

Worth doing `nav_gate.py` in the same pass — it answers the adjacent question
(does the navmesh bake across stairs) and feeds the same family of registry
fields. `ENGINE_GATES.md` describes both, plus `godot_gate.py` and
`mp_smoke.py`, as a manual reference run whose registry fields
(`runtime_walktest`, `godot_import`, `multiplayer_smoke_test`) are set by hand.
These are the asset gates. They belong in the planner.

**3. Lot places enemies twice, and nothing checks the two agree.** `lot.py:1337`
(the reporter) calls `site_spawns.place_enemies(site_spec, walk_pos)`;
`lot.py:975` (`_lasertag_hook_nodes`, the writer) calls it again with its own
`pos`, which has been through `seat_destinations` a second time with bounds
derived from the already-seated points. The comment claims "same inputs, same
answer". That claim is untested. Place once, thread the result through, or
assert the two agree.

**4. Lot emits absolute `res://` paths at source.** It bakes building GLBs as
`res://C:/Projects/.../shell.glb` — a reference to one developer's disk, which
is the plainest violation of the standalone contract. Staging rewrites them and
`PRESENTATION_UNRESOLVED_REF` blocks if any survive, so the guarantee currently
rests on two downstream repairs rather than on Lot not breaking it. Fix where
the path is written.

**5. A run that evaluated nothing reported a clean pass.** The worst defect in
this list, because a level that grades badly is fine and a pipeline that is
wrong about itself is not.

`--art` printed `Structural checks passed (blockers open: 0, total findings: 0)`
while every artifact on disk kept its previous timestamp and the reports in
those directories contain six findings each, including a FAIL on `TRAVERSAL`.
`index.sqlite` advanced; nothing else did.

Narrowed 2026-07-27, and the obvious explanation is wrong. **The cache-hit path
already replays findings** — `Scheduler._attempt_job` materialises the cached
outputs, calls `_normalize`, fails the job on any blocking issue, and returns
the issues on the outcome. So a cache hit is not silent, and "the findings were
dropped because it came from cache" is not the answer.

**Also eliminated, same pass:** the *execute* path does not drop findings
either. `_attempt_job` computes `issues = self._normalize(...)`, uses them for
the blocking check, publishes, and returns `JobOutcome(job=job, issues=issues,
artifacts=artifacts)` — findings are carried on the outcome in both the
succeeded and the cache-hit return. And both paths call `_publish_stable`, so
"outputs were never published" is not it either.

So the loss is not in the scheduler's outcome plumbing. The CLI computes its
line from `aggregate(summary.all_issues)`, and prints
`tag = "cache" if o.cache_hit else o.job.status.lower()` — which is how we know
those `succeeded` lines were genuine executions rather than cache hits wearing
a different label.

That leaves the aggregation itself, or something particular to that run's job
set. Threads:

* The stage lines in that run read `succeeded`, not `cache`. A cache hit sets
  `states.SKIPPED_CACHE_HIT`, which the CLI renders as `cache` — so those jobs
  took the *execute* path, reported success, and still wrote nothing. Either
  the command ran and its outputs were never published, or `succeeded` is being
  printed for a state that did not execute.
* How `summary.all_issues` is assembled from the per-job outcomes — that is
  the one link in the chain not yet read, and the only place left where issues
  present on every outcome can total zero.
* `work_dir` is `jobs/<job_id>/<attempt>/out` and `_publish_stable` HARD LINKS
  into `jobs/<job_id>/out`, so the stable copy and the attempt copy share an
  inode. Worth knowing before reasoning from timestamps again: those two paths
  cannot disagree, and a run that appears to leave `out/` untouched has not
  written its attempt dir either.

Start from the run that reproduces it rather than from the code: the
fingerprint receipt (`fingerprint.last.json`, written on every evaluation
including cache hits) records the digest and every input hash at decision time,
which is enough to tell a cache hit from an execution after the fact.

**6. The tactical advisory reads a scene that may not exist yet.**
`tactical.advise_scene` treats a missing scene as silence by design — the
adapter's pre-flight owns "there is no scene here" — but that assumes the two
run at the same moment. When they do not, the scene half of the advisory
silently vanishes. Make "I could not read the scene" say so.

**7. The certified set has drifted.** Four of seven pins no longer match disk:
deli_counter 0.83.0 → 0.88.0, level_factory 0.10.5 → 0.13.4, lot 0.23.0 →
0.24.0, zoo 0.31.0 → 0.32.0 — and today moved several of them further. Nothing
running is the combination `factory.manifest.json` certifies.
`level-factory verify-manifest` reports it in one command. The manifest's note
claiming patina's VERSION file is empty is also stale — it reads 0.18.0.

### Not to be worked on

Under the boundary at the top of this file, these are downstream's model of
combat and none of them make the levels better: the crew bot's target memory or
threat response; the enemy firing at t = 0.0 despite a 0.25-0.5 s reaction
delay; anything tuned against survival time, engagement distance, kill counts or
opening timing. Laser Tag findings of that shape are information for a human at
candidate selection, not work items.

### Smaller, carried

`LT_MetricsCollector.record_event` zeroes `position` for `PlayerStuck` and
`LineOfSightGained` via its trailing `_log_event(event_name, null,
Vector3.ZERO, metadata)` — which now matters, because `PlayerStuck` position is
exactly what item 1 would want to know. The crew's sight range is not settable
from the scenario resource (`LT_ENGAGEMENT_NOT_CONFIGURABLE`): the scenario has
`enemy_sight_range` and no player equivalent, so 45 m lives only in
`LT_BotPlayerController`'s `@export` default. Godot exits **1** on a WARN grade
and **2** on FAIL, so exit status cannot distinguish "graded poorly" from "run
failed". Laser Tag emits `NAVIGATION_MISSING` only to stdout, so LF's
`CODE_DEGRADED` can never fire from the report JSON. A `JOB_TIMEOUT` finding
should say "Godot was killed at the 900 s job timeout" rather than raw Windows
status `3221225786`. Lot ignores the brief's `target_minutes`
(`site_pacing.py`), and the project default `[25, 35]` disagrees with the
brief's `[12, 20]` with nothing reconciling them. Version constants disagree
across Lot (`VERSION`, `lot.py`, `version.py`, CHANGELOG) and LF
(`pyproject.toml` / `VERSION` vs CHANGELOG) — left alone deliberately,
fingerprints depend on them.

Retired from this list because they are fixed: provenance recursion (was
eleven deep, reached seventeen and killed a run, now filtered at the scheduler);
`cater.needs_build` comparing mtimes (now a content digest with a
`<glb>.spec.sha256` stamp); the non-portable absolute `ext_resource` (still
emitted, but promoted to item 4 rather than carried, because it violates the
standalone contract rather than being untidy).

## Commands

Tests, both repos. Note the asymmetry: Level Factory's `pyproject.toml` already
sets `addopts = "-q"`, so passing `-q` again on the command line makes it `-qq`
and pytest drops the summary line entirely — the run looks like a wall of dots
that never reports a count. Lot has no such `addopts`, which is why it prints
one and LF appeared not to.

```powershell
cd C:\Projects\gabagool_studios\gabagool_factory\lot
python -m pytest tests -q

cd C:\Projects\gabagool_studios\gabagool_factory\level_factory
python -m pytest tests
```

The run — note the `cd` is the **factory root**, not `level_factory`.
`level_factory/` has no `__init__.py`, so `-m level_factory` resolves as a
namespace package only when its parent is the working directory. Running it from
inside `level_factory` fails with a bare `No module named level_factory`, which
looks like a broken install and is not one:

```powershell
cd C:\Projects\gabagool_studios\gabagool_factory
python -m level_factory -C C:\Projects\gabagool_studios\gabagool_factory\rockay-ws run category5_baie_dore_001 --art --force
```

Use `--force` after changing any tool. A plain re-run re-evaluates the graph but
unchanged stages still cache-hit, and until the addon entered the fingerprint a
patched Laser Tag was an unchanged stage.

**Read the opening, per side.** The most useful check there is now — the enemy
column is what the gate reads, and the gap between the two columns is item 1:

```powershell
$ws = "C:\Projects\gabagool_studios\gabagool_factory\rockay-ws\.level_factory"
foreach ($s in 5017,5118,5219,5320,5421) {
  $r = "$ws\jobs\category5_baie_dore_001.laser_tag_evaluate.candidate.seed_$s\out\lasertag.report.json"
  if (Test-Path $r) {
    $j = (Get-Content $r -Raw | ConvertFrom-Json).summary
    "seed $s  enemy=$($j.avg_time_to_first_enemy_shot)  crew=$($j.avg_time_to_first_player_shot)  survival=$($j.avg_player_survival_seconds)  route=$($j.route_completion_rate)  wipes=$($j.team_wipe_count)  timeouts=$($j.timeout_count)"
  } else { "seed $s  -- no report" }
}
```

A blocked run leaves its report under `jobs\<job>\1\out\` rather than
`jobs\<job>\out\`, because the publish step is downstream of the gate. Swap
the path if a seed reads "no report" on a run that clearly executed.

Confirm the graded scene came from this run — the check the staging fix makes
possible, and which only started returning anything on 2026-07-27:

```powershell
$ws = "C:\Projects\gabagool_studios\gabagool_factory\rockay-ws\.level_factory"
foreach ($s in 5017,5118,5219,5320,5421) {
  $notes = "$ws\staging\category5_baie_dore_001.laser_tag_evaluate.candidate.seed_$s\staging.notes.json"
  "seed $s"; Get-Content $notes | ConvertFrom-Json |
    Select-Object scene_staged, scene_source_sha256, scene_source
}
```

A `staging.notes.json` of 140 bytes is the pre-fix shape and means the staging
fix did not run; ~440 bytes with a `scene_source_sha256` is the current one.

Compare what Lot wrote against what Godot loaded, for one seed. Note this can
only ever compare the artifacts *currently* on disk — if they came from
different runs it says nothing, which is the method error that cost a day:

```powershell
$ws = "C:\Projects\gabagool_studios\gabagool_factory\rockay-ws\.level_factory"
$seed = 5320
$built  = "$ws\jobs\category5_baie_dore_001.lot_assemble.candidate.seed_$seed\out\site_walk.tscn"
$graded = "$ws\staging\category5_baie_dore_001.laser_tag_evaluate.candidate.seed_$seed\level.tscn"
Compare-Object (Get-Content $built) (Get-Content $graded)
```
