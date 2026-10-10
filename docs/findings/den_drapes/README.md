# A den's windows drawn shut (Zoo 1.91.0, Deli Counter 0.205.0, roadmap 219 note 2)

**Question.** The walker, walking club_block_014 on 2026-10-09: "the windows
in any 'den of sin' building should have curtains or drapes or blinds So
people outside can't see in, and you keep the streetlight light out of the
club", with a red drape as the comp. Three things needed answering:
- what a drape is in Zoo's terms, and whether it reads as cloth from both
  sides;
- where it hangs;
- what happens to the light the window let in.

**Frame and units.** Metres. Zoo's frame: x along the window, the room at
-Y, z up from the hem. Deli Counter's spec frame: the footprint centred on 0,
z off the ground floor.

## The piece (Zoo 1.91.0)

`window_drape`: two velvet panels drawn shut under a box pelmet, oxblood
(`club_forms.VELVETS[0]`).
- **The pleats are geometry,** 12 facets a 12 cm pitch. At that count the
  sharpest turn between neighbouring facets is 43.8 degrees, under Zoo's
  50-degree smoothing split. At 8 facets it is 60.7, and the crest would read
  as a ridge. `max_facet_turn` measures it.
- **Triangles:** 944 at a 1.5 m window, and 404 to 1,844 across the genome's
  corners.
- **The coincident-face census** (`zoo/tools/coplanar_census.py`, Blender
  5.1.1): "3 builds, 0 with coincident pairs, 0 that did not build".

**The frames.** `build_drape.py`, run in Blender, built the piece at
strip_club_a01's window (1.5 x 0.16 x 1.62 m) to a GLB. `probe.gd` framed it
in Godot 4.7, GL Compatibility, against a dark backdrop, then quit. It saved
`run.log` and two frames:
- `room.png`, from the room under a warm low light: pleated red velvet under
  its pelmet, the hem waved;
- `street.png`, its back under a cool light, which is what the street sees
  through the glass: pleated cloth, not a board.

`velvet` has no Pixelcoat pack, so it is flat colour: matte, no sheen. These
are frames of the piece alone, under the probe's own lights, not of a level;
the probe's warm lamp is strong, and the red reads brighter than a dim club
will show it.

## Where it hangs (Deli Counter 0.205.0)

`level_design.plan_den_drapes` hangs one on every window of a strip club,
off the window the builder cuts. The migration (`migrate_den_drapes.py`)
printed:

    window_drape_s0_1 at (12.0, -11.74, 2.475) 1.5 x 0.16 x 1.55      strip_club_a01
    window_drape_s0_1 at (11.0, -11.74, 2.475) 1.5 x 0.16 x 1.55      strip_club_a03
    window_drape_s1_1 at (-11.0, -11.74, 5.725) 1.7 x 0.16 x 1.65     strip_club_a03
    window_drape_s1_2 at (11.0, -11.74, 5.725) 1.7 x 0.16 x 1.65      strip_club_a03

- **a01's window is built at x 12.0,** read off
  `build/strip_club_a01.gameplay.json`, where the spec's `pos * run` says
  11.9: the builder snaps openings to the grid, and the drape follows the
  builder.
- **The drape runs** 0.15 m past each jamb and 0.10 m under the sill. Its
  pelmet stops at the ceiling's clear height, 3.25 m, which is 0.05 m over
  a01's 3.2 m head.

## The light

A window derived a `window` area light standing for the street through the
glass. A draped window derives none (`lights._drapes_window`). The window is
still counted first, so the next window's light keeps its id.

## What this does not show

- **A level at night,** owed by the proof run's frames: the drape lit by the
  club's washes, and the street side lit by the street.
- **Gameplay.** The drapes take the view through four windows that sit 1.4
  to 1.8 m off their floors.
  - Deli Counter's `sightlines.py` is intel, never a gate. It treats every
    opening as see-through, its worst case.
  - It counts a volume as blocking only if it is at least 1.6 m tall and
    spans the 1.6 m eye height over its floor (`_tall_vol_rects`).
  - a01's and a03's ground-floor drapes, 1.55 m tall from 1.7 m up, do not
    block. a03's upstairs pair, 1.65 m spanning 5.2 m, do.
  - What the drapes do to a fight was not measured.
