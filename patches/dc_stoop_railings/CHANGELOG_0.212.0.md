## [0.212.0] - a stoop's iron railings, one each side

**Factory roadmap 240, the walker's calls of 2026-10-13**: "3 risers, concrete, railings both sides --
build the railings". 0.211.0's stoops already have three risers and concrete; this adds the comps'
"iron railings".

- **`stoop.plan` -> `rails`**: one railing a side, each as two slots of Zoo's `stoop_railing` (1.105.0).
  - a LEVEL section along the landing, from its front edge to the facade, 36 in tall over the landing;
  - a FLIGHT section from that edge down to a post on the bottom tread, its foot on the tread and its
    top 36 in over the landing.

  Each railing stands 5 cm inside the stoop's side, and the way up between them is 1.32 m, wider
  than the contract's 1.1 m corridor. The rail is 36 in over the landing at the flight's high end, and
  34.75 in over the nosing line at its post, inside IRC R311.7.8.1's 34-38 in (Zoo's forms hold the
  same number). The flight ends 1.42 m out, inside the stoop's 1.74 m.
- **5 cm in, not flush.** Flush, a flight's box shares the middle tread's side plane, facing the same
  way, over a tread by a riser: 0.2794 x 0.1778 = 0.0497 m2. The composer's z-fight gate reads a
  module as its box and skips a pair under 0.05 m2 (`zfight_gate.AREA_MIN`), so flush would have
  passed by 0.3 cm2, one deeper tread from a flag. `test_stoop.py` asks the gate's own
  `visible_fights` with no floor and finds no railing in a pair a camera can reach. Its control, each
  railing pushed flush, finds the two flights against the middle tread.
- **The turn:** `rot_y` 270. Zoo draws the run along its X with the high end at +X, and the composer
  turns a module by `tscn_export.godot_basis` (Ry(-t)), so 270 points +X at the house. 90 would point
  each flight's rail down toward the street. `test_stoop.py` holds the turn to `godot_basis` itself.
  The composer's fit keeps the slot's own turn on the tie a thin railing makes between 90 and 270.
- **The colliders are Deli Counter's**, in the greybox the graders walk:
  - the level section is its box;
  - the flight is a slab whose top face is the rail, 36 in deep measured upright, turned to the rail's
    pitch as the stoop's ramp is.

  Zoo's module carries none (`collision: false`). A box around a flight would have stood a third of a
  metre over its low end. Named `stoop_rail_*`, which Level Factory 0.197.0 reads as stoop, so the
  terrace stands the house where it stood.
- **`empty_rowhome`** declares the railing's iron (`metal_painted`, "Metal") beside the stoop's
  concrete. The twelve specs are regenerated, the presets' output byte for byte.

**Built:** build.py --all, 146 shells. Each of the twelve rowhomes, read off its manifests: four `stoop_rail_*` slots, species `stoop_railing` in `metal_painted` at `rot_y` 270, each `prop` in `surface_roles`, and four iron surfaces, `stoop_rail_<side>_<form>_col`. Among all twelve there are two modules: the level railing, 0.9 x 0.038 x 0.9144 m, and the flight, 0.5247 x 0.038 x 1.27 m -- the two Zoo 1.105.0's kit build built. Their colliders through Level Factory's reader (the factory's `patches/lf_stoop_railings/rail_hulls_0196.log`): on gs_empty_rowhome_a the level boxes stand at x -2.181 and -0.819, 0.9144 m over the 0.9 m landing, and each flight's slab reaches 1.4088 m in front of the facade, inside the stoop's 1.738 m

**Suite:** 1,441 passed, 2 skipped (the bpy round-trip fixtures, run in their own process), exit 0: 0.211.1's 1,432 and `test_stoop.py`'s nine new checks, all nine failing on 0.211.1, run against an export of it with the new file beside it. `test_stoop_circulation.py` reads the railings off the built shells: four slots a house, Zoo's species in iron, `prop` to the circulation gate, and every rowhome's circulation clear with them in it
