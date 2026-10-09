# Cold run 9210 -- 0 interventions; the site audit reaches the validation report

club_block_014, seed auto, staged from cold run 9209. It tests **Lot 0.102.0**
and **Level Factory 0.163.0** (roadmap 215):
- **Lot** keeps its site audit in the site's gameplay manifest, not only in
  its job log.
- **Level Factory** reads it into the validation report. So every cold
  run's findings diff now counts it.

Tool versions hashed at `--begin`: Lot 0.102.0, Level Factory 0.163.0, Laser
Tag 0.25.0, Zoo 1.86.0, Deli Counter 0.203.0, Lux 0.69.0, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0. Only Lot and Level Factory
moved since 9209.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0). Every leg ran.

**Picked: seed_9181**, on the same figures as 9206 to 9209:
- 9080 at 1 major and route completion 0.92;
- 9181 at 0 majors and 0.96;
- 9282 at 1 major and 0.96.

The new findings are moderate and info, so they move no candidate's count of
majors. `pick_candidate.py` counts majors only.

## The findings diff counts the site audit

`cold_drive.sh`'s findings step, 9209 against 9210: **58 to 72.**

| code | 9209 | 9210 |
|---|---|---|
| `S_GETAWAY_AT_SPAWN` | 0 | 4 |
| `S_RESPONDER_ARC` | 0 | 4 |
| `S_STREET_CROSS` | 0 | 6 |

Nothing else moved, and no `LOT_SITE_AUDIT_UNREAD` was raised: every Lot
assembly's block was read.

**Every one of the 14, attributed** (`audit_codes.py`, which reads the
validation report and the Lot jobs' logs; output `audit_codes.txt`, and
`audit_codes_9209.txt`, the control: 0 of 58):

| the Lot run | the arc | findings |
|---|---|---|
| seed_9080, `lot_assemble` | 33 deg | `S_RESPONDER_ARC`, `S_GETAWAY_AT_SPAWN` |
| seed_9181, `lot_assemble` | 6 deg | `S_RESPONDER_ARC`, `S_GETAWAY_AT_SPAWN`, `S_STREET_CROSS` x2 |
| seed_9282, `lot_assemble` | 16 deg | `S_RESPONDER_ARC`, `S_GETAWAY_AT_SPAWN`, `S_STREET_CROSS` x2 |
| seed_9181, `themed_site_assemble` | 6 deg | the same four as its `lot_assemble` |

- **Why four of each.** The selected candidate is assembled twice: as a
  candidate, and themed in the art leg. Each Lot run carries its own audit.
- **Why six crossings, not eight.** seed_9080's legs cross no road.
- **The report matches the job logs line for line.** `S_RESPONDER_ARC` is
  moderate, the rest info; all are non-blocking.

## What held

- **The art leg:** 0 blockers open. Its `exit 1` is the approval gate
  waiting, as in 9209.
- **The export:**
  - the light bake reads as 9209's: 432 models lightmapped, 7 kept dynamic,
    1 spawned set dynamic, 3,898 users;
  - the package exported.

## What it leaves

**`S_RESPONDER_ARC` is now a counted finding on every candidate of this
mission.**
- **The arcs:** 33, 6 and 16 degrees, against the rule's 210.
- **Whether that is the roads' fault, the rule's, or the gameplay layer's
  design** is roadmap 215's open question. It is not decided here.
