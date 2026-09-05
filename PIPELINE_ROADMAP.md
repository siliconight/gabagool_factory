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

Lot suite green. Level Factory 471 passed, 11 skipped, 0 failures —
**482 collected**.

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

### Four commits that did not say what was in them

Not a pipeline defect, but the same shape as the ones above and it cost a
session's trust in its own history, so it is recorded here rather than in a
commit message nobody will read twice.

`commit_session.ps1` staged with `git add -A`. Four repos got a commit whose
message described a README banner and whose contents did not. `dispatch` took 28
files and ~2015 insertions of Level Factory smoke-test output — `mission.tscn`,
GLBs, PNGs, `HANDOFF.md` — build artifacts of this pipeline committed into a
tool repo. `deli_counter` took `stairwell.py` (+193) and a new
`test_stair_containment.py` (+165); `pixelcoat` took a new
`profiles/themes/rockay.json`; `patina` took its `VERSION`. Those three were
real, wanted work that predated the session and simply had nowhere else to go.

Fixed two different ways, because they were two different problems. The
artifacts went back to untracked and `_lf_smoke_out/` went into `.gitignore`
(`undo_smoke_out.ps1`). The source work was split — each repo's one commit
became the README banner plus a second commit that describes the change
(`split_swept_commits.ps1`, resumable, refuses to rewrite anything already
pushed). Arithmetic closes on all three: 372 = 357 + 15, 29 = 17 + 12,
13 = 1 + 12.

The root cause is fixed in `commit_session.ps1`: it stages tracked
modifications with `git add -u`, takes new files only when a caller names them
in `-include`, and prints what it deliberately left untracked. A commit that
does not say what is in it is worse than no commit, and the expensive part here
was not the sweep — it was that the sweep was silent.

### The anchors land on scraps

The first honest walktest, 2026-07-28. All four seeds came back `ok: false` with
the same seven legs failing in each, every one reading

    path stops 32.71 m short (disjoint islands)

Six measurements, each eliminating the previous hypothesis:

* **`nav_gate.py` passes the same building.** 356 polygons,
  `stair_0: ok (path lower<->upper)`. The stair geometry is sound.
* **But the gate proves it against geometry that never ships.** It loads the glb
  through `GLTFDocument` at RUNTIME, so no importer runs, every `-colonly` /
  `-convcolonly` node is still a MeshInstance3D, and it bakes with
  `PARSED_GEOMETRY_MESH_INSTANCES`. The assembled site instances the IMPORTED
  glb, where those same nodes are colliders with no visual mesh. That is a real
  defect in the gate, independent of everything below — see item 10.
* **Source geometry is not the variable.** Re-baking the same staged site three
  ways: mesh instances 40992 verts / 1809 polys, static colliders 54048 / 1822,
  both 95040 / 1827 — and 40992 + 54048 = 95040 exactly, so convex hulls parse
  fine and the stair ramps are in the bake. All three fail the identical nine
  legs.
* **No agent parameter is the variable either.** Six bakes over identical parsed
  geometry, varying one thing each: climb 0.6 (which floors cleanly, unlike the
  ratified 0.5 → 0.45), agent height 1.0, cell height 0.05, cell size 0.10.
  Island count stays at 61; lowering agent height makes it *worse* (70).
* **The navmesh is not fragmented.** Island sizes:
  `[1675, 10, 10, 10, 10, 2, 2, 2, ...]`. **91.7% of all polygons are in one
  connected island** — one large connected surface plus about sixty
  two-polygon scraps.
* **The anchors sit beside the scraps.** Snapping every declared anchor onto the
  baked mesh puts `crew_home` on the 1675-polygon island and lands proxy after
  proxy next to islands of 2. `crew_home` comes from `_walk_positions`; the
  other twenty come from `_navqa_anchors` + `_pv3_array(..., lift=1.0)`.

**The reading that fits every measurement:** an anchor snaps onto a two-polygon
scrap, and a path from a scrap to the main island genuinely does not exist, so
`map_get_path` returns a partial path and the director reports "disjoint
islands" — which is *correct*. The navmesh is not fragmented in general; the
endpoints are on the fragments. It also explains the one result that never fit:
the walkers reach 20/20 targets over ~770 m using twelve ladder/drop
transitions, because a physical capsule falls onto whatever surface exists and
walks on, while a path query is stuck wherever it snapped.

**Two corrections, both mine, both stated because a confident wrong reading is
what this file exists to prevent.**

I measured the site ground at 71.1% coverage of its bounding box — 5,492 m²
with nothing to stand on — and called it a tiling failure. It is not: four
building footprints at 44 × 32 m are 5,632 m², and `site_ground.py` documents
the policy that Lot cuts an inset hole under every building that demonstrably
floors itself. The holes are deliberate. The measurement was right and the
conclusion was wrong.

And I called "disjoint islands" a misleading inference, on the strength of a
probe that snapped anchors by **nearest vertex** while the engine uses
`map_get_closest_point`, which finds the closest point ON a polygon. A point
half a metre above the middle of a large polygon is metres from its nearest
vertex, so my snap distances are upper bounds and the "off-mesh" flags they
produced are not trustworthy. The director's own `SNAP_MAX` check uses the right
API and did **not** fire, which means every anchor is within the ratified 2.0 m.
The island membership is the part of that probe worth keeping.

**What is genuinely missing:** nothing checks the SIZE of the island an anchor
snaps to. Distance-to-mesh passes at 0.7 m while the anchor stands on a scrap
that goes nowhere, and those two failures are indistinguishable in the report.
See item 8.

### The scraps were the furniture — resolved 2026-07-28

The reading above was right about *where* the anchors were and wrong about *what*
they were standing on, and the difference is the whole fix. Four more
measurements, the first two in Godot and the last two offline against the shipped
glb and the walktest report together:

* **The stairs connect in the shipped scene.** `stair_probe.gd` runs
  `nav_gate.py`'s own test against `site_navqa.tscn`'s baked region rather than a
  private bake: all four building instances report `PATH lower->upper`, 14.6 m
  over 20 points, with navmesh 0.07 m from the mid-flight point. Item 10's method
  is still wrong; its pass transferred here. The storeys are joined and the
  geometry is not the defect.
* **Reachability is not symmetric, and the census hid it.** Only five of
  twenty-one anchors reached anything: `home` and one per building, all four
  snapping onto `slab_0`, a building's own ground floor. The other sixteen showed
  `reaches: 1`. They still landed in "one cluster of 21, 0 stranded" because
  `_reaches` counted a 2.9 m *drop* as connectivity in both directions, so
  union-find glued every island to the floor. A drop is not a two-way edge.
* **Every failing anchor snapped +0.3 m above a piece of furniture.** Parsing
  `shell.glb` and the four instance transforms in `site.tscn` and looking up the
  column under each anchor: `cage_counter` top 1.1 → snap 1.4; `count_table` 4.9
  → 5.2; `vault_block` −2.6 → −2.3. The floor slabs are at exactly −4.0 / 0.0 /
  4.0 / 8.0, where the room records say they are. Nothing had drifted.
* **The markers are ON the props, and the floor beneath them is inside a solid
  box.** `OBJECTIVE_CAGE` carries z 0.9 because it is on the cashier counter.
  `LOOT_VAULT_CASH` carries z −2.8 at the centre of an 8 × 6 m vault block. There
  is no navmesh directly under either, so the nearest surface in any direction is
  the prop's own top — a 1.0 m ledge nothing can climb to.

**A marker is where a thing IS. An anchor is where a body has to stand to use
it.** Those are different points, and the pipeline had never distinguished them.
Both earlier attempts at this were the same mistake in different directions: one
added a metre to markers that already carried body height, the other trusted the
marker height itself.

Fixed as Lot 0.28.0 (CHANGELOG 0.36.0) and Level Factory 0.18.0. `_navqa_anchors`
resolves every marker through `rooms[building/room].center[2]` — the storey's
floor elevation, read rather than derived from `story × 4` — and merges the
markers that coincide once dropped (the vault objective and the vault loot are
one XY, 0.2 m apart in Z; that pair is why the reachability census under-reported
for a day). The director then searches the anchor's own storey plane outward in
rings for the first place a body fits, so the vault loot resolves to the floor at
the vault's edge. The band is asymmetric on purpose: a body height DOWN, one
max_climb plus a voxel UP. Down is where the floor is when a marker carries body
height; up is how a counter top came to stand in for a floor.

Three things that used to be conflated are now separate findings.
`WALKTEST_ANCHOR_NO_FLOOR` means the anchor's storey produced no navmesh at all —
a room that did not bake, which is geometry. `WALKTEST_ANCHOR_ISOLATED` means it
stands somewhere real that connects to nothing — which is placement.
`WALKTEST_MARKER_BURIED` (minor, never blocking) means the route is fine and the
marker is inside the furniture. The old `SNAP_MAX` proximity test failed the
vault loot at 3 m and called it an off-mesh anchor, which blamed the navmesh for
where a marker was put.

### The vault is sealed on purpose — the last of it, 2026-07-28

With the anchors on their floors, failures fell from nine legs of thirty-nine to
one or two of thirty-one, and every remaining one was a vault. The basement
geometry, read straight out of `shell.glb`:

* `int_-1_4` is a full-height wall running the whole 32 m at building-local
  x 0. Its one opening is filled by `int_-1_4_open0_BREACHPANEL` (y −3.85 to
  −1.65) with its lintel above; the gap under the panel is **0.15 m**. The spec
  agrees — `kind: "breach"`, `breach_class: "reinforceable"`,
  `material: "concrete"`, tag `vault_breach`. The vault is entered by blowing it.
* The stair discharges at x −18 to −14, entirely on the far side. The vault half
  has no walkable entrance at all, correctly.
* `LOOT_VAULT_CASH` sits at the centre of `vault_block`, an 8 × 6 m mass that
  **straddles that wall**. Nearest standing room is ~3.5 m past a block corner,
  and the two sides are within centimetres of each other in distance from the
  marker — so which side the ring search picked was a tie-break on identical
  geometry. That is why it was one or two vaults per seed and not all four.

So the mission spine was going to fail on the vault forever, on every seed of
every mission, and `WALKTEST_ENFORCED` could never have been flipped.

Lot 0.29.0 runs the census twice: an anchor that comes out off the main network
is re-searched for the nearest standing room that can walk to a main-network
anchor **and back**, bounded by the same 6 m. For a sealed room that is the floor
outside its door, derived from the navmesh rather than guessed from a wall normal
Lot does not have for interior walls. It is the one place the walktest passes
over a substitution, so the anchor carries `unreachable_stand_m`, the director
prints it, and `WALKTEST_ANCHOR_BEHIND_BARRIER` reports it.

**Result:** three of four candidates `ok: true`, 0 of 31 legs failing, 0
stranded, 0 without standing room. The first walktest pass this pipeline has ever
produced. Item 13 is the fourth.

**Item 11 is smaller than it looked, and item 12 is what is left of it.** The
interiors do bake — `slab_0` carries navmesh, the stairwells connect, and
`crew_home` inside b2 reaches the street. What inflates the island count is that
props bake as walkable surfaces: `gaming_tables` is a 12 × 6 m box whose top is
72 m² of navmesh a metre off the floor that nothing can reach. Sixty-one islands,
91.7% of polygons in one piece, and the rest is furniture.

### One bake, two items — and the third was already fixed — 2026-08-14

Items 10 and 12 are two readings of one setting. Item 16 looked like a third and was not; that correction is below, and it is the most useful thing in this section.

`lot.py` writes `geometry_parsed_geometry_type = 2` into every walk scene it
emits (lines 1430 and 1643, and the value is in the shipped `.tscn` files).
`lot_site_walk.gd` says what that means in its own comment: *BOTH (default
here) parses meshes AND `PARSED_GEOMETRY_STATIC_COLLIDERS` (the .glb ships
`-colonly` bodies)*. And `geometry_collision_mask` — the property item 12
named as the fix — **does not appear anywhere in `lot`, `level_factory` or
`zoo`**. Not set wrongly. Not set.

So the navmesh bake consumes the visual meshes *and every static collider in
the scene*, unfiltered.

That one sentence produces all three symptoms:

* **The stairs (item 16) — NOT this, and the correction is the point.**
  This section first claimed them: the stairs ship `-convcolonly`, a convex
  hull over a staircase is a solid wedge at 39.2°, under the 55° the bake
  accepts, so it must bake walkable over solid — and `navmesh_solid_probe.gd`
  had swept the walker's capsule through `stair0ramp_-1` at 39 of 41 samples.
  It was wrong. The library sweep the same day walked **20 sites in 3,481 s
  with 0 stuck walkers and 0 barrier resolutions**, including all three sites
  that defined item 16. `lot`'s own CHANGELOG had said why since 2026-08-02:
  **0.40.0, "the walker could not climb a legal stair"** — gravity applied
  every frame regardless of `is_on_floor()`, pinning the capsule into the
  ramp-floor junction, and a step-up probe that was a single 0.5 m lift with
  no fallback. Its words: *a ramp that is legal by every number in
  agent_contract.json, and a physical capsule that cannot climb it. That is
  this tool, not the site.* The probe was sweeping from the walker's own
  pinned position, so it measured the consequence of the locomotion bug and
  read as a bake defect to someone arriving in search of one. Item 16 is
  closed.
* **The props (item 12).** `cage_counter`, `vault_block`, `gaming_tables`
  are static colliders in the same unmasked bake. Their tops bake walkable by
  construction, exactly as the item describes. The item was right about the
  mechanism and wrong only in assuming it was configured.
* **The gate (item 10).** `nav_gate.gd` bakes
  `PARSED_GEOMETRY_MESH_INSTANCES` — type 1 — against scenes that ship at
  type 2. Two bakes, two shapes, and a pass that cannot transfer because it is
  not measuring the same solid.

**The test that settled it was the sweep, not a rebake.**
`library_walk.py` on 2026-08-14: 20 sites, 3,481 s, **19 pass and 1 blocked**,
with `stranded`, `no_floor`, `barrier` and `stuck` all zero on every row. The
one blocked site is `ref_pvp`, and its walkers finished — 15/15 legs, 0 stuck.
Its finding is `LOT_DESTINATION_ABOVE_FLOOR`: an objective marker 3.60 m above
the site ground plane, too tall to read as furniture, so Lot left it where the
marker put it. That is item 9's residual gap — *Lot still cannot answer "is
this anchor over anything?" offline* — not a navmesh defect.

So for items 10 and 12 there is still no measurement, only the reading above.
The rebake at `geometry_parsed_geometry_type = 1` would still say whether the
unmasked colliders change the baked surface; what it can no longer be expected
to change is stuck walkers, because there are none.

**Type 1 is the diagnostic, not the fix.** Dropping static colliders loses
real geometry: a wall that ships as `-colonly` with no visual mesh vanishes
from the bake, and navmesh through walls is worse than navmesh through stairs.
The fix is the mask item 12 specified — prop and stair-hull colliders onto
their own physics layer in Deli Counter, masked out of the bake in Lot — and
it stays a cross-repo change wanting an `agent_contract.json` entry rather
than two magic numbers.

**What is asserted here and what is not.** Asserted, by reading: `lot.py`
writes type 2, `geometry_collision_mask` exists nowhere, and `nav_gate.gd`
bakes type 1 against scenes that ship at type 2. Inferred, and still not
measured: that the unmasked colliders are what put walkable polygons on prop
tops. So items 10 and 12 are NARROWED, not CLOSED.

**And the lesson this section is now mostly about.** Its first version joined
item 16 to these two on a hypothesis that `lot` 0.40.0 had already refuted and
fixed, in a CHANGELOG entry nobody was reading — because `lot`'s VERSION said
0.33.0 while its CHANGELOG documented through 0.41.0. The version drift
repaired earlier that same day had been hiding the answer to this file's
self-declared biggest open question. An instrument that measures a consequence
looks exactly like an instrument that measures a cause, and the only defence is
the record: the answer was written down, dated 2026-08-02, in the repo that
fixed it.

## What to do next

Status convention: one line directly above an item, carrying the evidence.

    *STATUS: CLOSED 2026-08-12 -- 127 lights in the shipped presentation scene*

    **30. Nothing instantiates the light loader ...**

Vocabulary is `OPEN`, `CLOSED`, `RETRACTED`, `NARROWED`, `SUPERSEDED`,
`ANALYSIS`. The last one is not a hedge: items 31 and 32 are reductions of
engine documentation, nothing closes them, and counting them as open defects
makes this file lie about its own size.

The table below is DERIVED from those lines by `roadmap_status.py`, not typed.
`roadmap_status.py --check` exits 1 when it drifts and `--write` regenerates
it, the way `factory_map.py` maintains the stage table in `PIPELINE_MAP.md`.
An item with no status line is reported as resting on a sentence --
`roadmap_status.py --unclassified` lists them, and that list is the remaining
work of adopting this.

<!-- BEGIN GENERATED: roadmap_status.py -- do not edit by hand -->

| # | status | item | evidence |
|---|---|---|---|
| 1 | **CLOSED** *(inferred)* | Cover is exonerated — the trap is somewhere else | Closed 2026-07-27 |
| 2 | **CLOSED** *(inferred)* | `walktest.py` into the DAG | Closed 2026-07-27** as Lot 0 |
| 3 | **CLOSED** | Lot places enemies twice, and nothing checks the two agree | 2026-08-16 -- PLACED ONCE AND THREADED THROUGH, which is the first of the two remedies thi |
| 4 | **OPEN** *(inferred)* | Lot emits absolute `res://` paths at source | — |
| 5 | **CLOSED** *(inferred)* | A run that evaluated nothing reported a clean pass | Closed 2026-07-27 as Level Factory 0 |
| 6 | **OPEN** *(inferred)* | The tactical advisory reads a scene that may not exist yet | — |
| 7 | **CLOSED** *(inferred)* | The certified set has drifted | Closed 2026-07-27 as **factory 1 |
| 8 | **CLOSED** | Nothing checks the SIZE of the island an anchor snaps to | 2026-08-14 -- shipped as Lot 0.28.0 + Level Factory 0.18.0; the seed_5219 report carries a |
| 9 | **NARROWED** | Lot emits nav-QA anchors nothing checks | 2026-08-16 -- the residual this item names for itself, "Lot still cannot answer 'is this a |
| 10 | **NARROWED** | `nav_gate.py` certifies geometry that never ships | 2026-08-14 -- quantified. `nav_gate.gd` bakes PARSED_GEOMETRY_MESH_INSTANCES; `lot.py:1430 |
| 11 | **RETRACTED** *(inferred)* | The building interiors barely bake | Retracted 2026-07-28 |
| 12 | **NARROWED** | Props bake as walkable navmesh, and nothing can reach them | 2026-08-14 -- the mechanism this item named is not misconfigured, it is ABSENT: `geometry_ |
| 13 | **RETRACTED** *(inferred)* | RETRACTED — seed 5320's vault was never broken; its walktest never ran | RETRACTED — seed 5320's vault was never broken; its walktest never ran |
| 14 | **OPEN** | Seed 5017 has a collision trap the path query cannot see | 2026-08-12 -- unchanged; re-measure after the first run on a level that has walls |
| 15 | **CLOSED** *(inferred)* | Fail-fast is mission-wide, but the failures are candidate-scoped | Closed 2026-07-28 as Level Factory 0 |
| 16 | **CLOSED** | The navmesh contains routes the collision geometry blocks | 2026-08-14 -- not a bake defect. Lot 0.40.0 fixed it as walker locomotion on 2026-08-02 (g |
| 17 | **NARROWED** | The pipeline has never been run cold, so nobody knows what it costs to | 2026-09-05 -- TWO CONSECUTIVE RUNS AT ZERO, BOTH SHIPPING A GATED PACKAGE, AND THE ITEM ST |
| 18 | **OPEN** *(inferred)* | Every gate measures whether a level WORKS. None measures whether it is | — |
| 19 | **OPEN** *(inferred)* | Every tool grew a Godot half before there was a DAG to say who owns wh | — |
| 20 | **OPEN** *(inferred)* | Patina's Godot half is a renderer from before Lux was one | — |
| 21 | **CLOSED** | Four of eight tools have drifted from what Level Factory certified | 2026-08-22 -- factory 1.34.1 promoted and verify-manifest reads TEN OK against the live ma |
| 22 | **OPEN** *(inferred)* | Outdoor props have no swap contract, so cover stays boxes forever | — |
| 23 | **CLOSED** *(inferred)* | A Node-typed export written by a tool is discarded in silence, and the | Closed for Lux on 2026-08-01; the general form is |
| 24 | **OPEN** *(inferred)* | Lux gives runtime scaffolding an `owner`, which is what bakes it into  | — |
| 25 | **OPEN** *(inferred)* | A project `cater` has SERVED does not run until the editor imports it | — |
| 26 | **OPEN** *(inferred)* | Something finally looks at the picture | — |
| 27 | **CLOSED** | The portable export ships a scene without its geometry, and every gate | 2026-08-12 -- 36 resources, closure ok, portability PASS. SESSION_0812 |
| 28 | **OPEN** *(inferred)* | The VRAM question is about zoo's GLB embedding, not about pixelcoat | — |
| 29 | **CLOSED** | The art path themes one building; the site is never themed, and the si | 2026-08-12 -- the export carries five archetypes plus site_base.glb, not one building |
| 30 | **CLOSED** | Nothing instantiates the light loader, so shipping the anchors would n | 2026-08-12 -- 116 OmniLight3D + 11 SpotLight3D under LuxFixtureLights in the shipped scene |
| 31 | **ANALYSIS** | Lighting: what the engine requires of the geometry, and what Lux can d | engine constraints, not a defect. Note project.godot writes gl_compatibility |
| 32 | **ANALYSIS** | Two lighting systems, and none of the interior one is switched on | a working model plus an engine fact; the interior lights do now spawn (item 30) |
| 33 | **CLOSED** | The export does not contain the level, and the closure judge said so o | 2026-08-12 -- 21 unresolved -> 0, 132 misrooted -> 0, engine parser_error_count 0 |
| 34 | **CLOSED** | The greybox is a site; the themed export is a fragment of one | 2026-08-12 -- themed_site_assemble; the export is the whole site, five buildings |
| 35 | **OPEN** *(inferred)* | The graybox/art relationship: it is a SWAP, and most of the recommende | — |
| 36 | **NARROWED** | Walking it. Zoo's inserts are exact; the layer with no slot is the one | 2026-08-12 -- walk plumbing superseded by cmd_walk wrapping the export; the nine findings  |
| 37 | **CLOSED** | Every building on the site is the same building | 2026-09-05 -- BUILT, THEMED, AND SHIPPED IN A PACKAGE. The mechanism was already there and |
| 38 | **CLOSED** | Light anchors hung below the slab, and four Deli Counter tests that we | 2026-08-02 -- cap_thick threaded into derive_light_anchors and build_light_manifest |
| 39 | **RETRACTED** *(inferred)* | Cache correctness: the mechanism is designed and never wired, and the  | RETRACTED: `--force` is not broken |
| 40 | **OPEN** *(inferred)* | The "is this called?" sweep, run | — |
| 41 | **NARROWED** | The dressing layer is STRUCTURAL ART routed through the decoration cha | 2026-08-18 -- THE ROUTING ARGUMENT STANDS AND EVERY NUMBER UNDER IT IS DEAD. Re-measured o |
| 42 | **NARROWED** | A level leaves the factory with a name that does not say what it is | 2026-08-14 -- stage 1 SHIPPED and proven on a real package: level_factory 0.26.0 (build di |
| 43 | **CLOSED** | A whole CLI spelling stopped working and nothing noticed | 2026-08-15 -- one failed stage, not nine failures, and not the cause written below. `prese |
| 44 | **OPEN** | The green boxes could be cars, and the collision would not change | 2026-08-14 -- specified by `Semantic_Proxy_Replacement_Art_Pass` and `City Collision ArtPa |
| 45 | **OPEN** | Large playable surfaces are visually flat, and the fix is not more gra | 2026-08-14 -- specified by `Surface_Dressing_Level_Depth_Guide`; nothing built. Item 41 is |
| 46 | **NARROWED** | Forty-five state machines a run, reaching nobody | 2026-08-22 -- THE PIPE IS CONNECTED AND FED. Steps 1-3 shipped and proven end-to-end on cr |
| 47 | **CLOSED** | A recipient with their own lighting has to take ours or take graybox | 2026-08-16 -- DELIVERED, and the cold package it was waiting on exists. All three shapes l |
| 48 | **CLOSED** | The same job and the same seed draw a different building on the art pa | 2026-08-16 -- FIXED and re-measured on a cold workspace. level_factory 0.38.0 keys the nar |
| 49 | **CLOSED** | Step 2.5 replaces a self-contained root scene with one that names a di | 2026-08-16 -- FIXED as level_factory 0.39.0 and proven on the package. `_assembly_building |
| 50 | **CLOSED** | The package ships a resource manifest that describes a different packa | 2026-08-16 -- FIXED as level_factory 0.40.0 and confirmed on the package. The finding was  |
| 51 | **CLOSED** | `lot`'s own suite has been red through every certification this month, | 2026-08-16 -- ALL THREE FIXED AND RE-MEASURED. TWO of the three mechanisms this item propo |
| 52 | **CLOSED** | `lot_demo_001` re-measured, and the route exposure it reports is the d | 2026-08-16 -- MEASURED on the mission it was overdue for. All stages EXECUTED rather than  |
| 53 | **NARROWED** | One Lux check is a silent no-op, and the filename literals are tidines | 2026-08-18 -- FIRST RANKED FIX SHIPPED, and the mechanism this item gave for it was WRONG. |
| 54 | **CLOSED** | One mesh spans a whole room, and two light caps are paying for it | 2026-08-24 -- CENSUS PASS, WALK CLEAN, CAP DELETED. The closing run (census #8, `walk.tscn |
| 55 | **OPEN** | The level ships sign fixtures with no sign art, and three of four cann | 2026-08-18 -- MEASURED. Four `AreaPanel_Surface` nodes ship in `lot_demo_001`, each a 1.4  |
| 56 | **OPEN** | The global light budget is derived from scene text, and the running le | 2026-08-23 -- MEASURED at discovery, unworked. Found by item 54's closing instrument on it |
| 57 | **OPEN** | Asset boundaries are implementation details; architectural boundaries  | 2026-08-23 -- FRAMED, UNWORKED. Raised from the 2026-08-23 walks of the tiled, deduped, tr |
| 58 | **NARROWED** | A facade corner is open to the sky, and light walks straight through t | 2026-08-25 -- FIXED AND VERIFIED ON REAL GEOMETRY. Deli Counter 0.102.0 insets each exteri |
| 59 | **OPEN** | One door, two corridors: a partition ends inside the aperture and spli | 2026-08-24 -- LIBRARY SURGERY LANDED; GENERATOR AVOIDANCE AND THE FOUNDING SIGHTING REMAIN |
| 60 | **OPEN** | Light walks through walls: a fixture in the next room lights this one' | 2026-08-24 -- FIRST TIER SHIPPED, WALK PENDING; THE FULL POLICY STILL UNDECIDED. Lux 0.25. |
| 61 | **NARROWED** | Optional color-preserving film emulsion for Lux | 2026-09-04 -- BUILT, COMPILED, RENDERED AND TIMED ON REAL HARDWARE IN LUX 0.28.0, AND AS O |
| 62 | **OPEN** | The capability-gap signal: a tool that cannot make what was asked says | 2026-08-24 -- CONVENTION WRITTEN, SIGNAL NOT UNIFORM, AND THE ONE PLACE THAT ALREADY BUILT |
| 63 | **OPEN** | Two coordinate frames share one `fit.dims` field, and nothing in a slo | 2026-08-24 -- REFRAMED THE SAME DAY IT WAS FILED, AND THE FIRST READING IS KEPT BELOW BECA |
| 64 | **OPEN** | Zoo built the corner module forty-one days ago and nothing has ever as | 2026-08-24 -- FOUND, PRICED, UNBLOCKED IN PRINCIPLE. Three concrete preconditions measured |
| 65 | **OPEN** | The site copies go stale silently, and the detector that would say so  | 2026-08-25 -- MEASURED AT 24 DAYS AND ~20 RELEASES, AND CLEARED THE SAME DAY. The propagat |
| 66 | **OPEN** | `verify-manifest` prescribes a remedy that under-proves what it certif | 2026-08-25 -- MEASURED, AND THE FIRST READING OF IT WAS WRONG AND IS KEPT BELOW. The suite |
| 67 | **OPEN** | `promote_factory.ps1` is a frozen one-off wearing a reusable name | 2026-08-25 -- READ IN FULL, NOT RUN. Anyone who runs it loses a CHANGELOG entry before it  |
| 68 | **CLOSED** | A blocker on the candidate a human SELECTED is discounted because the  | 2026-08-27 -- FIXED IN LEVEL FACTORY 0.50.0 AND PROVEN ON THE RUN THAT FOUND IT. `aggregat |
| 69 | **CLOSED** | Deli Counter's seed never varies, so every candidate is the same build | 2026-09-05 -- THIS ITEM'S OWN ACCEPTANCE TEST, MET ON A REAL RUN. It asked for distinct `s |
| 70 | **CLOSED** | `cold_run.py` counts the pipeline's own writes into a tool repo as int | 2026-08-27 -- BOTH GAPS FIXED AND PROVEN ON THREE SYNTHETIC RUNS. `cold_run.py` now ATTRIB |
| 71 | **CLOSED** | The fixture co-location gate measures bracket-to-bulb and calls it a f | 2026-08-28 -- RETRACTED AS FILED, REFRAMED, FIXED IN LUX 0.26.0, AND PROVEN TWICE: ONCE SY |
| 72 | **CLOSED** | Nothing checks that a brief's theme resolves until the art pass is alr | 2026-08-29 -- CHECKED IN FOUR PLACES, AND THE ONE THAT SAVES THE TIME IS `run` REFUSING BE |
| 73 | **CLOSED** | Two identical consecutive runs cached nothing and disagreed about what | 2026-09-05 -- MECHANISM FOUND, FIXED, AND PROVEN UNDER THE CONDITIONS THAT BROKE COLD RUN  |
| 74 | **OPEN** | Every wall in every building is the same 2.00 m module, and it gets wo | 2026-08-29 -- MEASURED ACROSS TWELVE SHIPPED BUILDINGS WITH A NEW INSTRUMENT, NO FIX ATTEM |
| 75 | **CLOSED** | Delco's facade relief was drawing the module grid it exists to break u | 2026-08-29 -- ZOO 0.53.0 AND 0.54.0. THE RELIEF WAS TRACING THE MODULE GRID BY TWO SEPARAT |
| 76 | **OPEN** | Every mechanism this factory has for making two copies of one module l | 2026-08-29 -- FOUR MECHANISMS READ IN THE CODE, NONE REACHABLE FROM A BRIEF. ONE OF THEM I |
| 77 | **OPEN** | `cold_run.py --begin` cannot tell that a run is starting mid-edit | 2026-08-29 -- COST ONE AMBIGUOUS COUNT ON `cold_7003`, AND THE AMBIGUITY IS UNRESOLVABLE F |
| 78 | **NARROWED** | Nothing measures how a level LOOKS -- only what it is made of | 2026-08-29 -- FILED AS "NOTHING MEASURES APPEARANCE", WHICH WAS FALSE AND WAS WRITTEN WITH |
| 79 | **OPEN** | Nothing in the pipeline represents a facade, so nothing can compose on | 2026-08-29 -- THE FRAME ITEMS 74 THROUGH 76 ARE SYMPTOMS OF. NAMED FROM A WALKTHROUGH CRIT |
| 80 | **OPEN** | Deli Counter's one-mesh-in-VRAM discipline is not carried any further  | 2026-08-29 -- DELI COUNTER'S GUARANTEE SURVIVES THE ART PASS; THE STEP AFTER IT IS WRITTEN |
| 81 | **NARROWED** | Zoo's wear noise runs at the mesh's vertex density, and a wall module  | 2026-08-29 -- THE MECHANISM IS REAL IN THE FILE AND INERT IN THE ENGINE. REMOVING THE WEAR |
| 82 | **ANALYSIS** | Every tool's contract is about a piece. No contract is about the whole | 2026-08-29 -- THE FRAME. ITEMS 73 THROUGH 81 ARE FACES OF THIS ONE FACT, AND IT EXPLAINS W |
| 83 | **NARROWED** | The renderer lights the wall per piece, so light draws the module grid | 2026-08-29 -- REFUTED AS THE CAUSE OF THE EXTERIOR BANDING, BY ABLATION, WITHIN THE HOUR I |
| 84 | **OPEN** | Zoo computes per-vertex wear, exports it correctly, and the engine doe | 2026-08-29 -- DIAGNOSED, NOT FIXED, AND THE FIX IS A DECISION RATHER THAN A FLAG. 1,896 KI |
| 85 | **OPEN** | Fixtures spawn inside walls, and the co-location gate cannot notice | 2026-08-29 -- OBSERVED IN A WALKTHROUGH AND SET ASIDE, NOT INVESTIGATED. RECORDED BECAUSE  |
| 86 | **CLOSED** | A 3 mm chamfer was shading every flat wall as a cushion | 2026-08-29 -- ZOO 0.52.0, AND THE ONLY VERDICT THAT MATTERS: THE PERSON WHO REPORTED IT LO |
| 87 | **NARROWED** | Deli Counter's one-mesh-in-VRAM discipline stops at the texture | 2026-08-29 -- MECHANISM PROVEN END TO END, NOT YET IN THE PIPELINE. `tools/detach_textures |
| 88 | **NARROWED** | Deli Counter stretches a unit box to fill slot remainders, and the ski | 2026-08-29 -- THE LANE IS CHOSEN AND CONFIRMED BY EYE, AND IT IS NOT ONE OF THE TWO THAT A |
| 89 | **CLOSED** | Disabling Detect 3D silently disabled mipmaps, and it cost nothing unt | 2026-08-29 -- FOUND AND FIXED IN THE SAME PASS, AS A DIRECT CONSEQUENCE OF ITEM 87. `mipma |
| 90 | **NARROWED** | `look_shots` was never measured against itself, so its own repeatabili | 2026-09-02 -- THE PER-PIXEL RULER IS STILL UNCALIBRATED AND EVERY `%px changed` FIGURE BEL |
| 91 | **CLOSED** | World-space UVs reached the shipped build | 2026-08-30 -- CONFIRMED ON A SHIPPED PACKAGE, NOT A MECHANISM PROOF. THE COMPOSED `out/pre |
| 92 | **NARROWED** | Lux REPLACES the art pass's lighting instead of adding to it | 2026-09-02 -- MEASURED, AND THE DELETION LOSES. SUN LINK vs DELETION IS overview -0.05 AND |
| 93 | **OPEN** | Editing a driver script does not invalidate its job's cache | 2026-08-30 -- A TOOL'S OWN CODE IS NOT IN ITS JOB FINGERPRINT, SO THE PIPELINE SERVES THE  |
| 94 | **CLOSED** | Nothing in the pipeline binds fixture emissives, and the gate that cer | 2026-09-01 -- MEASURED ON A REAL GATE RUN WITH THE NEW DRIVER STAGED (9,098 BYTES, NOT 5,6 |
| 95 | **OPEN** | The site light manifest declares a version its anchors outgrew | 2026-09-01 -- `lot.merge_lights` STAMPS A HARDCODED "1.0.0" ON A SITE MANIFEST WHOSE ANCHO |
| 96 | **OPEN** | Daylight anchors are specified and never realized, because the manifes | 2026-09-01 -- 24 WINDOW ANCHORS ARE DERIVED, MERGED, SHIPPED IN THE MANIFEST AND NEVER BEC |
| 97 | **OPEN** | `delco_1997` is a theme two repos would have to grow, and only the smo | 2026-09-02 -- A THEME NOTHING CARRIES, ASKED FOR BY THE ONLY HARNESS THAT PROVES THE PIPEL |
| 98 | **OPEN** | Deli Counter cannot commit through its own pre-commit hook | 2026-09-05 -- MEASURED WHILE COMMITTING, NOT WHILE LOOKING FOR IT. `check.py` EXITS 1 ON T |
| 99 | **OPEN** | A theme has to exist in two repos, and only two do | 2026-09-05 -- MEASURED, NOT FIXED. NINE PIXELCOAT PROFILES, FOUR ZOO STYLES WITH REAL SPEC |
| 100 | **OPEN** | `site_shape` silently falls back to a row | 2026-09-05 -- MEASURED AS A CONTROL DURING COLD RUN 5's PRE-CHECK. TWO BRIEFS ON DISK ASK  |
| 101 | **OPEN** | The handoff hands the server addresses that resolve to nothing | 2026-09-05 -- MEASURED ON A SHIPPED PACKAGE. THE EXPORT DELIBERATELY REPLACES DISPATCH'S ` |

**101 items: 41 open, 36 closed, 3 retracted, 18 narrowed, 3 analysis.** 21 rest on a sentence rather than a status line -- run `roadmap_status.py --unclassified` for the list.

A status is the block directly above the item, wrapped or not: `*STATUS: CLOSED 2026-08-12 -- what proves it*`. Vocabulary: `OPEN`, `CLOSED`, `RETRACTED`, `NARROWED`, `SUPERSEDED`, `ANALYSIS`.

<!-- END GENERATED -->

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

**Closed 2026-07-27** as Lot 0.25.0 + Level Factory 0.15.0. All four edits made,
plus two the trace had not seen.

**The open question is settled: `PlannedCommand.environment` DOES reach the
child.** `jobs/runner.run_command` builds `full_env = dict(os.environ)` and then
`.update(env)`, so the mapping is merged over the parent environment rather than
replacing it. The adapter passes `{"LOT_GODOT": <configured binary>}` and the
stage works on a machine where Godot is not on PATH. No `--godot` argument was
needed. (It does mean an absolute binary path lands in the fingerprint's
`declared_environment` — the same way Laser Tag's Godot path already lands in
`normalized_arguments` — so the cache is machine-specific, which is arguably
what it should be.)

**What the trace had not seen: `walktest.py` reports a check it never ran as a
pass.** With no Godot 4 binary it prints SKIP and returns 0, writing no report.
That is right for a hand-run — a developer without Godot should not have their
build fail — and catastrophic for a pipeline stage. It is item 5 exactly,
offered back through a runner flag, two days after item 5 was removed from the
scheduler. The adapter passes `--require`, which turns the skip into a failure;
no report is written and the output contract fails the job for the honest
reason. Verified by running it both ways with PATH stripped.

**Second thing the trace had not seen:** the report lands beside the scene, in
the throwaway project, not in the job's `work_dir`. Lot 0.25.0 adds
`--report-dir` (five lines and a copy that returns None when there is nothing to
copy, so a report that was never written cannot be papered over).

The findings **warn rather than block**, behind `WALKTEST_ENFORCED = False`.
They are built to block — reachability and closure are what this stack certifies
about the asset, unlike a firefight grade, so a site whose objective cannot be
reached is broken output rather than a design note — but the existing library
has never been checked this way and promoting on day one would fail missions
wholesale before anyone has looked at one. Same rollout as
`deli_counter.stairwell.CONTAINMENT_ENFORCED`. **A green run does not yet mean a
navigable candidate**; it means nothing has been promoted yet. Flipping the flag
is its own pass, and wants a walktest of the existing library first.

Adding a mandatory stage to the graybox base blocked every end-to-end and
service test at once — correctly, since the fixture pipeline had no nav QA
runner and a stage that cannot run must not pass. A stub `walktest.py` joins
`tests/fixtures/repos/lot/`. It deliberately does not reproduce the real
runner's skip path: the adapter always passes `--require`, and the skip is
covered in Lot's own tests.

Codes: `WALKTEST_LEG_UNPATHABLE`, `WALKTEST_WALKER_STUCK` (carries the
coordinates the director records for a walker that ran out the clock),
`WALKTEST_NAVMESH_EMPTY`, `WALKTEST_NO_SPAWNS`,
`WALKTEST_FAILED_WITHOUT_DETAIL` (a report that says `ok=false` and itemises
nothing reads as a pass to anything counting findings), and
`WALKTEST_REPORT_UNREADABLE`. Seven runner tests in Lot, seventeen adapter tests
and two planner tests in Level Factory.

**Still open, and the reason to keep this item in mind:** `nav_gate.py` was
worth doing in the same pass and was not. See below.

`nav_gate.py` answers the adjacent question — does the navmesh bake across
stairs — and feeds the same family of registry fields. `ENGINE_GATES.md`
describes it, plus `godot_gate.py` and `mp_smoke.py`, as a manual reference run
whose registry fields (`runtime_walktest`, `godot_import`,
`multiplayer_smoke_test`) are set by hand. These are the asset gates and they
belong in the planner, the same way `walktest_navqa` now does. The walktest
adapter is the working template for all three: stage a throwaway project, run
the tool with the flag that refuses to skip, declare the report as the expected
output, and gate the findings behind a rollout flag until the library is clean.

*STATUS: CLOSED 2026-08-16 -- PLACED ONCE AND THREADED THROUGH, which is the first of the two remedies this item names. `place_enemies` now runs once, in `assemble`, before the site report closes; the result is handed down through `write_walk_scene` -> `_lasertag_hook_nodes` -> `_lasertag_hook_plan`, which places only when `enemies=None` so the standalone test callers are unaffected. The assertion this item offers as its alternative was deliberately NOT taken: an assertion detects a disagreement after the fact, and there is now no second call to disagree. `patch_lot_place_once.py`. THE ORDERING CONSTRAINT THAT JUSTIFIED THE SECOND CALL IS INTACT -- `lot.py`'s comment says the walk scene is written after the report closes and a placement Lot could not honour has to travel with the site rather than sit in a .tscn nobody diffs; the placement still happens in `assemble`, and only the RE-placement is gone. VERIFIED ON THE ARTIFACT: the selftest proves byte-identical scene bodies on `BAIE_DORE` and counts place_enemies calls (1 standalone, 0 when threaded), but a fixture licenses nothing about a mission, so `lot_demo_001` was re-run and all three navqa scenes hashed identical to the pre-threading run -- e9177e9b (5017), 25bdce90 (5118), b3bd2815 (5219) -- with seed_5219's cover_plan unchanged at placed 16 / route_open 14 / unbreakable 0 / pinches 0, and `laser_tag_evaluate` correctly cache-hitting on all three. WHAT THIS ITEM'S HISTORY IS WORTH KEEPING FOR: it was OPEN with an explicit status line re-confirmed on 2026-08-12, it named both call sites, and an item-51 investigation on 2026-08-16 re-derived its entire content as a new finding without searching for it. The roadmap already knew. NOTED, NOT FIXED: `walktest_navqa` re-executed on all three candidates despite byte-identical input while `laser_tag_evaluate` cached -- same unchanged upstream, two different answers. Wasted work rather than wrong output, and another face of item 39's unpopulated `upstream_artifact_hashes`*

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

**Closed 2026-07-27 as Level Factory 0.14.0.** It was a third path, and the two
obvious ones were correctly eliminated first. The cache-hit path *does* replay
findings — `_attempt_job` materialises the cached outputs, calls `_normalize`
and returns the issues on the outcome. The execute path *does* carry them, and
both call `_publish_stable`. Neither was the answer.

The answer was the **resume pre-skip**, which runs before either path is
reached. `Scheduler.run` opened by reading each job's status out of the index
and, for any it found already succeeded, marking it complete without
dispatching it:

```python
if not force:
    for jid, job in jobs_by_id.items():
        existing = self.index.get_job(jid)
        if existing and states.job_succeeded(existing.status):
            completed.add(jid)
            summary.outcomes.append(JobOutcome(
                job=existing,
                cache_hit=existing.status == states.SKIPPED_CACHE_HIT))
```

That `JobOutcome` takes the default `issues=[]`. A pre-skipped job never reaches
`_attempt_job`, so `_normalize` never runs and its findings are never replayed.
And `cache_hit` is set only for a recorded `SKIPPED_CACHE_HIT`, so a job an
earlier run had EXECUTED came back `cache_hit=False` and the CLI printed
`succeeded` — which is exactly why the stage lines in that run read `succeeded`
rather than `cache` while nothing was written. The observation that looked like
evidence against the cache was evidence for a path nobody had looked at.

Two things made it a lost record rather than a wrong number, and both are still
open — see the carried list. `index.sqlite` has no findings table at all (jobs,
artifacts, missions, meta, nothing else), so a finding exists only in the run
that produced it. And `cmd_run` then wrote the empty `summary.all_issues` over
`.level_factory/validation/<mission>.json` and stamped the mission `built`.

**The fix is to delete the pre-skip, not to patch it.** The content cache
already does this work and does it honestly: keyed on the build fingerprint
rather than a recorded status, so it cannot be fooled by an upstream that moved
underneath a stale success — the failure mode the old comment there described
and accepted. Resume stays cheap because an unchanged stage still cache-hits
without re-running its tool. `--force` existed only to opt out of the pre-skip,
which means the honest behaviour was opt-in; it is now the only behaviour and
the flag's help says so.

**The test asserted the defect, and was green the whole time.**
`test_force_reruns_already_succeeded_job` asserted `"a" not in executed` and had
passed since the pre-skip was written. The behaviour was specified, and the
specification said a re-run may report a grade it never looked at. That is the
same shape as the `avg_time_to_first_contact` gate above: a measurement
faithfully implemented against the wrong quantity. A green suite confirms the
code matches the intent; it cannot tell you the intent was wrong. Rewritten as
`test_a_recorded_success_is_still_dispatched` (same graph, `force` both ways,
results asserted identical), plus six in
`tests/unit/test_resume_replays_findings.py`. Level Factory now reads
**445 passed, 11 skipped, 456 collected**.

**6. The tactical advisory reads a scene that may not exist yet.**
`tactical.advise_scene` treats a missing scene as silence by design — the
adapter's pre-flight owns "there is no scene here" — but that assumes the two
run at the same moment. When they do not, the scene half of the advisory
silently vanishes. Make "I could not read the scene" say so.

**7. The certified set has drifted.** Closed 2026-07-27 as **factory 1.6.0**.

Five pins were stale — deli_counter 0.83.0 → 0.88.0, level_factory 0.10.5 →
0.13.4, lot 0.23.0 → 0.24.0, pixelcoat 0.9.0 → 0.11.0, zoo 0.31.0 → 0.32.0 —
so nothing running was the combination `factory.manifest.json` certified.
`verify-manifest` now reports nine OK and laser_tag UNKNOWN, which is the
designed answer for a tool with no VERSION source. The stale notes on patina
(claiming its VERSION file is empty; it reads 0.18.0) and pixelcoat are gone.

Two things the new manifest says that the old one did not. laser_tag carries a
note explaining what *does* pin it — the Level Factory adapter hashes
`addons/laser_tag_tool` into `fingerprint_inputs`, so an addon edit invalidates
the cache even though no version string moves — because "UNKNOWN" on its own
reads as unprotected. And the description states what this set was **not**
verified by: walktest is not a DAG job yet, so playable-shell reachability is
still checked out of band. A certification that only lists what passed invites
the reader to assume the rest.

Re-certify with `recertify.ps1`, or by hand after any tool version moves.
Drift is the manifest working; drift left standing is the manifest lying.

*STATUS: CLOSED 2026-08-14 -- shipped as Lot 0.28.0 + Level Factory 0.18.0; the seed_5219 report carries anchors[22], reaches 21 on every one, one cluster of 22, 0 stranded, 0 without standing room. The status line said OPEN while this item's own body said closed on 2026-07-28*

**8. Nothing checks the SIZE of the island an anchor snaps to.** The
highest-leverage item in this file, because it is the gap that cost the day.
`_prove_path` already refuses an anchor further than `SNAP_MAX` (2.0 m, from
`agent_contract.json` `qa.snap_max_m`) — and that check passed on every anchor
in every failing run, because distance to mesh was never the problem. An anchor
0.7 m from a two-polygon scrap is *on* the navmesh and goes nowhere, and the
report cannot tell that apart from a genuinely blocked route.

The measurement to add uses only the engine's own API, no vertex heuristics:
after snapping all anchors, run `map_get_path` between every pair and record how
many other anchors each one can reach. An anchor that reaches zero is stranded,
and a leg failing from a stranded start should say so instead of describing the
navmesh. Twenty anchors is 400 queries; it costs nothing next to a 230 s walker
run. Emit it in the report as an `anchors` array, and the walktest adapter turns
it into `WALKTEST_ANCHOR_ISOLATED`, distinct from `WALKTEST_LEG_UNPATHABLE`.

Closed 2026-07-28, in two versions, and the second one is the lesson. Lot 0.26.0
built the census and it reported **0 stranded on a run where sixteen of
twenty-one anchors could not be walked to** — because `_reaches` carried
`_prove_path`'s vertical-access concession, which counts a 2.9 m drop as arrival,
so union-find glued every furniture island to the floor through one-way edges.
The new instrument had inherited the old instrument's excuse. Lot 0.28.0
clusters on strict reachability only; legs keep the concession, because a ladder
is real access and the proof says which kind it found. **A connectivity metric
built out of a permissive predicate measures the predicate.**

*STATUS: NARROWED 2026-08-16 -- the residual this item names for itself, "Lot still cannot answer 'is this anchor over anything?' offline", now has TWO measured instances and they agree. `ref_pvp` on 2026-08-14: an objective marker 3.60 m above the site ground plane, `library_walk.py` the blocked site of 20, walkers finishing 15 of 15 legs with 0 stuck. `lot_demo_001` candidate seed_5219 on 2026-08-16 under lot 0.42.0: the same finding at 6.00 m, `walktest_navqa` PASS with every bot `targets_reached 1/1`. Both are `LOT_DESTINATION_ABOVE_FLOOR`, both have clean walkers, and NEITHER is a navmesh defect -- Lot leaves the marker where it was put because it cannot read what is under it offline, and Laser Tag then cannot path to it and reports TRAVERSAL at 0%. The gap is unchanged and unbuilt; what is new is that it now has a second instance and a second site, so it is a class rather than one odd map. `site_cover.pinches()` remains the template this item names. See item 52*

**9. Lot emits nav-QA anchors nothing checks.** Closed 2026-07-28 as Lot 0.28.0
+ Level Factory 0.18.0 — see *The scraps were the furniture* above. Anchors are
resolved to their room's floor before they are emitted, coincident anchors are
merged and counted, an unroomed marker is named on stdout rather than guessed at
silently, and the director reports which of three different things went wrong
instead of one code for all of them.

What did **not** get built, and is the honest gap left: Lot still cannot answer
"is this anchor over anything?" offline. It knows the ground tiles
(`_ground_tiles`), the footprint holes (`ground_holes`) and now the storey
elevations, but nothing checks the props, and the props are what the anchors were
landing on. The check that caught this was Godot's, after the fact. If that
offline read-back is ever built, `site_cover.pinches()` is the template — the
same defect shape as the cover placement fixed on 2026-07-27, a search reporting
where it DECIDED to put something rather than where it PUT it.

*STATUS: NARROWED 2026-08-14 -- quantified. `nav_gate.gd` bakes PARSED_GEOMETRY_MESH_INSTANCES; `lot.py:1430,1643` write `geometry_parsed_geometry_type = 2` for the scenes that ship. The two bakes voxelise different shapes, which is why the pass does not transfer. Shares a root with 12 -- see *One bake, two items* above*

**10. `nav_gate.py` certifies geometry that never ships.** It loads the glb at
runtime through `GLTFDocument`, so the importer never runs and every
`-colonly` / `-convcolonly` node is still a MeshInstance3D; it then bakes with
`PARSED_GEOMETRY_MESH_INSTANCES`. The shipped scene instances the imported glb,
where those nodes are colliders. The gate's pass is real and does not transfer.
It should bake what the runtime loads — instance the imported scene, or parse
`PARSED_GEOMETRY_BOTH` the way the navqa scene does — or it will keep answering
a question nobody asked.

**11. The building interiors barely bake.** Retracted 2026-07-28. They bake.
`slab_0` carries navmesh in all four buildings, the stairwells connect all three
storeys, and `crew_home` standing inside b2 reaches the street. The polygon
arithmetic that produced this item was right and the conclusion was wrong: the
interiors are small because a 44 × 32 m floor eroded by a 0.4 m agent is a few
large polygons, not because they failed to bake. What is actually in the
remainder is item 12.

*STATUS: NARROWED 2026-08-14 -- the mechanism this item named is not misconfigured, it is ABSENT: `geometry_collision_mask` has no occurrence anywhere in lot, level_factory or zoo, and the bake is type 2, so every prop collider feeds it unmasked. Still the candidate cause of the 1,179 player_stuck_events in SESSION_0811. NOTE: the 2026-08-14 sweep walked 20 sites with 0 stuck walkers, so whatever these dead polygons cost, it is not stopping walkers today*

**12. Props bake as walkable navmesh, and nothing can reach them.**
`gaming_tables` is a 12 × 6 m box whose top is 72 m² of navmesh a metre off the
floor; `cage_counter`, `count_table`, `bar_cover` and `vault_block` all do the
same at 1.1, 4.9, 1.2 and −2.6. A 1.0 m ledge is above `agent_max_climb` (0.5,
floored to 0.45 by the bake), so every one of them is an island by construction.
That is sixty-one islands in a navmesh that is 91.7% one piece, and it is why an
anchor placed at marker height had somewhere wrong to land at all.

Dead polygons are not harmless: they are what a nearest-navmesh query finds
first, and any future code that asks "where is the navmesh near X" will hit them
the same way. The mechanism is `NavigationMesh.geometry_collision_mask` — put
prop colliders on their own physics layer in Deli Counter and mask them out of
the bake in Lot's navqa and site scenes. That is a cross-repo change with a
collision-layer contract in the middle of it, so it wants its own pass and its
own entry in `agent_contract.json` rather than two magic numbers.

The alternative reading, which should be settled before building either: some
props *should* be mountable (a bar top, a low crate) and the right answer is a
ramp or a step, not a mask. Deli Counter owns that decision — it is the repo that
knows which prop is cover and which is scenery.

**13. RETRACTED — seed 5320's vault was never broken; its walktest never ran.**
This item said one candidate of four reported a vault anchor off the main
network, and proposed measuring the geometry before touching the search bound.
The measurement was worth making and the item was wrong, in the most instructive
way available: there was nothing wrong with seed 5320.

Rasterising both seeds' basements offline — cell size from the bake, blocked
wherever a collider occupies the agent's headroom, eroded by the agent radius,
flood-filled from the stair discharge — gives *identical* numbers: 1191.8 m²
walkable, 594.2 m² (49.9%) reachable from the stair, nearest standing room 3.74 m
from the loot on the sealed side, nearest **connected** standing room 3.75 m on
the stair side. Well inside the 6 m bound. There was no geometric difference
between the seed that failed and the three that passed.

What was different is that seed 5320's `walktest_navqa` **had not run**. Its
`fingerprint.last.json` was 7.7 hours older than the other three, and its `out/`
still held a report from the previous director. The verdict on screen was that
stale file being read as the current answer — by the printer I wrote, and by me.

The chain, and every link is worth keeping:

* `LT_ROUTE_NEVER_COMPLETED` blocked seed 5320. That is Laser Tag reporting a
  navigability fact from a firefight — on a report showing 835 player-stuck
  events, six team wipes and a 180 s clock.
* The scheduler fail-fasts on the first blocked job, so `walktest_navqa` for that
  candidate never dispatched. **The coarse instrument silenced the precise one.**
* `RunSummary.outcomes` holds only jobs that ran, so nothing enumerated the
  casualties, and the summary line `jobs: 24 (cache reuse: 22)` read as a
  complete account of the run.
* A job's stable `out/` keeps the previous run's artifacts, so "never ran" and
  "ran and passed" are indistinguishable to anything reading the artifact.

Fixed in Level Factory 0.20.0: the route finding stops blocking and names the
walktest as the authority; `RunSummary.never_dispatched` is populated and
printed. All five candidates now walk — 0 of 31 legs failing on every one — and
seed 5421 had never been walktested at all.

The one carried note: `STAND_SEARCH_M = 6.0` is still a number I chose rather
than a ratified one, and every other dimension in this stack comes from
`agent_contract.json`. It belongs there with the rest.

**The lesson, which is the reason this stays in the file rather than being
deleted.** I wrote a roadmap item, a manifest exclusion and a commit message
about a defect that did not exist, on the strength of an artifact I never checked
the age of — while in the middle of an investigation whose entire subject was
proxies mistaken for the things they stand for. The instrument that produced the
wrong reading was one I had built that morning. Check that the measurement in
front of you was taken by the run in front of you.

*STATUS: OPEN 2026-08-12 -- unchanged; re-measure after the first run on a level that has walls*

**14. Seed 5017 has a collision trap the path query cannot see.** The first real
find the walktest has produced on its own, and the first thing PASS 2 has ever
caught that PASS 1 could not:

```
proof failures: 0
walker player_0: stuck@target_8 at (20.5, 0.9, -2.7) reached 8/16
walker player_1: stuck@target_8 at (20.5, 0.9, -2.7) reached 8/16
walker player_2: stuck@target_8 at (20.5, 0.9, -2.7) reached 8/16
walker player_3: stuck@target_8 at (20.5, 0.9, -2.7) reached 8/16
```

Every path proof passes: the polygon graph says there is a route to `proxy_8`.
Four independent capsules under real physics then stop at the *same coordinate*
on the same leg. That is not noise — it is deterministic, and it is exactly the
class the walker pass exists for. Something at (20.5, 0.9, -2.7) is walkable on
the navmesh and not traversable by a body: a lip above `max_step_up`, a doorway
narrower than the capsule after collision margin, or geometry the bake smoothed
over that the collider does not.

Start by finding what is at that point in seed 5017's site — the same offline
column read that settled the anchors will do it — and compare the navmesh
polygon there against the collider. If it is a doorway, `min_door_width` in
`agent_contract.json` is the number it should have been checked against and Deli
Counter owns it.

**15. Fail-fast is mission-wide, but the failures are candidate-scoped.**
Closed 2026-07-28 as Level Factory 0.22.0.

`Job.candidate_id` had existed all along; the scheduler was not reading it. A
job that fails now eliminates its CANDIDATE and lets the other four finish, and
only a mission-level job — one with no `candidate_id` — still stops the run.
Dependents needed no handling at all: `ready` is only appended when a dependency
SUCCEEDS, so anything downstream of a failure already never became ready. What
was missing was saying so. `RunSummary.not_run_reason` gives every un-dispatched
job its sentence, because the bare list reads as five things going wrong on a
run where four candidates built cleanly and one was correctly dropped.

Seven tests cover it, including the two edges that matter. A mission-level
failure still fails fast — the concession is narrow, and nothing downstream of
one can be salvaged by carrying on. And all five candidates failing is *not* a
blocked run: it is a mission with nothing to select from, which is candidate
selection's decision to announce rather than something the scheduler should
disguise as a crash.

This was the precondition for `WALKTEST_ENFORCED`. Flipping it before this would
have turned one flawed candidate into a dead mission.

*STATUS: CLOSED 2026-08-14 -- not a bake defect. Lot 0.40.0 fixed it as walker locomotion on 2026-08-02 (gravity applied off-floor; single-lift step probe), and the library sweep on 2026-08-14 walked 20 sites in 3,481 s with 0 stuck walkers and 0 barrier resolutions -- including all three sites that defined this item. The earlier same-day narrowing to a convex-hull bake was wrong; see *One bake, two items* above*

**16. The navmesh contains routes the collision geometry blocks.** The library
sweep's whole remainder, and the biggest open question in this file.

Twenty registered mission sites re-walked with the fixed Lot on 2026-07-28.
Seventeen come back clean. **Zero stranded anchors, zero rooms that failed to
bake, zero barrier resolutions outside the casino, every mission spine walkable
on every site** — the anchor work generalises. Three fail, and all three fail
identically: every path proof passing, all four walkers stopped on one
coordinate, at a stair.

What the walker reports, once Lot 0.39.0 stopped the serializer eating it:

```
walker bot_1 STUCK at (35.8, -2.3, -14.9) 0.75 m from waypoint 2/18
  on_floor=true on_wall=true; touching: stair0ramp_-1
  STEP_FAIL: lifted clear but nothing to step onto ahead
  contact normal (0.0, 0.0, 1.0)
```

The normal is **horizontal**. And the ramp, measured out of the glb with full
node transforms rather than untransformed bounds:

```
slab_col_-1   y [-3.50, -3.20]     the basement floor, top at -3.20
stair0ramp    y [-3.20,  0.20]     foot exactly on that floor, rises 3.40 m
              x [-8.08, -3.92]     4.16 m run -- the flight climbs along x
              z [ 3.20,  4.80]     1.60 m wide
              side faces 3.40 m tall
```

39.2 degrees. The bake accepts 55, the walker's `floor_max_angle` is 56, and its
foot meets the slab exactly — there is no step to mount and no slope to fail.
The walker is walking into the **side** of the staircase, 3.4 m of wall, on a
path `map_get_path` produced. Three sites, one shape.

So this is not a walker defect and not a layout defect. **The bake and the
colliders disagree about the same staircase**, which puts it in the same family
as item 10 (`nav_gate` baking geometry that never ships) and item 12 (props
baking as walkable). It is the most serious of the three, because this one hands
out routes.

The measurement that closes it, and the probe is written
(`navmesh_solid_probe.gd`): take every baked polygon near the stuck point, stand
the walker's own capsule on it, and ask the physics server whether that capsule
is inside anything. A polygon a body cannot occupy should not have baked. If the
offenders name `stair0ramp_*`, the question moves to
`geometry_parsed_geometry_type = 2` — the scene parses mesh instances AND static
colliders, so the visual stair steps and the `-convcolonly` hull beside them both
feed the voxeliser, and those two are not the same shape.

If every polygon there comes back CLEAR, this reading is wrong and the route is
blocked by something the capsule query cannot see, which would be worth knowing
before anything is changed.

**Do not "fix" this by loosening the walker.** Lot 0.40.0 already made two
genuine walker improvements while chasing this — gravity applies only when
airborne, and the step probe tries three heights instead of one — and neither
moved the result, which is exactly how it should have gone. The walker is now
right and the route it was given is wrong.

*STATUS: NARROWED 2026-09-05 -- TWO CONSECUTIVE RUNS AT ZERO, BOTH SHIPPING A
GATED PACKAGE, AND THE ITEM STILL ASKS FOR MORE. `cold_8001` (bank_block_001,
varied lot, seen vocabulary) and `cold_9001` (precinct_yard_001, an archetype
no brief had requested and the one site shape never built): **0 interventions,
0 retries, 0 unattributed file changes each**, three pipeline-attributed spec
writes each, and a portable package each. The three earlier runs each failed
to produce one -- 7001 on a gate later found broken (71), 7002 on a theme that
did not exist (72), 7003 refused at export (73) -- and all three causes are
closed. WHAT IS STILL NOT MEASURED: an unseen THEME, which is not the same as
an unseen brief and is currently impossible -- item 99. Nobody has walked
either package, so both are "works" and neither is "good" (item 18), and
`LT_MAP_TRAVERSAL` is 0% on all six candidates as on every evaluation ever
run. Two is not "several". Evidence: `docs/findings/COLD_RUN_8001.md` and
`COLD_RUN_9001.md`, journals under `_runs/cold/`.*

**17. The pipeline has never been run cold, so nobody knows what it costs to
make a level.** The item the other sixteen do not cover.

Everything in this file measures a defect and closes it. None of it answers the
question the toolchain exists to answer: hand the tools a spec they have never
seen, run one command, and does a walkable, gated package come out with no
human and no assistant touching anything on the way? Today that is unknown, and
the numbers that look like they answer it do not:

    library_walk    19 of 20 sites walk       every one of the twenty has been
                                              iterated on. This measures a
                                              library already fixed, not a
                                              pipeline that works first time.
    check_all       steps/freshness/stairs    the same twenty, same objection
                    clean
    walkup_siege    walks end to end          reached after a long sequence of
                                              patches, which is the thing being
                                              questioned

**The metric is patches-required-per-level, and it is currently unmeasured.**
The acceptance test: pick a spec that has never been through the pipeline, run
it untouched, and record every intervention it needed. A run needing zero is
the first real evidence. A run needing four is a list of four defects, which is
worth more than another guardrail. Repeat on several specs before believing
either result -- one cold run that happens to succeed proves less than it feels
like it does.

**WHAT ROCKAY-WS IS, since this file has been sloppy about it.** It is a level
to iterate against. It is not the deliverable and it is not evidence of a
finished product. The deliverable is the TOOLS: a pipeline someone else points
at their own game to generate levels. A fix that makes rockay-ws work and does
not generalise has not moved the deliverable, and this file should stop counting
those as progress. (The same care applies in the other direction: rockay-ws's
342 .gd files are vendored copies of the lux, patina, pixelcoat and zoo addons,
already checked at their own repos, which is why check_all skips them. They are
copies, not evidence -- the distinction matters because a finding in genuinely
GENERATED output would be a finding about the generator and the most actionable
kind there is.)

**18. Every gate measures whether a level WORKS. None measures whether it is
GOOD.** The three problems reported from playing a generated level:

    stairs too steep to climb        check_stair_pitch.py    measured
    kerbs placed in odd zig-zags     nothing                 invisible
    paths drawn across road          nothing                 invisible
    carriageways

Two of three were caught by a person looking at the screen, and there is no
instrument that would have caught them otherwise. Every guardrail in this repo
answers "can a body traverse this" -- traversal correctness -- and a level can
be perfectly traversable and still read as obviously machine-generated. So long
as that gap exists, shipping requires a human to play every level, which is the
same dependency item 17 is about wearing different clothes.

The measurable part of "good" is where to start, because it can be gated:
a path that crosses a road should yield to it (walkup_siege's path_0 covers
16.0 m of asphalt at 30 degrees, path_2 covers 8.7 m at 66 degrees, and the lip
is 0.0157 m so no traversal gate can see it); a kerb cut should run
perpendicular to its kerb, not diagonally; a flight of stairs should have a
consistent pitch across a building. The parts that are not measurable stay a
human's job, and saying which is which is itself work nobody has done.

**19. Every tool grew a Godot half before there was a DAG to say who owns
what.** The general form of items 20 and 21, and the one to keep if only one
survives.

There are at least four editor/runtime addons across the toolchain:

    addons/patina/              PS1 shader, per-surface apply, dock
    addons/zoo_importer/        family/habitat manifests, ATT_ socket Snap
    addons/pixelcoat_importer/  fixes texture import settings, writes .tres
    deli_counter's plugin dock  "Set up & Play"

plus `addons/lux/`, which is a rendering framework rather than an importer.
Every one of them was the right call when it was written: the tool needed
something in-engine and nothing else existed to provide it. They accumulated the
same way the version drift in item 21 did — not through carelessness, but
because the picture arrived after the parts.

**The problem is that each one is a thing that does not survive a bare folder
drop**, which is precisely what the shared header of every README in this repo
forbids: "the deliverable is a level shell that must work standalone in somebody
else's Godot project with none of these tools present." An addon is not present.

The honest default, now that a DAG exists to enforce it: **one addon ships, and
it is Lux**, because lighting and display genuinely are runtime and cannot be
baked into a mesh. Everything else either bakes into the .glb and the texture
set, or it is authoring convenience that does not belong in a pack at all. Zoo's
Snap workflow and its exhibit manifests are the clear second case — they help
somebody build a level and cost a recipient nothing when absent.

**THE LIGHTING CHAIN IS THE EXAMPLE OF THIS ALREADY DONE RIGHT, and it is worth
copying rather than re-deriving.** Deli Counter decides WHERE lights belong and
emits `<building>.lights.json`. Lot merges every building's manifest with its own
exterior streetlight anchors into one site manifest. Then ONE contract feeds TWO
consumers with no second source of truth: **Zoo bakes the visible fixture — the
housing, the collision, the emissive face — anchored at exactly the point the
light emits from, and Lux spawns the `Light3D` rig at that same anchor.** Zoo's
half ships inside the .glb and survives a bare drop; Lux's half is the one addon.
Nobody has to reconcile a lamp with its light because neither of them decided
where it goes.

So Zoo's fixture work is NOT authoring convenience and does not belong in the
same bucket as its importer dock. The dock, the Snap workflow and the exhibit
manifests are the convenience half; the baked kit, dressing and fixture geometry
are deliverable and must ship.

**AND THIS MAKES THE DROPPED LIGHTS FILE WORSE THAN IT LOOKED.** The cold run
found that Lot wrote `coldrun_pawn_job.site.lights.json` with 7 anchors and
`lot/package.py` did not put it in the pack — its manifest lists ten files and
lighting is not one of them. Under this chain that is not a missing sidecar. It
means **the pack ships the lamp housings and not the lights**: Zoo's fixtures are
baked into the geometry and visible, and the anchors Lux needs to put a
`Light3D` at each one are absent. A recipient gets a level full of light
fittings that do not emit. Fixing that is one line in the packer and it should
not wait for anything else in this item.

Unresolved under this rule: Patina's decal pass instantiates `Decal` nodes from
`decals.instances[]`, and no shader change bakes that. Either the stamps composite
into the texture set offline, or decals remain a runtime dependency whoever owns
them. That is the single hardest case and it should be decided on its own.

**20. Patina's Godot half is a renderer from before Lux was one.** The specific
case, with code behind it rather than inference.

Patina's `ps1.gdshader` implements what its own header calls "the four signature
PS1 tells". Lux carries all four as named uniforms in
`lux_stylized_standard.gdshader` and `lux_ordered_dither.gdshader`:

    vertex snapping     vertex_snap_enabled, vertex_snap_resolution
    affine mapping      affine_amount               (9 references)
    ordered dither      lux_ordered_dither.gdshader (13 references)
    colour depth        quantize / levels           (8 references)

Lux adds banded diffuse, palette pull, rim, specular, wetness, mach-band
emphasis, and `grime` / `grime_color` on top. Patina's file is 2,688 bytes and
exists twice — `addon/patina/ps1.gdshader` and `shaders/ps1.gdshader`, identical
length. Lux's two are 7,799 and 4,437, at a version `verify-contracts` calls
certified. Patina's carries "FIRST-RUN-IN-ENGINE ... has not been walked in the
editor yet."

**THE REASON TO ACT IS NOT DUPLICATION. It is that Patina's shader is the one
component making vertex colour ambiguous.** In code:

    patina/ps1.gdshader   render_mode vertex_lighting, ambient_light_disabled,
                          shadows_disabled
                          vec3 col = COLOR.rgb;   // vertex colour = the lighting

    lux_stylized_standard render_mode diffuse_burley, specular_schlick_ggx
                          uniform bool use_vertex_color = true;   // -> albedo
                          plus a real light() function

Zoo bakes wear into COLOR_0 and its README says to enable "Vertex Color > Use as
Albedo to multiply the baked grime into the base color". Patina's OWN offline
pass bakes banding, mottle and per-slot variation into the same channel
expecting the same thing. Patina's shader is the only place in the toolchain
that reads it as illumination instead. Retire it and the channel means one thing
everywhere.

**THE MIGRATION IS ALREADY HALF-WRITTEN, in a flag.** Patina's `--depth` presets
are the seam: `lux` "bakes only what Lux can't derive — Lux owns runtime light,
so it owns shadow colour and distance fog", against `delco`, "standalone (no
Lux) — owns the whole look". That is Patina ceding ground one concern at a time
as Lux matured. Finishing it means making `lux` the only mode and retiring
`delco` as a compatibility path for a world that no longer exists.

    retires   ps1.gdshader (both copies), patina_apply.gd, patina_dock.gd,
              plugin.gd, plugin.cfg, the --depth delco/exterior presets
    stays     the entire offline bake: vertex nuance, banding, mottle,
              per-slot variation, auto-UV, anchors, dressing. Densify stays
              too -- Lux's affine has the same limitation, since Godot still
              exposes no `noperspective` qualifier.
    connects  a PS1 preset .tres beside Lux's five, and shell.patina.json
              feeding Lux uniforms instead of driving a private shader.

**THE OPEN QUESTION, not to be folded in as settled.** Pixelcoat's stated
purpose is "repeating materials, trim sheets" for 3D surfaces. Patina also emits
structured and posterized texture sets. If Pixelcoat owns the skin, Patina's
texture output should narrow to wear LAYERS -- grime masks, edge dirt, streaks
that multiply over a Pixelcoat pack rather than replacing it. That would make
the boundary legible: Pixelcoat is what a surface is made of, Zoo is the
geometry wearing it, Patina is what makes it look used, Lux is how it is lit.
But Patina posterizes textures while Lux quantizes the frame, and those may
compose into the intended look or fight and band on already-flat surfaces.
Read Patina's texture modes against Pixelcoat's before deciding. Only the shader
half of this item is established.

*STATUS: CLOSED 2026-08-22 -- factory 1.34.1 promoted and verify-manifest reads TEN OK against the live manifest. Six pins re-earned through the full runbook (zoo 0.48.0, deli_counter 0.94.0, lot 0.48.0, level_factory 0.48.0, dispatch 0.4.2, laser_tag 0.9.0): zoo walkabout green through Blender 5.1.1, 536+380+82 tool tests, LF fast suite + real-tool smoke, laser_tag's 68-check and spawn-separation runners plus the 3-process ENet trio (HOST/CLIENT/LATE PASS). The re-cert itself surfaced three latent defects, which is the argument for running it: dispatch's suite had been un-collectable since the v0.2 refactor (fossil authority.py, retired as 0.4.1), the suite read its own UTF-8 outputs as cp1252 on Windows (0.4.1 follow-up), and 0.4.1's VERSION predated the code it named -- verify-manifest's staleness check refused it and 0.4.2 is the bump it demanded. laser_tag's phantom v0.8.0 tag is also retired: v0.9.0 exists on the commit it names.*

**21. Four of eight tools have drifted from what Level Factory certified.**
Measured, not argued: `python -m level_factory -C rockay-ws verify-contracts`

    DRIFT   deli_counter   installed 0.88.0  vs certified 0.75.0
    DRIFT   lot            installed 0.32.0  vs certified 0.18.3
    DRIFT   pixelcoat      installed 0.11.0  vs certified  0.9.0
    DRIFT   zoo            installed 0.32.0  vs certified 0.30.2
    OK      dispatch, laser_tag, lux, patina

**The four that drifted are exactly the four that produce geometry and art.**
The four that match are consumers and services. Lot is fourteen minor versions
past its certification, and the Level Factory adapter still declares
`output_contract_version = "lot.site.0.18"` to match — so anything run through
the DAG today is validated against a Lot predating the kerb-cut work, the step
gates, and the flat-surface change. The art stages are the ones nobody has run
recently, and they are the ones furthest out of date; those two facts are the
same fact.

Note that item 20 would re-certify two tools that currently read OK. That is not
an argument against it, but it does mean the drift should be closed first, so
the re-certification has a clean baseline rather than absorbing four unrelated
version jumps at the same time.

**22. Outdoor props have no swap contract, so cover stays boxes forever.** The
art path's missing wire, and the reason a lit site still reads as a blockout.

Lot places cover as primitive 1 m boxes -- `LOT_COVER_PLACED: 22 piece(s) of 2 m
cover were placed to break sightlines` -- and nothing downstream is invited to
replace them. That is not a Zoo limitation. Zoo already owns "structural kit
modules built to Deli Counter's slot dims, dressing props, and light fixtures",
and it already does exactly this swap one scale down:

    Deli Counter    greyboxes a building, emits <name>.slots.json -- "every
                    wall / doorway / window / breach slot with a transform, fit
                    dims, and a role"
    Zoo             builds modules to those dims; "the resolver swaps them in
                    for the grey boxes -- missing modules keep the box, so the
                    art pass stays progressive"

**Lot has no equivalent.** There is no `<site>.slots.json`, so Zoo's props and
Pixelcoat's skins have nothing to resolve against outdoors. The machinery exists
at both ends and the manifest between them does not.

WHY THIS IS NOT JUST "EMIT A LIST OF POSITIONS". A car is not a 1 m cube. Cover
was placed to occlude a measured sightline -- Laser Tag opens fire at 45 m and
`LOT_SIGHTLINE_OPEN` reports what is still exposed after placement. Swap in
geometry with a different footprint and the thing the placement was solving has
silently changed, with no gate able to see it. Which is precisely what Zoo's
`fit_*` validation is for: "modules whose dimensions exactly fit the requesting
slot". So outdoor cover wants the same treatment as a wall slot -- transform,
fit dims, and a role (`vehicle`, `dumpster`, `crate`, `planter`) -- with the box
kept whenever nothing fits, so the art pass stays progressive here too.

The same contract would carry the rest of the outdoor vocabulary: blockers are
already "facade shell" capable, and roads, kerbs and courtyards are surfaces
Pixelcoat could skin if anything told it their extents and material roles.

Do not start this before the drift in item 21 is closed. It adds a contract
between two tools that are both currently uncertified.

**23. A Node-typed export written by a tool is discarded in silence, and the
whole library carries it.** Closed for Lux on 2026-08-01; the general form is
open.

Godot resolves an exported Node property from a `.tscn` only when that node's
`[node ...]` header lists the property in a `node_paths` field. The text loader
builds its set of node-path properties from that field alone. A property written
as a bare `sun_light = NodePath("../Sun")` is therefore assigned literally — a
NodePath into a `DirectionalLight3D`-typed slot — and GDScript rejects the type
and drops it with **no error, no warning, and no trace at load**.

`tools/lux_inject.py` wrote exactly that, so Sun Link had never once taken
effect. Measured on 4.7.stable with one field the only difference: two visible
DirectionalLight3D against one, and the adopted sun reading the preset's 1.500
instead of Lot's untouched 1.000. The two suns sat **one degree apart** in
elevation, which is why the result read as shadow acne rather than as an obvious
second light — and why four commits of geometry work were spent on it first.

The sweep is the part to keep. Across all 242 `.tscn` on disk:

    LuxRoot scenes                33   (9 product + 24 addon copies)
    declaring node_paths           0
    not declaring node_paths      33

The string does not appear anywhere in the tree.

**But it only bites one of the two paths, and the first draft of this item got
that wrong.** A LuxRoot reaches a scene either through `tools/lux_inject.py`,
which writes the node as TEXT, or through Level Factory's `lux_apply` job, whose
`run_lux_apply.gd` builds it IN-ENGINE and saves with `PackedScene.pack()` +
`ResourceSaver.save()`. The engine's own saver emits `node_paths` for a
Node-typed export automatically, so path 2 could never have had this defect --
and in any case has no sun to link to: the composed presentation scene comes
from `deli_counter/themed_tscn.py`, whose entire node vocabulary is a root
`Node3D`, a `GreyboxBase` instance and one instance per slot. No
`DirectionalLight3D`, no `WorldEnvironment`, no `Sun`. So "every dressed project
has been double-lit" is true of the `cater`/`lux_dress` path and false of the
Level Factory path.

Which leaves the open question this item did not start with: **the two paths
ship different lighting and nobody has compared them.** Path 1 ships Lot's `Sun`
driven by Lux. Path 2 ships a bare scripted `LuxRoot` with `active_preset` and
none of Lux's runtime children -- at runtime `Engine.is_editor_hint()` is false,
so Lux sets no owner and `PackedScene.pack()` drops them -- relying on
`apply_on_ready` to re-manufacture the look wherever it loads. That is a
defensible design and it is not the same picture as path 1's, which is enough to
want it measured rather than assumed.

**The fix does not reach the existing library.** `lux_inject` returns early on
`if SCRIPT_RES in src`, so re-running it prints "already has a LuxRoot" and
changes nothing; those scenes need restoring from their `.pre_lux` backups and
re-injecting. And the general defect is not Lux's: any tool in this repo that
writes a Node-typed export into a scene has the same hole, and nothing checks
for it. A `node_paths` assertion belongs next to
`PRESENTATION_UNRESOLVED_REF` — it is the same class of guarantee, a reference
that looks written and is not.

**24. Lux gives runtime scaffolding an `owner`, which is what bakes it into a
saved scene.** The mechanism behind the editor accumulation, confirmed
2026-08-01. The multiplication is not.

Driving Godot's headless editor at a dressed project and reading the edited
scene tree: of the six children Lux parents onto itself, exactly three carry
`owner = edited_scene_root` — `LuxWorldEnvironment`, `LuxSun`, and the post-FX
`CanvasLayer` — and exactly those three are the ones present in
`_runs/lux_0801b`'s editor-saved scene. The three ownerless module Nodes
(`LuxEnvironment`, `LuxLighting`, `LuxPostFX`) are absent from it. Owner is the
whole difference between runtime scaffolding and a saveable member of the scene,
and one Ctrl+S is all it takes.

The addon assigns it in nine places: `lux_environment.gd:42`,
`lux_lighting.gd:30`, `lux_post_fx.gd:57,58,59,84,85`,
`lux_fixture_spawner.gd:51,77`, `lux_light_loader.gd:43,57,188`. Runtime modules
should be ownerless; the editor tooling that legitimately wants a saveable node
should say so at the call site rather than every `ensure_*` doing it by default.

What this does NOT establish, and the reason the item stays open: a single clean
headless editor load produces **one** LuxSun and **one** CanvasLayer, not the
four lights and three stacks observed by hand. The multiplication needs whatever
else that session did — script reloads are the obvious candidate — and has not
been isolated. `patch_lux_rebuild.py`'s clearing loop was aimed at this and did
not stop it; it is defensible hygiene and it is not the fix.

Found alongside it: **in the editor, Lux creates a second WorldEnvironment**
beside the level's own, while at runtime it correctly adopts the existing one.
`ensure_world_environment`'s reuse path fails specifically under
`Engine.is_editor_hint()`.

**25. A project `cater` has SERVED does not run until the editor imports it.**

Running the walk scene on a generated project Godot has never opened gives 59
parse errors: `lux_root.gd` and `lux_preset.gd` fail to load outright because
`class_name` resolution needs the editor's scan, and all four buildings report
`Node './deli' was modified from inside an instance, but it has vanished`
because the `.glb` files were never imported. It does not self-heal — a second
run is byte-identical. One `--import` pass fixes it completely: 0 errors.

This is ordinary Godot behaviour and harmless for a human, who opens the project
before pressing F6. It is a silent trap for anything automated, and `cater`
closes with `SERVED -> open <scene> in Godot, F6` without mentioning it. Any
pipeline stage that runs a generated project must import first;
`tools/godot_probe.py` does, and that is the only reason the light census
measures a populated scene instead of an empty one.

**26. Something finally looks at the picture.** A partial answer to item 18, and
deliberately a small one.

`tools/look_shots.py` renders a generated level from cameras derived from its
own mission spine — eye-level shots standing on the scene's exported
`spawn_pos` / `objective_pos` / `extraction_pos` at the height of the Player's
own `Camera3D`, facing the next leg, plus an overview framed from the site AABB
against the camera FOV — and reports a Rec.709 luminance histogram per frame.
Nothing in it is a coordinate somebody liked, so a bigger site frames correctly
without re-tuning.

It does not close item 18 and should not be described as doing so. A histogram
cannot tell you a level reads as machine-generated; the kerb zig-zags and the
paths across carriageways are still invisible to it. What it removes from the
human's plate is the crudest failure — a frame crushed against white — which
until now nothing in the pipeline could see, because nothing in the pipeline had
ever looked at an image.

Its first honest result was a retraction, which is the reason to trust the
second one. A hand-run at 1280x720 through hand-placed cameras reported Lot's
own WorldEnvironment blowing 28.6% of the overview to pure white. Re-measured
through the tool's derived cameras at 1600x900, the same project clips 0.00% at
255; the real effect is 18.62% of pixels within three codes of white against
1.13% with Lux, and mean luminance 108.6 against 147.0. Two framings of one
scene are two instruments.

Not yet gated on anything, and it should not be until somebody decides what
number a level has to beat. It also needs a display — `--headless` disables
rendering — so on a machine without one it runs under llvmpipe, which is an
instrument you may A/B against itself and may not quote beside a Forward+ figure.

*STATUS: CLOSED 2026-08-12 -- 36 resources, closure ok, portability PASS. SESSION_0812*

**27. The portable export ships a scene without its geometry, and every gate in
the chain passes it.** Found 2026-08-01 by pointing `tools/look_shots.py` at a
freshly exported package. Half fixed; the half that matters is open.

`export --mode portable-godot` on `category5_baie_dore_001`, run minutes before
this was written, produced a package whose presentation scene declares twelve
`ext_resource` entries. **Ten of them are not in the package:**

    MISSING  site_base.glb
    MISSING  art/zoo/roof_rockay_01_w4400.glb
    MISSING  art/zoo/wall_rockay_01_w200.glb        (x160 instances)
    MISSING  art/zoo/wall_rockay_01_w35.glb         (x124)
    MISSING  art/zoo/wallEnd_rockay_01.glb          (x29)
    MISSING  art/zoo/doorway_rockay_01_w120.glb
    MISSING  art/zoo/doorway_rockay_01_w320.glb
    MISSING  art/zoo/breach_rockay_01_w150.glb
    MISSING  art/zoo/breach_rockay_01_w140.glb
    MISSING  art/zoo/window_rockay_01_w160.glb
    OK       runtime/lux/runtime/lux_root.gd
    OK       runtime/lux/presets/blue_hour.tres

**211 of the scene's 243 nodes instance one of those ten.** The package does
ship two `.glb` files -- `assets/lot.glb` and `assets/shell.glb` -- and the
scene references neither. There are zero mesh sub-resources. What a consumer
opens is a correctly-lit empty world: Blue Hour applied properly (sun at +4.0
degrees elevation, ACES, glow, fog), and nothing for it to fall on. Photographed
from the AABB centre at eye height in all four cardinal directions: four
near-identical histograms, mean 69, no geometry in any of them.

**Why nothing caught it, and this is the transferable part.** `closure.py`'s
`scan_closure` is correct -- run against that package by hand it returns
`ok: false, missing_resource_count: 10` and names all ten. It was reachable from
exactly one call site, `portability.py:68`, inside `run_portability_test` -- a
separate command, off the path that produces the deliverable. Same shape as the
traversal gate found the same evening: the guard exists, works, and is not on
the road.

Worse, the export wrote a file **named** `export_closure.json` that reported
`"unresolved": []`. That file is `localize_export`'s report -- the FIXER's log.
`localize.py`'s own docstring says it: *"scan_closure (closure.py) is the judge;
this module is the fixer."* The fixer's `unresolved` fills only when a repair was
ATTEMPTED and failed. A scene referencing a `.glb` that was never copied in is
not something the fixer tries to repair, so it leaves no trace. One name
answering two different questions is how an empty package read as verified --
including to the author of this entry, for about an hour.

**Landed:** `export_mission` now calls `scan_closure` and writes the verdict to
`export_closure_scan.json`, deliberately named apart from the fixer's log. It
warns rather than blocks, behind `CLOSURE_ENFORCED = False`, for the same reason
`WALKTEST_ENFORCED` does: the current export is broken by a *different* defect,
and failing on day one would block every export on something this change did not
cause. The export now prints ten `EXPORT_CLOSURE_BROKEN` lines and drops a report
saying `"ok": false`. Level Factory's suite still exits 0.

**Open, and it is the one that makes levels contain art:** the Zoo modules are
never copied. `export_mission` copies `base_dir` and `presentation_dir`; the
presentation dir is the `lux_apply` job's `out/`, and the `art/zoo/*.glb` live in
the **zoo_kit_build** job's output at `res://art/zoo/` in the staged project.
Neither copy brings them. The art pass runs, Zoo fills the slots, Pixelcoat
skins them, Lux lights it -- and the export drops all of it. Fix the copy, then
flipping `CLOSURE_ENFORCED` is a two-character change and the gate becomes real.

**28. The VRAM question is about zoo's GLB embedding, not about pixelcoat.**
Raised as "we do resource/VRAM sharing for deli counter, can pixelcoat do it
too"; the premise does not survive reading, and the direction of the error is
the useful part.

**Deli Counter does MESH sharing, not texture sharing.** `deli_counter.py:76`
caches Blender mesh datablocks keyed by role+dims, so the glTF carries one mesh
and N nodes. Measured on the rockay building: **333 module instances against 14
distinct PackedScene GLBs**, 23.8x reuse, carried by `wall_rockay_01_w200` (160)
and `wall_rockay_01_w35` (124). The phrase "one texture in memory" is quoted from
DC's own README where it is a *rider* on mesh sharing, not a mechanism. DC
authors no visual materials at all -- zero hits for `ShaderMaterial`,
`surface_override_material` or any material cache in the repo, and the README
says plainly *"Deli Counter doesn't bake visual materials -- you texture in your
engine."*

**The material sharing already ships, in zoo.** `zoo/zoo_keeper/bpylayer/materials.py:63`
caches one `M_Skin_<kind>_<theme>` per (kind, theme) and returns the existing
datablock on a hit; `_load_image` uses `check_existing=True`. Resolution is
kind-level by design (`core/skins.py`): every Zoo mesh already carries
world-meter cube-projected UVs, so one pack skins every metal part of every
species at uniform density.

**Nothing structurally blocks it.** Checked every candidate for a per-surface
parameter that would force distinct materials: tile density lives in **mesh
UVs**, wear in the `COLOR_0` attribute, tiling metres and opacity are per-pack
constants, interpolation is hardcoded, palette is baked into the albedo PNG. No
per-instance uniform is needed because nothing needs to vary per instance. Sign
faces are the one deliberate exception and should stay distinct -- three
storefronts want three signs.

**The actual gap:** `zoo/zoo_keeper/bpylayer/export.py:23` uses
`export_format="GLB"`, and GLB embeds textures as binary chunks. Blender's
material cache dedups *within* one export, but zoo emits one GLB per
(type, width), so each of those 14 module files carries its own copy of the same
pack. The 333 to 14 win is entirely geometric; the texture side is 14x, not 1x.
Deduplicating it means external texture references at the zoo export boundary or
a Godot-side post-import remap.

Two pieces of machinery for this already exist and have **zero consumers
anywhere in the factory**: pixelcoat's `integrations/godot/addons/pixelcoat_importer/pack_importer.gd`
writes one shared `_material.tres` per pack, and `pixelcoat/core/atlas.py` (v0.8)
packs N packs into one atlas per map. Grepping the tree for `pixelcoat-atlas`,
`_atlas.json` or `build_atlas` outside the pixelcoat repo returns nothing; zoo's
`skins.load_pack` reads `*.pack.json` only and cannot consume an atlas. Pixelcoat
0.11.0's docs mention VRAM, draw calls, memory and texture sharing exactly zero
times.

So: not a pixelcoat feature request. A zoo export change, with pixelcoat's
already-built importer and atlas as the machinery to point it at.

*STATUS: CLOSED 2026-08-12 -- the export carries five archetypes plus site_base.glb, not one building*

**29. The art path themes one building; the site is never themed, and the site
spec has no roads in it.** Proven by hand 2026-08-01. The design works, nothing
is wired, and the second half of this item was found by looking at a picture.

`presentation_compose` is described in `PIPELINE_MAP.md` as what makes `--art`
mean "themed level rather than grey level with a lighting pass". It composes one
BUILDING -- DC's `portable_building.build_package` under `--building-id site`,
named that only so the Lux stage can resolve it without knowing the building_id
at plan time. `lux_apply` then lights that building. Nothing themes the site,
and the exported package contains one building and no ground.

**The mechanism to fix it already exists in Lot and needed no code.** `lot.py`'s
`_building_source` prefers a `scene` key (a .tscn) over `glb`, and its docstring
says why: *"Deli Counter's primary output is the .tscn; the baked .glb is the
self-contained special case. Both are instanced the same way (a PackedScene
ExtResource), so this is the only place the distinction lives."* Proven by
running it: copy the compose output into a project, rename its `site.tscn` to
`themed_building.tscn` so Lot does not overwrite its own input, add
`"scene": "themed_building.tscn"` to each building in the candidate's site spec,
run `lot.py --walkable`:

    [lot] building 'b0' has both scene and glb; using scene (themed_building.tscn)
    [lot] assembled 'site_themed.json': 4 buildings, 100 markers, 28 rooms
    [lot]   -> site.tscn
    [lot]   -> site_walk.tscn  (spawn (-29, 0, 0) -> objective (-101.5, 16, 0)
                                -> extraction (39, -28, 0))
    [lot] site lights -> site.site.lights.json (72 anchors)

Four themed buildings, a mission spine, and a light manifest. Zero code changes
in either tool.

**Then the picture showed what the log did not say plainly: there are no roads.**
Lot had already reported it --

    [lot] WARNING: isolated buildings: b0, b2, b3
    [lot]   objective approaches: 0

-- and the reason is not Lot. Compare what cater's hand-authored specs carried
against what `_write_site_spec` generates:

    cater's coldrun_pawn_job.json      LF's _write_site_spec
      name, ground, buildings            name, ground, buildings
      paths      [garage->deli, ...]     --
      courtyards [{at, size_x, size_y}]  --
      cover      [{at}, {at, size}]      --
      perimeter  {height: 3}             --
      spawn/objective/extraction         spawn/objective/extraction

**Level Factory has never asked Lot for a road network.** No `paths`, no
`courtyards`, no `perimeter`. The site graph therefore has no edges, every
building is its own island, and there are zero approaches to the objective --
not a failure, an omission. Cover is the exception and gets placed anyway
(`LOT_COVER_PLACED: 11`), because Lot derives that from sightlines rather than
from the spec. This is the concrete answer to "we made sites with cater as a
starting point": the placement half was carried across and the connectivity half
was not.

**The limitation the probe found, and the reason to fix it before shipping this:**

    LOT_DESTINATION_COLLISION_UNREAD: 4 geometry source(s) could not be read for
    collision ... b0: themed_building.tscn: declares collision shapes in the
    scene text, which this reader does not model

Lot models collision in a `.glb` and cannot read it out of a `.tscn`. So with
scene-backed buildings every spatial check it runs -- nav-hook seating,
destination resolution, cover placement against footprints -- works from a
partial picture, and Lot says so with its own finding code rather than guessing.
That is the tool behaving correctly and it is still a hole: the themed path
currently degrades the checks that make a site walkable.

The work, in the order it should happen:

1. Teach Lot's collision reader to parse scene-declared shapes, or have the
   composer emit a collision sidecar Lot can read. Until then a themed site is
   assembled against an incomplete model of itself.
2. `_write_site_spec` emits `scene` alongside `glb` (Lot prefers `scene`), plus
   `paths`, `courtyards` and `perimeter`. One function, one dict.
3. Repoint `lux_apply` at the assembled themed SITE rather than the composed
   building, so one LuxRoot lights the whole level. Note that lighting the
   building and then instancing it N times would give N LuxRoots -- the thing
   Lot instances must be the un-lit themed scene.
4. Export ships the site. Item 27 fixed the assets; the entry scene still
   instances only the presentation building.

*Step 1 done, and steps 2-4 re-scoped from measurement, 2026-08-02.*

**Step 1 is in.** `lot/site_collision.py` now models scene-declared colliders:
BoxShape3D exactly, sphere/capsule/cylinder by conservative bound, everything
else still `unread`. The distinction that makes it safe is the body above the
shape -- `Area3D` is not a wall. Deli Counter bakes a ladder's climb volume as
an `Area3D` with a `CollisionShape3D` inside, and in the themed scene measured
today that was the ONLY `CollisionShape3D` in the file: the reader was blinding
itself over the single node that must NOT be solid, because filling it would
turn the one route up into a blockage. Six tests added, 329 pass in Lot.

**Steps 2-4 are smaller than this item assumed, and the blocker is elsewhere.**
Lot needs no further work. `_building_source` already prefers `scene` over
`glb` and says why -- "Deli Counter's primary output is the .tscn; the baked
.glb is the self-contained special case. Both are instanced the same way" --
and `read_site` already resolves `b.get("scene") or b.get("glb")`. **Lot can
assemble a site out of themed building scenes today.**

What is missing is a job that asks it to. The DAG runs
`lot_assemble` -> candidate selection -> zoo/patina -> `presentation_compose`
-> `lux_apply`, so at the moment the site spec is written the themed building
does not exist yet. And `presentation_compose` composes ONE BUILDING and names
its output `site.tscn` -- the driver says so outright: "`--building-id site`
gives the scene a stable name so the Lux stage can resolve `<out>/site.tscn`".
Everything downstream reads a file called `site.tscn` and reasonably takes it
for the site. The planner's own comment records the moment this was cemented:
"Lux apply over the COMPOSED themed presentation scene (not the greybox site)
-- this is the wiring that was missing."

Measured consequence, item 34: Lot's greybox spans ~150 m and holds four
buildings; the themed export spans ~27 m and holds one.

So the remaining work is one new DAG node, not a rewrite:

    lot_assemble ... -> presentation_compose -> [themed_site_assemble] -> lux_apply

`themed_site_assemble` re-runs Lot with the SAME placement spec the greybox
used, with every building's `scene` set to the composed themed building. It is
cheap because there is only one themed building to make: `_write_site_spec`
already points every building at the same `shell.glb`, so the themed site is
that one composed scene instanced N times at the placements Lot already chose.
`lux_apply` then lights the site instead of a building, and the export follows
Lux as it already does.

Two alternatives, rejected and recorded so they are not re-proposed:

- *Move compose before `lot_assemble`.* Structurally blocked: compose depends
  on candidate selection, which depends on Lot's output.
- *Have compose emit the site itself.* It would duplicate Lot's placement,
  perimeter and path logic in Deli Counter's composer, which is the one thing
  the adapter boundary exists to prevent.

The thing to watch when it lands is the collision contract. The greybox site is
authoritative for collision; the themed scene keeps DC's greybox floors as its
walkable base, so a themed site should read the SAME solids as the greybox one.
`tools/stage_census.py` will show the node and reference counts; the honest
check is that the walk test still reaches 16/16 from the themed site, not that
the scene looks right.

*Landed and photographed, 2026-08-02.* `themed_site_assemble` is in the DAG
between `presentation_compose` and `lux_apply`, and the export carries a site.

    scene                overview eye_y   implied extent
    Lot greybox                  122.39           ~150 m
    themed export, before         21.97            ~27 m
    themed export, after         115.68           ~142 m

The frames agree with the number: four buildings in a row on the plate, the
same shape Lot's greybox has, and the objective shot stands in front of a
two-storey facade with a lit doorway instead of one wall run. The ~8 m the
themed site is short of the greybox is the AABB reading themed geometry rather
than greybox blocks and is not, on this evidence, a defect.

Node counts read low and correctly: `themed_site_assemble` 119 nodes / 1
ext_resource, `lux_apply` 120 / 3. The site INSTANCES the composed building
rather than inlining it, so the building's 353 modules sit behind a single
reference, and Lux's delta is +1 node (the LuxRoot) and +2 references (the
preset and `lux_root.gd`) -- the same delta it had before.

Three things had to change together and each is worth naming:

- **The spec file's DIRECTORY varies, not its name.** The Lot adapter derives
  expected outputs from the spec file's stem while Lot names outputs from
  `spec["name"]`. `site_themed.json` made the adapter wait for
  `site_themed.tscn`, Lot wrote `site.tscn`, the job failed on a missing output
  and took `lux_apply` with it. Two naming authorities over one file, and only
  one of them had been asked.
- **The export stopped deleting `site.tscn`.** That skip was added earlier the
  same day and was correct while Lux inlined its geometry. Once the site
  instanced the building instead, `lux.applied.tscn` carried `res://site.tscn`
  as a reference and the skip broke the package. The closure judge caught it on
  the first export -- `EXPORT_CLOSURE_BROKEN: unresolved res://site.tscn` -- and
  named the exact file.
- **The entry scene instances ONE of the two.** `write_entry_scene` instanced
  `site.tscn` AND `presentation/lux.applied.tscn` as peers, which is what the
  skip had been suppressing. They are not peers: the presentation scene is the
  level, `site.tscn` is what it is built from. The presentation scene wins when
  it exists; `site.tscn` is the entry only for a graybox export with no
  presentation pass, and a control test now covers that case.

`navqa` is deliberately off for the themed site: re-baking nav from themed
geometry would judge navigation against what the collision contract calls a
visual substitution, and a disagreement there is a contract violation rather
than a nav finding.

**Still open, and now measurable on a real site.** The centre statistic finally
separates inside from outside on the same run:

    overview     frame 73.1   centre 100.7
    spawn        frame 58.7   centre  93.4
    objective    frame 69.1   centre  44.9
    extraction   frame 85.2   centre  57.6

Objective and extraction read DARKER at the centre than in the frame; spawn and
overview read brighter. That is interiors against sky, and the interior figures
are the ones items 30-32 are about: no anchored lights exist, emissive cannot
light anything under `gl_compatibility`, and the geometry has no UV channel for
a lightmap. Nothing about the themed site changes that; it just gives the
question a level to be asked about.

*STATUS: CLOSED 2026-08-12 -- 116 OmniLight3D + 11 SpotLight3D under LuxFixtureLights in the shipped scene*

**30. Nothing instantiates the light loader, so shipping the anchors would not
have lit anything.** Corrects item 19, which is right about the packer and wrong
about the consequence.

Item 19 says the pack ships lamp housings without lights because
`lot/package.py` omits `<site>.site.lights.json`, and calls the fix "one line in
the packer". Measured on the themed-site probe, where that manifest IS present
and `tools/lux_inject.py` confirms it at inject time -- *"site.site.lights.json
is present, so lux_light_loader has anchors to spawn from"* -- the census reads:

    OmniLight3D  0 (0 visible)     SpotLight3D  0 (0 visible)
    LuxRoot 1
      Lux   sun_light=Sun
        children: LuxEnvironment, LuxLighting, LuxPostFX, @CanvasLayer@2

Seventy-two anchors on disk, zero lights in the tree, and no loader among
LuxRoot's children. `_build_modules` instantiates `LuxEnvironment`,
`LuxLighting` and `LuxPostFX` and never touches `LuxLightLoader` or
`LuxFixtureSpawner`. The manifest is read by nothing.

So the packer line is necessary and not sufficient, and doing it alone would
produce a package that carries a file no code opens -- which reads as fixed. The
visible consequence is measurable: on the single-building export, interiors sit
at mean luminance 20 against 72 outside, a 52-point gap that is entirely the
absence of fixture rigs at a 4 degree sun.

Whether the loader belongs in `_build_modules` or behind an explicit call is a
design decision this item does not make. What it establishes is that wiring it
is part of the same fix, and that item 19's estimate should not be quoted at one
line.

*Measured 2026-08-02, before any patch. The paragraph above is left as written;
this corrects it.* "Wire the loader into `_build_modules`" was not a fix that
could have worked, and there are four reasons the anchors light nothing rather
than one. Each is sufficient by itself.

**(i) Neither spawner is a module, so `_build_modules` could never have held
one.** `LuxLightLoader` and `LuxFixtureSpawner` are both `class_name ... extends
RefCounted` with only static methods. They are not Node3Ds and cannot be
children of LuxRoot. Their own headers name their callers: the loader says
"Editor-time tool -- driven by the Lux dock's 'Bake Lights' section"; the
spawner says "Editor: the Lux dock's 'Spawn From Fixtures' button. Runtime:
`LuxFixtureSpawner.spawn(level_root)` once after the level loads." The design
already names the runtime call. Nothing makes it. The pipeline runs headless and
there is no dock, so on the build path both entry points are unreachable.

**(ii) The fixture-marker path has no markers.** `LuxFixtureSpawner` finds lamps
by the `LuxEmit` name prefix and reads placement out of glTF extras. Read
straight from the glTF JSON of the shipped assets: `shell.glb` and `lot.glb`
carry **855 nodes each, zero beginning `LuxEmit`, and zero nodes with any
`extras` at all**; `cr_deli.glb` carries 913 nodes with the same zeroes. So
calling `spawn()` at runtime today returns count 0 and its own message -- "Import
a Zoo v0.30+ fixtures GLB first". `zoo_fixtures_build` is a job in the DAG; its
hardware is not reaching the composed assets. That is a separate gap from this
item and should not be folded into it.

**(iii) The rig classes are not in the package.** The current export's
`runtime/lux/runtime/` ships six files -- `lux_root`, `lux_environment`,
`lux_lighting`, `lux_post_fx`, `lux_emissive_binder`, `lux_runtime_api`.
`lux_light_loader.gd`, `lux_fixture_spawner.gd` and the whole `rigs/` directory
are absent, while `resources/lux_light_rig.gd` -- the resource the rigs consume
-- does ship. So even a correct call would fail to resolve `LuxFluorescentRig`.
The addon subset in `addon_sources` was chosen for a scene that had no lights in
it, and it is self-consistent with that scene.

**(iv) Item 19's packer line** -- `<site>.site.lights.json` missing from the pack
-- is real and is the least of the four.

Which fix, then. The manifest bake is the only live path: the anchors exist, the
markers do not. `LuxLightLoader.bake()` sets `owner` on the container, on each
rig and recursively on the rigs' children (`_reown`), which is exactly what
`PackedScene.pack()` needs -- so a bake run at BUILD time produces lights as
scene content, and the shipped level does not read the manifest at runtime at
all. `tools/godot_probe.py` already mirrors a project and drives Godot headless
against it, which is the same machinery a bake step needs. Note the rig NODES
pack alongside their built lights, so (iii) still has to be fixed either way:
ship the rig scripts, or flatten the bake to plain Light3Ds before saving. That
is a decision this item does not make, and it should be made by looking at what
the standalone contract costs in each case rather than by preference.

*STATUS: ANALYSIS -- engine constraints, not a defect. Note project.godot writes gl_compatibility*

**31. Lighting: what the engine requires of the geometry, and what Lux can
decide alone.** Sources brought on 2026-08-02, read and reduced to what bears
on this pipeline.

The finding that ranks the rest: **every global-illumination technique Godot 4
offers except ReflectionProbe is a contract between three parties, and Lux is
only one of them.** The Environment setting is Lux's. The `gi_mode` on each
`GeometryInstance3D` and the UV2 channel are Deli Counter's and Zoo's. The
renderer is the *consumer's* -- and under the standalone contract we do not
control it.

From the engine documentation (`godot-docs`, `tutorials/3d/global_illumination/`):

- **SDFGI** -- "Only supported when using the Forward+ renderer, not the Mobile
  or Compatibility renderers." Semi-real-time; supports dynamic lights but *not*
  dynamic occluders or dynamic emissive surfaces. Meshes need `gi_mode = Static`.
  Needs about 25 frames to converge. Explicitly called viable for procedurally
  generated levels.
- **VoxelGI** -- Forward+ only as well; mid cost, better reflections, and "light
  leaks if surfaces are too thin".
- **LightmapGI** -- runs on all renderers, is the *fastest* at runtime, and is
  the only one the docs call not viable for procedurally generated levels. It
  requires a UV2 channel per mesh, a bake step with RenderingDevice, and
  reserves the material's UV2 slot permanently. Default texel size `0.2`, max
  bounces `3`, at most 8 LightmapGI nodes rendered at once.
- **ReflectionProbe** -- all renderers, no geometry contract, poor indirect
  light. The only technique that asks nothing of the mesh.

Three things follow that this pipeline can act on, in the order they can be
measured.

*(a) The renderer question is already half-instrumented and wholly unanswered.*
`tools/look_shots.gd` reports `rendering_method` and `adapter_api` separately
and says why: the setting is what the project asks for, the API version is what
the process bound. Neither has been read against a GI expectation. Whether any
Lux preset sets `sdfgi_enabled` at all has not been checked -- `light_census`
counts light nodes and does not look at the Environment, so the census cannot
answer it today. Add the Environment's GI fields to the census; that is one
block in `light_census.gd` and it turns this paragraph into a reading. It
matters because a preset that assumes SDFGI produces flat lighting under
Compatibility with no error at all -- the same silent-drop shape as the Sun Link
bug, one layer up.

*Answered 2026-08-02.* `look_shots` on the portable export reports
`"rendering_method": "gl_compatibility"`, `"adapter_api": "3.3.0 NVIDIA 610.74"`,
`"adapter": "NVIDIA GeForce RTX 2060"`, engine `4.7-stable`. Both fields agree,
so this is not a driver falling back: the project asked for Compatibility and
got it, on a card that runs Forward+ without complaint.

And it is not the consumer's choice. `packages/exporting/export.py`,
`_write_project_godot`, writes `renderer/rendering_method="gl_compatibility"` as
a literal. Every portable-godot export carries it. The old export on disk and
the current one both read the same way.

So the ordering in (a) was right and the owner was wrong. The renderer *is* the
whole question for real-time GI, and Level Factory answers it, in one line, in a
file in this repo. Under `gl_compatibility`:

- SDFGI and VoxelGI are unavailable -- Forward+ only.
- Therefore emissive lights nothing (item 32).
- Therefore LightmapGI is the only GI that could run, and (b) shows the geometry
  carries no UV channel at all.

**Every form of global illumination is foreclosed by the export profile, before
any question about the geometry or about Lux.** That is a decision to make
deliberately, not a constraint to design around: it was presumably taken for
reach, and nothing in the repo records the trade. Whoever changes it should
change it knowing that Forward+ turns three of the four techniques back on and
costs whatever it costs on the target hardware -- which is measurable, by
re-running this same tool with `--rendering-driver` and diffing the histograms.

*(b) The UV2 question is a fact about files already on disk.* LightmapGI is the
one option that would survive a Compatibility consumer, and it is gated entirely
on whether the Deli Counter GLBs carry a second UV set. That is inspectable now,
without Godot: read the `TEXCOORD_1` accessors of a built `shell.glb`. If they
are absent, LightmapGI is not "a decision we have not made" -- it is unavailable
until DC's exporter emits them, and the import-side answer that the docs give
(**Meshes > Light Baking** set to Static Lightmaps) does not apply, because the
pipeline imports headlessly and the shipped package is not re-imported by us.
**This is the next lighting instrument to write, and it is cheaper than every
other item here.**

*Measured 2026-08-02, by `tools/glb_uv_census.py` -- written for this question
and run before it shipped.* Eight files: six Deli Counter shells out of
`deli_counter/build/`, and both assets of the portable export. 1157 primitives.
Every one of them carries `POSITION` and `NORMAL` and **nothing else** -- no
`TEXCOORD_0`, no `TEXCOORD_1`, no `COLOR_0`, zero materials, zero textures, zero
images, generator `Khronos glTF Blender I/O v5.1.19`. The paragraph above
predicted a missing UV2; the reading is stronger than that and changes the shape
of the answer rather than confirming it.

Run across the whole Deli Counter library the same day: **103 files, 12091
primitives, zero TEXCOORD_1 and zero TEXCOORD_0**, every file reading
`NORMAL,POSITION`. The eight-file figure above was a sample and is left in
place; this is the library.

Three consequences, and one of them is good news:

- **LightmapGI cannot bake this geometry as it stands**, and the gap is not one
  channel but both.
- **SDFGI and VoxelGI need nothing from these files.** Their requirement is
  `gi_mode = Static` on the instance, and the export's own `shell.glb.import` --
  written by Godot with its defaults, read here rather than assumed -- carries
  `meshes/light_baking=1`, which is that mode. So the real-time techniques are
  already satisfied on the geometry side and gated *only* on the consumer
  running Forward+. That inverts the ordering of (a) and (b): the renderer
  question is the whole question for real-time GI, and the UV question belongs
  to the baked path alone.
- **The baked path has a cheaper lever than "Deli Counter must export UV2".**
  The same `.import` file shows `meshes/light_baking=1` beside
  `meshes/lightmap_texel_size=0.2`, and the importer only reads the texel size
  when light baking is `2` -- the value its own option-visibility check names as
  Static Lightmaps. At `2`, Godot generates the second UV set itself, on import,
  from geometry that has none. No Blender change and no Deli Counter change: a
  value in a file. **What is not established** is whether the packer can ship
  that `.import` and have a consumer's Godot honour it instead of regenerating
  it with defaults, and whether the unwrapper succeeds across 183 separate mesh
  resources per shell. Both are readings, not arguments -- set the value, open
  the project, see whether a UV2 appears. Do not quote the one-line fix until
  that run has happened.

One thing the same census settles in passing: zero materials and zero textures
in every file means all colour is assigned downstream, in Godot, and none of it
rides in the glb. `meshes/ensure_tangents=true` is therefore generating tangents
for meshes with no UVs to derive them from -- inert today, and worth a look the
first time anything normal-maps.

*(c) "Not viable for procedurally generated levels" is about runtime, and LF's
levels are frozen at build.* The doc's objection is that you cannot bake what
does not exist yet. LF generates, then freezes, then ships -- so the objection
lands on the *pipeline shape*, not on the levels: baking would need a new job
driving Godot with a RenderingDevice, after `presentation_compose` and before
`dispatch_handoff`. `tools/godot_probe.py` already mirrors a project and runs
Godot headless against it, which is most of that job's body. Cost, not
impossibility. Do not quote LightmapGI as ruled out.

Two couplings to items already open:

- **To item 26 (Pixelcoat VRAM).** Lightmaps are additional textures per level,
  on top of whatever atlas Pixelcoat shares -- the docs warn that baking "may
  require significant VRAM" and that oversized textures risk crashes, with a
  16384 ceiling. If the VRAM answer for Pixelcoat is "one texture in memory",
  lightmaps are a second budget, not a line in the first.
- **To the site geometry.** "Light leaks if surfaces are too thin" is a claim
  about wall thickness against cell size, and the perimeter added to
  `_write_site_spec` this session states a height (3 m) and no thickness. If
  VoxelGI or SDFGI is ever chosen, that thickness stops being cosmetic. The
  docs' own mitigation is `Y Scale` at 75% or 50%, "without impacting
  performance" -- a number to test, not to adopt.

And the part that is craft rather than engine, from the three artist-facing
sources. Two claims are worth carrying because they are checkable against what
Lux already does, and one is worth leaving out:

- *Establish global and key lights first*, and *push a small number of lights as
  far as you can* (80.lv). A Lux preset is already a small named set rather than
  a pile, so this is a rule the design happens to satisfy; it is worth writing
  down so that the fixture loader from item 30 does not quietly turn a preset
  into an accumulation.
- *"Gameplay always comes first"* -- high-contrast lighting must not create
  unreadable shadow areas (80.lv). This is the one that names a gap in our own
  instruments. `look_shots.gd` reports a whole-frame Rec.709 histogram and states
  outright that it cannot tell "washed out" from "correctly bright for noon". A
  whole-frame mean also cannot tell a readable level from one where the objective
  sits in a hole: item 30 measured interiors at mean 20 against 72 outside, and
  that 52-point gap is invisible in a site average. **The derived statistic is
  local contrast at the mission spine**, which the tool can already compute
  because it already stands the camera at `spawn_pos` / `objective_pos` /
  `extraction_pos`. Take the histogram of the centre region as well as the frame,
  and report both. An extension of an existing instrument, not a new one.
- The colour-mood guidance -- cool for loneliness, warm for safety, red for
  danger (300mind) -- is a claim about audiences, not about this renderer, and
  nothing here can measure it. It stays out of the tools and belongs to whoever
  authors a preset.

Finally, an A/B this pipeline can run and has not. `look_shots.py` mirrors the
project before it injects, so it can render the same derived cameras twice with
`Environment.sdfgi_enabled` flipped between runs and diff the histograms. That
is the only way any claim in this item becomes a number rather than a citation --
and it is the honest test, because a GI difference that does not move the
histogram at the spine is a GI difference the player does not get.

Sources read for this item: the Godot GI tutorials (`introduction_to_global_illumination`,
`using_sdfgi`, `using_lightmap_gi`); 80.lv, "Working on Lighting for Video Games";
300mind, "Lighting in Game Design"; Godot forum thread 99831, "Realistic lighting
in interior" -- which adds that VoxelGI wants "closed and somewhat small levels"
at 200-400 m and that reflection probes combined with VoxelGI are redundant and
conflicting.

*STATUS: ANALYSIS -- a working model plus an engine fact; the interior lights do now spawn (item 30)*

**32. Two lighting systems, and none of the interior one is switched on.**
The working model, as stated on 2026-08-02: there is the global illumination of
the sun above, and there is the interior light inside the buildings Deli Counter
makes -- Zoo supplies the fixture assets and their anchors, Lux spawns the
lights out of them, Pixelcoat supplies the emissive layer, and the result should
read as intimate and muted: enough to see by, not enough to blind.

The split is right, and the engine splits the same way. The step that needs
correcting is the emissive one.

**Emissive is not a light source.** Godot's own words for StandardMaterial3D:
emission "is added to the resulting final image and is not affected by other
lighting in the scene", and it "does not include light surrounding geometry
unless VoxelGI or SDFGI are used". A Pixelcoat emissive layer therefore glows
and lights nothing -- on every renderer -- unless one of the two Forward+-only
real-time techniques is running, or a lightmap baked it, which item 31 shows
this geometry cannot do today. Under Compatibility the emissive layer is
decoration. That is the same failure class as the Sun Link bug and as item 30's
loader: something present, apparently configured, doing nothing, with no error.

Which puts the load back on the fixtures, and item 30 measured those: 72 anchors
on disk, zero OmniLight3D, zero SpotLight3D, no loader among LuxRoot's children,
interiors at mean luminance 20 against 72 outside. **So of the three interior
mechanisms in the model -- anchored lights, emissive, and GI -- exactly none is
currently delivering any light.** The 52-point gap is not a tuning problem.
Nothing is switched on.

A hard limit to design against before the loader lands. On the Compatibility
renderer "up to 8 OmniLights + 8 SpotLights can be rendered per mesh resource";
Mobile carries the same per-mesh cap plus 256 of each per camera view. Seventy-two
anchors in one building is well past that in aggregate but not necessarily per
mesh -- the shells measure 183 mesh resources apiece, so the fixtures may
distribute under the cap. That is something the census can measure once lights
exist: count the lights whose range overlaps each mesh resource's AABB. Until
then the figure is a ceiling to know about, not a violation to claim.

The tuning target is already a statistic. "Not blinded" is `clipped_pct` and
`near_clipped_pct`; "can still see" is `p05` and `crushed_pct`; `look_shots.gd`
reports all four. What is missing is that they are whole-frame figures, and an
interior is a small part of an exterior-dominated frame -- which is the same
defect item 31 names, and the same fix. One extension serves both, which is a
reason to do it once and early.

The order this implies is not the order the model reads in:

1. Wire the loader (item 30). Nothing downstream in the interior chain can be
   evaluated while the count of interior lights is zero.
2. Extend `look_shots` to report a centre region alongside the frame, so "muted
   but readable" becomes a number instead of a look.
3. Only then decide GI -- because GI is what would make the emissive layer mean
   anything, and that decision is a bet on the consumer's renderer (item 31).

*STATUS: CLOSED 2026-08-12 -- 21 unresolved -> 0, 132 misrooted -> 0, engine parser_error_count 0*

**33. The export does not contain the level, and the closure judge said so on
its first run.** Measured 2026-08-02 by looking at the pictures.

`look_shots` reads the spine out of `gameplay_anchors.json` and stands the
camera at spawn, objective and extraction. The exposure figures came back
healthy -- mean 77.9 / 80.8 / 87.2, p95 96-98, no clipping, centre tracking
frame -- and every one of them is a well-exposed photograph of an empty site.

    overview     a ground plate with a light kerb, floating in sky. No buildings.
    spawn        standing on a pale ground plane; a low perimeter wall band with
                 gaps runs across the horizon. No buildings.
    objective     fragments: a few wall segments, one ladder, and a slab floating
                 in mid-air over a washed-out ground. No enclosure, no interior.

So the whole lighting investigation in items 30-32 was carried out against a
package with no buildings in it. Nothing measured there is wrong, and none of it
is about a level.

**RETRACTED, kept above the thing that replaced it.** Earlier the same day, this
file was going to record that `export_closure_scan.json`'s ten entries --
`lux.applied.tscn: unresolved res://site_base.glb` and nine
`res://art/zoo/*.glb` -- were false positives, on the grounds that every one of
those files is present in the export directory with an `.import` sidecar beside
it. That inference is wrong. Presence on disk is not resolvability, and the
render is the arbiter: the scene references those meshes, the scan says the
references do not resolve, and the picture shows the meshes are not there. The
judge was right on its first outing and was overruled from a directory listing
by someone who had not looked at the frame.

Two things follow, and the ordering matters more than either.

**The priority inverts.** An export that does not carry the level outranks every
question about how the level is lit. Items 31 and 32 stay open and stay true --
`gl_compatibility` still forecloses GI, emissive still lights nothing without
it, the meshes still carry no UV channel -- but none of them is the reason the
package looks like this, and none of them should be worked before this is.

**`CLOSURE_ENFORCED` should flip once this is fixed.** The flag was set to False
because the existing library had never been read against the judge and a gate
that fails on its first run teaches people to bypass it. Its first run found a
real defect that four instruments and a directory listing missed. That is the
argument for enforcing it, and the argument should be made after the ten
references resolve, not instead of fixing them.

And a note on method, because it is the whole lesson of the day. Four
instruments agreed the package was fine: pytest at 496 passed, the exposure
histogram, the light census, the UV census. All four were measuring true things
about an empty plate. The first look at a rendered frame settled it in one
glance. `look_shots` exists because "nothing in the pipeline had ever looked at
a picture" -- and for most of this session its numbers were read while its PNGs
went unopened.

*The mechanism, measured the same day.* Counted rather than argued, and it
refutes the guess in the paragraph above that the missing geometry was a
packaging problem.

    presentation_compose/out/presentation/site.tscn   353 nodes, 25 ext_resource
    lux_apply/out/lux.applied.tscn                    243 nodes, 12 ext_resource

`lux_apply` loses 110 nodes and 13 module references. `lux.applied.tscn` does
NOT instance `site.tscn` -- it is a flattened scene naming `res://site_base.glb`
and the `art/zoo` modules directly -- so the `site.tscn` skip added to
`export.py` this session is NOT the cause, and that hypothesis is dead.

Building index is the second token of every module node name. In `site.tscn`:

    building 1    113 nodes
    building 0    112 nodes
    building -1    93 nodes
    building 14     1 node

And every one of the 110 nodes `lux_apply` drops belongs to building 0 or 1:

    int_0_0_seg  23    ext_0_S_seg  20    ext_0_S_open  3    Dressing  1
    int_1_2_seg  23    ext_1_S_seg  20    ext_1_S_open  2    Fixtures  1
    int_1_3_seg   8    int_0_1_seg   4    int_0_0_open  2
    int_1_2_open  2    int_0_1_open  1    int_1_3_open  1

**The two real buildings are dropped in their entirety and the 93 nodes filed
under the -1 sentinel all survive.** What ships is the sentinel geometry and the
greybox base, which is exactly what the frames show: a ground plate, one wall
run, one roof slab in mid-air.

The shape of the loss names its own mechanism. `PackedScene.pack()` keeps only
nodes with an `owner`, and Lux sets `owner` under `Engine.is_editor_hint()` --
`lux_apply` runs headless. Whatever built the -1 nodes owned them; whatever built
buildings 0 and 1 did not. This is the third appearance of the same failure
family in one file: the Sun Link NodePath dropped for want of `node_paths`, the
light loader never called because it is not a module, and now the level itself
dropped for want of `owner`. Each is silent, each leaves a file that looks
correct, and none of them errors.

Two consequences beyond the obvious one.

**Item 30 gets a measured cause.** `Dressing` and `Fixtures` are among the
dropped containers. That is why nothing downstream of `lux_apply` carries
fixture hardware, and it is a better answer than item 30's guess that
`zoo_fixtures_build` was not reaching the composer. The fixtures reach the
composer; Lux drops them.

**`ext_-1_*` is a separate defect and should not be folded in.** 93 nodes under a
sentinel building index means the composer failed to resolve which building
those modules belong to, and it is worth knowing whether their transforms are
also sentinel -- the floating roof suggests so. Fixing the `owner` drop would
ship the two real buildings AND this junk. Both need doing; only one of them is
why the site is empty.

*Unresolved, and named so it is not quietly dropped.* `export_closure_scan.json`
reports 10 unresolved references to files that are demonstrably present in the
export directory, and `scan_closure` runs at step 3.6, AFTER the art copy at
step 2.5, building its `present` set by `rglob` at scan time. Those two facts
cannot both be right. Re-running `scan_closure` against the export as it stands
settles it in one command, and until that is done neither "the judge is buggy"
nor "the judge is correct" should be quoted -- including the retraction above,
which was written from the render and not from the scanner.

*Settled.* `scan_closure` re-run against the export exactly as it stands:
`missing 0 ok True`. The judge is correct and the package's references resolve.

So the `export_closure_scan.json` sitting in the export directory, with its ten
issues and `"ok": false`, is a STALE ARTIFACT from an earlier run -- not a false
positive and not a live failure. Three readings of the same file in one day,
and the third is the only one that checked which run wrote it.

That is the method error this file already documents at the top: comparing
artifacts that are only ever "the ones currently on disk" says nothing when they
came from different runs. The export directory demonstrably holds mixed vintages
-- `project.godot` there now carries Godot's editor header and a `main_scene`
that disagrees with `export_profile.json`, so the editor has rewritten it in
place since the export ran. **Treat the export directory as evidence only for
the run that just produced it, and re-run the producer rather than reading its
leftovers.** The three retractions above cost more time than the re-run would
have.

None of this touches the finding: `lux_apply` still drops 110 nodes and both
real buildings, and that happens upstream of the export.

*The mechanism, corrected again, and this time with an exact count match.* The
`owner`/`PackedScene.pack()` reading above is REFUTED. Every node in `site.tscn`
is `parent="."` -- 324 of them -- and the survivors and the casualties sit side
by side at the same depth, so no subtree was orphaned and no ownership rule
separates them. What separates them is the module they instance:

    kept       0_greybox_base   1_roof_rockay_01_w4400   2_wall_rockay_01_w200
    dropped    7_wall_rockay_02_w200   8_wallEnd_rockay_02   L_Dressing  L_Fixtures

Survivors are `_01_` variants. Casualties are `_02_`, `_03_`, `_04_`. Tested
against the compose output directly: all 24 `.glb` files are present, every
`_01_` has a `.glb.import` sidecar, and not one `_02_`/`_03_`/`_04_` does. **13
modules without a sidecar; 13 `ext_resource` entries lost between the two
scenes** (25 -> 12). A `.glb` with no `.import` cannot load as a PackedScene, so
`ExtResource` resolves to null, the node cannot be built, and `pack()` writes a
scene without it. Silently. The floating roof is an `_01_` whose walls were all
`_02_` and up.

The sidecars are not authored -- they are generated by an import pass, and
`packages/staging/godot_project.py` runs one:

    if godot_executable:
        try:
            subprocess.run([godot, "--headless", "--path", dest, "--import"],
                           capture_output=True, timeout=300)
        except (OSError, subprocess.SubprocessError):
            pass

Output captured and thrown away, return code never read, exceptions swallowed.
When that pass fails the staged project retains only the sidecars that were
copied in from source, and the job reports success. **This is the same defect
the walktest carried -- "a stage that could not run kept saying succeeded" -- in
the file that stages every Godot job in the pipeline.** Whatever the underlying
import failure turns out to be, the swallow is the reason nobody found it, and
it should be fixed whether or not the import failure is easy.

So the causal chain, end to end, and every link measured:

    --import fails, silently
      -> 13 of 24 zoo modules have no .import in the staged project
      -> their ExtResource references resolve to null
      -> pack() writes lux.applied.tscn without those 110 nodes
      -> the export ships a ground plate, one _01_ wall run and a floating roof
      -> look_shots photographs it and reports a healthy exposure
      -> four instruments and 496 tests agree the package is fine

**Four hypotheses were refuted along the way** -- the `site.tscn` skip, the
closure judge, a dropped container subtree, and node ownership -- each of which
looked correct until it was counted. They are left above this paragraph on
purpose. The reason the fifth is different is not that it sounds better: it is
that 13 and 13 are the same number.

*Half of the paragraph above does not survive its own timestamps.* Read them
before quoting any of it.

    presentation_compose/out/presentation/site.tscn   mtime 1785009219827
    lux_apply/out/lux.applied.tscn                    mtime 1785009233382

Thirteen and a half seconds apart, so **the 353 -> 243 drop is one run's work and
the attribution to `lux_apply` holds.** Both are from 2026-07-25. The export that
started this whole investigation, dated 2026-08-02, copied week-old artifacts.

What does NOT hold is the causal step. The claim was that the staged project
lacked `.import` sidecars because the swallowed `--import` call failed. Measured
on the staging directory as it stands: **27 glb, 27 import, before and after a
hand-run import pass, exit code 0.** The pass works. And the directory's own
timestamps say why that proves nothing either way -- `art/` is 07-25, while
`project.godot`, `.godot/` and `staging.notes.json` are 07-27, so the project
was re-staged and re-imported TWO DAYS AFTER `lux_apply` produced its output.
The 27/27 is post-hoc. Whether the sidecars existed at the moment that mattered
is not readable from anything on disk.

So the standing position, stated exactly:

    ESTABLISHED   lux_apply loses 110 nodes and 13 module references, in one
                  run, 13.5 s apart. Both real buildings go; the -1 sentinel
                  geometry stays.
    ESTABLISHED   the 13 lost references correspond one-for-one with the 13
                  modules that have no .import sidecar in the COMPOSE OUTPUT.
    NOT ESTABLISHED  that a failed import pass caused it. The correlation is
                  exact and the mechanism is unproven.
    ESTABLISHED   `stage_godot_project` discards the import pass's return code,
                  output and exceptions. That is a defect on its own terms --
                  the same "a stage that could not run kept saying succeeded"
                  the walktest carried -- and worth fixing whether or not it is
                  this bug.

**And the rule this session earned the hard way: stop reading leftovers.** Five
hypotheses were refuted here, and at least three of them survived as long as
they did because a file on disk was treated as evidence about a run that did not
write it -- a stale `export_closure_scan.json`, a `project.godot` the editor had
rewritten, a staging directory re-imported two days after the job it belongs to.
The roadmap already carried this rule at the top, about seed 5320, and it was
quoted twice today before being broken again.

Nothing further should be concluded from these directories. Re-run compose and
lux_apply as one pass, and take the counts from that.

*RETRACTED IN FULL, on a clean run. `lux_apply` loses nothing.*

    presentation_compose   353 nodes  25 refs   2026-08-02 09:33:03
    lux_apply              354 nodes  27 refs   2026-08-02 09:49:41
    presentation_compose -> lux_apply: +1 nodes, 0 reference(s) lost, 2 gained

The +1 node is the LuxRoot the driver adds; the +2 references are the preset
and `lux_root.gd`. Nothing is dropped. Every paragraph above that attributes
missing geometry to `lux_apply` -- the 110 nodes, the 13 references, "both real
buildings are dropped in their entirety", the `owner` mechanism, and the
`.import` sidecar mechanism that replaced it -- describes a comparison between a
2026-08-02 compose output and a 2026-07-25 lux output. Two runs, eight days
apart. There was no drop.

What is still true is smaller and duller: **the export photographed at the top of
this item was built from stale job outputs.** The empty frames are real; they are
a picture of a package assembled from a lux scene produced eight days before the
compose scene it was supposed to follow. The site is not empty because a stage
eats it. It is empty because the exporter shipped last week's.

The sidecar observation survives as an observation and dies as a cause:
`presentation_compose` really does write 15 of its 25 references without an
`.import`, on a fresh run -- and `lux_apply` resolved all 27 anyway. The staging
import pass evidently generates what it needs. So "modules without sidecars get
dropped" was a correlation across two runs, and it is not a mechanism.

**This is the sixth refutation in one item, and the only one that matters,
because it was self-inflicted by the exact failure the guard in
`tools/stage_census.py` exists to prevent.** The tool printed REFUSED. The
refusal was overridden with `--allow-mixed`, the marked lines were read anyway,
and the result was committed as ESTABLISHED -- by the same hand that had written
the refusal into the tool an hour earlier, in a file that already carried the
rule twice. A guard nobody obeys is a comment.

Two things worth keeping from the wreckage, both real:

- `--force` does not re-run the whole graph. `zoo_kit_build` and
  `dispatch_handoff` stayed at 2026-07-24 through a `run ... --art --gameplay
  --force`. That is what let an eight-day-old `lux.applied.tscn` reach an
  export made today, and it is the actual defect behind the empty site.
- `stage_census`'s 600 s default span is too tight for a real run: compose and
  lux_apply sat 998 s apart in one honest pass, with the nav walk between them.
  The guard should compare per-PAIR rather than across the whole set, so a
  fresh pair reads as fresh even when a cached stage upstream is a week old.

*Confirmed, from one run, end to end.* Re-exported from the 2026-08-02 outputs
and photographed through the tool's own derived cameras:

    lux_apply         354 nodes  27 refs   09:49:41
    dispatch_handoff  179 nodes   2 refs   09:49:42   (bakes to lot.glb/shell.glb)
    export            354 nodes  27 refs   09:57:20   +0s

The export carries the full lux scene -- 354 and 27, against the 243 and 12 the
stale package shipped. **The empty site was staleness and nothing else.** The
frames now show textured walls, doorways, a corridor and an interior. There is a
level in the package.

`dispatch_handoff` reducing 354 nodes to 179 with 2 references is it baking the
assembled site down to `lot.glb` and `shell.glb`; the export follows the lux
path, not the dispatch path, so that reduction is a parallel branch and not a
loss. Named here only so the next reader does not re-chase it.

And the interior statistic earned its place on its first honest run:

    name         eye_y   mean   centre   p95   centre p95
    overview     21.97   76.0     77.0   187          195
    spawn         1.60   76.2     71.3    94           96
    objective     2.50   54.3     30.9    87           87
    extraction    1.60   86.0     86.3    97           98

Three shots have the centre within a few points of the frame. The objective has
**centre 30.9 against a frame mean of 54.3** -- the camera is looking into an
interior, and the frame mean alone reads as unremarkable. That is exactly the
gap item 32 predicted from item 30's 72-against-20, measured this time at a
place a player stands, in a package built from one run.

So the standing state, with the day's five dead hypotheses behind it:

    REAL     job invalidation. `--force` left zoo_kit_build and
             dispatch_handoff at 2026-07-24 through a full run, which is how an
             eight-day-old lux.applied.tscn reached an export made today. This
             is the defect that produced every empty frame.
    REAL     interiors are unlit, now with a number from a real interior:
             30.9 centre against 54.3 frame at the objective.
    REAL     gl_compatibility forecloses SDFGI and VoxelGI (item 31), so
             Pixelcoat's emissive layer cannot light those interiors, and the
             library carries no UV channel for LightmapGI either.
    OPEN     the site reads sparse -- a large plate, a perimeter, and thin
             pieces scattered across it. Whether that is the ext_-1 sentinel
             index placing modules badly, or simply what a two-building site
             looks like, is not established and should not be guessed at.
    NOT A    lux_apply, presentation_compose, the closure judge, node
    DEFECT   ownership, and import sidecars. All five were refuted.

*STATUS: CLOSED 2026-08-12 -- themed_site_assemble; the export is the whole site, five buildings*

**34. The greybox is a site; the themed export is a fragment of one.** Measured
2026-08-02, one run, one tool, the same three places in both scenes.

`look_shots` against Lot's `site_walk.tscn` from seed 5320, and against the
portable export built from the same run:

    scene         overview eye_y   implied extent   spawn   objective   extraction
    Lot greybox           122.39          ~150 m   105.8       126.9        107.4
    themed export          21.97           ~27 m    76.2        54.3         86.0

The extent falls out of the tool's own framing -- `dist = (extent/2) /
tan(37.5 deg) * 1.25` -- so the two overview heights are a measurement of site
size, not a camera preference. The walk test's own proxies span x from -118 to
+92, about 210 m, which agrees with the greybox and not with the export.

The frames say it plainly. **Lot's greybox is four buildings in a row on a long
ground plate**, distinct in size, legible as a block. The themed export is a
short run of walls and one corridor, on a plate with thin pieces scattered over
it. `site.tscn` carries building indices 0 and 1 and a `-1` sentinel; the
greybox carries four. Something between Lot and the export is delivering part of
the site, and this item does not say what -- it says the two ends disagree and
by how much.

What theming DOES preserve is the room. Both objective shots stand in an
enclosed space with doorways and a ceiling; the greybox reads at mean 126.9 with
the centre at 128.2, the themed at 54.3 with the centre at **30.9**. The shape
survives the art pass and the light does not: the themed interior is the one
place in either scene where the centre and the frame disagree, and it disagrees
by 23 points. That is items 30 and 32 confirmed at a place a player stands, and
it is the first interior measurement all day taken from a real interior.

Exposure across the two is NOT comparable and should not be quoted as a
regression: the greybox runs the stock WorldEnvironment and the export runs
Lux's grade. `look_shots.gd` says so in its own header -- two framings of one
scene are two instruments. The comparison that holds is structural: extent,
building count, and whether the centre of a frame disagrees with the frame.

And the walk test, same run, seed 5320, which is the other half of "is this
playable":

    player_0..3   16/16 targets reached, 816-821 m travelled, 4 vertical legs by ladder
    path proofs   27 ok, 4 fail        stranded 4, behind a barrier 3, no standing room 0

All four walkers reach everything. The four failures share one signature to two
decimals: the path stops **7.79 m short**, ends at **y = 4.3**, and the target
stands at **y = 0.2**. The isolated endpoints are proxies 1, 5, 9 and 13 of 16
-- **the same slot in each of four buildings**. One defect replicated four
times, on an upper floor with no route down at that slot, in a site whose
walkers use ladders successfully elsewhere. Worth naming as its own item when
someone picks it up; it is not a placement accident.

**35. The graybox/art relationship: it is a SWAP, and most of the recommended
shape is already the contract. What is missing is the library.** Guidance
brought 2026-08-02, reconciled against what this pipeline measurably does
rather than filed as received advice.

**The verb first, because it changes the reading.** Nothing replaces a greybox
mesh. `deli_counter/docs/ASSET_SWAP_CONTRACT.md` names five things a slot and a
zoo entry must agree on -- identity, dimensions, pivot, openings, collision --
and states the consequence: *"If all five hold, swap is a name lookup + a
transform copy. If any fails, the piece stretches, floats, clips, or ghosts."*
The greybox keeps collision; Zoo substitutes the visual at the same transform.
"Replace" implies the greybox stops existing, and it does not: that is the
whole reason a themed building can still be walked.

**What the guidance recommends and this pipeline already does.** Read from the
artifacts, not from intent:

- *Three layers with separate authority.* DC's themed scene carries
  `Functional/GameplayAnchors/...`, `Ladders`, `Dressing` and `Fixtures` as
  distinct subtrees. The split exists in the node names.
- *Semantic slots, not geometry analysis.* DC writes `<name>.slots.json`
  directly and compose consumes it with `--slots`. Measured on
  `gas_station_a03`: 68 slots, roles `wall 54, doorway 7, breach 3, window 3,
  roof 1`, `size_mod` `full 50 / end 18`, facing `N/S/E/W/X/Y/up`, `module_size
  2.0`, `module_library "art/zoo"`. Nothing reverse-engineers intent from
  triangles.
- *A fixed pivot convention.* All 68 slots declare `pivot: "center"`. One
  convention, stated per slot.
- *Openings declared, not inferred.* 13 of 68 carry an `openings` list.
- *Collision ownership per slot.* `fit.collision` reads `convex` on 67 and
  `trimesh` on the roof.
- *Non-destructive, with a manifest.* `portable_resource_manifest.json` plus a
  compose summary recording `placement_check`, `closure`, `zfight_check` and
  `circulation_check`. The placement gate's own line -- "N/M modules sit on the
  greybox collision" -- is the acceptance check the guidance asks for.
- *The pipeline order.* The recommended flow (DC -> traversal validation ->
  human lock -> Zoo -> materials/wear -> lighting -> regression -> package) is
  the planner's DAG, near enough edge for edge.

So the guidance's central rule -- the graybox says where the game is, the art
says what it looks like -- is not a change of direction. It is a restatement of
the contract this repo already wrote down.

**The one place the guidance and the pipeline genuinely part company, and it
explains a lot.** The slot manifest's `coverage` field reads
`wall/generated`, `doorway/generated`, `window/generated`, `breach/generated`.
Every module is GENERATED. The guidance is about a *controlled library of
handcrafted, beveled modules*; this pipeline procedurally makes its swap pieces
instead. That single fact accounts for findings recorded elsewhere in this file:

- Item 31 measured 103 GLBs and 12091 primitives carrying **POSITION and NORMAL
  only** -- no UV channel, no materials, no textures. Generated geometry with no
  authoring pass has nothing to carry them.
- So the guidance's material sections -- trim sheets, texel density targets,
  shared material families, decals, vertex-colour wear -- are not "not done
  yet". They are **inapplicable to geometry with no texture coordinates**, and
  every one of them is blocked behind the same UV question LightmapGI is.
- The bevel guidance likewise. World-space bevel widths, silhouette versus
  lighting versus surface-detail bevels, hardened normals: all of it presumes an
  authored mesh. Nothing in the current chain has a place to put it.

**What the library is missing, measured against the guidance's own list.** The
`art/zoo` directory holds `wall_rockay_01..04`, `wallEnd_rockay_01..04`,
`doorway_rockay_01..04` at several widths, `window_rockay_01/02`,
`breach_rockay_01` and `roof_rockay_01`. Against the recommended wall family
that is: straight walls yes, endcaps yes, opening frames yes, damaged/breach
variants yes. **Absent entirely: interior corners, exterior corners, columns,
beams, stair flights, stair landings, parapets, thickness transitions, and
every seam-management piece** -- baseboards, crown trim, pilasters, fascias.
The guidance's observation that modular environments fail at their boundaries
rather than in the middle of a module is the relevant one: this library is all
middles.

That is consistent with the frames in item 34. The themed export photographed
as a plate with thin pieces scattered on it and one corridor -- walls without
corners do not close a room.

**Fields the guidance would add to the slot record, and whether they are worth
adding.** The slot already carries identity, role, size variant, style,
transform, pivot, openings and a collision mode. It does NOT carry:

- `allowed_outward_overhang_m` / `allowed_inward_intrusion_m`. Worth adding,
  and the more valuable of the two is the intrusion limit -- it is the number
  the placement gate would need to enforce "art may wrap the shell but must not
  eat playable space". Today the gate checks that modules SIT ON the greybox
  collision; whether it checks intrusion is not established and should be read
  before anyone claims it does.
- `connection_edges`. Only meaningful once corner and transition pieces exist.
- `material_family`. Blocked behind the UV finding; premature.
- `variant_seed` per slot. The pipeline seeds per candidate, not per slot, so
  this would buy per-piece variation the library cannot yet supply.

**Two implementable gates the guidance names that this pipeline does not have:**

- *An import-time rejection of unauthorised collision.* Godot can build
  collision from imported meshes by name suffix, and a post-import script can
  refuse any the manifest did not grant. Today nothing checks; the contract is
  honoured because the exporter happens not to emit collision, which is a
  property of the current exporter rather than a guarantee.
- *A composed-section tier.* The guidance separates authoring module / composed
  section / runtime chunk. This pipeline has the first and the last and nothing
  between: `site.tscn` measured 353 nodes with ~20 module instances per
  building run, all individual. Occlusion is a related gap -- large simple
  walls make good occluders and nothing in the chain emits any.

**A documentation finding, recorded because it will mislead the next reader.**
`ASSET_SWAP_CONTRACT.md` opens with *"Status (as of 0.35.0): design spec -- NOT
yet implemented."* That is stale. DC emits the slot manifest, compose consumes
it, and modules are demonstrably instanced at slot transforms -- measured today.
The doc describes an editor-driven swap ("in the Godot editor you compose the
building scene"); what shipped is headless and driven by
`run_presentation_compose.py`. Someone should reconcile the status line and the
workflow section with what runs, or the next person will build the thing twice.

**The order this implies**, given everything else in this file: the library gap
(corners, transitions, seam pieces) is the one that would visibly improve levels
and needs no upstream change. The material and bevel work is downstream of the
UV question in item 31. The intrusion limit is a small, checkable addition to a
gate that already exists. And none of it moves before item 29 ships a themed
SITE rather than a themed building, because a kit with no corners is easier to
judge on four buildings than on one.

*STATUS: NARROWED 2026-08-12 -- walk plumbing superseded by cmd_walk wrapping the export; the nine findings stand*

**36. Walking it. Zoo's inserts are exact; the layer with no slot is the one
breaking the level.** 2026-08-02, a human walked the themed site and found nine
things in twenty minutes that four instruments had not.

The walk needed a project that did not exist. Lot writes the themed site with
the composed building referenced by an ABSOLUTE path -- `res://C:/Projects/...`
-- which Godot cannot load, and the portable export strips the walk scene by
contract, so it ships no player. `tools/walk_themed.py` assembles a throwaway
project from the pieces: the composed building as `building.tscn` with its
`art/` and `site_base.glb`, the themed site with that reference made local,
Lot's walk scene as the entry, and `addons/lot` for the player. It is scratch
and rebuilds from one command, which after item 33 is the only kind of copy
worth making.

**What the art pass gets RIGHT, measured two independent ways.** Deli Counter's
own placement gate reads `checked 318, matched 318, mismatched 0, ok true`. And
`tools/insert_overhang.py`, written for this and comparing every instanced
module's glTF AABB against its slot's declared `fit.dims`, finds **no module off
its slot in any axis** -- not oversize, not tipped. The suspicion that inserts
were dodging the shape contract is refuted. Zoo's structural modules honour
their slots exactly, and nothing in the composed building reaches above the roof
at y = 8.00.

**What breaks the level is `Dressing`, and it is unpoliced by construction.**
Identified by the one test no instrument here replaces: hiding the `Dressing`
node in the editor made the offending geometry disappear.

    Dressing   y -6.84 .. 6.84      declared envelope floor  y -4.00
    Fixtures   y -0.30 .. 0.30
    -- both ANSWER NO DECLARED SLOT

Three faults, one cause:

* **Rods standing floor-to-ceiling in open interior space**, with no collision.
  The no-collision part is CORRECT -- the art pass never creates collision --
  and it is what makes them worse: they read as obstacles, and a player walks
  through them.
* **Props below the floor**, tops emerging through it. `Dressing` reaches 2.85 m
  under the basement floor.
* Neither is checked by anything. The placement gate scores the 318 modules that
  answer slots; `Dressing` answers none, so it is not among them. The
  circulation gate checks props against ladder volumes, doorway apertures and
  stair footprints -- not open floor, and not the floor plane itself.

This is item 35's prediction arriving with numbers: the layers with no slot to
answer to are the ones that go wrong, and `allowed_inward_intrusion_m` is the
field that would have caught the rods. `insert_overhang.py` explicitly refuses
to guess at inward intrusion because a bounding box cannot answer it -- and a
person walking the level answered it in thirty seconds.

**Two faults with other causes, both already measured elsewhere.**

* **Windows shade as moiré.** The window modules ship `glass_wavy_normal.png`
  and `glass_wavy_roughness.png`; item 31 measured zero TEXCOORD channels across
  103 files and 12091 primitives. A normal map on geometry with no UVs samples
  garbage. Same root as the LightmapGI blocker -- one cause, not two. Note that
  flat albedo surfaces (the wood wall) shade fine, which is the same finding
  seen from the other side.
* **Doorways stacked in one column, and a wall crossing a window.**
  `compose.summary.json` from this build reads `zfight_check: ok false`, 8
  buried pairs, each 0.061 m2, at planes 3.696 and 7.696 -- the two storey
  ceilings, exterior segment against interior. `run_presentation_compose.py`
  returns 3 when that gate fails, and the compose job reported `cache` on this
  run. **A red gate is being served from cache as a green one**, which is the
  staleness class of item 33 in a new place and should be treated as the more
  serious of the two findings.

**RETRACTED: the `-1` group is the BASEMENT, not a sentinel.** Items 33 and 34
record "93 nodes under a `-1` sentinel building index" as evidence that the
composer failed to resolve which building modules belong to, and item 34 calls
it a separate defect worth its own item. It is not a defect at all. Grouped by
index and measured:

    -1    93 nodes   y -4.00 .. -0.30
     0   112 nodes   y  0.00 ..  3.70
     1   113 nodes   y  4.00 ..  7.70

Three storeys on one footprint. `COORDINATE_CONTRACT.md`, ratified, says it in
as many words: "floor 0 = ground = Z 0; basement = story -1". The token is the
STOREY, not the building. Nothing should be spent chasing it.

**And a correction to the instrument, because it made a weak claim sound
strong.** `insert_overhang.py` first ranked only modules BIGGER than their slot.
A wall tipped onto a horizontal axis is the same box in a different orientation
-- shorter than its slot, never larger -- so "no module is bigger than its slot"
was true and would have missed exactly the fault it was pointed at. It now
compares absolute deviation and reports height mismatch separately, since yaw is
granted by the slot and rotation about a horizontal axis is not. The clean
result above is from the corrected version.

Three frame errors were made writing that tool in one hour -- Z-up dims against
Y-up boxes, the ground plate mistaken for the shell, and yaw counted as size --
and each printed confident, plausible, wrong numbers. All three announced
themselves the same way: **equal and opposite values on two axes.** That pattern
in this tool's output means the tool is wrong, not the art.

**And the fixtures are inside the floor slabs -- all of them.** Spotted by eye
while walking (a lit panel visible only from between storeys), then measured
from `site.site.lights.json`, 75 anchors:

    z        type                          storey geometry
     -0.10   fluorescent x 4               ground floor slab spans -0.30 .. 0.00
      1.50   window x 8
      2.45   wall_pack x 8
      2.55   sign x 4
      2.85   wall_pack x 4
      3.90   fluorescent x 12              storey-1 slab spans  3.70 .. 4.00
      5.60   window x 16
      6.00   streetlight x 7
      7.90   fluorescent x 12              roof slab spans      7.70 .. 8.00

**28 of 28 fluorescents sit inside a floor slab.** The pattern is identical at
every level: the anchor is exactly 0.10 m below the floor ABOVE it, while the
ceiling of the room below is 0.30 m lower -- so the light is buried 0.20 m up
inside a 0.30 m slab, invisible from either room and lighting a void. One wrong
reference plane, applied uniformly: the fixture is measured from the slab above
instead of from the ceiling below.

Nothing else in the manifest has this shape. Windows at 1.50 and 5.60,
wall packs at 2.45 and 2.85, signs at 2.55, streetlights at 6.00 -- all sit in
open space at plausible heights. It is the ceiling-mounted type alone, and it is
every one of them.

**This reorders item 30.** That item says the light loader is never called and
treats wiring it as the fix. Wiring it now would spawn all 28 interior lights
INSIDE solid slabs: the interiors would stay exactly as dark as they are, the
census would report 28 lights present, and the fix would read as having failed
for some other reason. The anchor heights have to be corrected first, or the two
defects will mask each other -- which is the same trap as measuring an export
built from last week's job.

It also gives item 32's interior figures a second cause. The objective shot
reads centre 30.9 against a frame mean of 54.3; `gl_compatibility` forecloses
GI, no loader spawns the anchored lights, AND the anchors are in the wrong place
by 0.20 m. Three independent reasons the rooms are dark, and only the third is
cheap to fix.

**What `Dressing` actually contains, and it names every unexplained thing in
this file.** `tools/glb_nodes.py` on the baked layer -- 2255 nodes:

    count  family              y_min    y_max      building spans -4.00 .. 8.00
     1389  Cover_panel_field   -4.37    12.07
      299  Cover_gutter_run    -0.38    12.61
      299  Cover_pilaster      -2.15     5.85
       64  Cover_edge_strip     7.70     9.00
       64  Cover_base_course   -4.30    -4.00
       64  Cover_curb          -4.30    -4.30
       60  Cover_conduit_run    4.78     5.68
       16  Cover_frame          1.10     5.60

    below y = -4.00 (the basement floor): 114 nodes

* **The rods are `Cover_pilaster`** -- 299 of them. A pilaster is a shallow
  column against a wall; standing free in open floor is what makes them read as
  obstacles, and they are collision-less by contract, so a player walks through.
* **The parapet stubs are `Cover_edge_strip`**, 7.70..9.00 -- one metre above a
  roof that stops at 8.00.
* **The slabs above the roofline are `Cover_panel_field` and
  `Cover_gutter_run`**, reaching 12.07 and 12.61 on an 8 m building. Gutters
  4.6 m above the roof they drain.
* **114 nodes sit under the basement floor** -- curbs and base courses at -4.30,
  panel fields at -4.37.

So the layer spans -4.37 .. 12.61 around a building of -4.00 .. 8.00. It
overshoots at both ends, and the overshoot upward is the larger by a factor of
twelve.

**A limit in `insert_overhang.py`, found by this.** It reported `Dressing` at
y -6.84..6.84, which disagrees with the node translations above. The cause is
its AABB: it hulls each mesh's POSITION `min`/`max` and applies only the
top-level node transform, never composing the per-node transforms INSIDE the
GLB. For a scene of instanced modules that is right -- each module is its own
file at its own node. For a baked layer, where 2255 props live in one file with
their own transforms, it measures the wrong thing and understates the extent.
The 2.85 m figure quoted above is therefore a floor, not the number: the real
overshoot is 4.61 m above the roof. Fix the AABB or restrict the tool to
instanced modules and say so; do not quote its numbers for baked layers.

**And a correction to item 30: the LuxEmit markers DO exist.** That item records
"855 nodes, zero beginning `LuxEmit`, zero nodes with any `extras`" and
concludes `LuxFixtureSpawner` has nothing to find. That reading was taken on the
SHELL glb. The fixtures layer, read here:

    count  family                        y_min   y_max
       34  FluorescentFixture_Diffuser   -0.05    7.95
       34  FluorescentFixture_Housing    -0.05    7.95
       34  LuxEmit_fluorescent           -0.10    7.90
        3  WallPack_Lens / Body / Arm     2.56    2.96
        3  LuxEmit_wall_pack              2.45    2.85
        1  SignBox_Face / Cabinet / Arms  2.55    2.55
        1  LuxEmit_sign                   2.55    2.55

**38 `LuxEmit_*` markers, baked by Zoo exactly as the spawner's contract
describes.** Item 30's conclusion that the marker path is dead is wrong; what is
true is that nothing calls the spawner, and that the markers are in the fixtures
layer rather than the shell. Zoo has held up its end.

This also confirms the buried lights from the geometry side rather than the
manifest: the fluorescent HOUSING sits at 7.95 and its emitter at 7.90, inside a
floor slab spanning 7.70..8.00. The hardware is in the slab, not just the anchor.

**Ordering this implies.** The z-fight gate being bypassed by cache is first: it
is a gate that already knows the answer and is not being heard. The `Dressing`
placement is second and needs a rule before it needs a fix -- an intrusion limit
in the slot manifest, and a gate that reads it. The UV question is third and is
item 31's. Zoo's structural library needs nothing on this evidence, which is
worth saying plainly after a day spent suspecting it.

*STATUS: CLOSED 2026-09-05 -- BUILT, THEMED, AND SHIPPED IN A PACKAGE. The
mechanism was already there and nothing had ever asked it for a whole level.
`cold_8001` set `lot_library` and each candidate drew three DISTINCT
archetypes -- seed_8001 deli_a01 / freight_terminal_a03 / brewery_a01,
seed_8102 depot_a01 / stadium_a02 / train_yard_a03, seed_8203
freight_terminal_a03 / construction_site_a01 / pawn_shop_a02 -- different
within each site AND between candidates. The art layer fanned out per
archetype through zoo_fixtures, patina_apply, patina_dressing, zoo_kit,
zoo_dressing and lux_fixture_gate, and `presentation_compose`,
`themed_site_assemble`, `lux_apply` and `dispatch_handoff` all succeeded. THE
PORTABLE PACKAGE CARRIES THREE PER-BUILDING DIRECTORIES (`depot_a01`,
`stadium_a02`, `train_yard_a03`) with its 33 interactives distributed 9/11/13
across them. Against this item's founding measurement -- "1 `ext_resource`, 4
instances" -- that is closed. RESIDUAL, and it belongs to item 79 not here:
articulation is still module-periodic by construction, because `relief_parts`
never learns where a module sits in the run.*

**37. Every building on the site is the same building.** Noticed while walking
-- "very similar stair/ladder placement... a lack of variety" -- and the
measurement is stronger than the observation: they are not similar, they are
identical, rotated.

    _write_site_spec:  glb = str(_latest_output(deli_out, "shell.glb"))
                       buildings = [{"id": f"b{i}", **source, ...
                                     "at": p["at"], "rot": p["rot"]} ...]

One shell, N placements. Only `at` and `rot` differ. The assembled themed site
agrees from the other end: **1 `ext_resource`, 4 instances**. Stairs and ladders
land in the same relative place in every building because there is one building.

**And this is not Deli Counter's limit.** `deli_counter/build/` holds **41
distinct archetypes across 103 GLBs** -- airport_terminal, apartment_walkup,
arena, auto_shop, bank_branch, bank_tower, brewery, casino, clinic,
construction_site, country_club, courthouse, credit_union, deli, depot,
freight_terminal, funeral_home, gas_station, landmark_hall, large_warehouse,
mansion, marina, market_hall, museum, parking_garage, pawn_shop, pharmacy,
rail_station, self_storage, stadium, strip_club, strip_retail, supermarket,
train_yard, warehouse, and more. The generator has variety to spare. The site
spec asks for one thing four times.

**RE-MEASURED 2026-09-04, AND MOST OF THIS ITEM IS ALREADY BUILT.** This item
has carried no status line since it was written, so it has been counted OPEN
on the strength of its opening sentence while the work it asks for landed
underneath it. What exists now:

* `packages/pipeline/building_library.py` -- `index`, `pick_lot`, `lot_for`,
  `require_themed_shells`, `require_art_inputs`, `stale_shells`. It selects a
  lot of distinct archetypes from a build directory, deterministic on
  (library, seed, count).
* `_write_site_spec` places a MIXED row -- `site_variation` takes per-building
  footprints, and `uncovered` + `overlapping` refuse a row that does not fit.
* `_lot_for_compose` publishes one themed scene per archetype, and
  `themed_scene` is EITHER one scene (single-shell) OR a mapping
  {archetype_id: scene}, so each building is dressed as itself.
* The planner fans out per archetype. **This is roadmap 41 step 4, which this
  item and three briefs name as the thing it waits on, and it has landed.**

MEASURED, by planning rather than by reading: `plan lot_demo_001 --art` emits
`zoo_fixtures_build`, `patina_apply`, `patina_dressing`, `zoo_kit_build`,
`zoo_dressing_build` and `lux_fixture_gate` jobs for FIVE distinct archetypes
-- arena_a03, large_warehouse_a01, mansion_a02, pvp_station_ref,
strip_club_a03 -- converging on one `presentation_compose`, then
`themed_site_assemble` and `lux_apply`.

**SO THE RESIDUAL IS ADOPTION, NOT CODE, AND IT IS WORSE THAN IT LOOKS.** The
varied lot is opt-in on `lot_library` and dormant without it, deliberately, so
that an evaluated mission is not silently re-placed. Every brief on disk,
audited:

    cold_7001  category5_baie_dore_001   building_count 4   no lot_library
    cold_7002  bank_block_001            building_count 3   no lot_library
    cold_7003  bank_block_001            building_count 3   no lot_library
    rockay     category5_baie_dore_001                      no lot_library
    lot_demo   art_probe_001                                no lot_library (deliberate)
    lot_demo   lot_demo_001              building_count 5   SET
    rockay     rockay_lot_demo_001       building_count 5   SET
    unlit_3b   unlit_probe_001           building_count 1   SET (inert at 1)

The two that set it are demos of the feature. **All three cold-run briefs --
the runs that exist to answer item 17 -- do not**, so every intervention count
this file quotes was measured on a site of one repeated building, and item
69's five identical shells were compounded by this item placing them four
times each.

**WHAT SHIPPED FOR IT.** Level Factory 0.54.0 prints, from `_write_site_spec`
when a brief asks for more than one building and names no library:

    [site] 3 buildings, ONE archetype: this brief sets no `lot_library`, so
    the same generated shell is placed 3 times (roadmap 37). Point it at a
    build directory -- e.g. deli_counter/build -- for a lot of different
    buildings.

That is the item 62 capability-gap shape: what was asked, what will actually
be built, and the one key that changes it. Two tests in
`tests/unit/test_lot_library_signal.py` pin both branches -- it fires at
count > 1 and stays quiet at 1, because a warning on a single-building brief
trains the reader to scroll past the line that matters.

**WHAT IS STILL UNPROVEN, AND IT IS THE EXPENSIVE HALF.** Everything above is
a PLANNED DAG and a spec on disk. No `.glb` was built, so the varied themed
lot -- five different buildings, each dressed as itself, composed into one
site -- has never been produced end to end. That is a Blender run, and it is
the same run item 69's acceptance test needs. Doing them together is the
cheap order: one cold run with `lot_library` set and the candidate seed
threaded answers both, and answers item 17's third run at the same time.

The DAG says the same: one `deli_generate` job per candidate, so a mission
produces one building and the site repeats it. Nothing is broken here -- it does
exactly what it was written to do -- and it is the single biggest reason a
generated level reads as generated.

**The same lesson is already in this codebase one level up.** `cmd_run` carries
a candidate-diversity check with the comment: *"A mission generates N candidates
so a human can choose between them; that only means something if the N are
different. Nothing had ever compared two, so five copies passed validation five
times."* That is this defect, at the candidate layer, already found and fixed
once. The building layer never got the same treatment.

Two shapes a fix could take, and they cost very differently:

* **N `deli_generate` jobs**, one per building, seeded apart. Real variety --
  different rooms, different stair and ladder placement, different slot counts
  -- at N times the generate and compose cost, and N themed buildings to
  compose rather than one. It also ends the convenience item 29 relies on, that
  there is a single themed scene to instance.
* **Select N from the existing library.** The 103 GLBs are already built. This
  is a selection problem rather than a generation one, and it costs almost
  nothing at build time -- but each building would need its own slots manifest
  and its own themed compose, so the compose stage still multiplies.

Which to take is a decision about what a mission IS -- one archetype repeated
down a street, or a block of different premises -- and this item does not make
it. What it establishes is that the monotony is chosen in `_write_site_spec`,
not imposed by Deli Counter, and that a diversity check at the building layer
would have said so without anyone walking the level.

*STATUS: CLOSED 2026-08-02 -- cap_thick threaded into derive_light_anchors and build_light_manifest*

**38. Light anchors hung below the slab, and four Deli Counter tests that were
already red.** 2026-08-02.

**The fix.** `lights.py` derived a ceiling row's height as
`floor + story_height - 0.1`. That expression's second term is the storey TOP --
the next floor's floor -- so the fixture landed 0.10 m below the slab's TOP face
and therefore 0.20 m INSIDE a 0.30 m slab. Item 36 measured the consequence: 28
of 28 fluorescents buried, invisible from either room, lighting a void.

The rule was already written down and this was its third consumer.
`Building._cap_thick` returns the thickness of the slab capping a storey and
says why it exists: *"One rule, one place, because both wall emitters need it
and two copies drift."* The wall emitters subtract it (`wh = H -
self._cap_thick(s, top)`). The light manifest did not.

`derive_light_anchors` and `build_light_manifest` now take `cap_thick`, a float
or a callable of the storey index, and `write_light_manifest` passes the
builder's own `_cap_thick`. **It is required, with no default** -- a default of
zero would silently reproduce the defect it exists to fix, and this kit does not
ship guards that pass by omission. Three tests added: the fixture must end below
the slab's underside, `cap_thick` may vary by storey (a top storey is capped by
a roof, which need not match a floor), and omitting it raises.

Expected after a rebuild: fluorescent anchors at 3.60 / 7.60 / −0.40 in place of
3.90 / 7.90 / −0.10.

**Every building in `deli_counter/build/` is stale from the moment this lands.**
103 GLBs whose light manifests carry the old heights. That is not a defect, it
is the cost, and it should be stated in the commit rather than discovered later.

**Four tests were already failing before this change**, verified by stashing it
and re-running -- same four, same messages:

    test_nav_gate.py::test_run_gate_parses_result_and_exit_code
    test_nav_gate.py::test_run_gate_failure_verdict
        OSError [WinError 193] "%1 is not a valid Win32 application" --
        environmental, a stub executable the harness cannot exec.

    test_pvp_heist.py::test_opposing_spawn_sightline_fails
        asserts PVP-SPAWN-LOS in the errors; gets an empty set.
    test_failing_fixtures.py::test_fixture_fails_for_documented_reason
        [fx_pvp_spawn_los.json] -- "PASSED but must fail (opposing spawns share
        a direct clear sightline)".

**The PVP pair is one defect seen from both ends: the spawn-sightline check has
stopped firing.** A fixture built to be caught is passing, and the check that
should catch it reports nothing. Same class as the z-fight gate being served
from cache in item 36 -- a gate that knows the answer and is not heard -- and
worth the same priority. Not fixed here, and not this session's doing; recorded
so the next reader does not file it as flaky.

*Landed, and the fix needed a second one to become visible.* The anchor change
alone produced no change in the site: Deli Counter emitted -0.40 / 3.60 / 7.60
while `site.site.lights.json` still read -0.10 / 3.90 / 7.90.

**The Lot adapter's fingerprint hashed the building GLBs and not the manifests
beside them.** The light fix moved no geometry -- every `shell.glb` came out
byte-identical, which is correct and is the point -- so the fingerprint did not
move, `lot_assemble` reported `cache`, and the site kept last run's anchors. Lot
merges each building's `<stem>.lights.json` into `site.site.lights.json`: its
output depended on a file its fingerprint did not watch.

`fingerprint_inputs` now reads the SITE SPEC and folds in every file it names --
each building's `scene`/`glb`/`gameplay`, plus the `<stem>.lights.json` and
`<stem>.gameplay.json` siblings the spec never mentions. Reading the spec rather
than the caller's `building_glbs` list is deliberate: the spec is what Lot
consumes, so a building added there cannot be missed by someone forgetting to
extend a parallel argument, and a test asserts exactly that case.

After: `lot_assemble` succeeded on all five seeds, `deli_generate` correctly read
`cache` (its own output was unchanged), and the site reads 3.60 / 7.60 / -0.40.

**This is the second stage in one day whose inputs were wider than what it
hashed**, and the pair is worth naming as a pattern rather than two incidents:

    --force did not re-run the whole graph        (roadmap 33)
    a fingerprint blind to a file the stage merges (here)

Both produce one symptom: **a green run that ships last week's answer.** Neither
is detectable from the job's own output, because a cache hit and a correct
re-run look identical from downstream -- which is why `tools/stage_census.py`
prints mtimes and refuses cross-run comparisons. Any stage that reads a file it
does not hash belongs on that list; the audit has not been done for the other
adapters, and should be.
**39. Cache correctness: the mechanism is designed and never wired, and the
pattern behind that is the finding.** Written 2026-08-02 after two stale-cache
defects in one day. Nothing here is implemented; the measurements it asks for
come first.

**RETRACTED: `--force` is not broken.** Items 33 and 38 record that "`--force`
did not re-run the whole graph" as though it were a defect. It is a deliberate
no-op, and `scheduler.py` says so:

    # `force` is kept in the signature because `cmd_run` passes it. The
    # behaviour it used to select is now the only behaviour.

The surrounding comment explains the decision: the content cache is keyed on the
build fingerprint rather than on a recorded status, so a cache hit is an honest
statement about inputs and there is nothing to bypass. That is the right call.
It also means **there is no escape hatch** -- when the cache is wrong, a person
cannot force past it, only delete it. Everything below follows from that: the
cache does not need an override, it needs to be correct.

**The mechanism exists and has never been connected.** `BuildFingerprint`
carries a field for precisely this problem:

    upstream_artifact_hashes=list(job_spec.get("upstream_hashes", [])),

`upstream_hashes` occurs **once in the whole repository** -- that read. Nothing
writes it. The list is always empty, on every job, in every run.

**What to do: populate it from the DAG, in the scheduler.** `depends_on` is the
truth about what feeds what, and the scheduler already hashes a job's artifacts
when it publishes to the cache. Folding an upstream job's artifact hashes into
its dependents' fingerprints makes invalidation STRUCTURAL: any upstream output
change invalidates downstream regardless of whether that adapter remembered to
hash the right file. Both of today's defects die at once, and so do the ones
nobody has hit yet.

`fingerprint_inputs` would then only need to cover inputs from OUTSIDE the DAG
-- the site spec Level Factory writes, tool configuration, seeds. Today every
adapter re-states the dependency graph by hand, which is a second copy of
knowledge the planner already holds; this codebase has a name for what happens
then, in `_cap_thick`'s own docstring: *"two copies drift."*

**What NOT to do: audit the adapters one at a time.** It fixes the instances
found and not the class, it goes stale the first time someone adds a file read,
and it is the same hand-maintained duplication that produced the defect.

**Two measurements first, because this could kill the cache outright.**

1. *Are job outputs deterministic run to run?* The output directories are full
   of `*.provenance.json`. If those carry timestamps, then every upstream hash
   changes on every run, nothing ever caches, and every build becomes a full
   rebuild -- turning a correctness fix into a performance catastrophe. The
   answer is a diff of two runs' outputs, not a guess. Whatever must be excluded
   should be excluded by a STATED list; a silent exclusion is how a fingerprint
   goes blind in the first place.
2. *What does the receipt already say?* `_attempt_job` writes
   `fingerprint.last.json` on every evaluation INCLUDING cache hits, with a
   comment about diagnosing a cache hit that should not have happened. It was
   never read today. It would have answered "why did `lot_assemble` hit the
   cache" in one file instead of the four steps it took.

*Measurement 1, answered.* An artifact provenance record, read from
`lot_assemble`'s output:

    "created_at": "2026-08-02T18:55:42.288193+00:00",
    "inputs": [],
    "produced_by": { "job_id": ..., "repository_commit": ..., "tool_version": ... }

**`created_at` is a wall-clock timestamp**, so every `*.provenance.json` differs
on every run by construction. They MUST be excluded from any upstream hashing --
including them would invalidate every downstream job on every run and convert
the cache into a full rebuild, which is the failure mode this item exists to
avoid. The exclusion is `*.provenance.json`, stated here so it is a decision on
the record rather than a filter someone adds quietly.

Everything else in that record is stable and worth keeping: `repository_commit`
and `tool_version` are already folded into the fingerprint separately, and
`logical_name` is what an upstream hash would key on.

*And a third instance of the pattern, in the same file.* The provenance record
carries `"inputs": []`. Empty -- like `upstream_artifact_hashes`, and for the
same reason: the field is declared and nothing populates it. **An artifact that
records what produced it and not what it was produced FROM cannot answer "is
this stale", which is the question both of today's defects turned on.** Two
fields, one absence, and populating either would have surfaced the problem.

That makes four in one day: the light loader, Zoo's LuxEmit markers,
`upstream_artifact_hashes`, and `provenance.inputs`. The grep for "declared but
never written" is looking like the highest-yield hour available.

**And the pattern underneath, which outranks the fingerprint story.** Three
times in one day the design was right and the wiring was absent:

    the light loader          designed, documented, never called (item 30)
    Zoo's LuxEmit markers     baked correctly, nothing reads them (item 36)
    upstream_artifact_hashes  a field in the fingerprint, never populated

None of these is a design error. Each is a correct piece that no code path
reaches, and each read as a *missing feature* until someone measured. The useful
review question for this toolchain is not "is this designed correctly" -- it
generally is -- it is **"is this called?"** A grep for the writer of every
declared input, and for the caller of every public entry point, would be a short
afternoon and would probably find more.
**40. The "is this called?" sweep, run.** `tools/never_wired.py` across nine
repos, 2026-08-02. It reports questions, not defects -- a key can legitimately
be written by another repo or by hand-authored JSON, and this triage is the
human half.

**Noise, named so nobody re-triages it.** Roughly four fifths of the output is
correct by design and falls into four groups:

* **Environment variables** -- `BLENDER`, `DC_GODOT`, `DC_THEME`,
  `ANTHROPIC_API_KEY`, `LF_TOOLS_DIR`, `DISPLAY`. Read from `os.environ`,
  written outside Python.
* **External schema keys** -- glTF (`translation`, `bufferView`, `accessors`,
  `POSITION`, `TEXCOORD_0/1`, `componentType`) and Blender node sockets
  (`Color`, `Roughness`, `Base Color`, `Factor`, `BSDF`, `Surface`). Read from
  data this toolchain does not author.
* **Cross-repo manifest fields** -- `matched`, `checked`, `dangling_refs`,
  `conflicts`, `path_proofs`, `sim_seconds`, `walkers`. Written by one tool,
  read by another; the boundary the scanner cannot see across.
* **Test fixture data** -- `bank/attacker_spawn`, `a.glb`, `expected_code`.

**Three leads that are not noise.**

*(a) Laser Tag finding codes that appear only in tests.* `LT_MAP_TRAVERSAL` (4
reads), `LT_MAP_MISSING_PLAYER_SPAWN` (3), `LT_MAP_ENEMY_STUCK` (1),
`LT_MAP_NAVIGATION_MISSING` (1) -- **every read is inside
`tests/unit/test_lasertag_readiness.py`**, and nothing in Level Factory writes
any of them. Either Laser Tag emits them (it is not Python, so the scanner
cannot see it) or the tests assert on codes nothing produces, in which case they
pass by never firing. **That is the exact shape of the PVP sightline gate in
item 38** -- a fixture built to be caught, passing. This is the one to check
first, and it is one grep in the Laser Tag repo.

*(b) Dispatch importers naming files that may not exist.* `dispatch/importers/`
reads `lux.lighting.json` and `lux.volumes.json`. Lux's adapter declares its
outputs as `lux.applied.tscn`, `lux.quality.json` and `lux.validation.json` --
neither of the two names Dispatch is looking for. Also `shell.patina.glb`,
`shell.collision.json`, `lot.nav_hints.json`, `shell.nav_hints.json`. If those
importers silently no-op on absent files, the Dispatch handoff has been running
on a subset of its intended inputs and reporting success -- the same failure
class as everything else found today.

*(c) Substantial functions with no caller.* Worth a look rather than a verdict:

    deli_counter  export_glb              deli_counter.py:2363
    dispatch      build_authority_map     authority.py:66
    dispatch      authority_for           authority.py:56
    level_factory advise_spawn_placement  validation/spawn_placement.py:395
    level_factory unfinished_jobs         project_store/index.py:150
    patina        register_theme_family   slots.py:231
    patina        slot_tint_floor         slots.py:236
    deli_counter  climb_height            ladder.py:184

`export_glb` in the building emitter and `build_authority_map` in Dispatch are
the two that read like load-bearing pieces rather than helpers.

**And the tool flagged its own visitors on the first run** -- `visit_Call`,
`visit_Dict`, `visit_Subscript` -- because `ast.NodeVisitor` dispatches by name.
Fixed by an explicit exclusion list covering that, Blender's operator protocol
(`execute`, `draw`, `register`, `unregister`, `poll`) and pytest hooks. The list
is in the source rather than hidden, because an exclusion nobody can see is how
a scan quietly stops covering things -- which is the defect this whole item is
about, committed by the instrument that looks for it.

*STATUS: NARROWED 2026-08-18 -- THE ROUTING ARGUMENT STANDS AND EVERY NUMBER UNDER IT IS DEAD. Re-measured on FIVE buildings out of the certified portable-godot package (`tools/glb_nodes.py --json`, each `art/dressing/*.glb` against its own `site_base.glb`). The 0.30 m below-floor offset: GONE -- curb and base course sit at exactly 0.00 on all five and `--below 0` returns zero nodes on all five, including `pvp_station_ref`, which does have a basement at -3.75. The extra-storey height: GONE -- every gutter is BELOW its building's top (-0.88, -0.88, -0.23, -0.98, -0.23 m). The 1389 `Cover_panel_field`: the family DOES NOT EXIST, nor do `Cover_pilaster` or `Cover_frame`; five families and 231-260 nodes per building, against 2255. The offsets are now quantised by roof TYPE -- parapet buildings +0.50 edge / -0.88..-0.98 gutter, slab buildings +0.15 / -0.23 -- which is a rule, not drift. WHAT SURVIVES: the routing. Dressing is still on the props channel with no slot, no placement gate, no collision authority and no intrusion limit, and `allowed_inward_intrusion_m` still appears in exactly one file in this repo -- this one, four times, all proposing it, zero occurrences in code or manifest. The item's stated ORDER is corrected below: the two reference-plane leads are not cheap fixes, they are not defects*

**41. The dressing layer is STRUCTURAL ART routed through the decoration
channel, and that is why nothing checks it.** Raised 2026-08-02 after a second
walkthrough: "there is still dressing all over in a way that doesn't look good."

**Read the family names.** `tools/glb_nodes.py` on the baked layer, 2255 nodes:

    1389  Cover_panel_field    -4.37    12.07
     299  Cover_gutter_run     -0.38    12.61
     299  Cover_pilaster       -2.15     5.85
      64  Cover_edge_strip      7.70     9.00
      64  Cover_base_course    -4.30    -4.00
      64  Cover_curb           -4.30    -4.30
      60  Cover_conduit_run     4.78     5.68
      16  Cover_frame           1.10     5.60

Panel fields, pilasters, gutters, base courses, curbs, edge strips, frames.
**None of that is decoration.** In the taxonomy this project adopted (item 35)
it is layer 2, structural art -- the material that wraps the shell and therefore
must FIT it. It is being emitted through the layer-3 props channel, which is
exactly why it has no slot, no placement gate, no collision authority and no
intrusion limit. Nothing enforces fit on geometry whose entire job is to fit.

That reframes the problem from tuning to ROUTING. A pilaster attaches to a wall
line; a gutter runs along a roof edge; a base course sits on a floor. Those are
slot relationships, and Deli Counter already emits slots carrying dimensions,
pivots and transforms. Free-placing them and hoping is what puts rods in the
middle of rooms.

**Two numbers say the placer has reference-plane errors, not taste problems.**

*(a) A 0.30 m offset below the floor.* `Cover_base_course` runs -4.30..-4.00 and
`Cover_curb` sits at -4.30, against a basement floor at **-4.00**. A curb belongs
ON the floor. The magnitude is the slab thickness, and the shape is identical to
the light-anchor defect in item 38: a placer measuring from the wrong plane.

*(b) Roughly one extra storey of height.* `Cover_gutter_run` reaches **12.61**
and `Cover_panel_field` **12.07** on a building that stops at **8.00**. The
building is three storeys of 4 m spanning -4.00..8.00; 12 is what three storeys
measure if you stack them from 0 and forget the basement starts below it. Worth
testing directly rather than assuming -- but a gutter 4.6 m above the roof it
drains is not a near miss.

*Not everything above the roof is wrong.* `Cover_edge_strip` at 7.70..9.00 is
probably CORRECT: a parapet standing a metre above the roof slab is
architecture. Which is precisely why this needs a stated tolerance rather than
"anything above the roofline is a defect" -- a gate written from the frames
would have condemned the one family that is behaving.

**1389 panel fields is the wrong mechanism, not a wrong number.** Panel fields
on a wall are what a MATERIAL does -- a trim sheet, a tiling texture. Emitting
them as 1389 meshes is the "do not fragment excessively" failure from item 35,
and moving them to a material is blocked behind the UV question in item 31.
That makes three things now waiting on UVs: window shading, lightmaps, and this.

**And whatever stays free-placed needs a contract.** `allowed_inward_intrusion_m`
in the slot manifest and a gate that reads it. Today there is literally nothing
for the dressing to violate, which is why every gate passes on a level with rods
standing through the floor.

**Order.** The two reference-plane leads first: they are cheap, probably one
expression each, and the light-anchor fix is the template. Then the intrusion
contract. The reclassification and the material question are real work and want
a decision before code.

RE-MEASURED 2026-08-18 -- THE TWO REFERENCE-PLANE LEADS ARE NOT DEFECTS

Everything above this line was measured on 2026-08-12 against ONE baked layer.
Re-run on the five buildings of the certified `LF_lot_demo_001.portable-godot`
package, `tools/glb_nodes.py --json` on each `art/dressing/*.glb` against that
building's own `site_base.glb`:

```
                      shell y            gutter   vs top      edge strip   vs top
arena_a03            -0.15 .. 12.50       11.62    -0.88    13.00..13.00    +0.50
large_warehouse_a01  -0.15 ..  6.50        5.62    -0.88     7.00.. 7.00    +0.50
mansion_a02          -0.15 ..  7.45        7.22    -0.23     5.90.. 7.60    +0.15
pvp_station_ref      -3.75 ..  7.80        6.82    -0.98     6.90.. 8.30    +0.50
strip_club_a03       -0.15 ..  7.05        6.82    -0.23     5.58.. 7.20    +0.15

Cover_curb          0.00 .. 0.00   on all five      --below 0: 0 node(s), all five
Cover_base_course   0.00 .. 0.00   on all five
```

**(a) is gone.** The curb and base course sit at EXACTLY 0.00, no spread, and
nothing in the dressing layer is below grade -- on `pvp_station_ref` least of
all, which genuinely has a basement at -3.75 and would show it.

**(b) is gone, and inverted.** Not one gutter is above its building; every one
is 0.23 to 0.98 m below the top. The claim was 4.6 m above.

**(c) is gone.** `Cover_panel_field` -- 1389 nodes, the largest family and the
entire basis of the "wrong mechanism, not a wrong number" argument -- does not
exist in any of the five. Neither does `Cover_pilaster` or `Cover_frame`. Five
families survive, 231-260 nodes per building against 2255.

**And the offsets are a rule.** The three buildings whose shells carry literal
`parapet_N/S/E/W` families at the shell max -- arena, large_warehouse,
pvp_station -- place the edge strip +0.50 above it and the gutter -0.88..-0.98
below. The two that top out in `slab` with no parapet -- mansion, strip_club --
use +0.15 and -0.23. Two roof types, two constants each, repeated exactly. An
edge strip half a metre above a parapet is a coping, which is the reading this
item already offered for `Cover_edge_strip` and warned about acting against:
"a gate written from the frames would have condemned the one family that is
behaving."

WHAT THIS DOES NOT TOUCH

The ROUTING argument, which is the item's actual thesis and is unaffected by
any of the above. Dressing is still structural art on the layer-3 props
channel: no slot, no placement gate, no collision authority, no intrusion
limit. `allowed_inward_intrusion_m` occurs in exactly one file in this
repository -- this one, four times, every one of them proposing it. There are
zero occurrences in code or in any manifest. Nothing has been built.

So the ORDER above is wrong and this replaces it. There are no cheap
reference-plane fixes to take first, because there is nothing there to fix.
What is left is the part the item itself called "real work that wants a
decision before code": the intrusion contract, the reclassification, and the
panel-field material question -- and that last one is now moot on this
evidence, because the panel fields are gone.

ONE THING NOT RE-MEASURED. This is the geometry, read from the node table. It
is NOT the walkthrough that raised the item -- "there is still dressing all
over in a way that doesn't look good" -- and a placer that is arithmetically
correct can still look wrong. The numbers say the two published defects are
not there. They do not say the level looks right.
*STATUS: NARROWED 2026-08-14 -- stage 1 SHIPPED and proven on a real package: level_factory 0.26.0 (build dir), 0.27.0 (archive name, stable interior folder, LF_MANIFEST.json), factory-v1.19.0. `LF_lot_demo_001_s5219_20260814T211037Z_f1.18.0_portable-godot.zip`, 213 entries all under `LF_lot_demo_001/`, manifest read back and correct. REMAINING: the interior renames -- `lot/<building>/` -> `sites/<building>/` and dropping `assets/lot.glb` -- which move `res://` paths inside the package and want their own portability run. Original note follows. `docs/EXPORT_NAMING.md`: THREE names -- build dir `LF_<mission>.<profile>/` (two profiles coexist in the workspace), folder inside the archive `LF_<mission>/` (stable, so `res://` paths survive an update), archive `LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip`. The grammar is composed in four places today -- export.py:232, commands 2057/2248/2260 -- and export.py:441's `with_suffix` is why the zip has no profile. Remaining work is `packages/core/ids.py` plus those four callers*

**42. A level leaves the factory with a name that does not say what it is.**
Item 27 closed whether the export WORKS: 36 resources, closure ok, portability
PASS in a clean Godot project. This is the other question — whether the thing
can still be identified once it is on somebody else's disk.

Today, `.level_factory/exports/`:

```
lot_demo_001.portable-godot/                  the drop-in folder
lot_demo_001.portable-godot.portability.json
lot_demo_001.pure-shell/                      a different profile, same shape
lot_demo_001.zip                              18.6 MB, profile unstated
```

**Nothing in those names carries a version or a date.** Not the factory
version that built it, not the tool versions that went into it, not when it
ran. Two exports from two different weeks are indistinguishable on disk. Send
someone `lot_demo_001.zip` twice and they cannot tell which is newer without
unpacking it and knowing that `build.lock.json` is the file to open.

The information is not missing — it is unplaced. `build.lock.json` carries
`created_at`, `spec_sha256` and per-file hashes; `export_profile.json` names
the profile; `factory.manifest.json` pins the certified set. None of it
reaches the name, which is the only part a recipient sees first. That is the
same defect this file spent 2026-08-14 finding everywhere else: a record that
exists somewhere nobody reads.

**And it is named after one tool of ten.** The folder is `lot_*`, the
per-building subtree is `lot/<building>/`, and `assets/` holds `lot.glb`
alongside `shell.glb` — 242,168 bytes each, identical mtime, the same asset
under two names, one of them a tool's. A level is the output of the whole
DAG: Deli Counter shells, Zoo kits, Pixelcoat materials, Patina wear, Lux
light, Dispatch packaging, Lot assembly. Naming the result for the assembler
tells a recipient the wrong thing about what they have, and tells the next
maintainer the wrong thing about who owns it.

**What the name has to carry**, stated as properties rather than a format,
because the format is a decision:

* **Identity** — the mission, so it is obvious what level this is.
* **Provenance** — the factory version, so the pinned tool set is recoverable
  from `factory.manifest.json` at that tag.
* **Time** — when the run happened, sortable, so two exports order themselves
  in a directory listing without being opened.
* **Profile** — `portable-godot` vs `pure-shell`, on the zip as well as the
  folder, because the zip is what gets sent.
* **Origin** — that this came out of a Level Factory at all, rather than out
  of `lot`.

**What is already right and should not be broken.** The contents are
correct and portability is proven; this is a naming and manifest change, not
a repackaging. `HANDOFF.md` (437 bytes today) is the natural place for the
same facts in prose, since it is the first file a recipient opens. Whatever
scheme is chosen wants to be written once in Dispatch or Level Factory and
read everywhere else, rather than composed by each caller — otherwise the
next `make_package.ps1` will name it a fourth way.

*STATUS: CLOSED 2026-08-15 -- one failed stage, not nine failures, and not the cause written below. `presentation_compose` failed on a missing `*_dressing.glb`: the test-fixture Zoo stub's `--dress` branch wrote its index and no geometry, while its own `--fixtures` branch twenty lines above had always written both. NOT a 0.32.0 regression -- the guard appears twice in `adapters/presentation/__init__.py.pre_032` and twice in the current file, unchanged, predating 0.32.0 by ~9 days. Fixed in level_factory 0.33.0; tests/service + tests/integration 28 passed, 0 failed*

**43. A whole CLI spelling stopped working and nothing noticed.**

> **CORRECTED 2026-08-15, and the paragraph below is kept because being
> wrong this way is the finding.** The art stages planned and ran. The
> run printed `pixelcoat_build succeeded`, `zoo_kit_build succeeded`,
> `patina_dressing succeeded`, `zoo_dressing_build succeeded`, then
> `presentation_compose failed` -- and `themed_site_assemble`,
> `lux_apply` and `dispatch_handoff` never ran behind it. The nine
> symptoms listed below are ONE failure and eight downstream absences.
>
> The list read as nine independent facts because it was assembled from
> test names without opening the run. `diagnostics
> <mission>.presentation_compose` named the cause in one command:
> `input_validation_error -- no '*_dressing.glb' ... the job that bakes
> it reported success without publishing one`.
>
> The test could not have told anyone either: it asserted `stage in
> r.stdout`, and the line `bank_block_001.presentation_compose  failed`
> CONTAINS `presentation_compose`. Six of its eight stage checks passed
> on the run that broke.

`run --target presentation` plans no art stages. The run reports
`deli_generate ... cache`, `lot_assemble ... cache`, `Structural checks
passed`, exits 0, and stops. No `lux_apply`, no `dispatch_handoff`, no
presentation compose.

Nine tests say so, in nine different ways:

```
missing stage lux_apply                       test_presentation_export
no presentation previews for m1               test_advanced_review
m1.dispatch_handoff/out/mission.tscn missing  test_batch_production
presentation_status 'pending' != 'ready'      test_facade
job_console("m1.lux_apply") is None           test_facade
node_detail state 'PLANNED' != 'SUCCEEDED'    test_facade
```

`_resolve_layers` treats `--target` as the legacy path -- "explicit
`--art`/`--gameplay` win; otherwise fall back to the legacy `--target`
mapping." The first place to look is `packages/pipeline/planner.py`'s
`layers_for_target`: it either still knows the word `presentation` or it does
not, and it is one function.

**The interesting part is not the mapping.** It is that a documented CLI
spelling could stop planning anything at all, and the only things still
exercising it were tests that had not run since
`tests/test_presentation_fingerprint.py` began failing at import. Collection
aborts before any test in the directory executes, so one broken import took
`tests/integration` and `tests/service` dark together. level_factory 0.32.0
fixed the import; these nine are what was behind it.

Whether they are pre-existing or were exposed by 0.32.0's new `composer`
fingerprint key -- which turns former cache hits into real runs -- is
answered by reverting 0.32.0 and running the two directories again. Do that
before assuming either.

*STATUS: OPEN 2026-08-14 -- specified by `Semantic_Proxy_Replacement_Art_Pass` and `City Collision ArtPass Substitutes`; nothing built. The gate it needs was built today and works*

**44. The green boxes could be cars, and the collision would not change.**
A graybox block is a semantic placeholder: it says what belongs here, not
what it looks like. Its transform already defines position, rotation, scale
and gameplay footprint. Replace the placeholder with an art asset, keep the
block's collision as the authority, and a validated level becomes a
believable one without reopening traversal.

```
Graybox Block -> Identify Object Type -> Select Art Asset
              -> Fit / Orient -> Retain Proxy Collision
              -> Add Non-Collision Detail
```

**The abstraction that makes a small library go far** is shape to category
to variants, not block to model:

```
BOX_MEDIUM_CITY     -> ATM / vending machine / utility cabinet / news rack
BOX_LARGE_CITY      -> dumpster / generator / HVAC / pallet stack
BOX_VEHICLE         -> sedan / taxi / police car / abandoned car
BOX_LONG_CITY       -> bench / planter / barrier / bike rack
CYLINDER_SMALL_CITY -> bollard / hydrant / parking meter / trash can
```

Roughly twenty "universal" proxies -- car, van, dumpster, ATM, vending
machine, utility cabinet, concrete planter, bench, mailbox, news box, trash
can, pallet stack, crate stack, construction barrier, shipping container,
HVAC unit, generator, vendor kiosk, bus shelter, trash pile -- cover most
city graybox. Zoo owns those families, their pivots, bounds, tags and
variation sets. Pixelcoat skins them, which is where the visual variety
multiplies again: one mesh family, several material treatments.

**Art is allowed to exceed the collision.** Mirrors, antennas, handles,
signs, cables, bumpers may protrude and carry no collision of their own.
That is the whole point -- dimensionality without changing navigation.

**Reversible, always.** A designer must be able to reveal the proxy. The
relationship between gameplay object and visual representation stays
explicit rather than being consumed by the substitution.

WHAT THIS NEEDS FIRST, AND IT IS NOT CODE

**Something must name the category, and today nothing does.** Lot's
`markers` carry a `type` (`attacker_spawn`, `cover`), and Deli's carry ids
like `COVER_LOW_AUTO_DESK_MANAGER_OFFICE_0` -- but a *prop block* with a
`BOX_MEDIUM_CITY` tag does not exist in either vocabulary. Deli Counter
emits the block; something has to say what it stands for. That is a contract
question between DC and Zoo and it comes before any substitution code.

**The gate this needs already exists, as of today.** The functional lock now
protects `openings`, `surfaces`, `ground` and the anchor registry, refuses to
be written empty, and reports drift on a real comparison -- level_factory
0.29.0 through 0.31.0, factory-v1.21.0. A proxy replacement that quietly
changed collision would move `collision_fingerprint`, and until this morning
that hash could not have noticed. Run the substitution after the functional
shell lock and the lock is the acceptance test.

**Rejection is a feature.** An asset that cannot fit the gameplay volume
within the allowed scale and yaw limits is refused, not squeezed. Item 41 is
the same boundary from the other side -- structural art routed through the
decoration path -- and both want `allowed_inward_intrusion_m` in the slot
manifest with something that reads it.

*STATUS: OPEN 2026-08-14 -- specified by `Surface_Dressing_Level_Depth_Guide`; nothing built. Item 41 is the same boundary approached from the other side*

**45. Large playable surfaces are visually flat, and the fix is not more
grass.** Surface Dressing is collisionless instanced detail placed across
gameplay surfaces for relief, silhouette breakup, parallax and contact --
without adding gameplay relief. The problem it solves is that a clean
graybox reads as a diagram.

**The stack is layered responsibility, not one increasingly complicated
mesh:**

```
0  Gameplay geometry   floors, walls, stairs, cover      COLLISION AUTHORITY
1  Macro environment   buildings, cliffs, machinery      silhouette and space
2  Mid dressing        pipes, cables, crates, boards     "somebody authored this"
3  Surface dressing    grass, rubble, litter, roots      relief; collisionless
4  Surface detail      decals, cracks, grime             no geometry at all
5  Atmosphere          fog, dust, particles, shafts      depth through air
```

**Core rule: gameplay complexity and visual complexity scale
independently.** A level keeps simple collision and renders a dense
presentation layer.

WHERE IT LIVES IN THIS TOOLCHAIN

Post-lock, and every tool already has the right job for it. Deli Counter
exposes safe surfaces and semantic zones and is not modified by decorative
placement. Zoo owns the dressing asset families with `collision_policy:
none`. Pixelcoat breaks flatness in material before geometry is added --
texture noise and mesh noise must not compete at the same frequency. Patina
is the natural home for placement logic: clusters, seam dressing,
environmental cause, density, negative space. Lux makes relief produce
readable contact shadows without paying for shadow on every pebble. Dispatch
keeps it under a presentation branch that can be culled or disabled whole.
Level Factory gates it and can fail a build.

**The manifest is the deliverable, not the scene.** `surface_zone_id`,
`asset_set`, `placement_mode` (scatter / seam / cluster / anchor / spline /
authored), `density`, `scale_range`, `yaw_range`, `height_band`,
`collision_policy`, `shadow_policy`, `exclusion_tags`, `seed`,
`quality_tier`. Deterministic from a seed, or it is not reproducible and
does not belong in this pipeline.

**Placement rules that are art direction, not code**, and which the manifest
has to be able to express: cluster rather than scatter evenly, because
uniform spacing reads as procedural noise; anchor detail to causes -- growth
at cracks and moisture, rubble at damage, trash against walls and traffic
edges; dress intersections first, because wall-to-floor and prop-to-ground
seams are where modular construction shows; use two to four height bands
(2-10 cm micro, 10-30 cm cover, 30-70 cm medium, selective 70-150 cm).

**The test, and it is a good one:** hide the dressing layer and the level
should still play correctly. Show it and the same level should feel
materially richer. If a dressed level *plays* differently, the presentation
layer is too intrusive -- and Laser Tag is the instrument that says so,
against its own pre-art baseline.

DEFINITION OF DONE, AND ONE LINE OF IT IS NEWLY CHECKABLE

Collision unchanged from the locked version. Navigation regression passes.
Objective anchors, doors, interactables and cover language stay readable. No
decorative asset makes a believable but false traversal promise. No visible
uniform scatter from primary views. Density reducible or disableable without
affecting gameplay. Runtime budgets pass in Godot on worst-case views, not
empty scenes. The package remains deterministic from the manifest.

"Collision unchanged from the locked version" was not a checkable statement
before today. The functional lock hashed two Deli stair systems and would
have reported no drift no matter what a dressing pass did to the site. As of
level_factory 0.31.0 it protects 1,171 records including every collision node
name and every opening, so a dressing pass that touches collision now moves a
hash. This item and items 29 through 31 of that work were built in the wrong
order and it happened to work out.

*STATUS: NARROWED 2026-08-22 -- THE PIPE IS CONNECTED AND FED. Steps 1-3 shipped and proven end-to-end on cr_deli's real gameplay.json: Lot 0.48.0 carries `interactives` into the site (ids VERBATIM -- they are the network handle; transforms world-placed exactly like markers), level_factory 0.48.0 passes them through dispatch staging untouched, and Dispatch ships `interactives.json` beside `gameplay_anchors.json` -- 23/23 machines byte-identical at every hop, plus a `Handoff/Interactives` scene node and `interactive_count` in the manifest. The lock question is answered in `docs/FUNCTIONAL_LOCK.md` ("two collision states, one hash": the locked shell is the DEFAULT state; per-state truth is protected as DATA by `interactive_registry_hash`, keyed on `id`, schema v0.2 -> v0.3), and `interactives` sits in PROTECTED_KEYS with deli backfill. STEP 4 SHIPPED as DC 0.95.0: `material` and `breach_class` populate at spec load from the law every authored spec already followed by hand (window -> glass 16/16; breach -> host wall's material 12/12; soft_wall on drywall/wood/glass, reinforceable on brick_ext/concrete, 12/12), authored values always win, fixtures with no material vocabulary stay honestly null, and the machines carry both as ADVISORIES so the netcode's own input answers "what does a charge do here" without joining back to openings. Building it surfaced a vocabulary drift: an LF-generated spec authors breach_class "reinforced" where `floorplan.py` reads `== "reinforceable"` -- one letter, and the breach never got the treatment its author asked for; `tactical.py` now warns on unrecognized values, and THE GENERATOR THAT WROTE IT HAS NOT BEEN LOCATED. REMAINS: that generator, and the INTERACTIVES.md twin-file sync check -- still nothing compares the two copies, and they HAVE drifted.*

**46. Forty-five state machines a run, reaching nobody.**
The question this started from -- can a destructible system live in tools that
deliberately do not overstep into authoritative gameplay, netcode or backend
-- was answered before it was asked. `deli_counter/docs/INTERACTIVES.md`:

> **The contract describes STATE, never SYNCHRONIZATION.** It says *what* is
> interactive, *what discrete states* it can be in, and *what named
> transitions* move between them. It says **nothing** about who is
> authoritative, how state replicates, tick rate, or interpolation.
>
> Deli Counter must never emit a field that tells the netcode *how* to
> replicate.

That is the boundary, written down and implemented. `Replicated Destructible
Proxy` describes a system whose declaration layer this factory already
builds.

WHAT DELI COUNTER ALREADY EMITS

Every interactive fixture is `(stable_id, states[], default, transitions[])`
-- the entire networked surface -- and the doc's own table shows it mapping
onto snapshot, event/RPC, lockstep and rollback without committing to any:

```json
{ "id": "primos_pizza:if:2cf6a380", "kind": "breach_wall",
  "slot_ref": "ext_0_N_open1",
  "states": ["intact", "breached"], "default": "intact",
  "transitions": [{"event": "breach", "from": "intact", "to": "breached"}],
  "reversible": false, "source": "inferred" }
```

Inference covers the cases without any authoring: `door`/`garage` ->
`[closed, open]`, `breach` -> `[intact, breached]`, `vault` -> `[locked,
unlocked, open, breached]`, `teller` -> `[intact, shattered]`, `safe_deposit`
-> `[intact, drilled]`. A `window` opts in with `breakable: true` and becomes
`[intact, broken]` -- which is the breakable-glass case from the source
document, already built.

**Ids are derived from place, never from an array index** --
`sha1(building, wall, story, kind, round(pos, 4))` -- because openings are
re-sorted by position during the geometry pass and an index would renumber.
Moving an opening changes its id, which is correct: it is a new place.

**And the two-collision-states question already has an answer at this layer.**
`<building>.slots.json` carries `collision_per_state: {"intact": true,
"breached": false}` beside `state_geometry: {"intact": "wall", "breached":
"breach"}`. DC says which states collide. What it does not say is which of
them the FUNCTIONAL LOCK protects, and that question is still open (below).

THE MEASUREMENT

```
deli_generate  shell.gameplay.json       "interactives": 9    per building
lot_assemble   site.site.gameplay.json   no `interactives` key
the package    LF_lot_demo_001_*.zip     0 files mention "interactive"
```

The package's only gameplay file is `gameplay_anchors.json`, carrying
`anchors, dispatch_version, mission_id, schema`. `INTERACTIVES.md` says the
game reads the `interactives` array to replicate state. It never arrives.

**Same shape as the thirteen dropped markers**, and found the same way: Lot
assembles from Deli's shells and carries forward what it restates, and
`interactives` is not in that set. This one is worse because there is no
partial overlap to argue about -- the key is simply absent.

THE WORK

1. **Lot carries `interactives` into the assembled site**, namespaced per
   building the way markers are. Ids are already globally unique
   (`<building>:if:<hash>`), so this is a concatenation, not a merge.
2. **Dispatch ships them** beside `gameplay_anchors.json` -- gameplay side of
   the packaging split, not presentation. They ARE the netcode's input.
3. **The lock protects them.** `interactives` becomes a protected key, so an
   art pass that changes which fixtures exist or what states they have is
   drift. Every mechanism for this exists as of level_factory 0.31.0; it is
   one entry in `PROTECTED_KEYS` once the key is present.
4. **Then, and only then, `breach_class` and `material`.** Both are still
   null on all 76 openings and read by nothing. They are real gaps -- material
   is what decides whether a thing shatters, splinters or dents -- but
   populating them before the pipe is connected is decorating a disconnected
   pipe.

STILL OPEN, AND IT BLOCKS STEP 3

**Two collision states, one hash.** `collision_per_state` says a breached
wall does not collide. The functional lock hashes one collision fingerprint.
Which state is the locked shell -- default, worst case, or every state as a
set? `docs/FUNCTIONAL_LOCK.md` has no answer, and a shell whose collision is
conditional is a different kind of object from the one that document
describes. Answer it there before `interactives` enters the protected set.

**And `INTERACTIVES.md` says its twin lives in the zoo repo** -- "the same
file lives in the **zoo** repo -- keep them in sync." Nothing checks that they
are. Two copies of a contract with no comparison between them is the shape of
every other defect in this file.

*STATUS: CLOSED 2026-08-16 -- DELIVERED, and the cold package it was waiting on exists. All three shapes landed: `LAYER_LIGHT` (0.35.0) is a real fourth layer with `_LAYER_REQUIRES = {LAYER_LIGHT: LAYER_ART}` so it cannot be asked for without art, and ONLY Lux's apply pass moved -- `zoo_fixtures_build` and `lux_fixture_gate` stayed in `LAYER_ART`, so an unlit package still ships validated light FIXTURES and drops only the render solution; `MODE_ART_UNLIT` (0.36.0) is the export mode; `--unlit` is the flag on `run`, `plan` and `batch run`. `dispatch_dep = lux_jid if LAYER_LIGHT in layers else themed_jid` rewires the graph around the hole rather than special-casing it. PROVEN COLD on `unlit_probe_001` through Blender 5.1.1 and headless Godot 4.7: `lux_apply` never ran, `lux_fixture_gate` did, `dispatch_handoff <- themed_site_assemble`, and after items 48 and 49 closed the export came back `ok: true`, `issues: []`, `unresolved_relative_count: 0` in BOTH `portable-godot` and `art-unlit`. The A/B is the answer to question 1 stated by an artifact: on a mission where Lux NEVER RAN the two packages are byte-identical -- 56 files, 7,158,515 bytes, zero files differing -- because there is nothing to subtract. FOUR QUESTIONS ANSWERED: absent, not ignorable (33 Lux files dropped on lot_demo_001 and nothing else); the light anchors DO ship, because the fixture bake and its gate stayed in the art layer; the entry scene is `site.tscn`, shipped by 0.37.0; and the fourth-layer / sub-flag / third-mode question was answered ALL THREE rather than one. WHAT IS NOT DONE, and is now item 53: the decoupling this item exists to serve is real in the DAG and absent at the FILE level -- Lux's output names are string literals in 8 modules -- and the CLI expresses the fourth layer by SUBTRACTION (`--art` means art AND light, `--unlit` removes it; there is no positive `--light`), which is an interface decision nobody has made*

**47. A recipient with their own lighting has to take ours or take graybox.**

> **SHIPPED 2026-08-15 (stages 1-3a).** `--art` still means art + light
> and `--target presentation` still plans the full stack; `--unlit`
> subtracts. Only Lux's APPLY pass moved -- `zoo_fixtures_build` bakes
> the physical hardware and `lux_fixture_gate` machine-checks it, and
> both stay in the art layer, so an unlit package ships validated
> fixtures and their `LuxEmit` markers as a contract another lighting
> system can read.
>
> **The prediction below was right and incomplete.** The seam WAS
> half-cut where the item said. What it did not predict is that there
> was a hole behind it: `themed_site_assemble` writes a 31,872 byte
> `site.tscn` that reached NO package, and the lit export only worked
> because Lux's output stood in for the assembly. Cutting Lux out left
> 180 files, 28.6 MB of geometry, and an entry that instanced nothing --
> which `export_closure_scan.json` reported as `ok: true,
> resource_count: 6`, because closure walks FROM the entry and an entry
> referencing nothing is trivially closed.

The goal, stated plainly: a Level Factory package that had a FULL art pass,
where including Lux is a choice. Another team may have their own lighting
system and still want the kits, the materials and the wear.

Today there are two useful answers and neither is that one:

```
portable-godot   everything, Lux included
pure-shell       functional geometry + collision only -- the whole art pass
                 goes with it
```

**The seam is already named, by hand, in `export.py`:**

```python
# Files that carry presentation only (dropped in pure-shell mode).
_PRESENTATION_FILES = {"lux.applied.tscn", "lux.quality.json"}
```

Those two files are Lux's output and nothing else's. Somebody has already
written down where lighting ends -- it is just wired to a mode that also
throws away Zoo, Pixelcoat and Patina.

**The bundling is one level up.** `--art` is described in the CLI as "add the
Art layer (Zoo/Pixelcoat/Patina/Lux)" -- one layer, four tools. Three of them
do SURFACE work a recipient keeps. The fourth does lighting they replace.
Splitting that is most of the item.

**And `lux_strategy` is already a choice with the wrong options.**
`localized` copies the minimal Lux runtime into the package; `baked` writes
presentation to vertex/lightmap data so no Lux runtime is needed. Neither
serves a studio with its own lighting: baked light data is still OUR lighting
decisions welded into their level. The missing value is a third one -- ship
the art, ship no light.

FOUR QUESTIONS, AND THEY WANT ANSWERS BEFORE CODE

1. **Absent or ignorable?** Does "no Lux" mean the lightmaps are not in the
   package, or present and safely ignored? Absent is smaller and honest;
   ignorable lets a recipient A/B ours against theirs. They are different
   products.
2. **Do the light ANCHORS ship anyway?** Lot derives where lights were
   intended to go. A team bringing its own lighting still probably wants that
   -- it is level design intent, not a lighting solution. Item 38 is about
   those anchors hanging below the slab, so they are real data with a known
   history.
3. **What is the entry scene?** `write_entry_scene` makes a graybox export's
   entry `site.tscn` and a lit export's entry the presentation scene. An
   art-pass-without-Lux package has a composed root and no
   `lux.applied.tscn`. Nothing decides that case today.
4. **A fourth layer, a sub-flag on `--art`, or a third export mode?** All
   three work. A mode is the cheapest to package and the most visible in the
   name; a layer is the most honest about what actually ran. Decide before
   building, because the answer changes what `--force` re-runs.

WHAT IS ALREADY PAID FOR

A third profile costs nothing in naming. `export_build_dir_name` and the
archive grammar both carry the profile (level_factory 0.26.0 and 0.27.0), so
`LF_<mission>.art-unlit/` coexists with the other two in one workspace by
construction, and the archive says which one it is. That was not true a day
before this was written.

**But the closure scan and the portability test have never seen this mode.**
`CLOSURE_ENFORCED`'s comment is the precedent: a mode nobody has scanned gets
scanned before it gets enforced, and the first run that scans it is expected
to find something.

*STATUS: CLOSED 2026-08-16 -- FIXED and re-measured on a cold workspace. level_factory 0.38.0 keys the narrowing on the brief instead of on the invocation's planned graph; `art_run` is gone from the signature, the call site and the module. Re-running `tools/run_3b_unlit.ps1` from empty, through Blender and headless Godot: `lot_assemble`, `walktest_navqa` and `laser_tag_evaluate` all report `cache` on the art pass -- the art run produced a byte-identical site spec, so the assemble did not re-execute and neither did the graders. The graded site IS the shipped site, established by the fingerprint cache rather than by anyone comparing two files. `[site] graded lot: 98 of 123 ... keyed on the brief` now prints identically in both invocations, and the functional lock does not fire. Suite 823 passed / 11 skipped / 0 failed. Question 1 -- whether the draw may move behind `candidate_selected` at all -- is NOT answered by this and is carried into item 49's neighbourhood. ORIGINALLY MEASURED on unlit_probe_001, one workspace, one seed. `lot_assemble.candidate.seed_5017` succeeded twice in `_runs/3b/run.log` (lines 31 and 51) and drew a different building each time: graybox `cr_garage` (17 openings, 178 colliders, 12 markers), art `landmark_hall_a03` (13 openings, 176 colliders, 7 markers), with `shell.glb` byte-identical across both fingerprints. Everything that graded the mission graded the first draw. The functional lock caught it and refused the export -- this item is the redraw, not the lock. MECHANISM LOCATED: `commands/__init__.py:238` computes `_art_run` from THIS INVOCATION'S planned graph, and `:942` narrows the greybox pool on it -- so `batch create` draws from 123 and the art run draws from 98, and `pick_lot` is handed a different list for the same seed. Evidence preserved in `docs/findings/ITEM48_THE_DRAW_MOVED.md` because `_runs/` is gitignored*

**48. The same job and the same seed draw a different building on the art
pass, and everything that graded the mission graded the other one.**
`unlit_probe_001` was a fresh workspace built for roadmap 47 stage 3b: one
mission, one candidate, seed 5017, run once from empty. In it,
`unlit_probe_001.lot_assemble.candidate.seed_5017` -- one job id, one
candidate, one seed -- ran twice and produced two different sites.

```
_runs/3b/run.log:31   under `batch create`
_runs/3b/run.log:51   under `run --art --unlit --gameplay`
```

The two draws, from the adapter fingerprints and the two site specs:

```
                          building           openings  colliders  markers
graybox  22:01:21Z        cr_garage                17        178       12
art      21:49:26Z        landmark_hall_a03        13        176        7
```

(Those two timestamps are the fingerprints that survive on disk. The FIRST
graybox assemble, the one under `batch create`, has been overwritten by the
third -- `fingerprint.last.json` keeps only the last. Its building is known
from the lock and the graders it fed, which measured `cr_garage`.)

`shell.glb` hashes `a929d7d2...` in BOTH fingerprints. The lot is the same
lot. The building standing in it is not.

**The pipeline says so itself, in a line written to reassure:**

```
[site] graded lot (art run): 98 of 123 shell(s) can carry a theme
       -- the graded draw and the shipped draw come from the same pool
```

Same pool, different filter. A seeded draw over 98 candidates does not land
on the same element as a seeded draw over 123, and the sentence that says
"the same pool" carries both numbers -- the reassurance and the evidence
against it are the same string.

**Everything that graded the mission graded the first draw.**
`walktest_navqa`, `laser_tag_evaluate`, the structural checks (14 findings)
and the functional lock all completed under `batch create`, before the art
run re-drew. Their verdicts describe `cr_garage`. The package would have
shipped `landmark_hall_a03`.

**The lock caught it, and that is the good news.** Export refused, in both
modes:

```
export blocked by functional regression:
  - collision_fingerprint changed after art pass
  - gameplay-anchor registry changed after art pass
```

That is the functional lock doing precisely the job it was built for, on its
first mission that ever put it to the test. Nothing else in the pipeline is
positioned to notice: the graders never see the second site, and the export
closure scan checks that files resolve, not that they are the ones that were
graded. **Any fix that makes this export succeed by relaxing the lock is the
wrong fix.**

**And a third `lot_assemble`, graybox, at 22:01:21Z drew `cr_garage` again**
-- so the unthemed draw is stable across invocations and the themed one is
the departure. That rules out plain seed nondeterminism.

WHERE IT IS, EXACTLY

```python
# commands/__init__.py:238 -- DOES THIS RUN HAVE AN ART LAYER?
_art_run = any(j.stage_id == "themed_site_assemble"
               for j in plan.graph.jobs())

# commands/__init__.py:942, in _write_site_spec -- which pool GREYBOX draws from
if themed_map or art_run:
    complete = building_library.require_themed_shells(complete, count)
lot = building_library.pick_lot(complete, seed, count)
```

`_art_run` is read off **the graph planned by this invocation**. It is not a
property of the mission, the brief, or the candidate:

```
batch create                    plans no themed_site_assemble   123 -> cr_garage
run --art --unlit --gameplay    plans one                        98 -> landmark_hall_a03
```

**And this was a deliberate change, made for a good reason, that moved the
defect instead of closing it.** The comment above line 942 records that the
narrowing was extended to the greybox branch because
`probe_pool_divergence.py` had measured, on `lot_demo_001`, that 14 of 15
building slots already carried an archetype other than the one Laser Tag
graded, and 13 graded archetypes never shipped at all. The stated goal --
"grade the pool that ships" -- is right.

It made the greybox pass and the themed pass agree WITHIN one invocation. It
could not make them agree ACROSS invocations, because `batch create` plans no
art layer, and `batch create` is where the graders, the structural checks and
the functional lock all run. The divergence moved from inside a run to
between the run that grades and the run that ships, where the lock is the
only thing standing.

`building_library.lot_for()` is NOT this path -- it returns `[], []` below
`building_count < 2` and this brief asked for one building -- but its own
comment carries the same warning from the other side: *"a narrower pool
re-selects every lot already built and graded."* Two selectors, one hazard,
written down twice, and neither writing-down was a check.

**So question 2 below is no longer "should we?" but "keyed on what?"** The
narrowing wants to depend on something true of the MISSION for its whole
life. `lot_library` on the brief is the obvious candidate: it is already what
gates the art layer, it is set before `batch create` runs, and a mission
without it never reaches this branch at all, so existing single-shell
missions stay byte-for-byte. That is a one-line change and it is deliberately
NOT made yet, because it re-selects buildings for every mission carrying
`lot_library` and question 1 outranks it.

**The evidence is preserved.** `.gitignore:20` ignores `_runs/`, and
`fingerprint.last.json` has already overwritten the first graybox assemble.
`docs/findings/ITEM48_THE_DRAW_MOVED.md` carries the run log, both site
specs' counts, all five fingerprints verbatim, and a sha256 for every file
quoted -- so this item survives the workspace being deleted.

THE SECOND HALF: NOTHING CAN JOIN A GRADE TO A SITE

Even where the draw does not move, no artifact can prove the graded scene is
the assembled one, because the two sides record disjoint identifiers:

```
lot_assemble         building_hashes + site_spec_hash   no scene hash
walktest_navqa       scene_hash                          no building hashes
laser_tag_evaluate   scene_hash                          no building hashes
```

There is no key in common, so "did the graders grade what shipped?" is not a
question this system can be asked -- it is inferred from job ordering. On
`lot_demo_001` the inference happens to hold, and only by 19 seconds:
`lot_assemble` at `2026-08-13T23:20:57`, walktest at `23:21:16.383`, Laser
Tag at `23:21:16.984`. The two graders' own `scene_hash` values differ from
each other (`b3bd2815...`, `abf3edf5...`), so they do not agree on a subject
identifier either.

**`lot_demo_001`'s lock has never guarded an art pass.** It was approved
`2026-08-14T22:56`, 23h36m after that assemble, so it records a post-art
state and there is nothing left for it to disagree with. It exports cleanly
for that reason and not because its draw is stable. Item 47's stages 1-3a
were all measured on that mission, which is why none of them saw this.

QUESTIONS BEFORE CODE

1. **May the draw narrow after a candidate is approved at all?**
   `candidate_selected` is a HUMAN approval. As it stands, the art pass
   re-runs the draw behind that approval and can hand back a different
   building. The cheapest correct answer may be that the themed re-draw is
   simply not allowed to change the building -- theme the one that was
   approved, or fail.
2. **Or constrain the graybox draw to the 98 from the start?** Then the
   graded and shipped buildings are the same object by construction. It
   costs 25 shells of variety and buys the entire question.
3. **Is `lot_assemble` one job or two?** One job id producing two different
   sites in one workspace is exactly what makes this invisible in a job
   listing, in `index.sqlite`, and in the run log -- both lines say
   "succeeded".
4. **What does a fingerprint have to carry for the question to be
   askable?** The minimum is a shared key: the assemble emitting the scene
   hash it wrote, or the graders emitting the building set they loaded.
   Either one turns the joinability gap into a query.

RELATED, AND NOT THE SAME

Item 43 was "a whole CLI spelling stopped working and nothing noticed." Item
5 was "a run that evaluated nothing reported a clean pass." Both are the same
family as the second half of this item -- a check that cannot see what it
claims to cover -- but the first half is not that. The first half is a
producer that gives two answers to one question, and it was caught, by the
one guard built to catch it.

*STATUS: CLOSED 2026-08-16 -- FIXED as level_factory 0.39.0 and proven on the package. `_assembly_building_dir` reads the assembly scene and returns `lot/<id>` when it names exactly one such package AND the composed root has no `lot/` of its own; the composed root is copied THERE instead of to the package root, and the composer's own `site.tscn` stops being skipped because under `lot/<id>/` it IS the building. A varied lot hits neither condition and is untouched. Re-exported from the cached 3b workspace: BEFORE `ok: false`, `site.tscn: relative ext_resource resolves to nothing: lot/shell/site.tscn`, entry reaching 2 of 56 files; AFTER `ok: true`, `issues: []`, `unresolved_relative_count: 0`, in BOTH `portable-godot` and `art-unlit`, with `lot/shell/site.tscn` 48,004 B and its 31 GLBs beside it and NO duplicate copy at the root. The export also reached artifacts it had never written before -- `project.godot`, `LF_MANIFEST.json`, `export_profile.json`, `output_layers.json`, `portable_resource_manifest.json` -- because it had never got past the closure gate on this mission. tests/unit green. CAUSE, from a hash-verified read (`export.py` 31,675 B, sha256 5303E3D0...): `export_mission` step 2.5, added in 0.37.0, copied the assembly scene over the package root and nothing else from that job, so on a SINGLE-SHELL mission a self-sufficient inlined scene was replaced by one naming `lot/<id>/`. 0.37.0 was measured on five-building lot_demo_001, which is why nothing caught it. `--unlit` acquitted: both modes failed and both now pass*

**49. Step 2.5 replaces a self-contained root scene with one that names a
directory the export never carries -- on single-shell missions only.**
`unlit_probe_001` exported for the first time on 2026-08-16, item 48's fix
having removed the functional-lock refusal that had been stopping it. Both
modes then failed the same way:

```
EXPORT_CLOSURE_BROKEN: 0 unresolved res:// reference(s), 0 misrooted,
                       1 unresolved relative, 0 absolute path(s)
  site.tscn: relative ext_resource resolves to nothing: lot/shell/site.tscn (from ./)
  resource_count: 2
```

THE CHAIN, EVERY LINK VERIFIED

`_write_site_spec`'s single-shell branch names the path and records the
source. `"shell"` is a hardcoded literal on that branch, NOT a library id:

```python
if themed_scene and not themed_map:
    staged_packages["shell"] = str(Path(themed_scene).parent)
    source = {"scene": "lot/shell/site.tscn"}
```

That goes to `packages.json`, the Lot adapter plans a staging command against
`staging_manifest_path`, and `packages/staging/site_packages.py` delivers.
It arrived -- this is on disk:

```
themed_site_assemble/out/site.tscn                    5,567   the assembly
themed_site_assemble/out/lot/shell/site.tscn         47,460   the building
themed_site_assemble/out/lot/shell/site_base.glb    255,352
themed_site_assemble/out/lot/shell/art/zoo/*.glb     30 files
```

Then `export_mission` takes exactly one file out of that directory:

```python
# 2.5 THE ASSEMBLY SCENE
if profile.mode != MODE_PURE_SHELL and themed_site_dir:
    themed_scene = Path(themed_site_dir) / "site.tscn"
    if themed_scene.is_file():
        shutil.copy2(str(themed_scene), str(export_dir / "site.tscn"))
```

One file. Not the `lot/` tree beside it that the file references.

WHY ONLY SINGLE-SHELL MISSIONS

Step 2 copies `composed_root` to the export ROOT. What is in a composed root
depends on how many buildings the mission has, and `export.py`'s own comment
states both shapes:

```
A single-shell compose INLINES its geometry and its presentation scene DOES
name `res://site.tscn`. A themed multi-building site instances five packages
and names `res://lot/<archetype>/site.tscn` instead -- measured on
lot_demo_001: five such refs, no `res://site.tscn`.
```

So a varied lot's composed root already contains `lot/<archetype>/`, and
`_copy_tree` carries it; the assembly's references resolve and always have.
A single-shell composed root contains `site.tscn`, `site_base.glb` and `art/`
at its TOP LEVEL -- which is why those files appear at the package root with
mtimes matching `lot/shell/`'s copies. They are not that directory flattened.
They are the same composer output, copied twice from one source by two
different steps, and `copy2` preserves mtimes.

**0.37.0 introduced it, and 0.37.0 was right about the problem it fixed.**
Before step 2.5 the single-shell root `site.tscn` was the composer's inlined
building, which resolved against the `site_base.glb` and `art/` beside it and
closed. Step 2.5 exists because on lot_demo_001 the assembly scene reached no
package at all and an unlit export opened to nothing. It fixed that, on a
five-building mission, where the assembly's references were already present.
On a one-building mission the same copy replaces a scene that resolves with a
scene that cannot.

**THE FIX, AND IT IS A CHOICE.** Step 2.5 must carry what it names -- copy
`themed_site_dir`'s `lot/` subtree alongside the scene -- or the single-shell
spec must stop routing through `lot/shell/` and reference the root directly,
or step 2.5 must not fire when the composed root is the inlined single-shell
shape. The first is the smallest and keeps one rule for both mission shapes.
The last restores the pre-0.37.0 behaviour and re-opens what 0.37.0 closed.
Doing none of them is the current behaviour, and it ships.

**And nothing tests the one-building themed export.** Every measurement in
roadmap 47's stages 1-3a was taken on lot_demo_001, five buildings; 3b used
one building precisely because the point was the layer set rather than the
scale. That choice is what surfaced this, and a fixture at each shape is what
would have caught it before an export did.

WHAT THIS ITEM SAID FIRST, AND SECOND, AND WHY BOTH WERE WRONG

**First:** that the archetype was called `shell` because the lot was drawing
this pipeline's own output back out of `deli_counter/build` as a source.
`tools/probe_lot_own_output.py` was written to test it and refuted it: on the
real library `shell`, `site`, `site_base` and `lot` are not in it at all, and
`source_exclusion` catches the eleven it claims to (two facades, nine `lf_`
ids) with nothing slipping past. The `shell` in `lot/shell/` is a literal on a
code branch. The evidence that suggested otherwise -- `assets/lot.glb` and
`assets/shell.glb` shipping at one sha256, `a929d7d2...`, 242,176 bytes each
-- is real and is roadmap 42's outstanding `assets/lot.glb` work, not this.

**Second:** that the export FLATTENED `lot/shell/` to the root, and that a
basename collision between `lot/shell/site.tscn` and the site's own
`site.tscn` ate the building. That was inferred from matching mtimes and it
is wrong: nothing flattens that directory, and the matching mtimes are two
`copy2` calls from one source. The collision is real but it is not a
collision -- step 2.5 overwrites deliberately, and `export.py`'s comment says
so in as many words.

Both were written from evidence and ahead of the code. The same probe that
killed the first one also reproduced item 48's divergence from the library
alone -- seed 5017, wide pool `cr_garage`, themed pool `landmark_hall_a03` --
so it earned its keep twice. The second was killed by reading
`export_mission` out of a file stamped with its own byte count and sha256,
which is now the rule for this item: a mechanism claim here cites a verified
read or it does not go in.

*STATUS: CLOSED 2026-08-16 -- FIXED as level_factory 0.40.0 and confirmed on the package. The finding was not one stale manifest but TWO manifests: Dispatch's `resource_manifest.json` (`dispatch.resource_manifest.v0.2`, 17 entries, recording `mission.tscn` at 16,246 bytes beside a 688-byte file, written at `...388494` and overwritten by LF at `...389514`) and LF's own `portable_resource_manifest.json` (`level_factory.portable_manifest.v0.1`, 58 resources with sha256 and size each, including `lot/shell/site.tscn` and all 31 art/zoo GLBs, written at export time and CORRECT). The stale one had the better name, so it is the one a recipient opens. FIX: `resource_manifest.json` joins the `skip` set the handoff copy already uses -- dropped rather than regenerated, following the composed-root copy twelve lines below which already skips `portable_resource_manifest.json` because the composer writes one and LF writes its own. If a recipient contract ever needs that name, REGENERATE it there rather than un-skip it; the problem was never the file, it was the file being stale. CONFIRMED by re-export: no `resource_manifest.json` in the package, `portable_resource_manifest.json` 10,651 -> 10,485 B (one fewer file to describe), and the closure scan byte-for-byte unchanged -- `ok: true`, `issues: []`, `resource_count: 3`, every counter identical. `_METADATA_FILES` meant the scan never read either manifest for references, so nothing was depending on it*

**50. The package ships a resource manifest that describes a different
package.**
`dispatch.resource_manifest.v0.2`, in the export root, next to the files it
is wrong about:

```
resource_manifest.json:  mission.tscn   16,246 bytes  sha256:35165b8d...
on disk:                 mission.tscn      688 bytes
```

The mtimes say what happened without needing anybody's memory:
`resource_manifest.json` was written at `...388494` and `mission.tscn` at
`...389514`. Dispatch wrote a manifest describing ITS entry scene; Level
Factory then replaced the entry scene with its own 688-byte portable one and
left the manifest alone. A consumer verifying the package against its own
manifest fails on the first file.

**And it is not only stale, it is short.** The manifest lists 14 files. The
package holds 56. `site.tscn`, `site_base.glb` and all 30 `art/` GLBs are
absent from it -- which means a recipient checking "did I receive everything"
against this file would conclude yes while holding a package whose art is
undescribed.

This is the same boundary as the discarded 65,493-byte Dispatch
`mission.tscn` already on the smaller list: two tools write the same
artifact, the second wins, and the first tool's account of the package
survives it. The manifest is either Dispatch's to own and LF must not
overwrite what it describes, or it is a package-level artifact and belongs
downstream of every writer. It is currently neither.

*STATUS: CLOSED 2026-08-16 -- ALL THREE FIXED AND RE-MEASURED. TWO of the three mechanisms this item proposed were refuted by measurement; the third was correct as written. Defect ONE (six stale callers) is FIXED and re-measured: `patch_lot_stale_spawn_callers.py` gives the four geometry assertions a one-point path at six call sites and derives the two read-backs' window from the route with `crew_reaction_path`, the way `place_enemies` does at `site_spawns.py:803` -- a read-back on `[spawn]` would ask an easier question than the search and pass exactly the maps the search had been too generous about. The predicate was NOT touched; its refusal to default `crew_path` worked as designed and only the follow-through was missing. Suite 328 passed / 8 failed -> 334 passed / 2 failed. Defect THREE's MECHANISM IS REFUTED and rewritten below: it is not 48's family and the scene is not losing the plan. `_lasertag_hook_nodes` seats the hooks and clears the crew spawn before planning, and the test planned from the RAW route -- on BAIE_DORE, whose crew spawn is the dead centre of a 44 x 44 shell, `clear_crew_spawn` moves it 23.5 m and takes all six enemies with it. Planned from the same `pos` the scene was written from, 0 of 18 coordinate pairs fail at abs_tol=1e-3. Defect TWO is MEASURED AND FIXED, and it was neither of the two things this item offered. TWO FAULTS STACKED. First, `assemble` never cleared the crew spawn, so cover was planned for a crew standing INSIDE building `b0` at (-70.0, 30.0) while the scene shipped the cleared spawn at (-60.5, 30.0); from inside a shell almost every sightline reads as already broken, which is why `plan_cover` claimed `open_lines=0` over a map with a clear 51.9 m lane. `patch_lot_cover_ships_spawn.py`. That also settles the 52.8-versus-51.945 instrument disagreement: two different enemy sets, both numbered from zero, one placed from each spawn. Second, with the inputs corrected the planner became honest (`open_lines` 0 -> 1) and showed the real fault: the 12-piece opening budget is spent longest-first over ALL marker pairs, and none of the twelve touched a line the crew stands on -- six broke enemy-to-enemy sightlines, which describe nothing about who opens fire on the crew. Serving the crew's lines first, same budget, stable sort so longest-first survives inside each group: 3 of 12 pieces now touch the crew, all seven of its lines close, `open_lines` 0. `patch_lot_cover_crew_first.py`. `test_site_cover.py` was NOT modified -- it asserted the right contract throughout. STILL OPEN, deliberately: `assemble` and `write_walk_scene` derive the mission points twice and this only makes the two agree; enemy-to-enemy pairs still consume budget after the crew is served (excluding them outright measured 7 opening pieces and 18 total, also with 0 open lines); and cover planning is still coupled to `place_enemies`, which is awkward given enemy placement belongs to the gameplay layer and not to this pipeline. AND SEE ITEM 3, "Lot places enemies twice, and nothing checks the two agree", which described the double placement before this session re-derived it as a new finding: item 3 carried an explicit OPEN status line dated 2026-08-12 saying both call sites had been re-confirmed, so it was neither unclassified nor stale -- it simply was not searched for. Its prescription -- place once and thread the result through, or assert the two agree -- is the fork this session chose between without knowing the item had already framed it, and the "deliberately still open" note above is that item's point restated*

**51. `lot`'s own suite has been red through every certification this month,
and one of the three defects is a level that is not the level that was
planned.**
Run on 2026-08-16 against a clean checkout of `lot` 0.41.0, so none of this
is fallout from level_factory 0.38.0-0.40.0:

```
8 failed, 328 passed in 4.26s
```

**ONE: the arity bug, six tests.** `tests/test_site_spawns.py:345` calls the
predicate with three positional arguments:

```python
assert site_spawns.opening_engagement_is_fair(
    point[:2], spawn, occluders), (...)
```

and `site_spawns.py:470` iterates the second one:

```python
if all(math.dist(candidate, p) >= reach for p in crew_path):
```

`spawn` is `SEED_5320_ROUTE["spawn"][:2]`, a single 2-tuple. Bound to
`crew_path` it iterates to floats, and `math.dist(candidate, 37.7)` raises
`TypeError: 'float' object is not iterable`. A spawn POINT is arriving where
a crew PATH is wanted. Six red lines, one fix:

```
test_an_enemy_down_an_open_street_inside_sight_range_is_not_fair
test_the_same_enemy_behind_a_building_is_fair
test_and_so_is_one_further_off_than_either_side_can_open_fire
test_the_sight_range_itself_is_not_a_standoff
test_no_enemy_can_shoot_the_crew_before_it_has_moved
test_the_written_positions_are_read_back_and_not_taken_on_trust
```

Which of the two sides is wrong is NOT established here. The caller may be
passing the wrong thing, or the signature may have gained a parameter without
its callers. Six tests agreeing on the same call shape is weak evidence for
the caller, and the function's own docstring is the thing to read first.

**TWO: the cover was planned for a crew standing somewhere else, and then
for the wrong lines. -- MEASURED AND FIXED 2026-08-16.**

Two faults, one behind the other. Neither is "the search" or "the check".

**FAULT ONE: cover planned for a crew the scene does not ship.** `assemble`
seated the mission points and never cleared the crew spawn, so it planned from
(-70.0, 30.0) -- the dead centre of `b0`, footprint x -78.0 .. -62.0 --
while `write_walk_scene` cleared it to (-60.5, 30.0) and shipped that. From
inside a shell the building occludes almost everything, so `plan_cover`
reported `open_lines=0`: it believed it had covered a map it had never
correctly measured. One statement in `assemble` fixes it; the shipped spawn
does not move, because `write_walk_scene` already cleared it and seat+clear is
idempotent (measured: 0.000000 m on a second application).

This also disposes of the 52.8-versus-51.945 disagreement recorded above. Two
`place_enemies` calls fire inside one `assemble` -- `lot.py:1874` for the cover
plan and `lot.py:1257` for the scene -- and before the fix they returned
different six-enemy sets, both numbered from zero. There was no instrument
error. There were two different `Enemy_5`s.

**FAULT TWO: the opening budget never reached the crew.** With the inputs
corrected the planner became honest -- `open_lines` 0 -> 1 -- and the real
defect showed. `open_sightlines` returns every marker pair over the opening
range, longest first, and `plan_cover` takes twelve. On this site those twelve
were:

```
Cover_0  Extraction -> Objective     Cover_6   Enemy_0 -> Extraction
Cover_1  Enemy_5 -> Objective        Cover_7   Enemy_4 -> Objective
Cover_2  Enemy_2 -> Enemy_5   <--    Cover_8   Enemy_0 -> Enemy_5   <--
Cover_3  Enemy_3 -> Enemy_5   <--    Cover_9   Enemy_5 -> Extraction
Cover_4  Enemy_0 -> Objective        Cover_10  Enemy_4 -> Enemy_5   <--
Cover_5  Enemy_1 -> Enemy_5   <--    Cover_11  Enemy_0 -> Enemy_3   <--
```

ZERO of the twelve involve `LT_PlayerSpawn`. Six break enemy-to-enemy
sightlines -- cover so one enemy cannot see another, which says nothing about
who opens fire on the crew, since they are the same team. The crew had seven
open lines (130.5, 115.9, 106.4, 77.3, 67.8, 53.9, 51.9 m) and got none, and
`unbreakable` was 0 throughout, so a placeable spot existed the whole time.

Serving the crew's lines first fixes it on the SAME budget. The longest-first
heuristic is kept inside each group by sorting stably on one boolean:

```
                    opening pieces  touching crew  total  open_lines  test
longest first                   12              0     23           1  FAILS
crew lines first                12              3     23           0  PASSES
```

Three pieces close all seven crew lines -- "the worst line's fix usually
shortens three others" working, finally pointed at the lines that matter.

`test_site_cover.py` was NOT modified. It asserted the right contract from the
start, and the instruction in this item not to loosen or skip it was correct.

WHAT IS STILL OPEN, DELIBERATELY

- `assemble` and `write_walk_scene` still derive the mission points twice,
  independently. Fault one is fixed by making the two agree, not by making
  there be one.
- Enemy-to-enemy pairs still consume budget once the crew is served. Excluding
  them outright measured 7 opening pieces and 18 total, also with 0 open
  lines -- fewer pieces for the same result, but it is a separate decision
  about what `open_sightlines` should return at all.
- Cover planning still derives its priorities from `place_enemies`, which is
  awkward if enemy placement is leaving this pipeline for the gameplay layer.

The reading this replaces, kept because a retracted finding is cheaper to keep
than to rediscover:

**TWO: the cover assertion.**

```
test_site_cover.py::test_the_cover_that_was_planned_is_in_the_scene_that_gets_shipped
AssertionError: Enemy_5 still sees the crew spawn down 51.9 m of open ground
               in the scene that shipped
```

That test exists because a search whose model of cover is wrong passes every
candidate on the way in and still writes a map that opens with a shot -- the
check the search cannot perform on itself. It is currently failing, which
means either the search or the check is wrong, and both readings are worth
the same until somebody measures.

**THREE: the scene DOES carry the position the planner chose. The TEST was
holding a different plan. -- MECHANISM CORRECTED 2026-08-16, measured.**

`_lasertag_hook_nodes` does not plan against the positions it is handed. It
seats the nav hooks onto floor, clears the crew spawn off the wall it is
standing against, and spreads the enemies along the route THOSE TWO STEPS
produce (`lot.py:1242-1253`). The test planned from the raw dict instead:

```python
planned = site_spawns.place_enemies(BAIE_DORE, route()).positions
```

On `BAIE_DORE` the crew spawn (51.0, -5.0) is the dead centre of `b1`, a
44 x 44 shell at (51, -5). `clear_crew_spawn` moves it to (51.0, 18.5) --
23.5 m -- and `seat_destinations` drops the objective from z 0.9 to 0.0. The
route's first point moves, so every enemy spread along it moves too. All six
disagree, not only the pair the assertion reached first:

```
 i    planned x (test)   product x (scene)
 0           19.242160           37.734968     <- the assertion's pair
 1           64.683855           36.919915
 2           69.055220           48.119216
 3           73.426585           65.310451
 4           88.003898           82.593142
 5          107.547001           99.869736
```

`37.73496811511527` through `_v3`'s `{:g}` is `37.735`, the number in the
traceback. Recomputed from the same `pos` the scene was written from, **0 of
18 coordinate pairs fail at `abs_tol=1e-3`**. Nothing else was behind it.

So this is defect ONE's family, not 48's: a stale caller reproducing the
tool's pipeline with inputs the tool does not use. The ordering hypothesis
below is refuted directly -- reordering can only produce numbers that are IN
the planned set, and 37.735 is not any planned coordinate on any axis.

WHY IT DRIFTED, AND WHAT WAS DONE ABOUT IT. Because `_lasertag_hook_nodes`
returned only the scene body, the one question worth asking of it -- are the
positions in the scene the positions that were planned -- could be asked ONLY
by re-running its derivation by hand. The test's copy of that sequence went
stale, and a third preprocessing step would have desynced it again. The
derivation now lives in `_lasertag_hook_plan`, which returns the resolved
positions, route and enemies; `_lasertag_hook_nodes` calls it and writes the
same body (asserted byte-identical, not assumed). The test asks the tool which
plan it used. `patch_lot_hook_plan.py`.

Noted while reading and NOT a defect: `lot.py:1409-1414` seats and clears
`pos` and then hands it to `_lasertag_hook_nodes`, which does both again.
Measured idempotent on this site with `solids=None` -- the crew spawn moves
0.000000 m on the second application. Untested on sites with a collision
reading.

WHAT THE ORIGINAL READING GOT RIGHT. Both of its warnings were correct and are
why this stayed findable: widening the bound or skipping the test would have
buried a genuine input mismatch. What it got wrong was the mechanism, by
comparing two artefacts without first establishing they came from the same
build -- the failure `CLAUDE.md` rule 1 names. It is kept below in full,
because a retracted finding is cheaper to keep than to rediscover.

REFUTED 2026-08-16 -- the reading the block above replaces:

**THREE, AND THE ONE THAT MATTERS MOST: the scene does not carry the position
the planner chose.**

```
test_site_spawns.py:461  test_the_walk_scene_carries_the_placed_positions
    for got, want in zip((gx, gy, gz), (sx, sz + 1.0, -sy)):
        assert math.isclose(got, want, abs_tol=1e-3), (got, want)
AssertionError: (37.735, 19.242160304653307)
```

**This is not a tolerance failure and must not be filed as one.** 37.735
against 19.242 is 18.5 m apart; no `abs_tol` closes that. The test's comment
is about surviving two roundings in the same direction, which is what makes
the assertion LOOK like a precision check and is exactly how this would get
written off. The pairing is an axis remap -- site `(x, y, z)` to Godot
`(x, z + lift, -y)` -- and the first pair, `gx` against `sx`, is the one that
fails. An ordering difference, or a remap applied twice, produces a gap of
that size; a rounding never does.

Its docstring states the stake: *"The scene is the artifact Laser Tag reads;
the plan is only useful if it is what got written."* It asserts
`len(written) == len(planned) == 6` and both sides pass that, so six enemies
were written and six were planned -- they are just not in the same places.

**THAT IS ROADMAP 48's FAMILY, ONE TOOL DOWN.** 48 was the graded site not
being the shipped site. This is the planned SPAWN not being the shipped
spawn, inside the tool that does the placing, caught by a test written for
precisely that and red long enough that four certifications have shipped over
it. `factory-v1.25.0` records the 8 failures but not this reading of them.

WHAT NOT TO DO

Do not fix the tolerance. Do not skip the test. The assertion is correct and
the number it prints is the finding.


*STATUS: CLOSED 2026-08-16 -- MEASURED on the mission it was overdue for. All stages EXECUTED rather than cache-hit, because `tool_version` is folded into the build fingerprint and the cached receipt said `Lot 0.33.0` -- so every earlier number for this mission came from nine minor versions back. Cover verified at five buildings with a real collision reading: `LOT_SIGHTLINE_OPEN` on NONE of three candidates, `unbreakable 0`, `pinches 0`. One change was tried and REJECTED on measurement, and the reason is the useful part of this item Its retirement of the enemy-enemy exclusion is REVERSED 2026-08-17 on precedence, not on evidence -- see the reversal below*

**52. `lot_demo_001` re-measured, and the route exposure it reports is the
design working rather than failing.**
Re-run 2026-08-16 under level_factory 0.40.0 and lot 0.42.0, the first numbers
on this mission since Lot 0.33.0. Its cached assemble receipt
(`fingerprint.last.json`) read `evaluated_utc 2026-08-13T23:20:57`,
`tool_version "Lot 0.33.0"` -- so the 45/100 and `route_completion_rate: 0.0`
this roadmap carries were produced nine minor versions back. The new artifacts
are stamped: `tool_version "Lot 0.42.0"`, `repository_commit df848df`.

`lot_assemble`, `walktest_navqa` and `laser_tag_evaluate` all EXECUTED on all
three candidates. That confirms item 39's claim that `tool_version` is folded
into the fingerprint, on a real mission -- a tool upgrade does invalidate a
workspace.

**WHAT THE COVER WORK DID AT FIVE BUILDINGS.** Item 51's fixes had only ever
been measured on `test_site_cover`'s two-building yard with no collision
reading. On the real mission, with 959 colliders and 1,029 surfaces:

```
LOT_SIGHTLINE_OPEN   fired on NONE of the three candidates
seed_5219 cover_plan  placed 16 (5 opening + 11 route)
                      route_open 14   unbreakable 0   pinches 0
```

The opening pass closed every marker sightline with FIVE of its twelve pieces.
Crew-first ordering holds at scale.

**AND LASER TAG ASKS FOR ENEMY-TO-ENEMY COVER BY NAME.** Item 51's entry left
"exclude enemy-to-enemy pairs from the opening budget" standing as a live
alternative, on the reasoning that such a line says nothing about who shoots
the crew. It is not an alternative. `LT_OPEN_SIGHTLINE` reports those lines
with coordinates and a remedy -- *"Enemy_2 and Enemy_5 see each other across
108.1 m of open ground, past the 45 m at which Laser Tag opens fire; fix: cover
near (19.0, 36.3) would break it"* -- three of them on seed_5219 alone.
Excluding those pairs would delete cover the grader requests. Retired.

**REVERSED 2026-08-17. LOT OUTRANKS THE GRADER.** The retirement above is
withdrawn. It rested on `LT_OPEN_SIGHTLINE` naming those lines with a
remedy -- that is, on the grader's request being authoritative. It is not.
Laser Tag is advisory, Lot builds the level, and enemy placement is leaving
Lot for the gameplay layer, so a request phrased in `Enemy_*` markers
cannot bind Lot's budget.

**WHAT WAS MEASURED FIRST.** The shipped export carried 16 pieces, each
recording the pair it was placed for:

```
11  route@N -> Enemy_M            the route pass
 3  Enemy_M -> LT_ObjectivePoint
 2  Enemy_M -> Enemy_N
 0  anything touching LT_PlayerSpawn
```

15 of 16 pieces are placed against an `Enemy_*` point. `open_sightlines` is
all-pairs, so K enemies contribute C(K,2) lines. The enemy markers are
functioning as a six-sample approximation of "somewhere a shooter could
stand" -- which is why removing them does not merely trim the budget, it
removes most of the planner's question.

**SEED-MATCHED, BOTH DIRECTIONS, SAME THREE CANDIDATES.** Reverted, re-run,
read per seed, re-applied, re-read -- and the second patched read reproduced
the first exactly, with every stage cache-hitting, so the numbers are not a
rebuild artefact:

```
seed   reverted (placed, route_open)   patched     what moved
5017   (9, 3)   one enemy-enemy        (8, 3)      waste removed, no cost
5118   (9, 0)   one enemy-enemy        (9, 0)      freed slot went to the
                                                   ROUTE: enemy-route 4 -> 5
5219   (16, 14) two enemy-enemy        (14, 15)    one route stretch left open
```

**THE COST IS REAL AND IS NOT ARGUED AWAY.** On seed_5219 `route_open` goes
14 -> 15. One of the two enemy-enemy crates was incidentally blocking a
route line, and the route pass did not replace it because its own density
cap (`ROUTE_METRES_PER_PIECE`) was already met -- the same cap that made
the spare-budget change above wrong. Mission findings went 51 -> 50 across
the three candidates.

**WHAT WAS NOT DONE, STATED PLAINLY.** Which finding disappeared was not
isolated, and `LT_OPEN_SIGHTLINE` was NOT counted patched-versus-reverted
per seed. Item 52's claim that excluding these pairs deletes cover the
grader asks for is therefore UNREFUTED on its own terms. It is overruled
because Lot outranks Laser Tag, not because it was shown to be wrong. If
that ordering is ever revisited, this is the measurement to take first.

**METHOD FAILURE WORTH RECORDING.** The exclusion was re-derived from
scratch and shipped before this item was read. The roadmap had already
analysed it, with the grader's coordinates, and retired it -- and this item
also already carried `seed_5219 placed 16 ... route_open 14`, the exact
"before" numbers that were re-measured with a full pipeline run. Same
failure as item 3. The measurement got done; the search did not.

**SHIPPED** in lot 0.44.0, `site_cover.py`, inside `plan_cover`'s nested
`outstanding()`. Deliberately NOT in `open_sightlines`, which is byte-
identical and still returns every pair, so Laser Tag and
`level_factory/packages/validation/` see exactly what they saw.

**WHAT ACTUALLY DECOUPLES LOT.** Re-pose the question on standable ground:
cover the stretches of the crew's route visible from anywhere a shooter
could legally stand within `OPENING_RANGE`, rather than from six sampled
enemy points. That removes `Enemy_*` from `cover_points` altogether. Not
attempted as code. SCOPED AND MEASURED 2026-08-17 -- see directly below.

**MEASURED 2026-08-17. THE OBVIOUS METRIC IS REFUTED.** The re-posing above
was scoped and probed read-only against all three `lot_demo_001` candidates.
No code shipped.

**THE SAMPLER IS FREE.** Lot already knows where a body can stand --
`site_spawns.outdoors` is two point-in-rect tests -- and sweeping the route
band at 5 m x 5 m yields 353-713 standable posts in 0.00 s. Cost was never
the obstacle.

**BOOLEAN EXPOSURE SATURATES**, so "count exposed route samples instead of
pairs" is dead on arrival:

```
seed   posts pairs_e pairs_p exposed_e exposed_p samples budget
5017    371      27    1381         9         9       9      7
5118    353      25    1014         8         8       8      6
5219    713      51    3902        16        16      16     11
```

Every route sample is ALREADY exposed under the six enemy points -- 9/9, 8/8,
16/16 -- so the posts add nothing and the number is pinned at maximum. Pairs
fail in the other direction: 3902 against a route budget of 11.

**ARC EXPOSURE DISCRIMINATES.** Bin each sample's threat bearings into 72
slices of 5 degrees and measure what fraction of the full 360 holds a shooter
with a clear line:

```
seed  mean_enemies  mean_posts  at_full_360   spread (posts)
5017      4.0%        68.2%        0 / 9        43% .. 93%
5118      4.2%        65.8%        0 / 8        44% .. 90%
5219      4.3%        79.7%        0 / 16       51% .. 99%
```

`mean_enemies ~ 4%` is the number this item was missing. **Six enemy points
occupy about three of seventy-two bearings.** Lot has been planning cover
against a 4% sample of the directions a shooter could come from, which is the
quantitative form of "15 of 16 pieces are placed against an `Enemy_*` point".

**TODAY'S PLACEMENT IS NEAR-RANDOM AGAINST ARC.** Scoring the pieces Lot
actually placed, against a greedy arc-maximising placement on the same
budget:

```
seed  budget  placed  before   after today     after greedy    greedy cost
5017     7       8     68.2%   57.4%  (-10.8)  34.1%  (-34.1)     3.0 s
5118     6       9     65.8%   55.4%  (-10.4)  41.0%  (-24.8)     1.6 s
5219    11      14     79.7%   69.8%  ( -9.9)  46.4%  (-33.2)    31.1 s
```

Today's placement reduces arc by ~10% on EVERY seed regardless of geometry.
That flatness is what optimising a 4% sample looks like. Greedy reaches
2.4x-3.4x the reduction using FEWER pieces every time -- 7 against 8, 6
against 9, 11 against 14.

**WHAT THIS DOES NOT ESTABLISH.** The greedy figure is an UPPER BOUND from a
capped 250-candidate set with no separation or legality constraints beyond
`_piece_rect`; a real planner lands below it. Greedy scoring cost 31.1 s on
seed_5219 against `assemble`'s own 0.18 s, so restricting candidates to the
neighbourhood of high-exposure samples is MANDATORY rather than an
optimisation. The opening pass has not been analysed under arc at all --
only the route pass. Nothing was tried on any mission but `lot_demo_001`.

**METHOD NOTE.** The first sweep measured Lot's DECLARED-footprint fallback
without noticing. `package._find_asset` looks for a `.glb` next to the site
spec and then in `<dc>/build/<name>`; the spec names `buildings/<stem>.glb`,
the library stores `<stem>.glb` at `build/` root, and the pipeline's temp dir
had been cleaned of its staged copies -- so neither path resolved and
`assemble` degraded in silence. The probe now stages the geometry itself and
REFUSES to report numbers if `LOT_OCCLUDERS_DECLARED` fired. With staging it
reproduces the recorded run exactly: `LOT_COVER_PLACED 14`,
`LOT_ROUTE_COVER_PLACED 11 of 14`, `LOT_ROUTE_EXPOSED 15` against the
artifact's `placed 14` / `route_open 15`. Saturation was present in both
readings, so the refutation did not depend on the faulty one. Luck, not
method.


**PREDICTION 3 FIXED, AND THE BOUND GOT BETTER.** The 31.1 s was scoring
every bearing key against every candidate. Three changes: a bounding-box
reject before the real segment test; per-candidate TOUCHED KEYS, so a
candidate scores against the ~50 bins it can affect rather than all ~900; and
a candidate band restricted to 12 m of the route. `COVER_SEPARATION` (6 m) is
now enforced between chosen pieces, which the first bound ignored.

```
seed  budget  today     greedy WIDE          greedy NEAR (12 m, 6 m sep)  kept
5017     7    -10.8%    -34.1%  (233 cand)   -40.3%  ( 99 cand)           118%
5118     6    -10.4%    -24.8%  (227 cand)   -38.2%  ( 79 cand)           154%
5219    11     -9.9%    -33.2%  (236 cand)   -51.0%  (242 cand)           153%
```

**31.1 s -> 0.2 s worst case, and the RESTRICTED band beats the unrestricted
one on every seed.** A `COVER_SIZE` piece at distance d subtends about
2*atan(COVER_SIZE/2/d) -- 33 degrees at 5 m, 11 at 15 m, 4 at 45 m -- so
sampling the whole post set evenly diluted the near candidates that carry the
arc. Restricting concentrated the budget where the geometry says it belongs.

Today's placement reduces arc by ~10% on every seed. A restricted, separated,
realistic greedy reaches 38-51%. That is **3.7x-5.2x**, not the 2.4x-3.4x an
unconstrained bound suggested. The bound became more honest AND better, which
is the opposite of what was expected when candidate restriction was written
down as a risk.

STILL AN UPPER BOUND. Candidates are standable posts, not verified legal
piece positions, and nothing checks them against `_usable`. A real planner
lands below this.

Probe: `tools/probe_standable_sweep.py` -- read-only, stages its own
geometry, about 2 s for all three seeds.

**THE CHANGE THAT WAS TRIED AND REJECTED.** `route_open: 14` reads like a
defect. The opening pass had left SEVEN of its twelve unspent while the route
pass exhausted all eleven of its own, so the obvious move is to carry the
leftover down. It was written, and it worked on a constructed case -- route
pieces 4 -> 10, route_open 14 -> 2, opening untouched, pinches 0.

It is wrong, and `tests/test_lot.py::test_route_budget_scales_with_the_route_
and_is_reported_when_short` says so: it asserts the route budget is exactly
`ceil(route_length / ROUTE_METRES_PER_PIECE)`, and the carry made it 4 where
the test wants 1. **The test is right.** Its docstring -- *"A flat twelve is
generous on a 40 m approach and nothing on a 250 m one"* -- is arguing that the
allowance must be a scaled CAP, and `plan_cover`'s own comment says what the
cap is for: *"a producer that placed one per line would litter the street with
crates."* Carrying up to twelve flat pieces onto a deliberately scaled cap
pushes the route pass toward one-piece-per-open-line, which is the behaviour
the cap exists to prevent. The mitigation offered for it -- that extra pieces
only land on genuinely exposed lines -- is not a mitigation, it IS the failure
mode.

So the 14 is not a cover-budget defect. The route runs ~270 m past SIX enemies
each with a 45 m envelope; the exposed-stretch count is a function of enemy
density against route length. The cap stops Lot answering an enemy-density
problem by filling the street, and `LOT_ROUTE_EXPOSED` reports the remainder
honestly, which is exactly what the second half of that test demands.

WHAT NOT TO DO

Do not raise the route budget to make `route_open` smaller. Do not carry the
opening's leftover. Both were tried on 2026-08-16 and the suite refused them
for a stated reason. If route exposure is to come down, the lever is enemy
placement -- which is leaving this pipeline for the gameplay layer -- or a
different notion of what the route pass is for, not more pieces.

**WHAT IS ADVISORY HERE AND WHAT IS NOT.** Lot makes the level; Laser Tag
grades it. Its numbers are recorded because they are evidence, not because they
are gates: seed_5017 FAIL 40 over 25 runs with 4% traversal, seed_5118 0% and
the route never completed, seed_5219 16%, overexposure 45-69%, player-stuck
861 / 3,663 / 718. `LT_ROUTE_NEVER_COMPLETED` names its own instrument --
*"walktest_navqa walks the same spine on the baked navmesh with no combat in
it, and says which leg failed. Read that first."* It was read: **PASS**, every
bot `targets_reached 1/1` on all four legs. The map is walkable. Laser Tag's
own text attributes the failure to the crew halting on contact, which is
downstream's model of combat and out of scope under this file's boundary.

The one Lot-side finding in that set is `LT_DESTINATION_ABOVE_FLOOR` on
seed_5219 -- an objective marker 6.00 m above the ground plane -- and that is
item 9's residual gap, second instance. Not new, and not a navmesh defect.

*STATUS: NARROWED 2026-08-18 -- FIRST RANKED FIX SHIPPED, and the mechanism this item gave for it was WRONG. It said `lux.quality.json` "already echoes the applied preset back" and ranked first a comparison against `_preset_for(model)`. It echoes the REQUEST: `run_lux_apply.gd` writes `{"preset": preset_name, ...}`, the `--preset` argument straight back out, so the proposed check compared a string with itself -- inside an item whose subject is checks that cannot fail. Fourth mechanism published from a grep this session; corrected in place below rather than rewritten. level_factory 0.41.0 reads `LuxRoot.get_current_preset()` instead (`lux_root.gd:641`, `_current`, assigned only by `_apply_immediate` from the library resource), reports it as `preset_applied`, and raises LUX_PRESET_NOT_APPLIED when the two disagree -- no Python touched, the finding rides the existing `lux.validation.json` channel. NOT YET RUN ON HARDWARE. What remains open is the third-ranked item only: 27 filename literals across 8 modules, tidiness*

**53. One Lux check is a silent no-op, and the filename literals are
tidiness with one real consequence.**
Item 47 asked for a fourth layer so that Lux could change without touching
level building. In the DAG it worked: `lux_apply` is simply not planned when
`LAYER_LIGHT` is absent, and `dispatch_dep` rewires around the hole. The
fixture bake and its gate stayed in `LAYER_ART`, so the level-design data is
on the level side of the seam and only the render solution is on Lux's.

**What survives the seam is the filenames.** Measured 2026-08-16 over
`level_factory\`, excluding `.pre_*`, `__pycache__` and `tests\`:

```
9  packages/exporting/export.py
4  adapters/lux/__init__.py
4  packages/exporting/localize.py
3  apps/cli/commands/__init__.py
2  packages/pipeline/planner.py
2  packages/preview/walk_preview.py
2  packages/service/facade.py
1  packages/exporting/closure.py
```

27 matching lines, 8 modules, 4 packages. (That count includes comment
mentions; a code-only pass over the same tree returns the same eight
modules.) The names are `lux.applied.tscn`, `lux.quality.json` and
`lux.validation.json`, and no two readers even agree on which subset matters
-- `closure.py`'s `_METADATA_FILES` names the two JSONs, `export.py`'s
`_PRESENTATION_FILES` names the scene and one JSON, `planner.py`'s
`expected_outputs` names all three.

**THEY DO NOT FAIL ALIKE, WHICH IS THE PART THAT MATTERS.** Rename a Lux
output tomorrow and:

```
planner.py           expected_outputs misses -> the JOB fails, loudly
walk_preview.py:249  has_lux = (dest/"presentation"/"lux.applied.tscn").is_file()
                     -> reads False, and the preview renders UNLIT in silence
```

A guard that fails loudly and a check that reads False are not the same
event, and the second is the one this file keeps finding.

**AND THE PRESETS ARE COUPLED BY DISPLAY NAME.** `_preset_for` maps
`time_of_day` onto Lux preset names as strings -- "Blue Hour", "Delco Summer
Afternoon", "Gas Station Fluorescent" -- and its own comment records why that
is dangerous: Lux registers presets under DISPLAY names, and a wrong name
makes `blend_to_preset` a silent no-op, proven on hardware in the Lux visual
pass. A rename in Lux's preset library does not break this. It stops it
working.

**WHAT ACTUALLY COSTS SOMETHING.**

**THE ONE WITH MEASURED HARM -- `_preset_for` is a silent no-op, and the
check that closes it is free.**

It maps `time_of_day` onto Lux preset DISPLAY names -- "Blue Hour", "Delco
Summer Afternoon", "Gas Station Fluorescent" -- and its own comment records
that a wrong name makes `blend_to_preset` do nothing, proven on hardware in
the Lux visual pass. Nothing else in this item has already cost something.

IT WAS NOT NEARLY CLOSED BY THE ARTIFACT, AND THIS ITEM SAID IT WAS.

The claim was read off a filename and a field name rather than off the
driver. `assets/godot/run_lux_apply.gd` (6,902 B, sha256 0CC60D6D..., line
128):

```
var quality := {"preset": preset_name, "applied": applied_ok, ...}
```

`preset_name` IS the `--preset` argument. That field is the request written
straight back out. Comparing it against `_preset_for(model)` compares a
string with itself -- a check that cannot fail, proposed inside an item whose
subject is checks that cannot fail. Both sides of the table this item
published were the same string, and its agreement meant nothing:

```
requested   _preset_for(model)          ->  "Blue Hour"
"applied"   lux.quality.json["preset"]  ->  "Blue Hour"   <- the SAME string
```

**WHAT LUX ACTUALLY OFFERS, AND WHAT SHIPPED.**

`LuxRoot.get_current_preset()` returns `_current` -- `lux_root.gd:641`
(25,638 B, sha256 529f70e7...) -- and `_current` is assigned in exactly one
place, `_apply_immediate`, from the LIBRARY resource. It cannot be the
argument arriving back round.

Reading it also covers a failure the driver's existing library-dictionary
check cannot see. `apply_preset` returns early when `_initialized` is false,
assigning `active_preset` and applying nothing:

```
func apply_preset(preset: LuxPreset, blend_time: float = 0.0) -> void:
    if preset == null:
        return
    if not _initialized:
        active_preset = preset      # and applies NOTHING
        return
```

The name is in the library, so `preset_known` is true, so no issue is raised,
and the level ships with no look. The dictionary says the preset exists; only
LuxRoot says it arrived.

level_factory 0.41.0:

```
lux.quality.json     "preset"          the REQUEST, meaning unchanged
                     "preset_applied"  NEW -- get_current_preset()
lux.validation.json  LUX_PRESET_NOT_APPLIED (moderate) when they disagree
```

No Python changed. The driver already writes findings to
`lux.validation.json` and the Lux adapter's `normalize_validation` already
passes arbitrary codes through, so the new finding reaches the findings
channel without the adapter being touched. Same release, same file, same
shape of defect: `ResourceSaver.save(...)`'s return was discarded and
`applied_ok` tracked only `pack()`, so a save that failed reported
`applied: true` for a scene that was never written.

NOT YET RUN ON HARDWARE. No Godot process has produced a `preset_applied`
field yet. `tests/unit/test_lux_preset_readback.py` is a source-shape test
and says so in its own docstring -- it pins the one regression that would
restore the tautology without changing an output key, and it proves nothing
about the driver running. The next lit run is the evidence.

**AND THE FILENAME LITERALS -- third, tidiness, with one real consequence.**

```
9  packages/exporting/export.py        2  packages/pipeline/planner.py
4  adapters/lux/__init__.py            2  packages/preview/walk_preview.py
4  packages/exporting/localize.py      2  packages/service/facade.py
3  apps/cli/commands/__init__.py       1  packages/exporting/closure.py
```

27 matching lines, 8 modules, 4 packages, for `lux.applied.tscn`,
`lux.quality.json` and `lux.validation.json`. (Includes comment mentions; a
code-only pass returns the same eight modules.) No two readers agree on the
subset that matters -- `closure.py`'s `_METADATA_FILES` names the two JSONs,
`export.py`'s `_PRESENTATION_FILES` names the scene and one JSON,
`planner.py`'s `expected_outputs` names all three.

A shared constant does not decouple: a Lux rename still edits Level Factory,
in one place rather than eight, against a name stable across 0.15.x to
0.16.0. THE ONE REAL CONSEQUENCE, stated correctly: a rename would send
`walk_preview` to its fallback, and if that missed too the preview would
report `"lighting": "preview rig"` for a package that DOES carry Lux. Wrong,
but reported -- it lands in the return value and in `walk.source.json`'s
sibling fields, so it is findable rather than invisible. Worth tidying when
something else already has those files open. Not as a project.

WITHDRAWN: `walk_preview` DOES NOT SILENTLY RENDER UNLIT

The previous re-scope ranked it first, on the strength of a grep line
(`walk_preview.py:249  has_lux = ...`) read without opening the function.
Read (18,781 B, sha256 3400109C...):

```python
308:  has_lux = (dest / "presentation" / "lux.applied.tscn").is_file()
309:  if not has_lux:
311:      has_lux = "addons/lux" in (dest / level).read_text(encoding="utf-8")
314:  if has_lux:      # instance the level as-is; Lux owns the lighting
325:  else:            # build a preview RIG -- DirectionalLight3D, shadows, bias
376:  lighting = "lux (content-owned)" if has_lux else "preview rig"
393:  return {..., "lighting": lighting, ...}
```

Two-way detection with a documented fallback; no unlit render, a substituted
rig; and the choice is REPORTED in the return value. That is the opposite of
a check that finds nothing and proceeds. Its own comment records this being
fixed once already, for the failure it was just accused of: `localize_export`
strips `addons/lux` by contract, so an earlier version found nothing, added
the dev rig ON TOP of Lux's WorldEnvironment and washed out the applied look.
It now asks what `write_entry_scene` keys on, so the two cannot disagree.

The 152-fixture-lights-against-`OmniLight3D 0` incident is not this line
either. That is `walk_fixtures.gd` and the walk project not inheriting
`lux.applied.tscn` -- a different mechanism in a different place, attached
here by mistake.

THE LINE NUMBER HAD MOVED, 249 to 308, WHICH WAS THE TELL. A note citing a
line that no longer says what the note says is a note about a file that has
changed. This is the third mechanism in this item's neighbourhood published
ahead of the read, and the second inside a section arguing for reading first
-- so it is recorded here rather than quietly corrected, on the same rule
item 49 adopted: a mechanism claim cites a verified read or it does not go
in.

WHERE THE CONSTANT WOULD GO, MEASURED

Decided 2026-08-17: the Lux adapter, as the name a reader goes to. But the
import graph does not allow the literal version of that.
`adapters/ -> packages/` is pervasive (every adapter imports
`packages.adapters.sdk` and `packages.core.hashing`), while
`packages/ -> adapters/` happens in exactly ONE file --
`packages/adapters/registry.py:13-22`, which imports all ten adapters and is
a registry by design. A generic package importing one specific tool adapter
would invert that, and `adapters/lux/__init__.py` imports `packages.*` at
module level, so it risks a real cycle rather than only an ugly edge.

The shape that survives: define in `packages/adapters/sdk.py` -- the shared
surface every adapter already imports -- and RE-EXPORT from
`adapters/lux/__init__.py`, so `adapters.lux.LUX_APPLIED_SCENE` still
resolves and the adapter stays the name. Moving the definition into Lux
itself later is then a one-file change, because the eight readers already go
through one symbol.

THE INTERFACE QUESTION: DECIDED, LEAVE IT

`--art` means art AND light; `--unlit` subtracts. There is no positive
`--light`, and there will not be one. Decided 2026-08-17. The spelling is
cosmetic next to the two checks above, a positive `--light` is a breaking CLI
change touching every brief, script and doc that says `--art` today
(including `tools/run_3b_unlit.ps1`), and the planner's fourth layer is real
whatever the flag calls it. Recorded as decided so it stops being reopened.

CHASED AND CLOSED: "A VARIED LOT IS CURRENTLY UNLIT"

`level_factory/docs/extracted/site.md:1137-1145` carries, as a known
consequence, that a varied lot never gets lit at all:

> "**A varied lot is currently UNLIT** regardless: `lux_apply` lights
> `presentation/site.tscn`, the mission shell, which a varied lot does not
> place."  -- `WALKABLE_SITE.md:124-126`

If current that would enlarge this item considerably -- it would mean `--art`
on a multi-building mission has been shipping unlit packages by accident
rather than by flag. It is NOT current. From
`apps/cli/commands/__init__.py` (126,865 B, sha256 20188C0F...), lines
637-653:

```python
themed_job  = _dep(job, "themed_site_assemble")
compose_job = _dep(job, "presentation_compose")
if themed_job:
    # The themed SITE: Lot's assembly of the composed building at
    # the candidate's own placements. Lighting the composed building
    # instead put one LuxRoot over one building and called it a
    # level (roadmap 29/34).
    composed_scene = _latest_output(jobs_dir / themed_job, "site.tscn")
elif compose_job:
    composed_scene = _latest_output(jobs_dir / compose_job,
                                    "presentation/site.tscn")
```

`lux_apply` lights the ASSEMBLED SITE whenever `themed_site_assemble` is
planned, which is whenever the art layer runs; `presentation/site.tscn` is
the `elif`. And the adapter hardcodes nothing -- `adapters/lux/__init__.py:53`
reads `job_spec["composed_scene"]` and refuses without it -- so the scene
targeting was never Lux's to get wrong, which is worth knowing for this
item's own question about where the seam belongs.

**BOTH SOURCES THAT SECTION RESTS ON ARE STALE.** `WALKABLE_SITE.md:124-126`
predates `themed_site_assemble`, and its own "Related open work" lists the
`--render` split as the thing that would "light the varied lot". The other,
`VARIED_THEMED_LOT.md:8-11` -- "`run <mission> --art` -> ONE building repeated
N times" -- predates one-compose-per-archetype, which
`tests/test_presentation_lot.py` now pins with `len(cmds) == 1 + len(lot)`.
`WALKABLE_SITE.md` has been marked superseded in place rather than edited
away. `site.md` is generated into `docs/extracted/` and is left alone; it was
honest about itself -- "the known consequence is documented rather than
measured" -- and that caveat is the only reason this was catchable instead of
believed.

MEASURED, AND ONLY HALF ANSWERED

Re-exported 2026-08-17 from the cached `lot-demo-ws`, both modes, no Blender
or Godot needed. All three predictions held. `lot/` holds FIVE subdirectories
-- item 49's fix correctly declined to touch the varied shape, which is the
condition `_assembly_building_dir` was written to fail. `resource_manifest.json`
is gone (0.40.0). Closure `ok: true`, 0 missing, 0 misrooted, 0 unresolved
relative, in `portable-godot`, `art-unlit` and `pure-shell` alike:

```
LF_lot_demo_001.portable-godot   resource_count 36   lot/ 5
LF_lot_demo_001.art-unlit        resource_count  7   lot/ 5
LF_lot_demo_001.pure-shell       resource_count  2   lot/ 0
```

The 29 between the first two is the localized Lux runtime -- `resource_count`
counts only `.tscn/.tres/.gd/.gdshader`, so it is the scripted part of the
"33 Lux files dropped and nothing else" measured for 0.36.0. The lit varied
package ships Lux's runtime; the unlit one does not.

**AND THE VARIED LOT IS LIT.** The claim above is not merely superseded by a
code branch, it is contradicted by the artifact:

```
presentation/lux.applied.tscn   141,265 B
presentation/lux.quality.json   {"applied": true,
                                 "fixture_lights": 136,
                                 "fixture_msg": "Spawned 136 fixture light(s)
                                                 from 136 marker(s)",
                                 "preset": "Blue Hour"}
```

`lux_apply` ran on the five-building assembly, spawned 136 lights from 136
markers and applied the preset. Incidentally that exercises this item's own
`_preset_for` coupling and it HELD: the brief says `time_of_day: night`,
`_preset_for` returns `"Blue Hour"`, Lux reports `"Blue Hour"`. Fragile by
construction, not broken today.

WHAT IS STILL NOT ANSWERED, AND IT IS NOW ONE STEP

Lux's own output says it: `"note": "previews need a render context"`. 136 is
what was SPAWNED in a headless run. It is not a count of what RENDERS, and
those are the two numbers `WALKABLE_SITE.md:115-120` already recorded
disagreeing -- `lux.quality.json` at 152 fixture lights while the preview ran
`OmniLight3D 0`, with the note *"a preview that is lit differently from the
level is worse than no preview, because it gets believed."*

So `lux_apply` demonstrably reaches the assembly's markers. Whether those
lights survive to a frame needs the `portable-godot` folder opened in a clean
Godot project WITH a render context, and nothing substitutes for that -- not
another export, not a bigger scan. It is the one remaining step and it is
manual.

ONE CAVEAT ON THE NUMBER. `lux.quality.json` is stamped 2026-08-15 and copied
through unchanged; `lux.applied.tscn` is stamped today because `localize`
rewrote its `res://` paths on export. 136 is therefore a CACHED figure from
the last real `lux_apply`, correct for unchanged inputs and not a fresh
measurement.

### Not to be worked on
Under the boundary at the top of this file, these are downstream's model of
combat and none of them make the levels better: the crew bot's target memory or
threat response; the enemy firing at t = 0.0 despite a 0.25-0.5 s reaction
delay; anything tuned against survival time, engagement distance, kill counts or
opening timing. Laser Tag findings of that shape are information for a human at
candidate selection, not work items.

### Smaller, carried

**The export closure scan reads what it counts -- asked, and answered.**
Raised on 2026-08-16 because `lot/shell/site.tscn` carries 34
`res://lot/shell/...` references while the scan reported `resource_count: 3`
and `missing_resource_count: 0`, and those 34 appeared in none of its
numbers. Read out of `closure.py` (12,146 B, sha256 1467E73D...): the scan
does NOT walk a reference graph from the entry. It globs every file whose
suffix is in `_SCANNED_SUFFIXES`, reads each one's text, and checks every
`res://` it finds against `present` -- a set built from `rglob("*")` over the
whole package, GLBs included. So `lot/shell/site.tscn` was opened and all 34
were checked. `resource_count` is a count of scene and script FILES present,
not of resources reached; 3 is `mission.tscn`, `site.tscn` and
`lot/shell/site.tscn`. `ok: true` does mean the art resolves.

Recorded rather than deleted for two reasons. The obvious test does NOT work
-- renaming a GLB inside the export directory and re-exporting proves
nothing, because `export_mission` does `shutil.rmtree(export_dir)` and
rebuilds from source before scanning, so the file is back before anybody
looks; that was tried on 2026-08-16 and the rename-back failed because the
rebuild had already replaced it. And the scan has been wrong about precisely
this before: its own comment records `any(pr.endswith(rel) for pr in
present)` certifying lot_demo_001 at `ok: true, 0 missing` while five
building scenes each dangled 33 references, "floors and a staircase in an
empty sky". That is roadmap 49's defect one layer up, which is why
`misrooted_resource_count` is a separate counter and why it reading 0 is
worth as much as the missing count reading 0.

factory-v1.25.0's description says this was UNMEASURED. It was, at the moment
that set was certified. It is measured now, and the next certification can
say so; a pushed tag does not get rewritten to look better than it was.

**`probe_unlit_ab.py`'s manifest section reads nothing and reports `ok` for
it.** Run against the 3b packages it printed `profile=None layers=None
package_dir=None archive=None` for both, then `ok the unlit manifest does not
claim the light layer` -- a pass derived from a file it never opened. It looks
for `LF_MANIFEST.json`, which only an ARCHIVE export writes; a `--format
folder` export has no such file. Three of its four LOOK lines come from the
same absence. This is the defect the probe was written to find, in the probe,
and its manifest output should not be read until it either locates the folder
export's manifest or says out loud that it found none.

**`MIGRATIONS.md` indexes one run rather than a directory.** `tidy_migrations.ps1`
builds the table from the files *that invocation* moved, so when `tidy_tools.ps1`
filed five scripts into `migrations/2026-08/` and a later `tidy_migrations` run
moved two more, the index was rewritten to list two and the five vanished from
it. The directory holds seven. Generate the table by walking
`migrations/<bucket>/` and it is correct no matter which script filed something,
and self-healing when one skips the index entirely. Same shape as everything
else in this file: an enumeration of one run standing in for a description of a
set.

**`archive_scratch.ps1` is superseded and its list has rotted.** It enumerates 23
filenames, three of which -- `lf_patch.ps1`, `guardrail_regate.ps1`,
`reconcile_version.ps1` -- it would have archived as one-shots. It was right
about all three, and only its `git ls-files` tracked-check stopped it. Those
three are now in `migrations/2026-08/` where they belong.
`tidy_migrations.ps1` does the same job by rule. Retiring one of the two is a
decision rather than a tidy, so both are still there.

**`ps1.gdshader` exists twice**, at `patina/godot/addon/patina/ps1.gdshader` and
`patina/godot/shaders/ps1.gdshader`, identical 2,688 bytes. The addon README
says the copy inside the addon is the one that travels. Two copies of a shader
is the same drift risk as two copies of a rule, and item 20 may retire both
anyway.

**`cater.py` writes a `project.godot` with no main scene.** `package.py
--walkable` sets `run/main_scene` and says so; cater writes "minimal
project.godot" without one, so F5 in a cater-built project fails with "no main
scene defined" and only F6 on the open scene works. Two writers of the same file
disagreeing about what a complete one contains. One line in cater.


**Findings have nowhere to live but the run that found them.** `index.sqlite`
has tables for jobs, artifacts, missions and meta, and none for findings, so
nothing can answer "what did the last run say?" without re-running it. And
`cmd_run` writes `.level_factory/validation/<mission>.json` unconditionally, so
a run that evaluates nothing still overwrites what the last run found — it
should write only when the run actually evaluated something. Neither caused item
5; together they turned it from a wrong number into a destroyed record, which is
why it survived long enough to need an investigation.

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

`gdcheck.py` flags four files and is wrong on all four, which makes it a
guardrail heading for the off switch. Two separate defects, both text
heuristics standing in for tokenising. **The bracket counter strips comments
before masking strings** (`ln.split("#")[0]` runs inside the `re.sub`, so it is
evaluated first), and a `#` inside a string literal then eats the rest of the
line: `Color.html(cosmetic.get("color", "#ffffff"))` truncates to
`return Color.html(cosmetic.get("` and scores +2, which is exactly the net
LT_Cosmetic.gd reports; `"%s (#%d)" % [...]` scores +1, exactly LT_GhostPlayer's.
Mask strings first, then strip comments. **The implicit-concatenation check
tests `prev.endswith('"')` without stripping trailing comments**, so a dict
whose values carry `# e.g. "res://..."` comments flags every following line
(deli_counter_postimport.gd 37-38), and it has no notion that a line legally
begins with a string -- a `match` on string patterns trips it on every arm
(LT_DebugLaser.gd 180, 182). gdparse accepted all four files, and gdcheck's own
docstring claims trap 1 is a syntax error gdparse sees; that contradiction was
the tell.

Retired from this list because they are fixed: provenance recursion (was
eleven deep, reached seventeen and killed a run, now filtered at the scheduler);
`cater.needs_build` comparing mtimes (now a content digest with a
`<glb>.spec.sha256` stamp); the non-portable absolute `ext_resource` (still
emitted, but promoted to item 4 rather than carried, because it violates the
standalone contract rather than being untidy).

*STATUS: CLOSED 2026-08-24 -- CENSUS PASS, WALK CLEAN, CAP DELETED. The
closing run (census #8, `walk.tscn` on the recomposed lot_demo_001 preview,
engine 4.7-stable): 5,055 visible meshes, ZERO over the engine default of 8,
worst exactly 8 (`b1/GreyboxBase/slab_1_t2_5`), 128 positional lights, zero
twins, ranges 3.6-6.35 m. The human A/B walk at per-object 8 vs 40 saw no
difference -- no brightness steps at tile boundaries, no thin lines, floors
lit ("no more of that weird lines"). Getting the last 14 meshes under budget
took the census growing MARGIN FORENSICS (per offender: each claimant's
range minus its distance to the mesh, sorted slimmest first, so a range trim
is priced by measurement instead of guessed -- plus a warm/cool color tag,
because the pendant is deliberately the fluorescent rig in a costume and
paths cannot tell them apart) and two lux releases the forensics priced:
0.23.0 (fluorescent range drop+1.0, clamp 4.0..7.5, the first census with
the drop chain alive end to end) and 0.24.0 (drop+0.75, shedding the b0
claimants that bound with 0.17 m to spare). The drop chain itself was dead
until a probe read the RUNNING tree: Godot imports glTF node extras as ONE
metadata entry named `extras` holding the whole dictionary, so
`get_meta("lux_drop")` returned null in every build since zoo 0.30 and the
name-parse fallback masked it -- lux 0.22.0 (`marker_payload`) opened the
box. En route the same instrument caught and killed: every fixture light
existing TWICE (lux 0.17.0 rig-sweep dedup), the eleven-bulb chandelier row
a 275 m^2 suite got from area/25 alone (DC 0.99.1 pendant guardrails), and
plate-bevel V-grooves masquerading as budget seams (zoo 0.50.0 unbeveled
plates). Deleted in level_factory 0.49.0: `PER_OBJECT_CEILING`,
`per_object_cap()`, and the per-object block in `rendering_block`; the
absence is pinned by `test_no_package_writes_a_per_object_cap` exactly as
hard as the value used to be. Two observations were recorded here as
unresolved -- mesh count 4,679 -> 5,055 between the 02:27 and 11:10 builds,
and b1's slab tile names shifting (a `t2_5` where #7 read `t2_3`/`t3_3`) --
and the first attribution written (greybox-vs-themed standing shells) was
WRONG. RESOLVED 2026-08-24, found in the repo after the closure was drafted:
Deli Counter 0.100.0 shipped between the two builds -- `SLAB_TILE` 8.0 ->
5.0 sized from THIS kit's lamp density, and parapet visuals routed through
`slab_tiles` (the one greybox visual that had escaped the tile law) -- so
the deltas are finer tiling, and the GEOMETRY, not the 0.24.0 range trim
alone, is what cleared b1's tiles and the 52 m parapet. The census verdict
stands either way; the credit line changes. Provenance settled by git the
same day: the 0.100.0 work sat UNCOMMITTED on top of v0.99.1 -- authored by
a second, since-closed session working the same tree (seven files written
inside two seconds, no patch script, census-#7-informed changelog) -- and
was adopted into history as v0.100.0 with the DC suite as the gate. The
process lesson (one writer per repo at a time; commit before handing a repo
across sessions) is now a rail in USING_THE_FACTORY.md. The global cap's
declaration-vs-running-tree gap stays item 56; the first-load hitch stays
open below. Prior state (2026-08-23): OPEN -- SPLIT IMPLEMENTED, AWAITING
THE CLOSING CENSUS.
Both sources of room-spanning meshes now tile to light-budget size. Zoo 0.49.0
cuts every plate VISUAL into <=8 m tiles (`core/arch.tile_parts`, wired in
`build_slab`; collision still built from the UNTILED plate -- proven on a
52 x 32 m roof with the bank-branch ladder void: 43 tiles, largest edge
7.429 m, the same 4 collision boxes as before, ladder column open). Deli
Counter 0.96.0 tiles the full-footprint `slab_<n>` visuals the stripped base
keeps (pvp_station_ref, 34 x 26 m x 4 storeys: 80 tiles at 6.8 x 6.5 m, four
trimesh collision slabs byte-unchanged), teaches `_slab_holes_cut` to cut
EVERY intersecting tile instead of the first name match, and switches
`roof_covered_nodes` to containment so a themed roof strips the whole tile
set instead of z-fighting it. The closing instrument exists now too:
`tools/mesh_light_census.py` + `.gd` walk the RUNNING tree and count, per
visible mesh, the visible omni/spot lights whose range reaches its world
AABB -- built because the 111-over-8 numbers below come from module FILENAMES
and can open this item but not close it. THE BEFORE NUMBER IS NOW MEASURED
(2026-08-23, `walk.tscn` on the shipped lot_demo_001 preview, engine
4.7-stable, 272 positional lights visible): 3,016 visible meshes, 804 over 8,
201 over 16, 51 over 32, worst 72 on `b1/GreyboxBase/slab_0` -- the estimate
was off by a factor of seven because it measured files, not the tree. TWO
FINDINGS THE ESTIMATE COULD NOT SEE. (1) Lot's ground routes are offenders
too: `path_0/mesh` at 65 x 8 m sees 58 lights, `path_1` 52, `path_3` 44 --
the tile law has to reach lot's path meshes or zero-over-8 is unreachable.
(2) The census counted 272 visible positional lights in a project whose
`max_renderable_lights` is 136: `count_package_lights` globs .tscn TEXT, so
a light rig instanced N times counts once and a runtime-spawned fixture
light counts zero -- the global cap is sitting at HALF the real light
population, which is the areas-stay-dark defect that cap exists to prevent,
live today and hidden. That needs its own item; it is not this one's to fix.
SINCE THEN, the census earned its keep three more times: lot 0.49.0 tiled
the paths/ground/roads it caught (58 lights on one 65 m path mesh); its
light forensics flushed lux 0.17.0 (every fixture light existed TWICE --
bake-saved and runtime-rebuilt, 272 visible against 136 authored, all
within 10 cm of a twin) and priced the flat range: 8.0 claimed budget slots
through walls (walked at the engine default as a hard brightness grid),
the 4.5 trim left tall halls with lit ceilings over PITCH-BLACK floors
(attenuation reaches zero at the range; energy cannot light what range
does not reach). So DC 0.97.0 stamps each ceiling anchor's DROP to its own
floor and lux 0.19.0 derives range = clamp(drop + 1.5, 4.5, 8.0). Census
after tiling + dedup + trim: worst 23, zero over 32, 308 over 8 and
falling with the derived ranges. REMAINS: rebuild the shell library
(lights.json now carries drop), recompose, census reads zero over the
engine default of 8, the walk at default 8 shows no set-boundary grid,
then delete `PER_OBJECT_CEILING = 40` from
`packages/core/godot_project.py` (the deletion and its test updates are
drafted and held).
The first-load frame hitch stays open and unmeasured. Prior state
(2026-08-18): MEASURED AND MITIGATED, NOT FIXED -- two derived engine caps
paying for the plates; 111 of 920 meshes over 8, 39 over 16, one over 32,
every offender a building-wide roof or floor/ceiling plate*

**54. One mesh spans a whole room, and two light caps are paying for it.**
Raised 2026-08-18, walking `LF_lot_demo_001.portable-godot` with 136 fixture
lights in it. Three symptoms arrived in sequence and only the third named the
cause: lights blinking as the camera moved, then areas that stayed dark
permanently, then -- standing still -- a hard brightness step across a floor
where two slabs met.

**TWO LIMITS, AND THEY FAIL DIFFERENTLY.** GL Compatibility carries both, and
conflating them cost two releases:

```
rendering/limits/opengl/max_renderable_lights   default  32   a GLOBAL budget
rendering/limits/opengl/max_lights_per_object   default   8   a PER-MESH budget
```

Above the global cap lights are not drawn AT ALL, which is why areas stayed
dark permanently rather than flickering -- 136 lights against a budget of 32.
Above the per-mesh cap a single mesh drops lights, which on a building-sized
slab shows up standing still, as a seam.

**THE MEASUREMENT.** Counting lights whose range reaches each mesh's bounding
box, across all five buildings of the shipped package:

```
building              meshes   >8   >16  >32  worst  worst mesh
mansion_a02              163   26    11    0     26  roof_footprint
pvp_station_ref          240   49    15    1     36  roof_footprint
large_warehouse_a01      117    3     1    0     17  roof_footprint
arena_a03                227   10     3    0     26  roof_footprint
strip_club_a03           173   23     9    0     25  roof_footprint
---------------------------------------------------------------
across all five          920  111    39    1
```

Every offender is a roof or floor/ceiling plate 34-52 m across. Wall segments
sit at 6 or below. `arena_a03`'s roof is `roof_rockay_04_w5200_d3200` -- 52 m
by 32 m, one mesh, one light budget, competing with `wall_rockay_04_w200` at
2 m for the same slots. When the big one loses, a whole room goes dark at once.

Caveat on those numbers, stated because they will be quoted: extents come from
the `_w`/`_d` in the module filenames, height is assumed at +/-3 m, and
per-module rotation is ignored. They are indicative. The one that is not
indicative is the single mesh over 32, because it matched the reported symptom
exactly -- "still blink a bit, or just turn off in certain rooms" at a cap of
32, with exactly one mesh above it.

**WHAT WAS RUN ON HARDWARE**, in the walk preview, each a separate walk of the
same route:

```
per-object   global    result
        8        32    heavy blinking
       64        32    still blinks, areas stay dark
        8       256    clean, and the load-in hitch is SMALLER
       64       256    clean
       40       256    clean            <- shipped
```

The global cap is what stopped the blinking and the dead areas. The per-object
cap is what stopped the seam, which only appears when the camera is still and
was therefore missed entirely by the runs above it.

**TWO MECHANISMS WERE PUBLISHED WRONG BEFORE THE THIRD WAS ISOLATED.** 0.43.0
wrote the per-object cap and named it as the cause of the blinking; it was not,
and the engine said so when finally asked directly (`max_renderable_lights
exists=true value=32`). 0.43.2 then REMOVED the per-object cap, having tested
only for blinking -- and reintroduced the seam. 0.43.3 tested the two symptoms
separately and shipped both caps, each derived from the package rather than
picked to make something stop.

**WHAT IS ACTUALLY WRONG, AND IT IS NOT A SETTING.**

A single mesh spanning a whole room is the reason either cap is needed. Split
those plates to room-sized pieces and every one of the 111 offenders drops
inside the engine's own default of 8; the per-object cap becomes unnecessary
and its shader cost goes with it. Frustum culling improves for free, because a
52 x 32 m mesh is either fully in frame or fully drawn anyway.

**AND THIS IS ITEM 35's QUESTION FROM THE OTHER SIDE.** Item 41 measured 1389
`Cover_panel_field` nodes and called excessive fragmentation the defect. This
item measures meshes too LARGE to light correctly. Both are the same missing
decision -- what size should a mesh be -- approached from opposite ends, and
neither can be settled by a rule that only says "fewer" or "more".

**THE LOAD-IN HITCH -- OPEN, AND A HYPOTHESIS ONLY.** A frame hitch on first
load was reported from the walk, and it got smaller when 0.43.2 dropped the
per-object cap from 64 to the engine default. That is consistent with shader
variant compilation on first draw -- the per-object light count sizes the
shader's light loop, so more variants to compile -- but NOTHING HAS MEASURED
IT. No frame timing was captured, no variant count, no before-and-after on the
same route. It is recorded here as an observation with a plausible cause, and
it should not be quoted as a finding until somebody times it. It matters
because this layer has to stay cheap while the game grows into it.

**WHAT WOULD CLOSE THIS.** Room-sized floor, ceiling and roof meshes, measured
the same way -- re-run the per-mesh light census and show zero meshes over the
engine default of 8. At that point `packages/core/godot_project.py` stops
writing the per-object cap because no package needs it, and the constant
`PER_OBJECT_CEILING = 40` and its comment go with it.

*STATUS: OPEN 2026-08-18 -- MEASURED. Four `AreaPanel_Surface` nodes ship in
`lot_demo_001`, each a 1.4 x 1.4 m single-sided `QuadMesh` at y 2.5 under
`LuxFixtureLights`, spawned by `LuxFixtureSpawner` as the emitter face of an
area-light rig. The LIGHT works. The SURFACE is blank, so it reads in-level as
a white card -- photographed 2.9 m from a doorway on `arena_a03`. One of the
four rigs is named `Spawned_sign`, which is what the fixture type is; the other
three are `@Node3D@27`, `@Node3D@71`, `@Node3D@99` -- engine-generated names,
so nothing downstream can select them. NOT CLAIMED HERE: whether a blank
emitter is a defect or simply unfinished content. That is an art decision and
this item does not make it*

**55. The level ships sign fixtures with no sign art, and three of four cannot
be addressed.**
Raised 2026-08-18 from a walk of `LF_lot_demo_001.portable-godot`: a white
rectangle beside a doorway, circled in a screenshot, which no automated check
had ever mentioned.

**WHAT IT IS.** Four nodes, in the whole five-building lot:

```
@Node3D@27/AreaPanel_Surface     world (  -1.4, 2.5,  80.2)
@Node3D@71/AreaPanel_Surface     world (  40.8, 2.5, -17.0)   <- the one photographed
@Node3D@99/AreaPanel_Surface     world (  73.2, 2.5, -84.2)
Spawned_sign/AreaPanel_Surface   world ( -75.2, 2.5,  63.6)
```

Each is a `QuadMesh`, `size = Vector2(1.4, 1.4)`, carrying a material. They are
the emitter faces of Lux area-light rigs: Zoo exports a `LuxEmit_*` marker,
`LuxFixtureSpawner` builds the rig, and the rig includes a visible panel
because a real luminaire has one. The light is correct. Nothing ever puts
artwork on the panel, so it renders as a blank 1.4 m card at head height. The
walker's own word for it was "signs", before any evidence existed -- and the
fixture type agrees.

**WHY EVERY FILE-LEVEL INSTRUMENT MISSED IT, AND WAS RIGHT TO.** The panel is
created at RUNTIME by the spawner and packed into `lux.applied.tscn`. It is in
no GLB and is not authored in any `site.tscn`. Five explanations were published
and refuted in order, each by a measurement:

```
broken glass material      refuted: nearest window is 7.41 m away, one storey up
a degenerate plane         refuted: `glb_nodes --flat`, 150 GLBs, 0 degenerate
the doorway module         refuted: it holds 4 nodes -- 2 jambs, a header, a collider
untextured jambs/header    refuted: `glb_materials`, all 3 visible prims textured
a rendered collision mesh  refuted: 0 visible surfaces with no material, 2093
                                    StaticBody3D -- `-colonly` converts correctly
```

The instrument that found it was reading `lux.applied.tscn`'s own node list --
the only place the thing exists. `glb_nodes.py`'s docstring already framed this
exact question ("what is that white square I can only see from one side?") and
its `--flat` answer said so: "Whatever you saw is not in this file -- try the
site." A `QuadMesh` is single-sided, which is why that phrasing fits.

**THE NAMING GAP, WHICH IS THE PART THAT COSTS SOMETHING LATER.** Three of the
four rigs are `@Node3D@<n>` -- names the engine generated because the spawner
did not set one. Only `Spawned_sign` is addressable. Anything that later wants
to find these panels, gate them, texture them or count them has nothing stable
to select on, and the numbers shift every time the spawn order does.

**WHAT THIS ITEM DOES NOT DECIDE.** Whether a blank emitter panel is a defect.
An unlit sign face awaiting artwork is a perfectly normal state for content
that is not finished, and this pipeline's job is to place the fixture, not to
draw the sign. What is NOT normal is that nothing anywhere says these panels
exist, so a level ships with four blank white cards at eye height and every
gate reports clean.

**WHAT WOULD CLOSE THIS.** Either artwork on the panel, or a stated decision
that the emitter face is invisible by default and Zoo's marker carries the
sign texture when there is one -- plus, in both cases, a name from the spawner
so the four are addressable, and a count in the validation output so a level
with unfinished sign faces says so instead of being found by somebody walking
past one.

*STATUS: OPEN 2026-08-23 -- MEASURED at discovery, unworked. Found by item
54's closing instrument on its first honest run and recorded here the same
day, because "the roadmap already knew" (item 39's epitaph) is only true of
findings that get written down*

**56. The global light budget is derived from scene text, and the running
level has twice as many lights as the number it was given.**
Raised 2026-08-23 by `tools/mesh_light_census.py` on `lot_demo_001`'s walk
preview: the census counted **272 visible positional lights** in a running
tree whose `project.godot` says `max_renderable_lights=136`. GL Compatibility
does not degrade above that cap -- lights past it are simply not drawn -- so
roughly half this package's lights are culled somewhere every frame, with
which half winning decided by the camera. That is the areas-stay-dark /
blinking defect 0.43.x measured and fixed, alive again underneath the fix,
and invisible to every file-level instrument for the same reason twice over.

**WHY THE NUMBER IS WRONG.** `packages/core/godot_project.py::
count_package_lights` globs every `.tscn` under the package and counts
`type="OmniLight3D|SpotLight3D|DirectionalLight3D"` DECLARATIONS in the text.
Two mechanisms make the running tree bigger than the text: a light rig scene
instanced N times contributes N runtime lights and ONE declaration, and
`LuxFixtureSpawner` builds its area-light rigs at RUNTIME from `LuxEmit_*`
markers, contributing lights that exist in no `.tscn` at all (item 55
documents the same spawner's panels evading every file instrument). The
docstring's claim -- "a package cannot render more lights than it contains"
-- is true of the package and false of the tree, and the cap is written
against the package.

**WHAT WOULD CLOSE THIS.** Derive the global cap from the RUNNING tree's
light population (the census payload already measures exactly this number),
or make it instance- and spawner-aware at derivation time -- and either way,
a gate that compares the shipped cap against a runtime count so the two can
never drift silently again. Not folded into item 54, whose subject is meshes
over the PER-OBJECT budget; this is the GLOBAL budget lying about the
population, and its fix lives in level_factory + lux, not in the geometry.
NOTE 2026-08-23: lux 0.17.0 removed the x2 itself (every fixture light
existed twice -- bake-saved AND runtime-rebuilt), so the running tree now
matches the written cap on lot_demo_001. The DERIVATION is still text-based
and still counts an instanced rig once and a spawned light zero times; this
item stays open for the class, with its live instance dead.

*STATUS: OPEN 2026-08-23 -- FRAMED, UNWORKED. Raised from the 2026-08-23
walks of the tiled, deduped, trimmed lot_demo_001, where the remaining
reads-as-tiles feeling was no longer any single defect but the absence of a
grammar. Item 58 below is the first Critical-class instance filed under it*

**57. Asset boundaries are implementation details; architectural boundaries
are what the player should see.**
Raised 2026-08-23. The walk that followed item 54's tiling read as more
cohesive under the light caps and STILL read as modular in places, and the
reasons sort cleanly under one principle: a modular seam should either
disappear, or become an intentional architectural feature. The house already
runs much of this playbook -- `relief_parts` puts a pier at every 2 m wall
module boundary (seams AS architecture, carved inward because the 546-cover
fiasco banned proud-of-the-wall masks); openings can never be bisected
because a window IS a module; floor/ceiling materials break at room
boundaries; the shot bot's 1 mm-flip jitter metric is a close-range seam
instrument; and item 54's plate tiles are engineered invisible (coplanar,
flat identical normals, UVs position-projected in module space so the
pattern flows across tile cuts). What it does NOT have, measured against
that principle:

- **Between-module texture continuity.** `cube_project_uv` projects in
  module-local space and every instance of `wall_rockay_01_w200` is the same
  GLB, so a facade samples the identical texture patch every 2 m --
  `[ABCABC][ABCABC]`, the classic giveaway, with per-part wear jitter baked
  into the shared GLB so the WEAR repeats too. The piers give each boundary
  a cover story; the repetition inside each bay is what still reads. The fix
  direction (per-instance `uv_offset` exists in the signature already, or
  building-space projection) trades directly against the kit economy of one
  module instanced N times -- that trade is this item's core decision, and
  it is item 41/35's "what size should a mesh be" wearing a texture.
- **Weathering in building space.** Zoo wear is per-part and rides the
  shared GLB; real grime responds to the building (runoff, ground splash),
  not to asset bounds. Patina reads `surface_roles` and is the right layer;
  how far its wear actually crosses module boundaries is UNGROUNDED -- read
  before claiming.
- **An edge vocabulary and a resolver.** Slots declare dims/material/style
  but not what their EDGES mean (CONTINUOUS_BRICK vs BAY_BOUNDARY), so
  nothing can warn "these two modules meet mid-surface with no transition"
  or insert a separator from a pool (column, trim, downpipe, material
  band). `wallEnd` is a scaled end-cap, not a corner family
  (Corner_90_Inside / Outside / material-specific) -- see item 58 for what
  that costs today.
- **A mid-distance instrument.** The 1 mm-flip gate sees cracks; nothing
  measures "reads as tiles from 40 m" (silhouette fragmentation, bay-rhythm
  periodicity, per-module color blocking). Buildable on the godot_probe
  pattern: fixed-distance station shots plus a repetition metric.

**WHAT WOULD CLOSE THIS.** Not one patch: an adopted grammar. Each shipped
piece counts -- edge metadata in the slots contract, a corner module family,
one demonstrated continuity mechanism (building-space UV or per-instance
offset) with its cost measured against the instancing economy, weathering
moved to building space, and the mid-distance instrument -- with the walk as
the judge each time.

*STATUS: NARROWED 2026-08-25 -- FIXED AND VERIFIED ON REAL GEOMETRY. Deli
Counter 0.102.0 insets each exterior run to the perpendicular wall's inner
face and seats a `wallEnd` unit post at each corner, N/S owning the turn;
0.102.1 fixed the one regression that shipped with it. Rebuilt through
Blender 5.1.1 across the whole library and re-measured by the gate:
**ENV_CORNER_OPEN 988 -> 0 over 124 buildings**, with ENV_RUN_GAP 1 (the
pre-existing `auto_shop_a02` sliver, whose whole span is under the threshold
and so has no module to absorb into), ENV_PLACEMENT_DRIFT 0,
ENV_SHAPE_UNRECOGNISED 0 -- every figure landing on the number predicted
before the rebuild. Cost in the kit: ZERO new modules. The post is
`size_mod="end"`, so `slot_typename` returns `wallEnd`, the one species DC
scales, and Zoo's `exact = typ != "wallEnd"` gives it unit treatment with no
change in that repo and no new stem; an exact-fit corner would have been 18
modules per theme per style. THE GATE CAUGHT THE REGRESSION ITS OWN CHANGE
INTRODUCED, which is the argument for having built it first: the corner
change alone took ENV_RUN_GAP 1 -> 2, one new 0.050 m hole beside a window in
`strip_retail_a01`. Instrumenting the builder (`patch_dc_span_probe.py`,
applied and reverted byte-for-byte) found `_wall_span` computing a span's
remainder TWICE by two algebraically identical expressions that are not
identical in floating point -- `L - n*M` read 0.05000000000000071, too big to
absorb, while `b - x` read 0.04999999999999982, too small to emit, so the
5 cm was neither absorbed nor emitted. A threshold asked of two spellings of
one number has a blind window either side of it. 0.102.1 computes it once.
Worth recording that this mechanism was hypothesised, REFUTED against a
reconstruction from the manifest, and then confirmed on the builder's own
floats: the reconstruction assumed the span began after the previous module
(a=0.15) when it begins at the run's inset edge (a=-9.85) across six modules,
and the manifest's 4-decimal rounding could not have settled it either way.
THE GATE IS WIRED AND ENV_CORNER_OPEN HAS GRADUATED, same day and by item
59's rule -- a code goes WARN -> FAIL when the shipped library reads ZERO for
it, never before, because a gate switched on over a red library is one
everyone learns to pass with a flag. `envelope_continuity.py` now carries a
`SEVERITY` table with the measured count beside every entry, and is
registered in `tools/check_all.py` as the `envelope` check, second in the
order because it is pure JSON and cheap. It honours that runner's three-state
contract: 0 checked-and-clean, 1 checked-and-found, 2 COULD NOT CHECK. FAIL
today: `ENV_CORNER_OPEN` (0), `ENV_PLACEMENT_DRIFT` (0),
`ENV_SHAPE_UNRECOGNISED` (0). WARN until they reach zero: `ENV_RUN_GAP` (1,
auto_shop_a02) and `ENV_DIMS_FRAME_CANONICAL` (349, item 63); `--strict`
promotes every WARN to FAIL and is how the cost of the next graduation gets
priced before anyone commits to it. One distinction the wiring forced and
that is worth keeping: a manifest with NO exterior walls is not a refusal.
Thirteen of the 137 carry 1-5 slots and no `wall` field -- mission and site
stubs, not buildings -- and folding them into "could not check" would have
left the runner permanently amber, which is an amber nobody reads. They are
listed and skipped; only a manifest this cannot MEASURE (unknown version,
unknown frame, malformed slot) returns 2. All three states verified end to
end through `check_all.py`: clean library exit 0, a library with open corners
exit 1, a missing build directory exit 2. FULL GATE GREEN 2026-08-25 after the sites were rebuilt: gdscript, envelope,
freshness, stairs and steps all clean -- `stairs` and `steps` being the two
worth watching, since they were green against sites twenty DC versions old
and stayed green reading geometry that jumped all twenty at once. The
staleness that surfaced on the way is item 65. WHAT REMAINS: the FOUNDING
SIGHTING is
still not tied to this defect (the overlay's 21.63 m ray lands on
`ext_0_N_seg8`'s span, ~19 m from the nearest corner) and should be tied or
explicitly retired rather than left implying it was. Certification is also
owed: DC moved 0.101.2 -> 0.102.1 and no `factory-v` entry has been cut.
PRIOR STATUS, kept because the measurement in it is what the fix was built
on: LOCATED IN DATA, AND IT IS THE WHOLE LIBRARY.
Measured read-only against the census-#8 `lot_demo_001` walk preview and,
independently, against Deli Counter's own `build/<id>.slots.json`; then swept
over all 137 slot manifests by the gate this item asked for
(`tools/envelope_continuity.py`, new). Every exterior run terminates EXACTLY
on the perpendicular wall's centreline -- 0.000 m past it, no exceptions --
leaving a re-entrant notch of half the wall thickness on each side, full
storey height, at every outside corner, open on two faces and open to the sky.
LIBRARY CENSUS: 124 buildings read, ZERO with no finding, 988 open corners.
The notch tracks the thickness exactly and nothing else -- 0.150 m on the 0.30
walls (812 corners), 0.175 on the 0.35 walls (152), 0.125 on the 0.25 walls
(24) -- which is the same rule stated three times and rules out any reading
where the number is a tolerance or a rounding. The gate also read the composed
scenes for the five `lot_demo_001` buildings and found ZERO placement drift
against their slots, so the scene realizes the request exactly and the corner
is missing from the request. The ROOFS use the
same convention (`roof_rockay_01_w3400_d2400` spans centreline to centreline,
`roof_rockay_04_w5200_d3200` likewise), so the outer 0.15 m of the whole wall
ring is uncapped -- independent corroboration from a different species.
CANDIDATE ONE CONFIRMED: the corner is nobody's job, `wallEnd` is a
straight-run remainder filler and nothing in the vocabulary turns. TWO AND
THREE REFUTED: runs are contiguous to 1e-6 and land on exact integers
(+/-17.000, +/-26.000, +/-18.000), so nothing was stripped by the name-boundary
strip; and rounding does not produce one value forty times. AUTHORED UPSTREAM,
not introduced at assembly -- the SLOT SPEC already stops at the centreline,
so Zoo and Lot are acquitted and the corner is missing from the REQUEST, which
makes this item 62's gap protocol (a Deli Counter slot role plus a Zoo
`Corner_90_Outside`/`Inside` species -- item 57's corner family) rather than a
patch. NOT CLAIMED, deliberately: the notch is an L-shaped pocket whose INNER
quadrant both runs cover, so this is a visible corner slot and a sky/backlight
leak but NOT a through-breach -- the item's sightline and tactical-cover
consequence is UNSUPPORTED by the plan geometry and should be restated or
dropped; and the FOUNDING SIGHTING IS STILL NOT TIED to it, because the
overlay's 21.63 m ray from (-63.4, 1.6, 86.4) lands on `ext_0_N_seg8`'s span,
~19 m from the nearest corner, while `seg9` sits at 23.2-24.1 m -- the
overlay's two numbers do not agree with each other. The instrumentation gap
this item flagged is QUANTIFIED: `ext_0_N_seg9` EXISTS IN ALL FIVE BUILDINGS,
and only mansion_a02's is within reach of the walk position (24.08 m; the next
is 74.78 m) -- print the building. THE RULER FAILED TWICE BEFORE IT WORKED,
and that is the binding constraint on the gate this item asks for: `_w<cm>` is
the module's X EXTENT, which is the run width on an N/S run and the THICKNESS
on an E/W run (`wall_rockay_01_w30` is 0.30 m thick and 2.00 m long, and no
filename records the 2.00), and `fit.dims` is [x, y, z] rather than [width,
thickness, height]. Reading either BY ROLE prints a comb of 1.700 m
(= 2.000 - 0.300) gaps on every E/W run and nothing on N/S; the first pass
reported 222 gaps and every one was that number or half of it. An
envelope-continuity gate MUST resolve dims by AXIS from the run's orientation,
or read the GLB bounds through `module_extents.py`'s tested reader -- a gate
that parses stems would pass the corner and fail 222 sound joints, the exact
inversion. UNRESOLVED and not quoted as a finding: 30 residual slot-side gaps,
all at E/W openings, far likelier the ruler a third time than the wall. GLB
BOUNDS WERE NEVER READ -- thickness 0.300 comes from the slot spec's
`fit.dims`, authoritative for what was ASKED but not for what was BUILT.
THE GATE IS BUILT AND UNBLOCKED: `tools/envelope_continuity.py` reports
`ENV_CORNER_OPEN`, `ENV_RUN_GAP`, `ENV_DIMS_AXIS_SWAP` and
`ENV_PLACEMENT_DRIFT` off the slot manifest alone -- so it fires before any
geometry exists -- pins `slot_manifest_version` and `space` and REFUSES an
unrecognised shape rather than counting it clean, and carries a `--selftest`
that fails on a name-parsing ruler. It is NOT wired into any job yet, and it
is deliberately not blocking: 124 of 124 buildings fail it today, so it
graduates the way item 59's L18 did, once the library is clean. TWO OTHER
THINGS THE SWEEP FOUND, both filed rather than folded in: exactly ONE real run
gap in the whole library (`auto_shop_a02`, storey 0 N, 0.050 m between
`ext_0_N_open0` and `ext_0_N_seg3` -- one authoring step, and the only one),
and 349 slots whose `fit.dims` is in a different frame from their
neighbours -- filed as item 63, and REFRAMED the same day: neither frame is
wrong, nothing declares which is in use, and that is a PRECONDITION of the
corner fix rather than a tidy-up beside it. REMAINS: give
corners an owner, wire the gate, graduate it, and tie or retire the founding
sighting. Full evidence in
`docs/findings/ITEM58_THE_CORNER_IS_NOBODYS_JOB.md`, because
`.level_factory/preview/` is gitignored*

**58. A facade corner is open to the sky, and light walks straight through
the building envelope.**
Raised 2026-08-23, walking lot_demo_001: at walk position (-63.4, 1.6, 86.4)
the vertical joint where a themed exterior wall run meets the facade return
(module `ext_0_N_seg9`, a zoo-library wall module) stands visibly OPEN -- a
gap wide enough that sky/backlight shines through the corner from outside,
photographed with the crosshair on `Wall` at 21.63 m. Item 57's taxonomy
calls this Critical: a gap between pieces exposes modular construction
instantly, and this one also breaches the envelope (sightline and light leak
through a wall the gameplay layer treats as solid -- tactical cover reads
wrong at exactly the corner a player would hug). NOT YET DIAGNOSED, candidate
mechanisms in likely order: the corner junction is nobody's job (`wallEnd`
fills straight-run remainders; no corner module family owns the turn); a
themed module narrower than its greybox slot after the name-boundary strip
removed the greybox that used to fill the joint; or seg-boundary rounding
between adjacent wall slots. **WHAT WOULD CLOSE THIS:** locate the joint in
the composed scene, measure the gap against the slots on both sides, give
corners an owner (module family or corner-aware wallEnd), and add the gate
item 57 asks for -- an envelope-continuity check over adjacent exterior wall
slots' themed extents, so an open corner fails a build instead of waiting
for a walker with a screenshot.

**OWNERSHIP DECIDED 2026-08-24: DELI COUNTER OWNS THE CORNER.** The reasoning
is the routing table's own, stated plainly -- a corner is part of a BUILDING,
so it is a slot, and slots are Deli Counter's. Zoo may author a better-looking
corner afterwards, into the slot DC declares; what DC must own is the
COLLISION piece and the modular economy it sits in. The consequence, if a
corner ever turns out NOT to be part of a building, is that the routing itself
needs rethinking -- not that this slot moves.

**TIER ONE COSTS NO NEW GEOMETRY, and the mechanism is already in the file.**
`_record_wall_slot` says it: a `wallEnd` "is authored as a UNIT box and the
size rides as a per-slot scale: one module fits every remainder", verified
in-engine as unit box x `fit.dims` reproducing the baked shell 1:1. A corner
post is that same unit box at scale `[t, t, storey_h]`. So the collision-
correct first tier adds ZERO new GLBs to any kit -- it is more instances of a
species every kit already carries, which is the whole VRAM argument: one mesh,
N instances, not N meshes. Four per storey, 988 across the library.

**THE GEOMETRY.** Every run currently terminates ON the perpendicular wall's
centreline. Pull each run end back by half the wall thickness -- to the
perpendicular wall's INNER face -- and seat a `t x t` post at the intersection
of the two centrelines. No overlap, envelope closed, footprint unchanged at
`+/- (half_span + t/2)`. The pull-back needs no new logic: the `wallEnd`
remainder already absorbs an arbitrary end width, so only the span
computation moves.

**TIER ONE IS A `wallEnd`, AND THE NAMING QUESTION IS ANSWERED BY THE UNIT
RULE.** `kit.py`'s `exact = typ != "wallEnd"` is one hardcoded string: anything
NOT literally named `wallEnd` is exact-fit, one module per distinct size.
Priced against the library, an exact-fit corner is **18 modules per theme per
style** (18 distinct thickness x storey-height pairs) against **one** unit
module scaled per slot -- and mansion_a02 alone uses styles 01/02/03, so that
multiplies twice. Worse than the count: a corner slot must carry a non-unit
scale `[t, t, h]`, and an exact-fit module scaled by its slot is
`module_extents.py`'s wallEnd mis-measurement running in reverse. So the post
is emitted as an ordinary `role: "wall", size_mod: "end"` slot at the corner
position, both naming laws unchanged, and the corner-ness rides on the
`slot_id` (`ext_<storey>_<NW|NE|SW|SE>_corner`) -- the handle everything here
is already addressed by. NOTE the option this rejects was mis-stated when it
was framed: "a wallEnd with a corner `size_mod`" does NOT work, because
`slot_typename` returns `wallEnd` only when `size_mod == "end"` exactly and a
`"corner"` size_mod falls through to `"wall"`, which is the exact-fit path.

**TIER TWO IS ZOO'S, AND ZOO ALREADY BUILT IT -- see item 64.**
`wallCorner` is a complete recipe plus a full genome entry, rockay included,
dated 2026-07-14, and nothing has ever asked for one. So tier two is not
"grow a species", it is "arm three things and ask", and all three are
measured in item 64: the genome's 2.0-4.5 m height range excludes 252 of the
988 corners, the stem carries width only so `wallCorner_rockay_01_w30` would
have to be 14 distinct solids, and the gap report that would have said so is
never armed. Also gated on item 63 for the same reason as before: a square
post is frame- and rotation-invariant, an L with a front and a back is not.

**AND THE L CANNOT BE A UNIT MODULE, which is why the tiers split where they
do.** Scaling an L's leg length scales its thickness with it; a `t x t` post
is a cube and a scaled cube is still a cube. The geometry itself is what makes
tier one cheap and tier two structurally exact-fit.

**THE INSIDE CORNER: MEASURED, ZERO INSTANCES.** 247 storeys across the
library, every one carrying exactly the runs N/S/E/W, and zero exterior runs
with more than one perpendicular offset -- every building is a rectangle in
plan. So it is not designed for, and `envelope_continuity.py` already refuses
a storey whose run set is not the four rather than measuring it wrong.

*STATUS: OPEN 2026-08-24 -- LIBRARY SURGERY LANDED; GENERATOR AVOIDANCE
AND THE FOUNDING SIGHTING REMAIN. DC 0.101.1 slid all 33 offending
openings clear (28 specs, keep-side minimal motion by default; recorded
exceptions: two garage_bays crossed to the garage they name, five
dead-center collisions direction-picked from room roles, and the parking
family's vehicle_in adjudicated a DEFECT -- the wall it hit separates the
attendant booth, the OBJECTIVE room, from the deck). Verified per spec at
edit time (full lint before/after, zero L18, no other finding gained or
lost) and on the rebuilt library: `layout_lint --all` reads 0 FAIL, 93
WARN, no L18 line in it. SAME DAY, the built-output half: `tools/door_split_probe.py` + `.gd`
walk the RUNNING composed scene deriving each aperture from its
Doorway_Jamb_L/R pair (the probe's own first run matched any *Doorway*
mesh and reported 102 walls sitting FLUSH against jambs -- correct
construction read as defects; the lesson is in its docstring). VERDICT on
lot_demo_001: 45 apertures, ZERO walls inside any of them -- the founding
sighting was fixed en route by the week's rebuilds, and its class has an
instrument now. The probe's four findings were all `AreaPanel_Surface`
sign quads hanging in exterior doorway spans: item 55's blank cards,
three of four still engine-named, not walls. On that zero plus the clean
library, L18 GRADUATED WARN -> FAIL (DC 0.101.2) -- a doorway-splitting
spec now fails its build instead of waiting for a walker. REMAINS, the
last third: the floorplan GENERATOR learns avoidance (nudge the opening
or end the partition a bay short), for which the FAIL gate is the
backstop, not the fix. Earlier same day: LINT SHIPPED (WARN), AVOIDANCE
PENDING THE COUNT. `layout_lint.py` L18 (DC 0.101.0): no partition may terminate
inside a doorway's aperture span plus a 0.3 m leaf margin on the wall it
meets -- exterior and interior hosts alike, endpoints judged through
`clamp_partition_span` so the lint and built geometry cannot disagree, a
wall CROSSING the aperture line deliberately exempt. Eleven tests pin the
geometry and the exemptions. Numbered L18 because the changelog assigns
L17 to the stair-volume-narrowing lint, which is ABSENT from today's
layout_lint.py -- that discrepancy is its own open question (a documented
FAIL gate that does not run is silent coverage loss, item 62's disease).
MEASURED 2026-08-24 (`layout_lint.py --all`, 129 specs): 33 L18 findings
across 28 specs -- the LARGEST single rule in the library (L9 cover-boxes
24, L16 marker rooms 20, L6 objective-touches-entry 19). Every finding is
an EXTERIOR host on story 0, and they cluster: (1) the person-door class,
14 findings, unambiguous -- `front_entry_east` x5 with IDENTICAL numbers
(cr_gas, gas_station, gas_station_a01, gas_street, gs_corner_station: one
cloned ancestor), `alley_entry` x4 (the deli family, same story),
`breach` x2, `west_entry`, `rear_service`, `alley_door`; (2) the wide-bay
class, 19 findings (vehicle_in x5m x4, loading_bay x4, docks and gates)
-- SIX of which land 0.00-0.20 m from the aperture CENTER: a spine
partition at coordinate zero running into a dock door also centered at
zero, the symmetric-layout collision. Two findings sit within 0.10 m of
passing (freight dock_n1 2.50 vs 2.55, marina gear_dock 2.00 vs 2.10).
TWO QUESTIONS BEFORE SURGERY: whether a wall ending mid-`vehicle_in` on
the parking family is a defect or an intentional in/out lane divider (one
render decides); and why the FOUNDING sighting is absent -- zero
interior-host findings library-wide means the zoo doorway split is either
slot-EMITTED by the builder (invisible to a spec lint, needing a
built-output check instead) or lives in a layout not in specs/.
Clone-dedup puts the real fix count near 20; every fix changes geometry,
so they batch into ONE shell rebuild. WHAT REMAINS: the two
adjudications, the ~20 spec fixes (nudge the opening or stop the
partition a bay short), generator avoidance for the same rule, and
graduation WARN -> FAIL once the library lints clean. Prior state
(2026-08-23): SIGHTED, RULE DESIGNED, UNBUILT -- queued behind item 54's
rebuild*

**59. One door, two corridors: a partition ends inside the aperture and
splits the egress.**
Raised 2026-08-23, walking lot_demo_001: at (22.1, 1.6, 70.3) in the `zoo`
building, an opening under `int_0_0_seg17` has a partition's `WallEnd`
standing in the middle of its aperture -- one doorway divided into two
squeeze-past channels by a wall edge-on to the door. Item 57's semantic rule
names it exactly: a seam (here, a wall termination) must not cut through
something the eye reads as ONE object, and a door is the strongest such
object in a heist game -- egress is gameplay vocabulary, and "which half of
the door do I take" is not a question a building should ask. THE RULE FOR
DELI COUNTER: no partition may terminate inside an opening's aperture span
(plus a leaf-clearance margin, ~0.3 m each side) on the wall it meets --
detection is geometric (partition endpoint's coordinate on the host wall
inside [opening_center - w/2 - margin, opening_center + w/2 + margin]), and
it covers exterior walls and partition-hosted openings alike, since this
sighting is a partition T-ing into an interior wall's doorway.
**WHAT WOULD CLOSE THIS:** the check in `layout_lint.py` (warning first, so
it cannot red an in-flight certification; error once the library is clean),
the AVOIDANCE in the floorplan/generator path (nudge the opening along its
wall or terminate the partition one bay short -- never silently delete
either), and a regenerated library with zero warnings.

*STATUS: OPEN 2026-08-24 -- FIRST TIER SHIPPED, WALK PENDING; THE FULL
POLICY STILL UNDECIDED. Lux 0.25.0 turns on `shadows_enabled` for the
sign/window area rigs -- the only shadowed lights in the package, four
rigs against ~128 interior fixtures; the plumbing existed end to end
(LuxLightRig carried the field, LuxAreaLightRig applies it on both render
paths) and nothing had ever set it. Verification is the walk at
arena_a03's interior (47.0, 1.6, -13.2): the through-wall wash gone, the
doorway spill kept. Interiors stay unshadowed pending the quality-profile
decision this item owns. Prior state (2026-08-23): SIGHTED, LEVERS
PRICED, DECISION NOT TAKEN.
Partially mitigated in the same day's lux work: drop-derived ranges (0.19.0)
shrink how far a lamp reaches through anything. SECOND SIGHTING 2026-08-24,
and it names the worst class: walking the census-#8 build, arena_a03's
interior ceiling at (47.0, 1.6, -13.2) carries a broad wash from the SIGN
outside the S doorway -- an area rig at energy 3.0 mounted ON the envelope,
so its range sphere is always half inside the building it hangs from.
Collision cannot block light in GL Compatibility; only a shadow map can,
which re-prices lever (a): signs are FEW (lot_demo_001 ships four, item 55)
where interior fixtures run ~128, so `shadow_enabled` on the sign/window
area rigs ALONE is the affordable first tier of the quality-profile
decision -- the tall-pole test to run before ever shadowing interiors.
Doorway spill stays legitimate light; the wash arriving THROUGH the wall
above a closed envelope is the defect. The wash pattern also answers the
seam question asked at the sighting: a geometric reveal between wall and
roof would read as a crack-line of light at the joint, and this is a broad
sphere-shaped pool -- the light is not finding a gap, it is ignoring the
wall entirely*

**60. Light walks through walls: a fixture in the next room lights this
one's ceiling.**
Raised 2026-08-23, walking lot_demo_001: at (0.8, 1.6, 74.3) in
`pvp_station_ref`, the ceiling above a partition carries the glow of the
NEXT room's fluorescent -- `shadows_enabled` is false on every rig the
loader builds, and an unshadowed light illuminates everything in range with
walls never consulted. The same fact drives item 54's budget accounting
(binding ignores occlusion) and this, its visible half. THE LEVERS, priced:
(a) `shadow_enabled` on interior fixture rigs -- correct and expensive; GL
Compatibility pays per shadowed light and a 136-light package cannot afford
all of them, so this wants the `LuxQualityProfile` gate (highest tier
shadows everything, lower tiers shadow pendants/objective rooms only, floor
tier none); (b) drop-derived ranges already shipped -- a range that stops at
the room's own scale stops most cross-room reach for free; (c) per-room
`light_cull_mask` layers -- surgical but kills LEGITIMATE spill through
doorways, and Godot's 20 render layers cannot number every room on a site.
**WHAT WOULD CLOSE THIS:** a decision recorded here, then the quality-tier
shadow policy in the loader/rigs, then a walk that shows walls stopping
light where doors let it through.

*STATUS: NARROWED 2026-09-04 -- BUILT, COMPILED, RENDERED AND TIMED ON REAL
HARDWARE IN LUX 0.28.0, AND AS OF 0.29.0 SECTION 50 IS THREE OF FIVE COLUMNS
MEASURED, SECTION 51 HAS A HARNESS AND ONE MACHINE IN IT, SECTION 54'S EDGE
CASE IS CLOSED AND THE HALF-RESOLUTION PASS IS PRICED. WHAT REMAINS IS SIX
HARDWARE CLASSES AND TWO COLUMNS NO ENGINE COUNTER REPORTS. SECTION 41'S BUDGET IS MET ACROSS SECTION 50'S WHOLE
RESOLUTION MATRIX. THE TDD'S OWN PREMISE WAS REFUTED ON THE WAY, TWO OF ITS
SECTIONS CONTRADICT EACH OTHER, AND ONE OF ITS ACCEPTANCE TESTS IS NOT
REPRODUCIBLE AT 8-BIT OUTPUT. THE hdr_2d DECISION IS TAKEN AND
WIRED, AND THE FEATURE HAS BEEN WALKED, TUNED BY EYE AND SHIPPED AS ONE
SWITCH. `LuxRoot.film_mode` / `set_film_mode()` turns the whole treatment on or
off for a Level Factory export without touching a preset, because the shipped
presets store no film_* fields at all and inherit the settled defaults. FILM NO
LONGER TOUCHES THE RENDER TARGET: film_manage_hdr_2d DEFAULTS FALSE, because
raising it is a TONE change larger than the grain it serves and it moves in
opposite directions on different rasterisers -- llvmpipe takes a pixel at
[0,0,0] to [0.0118,0.0118,0.0118] with film still off, an RTX 2060 turns the
whole frame into its linear form. WITH THE TARGET HELD AT 8 BITS AND FILM THE
ONLY VARIABLE, hue edges per lit scanline fall 47.9 to 21.6, 45.4 to 22.8, 9.9
to 5.1 and 17.7 to 11.4: 1.55x to 2.22x, every shot. THAT IS THE HONEST FIGURE
AND IT SUPERSEDES A 3.6x-5.9x ONE THAT HAD THE RENDER TARGET SWITCHING
UNDERNEATH IT. AND THE MECHANISM IS NOW DEMONSTRATED RATHER THAN INFERRED: at a
VISIBLE grain, film with PER-CHANNEL quantization makes the rainbow 1.5x WORSE
(47.9 to 73.3) before the shared decision takes it 2.2x below the baseline --
which is exactly the mechanism section 3d named, and it was invisible while the
grain default was 8x too low to see. FILM DEEPENS THE BLACKS RATHER THAN
LIFTING THEM: pure black 55.6% to 87.1% of frame, 99.7% of black pixels
unchanged. THE PERFORMANCE RE-MEASURE IS DONE AND SECTION 41 NOW FAILS: on an RTX 2060 at
3840x2160 film costs 0.2610 ms, which is 0.78% of a 30 fps frame and 1.57% of a
60 fps one but 2.35% at 90 fps and 3.13% at 120 fps against a ~2% budget. THE CAUSE IS NOW MEASURED, BY BISECT
RATHER THAN BY GUESS -- each film term priced by removing it at the failing
cell. THE SECOND SHADER IS FREE (+0.0069 ms with its whole block branched
over), so every theory offered about the cost was wrong: not the octave loop,
not the shader swap, not the resolution lock. The entire +0.2534 ms is the film
ARITHMETIC -- grain fetch, dihedral tile coordinate, exp2 transmission -- and
IT CANNOT BE TUNED AWAY: removing both removable terms (resolution lock 0.0041,
chroma dye 0.0118) saves 6.1% against the 15%-34% needed. THE DENSITY MODEL IS
THE BUDGET.
SO THE FEATURE HAS A MEASURED ENVELOPE RATHER THAN A FAILURE. Film costs 0.0450
ms at 720p, 0.0990 at 1080p, 0.1760 at 1440p and 0.2580 at 4K, against section
41 budgets of 0.67/0.33/0.22/0.17 ms at 30/60/90/120 fps: INSIDE BUDGET
EVERYWHERE EXCEPT 4K ABOVE 60 FPS AND 1440p AT 120. That is documented in
lux/addons/lux/docs/film_emulsion_authoring.md so it is a scoping decision
rather than something the first 4K120 build discovers. Both figures are FLOORS
on an empty scene, so 1440p at 90 and 4K at 60 are thin rather than
comfortable. THE HALF-RESOLUTION PASS IS NOW PRICED AND DELIBERATELY NOT BUILT
(`lux/tools/film_halfres_probe.py`). NO NEW TIMING HARNESS WAS WRITTEN, ON
PURPOSE: a half-res pass at 4K renders exactly as many fragments of exactly the
same shader as a full-res pass at 1080p, and the resolution lock makes the
per-fragment work identical too, so its cost IS a cell section 50 already
measured -- building a SubViewport rig to re-measure it would only have added a
new way to be wrong about a number already in hand. It closes EVERY failing
cell, leaving 0.1232 / 0.0677 / 0.1217 ms for the upscale blit at 4K@90,
4K@120 and 1440p@120. WHAT IT COSTS IS THE GRAIN, AND TWO PREDICTIONS WERE
WRONG BEFORE THE MEASUREMENT STOOD UP: a Nyquist argument on the band edges
said the fine band would ALIAS at 1440p-half (it does not), and the first probe
box-downsampled a full-res render -- a fair low-pass -- and reported 0.0%
aliasing everywhere, which should have been the tell, because a half-res PASS
point-samples once per half-res fragment and folds rather than attenuates.
Corrected: 74.3% of grain amplitude retained at 4K and 65.6% at 1440p, aliasing
0.0% at both, and the FINE BAND -- 68% of the blend, placed near Nyquist on
purpose so the grain reads as crystals rather than blobs -- falls from 31.5% to
13.5% of energy at 4K. IT SOFTENS RATHER THAN ALIASES, so half-res is NOT a
quality setting: it is a SECOND STOCK, the same emulsion coarser, because half
the pixels is half the pixels. That is a look decision and this item does not
make it. Aliasing appears only at 1080p (10.2%), so the technique is viable
exactly where it is needed and breaks where it is not. Worth stating next to
all of it: 4K at 120 fps is chasing motion clarity and film emulsion is a 24
fps aesthetic -- half-res makes the cell FIT, it does not make it a thing
anyone wants.
THE EARLIER ATTRIBUTION IS RETRACTED. It was attributed to the octave
loop -- a `for` bounded by a UNIFORM cannot be unrolled -- and a single-octave
fast path was built on that reasoning and measured: 0.2610 -> 0.2580 ms, THREE
MICROSECONDS. The fast path is kept because it is free and arithmetically
identical at the default, but the explanation was a guess and measurement
rejected it. NOR IS THE REGRESSION ITSELF ESTABLISHED: the comparison is
0.28.0's 0.1340 ms against today's 0.2540 with NO CONTROL, because 0.28.0's
`no post` column was never recorded -- a machine that is merely slower today
produces the same apparent doubling. What is known without any of that is the
absolute figure and its verdict. Finding the cost needs a BISECT of the shader
terms, not another hypothesis. And the figure is a FLOOR taken on an empty scene, so a real
level can only be worse. SECTION 45 AT 8 BITS reads chroma/luma 0.3365 --
inside the hard 0.40 bar, outside the preferred 0.20 -- where at float it reads
0.1914; the probe's own noise-floor control attributes most of that to the
FORMAT rather than the grain, since the chroma-free baseline still measures
0.000412 there against 0.000091 at float. OPTIONALITY IS RE-PROVEN ON ALL NINE
SHIPPED PRESETS: none asks for film, none activates it, deleting the shader and
grain asset moves none further than the build's own nondeterminism, and the two
with grain_strength 0 are bit-identical. AND THE RAINBOW CLAIM IS NOW EXACT: on
a flat coloured patch with the grain off, saturation spread from quantization
alone is 0.082397 per-channel against 0.000000 shared -- not smaller, ZERO,
because one multiplier applied to three channels leaves hue and saturation
untouched by construction. SECTION 50'S OTHER COLUMNS ARE NOW THREE OF FIVE, AND POWER IS THE ONE THAT
CHANGED A DECISION. `film_render_probe.py --perf --power` samples nvidia-smi at
100 ms and attributes it to each configuration's OWN timed window -- warmup
excluded, because shader compilation and the clock ramp both move watts and
neither is the feature; polling around the whole process would have averaged
import, scene build and five configurations together and published the mean as
"film", which is how a power column gets written without measuring anything.
FILM COSTS +7.6 W AT 720p RISING TO +12.1 W AT 4K. On a desktop that is inside
the noise. A STEAM DECK'S ENTIRE BUDGET IS 15 W, so the handheld class stopped
being one entry in a coverage list and became the row to fill first -- a
conclusion no frame-time column could have produced. Power also independently
supports the hdr_2d reading above: the film delta gets SMALLER with the float
target on (7.0 vs 10.3 W at 1440p, 8.8 vs 12.1 W at 4K), the same direction the
frame times went, so two instruments now point at the bandwidth-bound
hypothesis and it is still a hypothesis. hdr_2d itself costs +35.9% on the
baseline pass at 4K and ~6-7 W. VRAM READS +0.000M AT EVERY RESOLUTION AND THAT
IS A FLAW IN THE MEASUREMENT RATHER THAN A FINDING: all five materials
including the grain texture are built before any timing runs, so the texture is
resident in the BASELINE row too and the delta cancels. What the row does prove
is the prediction it was built to test -- flat across all four resolutions, so
nothing about film's VRAM scales. The absolute comes from the asset and not the
instrument: one 128x128 RGBA8 texture, 64 KiB, once. RAM +0.006M. BANDWIDTH AND
SHADER STALLS ARE LEFT EMPTY RATHER THAN ESTIMATED -- no engine counter reports
either, deriving bandwidth from resolution x format x taps is arithmetic
dressed as a measurement, and stalls need Nsight, RGP or PIX. A named gap beats
a fabricated column.
SECTION 51 IS NOW A FILE RATHER THAN A PLAN. `lux/tools/film_hw_sweep.py`
appends ONE record for ONE machine to `lux/docs/data/film_hw_sweep.jsonl`. The
reason this section stayed untouched while everything around it closed is
structural: a sweep written as a single invocation cannot be started until the
last card arrives, so it never gets started. Inverted, the sweep IS the file and
machines can be added months apart by different people. Records are NEVER
overwritten -- re-measuring appends and the report prints the movement, which is
most of what a sweep is for -- and sample counts are a constant rather than a
flag, because two rows measured differently cannot be put next to each other.
FIRST ROW: RTX 2060, worst cell 0.2590 ms at 4K/hdr_2d true, reproducing the
0.2580 above across a separate run and a separate harness. SIX OF SEVEN CLASSES
REMAIN OPEN (AMD discrete, Intel Arc, integrated, handheld, Apple/Metal,
software) and the report names them -- the same quantity of unmeasured hardware
as before, stated as a list of machines to find. Read the envelope above as one
GPU's, not as the feature's.
SECTION 54'S FILM-MODE EDGE CASE IS CLOSED, AND IT WAS NEVER THE FEATURE.
RETRACTED: "the film-mode test segfaults llvmpipe at is_film_emulsion_active()",
a sentence that had been written into the probe's own comments and its report
text and sent three rounds of debugging at the rasteriser. THE CAUSE WAS THE
PROBE: the viewport-cleanup test above it frees the LuxRoot BY DESIGN -- it is a
test OF teardown -- and the film-mode test then called set_film_mode() on a
freed node. The free landed during an await, so there was no catchable error, an
unsymbolised C++ backtrace, and a reported line that drifted onto a two-term
getter that cannot abort anything. A freed Node still answers != null in
GDScript; only is_instance_valid() tells the truth, and that is what kept it
invisible. AND THE FIX BROKE THE TEST BELOW IT: reordering put film mode first,
set_film_mode() moves the film MASTER as well as the mode flag (it has to,
against section 10's three-key AND), so the cleanup test inherited the master
off and reported that it never got film running. THAT IS THE SAME DEFECT ONE
PAIR ALONG -- one test mutating shared state on _lux and the next inheriting it
-- and the reorder only moved which pair it broke. Fixed from both sides,
because either alone fixes the symptom and leaves the coupling, and
master_restored is asserted so the next leak fails where it happens. It was
caught only because the cleanup test REFUSES TO PASS ITSELF when it did not
observe what it was measuring; that is luck rather than coverage, and it is the
argument for tests that report "I measured nothing" instead of a value. GREEN on
both builds: film present ON->active OFF->inactive, film DELETED ON->inactive
OFF->inactive, shipped preset unmutated in both, viewport raised and restored on
both paths.
WHAT IS LEFT IS SECTION 51'S SIX REMAINING CLASSES, THE TWO COLUMNS THAT NEED
VENDOR TOOLS, AND A HALF-RES PASS THAT IS PRICED BUT UNBUILT.
Phases 1, 3, 4 and 5-7 landed (phase 2's reordering is folded into the shader
variant). THE PREMISE, AND A CORRECTION TO THE FIRST READING OF
IT. The TDD names the problem as "digital-looking noise applied independently
to RGB channels". The GRAIN does not do that -- it computes ONE scalar and adds
it to all three channels, scoring `chroma_noise 0.000000` on section 45's own
metric over 200 000 samples. This item first recorded that as "Lux has never
had a rainbow-speckle problem", WHICH WAS WRONG: the grain was cleared and the
finding generalised to the pipeline without measuring the other half of it. THE
RAINBOW IS THE ORDERED DITHER. It quantizes R, G and B independently, so on a
coloured surface the channels cross their level boundaries at different screen
positions, and a channel that dithers alone is pure chroma noise -- exactly
section 1's "unrelated red, green, or blue pixels". Measured on a flat orange
patch where nothing else can vary: per-channel quantization scores 1.500 on
section 45's metric and moves saturation by 0.0797, against the grain's 0.0000.
Worse, film emulsion as SPECIFIED makes it more visible rather than less, because
section 16 puts film before the dither and removing the additive grain's luma
noise unmasks the chroma underneath: on flat coloured patches in the real render
the ratio goes 0.225 with the legacy grain to 1.687 with film. THE FIX IS THE
DENSITY MODEL'S OWN IDEA ONE STAGE LATER -- quantize luminance and scale the
colour by the ratio, one shared decision instead of three, with a
`dither_luma_scale` to recover the finer banding three interleaved decisions
give (38 luminance steps at 3x against per-channel's 36, and a finer maximum
step). Measured on the rendered sample scene over 2183 flat coloured blocks,
saturation variation falls from 0.04178 as shipped to 0.01509, and the grain
accounts for very little of that -- the quantization accounts for nearly all of
it. BOTH PROBES NOW CARRY THE
CLAIM rather than a scratch script: `film_math_probe.py` asserts both halves --
that per-channel quantization DOES move saturation (0.027265 worst) so a fix
that did nothing could not pass, and that a shared decision moves it by nothing
(3.33e-16) -- and `film_render_probe.py` measures 0.082397 against exactly
0.000000 on hardware at both precisions. The audit carries the retraction in
place, at the head of the section that made the wrong call. ALL OF THIS IS
OPT-IN -- BUT 0.28.0 GOT ONE PART OF THAT WRONG AND LUX 0.28.1 FIXES IT: a
`const ... := preload()` of the film assets in LuxPostFX resolved at SCRIPT
load, so on a project whose `.godot/` predated the grain texture the script
failed to load, `LuxPostFX.new()` returned null, and there was NO POST STACK AT
ALL with `Nonexistent function 'apply' in base 'Nil'` every frame. Found by the
first run of the demo on a machine other than the one that wrote it. THE LESSON
IS THE FIX: optionality that has not been tested by REMOVING the thing is a
claim, not a property; it is now tested that way (delete the grain asset, Lux
renders normally with one warning). AND THE RINGS AROUND A LIGHT POOL ARE WHERE
THE RAINBOW IS MOST VISIBLE ON REAL GEOMETRY -- counting neighbouring pixels
whose hue jumps more than 15 degrees along one scanline through the pool, 149 as
shipped against 4 with the shared decision, and 171 with film grain but
per-channel quantization: film ON makes the rainbow EASIER to see until the
quantizer is fixed too. The coherence dial exists on the FILM shader only,
the baseline shader is byte-identical, and an earlier draft that let `grain_mode`
gate the legacy grain was backed out so that no film property can change a
scene which never asked for film. THE REAL DEFECT, measured
on one orange swatch at four exposures at the shipped `grain_strength = 0.03`:
additive grain leaves hue exactly alone but modulates SATURATION, by +4.2% on a
bright swatch and **+53.3% in deep shadow**, because an absolute offset is
proportionally huge on a dark pixel. Film's density model, on the same swatches
under the same noise, moves saturation by 0.36% worst case. That is a better
argument for the feature than the TDD makes and it is the one to quote. TWO
FREE FINDINGS: grain is applied AFTER quantization (line 114 after line 100),
undoing the level snapping the final clamp's own comment says exists to be
preserved -- the section 16 ordering violation; and the grain hash multiplies
`uv` by `time_seed`, which is seconds of playtime, so it is a FREQUENCY scale
rather than a reseed and grain frequency climbs to 1000x over the first ~16.7
minutes of play (a `sin()` argument near 91 000, where fp32 is
hardware-dependent) before snapping back. Both are independent of film emulsion
and both remain on the baseline path. WHAT BLOCKS SECTION 20, AND IT IS A HUMAN
DECISION: `project.godot` does not set `rendering/viewport/hdr_2d`, so the
viewport target is 8-bit and scene colour is already RGB8 before any
canvas_item pass samples it -- sections 7 and 20 cannot both hold. The only fix
costs the 2D target RGBA8 -> RGBA16F, about +7.5 MiB at 1080p, against a 0.25
MiB budget written for the grain asset and never meant to price a format change
to a buffer that already exists. `tools/film_precision_probe.py` measures it
(and prices the hdr_2d option) rather than trusting a class reference for a
different engine version. TWO DELIBERATE DIVERGENCES, both measured and both
because the TDD contradicts itself: `grain_mode` defaults to Simple, not the
TDD's Off, because Off would silently strip grain from all nine shipped presets
while section 12 promises they stay unchanged; and `film_chroma_ratio` defaults
to 0.10, not 0.12, because 0.12 scores 0.2251 and fails the TDD's own preferred
bar of 0.20 while 0.10 scores 0.1876 and clears it. Section 47 is also
internally inconsistent -- its literal "Dark RMS > Midtone > Highlight" is only
satisfiable by the additive model section 27 forbids -- and the relative reading
this meets is recorded. COMPILED AND RENDERED 2026-09-02, which
was the whole of the risk at the time of writing and is now retired.
`tools/film_render_probe.py` builds a minimal project around the two shaders,
imports it and draws known patches through both at each `hdr_2d` setting. The
compile receipt is the IDENTITY case rather than a clean log -- film off, every
other stage neutral, the pass returns its input exactly (`luma_noise 0.000000`,
one distinct code, two patches, both precisions), and a shader that failed would
have been replaced by a fallback that does not reproduce its input. THE MODEL
AND THE ENGINE AGREE to within 1% wherever the signal exceeds the render
target's own precision (neutral at strength 0.10: model 0.005112 luma against
engine 0.005064). SECTION 20 IS NOW MEASURED, not argued from a class reference
for a different engine version: 8-bit integer as shipped and floating point with
`rendering/viewport/hdr_2d = true`, on both rasterisers, so the option is one
line and the setting name is right for 4.7. The exact format differs by driver
(RGBA8/RGBAF on llvmpipe, RGB8/RGBH on the RTX 2060) and the first write-up of
this got it wrong, from a hand-written int-to-name table in the probe driver
that had 11 as RGBH when 11 is RGBAF -- caught only because the NVIDIA run
returned an id the table did not contain. The probe now names formats from
`Image.FORMAT_*` inside Godot; the correction is recorded here because a
measured fact was misreported, even though the conclusion was not affected. AND THE 8-BIT COST IS CONCRETE -- the baseline's grain is
chroma-free BY CONSTRUCTION, so the chroma it measures is the format's own
floor, and that floor is 0.001811 at 8 bits against 0.000009 at 16. The entire
chroma signal at 8-bit output was per-channel rounding. Section 45's ratio
follows it: 0.3340 at 8 bits, 0.1901 at 16, so the TDD's own preferred bar of
0.20 is UNREACHABLE at 8 bits by any implementation, and the default grain
spans three distinct codes there. THE RESULT THE FEATURE EXISTS FOR, rendered at
default strengths: saturation span 0.15% film against 4.16% baseline on orange,
and 0.33% against 50.02% in deep shadow. ONE TRAP RECORDED so it is not sprung:
section 45's metric is not a chroma measurement on a COLOURED patch -- with the
chroma term switched off entirely it still reads 0.6023 on orange and 0.9894 on
red, because std(R-G) there is driven by the shared transmission multiplying a
non-zero R-G. Both probes run that control on every invocation. AND THE STRONGEST ARGUMENT FOR hdr_2d IS ONE NOBODY
WROTE DOWN: at 8-bit output the acceptance test is NOT REPRODUCIBLE ACROSS
HARDWARE. Same build, same probe, same patches, llvmpipe against an RTX 2060 --
with hdr_2d off the two disagree by up to 70% (baseline chroma floor 0.001359
against 0.000412 on orange); with it on they agree to 0.20% worst case, and that
is a 32-bit float target against a 16-bit one rather than two runs of the same
thing. A test whose result moves 70% with the graphics card is measuring the
card. It also answers a question nobody asked: 16-bit float has the headroom, so
nothing argues for RGBAF. SECTION 41 IS MEASURED AND MET on an RTX 2060 across
every resolution in section 50's matrix, using the engine's own per-viewport GPU
counter over 600 timed frames per configuration after 120 discarded, and three
configurations per cell (no post pass / baseline / film) so the figure is the
film shader's ADDED cost and not the pass's total: film adds 0.0240 ms at 720p,
0.0510 at 1080p, 0.0920 at 1440p and 0.1340 at 4K with hdr_2d on. Against the 2%
allowance every cell passes; THE WORST IS 4K AT 120 FPS WITH hdr_2d OFF at
1.79%, which is 12% of budget to spare, and that cell should be read as UNPROVEN
rather than passed because the measurement is a FLOOR taken on an empty scene
where nothing competes for bandwidth. AND THE hdr_2d DECISION IS NOW PRICED IN
TIME: +0.0430 ms on the post pass at 1080p -- 33.6% of the pass but only 0.26%
of a 60 fps frame -- on top of the +7.5 MiB. Film is also CHEAPER with hdr_2d
on, at all four resolutions, 4 for 4, by about 10%; the likely reading is that
the float target makes the pass bandwidth-bound so the extra arithmetic hides
behind memory traffic, which is a hypothesis from four consistent measurements
and not a profile. So hdr_2d partially pays for itself on the pass film runs in.
WHAT REMAINS: section 51's hardware sweep is untouched and one RTX 2060 is
nobody's minimum spec -- no integrated GPU, no AMD, no Intel, no handheld;
section 50 also wants VRAM, RAM, bandwidth, power and shader stalls, and only
frame time is measured; section 51's hardware sweep is untouched and one RTX 2060 is
nobody's minimum spec -- AND THAT SWEEP IS NOW LOAD-BEARING FOR THIS FEATURE'S
ATTRIBUTION, NOT ONLY FOR SECTION 41'S BUDGET, BECAUSE TWO RASTERISERS ALREADY
DISAGREE ABOUT IT.
THE WALK HAS HAPPENED (2026-09-03) on an RTX 2060 and this item's closing
condition is met: `lux/tools/film_walk_probe.py` runs film on the staged night
strip -- three Patina store shells with dressing, the fixtures GLB, 59 light
rigs baked, 147 fixtures spawned, Gothic Street Night -- four cameras, and FOUR
states, because three could not answer the question. The film states raise
use_hdr_2d, so every earlier film-off-versus-film-on reading measured FILM OR
THE RENDER TARGET AND COULD NOT SAY WHICH; `hdr_only` is film off at the film
states' target, which splits them. Hue edges per lit scanline fall 32.9 -> 8.7,
33.5 -> 5.7, 28.8 -> 6.6 and 10.9 -> 3.0: 3.6x to 5.9x, every shot. BOTH HALVES
CONTRIBUTE. The render target alone is worth 2.02x, 2.94x, 4.11x and 2.06x --
more than the quantizer on three of four shots -- and the quantizer adds 1.87x,
2.00x, 1.06x and 1.77x on top. THE GRAIN CONTRIBUTES NOTHING: hdr_only ->
film_perchannel is film fully on with per-channel quantization and moves 16.3 to
15.4, 11.4 to 9.6, 7.0 to 8.0, 5.3 to 4.9. That is the one attribution both
rasterisers agree on. The probe asserts each state rendered in the configuration
its column claims and aborts otherwise, which earned itself on the first run by
catching film_shared silently rendering at hdr_2d=false.
RETRACTED, SAME DAY, BY THE FIRST HARDWARE RUN: an llvmpipe attribution
published here saying "THE RENDER TARGET IS NOT THE FIX (47.9 -> 42.7, not even
consistent in sign)". On hardware it is 2.0x to 4.1x. Section 2b already
recorded that the 8-bit figures do not agree across rasterisers, and `film_off`
IS the 8-bit column, so every ratio taken against it was exposed to exactly that
and was published anyway. THE LESSON: a control tells you THAT two causes are
separable; it does not tell you their sizes on hardware you did not run.
ALSO RETRACTED: "film emulsion is not a treatment for item 57 and mildly works
against it on raking facades", with a claimed +12% on the raking shot.
ITEM 57 IN THE SHIPPED CONFIGURATION: NO EFFECT. Detection rate 68/82/87% film
off against 66/82/92% film on, three shots with a real module; the fourth has
none in any state. The earlier hardware reading of a modest loosening was taken
with the render target switching, and this single-variable one supersedes it.
THE ORIGINAL HARDWARE RE-WALK, KEPT BECAUSE ITS METRIC LESSON STANDS. Prominence is only
meaningful where a bump was found; argmax always returns something, so a shot
with no module reports the search floor and that number then gets compared
across states as though it meant something. The tool now reports DETECTION RATE
-- the fraction of lit rows carrying a real interior bump. film_off / hdr_only /
per-chan / SHARED: 01_strip 31/44/47/47% at the search floor in every column, so
it has no module and cannot answer this at all; 02_pawn_front 72/78/77/79% at
pitch 26, unmoved; 03_facade_raking 82/85/71/71% at pitch 50; 04_pool
25/81/8/3% at pitch 53. THE ANSWER IS A MODEST YES ON THE ONE GENUINE FACADE
SHOT: 03_facade_raking loses detection 85% -> 71% and prominence 0.1171 ->
0.1008, about 14% down, which is the original screen-space-grain hypothesis
surviving weakly. 04_pool's collapse from 81% to 3% is NOT an item-57 result --
what is periodic in a light pool at pitch 53 is the concentric banding of the
falloff, not a wall module, so that is the rainbow finding appearing in a second
statistic: a good consistency check and a bad item-57 datum.
AND THE OLD REPETITION METRIC IS RETRACTED ENTIRELY. It reported
max(autocorrelation[8:w/3]) and called it periodicity; autocorrelation of any
low-pass signal falls monotonically from lag 0, so that maximum is a SMOOTHNESS
measure wearing a periodicity label, and it ranks backwards -- 0.976 on a
synthetic signal with no periodicity at all, dropping to 0.916 when a real 40 px
module is ADDED. Replaced by bump prominence above the autocorrelation's own
decay envelope, and the tool now proves the metric on signals with known answers
before it measures anything, because nothing caught the first one having never
asked it to measure something whose answer was known.
NEW, UNRESOLVED, AND MORE CONSEQUENTIAL THAN ANYTHING ABOVE: RAISING THE RENDER
TARGET IS NOT TONALLY NEUTRAL ON REAL HARDWARE. `film_off` and `hdr_only` differ
only in use_hdr_2d, with film OFF in both, and on 04_pool mean luminance goes
0.2046 -> 0.1004 -- half -- with 45% of pixels differing by more than 0.15. It is
not a readback encoding artifact: applying the sRGB transfer function to
hdr_only does not recover film_off (0.114 raw, 0.086 encoded, and the encoded
mean overshoots at 0.227 against 0.182). The hdr_2d decision set out further
down this status rests on a patch-level measurement that the raised target lands on the SAME
values only more precisely; that may still hold at patch level, but end to end
through the post stack on hardware it does not. Since film_manage_hdr_2d
defaults to true, TURNING FILM ON HALVES THE BRIGHTNESS OF THIS SCENE BEFORE ANY
FILM ARITHMETIC RUNS. Hypothesis, untested: the float target no longer clamps at
1.0 before post, so the grade's contrast pivot, the palette zones and the
quantizer all see a different input range. WHAT WOULD CLOSE IT: measure the post
pass's input range in both targets, and decide whether film_manage_hdr_2d should
default false or the post stack should normalise.
THE hdr_2d DECISION IS TAKEN: `LuxRoot.film_manage_hdr_2d` raises the viewport
to a floating-point target while film is running and restores whatever was there
when it stops -- not a project setting, because Lux is an addon and cannot edit
a consuming game's project.godot, and scoped to film so that with film off in
every shipped preset it changes nothing. THE FACT IT RESTS ON WAS MEASURED
FIRST: a 3D scene resolved into the raised target lands on the SAME values, only
more precisely (0.25098/0.50196/0.74902 at 8 bits against
0.24915/0.50098/0.74951), NOT on their linearised equivalents
(0.05088/0.21404/0.52252) -- the post stack keys its contrast pivot, palette
zones and quantization off 0.5, and had the target gone linear every one of
those thresholds would have moved and all nine presets would have needed
retuning. AND IT HAS BEEN SEEN RUNNING, which is the first time anything in this
item has been looked at rather than measured: `lux/tools/film_demo.gd` drives
the sample scene with a runtime toggle, and captures three states in one run so
the two changes can be told apart -- render target alone 0.014127 mean absolute
difference, grain model alone 0.008058, player-visible total 0.011991. THE
PRECISION CHANGE MOVES THE IMAGE MORE THAN THE GRAIN MODEL DOES, which is worth
knowing before anyone credits the whole before/after to the grain. The
grain-model change is exposure-weighted on real geometry exactly as on synthetic
patches: relative difference 0.320 in the darkest band falling monotonically
through 0.104, 0.053, 0.030 and 0.018 to 0.011 in the brightest*

**61. Optional color-preserving film emulsion for Lux.**
Raised 2026-08-23 by TDD (50 sections; `lux/docs/film_emulsion_tdd.md` is
authoritative -- this entry is the index card). PURPOSE: present Lux's
continuous lighting color photographically -- suppress RGB-channel breakup,
per-channel speckle, posterization -- with grain that stays RELATED to the
underlying color (luminance-driven density, exposure-dependent, chromatic
variation restrained) instead of digital per-channel noise. CORE PRINCIPLE:
preserve color precision first, apply photographic response, THEN any
artistic reduction -- never quantize and try to win the look back.
ARCHITECTURE CONSTRAINTS: lives INSIDE the existing Lux post shader (a new
mandatory full-screen pass is prohibited), packed grain texture, shader
variants, zero cost when disabled ("the scene must render normally without
it" -- disabled performance is itself an acceptance test). ENABLEMENT is a
three-key AND: preset (`film_emulsion_enabled`) x quality profile
(`allow_film_emulsion`) x LuxRoot runtime switch, existing presets
unchanged. Natural and Retro modes; V2 may add a film LUT. ACCEPTANCE is
spelled out as tests: color continuity, lighting fidelity, rainbow-speckle,
hue preservation, exposure response, banding, temporal stability, and a
performance matrix with VRAM/RAM/CPU/GPU/bandwidth budgets.
**WHAT WOULD CLOSE THIS:** the TDD's own acceptance battery, green, on
hardware, with the walk as the final judge -- and item 57's texture-rhythm
observations re-walked under it, since film response may change how the
modular repetition reads.

*STATUS: OPEN 2026-08-24 -- CONVENTION WRITTEN, SIGNAL NOT UNIFORM, AND THE
ONE PLACE THAT ALREADY BUILT THE REPORT NEVER ARMS IT. `USING_THE_FACTORY.md`
states the protocol and names today's honest coverage; nothing emits the tag
yet. MEASURED 2026-08-24: `kit.plan_kit` takes `known_species` and documents
it -- "any planned module whose backing species is unknown lands in
`missing_modules` (the production gap report the Production Package
requires) instead of crashing at build time" -- and its ONLY caller,
`zoo/tools/zoo_cli.py:370`, is `plan_kit(manifest, theme=args.theme,
style=args.style)`. The argument is never passed, so `missing_modules` is
always empty and an unknown species is planned, never built, and silently
kept as a greybox box by Deli Counter's progressive resolver. Level
Factory's zoo adapter shells out to that CLI and does not mention it either.
This is the machinery already existing and unarmed rather than missing --
one argument, in the place the protocol most needs it, and it is what item
64's corner recipe went 41 days without anyone noticing*

**62. The capability-gap signal: a tool that cannot make what was asked
says so, uniformly, and names the owner.**
Raised 2026-08-24 while writing `USING_THE_FACTORY.md` (the operator's
charter, new at the root). The factory's answer to "the catalog cannot
make this" is the gap protocol: the OWNING tool grows a new capability --
a Pixelcoat skin pack, a Zoo species, a Deli Counter anchor rule, a Lux
tuning row -- rather than anyone hand-authoring a one-off downstream. The
protocol only fires if gaps are VISIBLE, and today they are visible
unevenly. Good: `LuxFixtureSpawner.spawn` returns every skipped marker
with a reason; `build_freshness.py` refuses to grade a stale library.
Bad, both paid for this week: Zoo's fixture pass dropped the new `pendant`
anchors without a word (no `FIXTURES` row -> no marker -> no light; the
gap surfaced as dark basements in an instrument count, not as a line in
the build log -- zoo 0.50.0 added the species, which fills the gap and
leaves the silence), and the spawner's name-parse fallback carried the
whole marker contract from the day it was written until a probe of the
running tree found the payload dead (lux 0.22.0). A gap that surfaces in
a walk instead of a build log costs a human playtest to find.
**WHAT WOULD CLOSE THIS:** one convention, implemented in every tool that
consumes a request it might not satisfy: on an unsatisfiable ask, emit a
`CAPABILITY_GAP` line naming (1) what was asked, (2) the nearest
capability that exists, (3) the repo that owns growing the real one -- on
stdout and in the tool's report artifact where one exists; Level Factory
surfacing gap counts in run summaries; and one test per tool proving an
unknown ask produces the tag rather than silence.

*STATUS: OPEN 2026-08-24 -- REFRAMED THE SAME DAY IT WAS FILED, AND THE
FIRST READING IS KEPT BELOW BECAUSE IT WAS WRONG IN AN INSTRUCTIVE WAY. Filed
at 349 findings as "openings are transposed", a defect report about a
CONVENTION; reading `zoo_keeper/core/kit.py` and then the composed scenes
refuted it. Both frames produce correct geometry, `rot_y` is honoured for 8 of
698 exterior modules, and the real defect is that nothing in a slot says which
frame it is in*

**63. Two coordinate frames share one `fit.dims` field, and nothing in a slot
says which one it is in.**
Raised 2026-08-24 by `tools/envelope_continuity.py` while it was being written
against `deli_counter/build`. `fit.dims` is `[x, y, z]` -- but in WHICH frame
is decided by the slot's role and stated nowhere.

**MEASURED, and the split is exact.** Of 281 E/W exterior slots across the
five `lot_demo_001` buildings, 266 carry dims in BUILDING space and 15 carry
them CANONICAL-X; library-wide the canonical-X count is **349 across 124
manifests**. Every one of them is an `_open` slot. No wall segment anywhere is
canonical-X.

**BOTH ARE CORRECT, AND THAT IS THE FINDING.** The two writers in
`deli_counter.py` disagree on purpose and each is right for its own consumer.
`_record_wall_slot` passes the box size straight through, already in building
space, and its module is placed UNROTATED. `_record_opening_slot` writes
`[width, wall_thick, height]` -- role-ordered, canonical-X -- which is the
frame `_slot_orient`'s own docstring names: "brings a canonically-authored
module (along X) onto this wall". Zoo's `plan_kit` documents the field as
`[w, d, h]` and reads it positionally, so the OPENINGS are the ones obeying
the published contract and the segments are the ones departing from it.

**`rot_y` IS THE KNOB THAT MAKES IT WORK AND IT IS ALMOST ENTIRELY INERT.**
Measured over 698 exterior modules in the same five buildings, slot `rot_y`
against the basis actually written into the composed scene:

    facing  kind   slot rot_y   scene rot   count   honoured
    E       open           90          90       8   yes
    N       open            0           0       9   yes
    N       seg             0           0     194   yes
    E       seg            90           0     133   no
    S       open          180           0      20   no
    S       seg           180           0     194   no
    W       open          270          90       7   no
    W       seg           270           0     133   no

Eight modules in seven hundred are placed at the angle their slot asks for.
Every other combination still lands correctly -- an S run travels along X like
an N run, so canonical-X is already right there, and a symmetric doorway
flipped 180 degrees is the same solid -- which is exactly why nobody has
noticed. This is CLAUDE.md's own named defect: a knob with no effect is itself
a defect, because the next person to turn it will be disbelieved by the
geometry. Anyone who starts honouring `rot_y` uniformly rotates 133 E-wall
segments by 90 degrees and turns each of those walls into a comb.

**WHAT IS NOT CLAIMED.** That any shipped artefact is wrong. Item 58's gate
reads ZERO placement drift against these same slots. The cost is paid by the
NEXT reader: the envelope gate's first pass trusted the field positionally and
printed a comb of phantom gaps, and its second pass had to recover the frame
by asking which axis carried the run's thickness.

**WHAT IT COSTS THE CORNER WORK, EXACTLY.** A corner slot is a NEW slot and
whoever writes it must pick a frame with nothing in the file to tell them
which. Item 58's TIER ONE escapes by luck: a square post is `[t, t, h]`, the
same triple in both frames and the same solid at any `rot_y`, so the
ambiguity cannot bite it. TIER TWO does not escape -- the moment Zoo authors
a corner with a front and a back, the frame and the rotation both become
load-bearing, and there is nothing to read them off. So this gates the
authored corner, not the collision one.

**WHAT WOULD CLOSE THIS.** Declare the frame per slot -- a `dims_frame`
field, `"building"` or `"canonical_x"`, written by both writers and READ by
every consumer -- or unify on one and re-derive the other's callers. Either
way `rot_y` gets the same treatment: honoured everywhere or removed, not left
right eight times in seven hundred. Plus the test that fails today: for every
exterior run, each slot's declared frame agrees with the extent the run
actually needs.

REFUTED 2026-08-24, kept because a retracted finding is cheaper to keep than
to rediscover -- the reading this replaces:

    "A slot's fit.dims is transposed on every E/W opening, so the field that
    states a module's size disagrees with its own neighbours... every
    transposed slot is an _open slot on an E or W wall... WHAT WOULD CLOSE
    THIS: either the writer emits fit.dims in the declared space for openings
    as it already does for segments..."

That reading had the measurement right and the owner backwards. It was
produced by comparing openings against their neighbouring segments and
declaring the minority wrong, without asking what either frame was FOR --
the same shape as this file's recurring defect, a cheap observable standing
in for an expensive truth. Reading `kit.py`'s `[w, d, h]` contract and then
the composed scene's node bases cost about ten minutes and reversed the
conclusion.


*STATUS: OPEN 2026-08-24 -- FOUND, PRICED, UNBLOCKED IN PRINCIPLE. Three
concrete preconditions measured against the shipped library, none of them
large; the species and its recipe need no authoring at all*

**64. Zoo built the corner module forty-one days ago and nothing has ever
asked for one.**
Found 2026-08-24 while deciding who should own item 58's corner.
`zoo_keeper/recipes/wallCorner.py` and
`zoo_keeper/genome/species/wallCorner.json` are both complete and both dated
2026-07-14. The recipe's own docstring is written against exactly the defect
item 58 measured: *"L-shaped corner module joining two wall runs... Pivot at
the OUTSIDE corner, ground level -- the corner drops onto the meeting point
of two DC wall runs with no offset math."* It emits `Corner_LegA` /
`Corner_LegB` with the shared column removed so the legs cannot z-fight, and
it returns collision boxes. The genome entry carries all five themes
including `rockay`, `collision: true`, a 300-triangle budget,
`params.thickness` defaulting to 0.3, and the keywords "wall corner",
"corner", "corner wall". Recipes auto-discover by filename, so
`recipes.get("wallCorner")` resolves today.

**NOTHING REQUESTS IT.** `deli_counter._slot_typename` never returns
`wallCorner`; neither does `kit.slot_typename`. The only other occurrence in
the whole tree is `SESSION_0821.md` listing it among the architecture species
that must stay theme-owned. So the capability was grown and the REQUEST was
never made -- item 62's protocol failing from the other end, and precisely
what item 40's "is this called?" sweep exists to surface.

**THREE PRECONDITIONS, EACH MEASURED AGAINST THE SHIPPED LIBRARY.**

1. **The declared height range excludes a quarter of the corners.** The
   genome says `height` 2.0-4.5 m. **252 of 988 corners** sit on taller
   storeys: 4.7 m (144), 5.2 (44), 5.7 (44), 6.2 (12), 5.1 (8).
2. **The filename would collide, and not hypothetically.**
   `kit.py`'s `exact = typ != "wallEnd"` makes `wallCorner` exact-fit, and it
   is in neither `PLATE_ROLES` nor `VOLUME_ROLES` -- so the stem carries
   WIDTH only, no depth and no height. Keyed on thickness alone,
   `wallCorner_<theme>_<style>_w30` would have to be **14 distinct solids**
   (fourteen storey heights at 0.30 m) and `_w35` three. One file wins. This
   is the collision `kit.py` documents three separate times and calls "the
   third time this exact collision has been paid for" -- `_d` for plate
   depth, `_v` for stairwell voids, `opening_tag` for apertures. The fix is
   the same one those got: put `wallCorner` where depth and height reach the
   stem.
3. **The gap report is never armed** -- item 62, measured there.

**WHY THE L CANNOT SIMPLY BE THE TIER-ONE PIECE.** Scaling an L's leg length
scales its thickness with it, so `wallCorner` is structurally exact-fit and
cannot ride the unit-box scale that makes a `t x t` post one module for the
whole library. That is the geometric reason item 58 ships a cube first and
this second, and not an ordering preference.

**WHAT WOULD CLOSE THIS.** The three above, then Deli Counter promoting its
corner slots from `wallEnd` to `wallCorner` -- one function in each repo,
paid once, when there is art to justify 18 modules per theme and style. Item
57 gets its corner vocabulary out of it, which is the actual prize.


*STATUS: OPEN 2026-08-25 -- MEASURED AT 24 DAYS AND ~20 RELEASES, AND CLEARED
THE SAME DAY. The propagation is still manual and still in no job, which is
the item; the backlog it accumulated is gone*

**65. The site copies go stale silently, and the detector that would say so
is in no job.**
Found 2026-08-25 while closing out roadmap 58. Deli Counter builds
`deli_counter/build/<id>.glb`; the geometry a SITE walks is a separate copy
under `lot/specs/<site>/buildings/`, and `tools/rebuild_buildings.py` is the
only thing that propagates one to the other. Its own docstring says so --
"a fix in `deli_counter.py` reaches a site only after that .glb is rebuilt
through Blender, and nothing else in the toolchain does it" -- and nothing
runs it.

**MEASURED.** Every site slot was stamped **2026-08-01**. Deli Counter was
at 0.102.1 and had passed through roughly TWENTY minor versions since --
0.84 through 0.102, including 0.96.0, whose whole subject was tiling
room-spanning slab visuals into light-budget-sized meshes (roadmap 54), plus
interactive state twins, ladder solidity, material-driven skin styles and
prop stem depth. `check_freshness.py` reported **57 distinct buildings across
62 site slots** stale. The rebuild bears the scale out: every file grew,
typically 1.5x to 2.5x -- `large_warehouse_a03` 293,860 -> 750,340 bytes,
`arena_a03` 208,720 -> 535,812 -- which is twenty releases arriving at once,
not any one change. `built 57, copied 5, stamped 62, failed 0, no-spec 0`.

**THE COST, and it is the part that matters.** Every measurement taken on a
SITE in that window was taken on geometry up to twenty Deli Counter versions
old -- walks, nav-gate readings, Laser Tag runs. That is this file's own
first rule, "name what produced an artefact before concluding anything from
it", failing for three weeks in the one place nobody was looking. Any
site-derived number from 2026-08-01 to 2026-08-25 should be re-read with that
caveat or re-measured.

**THE GUARD EXISTED AND WAS NEVER RUN.** `check_freshness.py` detects exactly
this, by content hash, and is registered in `tools/check_all.py`. It was
correct the whole time. `check_all.py`'s own docstring names the disease --
"that is how a guardrail stops being respected: not by failing, but by nobody
running it" -- and this is that sentence, measured at 24 days.

**WHAT WOULD CLOSE THIS.** Not "remember to run it". Either the propagation
becomes a job in the DAG so a DC version bump reaches the sites the way it
reaches the library, or the graders REFUSE a stale site instead of grading
it. The precedent for the second is already in the house and named in item
62 as a thing done right: `build_freshness.py` refuses to grade a stale
library. A walk, a nav-gate or a Laser Tag run against a site whose stamp
predates the builder should stop, not produce a number.


*STATUS: OPEN 2026-08-25 -- MEASURED, AND THE FIRST READING OF IT WAS WRONG
AND IS KEPT BELOW. The suite is green and shallower than the sentence that
recommends it*

**66. `verify-manifest` prescribes a remedy that under-proves what it
certifies.**
Found 2026-08-25 while sizing a re-cert. `level-factory verify-manifest`
reports DRIFT on five of ten tools and ends every one of those lines with the
same instruction: *"re-run the real-tool smoke and re-certify"*. That names
ONE suite. `docs/CERTIFY.md` requires three more legs -- the zoo walkabout
(real Blender), the engine leg (`nav_gate` / `godot_gate` / `roundtrip` /
`walktest` / `mp_smoke`, needs Godot), and the lux visual leg -- and says of
the real-tool smoke only that it is "what makes 'certified together' true
rather than asserted".

**WHAT THE SMOKE ACTUALLY PROVES.** Measured: `tests/real_tools` is 10 tests
in **4.95 seconds**. It runs the genuine CLIs -- a real `dispatch build` end
to end against real Lot output and LF's own staging, real patina, pixelcoat,
zoo plan, lasertag runner, lux driver -- and asserts real artifacts and no
blockers. That is adapter-and-contract depth, and it is worth having. What it
does NOT do, by construction, is build geometry: five seconds cannot launch
Blender, and `test_real_dispatch_handoff_from_lf_staged_inputs` says so in
its own docstring -- *"DC build needs Blender; use a realistic DC-schema
gameplay fixture."* The substitution is deliberate and correct for a smoke.
It is not a re-certification.

**SO THE RISK IS A GREEN RUN THAT MEANS LESS THAN THE SENTENCE SUGGESTS.**
Somebody follows the tool's advice, the smoke passes in five seconds, and the
set gets stamped on evidence that never touched the geometry the drifted
tools produce. On 2026-08-25 the drift was deli_counter +8 minor and lux +9 --
exactly the two whose output is geometry and light.

**SECOND, SMALLER.** Six of the ten real-tool tests are guarded by
`pytest.skip` on a missing fixture, and the suite surfaces no coverage count.
On this run one skipped -- the bundled dispatch example, whose `inputs` point
at pre-built tool outputs the dispatch repo does not ship. That skip is
deliberate, documented in the test, and its subject IS covered by the sibling
above; it is named here only because a suite where six tests can go quiet
without the total changing is one where a real absence would read the same
as this benign one.

**WHAT WOULD CLOSE THIS.** Make the remedy line say what the remedy is --
point at `CERTIFY.md`'s legs rather than one suite -- and have the smoke
print what it ran and what it skipped, so "green" carries its own coverage.
Neither is a code-path change; both are a check saying what it checked.

RETRACTED 2026-08-25, same hour, kept because the retraction is the useful
part: this was first written as "the only test with real cross-tool depth
skipped, so the suite certifies nothing". That was wrong. The end-to-end
LF -> dispatch bridge is `test_real_dispatch_handoff_from_lf_staged_inputs`,
it ran, and it asserts a real `dispatch build` with no blockers. The claim
was made from a skip message without reading the test beside it -- this
file's own first rule, reached for a third time in one session.

*STATUS: OPEN 2026-08-25 -- READ IN FULL, NOT RUN. Anyone who runs it loses a
CHANGELOG entry before it fails*

**67. `promote_factory.ps1` is a frozen one-off wearing a reusable name.**
Found 2026-08-25. `scripts/promote_factory.ps1` sits beside the tidy scripts
and is what a reader reaches for to promote a certified set. It cannot do
that. It is hard-wired to **1.3.0**, dated 2026-07-19: the factory CHANGELOG
entry is a literal heredoc naming pixelcoat 0.11.0 and zoo 0.35.0, it looks
for `factory.manifest.v1.3.0-candidate.json`, and it throws if the promoted
manifest's `factory_version` is not the string `"1.3.0"`.

Run today it would **prepend a two-month-old entry to `CHANGELOG.md` and
then fail** -- the write happens in step 1, the version assertion in step 3.
The damage is a corrupted changelog, and it lands before anything tells you
the script was wrong.

The live procedure is `docs/CERTIFY.md` Step 5, which is manual and correct.
This script is a transcript of one promotion that was left where a tool
belongs.

**WHAT WOULD CLOSE THIS.** Either parameterise it (`-Version`, entry text
from a file, candidate path derived) or move it to `_archive/` and let
CERTIFY.md be the only answer. Not both, and not left as it is: a script
named for a repeatable operation that destroys a file on its way to failing
is worse than no script.

*STATUS: CLOSED 2026-08-27 -- FIXED IN LEVEL FACTORY 0.50.0 AND PROVEN ON THE
RUN THAT FOUND IT. `aggregate` takes `selected_candidate` and never moves the
selection's own blockers to `blocking_eliminated`; `cmd_run` passes it from
the same `.selected` marker the approval gate writes. Opt-in with a `None`
default, so `cmd_validate` and every other caller are untouched. The
acceptance test was the same command on the same cached workspace before and
after, and only the reporting moved. 0.49.0: "2 blocker(s) belong to
eliminated candidate(s) and do not block the mission / Structural checks
passed (blockers open: 0, total findings: 119)". 0.50.0: "THE SELECTED
CANDIDATE WAS ELIMINATED: category5_baie_dore_001.candidate.seed_7001 / its
blockers still count, and this mission has no viable selection until another
candidate is approved / Blocked: unresolved blocking issues (blockers open:
2, total findings: 119)". **119 BOTH TIMES** -- findings are partitioned,
never dropped, and the count that did not move is the evidence that nothing
was invented to make the gate fire. Three checks stood behind it before the
run: the patch's own selftest against the installed module; eight cases in
`tests/unit/test_selected_candidate_blockers.py` that ALL fail against
0.49.0; and the 2026-08-12 patch's OWN selftest still passing unchanged, so
the fix this one overshot is not loosened. WHAT IS NOT CLOSED BY THIS: the
two `LUX_FIXTURE_COLOCATION` blockers are real and still open (0.25 m lamp
offsets on seed_7001) -- the gate now reports them, nobody has fixed them --
and this item's two secondary observations stand, that `lux_fixture_gate` was
marked `blocked` while `lux_apply` ran after it anyway, and that the gate
process exits 0 while printing `colocation_errors=2`. Neither is the
accounting defect this item names, and neither should be silently inherited
by whoever reads the closure.*

**68. A blocker on the candidate a human SELECTED is discounted because the
pipeline eliminated that candidate.** Found 2026-08-27 during `cold_7001`.
The run reported `Structural checks passed (blockers open: 0, total findings:
119)` on a mission whose selected candidate carried two unresolved blockers.

The chain, each link read off disk rather than reasoned about:

    .level_factory/approvals/category5_baie_dore_001.selected
        category5_baie_dore_001.candidate.seed_7001

    validation/category5_baie_dore_001.json -- 2 issues, severity "blocker",
    blocking: true, both candidate_id ...candidate.seed_7001
        LUX_FIXTURE_COLOCATION  20 marker(s) with no lamp within 0.10 m
        LUX_FIXTURE_COLOCATION  20 lamp(s) more than 0.10 m from any marker

    console
        1 candidate(s) eliminated (the rest carried on): ...seed_7001
        2 blocker(s) belong to eliminated candidate(s) and do not block the mission
        Structural checks passed  (blockers open: 0, total findings: 119)

The mechanism is `packages/validation/model.py:121`, in `aggregate`:

    elif issue.blocking:
        if issue.candidate_id in eliminated_candidates:
            blocking_eliminated.append(issue.issue_id)
        else:
            blocking_open.append(issue.issue_id)

**The predicate never consults `.selected`.** The docstring's reasoning is
right as far as it goes -- "the mission is not blocked by a candidate it
stopped building. N candidates exist so that some can be bad" -- and it is
correct for a candidate nobody chose. It has no clause for the one candidate
whose blockers are the only ones that can matter. So the discount fires
hardest exactly where it should not fire at all.

It is also the overshoot of a fix this same docstring records: the 2026-08-12
`lot_demo_001` case where an eliminated candidate wrongly blocked the mission
and "the run that continued reported as the run that halted". That was fixed
by discounting eliminated candidates. This is that fix going one step too far
in the other direction, and it is the more dangerous direction -- the earlier
bug made a good run look broken, this one makes a broken run look good.

**Two smaller things from the same episode, same theme -- the block did not
block.** `lux_fixture_gate` was marked `blocked` and `lux_apply` ran after it
and succeeded. And the gate process itself exited **0** while printing
`[fixture_gate] markers=37 spawned=37 colocation_errors=2`; the blockers were
manufactured downstream from its report, not from its exit code.

The underlying lamp defect is minor -- 0.25 m offsets. That is not the point.
A thing labelled `blocker` reached `blockers open: 0` and printed `passed`.

**WHAT WOULD CLOSE THIS.** `aggregate` needs the selected candidate, and a
blocker belonging to it stays in `blocking_open` whatever the scheduler did
with it. If a selected candidate is eliminated, that is itself the finding to
surface -- the mission has no viable selection -- not a reason to stop
counting. Whatever the remedy, the acceptance test is this run: `cold_7001`
must not print `passed`.

*STATUS: CLOSED 2026-09-05 -- THIS ITEM'S OWN ACCEPTANCE TEST, MET ON A REAL
RUN. It asked for distinct `shell.glb` sizes from a re-run cold workspace.
`cold_8001` wrote `lf_bank_block_001_8001.json` seed 8001,
`lf_bank_block_001_8102.json` seed 8102 and `lf_bank_block_001_8203.json` seed
8203 -- the CANDIDATE seeds, where before the fix all three would have read
1999, `bank`'s own authored preset literal -- and produced three distinct
shells: 410748, 410712 and 410752 bytes. The drop was never a drop: the seed
was never sent, because `new_level.py` had no way to take one. Built as Deli
Counter 0.103.1's `--seed` (0.103.0), threaded and fingerprinted in Level
Factory 0.54.0. WHAT REMAINS TRUE AND IS NOT THIS ITEM'S: the seed moves
seeded cover and its markers and moves no stairs, ladders, rooms or shell, so
BUILDING variety came from item 37's varied lot on this run, not from the
seed. Both landed together and the run cannot separate their contributions.*

**69. Deli Counter's seed never varies, so every candidate is the same
building.** Found 2026-08-27 during `cold_7001`. `candidate_count: 5` produced
five site layouts of one identical building set.

Every spec Level Factory handed Deli Counter carried the same seed:

    deli_counter/specs/lf_category5_baie_dore_001_7001.json   "seed": 1989
    deli_counter/specs/lf_category5_baie_dore_001_7405.json   "seed": 1989

Those two files differ in **exactly three lines**, all of them name strings
(`..._7001_stair_0` against `..._7405_stair_0`). Every geometric field is
identical, all five `shell.glb` are 625,404 bytes, and DC's own log confirms
it built `seed=1989` for the candidate named 7001. `1989` appears in the
batch, the brief and this file exactly nowhere.

Level Factory computes the candidate seed correctly and passes it --
`apps/cli/commands/__init__.py:282` is
`"seed": int(job.candidate_id.rsplit("_", 1)[-1])` -- and Lot, two lines
later at :287, receives it and uses it. **Where the seed is lost between that
dict and the file DC reads has not been located**, and this item does not
guess at it. The seed does reach the FILENAME, which narrows it.

The consequence is not that candidates are identical -- they are not. Lot
varies the layout, and the five differ measurably: Laser Tag scored 65 / 50 /
50 / 55 / 50, nav-qa passed 7001 and 7203 and failed the other three, and the
site spines ran 973 m to 1106 m. What is missing is building variety.
`candidate_count` is meant to buy shapes to choose between; it currently buys
arrangements of one shape.

**LF's own diversity check passes on this.** It printed `candidates: 5 built,
all distinct` -- true, and it compares assembled sites, so five byte-identical
building sets sail straight through it. A check can be honest and shallow at
the same time.

**WHAT WOULD CLOSE THIS.** Find the drop, thread the candidate seed to DC,
and re-run `cold_7001` -- five distinct `shell.glb` sizes is the acceptance
test. Then give `candidate_diversity.py` something to say about buildings, so
the check that reported `all distinct` here would not do so again.

**THE DROP, FOUND 2026-09-04. THERE WAS NO DROP.** The seed was not lost
between LF's spec dict and the file DC reads, which is where this item kept
looking. It was never put on the wire. `new_level.py` had no `--seed`
argument, so `adapters/deli_counter/__init__.py` used the candidate seed for
the spec FILENAME only -- `_level_name` returns `f"{base}_{seed}"` -- and the
`"seed"` field in the written spec is whatever the recipe authored.
`presets.py:1457` pins `"seed": 1989` inside `casino_tower`; `bank` pins
1999. Fifteen recipes pin one each, mostly years. So the figure varied by
brief exactly as this item measured, and the correct reading of that evidence
was not "the drop moves around" but "there is no drop -- you are reading the
preset's own constant".

**WHY THE ADAPTER DID IT.** Not an oversight; a documented decision resting
on a claim that is false. Its docstring said *"``new_level`` has NO seed flag
-- DC is deterministic per preset; candidate variation comes from Lot's site
assembly downstream"*, and `fingerprint_inputs` excluded the seed on the same
grounds, commenting *"the seed does NOT affect the building"*. The first
clause was true and the second was not: `presets.make` injects the seed
before the seed-consuming passes, `stair_place` rolls its probabilistic
extras on `spec.seed`, and `level_design.seed_cover` rolls each room's cover
on `f"{seed}:{room_id}:seed_cover"`. `stair_regression.py` has swept up to
100 seeds per preset since it was written, injecting at exactly that point.
The lever existed and had a proof harness; only the CLI could not reach it.

**WHAT SHIPPED.** Deli Counter 0.103.0 adds `--seed` to `new_level.py` and a
`seed=` parameter to `presets.make`, injected between the recipe and
`_finish_stairs`, which is the only place it does anything -- a seed written
into a finished spec changes the number the builder prints and no geometry.
Level Factory 0.54.0 passes `--seed <candidate seed>` and, necessarily, adds
the seed to `fingerprint_inputs`. That second half is not tidiness: without
it five candidates differing only by seed hash identically and cache-hit to
one build, which is the state being fixed, and the fix would have read as a
null result.

**MEASURED, AND NARROWER THAN THE FLAG SOUNDS.** Seven presets, two seeds
each (4001 / 9002), level name held CONSTANT so ids do not move:

    preset            stairs   ladders   volumes   markers
    casino_tower         0/1       0/1      8/14      8/23
    bank                 0/2       0/0      8/11      8/14
    warehouse            0/0       0/0      7/13      7/17
    hospital             0/2       0/0      8/18      8/22
    pawn_shop            0/1       0/2       2/6       4/9
    office               0/1       0/2      0/10      0/12
    parking_garage       0/1       0/0      0/25      0/12

The seed moves seeded cover volumes and the markers derived from them. It
moves NO stairs and NO ladders on any preset tested, and on `office` and
`parking_garage` it moves nothing at all -- `seed_cover` skips rooms with no
`combat_range` and rooms that already carry authored cover. Shell, rooms and
partitions compare byte-identical across seeds on every preset.

**A REFUTATION OF THIS SECTION'S OWN FIRST READING, KEPT.** The first pass
reported `stairs(2/2 differ)` on bank and `ladders(2/2 differ)` on office and
was about to be written up as stair variety. It was the instrument: a stair's
`id` embeds the level name, and the probe had varied the name along with the
seed, so every stair "differed" by its own label. Re-run with the name pinned,
every stair and ladder is identical. This is the third time in this file a
probe has reported its own inputs back as a finding.

**WHAT IS PROVEN AND WHAT IS NOT.** Proven: the flag exists and works
(`presets.make(seed=)` injection point verified by generating specs at 1989
and 7405 off `casino_tower` -- the override at the authored value is a no-op,
which is the control); the adapter emits `--seed 7405` and fingerprints two
candidate seeds distinctly; DC's suite is 583 passed / 2 skipped,
`stair_regression.py --quick` is 48 variants / 0 failures, and Level Factory's
full suite exits 0. NOT proven: no `.glb` was built, because that needs
Blender. This item's stated acceptance test -- five distinct `shell.glb` sizes
from a re-run `cold_7001` -- is exactly the right test and has not been run.
Until it is, "candidates now differ" is a claim about specs, not about
buildings.

**WHAT REMAINS, AND IT IS THE HALF THIS ITEM NAMED.** "What is missing is
building variety" still stands: five candidates now carry different cover and
the same shell, rooms, stairs and ladders. The seed cannot fix that, because
the shell is not a function of it. The lever is the PRESET -- item 37, one
shell placed N times, against 41 archetypes Deli Counter already builds --
and `candidate_diversity.py` still compares assembled sites, so it would
report `all distinct` on five identical buildings again tomorrow.

*STATUS: CLOSED 2026-08-27 -- BOTH GAPS FIXED AND PROVEN ON THREE SYNTHETIC
RUNS. `cold_run.py` now ATTRIBUTES rather than subtracts: a changed file is
matched against a `GENERATED` table of narrow patterns, each carrying the
reason it is there, and the report prints that reason beside every attributed
file so the claim is audited on every read instead of trusted once. Anything
unclaimed is counted, which is the safe direction. The table is deliberately
`deli_counter/specs/lf_*.json` and `CATALOG.md` rather than the directory --
the rest of `deli_counter/specs/` ships with the repo, and hand-editing one
of those until the output works is the failure mode roadmap 17 is named
after. `--observe` is the third journal kind, reported as its own figure and
counted toward nothing. The verdict now follows `max(noted, unattributed)`
instead of treating any hash hit as an intervention. Proven end to end on
three synthetic runs rather than by reading the code: (A) a run writing only
generated specs reports INTERVENTIONS 0 and exits 0, with the retry and the
observation on their own lines; (B) a silent edit to `deli_counter.py`
alongside a generated spec is still caught -- 1 attributed, 1 unattributed,
DISAGREEMENT printed, exit 1; (C) a SHIPPED spec hand-edited in that same
directory is still caught, which is the case a directory-wide skip would have
blinded. The selftest pins `cold_7001`'s six real paths verbatim from its own
`diff.json`, and pins six paths `GENERATED` must never excuse. `diff.json`
now carries `attributed` (with reasons) and `unattributed`. Runbook updated.
WHAT THIS DOES NOT DO: it does not make the table right, only auditable. If
another tool starts writing into a repo mid-run, the count goes UP until
somebody adds a line and says why -- which is the correct way round.*

**70. `cold_run.py` counts the pipeline's own writes into a tool repo as
interventions.** Found 2026-08-27 by running it. `--end` on `cold_7001`
printed `INTERVENTIONS: 1` for a run in which nobody edited anything.

All six hash-detected files were written by the pipeline:

    changed  deli_counter/specs/CATALOG.md
    added    deli_counter/specs/lf_category5_baie_dore_001_{7001,7102,7203,7304,7405}.json

Level Factory writes its per-candidate DC specs into `deli_counter/specs/`
-- a repo `cold_run.py` hashes -- and DC regenerates `CATALOG.md` as a side
effect. The tool does not hide this: it prints every touched file and says
"read diff.json before quoting a number", and classifying them took a minute.
But the headline figure was wrong, and a headline figure that needs a human
to correct it is the thing this instrument exists to avoid.

**The obvious fix is wrong.** Adding `specs` to `SKIP_DIRS` would blind the
detector to hand-editing a spec until the output works, which is the exact
failure mode item 17 is named after. The distinction needed is not WHERE a
file sits but WHO wrote it, and a hash cannot see that.

**A second gap, found the same way.** There is no way to record an
observation. A journal correction had to be filed with `--note` and landed in
the intervention column, inflating the count by one more. `--note`, `--retry`
and nothing else is one category short.

**WHAT WOULD CLOSE THIS.** Two changes, both small. Record the set of paths
the pipeline wrote during the run -- LF already knows them -- and subtract
that set from the diff before counting, leaving anything unaccounted-for as a
genuine intervention. And add a third journal kind (`--observe`) that reports
separately and counts toward nothing. Until both land, `cold_run.py`'s
printed total is a starting point for a human, not a result.

*STATUS: CLOSED 2026-08-28 -- RETRACTED AS FILED, REFRAMED, FIXED IN LUX
0.26.0, AND PROVEN TWICE: ONCE SYNTHETICALLY AND ONCE ON THE LEVEL THAT FOUND
IT. What was filed as "Lux spawns every fixture lamp 0.25 m off its marker"
was the ruler, not the geometry. `lux_light_loader.gd` sets
`r.mount_height = -0.25` in the `"fluorescent"` branch alone -- pendant,
streetlight and wall_pack are all 0.0 -- and Lux **0.20.0 shipped that
deliberately** off the 2026-08-23 walk ("Real tubes hang; ours do now"),
because a lamp flush on the ceiling plane streaks at glancing angles and
scorches a ring. The spawner puts the RIG ROOT on the marker, the rig hangs
its bulb below, and `check_fixture_colocation` compared marker to `Light3D`
against a flat 0.10 m tolerance -- measuring bracket-to-bulb and calling a
decision a defect. THE FIX (`patches/patch_lux_colocation_anchor.py`): a
light's anchor is its rig root when it was spawned into `LuxFixtureLights`
and the light itself otherwise, so both halves measure rig roots while
manifest-baked lamps still satisfy a marker. A per-type tolerance was
rejected as worse -- it would need updating whenever a mount height is tuned,
which is the coupling that caused this. PROOF 1, `lux/tools/colocation_selftest.gd`
(needs `--import` first; the class cache is why its first run died in a wall
of "Could not find type LuxRoot"): case 0 MEASURED the drop rather than
assuming it -- rig root 0.0 from its marker, bulb 0.25 below -- which matters
because a fix that stops the check complaining is indistinguishable from one
that stops it working; then a hung fixture passes, a rig moved 5 m fails with
BOTH findings and recovers, an unspawned scene reports dark hardware, and a
baked lamp counts. PROOF 2, `cold_7002` re-run: `lux_fixture_gate` blocked ->
succeeded, and `blockers open: 2, total findings: 55` -> `blockers open: 0,
total findings: 53`. **55 - 2 = 53**: exactly the two blockers left and
nothing else drifted, which a loosened tolerance would not have managed. The
mission then exported. NOTE THE MUTUAL CONCEALMENT: this gate had been wrong
since Lux 0.20.0 and nothing saw it, because item 68 was discounting its
blockers as belonging to an eliminated candidate. A silent gate and a lying
aggregator cancel out and the run reports clean.*

**71. The fixture co-location gate measures bracket-to-bulb and calls it a
floating light.** Filed 2026-08-27 as "Lux spawns every fixture lamp 0.25 m off
its marker", retracted 2026-08-28 on reading the producer. The retraction is
kept because it is the more useful half.

WHAT WAS FILED, and it was wrong: `cold_7001` and `cold_7002` both blocked on
a matched pair of `LUX_FIXTURE_COLOCATION` errors with the same worst distance
to the centimetre --

    cold_7001   markers=37 spawned=37   20 unmatched   worst 0.25 m
    cold_7002   markers=19 spawned=19   12 unmatched   worst 0.25 m

-- and a constant across two themes, two archetypes, two building counts and
two Zoo kits was read as a hardcoded displacement bug in the producer. It is a
hardcoded displacement. It is not a bug.

THE CHAIN, each link read in source:

    lux_light_loader.gd, "fluorescent" branch only
        r.mount_height = -0.25
        # A hand's width BELOW the anchor: a lamp sitting on the ceiling
        # plane spends half its sphere grazing the ceiling -- streaks at
        # glancing angles and a scorched ring around the fixture (same
        # walk). Real tubes hang; ours do now too.
      ... "pendant" 0.0, "streetlight" 0.0, "wall_pack" 0.0

    lux_fixture_spawner.gd
        rig.global_transform = mk.global_transform      # rig root ON the marker

    lux_fluorescent_rig.gd
        start := -(r.count - 1) * 0.5 * r.spacing        # count 1 -> start 0
        lamp.position = Vector3(start + i * r.spacing, r.mount_height, 0.0)
                                                        # -> (0, -0.25, 0)

    lux_validator.gd, check_fixture_colocation(scene_root, tolerance = 0.1)
        mp := marker.global_position
        d  := (mp - light.global_position).length()      # bracket to BULB
        if d > tolerance: dark += 1

**The offset is art direction somebody walked the level to find.** Removing it
to satisfy this check would re-introduce the streaking and the scorched ring
the comment describes. This is the third time this file has been caught
measuring with the wrong ruler -- the 222 phantom envelope gaps, the
reconstruction that "refuted" the float bug, and now this -- and the pattern is
always the same: an artefact disagreed with an expectation and the producer
was blamed before it was read.

**TWO BUGS WERE HIDING EACH OTHER.** This gate has been wrong for as long as
fluorescents have hung, and nothing saw it, because item 68 was discounting its
blockers as belonging to an eliminated candidate. Fixing the accounting on
2026-08-27 is what made the bad gate visible. A silent gate and a lying
aggregator cancel out, and the run reports clean.

**WHAT IS ACTUALLY OPEN.** The check blocks every level that contains a
fluorescent fixture, which is every interior this factory builds. It is the
one thing standing between item 17 and a cold run that reaches a package
passing its own gate.

**WHAT WOULD CLOSE THIS.** The contract the gate means to enforce is "a rig
landed on every marker, and no rig is floating in space unattached to
hardware". That is a statement about RIG ROOTS, not about bulbs -- where the
bulb sits inside its own rig is Lux's business and is tuned per type. So
compare marker positions against the spawned rig nodes rather than against
their `Light3D` descendants, which keeps the genuine failure (a rig nowhere
near any marker) catchable while ceasing to punish an intentional mount
offset. A per-type tolerance would also work and is worse: it would need
updating every time a rig's mount height is tuned, which is exactly the
coupling that produced this. Acceptance test: `cold_7002` re-run to a package
-- that workspace is cached up to the art pass, so it is cheap -- and a
synthetic rig placed 5 m from any marker must still be caught.

*STATUS: CLOSED 2026-08-29 -- CHECKED IN FOUR PLACES, AND THE ONE THAT SAVES
THE TIME IS `run` REFUSING BEFORE IT DISPATCHES ANYTHING. Shipped as Level
Factory 0.51.0. `packages/tools/themes.py` reads what the installed tools
actually carry -- Pixelcoat's `profiles/themes/*.json`, and the `styles` keys
across Zoo's species -- and reports Zoo coverage as a FRACTION rather than a
boolean, because "3 of 48 species carry it" and "48 of 48" are different
answers. `run` now refuses an art layer whose theme does not resolve, before
any job is dispatched, and only when an art layer is planned since graybox
needs no theme. `plan` prints the theme and whether it resolves on EVERY
plan, because a graybox plan is exactly when a reader is deciding whether to
add `--art`. `doctor` lists the themes Pixelcoat and Zoo carry -- not a
verdict on any brief, since doctor does not know which mission you mean, but
the list that makes `delco_1997` next to `delco` obvious. And the Pixelcoat
adapter's `validate_configuration` refuses a theme with no profile, naming
the path and what IS installed, so a run that reaches dispatch anyway fails
as an input-validation error rather than a bare `exit=1`. THE PATH WAS NEVER
A MYSTERY: `fingerprint_inputs` has always built exactly
`profiles/themes/<theme>.json` to hash the profile into the fingerprint. The
adapter knew where the file goes and never asked whether it was there.
PROOF: `tests/unit/test_theme_preflight.py`, nine cases covering the
`cold_7002` theme itself, partial Zoo coverage, an unparseable species being
skipped rather than guessed at, and an unconfigured repository NOT being
reported as a no. Eight of those pin a new module's contract and could not
have failed before it existed; the ninth is the real regression test and does
fail against 0.50.0. Stated that way rather than as "nine tests, all red
before", which would have been the flattering version. CLOSED ONE STEP EARLY,
CORRECTED 2026-08-30: the feature was right and the SUITE WAS RED FOR A DAY --
970/981 with seven failures, because the stub Pixelcoat repo under
`tests/fixtures/repos/` carried no `profiles/` directory at all while every
fixture batch names `theme_family: delco_1997`. The check is correct; the
fixture install was the thing that could not resolve its own theme. Six of the
seven were the cascade -- a refused art layer leaves no presentation preview,
which reads as `pending` where the facade expects `ready` -- and only
`test_presentation_export_and_portability` named the cause. Fixed by adding
that profile, shape copied key-for-key from the real
`pixelcoat/profiles/themes/delco.json` rather than invented. 970 passed, 11
skipped, 0 failed. THE LESSON IS THE STATUS LINE ITSELF: this item said CLOSED
while its own test suite disagreed, and nobody was looking at the suite*

**72. Nothing checks that a brief's theme resolves until the art pass is
already running.** Found 2026-08-28 in `cold_7002`.

The brief said `"theme": "delco_1997"`. Pixelcoat ships
`profiles/themes/delco.json` and no `delco_1997.json`; Zoo carries a `delco`
style and no `delco_1997`. The run found this out here:

    $ python3 -m pixelcoat.cli.main theme-library --theme delco_1997 ...
    pixelcoat: error: no theme profile for 'delco_1997' at
      ...\pixelcoat\profiles\themes\delco_1997.json
    (exit=1, duration=2.03s)

**Two seconds to fail, after the entire graybox leg had run.** `doctor` passed.
`plan` passed and printed a twelve-job DAG without a word about the theme.
Three candidates went through Deli Counter in Blender, then Lot, Laser Tag and
walktest -- tens of minutes of real compute -- and then the art pass stopped
on a file that could have been stat-ed before the first job was dispatched.

The missing profile is a content gap and arguably not a pipeline defect at
all. **The absence of the check is the defect**, and it is the same species as
the rest of this file: a precondition discovered only by violating it,
expensively, late.

**WHAT WOULD CLOSE THIS.** `plan` resolves the theme and says so -- which
theme each art stage will ask for, and whether it exists -- and `doctor`
reports the themes the installed Pixelcoat and Zoo actually carry. Neither
needs a new mechanism; both are a check saying what it checked, before
spending anything.

*STATUS: CLOSED 2026-09-05 -- MECHANISM FOUND, FIXED, AND PROVEN UNDER THE
CONDITIONS THAT BROKE COLD RUN 3. NOT the stated cause. LF's DC specs are
gitignored and none is tracked, and `_read_git_commit` excludes untracked
files ON PURPOSE so pipeline writes cannot bust the cache. `specs/CATALOG.md`
is TRACKED, `new_level.py` refreshed it on every spec write, and it indexed
the `lf_*` transients -- so the one tracked file the pipeline touches went
straight into the fingerprint. MEASURED: one `new_level.py --preset bank`
moved the revision from `099a9cd` to `099a9cd+dirty.cbd2f89b2b4fe547` with
CATALOG.md the only dirty tracked file. Fixed in Deli Counter 0.103.1 --
`catalog.py` skips `lf_*`, the same ids `building_library.index` already
refuses -- after which the same write leaves the revision byte-identical.
PROVEN ON `cold_8001`: DC and Lot revisions identical at the functional lock
and again after the art pass, no `+dirty` at either point; `deli_generate` and
`lot_assemble` CACHE-HIT where cold_7003 re-ran them 1.3 s and 6.6 s after the
lock; and the export exited 0. CATALOG.md does not appear in that run's
changed-file list at all. THE SECOND HALF IS NOT CLOSED BY THIS AND IS NOT
CARRIED HERE: the unexplained seven-finding difference between two identical
runs had its evidence destroyed and cannot be reopened from this run.*

**73. Two identical consecutive runs cached nothing and disagreed about what
they found.** Found 2026-08-28 in `cold_7002`, before any intervention.

`run bank_block_001` was issued twice in a row with nothing changed between
them. Neither invocation reused a single cached job -- all twelve re-executed
both times -- and the findings total moved:

    run 1   Structural checks passed  (blockers open: 0, total findings: 49)
    run 2   Structural checks passed  (blockers open: 0, total findings: 42)

**Half of it has a mechanism.** The build fingerprint carries the tool repo's
dirty state:

    "repository_commit": "009048b8c44bfc...+dirty.404bb756aa90cc84"

and Level Factory writes its per-candidate DC specs INTO `deli_counter/specs/`
(item 70). So the pipeline dirties the repo whose dirty hash it fingerprints,
and the next run misses the cache it just populated. That is the determinism
guarantee eating itself, and it is item 70's root cause with far more at stake
than a miscounted instrument.

**The observation that refutes the tidy version, kept rather than dropped:**
`cold_7001`'s re-run DID cache-hit Deli Counter and Lot under what look like
the same conditions. So the mechanism above is not the whole story, and this
item does not claim it is.

**The seven-finding difference has no explanation at all.** The scheduler
keeps only attempt `1/`, so run 2 overwrote run 1's reports and the two cannot
be compared. If Laser Tag is not reproducible at a fixed seed, that is a
serious finding about every grade this factory has ever recorded; if something
else drifted it is a different one. Nobody can say which from what is on disk.

**WHAT WOULD CLOSE THIS.** Two separable pieces. Stop the pipeline writing
into a repo it fingerprints, or exclude generated paths from the dirty hash --
then two identical runs should be all-cache, which is cheap and falsifiable.
And keep attempt directories instead of overwriting `1/`, so a run that
disagrees with its predecessor can be diffed against it rather than guessed
at. The second is what makes the first checkable.

**PROMOTED 2026-08-29 BY `cold_7003`, WHICH IS THE SAME MECHANISM WITH A
WORSE CONSEQUENCE.** The art pass was gate-clean and needed no intervention.
The export was then refused:

    gameplay-anchor registry changed after art pass
    interactive registry changed after art pass

`collision_fingerprint` did NOT drift -- the shape of the level is unchanged.
Only the two registries the lock also fingerprints moved. The timeline says
why, and it is item 70's root cause again:

    12:06:31.899   functional shell lock approved
    12:06:33.247   deli_generate re-evaluated   (+1.3 s)
    12:06:38.478   lot_assemble re-evaluated    (+6.6 s)

**The art run cache-missed and re-ran the very jobs the lock had fingerprinted
1.3 seconds earlier.** The lock is not wrong to refuse; the registries really
did change. It is fingerprinting a tree the pipeline is still writing to.

The lock was deliberately NOT re-approved. Re-approving clears the block and
destroys the evidence in the same motion, and the block is correct.

**This moves the item's weight.** As filed it was a determinism curiosity
worth two runs of confusion. It is now the reason item 17 -- the only item
that measures what the toolchain is for -- has no yes after three cold runs:
7001 exported on a gate later found broken, 7002 blocked on a missing theme
profile, 7003 blocked here. Evidence: `docs/findings/COLD_RUN_7003.md`.


*STATUS: OPEN 2026-08-29 -- MEASURED ACROSS TWELVE SHIPPED BUILDINGS WITH A
NEW INSTRUMENT, NO FIX ATTEMPTED. THE NUMBER IS NOT A ONE-BUILDING COMPLAINT
AND IT DOES NOT PLATEAU*

**74. Every wall in every building is the same 2.00 m module, and it gets
worse the longer the facade.** Found 2026-08-29 by walking `bank_block_001`
seed 7003 and then measuring what had been walked.

`_wall_span` (`deli_counter.py:756`) tiles each solid span into whole modules
of `_module_size()`, which defaults to 2.0 m, and puts the remainder in a
`wallEnd`. The shipped art confirms it from the other end: the whole themed
art directory for that level holds exactly two wall meshes,
`wall_delco_01_w200` and `wall_delco_01_w30`.

`tools/repetition_census.py` reads either the composed `.tscn` or Deli
Counter's own `*.slots.json` and reports, per wall run, the longest number of
IDENTICAL consecutive forms -- a form being a mesh AND the scale it was
stretched to, because DC scales `wallEnd` per slot and three wallEnds at three
widths are three things. Floor 1, ceiling the run's own segment count.

Twelve buildings off the shipped library:

    building              insts  stems  forms   reuse   worst  100%-runs
    large_warehouse_a03     356     13     33   10.79      28      7/15
    arena_a01               237     10     27    8.78      27      4/10
    arena_a03               238     16     32    7.44      26      3/11
    country_club_a01        179     13     23    7.78      20      5/10
    supermarket_a03         184     11     21    8.76      20      5/10
    bank_tower_a01          176      5     20    8.80      19      4/10
    mansion_a03             272     12     29    9.38      19      6/16
    depot_a01               110      9     23    4.78      13      0/6
    bank_tower_a03           99      5     23    4.30       9      0/6
    gas_station_a01          79     12     29    2.72       8      0/6
    pharmacy_a01             67     12     20    3.35       7      0/6
    strip_retail_a02         54     12     22    2.45       7      1/6

`worst_run` median 19. `large_warehouse_a03` has SEVEN runs that are 100% a
single form; `bank_tower_a01` has four, off five distinct stems across 176
instances. Every run in every building sits at pitch 2.00.

**The building that prompted this scored 14 -- below the median.** The
complaint was raised on the mildest example available.

**The shape of the table is the finding.** The small buildings score well
because their runs are too short to repeat, not because they were authored
better; a 14 m run holds seven modules and cannot hold twenty. Repetition is
linear in facade length and **there is no floor** -- a 100 m facade is fifty
identical panels. Any fix that does not scale with run length is a patch on
today's library rather than a position on the next one.

**THE FRAMING THIS WAS MISSING, from outside the codebase.** Kronenberger
(beyondextent.com, *Balancing Modularity and Uniqueness in Environment Art*):
modularity is not one grid, it is LAYERED. Large grid-aligned pieces buy
speed; smaller nested pieces on a finer grid -- or on no grid at all -- buy
apparent uniqueness without giving the speed back. Her working example is a
100-unit base grid dropping to 50 for smaller parts, "two-tier freedom while
maintaining alignment", and: "Even if the main pieces should be visibly
modular pieces, it looks always more interesting to break things up on a
smaller level."

**This factory has exactly ONE layer.** `_module_size()` is a single number,
2.00 m, and every measurement in the table above is that one number seen from
a different angle. The answer is not more variety at that layer; it is a
second one.

With a caveat this repo learned the hard way and an outside article cannot
know: her small off-grid decorative pieces sit PROUD of the surface, and this
pipeline already had those -- Patina emitted panel and pilaster orders, Zoo
built them standing off the face, and 546 of them ended up as non-collision
geometry in space a body walks through. That is why `arch.relief_parts` carves
inward instead. A second layer here has to be subtractive, or has to be
something other than geometry.

**WHAT WOULD CLOSE THIS.** Not a threshold -- where the gate belongs is a
taste call and the instrument deliberately reports no verdict. Either the
vocabulary grows with the span (a bay library selected per module rather than
one `DC_MODULE`, plus the `wallCorner` of item 64) or item 76's per-instance
work lands and item 78's second ruler is built to see it. Evidence:
`docs/findings/REPETITION_BASELINE.md`.

*STATUS: CLOSED 2026-08-29 -- ZOO 0.53.0 AND 0.54.0. THE RELIEF WAS TRACING
THE MODULE GRID BY TWO SEPARATE MECHANISMS AND BOTH ARE GONE: `bay: 2.4`
AGAINST A 2.00 m MODULE MADE `round(w/bay)` 1, SO NO WALL IN ANY BUILD EVER
GOT AN INTERIOR PIER; AND FLUSH FULL-WIDTH END PIERS PUT A DOUBLE-WIDTH STRIP
AT EVERY SEAM AND NOWHERE ELSE. NOW `bay: 1.0` WITH HALF-WIDTH ENDS, SO A SEAM
IS GEOMETRICALLY IDENTICAL TO A BAY LINE. MEASURED ON THE NORTH ELEVATION,
SPECTRAL POWER AT THE 2 m MODULE PITCH FELL 1548 -> 1044 WITH THE VERTEX
LAYER HELD CONSTANT -- A 33% REDUCTION, NOT THE 5.6x THE CONFOUNDED FIRST
COMPARISON CLAIMED. TWO REGRESSION TESTS PIN IT AND BOTH FAIL AGAINST THE OLD
GEOMETRY. `pier` ALSO RAISED 0.02 -> 0.1 IN 0.54.0 BECAUSE 0.02 IS 1.3 PIXELS
AT THE ELEVATION'S 66.7 px/m AND THE RHYTHM WAS CORRECT AND INVISIBLE. THE
RESIDUAL IS ITEM 79: ARTICULATION COMPUTED PER MODULE CAN CHANGE THE RHYTHM'S
FREQUENCY BUT NEVER ITS PHASE*

**75. Delco's facade relief was drawing the module grid it exists to break
up.** Found 2026-08-29, while looking for why item 74's buildings read as
moulded plastic rather than merely repetitive.

Delco carried no `relief` block, so it fell through to `arch.RELIEF`'s
defaults. Run on a real 2.0 x 0.3 x 3.6 module those produce:

    Pier_0   center=(-0.93, 0, 0.165)   size=(0.14, 0.30, 3.03)
    Pier_1   center=( 0.93, 0, 0.165)   size=(0.14, 0.30, 3.03)
    Field_0  center=( 0.00, 0, 0.165)   size=(1.72, 0.20, 3.03)

`relief_parts` places its end piers FLUSH with the module edges, which is
right on its own terms -- one centred on the edge would hang half its width
into the neighbour and double at every seam. But two flush 0.14 m piers MEET
at each seam. What the eye gets is a 0.28 m wide, 3.03 m tall, full-depth
strip standing 0.05 m proud of the field, repeating at exactly the module
pitch for the length of the building.

`arch.py:387` says the per-style override "is where the VARIATION belongs --
one rhythm on every wall of every building is the failure mode this replaces."
Exactly one style block in the whole genome library used the hook: `wall.json`
`rockay`, setting `reveal: 0.0` -- to turn relief OFF.

**FIXED IN ZOO 0.51.0**, not verified. `delco` now carries `pier` 0.02 and
`reveal` 0.015; the seam strip goes 0.28 m -> 0.04 m and 0.05 m -> 0.015 m
proud. Plinth and cap are kept deliberately: they are the same height on every
module so they run continuous ACROSS seams, and horizontal bands are the cue
that reads as one building rather than a stack. Nothing structural moves --
relief is not in `kit.module_stem`, so the resolver sees the same filenames;
the collider is built from `slab` and not `visual`, so no collision box
changes; `relief_parts` guarantees the outer bbox stays exactly (w, d, h).

**WHAT WOULD CLOSE THIS.** A rebuilt level, looked at. The numbers above are
geometry and are settled; whether 0.02 reads as relief or as mush is not, and
`repetition_census.py` is structurally blind to it (item 78). `{"reveal": 0.0}`
-- rockay's value -- is the other end of the dial and flattens the wall to a
single panel, plinth and cornice with it.

*STATUS: OPEN 2026-08-29 -- FOUR MECHANISMS READ IN THE CODE, NONE REACHABLE
FROM A BRIEF. ONE OF THEM IS BLOCKED BY A SINGLE MISSING MODEL FIELD. THE
WORLD-SPACE ONE IS NO LONGER A CANDIDATE BUT A RESULT: RE-MEASURED AGAINST A
NULL RUN (ITEM 90) IT CLEARS THE FLOOR ON 7 OF 8 SHOTS, max |delta| 43-217
AGAINST 7-16, AND IT WAS CONFIRMED BY EYE TO FIX ITEM 88. THE EARLIER
"13.6-19.0% OF PIXELS" READING SURVIVES ITS OWN AUDIT, THOUGH THE FLOOR IT
WAS QUOTED AGAINST DID NOT*

**76. Every mechanism this factory has for making two copies of one module
look different is implemented, and none of them is wired in.** Found
2026-08-29, surveying what item 74 could be fixed WITH.

1. **Patina's theme is always empty.** `commands/__init__.py:558` reads
   `getattr(model, "patina_theme", "") or "default"`, and `patina_theme` is
   not a field on the brief model or on `mission.brief.schema.json`. The
   comment directly above it says to "pass an explicit patina_theme if the
   brief sets one" -- no brief can. Every level ever built got `"default"`.
   Patina ships a `delco_1997_gas_station` builtin, named in that same
   comment, carrying water stains, paint chips, rust streaks, oil, scuffs and
   vertical banding. It has never been selected.
2. **`art_mode` is hardcoded `"vertex-color"`** on both branches
   (`commands/__init__.py:552, 565`), which short-circuits Patina's entire
   texture half.
3. **`--slot-variation` is never passed.** Patina implements it, plus an
   `instances.json` whose own schema note says it "breaks modular
   repetition". Nothing in level_factory mentions either.
4. **Pixelcoat's generation-7 stack is unreachable from a theme.** A theme
   profile is a 24-entry lookup table and nothing else; `weathering.py`'s edge
   wear, cavity grime, streaks and rust, and the `variations` maps, live on a
   `pixelcoat build <recipe>` path the planner never plans.

**RETRACTED IN THE SAME BREATH, so it is not carried forward as a fifth.**
`cube_project_uv`'s unused `uv_offset` looked like the cheapest fix here and
is not one. There is ONE `wall_delco_01_w200.glb` and it is instanced, so any
offset passed at build time shifts every copy together. The docstring that
made it look right is describing dressing covers, which are built at the
origin and transformed afterwards. Kit modules are a different situation and
the conclusion does not carry across.

**WHAT WOULD CLOSE THIS.** Not all four. The question of which LAYER should
own variation -- kit vocabulary (74), module surface (75), or per-instance
(here) -- is deliberately NOT settled in this item, because the evidence that
would settle it is item 75's rebuilt level and nobody has seen it. Writing the
doctrine first would be writing it from inference, which is how the `uv_offset`
retraction above happened.

*STATUS: OPEN 2026-08-29 -- COST ONE AMBIGUOUS COUNT ON `cold_7003`, AND THE
AMBIGUITY IS UNRESOLVABLE FROM WHAT IS ON DISK*

**77. `cold_run.py --begin` cannot tell that a run is starting mid-edit.**
Found 2026-08-29 while closing `cold_7003`.

`--begin` hashes 2357 source files and proceeds. It has no idea whether those
files were mid-change. On `cold_7003` a tool file changed six minutes into the
run and 55 seconds before the first job wrote output:

    11:59:22   --begin, 2357 files hashed
    12:05:38   level_factory/apps/cli/commands/__init__.py written
    12:06:33   deli_generate first output

The instrument correctly counted it and correctly flagged the disagreement.
But an edit made DURING a run to rescue it and an edit that was simply still
landing when `--begin` fired are indistinguishable afterwards: `before.json`
stores hashes, not content, and there is no backup sidecar. The likeliest
account -- the item-72 patch re-application arriving late -- cannot be proven,
so `cold_7003` carries a 1 that may or may not describe a defect.

**WHAT WOULD CLOSE THIS.** Record each tool repo's dirty state at `--begin`
and print it, so a later change in a repo that was ALREADY dirty is
interpretable instead of archaeological. Note the wrinkle that makes this
non-trivial and worth thinking about rather than just adding: the repos are
routinely dirty by design, because the pipeline writes its DC specs into
`deli_counter/specs/` (items 70 and 73). The check is not "refuse if dirty",
it is "say what was dirty, so the diff can be read".

*STATUS: NARROWED 2026-08-29 -- FILED AS "NOTHING MEASURES APPEARANCE", WHICH
WAS FALSE AND WAS WRITTEN WITHOUT LOOKING IN `tools/`. FOUR INSTRUMENTS
ALREADY DO; NONE HAS EVER BEEN POINTED AT THE KIT PATH, AND ON THAT PATH THE
THING THEY MEASURE CANNOT EXIST YET*

**78. Nothing measures how a level LOOKS -- only what it is made of.** Found
2026-08-29, immediately after building `repetition_census.py`.

The census measures the repetition of the FORM VOCABULARY: which mesh, at
which size, how many, how many in a row. That makes it the right instrument
for item 74 and the WRONG one for item 76. Per-instance variation changes how
two copies of one mesh look without changing that they are one mesh, so a run
of fourteen would still read fourteen after `--slot-variation` landed. A flat
number would not be that work failing; it would be this ruler not pointed at
it.

The limitation is written into the tool's own docstring so it is not
discovered by being surprised. It is filed here because of what it implies:
**item 76's work cannot currently be gated, only admired.** Every other claim
in this factory is measured, and the one the buildings are actually judged on
would not be.

**CORRECTED THE SAME DAY, AND THE CORRECTION IS THE POINT.** This item was
filed claiming no instrument reads appearance. `tools/` was not opened before
writing it. Four already do:

  * `vertex_variation.py` -- COLOR_0 per family in a GLB, reporting BETWEEN
    (spread across instances) and WITHIN (spread inside one mesh) separately,
    because they fail for different reasons. Built for the dressing path,
    where it caught 2,098 covers exporting pure white.
  * `look_shots.py` / `look_shots.gd` -- renders fixed cameras and writes
    per-shot luminance statistics.
  * `shot_diff.py` -- compares two shot runs, statistics always and pixels
    with `--images`, and has a `--gate`. Its own docstring lists this class of
    defect, including "1374 panels sampling one patch of concrete".
  * `facade_rules_sweep.py` -- runs the real Patina facade rules over all 109
    shipped manifests offline, no Blender, no Godot.

**POINTED AT THE KIT FOR THE FIRST TIME, 2026-08-29**, on the module that
appears 66 times in `bank_block_001`:

    wall_delco_01_w200.glb
    family          n     mean   BETWEEN sd   WITHIN sd
    Wall_Field      1   0.7857      0.00000     0.10957
    Wall_Base       1   0.7929      0.00000     0.11508
    Wall_Cap        1   0.8245      0.00000     0.10366
    Wall_Pier       2   0.8011      0.00375     0.10447
    NO PER-INSTANCE VARIATION (3 families): every copy is the same colour

    lf_bank_block_001_7003_dressing.glb
    Cover_edge_strip   64   0.8140    0.02060     0.09980
    ... every family varies both between instances and within one

Two facts in one reading. **WITHIN 0.11 on every wall part is item 81's
lozenge with a number on it** -- panels sitting at 79% brightness with an 11%
spread painted across each one. And the dressing path varies between instances
while the kit path does not, which is item 76 measured rather than argued.

**SO THE REAL GAP IS NARROWER AND WORTH STATING EXACTLY.** For the DRESSING
path, an instrument exists, works, and has caught real bugs. For the KIT path,
`vertex_variation` reports zero between-instance variation and will keep
reporting zero however it is improved, because each stem is ONE mesh instanced
at scene level -- there is no per-instance channel for it to read (items 76 and
80). And for composition -- whether a facade reads as authored -- `look_shots`
says the honest thing in its own docstring: "a histogram cannot tell you a
level looks generated."

**WHAT WOULD CLOSE THIS.** Two things, neither of them a new instrument from
scratch. Run `vertex_variation` over the kit as part of the art pass, so the
zero is reported by the pipeline instead of discovered by a walkthrough. And
give `look_shots`/`shot_diff` a facade framing -- a straight-on elevation shot
per face -- so a composition change has a before and after that is not a
person's memory. Both are wiring, which is the shape of nearly everything in
items 76 through 82.

*STATUS: OPEN 2026-08-29 -- THE FRAME ITEMS 74 THROUGH 76 ARE SYMPTOMS OF.
NAMED FROM A WALKTHROUGH CRITIQUE, GROUNDED IN THE EMITTER, AND NOT A TUNING
PROBLEM: THE OBJECT THAT WOULD CARRY A COMPOSITION DOES NOT EXIST*

**79. Nothing in the pipeline represents a facade, so nothing can compose
one.** Found 2026-08-29, walking `bank_block_001` seed 7003 after items 74 and
75 had both been addressed and the building still read wrong.

The critique that produced this, recorded because it is the most exact
statement of the problem anyone has made and it is not the author's:

> The facade reads less like a building and more like a row of individually
> generated facade pieces placed beside one another. [...] The repetition sits
> in an uncanny middle ground: the pieces are too similar to feel
> intentionally varied, too inconsistent to establish a clean architectural
> rhythm, and their differences do not appear connected to structure,
> function, or composition. [...] Fragmented rather than composed. Repeated
> rather than rhythmic. Varied without apparent reason. Detailed locally but
> undesigned globally.

**Every bullet of it has a line number.** `_emit_wall_run`
(`deli_counter.py:893`) is the whole of the facade logic:

    cursor = -full / 2.0 + inset
    for j, h in enumerate(carve):            # openings, sorted by position
        k = self._wall_span(..., cursor, h["u"] - h["w"]/2.0, k, material)
        self._opening_piece(..., h, j, material)
        cursor = max(cursor, h["u"] + h["w"]/2.0)
    k = self._wall_span(..., cursor, full/2.0 - inset, k, material)

It receives ONE run -- one face of one storey -- plus the openings already
placed by `_exterior` as a fraction of that run. It marches left to right,
fills the gaps with whole 2.00 m modules, and stops.

  * *"the upper and lower rhythms do not align"* -- each storey is a separate
    run with separately placed openings. The function cannot align them
    because it never sees another storey.
  * *"nothing appears to carry weight downward"* -- there is no vertical
    structure to carry it. The module grid restarts at `-full/2 + inset` on
    every run independently.
  * *"variations in width and opening appear arbitrary"* -- they are
    remainders. `rem = b - (a + n*M)` is arithmetic left over from tiling, and
    `size_mod="end"` turns it into a scaled `wallEnd`. No width in the
    building was chosen.
  * *"corners simply stop the pattern"* -- literally. `corners=True` seats one
    scaled unit box at each end of the run (item 58).
  * *"nothing groups the small modules into larger architectural masses"* --
    the only grouping concept in the emitter is "the span between two
    openings", and its output is N copies of one module.
  * *"no clear hierarchy... the entrance is not strong enough to organize the
    composition"* -- the entrance is an opening in a list, sorted by
    coordinate. Nothing marks it as primary.

**This is the frame, and 74 through 76 are inside it.** The module vocabulary
(74), the relief (75) and the per-instance variation (76) are all answers to
"why do two pieces look the same". The critique is not about two pieces. It is
that the pieces never had a whole to belong to. Confirmed by elimination in
the same session: 75's relief was quietened and 74's census did not move, and
the building still read as a row of boxes, because neither touches this.

**WHAT WOULD CLOSE THIS, and it is a new capability rather than a fix.**
Something upstream of slot emission that owns ALL storeys of ONE face at once
and decides, before any module is placed: a bay grid every storey lands on; a
hierarchy that marks one bay primary; grouping into masses larger than a
module; and corners as a designed condition rather than a remainder. Deli
Counter is the right home -- it already owns the floorplan the openings come
from -- and `_emit_wall_run` becomes the thing that EXECUTES a composition
rather than the thing that substitutes for one.

**WHAT THIS ITEM MUST NOT BECOME.** A list of architectural rules invented by
whoever is holding the keyboard. The grammar -- what a delco facade actually
wants -- is a design decision and does not belong in a roadmap item written by
the person who could not see the problem until it was pointed out. This item
owns the MECHANISM: that there is nowhere to put a grammar. Evidence:
`_runs/walk_wear0`, and the three walkthrough screenshots of 2026-08-29.

*STATUS: OPEN 2026-08-29 -- DELI COUNTER'S GUARANTEE SURVIVES THE ART PASS;
THE STEP AFTER IT IS WRITTEN IN TWO HALVES AND NEITHER IS WIRED. RAISED AS A
PERFORMANCE CONSTRAINT ON 74 AND 79, AND IT DECIDES THE LAYER QUESTION 76
DECLINED TO SETTLE. NOW WITH A REASON TO MOVE: WORLD-SPACE UVs ARE MEASURED
AND CONFIRMED TO FIX BOTH THE PER-MODULE TEXTURE RESTART AND ITEM 88'S
STRETCH IN ONE MECHANISM, AND THE ONLY THING BETWEEN THAT AND THE SHIPPED
BUILD IS THAT `--triplanar` LIVES IN `walk_themed.py` AS A RUNTIME FLAG THAT
PRINTS "NOT what ships". THE UNMEASURED BILL IS FILL RATE: TRIPLANAR SAMPLES
THREE TIMES PER MAP, SO NINE SAMPLES ACROSS ALBEDO/ROUGHNESS/NORMAL, AND
NOBODY HAS PUT A FRAME TIME ON IT*

**80. Deli Counter's one-mesh-in-VRAM discipline is not carried any further
than the export, and the two pieces that would carry it are both dead code.**
Raised 2026-08-29 as a constraint on how items 74 and 79 may be answered.

**The discipline, which is real and well kept.** `Builder._module_cache`
(`deli_counter.py:78`): identical modular segments keyed by role+dims, and
repeated placement assets keyed by asset id, link a SINGLE mesh datablock.
`_box(..., share_key=...)` (`:251`) bakes the size into the shared mesh and
leaves object scale at 1 -- deliberately, "so an art pass on the module isn't
stretched differently per instance". `_instance_module` (`:186`) imports a GLB
once and links the cached datablocks. `_paint` (`:386`) knows about it: the
share key is role plus dims, so a shared mesh always has one role and painting
it once is correct. Result: "the glTF export carries one mesh + N nodes ->
Godot loads one Mesh resource instanced N times."

**It survives the art pass.** Measured on the composed `bank_block_001`:
**241 scene-node instances against 36 shared PackedScenes.** One mesh and one
texture set per stem, exactly as promised, with the themed modules swapped in
for the greybox ones.

**And it stops there.** 241 nodes is 241 separate instances as far as the
renderer is concerned. Nothing folds them into GPU instancing, and there is
therefore no per-instance channel at all -- which is the same absence item 76
reports from the other end.

**BOTH HALVES OF THE NEXT STEP ARE ALREADY WRITTEN AND NEITHER IS CALLED.**

  * `level_factory/packages/exporting/dressing_scene.py` is a complete
    MultiMesh exporter. Its docstring: "3,948 instances of four meshes is the
    case instancing exists for -- as MultiMeshes that is four draw calls". The
    buffer layout was SETTLED 2026-08-19 and isolated in `multimesh_floats()`.
    **Grep for `dressing_scene` outside itself returns nothing.** It carries
    per-instance TRANSFORM only -- no colour, no custom data.
  * Patina's `--slot-variation` emits `instances.json`, schema
    `patina-instances/1`, described in its own source as "per-slot instance
    color/custom_data; keyed by slot_id; feeds MultiMesh per-instance buffers,
    breaks modular repetition". The level_factory adapter never passes the
    flag and nothing in `packages/` mentions the file.

One writes the buffer and cannot vary appearance; the other computes the
variation and has nothing to write it into. They are two halves of one
feature, built separately, connected to nothing.

**WHY THIS DECIDES THE LAYER QUESTION.** Item 76 declined to say whether
variation belongs to kit vocabulary, module surface, or per-instance data,
because the evidence was not in. This is evidence, and it is not aesthetic.
Growing the vocabulary (item 74's obvious answer -- a bay library, more
widths) mints a new stem per width per style per theme, and every stem is a
new mesh AND a new texture set in VRAM: cost linear in variety. Per-instance
variation is one mesh, one texture set, and a buffer: cost constant in
variety. The two goals -- fewer draw calls and less visible repetition -- want
the same change, which is rare enough to be worth acting on.

**THE TENSION, NAMED BEFORE ANYONE SPENDS A WEEK ON IT.** Godot budgets
positional lights PER INSTANCE, and this factory already knows it: `_arch.py`
tiles plate visuals into smaller meshes precisely to buy more light budget
(item 54), and the walk project ships `limits/opengl/max_lights_per_object=16`
against a level Lux spawns ~150 fixtures into. **A MultiMeshInstance3D is ONE
instance.** Folding 66 wall placements into one MultiMesh hands all 66 a
single 16-light budget. So MultiMesh is plainly right for the case
`dressing_scene.py` was written for -- thousands of small props -- and is NOT
obviously right for walls in a fixture-lit interior. That has to be measured
before it is assumed, and `tools/light_census.py` is the instrument that would
measure it.

**CORRECTED 2026-08-29 BY AN OUTSIDE SOURCE, and the correction matters.**
The paragraph above says per-instance data is "the only VRAM-bounded way to
express a composition". That is false, and it was reasoned from this codebase
alone. Lea Kronenberger, *Balancing Modularity and Uniqueness in Environment
Art* (beyondextent.com), names two mechanisms that are equally bounded and
cheaper:

  * **World-space / triplanar projection.** UVs computed from world position
    rather than from the mesh. "Ignores UV seams, allowing aggressive scaling
    and rotation without visible stretching" -- and her arcs are "the exact
    same model, just stretched and rotated differently".
  * **Shader colour variation tied to world position.** Every instance is at a
    different world position, so the variation is free: no buffer, no
    `instances.json`, no MultiMesh, and therefore NO COLLISION WITH THE LIGHT
    BUDGET, which is the objection that made walls the hard case above.

**AND THE FIRST ONE COLLAPSES ITEM 74 INTO THIS ONE.** Deli Counter already
has a mesh that fills any width for free -- `wallEnd`, "authored as a UNIT box
and the size rides as a per-slot scale: one module fits every remainder". It
is confined to filler for exactly one reason, stated at
`_record_wall_slot`: "Full-width walls and openings stay exact-fit (scale 1)
so themed art is never stretched." **World-space UVs delete that reason.** A
scaled box under a world-projected material does not stretch its texture, so
the VRAM-free trick stops being usable only for hidden remainders and becomes
usable for every wall at any width. Item 74 wants width variety; item 80 says
variety must not be linear in stems; this is the mechanism where both are
true at once.

**WHAT WOULD CLOSE THIS, reordered by the above.** World-space UVs on the kit
materials first: no new mesh, no new texture set, no buffer, no light-budget
question, and it is testable in one art pass with `look_shots` elevations
either side. MultiMesh second and only for dressing, where the exporter
already exists and the light budget does not apply -- and measured with
`light_census.py` before any wall follows it. `instances.json` third: still
worth having, no longer the cheapest thing available.

*STATUS: NARROWED 2026-08-29 -- THE MECHANISM IS REAL IN THE FILE AND INERT IN
THE ENGINE. REMOVING THE WEAR ENTIRELY MOVES THE RENDER BY NOTHING ABOVE THE
INSTRUMENT'S OWN NOISE FLOOR, SO WHATEVER OUTLINES THOSE PANELS IS NOT THIS.
THE LAYER NOT ARRIVING IS NOW ITEM 84. AND THE THING THAT WAS ACTUALLY
OUTLINING THEM HAS BEEN FOUND AND FIXED -- IT WAS VERTEX NORMALS, NOT COLOUR;
SEE ITEM 86, SHIPPED AS ZOO 0.52.0 AND CONFIRMED BY EYE. THIS ITEM'S OWN
QUESTION -- WHAT WEAR SHOULD DO ON A MESH WITH NO INTERIOR VERTICES -- IS
UNANSWERED AND IS WHY 84 CANNOT SIMPLY BE SWITCHED ON*

**81. Zoo's wear noise runs at the mesh's vertex density, and a wall module
has eight vertices.** Found 2026-08-29 from a walkthrough screenshot in which
every 2 m panel read as a separate soft lozenge, bright in the middle and dark
at its own edges, fifteen in a row.

`wear_colors` (`bpylayer/geometry.py:493`):

    dark = min(1.0, concave * 1.5 + noise * 0.5) * wear

`concave` is the average edge angle at a vertex. It darkens real interior
corners and is right. **But a wall module is a box, so no vertex is concave**,
that term is zero, and only `noise * 0.5 * wear` survives. Delco's wall
carries `wear: 0.35`. Eight vertices, each handed an independent random
darkening, then interpolated across the face:

    wear=0.35   corner brightness 0.852 .. 0.955   spread 10.2%

**The docstring calls that term grime, and on a dense mesh it would be.** On a
four-vertex quad the only spatial frequency available is the panel itself, so
instead of grime it paints one soft blob per module. The RNG is seeded from
the filename stem with a hardcoded `0` (`bpylayer/build.py:187`), so every
instance gets the SAME blob -- the same bright centre, the same dark corners,
and therefore the same hard discontinuity at every seam. The wrong frequency,
repeated exactly.

Ruled out in the same pass: `ambient` is not the cause. `_ambient_tint` keys
on the face normal's up-component, and a vertical wall face has `nz ~ 0`,
which lands the tint between cool and warm at near-neutral. Only `wear` varies
across a vertical panel. And it is lighting-sensitive by construction -- a
vertex colour multiplies the lit result -- which matches the observation that a
brighter key made it worse rather than better.

**MEASURED 2026-08-29, and the numbers say something stronger than the
arithmetic did.** `vertex_variation.py` on the module placed 66 times, and the
same module rebuilt at `wear: 0.0`:

    wear 0.35   Wall_Field mean 0.786   WITHIN sd 0.10957   colour 0.642 .. 0.982
    wear 0.00   Wall_Field mean 0.983   WITHIN sd 0.01560   colour 0.974 .. 0.991

The residual 0.016 at zero wear is `_ambient_tint` across differently-oriented
faces, which is what it should be. Everything else is the wear layer: panels
sitting a fifth darker than unshaded, with a 34-point spread across one 2 m
face.

**AND WHERE THAT SPREAD LANDS IS THE WHOLE PROBLEM.** Reading the GLB's own
POSITION and COLOR_0 back:

    Wall_Field: 85 vertices, 100% of them on the panel's outer shell
                darkest quartile: mean normalised radius 1.000

**A bevelled box has no interior vertices.** Every vertex it owns is on its
perimeter, so per-vertex shading is structurally incapable of putting grime
anywhere except the module's own edges and corners. This is not a value that
is too high. It is a function written for meshes with interiors, applied to
meshes that have none.

The consequence in one line, and it is the observation that found this: *"in
real life a flat wall wouldn't have repeating shadows across it even if it was
made with multiple pieces of stone"* -- **the shading is baked occlusion drawn
at the module joint, which is the one place on a facade with no occlusion at
all.** Real ambient occlusion darkens where two walls meet or where a ceiling
overhangs; this darkens where two coplanar panels abut. It is not merely wrong
in magnitude, it is wrong in location, and it lands on exactly the seams the
composition needs to hide.

Confirmed independent of everything else tried the same day: the corner
shading survives world-space triplanar (it is vertex colour, not UV) and
survives removing all ~150 fixtures (it is baked, not lit) -- see item 83.

**PROBE RUN AND READ, 2026-08-29, AGAINST A MEASURED NULL.** One art pass,
one variable, `shot_diff --art-changed` confirming the art digest moved
(`c0d9e71f7dcc` -> `f36543946260`) and the treatment did not. And, by accident,
a NULL EXPERIMENT the run before it -- two independent assemblies, launches and
renders of byte-identical art -- which is what makes the reading meaningful:

    shot          null (identical art)      wear 0.35 -> 0.00
    elev_E          0.01%   max 15            0.01%   max 14
    elev_N          0.00%   max 14            0.00%   max 15
    elev_S          0.00%   max  7            0.00%   max  7
    elev_W          0.00%   max  7            0.00%   max  7
    spawn           0.03%   max 16            0.01%   max 15
    extraction      0.92%   max 16            0.44%   max 16

**Deleting the entire wear layer is indistinguishable from changing nothing.**
Every shot is at or below the floor of an instrument that reproduces to 0.00%
on the elevations. The vertex colours are unquestionably in the GLB -- 0.642 to
0.982, WITHIN sd 0.110, measured above -- and they are not reaching the
renderer. See item 84.

**SO THE CORNER OUTLINES ARE NOT THIS ITEM.** The observation that opened it
stands; the attribution does not. Whatever draws a border on every panel is the
3 mm bevel chamfer catching the sun, or the relief field edge (item 75's
remaining 1.5 cm reveal), and this item cannot be the cause of something it has
no measurable effect on. It stays open because the topology finding is real and
will matter the moment item 84 is fixed -- at which point every module gets its
own dark border for the first time, visibly.

**EARLIER, AND SUPERSEDED BY THE ABOVE.** `wear` was set to 0.0 for delco walls only, every
other style and species left as a control, and the level rebuilt. The
screenshot that came back was read for something else (item 82) and the
comparison was never made. **The value has been restored to 0.35**, because a
tool repo should not carry an unvalidated probe, and 0.0 was never a shipping
proposal -- a wall with no wear reads as plastic.

**WHAT WOULD CLOSE THIS.** Not a value, and not scaling the noise either --
on a box `concave` is zero at every vertex, so keeping only the honest term
gives the same result as `wear: 0`, and the wall goes plastic (measured above:
mean 0.983, spread 0.016). Occlusion has to stop being a property of the
MODULE and become a property of the SPACE. Two routes, and they are the same
statement at different layers: put grime in the texture, where Pixelcoat has
the resolution and world-space projection makes it continuous across joints
(item 80); or get real occlusion from the scene, which on this renderer means
the Forward+ question item 83 raises, because Compatibility has no SSAO. Note the honest caveat on judging any of it: `repetition_census.py` is
blind to this by construction (item 78), so the only current reader is a
person looking at a render.

*STATUS: ANALYSIS 2026-08-29 -- THE FRAME. ITEMS 73 THROUGH 81 ARE FACES OF
THIS ONE FACT, AND IT EXPLAINS WHY A DAY OF INDIVIDUALLY CORRECT LOCAL FIXES
CHANGED NOTHING A PERSON COULD SEE*

**82. Every tool's contract is about a piece. No contract is about the whole,
so the composed artifact is nobody's deliverable.** Named 2026-08-29, after
four separate causes of one visible defect had been found and fixed
individually without the defect moving.

Ten tools, each with a clean contract, each verifiably meeting it. Deli
Counter guarantees exact-fit dims, collision truth and gameplay anchors. Zoo
guarantees one mesh per (type, theme, style, dims). Pixelcoat guarantees a
deterministic pack per material kind per mission. Patina guarantees vertex
nuance and a dressing manifest. Lux lights it, Laser Tag grades it, the
functional lock fingerprints it. **All of that is true at once, and the
building still reads as a row of boxes.**

Every finding of 2026-08-29 is this same fact wearing a different hat:

  * **81** -- Zoo's wear is correct PER MESH, which is exactly why it draws
    each piece's own boundary.
  * **74** -- the module vocabulary is correct PER SLOT, which is exactly why
    a 30 m facade is fifteen identical answers to fifteen identical questions.
  * **76, 80** -- the per-instance channel is written in two halves and wired
    in neither, because nothing downstream has a whole to hand it.
  * **79** -- there is no facade object, so there is nowhere a composition
    could live even if one were authored.
  * **78** -- the one instrument built today measures pieces and is blind to
    appearance. It bit twice in one afternoon.
  * **73** -- the same shape outside the art pass entirely: a contract about a
    part (fingerprint the repo) defeated by the whole (the pipeline writes
    into it).

**THE PREDICTION THIS MAKES, which is the reason to file it rather than
admire it.** The next local fix will also not move the result. On 2026-08-29
the relief was quietened (75), the census did not move a single row, the wear
was zeroed (81), and a facade composition pass was drafted whose measured
effect on eleven of twelve shipped buildings was **zero overrides and one new
stem**. Three correct local changes, no visible change. That is not bad luck;
it is what an absent level of ownership predicts.

**WHAT FOLLOWS, and it is one programme rather than seven items.**

  1. A NAMED COMPOSITION (79). You cannot compose what the system cannot name.
     Deli Counter is the home; it already owns the floorplan.
  2. A PER-INSTANCE CHANNEL from that composition to the render (76 + 80).
     Both halves exist: `dressing_scene.py` writes MultiMesh buffers and has no
     importers; Patina's `instances.json` computes per-slot variation and is
     never requested. It is the only VRAM-bounded way to express a composition
     (item 80's constraint).
  3. AN INSTRUMENT THAT READS THE COMPOSED RESULT (78), not the parts.
     Without it every change is judged by eye at the end of a four-hour run,
     which is the loop this whole day was.

**WHAT THIS ITEM DOES NOT LICENSE.** Inventing an architectural grammar, and
building an eleventh tool. The grammar is a design decision and belongs to the
person who can see the building. The gap this item names is a MECHANISM gap:
there is nowhere to put a grammar and no way to check one. Recorded plainly
because it matters: this was seen by the person looking at the render, not by
the person reading the code, after the code had been read all day. That is
itself the finding.

*STATUS: NARROWED 2026-08-29 -- REFUTED AS THE CAUSE OF THE EXTERIOR BANDING,
BY ABLATION, WITHIN THE HOUR IT WAS FILED. THE MECHANISM IS REAL AND STILL
UNTESTED INDOORS, WHICH IS THE ONLY PLACE ITS LIGHTS ARE*

**83. The renderer lights the wall per piece, so light draws the module grid
instead of dissolving it.** Observed 2026-08-29, walking the themed level:
*"in real life a flat wall wouldn't have repeating shadows across it even if
it was made with multiple pieces of stone"*, and *"light should be adding
cohesion, not be specific to each piece."*

That inverts what light is for here. A real wall is lit as a SURFACE and the
joints between its pieces are the one thing light does not care about. In this
pipeline light is bound PER MESH, every module is its own mesh, and so the
lighting discontinuity lands exactly on the module boundary -- which makes
light the loudest thing drawing the grid rather than the thing hiding it.

**THE MECHANISM IS ALREADY DOCUMENTED IN THIS REPO, from the other end.**
`tools/mesh_light_census.py`: "GL Compatibility budgets positional lights PER
MESH... A mesh over the budget silently drops lights, which shows up standing
still as **a hard brightness step where two slabs meet**." Three tools reason
about the cap independently -- `zoo/core/arch.py:318`,
`deli_counter/floors.py:177`, `lux_light_loader.gd:111` -- and the walk
project ships `max_lights_per_object=16` against a level Lux fills with
fixtures. **CORRECTED 2026-08-29: that count was carried over from another
level and is wrong for this one.** `walk_fixtures` reports `Spawned 57 fixture
light(s) from 57 marker(s)` with `omni=51` in the tree -- 57, not ~150, and 51
of them omni. The mechanism argument does not depend on the exact number, but
it was quoted three times today and was never measured on this building. (The
57-vs-51 gap is unexplained and may be benign -- not every rig type need be an
OmniLight3D -- but nobody has checked.)

**AND THE FACTORY'S RESPONSE TO THE CAP HAS BEEN TO MAKE THE PROBLEM WORSE.**
Item 54 tiles room-spanning plates into smaller meshes precisely to buy light
budget. That is correct for the budget and it multiplies boundaries, and every
boundary is a place two meshes can disagree about light. `_arch.py` already
caught half of this and fixed the wrong half: it removed the chamfer from
plate tiles because "where two tiles abut, the two chamfers form a V-groove...
a thin bright/dark line drawn along every internal tile seam, WORST NEAR A
FIXTURE." The chamfer was the smaller contributor. The lighting seam it names
in the same sentence is still there.

**NOT MEASURED YET, and that is the next thing.**
`python tools\mesh_light_census.py _runs\walk_themed_relief` counts the
positional lights reaching each visible mesh and compares them to the project
cap. Discriminator by ablation: `walk_themed.py --no-fixture-lights` builds
the same level with the ~150 fixtures absent. If the per-panel banding
survives that, it is baked (item 81's vertex wear); if it goes, it is light
binding and this item is the cause.

**REFUTED FOR THE EXTERIOR, SAME DAY, BY THE ABLATION THIS ITEM ASKED FOR.**
`walk_themed.py --no-fixture-lights` built the identical level with all ~150
fixtures absent. On the north elevation, against the fixtures-on build:

    band mean       193.04  ->  193.03
    mean |dI/dx|     7.306  ->   7.310
    strong edges        15  ->      15      (unchanged)
    whole-frame max pixel delta: 15, with no structure

**Nothing.** The fixtures are interior; the exterior is sun-lit and carries
about three positional lights, nowhere near the cap of 16. At `spawn` -- eye
level, looking through the glass into the lobby -- the same ablation moves
57.66% of pixels with a max delta of 224, so the fixtures matter enormously
where they are. They are not on the facade.

**AND THE EDGES ARE SHADOWS CAST BY OUR OWN RELIEF.** Classifying each strong
edge by the shape of the brightness profile across it -- a recess casts a DARK
LINE with both sides brighter, a surface discontinuity makes a monotonic STEP:

    5 dark lines (recess shadow)   4 steps (2 building ends, 2 window frames)

So the repeating lines survive triplanar, survive removing every fixture, and
read as recess shadows. They are the `relief` field edge: item 75 took the
pier from 0.14 m to 0.02 and the reveal from 0.05 to 0.015, and **1.5 cm is
still enough to draw a line under a directional sun.**

The observation that started this item was *"a flat wall wouldn't have
repeating shadows across it"*. It is correct, and the wall is not flat -- it
is corrugated at exactly the module pitch, by us, on purpose. The answer is
not to change the light. It is `{"reveal": 0.0}`, which `relief_parts`
collapses to a single flat panel, and which `rockay` already uses.

(Caveat on the classifier: it is ad-hoc, written in one cell, and the edge
COUNT moves with the row band chosen -- 15 over a wide band, 9 over a tight
one. The ablation result does not depend on it; the dark-line/step split
should be re-derived properly before it is quoted as a number.)

**THE TRADEOFF THIS RAISES, which is not mine to take.**
`max_lights_per_object` lives under `rendering/limits/opengl/` -- it is a
Compatibility-renderer limit. Forward+ uses clustered lighting and has no
per-object light cap, so on that renderer this entire class of artefact does
not exist, and `arch.py`'s reason for tiling plates evaporates with it. Both
the walk project and the shipped export choose `gl_compatibility` deliberately
(`walk_themed.py`: "MUST match the shipped export's project.godot"). Changing
that is a reach-and-performance decision with consequences well beyond a
facade, and it belongs to whoever owns that choice. It is recorded here
because "light should add cohesion" has a structural answer and this is it.

*STATUS: OPEN 2026-08-29 -- DIAGNOSED, NOT FIXED, AND THE FIX IS A DECISION
RATHER THAN A FLAG. 1,896 KIT SURFACES CARRY COLOR_0 AND 0 OF 19 MATERIALS
READ IT. THE EXPORT IS FINE; THE IMPORT DROPS IT. NOW WITH A MEASURED
COUNTER-ARGUMENT: FORCING THE LAYER ON MULTIPLIES THE 2 m MODULE SIGNATURE BY
3.8x (SPECTRAL POWER AT THE MODULE PITCH, NORTH ELEVATION, 278 OFF -> 1044
ON, GEOMETRY HELD CONSTANT). THAT IS A LARGER EFFECT THAN THE RELIEF FIX OF
ITEM 75 AND IT POINTS THE WRONG WAY. THE LAYER IS STILL DEAD WEIGHT AND STILL
WORTH FIXING, BUT NOT AS BAKED: THE WEAR IS COMPUTED PER MODULE AND SO
REPEATS PER MODULE BY CONSTRUCTION, WHICH IS ITEM 79'S ROOT CAUSE WEARING A
THIRD MASK*

**84. Zoo computes per-vertex wear, exports it correctly, and the engine does
not use it.** Found 2026-08-29 by deleting the layer and finding that nothing
changed.

The colours are in the file. `vertex_variation.py` on the shipped module:

    wear 0.35   Wall_Field mean 0.786   WITHIN sd 0.10957   colour 0.642 .. 0.982
    wear 0.00   Wall_Field mean 0.983   WITHIN sd 0.01560   colour 0.974 .. 0.991

A fifth of the wall's albedo, present in COLOR_0, byte-verified. And rendering
the two builds through the same cameras with one variable moved and a measured
null to compare against, **every shot sits at or below the noise floor** (item
81 carries the table). A quarter of an albedo cannot change by that much and
move nothing.

**THE SAME FAMILY, TWICE ALREADY FIXED, ONE STEP EARLIER EACH TIME.**
`bpylayer/geometry.py`'s own comment records it: "Measured on a shipped dressing
GLB: COLOR_0 was 1.0 on every vertex of all 2098 covers... the wear was
computed, written into a colour layer named 'Wear', and dropped at the export
boundary because `export_glb` exports `export_vertex_color="ACTIVE"` and
nothing ever made that layer active." That fixed the EXPORT. Whether anything
CONSUMES the layer after import was never asked, and the answer appears to be
no.

**READ BACK OFF THE RUNNING SCENE, 2026-08-29** (`walk_themed.py
--vertex-colors report`, which grafts a node that inspects the imported
materials):

    [walk_vertexcolor] kit surfaces:  1896 carry COLOR_0, 0 do not
    [walk_vertexcolor] kit materials: 0 already use vertex colour as albedo, 19 do not

**Total on both counts.** Every kit surface in the level carries the colour
array, and not one material is told to use it. The export is not the problem --
the 2026 dressing fix holds, and 1,896 surfaces prove it. Godot's glTF importer
does not set `vertex_color_use_as_albedo`, so every per-vertex wear value Zoo
has ever computed has been discarded at the material boundary.

Note this also took a tool fix to see at all: `godot_probe.run_probe` captures
Godot's output and `look_shots`'s `--verbose` printed only the command line,
so a probe whose entire result is a `print` was invisible. Anything
`walk_fixtures` and `walk_triplanar` have ever printed was going into a void
as well.

**WHAT WOULD CLOSE THIS.** One check and one flag. `BaseMaterial3D` ignores
COLOR_0 unless `vertex_color_use_as_albedo` is set, and Godot's glTF importer
decides that on its own; the check is to read the flag off the imported
material, which the `walk_triplanar.gd` pattern already does for
`uv1_triplanar` and could do in five lines. If it is false, the same runtime
script sets it and the ablation is re-run -- and this time the wall should
visibly move, which is the whole point.

**AND THE ORDER MATTERS.** Do not "fix" this and item 81 in the same pass.
Turning the layer on restores a fifth of albedo of per-module border shading to
every wall in the library, which is item 81's defect arriving for the first
time. The sequence is: confirm the layer is off, decide what wear SHOULD do on
a mesh with no interior vertices, then turn it on.

*STATUS: OPEN 2026-08-29 -- OBSERVED IN A WALKTHROUGH AND SET ASIDE, NOT
INVESTIGATED. RECORDED BECAUSE THE EXISTING GATE CANNOT SEE IT BY
CONSTRUCTION*

**85. Fixtures spawn inside walls, and the co-location gate cannot notice.**
Observed 2026-08-29 walking `bank_block_001`: a hanging light half-buried in
the wall at a wall/ceiling junction, its glow bleeding through the surface.

**WHY THE GATE MISSES IT, which is the reason this is worth a number.** Lux's
`check_fixture_colocation` (item 71) asks whether the spawned rig landed on
its marker -- rig root against anchor, and it now compares them correctly.
That is a question about the FIXTURE. Nothing anywhere asks whether the
MARKER is in open space. An anchor placed a few centimetres inside a wall
passes co-location perfectly, because the lamp is exactly where it was told
to be.

Same shape as item 82: every contract is about a part. The fixture is checked
against its anchor, the anchor is checked against nothing, and the space
between them belongs to no tool.

**WHAT WOULD CLOSE THIS, and it is cheap.** Deli Counter already emits the
collision boxes and knows every wall's thickness; a fixture anchor inside one
is a point-in-box test at spec time, before any art is built. Lux would be the
wrong home -- by the time it spawns, the geometry is already committed and all
it could do is report. Note also that anchors sit at the wall/ceiling junction
by design, so the test needs a tolerance rather than a strict containment
check, and the tolerance is a decision somebody has to make.

**NOT MEASURED.** One screenshot, one fixture. Nobody knows whether this is
one bad anchor or a systematic offset, and `mesh_light_census.py` walks the
running tree and could answer it -- every spawned rig against the collision it
sits in -- without a new instrument.

*STATUS: CLOSED 2026-08-29 -- ZOO 0.52.0, AND THE ONLY VERDICT THAT MATTERS:
THE PERSON WHO REPORTED IT LOOKED AT THE NEXT BUILD AND SAID IT WAS FIXED.
MEASURED BEFORE AND AFTER ON THE SHIPPED MESH -- 15 FRONT-FACE VERTICES, ALL
AT dot 0.8756 WITH THE FACE NORMAL, 28.9 DEGREES OFF FLAT*

**86. A 3 mm chamfer was shading every flat wall as a cushion.** Found
2026-08-29, after four other investigations had each failed to explain the
same artefact.

Every panel on the facade carried a pair of diagonal wedges, identical on all
66 placements. `wall_delco_01_w200.glb` says why:

    front face (y=-1.200)     15 verts
       distinct normals: 4
         [-0.342 -0.876 -0.342]  x4
         [-0.342 -0.876  0.342]  x3
         [ 0.342 -0.876 -0.342]  x4
         [ 0.342 -0.876  0.342]  x4
       dot with the flat face normal: min 0.8756  max 0.8756

Not one vertex on the face carried the face's own normal. Every one pointed at
its nearest corner, so the panel shaded as a pillow and the quad's
triangulation drew the diagonal across it.

**THE MECHANISM.** `bevel_edges` cuts a one-segment chamfer that sits about 45
degrees off each face it touches. `SMOOTH_ANGLE_DEG` was 50. Fifty is greater
than forty-five, so the chamfer was smoothed INTO the face -- and a box face
has no interior vertices, so every normal it owns is a corner normal and
nothing holds the middle flat. On a prop that is the highlight roll-off a
bevel exists for. On a wall it is ruinous.

**WHY IT TOOK FOUR TRIES.** It survived world-space triplanar (it is normals,
not UVs), survived `wear: 0.0` (not vertex colour -- item 84), survived
deleting all 57 fixture lights (band mean 193.04 -> 193.03, item 83), and is
invisible to `repetition_census.py`, which measures form vocabulary and by
construction cannot see a shading artefact baked into one shared mesh. Four
instruments each correctly reported "not me" and the absence was read as
mystery rather than as evidence.

**SCOPED ON PURPOSE.** `bm_to_object` takes a `smooth_angle` and only
`recipes/_arch.py` passes 0.0. Cylinders still need the 50-degree default: a
14-segment water tank at 25.7 degrees per segment reads as a dodecagon
without it.

*STATUS: NARROWED 2026-08-29 -- MECHANISM PROVEN END TO END, NOT YET IN THE
PIPELINE. `tools/detach_textures.py` REWRITES A BUILT KIT'S `images[]` TO
`uri` REFERENCES: 80 TEXTURE RESOURCES -> 23, ART PAYLOAD 4.65 MB -> 2.28 MB,
183 PRIMITIVES BIT-IDENTICAL, AND THE RENDER MEASURES INSIDE THE INSTRUMENT'S
OWN REPEATABILITY (ITEM 90). WHAT REMAINS IS A DECISION -- WHERE THE DETACH
RUNS -- AND THE SECOND HALF: THE `tex/` FOLDER HAS TO TRAVEL WITH THE ART
THROUGH ASSEMBLY AND EXPORT, WHICH TODAY IT DOES NOT*

**87. Deli Counter's one-mesh-in-VRAM discipline stops at the texture.**
Found 2026-08-29, checking an aside about Godot's import cache rather than
assuming it.

Pixelcoat writes ONE texture per material -- a single 256x256
`concrete_delco_albedo.png` for the level. Zoo exports each module as a
self-contained GLB, and a self-contained GLB embeds the image bytes it
references: `images[]` carries `bufferView`, not `uri`. Two individually
correct decisions multiply.

    tools\texture_census.py _runs\wG\art
      35 GLB file(s)
      23 distinct image payload(s) stored 82 time(s)
      3.21 MB stored   0.84 MB unique   duplication factor 3.82x
      concrete_delco_albedo   57129 B  256x256   18 copies
      drywall_delco_albedo   157082 B  512x512    5 copies

**AND THE ENGINE DOES NOT DEDUPLICATE.** That is the fact that decides whether
this costs disk or VRAM, so it was observed separately rather than inferred:
the project's `.godot/imported` cache holds 18 `.ctex` files for
`concrete_delco_albedo`, 5 for `drywall_delco_albedo`, 4 for each of the
three `glass_facade_mirror_blue` maps. Every row matches the GLB census
one-for-one. Godot creates one texture resource per (GLB, texture) pair.

**WHAT IS AND IS NOT CLAIMED.** The duplication is per distinct ASSET, not per
PLACEMENT -- a 66-placement wall run still loads one Mesh, so item 80's
discipline is intact and untouched. The 27.6 MB figure the census prints is
`width*height*4` for base levels only, no mips and no block compression; it
moves by a large factor with the importer's compression mode and is a
comparison against itself, not a budget. Nobody has measured a frame-time or
an allocation. This is a count.

**THE INSTRUMENT EXISTS AND ITS FAILURES ARE IN ITS DOCSTRING.** The import-
cache grouping was wrong twice before it was right -- keyed on the whole
filename every file grouped alone and it reported no duplication at all; keyed
on a trailing `<word>_albedo` it collapsed concrete, drywall and carpet into
one bucket. It now matches against the texture names read out of the GLBs in
the same run, which is the standing rule about never writing a checker against
a guessed schema, arrived at the hard way.

**BEARING ON TRIM SHEETS.** A trim sheet consolidates many textures into one
larger sheet. Embedded per-GLB, that is a bigger payload duplicated across the
same 35 files. Sharing has to come first or the atlas makes this worse.

*STATUS: NARROWED 2026-08-29 -- THE LANE IS CHOSEN AND CONFIRMED BY EYE, AND
IT IS NOT ONE OF THE TWO THAT ADD ASSETS. WORLD-SPACE TRIPLANAR MAKES TEXTURE
DENSITY INDEPENDENT OF NODE SCALE, SO A SQUASHED UNIT BOX STOPS BEING A
SQUASHED TEXTURE. WALKED IN `wL` AT THE TWO COORDINATES THE DEFECT WAS
REPORTED FROM -- THE CORNER AT x -15.8 z 29.0 AND THE INTERIOR JAMB AT
x -4.6 z 20.5 -- AND THE STRETCHED STRIPS ARE GONE. MEASURED AGAINST A NULL
(ITEM 90): 7 OF 8 SHOTS CLEAR THEIR OWN FLOOR, max |delta| 43-217 AGAINST
FLOORS OF 7-16. WHAT REMAINS IS THAT `--triplanar` IS A WALK-PROJECT RUNTIME
FLAG AND NOT WHAT SHIPS -- SEE 76 AND 80 -- AND THAT IT FORECLOSES TRIM
SHEETS, WHICH IS A DESIGN DECISION AND NOT A BUG*

**88. Deli Counter stretches a unit box to fill slot remainders, and the skin
stretches with it.** Found 2026-08-29, walking `wH2` -- reported as "the
Pixelcoat application on these bands reads as stretched", which is what it
looks like and not where it comes from.

**PIXELCOAT AND ZOO ARE BOTH CLEAN.** Every mesh in the wall kit carries the
same texel density, relief parts included:

    Wall_Base      2.00 x 0.45 x 0.30    uv/m med 1.200
    Wall_Pier_1    0.02 x 2.73 x 0.30    uv/m med 1.200
    Wall_Field_0   0.98 x 2.73 x 0.27    uv/m med 1.200
    Wall_Panel     0.30 x 3.30 x 2.00    uv/m med 1.200

and every material's `KHR_texture_transform` is square -- `concrete_delco` is
`scale 0.400,0.400`, and no material in the kit has a non-uniform one.

**THE STRETCH IS APPLIED AT PLACEMENT.** `building.tscn` has 238 transformed
nodes. 46 carry a non-uniform scale, and the mesh is the same one every time:

    wallEnd_delco_01.glb    35        wall_delco_01_w200.glb    66  uniform
    wallEnd_delco_03.glb     6        wall_delco_01_w30.glb     62  uniform
    wallEnd_delco_02.glb     5        window/doorway/prop       all uniform

    ext_-1_N_seg14   1.700 3.300 0.300     ext_0_N_seg10    0.150 3.300 0.300
    int_0_0_seg12    0.300 3.300 0.300     int_-1_2_seg7    0.300 3.300 1.650

`wallEnd` is a UNIT BOX. `wall_delco_01_w200` has its width baked into the
mesh by Zoo and is placed at scale 1; `wallEnd` is the exception to that and
is scaled to whatever remainder is left. A 1x1x1 mesh scaled to 0.30 x 3.30
carries UVs authored for a square, so the stone comes out 11 times taller than
wide -- and the 0.15 m instances come out 22:1. The visible artefact is the
thin 0.30 m RETURN face, which is why it reads as a vertical streak at
building corners and beside openings, where remainders land.

**BOTH SIDES OF THE BUILDING.** 38 exterior, 8 interior. The interior ones sit
beside doorways in the lobby and vault rooms and are the same 11:1.

**THREE PLACES IT COULD BE FIXED, and the choice is not obvious.** Zoo could
build `wallEnd` to exact dims the way it already builds walls -- cheapest, and
it multiplies the asset count against item 87's texture duplication. Deli
Counter could ask for a sized module instead of scaling a unit box, which is
the bay-library work in items 74 and 64. Or world-space UVs make density
independent of node scale entirely (items 76, 80), which would also fix the
per-module texture restart with one mechanism.

That third option is the tell. This is the same failure as the relief (item
75), the baked wear (item 84) and the seam restart (item 76): appearance
derived from the MODULE rather than from the WORLD. Item 79's root cause,
found for the fourth time in one day, this time wearing a transform.

*STATUS: CLOSED 2026-08-29 -- FOUND AND FIXED IN THE SAME PASS, AS A DIRECT
CONSEQUENCE OF ITEM 87. `mipmaps/generate=true` ADDED TO THE WALK PROJECT'S
`[importer_defaults]`; max |delta| PER PIXEL FELL FROM 148 TO 15, WHICH IS THE
NOISE FLOOR*

**89. Disabling Detect 3D silently disabled mipmaps, and it cost nothing until
textures left the GLB.** Found 2026-08-29, the first time a walk project was
built with external textures.

`walk_themed.py` sets `detect_3d/compress_to: 0` so the headless import cannot
reach the S3TC compressor, which has no rendering device and dies with signal
11. That is correct and stays. What nobody noticed is that "Detect 3D" is the
mechanism that turns mipmaps ON as well as compression, so every texture it
touches imports as a 2D texture with no mip chain:

    _runs/wI/art/tex/concrete_delco_albedo.png.import
        mipmaps/generate=false
        detect_3d/compress_to=0

**IT WAS INERT UNTIL 87.** While every texture was EMBEDDED in a GLB, the
glTF importer built its own for 3D and the project default never applied.
Detaching them made the setting reachable for the first time, and the same
scene rendered measurably worse:

    wH embedded vs wI detached        mean 3.32   max |delta| 51 / 54 / 148
    noise floor (same project twice)  mean 2.12   max |delta|  7 /  7 /  15

Not a missing texture -- an un-mipmapped one, aliasing on every oblique
surface, which is why it read as "the windows are less transparent": an
aliasing normal map changes the specular. Reported by eye before the
instrument was pointed at it.

**THE FIX IS TO ASK BY NAME.** Mipmap generation is CPU-side, so unlike the
compressor it is safe under `--headless`. The two settings are now coupled in
the comment block, because the next person to disable a detector needs to know
what else the detector was doing.

*STATUS: NARROWED 2026-09-02 -- THE PER-PIXEL RULER IS STILL UNCALIBRATED AND
EVERY `%px changed` FIGURE BELOW ~42% STILL MEANS NOTHING. THE AGGREGATE ONE
IS NOW MEASURED AND ITS FLOOR IS ZERO: EIGHT SHOTS, NOTHING CHANGED, d_mean
d_p50 d_clip% d_crush% ALL +0.00. SO `shot_diff` WITHOUT `--images` NEEDS NO
NULL AT THIS FRAME COUNT, AND `max |delta|` REMAINS THE PER-PIXEL STATISTIC
THAT SEPARATES*

**90. `look_shots` was never measured against itself, so its own repeatability
was unknown.** Found 2026-08-29, when a change that moved no geometry produced
the same difference as one that did.

Shooting `wJ` twice, changing nothing between runs:

    elev_N     mean 2.1185   %px>2 41.977%   max  9
    elev_W     mean 2.1305   %px>2 41.952%   max  7
    spawn      mean 2.0852   %px>2 39.223%   max 15
    objective  mean 2.1283   %px>2 40.894%   max  7

`look_shots` accumulates six frames per shot because TAA and glow need more
than one, so two launches of the same scene do not converge to the same
pixels. That is the floor, and it is enormous by the measure everyone reaches
for first.

**WHAT IT INVALIDATES.** The pier 0.02 -> 0.10 change (item 75) was reported
here at "36.85% of pixels changed" on the north elevation. Re-measured:

    pier .02 -> .10   elev_N  mean 2.1168  %px 41.916%  max  10   <- NOISE
                      elev_W  mean 2.1984  %px 41.953%  max 122   <- real
                      spawn   mean 7.3961  %px 60.028%  max 211   <- real

The conclusion drawn from it -- invisible head-on, visible where light grazes
-- survives, and the number offered as evidence did not support it. Any
comparison in this file resting on a sub-42% pixel count needs re-reading,
including the triplanar A/B of 2026-08-29 (13.6-19.0% of pixels against a
claimed 0.00-0.01% floor); those figures were reported in session and are not
recorded here, but the qualitative claims that rest on them are -- items 81,
84 and 86 each say an artefact "survives triplanar".

**WHAT TO DO ABOUT IT.** `max |delta|` separates cleanly at this scale --
floor 7-15, an un-mipmapped import 51-148, a real geometry change 122-211 --
and `shot_diff.py` should report it and refuse a verdict below the floor. The
floor is a property of the project and the frame count, not a constant, so the
honest form is a NULL SHOT: shoot twice, subtract, and only then compare.

**THE OTHER HALF OF THE RULER, MEASURED 2026-09-02.** This item's floor is a
PER-PIXEL one, and it is enormous. The AGGREGATE statistics `shot_diff` prints
without `--images` have a different floor, and nobody had measured that either.
Shot on `_runs/ab_del` -- `category5_baie_dore_001`, eight shots, 1600x900,
six frames each, nothing changed between the two runs:

    shot              d_mean     d_p50   d_clip%  d_crush%
    elev_E             +0.00     +0.00     +0.00     +0.00
    elev_N             -0.00     +0.00     +0.00     +0.00
    elev_S             +0.00     +0.00     +0.00     +0.00
    elev_W             -0.00     +0.00     +0.00     +0.00
    extraction         +0.00     +0.00     +0.00     -0.02
    objective          +0.00     +0.00     +0.00     +0.01
    overview           +0.00     +0.00     +0.00     +0.00
    spawn              +0.00     +0.00     +0.00     +0.00

**ZERO, to two decimals, on every shot and every statistic.** The same TAA and
glow accumulation that moves 40% of the pixels moves the frame MEAN by nothing
at all, because it is noise about a stable value and averaging is what kills
it. So the two measures are not two views of one floor -- they are a measure
that needs a null shot and a measure that does not.

**WHAT THIS DOES AND DOES NOT CHANGE.** It does NOT weaken anything above:
every `%px changed` figure below ~42% is still meaningless, `max |delta|` is
still the per-pixel statistic that separates, and the triplanar A/B still
needs re-reading. What it adds is that `d_mean`, `d_p50` and the clip/crush
percentages can be compared directly, with no null and no floor, at this frame
count and resolution. The A/B that produced this null exercised that
immediately: `elev_S +63.38` and `spawn +15.21` between two lighting builds
are real numbers rather than noise, and they were trustworthy the moment the
null came back zero.

**AND THE CAUTION THAT SURVIVES.** A floor is a property of the project, the
frame count and the resolution -- this item says so and it is still true. Zero
here is not zero everywhere; it is zero for eight derived cameras on one
themed site at 1600x900 with six frames. A scene with moving dressing, a
day/night cycle or a flickering fixture rig would move the mean, and the null
is what would say so. Shoot it anyway; it is one extra `look_shots` call and
it now costs a comparison nothing to be sure.


*STATUS: CLOSED 2026-08-30 -- CONFIRMED ON A SHIPPED PACKAGE, NOT A MECHANISM
PROOF. THE COMPOSED `out/presentation/project.godot` CARRIES
`scene={"import_script/path": "res://zoo_worldskin.gd"}` AND THE SCRIPT SITS
BESIDE IT; GODOT IMPORTED IT AND THE BUILDING WAS LOOKED AT. PROVEN AT RUNTIME
FIRST, CONFIRMED BY EYE, BAKED AT IMPORT, RE-MEASURED AGAINST A NULL, THEN RUN
THROUGH THE PIPELINE END TO END*

**91. World-space UVs reached the shipped build.** Closed 2026-08-29, the
pipeline half of items 76, 80 and 88.

`tools/zoo_worldskin.gd` is an `EditorScenePostImport` script that sets
`uv1_triplanar` / `uv1_world_triplanar` and a MEASURED `uv1_scale` on kit
module materials. `level_factory/assets/godot/` carries the shipping copy and
`run_presentation_compose.py` installs it into the composed package, next to
the `config/features` patch that was already there for the same reason -- DC
writes the project, LF corrects it.

**WHY AT IMPORT.** glTF cannot express "project from world position", so this
can only be a material property set after import. The two other places both
cost something: mutating a shared material in a composed scene does not
survive being saved, and `surface_material_override` per placement is a
separate material for each of 218 kit modules -- item 80's discipline undone
at the material layer for a boolean. At import the material is edited once
inside the imported scene and every instance shares it.

**WHAT IT FIXED.** Both faces of the same defect: the per-module texture
restart (76) and `wallEnd`'s 11:1 stretch (88). Confirmed by eye at the two
coordinates the stretch was reported from, and measured against a null (item
90) -- 7 of 8 shots cleared their floor, max |delta| 43-217 against 7-16.

**THE RESIDUAL, RECORDED RATHER THAN WAVED AWAY.** Baking at import
reproduces the runtime proof to within ~50 pixels of a 1.44 Mpx frame. That is
real, not noise: the null pair differs by 0 pixels above the same threshold
while this differs by 50-54. The obvious cause was ELIMINATED -- all 218 kit
placements sit under `ext_`/`int_` slots, so both scripts cover the same set.
The leading candidate is `uv1_scale` being derived from the mesh at a
different point in the import pipeline (before vs after LOD generation), which
both scripts print and nobody has compared.

**UNMEASURED BILL.** Triplanar samples three times per map -- nine across
albedo/roughness/normal. No frame time exists for it on the 2060 under
gl_compatibility. And it FORECLOSES TRIM SHEETS on any surface it touches,
because a trim sheet is an authored UV layout and this throws UVs away. That
is a design decision, taken, not a bug.

*STATUS: NARROWED 2026-09-02 -- MEASURED, AND THE DELETION LOSES. SUN LINK vs
DELETION IS overview -0.05 AND EVERY OTHER SHOT +/-0.00 AGAINST A FLOOR OF
ZERO, WHILE THE UNLINKED TWO-SUN BUILD IS elev_S +63.38. THE ROW HAD NEVER
BEEN SHOT BECAUSE THE TOOLS COULD NOT PRODUCE IT; `walk_themed --sun-link`
NOW DOES. WHAT REMAINS IS A DEFAULT FLIP SOMEBODY HAS TO OWN, AND THE
THREE-STATE SEAM*

**92. Lux REPLACES the art pass's lighting instead of adding to it.** Named
2026-08-29 by the person who owns the design, at the end of the facade work.

**THE SHAPE OF THE PROBLEM.** Lighting is currently subtractive: something
strips what is there and puts its own in. `walk_themed.py` says so in its own
output -- `lux : ... (Lot's own sun/env removed)` -- and `graft_lux` drops
Lot's WorldEnvironment and Sun unless `--keep-walk-lighting` says otherwise.
`run_lux_apply.gd` rewrites the scene it is handed. So the art pass owns
light, and Lux owns it back by demolition.

**WHAT ADDITIVE WOULD MEAN.** The art pass stops owning light at all, and Lux
contributes a layer over a scene that never had a competing one. That is
cleaner for the same reason the relief was moved from additive covers to
subtractive carving (item 75's history, in reverse): the current shape works
by one stage undoing another, and every such pair eventually disagrees.

**WHERE TO START, and this is the whole point of writing it down now.** Read
before proposing. Three files decide it and none has been read with this
question in mind:

  * `lot/godot/addons/lot/` -- what lighting does Lot put in a site, and why
    does the walk harness need its own sun at all;
  * `lux/` -- `run_lux_apply.gd` (in `level_factory/assets/godot/`) and the
    preset resources: what does apply DO, replace or overlay;
  * the `lux_apply` job in `level_factory` -- what it is handed and what it
    returns, and whether `lux_fixture_gate` assumes either shape.

**WHAT IT TOUCHES.** Lot, Lux and the `lux_apply` job at minimum. Item 83
(the per-piece lighting ablation) and item 85 (fixtures inside walls) are both
in this neighbourhood and should be re-read before design, not after.

**THE INSTRUMENT ALREADY EXISTS.** `look_shots` + `shot_diff --null` can hold
this honest: lighting changes are exactly the kind that move a mean and prove
nothing, and item 90 is the reason to distrust any pixel count under ~42%
without a floor. Shoot a null first.

**WHAT THE THREE TOOLS ACTUALLY DO TO LIGHT.** Read 2026-08-31, which is what
the status line above asked for and all that was done. Grounded on:
`lot/lot.py` 109,130 -- `tools/walk_themed.py` 55,962 -- `tools/lux_inject.py`
7,870 -- `level_factory/assets/godot/run_lux_apply.gd` 9,024 --
`level_factory/adapters/lux/__init__.py` 14,700 --
`level_factory/packages/pipeline/planner.py` 27,558 --
`level_factory/apps/cli/main.py` 12,589 -- `apps/cli/commands/__init__.py`
130,113 -- `lux/addons/lux/runtime/{lux_root,lux_environment,lux_lighting,
lux_light_loader,lux_fixture_spawner}.gd` -- `lux/addons/lux/editor/
lux_dock.gd` 15,472. Every staged byte count landed exactly on the figure the
device reported. `themed_site_assemble/out/site.tscn` and
`lux_apply/out/lux.applied.tscn` could NOT be read -- the job cache hardlinks
them and the bridge refuses `nlink > 1` -- so the one claim resting on that
gap is flagged at the end.

**LUX DELETES NOTHING.** `LuxEnvironment.ensure_world_environment`
(`lux_environment.gd:27`) ADOPTS an existing WorldEnvironment -- the parent's
direct children first, then the whole scene tree -- and writes only the grade
onto it; `_sky_is_provided` skips the sky block entirely when somebody else
owns it. `LuxLighting.ensure_sun` (`lux_lighting.gd:23`) returns early when
`sun` is already valid. The only deletion in the addon is
`LuxRoot._build_modules` (`lux_root.gd:169-175`), which clears its OWN direct
children of the module types, for @tool idempotency, and whose comment says
why: one LuxRoot had accumulated three DirectionalLight3D and three CRT post
stacks across script reloads. The sentence this item was opened on -- "Lux
owns it back by demolition" -- is not true of Lux.

**THE ART PASS OWNS NO LIGHT TO BE REPLACED.** `planner.py:40-52` is already
explicit about the split: fixture HARDWARE and its `LuxEmit` markers are
LAYER_ART, light is LAYER_LIGHT, and "an unlit art package therefore still
ships validated fixtures and their `LuxEmit` markers, which is a contract
another lighting system can read." `presentation_compose` emits no lighting.
So the thing item 92 says is being replaced does not exist.

**LOT PUTS NO LIGHT IN A SITE EITHER.** 109 KB of `lot.py` has exactly two
lighting emission sites, and both are WRAPPER scenes: `write_walk_scene`
(~1607-1628) and `write_navqa_scene` (~1804-1819). Each emits a
ProceduralSky WorldEnvironment (`ambient_light_energy = 0.6`, `tonemap_mode =
2`) and a `Sun` DirectionalLight3D with `shadow_enabled`, as SIBLINGS of the
instanced `Site`, with the comment saying it mirrors Deli Counter's
`level_test.tscn` so the runtime scene does not render unlit. That is HARNESS
lighting, not an art pass. The content scene carries none -- the same rule
CLAUDE.md already records for `walk.tscn` versus `site.tscn`.

**THE DEMOLITION IS ONE FUNCTION, IN THE PREVIEW PATH ONLY.** `graft_lux`
(`tools/walk_themed.py:442`) text-deletes the `WorldEnvironment` and `Sun`
node blocks out of Lot's walk scene, default on, `--keep-walk-lighting` to
disable. Nothing in the shipped path deletes anything: `lux_apply` stages a
throwaway project holding the addon plus the assembled scene, and
`run_lux_apply.gd` only ADDS a LuxRoot and the fixture rigs.

**THE ADDITIVE SHAPE ALREADY EXISTS, AND THE TWO GRAFTS DISAGREE.** This is
the finding that decides the item. `tools/lux_inject.py` does the same job as
`graft_lux` and does it by composition: it keeps Lot's WorldEnvironment ("The
existing WorldEnvironment stays ... Removing Lot's would be work for no gain")
and sets `sun_light = NodePath("../Sun")` under the
`node_paths=PackedStringArray("sun_light")` header the scene loader requires,
so Lux DRIVES Lot's sun instead of adding one beside it. Its own comment
records the measurement: 2 directional lights without that field, 1 with it,
on 4.7.stable. Two tools in this repo answer the same question opposite ways,
which by CLAUDE.md means one of them is wrong and nothing should be built on
either until that is settled.

`graft_lux`'s justification argues against the UNLINKED additive shape, not
against the linked one, and its table has no row for the linked one:

    no Lux          mean 108.6   p95 254   near-clip 18.62%
    Lux, 2 suns     mean 151.7   p95 248   near-clip  3.17%
    Lux, 1 sun      mean 147.0   p95 222   near-clip  1.13%   by DELETION
    Lux, Sun Link      --          --          --             NEVER MEASURED

**THREE THINGS NOBODY HAD WRITTEN DOWN.**

  * ENVIRONMENT ADOPTION IS AUTOMATIC AND SCENE-WIDE; SUN ADOPTION IS NOT.
    `_resolve_sun_link` (`lux_root.gd:111`) resolves only an explicitly
    assigned `sun_light` or a SkyMint-SHAPED node -- `_find_skymint`
    duck-types on a `sun_light` property holding a DirectionalLight3D. A plain
    `DirectionalLight3D` named `Sun`, which is exactly what Lot emits, is
    never found. That asymmetry is the entire reason `graft_lux` has to
    delete: leave both in and you get one environment and two suns.
  * SUN LINK IS DEFINED IN TWO DIRECTIONS AT ONCE. With `sun_light` set,
    `LuxLighting.apply` (`lux_lighting.gd:33-50`) WRITES the preset's
    transform, colour, energy and shadow settings onto the linked light, and
    `_track_sun_light` (`lux_root.gd:463`) then READS those same values back
    off it every frame to feed the vertex path. So Sun Link does not preserve
    Lot's sun angle -- it round-trips Lux's own preset through Lot's node.
    Harmless while the preset is the intended answer; load-bearing the moment
    a consumer expects their own sun to survive. The @export doc says "track a
    live DirectionalLight3D"; the code also overwrites it. Decide which it is
    before designing on it.
  * `lights_json` IS AN UNFINISHED THOUGHT, in the sense CLAUDE.md already
    names. `LuxAdapter.fingerprint_inputs` hashes it
    (`adapters/lux/__init__.py:100`); `plan_commands` never passes it;
    `run_lux_apply.gd` accepts only `--scene`, `--preset`, `--out`; and
    `LuxLightLoader.bake` has exactly one caller in the whole tree,
    `lux_dock.gd:431`, the editor dock. `site.site.lights.json` is 24,800
    bytes of merged light anchors on the rockay build that the headless
    pipeline never reads. It is also the ONE artifact a team bringing its own
    lighting would want, which is why it belongs in this item and not a
    separate one.

**WHAT THIS ITEM IS ACTUALLY ABOUT, restated by the person who owns the
design, 2026-08-31: a Level Factory user chooses whether Lux renders their
lighting, or they bring their own, or they take the buildings and placement
and nothing else.** That reframes the work and shrinks it. The choice already
exists at the PLAN level and says so in its own help text: `--art --unlit`
("The level is themed and dressed, its light fixtures are baked and gated, and
no Lux render is applied -- for a team bringing its own"), `export --mode
art-unlit`, and `_layers_produced` reporting LAYER_LIGHT from `lux_apply`'s
output rather than from the art pass. What does NOT exist is the same choice
at the SCENE level, and that is the gap:

  1. The two modes are mutually exclusive BY DEMOLITION rather than by
     composition. `--keep-walk-lighting` is the only way to keep Lot's rig
     with Lux present, and it is documented as the bad option because it
     leaves two suns. There is no "Lux grades the environment and drives the
     sun the level already has", even though `lux_inject.py` builds exactly
     that and Lux supports it.
  2. The no-Lux path ships no typed light contract. It ships `LuxEmit_*`
     markers inside the GLBs and a `site.site.lights.json` nothing exports.
     A consumer gets hardware and no anchors.
  3. Nothing proves the claim. `probe_lux_free.py` proves a package does not
     REQUIRE Lux. Nothing proves an art-unlit package is LIGHTABLE by someone
     else -- that the anchors are present, typed, and in the right frame.

**THE SEAM, PROPOSED AND NOT BUILT.** One named choice, three states, no
deletion in any of them:

    light = lux    Lux owns the look. It adopts the environment the scene
                   has and drives the sun the scene has (Sun Link), rather
                   than the scene arriving pre-stripped.
    light = own    The level keeps its own rig -- Lot's today, the
                   consumer's tomorrow. No LuxRoot is grafted at all.
    light = none   No rig, no LuxRoot. Geometry, fixtures, markers and the
                   anchor manifest, for a consumer who lights from scratch.

`--unlit` already selects between the last two by accident of what it omits;
it does not distinguish them, and the difference matters to somebody
integrating. Whether that becomes a third flag value or stays two flags is a
decision, not a finding, and it should be taken after the measurement below
rather than before it.

**THE RUNBOOK, and the null goes first.** Item 90 is the reason no pixel count
under ~42% is believable without a floor, and a lighting change is exactly the
kind that moves a mean and proves nothing. So, on one mission, one seed,
nothing else changing:

    1. NULL. Shoot `look_shots` twice against an UNCHANGED project and
       `shot_diff --null` them. Record the floor. Any A/B difference below it
       is not a difference.
    2. A -- DELETION, today's default:
       `python tools\walk_themed.py --mission <id> --lux-repo <lux>`
       then `look_shots`.
    3. B -- SUN LINK, the untested row: same command with
       `--keep-walk-lighting`, then `python tools\lux_inject.py <project>`
       on the walk project so the LuxRoot carries
       `node_paths=PackedStringArray("sun_light")` and
       `sun_light = NodePath("../Sun")`. Confirm ONE DirectionalLight3D with
       `tools/light_census.py` -- which counts the RUNNING tree, not the
       scene file -- BEFORE shooting anything. Two suns here means the
       node_paths header did not take, and the shot would be measuring the
       old defect.
    4. C -- NO LUX, the reference: `walk_themed.py` with no `--lux-repo`.
    5. `shot_diff` A-B, A-C, B-C against the floor from step 1.

The result to look for is not "which is prettier". It is whether B and A
differ by more than the null floor. If they do not, the deletion in
`graft_lux` is buying nothing that composition does not, and it should go.
If they do, the difference has a cause and the cause is nameable -- start
with the sun angle, because Sun Link overwrites Lot's and the two rigs do not
point the same way.

**THE RESIDUAL, recorded rather than waved away.** The claim that the
`lux_apply` INPUT carries no lighting rests on lot.py's two emission sites
plus the shipped artifact downstream of it -- `walk_preview_rebuilt/
walk_preview/site_lux.tscn`, 62,240 bytes, 350 `[node` lines, one `LuxRoot`
with an `active_preset`, zero WorldEnvironment, zero Light3D. It does NOT
rest on reading `themed_site_assemble/out/site.tscn`, which the hardlinked
job cache would not serve. That artifact also shows the deeper fact about
the shipped level: ITS LIGHT IS NOT IN THE SCENE FILE AT ALL. Every light is
manufactured at load by an @tool script's `_ready`, because runtime-created
nodes have a null owner and `PackedScene.pack` drops those. Anyone reasoning
about "the lighting in the shipped scene" by reading the shipped scene will
find nothing and conclude wrongly -- which is the same trap CLAUDE.md records
for `grep -c Light3D site.tscn`, one layer further in.

**WHAT IT TOUCHES, revised.** Lot is NOT in the blast radius after all -- it
emits harness lighting into wrapper scenes and nothing asks it to change.
`tools/walk_themed.py` and `tools/lux_inject.py` are, because they disagree.
`level_factory`'s lux adapter is, for the `lights_json` it hashes and never
passes. Lux itself is, only for the sun-adoption asymmetry and the two-way
definition of Sun Link. `lux_fixture_gate` is NOT: it runs in its own staged
project over a `*_fixtures.glb` and assumes nothing about the site's
lighting shape -- one of the three questions this item asked, answered no.

**THE ROW IS MEASURED, 2026-09-02, AND THE DELETION LOSES.** Three walk builds
off one `themed_site_assemble` output -- `category5_baie_dore_001`, art digest
`3c0065a88983` identical across all three -- eight derived cameras, 1600x900,
six frames each. Aggregate floor established first and it is ZERO on every
shot and every statistic (see item 90), so no null is carried into the
comparisons below and none is needed.

    build         Lot's Sun / env   sun_light   vs the deletion build
    ab_del        removed           --          baseline
    ab_link       KEPT              not wired   elev_S +63.38  elev_E +27.40
                                                spawn  +15.21  overview +4.39
    ab_sunlink    KEPT              WIRED       overview -0.05  elev_W -0.01
                                                every other shot +/-0.00

**SUN LINK AND DELETION ARE THE SAME PICTURE.** The +63 was never the price of
keeping Lot's lighting. It was the price of keeping it UNLINKED -- two
directional lights at different azimuths, which is why the south and east
elevations moved and the north and west barely did. Wire the link and the
difference collapses to two hundredths of a code on one shot.

That is not a lucky null, and it has a mechanism: in BOTH configurations the
scene ends up with one directional light at the preset's orientation and one
Environment carrying the preset's grade. `LuxEnvironment.ensure_world_environment`
adopts Lot's WorldEnvironment rather than building a second one, and
`LuxLighting.apply` writes the preset's transform, colour, energy and shadow
settings onto whichever sun it holds. Only WHICH NODE OBJECT owns them differs
between the two builds, and a node's identity is not visible in a photograph.

**THE DIAL WAS CONFIRMED BEFORE THE NULL WAS BELIEVED**, because this file's
own rule says a null result is evidence about the wiring until proven
otherwise. `_runs/ab_sunlink/site_walk.tscn` carries
`node_paths=PackedStringArray("sun_light")` in the LuxRoot header and
`sun_light = NodePath("../Sun")` under it; `_runs/ab_link/site_walk.tscn`
carries neither, zero of each. The two scenes differ in exactly the wiring
under test and the +63/-0.00 split falls on that line.

**WHY IT HAD NEVER BEEN SHOT, which is the part worth keeping.** Not for want
of trying: THE TOOLS COULD NOT PRODUCE THE ROW. `graft_lux` wrote a LuxRoot
carrying a script and a preset and nothing else, so `--keep-walk-lighting`
gave the two-suns build and there was no third option. `lux_inject.py` writes
the two missing lines and refuses to run on a scene that already has a LuxRoot
-- which `graft_lux` has just put there. The two tools that disagreed about
lighting policy could not be combined to test the disagreement. A first
attempt on 2026-09-02 stacked them anyway and silently re-measured the
two-suns row: the overview came back +4.39 against the +4.7 this item's own
table records between two suns and one, which is what gave it away.
`walk_themed --sun-link` now emits those two lines, and the walk subject
stamps `sun_link` into its treatment block so `shot_diff` reports the
experiment instead of calling two different builds identical.

**WHAT REMAINS, and it is now a decision rather than a question.** The
measurement says the deletion can go: replace it with Sun Link and the picture
does not move. That is a default flip in `graft_lux` -- `--keep-walk-lighting
--sun-link` becomes the behaviour and the deletion becomes the opt-out, or
disappears. It was not done in the session that measured it, deliberately: a
picture that does not move is not the only reason a team might want Lot's
environment gone, and whoever owns the walk preview should say so before the
default changes under them. The three-state seam this item proposed -- `light
= lux | own | none` -- is unaffected and still unbuilt.

**THE RESIDUE, recorded rather than rounded away.** `overview -0.05` and
`elev_W -0.01` are small but they are NOT the floor, which is 0.00 exactly.
Something real differs. The likely cause is that Lux overwrites most of Lot's
Environment and not all of it -- `apply` writes ambient, tonemap, fog, glow
and adjustment, and whatever Lot set that Lux never touches survives into the
adopted environment and not into a freshly built one. That is a hypothesis
from reading `lux_environment.gd`, not a measurement, and it would be settled
by diffing the two Environment resources rather than by shooting anything.


*STATUS: OPEN 2026-08-30 -- A TOOL'S OWN CODE IS NOT IN ITS JOB FINGERPRINT,
SO THE PIPELINE SERVES THE PREVIOUS BEHAVIOUR OF A SCRIPT THAT WAS JUST
REWRITTEN AND SAYS `cache` WHILE DOING IT. ONE DRIVER IS ALREADY TRACKED, SO
THE PATTERN TO COPY EXISTS*

**93. Editing a driver script does not invalidate its job's cache.** Found
2026-08-30, trying to prove item 91 on a shipped build.

`run_presentation_compose.py` was rewritten to install the worldskin importer
default. The next full run reported `bank_block_001.presentation_compose
cache` and shipped the old package. The stage was not stale by any measure the
scheduler had: its INPUTS -- slots, modules, theme, style -- were identical.
Only the code that consumes them had changed, and that is not fingerprinted.

**IT IS AN INCONSISTENCY, NOT AN OVERSIGHT OF THE WHOLE IDEA.**
`tests/unit/test_lux_driver_in_fingerprint.py` exists, so the Lux driver IS
deliberately part of its job's fingerprint. Presentation's is not. One is
tracked, one is not, and the untracked one fails by silently serving a stale
answer -- the worst of the three possible behaviours.

**WHAT THIS COST, and it is the reason it is worth a number.** Two full
pipeline runs that looked clean and proved nothing, plus a wrong recovery
suggested from memory rather than from the code:

  * `--force` is `action="store_true"` with help that reads "accepted and
    ignored: every stage is now always re-evaluated against the cache". It is
    a no-op that LOOKS like the answer to exactly this problem.
  * deleting `fingerprint.last.json` does nothing either; the cached answer
    lives in `.level_factory/index.sqlite` and the sidecar is a receipt.
  * the working command is `cache forget <job_id>`, which has been in
    `apps/cli/main.py` the whole time and returns
    `{"forgotten": true, "note": "the job will re-run on the next pass"}`.

Two of those three were guessed before the CLI was read. Reading it first
would have cost one look and saved two runs.

**WHAT WOULD CLOSE THIS.** Copy the Lux pattern: put each driver script's
content hash into its job's fingerprint, so editing a tool invalidates the
work it produced. The test to mirror already exists and is named after the one
job that got it right.

**AND A SMALLER ONE ALONGSIDE IT.** `--force` should either do something or be
removed. A flag whose help text says it is ignored is a flag everyone will
keep reaching for, because the name promises exactly what they want.

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

*STATUS: CLOSED 2026-09-01 -- MEASURED ON A REAL GATE RUN WITH THE NEW
DRIVER STAGED (9,098 BYTES, NOT 5,667). SEARCH ROOT `FixtureGate`, 4 OF 4
LIT-FACE MATERIALS BOUND -- ONE PER ZOO SPECIES, CHECKED AGAINST THE FIXTURES
MANIFEST -- AND GLOW ENERGY 10.638 -> 0.0 -> 10.638 ACROSS THE POWERED CUT,
BESIDE LAMPS 47.063 -> 0.0 -> 47.063. 37/37 MARKERS, NO COLOCATION ERRORS*

**94. Nothing in the pipeline binds fixture emissives, and the gate that
certifies the power beat cannot see them.** Found 2026-08-31 while separating
the art layer from the light layer for item 92. Lux 0.26.0.

**THE CONTRACT, and it is a good one.** Zoo's fixture pass bakes the lit faces
into the fixture GLBs as glTF emissive -- troffer diffusers, streetlight
lenses, sign faces, wall-pack lenses -- under a naming rule: `M_*` with a
`_Lens`, `_Diffuser` or `_Face` suffix. `LuxEmissiveBinder.bind` walks a
scene, stamps each matching material's base emission energy into resource
meta (idempotent, so a re-import is safe) and registers it with
`LuxLighting`. From then on `set_fixtures_powered(false)` kills the GLOW
together with the rig lights, and restoring power brings the stored energy
back. That is the power-cut heist beat, and it is the correct place for the
art/light seam: Zoo owns the emissive face because it is hardware; Lux owns
whether it is lit because that is render.

**WHO CALLS IT.** Every harness Lux ships:

    lux/tools/visual_pass.gd:80                    bind_fixture_emissives
    lux/tools/walk_harness.gd:119                  bind_fixture_emissives
    lux/walk/headless/walk_night_strip.gd:113      bind_fixture_emissives
    lux/walk/headless/visual_night_strip_dressed.gd:85   bind_fixture_emissives
    lux/addons/lux/editor/lux_dock.gd:443          LuxEmissiveBinder.bind

**WHO DOES NOT.** Both of Level Factory's drivers:

    level_factory/assets/godot/run_lux_apply.gd    -- ships the level
    level_factory/assets/godot/run_fixture_gate.gd -- certifies the beat

and `walk_themed.py`'s injected `_SPAWN_GD`, which spawns fixture lights into
the walk preview and binds nothing either. So a level Lux walks in its own
harness has bound emissives and a level LEVEL FACTORY BUILDS DOES NOT. The
tool and the pipeline that drives it disagree about what a finished level is.

**WHAT IT COSTS, first half.** `LuxLighting._emissives` is empty in every
shipped level, so `set_fixtures_powered(false)` kills the rig lights and
leaves every lens, diffuser and sign face glowing at full energy. The power
cut takes the light and not the look of the light.

**WHAT IT COSTS, second half, and this is the worse one.**
`run_fixture_gate.gd` exercises the powered kill/restore by summing
`_energy(lamps)` over the spawned LIGHTS -- its own comment says
"visibility-kill" -- before and after `set_fixtures_powered`. It never binds,
so there is nothing else it could measure. The gate therefore reports
`powered: {kill: true, restore: true}` on a level whose glow cannot be killed
at all, and `LUX_FIXTURE_POWER_GATE` is a BLOCKING issue in the Lux adapter.
A blocking gate that passes on half its subject is the shape CLAUDE.md
already has a rule about: a number that silently describes four fifths of a
table is worse than no number, because it looks actionable and is not.

**THE SYMPTOM WAS ALREADY WRITTEN DOWN, in a flag's help text.**
`walk_themed.py --no-fixture-lights` explains itself by saying fixtures are
lit by the WorldEnvironment's glow pass "whether or not any light is cast, so
the eye cannot separate a working fixture from a dead one." That is this
defect, described from the walkthrough end, by somebody who did not have the
binder in mind. It is also why a walk cannot be used to check the gate: both
instruments are blind in the same direction.

**THE FIX IS NOT THE ONE-LINER IT LOOKS LIKE, and that is the reason to write
this down rather than patch it.** Adding `bind_fixture_emissives()` to
`run_lux_apply.gd` would bind at APPLY time and then `PackedScene.pack` the
result -- and neither half of the binding survives packing. The registration
is runtime state on a LuxRoot instance. The base energy is `set_meta` on a
material that came from an imported GLB, an EXTERNAL resource the packed
scene references rather than owns. So the shipped `lux.applied.tscn` would
carry no more than it does today, and the driver would report a success that
the level does not contain -- the same silent-loss shape `run_lux_apply.gd`
already guards against for the preset and for fixture-light ownership, one
resource layer further out.

Binding has to happen AT LOAD, in the level, every time. The candidate worth
reading before proposing: `LuxRoot._ready` already calls `_build_modules`,
`_load_default_library` and then applies the preset when `apply_on_ready` is
set. Binding there would make every level carrying a LuxRoot bind itself with
nothing downstream to remember. Whether that is right depends on questions
nobody has answered -- what it costs on a scene with 218 kit placements, what
it does under `@tool` in the editor where `_ready` runs on every script
reload, and whether a consumer who is NOT using Lux for light should still
get the binding. Read `lux_root.gd:90-105` and `lux_emissive_binder.gd`
together before deciding.

**HOW TO SEE IT WITHOUT GUESSING.** The gate's own report is the instrument,
once it is asked the other question: bind first, then sum emission energy
over the bound materials across the same kill/restore, and record both
figures. A gate that reports lamp energy and glow energy separately cannot
pass on half the behaviour. `tools/mesh_light_census.py` and
`tools/light_census.py` already count the RUNNING tree rather than the scene
file, which is the only frame in which any of this is visible.

**WHAT WAS REFUTED ON THE WAY, kept because it is cheaper than
rediscovering.** This item was first stated as "`bind_fixture_emissives` has
no caller anywhere in the tree." That was wrong, and wrong for an
instructive reason: the claim was made from a grep over the SUBSET of files
staged at that moment, and Lux's four harnesses were not among them. Staging
the rest turned "nobody calls it" into "everybody except the pipeline calls
it" -- a smaller claim and a better one, because a mechanism four harnesses
depend on is proven to work and the question becomes why the driver skips it.
Rule 1 of CLAUDE.md's verification section, in a new costume: name what
produced the evidence before concluding from it, and a grep's evidence is
bounded by what was staged.

**WHAT SHIPPED, 2026-09-01.** Lux 0.27.0 and Level Factory 0.52.0, together,
because neither half is worth anything alone: a bind nobody can measure and a
measurement of a bind that never happens are the same non-event.

  * `LuxRoot.bind_emissives_on_ready` (default true) binds at load, after
    `_build_modules` -- which replaces `_lighting` and therefore empties
    `_emissives`, so binding before it would register into the module about
    to be discarded.
  * `bind_fixture_emissives` resolves `owner`, then the parent, then
    `current_scene`, then `self`, and returns the root it walked. The old
    order reached `self` FIRST in every headless run, because a `-s` driver
    has no current scene -- so wiring the call without this would have bound
    zero materials and reported ok. That is the second defect this item found
    and it was hiding behind the first.
  * `run_fixture_gate.gd` binds and measures lamp AND glow energy across ONE
    kill/restore, and reports a `glow` block. `LUX_FIXTURE_GLOW_GATE` blocks;
    `LUX_NO_FIXTURE_EMISSIVES` and `LUX_FIXTURE_GLOW_UNMEASURED` report.
  * `adapters/lux` `adapter_version` 0.5.0 -> 0.6.0, so every existing entry
    executes once against the wider instrument rather than serving a verdict
    taken with the narrower one.

**WHAT IS NOT PROVEN, and it is the part that matters.** No Godot was
available to the session that wrote the patch. Both scripts pass
`tools/gdcheck.py`, and the three new findings were exercised against
synthetic reports across all six branches -- including lamps and glow failing
together, which must report two findings and does. None of that is an engine.
The first real `lux_fixture_gate` run is the measurement, and a
`LUX_FIXTURE_GLOW_GATE` on it is this defect being CAUGHT, not a regression.
Until that run exists, this item is a patch with a test harness attached, and
the factory manifest's lockstep check will call the tool set drifted until
both repos are promoted -- pins are re-earned, not typed.

**CLOSED BY A REAL GATE RUN, 2026-09-01.** `category5_baie_dore_001`,
`--art --unlit`, the whole graybox base re-run underneath it. The staged
driver was the new one -- 9,098 bytes against the old 5,667 -- so this is the
widened instrument reporting, not the old one passing again.

    "glow": { "search_root": "FixtureGate",
              "bound": 4, "materials": 4,
              "kill": true, "restore": true,
              "energy_before": 10.6379997730255,
              "energy_off": 0.0,
              "energy_restored": 10.6379997730255 }
    "powered": { "kill": true, "restore": true,
                 "energy_before": 47.0630792379379,
                 "energy_off": 0.0,
                 "energy_restored": 47.0630792379379 }
    markers 37   spawned 37   spawnable 37   colocation_errors 0

Read in the order the risks sit. `search_root` is `FixtureGate` and not
`LuxRoot`, so the root resolution fix took -- had it said `LuxRoot`, every
other number in the block would have been a measurement of an empty node.
`bound` equals `materials`, so the binder and the gate walk the tree the same
way and neither is counting a set the other does not touch. And `materials`
is 4 rather than 0, which is what stops this being a pass for the wrong
reason: `LUX_NO_FIXTURE_EMISSIVES` is deliberately non-blocking, so a run that
found nothing would also have reported zero blockers.

**FOUR MATERIALS AGAINST THIRTY-SEVEN FIXTURES IS THE RIGHT ANSWER, and it
was checked rather than assumed.** `lf_..._fixtures.built.json` (Zoo 0.31.0)
reports exactly four species -- `fluorescent_fixture` 20, `pendant_fixture`
13, `wall_pack` 3, `sign_box` 1 -- and a glTF import produces one material
resource per glTF material, shared by every mesh instance using it. The
binder dedupes by material object. So four is one lit-face material per
species, every one of them found; it is not thirty-three fixtures with no lit
face. The six skipped markers are all `window`, reason "daylight/preset -- no
hardware", which is the contract.

The glow now dies with the power and comes back at exactly the value the
binder stamped: 10.6379997730255 out and the same float back, which is what
restoring from `BASE_META` should look like and is why exact equality is the
right test at that one site.

**AND ON THE LIT PATH TOO, 2026-09-02.** The paragraph that stood here said
the shipped `lux_apply` path was still unproven because the gate run had been
`--unlit`. It is proven now. `run category5_baie_dore_001 --art` on rockay-ws,
`lux_apply` job log:

    [lux] Bound 4 fixture emissive material(s) (searched Site)
    [lux] Spawned 148 fixture light(s) from 148 marker(s)
    [lux] requested 'Blue Hour' applied 'Blue Hour'
    (exit=0, duration=1.64s)

`searched Site` rather than `LuxRoot`, by a DIFFERENT route than the gate:
`run_lux_apply.gd` sets `owner` on the line after `add_child`, so `_ready`
finds a null owner and falls through to the parent, which is the scene root.
The gate resolves through its own parent, `FixtureGate`. Both land on a node
that actually contains fixtures, which is the whole point of the chain. Four
materials again -- one per Zoo species -- now against 148 markers on a full
site rather than 37 on one building, none skipped, and `lux.validation.json`
empty.

**THE COST QUESTION IS ANSWERED AND IT WAS NOT A QUESTION.** This item asked
what the on-ready bind costs on a scene with 218 kit placements. The entire
driver run -- load, attach LuxRoot, build modules, apply preset, bind, spawn
148 rigs, pack and save a 276 KB scene -- is 1.64 seconds. The tree walk is
not measurable against the rest of it.

**WHAT THIS STILL DOES NOT SAY.** That the lighting is GOOD. Nothing else in
item 94 is outstanding.

*STATUS: OPEN 2026-09-01 -- `lot.merge_lights` STAMPS A HARDCODED "1.0.0" ON
A SITE MANIFEST WHOSE ANCHORS ARE DELI COUNTER 1.1.0. MEASURED ON A BUILD
MADE THE SAME DAY: ENVELOPE 1.0.0, `drop` PRESENT ON 28 OF 28. NOTHING READS
THE FIELD TODAY, WHICH IS WHY IT HAS SURVIVED -- THE FIRST CONSUMER TO GATE
ON IT IS THE ONE THAT PAYS*

**95. The site light manifest declares a version its anchors outgrew.** Found
2026-09-01, writing `tools/probe_lightable.py` for item 92's handoff question.

Two producers, one envelope field, and only one of them maintains it.
`deli_counter/lights.py:12` stamps `LIGHT_MANIFEST_VERSION`, currently
`1.1.0`, on each building's `<name>.lights.json`. `lot.merge_lights`
(`lot.py`, the site-level merge) builds its own envelope and writes
`"light_manifest_version": "1.0.0"` as a LITERAL, never reading the version
of the files it is merging.

The anchors are copied wholesale -- `wa = dict(a)` -- so 1.1.0 content passes
straight through. Measured on `category5_baie_dore_001` rebuilt 2026-09-01
10:06, `site.site.lights.json` 25,288 bytes: envelope `1.0.0`, and `drop`
present on 28 of 28 ceiling-hung anchors. `drop` is a 1.1.0 field. The file
declares one contract and satisfies a later one.

**WHY IT HAS SURVIVED.** Nothing reads the field. `LuxLightLoader.bake`
checks for an `anchors` key and nothing else; `probe_lightable.py` is the
first thing in the tree that looks at the version at all, and it was written
last week. A version nobody gates on cannot fail, which is exactly the
condition in which it drifts.

**WHY IT MATTERS ANYWAY, and this is the whole reason it is filed rather than
patched quietly.** `planner.py` promises the unlit package ships "a contract
another lighting system can read", and `--art --unlit` is documented as being
for a team bringing its own lighting. The envelope version is the field that
exists to make that handoff safe. A consumer that gates on `1.0.0` and gets
1.1.0 anchors reads the wrong contract, and a consumer that gates on `1.1.0`
rejects a file that satisfies it. Both failures are ours.

**WHAT ELSE THE MERGE DROPS, unjudged.** The building envelope carries
`building_id` and `theme`; the site envelope carries neither, and re-keys the
building onto each anchor instead. That may be deliberate -- a site has many
buildings and one theme is not obviously the site's -- but nothing says so,
and a reader cannot tell a decision from an omission. Establish which before
changing the shape.

**WHERE TO START.** `lot.py` `merge_lights` and `deli_counter/lights.py`
together, in one sitting. The options are not equivalent and the choice is a
design decision, not a bug fix: propagate the maximum of the merged building
versions; version the SITE manifest independently of the building one and say
so in the envelope; or carry the set of merged versions explicitly so a
consumer can see what went in. Owner is `lot` -- it writes the file -- and
`probe_lightable.py` already fails on an unknown version, so it is the gate
for whatever gets chosen.

*STATUS: OPEN 2026-09-01 -- 24 WINDOW ANCHORS ARE DERIVED, MERGED, SHIPPED IN
THE MANIFEST AND NEVER BECOME LIGHT: THE ONLY CODE THAT TURNS THEM INTO RIGS
IS `LuxLightLoader.bake`, WHOSE SOLE CALLER IN THE TREE IS A DOCK BUTTON.
MEASURED ON A REAL BUILD AND ON A REAL GATE RUN. THE MARKER PATH SKIPS THEM
BY DESIGN AND SAYS SO*

**96. Daylight anchors are specified and never realized, because the manifest
bake path has no caller outside the editor.** Found 2026-09-01, tracing the
art/light layer boundary after item 94.

Lux has two ways to turn an anchor into a rig, and they are NOT rivals --
they share one tuning table. `LuxFixtureSpawner` places rigs at Zoo's
`LuxEmit_*` markers; `LuxLightLoader.bake` places them from a
`.lights.json`; and the spawner calls `LuxLightLoader.rig_for_anchor` for
every rig it makes, so brightness, range and colour come from one place
whichever path ran. That part is sound and the division is written down:
Zoo owns WHERE, Lux owns HOW BRIGHT.

The gap is which path the PIPELINE runs. `run_lux_apply.gd`,
`run_fixture_gate.gd` and `walk_themed.py`'s injected spawn script all call
the marker path. `LuxLightLoader.bake` has exactly one caller in the whole
tree: `lux_dock.gd:431`, the editor's "Bake Lights" button.

**AND THE MARKER PATH SKIPS DAYLIGHT ON PURPOSE.**
`LuxFixtureSpawner.spawn` skips `window` and `sun` -- daylight has no
hardware, so Zoo bakes no marker for it -- and the spawner's own docstring
says daylight "stays on the manifest bake path". That sentence is true about
Lux and false about Level Factory, because Level Factory never runs that
path.

**MEASURED, both ends.** The 2026-09-01 site manifest carries 24 `window`
anchors of 75 records. The same day's `lux_fixture_gate` run reports 37
markers, 37 spawned, and 6 skipped -- every one of them a `window`, reason
"daylight/preset -- no hardware". So the anchors exist, the rig branch exists
(`_rig_for` maps `window`/`sign` to `LuxAreaLightRig`, with `size` read from
the anchor), and nothing in a built level ever constructs one.

**IT IS NOT OBVIOUSLY A BUG, WHICH IS WHY IT IS AN ITEM.** A preset sun plus
sky ambient may be the intended answer for daylight, in which case 24 window
anchors are dead weight in a manifest that advertises them to consumers, and
the fix is to stop deriving them or to mark them advisory. If they ARE meant
to light, the fix is a pipeline caller for the manifest bake -- and the
`_rig_for` comment argues these are expensive: area rigs are "THE ONLY
SHADOWED LIGHTS IN THE PACKAGE", deliberately, per item 60. Twenty-four of
them is not four. Decide which before wiring anything.

**THE SECOND FACE OF THE SAME FACT.** `LuxAdapter.fingerprint_inputs` hashes
`lights_json`; `plan_commands` never passes it; `run_lux_apply.gd` accepts
only `--scene`, `--preset` and `--out`. The manifest is a cache input to a
job that cannot read it. That is CLAUDE.md's unused parameter -- somebody
knew the manifest mattered to the answer and stopped before using it -- and
it is the same unfinished thought as the missing caller, seen from the
pipeline side. Whichever way item 96 is decided, that hash should stop
claiming an input the command does not take.

*STATUS: OPEN 2026-09-02 -- A THEME NOTHING CARRIES, ASKED FOR BY THE ONLY
HARNESS THAT PROVES THE PIPELINE END TO END. NEEDS A PIXELCOAT SKIN PACK AND
ZOO SPECIES STYLES, NOT ONE FILE. LF 0.53.0 POINTED THE SMOKE AT `delco` SO
THE HARNESS STOPS MEASURING THE CATALOGUE; WHETHER `delco_1997` SHOULD EXIST
IS UNANSWERED*

**97. `delco_1997` is a theme two repos would have to grow, and only the
smoke ever asked for it.** Named 2026-09-02, after the theme preflight refused
a smoke run in seconds that used to fail after a full Blender leg.

**WHAT THE PREFLIGHT SAYS, verbatim**, and it is a good example of the
capability-gap signal `USING_THE_FACTORY.md` asks every tool for -- what was
asked, what exists, who is short:

    theme: delco_1997 - NO PIXELCOAT PROFILE at ...\themes\delco_1997.json
      pixelcoat carries: bank, casino, delco, rockay, rockay_civic,
        rockay_retail, rockay_service, stadium, street
      zoo: no species carry a 'delco_1997' style (56 scanned) - the kit
        falls back to flat colour
    refusing to run an art layer against a theme that does not resolve.
    Nothing has been dispatched.

**IT IS TWO REPOS, WHICH IS THE POINT OF FILING IT.** A Pixelcoat profile
alone does not make the theme: Zoo has no species carrying that style across
56 scanned, so the kit would resolve the skin and still render flat colour.
Under the gap protocol that is a Pixelcoat skin pack AND a Zoo species-style
pass, versioned and changelogged in both, and it is a DESIGN decision -- what
a 1997 Delco looks like as distinct from `delco` -- before it is a build task.

**HOW LONG IT HAS BEEN TRUE.** `smoke_lf.ps1` has requested `delco_1997`
since it was written. Before Level Factory 0.51.0 the run reached
`pixelcoat_build` and exited 1 there, after the functional lock had already
spent real Blender time; the 0.51.0 changelog records exactly that run. The
preflight moved the failure to stage 9 in seconds. So nothing regressed and
nothing was ever built -- the harness has simply never completed its
presentation leg, and the cost of finding that out fell by most of an hour.

**WHAT 0.53.0 DID AND DID NOT DO.** It pointed the smoke at `delco`, a theme
Pixelcoat carries. Two string edits, no logic. That is a fix to the HARNESS,
which should test the pipeline rather than the catalogue, and it is not an
answer to this item. `delco_1997` still does not exist, and this item is
where that stays visible.

**WHY IT MATTERS BEYOND THE SMOKE.** The smoke is the only thing that
re-earns certification. While it could not complete, `verify-manifest`
reported DRIFT on five tools -- deli_counter certified 0.94.0 against 0.102.1
installed, lux 0.16.0 against 0.27.0, lot 0.48.0 against 0.51.0, zoo 0.48.0
against 0.54.0, level_factory 0.48.0 against 0.52.0 -- with no route to clear
any of it. A blocked harness does not announce itself as a blocked
certification; it just looks like a failing test nobody has got to.

**THE OPEN QUESTION, and it is not a technical one.** Does the design want a
`delco_1997`? If yes, it is a capability request in Pixelcoat's and Zoo's own
grammar and belongs to whoever owns the look. If no, the string was always a
placeholder and this item closes as RETRACTED with the smoke change standing.
Nobody has been asked.

*STATUS: OPEN 2026-09-05 -- MEASURED WHILE COMMITTING, NOT WHILE LOOKING FOR
IT. `check.py` EXITS 1 ON THREE SHELLS WHOSE STAIR ENDPOINTS BAKE ONTO
DISJOINT NAVMESH ISLANDS, AND HAS DONE SINCE BEFORE 2026-08-24. THE HOOK
THEREFORE REFUSES EVERY COMMIT, WHICH IS A CANDIDATE EXPLANATION -- NOT A
PROVEN ONE -- FOR WHY FOUR RELEASES SAT UNCOMMITTED IN THE WORKING TREE.
SECOND CAUSE, SEPARATE AND RECURRING: `build_freshness` GATES ON TEN `lf_`
SHELLS THAT ARE LEVEL FACTORY'S OWN COMPOSED OUTPUT, TRACKED IN DELI
COUNTER'S REPO, SO AN LF RUN CAN RED DC'S COMMIT GATE.*

**98. Deli Counter cannot commit through its own pre-commit hook.** Found
2026-09-05 while committing the four releases item 69's work sat on top of.

**THE GATE IS RED AND HAS BEEN FOR AT LEAST TWELVE DAYS.**
`.git/hooks/pre-commit` runs `check.py`, which ORs every leg's exit code
together. `nav_gate.py --all` reports `3/136 shell(s) FAILED traversal`:

    night_pawn                              stair_0 no_path (islands 0 / 1)
    primos_pizza                            stair_0 no_path (islands 1 / 3)
    cbp_town_finale_midbalanced_schemafixed stair_0, stair_1 no_path

All three are stair endpoints baking onto DISJOINT navmesh islands, which is
a geometry-or-bake question, not a spec question -- none of the three specs
was touched by 0.101.1's surgery, and the 0.103.0 change that surfaced this
is geometry-neutral by construction (`presets.make` reads `seed` only under
`if seed is not None`, `build.py` never passes it, and `gas_station` rebuilt
byte-identical .glb / .slots.json / .gameplay.json across the change).

**WHAT THIS MAY EXPLAIN, OFFERED AS A HYPOTHESIS AND NOT AS A FINDING.**
Deli Counter HEAD stopped at 0.101.0 on 2026-08-24 while the working tree
reached 0.102.1, and `USING_THE_FACTORY.md`'s one-writer-per-repo rail was
written the same day about that exact divergence. A gate that refuses every
commit is a plausible reason four good releases stayed uncommitted -- and it
is only plausible. Nobody has been asked, and the alternative (a session that
simply closed) is recorded in the rail itself.

**THE SECOND CAUSE IS STRUCTURAL AND WILL RECUR.** `build_freshness.py`
returns 1 when any `build/*.glb` is older than the newest file in
`GEOMETRY_SOURCES`, and `check.py` folds that into its exit code -- correctly:
a stale shell does not make the nav gate answer weakly, it makes it answer
wrongly with confidence. But ten of the shells it grades are `lf_*`, Level
Factory's own composed output, written into Deli Counter's `build/` and
TRACKED there (`git ls-files build | grep lf_` -> 10 manifests). So:

* editing any geometry source fossilises them along with the real library,
  and clearing the gate means rebuilding Level Factory's transients from
  Level Factory's transient specs, inside Deli Counter's repo;
* `building_library.index` already excludes them as `non_source` with a
  written reason, so the library ITSELF does not offer them to a lot -- only
  the freshness gate cannot tell them apart.

This is the same boundary roadmap 70 measured from the other side, where
`cold_run.py` counted the pipeline's own writes into a tool repo as human
interventions. One repo is both source and sink, and the two tools disagree
about which files are evidence.

**WHAT WAS DONE, AND WHAT WAS NOT.** The five commits of 2026-09-05 were
made with `--no-verify` and the attribution written into every message, which
is the one use `USING_THE_FACTORY.md` sanctions -- "only for a failure already
attributed to something pre-existing and written down". Every other leg of
`check.py` passes: specs, audit, layout lint, stair regression (48 variants, 0
failures), build freshness (139 shells up to date after the rebuild) and
catalog freshness. Nothing was done about the three shells.

**WHAT WOULD CLOSE THIS.** Either fix the three stair bakes, or decide the
three are dead demo content and retire them -- but decide, rather than leaving
a red gate that every future commit has to be waved past, because a gate
everyone bypasses is a gate that is not there. The `lf_` half wants the
freshness check to know what `building_library.index` already knows: an id
beginning `lf_` is not this library's to grade.

*STATUS: OPEN 2026-09-05 -- MEASURED, NOT FIXED. NINE PIXELCOAT PROFILES,
FOUR ZOO STYLES WITH REAL SPECIES COVERAGE, AND AN INTERSECTION OF TWO. EVERY
BRIEF EVER WRITTEN USES ONE OF THOSE TWO, WHICH IS NOT HABIT -- IT IS THE ONLY
THING THAT BUILDS. THIS IS THE GENERAL FORM OF ITEM 97 AND A HARDER CEILING ON
LEVEL DIVERSITY THAN 37 OR 69 WERE.*

**99. A theme has to exist in two repos, and only two do.** Found 2026-09-05
while designing cold run 5 around vocabulary the tools had never been asked
for. The archetype and the site shape had unused values to draw on. The theme
did not.

    theme               pixelcoat profile    zoo species carrying it
    rockay                     yes                  56 / 56
    delco                      yes                  39 / 56
    center_city                NO                   54 / 56
    industrial_flats           NO                   54 / 56
    bank                       yes                   0
    casino                     yes                   0
    stadium                    yes                   0
    street                     yes                   0
    rockay_civic               yes                   0
    rockay_retail              yes                   0
    rockay_service             yes                   0

**BOTH HALVES ARE REAL AND THEY FAIL DIFFERENTLY.** A Pixelcoat profile with
no Zoo species resolves the skin and the kit still renders flat colour -- the
`delco_1997` failure of item 97, except these seven pass the theme preflight
because a profile DOES exist, so they fail later and more quietly. A Zoo style
with no Pixelcoat profile is refused at preflight, which is the better
failure. `center_city` and `industrial_flats` are Zoo's two best-covered
styles after `rockay` and neither can be asked for.

**WHY IT MATTERS MORE THAN IT LOOKS.** Items 37 and 69 were about variety
WITHIN a level -- different buildings, different candidates. This is variety
BETWEEN levels, and it is capped at two looks no matter how many buildings,
seeds or archetypes the rest of the pipeline learns to vary. A brief asking
for anything else gets flat colour or a refusal.

**WHAT WOULD CLOSE THIS.** Not a fix, a decision and then content: either
Pixelcoat grows profiles for `center_city` and `industrial_flats` (cheapest --
the Zoo coverage is already there at 54/56), or Zoo grows species styles for
the seven profiles that have none, or the two repos agree a shared theme
vocabulary and `doctor` reports the intersection rather than each side's list.
Today `doctor` prints both lists and leaves the reader to intersect them by
eye, which is how this went unnoticed.

*STATUS: OPEN 2026-09-05 -- MEASURED AS A CONTROL DURING COLD RUN 5's
PRE-CHECK. TWO BRIEFS ON DISK ASK FOR A SHAPE THEY HAVE NEVER RECEIVED, AND
NOTHING SAYS SO. THE ARCHETYPE PATH WAS FIXED FOR EXACTLY THIS CLASS OF BUG
AND RAISES; THE SHAPE PATH STILL GUESSES.*

**100. `site_shape` silently falls back to a row.** Found 2026-09-05, choosing
a site shape for cold run 5 that had never been built.

`site_variation.SHAPES` is `("row", "L", "courtyard")` and `_SHAPE_ALIASES`
maps a brief's spelling onto one of them, with `.get(spelling, "row")` as the
last word. The comment defends it -- "refusing a spelling would stop a build
over a label" -- and the cost is that a spelling nobody added is indistinguishable
from a spelling that means row:

    site_shape courtyard     -> courtyard
    site_shape street_block  -> row          <-- not in the table
    site_shape boardwalk_crescent -> row     <-- not in the table

`bank_block_001` asks for `street_block`. `category5_baie_dore_001` asks for
`boardwalk_crescent`. **Neither has ever been laid out as anything but a row**,
through every evaluation either mission has had. `courtyard` had never been
built by anything until cold run 5 asked for it by its exact alias.

**THE PRECEDENT IS IN THE NEXT FILE ALONG.** `_preset_for` used to end in
`return "bank"` and every lot-demo mission silently built banks; it now raises,
and its docstring says why: "a wrong-but-plausible building is the worst
failure this adapter can produce -- the pipeline succeeds, every gate passes,
and the deliverable is the wrong archetype." A wrong-but-plausible SITE is the
same failure one level up.

**WHAT WOULD CLOSE THIS.** Not necessarily raising -- the comment's objection
to stopping a build over a label is fair. Saying so is enough: a brief whose
`site_shape` is not a known alias should print what it asked for, what it got,
and the aliases that exist, in the voice `USING_THE_FACTORY.md` asks every tool
for. Then add `street_block` and `boardwalk_crescent` to the table, or change
the two briefs, deliberately and once.

*STATUS: OPEN 2026-09-05 -- MEASURED ON A SHIPPED PACKAGE. THE EXPORT
DELIBERATELY REPLACES DISPATCH'S `mission.tscn` WITH ITS OWN PORTABLE ENTRY,
WHICH IS CORRECT, AND TWO DISPATCH FILES STILL SHIP NODE PATHS INTO THE TREE
THAT WAS REPLACED. ZERO OF THOSE NODE NAMES EXIST IN ANY SCENE IN THE PACKAGE.
THIS IS ITEM 50'S STALENESS ON THE SIBLING FILES OF THE SAME PRODUCER, AND IT
LANDS ON THE ONE INTERFACE THE CONSUMING GAME READS FIRST.*

**101. The handoff hands the server addresses that resolve to nothing.** Found
2026-09-05 reading `LF_precinct_yard_001.portable-godot` to answer "what parts
of the pipeline are in this package".

**THE OVERWRITE IS NOT THE DEFECT.** `export.py` says so in a comment written
for roadmap 50: the export copies Dispatch's handoff directory in, "overwrites
`mission.tscn` with its own portable entry", and writes
`portable_resource_manifest.json`. That is right. LF's entry is 708 bytes, has
no addons and no autoloads, and instantiates
`res://presentation/lux.applied.tscn`; Dispatch's is 28,963 bytes and 83 nodes
carrying the structured tree

    MissionRoot
    |- Functional
    |  |- Geometry (LotSite, Shell)
    |  |- Collision
    |  |- GameplayAnchors (PlayerStarts, Objectives, ExtractionPoints,
    |  |                   Interactables, Triggers, AISpawnZones)
    |  \- NavigationHints
    \- Presentation

Two producers, one filename, and the portable one has to win -- a package that
requires an addon is not portable.

**WHAT IS THE DEFECT.** Item 50 found Dispatch's `resource_manifest.json`
describing a package that no longer existed, and DROPPED it: "two answers to
one question". The same reasoning was never applied to its siblings. Measured
on this package:

    file                                  Functional/ paths   Presentation/
    runtime_ownership_requirements.json           8                 5
    gameplay_anchors.json                         9                 0
    mission_manifest.json                         0                 0
    navigation_hints.json                         0                 0
    proposed_beat_graph.json                      0                 0
    interactives.json                             0                 0

And in every `.tscn` the package ships:

    Functional 0   Presentation 0   GameplayAnchors 0   Objectives 0
    Interactables 0   PlayerStarts 0   ExtractionPoints 0
    AISpawnZones 0   NavigationHints 0

So `"node": "Functional/GameplayAnchors/CoverPoints/deli_counter:AUTO_EVIDENCE_RACK"`
names nothing. Every cover point, objective, extraction point and AI spawn zone
is addressed into a tree the export removed.

**WHY IT MATTERS MORE THAN A STALE MANIFEST.** These two files are the
handshake to the layer this factory deliberately does not own. `PIPELINE_MAP.md`
is explicit that replication, authority and gameplay belong to the consuming
game, and `runtime_ownership_requirements.json` exists to tell that layer what
it must own -- `authoritative_owner: server`, `replication_required: true`,
`late_join_state_required: true`, per anchor. It is the first file an
integrating team opens, and its addresses are dead on arrival. The DATA
survives: every anchor still carries its position, so this is recoverable
rather than lost. What is broken is the binding.

**THE PATTERN THAT SURVIVED, and it is the clue to the fix.**
`interactives.json` is unaffected, because it addresses by stable `id`
(`courthouse_a01:if:...`) and never by node path -- the ids Deli Counter
derives from PLACE rather than from position in a tree. A contract keyed on
identity survived a re-parent that a contract keyed on tree position did not.

**WHAT WOULD CLOSE THIS -- three shapes, and this item does not choose.**

1. **Make the addresses true.** LF's portable entry instantiates the content
   under the same root names Dispatch declares, so `Functional/...` resolves.
   Most work, and it keeps a structured tree that a server-authoritative game
   genuinely wants.
2. **Rewrite the paths at export.** The export already rewrites `res://` refs;
   rewriting `node` fields to what it actually shipped is the same class of
   fix, and cheaper.
3. **Drop the node fields and keep identity.** Follow `interactives.json`:
   position plus stable id, no tree address. Smallest, and it gives up the
   convenience of a path.

What is NOT acceptable is the current state, where the package asserts a
binding it does not carry -- the same shape as item 55 (fixtures with no art)
and the export declaring `godot_version: 4.7` while telling the engine nothing
(fixed in level_factory 0.55.0).
