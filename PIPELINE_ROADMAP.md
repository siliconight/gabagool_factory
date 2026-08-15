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
| 3 | **OPEN** | Lot places enemies twice, and nothing checks the two agree | 2026-08-12 -- both call sites re-confirmed while threading `solids` through `place_enemies |
| 4 | **OPEN** *(inferred)* | Lot emits absolute `res://` paths at source | — |
| 5 | **CLOSED** *(inferred)* | A run that evaluated nothing reported a clean pass | Closed 2026-07-27 as Level Factory 0 |
| 6 | **OPEN** *(inferred)* | The tactical advisory reads a scene that may not exist yet | — |
| 7 | **CLOSED** *(inferred)* | The certified set has drifted | Closed 2026-07-27 as **factory 1 |
| 8 | **CLOSED** | Nothing checks the SIZE of the island an anchor snaps to | 2026-08-14 -- shipped as Lot 0.28.0 + Level Factory 0.18.0; the seed_5219 report carries a |
| 9 | **CLOSED** *(inferred)* | Lot emits nav-QA anchors nothing checks | Closed 2026-07-28 as Lot 0 |
| 10 | **NARROWED** | `nav_gate.py` certifies geometry that never ships | 2026-08-14 -- quantified. `nav_gate.gd` bakes PARSED_GEOMETRY_MESH_INSTANCES; `lot.py:1430 |
| 11 | **RETRACTED** *(inferred)* | The building interiors barely bake | Retracted 2026-07-28 |
| 12 | **NARROWED** | Props bake as walkable navmesh, and nothing can reach them | 2026-08-14 -- the mechanism this item named is not misconfigured, it is ABSENT: `geometry_ |
| 13 | **RETRACTED** *(inferred)* | RETRACTED — seed 5320's vault was never broken; its walktest never ran | RETRACTED — seed 5320's vault was never broken; its walktest never ran |
| 14 | **OPEN** | Seed 5017 has a collision trap the path query cannot see | 2026-08-12 -- unchanged; re-measure after the first run on a level that has walls |
| 15 | **CLOSED** *(inferred)* | Fail-fast is mission-wide, but the failures are candidate-scoped | Closed 2026-07-28 as Level Factory 0 |
| 16 | **CLOSED** | The navmesh contains routes the collision geometry blocks | 2026-08-14 -- not a bake defect. Lot 0.40.0 fixed it as walker locomotion on 2026-08-02 (g |
| 17 | **OPEN** *(inferred)* | The pipeline has never been run cold, so nobody knows what it costs to | — |
| 18 | **OPEN** *(inferred)* | Every gate measures whether a level WORKS. None measures whether it is | — |
| 19 | **OPEN** *(inferred)* | Every tool grew a Godot half before there was a DAG to say who owns wh | — |
| 20 | **OPEN** *(inferred)* | Patina's Godot half is a renderer from before Lux was one | — |
| 21 | **OPEN** *(inferred)* | Four of eight tools have drifted from what Level Factory certified | — |
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
| 37 | **OPEN** *(inferred)* | Every building on the site is the same building | — |
| 38 | **CLOSED** | Light anchors hung below the slab, and four Deli Counter tests that we | 2026-08-02 -- cap_thick threaded into derive_light_anchors and build_light_manifest |
| 39 | **RETRACTED** *(inferred)* | Cache correctness: the mechanism is designed and never wired, and the  | RETRACTED: `--force` is not broken |
| 40 | **OPEN** *(inferred)* | The "is this called?" sweep, run | — |
| 41 | **OPEN** | The dressing layer is STRUCTURAL ART routed through the decoration cha | 2026-08-12 -- unchanged, and the one on this list a viewer notices |
| 42 | **NARROWED** | A level leaves the factory with a name that does not say what it is | 2026-08-14 -- stage 1 SHIPPED and proven on a real package: level_factory 0.26.0 (build di |
| 43 | **CLOSED** | A whole CLI spelling stopped working and nothing noticed | 2026-08-15 -- one failed stage, not nine failures, and not the cause written below. `prese |
| 44 | **OPEN** | The green boxes could be cars, and the collision would not change | 2026-08-14 -- specified by `Semantic_Proxy_Replacement_Art_Pass` and `City Collision ArtPa |
| 45 | **OPEN** | Large playable surfaces are visually flat, and the fix is not more gra | 2026-08-14 -- specified by `Surface_Dressing_Level_Depth_Guide`; nothing built. Item 41 is |
| 46 | **NARROWED** | Forty-five state machines a run, reaching nobody | 2026-08-14 -- MEASURED, and the scope inverted. The declaration is not missing; it is fini |
| 47 | **NARROWED** | A recipient with their own lighting has to take ours or take graybox | 2026-08-15 -- stages 1 through 3b have all RUN; the layer split is proven and the first co |
| 48 | **OPEN** | The same job and the same seed draw a different building on the art pa | 2026-08-15 -- MEASURED on unlit_probe_001, one workspace, one seed. `lot_assemble.candidat |

**48 items: 21 open, 16 closed, 3 retracted, 6 narrowed, 2 analysis.** 25 rest on a sentence rather than a status line -- run `roadmap_status.py --unclassified` for the list.

A status is one line above the item: `*STATUS: CLOSED 2026-08-12 -- what proves it*`. Vocabulary: `OPEN`, `CLOSED`, `RETRACTED`, `NARROWED`, `SUPERSEDED`, `ANALYSIS`.

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

*STATUS: OPEN 2026-08-12 -- both call sites re-confirmed while threading `solids` through `place_enemies`*

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

*STATUS: OPEN 2026-08-12 -- unchanged, and the one on this list a viewer notices*

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

*STATUS: NARROWED 2026-08-14 -- MEASURED, and the scope inverted. The declaration is not missing; it is finished and dropped. `deli_counter/interactives.py` + `docs/INTERACTIVES.md` emit 9 replicable state machines per building. `site.site.gameplay.json` has no `interactives` key. The shipped package contains zero files mentioning "interactive". The work is a boundary, not a design*

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

*STATUS: NARROWED 2026-08-15 -- stages 1 through 3b have all RUN; the layer split is proven and the first cold package is blocked by item 48. `LAYER_LIGHT` (0.35.0) splits Lux's apply pass out of the art layer, keeping `zoo_fixtures_build` and `lux_fixture_gate` in it; `MODE_ART_UNLIT` (0.36.0) subtracts Lux's result at EXPORT time so one build ships two archives; 0.37.0 ships `themed_site_assemble`'s site.tscn, which reached no package at all and without which an unlit one opened to nothing. Measured on lot_demo_001: unlit entry 571 B instancing NOTHING -> 688 B instancing `res://site.tscn`; 33 Lux files dropped and nothing else; shared interior folder. 3b RAN 2026-08-15 on `unlit_probe_001` through Blender and headless Godot and answered both of its questions: `lux_apply` never ran, `lux_fixture_gate` did, `dispatch_handoff <- themed_site_assemble`. Export was then blocked -- IDENTICALLY in `art-unlit` and `portable-godot`, which acquits `--unlit` -- by a functional regression that is item 48, not this item. The layer split is proven; a package built end-to-end from a cold run is not, and cannot be until 48 is*

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

*STATUS: OPEN 2026-08-15 -- MEASURED on unlit_probe_001, one workspace, one seed. `lot_assemble.candidate.seed_5017` succeeded twice in `_runs/3b/run.log` (lines 31 and 51) and drew a different building each time: graybox `cr_garage` (17 openings, 178 colliders, 12 markers), art `landmark_hall_a03` (13 openings, 176 colliders, 7 markers), with `shell.glb` byte-identical across both fingerprints. Everything that graded the mission graded the first draw. The functional lock caught it and refused the export -- this item is the redraw, not the lock*

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

### Not to be worked on
Under the boundary at the top of this file, these are downstream's model of
combat and none of them make the levels better: the crew bot's target memory or
threat response; the enemy firing at t = 0.0 despite a 0.25-0.5 s reaction
delay; anything tuned against survival time, engagement distance, kill counts or
opening timing. Laser Tag findings of that shape are information for a human at
candidate selection, not work items.

### Smaller, carried

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
