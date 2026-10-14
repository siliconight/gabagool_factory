# Cold run 9302 -- the same command again: one applied scene (Lux 0.77.0, Level Factory 0.208.0)

**What it tested:** cold run 9301 repeated -- urban_row_001, seed_9104 named, the same toolchain (Lux 0.77.0, Level
Factory 0.208.0, Zoo 1.109.0, Lot 0.123.0, Deli Counter 0.219.0, Laser Tag 0.32.0) -- to read what two runs still
disagree on once every Lux rig rests before the pack (roadmap 247). Staged from cold run 9301.

**Result: 0 interventions (journal 0, unattributed files 0). Lux's applied scene came out as 9301's once Godot's
per-save ids are masked; what two runs disagree on is now those ids and the metadata, and nothing else.**

- **The job said it:** `[lux] 216 rig(s) at rest before the scene is packed`, as 9301's.
- **Measured against 9301's package** (`docs/findings/roofprops_bytes/package_9301_9302.out.txt`): 22 of 3,283 files
  differ -- the set 9300's NOTES attributes -- and every GLB and the lightmap are the same bytes.
- **All 12 scenes Godot saves read 0 lines different once its per-save ids are masked**
  (`per_save_ids_9301_9302.out.txt`): `bake.tscn`, the ten standing Empties' `site.tscn`, and
  `presentation/lux.applied.tscn`, whose eleven light energies differed in every pair of runs from 9295 to 9300.
- **The pick held: seed_9104 at PASS 100,** and 0 of 32 summary fields moved on each candidate against 9301
  (`fight_fields.py urban_row_001 9301 9302`, not kept).
- **Findings 109 -> 109.**

## The time

    run    shell   art     export   walk   retire   the drive
    9301   121 s   257 s   241 s    13 s   30 s     11.5 min (687 s)
    9302   117 s   228 s   201 s    11 s    9 s     9.7 min (584 s)
