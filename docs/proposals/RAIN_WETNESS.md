# Wetness on what the rain lands on (roadmap 157, slices 2-4)

Rain falls in a shipped package (Lux 0.35.0, LF 0.83.0, walked in cold runs
9052 onward) and lands on nothing: every surface is as dry as it was. The
walker, 2026-09-16: "improve the rain effect to include wetness on surfaces
that are being rained on", with two references, transcribed and linked below.
This is what they say, what this pipeline would have to do, and what has to be
measured before any of it is believed.

## Reference A -- raindrops that sit on a surface and dry out

A Godot shader tutorial (the walker sent the transcript). What it does:

- **One texture carries four channels.** Red and green are the X and Y of a
  normal map for the drops; the Z is taken as 1.0 in the shader, on the
  argument that a drop's normal is near-vertical anyway. Blue holds a random
  grey value PER BIG DROP (baked in Blender with a geometry-node "mesh island"
  index feeding a random value, so every drop gets its own number). Alpha
  holds the small droplets that never move, because surface tension holds
  them.
- **The animation is arithmetic, not frames.** A drop's mix ratio is
  `fract(drop.b - TIME * k)`: it falls, its influence decays, and when it
  reaches zero it wraps to one and the drop "lands" again. Because each drop
  starts from its own grey value, they land and dry at different times. The
  ratio is multiplied by the blue channel again so that where there is no
  drop, nothing changes.
- **Wetness is more than a normal.** The drop normal is mixed into the
  surface's own normal; roughness goes to 0 where a drop sits (water is
  smooth) and specular up; the albedo underneath is distorted slightly through
  a noise-offset UV, as a real drop refracts what is behind it.
- **Rain does not fall on a ceiling.** The mix is gated on the WORLD-space
  normal, so downward-facing faces stay dry.

**How it fits here, and the catch.** It needs a ShaderMaterial (or a
`next_pass`) on the surfaces that get wet. Every surface a package ships is a
StandardMaterial3D -- 295 of 295 in the 9052 walk copy, 0 ShaderMaterials --
which is exactly why Lux's `surface_wetness` reaches nothing today. LF 0.89.0
established the mechanism for adding a pass at import (the CRT sync roll:
`zoo_worldskin.gd` attaches a `next_pass` to named materials, measured below
the noise floor in GPU cost, with the depth-offset trap recorded). The same
route can carry wetness: at import, exterior surfaces get a wet pass driven by
a Lux uniform. The texture itself is authorable in the factory -- Pixelcoat's
generation_7 pipeline already makes wet maps no grammar uses.

## Reference B -- puddles with ripples and reflections

`https://godotshaders.com/shader/rain-puddles-with-ripples-and-reflection/`
by shadecore_dev (CC0), which includes marcelb's SSR and Zavie's ripple
effect. A POST-PROCESS spatial shader on a fullscreen mesh under the camera
(the page also gives a single-triangle setup worth about 20% over a quad):

- Rebuilds each pixel's world position and normal from the depth buffer, so
  it needs `hint_depth_texture` and `hint_screen_texture`.
- Puddles are two octaves of value noise thresholded against the surface's
  upward-facing component, so puddles form only on horizontal ground.
- Ripples are Zavie's: rings hashed per cell, radius growing with TIME,
  contributing a normal offset.
- Reflections are screen-space ray marching, with a fallback puddle colour
  where the ray leaves the screen.

**The catch, and it is the important one.** This is a screen-space
post-process with a depth-texture read and a ray march. Packages ship on GL
Compatibility, where Lux already measured what does and does not exist
(no particle trails, no sub-emitters, no volumetric fog; box and heightfield
collision work). Whether `hint_depth_texture` and screen-space reflection are
available and affordable in Compatibility on this hardware is NOT known and
must be measured before this shape is chosen -- the shader's own page assumes
a renderer this pipeline does not ship. If it is unavailable, slice 3's
existing plan stands: puddles as flat Zoo species placed by Patina, with a
cheap ripple normal, no SSR.

## What each owner would do

- **Lux** owns the weather state (`LuxWeatherProfile.surface_wetness`, already
  in the presets: Heavy Rain is 0.85) and would drive a single wetness value,
  plus a "rain is falling here" mask consistent with the rain colliders that
  keep interiors dry (Lux 0.35.0's boxes).
- **Level Factory** attaches the wet pass at import, as 0.89.0 does for CRT
  screens: choose the surfaces by the same evidence the vertex-colour pass
  used (a named material, not a guess), and keep interiors out of it.
- **Pixelcoat** authors the drop texture (four channels as above) and any wet
  albedo/roughness response, in its own grammar so the look stays the
  walker's and not a downloaded asset's.
- **Zoo / Patina** own puddles as geometry if the post-process route is
  refused.

## What must be measured before building

1. Does GL Compatibility on this machine give a usable `hint_depth_texture`
   and screen texture at 1600x900, and at what GPU cost? (Reference B is
   unusable here without it.)
2. Cost of a wet `next_pass` over the exterior surfaces of a real package,
   the way the CRT pass was priced: on/off, several stations, with the
   no-rain control.
3. Does the wet look survive the retro treatment? Pixelcoat's audit exists
   for exactly this, and a mirror-smooth puddle is not a 1997 Delco street.
4. Interiors stay dry: the same walk that proved rain stops at a roof
   (every under-roof frame rose 0 pixels) must prove wetness does too.
