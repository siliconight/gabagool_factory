## [0.30.0] - a guard held by another bot is blocked, not stuck

### Why now

Factory roadmap 242. `LT_EnemyMovement._update_stuck` closes a 3 s window and records `EnemyStuck` when a
guard that is trying to move has moved less than 0.5 m, whatever holds it. NPC Pathing then charges the map
`round(20 x stuck per enemy per run)` of its 20 points, past 0.25 events a run.

The factory traced every stuck event on four lots, each event's own frame of slide collisions
(`docs/findings/stoop_breadth/enemy_stop_trace.py`, its control two identical runs):

- warehouse_yard_001 seed_9206, WARN 68: all 51 were a guard pressed against another guard;
- bank_block_001 seed_9256, WARN 72: 22 of 23 against another guard, and one against a crew member;
- club_block_014 seed_9282: its one was against the level.

In SEEK every guard re-sets its destination to the same crew member every frame, and none steers round
another, so guards queue single file through the same corners. On restaurant_row_001 seed_9104, three
EnemyStuck events were a guard behind a guard behind a guard. The map was charged for the bots' own
crowding.

### What changed

- **`LT_EnemyMovement._update_stuck`** asks, as the window closes on a held guard, what this frame's move met
  (`_held_by_a_body`):
  - a contact under the feet is the floor and is skipped;
  - if every other contact is another bot's body (a CharacterBody3D), the guard is BLOCKED:
    `blocked_detected`;
  - any contact of the level -- a wall, a prop -- and it is stuck, `stuck_detected`, as before.
- **`LT_EnemyBrain._on_blocked`** handles a blocked guard as a stuck one: the same state, the same jitter,
  the same random draws. So every fight plays as it did. It records `EnemyBlocked`, not `EnemyStuck`.
- **`LT_MetricsCollector`** counts `EnemyBlocked` in `enemy_blocked_events` and sums it into the summary.
  The score does not read it.

### Tests

`runners/tests/test_a_queue_is_not_stuck.gd`, real physics with the engine stepping, 10 checks: [1] nothing in a guard's way, the control that it moves (14.60 m), neither stuck nor blocked; [2] a wall 0.45 m off, held at 0.099 m, stuck once and not blocked, as before; [3] another bot's body, held at 0.199 m, blocked once and not stuck; [4] the collector counts `EnemyBlocked` in `enemy_blocked_events` and `EnemyStuck` as before. PASS on 0.30.0; on an export of 0.29.0 it runs to its end and fails three -- the guard behind a bot is counted stuck, never blocked, and nothing counts `EnemyBlocked` -- the two controls passing there too.

All 25 tests in `runners/tests` and `runners` exit 0 in the repository on 0.30.0, headless under Godot 4.7

### Measured

Over the factory's 16 lots in seven mission families (its `docs/findings/route_snag/blocked_breadth.py`: each lot under Godot Physics with today's command, once with 0.29.0 exported from this repository's HEAD and once with 0.30.0). THE CONTROL: the two read identically in every summary field but the ones the change is about -- enemy stuck, its per-enemy rate, blocked, and the grade and score they feed -- on all 16, so every fight plays as it did. Enemy stuck 182 -> 23, and 159 now `enemy_blocked_events`:

    lot                            0.29.0                  0.30.0                  stuck -> stuck, blocked
    deli_001 seed_9191             PASS_WITH_TUNING 76     PASS_WITH_TUNING 80     30 -> 1, 29
    deli_001 seed_9393             WARN 74                 PASS_WITH_TUNING 80     45 -> 0, 45
    warehouse_yard_001 seed_9206   WARN 68                 WARN 73                 51 -> 13, 38
    bank_block_001 seed_9256       WARN 72                 PASS_WITH_TUNING 75     23 -> 0, 23
    gas_block_001 seed_9181        PASS_WITH_TUNING 86     PASS_WITH_TUNING 88     13 -> 0, 13
    crossroads_9600 seed_9600      PASS_WITH_TUNING 88     PASS_WITH_TUNING 89     13 -> 8, 5
    crossroads_9600 seed_9701      PASS 100                PASS 100                 6 -> 0, 6
    club_block_014 seed_9282       PASS 90                 PASS 90                  1 -> 1, 0

and the other eight read 0 stuck under both, their grades unchanged. Two WARN lots become PASS_WITH_TUNING. The 23 left are guards held by the level -- a wall in the closing frame's contacts, with or without a body -- and NPC Pathing still charges them: warehouse_yard_001 seed_9206 keeps 13 and its WARN, crossroads_9600 seed_9600 8
