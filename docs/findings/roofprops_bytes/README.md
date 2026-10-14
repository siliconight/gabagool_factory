# The roof props' bytes from run to run (roadmap 247)

**The question.** Cold runs 9294, 9295 and 9296 each built
`lot/pharmacy_a01/art/roofprops/pharmacy_a01_roofprops.glb` with the same command, `--seed` included. 9294's and
9296's are byte-identical, and 9295's is not. Roadmap 181 records the scatter as "deterministic per manifest and
seed". What differs?

**Measured** (`glb_order.py`, `glb_order.out.txt`; 9294 against 9295, and 9294 against 9296 as the control):
- **The glTF JSON is identical.** 2,569 of the 61,836 binary bytes differ, and all of them belong to one mesh:
  `SatelliteDish_metal_delco_1997`, the merged satellite dish.
  - Its positions, normals, UVs, colours and indices differ: 180 of 1,071 position values moved, the largest by
    0.75 m.
  - The mesh is the same set of 376 triangles, each with the same winding.
  - The 64 vertices whose positions differ lie between indices 79 and 160 of 357, in eight runs, and that span is
    a permutation of the same positions.
- **The control:** 9294 against 9296 differ in 0 bytes.

**What that says, argued here and not measured:** the dish is the same geometry with its vertices in a different
order, inside one span of the merged mesh rather than a whole part swapped. The merge orders its parts by name
(`zoo_keeper/core/partnames.group_parts`: "Sorted, not hash- or link-ordered"), so the order more likely changes
inside one part's build.

**Not traced:** which step reorders those vertices, and why one run in three.

**Why it matters, recorded and not fixed:** nothing a player sees moves. But a byte that changes without a cause
defeats any comparison of packages by hash: cold run 9296's NOTES had to read both builds to set this one aside.

## Lux's applied scene is not byte-stable either (found with cold run 9298)

**Measured** (`lux_energy_pairs.py`, `lux_energy_pairs.out.txt`; urban_row_001's packaged
`presentation/lux.applied.tscn`, 9295 to 9298, consecutive pairs, with node `unique_id`s and Godot's drawn
resource ids masked):
- The same ten lights' `light_energy` differ in every pair, by about one part in 10,000:
  - seven fluoros under `LuxFixtureLights`, each a `Spawned_pendant_*`;
  - `site_pole_43`, `site_pole_53` and `site_lamp_78` under `LuxClub`.
- `Spawned_fluorescent_038_dup2` reads 2.618 in 9295, 9296 and 9298, and 3.7 in 9297.
- Nothing else in the scene differs: 10 or 11 of its 9,581 lines a pair.

**Not traced:** what sets those energies, and why they move. The level's Lux carries failing and cycling rigs
(`light_bake.json`: 27 live in 9298), and whether these eleven are among them is not checked.

## Traced and fixed: Zoo 1.109.0 (2026-10-14)

**Reproduced from one command.** `../grader_speed/zoo_repro_probe.py --jobs` replayed cold run 9298's
`zoo_roof_props_build.pharmacy_a01` six times on Zoo 1.108.0: four GLBs, every difference in the merged dish, one of
the four 9294's and 9296's bytes (`replay6_1108.out.txt`). Over all of 9298's 40 Zoo jobs, three replays each, 39
built the same bytes every time and the pharmacy's roof props did not (`census_1108.out.txt`).

**Which step** (`stage_digest.py`, driven by `stage_runs.py`: the job's own command under Blender, Zoo's build steps
wrapped in memory, a digest of each dish part's mesh printed after each step; six fresh processes,
`stage_runs_1108.out.txt`):
- The pole, the arm and the feed are one mesh at every step.
- The bowl (`add_ellipsoid`, a `create_uvsphere`) reaches the bevel with its faces in an order that changes from
  process to process -- five orders in six -- the same faces, each from the same corner.
- It leaves the bevel with the same faces starting at other corners: their corner tuples sorted differ four ways,
  and rotated to their lowest vertex they agree.
- `bm_to_object`'s sort by corners (1.103.0) then orders them four ways, and the merge carries that into the dish's
  vertex order.

**Refuted and kept: "one build's normals are others, by up to 1.67".** `zoo_repro_probe.how` sorts each array's rows
alone; a float wobbling by 1e-4 can swap two near-equal rows and pair different vertices. Paired by position and UV
(`normal_shift.py`), the 1.108.0 variants' normals lie within 0.0044 degrees. Bytes, not shading. The stage digest's
normals, rounded to 1e-4, differed in one or two runs of six for the same reason.

**Why the bevel's input cannot be fixed** (`shuffle_bevel.py`, `shuffle_bevel.out.txt`; one process, the bowl's
faces laid in six shuffled orders, each bevelled through `bm_to_object`; two processes):
- bevelled as laid: six meshes, then four;
- the faces sorted back into `in_one_order`'s order first: six, then six. The bevel's choice of a start moves with
  more than the faces' order;
- restarted at their lowest vertex just after the bevel: one mesh, the same one in both processes.
- A first version of this check scaled the sphere's vertices by hand, left its face normals stale, and never bevelled
  (62 vertices, 72 faces, the sphere as made): its "one way" said nothing. The counts are printed for that reason.

