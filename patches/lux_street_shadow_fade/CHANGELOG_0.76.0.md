## [0.76.0] - a street light's shadow stops 30 m from the camera

**Factory roadmap 240, the pole line's price.** The shadow budget (roadmap 60) gives its maps to
the street lights first, and every shadowed street light in view draws its shadow pass whether the
player stands under it or 80 m down the street. Lot 0.118.0's pole line hangs its lamps at 7.50 m
where a steel lamp hung at 5.92, so each pass takes in more of the street: priced afterwards at
Level Factory's stations (`docs/findings/pole_line/` in the factory, 53 headings, GL
Compatibility), cold run 9262's twelve shadowed street lights cost 300.1 draws a heading against
133.4 for 9261's lamps, and the line +170.3 a heading over all. A steady street light is baked, so
its map at runtime shades only what moves through its pool; a failing one is live and its map
shades the street as well. Both are worth their draws where the player is.

- **`LuxStreetlightRig.shadow_fade_m`**: past it from the camera, a lamp's shadow fades out over
  `SHADOW_FADE_LENGTH_M` (5 m) by Godot's own `distance_fade_shadow`, and the light itself does
  not (`LIGHT_FADE_NEVER_M`). 0, the default, leaves a rig as before.
- **The loader's `streetlight` branch sets `STREET_SHADOW_FADE_M` (30 m)**: one span of a pole
  line -- Lot's poles stand at most 36 m apart and 31.2 to 33.2 on 9262's main road -- so the
  player keeps the shadow of the light overhead, and of both when between two. A wall pack and a
  canopy wash keep 0: their shadows stop light washing through their own wall, which matters from
  inside at any distance.
- **Measured before it was written**, the same four properties set in the rig vendored into a
  copy of 9262's package: -154.0 draws a heading (median -46, at most -740), 16.2 over 9261's
  lamps. The same properties written on the scene's lamps moved nothing -- `_rebuild()` frees the
  saved lamps and builds its own at runtime -- which is why it lives in the rig.

**Self-test:** `tools/street_shadow_fade_selftest.gd`, windowed on GL Compatibility: the loader's
pole lamp carries the fade, a wall pack does not, and in a frame a slab under the shadowed lamp
blacks the pool from inside the fade and not from past it, the fade off blacking it from both.
RESULT_SELFTEST

**Beside it:** RESULT_OTHERS
