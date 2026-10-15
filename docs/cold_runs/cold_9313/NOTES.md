# Cold run 9313 -- the light bake counts what it bakes (urban_row_001)

**What it tested:** Level Factory 0.212.0 (775cac8), the factory's roadmap 251: `add_primitive_uv2` gives a
second UV set to, and the export's log counts, only the scenes the bake draws -- `baked_scenes(export_dir)`, the
presentation and every scene it instances, transitively. On 0.211.1 every `.tscn` in the package got the mark and
the log summed every count as "lightmapped": cold run 9312's 225 was the presentation's 112, the content scene's
same 112 again, and the backdrop's ground, which `mission.tscn` loads at run time outside the bake.

urban_row_001's brief as cold run 9312 ran it, seed_9104 named as 9312 named it. The rest of the toolchain is
9312's (Deli Counter 0.222.0, Lot 0.123.0, Zoo 1.112.0, Lux 0.77.0, Patina 0.31.0, Laser Tag 0.32.0, the others as
factory 1.40.0 certifies). Staged from 9312.

**Result: 0 interventions (journal 0, unattributed files 0). The one line that was wrong reads 112, the two
scenes the bake never draws carry no second UV set, and the lightmap is byte for byte 9312's.**

- **The log:** `[export] light bake: 349 model(s) and 112 primitive mesh(es) lightmapped, ...; 3160 users` where
  9312's read `349 model(s) and 225 primitive mesh(es)` and the same 3,160 users (`export.log`).
- **The marks** (`uv2_marks.py`, `uv2_marks.out.txt`): `presentation/lux.applied.tscn` 112 `add_uv2 = true` in
  both runs; `site.tscn` 112 -> 0; `site_backdrop.tscn` 1 -> 0. `light_bake.json`'s `primitives` table reads
  `{"presentation/lux.applied.tscn": 112}` where 9312's carried the three.
- **The bake's input did not move, so its output did not:** `bake.exr` the same bytes as 9312's; all 329 GLBs the
  same bytes; 2,490 files in each package, none only in one.
- **The grades:** every candidate as in 9312 -- seed_9003 PASS_WITH_TUNING 89, seed_9104 PASS 100, seed_9205 PASS
  90 -- with the same enemy and crew spawns and 0 of 32 summary fields moved on each (`fight_fields_9312_9313.out.txt`).
  Findings 76 at the candidates and 109 after the export, as 9312's.
- **The 24 files that differ, each attributed** (`masked_scenes.py`, `masked_scenes.out.txt`):
  - **2 are the change:** `site.tscn` (2,819 -> 2,707 lines) and `site_backdrop.tscn` (269 -> 268) are identical
    once their `add_uv2 = true` lines are removed.
  - **12 are Godot's per-save ids,** roadmap 247's residue: the presentation, `bake.tscn` and the ten standing
    Empties' `site.tscn`, 2,169 / 3 / 280 to 1,247 lines apart and 0 once node `unique_id`s and resource ids are
    masked.
  - **10 are the metadata that records times, paths, versions and the hashes of the above:** `LICENSES.json`
    (`created_at`), `build.lock.json` (`created_at`, one input's and five outputs' hashes), `LF_MANIFEST.json`
    (`archive_name`, `built_utc`, and `factory_tag` 1.39.0 -> 1.40.0 with the seven tool pins that moved -- 9312
    ran before the factory's promotion and 9313 after it), `export_closure_scan.json` (`package_fingerprint`),
    `glb_reference_scan.json` (the workspace's path), `light_bake.json` (the `primitives` table above, the editor
    log's path, 74.7 -> 77.3 s in the editor, `bake_ms` 38,004 -> 41,809), `portable_resource_manifest.json` (the
    22 other entries' hashes) and `validation/report.{html,json,md}` (`generated`).
- **REFUTED AND KEPT:** `masked_scenes.py`'s first run masked `unique_id = N` and the scenes write `unique_id=N`,
  no spaces, so it reported 964 lines of the presentation and every differing line of the Empties' scenes as
  unmasked. The instrument's miss, not a finding; the pattern now takes either spelling and the counts above are
  its second run.

**What the backdrop's ground lost** is a UV2 nothing read: `mission.tscn` loads `site_backdrop.tscn` outside the
bake, and no lightmap samples it. What the ground COSTS in the frame is roadmap 252's, priced on 9308's package
after this run.

## The time

    run    shell   art     export   walk   retire   the drive
    9312   131 s   249 s   201 s    10 s    5 s    10.2 min (611 s)
    9313   114 s   221 s   211 s    12 s    6 s     9.8 min (585 s)

Neither is a speed measurement. 9313's export leg ran beside the proof of two Level Factory patches on a
throwaway copy (`patches/lf_layers_shown/prove_tests.sh`, two small pytest runs and a `git archive`, 07:21 to
07:23) and beside file reads; nothing opened a window.
