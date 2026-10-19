# Cold run 9332 -- gas_block_001 on Level Factory 0.218.2 and Deli Counter 0.231.1 (2026-10-19): the breadth sweep

Staged from 9309. Part of the breadth sweep of 2026-10-19; `docs/findings/breadth_sweep_2026-10-19/README.md` holds the sweep's table and both of its stops.

**Run:** 0 interventions, DONE, drive 7.9 min. The pick is seed 9080, PASS 100; enemy stuck 1, blocked 3, crew 0.
Findings 70 / 105. The light bake has 3,197 users.

**The drop-edge gate** passed. It reached 53,016 of 70,658 standable cells and counted 16 unguarded edges: 13 on
flights' own sides and 3 outdoors, none undeclared.

**Under Level Factory 0.219.0's lattice** the same package passes with 19 (the sweep's A/B, `gate_ab/`). Three new
rows are a ramp's open west side. At two of them the lattice ray grazed the ramp's face and met the fill under the
stair instead. The third met the ramp on the lattice too, but the flood did not reach it there. Three pairs are the
same edges a centimetre apart once rounded (`edge_cells_9332.out.txt`).
