# Cold run 9164 -- 0 interventions; an Empty's door shut to a ray, and no gutter on its party walls

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`. 9163's
stack again, after 9163 stopped on a full disk.

**Stack.**
- **Deli Counter 0.186.0** (roadmap 183): a facade's door aperture is
  filled full-thickness, as its window's is (`ext_..._open<k>_leaf` and its
  collider).
- **Patina 0.29.1** (roadmap 184): on an Empty, a face with no opening on
  any storey is a party wall and gets no gutter.

**Result:** every leg ran, `INTERVENTIONS: 0`.
- Shell: 3 candidates, all distinct; 0 blockers.
- Art exited 1 on 55 findings, as before.
- No `STEM COLLISION`.
- The walk copy is this run's.

## The two fixes, measured

**The door** (`patches/lf_empties/door_collision_probe.gd` on
`gs_empty_rowhome_f`, this run's walk copy):

| | rays across the doorway, x 1.2 to 1.8, at 1.0 and 2.0 m | walk capsule from the sidewalk |
|---|---|---|
| 9162 | open: 10 m into the shell | its front stopped 0.26 m inside the reveal |
| 9164 | stop at the wall's face | its front stops at the face (z 6.16 against 6.15) |

**The gutters** (Patina's orders, every Empty in the level):

| | front and back | east and west (party walls) |
|---|---|---|
| 9162 | 158 | 144 |
| 9164 | 158 | 0 |

In the street frame down the row (`docs/findings/empties_fixes_9164/`), the
stone party wall at the alley carries its coping along the top and nothing
hung below it.

## Before the run

- Deli Counter's `check.py` passed every check after `build.py --all`.
  Patina's suite: 383.
- Each new test failed on the version before it, and each control passed
  there and still does:
  - a building you enter keeps its doors open: more than 20 such buildings
    with doors, none with a leaf;
  - a free-standing building keeps a gutter on every face.
- Stem plan: 0 collisions in 145 buildings.

## The price

A = 9162's package, B = 9164's, A2 = 9162's again, with the two-pass
harness and 60 s cool-downs (`price_fixes.txt`, `price_fixes_robust.txt`).
- **Draws:** median -16 a view, mean -20, up to -62. The control is 0
  everywhere. The party-wall gutters were the only white metal on their
  sides, so those sides' merged metal meshes are gone.
- **Median frame**, against the mean of A and A2 over all 53 headings:
  -0.076 ms. The control's median is +0.030, with 0 headings more than 1 ms
  apart.
- **Light census:** 61 over the cap, unchanged, out of 5,086 meshes.
- **The package copies** were deleted as each report landed; 11.5 GB free
  afterwards.
