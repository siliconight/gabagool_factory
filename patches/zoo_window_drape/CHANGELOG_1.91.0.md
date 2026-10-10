## [1.91.0] - window_drape: two velvet panels drawn shut across a den's window

### What the walker asked for

**2026-10-09, walking club_block_014 (cold run 9213, roadmap 219 note 2):**
"the windows in any 'den of sin' building should have curtains or drapes or
blinds So people outside can't see in, and you keep the streetlight light out
of the club". The comp was a red drape. strip_club_a01's one window was clear
glass, and Zoo had no drape to hang in it.

### What it is

**A new species, `window_drape`.** Two heavy velvet panels are drawn shut
under a box pelmet, hung on the room side of the glass, with the front (the
room) at -Y.
- **The colour** is oxblood, the club chairs' first velvet
  (`club_forms.VELVETS`): the comp's red, darker, as a dim room shows it.
- **Excluded:** tie-backs (a den keeps them shut), a visible rod (the pelmet
  hides it), lace and anything a light shows through.
- **No collision.** The window's own pane seals the opening.

**The pleats are geometry, and their facet count is derived.** A pleat is a
sine across the panel: a 12 cm pitch, a 3 cm swing at the hem and 0.6 of it
under the pelmet, where the rod gathers them. Zoo smooths across an edge
whose faces meet under 50 degrees. At 12 facets a pleat the sharpest turn, at
the crest, is 43.8 degrees, and 27.1 under the pelmet. At 8 facets it would
be 60.7, splitting the crest into a ridge. `max_facet_turn` computes it, and
the tests hold it.

**Both sides are cloth,** because the street sees the back through the glass.
A panel is a closed slab: its pleated front, the same sheet 12 mm behind, its
hem and its two side edges. Its top runs 2 cm up into the pelmet. The panels
share one phase and cross 5 cm at the middle as two parallel sheets. On a
1.5 m drape their gap measures 7.9 to 8.1 mm where they cross: clear of the
coincident-face census's 2 mm, never one through the other.

**The planner is `core/window_drape_forms.py`.** `core/drape_forms.py` is
`dust_sheet`'s, since 0.84.0. This release's patch refuses to write a file
that already exists, which is how the name was found taken.

### The price

- **One material,** so the pelmet and the panels pack into one primitive:
  one draw a window.
- **No texture.** `velvet` has no Pixelcoat pack, so it is the flat colour,
  matte, with no sheen.
- **Triangles:**
  - 944 at strip_club_a01's window (1.5 x 0.16 x 1.62 m);
  - 1,064 at a03's upstairs pair (1.7 m);
  - 404 to 1,844 across the genome's eight corners, against a budget of
    2,000.
- **The library's dens have four windows:** a01 one, a03 three.

### Frames

Built in Blender 5.1.1 and imported into Godot 4.7 (GL Compatibility):
`docs/findings/den_drapes/` at the factory root.
- **From the room,** under a warm low light: pleated red velvet under its
  pelmet, the hem waved.
- **From the street,** its back under a cool light: cloth, pleated, not a
  board.

They are frames of the piece alone, not of a level.

### What it does not cover

- **Hanging it.** Deli Counter (0.205.0) hangs one in every window of a strip
  club, and draws no window light behind it.

### Tests

`tests/test_window_drape.py`:
- the drape is its slot exactly at every genome corner, inside its budget,
  with no coincident faces;
- the pleats stay under the smoothing angle, and 8 facets would not;
- both sides are cloth;
- the panels cross at the middle as two sheets;
- the velvet is the club chairs', with one material and no collision;
- built (Blender-gated): one velvet material, one primitive, no `-colonly`
  proxy.

`tests/test_genome.py`'s species set takes `window_drape`.

**Two guards that count species failed the suite's first run,** as they
exist to: a new species joins each on purpose.
- **`test_coincident_faces.py`'s `CENSUS_BUILDS`** goes from 366 to 369. The
  census was run for the drape in Blender 5.1.1: "3 builds, 0 with coincident
  pairs, 0 that did not build" (404 / 944 / 1,844 tris), recorded beside the
  count.
- **`test_theme_style_resolution.py`'s styled count** goes from 95 to 96,
  for the drape's own `delco` row.

**On 1.90.0:**
- the new file cannot import its planner;
- `test_all_species_load_and_validate` fails on a species set naming a genome
  that is not there.

**The suites:**
- **Zoo:** 4,067 passed, 400 skipped, 1 xfailed in 355 s (`python -m pytest
  -q`). 1.90.0's figures were 4,052, 398 and 1. The new file adds 12 and 1;
  the tests that sweep every species add 3 and 1 more.
- **Under Blender 5.1.1:** the drape's built test passed.
