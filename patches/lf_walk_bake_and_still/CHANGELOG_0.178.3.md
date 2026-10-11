## [0.178.3] - The walk keeps the bake, and its shot bot tells animation from fighting

**Roadmap 202, install test 5's two findings.** The test packaged the
1.37.0 set, unzipped it fresh and typed `START_HERE.md`'s commands:
`setup --venv` exited 0 with every doctor row PASS and no sitecustomize
error, `make` exited 0 with the package baked and the closure clean, and
`walk` exited 1.

- **The walk replaced the baked package with an unbaked one.** `walk`
  wraps the portable export and re-exports it first by calling `export`
  with the walk's own arguments, which carried no bake, into the same
  folder `make` shipped to. After `walk` the stranger's package held 2,526
  files with no `bake.exr` and no `light_bake.json`, where `make` had left
  3,008 and a bake. Every walk since 0.144.0 did this; nothing said so
  until 0.178.0's note under an unbaked export printed in the walk's
  output. The walk's parser now takes **`--bake-lights`** at the export's
  own default and `cmd_walk` hands it to the export, so the package stays
  baked and the walk shows what ships; `--no-bake-lights` is the quicker
  look, and leaves the package unbaked.
- **The shot bot counted a flickering tube as z-fighting.**
  `Ladder_ladder_0_base` failed at 1.39% fighting. The same station with
  the camera not moved at all read 1.27%, twice; every other station read
  0.00% still; the same station in 1.36.0's install test read 0.12%. A
  failing tube in that room (Lux 0.74.0 puts one in a room) changes
  between two frames whether the camera moves or not. `_shoot` now takes
  two **still frames** bracketing the moved one, and `_jitter_diff` judges
  only pixels the still frames agree on, reporting the rest as
  `animated_pct` -- printed by the walk's summary, judged nowhere. The
  verdict and its calibration (0.5%, between the control's 2.02% and
  sparkle's 0.12%) are unchanged.

**Proven on the real thing:** the patched bot run on install test 5's own walk preview passes all five stations, Ladder_ladder_0_base at 0.12% fighting (install test 4's figure) with 1.44% reported animated, and run on the bot's z-fight control (two quads 0.01 mm apart, `docs/findings/shotbot_sparkle/zfight_control.tscn` in the factory) still fails it at 2.02% fighting and 0.00% animated, the figure the shipped bot reads on the same control.

**Tests:** 2 more in `tests/unit/test_shotbot_fights.py`, 2 in
`tests/unit/test_walk_keeps_the_bake.py`. **Suite:** 2,226 passed, 14 skipped, 1 xfailed, exit 0 (the 2,221 of 0.178.2, the four new cases and the sibling guard's case for the new file; the draft's two test files proven first on a fresh clone, 9 passed).
