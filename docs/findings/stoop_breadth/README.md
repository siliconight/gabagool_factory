# Do the stoops and their railings change what the graders grade?

**Factory roadmap 240.** The stoop proposal (`docs/proposals/ROWHOUSE_STOOP.md`) asked for one more check before the stoops shipped. They change what Laser Tag and the walk test grade, so price them on the graders' breadth: 16 lots, both engines.

The check was never run, for the stoops (Deli Counter 0.211.x, cold runs 9271 and 9272) or for the railings after them (Deli Counter 0.212.0, cold run 9273). Each cold run graded restaurant_row_001's three candidates alike. No other mission family's lots have been graded with a stoop in them, and `docs/findings/route_snag/engine_breadth.py` stages lots built before the stoops.

## How

**The lots.** Of `engine_breadth.py`'s 16 lots, 8 have rowhome Empties in them:

- restaurant_row_001, three lots;
- warehouse_yard_001, three lots;
- bank_block_001, one lot;
- club_block_014, one lot.

Each carries 14 to 28 placed rowhomes. The other 8 lots (deli_001, gas_block_001 and crossroads_9600) carry none, so a stoop cannot reach their grade.

**The arms.** Each lot is graded three times. Every arm uses the level exactly as staged, except its `buildings/gs_empty_rowhome_*.glb`:

- `flat`: the twelve rowhomes as Deli Counter 0.212.0 builds them with `stoop=0`.
- `flat2`: the same again. This is the control: it must read identically to `flat` in every field read.
- `stoop`: the twelve as Deli Counter 0.212.0 built them, three steps up on a stoop with its railings.

Both shell sets come from the same Deli Counter (`build_flat.py`, `build_flat.out.txt`). The only differences are the stoop, its railings and the raised door. Each stoop shell carries 6 `stoop` nodes and 8 `stoop_rail` nodes, and 8 more colliders than its flat twin.

**The graders.**

- **Laser Tag:** today's addon, `--fixed-fps 60`, 25 runs from the seed its job used, under Godot Physics, the game's engine. It reads every field of the summary, the pins, and the navmesh the run baked.
- **The walk test:** the staged project's own director, walked by `lot/walktest.py`'s steps. It reads the verdict, each walker's status, the targets reached, the anchors' counts and the simulated seconds.

## Files

- `build_flat.py`, `build_flat.out.txt`: the two sets of shells, with each one's hash and node counts.
- `stoop_breadth.py`: the A/B. `results_laser_tag.json` and `results_walk.json` hold its rows, and `stoop_breadth_laser_tag.out.txt` and `stoop_breadth_walk.out.txt` hold its output.

## Results

**Both controls held on every lot.** `flat` and `flat2` read identically in every field, so each difference below is the stoops'. **Every bake sees the stoops:** Laser Tag's navmesh grows by 115 to 297 polygons a lot, and the walk test's by 115 to 297.

**The walk test: unchanged on all eight lots.** Every arm passes:

- every walker is ok and every target is reached (48 to 68 a lot);
- no anchor is stranded, behind a barrier or without standing room.

The only other change is the simulated walk, -0.4 to +0.9 s.

**Laser Tag: no stuck body at a stoop.** Over all three arms of eight lots there are 229 stuck events, and none is within 1 m of a stoop's plan box; the nearest is 10.93 m away. Neither arm has a player pin or a timeout.

    lot                            stoops  grade, flat -> stoop         route         enemy stuck
    restaurant_row_001 seed_9003     26    PASS 90 -> PASS 90           1.0 -> 1.0      0 -> 0
    restaurant_row_001 seed_9104     23    PASS 90 -> PASS 90           1.0 -> 1.0      0 -> 3
    restaurant_row_001 seed_9205     24    PASS 90 -> PASS 90           1.0 -> 1.0      0 -> 0
    warehouse_yard_001 seed_9004     15    PASS_WITH_TUNING 89 -> PASS 90   0.96 -> 1.0   0 -> 0
    warehouse_yard_001 seed_9105     14    PASS 90 -> PASS 90           1.0 -> 1.0      0 -> 0
    warehouse_yard_001 seed_9206     18    WARN 68 -> WARN 67           1.0 -> 0.96    51 -> 50
    bank_block_001 seed_9256         26    WARN 72 -> WARN 72           1.0 -> 1.0     23 -> 23
    club_block_014 seed_9282         28    PASS 90 -> PASS 90           1.0 -> 1.0      1 -> 3

**The fights move, both ways.** With the stoops in, most lots' fight fields change: shots, engagement distance, survival and deaths.

