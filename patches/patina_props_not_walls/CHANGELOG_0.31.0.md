## [0.31.0] - a prop is not the building

### Fixed
Factory roadmap 248, found attributing cold run 9303's package against 9302's (the factory's
`docs/findings/fire_escape/README.md`, "Found").

- **A prop standing proud of a wall took the wall's place.** `surfaces.classify` took the building's bounds from
  every visual mesh in the shell GLB, and called a vertical face an exterior wall when it stood within
  `_BOUNDARY_TOL` of them. Deli Counter greyboxes every `prop` slot as a visual box named by its `slot_id`, and three
  of its props stand proud of a front: a rowhome's stoop (Deli Counter 0.211.0), a corner shop's awning (0.219.0) and
  a walk-up's fire escape (0.220.0).
  - So the box was the front: the wall stopped reading as exterior, and the box's face read as exterior instead.
  - The anchor pass reads exterior-wall faces only, so it put the front's coping, base course and curbs on the box.
  - Measured on 9303's gs_midrise_a: its front anchors went roofline 12 -> 1, ground edge 8 -> 1, wall base 4 -> 1,
    the one of each on the stack's box face, 1.34 m off the wall. The rowhomes' front anchors had moved onto the
    stoop since cold run 9271, the corner blocks' onto the awning since 9297.
- **`classify(..., props=)`:** the meshes named are left out of the bounds and never read as exterior wall or roof.
  - Their faces keep the role their normals give, and a gameplay hint still wins.
  - Not trim, though `slots._ROLE_MAP` reads a prop as trim for tinting: that would retint every prop in the
    library's 9,933 prop slots, nearly all indoors, for nothing this defect needs.
  - Leaving a prop out of the bounds alone would not do: the exterior test accepts a face standing beyond the bound.
- **`SlotManifest.prop_ids()`:** the `prop` slots' ids, which are their greybox meshes' names. The CLI hands them to
  `classify`. A shell with no slots.json reads as before: nothing names its props.
- **`tests/test_props_are_not_walls.py`:** on 0.30.0 it fails, `classify` taking no `props` and `SlotManifest` having
  no `prop_ids`. On three real shells beside this repo -- gs_midrise_a's fire escape, gs_cornershop_c's awning,
  gs_empty_rowhome_a's stoop -- the anchors with the props named equal the anchors with the props taken out of the
  scene, and unnamed they do not.

**Suite:** python -m pytest -q tests: 401 passed, 1 skipped, exit 0 -- 0.30.0's 393 and the new file's 8. The new file on an archive of 0.30.0: 4 failed (no `props`, no `prop_ids`), the defect's own test passed, its 3 real-shell checks skipped with no Deli Counter beside the archive; on 0.31.0 all 8 pass (the factory's `patches/patina_props_not_walls/prove_tests_0300.out.txt`, `prove_tests_0310.out.txt`)

**Replayed** (the factory's `docs/findings/patina_props/replay.py`, every Deli Counter shell with a slots.json, the
dressing job's own command, 0.30.0 twice as the control): 158 shells, 474 runs, none failed; the control read every output of every shell byte-identical. 118 shells byte-identical in every output; 40 moved. 29 moved their dressing, the output a package carries: the five walk-ups and four corner blocks (their front anchors back from y -8.842 to the wall at -7.65), the twelve rowhome Empties (from the stoop's -7.609 to -6.15), seven gas stations (from the forecourt's canopy and pad, out to y -32.0, to the building's +-11.15) and twin_a01 (from its porch's -9.1 to -6.65). 11 moved only the styled GLB, which no package carries (`glb_only_roles.py`): seven enterable buildings whose rooftop unit's top had read as roof, 2 faces each, now floor; three parking garages whose 12 columns' tops had, 24 faces; and harbor_score, whose 58 slots are all props and whose stair rails had stood over its roof, so 0.30.0 read no roof at all -- 45 of its slabs, 98 faces, now read as roof, and its manifest gains the role. No shell with a prop past its other slots went unmoved
