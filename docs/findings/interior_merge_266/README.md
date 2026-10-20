# Enterable buildings' static modules merged per room cell and material (roadmap 266), 2026-10-20: prototyped, priced, shipped

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

## Shipped: Level Factory 0.223.0 (4174d64) and 0.224.0 (f754562)

0.223.0 is v3 in the export (`packages/exporting/merge_buildings.py`, `assets/godot/merge_buildings.gd`): after the
Empties' merge and before the light bake, rooms taken from Lot's site record into each building's frame through the
inverse of its node's transform, the module GLBs no file names dropped after it, on by default
(`ExportProfile.merge_buildings`; `export --no-merge-buildings` ships one module a slot). 0.224.0 splits a lit face
that is not a fixture's (`M_*_Face`: a sign, a screen) into a mesh of its own per instance, `LitR_<n>`, where it
stood, and merges the rest of its module; a fixture (a lens or a diffuser) and any ShaderMaterial module stay whole.
The records: `patches/patch_lf_merge_buildings.py`, `patches/lf_merge_buildings/`, `patches/patch_lf_lit_face_split.py`,
`patches/lf_lit_face_split/`.

Four prices, each against two controls priced on the same bytes, 53 station-headings:

| what | package | draws, all headings (a heading) | p95, merged minus the controls' mean (median) | the controls' floor | worst heading | over the 8-light cap, paired | video memory |
|---|---|---|---|---|---|---|---|
| 0.223.0's path on 9347's copies (`price_9347_production.out.txt`) | 9347, re-baked | 38,954 -> 34,590 (-82.3) | -0.249 ms (-0.144) | 0.097 | 10.05 / 9.88 -> 9.10 ms | 9 -> 9 | 126.3 / 130.4 -> 134.7 MiB |
| cold run 9349's package, twice (`docs/cold_runs/cold_9349/NOTES.md`) | 9349 against itself exported `--no-merge-buildings` | 38,938 -> 34,531 / 34,439 (-83.2 / -84.9) | -0.181 / +0.156 ms (-0.102 / +0.054) | 0.131 | 9.95 / 10.33 -> 9.13 / 9.96 ms | 9 -> 9 | 130.5 -> 134.7 MiB |
| **0.224.0's first cut, REFUSED** (`price_9349_lit_a.out.txt`, `_b`) | 9349, re-merged and re-baked | 38,938 -> 33,953 / 33,826 (-94.1 / -96.5) | -0.310 / -0.324 ms (-0.220 / -0.193) | 0.131 | -> 9.06 / 8.96 ms | **9 -> 11** | -> 130.2 / 134.3 MiB |
| 0.224.0 as shipped (`price_9349_0224_a.out.txt`, `_b`) | 9349, re-merged and re-baked | 38,938 -> 34,439 / 34,623 (-84.9 / -81.4) | -0.242 / -0.183 ms (-0.167 / -0.162) | 0.131 | -> 9.62 / 9.13 ms | 9 -> 9 | -> 134.5 MiB |

- **The draws fall by 81 to 85 a heading, 11 %, 418 to 420 at the most, every time it was measured.** The two
  passes of one package draw up to 184 apart in all: the harness's own two passes at a heading drew different
  counts at 0 to 4 headings a run.
- **The frame time is a smaller and noisier gain on this machine.** Three of the four merged runs on 9349 read
  0.18 to 0.32 ms a heading under the controls, beyond their 0.131 floor; one read 0.156 over. At about 4 ms a
  frame on this desktop GPU submission is not what the frame waits on, and the level's worst heading stays under
  10 ms either way. The merge is bought for the low-end target the packages ship for (GL Compatibility), and
  nothing here measures that machine.
- **0.224.0's first cut merged the fixtures' housings too**, keeping only their lit faces apart. It was the fastest
  arm on 9349, and it was refused by the light cap: two room cells' merged meshes, `MergedR_335` and `MergedR_336`,
  each paired 10 lights, and the meshes over the cap went 9 -> 11. CLAUDE.md lists "more than
  `max_lights_per_object` (8) lights reaching one mesh" among the shapes refused on cost; 10 more draws a heading do
  not buy two housings that the ninth and tenth lamp would not light.
- **0.224.0 as shipped changes nothing on this level, and is meant not to:** 9349 carries 6 lit faces in its
  buildings (deli_a03 4, office 2), and the 25 surfaces of the modules 0.223.0 left whole for them became 25 meshes
  (1,643 surfaces -> 789 meshes under 0.223.0, 1,662 -> 808 + 6 lit under 0.224.0; 2,953 mesh instances both). What
  it changes is a level with lit desk screens (Zoo 1.115.0, roadmap 148): each desk's screen a mesh of its own, the
  rest of the desk in its room cell's.
- **The look:** the prototype's frames, above. The export's own path is the prototype's v3; no frame of the
  shipped package is compared here.
- **The cost:** a 2048 x 1024 lightmap where the control's is 1024 x 1024, about 4 MiB of video memory.

## What is left

- The 6 m cell is MEASURED, not derived: it is what kept this level's light pairing at the control's. Another level's
  fixture spacing could want another, and the export would not say so; the perf census's paired count would.
- A light fixture stays whole (400 of cold run 9339's building surfaces were fixtures). Merging housings needs a unit
  that pairs no more lights than one fixture does -- measured here as two 6 m cells at 10.
- The low-end target's frame time: no machine of that class has priced it.
- "The bake unchanged in look (lightmap compared user by user)" -- the item's own test -- cannot be asked of a merge:
  the users are what change, 3,524 -> 2,880, and the atlas repacks with them. The frames stand in for it.
