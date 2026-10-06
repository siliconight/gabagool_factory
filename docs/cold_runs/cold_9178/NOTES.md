# Cold run 9178 -- 0 interventions; card_block_001 draws no demo shell

The proof run for Deli Counter 0.187.0 and Level Factory 0.144.4 (roadmap
185): a shell Deli Counter calls a demo is never drawn into a lot. Its brief
is card_block_001's (staged from 9174), with the seed picked by the driver
(seed_9162).

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**

**The draws, against 9174's on the same brief:**

| candidate | 9174 (before) | 9178 (after) |
|---|---|---|
| seed_9061 | card_shop_a01, pharmacy_a01, **setback_demo** | card_shop_a01, landmark_hall_a01, video_store_a01 |
| seed_9162 | card_shop_a01, **pvp_station_ref**, stadium_a01 | card_shop_a01, pawn_shop_a01, strip_retail_a02 |
| seed_9263 | card_shop_a01, parking_garage_a01, supermarket_a03 | card_shop_a01, pharmacy_a01, supermarket_a03 |

- No candidate draws a demo or reference shell.
- seed_9263's lot changed too, though it drew none. Five fewer shells in
  the pool re-deals every seed, as the 0.144.4 changelog says.
- The card shop, the brief's anchor, stands on every candidate.

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 45 findings.
- **Art:** 0 blockers of 66 findings.
- **Empties:** 12 merged.
- **Bake:** 2,349 users, 65.0 s in the editor.
