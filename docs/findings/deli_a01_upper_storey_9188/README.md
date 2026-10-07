# deli_a01's upper storey is cut off from the street in 9188's site bake

Measured 2026-10-06. **In progress: the cause of the main break is not
established.** What follows is what the bake says, and which reads would
decide the rest.

**The artefact, and what made it.** A `run_bake_sweep.py --dump`
(`docs/findings/stairwell_on_one_grid_in_four/`) of the scene Laser Tag
grades for cold run 9188's picked candidate, seed_9104:
`workspaces/cold-9188-ws/.level_factory/staging/restaurant_row_001.laser_tag_evaluate.candidate.seed_9104`.
This is the GREYBOX site that `lot_assemble` builds, not the themed export.
The bake has 165 islands. Island 0 holds the home point and 16,944 m²; it is
the street.

**Frames and units.** Level (x, y) is Godot (x, -z). The building frame is
level minus deli_a01's `at`, (-58, 1.01), at rot 0. That is the frame of
`deli_counter/build/deli_a01.gameplay.json`, so its rooms, openings and
stair footprints read directly against it. Heights are navmesh polygon
heights in metres: ground floor 0.25, story 1 3.55, roof 6.85, basement
-3.05.

## What is reachable, and what is not

- **The ground floor and the basement are island 0.** Probed 0.3 to 3.5 m
  either side of both doors (`front_customer_entry` on the south wall,
  `alley_entry` on the west): island 0 on both sides, at both doors.
- **The upper storey is not.**
  - Island 9: 592 m², heights 0.2 to 3.5. It holds the up-stair, its lower
    landing, `upper_hall`, `manager_office` and `apartment_hideout`.
  - Island 10: 186 m², height 3.55. It is `server_room`.
- Island 12 (957 m², 6.85) is the roof, which nothing is meant to reach.

**Refuted, kept.** The first report of this, in conversation on
2026-10-06, said "778 m² of deli_a01 is disconnected from the street". The
area was right; the implication that the deli was shut was wrong. The
building is open. Its upper storey is not.

## Break 1: the up-stair's lower landing

- **Island 9 reaches the ground.** It has floor-height polygons (0.25) at
  building x -16.25..-14.15, y 11.6..12.9. That is north of both stair
  footprints:
  - `deli_stair_down`: x -16.6..-15.0, y 7..11, floors -1 and 0;
  - `deli_stair_up`: x -12.6..-11.0, y 7..11, floors 0 and 1.
- **Island 0's stairwell floor stops short of it.** Between the two stairs
  (x -14.05..-13.05) it ends at y ≈ 11.2.
- **The closest approach is 0.41 m,** at building (-14.10, 11.44), with
  both sides at 0.25. It is not a step.
- **Not established: what fills that 0.41 m.** Story 1's interior walls
  leave seams of exactly 1.30 m (below). At any ordinary wall thickness,
  that implies an erosion much larger than 0.2 m a side. If so, 0.41 m is
  too narrow to be an obstacle eroded on both sides, and the gap is a hole
  or a crack in the floor rather than a thing standing on it. Two reads
  decide it, and neither has been made:
  - the bake's agent radius (`agent_contract.json` `nav_bake`, and the
    settings `run_bake_sweep` passes);
  - the shell's geometry in building x -15..-12.6, y 11.0..11.8 on the
    ground floor.

## Break 2: the server room has no door

- **Island 10 is `server_room` exactly.** The room's bounds are story 1,
  x -2..19, y 2..14. The island spans x -1.4..18.4, y 2.6..13.3.
- **Every opening into it is a breach:**

  | wall | opening | at | connects to |
  |---|---|---|---|
  | west, `int_1_2` | breach | (-2, 10) | `upper_hall` |
  | south, `int_1_3` | breach | (10.5, 2) | `apartment_hideout` |
  | north, `ext_1_N` | `roofline_breach` | (13, 14) | outside |
  | east | (exterior wall, no opening) | | |

- **Story 1's two doors connect the other rooms:** `apartment_hall` at
  (-9.5, 2) joins `upper_hall` and `manager_office`, and
  `hall_to_manager_office` at (-2, 0) joins `manager_office` and
  `apartment_hideout`.
- **The seams between island 10 and island 9 are all 1.30 m,** along x = -2
  and y = 2: the walls.

So the navmesh agrees with the spec. This is a breach-only room by
construction. Whether 186 m² with no door is the intent is a design call,
not a measurement.

## Instruments

- `navmesh_islands.py`: the largest islands other than the largest; area,
  height range, extent, and what footprint each lies over. Its docstring
  says "other than the spawn's". The code skips the LARGEST island. Here
  that is the same island (the home point is in island 0, the largest), so
  the listing holds for this bake and would not for one where it is not.
- `door_islands.py`: the island on each side of each exterior door or
  breach, at set distances along the wall's outward normal. Rot 0 only;
  refuses anything else.
- `island_seams.py`: the closest approaches between two islands in a
  height band, in both frames, beside every door-like opening's distance.

## Not established

- **The cause of break 1.** The two reads above decide it.
- **Whether DC's own gate sees break 1.** Deli Counter's nav gate and
  `stair_regression.py` ("all occupied stories reachable") bake the shell
  alone. If they say story 1 is reachable and this bake says it is not, two
  instruments disagree and one of them is wrong.
- **Whether break 1 predates Deli Counter 0.192.0.** That release moved
  deli_a01's counter islands off its stair hole and refurnished its upper
  hall. 9187's workspace is still on disk, so its seed_9104 scene can be
  baked the same way.
- **Whether the themed export carries the same break.**
