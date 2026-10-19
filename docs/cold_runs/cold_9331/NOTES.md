# Cold run 9331 -- convenience_001 on Level Factory 0.218.2 and Deli Counter 0.231.1 (2026-10-19): the breadth sweep

Staged from 9280. Part of the breadth sweep of 2026-10-19; `docs/findings/breadth_sweep_2026-10-19/README.md` holds the sweep's table and both of its stops.

**Run:** 0 interventions, DONE, drive 3.7 min. The pick is seed 9282, PASS 100; enemy stuck 3, blocked 24, crew 0.
Findings 54 / 77. The light bake has 565 users.

**The drop-edge gate** passed. It reached 14,702 of 18,095 standable cells and counted no unguarded edge. Under Level
Factory 0.219.0's lattice it reads the same, with no row moved (the sweep's A/B, `gate_ab/`).
