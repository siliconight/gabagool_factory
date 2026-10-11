## [1.101.0] - a roof's props keep off its hatches and landings, stand in the box they occupy, and draw as one roof

**Roadmap 181.** 0.25's roof scatter has never run in a level: Level
Factory's adapter read a key nothing wrote, and the command it would have
built could not have worked (`zoo_cli` answers `--roof-props` before
`--build-kit` and returns). Level Factory 0.179.0 plans it as a job of its
own; this release makes what it builds fit a roof a player stands on. 60 of
the library's 145 built shells carry a roof ladder.

- **A prop keeps off the roof's holes and landings.** `roofprops.roof_slots`
  reads the slot's `fit.voids` (the slab's holes -- stair heads, ladder
  hatches; 52 of the library's 133 roofs carry one) and `fit.keep_out` (the
  landings Deli Counter 0.209.0 writes for the ladders that top out on the
  roof); `scatter` places nothing on a hole or within `VOID_CLEAR` (1.0 m,
  the stride out of it) of its edge, nor on a landing. The plan and the
  index record `forbidden`, each roof's count of them.
- **A yawed prop is tested as the box it occupies.** The yaw is drawn before
  the position and `_extents` gives the footprint's half-extents at it; the
  margin clamp and the overlap test both read those. 0.25 read the
  unrotated box for both: the 0.35 m clearance happened to absorb the
  overlap for every current species, but a 90-degree HVAC (1.8 x 1.1) at
  the long edge of a 4 m roof reached 0.25 m from the footprint's edge --
  inside a 0.35 m parapet -- and on the 20 x 12 test roof a 1.6 m tank
  yawed 149 degrees stood 9 cm past the margin. Each placement now carries
  `local` and `extents`, the box, in the slot's own centred coords.
- **A water tank needs height.** Planned only on a roof whose top is
  `TANK_MIN_ROOF_M` (12 m) or more above the plan: a gravity tank serves
  floors below it, and a one-storey Delco roof is on street pressure. The
  library's roofs stand 3.2 to 13 m; two of 133 reach 12. (A taste call,
  recorded for the walker; the rule is a constant.)
- **A roof draws about once a species.** `build_roof_props` bakes each
  prop's placement into its vertices (as the dressing's covers since 1.68.0;
  the collider proxies the same way) and exports merged: a roof's props
  enter and leave view together, so the roof is the unit, and the merge
  groups a module's parts by family and material -- every `Hvac_*` part on
  the roof in `M_Hvac_<material>` one mesh, every `VentStack_*` another --
  which is about one mesh a species a roof, since each recipe paints one
  material (an HVAC is five parts, a dish four, a tank, a fan and a stack
  three each). `merge_parts` False is the one-build control, reached by
  `--no-merge-parts`; the index and the CLI's summary carry the merge's
  stats. Measured 2026-10-11 on Blender 5.1.1, flat materials, deli_a01's roof as the 0.208.0 library shipped it (38 x 28 m, top at 6.6 m, one hatch hole and no landings yet): 17 props -- 4 HVAC units, 6 vent stacks, 3 exhaust fans, 2 skylights, 2 dishes, no tank below 12 m -- 59 parts merged into 6 meshes, one a species family (the 15 collider proxies kept as themselves), 4,392 triangles both ways; 59 submissions to 6 by `docs/findings/fixture_merge/layer_count.py` on the merged and the `--no-merge-parts` GLB (`docs/findings/roof_props/`)

### Tests

`tests/test_roofprops.py`, thirteen tests: a 90-degree HVAC at the long edge
stays inside the margin, no prop stands on a hole's ring or a landing, a
tank needs a tall roof, a placement records the box it occupies, the extents
and the forbidden rects (all fail on 1.100.0, run against it first), and the
margin and overlap tests now judge the yawed box (the margin one fails on
1.100.0 too: the yawed tank). Placements differ from 1.100.0's for every
seed, since the yaw is drawn first; no level has had a roof prop, so nothing
shipped moves.

**Suite:** 4,163 passed, 438 skipped, 1 xfailed, exit 0 (5:45): 1.100.0's 4,157 and the six tests `tests/test_roofprops.py` grew; eight of its thirteen fail on 1.100.0, run against it first
