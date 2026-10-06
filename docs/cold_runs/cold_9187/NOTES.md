# Cold run 9187 -- 0 interventions; the stair-head trim proven in a level, and an enemy inside an Empty found and fixed

The proof run for Deli Counter 0.190.0. Every stair ramp's head is trimmed
onto its landing, and no generator draws a flight narrower than a corridor.
It is 9186's brief, restaurant_row_001.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**
- Findings went from 67 to 62 against 9186, with 0 blockers.
- **Themed fitness:** 102 of 127 shells are fit for a theme, measured with
  Level Factory's own `themed_fitness`. twin_a01 and deli_a03 are both fit;
  9186 graded 101.
- **Bake:** 485 models and 1,478 primitives lightmapped, 6 kept dynamic;
  118 steady rigs baked, 31 failing left live. 4,313 users, 96.2 s.

## The stair head, against 9186

seed_9003's mission is the same in both runs: spawn at the far building, and
the objective and extraction at deli_a03. The objective is the deli's upper
floor (`LT_ObjectivePoint` at height 3.30), so the route goes up the stair
and has to come back down.

| | 9186 (Deli Counter 0.189.0) | 9187 (0.190.0) |
|---|---|---|
| runs finished | 0 of 25 | **25 of 25** |
| objective reached | -- | 25 times |
| player stuck events | 3,148, all in one 2 m cell at the stair head | **3**, all on the ground floor |
| grade | dropped, `LT_ROUTE_NEVER_COMPLETED` | PASS_WITH_TUNING, 79 |

- The three stuck events in 9187 are at (6.0, 0.0, -29.0), twice, and
  (-13.5, 0.0, -27.9). They are at ground level, nowhere near the head of a
  stair 3.3 m up.
- seed_9003's two other buildings differ from 9186's: depot_a01 and
  self_storage_a01, where 9186 drew marina_a03 and country_club_a02. Fitness
  changed with twin_a01's return, and a change in which shells are fit
  changes every seed's draw. The deli and its role are the same.

## The candidates

| candidate | buildings | walk test | Laser Tag |
|---|---|---|---|
| seed_9003 | deli_a03, depot_a01, self_storage_a01 | PASS | PASS_WITH_TUNING 79, 25 of 25 |
| seed_9104 | deli_a01, office, rail_station_a02 | PASS, **picked** | PASS_WITH_TUNING 79, 25 of 25 |
| seed_9205 | deli_a03, parking_garage, supermarket_a01 | PASS | WARN 68, 22 of 25; `NO_REACTION_TIME` |

- Godot's path error fired 0 times in all three walk-test logs.
- seed_9205's lot also redrew. In 9186 it stood warehouse_a01 and
  auto_shop_a01 and was refused on `UNREACHABLE_SPAWN`. That refusal did not
  recur here because the lot changed, not because anything fixed it.

## What 9186's refusal turned out to be

Read while 9187 ran (`docs/findings/enemy_inside_an_empty/`).

**The defect.** Every `UNREACHABLE_SPAWN` refusal in cold runs 9164 to 9186,
four of them, was Enemy_5 standing inside an Empty: e15 in 9170 and 9174, e9
in 9179 and 9186.
- Lot's `place_enemies` pushes a route sample sideways until `outdoors()`
  calls it open ground. `outdoors()` read `buildings` only, and an Empty is a
  blocker.
- **The control:** all 18 of 9187's enemies stand in the open, and so do
  the other 17 of 9186's.

**Shipped after the run, so not in it:** Lot 0.97.3.
- Spawns keep out of every blocker. Enemies also keep out of the band
  behind an Empty row's front line, the ground the row's fences shut off.
- The fixture test is 9186's site as drawn.
- With the collision reading Lot passes, 0.97.3 moves no enemy on any of
  9187's candidates. The next run will measure it in a level, not prove the
  fix.

## Not looked into

- seed_9205 here: 36 enemy stuck events across 25 runs, and players
  surviving 8.3 s on average (`LT_MAP_NO_REACTION_TIME`). It was not picked.
