"""Roadmap 231, new: a street costs a hundred draws -- markings as MultiMeshes, bigger tiles after the
bake (`docs/findings/street_draws/`).

Appends the item at the end of the roadmap, status block directly above the heading. The file
must end with the last item's final newline and carry no 231 yet; nothing is written otherwise.
The generated index is regenerated afterwards by `tools/roadmap_status.py --write`.

    python patches/patch_roadmap_231_street_draws.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ITEM = """
*STATUS: OPEN 2026-10-11 -- measured, not started. Cold run 9233 priced a street for the first time: the `block` grammar's second side street and lane cost +107 draws and +0.55 ms p95 a heading median against 9232's package of the same lot, a tenth of a 5.7 ms frame, where the street is in view. `tools/draw_census.py` attributes it (`docs/findings/street_draws/`): the site scene's pool went from 666 to 795 box meshes and 141 to 178 materials, +89 of the boxes markings with +43 materials identical in every line but a per-marking wear offset, the rest slab and sidewalk tiles; and of the 795, 521 are the plate, the slabs and the sidewalks tiled at 8 m for the engine's 8-light cap, priced against live lights on 2026-08-23, before the package baked its lights by default. Two levers, in order, each priced the cover merge's way (draws and frame time at fixed stations, 9233's package the control): markings as one MultiMesh per paint colour (227 submissions to 2 or 3; the per-marking wear offset the loss, a shader's per-instance custom data the second step if the eye minds), and a bigger tile where the package bakes, gated by the paired-light census (no mesh over 8 live lights). Owner: Lot (`lot.py`'s street writers), with Level Factory's perf census as the gate.*

**231. A street costs a hundred draws: markings as MultiMeshes, bigger tiles after the bake.** Every level has a main street and a cross street, and until cold run 9233 nobody had priced one. The block grammar put a second street and a lane on the same lot and the harness read +107 draws a heading median (`docs/cold_runs/cold_9233/NOTES.md`, Priced), so the T's own cross street has cost about that on every level built.

**WHERE THE DRAWS COME FROM** (`docs/findings/street_draws/README.md`, `tools/draw_census.py` on 9232's and 9233's `site.tscn`):
- **Every marking is its own node and its own material.** `lot.py`'s `_yaw_quad_node` writes a Node3D with a quad and `_mat_sub` writes a `StandardMaterial3D` per marking, identical but for the `uv1_offset` `paint_offset` hashes from the marking's road, kind and position (so two bars a whole number of paint tiles apart do not wear alike; cold run 9044 measured 5 of 210 pairs matching). Its docstring: "each marking already has its own material, so a per-marking offset costs nothing" -- it costs a draw. 227 markings in 9233, 125 materials.
- **The plate, the slabs and the sidewalks are 8 m tiles** (`MESH_TILE`, `_mesh_tiles`), the reason written beside them: `max_lights_per_object` (8), a 65 x 8 m path mesh under 58 lights on 2026-08-23. That was live light. Since Level Factory 0.131.0/0.144.0 the package bakes by default and the live lights are the failing tubes, the cycling poles and the spots (9233: 206 rigs baked, 29 live), so the tile is paid for a cost that moved. 377 ground tiles and 144 slab and sidewalk tiles.
- The furniture species (meters, lamps, trees, shelters, signs, 22 more in 9233) are Zoo scenes instanced beside these and are the rest of the cost; not counted here.

**THE TWO LEVERS, IN ORDER.**
- **Markings as one MultiMesh per paint colour** (Lot): a unit quad, one world-triplanar paint material, every marking an instance with its size, yaw and position in the transform, the form Level Factory's export gives the surface dressing (4,285 instances in 4 draws). 227 submissions become 2 or 3, 125 materials 2 or 3. The loss: the per-marking wear offset; the world projection still wears each bar by where it stands, and the 5-in-210 aliasing returns. If the eye minds, the offset comes back as per-instance custom data read by a spatial shader in Lot's addon.
- **A bigger tile where the package bakes** (Lot): `MESH_TILE` 8 m to 24 or 32 m for the ground, the slabs and the sidewalks: 521 boxes to about 40. The gate: the paired-light census (Level Factory 0.159.0's perf census, PAIRED for the 8-light cap) on a package built with the bigger tile, no mesh over 8 live lights. The spec can carry the tile, or the census can be the gate.

**HOW IT IS PRICED:** draws and frame time at the fixed stations, 9233's package as the control and the same lot and grammar rebuilt on the changed Lot as the subject, a control run bracketing it (`docs/findings/horizon_glow/price_glow.py`, the per-heading median against the controls' mean keyed by station and yaw). The pool's count is the cheap check that the merge happened; the frame time is the price. The buildings' interiors are most of this level's 2,800 draws and are Deli Counter's and Zoo's; the cover merge (roadmap 180) took theirs down once.

Owner: Lot, with Level Factory's perf census as the gate.
"""


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert text.endswith("\n") and not text.endswith("\n\n\n"), "the roadmap's tail is not one item's final newline"
    assert "\n**231. " not in text, "231 exists"
    assert ITEM.startswith("\n*STATUS:") and "\n\n**231. " in ITEM
    text = text + ITEM
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 231: a street costs a hundred draws, opened")


if __name__ == "__main__":
    main()
