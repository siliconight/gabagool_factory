# Cold run 9228 -- 0 interventions, 0 retries; the roadside stands beyond the fence

gas_stop_001 (`gas_station` on a `strip` site), night and clear, seed auto,
staged from 9177's batch and brief. It proves roadmap 228's `roadside`
recipe end to end: Level Factory 0.175.0 decided the surroundings from the
archetype (the brief names none: `surroundings_resolved: {asked: "", got:
"roadside", known: true}`), Lot 0.109.0 laid the thin tree belt and the far
warehouses, Zoo 1.96.0's site kit built them, and Level Factory 0.174.0
shipped them as MultiMeshes behind 9224's fence. With 9226 (yards) and
9227 (parkland) this closes the three recipes 9225's borough left.

Tool versions hashed at `--begin` (`_runs/cold/cold_9228/before.json`): the
set 9226 and 9227 ran on, unchanged -- Deli Counter 0.205.0, Dispatch 0.5.2,
Laser Tag 0.25.0, Level Factory 0.175.0, Lot 0.109.0, Lux 0.73.0, Patina
0.30.0, Pipeline 0.6.0, Pixelcoat 0.62.0, Zoo 1.96.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9011** on the walktest and Laser Tag's route findings.
- **The shell leg:** 0 blockers of 53. **The art leg:** 0 blockers of 76.
- **The bake:** 401 models and 2,254 primitive meshes, 82 steady rigs
  baked, 20 failing left live, 144 room fills, 4,069 users, 114.4 s: the
  largest of the three recipe levels (a 240 x 120 m plate, three buildings).
  The backdrop is not in it.

## The roadside, laid, built and shipped

- **Lot** (`themed_site_assemble/1/job.log`): `LOT_PERIMETER_FENCED: 8
  run(s), 753.7 m` round the 240 x 120 m plate, and `LOT_BACKDROP_PLACED:
  recipe roadside, 0 rowhome(s) in 3 bands a side (N 93, S 93, E 37, W 35),
  6 module(s), 0 water tower(s)` (the rowhome tally is 9226's cosmetic
  defect, Lot 0.109.1's to fix). The site's slot manifest counts 258
  `site_backdrop` slots: 245 `backdrop_tree` (102 at 5 x 5 x 7 m, 73 at 7 x
  7 x 10, 70 at 9 x 9 x 13) in the thin belt, and 13 `backdrop_warehouse`
  (5 at 24 x 16 x 7, 3 at 32 x 16 x 8, 5 at 40 x 20 x 9) in the far band.
- **Zoo's site kit** built all six modules PASS.
- **Level Factory** (`export.log`): `[export] backdrop: site_backdrop.tscn
  -- 258 instances of 6 module(s) on their sides, 21 draw calls (N 0, S 0,
  E 0, W 0; 0 tower)`.

## Seen

`edge_before_after.png`: the control is this package with the backdrop
scene not loaded (`tools/backdrop_off.py`), the subject the package as
shipped; the stations are road 0's two ends (`tools/edge_stations.py`,
`stations.txt`: the plate's one road reaches both edges) and look_shots'
four elevated views. On a clear night under the moon:
- **Down the road to either edge** the control's lamps end against an
  empty horizon and the subject's against a line of crowns under the last
  lamps, the roadside's thin belt 4 to 20 m past the fence; the far
  warehouses, 66 to 92 m out, do not read at night from the road.
- **From the four elevated views** the belt is the whole horizon: ranks of
  round green crowns directly behind the storefront row (`elev_S`), and from
  east and west the near belt's 9 m crowns, 4.75 m past the fence, loom in
  the foreground larger than the buildings. This is the frame the walker's
  verdict on 9227 describes, "giant lolipops vs. trees": the same species at
  the same three sizes, closer to the fence than the parkland's, and in a
  clear sky with nothing to soften the spheres.
- **Roadmap 228 step F answers both halves:** Zoo 1.97.0 redraws the tree
  with a forking trunk and a lobed crown in three forms by the slot's
  proportions, and Lot 0.110.0 lays the belt in clusters with daylight
  between them, mixes the forms and starts the belt 6 m off the fence
  (4 m on a roadside). Both are drafted and proven on clones; 9229's
  successor prices them.

## Priced

`price/price.txt`, the package against its own backdrop-off copy through
`docs/findings/horizon_glow/price_glow.py` (control, subject, control; the
harness calls the subject `glow`): 53 headings a run, on the heaviest level
of the three (1,230 draws a heading mean, p95 4.7 to 4.9 ms).

| run | draws +mean | +min | +max | p95 +median ms | +max ms |
|---|---|---|---|---|---|
| control_1 | 0.0 | 0 | 0 | 0.03 | 0.32 |
| subject | 23.2 | 0 | 36 | 0.20 | 0.73 |
| control_2 | 0.0 | 0 | 0 | -0.03 | 0.18 |

The controls' spread is 0.09 ms p95 and 0 draws; no heading flipped
between its own two passes. Against the controls' mean the draws' median
over the 53 headings is **+25** (0 to +36: the 21 backdrop MultiMeshes and
the fence, seen from most headings on a 240 m plate) and the p95 median
**+0.20 ms, twice the controls' spread**: the first recipe with a frame
cost the harness can see, about a fifth of a millisecond on a 4.8 ms frame,
worst heading +0.73. The trees are 132 triangles each today; step F's
redraw at about 670 keeps the same draw count and 9229's successor prices
it here.

## What this run does not prove

The roadside by day; the look from a player's eye at the fence; and the
trees' look, which the walker has judged on 9227's parkland ("giant
lolipops vs. trees"): the same species stands here, and roadmap 228's step
F redraws it.

## Instruments

- `tools/recipe_run_record.sh 9228 gas_stop_001` made the control copy, the
  stations, the frames, the sheet and the price (`record.log`).
- `stations.txt`: the stations derived from the drawn spec. `price/`: the
  three perf reports. The frames: `_scratch/frames_9228/` (not tracked).
