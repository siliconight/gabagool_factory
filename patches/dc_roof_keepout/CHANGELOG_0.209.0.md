## [0.209.0] - a roof slot says where a body steps off a ladder, and a building carries a roof-props layer

**Roadmap 181.** Zoo's rooftop scatter (0.25) is reaching levels (Zoo
1.101.0, Level Factory 0.179.0), and 60 of this library's 145 built shells
carry a ladder to their roof: a unit standing where the body steps off
would block the route the ladder exists for. Two things this release owns.

- **`fit.keep_out` on every roof slot** (`roofs.roof_keep_out`): a 3 m
  square (`LANDING_HALF_M` = 1.5, the 1.3 m hatch and a stride past its
  edge) around each ladder whose top story is the roof, written in the
  centred coords `floors.room_voids` writes the slab's holes in -- world
  minus the centre handed in -- and dropped when it misses the rect, as a
  hole is. Empty on a roof no ladder reaches, so every other roof slot is
  byte-identical but for the key. Zoo >= 1.101.0 keeps its props off these
  and off the holes. The footprint roof hands `0.0, 0.0` as its centre, as
  the holes do: right when the top slab is centred, which every library
  roof with a hole is (two of 133 stand off-centre, both hole-less,
  measured 2026-10-11); a stepped building's holes and landings would be
  off by its inset together, and that is noted here rather than fixed.
- **A third content layer.** `portable_building.build_package(...,
  roofprops_glb=None)` bundles Zoo's `<building>_roofprops.glb` at
  `art/roofprops/` and instances it as `RoofProps`, as the dressing and
  the fixtures are. The circulation gate asks the same question of it
  (`circulation.check_dressing`: a unit over a ladder's climb volume, which
  reaches above its hatch, is a conflict), and `combine_circulation` makes
  one `circulation_check` of every arm that ran: one arm is itself, two or
  more are `{"ok", <arm>: check, ...}` with the verdict the AND of theirs
  -- 0.149.0's shape for shell and dressing, unchanged, plus `roofprops`
  when it ran. The readers split by name (`run_presentation_compose.
  circulation_gate`, Level Factory's `_circulation_arms`, which 0.179.0
  teaches the third name).

### Tests

`test_roof_fixtures.py`: a ladder to the roof writes its landing on the
roof slot, a ladder that stops below it writes nothing, a landing is in the
roof's centred coords and dropped off it (two fail on 0.208.0);
`test_circulation_arms.py`: one arm is itself, two keep 0.208.0's shape,
three add the roof, none is None.

**Suite:** 1,395 passed, 2 skipped, exit 0 on the repo before the library rebuild: 0.208.0's 1,389 and the six new tests; on a clone, the one test that reads the built library fails as it does unpatched (no `build/` there)

**Library:** rebuilt (`python build.py --all`, 145 shells, 2026-10-11, about 18 minutes): 52 of the 133 roof slots carry `keep_out`, one landing each (the ladders that top out on their roof -- deli_a01's at x 6.5..9.5, y -13.5..-10.5 around `night_deli_ladder_0`, its hatch's hole inside it), and with the key removed every one of the 145 slot manifests is identical to the 0.208.0 library's as the factory 1.38.0 package shipped it, which carried the key nowhere
