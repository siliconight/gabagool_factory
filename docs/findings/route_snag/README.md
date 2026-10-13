# Roadmap 242's snag: a body pinned at a counter's corner by the physics engine

Laser Tag's route on restaurant_row_001's picked lot (seed_9104) swung with every change to the
street furniture: route completion 1.00, 0.64, 0.72 and player-stuck events 9, 29, 72 across cold
runs 9261 (steel lamps), 9262 (the pole line) and 9263 (0.118.1's corner pole), where nothing but the
furniture changed. Roadmap 242 filed it with two suspected snags, "a kerb face at (-66, -5)" and "a
meter between two parked cars at (35, -17)".

## What the snag is

**Not a kerb face (REFUTED, KEPT).** 64 of 9263's 72 stuck events stand at ONE point, identical to
fifteen digits in every run -- Godot (-66.35009, 0.00094, 4.94045), plan (-66.35, -4.94) -- and that
point is INSIDE the deli (b0, the objective; footprint 38 x 28 m at (-51, 2.51)) on its ground
floor: one body radius (0.35 m) west of the front register counter's west end, level with its south
face (`deli_counter/build/deli_a01.slots.json`: `front_register_counter`, 6.0 x 0.9 x 1.1 m at local
(-12.0, -7.0)). 242's "kerb face" was a guess the item itself filed under "what to measure first";
the cold-run notes of 9262 and 9263 repeated it.

**What the bot does there** (`snag_trace.py`, `snag_trace.out.txt`; the job's own command on a copy of
its staged project, one run, the copy's harness and bot controller instrumented; its control: the
copy reproduces the job's first stuck event, t 72.0 at the same float, and the job's 7 events in that
run). LT_Player_04 has reached the basement objective (route point 2 of 3) and is heading back to the
van. Its next path point is 0.48 m south-south-east; it sets full speed (4.0 m/s) toward it; and
`move_and_slide()` returns six slide collisions every frame, ALL with the deli's floor slab
(`b0/slab_col_0`), normal straight up, travel shrinking to 0, the horizontal remainder unchanged. A
horizontal motion slid along an upward normal is the same motion, so the body spends its six slides
on the floor it stands on and goes nowhere, for good.

    tick 986  before (-66.35094, 0.000902, 4.938468)  vel (1.58, 0, 3.67)  -> moved 2 mm, slides 6
    tick 987  before (-66.35009, 0.000944, 4.940451)  vel (1.58, 0, 3.67)  -> moved 0,    slides 6

**Three arms, each a change at the pinned moment** (the same script, `--swap`, `--counter`,
`--jolt`):

    the floor slab's trimesh swapped for a box with the same top      still pinned  (REFUTED: not the trimesh)
    the register counter's collision disabled                         walks off the next tick at full speed;
                                                                      run 1: 0 stuck events (job: 7)
    the whole run under Jolt Physics (Godot 4.7's other 3D engine)    reaches the same corner at tick 1023,
                                                                      slides along the counter ("wall", 1
                                                                      slide) and walks on; run 1: 0 stuck

Two things put it there. **The bot cuts corners**: it turns toward the next path point once within its
arrival radius, about 0.44 m (`LT_Const.arrival_radius`: body radius, a tick's travel at the 4x step,
half a cell), where the navmesh's 0.4 m erosion leaves the 0.35 m body 5 cm of clearance -- so its move
clips the counter's corner, here by about 3 cm. **And Godot Physics pins it**: touching the corner and
the floor at once, `move_and_slide` takes the floor as each slide's first collision and never turns
along the counter. Lifted 2 mm off the floor, the same motion tests free (`snag_trace.out.txt`).

## Is the swing the pin? (`engine_ab.py`, `engine_ab.out.txt`)

The three lots, each through the job's full command (25 runs from seed 9104, the fixed clock), under the
engine the staged project runs -- it names none, so Godot Physics -- and under Jolt, nothing else
changed. Every Godot Physics arm reproduced its job in every field read.

    lot    engine   grade              score  route  player stuck (at the counter)  enemy stuck  deaths
    9261   Godot    PASS_WITH_TUNING   80     1.00    9 ( 6)                        3            29
    9261   Jolt     PASS_WITH_TUNING   80     1.00    1 ( 0)                        4            26
    9262   Godot    PASS_WITH_TUNING   76     0.64   29 (18)                        0            34
    9262   Jolt     PASS_WITH_TUNING   77     0.76    7 ( 0)                        0            38
    9263   Godot    PASS_WITH_TUNING   78     0.72   72 (64)                        0            26
    9263   Jolt     PASS_WITH_TUNING   79     0.84    7 ( 0)                        0            29

Under Jolt the counter pin is gone in all three and the stuck counts fall from 9, 29, 72 to 1, 7, 7.
The route still reads 1.00, 0.76, 0.84: what is left tracks the fights (deaths 26, 38, 29), not pins.
So most of 242's swing was the engine pinning a body on a corner the furniture's navmesh happened to
send it past -- not the furniture, and not the lot's geometry.

## Across mission families: the engine is not the fix (`engine_breadth.py`, `engine_breadth.out.txt`)

**RETRACTED, KEPT: "choose Jolt".** On restaurant_row_001 alone (above) Jolt looked like the cure, and
the recommendation given the walker the same afternoon was to standardise on it. The other families'
staged lots say otherwise. Sixteen lots of seven families -- restaurant_row_001 (3), deli_001 (3),
warehouse_yard_001 (3), bank_block_001, club_block_014, gas_block_001 (2), crossroads_9600 (3) -- each
copied with TODAY's Laser Tag dropped in (their jobs ran before the fixed clock and cannot be
reproduced), run under Godot Physics twice and Jolt once, 25 runs each from the job's own seed. Every
lot's two Godot Physics passes read identically (the control: 16 of 16).

                                     Godot Physics   Jolt
    all 16 lots       player stuck        108          60
                      pinned               74          25    (in 3 lots / in 5 lots)
    without the       player stuck         36          53
    counter's lot     pinned                8          23    (in 2 lots / in 4 lots)
                      enemy stuck         178         143
                      score, summed      1198        1172

66 of Godot Physics' 74 pinned events are the one counter in restaurant_row_001 seed_9104. Elsewhere
Jolt pins MORE: club_block_014 seed_9282 0 -> 5 at 2 places, crossroads_9600 seed_9701 0 -> 8 at one,
warehouse_yard_001 seed_9206 0 -> 4 at 2 places; and grades move both ways (gas_block_001 seed_9181
PASS_WITH_TUNING 75 -> WARN 65, warehouse_yard_001 seed_9206 68 -> 62). Each engine pins bodies at
different corners; neither is the fix. What both share is the bot cutting corners into geometry --
its 0.44 m arrival radius against 5 cm of clearance -- which is Laser Tag's, and the fix belongs there
whichever engine the game ships.

## What is not decided, and whose it is

**Which physics engine the game ships is the game's question**, and the walker does not know yet
(2026-10-12: "we are going to use Godot"). `engine_probe.gd` read it off Godot 4.7 itself: a project
that names no engine runs Godot Physics (`modules/godot_physics_3d/`), one naming "Jolt Physics" runs
Jolt (`modules/jolt_physics/`), both in the stock binary. Nothing above favours either for the factory's
sake; the grader should run whatever the game ships, and until that is chosen the default stands. Not
measured: a human-driven body, the enemies' own pins, and the second place 242 named (beside a meter
at (35, -17): 8 of 9263's 72 events, the same mechanism unproven).

## Laser Tag 0.28.0, drafted and HELD: the bot keeps to the mesh (`engine_breadth_028.out.txt`)

The fix the section above points at, drafted as `patches/patch_lt_keep_on_mesh.py`: `_advance_route`
reads its `delta`, and `_velocity_on_mesh` turns a step that would leave the navigation mesh by more than
`MESH_TOLERANCE_M` (0.01 m) back toward the mesh's closest point, at the same speed, on the same level
(`MESH_LEVEL_M` 0.5 m). Its own test (`lt_keep_on_mesh/test_bot_keeps_to_the_mesh.gd.txt`) passes on the
draft. Measured as above -- the same 16 lots and three runs a lot, the draft's addon dropped into each
copy (`LT_ADDON=_scratch/lt_draft/addons/laser_tag_tool python docs/findings/route_snag/engine_breadth.py`),
the two Godot Physics passes identical on all 16:

                      0.27.0 Godot   0.28.0 Godot   0.27.0 Jolt   0.28.0 Jolt
    player stuck            108             45            60            44
    pinned                   74              9            25            14

Where it helps, it helps a lot: restaurant_row_001 seed_9104 under Godot Physics 72 stuck and 66
pinned -> 7 and 0, route 0.72 -> 0.92; crossroads_9600 seed_9600 pinned 6 -> 2 under both; Jolt's new
pins at club_block_014 seed_9282 (5) and crossroads_9600 seed_9701 (8) gone. **Where it hurts, which is
why it is held:** bank_block_001 seed_9256 pinned 2 -> 7 under Godot Physics and 0 -> 7 under Jolt (its
Jolt route 0.92 -> 0.76); deli_001 seed_9191 under Godot Physics and seed_9393 under both score 10 lower
(76 -> 66, 74 -> 64), each with 0 -> 3 stuck events; gas_block_001 seed_9282 under Jolt 100 -> 90;
warehouse_yard_001 seed_9206 under Jolt pinned 4 -> 5, route 0.84 -> 0.76. Not attributed: where the
bank's seven pins stand, and what the deli's three new stuck events are. The patch refuses to write the
repository until they are; `--draft` on a copy still works.

## The stuck detector counts fights (`pin_trace.py`, `why_breadth.py`)

**The draft's bank "pins" are not pins.** `pin_trace.py census` on bank_block_001 seed_9256 under the
draft: its 7 stuck events are two bodies at one spot, LT_Player_02 at (11.697, 0, -0.918) in runs 6,
10, 11 and 20 and LT_Player_03 0.40 m from it in runs 6, 10 and 11, every one at t 12.0
(`pin_census_bank.out.txt`). `pin_trace.py trace` on run 6, its control held (the copy's first stuck
event the census's, time, body and position): the body's velocity is ZERO, on the floor, touching no
wall, its two teammates within 1.2 m, `_velocity_on_mesh` never reached -- the bot was not asking to
move (`pin_trace_bank.out.txt`). `_physics_process` stops a bot that sees an enemy
(`advance_while_engaging` off, the factory's setting), and `_update_stuck` closes its 4 s window and
records PlayerStuck when the body moved less than 0.5 m and no enemy is in sight AT THAT INSTANT. So
`census --why`: every bot counts, since its window last closed, its frames and those it had an enemy in
sight; THE CONTROL, the instrumented run's stuck events the plain census's, held. All 7 closed windows
with an enemy in sight in 59 or 60 of their 60 frames (`pin_why_bank.out.txt`): bots standing to fight,
counted as their enemy left their sight on the window's last frame. The spot pinned under 0.27.0 too,
3 events, with an enemy in sight 7 of 60 frames: those are not fights. (0.27.0's trace of run 12 FAILED
its control -- run 12 alone put the body 1 cm from where run 12 of the 25-run process did -- and is kept,
unused.)

**Across the draft's regressions, 18 of 21** (`pin_why_regressed.out.txt`, each control held): deli_001
seed_9191's and seed_9393's three each are fights, warehouse_yard_001 seed_9206's five of six under
Jolt, the bank's seven; the three left are real -- two bodies 0.11 m apart 3.4 m up on gas_block_001
seed_9282 under Jolt, no enemy in sight in any frame, and one on warehouse_yard_001 seed_9206.

**Under the shipped grader** (`why_breadth.py`, Laser Tag 0.27.0, the 16 lots as `engine_breadth.py`
ran them, each lot's row the same as `engine_breadth.out.txt`'s in every field -- 32 of 32 controls
held; `why_breadth.out.txt`): of 108 player-stuck events under Godot Physics 23 are fights, of 60 under
Jolt 28. `_score_traversal` takes 10 points for ANY player-stuck event, and 7 of the 32 lot-engine rows
owe the whole of theirs to fights: restaurant_row_001 seed_9003 under both engines (PASS_WITH_TUNING
80), deli_001 seed_9292 under both (80), deli_001 seed_9191 under Jolt (WARN 66), gas_block_001
seed_9181 under both (75, and WARN 65 under Jolt). And each false stuck event skips its bot a route
point, which a route then cannot be walked past (`route_walked`).

**The fix is Laser Tag's** (`patches/patch_lt_fight_not_stuck.py`, Laser Tag 0.28.0): a frame on which
the bot stands to fight restarts the window, so stuck means four seconds with no stand to fight in
which the body moved less than 0.5 m -- the rule `LT_EnemyMovement` already keeps for a guard not trying
to move, narrowed for the crew to a stand to fight so a bot hung on a path point under its feet still
counts. Its test, `test_a_fight_is_not_stuck.gd`, fails on 0.27.0 in 3 of 6 checks and passes on the
draft; the other 21 exit on the draft as on 0.27.0 (20 exit 0; `test_nav_bake_is_the_contract` cannot
run from a copy on either, and runs in the repository). The held keep-on-mesh draft is to be measured
again on top of it: its bank and deli regressions were this detector.

## Laser Tag 0.28.0, measured and shipped (`engine_breadth_fight.out.txt`, cold run 9266)

The fix's own breadth, `engine_breadth.py` with the draft's addon: every lot's two Godot Physics passes
identical (16 of 16). Against 0.27.0's rows: player-stuck 108 -> 92 under Godot Physics and 60 -> 24
under Jolt; pinned 74 -> 78 and 25 -> 14; scores up on 18 of the 32 lot-engine rows, the same on 11,
down on 3. Routes are walked further where false events had skipped route points: restaurant_row_001
seed_9104 under Godot Physics 0.72 -> 1.00, its 74 events all at the deli counter's corner,
(-66.350, 0.001, 4.940/4.941), where 0.27.0 read 72 events, 66 of them there -- the false events had
been skipping its crew past route points.

**RETRACTED, KEPT -- the next paragraph's verdict.** It called the three rows down "real non-progress".
`pin_trace.py trace --wide`, every third tick within 4 m (`pin_wide.out.txt`, each control held), shows
otherwise: on gas_block_001 seed_9282 the body walks east along the upper floor to its route point,
reaches it (route 1 -> 2), turns and walks back west through the same spot; on warehouse_yard_001
seed_9206 the same out and back to its route point; each round trip took about one window, so the
body ended near where the window began, and the detector, which measures net displacement, read a
completed leg as stuck. A second false positive, not non-progress.

**The three rows down are real non-progress 0.27.0 did not count.** gas_block_001 seed_9282 under both
engines (PASS 100 -> 90) and warehouse_yard_001 seed_9206 under Godot Physics (WARN 68 -> 58) gained
stuck events where 0.27.0 had none (`pin_why_fixed.out.txt`, `pin_trace_fixed.out.txt`, each control
held): no enemy in sight in the window, and the body back within 0.006 to 0.46 m of where it began --
traced, it crosses its spot going toward its next path point and, four seconds later, going back. The
detector moves a bot only when it fires, and 0.27.0 fired on neither lot, so up to those events the runs
are 0.27.0's: its crews went back and forth there too, and its fixed four-second grid did not count it.
The gas spot is the one the keep-on-mesh draft's two Jolt bodies stood at, 3.4 m up; the warehouse spot
its one. What drives the back and forth is not measured.

**In a real drive** (cold run 9266, 0 interventions): the generator's three candidates graded as the
breadth graded them -- seed_9003 PASS_WITH_TUNING 80 -> PASS 90 (its PLAYER_STUCK finding gone),
seed_9104 78 -> 80 at route 1.00, seed_9205 PASS 90 -- findings 119 -> 118, the pick seed_9104 still,
on Lot's majors against the other two.

## Laser Tag 0.28.1: a bot that reaches where it was going is not stuck (`engine_breadth_0281.out.txt`)

The round trips above are the detector's second false positive, and the fix is the first one's shape:
`_restart_stuck_window()` is now the one place the window restarts -- on a stand to fight (0.28.0), on
a route point reached and on a cover point reached. An arrival is progress; a jam after it still counts
a window later, and route points are finite and each reached once, so arrivals cannot hold a window
open (`patches/patch_lt_arrival_not_stuck.py`; `test_an_arrival_is_not_stuck.gd`, 8 checks, three
failing on 0.28.0 -- [1], its control, a round trip reaching nothing, still counts).

Its breadth, each lot's two Godot Physics passes identical on all 16: against 0.28.0, scores up on 11 of
the 32 lot-engine rows and down on NONE; player-stuck 92 -> 70 under Godot Physics and 24 -> 3 under
Jolt. What is left is real: 67 events at restaurant_row_001 seed_9104's deli counter, the one pin, and
three on crossroads_9600 seed_9600 under each engine. The three rows 0.28.0 lowered are back (gas_block_001
seed_9282 PASS 100 under both engines, warehouse_yard_001 seed_9206 WARN 68). Against this morning's
0.27.0: up on 22 rows, the same on 10, down on none; player-stuck 108 -> 70 and 60 -> 3.

## The keep-on-mesh draft on 0.28.0 (`engine_breadth_029_on_0280.out.txt`, `pin_mesh_9004.out.txt`)

Rebased onto 0.28.0 as 0.29.0 and measured before 0.28.1 existed: player-stuck 92 -> 17 under Godot
Physics and 24 -> 14 under Jolt, the deli counter's 74 pins gone; scores up on 7 rows and down on 7.
The downs were new "pins" -- events recurring to the millimetre across runs -- on warehouse_yard_001
seed_9004 (4 and 5) and crossroads_9600 seed_9701 (2 and 3), and one in seed_9104's basement under Jolt.
Traced (`pin_trace.py census --why`, `trace --wide`, each control held): seed_9004's seven events are a
body that "moved 0.000 m" -- passing the same spot heading south at 4 m/s toward its route point, and
sixty ticks later heading north from it; seed_9104's basement events the same out and back to the
objective. Round trips again, timed so exactly by the bot's fixed speed that they recur to the
millimetre and read as pins: **the breadth's pinned count cannot tell a deterministic round trip from a
body held by geometry**. 0.28.1 excuses the round trips found here, each to a destination; one that
turns without arriving anywhere (a re-plan, say) it would still count. The draft moves paths a little,
and which round trips line up with a window moves with them.

## Laser Tag 0.29.0: the keep-on-mesh draft on 0.28.1, shipped (`engine_breadth_029.out.txt`)

With both of the detector's false positives gone, the draft measured as what it is. Over the 16 lots,
each lot's two Godot Physics passes identical on all 16: **player-stuck 70 -> 0 under Godot Physics and
3 -> 0 under Jolt, pinned 69 -> 0 and 2 -> 0** -- restaurant_row_001 seed_9104's 67 events at the deli
register counter and crossroads_9600 seed_9600's three under each engine gone. Scores up on 4 of the 32
lot-engine rows (crossroads_9600 seed_9600 77 -> 88 under both engines, its route 0.88 and 0.92 -> 1.00;
restaurant_row_001 seed_9104 PASS_WITH_TUNING 80 -> PASS 90 under Godot Physics), down a point on 3
(deli_001 seed_9191 under Jolt; warehouse_yard_001 seed_9004 under Godot Physics, route 1.00 -> 0.96,
PASS -> PASS_WITH_TUNING; seed_9206 under Jolt, route 0.92 -> 0.88), the same on 25. Keeping to the mesh
moves where crews meet guards, and deaths moved both ways (warehouse_yard_001 seed_9004 28 -> 35 under
Godot Physics). **Not attributed:** the two routes a run shorter.

Across the day, this morning's 0.27.0 against 0.29.0 on the same 32 rows: player-stuck 108 -> 0 under
Godot Physics and 60 -> 0 under Jolt. The engine question this item began with no longer moves the
stuck count -- both engines read zero -- though scores still differ between them on some lots through
the encounter (gas_block_001 seed_9181 86 under Godot Physics against 76 under Jolt).

**In a real drive** (cold run 9267, 0 interventions; 0.28.1 and 0.29.0): restaurant_row_001's three
candidates PASS 90, route 1.00, no stuck event; findings 118 -> 117, the last LT_MAP_PLAYER_STUCK gone.
**The swing this item began with:** cold run 9263's lot -- route 0.72 and 72 stuck events under 0.27.0
-- reads PASS 90, route 1.00, none under 0.29.0 (`pin_9263_029.out.txt`); 9261's and 9262's lots were
retired before they could be read again (`engine_ab.py` builds their names, which the retire step's
protection cannot see -- filed separately).

**The two shorter routes, attributed** (`pin_trace.py census` under 0.29.0, the repository's Laser
Tag, each reproducing the breadth's row: warehouse_yard_001 seed_9004 under Godot Physics PASS_WITH_TUNING
89 at route 0.96, seed_9206 under Jolt WARN 72 at 0.88). Every run that ended short ended in a TEAM
WIPE, all four crew killed early -- seed_9004's run 7 at t 22.4; seed_9206's runs 4, 6 and 8 at 21.3,
16.0 and 15.9 -- with no stuck event and no timeout on either lot. Keeping to the mesh moves where
crews meet guards, and on these two lots one more fight went the guards' way: the encounter, not the
traversal.

## Laser Tag 0.30.0: a guard held by another bot is blocked, not stuck (`blocked_breadth.py`, `blocked_breadth.out.txt`)

The enemies' stuck count had the blind spot 0.28.0 and 0.28.1 took out of the crew's.
`LT_EnemyMovement._update_stuck` closes a 3 s window and records EnemyStuck when a guard trying to move
has moved under 0.5 m, whatever holds it. Traced on four lots, each event's own frame of slide
collisions (`docs/findings/stoop_breadth/enemy_stop_trace.py --lot`), 74 of 75 events had another body
among that frame's contacts, 73 another guard and one a crew member: in SEEK every guard re-sets its destination to the same crew member every
frame and none steers round another, so they queue through the same corners.

0.30.0 asks, as the window closes on a held guard, what this frame's move met
(`LT_EnemyMovement._held_by_a_body`): a contact under the feet -- its normal within `floor_max_angle`
of up -- is skipped; if every other contact is a CharacterBody3D, a guard or a crew member, the guard is
BLOCKED and records EnemyBlocked; any other contact and it is stuck, as before. A blocked guard is
handled as a stuck one -- the same state, jitter and random draws -- so the fights play as they did, and
the score does not read the new count (`enemy_blocked_events`).

`blocked_breadth.py` grades `engine_breadth.py`'s 16 lots twice under Godot Physics with today's
command, 25 runs from each job's seed: 0.29.0 exported from the repository's HEAD, and 0.30.0. **The
controls:** every summary field but the ones the change is about reads identically on all 16, and on
every lot 0.30.0's stuck and blocked add up to 0.29.0's stuck -- the same events, split.

    lot                            0.29.0                  0.30.0                  stuck -> stuck, blocked
    deli_001 seed_9191             PASS_WITH_TUNING 76     PASS_WITH_TUNING 80     30 -> 1, 29
    deli_001 seed_9393             WARN 74                 PASS_WITH_TUNING 80     45 -> 0, 45
    warehouse_yard_001 seed_9206   WARN 68                 WARN 73                 51 -> 13, 38
    bank_block_001 seed_9256       WARN 72                 PASS_WITH_TUNING 75     23 -> 0, 23
    gas_block_001 seed_9181        PASS_WITH_TUNING 86     PASS_WITH_TUNING 88     13 -> 0, 13
    crossroads_9600 seed_9600      PASS_WITH_TUNING 88     PASS_WITH_TUNING 89     13 -> 8, 5
    crossroads_9600 seed_9701      PASS 100                PASS 100                 6 -> 0, 6
    club_block_014 seed_9282       PASS 90                 PASS 90                  1 -> 1, 0

The other eight read 0 under both, their grades unchanged. **Enemy stuck 182 -> 23, 159 blocked;** six
scores up, none down; two WARN lots become PASS_WITH_TUNING. Each score moves by exactly what
`LT_ScoreCalculator._score_pathing` charges for the events taken out: past 0.25 events a run, round(20
x stuck per enemy per run) -- seed_9206's 51 cost 7 points and its 13 cost 2, so 68 -> 73, not the 75
the four-lot arithmetic gave for all 51; crossroads_9600 seed_9701's 6 were under the 0.25 line and
cost nothing.

**The 23 left are not attributed.** Each has a contact in its closing frame that is neither the floor
nor a body. The four-lot trace classed all 51 of warehouse_yard_001 seed_9206's events "teammate"
because it asked whether ANY contact was another guard; 0.30.0 still counts 13 of them, so those 13 had
another guard and a part of the level in the same frame. Whether the level holds those guards or a
queue presses them against it is the next instrument's question, and that lot stays WARN at 73.
Laser Tag 0.30.0's changelog calls the 23 "held by the level -- a wall": that is the rule's reading,
not a measurement -- no contact was named.

**In a real drive** (cold run 9275, 0 interventions, `docs/cold_runs/cold_9275/NOTES.md`): restaurant_row_001's
three candidates PASS 90 as in 9274, seed_9104 picked, findings 117 -> 117. seed_9104's three EnemyStuck --
the guards queued behind guards that `enemy_stop_trace.py` traced -- are 9275's three EnemyBlocked, the same
runs, times, guards and positions; every other summary field and every other event (1,331, 2,181 and 1,554
on the three candidates) read the same.
