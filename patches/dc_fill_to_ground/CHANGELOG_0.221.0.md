## [0.221.0] - a switchback's second flight stands on the floor under it

**The walker's walk of cold runs 9305-9307, findings 7-9** (the factory's `docs/findings/walk_2026-10-14/`). At
restaurant_row_001's office, from below the stair core: "bottom of this stair should come down all the way to the
ground"; beside it, a tall gap in the enclosure; inside, a core that "looks wrong in general".
- **Traced:** `flight_solid_under` fills a switchback's first two legs solid "to that storey's floor", on the
  premise that only the first leg of each run stands on one. With `cut_slabs`, leg 1's own storey floor is the slab
  its stair cut across both runs (`hole_span`). So its fill hung with a level bottom a storey over the floor below,
  over the walkway 0.134.0 kept open under the next leg, and that walkway's mouth was the gap.
- **The same shape stood in 17 legs of 14 library specs** (`floating_flights.py` there).
- **Asked, the walker chose: "fill the stairs to the ground".** That overrides 0.134.0's channel.

### Changed
- **`stairwell.flight_solid_base(spec, st, s)`:** the storey whose floor a leg's fill stands on.
  - A cut, multi-storey switchback's second leg, when it is filled, stands on the stair's lowest storey.
  - It keeps its own storey when something else opens that floor under its run (`slab_openings`).
  - Every other leg stands on its own storey, as before.
- **The builder's `_stairs`:** each tread's column, and its collider one riser short of the tread, stands on that
  floor. For every leg on its own storey the numbers are the same floats as 0.220.0's.
- **`stairwell.stair_guards`:** on the lowest storey the second run gets a back from leg 1's foot to the
  rectangle's arrival edge. It runs from the side wall's inner face to the run boundary and from the floor to the
  slab underside, beside the first run's back, which is unchanged. The core's face there is flush, where it was
  the gap the walker looked through.

### Tests
- **`test_stair_fill_to_ground.py`:** the walker's stair stands on the ground floor; only a cut multi-storey
  switchback's second leg moves; a floor cut under the second run keeps the old base; the office's core is closed
  to the north; every cut second flight in the library, 17 legs in 14 specs, stands on its stair's lowest floor.
- **`test_stair_back.py`:** two tests pinned 0.134.0's walkway and change with it:
  - `test_the_walkers_stair_gets_a_back_in_its_own_run_only` is now `..._in_each_run`;
  - `test_the_walkway_under_the_next_leg_keeps_both_its_mouths` is now `..._is_filled_to_the_ground`.

**Proven to fail first:** `test_stair_fill_to_ground.py` fails on 0.220.0, all 5, `stairwell` having no `flight_solid_base`; on 0.221.0 it passes with `test_stair_back.py` and `test_stair_underside.py`, 27 (the factory's `patches/dc_fill_to_ground/prove_tests_0220.out.txt`, run on a throwaway copy before the repo was touched)

**Suite:** `python -m pytest -q`: 1,533 passed, 2 skipped, exit 0, in 131 s -- 0.220.0's 1,528 and `test_stair_fill_to_ground.py`'s 5; `test_stair_back.py`'s two rewritten tests stand in their old ones' place

**Build:** `python build.py --all --blender C:/blender/blender.exe`: exit 0 in 579 s. Every changed file attributed, the build folder hashed before and after (the factory's `patches/dc_fill_to_ground/build_diff.out.txt`): 197 of 1,483. The 14 GLBs are the 14 shells whose second flight now stands on the ground -- bank, bank_job, cbp_town_finale_midbalanced_schemafixed, corner_deli_heist_01, cr_deli, final_stand, foundry_heist_vertical, harbor_score, night_deli, office, office_stepped, primos_pizza, rowhouse_raid and twin_a01. Of those, 12 also changed their slots and gameplay manifests, recording the second run's back (office: two `stair_guard_back` slots where it had one); the other two, foundry_heist_vertical and primos_pizza, are where an exterior wall already refuses the back. Every shell's manifest changed its `built_utc`
