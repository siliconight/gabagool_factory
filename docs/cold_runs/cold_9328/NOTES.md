# Cold run 9328 -- precinct_yard_001 on Level Factory 0.218.2 and Deli Counter 0.231.1 (2026-10-19): the breadth sweep

Staged from 9316. The first of the breadth sweep of 2026-10-19; `docs/findings/breadth_sweep_2026-10-19/README.md` holds the sweep's table and both of its
stops.

**Run:** 0 interventions, DONE, drive 8.0 min. The pick is seed 9203, PASS 100, with nothing stuck. Findings 77 / 108.
The light bake has 3,002 users.

**The drop-edge gate** passed. It reached 78,543 of 93,843 standable cells and counted 5 unguarded edges: 3 on things'
tops and 2 outdoors, none undeclared.

**Under Level Factory 0.219.0's lattice** the same package passes with 13 (the sweep's A/B, `gate_ab/`). The 8 new
rows are two flight sides and six edges off a guard's top. On the lattice a capsule stood exactly its radius from a
face, which Godot calls an overlap, and that hid them (`edge_cells_9328.out.txt`).

**Turned buildings:** 21 of the 25, every one a half turn, so the transform fix had nothing to read differently.
