## [0.25.0] - gutters at the eave, and downspouts to the ground

The walker, 2026-10-04: "also we need rain gutters".

### Fixed
- **The gutters stood on top of the parapets.** Deli Counter 0.177.0 made
  each parapet tile a wall slot on the storey above the top floor, so
  `roofline_slots` -- "the top storey's exterior walls" -- picked the
  parapets. Measured on cold run 9151's own orders:
  - `gs_empty_rowhome_f`'s ten gutters sat at z 9.92 on `parapet_*` slots,
    the top of the parapet, where 9148 had twenty-two at 8.92 under the
    roof;
  - the freight terminal's sat on its parapet top at 6.92.

  No gate looked at a gutter's height. Parapet slots are now left out
  before the top storey is found, so a gutter hangs at the eave again.

### Added
- **Downspouts** (`framing.downspout_orders`), emitted with `--gutters` so
  the pipeline's existing flag brings them. A gutter reads from the street
  by the pipe that carries its water down -- the pale leader down the party
  wall in the walker's South Philly photograph -- and nothing drew one.
  - **On the faces somebody sees:** every roofline face with a window, door
    or breach on any storey. A blank side wall -- an Empty's party wall --
    gets none.
  - **One a face, one more per `DOWNSPOUT_EVERY` (12 m) of gutter.** That
    figure is chosen from the 30-40 ft rule of thumb, not derived; no roof
    area is modelled.
  - **A short face takes a seeded end** (`DOWNSPOUT_INSET` 0.15 m in, at the
    corner or party line). A longer one takes both ends, and the rest at the
    module seams nearest an even spacing.
  - **Clear of the openings,** judged by the keep-out the filter already
    enforces (`openings.keep_out_boxes` / `hits`), so placement and filter
    are one test. A blocked end gives way to the other; an interior pipe
    slides to the next seam out; a pipe with nowhere clear is left out.
  - **From the gutter's underside to the floor of the face's storey 0.**
    `size` is the length and `pos` its middle, as a conduit's.
- `openings` learns the new cover: `_ZOO_CROSS["downspout"]` 0.076 (Zoo
  1.67.0), and `_run_axis` reads it as a vertical run like a conduit.

`version.py` is 0.25.0 with `VERSION`.

`tests/test_downspouts.py`:
- gutters hang at the eave, not on the parapet (fails on 0.24.0);
- a downspout comes down each face with an opening and no other (fails on
  0.24.0: none at all);
- it runs from the gutter's underside to the ground, outside the face, at
  one end;
- it takes the end clear of the openings, either way round;
- a 60 m face gets five;
- the same seed places the same pipes;
- the filter reads a downspout as a vertical run.
