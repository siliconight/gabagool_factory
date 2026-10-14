# Cold run 9298 -- a package carries the buildings its scene stands (Level Factory 0.207.0)

**What it tested:** urban_row_001 (9297's brief unchanged) on Level Factory 0.207.0 (dff4b8c), whose export leaves
out a composed `lot/<id>/` package the assembly scene does not stand (`patches/patch_lf_standing_lot.py`).

**seed_9104 named** against 9297's. Lot 0.123.0, Deli Counter 0.219.0, Zoo 1.108.0, Laser Tag 0.32.0. Staged from
cold run 9297.

**Result: 0 interventions (journal 0, unattributed files 0). The package carries the thirteen `lot/` packages its
assembly stands and no others, and nothing else in it moved but what any two exports differ in.**

- **The export said what it left out** (`export.log`):
  `[export] 3 composed building(s) no scene stands, left out: gs_cornershop_a, gs_cornershop_b, gs_midrise_g`.
- **Measured against 9297's package** (`patches/lf_standing_lot/package_trim.py`, `package_trim.out.txt`; the
  instrument read 0 on 9297's package against itself, and saw the awning's 4 imports and 28 files on 9296's
  against 9297's):
  - `lot/` packages 16 -> 13, every one named by the assembly's `site.tscn`, none named and absent;
  - files 3,704 -> 3,283, the 421 fewer all the three packages' (150, 150 and 121);
  - bytes 210,695,443 -> 199,146,399: 11.4 MB, 5.4 % of the package. The changelog's 12.2 MB was `du`'s allocated
    size;
  - the light bake's model imports 711 -> 616, the 95 all the three packages' (34, 34 and 27);
  - lightmap users 3,147 -> 3,147: none of the left-out meshes had been lit;
  - the closure verdict clean on both, `package_file_count` 3,698 -> 3,277.
- **Every file both packages carry is byte-identical but 23, each attributed:**
  - 6 by timestamps and workspace paths: `LF_MANIFEST.json` (and the closure's fingerprint it repeats, which
    follows the file list), `LICENSES.json`, `build.lock.json` (Dispatch's mission spec names the workspace; its
    resource manifest differs only in the validation reports' hashes) and the three `validation/report.*`;
  - 5 by the trim itself, each by the three packages' share and nothing else: `light_bake.json` (95 imports, and
    its timings and log path), `export_closure.json` (rerooted refs 16 -> 13), `export_closure_scan.json` (its
    counts and fingerprint; `resource_count` 83 -> 77 is their three `site.tscn` and three `zoo_worldskin.gd`),
    `glb_reference_scan.json` (glbs 691 -> 596) and `portable_resource_manifest.json` (421 entries fewer, and the
    21 other files' hashes);
  - 11 by Godot's per-save ids alone: `bake.tscn` and the ten standing Empties' `site.tscn`, which the export's
    Empty merge re-saves; 0 lines differ once node `unique_id`s and drawn resource ids are masked
    (`patches/lf_standing_lot/per_save_ids.py`, `per_save_ids.out.txt`; the mask read 0 on a scene against itself
    and still saw the awning on 9296's laundromat against 9297's);
  - 1, `presentation/lux.applied.tscn`: its resource ids, and 11 lights' `light_energy`, which differ in every
    pair of runs since 9295 and not because of this change (below).
- **The pick held: seed_9104 at PASS 100,** every grade as 9297's.

      seed 9003: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR, LT_MAP_TRIVIAL_ENCOUNTER), route completion 1.00, grade PASS_WITH_TUNING 89
      seed 9104: 0 major, route completion 1.00, grade PASS 100
      seed 9205: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90

- **No fight moved** (`docs/findings/urban_street/fight_fields_9298.out.txt`): 0 of 32 summary fields on any
  candidate, every spawn at 9297's transform.
- **Findings 109 -> 109.**

## The time

    run    shell   art     export   walk   retire   the drive
    9297   111 s   218 s   215 s    13 s   19 s     9.9 min (593 s)
    9298   113 s   216 s   203 s    12 s   19 s     9.7 min (584 s)

The light bake read 75.4 s in the editor against 9297's 70.4 s, and baked in 38.7 s against 36.4 s. That is one run
each, with StarCraft II running on the machine: no time saving can be read from either, and none is claimed.

## Not priced

Frame time and draw calls were not priced. Nothing the left-out packages held was instanced -- lightmap users did
not move, and every scene both packages carry reads the same once the per-save ids are masked, Lux's eleven light
energies apart -- so there is nothing at run time for a price to see; and StarCraft II was running.

## Found: Lux's applied scene is not byte-stable either (roadmap 247)

`docs/findings/roofprops_bytes/lux_energy_pairs.py` (`lux_energy_pairs.out.txt`), over 9295 to 9298: the same ten
lights' `light_energy` differ in every pair, by about one part in 10,000 -- seven `Spawned_pendant` fluoros under
`LuxFixtureLights`, and `site_pole_43`, `site_pole_53` and `site_lamp_78` under `LuxClub` -- and
`Spawned_fluorescent_038_dup2` reads 2.618 in 9295, 9296 and 9298 and 3.7 in 9297. Recorded under 247 beside the
roof props, not traced.
