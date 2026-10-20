# Cold run 9347 -- 0 interventions; restaurant_row_001, seed 9003: deli_a03's stair slot through the drop-edge gate

**What it was for.** Level Factory 0.222.0 repaired the drop-edge probe's model of a body (roadmap 173, What is left
item 7; `docs/findings/drop_edges_173/probe_body/`), measured on three packages none of which carried deli_a03 --
whose stair slot is where the lattice phase sweep's refusal stood, on cold run 9335. This run makes such a package:
restaurant_row_001's seed 9003 still draws deli_a03 (Level Factory 0.221.0's hole rate says yes for that candidate,
so its drop is kept), and it is cold runs 9340 and 9341's level.

**Tools:** Level Factory 0.222.0 (ee606d9), Deli Counter 0.237.0, Zoo 1.114.1, Lot 0.125.0, Lux 0.78.0. Staged from
9341; seed 9003 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`.
- **Shell:** 0 blockers of 79 findings. seed_9003 placed deli_a03; seed_9104 and seed_9205 deli_a01 (the hole rate's
  no -- 9205 drew deli_a03 and was swapped).
- **Art:** 0 blockers of 108 findings.
- **Export:** exit 0 on the new instrument: reached 55,638 of 69,747 standable cells, 26 unguarded, 0 undeclared
  (declared drop 10, ladder hole 6, outdoors 4, stair side 6); the light bake 353 models, 3,523 users.

## The slot through the gate (`docs/findings/drop_edges_173/probe_body/logs/gate_ab_cold-9347-ws.log`)

The phase sweep's six phases, the instrument before (0.221.0) and after (0.222.0), on a copy of this package:

| phase | before: reached / standable, verdict | after: reached / standable, verdict |
|---|---|---|
| p00 (shipped) | 55,451 / 63,916, passes | 55,638 / 69,747, passes -- the export's own scan, to the cell |
| **p11** | **41,244 / 62,281, REFUSES**: (-61.62, 3.30, -9.87), 3.3 m, slab_col_1 to slab_col_0 | 55,027 / 68,576, passes |
| p22, p33, p20, p02 | 53,069 to 55,443, passes | 54,666 to 55,780, passes |

The refused row is the phase sweep's on 9335 to the centimetre, and the flood's 41,244 its 41,322: both defects
reproduced on a fresh package and both gone after the repair. Before, the instrument refused 1 of 24 arms over the
four levels measured; after, 0 of 24.
