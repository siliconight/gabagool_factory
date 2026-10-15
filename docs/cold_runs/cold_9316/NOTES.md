# Cold run 9316 -- precinct_yard_001, the roof hatch's second cut: 0 interventions, both gates satisfied

Staged from 9315 (`stage_batch.py 9316 9315`), driven `cold_drive.sh 9316 9315 precinct_yard_001 auto`.
Tool state at `--begin`: Zoo 1.113.1 (c9c1596, the lid vertical inside the curb's footprint), Deli Counter
0.224.1 (d28277d7, the hatch excused from its own ladder's climb volume), Level Factory 0.215.1, Lot 0.123.0,
Lux 0.77.0, Patina 0.32.0. What it tested: roadmap 170 step 1 after 9315's two gate refusals
(`docs/findings/roof_openings_170/`, `docs/cold_runs/cold_9315/NOTES.md`).

**INTERVENTIONS: 0** (`--end`: journal 0, unattributed files 0). **Drive exit 0**: shell, approvals, art, export
(light bake: 321 models and 137 primitives lightmapped, 130 steady rigs baked), findings, walk, retire.

## The pick and the buildings

Three candidates, all distinct; seed_9203 PASS 100 (route completion 1.00) picked on the walk test and Laser
Tag's route findings, as on 9315 and 9279; seed_9001 PASS 90, seed_9102 PASS_WITH_TUNING 77. The exported site
stands library archetypes -- courthouse_a02 (b0), clinic_a01, convenience_store_a01, airport_terminal_a01 and
twelve rowhome Empties -- not the generated precinct shell, so the hatches in the package are courthouse_a02's
(`roof_hatch_-16_12`, its ladder facing S) and airport_terminal_a01's (`roof_hatch_24_8`). The library draw
differs from 9279's (`library-growth-reshuffles-lots`), so there is no like-for-like fight baseline for this
mission in an earlier run.

## The gates, per building (`presentation_compose`'s job.log)

- courthouse_a02: placement 340/340 modules on the greybox collision; circulation shell 0 conflicts across 10
  volumes, **1 excused** (the hatch in `ladder:ladder_0`), dressing 0, roofprops 0; z-fight 0 pairs across 521
  solids.
- airport_terminal_a01: placement 214/214; circulation 0 conflicts, 1 excused; z-fight 2 pairs across 312
  solids -- `ext_0_N_seg5` against `int_0_1_open1`, roadmap 177's wall-beside-an-opening class, as on 9315.
- convenience_store_a01: z-fight 2 pairs (the same class; it has no hatch). clinic_a01 and the twelve Empties:
  every gate OK.

Findings 84 -> 108 across the export: PRESENTATION_CIRCULATION 2 -> 0 and PRESENTATION_PLACEMENT_MISMATCH
2 -> 0 (9315's blockers); DISPATCH_FINDING 0 -> 7 and LUX_NO_ROOM_PROBES 0 -> 1 are the classes 9279's leg
carried too (8 and 1 then) -- Dispatch's "anchor type 'hatch' / 'ladder' / 'camera_socket' is not a known
type" lines are the `HATCH_` marker's, older than this change.

## In the package

`lot/courthouse_a02/site.tscn` and `lot/airport_terminal_a01/site.tscn` each instance
`prop_roof_hatch_delco_04_w166_d166_h20` at the slot, `metadata/interactive_id` and
`metadata/interactive_state = "open"`; the `_closed` variant was built (`[state:closed]` PASS) for the hidden
state.

## The frames (`hatch_frames/`, `hatch_station.out.txt`)

`../cold_9315/hatch_station.py <package> courthouse -16 12 10.1` put courthouse_a02's hatch at Godot
(-48.00, 10.10, 29.00) -- the building stands at (-32, 0, 41), unrotated -- and gave `tools/look_shots.py` three
cameras on the walk copy: `hatch_hinge_side` (mean luminance 141.6), `hatch_climber_side` (149.7),
`hatch_from_above` (131.2), none clipping. What they show: a rust-brown steel curb on the roof with its lid
standing vertical on the far edge from the climber's side, the opening and the ladder's rungs visible through
it from above, a roof prop beside it. The lid stands clear of the opening; which edge it hinges on is read off
`ladder.climb_rect`'s reach and is the thing for the walker's eye.

## Retire

The drive's retire removed 1.4 GB (its own rule). The walk copy made for the frames
(`_runs/walk_export_precinct_9316`) was removed after them; the drive's own walk copy stands as usual.
