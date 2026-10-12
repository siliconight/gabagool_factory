# Cold run 9261 -- the same set again: one lightmap

**What it tested:** whether two cold runs of one set now bake one lightmap.
9260's tools and inputs exactly, run again: Level Factory 0.193.0 (the bake
byte-reproducible for one workspace since 0.192.0) and Zoo 1.103.0 (every Zoo
job builds the same bytes twice, `docs/findings/grader_speed/README.md`).

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked; findings
122 -> 122; the export's own lines as 9259's and 9260's but for the editor's
time (58.1 s).

## Against 9260: the same lightmap

- **The layout:** every one of the 3,320 users placed the same
  (`lightmap_layout.out.txt`). Cold runs 9256 to 9259 had each packed the
  atlas differently, 2,858 users moving.
- **The light:** texel by texel, 16,777,201 of 16,777,216 texels bit for bit
  the same, the other 15 under 0.00005 apart (`lightmap_compare.out.txt`);
  user by user, nothing apart by 0.01 anywhere.
- **What still differs** between the two packages, 29 files: the 18 any two
  exports differ in (`light_bake.json`'s timings, four manifests, `bake.tscn`,
  the twelve rowhome Empties' `site.tscn`); the three bake files those 15
  texels live in; one rowhome's dressing model, whose merged covers came out
  with their triangles in another order although Patina's plan for it was
  the same file in both runs -- a Zoo residue the job replays had not caught
  in two tries -- and the files that hash it (`build.lock.json`,
  `glb_reference_scan.json`, the validation report's three); and Lux's
  applied scene, whose resource ids Godot draws anew at each save.

## The time

    run    shell   art     export   walk   retire   the drive
    9260   78 s    167 s   167 s    11 s    3 s     7.2 min (434 s)
    9261   79 s    165 s   183 s    11 s    4 s     7.5 min (449 s)

The machine as slow as for 9260, the export too this time, which runs no Zoo
(`docs/cold_runs/cold_9260/NOTES.md` for what was measured about it).

## What is evidence of what

- The lightmap: `lightmap_layout.out.txt` (user by user) and
  `lightmap_compare.out.txt` (texel by texel), against 9260's package.
- The package: a sha256 of every file in both, compared.
- The result: `cold_run.py --end` and the drive's findings step.
