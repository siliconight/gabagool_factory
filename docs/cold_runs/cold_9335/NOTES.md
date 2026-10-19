# Cold run 9335 -- restaurant_row_001 on Level Factory 0.219.0 (2026-10-19): the seam, proven

Staged from 9333, which stopped at the export on three undeclared drops that were the drop-edge instrument's own.
The tool change between them is Level Factory 0.219.0 (c80a7ec, `patches/patch_lf_edge_seam.py`): the instrument
lays its lattice 3.1 mm and 2.3 mm off the round coordinates. `docs/findings/breadth_sweep_2026-10-19/README.md`
holds the attribution.

**Run:** 0 interventions (journal 0, unattributed files 0), DONE, drive 7.8 min. The pick is seed 9003 again, PASS
90 with nothing stuck, as every candidate graded on 9311. Findings 81 / 110 and bake users 3,503, as on 9333.

**The drop-edge gate** passed. It reached 55,492 of 63,957 standable cells and counted 52 unguarded edges: 20 at
declared drops, 13 at ladders' shafts, 11 on flights' own sides and 8 outdoors. None was undeclared. The report
records its lattice offset, 0.0031 and 0.0023 m.

**The A/B predicted it.** The same gate, run with this instrument on a copy of 9333's package, read every count
here and the same 52 rows, none on either side alone (`gate_ab/LF_restaurant_row_001_lattice_rows.json` against
this run's `drop_edges.json`).
