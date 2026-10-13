## [0.28.0] - a bot standing to fight is not stuck

### Why now

Factory roadmap 242. `_update_stuck` closes a 4 s window and records `PlayerStuck` when the body moved
less than 0.5 m and no enemy is in sight AT THAT INSTANT; `_score_traversal` takes 10 points for any
player-stuck event at all, and the bot skips a route point, so a route that ends on the skip is not
walked. A crew bot standing to fight (`advance_while_engaging` off, the factory's setting: it stops)
that lost sight of its enemy as the window closed was counted. The factory found it tracing a draft of
this repository that "regressed" five lots (`docs/findings/route_snag/pin_trace.py`, `census --why`,
each instrumented run's stuck events the plain run's): 18 of the 21 stuck events it added were such
windows, an enemy in sight in 59 or 60 of their 60 frames -- bank_block_001 seed_9256's seven "pins",
both deli_001 lots' three each (76 -> 66 and 74 -> 64), five of warehouse_yard_001 seed_9206's six.

### What changed

- **`_update_stuck(delta, standing_to_fight)`**: a frame on which the bot stands to fight restarts the
  window -- the timer to zero, the anchor where the body stands. Stuck now means four seconds with no
  stand to fight in which the body moved less than `stuck_distance_threshold`. The question asked as
  the window closes (`_find_visible_enemy() == null`) stays. `LT_EnemyMovement._update_stuck` already
  restarts a guard's window whenever it is not trying to move; the crew's restarts on a stand to fight
  only, so a bot hung on a path point under its own feet -- not trying to move either -- is still
  counted.
- **`_physics_process`** passes `enemy != null and not advance_while_engaging`: a bot advancing while
  engaging is trying to move, so its window runs on through a fight as before.

### Tests

`runners/tests/test_a_fight_is_not_stuck.gd` drives `_physics_process` at 0.25 s a frame with a bot
that cannot move and a fake enemy: [1] the control, no enemy, stuck on frame 16; [2] an enemy in sight
on frames 1-15 and gone on 16, no stuck event; [3] one on frame 31, sixteen frames after the fight;
[4] advancing while engaging, stuck on frame 16 as before. 6 checks PASS on 0.28.0; on 0.27.0 three fail -- [2] records a stuck event for the bot that stood to fight, and [3] then finds it counted on frame 16 and none more on 31

All 22 tests exit 0 in the repository on 0.28.0, `test_nav_bake_is_the_contract` among them; on copies of 0.27.0 and 0.28.0 the other 21 exit alike

### Measured

Over the factory's 16 lots in seven mission families (`docs/findings/route_snag/engine_breadth.py` with this addon, today's command, each lot under Godot Physics twice -- the two identical in every field on all 16 -- and under Jolt once): player-stuck 108 -> 92 under Godot Physics and 60 -> 24 under Jolt; scores up on 18 of the 32 lot-engine rows, the same on 11, down on 3; routes walked further where false events had skipped route points -- restaurant_row_001 seed_9104 0.72 -> 1.00 under Godot Physics, its 74 events now all the one real pin at the deli counter. The three down, gas_block_001 seed_9282 under both engines and warehouse_yard_001 seed_9206 under Godot Physics, each gained events where 0.27.0 had none: bodies going back and forth over one spot with no enemy in sight, 0.006 to 0.46 m from where the window began (`pin_trace.py trace`, each control held). The detector moves a bot only when it fires and 0.27.0 fired on neither lot, so up to those events the runs are 0.27.0's: its crews did the same, and its fixed four-second grid did not count them
