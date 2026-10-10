## [1.95.0] - the backdrop beyond the plate's edge: a rowhome and a water tower

### What changed

**Roadmap 228, step C.** The walker picked E from the edge menu
(`docs/findings/edge_menu/` at the factory root): a chain-link fence at the
plate's edge (Lot 0.107.0), a sodium glow over it (Lux 0.73.0), and behind
it rows of rowhomes with lit windows and a water tower. These are the two
species those rows and that landmark are made of. Lot's bands (step D) place
them and Level Factory composes them as MultiMeshes (step E); nothing in a
level changes until then.

- **`backdrop_rowhome`:** one painted box with the roofline the menu's
  mockup lacked, a cornice, a flat roof with a chimney, a stoop at the door.
  `core/backdrop_forms.py` plans it and paints its facade: brick with its
  courses, a cornice band, two openings a storey over three storeys, the
  ground storey's left one the door, the lit windows (one in five, one in
  five of those a TV's blue, deterministic for the module's stem) in the
  emission map. ONE material (`M_BackdropRowhome_<stem>_Face`, Lux's
  binder owns the lit panes) and ONE surface, so a band of houses is one
  MultiMesh and one draw a side. 4.5 to 8 m wide, 6 to 11 m tall.
- **`water_tower`:** a tank on four braced legs, a cap and a red beacon
  (`M_WaterTower_Beacon_Lens`), 28 to 48 m tall; the painted steel in two
  parts and the lens.
- Both are backdrop: `collision: false`, never inside the playable extent.

**Built in Blender:** a three-slot kit (two rowhomes at 6.0 x 12 x 9.5 and 5.5 x 12 x 8.0 m, a tower at 14 x 14 x 40 m) built in Blender 5.1.1, theme delco: all three PASS, the rowhomes at 48 triangles with one material and one primitive each, the tower at 372 with its steel and its lens (`docs/findings/backdrop_kit/` at the factory root). The first build failed Zoo's exact fit on all three axes, since the cornice, stoop, chimney, cap and beacon stood outside the slot; the parts now stand exactly (w, d, h).

**The census** (`tools/coplanar_census.py`, three builds a species): "6
builds, 0 with coincident pairs, 0 that did not build", third run. The first
found 3 pairs a rowhome and 4 a tower, every part standing exactly on or
against another; `backdrop_forms.INSET` pushes each 4 mm into the one it
stands on, the tower's braces stand a thickness apart, and the stoop's foot
stands the inset above the body's bottom plane, which the second run found
it lying in.

**Tests:** 8 pure in `tests/test_backdrop.py` (12 cases), and the four
registries that audit every species by hand carry the two new ones.
**Suite:** 4,122 passed, 423 skipped (the builds that need bpy), 1 xfailed, exit 0 on the repo; on the draft copy before it, 4,095 passed with the census' three builds a species clean.
