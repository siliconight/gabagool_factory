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

**Retracted, kept:** `stoop_breadth_walk_staged_director_RETRACTED.out.txt`. The first walk walked each copy's staged director. The first lot it reached that was staged before Lot 0.117.0 was warehouse_yard_001 seed_9004. There it failed in the `flat` arm, with no stoop in it, on "navigation map is EMPTY at QA time", and the run stopped (the docstring of `stoop_breadth.py` has the measurement). The walk now gets today's director, as `walktest.py`'s `main()` gives every run.
