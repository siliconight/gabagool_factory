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

**Seen,** cold run 9225 (`docs/cold_runs/cold_9225/` at the factory root): `[export] backdrop: site_backdrop.tscn -- 277 instances of 19 module(s) on their sides, 69 draw calls`, and at the edge stations the road ends at the fence with a skyline of rowhome blocks, lit windows and the water tower behind it; the paint travels inside each extracted mesh (`embedded_textures: 2`). The 19 modules are Lot 0.108.0's three band depths making three modules of each pair; Lot 0.109.0 gives every band one depth.

**Priced,** 9225's package against 9224's at the fixed stations, control, subject, control: +43 draws a heading median (+17 to +91), the 69 MultiMeshes; p95 frame time +0.02 ms median, inside the controls' own 0.67 ms spread, 7 of 53 headings over +0.5 ms, the worst +1.25.

**Tests:** 8, `tests/unit/test_backdrop_layer.py`. **Suite:** 2,173 passed, 14 skipped, 1 xfailed, exit 0 (2,163 as 0.173.0, the 8 new tests and the sibling guard's two cases for the new files).
