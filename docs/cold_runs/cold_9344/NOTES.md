# Cold run 9344 -- 0 interventions; precinct_yard_001, seed 9708 on Zoo 1.114.1: the floor hatch's frame reads yellow

**What it was for.** Cold run 9343 found the floor hatch's safety-yellow frame reading dark brown: the yellow rides in
the frame's vertex colours, and Zoo 1.114.0 painted the form with the slot's `metal`, which the theme resolves to
rusted street steel, not tintable. Zoo 1.114.1 (524461d, `patches/patch_zoo_hatch_paint.py`) paints the floor form
on `metal_painted`, a tintable neutral pack. This run is 9343's brief and seed again with that one change.

**Tools:** Deli Counter 0.236.1, Level Factory 0.220.0, Zoo 1.114.1, Lot 0.125.0, Lux 0.78.0. Staged from 9343, seed
9708 named.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`.
- **Shell:** 3 candidates; 0 blockers of 74 findings; seed_9708's lot 9343's.
- **Art:** 0 blockers of 104 findings.
- **Export:** exit 0; greybox 0 surfaces; the light bake as 9343's (379 models, 149 primitive meshes, 4,632 users).
- **Findings 104 -> 104** against 9343, no code moving.

**The module the package ships:** `lot/apartment_walkup_a01/art/zoo/prop_roof_hatch_delco_04_w166_d166_h3_ffloor.glb`
carries `M_Skin_metal_bare_delco_29292b` (the hinge) and `M_Skin_metal_painted_delco_ffffff` (frame and lid) --
9343's carried `M_Skin_metal_delco`. Two materials either way, so no draw moves.

## Frames (`hatch_9343_vs_9344.jpg`)

9343's stations, the level's light and the inspection light, 9343 left and 9344 right. From the office, side-on: the
frame round the opening is a thin yellow line where it was a dark brown one, and the standing lid is grey painted steel
where it was rust. From the garage bay the opening in the ceiling grid shows the lid's grey underside.

**Measured off the frames** (`hatch_frame_pixels.out.txt`): the frame's pixels found in 9344's inspection frame (the 40
most yellow in the box round the opening) and read at the same positions in each image, sRGB mean:

| light | 9343 (Zoo 1.114.0) | 9344 (Zoo 1.114.1) |
|---|---|---|
| inspection | (69, 35, 7) | (217, 156, 20) |
| the level's | (26, 9, 1) | (99, 46, 5) |

**For the walker:** the frame is Deli Counter's 3 cm (`hole_causes.HATCH_FRAME`) -- a line at 4 m, not a band. The
yellow now reads where the light reaches it; whether the opening wants a wider frame, or the lid a colour of its own,
is a look call.
