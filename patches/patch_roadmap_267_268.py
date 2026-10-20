"""Roadmap 267 and 268 opened: what the walker's asset wishlist says the levels lack, read against what the factory
builds (docs/findings/asset_wishlist_2026-10-19/).

Anchored: the roadmap must end on item 266's last line, and hold no item 267 or 268; nothing is written otherwise.
Every line LF. Then `python tools/roadmap_status.py --write` and `--check` regenerate and verify the index.

    python patches/patch_roadmap_267_268.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
TAIL = (" **What would close it:** a merge pass priced the way the cover merge was -- draws and frame time at stations "
        "inside the merged rooms, before and after, with two controls -- the bake unchanged in look (lightmap compared "
        "user by user), and the walker told what it cost and bought.\n")
ITEMS = (
    "\n*STATUS: OPEN 2026-10-20 -- measured (`docs/findings/asset_wishlist_2026-10-19/box_slots.py`), not started.*\n"
    "\n**267. Furniture the generator places that Zoo builds as a box.** Read against the walker's asset wishlist "
    "(`docs/reference/PA_1999_Heist_Game_Asset_Wishlist_FINAL_GO_AHEAD.md`; the walker: \"may help us make assets we "
    "don't know we need to make our levels feel more alive\"), the strongest evidence of such an asset is one Deli "
    "Counter already places: 1,486 of the tracked library's 10,048 prop slots (14.8 %), in 142 names, name no species, "
    "and Zoo builds each as the plain box at its size (`box_slots_library.out.txt`). By count: the stairs' own guards, "
    "1,025 in 98 specs; columns 146 in 14; crate stacks 44 in 17, boxes on purpose as cover; pump islands 21 in 7; "
    "planters 15 in 7; slot machines 13 in the three casinos; market stalls 13 in the three market halls; kiosks 13 in "
    "6; the auto shops' vehicle lift 8 in 4; a pizza oven and its dough mixer, a jukebox, kegs, a forklift. Stand-ins "
    "too: a `locker` is built as a `filing_cabinet` and a `workbench` as a `counter`; and `roof_ac` and `club_bar` "
    "miss species Zoo already has (`hvac_unit`, `back_bar`) for want of a word in `prop_species.PROP_SPECIES`. Not "
    "measured: the share in Level Factory's own `lf_` buildings, which a cold run's package holds. **What would close "
    "it:** each name mapped to a species that fits it or given one -- the one-word mappings first, the stair guards "
    "once a frame shows whether a box reads wrong as a guard -- and the box share measured again on the library and "
    "in a cold run's package.\n"
    "\n*STATUS: OPEN 2026-10-20 -- read against the factory (`docs/findings/asset_wishlist_2026-10-19/`); not "
    "started; three taste calls for the walker.*\n"
    "\n**268. Families the wishlist calls foundation that no generator places.** From the same reading: building "
    "service clusters (B08: meters and disconnects on rowhouse fronts and store rears), window air conditioners and "
    "radiators (C12), the alarm bell box over a storefront and its panel inside (K08), extinguishers and exit signs "
    "(C15), washroom fixtures (C08: the library's one restroom, gs_corner_station's, holds a water heater), a "
    "temporary job on the street (B13: cones, a road plate, a barricade, a work light), hand trucks and stock carts at "
    "a rear door (E02), the upper room's furniture (C07, C09: the delis' apartment above the shop, the walk-ups' "
    "bedrooms), and the office's computer, phone and stereo (C17-C19). Two of the wishlist's rules map onto "
    "furnishing: one hero purchase per owner and the rest plain (\"put the visual budget where somebody put their "
    "money\"), and a current task per building -- a delivery mid-unload, a repair open on a bench -- of which roadmap "
    "265's crew kit is the first. **For the walker, not decided:** the wishlist's restraint on brand jokes against the "
    "walker's \"funny and crass\" invented brands; its rule that a real vehicle design is not cleared by removing its "
    "badge, against the getaway van drawn from a real step-van chassis; and what the stair guards should look like. "
    "**What would close it:** each family a species and a recipe that places it where its building's purpose says, "
    "priced in draws (most repeat across a block: one module a building, merged per material), and seen in a cold "
    "run's frames.\n")


def main():
    raw = ROADMAP.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap has CRLF lines; nothing written")
    text = raw.decode("utf-8")
    if "**267. " in text or "**268. " in text:
        raise SystemExit("REFUSED: an item 267 or 268 is already there; nothing written")
    if not text.endswith(TAIL):
        raise SystemExit("REFUSED: the roadmap does not end on item 266's last line; nothing written")
    ROADMAP.write_bytes((text + ITEMS).encode("utf-8"))
    print("roadmap 267 and 268 opened; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
