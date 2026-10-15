"""The nine open items that had no status line get one, 2026-10-15 (`docs/findings/open_items_remeasure/`).

19, 20, 24, 28 and 35 never had a status block (they predate the convention); 44, 45, 153 and 154 have one that
runs to several paragraphs, which `roadmap_status.py` cannot read (it joins the one block directly above the
heading), so the index called all nine `OPEN *(inferred)*`. This INSERTS a single-paragraph status directly above
each heading -- the earlier multi-paragraph blocks are left in place above the new line, as the record. Each
heading is asserted once. The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check` after it, and expect "0 rest on a sentence".

    python patches/patch_roadmap_status_lines_nine.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [
    (19, "\n\n**19. Every tool grew a Godot half before there was a DAG to say who owns\n", False,
     "*STATUS: CLOSED 2026-10-15 -- the rule the item proposed is the shipped package's state, re-read on cold "
     "run 9314's package (`docs/findings/open_items_remeasure/`): no `addons/` directory and 0 `res://addons` "
     "references; `runtime/lux` (25 scripts, 4 shaders, 7 presets, referenced by `presentation/lux.applied.tscn`) "
     "and `runtime/skymint` (the sky provider that arrives with Lux) are the one runtime that ships; Zoo's half is "
     "the import script `zoo_worldskin.gd` at the root; Patina's, Pixelcoat's and Deli Counter's Godot halves ship "
     "nowhere in it; 0 `Decal` nodes, so the decal question is answered by absence. The exterior lighting half the "
     "body refuted was fixed by Lot 0.79.0 (the poles are the anchors, worst distance 0.0000 m) and the lights "
     "reach the package (`light_bake.json`; 238 lights in the applied scene, 56's record).*"),
    (20, "\n\n**20. Patina's Godot half is a renderer from before Lux was one.**", False,
     "*STATUS: NARROWED 2026-10-15 -- the ambiguity is gone from every package and the files are still in the "
     "repo (`docs/findings/open_items_remeasure/`). `patina/godot/addon/patina/` (plugin, dock, apply script, "
     "`ps1.gdshader`) and `patina/godot/shaders/ps1.gdshader` exist, their README still saying the half has not "
     "been walked in the editor; they are consumed by nothing in any tool repo and shipped in no package (9314: 0 "
     "addons, its 5 shaders Lux's and SkyMint's). COLOR_0 has one reader in a package, `zoo_worldskin.gd`'s "
     "`_vertex_colour_albedo` (84). The open question settled itself: `art_mode` is `vertex-color` on both "
     "branches (76), Patina's texture half never runs, Pixelcoat is the skin; the PS1-preset half of the migration "
     "was overtaken by the walker's realism call. Left: deleting the dead folder, a Patina release.*"),
    (24, "\n\n**24. Lux gives runtime scaffolding an `owner`, which is what bakes it into a\n", False,
     "*STATUS: OPEN 2026-10-15 -- re-read at Lux 0.77.0 (`docs/findings/open_items_remeasure/`): 21 `owner =` "
     "sites across `lux/addons/lux/runtime/` where the item counted nine (environment 1, fixture spawner 2, light "
     "loader 12, lighting 1, post-FX 5); 18 of the runtime scripts are `@tool` and 15 of those ship in every "
     "package under `runtime/lux`, so a package opened in the editor and saved still has the trap. The second "
     "WorldEnvironment is gone -- `ensure_world_environment` searches the scene for an existing one before "
     "creating its own (Lux 0.49.0). The multiplication (four suns, three stacks) is still not isolated and the "
     "call-site rule is not written; what would close it is that rule, proven by loading a shipped "
     "`lux.applied.tscn` in the editor, saving, and diffing.*"),
    (28, "\n\n**28. The VRAM question is about zoo's GLB embedding, not about pixelcoat.**", False,
     "*STATUS: CLOSED 2026-10-15 -- the Zoo export change the item asked for shipped, and it was counted "
     "(`docs/findings/open_items_remeasure/embedded_textures_28.py`). Zoo 1.2.0 (2026-09-21, `share_textures`) "
     "writes a pack's images beside the GLB in `_tex/`, named by content hash, and the GLB references them by "
     "`uri`. On cold run 9314's package: 329 GLBs, 0 embedded images; 314 reference 1,250 images by uri, 277 "
     "distinct files, 8.9 MiB on disk, 0 missing, 4.51 references a file; 94 distinct images by content, 45 "
     "written in more than one `lot/<id>/art/zoo/_tex/` folder, one in 17 -- the duplication left is per "
     "building folder, not per module. What the engine keeps resident is 238's question (the reflection atlas "
     "was 82 % of it). `pack_importer.gd`'s shared `.tres` and `atlas.py` were not what did it.*"),
    (35, "\n\n**35. The graybox/art relationship: it is a SWAP, and most of the recommended\n", False,
     "*STATUS: NARROWED 2026-10-15 -- the contract stands (slot manifest 1.3.0) and most of the absent list "
     "exists, measured on the 158 built specs (`docs/findings/open_items_remeasure/`): roles wall 24,768, prop "
     "9,947, window 1,453, doorway 1,001, floor and ceiling 586 each, breach 271, roof 146; exterior corners by a "
     "`wallEnd` post at every corner (58: 988 -> 0 open; Zoo's `wallCorner` species, sized from 950 posts, is "
     "never emitted by Deli Counter); parapets 1,910 `parapet_*` slots; stairs 1,044 stair-named slots and a "
     "`stair_rail` species; columns as Lot's `col` nodes (239 on 9314's site); piers, plinth 0.45 m and cornice "
     "0.12 m on every solid wall module (`relief_parts`, 75); coping, base course and curbs as Patina dressing "
     "(248); UVs on every module, world-projected (88), so the no-UV clause is gone. No species or slot is named "
     "for a beam, a thickness transition, a baseboard, crown trim or a fascia.*"),
    (44, "\n\n**44. The green boxes could be cars, and the collision would not change.**", True,
     "*STATUS: NARROWED 2026-10-15 -- (1) and (2) of the scope shipped, (3) three of five, re-read "
     "(`docs/findings/open_items_remeasure/`; the multi-paragraph status above, which the index could not read, "
     "stands). (1) Deli Counter stamps `species` on 8,458 of 9,947 prop slots across the 158 built specs (85 %; "
     "9314's deli_a01 127 of 142, office 60 of 73, pharmacy_a01 26 of 28). (2) Zoo builds the hinted species at "
     "the slot's dims or the `prop` box and says which in `<id>_kit.built.json`: 9314's three builds record one "
     "fallback (deli_a01's `loading_pallet_stack`, 4.50 x 2.50 x 1.50 m outside the species' range) and 0 "
     "missing; the stems carry the species, and 9 of deli_a01's 75 prop modules are plain `prop_`. (3) `counter` "
     "(`bay_max` 4.0), `shelving` (2.4) and `teller_line` (2.0) repeat by bays; `bench` does not and no `locker` "
     "species exists. The 2026-09-11 fit count is not re-run -- the hint changed what it would mean; today's "
     "figure is the fallback count. The species' look is the walker's.*"),
    (45, "\n\n**45. Large playable surfaces are visually flat, and the fix is not more\n", True,
     "*STATUS: NARROWED 2026-10-15 -- the layer exists end to end, re-read (`docs/findings/open_items_remeasure/`; "
     "the multi-paragraph status above stands). Patina's `surface_dressing.py` writes the manifest with "
     "`surface_zone_id`, `asset_set`, `placement_mode` (scatter / seam / cluster / anchor), `density`, "
     "`scale_range`, `height_band`, `collision_policy`, `shadow_policy`, `seed` and `quality_tier` -- not "
     "`yaw_range`, not `exclusion_tags`; Lot's `site_surfaces.py` names the zones, Zoo builds the clutter "
     "species, and Level Factory's `dressing_scene.py` ships it as MultiMesh in its own scene (9314: 4,439 "
     "instances in 4 draws, no collision node written); the lock (LF 0.31.0) protects collision. The item's test "
     "-- hide the layer and the level plays the same, Laser Tag the judge -- has not been run as an A/B, and "
     "uniform scatter from primary views is the walker's eye.*"),
    (153, "\n\n**153. A street reads as ordered when its furniture says where cars and\n", True,
     "*STATUS: NARROWED 2026-10-15 -- every layer has shipped pieces, counted on cold run 9314's seed_9104 site "
     "(`docs/findings/open_items_remeasure/`; the multi-paragraph status above stands). Step zero: 4 roads, 10 "
     "sidewalks, 4 kerb cuts, 6 frontages. Markings: crosswalk bars 34, stop bars 4, centre line 21, edge lines "
     "12, bay ticks 54; no arrows, no yellow kerb face. The kerb line: streetlight 2, traffic signal 2, sign post "
     "7, fire hydrant 2, parking meter 47, litter bin 4, newspaper box 4, mailbox 2, utility pole 12 with wires, "
     "pole flyers 10, payphone 3, chain-link fence 8; no bollards placed (the species exists), no utility cabinet, "
     "no bike rack. Waiting places: bus shelter 3, bench 3, 46 street trees in grates; no planters. Cars: 22 "
     "`simple_car` parked in the bays the ticks draw, 3 cruisers, a step van. No walk note has judged the street "
     "as one to drive and cross, which is what closes it.*"),
    (154, "\n\n**154. The buildings are designed all at once, and Delco buildings are\n", True,
     "*STATUS: NARROWED 2026-10-15 -- one structural ask exists as an archetype and the other has no vocabulary, "
     "re-read (`docs/findings/open_items_remeasure/`; the multi-paragraph status above stands). The twin: "
     "`twin_a01`, one archetype, whether its halves differ unmeasured. The accretion: 0 hits, nothing says a part "
     "was added later. Surfaces: `siding_delco`, `shingle_delco`, `fieldstone_delco` exist; glass block and EIFS "
     "do not. Objects: utility poles and wires shipped (240; 12 poles on 9314's site), `satellite_dish`, "
     "`shop_awning`, `security_camera` and `roller_grill` are species; window air conditioners and security bars "
     "are not. The corridor: 241's urban type stands buildings 2.0 m off the sidewalk among mid-rises; buildings "
     "at the road with parking beside or behind is still not a Lot plan. Patina's per-instance differentiation "
     "is unwired (76). The walk that reads the place as built over time is not recorded.*"),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    for num, head, had_block, status in ITEMS:
        assert text.count(head) == 1, ("heading not found once", num)
        assert status.startswith("*STATUS: ") and status.endswith("*") and "\n" not in status, num
        i = text.find(head)
        above = text[:i].rstrip("\n")
        last_para = above.rsplit("\n\n", 1)[-1]
        assert not last_para.startswith("*STATUS:"), ("a status already adjoins the heading", num)
        if had_block:
            # The older, multi-paragraph status sits at the end of the previous item's body: between the previous
            # heading and this one. It is 5-24 k characters above the heading, so no fixed window would do.
            prev_heads = [m.end() for m in re.finditer(r"\n\*\*\d+\. ", text[:i])]
            assert prev_heads, num
            assert "\n*STATUS:" in text[prev_heads[-1]:i], ("expected an older status block above", num)
        text = text[:i] + "\n\n" + status + head + text[i + len(head):]
        j = text.find(head)
        assert text[:j].endswith(status), ("status does not adjoin its heading", num)
    RM.write_bytes(text.encode("utf-8"))
    print("nine status lines inserted; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
