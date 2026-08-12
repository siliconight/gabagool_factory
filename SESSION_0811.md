# Session 0811 — what Laser Tag can and cannot tell you about a level

Continues `SESSION_0810.md`. Three patches, one experiment designed to be
refuted and duly refuted, and one finding that changes what the grade is for.

**The short version:** of Laser Tag's 100 points, **60 are about the map and 40
are not**, and **25 of those 40 are structurally unreachable**. The number to
move is 40/60, and it is currently 40/60.

---

## The headline: the score is a step function, and this map sits on a plateau

`lot_demo_001` seed 5118 was evaluated five times over two days while the
palette, the lighting, the occlusion model, the crew size, the crew spawns and
the crew health all changed:

```
                                     total   map/60   encounter/40
palette + lighting + occluders          45      40         5
the 35 m conservatism                   45      40         5
crew of four, one spawn tile            10       -         -    (harness broke)
crew of four on a cleared ring          45      40         5
crew of four at 6 health                45      40         5
```

The total moved **once**, and that once was the harness failing to run.

Underneath it, between the last two rows alone:

```
                                   crew 1     crew 4     crew 4 hp6
shots_fired                           390       1522           1624
enemy_deaths                            6         91            108
avg_enemy_deaths_per_run             0.24       3.64           4.32
team_wipe_count                        25          2              0
avg_time_to_first_enemy_shot         0.38       2.06            2.2
player_stuck_events                    50       1290           1179
```

A **15× change in kills** and team wipes going **25 → 0**, and not one category
score moved. Every threshold is straddled:

```
cover           0.45, 0.32, 0.34   all >= 0.15          -> 20 every time
npc_pathing     3.00, 1.96, 1.72 per run, all > 1.25    -> penalty capped, 10
sightlines      overexposed > 0.15 every time           -> 10
traversal       route 0% every time, stuck > 0          -> 0 (floored twice)
combat_pacing   0.38, 2.06, 2.2   all < 3.00            -> 5
```

**The grade has about four reachable values in this regime.** It cannot see the
difference between a map where the crew is wiped 25 times out of 25 and one
where it is never wiped at all.

---

## Three patches

| patch | file(s) | bytes | sidecar |
|---|---|---|---|
| `patch_lot_crew_ring.py` | `lot/site_spawns.py`, `lot/lot.py`, `commands/__init__.py` | 50,713 → 53,893; 98,891 → 99,766; 104,344 → 104,856 | `.pre_crewring` |
| `patch_lf_score_split.py` | `packages/validation/lasertag_report.py` | 25,121 → 28,961 | `.pre_scoresplit` |

(`patch_lf_mission_scenario.py` landed late on the 10th and is written up there.)

### The crew ring

Giving `lot_demo_001` a `crew_size` of 4 sent the grade to **10/BROKEN**: zero
shots by either side, nobody dead, every run timing out at 180 s, 116 stuck
events. `LT_MapEvalHarness.spawn_players` puts every crew member on
`player_spawns[i % size()]` and `lot.py` wrote exactly one hook — so four
capsules landed on one coordinate, interpenetrated, and none of them could path.
With `shots_fired == 0` the scorer zeroes sightlines, cover *and* pacing
outright, which is how 45 collapses to 10.

Laser Tag has always supported a crew. `_walk` matches player spawns with
`begins_with(HOOK_PLAYER_SPAWN)`, so `LT_PlayerSpawn_1..N` are discovered with
**no change to Laser Tag at all**. Lot had only ever written one node. Fifth
instance of the pattern: a seam cut on one side, nothing threaded through.

`site_spawns.crew_spawns` now returns one position per crew member on the same
nearest-first rings `clear_crew_spawn` walks, each `outdoors()` and
`CREW_SPACING = 2.0 m` clear of everyone already placed. Index 0 never moves —
re-deciding the mission spawn would be two answers for one position. A crew of 1
emits the identical single node, so nothing already evaluated shifts.

### The score split

`metrics()` gains `lasertag_map_score` (cover + npc_pathing + sightlines, of 60)
and `lasertag_encounter_score` (traversal + combat_pacing, of 40). The total is
untouched — it is Laser Tag's number and redefining it would be a second opinion
about someone else's report. Nothing blocks; no ranking was rewired.

