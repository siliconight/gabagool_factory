# Cold run 9286 -- roadmap 197's own mission on Deli Counter 0.214.0: the generated deli's doors at 1.25 m

**What it tested:** Deli Counter 0.214.0 (2879716a) on deli_001, 9191's brief and seeds. The level is one
building, GENERATED from Deli Counter's `corner_deli` recipe, and its 1.1 m rear door is where roadmap 197
began. 0.214.0 writes every walkable door a preset makes at the agent contract's `min_door_width_m`. Staged
from cold run 9246, the mission's last, on Lot 0.120.2, Level Factory 0.199.0 and Laser Tag 0.31.0. 9246
ran Deli Counter 0.209.1, Lot 0.116.0, Level Factory 0.179.0 and Laser Tag 0.25.0, so this is not an A/B
of the doors alone.

**Result: 0 interventions (journal 0, unattributed files 0). The deli's doors are the contract's, and no
guard is stuck on any candidate.**

- **The doors**, read off each candidate's `deli_generate` job's `shell.gameplay.json`.
  - In 9246, six were at 1.1 m: `rear_staff_entry` (this item's), `kitchen_to_loading`,
    `customer_to_counter`, `cold_room_door`, `hall_to_manager_office` and `basement_corridor`.
    `front_customer_entry` was 1.2, and `alley_entry` and `apartment_hall` were 1.4.
  - In 9286 those seven are 1.25, and the two 1.4 m doors are unchanged.
- **The grader**, every candidate, against 9246 (Laser Tag 0.25.0 there):

      candidate   9246                            9286
      seed_9191   WARN 68, enemy stuck 49         PASS_WITH_TUNING 80, stuck 0, blocked 29
      seed_9292   PASS_WITH_TUNING 80, stuck 0    PASS 90, stuck 0, blocked 0   PICKED
      seed_9393   WARN 66, stuck 19, crew 6       PASS_WITH_TUNING 80, stuck 0, blocked 39, crew 0

- **The like-for-like, where there is one.** Roadmap 242 graded 9246's own staged seed_9191 -- the
  narrow doors -- under Laser Tag 0.31.0 (`docs/findings/route_snag/README.md`): PASS_WITH_TUNING 80,
  enemy stuck 0, blocked 29. 9286's seed_9191, with the wider doors, reads the same grade, stuck and
  blocked. For the rest, the grader, Lot and Level Factory have all moved since 9246, and nothing here
  separates the doors from them. seed_9292's PASS 90 is not attributed to the doors.
- **Findings 99 -> 94.** The majors are 6 -> 5, seed_9292's `LT_MAP_NO_REACTION_TIME` gone (average
  survival 11.0 s). Every candidate in both runs carries `WALKTEST_ANCHOR_ISOLATED`: anchor `proxy_4`,
  snapped 1.19 m onto the navmesh at (14.1, 3.6, -6.9) on the upper storey, on a cluster of one. It is
  the same in both runs and does not involve a door this release changed (`apartment_hall` is 1.4 m in
  both). It is pre-existing and not attributed here.
- **The bake:** 182 models and 74 primitive meshes lightmapped, 1,632 users (9246: 1,600).

## The time

    run    shell   art     export   walk   retire   the drive
    9286   57 s    76 s    102 s    6 s     4 s     4.1 min (246 s)

## What is evidence of what

- The doors: `jobs/deli_001.deli_generate.candidate.<seed>/out/shell.gameplay.json` in
  `workspaces/cold-9286-ws/.level_factory/`, against `workspaces/cold-9246-ws/`.
- The grader: `jobs/deli_001.laser_tag_evaluate.candidate.<seed>/1/out/lasertag.report.json` in both.
- The findings: `validation/deli_001.json` in both.
- The like-for-like: roadmap 242's `guard_steer_breadth.py` table in `docs/findings/route_snag/README.md`.
- The count: `cold_run.py --end`.
