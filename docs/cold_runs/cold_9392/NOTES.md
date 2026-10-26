# Cold run 9392 -- 0 interventions; restaurant_row_001, seed 9003: iron hardware, the office stair's balustrades, bus stop zones

**What it was for.** The tool releases since 9391, from the walker's walk of cold run 9386
(`docs/findings/walk_2026-10-23_9386/`): the door hardware in the stoop railing's black iron, to merge with it (Zoo
1.127.0; 9391's +2 meshes an Empty); the office stairwell's balustrades and the raking rail along its upper flight
(Deli Counter 0.268.0 and 0.269.0, Zoo 1.128.0 and 1.129.0; finding 6); a census that counts the Empties (Lot 0.130.0;
finding 7); bus stop zones with no parking (Lot 0.131.0; finding 10).

**Every leg ran, `INTERVENTIONS: 0`.** The light check: FAIL 3, PASS 33, REPORT 1, as 9391. The art leg's exit 1 with
"Structural checks passed" is 9391's too. The walk copy `_runs/walk_9392_restaurant_row_001`; the workspace
`workspaces/cold-9392-ws`. The proofs are `after.sh`, every output beside it.

## Each change, in the package (against 9391)

- **The bus stop zones -- PROVEN.** `patches/lot_bus_zone/zone_check.py` on the two runs' `themed_site_assemble` outs
  (`zone_check.out.txt`): 9391 had 6 parked cars, 12 meters and 14 bay ticks inside 120 ft of a shelter; 9392 has 0, 0
  and 0 (cars 26 -> 20 across the site). The site's mesh total 3,090 -> 3,038: 83 covers changed, -53 meshes between
  them (`count_by_site_child_diff.out.txt`) -- the cars that left and the cover re-drawn around them; the only
  non-cover change is b0 +1, the office (its new rails).
- **The office stair -- PROVEN.** `stair_9391_vs_9392.webp`, three stations (`walker6` the walker's own view of finding
  6, `east6`, `above6`), each in the shipped light and the inspection light: the two wooden block walls around the
  well are iron balustrades, and a raking rail climbs the upper flight where the block stood. The seam's collider is
  kept and unseen (Deli Counter 0.269.0); a body still meets it.
- **The iron hardware -- NOT PROVEN, and the cause found.** The colour reached the package: `blocker_0`'s knob mesh
  0.8597 -> 0.2717 albedo (`meshes_blocker0_9391.out.txt`, `meshes_blocker0_9392.out.txt`). The merge did not: every
  Empty's mesh count is 9391's. `meshes_under.gd`, extended in steps, printed each merged mesh's material name and the
  rest of `merge_empties.gd`'s key: the street side carries `M_Skin_metal_painted_delco_1997_0f0f11` TWICE, one with
  `uv1_scale (0.833, 0.833, 0.833) triplanar true`, one with `(0.833, 0.833, 1.0) triplanar false`. `glb_iron.py` on
  the source GLBs (`glb_iron.out.txt`): the knob (`Doorway_LeafHardware`, in `doorway_...glb`) and the railing
  (`StoopRailing_Iron`, in `prop_stoop_railing_...glb`) are one material, one colour, both with UVs -- so the split is
  Level Factory's world skin, which projects every material of a `doorway_` kit module and leaves a `prop_` alone.
  Zoo 1.127.0's claim, "on a side with a stoop the knob is the railing's material and merges into its mesh", was true
  of the material and false of the mesh. Answered by **Level Factory 0.242.0** (3561b73,
  `patches/patch_lf_hardware_uvs.py`): a mesh named `*_LeafHardware` keeps its own UVs. Expected: -1 mesh on each
  Empty's street side; the back door keeps one. To be proven in the next run.
  On the way, a guess refuted and kept: that the railing had no UVs and so no density to project from. Both have
  TEXCOORD_0; the cause is the module prefix.
- **The census (Lot 0.130.0).** A measurement, not geometry: it changes what the land-use census reports, and its
  numbers are in the finding (`docs/findings/walk_2026-10-23_9386/landuse/`). Nothing to see in the walk copy.

## For the walker

The walk copy: `_runs/walk_9392_restaurant_row_001` -- the office's stairwell (finding 6) and the bus stop (finding 10).
