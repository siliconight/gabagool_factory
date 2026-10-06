# Cold run 9180 -- 0 interventions; warehouse_yard_001 gets the lot library, and with it the Empties

The second proof run for Level Factory 0.145.0. Its brief is
warehouse_yard_001's (staged from 9176): `industrial_warehouse`, two
buildings, and no `lot_library`. The seed was picked by the driver
(seed_9206).

**The default, decided at `batch create`:**
- The workspace's copy of the brief records `deli_counter\build`.
- `industrial_warehouse` anchors on the `warehouse` family.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**

**The draws:**

| candidate | 9176 (before) | 9180 (after) |
|---|---|---|
| seed_9004 | shell.glb x2 | credit_union_a01, warehouse_a02 |
| seed_9105 | shell.glb x2 | mansion_a02, warehouse_a01 |
| seed_9206 | shell.glb x2 | pharmacy_a02, warehouse_a01 |

- Every candidate stands a warehouse and one other real building, where 9176
  placed two copies of one generated shell.
- **The Empties came with the library:** 12 merged, where 9176 had none.

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 46 findings.
- **Art:** 0 blockers of 60 findings.
- **Bake:** 2,044 users, 62.2 s in the editor.

**With 9178 and 9179, the block's three proof runs all pass.** The demo
shells are out, and the library by default reaches both no-library briefs
that can use it. county_hospital_001, one building with no hospital family,
keeps its generated building by construction and was not re-run.
