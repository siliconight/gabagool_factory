# Cold run 9352 -- 0 interventions; bank_block_001, seed 9054: the roof hatch stands over its ladder's cut

**What it was for.** The walker's look review, 2026-10-19 (the factory's roadmap 170): "the hole of the ladder
opening doesn't match the lid...they should match". Deli Counter 0.239.0 cuts a roof hatch's hole, files its drop
link and stands its slot at `roof_hatch.opening` -- the hatch's square centred on its ladder's own cut, which had run
0.35 m past the square, and 0.27 m past the curb, at every roof hatch in the library. This is cold run 9348's level,
whose bank_branch_a04 carries a roof hatch, `roof_hatch_16_12`, its ladder facing S.

**Tools:** Deli Counter 0.239.0 (b7998be3), Lot 0.126.0, Zoo 1.116.0, Level Factory 0.224.0, Lux 0.78.0. Staged
from 9348; seed 9054 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 8 min.
Shell 0 blockers of 73 findings; art 0 of 101; **findings 101 -> 101** against 9348. The shipped package stands
the hatch at Godot (16, 8.5, -11.55), Deli Counter's (16, 11.55): 0.45 m south of the link at (16, 12), over the
ladder's cut. 9348's stood at the link. Its workspace has since been retired as a pushed run's, and 0.238.0's
built slots record where it stood. casino_a03, the level's other roof-hatch building, moved its hatch the same way;
it is not framed here.

## The hatch (`hatch_9348_vs_9352.jpg`)

The stations of 9316's frames, the ones the walker judged (`docs/cold_runs/cold_9315/hatch_station.py <walk copy>
bank_branch_a04 16 12 8.5`): from above, from either side, aimed at the link in both runs. 9348 left, 9352 right,
three in the inspection light (`look_shots.py --inspect studio`) and one in the level's own rainy night.
- **From above:** in 9348 the cut's outline runs out past the curb's corner on the climber's side, and at night it
  is a dark notch there. In 9352 the curb's opening is the cut, edge to edge.
- **From the sides:** in 9352 the hole fills the opening the lid swings up from.

Not priced: the hatch module is 0.238.0's (1.66 x 1.66, the same stem). The roof moved a hole and a slot, and five
buildings' lights reflowed round it (`patches/dc_hatch_over_ladder/build_records.out.txt`). None of the five is in
this level.
