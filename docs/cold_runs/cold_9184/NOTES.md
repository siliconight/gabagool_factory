# Cold run 9184 -- 0 interventions; the row's end fences meet the perimeter (Lot 0.97.1)

The proof run for Lot 0.97.1: a fence does not grow the plate it marks the
edge of. It is 9183's brief and seeds, and the driver picked seed_9181
again, so the three runs 9182, 9183 and 9184 compare one candidate.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.** Findings
were 57 -> 57 against 9183, and 0 blockers in both legs (39 and 57
findings), as in 9182 and 9183.

**The plate and the ends** (`LF_gas_block_001.portable-godot/site.tscn`):

| | 9182 (no fence) | 9183 (Lot 0.97.0) | 9184 (Lot 0.97.1) |
|---|---|---|---|
| `perim_S` width | 246 m | 254 m | 246 m |
| west end fence ends at | -- | x -123.0, 4 m inside a wall at -127 | x -123.0, on `perim_W` at -123 |
| fence instances | 0 | 7 | 7 |
| bake | 4,280 users, 2,122 primitives | 4,312 users, 2,158 primitives | 4,290 users, 2,114 primitives |

- The walk-around 9183 left at both ends of the row is closed.
- The ground went back to 9182's size, and with it the 22 ground tiles the
  wider plate had added.
