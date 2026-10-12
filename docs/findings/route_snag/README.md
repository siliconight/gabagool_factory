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
