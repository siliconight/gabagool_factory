# Cold run 9246 -- roadmap 197 re-measured: the generated deli's enemies still jam, elsewhere

**What it tested:** nothing new shipped; it re-measures roadmap 197 on
today's tools. 9191's brief `deli_001` (one building, so no lot library:
the deli is GENERATED from Deli Counter's `corner_deli` recipe) with 9191's
own seeds, on Deli Counter 0.209.1, Lot 0.116.0, Level Factory 0.179.0, Laser
Tag 0.25.0 -- where 9191 ran Deli Counter 0.201.0 and older everything.

**Result: 0 interventions, 0 tool files changed.** Every leg ran; the package
exported and baked (1,600 lightmap users). Findings 74 at the shell, 99
after the art leg.

## The shell leg: no candidate is out

9191: all three candidates out on Laser Tag's `LT_MAP_ENEMY_PATHING_BROKEN`,
the driver taking the fewest majors. 9246, the same seeds:

    candidate   majors  route completion   enemy-stuck events (9191's)
    seed_9191   2       1.00               49   (177)
    seed_9292   2       1.00                0   (192)
    seed_9393   2       0.96               19   (--)

## Where the 49 stand -- not at the rear door

The building stands at site (6, 0), unturned (`site.site.drawn.json`), so a
Godot position (x, z) is building (x - 6, -z) in spec axes.

- **42 of seed_9191's 49** sit in two cells at Godot (-12, -3.5): building
  (-18, +3.5), just inside the west wall, 0.8 m south of `alley_entry`
  (1.4 m, y 4.3 to 5.7). A 1.2 m `shelf_run` stands along that wall's inside
  from y 1.9 to 3.1, 0.5 deep, ending 1.2 m short of the door's jamb; the
  stuck bodies stand at its end. A partition (`int_0_1_seg0`) meets the
  exterior wall 0.3 m past the door's other jamb, at y 6.0.
- **The other 7** (and 9 of seed_9393's 19) sit at Godot (-2.5, -15):
  building (-8.5, +15), 1 m outside the north wall in the `loading_bay`
  (3.2 m, x -11.1 to -7.9). The interior partition `int_0_0_seg13/14` meets
  the north wall at x -8.0 -- 0.1 m INSIDE the bay's opening: the roadmap
  189 neck "a door running past the end of its wall", seen from the other
  side.
- **None at `rear_staff_entry`**, the 1.1 m door that held 165 of 9191's
  177. Its width is under the contract's `min_door_width_m` 1.25 (as are the
  recipe's 1.2 m front door and 1.1 m counter door, all flagged by Deli
  Counter's `navigability` as a warning nothing reads), but it is not where
  today's enemies stop.

## The instrument (Laser Tag 0.25.0's enemy)

Reading the harness for why an enemy jams where the crew does not:
`_configure_enemy` never applies `_apply_body`, so every enemy keeps
`LT_EnemyPill.tscn`'s capsule of radius 0.40 -- the bake's agent radius,
which the contract says is not a body radius -- and the scene's
`path_desired_distance` 0.8, which Laser Tag 0.18.0 measured cutting
corners and jamming the crew (and replaced for the crew only). A navmesh
eroded by 0.40 leaves a 0.40 body nothing at a corner, and a waypoint
counted reached 0.8 m early turns it into one.

## The enemy rebuilt, on this run's own evaluation (`docs/findings/grader_speed/`)

seed_9191's staged evaluation project, copied three times, the job's exact
command (`--runs 25 --seed 9191`), A and A2 as shipped and B with Laser Tag
0.26.0's five files drafted in (`patches/patch_lt_enemy_body.py`, code only):

    run   grade              score  enemy stuck  route  enemy deaths  player deaths  first contact
    job   WARN               68     49           25/25  150           34             2.67 s
    A     WARN               68     49           25/25  150           34             2.67 s
    B     PASS_WITH_TUNING   76     28           25/25  150           33             3.13 s
    A2    WARN               68     49           25/25  150           34             2.67 s

**The job, A and A2 are identical in every field, all 1,943 events**: Laser
Tag's evaluation is deterministic across processes and machine load, so B's
difference is the enemy's body and steering and nothing else.
`INSTANT_CONTACT` WARN became `CONTACT_TIMING` PASS.

**What the 28 left are.** Placed by their own positions (two decimals, not
the cells):
- A's 42 at the west wall stood at building (-18.0, 3.5) and (-17.75, 2.75),
  B's 25 at x -17.6..-17.25, y 0.4..1.9: along the inside of the west wall,
  where a kitchen grill (0.9 m deep) and the 1.2 m shelf run (0.5 deep)
  alternate with 1.35 and 1.2 m gaps before the alley door.
- **None touches static geometry**: A's bodies stand 0.5 m off the shelf's
  corner and 0.8 m off the wall, B's over a metre off the grill's. Each
  quarter-metre cell holds events from five or six different enemies.
- The crew spawns outside the alley side (building -23, 7.5), enters by the
  alley door and walks that wall to the objective (-12, -8.25); the six
  enemies spawn in a row 1 m behind the north wall and chase them in. So the
  remainder is enemies queued on the crew's route among the pieces and each
  other (enemies collide with enemies, mask 7), or holding on targets they
  cannot reach. Which, a trace of each enemy's destination at the moment it
  stalls would say; nothing here does yet.

## What is evidence of what

- 0 interventions, the bake, the findings, the stuck counts and positions:
  this run.
- Where the clusters stand against the shell: the building's placement
  from Lot's drawn spec and the pieces from the shell's own
  `shell.slots.json` (seed_9191), not a render.
- 9191's figures: its NOTES, on older tools; compared as counts, not as a
  change in one variable.
