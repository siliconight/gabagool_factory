# The fire escape: steel on the urban street's walk-ups (roadmaps 156 and 241)

The walker, 2026-09-13, with a photo of a brick walk-up: "this is something i'd like to see in our toolset,
fireescape stairs brick, uneven architecture" (roadmap 156). Roadmap 241's urban street is the first generated
block with brick walk-ups on it. The plan is `docs/proposals/FIRE_ESCAPE.md`; this folder is what was built, seen
and priced.

## What shipped

- **Zoo 1.110.0 (c173a8a): `fire_escape`,** drawn a storey at a time from a slot's box alone, black painted steel,
  one material, no collision (`patches/patch_zoo_fire_escape.py`, `zoo_fire_escape/`).
  - `flight_a`, `flight_b`: a landing (a slatted deck in a frame, a hatch at one end of its 22 in stair band,
    36 in guards on three sides) and a flight rising behind its front guard to the box's top; `b` is `a`
    reflected, so a stack switches back.
  - `top_a`, `top_b`: the top landing alone. `drop`: the drop ladder.
  - The coplanar census reads it clean over 1,968 sizes; its three corners build at 48, 1,092 and 1,464 tris.
- **Deli Counter 0.220.0 (827038a4): where it stands** (`patches/patch_dc_fire_escape.py`, `dc_fire_escape/`).
  - On every mid-rise Empty of six storeys or fewer that is no corner block -- `gs_midrise_a`, `_b`, `_g`, `_h`,
    `_i`. Six storeys (`WALKUP_STOREYS`) is CHOSEN: the height a walk-up stops at before a building takes a lift.
  - On the front, centred on the end window column farther from the front door, at most 2.8 m wide, 1.2 m out.
  - A flight bay a storey from the second, the top landing whichever way the last flight comes up, and the drop
    under the lowest hatch, its foot 2.2 m over the ground floor.
  - Each storey is a `prop` slot in `metal_painted`, with no collider: the lowest landing stands a storey up, and
    Level Factory reads an Empty's street edge off its colliders.

## Before the cold run: the form, in Blender

`stack_frame.py` builds Zoo's forms with Zoo's own `prim_mesh`, one storey a box, as Deli Counter stands them on a
five-storey walk-up. Workbench, object colour: the form, not the shipped look.

- `stack_street.png`: from the far curb, 1.7 m up.
- `stack_near.png`: 3 m out, under the drop.

## Proven: cold run 9303 (`docs/cold_runs/cold_9303/`)

urban_row_001, seed_9104 named against 9302's; Zoo 1.110.0 and Deli Counter 0.220.0 the only change.

- **0 interventions.** Findings 109 -> 109.
- **What stood:** four walk-up designs, six blocks -- `gs_midrise_i` three times, `_a`, `_h` and `_b` -- and 28
  storey instances (4, 5, 5 and 6 a design). The package gained 16 GLBs, four a design (two flights, a top and
  the drop; flights of one width repeat).
- **The light bake:** 616 -> 632 models, the 16; lightmap users 3,147 -> 3,175, the 28.
- **The fights:** 0 of 32 summary fields moved on each of the three candidates, every grade as 9302's
  (`fight_fields_9303.out.txt`, from `docs/findings/urban_street/fight_fields.py urban_row_001 9302 9303`).

## Seen: `walkups_9303_sheet.png`

