# Cold run 9315 -- precinct_yard_001, the first run with a roof hatch; stopped at the art pass, on purpose by the gates

Staged from 9279 (`stage_batch.py 9315 9279`), driven `cold_drive.sh 9315 9279 precinct_yard_001 auto`.
Tool state at `--begin`: Zoo 1.113.0 (643131f), Deli Counter 0.224.0 (9675f7b8, the library rebuilt with it),
Level Factory 0.215.1, Lot 0.123.0, Lux 0.77.0, Patina 0.32.0. What it tested: roadmap 170 step 1, a
`roof_hatch` prop slot (Zoo's curb and hinged lid, open by default) on every `hatch` vertical link on a roof
slab (`docs/findings/roof_openings_170/`).

**INTERVENTIONS: 0** (`--end`: journal 0, unattributed files 0). **Drive exit 2 at the art pass**: `Blocked:
unresolved blocking issues (blockers open: 2, total findings: 84)`. No export, no package. The run is the
measurement of the two gates against the new species, and both gates were right.

## What ran

- Shell: the three generated precinct shells (`lf_precinct_yard_001_{9001,9102,9203}`) each carry
  `roof_hatch_13_-9` at (13, -9, 7.3), rot 180 (the ladder faces S), default `open`, with its `hatch`
  interactive entry. Walk test and Laser Tag on the greybox: seed_9203 PASS 100 (route completion 1.00), picked --
  the same pick as 9279. seed_9102 PASS_WITH_TUNING 77.
- Art: `zoo_kit_build` built `prop_roof_hatch_delco_04_w166_d166_h20.glb` PASS and its
  `..._closed.glb` PASS `[state:closed]` for the library buildings that carry a hatch. `presentation_compose`
  composed 17 scenes and refused two:
  - **courthouse_a02** (`roof_hatch_-16_12`): placement gate MISMATCH -- `placed [1.668, 1.835, 1.987]` on
    `greybox [1.66, 0.2, 1.66]`, fit 180 deg (the lid at 100 degrees leaning out past the curb; the gate
    measures the whole module's footprint, 0.25 m); circulation gate FAIL -- shell arm, `roof_hatch_-16_12`
    0.2 m into `ladder:ladder_0`.
  - **airport_terminal_a01** (`roof_hatch_24_8`): circulation gate FAIL, the same 0.2 m into `ladder:ladder_0`.
  - The z-fight gate: courthouse_a02 0 pairs with the hatch standing (521 solids); airport_terminal_a01 2 and
    convenience_store_a01 2, both `ext_0_N_seg5` against `int_0_1_open1`, the wall-beside-an-opening class
    roadmap 177 records -- not the hatch's (convenience_store_a01 has none).

## What it decided

- Zoo 1.113.1 (c9c1596): the lid stands vertical on a hinge 4 cm inside the back wall, its edges 5 mm inside the
  curb's planes -- the open footprint is the curb's. Census re-run: 260 tris, 0 pairs at every corner.
- Deli Counter 0.224.1 (d28277d7): `circulation.excused_own_furniture` excuses a `roof_hatch_*` prop in a
  ladder's climb volume as it excuses a stair's guard in its stair, listed as excused; `roof_hatch.py` is a
  geometry source.
- Cold run 9316 is the re-run, staged from this one.

## Kept

`hatch_station.py` -- where the precinct's hatch stands in a package of this mission and two cameras to see it
with (`tools/look_shots.py --station`); written for this run's package, used on 9316's.
