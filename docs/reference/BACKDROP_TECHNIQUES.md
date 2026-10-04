# Backdrops: what the walker's technique references give a 3D, free-camera, multiplayer game

The walker, 2026-10-04, between the Empties and the backdrops, sent four
references:
- Godot's `ParallaxBackground` class page;
- two transcripts of game-background lessons: environment design basics,
  and a night-city environment from reference to render;
- J. Meiners' "Pre-Rendered Backgrounds" article.

This file is the reading of them against our constraints, which decide what
transfers:
- a FIRST-PERSON camera the player moves freely;
- GL Compatibility on hardware nobody here has seen;
- every frame paid on every client (`CLAUDE.md`, performance over look);
- a 1990s Delco/Philly world (`EMPTIES_COMPS.md`,
  `PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md`).

## What each reference says, and what transfers

**Godot `ParallaxBackground`.** A 2D node: it inherits `CanvasLayer`, scrolls
`ParallaxLayer` children at different rates, and is deprecated in favour of
`Parallax2D`. NONE OF IT RUNS IN A 3D SCENE. In 3D, parallax is not a trick
to add: geometry at a distance moves across the view at the rate its
distance gives. What carries over is the idea of LAYERS -- here, distance
bands, each built for what the eye can resolve at that range.

**Pre-rendered backgrounds (Meiners).**
- **What it is:** stills rendered offline, composited with real-time
  characters using a pre-rendered depth image, so a body can pass behind
  scenery. Blender and game cameras match exactly; the camera is fixed per
  view and swaps between views. Custom C engine, OpenGL ES 2.0 / GL 3.2.
- **Limits it names:** fixed angles, depth precision, shadows that cannot
  fall on the background.
- **Fit here:** a pre-rendered VIEW needs the fixed camera this game does
  not have; move the player 20 m and the background is wrong.
- **What transfers:** the far band. Beyond about a kilometre, the parallax
  a player can make by walking the level is under a pixel, so the skyline
  can be rendered ONCE from the level's centre into a panorama and baked
  into the sky. It costs no draw, no geometry and no light -- it is the
  sky.

**Environment design basics (lesson 1).**
- Depth reads through contrast and value: far is lighter, lower in
  contrast and simpler; each nearer layer is darker, sharper and more
  detailed.
- There is always one light source, and highlights, midtones and cast
  shadows agree with it.

**A night city from reference to render (lesson 2).**
- Reference first, then thumbnails, blocking big shapes before small ones.
- Size sells distance.
- "Shapes that build an impression" over drawing every crack.
- Detail and contrast belong closest to the viewer; the far is simpler, so
  the eye knows where to look.
- At night: bright lights out of the dark.

## The bands this game gets

1. **Near, 0-60 m: the playable edge and the Empties.** Full 3D, collision,
   the art pipeline (Deli Counter 0.174.0, Level Factory 0.137.0).
   - The fence marks where playable stops (`fence-marks-the-playable-edge`).
   - Highest detail and contrast, and the bright lights: storefront neon,
     lit windows at full size, streetlights.
2. **Mid, 60-400 m: silhouettes with lit windows.**
   - Low-poly massing -- rowhouse runs, a factory, a steeple, a water
     tank -- built from the same kit vocabulary and wearing one atlas of
     dark facades and lit window dots.
   - No collision.
   - One MultiMesh per block or per band side, so it stays a handful of
     draws however many buildings it holds.
   - Fogged toward the sky's colour with distance: Godot's per-material
     depth fog, which GL Compatibility draws without a screen-space pass.
   - Lower contrast than near, fewer and smaller lit windows.
3. **Far, 400 m to the horizon: a pre-rendered panorama in the sky.**
   - Rendered from the level's centre out of the backdrop guide's recipes:
     Philadelphia skyline from the edge of the city, rowhouse sea, SEPTA
     corridor, ridge and water tower, refinery flare.
   - Baked into the sky the Lux stage already draws: zero draws.
   - Lightest, flattest and simplest of the three.
   - At night, silhouettes against the sodium skyglow, lit windows as
     pin-points.

**THE NIGHT VERSION OF THE DEPTH RULE**, since most of this game's frames
are night.
- The daylight rule says far is lighter.
- At night, far is a darker silhouette against a lighter, warmer sky glow:
  sodium-orange on the horizon from the city's own lights.
- Lit windows shrink and dim with distance.
- The near street keeps the brightest highlights and the hardest contrast.

The same rule stated once: contrast and detail fall with distance; the
value moves toward the sky's.

**ONE LIGHT SOURCE.** The key light of each band agrees with Lux's preset:
the moon or the sun, the same side. The far panorama is rendered under the
same preset as the level it hangs behind, and re-rendered per time of day
-- it is baked, and a baked sky lit from the wrong side is the cheapest way
to make a level look pasted on.

## Price, before it is built

- **Far:** nothing at runtime -- a sky texture already sampled.
- **Mid:** a few MultiMesh draws per side, priced on the harness when built.
- **Near:** the Empties' own cost, which their merge-by-material step is
  for.

Nothing here is a screen-space post-process or a depth-texture read; both
are on `CLAUDE.md`'s refused list.
