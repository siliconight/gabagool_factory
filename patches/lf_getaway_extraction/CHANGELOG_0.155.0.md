## [0.155.0] - The crew leaves from where it came: the extraction is the spawn building

**Roadmap 206.** The walker, 2026-10-07: "location of the getaway vehicle
should be the same as the missions spawn point. you spawn, do the job, then
return to the car"; 2026-10-08: "go ahead, place it at the spawn".

### The extraction draw

`site_variation.site_placements` drew the extraction among the buildings that
were not the spawn ("so the route crosses the site"). Measured 2026-10-07, it
crossed the site into the score building itself on 43 of 136 multi-building
candidate specs on disk, and on 2 of cold run 9195's 3 candidates: no second
half to the heist.

The extraction is now the spawn building. Lot 0.98.0 parks the getaway van at
its kerb and puts the crew's start and exit at the van's door, both
site-level markers, which Lot reads over any building's own.
- **No other number moves.** The draw that chose another building is still
  made, so every number a seed gives after it is unchanged: the buildings,
  the spawn and the objective of every candidate already graded. Only the
  extraction moves, by design.
- **The heist gate still passes.** Lot's `site_tactical` needs routes spawn ->
  objective and objective -> extraction. The second is now the first walked
  back, so a site that passed before passes now.

### Tests

The three that pinned the old draw now pin the new one:
- `test_score_building.py`: with a score anchored, the extraction is the
  spawn on every seed and count. The no-anchor pin keeps 0.151.0's spawn and
  objective for seeds 9000-9003, with the extraction the spawn; 0.151.0 drew
  b1, b0, b0, b0 there, and that draw is still made.
- `test_candidate_distinctness.py`: every candidate's extraction is its
  spawn.

**`brief.extraction_relationship` stays unbuilt.** 159 of 181 cold-run briefs
say `crew_start_backtrack`, and the van gives every heist that shape
whatever its brief says. Nothing reads the field, so it stays in
`UNBUILT_BRIEF_FIELDS`, and a brief that asks for another shape is not yet
heard.

**Suite:** 2,002 passed, 14 skipped (the real-tool smokes, `LF_TOOLS_DIR` unset), 1 xfailed, exit 0 -- `python -m pytest -q`, tallied off its progress lines (the conftest prints no summary).

