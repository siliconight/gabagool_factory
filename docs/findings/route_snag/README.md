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

## What is not decided, and whose it is

**Which physics engine the grader runs is the game's question.** A package names no engine; the
game's own project does, and the gameplay layer is outside the factory. If the game ships Jolt, Laser
Tag grading under Godot Physics measures a pin no player meets; if it ships Godot Physics, AI bodies
following navigation (the game's enemies) can pin the same way, and a human pushing a stick into a
corner might. Not measured: a human-driven body, the enemies' own pins, and the second place 242 named
(beside a meter at (35, -17): 8 of 9263's 72 events, the same mechanism unproven).
