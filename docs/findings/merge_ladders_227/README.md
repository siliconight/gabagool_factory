# The buildings' merge removed every building's ladders and markers (Level Factory 0.227.0)

**How it was found.** Install test 11 (`docs/findings/stranger_install/`), certifying factory 1.41.0, made the first
level from the unzipped package with Deli Counter 0.241.0's ramp fix, and its walk printed "walk bot: no
ladder_area3d in scene; traversal vacuous". 1.40.0's install test 9 had climbed all four of its site's ladders. The
composed scene still carried them -- `presentation_compose`'s `lot/deli_a01/site.tscn` has `Ladders` with
`Ladder_ladder_0` and `_1`, Area3Ds in groups `ladder_area3d` and `dc_ladder`, which Level Factory's `walk_bot.gd` and
`player_walk.gd` find by group -- and the exported package's had none. Level Factory 0.223.0's buildings' merge
(`assets/godot/merge_buildings.gd`, roadmap 266) takes a slot apart -- its StaticBody3Ds copied out whole under
`KitCollision`, its meshes' surfaces into the merged meshes -- and then removes the slot. `Ladders` held nothing it
judged unmergeable, so it was taken apart, and its Area3Ds went with it.

## The census (`merge_drop_census.gd`, `run_census.py`)

What else does a merge remove that it does not carry? The census instantiates each placed building in an UNMERGED
package, waits a frame as the merge does, applies 0.226.2's `_mergeable` (copied verbatim), and sorts every node of
every slot that would be taken apart: CARRIED (a StaticBody3D and everything under it; any other MeshInstance3D) or
DROPPED (the rest). Dropped nodes are counted by exact class; any in a group not starting "_" or with metadata is
listed; bare empties below a slot's root are counted by name; carried meshes with a group or metadata are listed.
For two candidate rules it lists the slots each would keep whole and the surfaces they hold:

* rule A: a CollisionObject3D that is not a StaticBody3D, or a node in a group not starting "_";
* rule W: a dropped node whose class is not exactly Node3D, or that is in such a group or carries metadata.

**The inputs.** Two levels, six enterable buildings: cold run 9356's (the first level's brief at seed 9205 --
deli_a01, parking_garage, supermarket_a01) and 9355's (the cold runs' brief at seed 9003 -- deli_a03, the office,
pharmacy_a01). Each workspace was copied to `_scratch/2026-10-20_merge_census/` and exported there with
`--no-merge-buildings --no-bake-lights`, leaving the cold runs' own records untouched (their logs:
`export_unmerged_9356.out.txt`, `export_unmerged_9355.out.txt`; the copies were deleted after). The light bake's absence
changes the import settings and so the Empties' merge (285 merged meshes against the shipped package's 172 -- not
attributed further); it changes no node's class, group or metadata, which are all the census reads.

| building | slots | merged by 0.226.2 | dropped, by class | grouped or with metadata | bare empties | carried meshes, flagged |
|---|---:|---:|---|---|---|---:|
| deli_a01 (9356) | 568 | 519 | Area3D 2, CollisionShape3D 2, Node3D 629 | 2 ladders, 14 markers | 94 `ATT_*`, 2 `TopOfLadder` | 843, 0 |
| parking_garage (9356) | 213 | 191 | Node3D 222 | 8 markers | 23 `ATT_*` | 249, 0 |
| supermarket_a01 (9356) | 180 | 158 | Node3D 190 | 7 markers | 25 `ATT_*` | 292, 0 |
| deli_a03 (9355) | 565 | 523 | Area3D 2, CollisionShape3D 2, Node3D 635 | 2 ladders, 14 markers | 96 `ATT_*`, 2 `TopOfLadder` | 857, 0 |
| office (9355) | 287 | 265 | Node3D 321 | 8 markers, 1 `LuxEmit_payphone_hood` | 47 `ATT_*` | 463, 0 |
| pharmacy_a01 (9355) | 115 | 97 | Node3D 119 | 7 markers | 15 `ATT_*` | 156, 0 |
| **all six** | **1,928** | **1,753** | | **4 ladders, 58 markers, 1 Lux marker** | | **2,860, 0** |

