## [0.185.0] - Blender jobs run three at a time where the machine allows, the width cold run 9251 measured

**Why now.** Roadmap 239, the art leg. Cold run 9250's job records put
about 102 s of its art leg in Blender jobs run one after another -- 16 kit
builds, 15 dressing builds, the fixtures, the roof props, the clutter --
because `blender` was capped at 1, TDD 19.2's default, never measured.
0.184.0 let a run set the width; cold run 9251 ran with
`LF_CONCURRENCY=blender=3` on 9245's lot and seeds.

**Measured.**

    run    Blender width   Blender window   art leg's jobs   the drive
    9250   1               114.0 s          251.7 s          12.6 min (its legs profiled)
    9249   1                                                 12.1 min
    9251   3                45.7 s          177.1 s          10.8 min

0 interventions, findings 122 -> 122, the package baked and shipped as
before. The models: two runs at one already differ -- 9248, 9249 and 9250
against each other: a mesh's triangles in another order, a merged mesh's
vertices in another order, two trash-bag props' weighted normals drifting
1e-4 to 3e-4, Deli Counter's shell manifest -- so every file the Blender
jobs built in 9251 was compared with 9250's and classed (the factory's
`docs/findings/grader_speed/blender_width_compare.py`): identical, the same
but for that order or a normal within 1e-4, or different. Every file
different at three is different between two runs at one as well, but one:
a trash-bag prop whose normals drifted 0.000108 at most, against 0.000100
between the runs at one and its twin's 0.000203 to 0.000299 -- the same
drift, across the comparison's line.

**What changed.** `BLENDER_PROVEN_WIDTH` 3 and `blender_cap(cpu_count)`:
half the logical CPUs, never below TDD 19.2's 1, never wider than the
proven width; `DEFAULT_CONCURRENCY["blender"]` reads it. A machine with
four logical CPUs runs two. `LF_CONCURRENCY` still overrides it for one
run.

**Not changed, and worth its own work:** the Blender builds are not
reproducible run to run, one at a time or three. A model built twice from
the same inputs can come back in another triangle or vertex order, with
normals a few 1e-4 apart; that is what made this comparison need classes,
and it is what a cache keyed on content cannot see past.

**Tests:** `tests/unit/test_blender_cap.py`, four (three on the measured
machine; never wider than proven; a small machine runs fewer and never
none; the default reads it), all failing on 0.184.0. Two tests had pinned
`blender` at 1 and now say why they do not: `test_godot_cap.py`'s "the
other classes did not move" leaves it out, and
`test_concurrency_override.py` overrides to a width the default is not on
whatever machine runs it. 2,278 passed, 16 skipped, 0 failed (JUnit, 2,294 tests); tests/unit/test_blender_cap.py, four, all failing on 0.184.0