**Honest assessment: it did not buy what it was sold as.** The classification is
correct and worth having — those categories genuinely measure different things —
but splitting a quantised number into two quantised numbers adds no resolution.
The diagnosis was conflation; the bigger problem is quantisation. Keep the
patch, credit it with bookkeeping and not insight.

---

## The experiment, and its refutation

`crew_health: 6` went into the brief with the hypothesis **and its falsifier**
written down in advance:

> if `route_completed` is still false at 6 health, traversal is unreachable by
> encounter tuning and the next question is the bot's halt-on-sight behaviour,
> not the numbers.

Result: **`team_wipe_count` 2 → 0**, kills 3.64 → 4.32 of 6, survival 12.0 →
15.8 s — and `route_completion_rate` **0.0**, with 18 of 25 runs still timing
out.

The crew is not dying. **It never walks.** It ends each run with roughly 1.7
guards alive, and `LT_BotPlayerController` advances its route only in the `else`
of "can I see an enemy", so one survivor freezes it for three minutes. Health
bought +0.68 kills per point; reaching 6.0 would need health 8 or 9, which is
tuning the encounter into triviality to satisfy a metric.

**Traversal's 25 points do not measure traversal. They measure total victory.**
No arrangement of geometry earns them and no sane encounter does either.

---

## What this means for the pipeline

**Laser Tag earns its keep through findings and raw metrics, not its score.**
Traceably, its findings have caused three geometry fixes: `clear_crew_spawn`
(132 stuck events at one point), the real-collider occluder fix (its raycast
disagreed with Lot's footprint rects), and the reverted 35 m conservatism (34 →
75 enemy-stuck caught a bad patch). Nothing else in the pipeline would have
noticed any of them.

Its continuous metrics are the signal:
`shots_blocked_by_collision_percent`, `avg_enemy_deaths_per_run`, stuck-per-run,
`avg_time_to_first_enemy_shot`, `team_wipe_count`. Every one of them moved
meaningfully this session. None of them reach the run line or candidate
comparison — **that is the fix the score split reached for and did not make.**

The encounter is now in a reasonable place and should be left alone: the crew
survives, clears two thirds of the opposition, is never wiped, and comes under
fire at 2.2 s against a 3.0 s target.

---

## Open, in the order I would take them

1. **Lux reaching the preview.** Never once seen. `walk_content_dir` returns
   `themed_site_assemble/out` and never looks at `lux_apply/out`;
   `_find_level_scene` prefers `site_lux.tscn` while lux writes
   `lux.applied.tscn`. `grep -rn "site_lux"` returns two lines, both inside the
   function that reads it. Not a rename — lux's `out/` holds the scene and two
   sidecars while the buildings it instances live upstream, so something has to
   decide where they are assembled.
2. **Surface the continuous metrics** on the run line and in candidate
   comparison, instead of a grade that cannot see a 15× change in kills.
3. **`sightlines` 10/20** — 37% of walkable positions visible to 3+ enemy
   spawns. Enemy *distribution*, not cover. `place_enemies` spreads by distance
   and never asks whether two enemies watch the same ground. 10 points on the
   half that measures the map.
4. **`npc_pathing` 10/20** — needs stuck under 0.25/run, currently 1.72.
5. **`player_stuck_events` 1179.** The largest anomalous number in the report
   and still unexplained. Four bots in a three-minute firefight shoving each
   other is the guess; it has not been measured.
6. **`enemy_count` still does not reach Lot.** `_lasertag_hook_nodes` takes
   `enemy_count=6` as a parameter default and nothing passes the brief's value.
7. Carried: `patch_map_derived.py` unapplied, nav-gate re-bake, `--sweep`
   summary miscount, `_bridge*` copies of plate constants, by-eye roof check.

---

## Things now known that were not

- Laser Tag's scoring is **threshold-quantised**, and `lot_demo_001` straddles a
  band edge in all five categories. Large real changes register as zero.
- `traversal` requires clearing every enemy, because the bot halts on sight.
- The crew spawn hook is **`begins_with`**, so a crew needs no Laser Tag change.
- The stock scenario was the only one ever used until 10 August, on every
  mission LF has evaluated.
- An experiment with its falsifier written down before the run is worth five
  without one. This one cost ten minutes and closed a question that two days of
  patching had not.
