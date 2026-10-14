# Cold run 9300 -- the same command again: what two runs still disagree on (Zoo 1.109.0)

**What it tested:** cold run 9299 repeated -- urban_row_001, seed_9104 named, the same toolchain (Zoo 1.109.0,
Level Factory 0.207.0, Lot 0.123.0, Deli Counter 0.219.0, Laser Tag 0.32.0) -- to read what still differs between
two packages built from one command (roadmap 247). Staged from cold run 9299.

**Result: 0 interventions (journal 0, unattributed files 0). Every Zoo model and the lightmap came out byte for byte
as 9299's; 22 of 3,283 files differ, and each is attributed.**

- **Measured against 9299's package** (`docs/findings/roofprops_bytes/package_9299_9300.out.txt`):
  - the same 3,283 files, thirteen `lot/` packages, 616 baked imports and 3,147 lightmap users;
  - **3,261 byte-identical**, among them every one of the package's 596 GLBs -- the 364 that Zoo 1.109.0 rebuilt,
    and the pharmacy's roof props, which 9294 to 9296 built two ways -- and `bake.exr` and `bake.lmbake`: one
    lightmap from one set of meshes.
- **The 22 that differ:**
  - **11 by Godot's per-save ids alone:** `bake.tscn` and the ten standing Empties' `site.tscn`, which read 0 lines
    different once node `unique_id`s and drawn resource ids are masked
    (`docs/findings/roofprops_bytes/per_save_ids_9299_9300.out.txt`);
  - **1, `presentation/lux.applied.tscn`:** its resource ids, and the same eleven lights' `light_energy` that
    differ in every pair of runs since 9295 (`lux_energy_pairs_9297_9300.out.txt`);
  - **10 metadata files,** read key by key (`metadata_9299_9300.out.txt`): timestamps, the workspace's path,
    the bake's timings, and the hashes and sizes of the files above.
- **Findings 109 -> 109.** The pick seed_9104 at PASS 100, every grade as 9299's, and 0 of 32 summary fields moved
  on each candidate (`fight_fields.py urban_row_001 9299 9300`, not kept: it read as 9299's against 9298's).

So after Zoo 1.109.0, the whole of what two runs of one command disagree on is Godot's per-save ids and Lux's
eleven light energies, and what hashes them.

## The time

    run    shell   art     export   walk   retire   the drive
    9299   109 s   211 s   200 s    11 s   21 s     9.5 min (571 s)
    9300   108 s   212 s   200 s    11 s   20 s     9.4 min (565 s)
