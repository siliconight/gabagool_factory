## [0.164.0] - The sky is in the bake

**The walker's call, 2026-10-09: "yes bake the sky in".** The bake's
`LightmapGI` takes `environment_mode = 1`, the scene's environment, in place
of `0`, none (`packages/exporting/light_bake.py`, `BAKE_TSCN`). The
environment is the WorldEnvironment LuxRoot builds. LuxRoot is `@tool`, so
the editor's bake has it.

**Why.** 0.131.0 shipped `0` with no reason recorded. A lightmapped surface
takes no ambient at run time (measured: `docs/findings/light_breakdown/` at
the factory root), so no baked wall or floor had ever received sky light.
Every surface the sun missed was lit by sun bounce and lamps alone. The
walker's lighting spec names the missing term: illuminance is sun + sky +
bounce + lamps (`docs/reference/Godot_4_7_Natural_and_Artificial_Lighting_Spec.md`).

**Measured before the change, by re-baking cold run 9214's level with each
mode** (`tools/lux_rebake.py --bake-environment`; light check frame means,
luma after the grade; `docs/findings/lighting_spec_vs_lux/`):

| slot (preset) | outside | rooms |
|---|---|---|
| a clear afternoon (Delco Summer Afternoon) | street cameras +15.1 and +21.4, facades +2.7 to +15.9 | -0.1 to +1.2 |
| Heavy Rain | +0.3 to +2.3 | -0.1 to +0.1 |
| Blue Hour | +0.5 to +3.7 | -0.1 to +0.1 |
| Delco Night | two outer facades +3.3 and +4.4, the rest 0.2 or less | -0.2 to +0.1 |

- **On a clear afternoon,** shade goes from near black to daylight
  (`sky_in_the_bake_clear_afternoon.png`). The light check goes from 2
  WARNs to 0: by day the street now reads brighter than the rooms, as it
  should.
- **A sealed room takes no sky:** every room moved 1.2 or less, at every
  slot.
- **The cost.** The bake took 90.2 s against 91.2 s in the afternoon, and
  83.4 s against 81.3 s at dusk. At run time it costs nothing, since the
  light lives in the lightmap.

**What it invalidates.** Exterior luma from a package baked by 0.131.0 to
0.163.1 is not comparable with one baked from here on: same level, same
station, more light outside. The rooms are comparable. `tools/lux_rebake.py
--bake-environment none` bakes as before, for a control.

**Tests.** `test_the_bake_takes_the_sky` in `tests/unit/test_light_bake.py`
fails on 0.163.1, finding `environment_mode = 0`. The file's other 14 pass
on both.