`walkup_stations.py` frames each walk-up from across the street (eye 1.7 m up on the far sidewalk, looking at the
block's front line 6 m up), for `tools/look_shots.py`. Blue hour, the package's own lighting.

- **Where a street lamp lights the front,** the stacks read as fire escapes: landings with pickets, the flights
  switching back between them, the drop under the lowest landing (the zoom, three stacks at twice the size).
- **Where none does,** black steel on dark brick nearly disappears.
- **Two stations stood under a street tree** (`walkup_0`, `walkup_5`, both `gs_midrise_i` end-on at the street's
  ends): its crown from below is a flat slab across the frame's top. Seen in passing; the crowns are roadmap 216's.

## Priced (`price/`)

`docs/findings/horizon_glow/price_glow.py`: 9302's package twice as the control, 9303's between them, Level
Factory's fixed stations, 53 headings. GL Compatibility on the walker's machine. No game was running, but the
Battle.net launcher was.

- **The controls agreed on every heading's draws,** and their p95 frame time differed by a median of 0.38 ms.
  That floor is wider than the 0.03 to 0.11 ms of the urban street's earlier prices.
- **Draws: +3.3 a heading on the mean, +26 at the worst, -2 at the least.**
  - 29 headings gained 1 to 26.
  - The worst was the level's busiest heading: `player_start_19` at 90 degrees went 2,550 -> 2,576, with
    nearly all 28 storeys in view.
  - 12 headings lost 1 or 2 draws, each with the same count of objects and 1,100 to 6,148 primitives, the
    controls agreeing to the object.
  - Not isolated: the occluders are the same set (`occluders.json` differs only in counting 28 more nodes
    "other"). Besides the new files, only the walk-ups' dressing, bases and scenes, the bake and the records
    moved (`package_9302_9303.out.txt`). The dressing is the finding below.
- **Frame time: -0.09 ms at the median heading,** inside the floor; +1.70 ms at the worst, where the controls'
  own worst were +0.94 and +1.33.
- **Memory after the warm-up:** textures +0.1 MiB; buffers -3.1 MiB and video -3.0, buffers being the figure
  that is not steady from run to run (`docs/findings/texture_memory/`).

**What the merge would buy:** one draw a walk-up in view, where it is four to six now (the refutation below).

## Refuted: "the per-side merge carries it"

The proposal's plan said Level Factory needed nothing new: "The per-side merge carries it", one more draw a
front. **It does not.** `merge_empties.gd` takes apart only slot children whose names give a side --
`ext_<storey>_<side>_*`, `parapet_<side>_*`, `roof_*`, `stoop_*` -- and `fire_escape_<storey>` and
`fire_escape_drop` give none. In 9303's package, `lot/gs_midrise_a/site.tscn` stands its five as instances of
their GLBs beside the merged sides, so each storey draws on its own: four to six a walk-up, 28 on the picked
candidate. Every storey and the drop wear one material (`M_Skin_metal_painted_delco_1997_0f0f11`, read off the
four GLBs' glTF JSON), so merged they would be one more mesh a front. Level Factory 0.196.0 met the same with the
rowhome's stoop.

## Merged: Level Factory 0.209.0 (3ffe5c6), cold run 9304

`_side` gives a `fire_escape_*` slot the front's side, S, as 0.196.0 did the stoop
(`patches/patch_lf_merge_fire_escape.py` and `lf_merge_fire_escape/`). A test reads Deli Counter's schema, whose
`fire_escape_stack` must name the front alone, so a back stack cannot be merged into the front's mesh unseen.

- **Before shipping, on a mirror of 9303's package** (`merge_fire_escape.sh`, `merge_fire_escape.out.txt`):
  - 0.208.0's script, the control, takes nothing from the four walk-ups;
  - 0.209.0's takes each one's 5, 6, 5 and 4 storey meshes and makes one merged mesh of them, with no collider to
    copy;
  - and takes nothing from the six other Empties.
- **Both new tests fail where they should** (`patches/lf_merge_fire_escape/prove_tests.out.txt`): the rule test
  against 0.208.0's script, the schema test against a Deli Counter naming a second side or none.
- **Cold run 9304** (0 interventions, seed_9104 named against 9303):
  - each walk-up's front carries five merged meshes and no storey instance; gs_midrise_c, the control, four;
  - lightmap users 3,175 -> 3,153;
  - 0 of 32 fields moved on any candidate (`fight_fields_9304.out.txt`).
- **Priced** against 9303 (`price_9304/`), 53 headings, 9303 the control twice: draws -3.7 a heading on the mean,
  -24 at the most, none gained; p95 inside a 0.11 ms floor; memory flat.
- **Against 9302, with no fire escape** (`draws_9302_9304.out.txt`): +2 draws at the worst heading and -0.4 on the
  mean, where unmerged it was +26 and +3.3.
  - Draw counts are exact and comparable across prices: 9303, measured in both, reads the same at all 53 headings.
  - The headings that read below 9302 (to -4) are where Patina moved the front's dressing (below).
- **Every differing file attributed** (`package_9303_9304.out.txt`, `per_save_ids_9303_9304.out.txt`). Found there:
  289 of the package's 612 GLBs, 9.2 MB with their import files, are named by no scene, and 315 of the bake's 632
  model imports are files no scene names (`unreferenced_glbs_9304.out.txt`; roadmap 249).
  - Most are the modules the Empties were merged from, this stack's among them.
  - A module checked by name appears only in `light_bake.json` and `portable_resource_manifest.json`.

## Found: the front's dressing moved onto the stack, and onto the stoop and the awning before it

Attributing the package's differing files (`package_9302_9303.out.txt`) found every walk-up's dressing GLB
smaller: gs_midrise_a 22,088 -> 21,252 triangles, its eight cover meshes the same. Patina's dressing job for
gs_midrise_a, the two runs read side by side:

- **Its anchors on the front collapsed:** roofline 12 -> 1, ground edge 8 -> 1, wall base 4 -> 1. The other three
  faces were untouched.
- **The one front anchor of each kind stands at y -8.842,** the front face of the stack's greybox boxes (centre
  -8.242, 1.2 m deep). The roofline anchor stands at z 13.47, the top landing box's top. The wall stands at -7.5.
- **So Patina ordered a coping strip at the top landing's top, and a base course and a curb on the sidewalk,**
  all 1.34 m off the wall, while the front lost its coping, base course and curbs. The same on all five walk-ups
  (gs_midrise_g's job, run though no candidate's scene stands it, too).

**Why**, read in Patina 0.30.0's `surfaces.classify`: a vertical face is an exterior wall when its centroid stands
within 0.25 m of the visual AABB, the box round every visual mesh in the shell. Deli Counter greyboxes each
fire escape storey as a visual box in the shell GLB Patina reads, so the box moved the front out 1.34 m. Then the
wall was not on the boundary any more, and the stack's faces were. The anchor pass reads only exterior-wall faces.

**It is older than the fire escape.** Anything Deli Counter stands proud of a wall does it:
- **The awning** (Deli Counter 0.219.0, cold run 9297 on): every corner block's anchors reach y -8.842, the
  awning box's face, in 9302 as in 9303.
- **The rowhome's stoop** (Deli Counter 0.211.0, cold run 9271 on): `gs_empty_rowhome_a`'s front anchors stood at
  y -6.15 in cold runs 9258, 9263 and 9270 (ground edge 3, roofline 4, wall base 2). From 9271 there is one of
  each, at -7.61, the bottom tread's face.
- **The control:** `gs_midrise_c`, which stands neither, reads +-7.65 in both runs.

Patina already knows a prop is not structure: it reads the shell's `slots.json` before it classifies, its
`_ROLE_MAP` reads a `prop` slot as trim ("props read as detail/trim for tinting purposes"), and each mesh is named
by its node, which Deli Counter names by its `slot_id`. `classify` never asks. Dropping the props from the box
alone would not do: the test accepts any face standing BEYOND the boundary, so the stack's face would still read
as a wall. Filed as roadmap 248.

## Instruments

- `walkup_stations.py <N> <mission> <seed>`: the stations, read off the candidate's site spec and Deli Counter's
  specs.
- `stack_frame.py`: the Blender frames above.
- The price: `docs/findings/horizon_glow/price_glow.py <control copy> <subject copy> price/`, 9302's package the
  control, 9303's the subject.
- `patches/lf_standing_lot/package_trim.py <9302 package> <9303 package>`: every file either carries, the bake's
  imports and users (`package_9302_9303.out.txt`); `per_save_ids.py` beside it for the scenes Godot saves
  (`per_save_ids_9302_9303.out.txt`).
- `merge_fire_escape.sh`: Level Factory 0.209.0's merge rule on a mirror of 9303's package, 0.208.0's script the
  control.
- `draws_across_prices.py`: draws per heading for 9302, 9303 and 9304 read across the two prices, after checking
  that 9303, measured in both, reads the same.
- `unreferenced_glbs.py <package>`: the GLBs no scene or resource names, and the bake imports among them (roadmap
  249). Named by no scene is not unused: it says where to look.

## Open for the walker

- Front or back: the street sees the front; the walker's photo shows a light well.
- Which buildings: six storeys or fewer and no corner block; whether a corner block takes one on its side.
- The steel's colour: black, as the photo; Philadelphia's are often black, sometimes rust or silver.
- At night it shows only under a lamp.
