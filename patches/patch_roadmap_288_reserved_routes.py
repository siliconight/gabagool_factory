"""Roadmap 288: the corner stores' floors reserve their routes (Deli Counter 0.250.0, cold run 9371) -- NARROWED.
Copied from `patch_roadmap_283_storey_shelter.py`'s status half: replaces 288's status block (the paragraph directly
above its heading, asserted to be the one this was written against) with one that keeps it after "Earlier status
kept:". The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_288_reserved_routes.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

HEADING_288 = '\n\n**288. Nothing measured what furnishing costs a route, and the corner stores\' rows cost the most.** The walker, 2026-10-21: free navigation and fun gunfights first. The guide filed the same day (`docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`, sections 5 and 14) asks for widths measured after furnishing and a dressing traversal cost, a route that grows more than 10 % flagged. The nav gate asks whether a marker is reachable; nothing compared a route with and without furniture, and roadmaps 148 and 281 shipped with no number for what they did to movement. `route_cost.py` does: per room of the library, two arms of one spec -- AUTHORED, less every volume furnish and the shelter pass wrote; FURNISHED, as it ships -- and per pair of the room\'s doors, open edges and objective or loot markers, the shortest path for the contract\'s 0.35 m body on the bake\'s 0.10 m grid and the widest-path bottleneck, read against the body, the bake\'s 1.00 m door floor and the guide\'s two abreast (1.90 m on the contract\'s body). Its controls read as they must: an empty room, furnish\'s own 0.90 m slot open to the body and closed to the bake, a 0.60 m slot closed, a detour the AUTHORED arm cannot see. Over 580 rooms of 128 specs, 2,338 pairs: FURNISHED / AUTHORED median 1.000, p90 1.026, p99 1.135, max 1.308; 50 pairs in 41 rooms over the guide\'s 10 %; furnishing closes no pair to a body and five to the bake (four in gas_station_a01\'s back office, 1.40 -> 0.99 m; self_storage_a01\'s vault unit to its objective); 195 pairs narrowed from two abreast to single file. By room kind (`by_kind.out.txt`), a corner store\'s selling floor -- Deli Counter 0.247.0\'s rows of 2026-10-21 -- carries the most of it: 16 of its 85 pairs grew over 10 % and 44 narrowed to single file (the gas stations\' sales_to_stock -> west_service 22.5 -> 25.8 m; deli_a03\'s market 16.9 -> 19.2 m and three of its routes 3.1 -> 1.33-1.54 m wide), against the office\'s 14 and 25 of 324 and the vault\'s 6 and 42 of 146. The 80 pairs no body joins in either arm are each attributed, none of them furnishing\'s (`unsnapped.out.txt`): 21 are the instrument\'s limits -- a door or an open edge landing on a stair\'s body, a marker inside its own vault block -- and 11 are authored geometry worth a look of their own: cbp_town_finale\'s six club doors opening onto atrium holes, a 2.2 m cooler run across the sales floor\'s side of all five gas stations\' office door, a booth within 0.25 m of where a body stands inside primos_pizza\'s and strip_retail_a01\'s front door. **What would close it:** the corner stores\' selling floors keeping a cross-aisle two abreast through their rows -- the guide\'s market, "a broad cross-aisle and at least two tested ways around the central fixtures" -- with the census read before and after; every furnishing change reporting this census beside its nav gate; the eleven authored cases each looked at; the census\'s limits (a route through a neighbouring room, stair guards, the hole a flight cuts in the storey above) named where they bite.'
STATUS_288_OLD = "*STATUS: OPEN 2026-10-21 -- measured the same day (`docs/findings/furnish_route_cost/route_cost.py`, over Deli Counter 0.249.0's library); the corner stores' selling floors are the first fix.*"
STATUS_288_NEW = "*STATUS: NARROWED 2026-10-21 -- the corner stores' floors done. Deli Counter 0.250.0 (f0ab57ca, `patches/patch_dc_reserved_routes.py`) reserves a corner store's routes before its rows are laid: `protected_routes`, square routes between a floor's doors and markers on the floor as furnish finds it (`unfurnished`), a greedy spanner at the guide's 10 %, corridors half `two_abreast_width()` (1.90 m) wide, kept clear by furnish's rows, floor pieces, clusters and chairs where `reserves_routes` says (a shop floor that stands rows); down a row each island on the writer's centimetre. Over the fourteen corner-store specs, every room of them: routes over 10 % 20 in 13 rooms -> 4 in 3, none on a corner floor (the four in back offices and back halls, which reserve nothing; a corner floor's worst 1.096); narrowed to single file 70 -> 54; two abreast after furnishing 129 -> 145; the floors' share 19.2-23.1 -> 17.2-22.1 %, inside the walker's band; no other room moved. Refuted and kept, each measured (`patches/dc_reserved_routes/`): diagonal routes (they cut the rows into scattered gondolas), a spanning tree (10 pairs over 10 % against 4), the aisle as the corridor (62 narrowed against 54), the fixtures pass asked (two stores lost both video poker cabinets), the rows a centimetre wider (off a room's own aisles). Cold run 9371 (restaurant_row_001 at seed 9003, Deli Counter the only tool moved): 0 interventions, findings 108 -> 108; from deli_a03's west door 9370 faces a wall of gondola fronts and 9371 looks down a lane two abreast to the kitchen door, 26.0 % of that frame moved, the controls 0.0 to 0.4 % (`docs/findings/reserved_routes_288/`). LEFT: the census's AUTHORED arm measures a store's rows against an empty floor, where the guide's 10 % is a flag on dressing over the functional build -- an arm that keeps furnish's functional pieces (anchors, rows) and strips only its dressing (clusters, small floor pieces) is the census's next step; then the reservation for the kinds the census names next, each measured before and after -- the office (14 of 324 routes over 10 %, 25 narrowed), the vault (6 and 42 of 146), the small objective rooms whose door-to-marker routes grow 20 to 30 %; the eleven authored cases; the census's limits named where they bite. Earlier status kept: OPEN 2026-10-21 -- measured the same day (`docs/findings/furnish_route_cost/route_cost.py`, over Deli Counter 0.249.0's library); the corner stores' selling floors are the first fix.*"


def main():
    raw = RM.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if STATUS_288_NEW[:80] in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    if text.count(HEADING_288) != 1:
        raise SystemExit("REFUSED: 288's heading is not there once; nothing written")
    h = text.find(HEADING_288)
    s = text.rindex("\n\n", 0, h) + 2
    if text[s:h] != STATUS_288_OLD:
        raise SystemExit("REFUSED: 288's status block is not the one this was written against; nothing written")
    text = text[:s] + STATUS_288_NEW + text[h:]
    if text.count(STATUS_288_NEW + HEADING_288) != 1:
        raise SystemExit("REFUSED: 288's status no longer adjoins its heading; nothing written")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 288: NARROWED, the earlier status kept; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
