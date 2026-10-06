# Cold run 9179 -- 0 interventions; restaurant_row_001 gets the lot library, and with it the Empties

The proof run for Level Factory 0.145.0: the lot library by default, where it
can honour the brief. Its brief is restaurant_row_001's (staged from 9175):
`corner_deli`, three buildings, and no `lot_library`. The seed was picked by
the driver (seed_9104).

**The default, decided at `batch create`:**
- The source brief names no library.
- The workspace's copy
  (`batches/cold_9179/missions/restaurant_row_001/brief/brief.json`) records
  `C:\Projects\gabagool_studios\gabagool_factory\deli_counter\build`.
- `corner_deli` anchors on the `deli` family.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**

**The draws:**

| candidate | 9175 (before) | 9179 (after) |
|---|---|---|
| seed_9003 | shell.glb x3 | courthouse_a01, deli_a03, market_hall_a03 |
| seed_9104 | shell.glb x3 | casino_a02, deli_a01, self_storage_a03 |
| seed_9205 | shell.glb x3 | auto_shop_a01, deli_a03, warehouse_a01 |

- Every candidate stands a deli and two other real buildings, where 9175
  placed three copies of one generated shell.
- **The Empties came with the library:** 12 merged, where 9175 had none.

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 45 findings.
- **Art:** 0 blockers of 65 findings.
- **Bake:** 4,556 users, 91.5 s in the editor.

**The anchor is a deli, which is what the brief's archetype says.** Whether a
deli's interior carries the Flappahs store's detail is a separate question,
the detail audit's: delis get the generic sales-floor fixtures, not the
store's counter, cooler wall or poker machines.
