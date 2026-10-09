# Cold run 9207 -- 0 interventions; the phantom LOT_RESPONDER_BLOCKED is gone

club_block_014, seed auto, staged from cold run 9206. Tests **Lot 0.100.1**
(roadmap 212): the responder planner checks the boxes it records.

Tool versions hashed at `--begin`: Lot 0.100.1, Level Factory 0.161.0, Laser
Tag 0.25.0, Zoo 1.86.0, Deli Counter 0.203.0, Lux 0.69.0, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0. Only Lot moved since 9206.

**`INTERVENTIONS: 0`.** The journal holds no entries, and the run's diff is
empty. Every leg ran.

**Picked: seed_9181**, as in 9206.

| seed | 9206 | 9207 |
|---|---|---|
| 9080 | 2 majors, route completion 0.92 | 1 major, 0.92 |
| 9181 | 0 majors, 0.96 | 0 majors, 0.96 |
| 9282 | 1 major, 0.96 | 1 major, 0.96 |

Seed_9080's second major was the phantom.

## Findings

59 to 58. The only move is `LOT_RESPONDER_BLOCKED`, 1 to 0.

9206's one was the phantom on seed_9080: a lane cleared the getaway van by
1e-6 m, the record rounded the box's edge onto the van's, and the read-back
saw 3.6e-15 m of overlap (`docs/cold_runs/cold_9206/NOTES.md`). Lot 0.100.1
rounds each box once, checks it, records it, and clears by 1 mm.

## The arrivals, every candidate

From each candidate's `lot_assemble` `responder_plan`:

| seed | arrivals | findings | lane shifts |
|---|---|---|---|
| 9080 | 3 | none | 0.649, 0, 0 |
| 9181 | 3 | none | 0, 0.649, 0 |
| 9282 | 3 | none | 0, 0.649, 0 |

**Every candidate steers exactly one lane, and by the same 0.649 m.** The
van's overhang is the same by design wherever it parks: `site_getaway`
stands a 2.60 m slot 0.20 m off the kerb, in a 2.2 m parking lane. The shift
is 0.648 m of need plus the record's 1 mm.

**The package.** `responder_arrivals.json` is schema v2: three arrivals,
the stops 9206 shipped, and the steered lane in nine boxes at
`lane_shift_m` 0.649.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 43 findings.
- **Art:** 0 blockers of 58. The leg exits 1, as before; the driver gates
  on "blockers open: 0".
- **The bake:** 432 models and 1,528 primitive meshes lightmapped, 7 kept
  dynamic; 76 steady rigs baked, 13 failing and 2 cycling left live; 172
  room fills; 3,898 users; 89.0 s in the editor.
