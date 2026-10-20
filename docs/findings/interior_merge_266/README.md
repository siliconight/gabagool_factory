# Enterable buildings' static modules merged per room cell and material (roadmap 266), 2026-10-20: prototyped and priced

**What was asked.** Roadmap 266 (from `docs/findings/multimesh_audit/`): the buildings hold 2,576 of a level's 3,798
surfaces, MultiMesh is not the lever for them -- they are baked, and a MultiMesh is one culling object -- and merging
is, per room and material, as the Empties merge per side (Level Factory 0.143.0) and the covers per side per material
(Zoo 1.68.0). "What would close it: a merge pass priced the way the cover merge was -- draws and frame time at stations
inside the merged rooms, before and after, with two controls -- the bake unchanged in look, and the walker told what
it cost and bought." This is that price, on a prototype, before anything ships. It serves runtime performance, the
walker's ask of 2026-10-20 ("more performant at runtime"), not interventions-per-level.

**What was read.** Cold run 9347's package (restaurant_row_001: deli_a03, office, pharmacy_a01 and twelve Empties;
Level Factory 0.222.0, Deli Counter 0.237.0), always on copies under `_runs/`, never the shipped folder.

## The census (`merge_census.gd`; `census_9347.out.txt`, `census_9347.json`)

Each building's composed scene, `lot/<id>/site.tscn`, sorted into what a merge must not touch and what it can:

| building | static | lit fixtures | collision base | interactive | openings | covers |
|---|---|---|---|---|---|---|
| deli_a03 | 1,047 | 264 | 218 | 32 | 24 | 8 |
| office | 438 | 142 | 143 | 8 | 18 | 8 |
| pharmacy_a01 | 156 | 62 | 20 | 9 | 4 | 8 |

Left alone, and why: a slot carrying `interactive_id` (a door, a breachable wall: its states swap), a `*_open<n>`
slot (a window's pane may be glass, sorted per mesh), a module wearing a Lux lit face (`M_*_Lens`, `_Diffuser`,
`_Face`: Lux binds them by material), any subtree with an AnimationPlayer or a script, the `GreyboxBase` (its slabs
are tiled to the light budget on purpose, roadmap 54) and the covers (merged per side since roadmap 180).

**REFUTED, kept** (`census_9347_refuted.out.txt`): the first census counted 240, 105 and 68 merge keys. It read every
slot's transform straight after `add_child`, inside `_initialize`, and got the identity, so every piece named for no
wall or room fell on one storey. The prototype, which waits a frame, merged the same surfaces into 271, 134 and 68;
the census, made to wait a frame, now agrees with it to the key.

## The prototype (`merge_buildings_proto.gd`, `proto_ab.py`)

`merge_empties.gd` with the census's classes: every static slot is taken apart -- its StaticBody3D colliders copied
out whole under `KitCollision` in the root's frame -- and its surfaces appended to one group per (unit, material,
uv1 scale and triplanar flags, surface format); each group one ArrayMesh, unwrapped for the lightmap at 0.2 m, as the
Empties' are. `proto_ab.py` makes two arms through identical steps -- copy, un-bake (`tools/lux_rebake.unbake`),
import, and Level Factory's own `light_bake.bake()` -- and only the merged arm runs the merge between import and bake.

What the UNIT is decided everything, and the three versions are kept with their prices (`price_table.py`;
`price_9347_v1.out.txt`, `_v2`, `_v3`; v3's merge report with its keys, `merge_v3_9347.json`):

| version | units | 1,641 static surfaces became | draws a heading (median, most) | p95 a heading | meshes over the 8-light cap, paired | lightmap |
|---|---|---|---|---|---|---|
| control (twice) | -- | -- | -- | the two differ by 0.097 ms (median 0.040, most 1.338): the floor | 9 | 1024 x 1024 |
| v1 | wall side a storey, partition run, furnished room; **anything else one unit a storey** | 473 | -87.6 (-40, -477) | -0.219 ms (median -0.046) | **19** | 1024 x 1024 |
| v2 | as v1, but anything else in **the room it stands in** (Deli Counter's rooms) | 535 | -83.7 (-39, -446) | -0.257 ms (median -0.098) | **11** | 1024 x 1024 |
| **v3** | as v2, every room unit **cut into 6 m cells** of the plan, the parapet into its four sides | **799** | **-79.6 (-50, -420)** | **-0.209 ms (median -0.103)** | **9** | **2048 x 1024** |

Over 53 station-headings the controls drew 38,954 both times; v3 drew 34,735. The level's worst heading
(attacker_spawn_5, yaw 90) went from 10.05 and 9.88 ms p95 at 2,115 draws to 9.14 ms at 1,799. Mesh instances
3,596 -> 2,963; lightmap users 3,523 -> 2,890; the bake 33.2 s -> 30.9 s.

- **v1 and v2 were refused by the light cap, not by the draws.** A merged mesh is one object to Godot's per-object
  light limit (8 on GL Compatibility, `max_lights_per_object`); a storey-wide unit -- v1's -- paired up to 14 lights,
  and so did one 15 x 20 m room's shelving in v2 (market_aisles' metal) and the parapet's ring (10). v3's 9 meshes
  over the cap are the control's 9, the roof the same mesh under a new name (`MergedB_35`, 10 lights, where the
  control names `roof_footprint`, 10). CLAUDE.md's refused shapes include "more than `max_lights_per_object` (8)
  lights reaching one mesh"; v3 adds none.
- **The look:** frames of both arms from the same eight interior cameras and the eight exterior ones
  (`look_shots.py`, the cameras fixed from the control's derived interiors -- derived per arm they moved, because the
  derivation reads meshes the merge renames): mean |difference| 1.1 to 5.6 on 13 of the 16, and 9.6 to 11.2 with
  3.6 to 5.7 % of pixels past 40 in three concrete rooms whose bake is speckled in both arms -- the lightmap's own
  noise, repacked. Geometry, doors, furniture and stairs read the same (`ab_fixed_v1.jpg`, v1; v3 measured the same way).
- **The cost:** v3's lightmap came out 2048 x 1024 where the control's is 1024 x 1024; the video memory read 134.7
  MiB against the controls' 126.3 and 130.4 (they differ by 4.1 themselves). v1 and v2 packed into 1024 x 1024; v3's
  cells are more, smaller charts. Not attributed further.

## What is left

- Shipping it: a Level Factory export step beside the Empties' merge (after the occluder bake, before the light
  bake), with the module drop that follows it, a fixture test and a package price.
- The 6 m cell is MEASURED, not derived: it is what kept this level's light pairing at the control's. Another level's
  fixture spacing could want another.
- Lit fixtures (468 surfaces here) and the slabs stay separate; whether their non-emissive parts could merge is not
  asked here.
