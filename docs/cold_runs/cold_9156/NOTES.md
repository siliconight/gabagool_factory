# Cold run 9156 -- 0 interventions; window air conditioners and bars on the Empties

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack** (the walker: "then do the window AC units and bars"):
- Deli Counter 0.181.0 chooses what hangs in each Empty window and writes
  it on the slot beside the pane:
  - `bars` on a barred pane;
  - `ac` on 30 in 100 eligible windows upstairs and 10 at the street;
  - never behind bars, in a boarded window, or in the box fan's.
- Patina 0.26.0 orders `window_bars` over the opening and `ac_unit` on the
  sill. Only on facade windows, and exempt from the opening keep-out beside
  `frame`.
- Zoo 1.69.0 builds them, and the pane stops painting bars:
  - **the unit:** a 52 x 36 cm cabinet, 30 cm out of the wall and back to
    the pane, with fins on its street-facing back, flank louvres, accordion
    panels to the jambs, and two L brackets;
  - **the bars:** 18 mm uprights on two bolted straps, black painted iron.
- Level Factory 0.140.0, Lux and Lot unchanged.

**Result:** every leg ran in 33 minutes, `INTERVENTIONS: 0`. Art exited 1
on 55 findings, as before. No `STEM COLLISION`. The walk copy is this
run's.

## Before the run

- **Every repo's suite passed.** Deli Counter's `check.py` reported "All
  checks passed" after `build.py --all` rebuilt all 139 shells, and the nav
  gate passed 138.
- **Each new test failed on the version before it.** Deli Counter 5 of 6,
  Patina 6 of 6, Zoo 8 of 8.
- **Zoo planned all 139 built buildings with 0 stem collisions.** That was
  checked because Deli Counter's slots changed.
- **A Blender pre-flight built two real rowhomes'** dressing with the new
  orders: 9 meshes each, `refused 0`, the bars in a new material
  `M_Skin_metal_painted_delco_1997_121212`, the units merged into the
  gutters' white.
- **The geometry is the right way round** (rowhome_a, its south face at
  y = -6.15):
  - the bars stand at -6.151 to -6.199, and z 0.80-2.50 runs 5 cm past the
    opening's 0.85-2.45;
  - the south metal mesh reaches -6.459 out (the unit and its fins) and
    -6.020 in (the pane).

## What the run built

Across the six rowhome variants: 3 barred windows and 7 air conditioners.

| | bars | units | placed |
|---|---|---|---|
| a | 1 | 2 | x2 |
| b | 1 | 2 | x4 |
| c | 0 | 1 | x5 |
| d | 0 | 2 | x6 |
| e (vacant) | 0 | 0 | x2 |
| f | 1 | 0 | x7 |

Placed, that is 29 units and 13 barred windows in the level.

- **Dressing GLBs:** 9 meshes on a rowhome with a barred window, 8
  otherwise. The units add none; each barred side adds its own black-iron
  mesh.
- **The bake's users went 5,125 -> 5,138, +13.** One bar mesh per barred
  placement.
- **Lights** (`patches/zoo_cover_merge/cover_light_census.gd`): 245 cover
  meshes, none reached by more than 8 live lights, the most any gets is 5.

## Frames

`docs/findings/empties_fixtures_9156/`, the same five views with and
without fill. `fixtures_closeups_9156.png` crops a unit and two barred
windows:
- **The unit reads as a window air conditioner:** white, fins across the
  back, louvres on the flank, two brackets on the brick below the sill.
- **The bars:** black uprights on a strap over a lit room, running past the
  sill onto the brick. The pane behind shows only its room now.

## The price

A = 9155's package, B = 9156's, A2 = 9155's again: 53 station x heading
pairs, measured back to back.

- **Draws:** median +4, mean +5, at most +18 a view (longest_sightline at
  90: 5,904 -> 5,922). The control A2 - A: 0 everywhere.
- **Median frame**, against the mean of A and A2 over the 52 headings where
  those two agree within 1 ms: median +0.066 ms, mean +0.145. The control's
  own median is +0.017, so the median view's cost is about 0.05 ms.
- **Two headings moved far more than their draws can explain**, and both
  hitched in the merge pricing an hour earlier, in a different run:
  - camera_socket_6 at 270: median 16.7 -> 20.9 ms and p95 17.7 -> 35.0 ms,
    for +13 draws (9155's notes: A 29.7 against A2 23.9 there);
  - defender_spawn_22 at 180: +2.0 ms for +0 draws (9155: 3.2 against
    2.1).

  At the 2-3 us a draw this harness has measured, +13 draws is about
  0.04 ms. These are hitches in a single run, not the fixtures' cost.
- **The harness light census:** 61 of 5,192 meshes over the cap, the same
  61 as 9155. The 13 bar meshes add none.

**The finding for the instrument:** those two headings hitch in one run of
three often enough to swing a mean. A price read from a single run per
package needs the mean-of-two control and the stable-heading summary
(`patches/zoo_cover_merge/price_robust.py`), or a harness that samples each
heading more than once.

Outputs: `price_fixtures.txt` (`compare_price.py`) and
`price_fixtures_robust.txt` (`price_robust.py`).
