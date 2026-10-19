# Cold run 9333 -- restaurant_row_001 on Level Factory 0.218.2 and Deli Counter 0.231.1 (2026-10-19): the breadth sweep

Staged from 9311. Part of the breadth sweep of 2026-10-19; `docs/findings/breadth_sweep_2026-10-19/README.md` holds the sweep's table and both of its stops.

**Run:** 0 interventions, STOPPED at the export on the drop-edge gate: `UNDECLARED_DROP_INDOORS`, 3 unguarded edges,
a 3.3 m drop at the west edge of deli_a03's up-stair discharge plate, site x -64.0. The pick was seed 9003. Findings
81 / 110. The light bake has 3,503 users.

**The stop was the instrument's.** The slab's cut and the plate are authored flush at site x -64.0, a lattice line.
Float32 rounding leaves a 1.7 um gap there, and the ray cast exactly on the line fell through it. Rays a float32 step
either side meet the slab and the plate. It was fixed in Level Factory 0.219.0 (`patches/patch_lf_edge_seam.py`), which lays the
lattice off the round coordinates. Under it this package passes with 52 unguarded and none undeclared.
