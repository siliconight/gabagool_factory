# The freight terminal's containers: Zoo's cargo container, recorded short side first (roadmap 267)

**What it was for.** Roadmap 267's last named word. freight_terminal_a01's four `container` volumes, 6.0 x 2.4 x 2.6 m,
were built as plain boxes -- Zoo planned them `prop_delco_1997_04_w600_d240_h260_mmetal` -- though Zoo has drawn the
ISO container since 0.82.0. Deli Counter records every hinted volume long side first, as the module's WIDTH, and Zoo's
`cargo_container` is long in DEPTH (2.3-2.5 m wide, 2.9-13.8 m deep), so no word could route them.

**What changed.** Deli Counter 0.245.0 (147111ee; `patches/patch_dc_depth_long.py`, `patches/dc_depth_long/`):
`prop_species.DEPTH_LONG` holds the routed species whose genome's whole depth range lies above its whole width range
-- ten Zoo species have that shape, one is routed, `cargo_container` -- and `long_axis_first(size, species)` records one
with its long side as the depth, turned 90 when that side is x. `container` routes to the species; the four are
written in its own `metal_painted`. `recorded_turn` is the one turn the two front readers (`level_design._front_turn`,
`lights._front_bearing`) ask now.

**REFUTED, kept: "the composer that mirrors it".** Roadmap 267's note of 2026-10-20 said the fix was "a depth-long rule
in `long_axis_first` and the composer that mirrors it". The composer mirrors nothing: `themed_tscn._fit_rotation` scores
each quarter turn by the module's placed footprint against the greybox slot's and tries the slot's own first, so a
2.4 x 6.0 module recorded at 90 lands on the 6.0 x 2.4 box at 90. Deli Counter alone changed, and the package below
places all four at 90 about the vertical.

## The level that shows it

Cold run 9364 (`docs/cold_runs/cold_9364/NOTES.md`): bank_block_001 at seed 9082, whose lot is bank_branch_a02,
freight_terminal_a01 and twin_a01. 0 interventions. In its package:

- **The module was built and placed.** `zoo_kit_build.freight_terminal_a01` built
  `prop_cargo_container_delco_1997_06_w240_d600_h260.glb`; the composed scene before the merge
  (`presentation_compose`'s `lot/freight_terminal_a01/site.tscn`) instances it as `container_0` to `container_3`, each
  `Transform3D` basis rows `[0, 0, -1], [0, 1, 0], [1, 0, 0]`, its 6 m along the building's x, at the volumes'
  centres; the door end faces west on all four.
- **The collider is the greybox box, as before.** The package's `lot/freight_terminal_a01/site_base.glb` carries
  `container_0_col-convcolonly` to `_3`, each 6.0 x 2.6 x 2.4 (Godot x, y, z) at its container -- the species does
  not own its collision (`prop_species.SPECIES_OWNS_COLLISION`), so the cover a body meets is the box it always was.
- **The export's gates:** 0 surfaces on a greybox material; closure ok, 0 issues over 83 resources.

## What it costs: 40 of the building's 188 merged meshes

`container_draws.py` reads the package's merged meshes (Level Factory's building merge writes one material to each)
and the pre-merge modules (`container_draws_9364.out.txt`). Each of the container module's 10 materials is carried by
exactly 4 merged meshes -- one per container, the four standing 9 m apart in `cross_dock`, one to each 6 m merge cell
-- and no other merged piece wears any of them (the vending machine wears the same black, and stands whole in the
west hall, instanced outside the merge with no override under it): **40 of freight_terminal_a01's 188 merged meshes
are the containers'**. The boxes they
replace were `metal`, a material their cells may already have carried, so they added at most four: **+36 to +40
submissions with all four in view**, about 0.13 ms at 3.47 us a draw (the slope of cold run 9062's measurement:
1,730 draws 9.49 ms, 6,376 draws 25.59 ms). An estimate of the frame cost, not a price: the backdrop yards' 97
containers measured +27.7 draws a heading with p95 inside the controls' 0.12 ms spread (roadmap 228's yards record),
and a change this size reads inside the harness's noise, so the count is the measurement that can move.

**CORRECTED: Deli Counter 0.245.0's changelog says nine draws a container and up to 36.** It read nine off the
module cold run 9279 shipped (`module_surfaces.out.txt`: the walk copy's cover module, byte-identical to 9279's
package's -- 9 visual meshes, 9 materials, 3,296 triangles with its collider), which carries no touch-up patch. This
run's module carries one: 10 visual meshes on 10 materials, 3,372 triangles. A container is nine or ten submissions,
by its patch.

**What the cheaper container would buy:** its colours moved into the `Wear` vertex colour, as the service counter and
the coffee island carry theirs -- one or two submissions a container, 4 to 8 here where it is 40, and the same saving
on every container Lot stands as cover or in a yard. Filed as roadmap 280; it waits on whether cover modules draw
vertex colour.

## Frames

`shots.sh` frames six stations in freight_terminal_a01's own frame, turned into each package's site frame by
`docs/findings/teller_queue_275/stations.py`; `compose_pair.py` puts each station's BEFORE beside its AFTER.

- **BEFORE** is `_runs/walk_export_precinct_yard_001`: its LF_MANIFEST names precinct_yard_001 at seed 9708 on Deli
  Counter 0.222.0, Level Factory 0.211.1 and Zoo 1.112.0, a clear afternoon in the `delco` theme. It is the newest
  package on this machine that places freight_terminal_a01, and it is an older toolchain and another level: the frames
  show what the containers WERE, not a controlled comparison of anything else in them.
- **AFTER** is cold run 9364's walk copy, `_runs/walk_export_bank_block_001`: a rain afternoon in `delco_1997`.

`containers_before_after_inspect.jpg`, the inspection light: four dark rust-brown boxes become four blue ISO
containers -- corrugated sides, the carrier's name down each side, the door end with its locking bars and owner code
at the west, the corrugated blind end at the east. `containers_before_after_lit.jpg`, each level's own light: a dim
hall either way; the containers read by their corrugation and lettering where the boxes were flat dark slabs.

**Seen, and the walker's call:** the four are ONE module -- the same blue, the same carrier, the same owner code. A
yard's containers differ, and an owner code is one box's. Each container its own `variant` would draw its own paint,
carrier and code -- Zoo seeds a module's streams by its stem (`bpylayer/build.py`), which a variant marks `_n<k>`, and
`container_forms.resolve` takes the paint, the marks and the patch each from its own stream, so two may still match by
chance. Standing a cell apart, they would add no submission (the merge already writes each cell's container into
meshes of its own), only build time.

## Files

- `shots.sh`, `compose_pair.py`: the frames, as above.
- `container_draws.py`, `container_draws_9364.out.txt`: the merged meshes by material.
- `glb_surfaces.py`, `module_surfaces.out.txt`: a GLB's meshes, primitives, materials and triangles, read from its
  JSON chunk -- this run's container and 9279's.
- `containers_before_after_inspect.jpg`, `containers_before_after_lit.jpg`.
