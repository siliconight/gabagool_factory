## [0.156.0] - The package starts and ends the mission at the getaway van

**Roadmap 204.** Lot puts the crew's start and exit at the getaway van as two
site-level markers (Lot 0.98.0), and Lot 0.99.0 adds where responders arrive
as more of them. None of them reached the package.

### The cause

`packages/staging/dispatch_inputs.py` turns Lot's gameplay `markers`,
`objectives` and `loot` into Dispatch anchors, and never read `site_markers`.
`ensure_mission_anchors` then covered the gap:
- **A start from nowhere.** With no `player_start` among Lot's anchors, it
  synthesized one at the centroid of every Lot anchor. On cold run 9198 that
  was `lot:mission_start` at (-7.03, 0.68), 14 m from the van.
- **Every extraction the mission's.** With extractions present and none
  tagged, it tagged every building's street point as the mission's.

The shape is the `ladders` line that was missing here in cold run 9076.

### The fix

`site_markers_to_anchors` stages Lot's site-level markers ahead of the
buildings' markers:

| Lot site marker | Dispatch anchor | tag |
|---|---|---|
| `crew_spawn` | `player_start` | `mission_start` |
| `extraction` | `extraction` | `extraction` |
| `responder_spawn` | `ai_spawn` | `responder` |

Any other type passes through as `markers_to_anchors` passes it.
- **Height:** a site marker stands on the plate, so its height is the
  ground's, as `lot._walk_positions` reads it.
- **Why the tags settle it:** `ensure_mission_anchors` now finds the start
  and the exit already tagged, so it neither synthesizes a start nor tags
  the buildings' extractions.
- **No facing is passed.** Lot's slot yaw and Dispatch's `rot_y` have not
  been shown to share a convention, and a yaw read in the wrong one is
  silently wrong.

### Measured on cold run 9200's own outputs

Seed_9054's Lot gameplay and Deli Counter shell, staged both ways and built
by the real Dispatch 0.5.2, `--mode shell-handoff`:

| | as 9200 shipped | with 0.156.0 |
|---|---|---|
| the `spawn` beat binds to | `lot:mission_start` (the centroid) | `lot:getaway_van_crew_spawn_0` |
| the `extract` beat binds to | `lot:EXIT`, `lot:STREET`, `lot:STREET_25` | `lot:getaway_van_extraction_0` |
| anchors | 64 | 68 |
| tagged `responder` | 0 | 3 |

- **The anchor count:** 68 is the synthesized start gone, plus the van's two
  and the three arrivals.
- **The positions:** the van's start lands at Godot (-4.15, 0, 14.95), where
  the walk scene stands the crew. The arrivals are `ai_spawn`s at their
  stops, under `AISpawnZones`.
- **The build passes:** readiness 100, 0 blockers.

**What this does not fix: the half of item 204 that is Deli Counter's.** The
`deli_counter:*` anchors -- its `crew_spawn` and `responder_spawn`, which
Dispatch still notes as unknown types -- come from the mission's own
generated shell, which a library lot never places. That is not touched here.

### Tests

`tests/unit/test_dispatch_site_markers.py` stages cold run 9200's seed_9054
as Lot wrote it -- the van's point, the three stops, two buildings' street
extractions -- and reads the anchors back from the file the staging writes.

**On 0.155.0, 4 of 5 fail:**
- the start is not at the van;
- the extraction is not the van's alone;
- a start is synthesized at the centroid;
- no responder anchors exist.

The fifth -- a site with no site markers stages exactly as before -- passes
either way, by design.

**Suite:** exit 0; 2,008 passed, 14 skipped (the real-tool smokes,
`LF_TOOLS_DIR` unset), 1 xfailed. That is 0.155.0's 2,002 plus this file's
5, plus the one case `test_sibling_locator.py` adds for every new source
file. Tallied off the progress lines: the conftest prints no summary.