- **The two route moves are one team wipe each in 25 runs.** On seed_9004 the wipe is in `flat`; on seed_9206 it is in `stoop`. Neither had a timeout, as roadmap 242 found of every short route.
- **The enemy-stuck moves are 10.9 m or more from any stoop.** On seed_9104 the 0 -> 3 is two enemies standing still at (-2.05, 0.02, 12.24) and (-2.75, 0.02, 12.24), the near side of the street, 18 m from the nearest stoop. Cold runs 9271 to 9273's own jobs carry the same three events, and 9270's has none. Those runs' notes called the candidates' grades "as in 9270", which is true of the grades. The cause of that spot is not measured here.

What is measured: the stoops change the navmesh, and the 25 seeded runs play their fights differently. What is not: whether any other geometry change of that size would move them as much. No null perturbation was run, so these moves are reported, not attributed to cover or sightlines. Roadmap 242 records the same swing from street furniture ("Laser Tag's route on a lot swings with any change to its street furniture"), and its body now carries this run as the swing measured again under Laser Tag 0.29.0.

## The seed_9104 enemies, looked at (`enemy_pin_probe.gd`, `enemy_pin.txt`)

What stands where the two enemies stop, on cold run 9274's staged Laser Tag level, loaded headless:

- **Nothing touches them.** A capsule of the contract's player size (0.35 m) on either point overlaps
  nothing. At 0.65 m it reaches building b1's south wall (`ext_col_0_S_seg2`, `seg3`).
- **The wall is the only solid near.** Eight rays at waist height find it 0.58 m to the south, which leaves
  a body 0.23 m clear. Every other way is open for 6 m, but one ray finds a cover piece 5.85 m off.

So **the stop is not geometry**.

