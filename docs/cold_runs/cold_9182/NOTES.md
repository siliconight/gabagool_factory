# Cold run 9182 -- 0 interventions; gas_block_001 stands the station with pumps on every candidate, and FLAPPAHS on its band and pylon

The second proof run for the store work of 2026-10-06. It uses 9165's brief
and seeds: `gas_station`, three buildings, the lot library, the Empties.
- Deli Counter 0.188.0 moved the Flappahs store out of the gas family.
- Pixelcoat 0.58.0 and Level Factory 0.146.0 name every station's band
  FLAPPAHS.
- Zoo 1.75.0 spells it FLAPPAHS on the pylon and pumps.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**

**The draws, against 9165:**

| candidate | 9165 | 9182 |
|---|---|---|
| seed_9080 | bank_tower_a02, freight_terminal_a01, **gas_station_a03** | **gas_station_a02**, landmark_hall_a02, rail_station_a01 |
| seed_9181 | arena_a03, gas_station_a02, marina_a02 | airport_terminal_a02, funeral_home_a03, **gas_station_a02** |
| seed_9282 | airport_terminal_a02, funeral_home_a02, gas_station_a02 | casino_a02, freight_terminal_a02, **gas_station_a02** |

- Every candidate now stands `gas_station_a02`, the station with pumps.
- In 9165, seed_9080 drew the Flappahs store, which has none.
- The other buildings moved too. The library's families changed under the
  same seeds (memory: library growth reshuffles lots), so compare stations,
  not neighbours.

**In the package** (seed_9181, the driver's pick):
- **Bands:** `b0=flappahs` on the station. Also `b1=delco_storage` on
  `airport_terminal_a02` and `b2=keystone_savings` on `funeral_home_a03`.
- **The pylon** (`prop_price_pylon_..._w340_d70_h900`): its face texture
  reads FLAPPAHS, cream on green, over REGULAR, PLUS and SUPER.
- **A pump module** is there (`prop_pump_delco_1997_05_...`).
- **32 Empties.**

**The two named bands are the defect Level Factory 0.147.0 removes.** An
airport called DELCO STORAGE and a funeral home called KEYSTONE SAVINGS are
`default`-pool shops on buildings that are not shops
(`docs/findings/two_names_one_building/`).

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 39 findings.
  - seed_9181 and seed_9282: 0 majors.
  - seed_9080: 1 major.
- **Art:** 0 blockers of 57 findings.
- **Bake:** 4,280 users, 86.7 s in the editor.
- **The findings diff** is against 9181's workspace, a different mission. It
  counts this mission's findings, not a change.

**Seen, not acted on:**
- **Two derivations of one price.**
  - Zoo's pylon prices regular at 1.19 and nine tenths.
  - Pixelcoat's `fuel_price` board (0.34.0) derives 1.21 from 1997
    Pennsylvania data.
  - Since Level Factory 0.146.0 the board is never dealt, so only the pylon
    shows a price.
- **One brand, two colours**, as in 9181. The band is cream on red; the
  pylon and door box are cream on green.
