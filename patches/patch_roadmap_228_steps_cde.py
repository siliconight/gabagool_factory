"""Roadmap 228, steps C, D and E proven in cold run 9225; the other recipes and the brief's field landing.

Replaces 228's status block and adds 9225's record to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_228_steps_cde.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- steps A and B PROVEN in cold run 9224 (restaurant_row_001, "
    "0 interventions, 0 retries, findings 74 to 74): Lux 0.73.0's glow and Lot 0.107.0's fence "
    "stand at the edge (`LOT_PERIMETER_FENCED: 6 run(s), 589.7 m`), the wall's 78 tiles are gone "
    "from the scene, and at every edge station the road ends at the chain-link against the dusk "
    "sky instead of at the pale wall (`docs/cold_runs/cold_9224/edge_before_after.png`). Priced "
    "against 9223's package at the fixed stations: -5 draws a heading median (-28 to +17), frame "
    "time inside the controls' 0.80 ms spread. Step C (Zoo 1.95.0's rowhome and water tower), D "
    "(Lot 0.108.0's bands by recipe) and E (Level Factory 0.174.0's MultiMesh composition) are "
    "landing; cold run 9225 proves and prices them.*\n"
)
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- the walker's E stands in a level. Steps A and B were proven "
    "in cold run 9224 and steps C, D and E in cold run 9225 (restaurant_row_001, 0 interventions, "
    "0 retries): `LOT_BACKDROP_PLACED: recipe borough, 276 rowhome(s) in 3 bands a side ... 1 "
    "water tower(s)`, shipped as `site_backdrop.tscn` with 277 instances, and at the edge "
    "stations the road ends at the fence with a skyline of rowhomes, lit windows and the water "
    "tower behind it (`docs/cold_runs/cold_9225/`). Priced against 9224's package: +43 draws a "
    "heading median, frame time inside the controls' 0.67 ms spread. The draws found a defect: "
    "three band depths made 18 rowhome modules where the plan counted 6 (69 MultiMeshes); Lot "
    "0.109.0 gives every band one depth. Landing with it: Zoo 1.96.0's tree and warehouse and "
    "Lot 0.109.0's `yards`, `parkland` and `roadside` recipes, and Level Factory 0.175.0's "
    "`surroundings`, named by the brief or decided by the archetype; cold runs 9226 to 9228 "
    "prove a recipe each. The walker's: the near band 4 m past the fence reads as a dark wall of "
    "windows down the main road at dusk.*\n"
)
BODY_ANCHOR = (
    "draws a heading, heavier than club_block_014's 1,150.\n"
)
ADDED = (
    "\n**STEPS C, D AND E SHIPPED:** Zoo 1.95.0 (`patches/patch_zoo_backdrop.py`), "
    "`backdrop_rowhome` as one painted box with a cornice, a chimney and a stoop, its windows and "
    "door in the paint and the lit ones in the emission, one material and one surface, and "
    "`water_tower`; both exact to the slot and census-clean after a 4 mm inset "
    "(`docs/findings/backdrop_kit/`). Lot 0.108.0 (`patches/patch_lot_backdrop.py`), "
    "`site_backdrop.plan` by the spec's `surroundings` recipe into a `backdrop` list, never cover, "
    "each piece a collisionless slot. Level Factory 0.174.0 (`patches/patch_lf_backdrop.py`), "
    "`backdrop_layer.ship_backdrop` on the dressing layer's road: `<site>_backdrop.tscn`, one "
    "MultiMesh a module a side, the entry scene instancing it beside the level.\n"
    "\n"
    "**C, D AND E PROVEN, cold run 9225** (`docs/cold_runs/cold_9225/NOTES.md`): 0 "
    "interventions; Lot laid 276 rowhomes and the tower, Zoo's site kit built the modules, Level "
    "Factory shipped 277 instances in 69 MultiMeshes with the paint inside each mesh. Seen: up the "
    "side road a skyline of rowhome blocks with lit windows and the tower on the horizon; down "
    "the main road the near band, 4 m past the fence, as a dark terrace of blocks at dusk. "
    "Priced: +43 draws a heading median (+17 to +91), p95 +0.02 ms median inside the controls' "
    "0.67 ms spread, 7 of 53 headings over +0.5 ms, the worst +1.25.\n"
    "- **The defect the draws found:** a module is a species at its dims, depth included, and the "
    "borough's three band depths (10, 11, 12 m) made 18 rowhome modules of the six (width, "
    "height) pairs, 69 MultiMeshes with the tower. Lot 0.109.0 gives every band one depth (12 m): "
    "seven modules, about 25 MultiMeshes. The next borough run measures it.\n"
    "- **Refuted on the way, kept:** the first read of the frames took the pale fronts for a "
    "missing texture; the extraction report says `embedded_textures: 2` a module and the "
    "pixels are dark brick under a blue dusk sky, (45, 56, 88).\n"
    "\n"
    "**THE OTHER RECIPES, landing:** Zoo 1.96.0's `backdrop_tree` (a trunk and a twelve-facet "
    "crown, 132 triangles, bark and vegetation) and `backdrop_warehouse` (a long low box with "
    "roof monitors, siding, a roll-up door and a strip of high windows, one material); Lot "
    "0.109.0's `yards` (stacked containers, warehouses, the tower), `parkland` (a tree belt and "
    "a far belt) and `roadside` (a thin belt and far warehouses); Level Factory 0.175.0's "
    "`MissionBrief.surroundings`, with `site_variation.surroundings_of` deciding from the "
    "archetype and the site shape when unnamed (a warehouse backs onto yards, a hospital onto "
    "parkland, a gas station on a strip onto the road, everything else onto the borough), "
    "recorded in the spec as `surroundings_resolved`. Cold runs 9226 (warehouse_yard_001), 9227 "
    "(county_hospital_001) and 9228 (gas_stop_001) are staged to prove a recipe each.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + ADDED).replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**228. "), "228's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 228: steps C, D and E proven in cold run 9225")


if __name__ == "__main__":
    main()
