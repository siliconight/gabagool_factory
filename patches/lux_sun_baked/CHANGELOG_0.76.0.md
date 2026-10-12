## [0.76.0] - the sun is baked while the lightmap shows

**Factory roadmap 243, the walker's call of 2026-10-12** ("bake the sun by default", after the frames).
Lux built the sun as a dynamic light: Level Factory's lightmap held only its bounce, and its light and
shadows were drawn live every frame. Measured in the factory (`docs/findings/lux_tiers/`, Level
Factory's 53 station headings, GL Compatibility, cold run 9264's level under `blue_hour`): the sun's live
shadows were 1,854 of a heading's 2,642 draws and 3.56 ms of its 8.0 ms median p95 -- the largest
single cost measured on a level. Baked WITH its shadows and drawn without them, the same level read 788
draws and 4.42 ms, and its frames kept High's look but where they could not: what moves casts and takes
no sun shadow, the baked shadows are as soft as the lightmap's texels, and sunlit facades the live map
left dark read lit.

- **`LuxLighting._apply_sun_mode`**, the one place the sun's bake mode and shadow are decided:
  - in the editor, where Level Factory bakes, the sun is STATIC with the preset's shadows, so the bake
    traces them (a static sun baked unshadowed bakes flat: measured, the factory's B arm);
  - at run time it is static and unshadowed while a lightmap shows;
  - and dynamic with the preset's shadows whenever none does -- no lightmap (a package exported without
    a bake), the power cut (`set_fixtures_powered(false)` hides the lightmap, and daylight must not go
    out with the lamps), or baked lighting switched off. The tier's `allow_sun_shadows` still rules.
- **Called** where the preset is applied and wherever the lightmap's state changes (`_sync_lightmaps`:
  binding, the power, the baked-lighting switch). A run-time change of the sun's bake mode hides and
  shows it to pair it again with the geometry, `set_baked_lighting`'s finding.

**Self-test:** `tools/sun_bake_selftest.gd`, headless: no lightmap, a lightmap bound, the power cut and
back, baked lighting off and on, a tier forbidding sun shadows, and a preset asking none. 12 checks PASS on 0.76.0; on 0.75.0 five fail, every case asking the sun static and unshadowed while a lightmap shows (it stayed dynamic and shadowed)

**Beside it:** every other self-test in `tools/`, 23 of them, exits 0 on both 0.75.0 and 0.76.0, each run as its docstring says (windowed on GL Compatibility where it opens a window, headless otherwise)