Nor is it a fight: in the six seconds before each stuck event, the report has no sighting and no shot from
either enemy (cold run 9274's job, runs 10 and 15). LT_Enemy_02 sights a player only 0.33 s after its own
stuck event in run 15.

Laser Tag counts an enemy stuck when it still has a destination and has moved less than its threshold over
the window (`LT_EnemyMovement._update_stuck`), with no test for what it is doing. LT_Enemy_02 stops at the
same place at the same time (t 9.07) in two runs, before any contact. That read as a destination the body cannot reach -- for example, one behind b1's wall, with the path ending at
the wall.

**RETRACTED, KEPT ABOVE: the unreachable destination.** `enemy_stop_trace.py` measured it
(`enemy_stop_trace.out.txt`). It patches a copy's `LT_EnemyBrain._on_stuck` only and runs the job's 25 runs.
THE CONTROL: the copy's summary and its three EnemyStuck events are the job's.

- **Each stuck enemy's target is reachable.** It is the crew member it seeks, about 36 m east. The path has
  49 points, and the enemy is at index 1, whose corner lies 1.84 m (or 2.55 m) east on flat ground. It is
  not finished and not reached.
- **Its velocity after `move_and_slide` is zero.**
- **That frame's one slide collision is another enemy.** LT_Enemy_02, in runs 10 and 15, is pressed against
  LT_Enemy_06, standing just east of it in its way. LT_Enemy_04, in run 10, is pressed against LT_Enemy_02.

So three enemies queue single file on one path along b1's south wall. In the SEEK state the brain re-sets the
destination every physics frame. Laser Tag's enemies steer with no avoidance, so a body pushes straight into
the one ahead, and `_update_stuck` counts a body held by a teammate as stuck.

**The 0 -> 3 is congestion, not geometry.** It is the stoops' navmesh change lining three enemies up on one
path -- the same class of count Laser Tag 0.28.0 and 0.28.1 took out of the crew's.

**Measured on the other lots** (`enemy_stop_trace.py --lot`, `enemy_stop_lots.out.txt`). Each lot as staged,
graded by today's Laser Tag with `_on_stuck` traced. THE CONTROL: two runs read identically, and they did on
every lot. Each event is classed by what this frame's move met:

    lot                              grade     enemy stuck   held by
    warehouse_yard_001 seed_9206     WARN 68       51        51 a teammate
    bank_block_001 seed_9256         WARN 72       23        22 a teammate, 1 a crew member
    club_block_014 seed_9282         PASS 90        1         1 the level (static)
    restaurant_row_001 seed_9104     PASS 90        0         -   (9264's lot, before the stoops)

**RETRACTED, KEPT: "73 of 75 are a body held by another body".** The sum is 74 -- 51 + 22 another guard,
1 a crew member -- and the class asked whether ANY of the frame's contacts was another body, not whether
a body was all that held it: Laser Tag 0.30.0, which asks the second (every contact but the floor a
body), still counts 13 of seed_9206's 51 as stuck, so those 13 had another guard and a part of the
level in the same frame (`docs/findings/route_snag/blocked_breadth.out.txt`). **74 of 75 had another body
among their contacts**, and one had only the level.

**The arithmetic of the score** (`LT_ScoreCalculator._score_pathing`): past 0.25 events a run, NPC Pathing
loses `round(20 x stuck per enemy per run)` of its 20. With six enemies that is 7 points for seed_9206's 51
and 3 for seed_9256's 23. Both WARN grades would read 75 -- PASS_WITH_TUNING's line -- without the
congestion. That is the arithmetic, not a run.

**Run, under 0.30.0** (`docs/findings/route_snag/blocked_breadth.py`): seed_9256 reads 75, as the
arithmetic said; seed_9206 reads 73, WARN, because 13 of its 51 are still counted -- 2 points.

This is Laser Tag's (roadmap 242): the class of count 0.28.0 took out of the crew's.

**Retracted, kept:** `stoop_breadth_walk_staged_director_RETRACTED.out.txt`. The first walk walked each copy's staged director. The first lot it reached that was staged before Lot 0.117.0 was warehouse_yard_001 seed_9004. There it failed in the `flat` arm, with no stoop in it, on "navigation map is EMPTY at QA time", and the run stopped (the docstring of `stoop_breadth.py` has the measurement). The walk now gets today's director, as `walktest.py`'s `main()` gives every run.

## The 23 Laser Tag 0.30.0 still counts (`enemy_stop_trace.py --lot --contacts --raw`)

`enemy_stop_residue.out.txt` on the four lots with any left, `enemy_stop_residue_raw.out.txt` with every
trace line on the two that hold 21 of them. Under 0.30.0 only a guard it still counts stuck reaches
`_on_stuck`, so each traced event is one of the 23; on each lot the trace's count equals the breadth's,
and its two runs read identically (THE CONTROL). Each is classed as 0.30.0 asks, the floor left out:

    lot                            stuck   as 0.30.0 asks     where
    warehouse_yard_001 seed_9206      13   13 level+body      all within 0.06 m of (1.50, 16.86)
    crossroads_9600 seed_9600          8    8 level           all within 1 mm of (44.41, 0.00, -6.63)
    deli_001 seed_9191                 1    1 none            (-2.85, 0.00, -14.80), nothing but the floor
    club_block_014 seed_9282           1    1 level           (-11.21, 0.01, 21.30), against Site/cover_142

**warehouse_yard_001 seed_9206, a wall's end and a guard ahead.** Each guard touches building b1's wall
where its south and west runs meet (`ext_col_0_S_seg22` or `ext_col_0_W_seg0`, the face at x 1.85,
normal -x) and another guard. The path's first point, the mesh under the body, is at x 1.45 -- the mesh's
edge, 0.40 m from the face -- so the guard stands 5 cm off the mesh. The next point is round the wall's
end, (1.75, 17.65), 0.83 m away, and the heading to it runs into both contacts: 48 degrees off the other
guard's normal and 72 off the wall's (the first event; the twelve others stand within 0.06 m of it).

**crossroads_9600 seed_9600, a stair ramp's low side.** Each guard's capsule rests on the long side edge
of building b2's stair ramp `stair0ramp_0`, 0.18 m above the floor (contact at (44.54, 0.18, -6.90),
normal (-0.38, 0.50, 0.78), 60 degrees from up). The collider is a box pitched 37.5 degrees, 1.6 m wide
(its corners from `pvp_station_ref.glb`); from the box, a 0.35 m sphere at the guard's place touches that
edge at that point with that normal, to two decimals. The path runs from the floor beside the ramp,
(44.35, -6.65), to a point on its top, (44.55, -7.25), crossing the side edge: the bake joins the floor to
the ramp across its side near the foot. The body walks up 0.1025 m with no step-up
(`clearances.unassisted_step_max_m`); the bake climbs one 0.15 m voxel; `agent_contract.json`'s
`agent_max_climb_derivation` names that band and leaves a rise in it to the consumer's step-up. Laser
Tag's crew bot steps up to the contract's 0.5 m (`LT_BotPlayerController._try_step_up`); its guards'
`LT_EnemyMovement` steers straight at the next path point, with no step-up and no keep-on-mesh.

Not measured: whether either place holds a guard that keeps to the mesh and steps up -- that is the next
change's breadth.

**Measured under Laser Tag 0.31.0** (the guards keep to the mesh and step up;
`docs/findings/route_snag/README.md`, "Laser Tag 0.31.0"): crossroads_9600 seed_9600's 8 are gone, and
warehouse_yard_001 seed_9206's are not -- 14 at the same wall's end (`enemy_stop_residue_0310.out.txt`,
the same trace with 0.31.0's addon), five of them touching only that wall and the floor, their velocity
pointing away from it, not moving.
