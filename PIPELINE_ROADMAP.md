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

**15. Fail-fast is mission-wide, but the failures are candidate-scoped, and that
is what makes enforcement unsafe today.** The whole point of generating five
candidates is to pick among them. But the scheduler stops the entire DAG at the
first blocked job, so one bad candidate does not get eliminated — it halts the
run, and every job after it never dispatches. That is how a Laser Tag finding on
seed 5320 stopped seed 5320's own walktest, and it is why `WALKTEST_ENFORCED`
should not be flipped yet: seed 5017 would block, and the four candidates that
pass would be collateral.

A candidate-scoped failure should eliminate the candidate, record why, and let
the rest of the DAG finish; only a mission-level job failing should stop the run.
`RunSummary.never_dispatched` (0.20.0) makes the current behaviour visible, which
is the minimum; it does not make it right. Until this exists, enforcement turns
one flawed candidate into a dead mission.

Under the boundary at the top of this file, these are downstream's model of
combat and none of them make the levels better: the crew bot's target memory or
threat response; the enemy firing at t = 0.0 despite a 0.25-0.5 s reaction
delay; anything tuned against survival time, engagement distance, kill counts or
opening timing. Laser Tag findings of that shape are information for a human at
candidate selection, not work items.

### Smaller, carried

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
