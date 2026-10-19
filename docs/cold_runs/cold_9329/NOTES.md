# Cold run 9329 -- county_hospital_001 on Level Factory 0.218.2 and Deli Counter 0.231.1 (2026-10-19): the breadth sweep

Staged from 9230. Part of the breadth sweep of 2026-10-19; `docs/findings/breadth_sweep_2026-10-19/README.md` holds the sweep's table and both of its stops.

**Run:** 0 interventions, STOPPED at the export on the drop-edge gate: `UNDECLARED_DROP_INDOORS`, 20 unguarded edges,
all one rim. It is the storey-2 slab round the hospital's elevator shaft, 7.2 m above the ground floor. The pick was
seed 9208. Findings 62 / 83. The light bake has 1,434 users.

**The gate was right.** `presets.hospital` stacks the shaft's holes on every storey and declared only storey 1's. It
was fixed in Deli Counter 0.232.0 (`patches/patch_dc_hospital_shaft.py`), and cold run 9334 is this mission again on
it.
