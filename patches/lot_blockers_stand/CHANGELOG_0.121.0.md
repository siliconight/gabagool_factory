## 0.121.0 - every planner that keeps clear of what stands keeps clear of the Empties

**Factory roadmap 241, the urban street's near side.** Five planners each take a `standing` list, the plan
rects of what already stands:
- the parking fields and their cars (`site_fields`);
- the forecourt pylons and the dumpsters (`site_furniture`, `site_dumpsters`);
- the dumpsters' pads and bags (`site_yards`);
- the cover planner (`site_cover`).

Each was handed the cover pieces placed so far and nothing else. The blockers, Level Factory's Empties, were
left out. That was harmless while every Empty stood across the road, where none of these planners places
anything. Level Factory 0.200.0's urban street brings them to the near side, into the gaps beside the
mission's buildings, which is where fields, dumpsters, pads and cover go.

- **`assemble`** reads every blocker's rect once, as built (`site_spawns.blocker_rects`, margin 0), and each
  of the four `standing` lists starts with them. They are obstacles, not buildings, so:
  - a field serves no blocker, and a dumpster stands beside no blocker;
  - the cover planner's sightlines still measure against the mission's buildings only.

  Empties blocking sight is a separate question, and it moves Laser Tag's fights.
- **`tests/test_blockers_stand.py`** spies on the four planners during a real `assemble` of the example
  compound with two Empties added, and asks that every call's `standing` holds both. It fails on 0.120.2.

**A strip level does not move:** every cold run on this disk from 9278 to 9287 had its picked candidate's `lot_assemble` job replayed from its own `job.log`, before and after (the factory's `docs/findings/urban_street/lot_replay.py`): nine strip missions and the first urban street, 10 jobs, 0 files differ. The control, the same jobs replayed twice before, is also 0. Across the road no planner places anything, so no blocker was in any planner's way

**Suite:** 835 passed, exit 0. `test_blockers_stand.py`'s planner check fails on 0.120.2: `plan_fields` was handed neither Empty