(`census_9356_unmerged.out.txt`, `census_9356.json`, `census_9355_unmerged.out.txt`, `census_9355.json`.) The
markers are Deli Counter's (`portable_building._marker_nodes`, whose docstring says a recipient game finds them with
`get_tree().get_nodes_in_group('attacker_spawn')`): spawns, objectives, extraction, cover, camera sockets, patrol
points, a ladder's and a hatch's marks, each a Node3D with groups and `metadata/marker_type`. The `ATT_*` empties are
Zoo's attachment sockets (`zoo/README.md`, "Every asset exports named `ATT_*` markers"); no tool reads them from a
package -- grepped across Level Factory's runtime, Lux, Laser Tag, Patina, Lot and Deli Counter -- and they carry
only their names.

**The two rules part on one slot.** Both keep the 8 `Ladders` and `Markers` slots, which hold no mesh. Rule W also
keeps the office's `payphone_rcce455f7_5`, 2 surfaces: its `LuxEmit_payphone_hood` is a bare-classed Node3D whose
metadata is `extras`, Zoo's glTF extras as Godot imports them -- Lux's emitter payload. Level Factory's `lux_apply`
spawns the lamp from it at build time and saves the lamp (`run_lux_apply.gd`), so no package reads the marker today;
but Lux's own runtime contract is `LuxFixtureSpawner.spawn(level_root)` "once after the level loads", which REPLACES
the spawned lamps with fresh ones from the markers, and a game that calls it would find this lamp's marker gone.

**Chosen: rule W** (Level Factory 0.227.0's `_cannot_carry`): outside a StaticBody3D, a node that is neither a
MeshInstance3D nor a bare Node3D, or any node in a group not starting "_" or with metadata, keeps its slot whole. It
is the general one -- an unrecognised node keeps its slot rather than vanishing, the direction a merge can afford, at
draws and never at content -- and on these two levels it costs one payphone's 2 surfaces. It asks the meshes too,
which none of the 2,860 failed. **What the cheaper version would buy:** a marker copied out of its module as a
collider is, the module's surfaces left in the merge -- here, the payphone's 2 surfaces.

**First read, refuted by the second level, kept:** after 9356's census the rule's comment said everything else a
merge removed was bare Node3Ds. 9355's office found the payphone's Lux marker; the comment shipped saying so.

## Predicted for the cold run that proves it

The same level as 9356 under 0.227.0: `slots_merged` 868 -> 864 (each building's `Markers`, deli_a01's `Ladders`),
`kept_carrying` 4, every other count of the merge's report as 9356's -- surfaces, merged meshes, colliders, lit
meshes -- and the package's `lot/deli_a01/site.tscn` carrying `Ladder_ladder_0` and `_1` in `ladder_area3d` and the
three buildings' 29 markers in their groups.

**Proven** (Level Factory 0.227.0, 2592e7a). Cold run 9357 made that level at 0 interventions and its report read
exactly the prediction: `slots_merged` 868 -> 864, `kept_carrying` 4, every other count 9356's, and the package's
deli_a01 holding its 2 ladders and the three buildings their 29 markers (`docs/cold_runs/cold_9357/compare_merge.py`,
`compare_merge_9356_9357.out.txt`). Its export differed from 9356's in one more line, attributed there: three of Lot's
gameplay anchors that name Deli Counter markers resolve again. Install test 12 then walked it from a fresh unzip:
"walk bot [OK] Ladder_ladder_0: climbed to 6.6 m and stood up", `Ladder_ladder_1` to 3.3 m, and the shot bot's five
stations, a base and a top at each ladder (`docs/findings/stranger_install/install_test_12/walk.txt`).
