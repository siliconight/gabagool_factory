# Cold run 9301 -- every animated Lux rig at rest before the applied scene is packed (Lux 0.77.0, Level Factory 0.208.0)

**What it tested:** urban_row_001 (9300's brief unchanged) on Lux 0.77.0 (4ce4c85), whose fluorescent, streetlight
and stage-light rigs answer `rest()`, and Level Factory 0.208.0 (b8fe4f7), whose `run_lux_apply.gd` rests every rig
before it packs the applied scene (roadmap 247).

**seed_9104 named** against 9300's. Zoo 1.109.0, Lot 0.123.0, Deli Counter 0.219.0, Laser Tag 0.32.0. Staged from
cold run 9300.

**Result: 0 interventions (journal 0, unattributed files 0). The Lux apply rested 216 rigs, and the applied scene's
lights moved to their rest values and nowhere else.**

- **The job said it** (`jobs/urban_row_001.lux_apply/1/job.log`): `[lux] 216 rig(s) at rest before the scene is
  packed`.
- **The package, against 9300's** (`docs/findings/roofprops_bytes/package_9300_9301.out.txt`): the same 3,283 files;
  28 differ.
  - **22 are the set any two runs differ in** (9300's NOTES): metadata, and the 11 scenes Godot saves with per-save
    ids, which read 0 lines different once those are masked (`per_save_ids_9300_9301.out.txt`).
  - **One of those 22, `presentation/lux.applied.tscn`, also carries the change** (`lux_energy_pairs_9300_9301.out.txt`).
    13 lights move to their rest values: seven pendants to 1.3, the failing tube to 3.7, four poles to 34.12 -- two
    of them, `site_pole_46` and `site_pole_76`, from 0.0, where their dark-starting cycle had saved them in every
    run -- and `site_lamp_78` to 18.43.
  - **6 are Lux's three changed rig scripts** under `runtime/lux/runtime/rigs/` and their `.gd.uid` files. The
    export's import pass gives the package's scripts their UIDs, and the shipped scenes name none (`export.py`'s own
    note). Across these runs the UIDs follow the scripts' bytes: the three changed rigs have new ones, and the
    unchanged area-light and sun-moon rigs keep theirs.
- **The lightmap is 9300's, byte for byte** (`bake.exr`, `bake.lmbake`), though two poles saved at 34.12 where they
  saved at 0.0. A saved lamp energy does not reach the bake, as `_rebuild` -- which frees every saved lamp and
  builds its own at load -- says it should not.
- **The pick held: seed_9104 at PASS 100,** and 0 of 32 summary fields moved on each candidate against 9300
  (`fight_fields.py urban_row_001 9300 9301`, not kept).
- **Findings 109 -> 109.**

## The time

    run    shell   art     export   walk   retire   the drive
    9300   108 s   212 s   200 s    11 s   20 s     9.4 min (565 s)
    9301   121 s   257 s   241 s    13 s   30 s     11.5 min (687 s)

StarCraft II was running when the run began (checked at 13:09), and the light bake read 97.8 s in the editor against
9300's 75.0: the run's time is not a measurement of the change.