**Zoo 1.109.0** (c2edb80; `patches/patch_zoo_bevel_restart.py`): `bevel_edges` restarts every face it leaves at its
lowest vertex, and `start_at_lowest` carries every loop layer's corner data with its corners where it refused a
bmesh carrying any -- a turning part reaches the bevel carrying its UVMap and Pivot layers.
- **Replays:** 40 of 40 of 9298's Zoo jobs the same bytes three times over (`census_1109.out.txt`); the pharmacy's
  roof props one GLB in six (`replay6_1109.out.txt`); the stage digest one mesh at every step after the bevel
  (`stage_runs_1109.out.txt`).
- **What it moves, once** (`churn.py`, `churn_1109.out.txt`, with a 1.108.0 replay as the control,
  `churn_1108_control.out.txt`): 1,138 of 1,866 files in all 40 jobs, where the control moved 1. Positions, colours
  and UVs are the same rows reordered; the triangles are other; the normals lie within 0.013 degrees over 797,941
  paired vertices (`normal_shift_1109.out.txt`; the control 0). Not measured: how far a quad split across its other
  diagonal moves a surface that is not flat.

**Found on the way, filed apart:** Zoo's `tests/test_club_bpy.py::test_bpy_what_shipped_before_is_what_main_built`
fails all five of its golden digests on 1.108.0 as on 1.109.0. It runs only inside Blender, so the suite never ran
it.

**Cold runs 9299 and 9300** (`docs/cold_runs/cold_9299/`, `cold_9300/`; urban_row_001, seed_9104 named, 0
interventions each):
- 9299 against 9298: nothing the graders read moved (`fight_fields_9299.out.txt`), and 1,078 files differ -- 364 of
  the package's 596 GLBs and what follows from them -- once (`package_9298_9299.out.txt`).
- 9300 against 9299, the same command again: 22 of 3,283 files differ (`package_9299_9300.out.txt`). Every GLB and
  the lightmap are the same bytes.

**What remains of 247:** two runs of one command still disagree on
- Godot's per-save ids, node `unique_id`s and drawn resource ids, in the scenes the export saves (`bake.tscn`, the
  standing Empties' `site.tscn`, Lux's applied scene): 0 lines once masked (`per_save_ids_9299_9300.out.txt`);
- Lux's eleven light energies in `presentation/lux.applied.tscn` (`lux_energy_pairs_9297_9300.out.txt`);
- the metadata that records times, paths and the hashes of the above (`metadata_9299_9300.out.txt`).

## Lux's light energies, traced and fixed: Lux 0.77.0 and Level Factory 0.208.0 (2026-10-14)

**Where they are written.** The eleven energies are already apart in the `lux_apply` job's own output, before the
light bake touches the scene: 9299's and 9300's `jobs/urban_row_001.lux_apply/1/out/lux.applied.tscn` differ in the
same 11 lines, at the same values, as their packages.

**Why** (read off the source): the job runs `run_lux_apply.gd` as a headless `SceneTree` script, which awaits seven
frames before it packs the scene. Lux's fluorescent and streetlight rigs animate a failing or flickering lamp from
their own clocks (`_fail_t`, `_flicker_phase`) on every frame they process, by the frame's wall-clock `delta`, and
the stage light cycles its colours on `_t`. `PackedScene.pack` saves the lamps wherever the clocks had reached.

**The fix, in two places:**
- **Lux 0.77.0** (4ce4c85; `patches/patch_lux_rig_rest.py`): the three rigs answer `rest()`, every lamp back at what
  its rebuild gave it, a failing lens back at its own glow, every clock at zero. `tools/rig_rest_selftest.gd`, 24
  checks, fails on 0.76.1 on its four `rest()` checks while its driven cases pass there.
- **Level Factory 0.208.0** (b8fe4f7; `patches/patch_lf_rigs_rest.py`): `run_lux_apply.gd` rests every rig in
  `lux_light_rig` after the last frame it awaits and before it packs, and logs how many.

**Replayed before it shipped** (`lux_apply_replay.out.txt`): 9300's own `lux_apply` job, from a copy of its staging
folder, twice as it ran and twice with both drafts.
- Unpatched, the two applied scenes are 10 lines apart once the per-save ids are masked; patched, 0, each run
  logging `[lux] 216 rig(s) at rest before the scene is packed`.
- Patched against unpatched, 12 lines move: the 10 lights that wandered, and **two poles, `site_pole_46` and
  `site_pole_76`, saved at 0.0 in every run** -- their failing cycle starts dark, so they never showed as run-to-run
  noise -- now at the energy their rebuild gives.
- **What a saved energy does at run time, read off the source, not measured:** a rig's `_rebuild` frees every lamp
  the scene saved and builds its own at load, from the rig.

**Cold runs 9301 and 9302** (`docs/cold_runs/cold_9301/`, `cold_9302/`; seed_9104 named, 0 interventions each, each
Lux apply logging 216 rigs at rest):
- 9301 against 9300 (`package_9300_9301.out.txt`, `lux_energy_pairs_9300_9301.out.txt`): 13 lights in the applied
  scene move to their rest values, poles 46 and 76 among them; Lux's three changed rig scripts and their `.gd.uid`
  files move with them; and the lightmap is 9300's byte for byte, though two poles now save at 34.12 where they saved
  at 0.0. Nothing the graders read moved.
- 9302 against 9301, the same command again (`package_9301_9302.out.txt`, `per_save_ids_9301_9302.out.txt`): 22 of
  3,283 files differ, and all 12 scenes Godot saves -- Lux's applied scene among them -- read 0 lines different once
  its per-save ids are masked.

**What remains of 247:** Godot's per-save ids -- node `unique_id`s and drawn resource ids -- in the 12 scenes the
pipeline has Godot save, and the metadata recording times, paths and the hashes of those.
