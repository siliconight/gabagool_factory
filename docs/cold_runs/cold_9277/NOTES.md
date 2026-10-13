# Cold run 9277 -- Deli Counter 0.213.0, six mid-rise Empties in the library and no draw moved

**What it tested:** Deli Counter 0.213.0 in a real drive of restaurant_row_001 (roadmap 241, step 1;
`docs/findings/urban_midrise/`). The library gains six mid-rise Empties, `gs_midrise_a` to `_f`, of 5 to 12
storeys. They are named out of the prefix Level Factory hands to every terrace, and as facades they are
outside the enterable draw. The library was rebuilt whole for the release (`build.py --all`, 152 shells), as
Deli Counter's freshness gate asks after any change to `presets.py`. So this run is the control: today's
mission must come out as it did.

**Result: 0 interventions, 0 tool files changed. Nothing moved.**

- **The lots:** the three candidates' staged `level.tscn` and `site.tscn` are byte-identical to 9276's.
  No `gs_midrise_*` is in any staged lot.
- **The grader:** every summary field of every candidate's Laser Tag report is identical to 9276's. All
  three PASS 90, and seed_9104 was picked as before.
- **Findings 117 -> 117**, no issue id moved.
- **The bake** is 9276's to the count: 567 models and 224 primitive meshes lightmapped, 3,392 users.

## The time

    run    shell   art     export   walk   retire   the drive
    9276   97 s    162 s   174 s    11 s    4 s     7.8 min (465 s)
    9277   91 s    161 s   187 s    12 s    4 s     7.9 min (473 s)

## What is evidence of what

- The lots: each candidate's `staging/restaurant_row_001.laser_tag_evaluate.candidate.<seed>/` in
  `workspaces/cold-9277-ws/.level_factory/`, against 9276's.
- The grader: the same jobs' `out/lasertag.report.json`.
- The count: `cold_run.py --end`.
- The family and its frames: `docs/findings/urban_midrise/`.
