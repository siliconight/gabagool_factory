# Cold run 9334 -- county_hospital_001 on Level Factory 0.218.2 and Deli Counter 0.232.0 (2026-10-19): the shaft fix

Staged from 9329, which stopped on the hospital's elevator shaft. The tool change between them is Deli Counter
0.232.0 (22f71e05): `presets.hospital` declares every hole it stacks, and a declared drop lands on the first floor
below that is not cut under it. Part of the breadth sweep of 2026-10-19; `docs/findings/breadth_sweep_2026-10-19/README.md` holds the sweep's table.

**Run:** 0 interventions, DONE, drive 4.1 min. The pick is seed 9208 again, PASS 100; enemy stuck 1, blocked 22,
crew 0. Findings 62 / 83 and bake users 1,434, as 9329.

**The drop-edge gate** passed. It reached 25,989 of 31,820 standable cells and counted 49 unguarded edges: 40 at
declared drops, 6 on things' tops and 3 on flights' own sides. None was undeclared, where 9329 read 20.

**Under Level Factory 0.219.0's lattice** the same package passes with 49 (the sweep's A/B, `gate_ab/`). One edge's
drop reads a centimetre less.
