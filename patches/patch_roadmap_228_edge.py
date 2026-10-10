"""Roadmap 228, filed: the edge of the plate is E, varied by level (the walker's call on the menu).

Appends item 228 after 227, the roadmap's last item, with its status block directly above its
heading, and points 219's status at it. Each anchor must match exactly once; nothing is written
on a miss. The generated index is regenerated afterwards by `tools/roadmap_status.py --write`,
never by this script.

    python patches/patch_roadmap_228_edge.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

TAIL = (
    "shorter folder or an administrator turning long paths on. `setup` weighs `<factory>\\levels`, "
    "the workspace `START_HERE.md` makes; `doctor` its own. It stays a WARN, not a FAIL, until the "
    "failure itself is measured.\n"
    "\n"
    "Owner: Level Factory.\n"
)
OLD_219 = (
    "Notes 8 and 12: the perimeter and backdrop menu is filed, six options framed and priced "
    "(`docs/findings/edge_menu/`), recommended D, the chain-link fence, the tree belt and the "
    "glow: the walker's to pick. The moon waits on the walker too.*\n"
)
NEW_219 = (
    "Notes 8 and 12: the walker picked E from the menu (`docs/findings/edge_menu/`), the "
    "chain-link fence with rowhomes and a water tower behind it and the glow over them, and asked "
    "for versions that differ by level: item 228. The moon waits on the walker too.*\n"
)
ITEM = (
    "\n*STATUS: OPEN 2026-10-10 -- the walker's call recorded and the arc designed; nothing built. "
    "Ships in five steps, each priced as the menu was: the glow (Lux), the fence at the plate's "
    "edge (Lot, Zoo), a backdrop rowhome kit and a water tower (Zoo), the bands beyond the plate "
    "by a per-level recipe (Lot), and their composition and the beacon (Level Factory, Lux).*\n"
    "\n"
    "**228. The edge of the plate: E, varied by level.** The walker, 2026-10-10, on the six-option "
    "menu in `docs/findings/edge_menu/` (roadmap 219, notes 8 and 12): \"I prefer E, but we should "
    "have multiple different versions depending on the level\". E is `fence` + `glow` + `houses` + "
    "`tower`: a fenced lot backing onto rows of rowhomes with lit windows, a sodium sky-glow over "
    "them and a water tower as the landmark. The recommendation had been D, the tree belt; the "
    "menu's own reading stands and is overruled: at the mockup's fidelity the houses read as blocks "
    "with windows and need a real kit, which is the work.\n"
    "\n"
    "**WHAT EXISTS, read 2026-10-10.**\n"
    "- **The wall:** `lot.py:2246` rings the ground that was built with four boxes, "
    "`perim_N/S/E/W`, at the height Level Factory writes into the site spec "
    "(`apps/cli/commands/__init__.py:2118`, `\"perimeter\": {\"height\": 3}`), in `PERIM_COLOR`, "
    "\"bright, flat, dead\" by its own comment. The spec carries `site_shape` and nothing that "
    "names the surroundings.\n"
    "- **The fence:** `site_fences.plan_fences` (Lot 0.97.0) closes an Empty row's gaps with "
    "Zoo's `chain_link_fence` (1.77.0, two draws a run, width 1 to 120 m), as cover slots "
    "(`species`, `at`, `yaw`, `dims`, `size`, `base`), cut at every road, path and building and "
    "never across a marker. Nothing fences the plate's edge.\n"
    "- **Trees:** five street species grown by one builder (`street_tree.py`, `core/tree_forms.py`); "
    "no backdrop tree.\n"
    "- **Houses:** none. The Empties are Deli Counter shells merged a side per material (Level "
    "Factory 0.143.0), too dear by far for 357 of them.\n"
    "- **A tower:** Zoo's `water_tank` is a rooftop tank, 1.6 m; no water tower.\n"
    "- **The sky:** Lux presets carry the sky's two colours, energy, fog and ambient, and may hand "
    "the sky to a provider (`sky_provider_script`); nothing draws a glow at the horizon. The "
    "mockup's ring is 380 m out, unshaded, alpha, fog ignored, climbing 20 degrees, one draw.\n"
    "- **Composition:** `packages/exporting/dressing_scene.py` turns a manifest of placements into "
    "one MultiMesh per mesh, 3,948 instances in four draws; the mockup's houses were one MultiMesh "
    "a side and band.\n"
    "\n"
    "**THE DESIGN, in the order it ships.** Every step is priced the way the menu was: Level "
    "Factory's fixed stations, before and after, against two controls' mean; and a station facing "
    "the edge is added, because the menu's stations face into the level and under-see the backdrop.\n"
    "\n"
    "**Step A, Lux: the horizon glow.** A ring LuxRoot builds from the preset: `horizon_glow_color`, "
    "`horizon_glow_energy`, `horizon_glow_top_deg`, `horizon_glow_radius_m`, zero energy drawing "
    "nothing. Sodium at night, the mockup's colours; haze by day; it ignores the fog by design (the "
    "glow is the haze) and climbs past the wall. Every version of the edge has it, so it lands "
    "first and alone.\n"
    "\n"
    "**Step B, Lot and Zoo: the fence at the plate's edge.** `site_fences.plan_perimeter`: one "
    "chain-link run a side, 0.25 m inside the wall, cut at the roads that leave the plate as the "
    "row fences are cut, and said (`LOT_PERIMETER_FENCED`). The wall keeps its collision and loses "
    "its tiles' visibility in the presentation, as the mockup did; where a road leaves the plate "
    "the wall's tile stays, dark (the menu's `wall_dark`), until a gate module exists. Eight draws "
    "a plate at most, two a run; a plate longer than Zoo's 120 m width takes two runs a side.\n"
    "\n"
    "**Step C, Zoo: `backdrop_rowhome` and `water_tower`.** The rowhome is a 3-storey block, 5 to "
    "7.5 m wide and 10 to 14 m deep, with the roofline the mockup lacked: a cornice, a parapet or "
    "a pitched roof, a chimney, a stoop; its windows an emissive atlas whose lit set is chosen per "
    "instance (MultiMesh custom data), one in five lit and one in five of those a TV's blue, so one "
    "mesh and one material serve a whole band. Dark brick from the style, under 300 triangles. The "
    "tower is the mockup's: a tank on four legs at about 40 m, a beacon Lux lights by role. Both "
    "are backdrop: no collision, no navmesh, `gi_mode` disabled, never inside the playable "
    "extent.\n"
    "\n"
    "**Step D, Lot: the bands, by recipe.** `site_backdrop.plan` lays what stands beyond the plate "
    "from `site_spec[\"surroundings\"]`, which Level Factory writes from the brief's `surroundings` "
    "where given and otherwise derives: a `street_block` or `strip` backs onto `borough` (E: "
    "rowhome bands at 4 to 14, 38 to 49 and 80 to 92 m with cross streets and lamps between, the "
    "tower past the north edge); a `yard` or an `industrial_warehouse` onto `yards` (containers, "
    "warehouse blocks, the tower); a `campus` or a `county_hospital` onto `parkland` (D: the tree "
    "belt); a `gas_station` on a `strip` onto `roadside` (the tree belt, a far billboard). The "
    "recipe is the level's; the seed varies each band within it. A new list in the spec, "
    "`backdrop`, carries the slots, never `cover`.\n"
    "\n"
    "**Step E, Level Factory and Lux: composition and the beacon.** The export composes `backdrop` "
    "as `dressing_scene` composes dressing, one MultiMesh a species a side a band, partitioned so "
    "the culler keeps what the player cannot see; Lux lights the tower's beacon. Then the price, "
    "A/B/A2, at the menu's stations and the edge-facing one.\n"
    "\n"
    "**NOT DECIDED, the walker's:** the rowhome kit's look once it is built (a sheet at the menu's "
    "stations); whether `borough` wants the tree belt in front of its far bands (F); what the "
    "other three recipes show, beyond what is named here.\n"
    "\n"
    "Owners: Lux (A, E's beacon); Lot (B, D); Zoo (B, C); Level Factory (D's field, E).\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.endswith(TAIL), repr(text[-200:])
    assert "**228. " not in text, "228 is already filed"
    assert text.count(OLD_219) == 1, text.count(OLD_219)
    text = text.replace(OLD_219, NEW_219) + ITEM
    i = text.index(ITEM) + 1
    assert text[i:].startswith("*STATUS: OPEN 2026-10-10"), "228's status is not where it should be"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 228 filed; 219's status points at it")


if __name__ == "__main__":
    main()
