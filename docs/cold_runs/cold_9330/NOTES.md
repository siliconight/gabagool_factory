# Cold run 9330 -- deli_001 on Level Factory 0.218.2 and Deli Counter 0.231.1 (2026-10-19): the breadth sweep

Staged from 9286. Part of the breadth sweep of 2026-10-19; `docs/findings/breadth_sweep_2026-10-19/README.md` holds the sweep's table and both of its stops.

**Run:** 0 interventions, DONE, drive 4.9 min. The pick is seed 9292, PASS 90, with nothing stuck. Findings 69 / 93.
The light bake has 1,643 users.

**The drop-edge gate** passed. It reached 26,736 of 28,405 standable cells and counted 66 unguarded edges: 28 at
declared drops, 13 at ladders' shafts, 11 on things' tops, 8 outdoors and 6 on flights' own sides. None was
undeclared.

**Under Level Factory 0.219.0's lattice** the same package passes with 64 (the sweep's A/B, `gate_ab/`). Two guard-top
rows go: one a ray grazing the guard's face on the lattice, one a drop of 0.501 against a 0.500 limit
(`edge_cells_9330.out.txt`).
