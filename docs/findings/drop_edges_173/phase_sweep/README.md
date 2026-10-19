# The lattice phase sweep (roadmap 173, What is left item 7), 2026-10-19: measured, not attributed

**What was asked.** How far the drop-edge gate's answer moves with the lattice's phase at the cell's own scale.
Level Factory 0.219.0 took every query off the round coordinates. It did not ask what a different phase of the same
0.5 m lattice would find. A verdict that flips with the phase is a false stop waiting for the level that lands on
the wrong phase, and a false stop is an intervention on somebody else's level, as cold run 9333's was.

**How.** `phase_instruments.py` writes Level Factory 0.219.0's `walkable_edge.gd` at six phases. Each changes only
its two `SEAM_NUDGE` constants and keeps the odd millimetres, moving the lattice a quarter cell at a time. Phase
`p00` is the shipped instrument byte for byte, the control. The factory's
`docs/findings/breadth_sweep_2026-10-19/gate_ab.py` ran the gate's own measure, classify and assert at every phase on
copies of the three distinct levels whose workspaces remain: cold runs 9335 (restaurant_row_001), 9332
(gas_block_001) and 9334 (county_hospital_001). `phase_table.py` reads the scans (`phase_table.out.txt`). Every arm's
scan and rows are in `gate_ab/`.

## The result

The verdict holds at 17 of 18 phase-package pairs. The control phase reproduces 9335's export scan exactly, and the
earlier A/B's 0.219.0 arm on the other two, whose exports ran 0.218.2.

| run | mission | phase (dx, dz) m | verdict | reached / standable | unguarded | undeclared |
|---|---|---|---|---|---|---|
| 9335 | restaurant_row_001 | 0.0031, 0.0023 (shipped) | passes | 55,492 / 63,957 | 52 | 0 |
| 9335 | restaurant_row_001 | 0.1281, 0.1273 | REFUSES | 41,322 / 62,359 | 52 | 1 |
| 9335 | restaurant_row_001 | the other four | passes | 53,144 to 55,485 | 41 to 54 | 0 |
| 9332 | gas_block_001 | all six | passes | 48,647 to 53,164 | 17 to 30 | 0 |
| 9334 | county_hospital_001 | all six | passes | 24,525 to 25,865 | 48 to 56 | 0 |

**One phase refuses a level the shipped phase passes.** At (0.1281, 0.1273), restaurant_row_001 refuses on one row:
(-61.62, 3.30, -9.87), a 3.3 m drop from the storey-1 slab (`slab_col_1`) to the ground. That is deli_a03's
up-stair again, beside the 0.4 m slot between the flight's east side (x -62.0) and the slab's hole edge (x -61.6),
just south of the discharge plate. The slab's top face, read off the package's GLB, bounds the hole at site x -64.0 to
-61.6 and z -13.81 to -8.71; the plate fills its north end from z -9.75. At the shipped phase that slot's edges are found from the stair's side and class
as a flight's own side. At this phase one is found from the slab's.

**At the same phase the flood reaches a quarter less of the level.** 41,322 cells against 53,144 to 55,492 at every
other phase. Something the body must pass to reach about 14,000 cells, a landing or a door, is lost at that phase.
That is item 7's "one-cell landing lost to a centimetre's offset", measured again on another level.

**The classes move with the phase everywhere.** Things' tops on gas_block_001 read 0 to 18, and declared drops on
county_hospital_001 read 40 to 48. Neither class is refused, so neither moves a verdict.

## Not established

- **Whether the refused row is a defect or an artefact.** It is not attributed. The slab's hole edge carries a guard
  rail (`stair_guard_rail_6_col`) along part of its length, and whether it ends there is unread. The slot is 0.4 m
  across: exactly the instrument's probe (`PROBE_R` 0.20) and narrower than the contract's body (0.35 radius), so the
  probe radius alone may decide it. The next step is the factory's `docs/findings/breadth_sweep_2026-10-19/edge_cells.gd`
  at this phase, on the row's cell pair and its neighbours.
- **What the flood loses at that phase.** It is not located. A reach map, the reached cells of `p11` against `p00`,
  would put it on the level.
- **Any other level.** Three levels were swept. The four other sweep missions' workspaces were retired by rule
  before this ran, and a cold run regenerates them.

## What it means for the gate, not yet decided

A gate that samples one phase can pass a level that another phase refuses, and the reverse. Two directions are
open, each a call for after the attribution: let the instrument's answer stand only where phases agree, for
example by refusing a row only if a second phase finds it too; or make the sampling finer where it matters, such as
the probe at the contract's body radius, or a half-cell sub-sample at a drop candidate. Neither is started.
