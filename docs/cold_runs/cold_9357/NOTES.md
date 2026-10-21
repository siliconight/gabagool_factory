# Cold run 9357 -- 0 interventions; restaurant_row_001, seed 9205: 9356's level with its ladders and markers

**What it was for.** Install test 11, certifying factory 1.41.0, made this level from the package -- 9356's, the
first level's brief at seed 9205 -- and its walk printed "walk bot: no ladder_area3d in scene; traversal vacuous":
Level Factory 0.223.0's buildings' merge removed every building's `Ladders` and `Markers` with the slots it took
apart (`docs/findings/merge_ladders_227/`). Level Factory 0.227.0 (2592e7a) keeps a slot holding what the merge
cannot carry whole. This run made the same level under it: the brief and batch staged from 9356's, byte for byte;
seed 9205 named.

**Tools:** Level Factory 0.227.0 (2592e7a); the rest as 9356 had them -- Deli Counter 0.241.0 (35d88455), Zoo 1.117.0
(48fdc71), Lot 0.126.0 (49dcf8d), Lux 0.79.0 (9132d32), Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline
0.6.0, Pixelcoat 0.62.0: the set factory 1.41.0 certifies.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0), read after `cold_run.py --end`; 8.5 min
(19:31:47 to 19:40:15). Shell 0 blockers of 74 findings; art 0 of 105; findings 105 -> 105 against 9356, which is
this level.

**The merge, against 9356's** (`compare_merge.py`, `compare_merge_9356_9357.out.txt`, both packages' own
`merge_buildings.json`): exactly the finding's prediction. `slots_merged` 868 -> 864 -- deli_a01 519 -> 517, the
parking garage 191 -> 190, the supermarket 158 -> 157 -- and `kept_carrying` names those four: deli_a01's `Markers`
and `Ladders`, and each other building's `Markers`. Meshes in, surfaces in, merged meshes, unwrapped, colliders and
lit meshes are 9356's in every building (1,384 / 1,587 / 781 / 789 / 829 / 8). The package's `lot/deli_a01/site.tscn`
carries 2 nodes in `ladder_area3d` and 14 in `dc_marker`, the garage's 8 markers and the supermarket's 7 -- 9356's
carried none -- the composed scenes' counts exactly.

**The export, line by line against 9356's** (`export.log`; the bake's seconds and the workspace's name set aside),
two lines differ, both attributed:
- the buildings' merge line, as above, now ending "4 slot(s) kept whole, holding what a merge cannot carry";
- "43 handoff node path(s) named nothing in the package" -> 40: `handoff_bindings.json`'s `gameplay_anchors.json`
  list loses `lot:b0/DEFENDER_SPAWN`, `lot:b1/DEFENDER_SPAWN` and `lot:b1/COVER_LOW` -- Lot's anchors that name
  Deli Counter marker nodes, which the merge had removed, and which now resolve. Its 31 others name no node by
  that name (`lot:COL00` where the garage's marker is `COVER_HIGH_COL00`) and move in both runs; not this change's
  (whether they resolved before 0.223.0 was not read).

Everything else is 9356's: the drop-edge gate (13 unguarded, 0 undeclared indoors), the closure (ok, 83 resources,
a package of 2,758 files), 0 greybox, the light bake's 2,775 users.

Not run here: the walk's self-check (the cold drive's walk step builds the walk copy without it -- roadmap 272).
Install test 12 walked this level from the package: both of deli_a01's ladders climbed, to 6.6 and 3.3 m, and five
shot stations framed where install test 11 framed one (`docs/findings/stranger_install/install_test_12/walk.txt`).
