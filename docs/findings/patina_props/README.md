# A prop is not the building: Patina's bounds (roadmap 248)

Found attributing cold run 9303's package against 9302's (`docs/findings/fire_escape/README.md`, "Found"): every
walk-up's front coping, base course and curbs had moved onto its new fire escape's greybox boxes, 1.34 m off the
wall. Patina 0.30.0's `surfaces.classify` took the building's bounds from every visual mesh in the shell GLB, and
called a vertical face an exterior wall when it stood within 0.25 m of them. Deli Counter greyboxes every `prop` slot
as a visual box named by its `slot_id`, so anything it stands proud of a wall became the wall. The anchor pass reads
exterior-wall faces only, and the dressing is ordered off the anchors.

## What shipped: Patina 0.31.0 (2279f04)

`patches/patch_patina_props_not_walls.py` and `patina_props_not_walls/`.

- **`classify(..., props=)`:** the meshes named are left out of the bounds and never read as exterior wall or roof.
  Their faces keep the role their normals give, and a gameplay hint still wins.
- **Not trim.** `slots._ROLE_MAP` reads a prop as trim for tinting, but forcing that here would retint every prop in
  the library's 9,933 prop slots, nearly all indoors, for nothing this defect needs.
- **Not the bounds alone.** The exterior test accepts a face standing beyond the bound, so a prop left only out of
  the box would still read as wall.
- **`SlotManifest.prop_ids()`** names a slots.json's `prop` slots, and the CLI hands them to `classify`. A shell with
  no slots.json reads as before.
- **`tests/test_props_are_not_walls.py`:** fails on an archive of 0.30.0 (4 of its 5 synthetic checks; the fifth
  documents the defect and passes on both). On three real shells -- gs_midrise_a's fire escape, gs_cornershop_c's
  awning, gs_empty_rowhome_a's stoop -- the anchors with the props named equal the anchors with the props taken out
  of the scene, and unnamed they do not.

## Replayed over every shell (`replay.py`, `replay.out.txt`, `replay.out.json`)

Every Deli Counter shell with a slots.json (158) through the dressing job's own command -- read off all 31 job logs
of cold runs 9303 and 9285, which differ only in the shell and the output path -- in three arms: 0.30.0, 0.30.0
again (the control), and 0.31.0.

- **The control:** 474 runs, none failed, and 0.30.0 twice wrote every output of every shell byte for byte.
- **118 shells unchanged** in every output.
- **29 moved their dressing**, the one output a package carries (the Zoo adapter builds covers from
  `.patina.dressing.json`; nothing else reads the anchors sidecar):
  - the five walk-ups and the four corner blocks: front anchors from y -8.842, the fire escape's and the awning's
    box face, back to the wall at -7.65;
  - the twelve rowhome Empties: from -7.609, the stoop's bottom tread, back to -6.15;
  - seven gas stations: from the forecourt's canopy and pad, out to y -32.0, back to the building's +-11.15. The
    pad, canopy, columns and pumps are prop slots, so this is the same defect, older than the stoop;
  - twin_a01: from its porch's -9.1 back to -6.65.
- **11 moved only Patina's styled GLB**, which no package carries (the packaged greybox base comes from Deli
  Counter's own GLB through `presentation_compose`). Measured by `glb_only_roles.py` (`glb_only_roles.out.txt`):
  - seven enterable buildings, a rooftop unit's top no longer roof (2 faces each);
  - three parking garages, 12 columns' tops no longer roof (24 faces);
  - harbor_score, whose 58 slots are all props: its stair rails had stood over its roof, so 0.30.0 read no roof at
    all; 45 of its slabs, 98 faces, now read as roof.
- **No shell with a prop past its other slots went unmoved** (a rough plan test off the slots.json, rotation
  included).

## Proven in a package

**Cold run 9305** (`docs/cold_runs/cold_9305/`; urban_row_001, seed_9104 named against 9304, 0 interventions):
- **The dressing orders:** 9304 ordered 3 off the walls on each walk-up, 12 on gs_cornershop_c and 18 on
  gs_cornershop_d, under their awnings; 9305 orders none off any wall. gs_midrise_a's coping strips 37 -> 48, curbs
  24 -> 30, base courses 12 -> 14. gs_midrise_c, with no prop past its walls, 372 orders in both, kind for kind.
- **Nothing the graders read moved:** 0 of 32 fields on each candidate (`fight_fields_9305.out.txt`); findings
  109 -> 109; the bake's 632 models and 3,153 users as 9304's.
- **Priced** against 9304 at 53 headings (`price_9305/`): +2.0 draws a heading on the mean, +6 at the most, none
  fewer; p95 inside a 0.06 ms floor; +0.2 MiB video memory.
- **Seen** (`roofline_9304_9305.png`): the coping along the front parapets again, bare in 9304. A roofline is
  strips with gaps, not one coping: Patina stands an anchor every 2.5 m (`AnchorOptions.roofline_spacing`), each
  jittered by up to 0.375 m either way along the run (`(rng.random() - 0.5) * spacing * 0.3`), and Zoo builds each strip 2.0 m long (`dressing.strip_size`: span 2.0 m at
  the 0.6 size hint). That is how every face of every building has always read; it is for the walker's eye.
  - First written "a 0.6 m piece every 2.5 m", reading the anchor's size hint as the strip's length; Zoo scales
    the hint, and the strip is 2.0 m.
- **The corner blocks' storefronts** differ by 2 pixels from the corner stations. What had floated at the awning's
  box is not seen from a 1.7 m eye across the street, so the orders are their evidence.

**Cold run 9306** (`docs/cold_runs/cold_9306/`; restaurant_row_001, a strip, the pick automatic, 0 interventions):
all twelve rowhome Empties' anchors within y +-6.15, the walls, where from 9271 to 9302 each front had one of each
kind at -7.61, the stoop's tread; gs_empty_rowhome_a's counts the replay's exactly. The three candidates PASS 90 at
route 1.00, as in 9293, the last run of that brief; findings 112, as 9293's. Not priced: no package from this
toolchain without 0.31.0 exists.

**Cold run 9307** (`docs/cold_runs/cold_9307/`; gas_block_001, the pick automatic, 0 interventions), against 9281,
the same brief a day earlier on Patina 0.30.0, whose workspace survives:
- **gas_station_a02:** in 9281 every coping strip, base course and curb it ordered -- all 180 -- stood off the
  building, on the forecourt's canopy and pad edges, and the building carried none of its own. In 9307 none stands
  off it: coping 64, base courses 26 and curbs 47 on the building, and 2 conduit runs.
- **Its twelve rowhomes:** back from the stoop's -7.61 to the walls' -6.15.
- **landmark_hall_a02 and rail_station_a01** order kind for kind as in 9281.
- **The grades** exactly as 9281's on all three candidates (seed_9080 PASS 100, picked again); findings 105 -> 105.
- **Seen, not decided:** from the far side of the road and from 22 m up at midnight the frames differ only in the
  road's foreground, the lightmap's repack. The forecourt's change is for a walk.

## Instruments

- `replay.py [--workers N] [--only a,b] [--compare]`: the three arms under `_scratch/patina_replay/`, then the
  comparison. `--compare` reads the arms on disk.
- `glb_only_roles.py`: the meshes whose roles 0.31.0 changes on the shells that moved only the styled GLB.
