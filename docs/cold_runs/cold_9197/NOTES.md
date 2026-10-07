# Cold run 9197 -- 0 interventions; the crew leaves the bank's vault

bank_block_001, 9194's brief and seeds. Tests Laser Tag 0.24.0 and Level
Factory 0.154.0 (roadmap 203): the crew bot takes the agent contract's step-up
(`max_step_up_m` 0.5, onto a top it can stand on), so on bank_branch_a04 it
leaves the basement vault past the service stair's open side (0.118 m), where
9194's crew wedged. Tool versions hashed at `--begin`: Laser Tag 0.24.0, Level
Factory 0.154.0, Deli Counter 0.203.0, Lux 0.68.2, Lot 0.97.4, Zoo 1.81.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0; no tool source file
changed). Every leg ran.

## Roadmap 203: the wedge is gone

Laser Tag, 25 runs a candidate -- the same three lots as 9194:

| candidate | b0 | 9194 completion | 9197 completion |
|---|---|---|---|
| seed_9054 | bank_branch_a04 | 0.08 | **0.84** |
| seed_9155 | bank_tower_a01 | 1.00 | 1.00 |
| seed_9256 | bank_branch_a04 | 0.00 | **0.84** |

The figures match the rerun on 9194's staged projects exactly
(`docs/findings/stair_step_up/`). `LT_ROUTE_NEVER_COMPLETED` 1 -> 0.

**The picker read completion** (`tools/cold_drive/pick_candidate.py`): all
three tied at 0 majors, and seed_9155 (1.00) won where 9194's lower-seed tie
had taken seed_9054 (then 0.08).

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 47 findings.
- **Art:** 0 blockers of 67 findings.
- **The bake:** 426 models and 1,516 primitive meshes lightmapped, 7 kept
  dynamic; 73 steady rigs baked, 14 failing left live; 175 room fills;
  3,799 users, 86.7 s in the editor.
- **Findings against 9194, 66 -> 67**, attributed:
  - `LT_ROUTE_NEVER_COMPLETED` 1 -> 0: the step-up.
  - `LOT_PACING_OUTSIDE_TARGET` 0 -> 4: Level Factory 0.153.0's pacing verdict,
    one per Lot run, non-blocking.
  - `LUX_CLUB_REFUSED` 0 -> 1 and `ZOO_FIXTURES_MARKERLESS` 0 -> 1: the picked
    candidate changed, and seed_9155's lot holds `strip_club_a01` (b2). Lux
    baked 42 of 44 club rigs and refused `b2/main_floor_stage` and
    `b2/vip_wing_stage`. The same refusal was in cold run 9167
    (club_block_014) and is filed nowhere -- roadmap 207. The Zoo finding is
    info: 13 of 18 club fixtures are hardware with no emitter marker by
    design.
  - `LOT_DESTINATION_RESOLVED` 3 -> 2: the picked bank is bank_tower_a01, not
    the branch whose objective hook stood on a desk.
  - `DISPATCH_FINDING` 10 -> 7, `LOT_ENEMY_SPAWN_STANDOFF` 3 -> 4,
    `LOT_PATH_END_OFF_DOOR` 5 -> 6, `LOT_SIGHTLINE_UNBREAKABLE` 2 -> 1,
    `LT_MAP_TRAVERSAL` 2 -> 1: a different shipped candidate; not attributed
    further.

**Not checked:** frames, frame time.
