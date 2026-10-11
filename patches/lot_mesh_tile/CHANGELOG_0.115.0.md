## 0.115.0 - the plate tile follows the bake

**Roadmap 231, the second lever.** The ground, the slabs, the sidewalk
bands, the fields, the pads and the perimeter walls are cut to `MESH_TILE`
(8 m) for Godot's per-mesh light cap, priced on 2026-08-23 against LIVE
lights. Level Factory has baked a package's lights by default since its
0.144.0, and the culler pairs no baked light with a lightmapped mesh
(Level Factory 0.159.0's paired census: cold run 9233's plates sat under
nine lights at worst, 2,895 of its 3,966 meshes under none), so the tile
was costing that level 521 of its 795 boxes for a cap that binds only
through the lights left live.

- **`mesh_tile(site_spec)`** reads the spec's `render`: `mesh_tile_m`
  names the tile outright; else `lights_baked` true takes
  **`MESH_TILE_BAKED`** (32 m, a quarter of a 128 m plate side); else
  `MESH_TILE`, and a spec that says nothing draws byte for byte as before.
  A tile under a metre is refused. Level Factory 0.178.0 writes
  `render.lights_baked` from its export's own default.
- `_mesh_child_lines`, `_box_node` and `_yaw_box_node` take `tile`;
  `_outdoor_nodes` passes the site's to the plate families and says the
  tile it took. Covers and blockers keep the 8 m law, being under it.
- **The paint is cut into cells** (`PAINT_CELL_M`, 32 m): `_marking_meshes`
  writes one mesh a colour a cell, by each marking's centre, the colour's
  one material shared. Cold run 9236 shipped 0.114.0's one mesh a colour
  and its paired census put each under 21 live lights against the cap of
  8 -- a mesh whose box is the plate reaches the failing tube behind every
  storefront, and the engine binds the first 8 it finds. A cell keeps each
  piece under the lights within its reach and culls as a piece.
- `_yaw_quad_node` is removed: 0.114.0 left it with no caller, and
  `_mat_sub` loses the `uv_offset` only it passed.
- Both numbers' proof is the paired census on the first package built with
  them -- no mesh over 8 live lights -- recorded under the factory's
  roadmap 231, where the price is.

**Tests:** 6 in `tests/test_mesh_tile_render.py`, 1 more and 3 adapted in
`tests/test_marking_meshes.py`. **Suite:** RESULT_SUITE.
