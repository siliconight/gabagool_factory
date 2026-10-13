## [0.213.0] - mid-rise Empties: five to twelve storeys of brick, out of today's streets

**Factory roadmap 241, step 1.** The walker, 2026-10-11, chose a new urban level type: mid-rise Empties
standing at the sidewalk line in continuous street walls, the enterable buildings among them, and the Delco
strip levels left as they are (the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`). This is the
family's first cut.

- **`presets.empty_midrise`**: a brick block of `floors` storeys, its windows in regular bays about 3.2 m
  apart across its width on the front (S) and the back (N), a lobby door at grade in one front bay and a
  service door behind it. The sides are left unlisted, so `auto_exterior` seals them as party walls. It has
  a parapet, is 15 m deep with a 3.1 m storey, and has a membrane roof. It is an Empty in every respect
  this builder keys on `facade`: shut doors, painted windows, only its roof slab.
- **`presets.EMPTY_MIDRISES`**: six blocks, `gs_midrise_a` to `_f`, of 5, 6, 7, 8, 10 and 12 storeys,
  15 to 24 m wide, in the rowhome family's three bricks and one stone front. No two are the same height,
  so a layout can draw them by cause, taller away from the action. `REGISTRY["empty_midrise"]`; six specs
  are written from the table and `specs/CATALOG.md` is regenerated.
- **Named out of today's streets.** Level Factory hands every `gs_empty_*` in the library to any brief
  that stands a terrace (`building_library.empty_rows`). Under that prefix these would stand in a Delco
  street, so they are `gs_midrise_*`, and they wait for the urban brief that asks for them (241, step 3).
  As facades they are already outside the enterable draw.
- **Not here:** the rooftop penthouse, the corner variant with a shop at grade, and the bay-window variant.
  Each needs a capability this builder does not have yet.
- **`navgate_baseline.json`** records the six UNJUDGED, as it records `gs_facade_rowhome` and the
  twelve rowhome Empties: an Empty has no interior for a spawn marker to stand in, so the nav gate
  checking zero markers is the correct outcome. `counts.unjudged` 21 -> 27.
- `test_empty_midrise.py`: the family's spread, the specs as the preset's own output, the prefix, the
  Empty's flags, the regular bays on every storey front and back, one door a face at grade, the party
  walls, and every block loading with its front to the street. It fails to import on 0.212.0.

**Built:** the six shells built by `build.py` under Blender 5.1.1, 2 to 3 s each: 223, 291, 367, 383, 557 and 615 slots, GLBs of 130 to 259 KB, every validation manifest `passed` with `facade` true, and no warning in any build log. Shown in greybox as a street wall beside a rowhome Empty, each piece tinted by its name (the factory's `docs/findings/urban_midrise/`)

**Suite:** 1,449 passed, 2 skipped (the bpy round-trip fixtures, run in their own process), exit 0: 0.212.0's 1,441 and `test_empty_midrise.py`'s eight, which fail to import on 0.212.0, run against an export of it
