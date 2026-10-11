# What a street costs in draws, and why: the shipped site scene's submissions by owner

Cold run 9233's price (`docs/cold_runs/cold_9233/NOTES.md`, Priced): the
`block` grammar's second side street and lane cost +107 draws and
+0.55 ms p95 a heading median against 9232's package of the same lot, a
tenth of a 5.7 ms frame, where the second street is in view. The T's one
cross street was never priced, so this is the first number on what a
street costs, and this finding attributes it before anything is merged.

## What was counted

`tools/draw_census.py` reads a package's `site.tscn` -- Lot's own ground,
streets, markings and furniture; the buildings, the backdrop and the
dressing are instanced or shipped beside it -- and counts the mesh
resources and materials by the owner their sub-resource ids name, and the
mesh nodes. A mesh node is one submission a frame when it is in view, so
the counts are the pool a heading draws from, not a heading's draws.
`draw_census_9232_9233.txt` is the two packages side by side.

| owner | 9232 (T) | 9233 (block) | +  |
|---|---:|---:|---:|
| `BoxMesh Ground` + `Ground_t` (the plate, in 8 m tiles) | 359 | 377 | +18 |
| `BoxMesh mark` (markings: bars, lines, dashes) | 138 | 227 | +89 |
| `BoxMesh road` (slabs, in 8 m tiles, split at cuts) | 54 | 78 | +24 |
| `BoxMesh sidewalk` | 51 | 66 | +15 |
| `BoxMesh frontage` | 22 | 25 | +3 |
| `BoxMesh fmark` + `field` (the parking field, lost in 9233) | 23 | 0 | -23 |
| other (paths, kerb cuts, yards, signs) | 19 | 22 | +3 |
| **mesh nodes** | **666** | **795** | **+129** |
| **materials** | **141** | **178** | **+37** |
| of them `mark` materials | 82 | 125 | +43 |

The +107 draws a heading is these +129 boxes where they are in view:
most of them the second street's markings (+89 boxes with +43 materials),
its slab and sidewalk tiles, and the lane's. The furniture species
(meters, lamps, trees, shelters, signs) are Zoo scenes instanced beside
these, 22 more of them in 9233; they are not in this table and are the
rest of the cost.

## Why there are so many, read off `lot/lot.py`

- **Every marking is its own node and its own material.** `_yaw_quad_node`
  writes a Node3D with a tiled quad and `_mat_sub` writes a
  `StandardMaterial3D` per marking, identical in every line but one: the
  `uv1_offset` `paint_offset` gives it, a hash of the marking's road, kind
  and position, so that two bars a whole number of paint tiles apart do
  not wear the same scuffs (measured on cold run 9044: 5 of 210 bar pairs
  matched). Its docstring says "each marking already has its own material,
  so a per-marking offset costs nothing" -- it costs a draw: 227 markings
  are 227 submissions when in view, through 125 materials that differ in
  nothing a merge would keep. This is the rule in `CLAUDE.md` ("never
  express colour-only variation as a new material") broken one step
  further: variation in nothing at all.
- **The plate, the slabs and the sidewalks are tiled at 8 m** (`MESH_TILE`,
  `_mesh_tiles`), and the reason is written beside it: the engine's
  `max_lights_per_object` (8), measured on 2026-08-23 when a 65 x 8 m path
  mesh stood under 58 lights. That was priced against LIVE lights. Since
  Level Factory 0.131.0/0.144.0 the package bakes its lights by default
  and the live ones are the failing tubes, the cycling poles and the
  spots (9233: 206 rigs baked, 29 failing left live), so a tile's light
  count is no longer the plate's; the tile exists for a cost that has
  moved. 377 ground tiles and 144 slab and sidewalk tiles are 521 of the
  795 boxes.

## The two levers, in the order to take them

1. **Markings as one MultiMesh per paint colour** (Lot): a unit quad with
   one world-triplanar paint material, every marking an instance with its
   size, yaw and position in the transform -- the form Level Factory's
   export already gives the surface dressing (4,285 instances in 4 draws)
   -- so 227 submissions become 2 or 3 and 125 materials become 2 or 3.
   What it loses: the per-marking wear offset; the world projection still
   wears each bar by where it stands, and the 5-in-210 aliasing
   `paint_offset` was written for comes back. If that matters to the eye,
   the offset returns as per-instance custom data read by a spatial
   shader in Lot's addon, a second step.
2. **A bigger tile where the package bakes** (Lot): `MESH_TILE` from 8 m
   to 24 or 32 m for the ground, the slabs and the sidewalks, which cuts
   521 boxes to about 40. The proof it needs before shipping is the
   paired-light census (Level Factory 0.159.0's `perf` census, PAIRED for
   the 8-light cap) on a package built with the bigger tile: no mesh over
   8 live lights. Lot does not know whether the package will bake; the
   site spec can carry the tile, or the census can be the gate.

Priced the way the cover merge was (Zoo 1.68.0, roadmap 180): draws and
frame time at the fixed stations, 9233's package as the control and the
same lot and grammar rebuilt on the changed Lot as the subject, a control
run bracketing it. The pool's count is the cheap check that the merge
happened; the frame time is the price.

## What this does not measure

Which of the 795 boxes a given heading sees (the harness's per-heading
draws do); the furniture species' share (a Zoo scene is several meshes);
the buildings' interiors, which are most of the 2,800 draws of this
level and are Deli Counter's and Zoo's (the cover merge took theirs down
once); and the look of a merged marking row against today's.

## Instruments

- `tools/draw_census.py`: the census; several packages side by side.
- `draw_census_9232_9233.txt`: the run of 2026-10-11 on 9232's and
  9233's packages.
