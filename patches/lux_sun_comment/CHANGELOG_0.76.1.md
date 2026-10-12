## [0.76.1] - a correction: the bake traces the sun's occlusion whatever its shadow flag

**No behaviour changes.** 0.76.0's entry below, its commit message and `_apply_sun_mode`'s comment said
a static sun baked with its shadows off "bakes flat" -- "measured, the factory's B arm". It was never
measured: B's frames were in no table. Measured since in the factory (`docs/findings/lux_tiers/`, cold
run 9264's level under `blue_hour`): arm B, the sun static with its shadow flag OFF for the bake, and
arm B2, ON, read the same frames at six stations -- a mean difference of 1.6 to 2.5 levels and at most
0.01 % of pixels over 16, a re-bake's own noise -- and both differ from the live unshadowed sun by 3.3
to 11.7. So 0.76.0's editor branch works for a different reason than it gave: the sun is STATIC there,
so the bake carries its light (left dynamic, the lightmap would hold only its bounce, and at run time a
static sun lights no lightmapped surface); its shadow flag, still as the preset and the tier ask, does
not change the bake.

- **`_apply_sun_mode`'s comment** says that, and names what the lightmap does not hold: what moves, and
  anything a level loads outside the baked scene, which take the sun with no shadow -- in the factory,
  the backdrop, which Level Factory does not bake (`docs/findings/lux_tiers/backdrop_split.py`).
- **`tools/sun_bake_selftest.gd`'s docstring** names the factory's cold run 9265 as the editor's proof:
  0.76.0 in a real drive, its frames reading as B2 inside a re-bake's noise.
