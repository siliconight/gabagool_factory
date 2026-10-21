# The floor-plan guide against the factory: what exists for an exploded axonometric view

The walker, 2026-10-21, sharing `docs/reference/Floor_Plan_to_3D_Layout_and_Automap_Guide.md`: "add this to the
roadmap to make our floorplan tool better and acheive that Exploded axonometric view, with architectural cutaways".
The guide's section 6 is that view; its sections 7 to 9 are an automap and a connectivity graph.

A read-only research pass's inventory, put in the repository's voice. It searched each tool repository directly: the
root `.gitignore` lists all ten (lines 3-12), so a search from the root skips them without saying so -- the search
that started this chase did exactly that and found nothing in code. Every claim marked **read again** was read at its
source before roadmaps 293 to 295 were filed; the rest are the pass's, with their paths.

## 1. The floorplan tool: `deli_counter/floorplan.py`

- **What it draws** (read again: the `<g id>` layers). `render_story` (414-667) returns one SVG per storey: grid;
  rooms (tinted boxes, `data-room`); furniture (volumes); open to below (hatched voids: authored `slab_holes` and
  `vertical_links` of kind `floor_hole` and `hatch`); walls (solid bands -- exterior walls by
  `setbacks.storey_extent`, partitions split by `partition_bounds.partition_spans` around `stairwell.wall_voids`);
  openings (door leaf and swing, window, dashed breach, garage comb; `data-opening` is the tag, or the kind untagged);
  stairs (footprint, landings, ascent arrow, numbered badge, UP/DN); ladders; markers; room labels; annotations (title,
  elevation, dimensions, north arrow, scale bar, legend); a stair key.
- **What it leaves out**: ramps, platforms, fire escapes, vault ledges, parapets, objectives, loot and zones, an
  opening's sill and height, `open_to`, a door's state, roofs and ceilings.
- **A storey** is chosen by `.story`; markers by their z band (105-109), volumes by base z (396-403), stairs by
  `floors_served` (268). Output is SVG at 12 px/m, north up, origin at the footprint's centre;
  `write_floorplans` writes `<name>.floor{B,0,1...}.svg` (688-699).
- **Two places it disagrees with what is built** (read again). Partitions are drawn `PART_T` = 0.15 m thick (37, 553)
  and built at `wall_thick` (`deli_counter.py:1750-1757`, `size = (wt, length, wh)`). The header writes the storey
  height as "clg" -- `f"{sh:.1f} m clg"` (604-605) -- and `sh` is floor to floor, not the ceiling.
- **When plans are made** (read again). Only by `validate.py` (247-255, into `build/floorplans/`), which the commit
  gate runs (`check.py:71`), and by `new_level.py` and `describe.py`. `build.py --all` never names it, so a cold run
  makes none. `build/floorplans/` is ignored (`deli_counter/.gitignore:9`) and holds 2,052 SVGs, 1,026 plans and
  1,026 sightline overlays (`sightlines.write_overlays`). Level Factory's `packages/service/facade.py:350-352` looks
  for `lot_out/floorplan.svg`, which nothing in Lot writes: a dead path.
- **Who calls it**: `validate.py`, `sightlines.py:384-385`, `pvp_heist.py:57` (`_marker_story` only), two tests, and
  the walker-review scripts `docs/findings/walker_review_2026-10-19/open_floor_plans.py` and
  `docs/findings/open_floor_table_260/plans.py`; `migrations/review_sheet.py:135` and `migrations/ai_review.py:136`
  read its output.

## 2. The vertical data a 3D view needs (guide sections 3-4)

- **Stated in a spec** (`spec_types.py`): `story_height`, `n_stories`, `has_basement` (560-562); `wall_thick`,
  `floor_thick` (564-565); `roof` (solid, open, none), `roof_mode`, `roof_thick` (575-579); a room's `roofed` and
  `ceiling_material` (442-447); parapets, setback insets; an opening's width, height and sill (91-93, defaults by kind
  119-141); exterior walls and partitions as separate lists, `auto_exterior` filling a side left unlisted; `SlabHole`
  (342-348); `VerticalLink` floor holes and hatches (457-477); a stairwell's x, y, from, to, width, run, style, facing
  and step rise (175-205).
