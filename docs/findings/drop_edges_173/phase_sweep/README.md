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

## Attributed, the same afternoon

**The refused row is an opening a body cannot enter** (`stair_guards_a03.py`, `phase_attrib.py`, `edge_cells_at.gd`;
outputs in `attrib/`). deli_a03's flight is 1.6 m wide, x -63.6 to -62.0, in a hole 2.4 m wide, so a 0.4 m slot runs
down each side of it. Guard rails 5 and 6 stand on the hole's edges from z -13.81 to -10.11, and the plate starts at
z -9.752, so each edge is unrailed for 0.36 m beside its slot. At the shipped phase the slab cell beside the east
edge is occupied by the end of rail 6, so no row asks that gap. At (0.1281, 0.1273) the slab cell clears the rail's
end, and its neighbour in the slot falls 3.3 m to the ground floor. The opening is 0.4 by 0.36 m, smaller than the
contract's body at 0.70 m across and than the probe at 0.40 m. The west edge's row at that phase lies within the
gate's 0.6 m margin of a 1.4 m drop hole deli_a03 declares inside the stairwell, x -63.7 to -62.3, so it is filed as
declared. The east row misses that margin by 8 cm and is refused.

**The flood's loss is a moat beside a kerb** (`reach_dump.py`; both phases' surfaces in `attrib/`, gzipped). At (0.1281, 0.1273) the flood never reaches 14,695
surfaces at the east end of the site, among them the outdoor ground east of x 33.5 and all three floors of the
office. Every link into that region crosses a kerb, and the cell beside each kerb is occupied: the standing probe,
1.80 m tall on its 0.20 m radius, overlaps the kerb's 8 cm face. Measured at the main road's south sidewalk, whose box
ends at z 13.665 (`site.tscn`: centre 15.165, 3 m deep): at the shipped phase the first frontage cell is 0.163 m from
that face and free, and at (0.1281, 0.1273) it is 0.038 m from it and occupied. At the kerb's top the probe's rounded
base reaches 0.144 m from its axis, so the shipped phase clears this kerb by 1.8 cm.

**What they share.** Both are the standing probe's model of a body, not the level. The first is a gap the probe
reads as a fall and a body cannot enter. The second is a kerb a body steps over and the probe cannot stand beside.
The candidates, neither started: a body-fit test before a gap counts as a fall, the contract's radius at the rim
sampled across the opening; and a standing test that ignores what a body steps over, so a solid wholly below the
step height does not occupy a cell. Each is a Level Factory instrument change, to be measured across phases as
0.219.0 was.

## Not established

- **Whether the unrailed 0.36 m of each hole edge is meant.** It is too small for a body either way. Whether
  Deli Counter's rail rule stops short of the plate on purpose is unread.
- **How many other kerbs the shipped phase clears by millimetres.** One was measured.
- **Any other level.** Three levels were swept. The four other sweep missions' workspaces were retired by rule
  before this ran, and a cold run regenerates them.

## What it means for the gate, not yet decided

A gate that samples one phase can pass a level that another phase refuses, and the reverse. Two directions are
open, each a call for after the attribution: let the instrument's answer stand only where phases agree, for
example by refusing a row only if a second phase finds it too; or make the sampling finer where it matters, such as
the probe at the contract's body radius, or a half-cell sub-sample at a drop candidate. Neither is started.
