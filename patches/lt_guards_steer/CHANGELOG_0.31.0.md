## [0.31.0] - the guards walk as the crew does: they keep to the mesh and step up

### Why now

Factory roadmap 242. 0.30.0 stopped NPC Pathing charging the map for the guards' own crowding. Of the 23
EnemyStuck events it still counted over the factory's sixteen lots, the factory placed 21 at two spots
(`docs/findings/stoop_breadth/enemy_stop_trace.py --lot --contacts --raw`):

- warehouse_yard_001 seed_9206, its 13 and its WARN 73: a guard 5 cm off the mesh against the end of a
  building's wall, a guard ahead of it, and its next path point round that wall's end;
- crossroads_9600 seed_9600, its 8: a guard whose capsule rests on a stair ramp's open side edge 0.18 m up,
  its path crossing that edge onto the ramp -- a rise the contract leaves to the consumer's step-up.

The crew bot stopped meeting both long ago: it steps up as the contract's player does (0.24.0) and keeps
to the mesh it plans on (0.29.0). `LT_EnemyMovement` did neither, though `agent_contract.json` says
npc_standard shares the player's metrics until a distinct class ships.

### What changed

- **`LT_Steering`** (new, `scripts/core/`): the crew bot's `_velocity_on_mesh` and `_try_step_up`, moved
  as static functions with their constants, and the body's radius beside them. One copy, so a lesson
  either body learns is both bodies'.
- **`LT_BotPlayerController`** calls them; its walk is the same.
- **`LT_EnemyMovement`** keeps each step on the mesh it plans on (`keep_to_mesh`, on), and after its slide
  steps up as the crew does (`max_step_up`, 0.5; `steps_taken` counts the steps).
- **`LT_MapEvalHarness._apply_body`** gives a guard the scenario's `player_max_step_up_m`, as it gives the
  crew.
- 0.30.0's comment on `blocked_detected` said 73 of 75 events; the factory's census had 74 of 75 with
  another body among their contacts. Corrected.

### Tests

`runners/tests/test_guards_walk_as_the_crew.gd`, the real enemy pill with its brain taken out, 8 checks: [1] round a counter's corner on a navmesh baked at the contract's numbers, the guard's axis 0.388 m from the box at its nearest, within 2 cm of the mesh's 0.4 m clearance; [2] the control, the box 5 m aside, the guard arrives; [3] round the corner it still arrives; [4] a 37.9 degree ramp met from its open side: one step taken, across to z 1.67, and standing on it, feet at y 0.288 where a capsule resting there stands at 0.287; [5] the control, a 0.08 m step walked with no step taken; [6] a 0.6 m box neither climbed nor stepped onto; [7] the harness gives a guard the scenario's step. PASS on 0.31.0. On an export of 0.30.0 it runs to its end and fails four -- the axis 0.359 m from the box, the guard held at the ramp's side at y 0.001 (two), no step from the harness -- and its controls pass there too.

All 26 tests in `runners/tests` and `runners` exit 0 in the repository on 0.31.0, headless under Godot 4.7, among them the crew's `test_step_up_is_the_contracts.gd` and `test_bot_keeps_to_the_mesh.gd` on the moved code

### Measured

Over the factory's 16 lots (its `docs/findings/route_snag/guard_steer_breadth.py`): each lot under Godot Physics with today's command, graded three ways -- by 0.30.0 (this repository's af09e20), by 0.31.0, and by 0.31.0 with the guards' new steering switched off in the copy (`keep_to_mesh` false and a step of 0). THE CONTROL: switched off, 0.31.0 reads 0.30.0 exactly -- every summary field, the grade and the score -- on all 16. So moving the crew's steering into `LT_Steering` changed nothing the crew does, and every difference below is the guards' steering. Enemy stuck 23 -> 14, blocked 159 -> 143:

    lot                            0.30.0                  0.31.0                  enemy stuck, blocked
    crossroads_9600 seed_9600      PASS_WITH_TUNING 89     PASS 90                  8 -> 0, 5 -> 3
    warehouse_yard_001 seed_9206   WARN 73                 PASS_WITH_TUNING 83     13 -> 14, 38 -> 36
    warehouse_yard_001 seed_9004   PASS_WITH_TUNING 89     PASS 90                  0 -> 0, 0 -> 0
    gas_block_001 seed_9181        PASS_WITH_TUNING 88     PASS_WITH_TUNING 87      0 -> 0, 13 -> 11
    deli_001 seed_9191             PASS_WITH_TUNING 80     PASS_WITH_TUNING 80      1 -> 0, 29 -> 29
    club_block_014 seed_9282       PASS 90                 PASS 90                  1 -> 0, 0 -> 1

The other ten read their grades as before. The guards move, so the fights move: on every lot some shot and survival fields moved. crossroads_9600 seed_9600's 8, at a stair ramp's open side, are gone. warehouse_yard_001 seed_9206's are not: its 14 stand where its 13 stood, a guard 5 cm off the mesh at a wall's end. Five of them touch nothing but that wall and the floor, their velocity after the slide pointing away from the wall, and they do not move (no slide travelled 0.1 mm) -- a body the physics holds there. That lot's +10 is OVEREXPOSED's line: the crew's mean survival 5.77 -> 7.34 s, one run's crew lasting 46.7 s where none had lasted 7.5. warehouse_yard_001 seed_9004's +1 is a team wipe gone (route 0.96 -> 1.00). gas_block_001 seed_9181's -1 is its route, 0.88 -> 0.80, with one team wipe more and two crew-stuck events where there were none; the one traced (`pin_trace.py`, run 12) is a crew member turning back and forth at its path's last point, its route point 0.58 m past it
