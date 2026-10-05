# Cold run 9162 -- 0 interventions; the terrace deals its houses: every row shows all twelve, none more than three times

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack.** Level Factory 0.142.0. `empties.terrace` deals its houses from a
shuffled bag of every design, refilled when empty, instead of drawing each
uniformly. Cold run 9160 had shown that a uniform draw from twelve designs
leaves two or three unused and shows one up to six times.

**Result:** every leg ran, `INTERVENTIONS: 0`.
- Shell: 3 candidates, all distinct; 0 blockers.
- Art exited 1 on 55 findings, as before.
- No `STEM COLLISION`.
- The walk copy is this run's.

## The row, measured

`patches/dc_more_rowhomes/count_terrace.py` on each candidate:

| seed | houses | designs used | most of one design | 9160, drawn |
|---|---|---|---|---|
| 9080 | 25 | 12 of 12 | 3 | 10 used, 5 |
| 9181 | 31 | 12 of 12 | 3 | 12 used, 6 |
| 9282 | 30 | 12 of 12 | 3 | 10 used, 5 |

Each design shows floor(n/12) or one more times, as the deal promises. No
two neighbours are the same house. With all twelve designs in the exported
row, it carries 17 TV antennas and 4 dishes (9161: 14 and 2).

## Before the run

- Level Factory's suite exited 0: 1,887 passed, 14 skipped, 1 xfail.
- The new tests' three defining ones failed on 0.141.0; the fourth
  (neighbours differ) passed there too and stays as a guard.
- The terrace has its own stream (`seed ^ 0x5E3A11`), so nothing else on
  the site moved.

## Frames

`docs/findings/empties_deal_9162/`. From above, the row reads as a street:
- brown, orange and red brick, cream siding, stone and painted block;
- two- and three-storey houses mixed;
- antennas on most roofs.

## The price

A = 9161's package, B = 9162's, A2 = 9161's again, with the two-pass
harness and 60 s cool-downs (`price_deal.txt`, `price_deal_robust.txt`).
- **Draws:** median 0, mean -24, from -377 to +179. Different houses stand
  in different places; the control is 0 everywhere.
- **Median frame**, against the mean of A and A2 over all 53 headings:
  +0.003 ms. The control's median is +0.002, with 0 headings more than
  1 ms apart. Nothing to price.
- **Light census:** 61 over the cap, unchanged, out of 5,136 meshes.

## Found on the way, not this run's

**An Empty's front door is open to a ray** (`patches/lf_empties/
door_collision_probe.gd`, headless, on this run's walk copy, at
`gs_empty_rowhome_f`).
- **Rays:** shot straight at the front at 1.0 and 2.0 m, they stop at the
  wall's face everywhere except across the doorway. From x 1.2 to 1.8 they
  travel the whole 10 m into the shell and meet nothing. Rays at the
  windows stop at the face, because each window has a pane collider in the
  base.
- **Bodies:** the gap is 0.7 m between the doorway's jamb colliders. The
  walk capsule (radius 0.4) stops in the reveal, so no body walks in.
- **What gets through:** a shot, a thrown object and a line-of-sight test
  pass through an Empty's front door into its hollow interior.
- **The fix belongs to Deli Counter's base:** a facade doorway gets a leaf
  collider, as a facade window gets its pane.

**The lines over `gs_empty_rowhome_l`'s roof** that 9161's notes traced
towards a party-wall gutter are queued with it: Patina hangs a gutter on
every top-storey wall, party walls included.
