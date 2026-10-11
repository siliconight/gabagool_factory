## [0.177.2] - The Lot adapter publishes the paint meshes

**Cold run 9234 stopped at the export's closure gate** (0 interventions,
and a failed run all the same): Lot 0.114.0 writes the road paint as one
wavefront mesh a colour beside `site.tscn`, declared as a Mesh
ext_resource, and `LotAdapter.collect_outputs` published
`.tscn/.json/.csv/.glb/.gd/.png` -- so the composed site referenced two
files that were never there, and the gate refused the package over two
relative references resolving to nothing. Correctly, and three stages
after the drop: the same shape as cold run 9016's skins (the `.png` that
joined the list on 2026-09-12).

- **`.obj` joins the published suffixes.** A published artifact has to be
  the whole artifact. One test stands a scene, its mesh and its manifest
  in a work dir and reads them back.
- 0.177.1's `mark_imports` is unchanged and now has sidecars to mark.

**Tests:** 1 in `tests/unit/test_lot_paint_published.py`. **Suite:** RESULT_SUITE.
