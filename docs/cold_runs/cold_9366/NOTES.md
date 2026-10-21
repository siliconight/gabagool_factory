# Cold run 9366 -- 0 interventions; bank_block_001, seed 9082: Zoo 1.120.1, stickers on some cars

**What it was for.** Cold run 9365's package carried a sticker on 27 of its 35 parked cars under Zoo 1.120.0; the
walker had asked for "some of the cars". Zoo 1.120.1 (2ed0d79) makes a sticker a chance per history, drawn last so
every car keeps 1.120.0's history, rust, primer, peel and seed. The same level a third time -- cold runs 9364 (Zoo
1.119.0), 9365 (1.120.0) and this -- staged from 9365, Zoo the only tool that moved.

**Tools** (`before.json`, every repo clean at `--begin`): Zoo 1.120.1 (2ed0d79); the rest as 9365.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0, retries 0); 7.0 min (04:21:19 to 04:28:19).
Shell 0 blockers of 79 findings; art 0 of 110; **findings 110 -> 110 against 9365**. The export's bake: 2,220 users
(9364 2,213, 9365 2,240).

**The cars, read from the package** (`docs/findings/car_wear_44/car_surfaces_9364_9365_9366.out.txt`): two of the eight
modules carry stickers -- the silver beater compact (four cars) and a driven tan SUV (three) -- seven of the 35 cars;
the cars' surfaces 147, against 140 at 9364 and 167 at 9365.

**Priced against 9364** (`docs/findings/car_wear_44/README.md`): draws differ at 20 of 53 headings, by +1 to +3, and
the control's two runs at none; frame time +0.015 ms where they moved and +0.014 where they did not, inside the
control's -0.040..+0.076 ms; texture memory +155,824 bytes, the one shared sticker sheet.

**The frames** (`cars_9364_9365_9366_inspect.jpg` and `_lit.jpg` in that folder): the beater's stickers, rust, primer
and lost clear coat in the inspection light; in the level's own heavy-rain light the cars are near-silhouettes and
little of it reads.
