# Cold run 9159 -- 0 interventions; a house's own brick: red, brown and orange in one row

gas_block_001, seed 9080, `empties: "across"`, `--bake-lights`.

**Stack.** The walker's South Philly photograph: "every house a different
brick: brown, red, orange".
- Pixelcoat 0.57.0 paints `brick_brown_delco` and `brick_orange_delco`,
  `brick_delco`'s grammar in their own palette and mortar, as kinds of
  their own mapped in both level themes. A theme holds one grammar per kind.
- Zoo 1.73.0 knows the kinds (`KNOWN_KINDS`, and a brick's 0.90 in
  `ROUGHNESS`).
- Deli Counter 0.183.0 maps them, holds them outside-only like brick, and
  builds `gs_empty_rowhome_a` in orange and `_c` in brown. `_f` keeps the
  red.

**Result:** every leg ran in 33 minutes, `INTERVENTIONS: 0`. Art exited 1
on 55 findings, as before. No `STEM COLLISION`. The walk copy is this
run's. The kit jobs printed `[zoo] skin: brick_brown <- brick_brown_delco`
and the same for orange: both resolved to their own packs, not a flat
fallback.

## Found on the way, all before shipping

- **Pixelcoat's theme test refused the grammars' kind.** They were first
  kind `brick`, on the guess that they would then take brick's material
  response. A theme slot's grammar must be of the slot's own kind, so they
  are `brick_brown` and `brick_orange`. The guess was wrong anyway: the
  response presets are read only by a grammar's wet variant
  (`responds_like`), and neither carries one.
- **Zoo's `test_kind_vocabulary`** holds `KNOWN_KINDS` and `ROUGHNESS` to
  the same keys; the two kinds needed a roughness too.
- **Two Deli Counter tests kept a literal of the old vocabulary**
  (`test_empties`' wall kinds, `test_inner_face`'s outside-only set). They
  moved with it, in `patch_dc_house_bricks_tests.py`. That is a follow-up
  rather than a re-application, because re-applying the patch after
  `build.py --all` would have made every shell look older than its code.
- **The Deli Counter commit first failed with "pathspec 'VERSION' did not
  match".** Two parallel shell calls share one working directory, and the
  other's `cd ..` moved it. Committed alone with `git -C`.

## Before the run

- Every suite passed: Pixelcoat 640, Zoo 3,308, Deli Counter's `check.py`
  after `build.py --all`.
- Each new test failed on the version before it.
- **The Blender pre-flight against a library built by Pixelcoat 0.57.0**
  (`patches/zoo_house_bricks/preflight_bricks.py`):
  - rowhome_c's walls, windows and doorways are `_mbrick_brown` modules in
    `M_Skin_brick_brown_delco_1997`, its door the oxblood (`_541414`);
  - rowhome_a's are `_mbrick_orange`, its door navy.

## Frames

`docs/findings/empties_bricks_9159/`. Across the street the row reads as
different houses: a brown house with its oxblood door, red ones, and an
orange one with its navy door behind the iron grille. The lintels, sills,
units and gutters are as in 9158.

## The price

A = 9158's package, B = 9159's, A2 = 9158's again: 53 station x heading
pairs, back to back.

- **Draws:** 0 change at every heading. The bricks are materials on modules
  that were drawn anyway.
- **Median frame**, against the mean of A and A2 over the 51 headings where
  A and A2 agree within 1 ms: median -0.013 ms. The control's own median
  is -0.011, so there is nothing to price.
- **The package:** 134 MB for both.
- **The light census:** 61 meshes over the cap, the same 61.
- **The control itself hitched:** camera_socket_0 at 90 and 270, A 11.7 /
  11.1 ms against A2 8.7 / 7.6. B hitched once, attacker_spawn_1 at 180
  (+1.9 ms for 0 draws). This is the fourth run in a row. The harness
  measures each heading once.

Outputs: `price_bricks.txt`, `price_bricks_robust.txt`.
