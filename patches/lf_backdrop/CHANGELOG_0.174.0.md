## [0.174.0] - The backdrop beyond the plate's edge ships as MultiMeshes

**Roadmap 228, step E.** The walker picked E from the edge menu
(`docs/findings/edge_menu/` at the factory root): a chain-link fence at the
plate's edge, rows of rowhomes with lit windows and a water tower behind it,
under a sky-glow. Lux 0.73.0 drew the glow, Lot 0.107.0 the fence, Zoo
1.95.0 the rowhome and the tower, Lot 0.108.0 planned the bands into the
drawn site's `backdrop` list. Nothing in a level showed the houses until
this.

**What ships.** `packages/exporting/backdrop_layer.py` takes the themed
site's drawn spec and the site kit it names (`cover_modules`), and on the
dressing layer's own road (`extract_meshes`, `dressing_scene`) puts
`<site>_backdrop.tscn` and `backdrop/<module>.res` into the package:
- one MultiMesh a module a side, the asset ids carrying the side
  (`<module>__N`), the four sides of a module sharing one extracted mesh,
  so the draws are modules times sides plus the tower and never the houses;
- every order collisionless (`dressing_scene.check_manifest` refuses
  otherwise), no navmesh, no lightmap;
- the entry scene instances it beside the level as it instances the
  dressing (`localize.write_entry_scene` takes `*_backdrop.tscn` too);
- `backdrop_layer.json` says what shipped and why not; a module the kit
  did not build is named and nothing ships rather than a band with a hole.

**Where the export finds it.** The themed site assemble's
`site.site.drawn.json`; a mission whose Lot laid no backdrop, or whose
export is a pure shell, ships exactly as before.

**Seen:** in cold run 9225, the first to carry Zoo 1.95.0, Lot 0.108.0 and this release together (`docs/cold_runs/cold_9225/` at the factory root); until that run this layer is exercised by its tests alone, and the entry is corrected with the frames afterwards.

**Priced:** cold run 9225's package against 9224's at Level Factory's fixed stations, control, subject, control, as every step of roadmap 228 is priced; the figures land in that run's notes and in this entry afterwards.

**Tests:** 8, `tests/unit/test_backdrop_layer.py`. **Suite:** 2,173 passed, 14 skipped, 1 xfailed, exit 0 (2,163 as 0.173.0, the 8 new tests and the sibling guard's two cases for the new files).