- **Derived in code**: a floor's elevation is `story * story_height` (`deli_counter.py:1377`, `1500`, `1703`); a
  wall's height `story_height - _cap_thick`; slab undersides (`stairwell._slab_undersides`); a head is sill plus
  height; stair geometry from `footprint_rect`, `stair_endpoints`, `floors_served`; the slab cut a stair makes
  (`slab_openings`).
- **Absent**: a per-storey elevation or height, a ceiling height, a partition's own thickness, and an atrium as one
  object through several storeys -- it is one `SlabHole` a slab.
- **`roof: "open"`** already hides a roof's visual and keeps its collision (`spec_types.py:571-575`): the guide's
  first cutaway step exists for one building at a time.

## 3. Stable identifiers (guide section 3)

- **Rooms**: `id` is required and authored (`spec_types.py:435`) -- `office.json`'s `lobby`, carried into
  `office.gameplay.json`. It survives a reshape.
- **Openings**: no id, an optional `tag` (`spec_types.py:98`); 9 of 16 built openings in `office` and 12 of 27 in
  `deli_a03` carry none. Interactive ids hash building, wall, storey, kind and position (`interactives.py:175-186`),
  so they change when a door moves; partition walls are named by their index, `int_<story>_<i>`
  (`deli_counter.py:1761-1762`), so reordering partitions renames their doors.
- **Stairs and ladders**: an optional `id` (`spec_types.py:203`), `stair_{i}` without one (`stairwell.py:108-109`).

## 4. 3D presentation that exists

- **Nothing axonometric, isometric, exploded or cutaway anywhere** (read again: no `.py` or `.gd` in any of the ten
  tool repositories or `tools/` names any of them), and the roadmap never had.
- `tools/look_shots.gd` (driven by `tools/look_shots.py` against a walk export): one perspective overview and four
  straight-on orthographic elevations, `elev_N/S/E/W`, plus eye-level shots -- PNGs and a manifest.
- `deli_counter/migrations/review_render.py`: the only Blender renderer -- Cycles, a 50 degree perspective camera,
  front, rear, sides, a top-down oblique roof view, entrance, objective, gameplay height and collision shots.
- `tools/massing.py` computes orthogonal silhouettes as numbers from `slots.json`; it draws nothing.

## 5. The connectivity graph (guide section 9)

- **`deli_counter/tactical.build_graph`** (157-286): rooms as nodes; edges from partition doors, exterior doors to
  outdoor rooms, open-plan shared edges, stairs, ladders and ramps, floor holes and hatches. Undirected: a floor hole
  joins both ways (read again: 279-285). Its stair rule (`_connect_stair_column`, 244-255) links every overlapping
  room pair across the storeys a stair spans, not only the rooms the stair serves. `evidence.py` writes it as
  `navigation.json`'s `adjacency`. `_count_independent_routes` (377) is a node-split max flow over it.
- Two more room graphs: `combat_audit._width_graph` (counts stairs, not ladders) and `_disjoint_paths2`;
  `layout_lint`'s `graph`, edges with kinds and EXT and ROOF nodes, still symmetric. `pvp_heist._bfs_path` blocks
  rooms, not doors.
- **Direction and access state exist only per link, in `gameplay.json`**: a ladder's nav link carries
  `bidirectional` and `access_state` (`ladder.py:438-453`); a drop is one-way with `required_capability: "drop"`
  (`ladder.py:477-511`); a stair door has `default_state` and `allow_random_lock`. No graph reads any of them.

## 6. An automap (guide sections 7-8)

Nothing: no minimap, automap, map scene or `own_world_3d` in any repository. `SubViewport` appears only to switch off
editor viewports during a bake; `SurfaceTool` and `ArrayMesh` only to merge meshes; `map_scene` is a Laser Tag key the
adapter refuses.
