"""Roadmap 284 NARROWED (Deli Counter 0.252.0: a piece that seats somebody stands with its chair). Copied from
`patch_roadmap_288_289_marker_routes.py`, one item: replaces its status block (the paragraph directly above its
heading, asserted to be the one this was written against) with one that keeps it after "Earlier status kept:". The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_284_table_chairs.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [(284, '\n\n**284. A dining table draws none to four chairs, and one in five stands with none.** `level_design`\'s `table_dining` seats `("table", 0, 4)`: `_seats` draws `rng.randint(0, 4)` chairs and clearance refuses some, so how many chairs a table has is chance. Measured on Deli Counter 0.249.0\'s library: 255 dining tables, 51 with no chair (20 %), 67 with one, 64 two, 43 three, 30 four; the chairless ones in 31 specs (cbp_town_finale\'s five; apartment_walkup_a01\'s, courthouse_a02\'s, final_stand\'s, landmark_hall_a01\'s and museum_a01\'s three each). The draw is also the most fragile thing in a room: a piece placed before the tables re-draws every table after it, and 0.249.0\'s one shelter crate took cbp\'s club_ring_overlook from 15 chairs at 9 tables to 3 at 8. The guide the walker filed on 2026-10-21 (`docs/reference/Lived_In_Levels_Clear_Navigation_4P_PVE_1999_PA.md`) reads both sides of it: a table with no chair is a cluster missing its reason (section 8, "what belongs together"), and loose half-metre chairs are the incidental obstacles navigation pays for (sections 12 and 15, "players stare at the floor"). Both point the same way: a table\'s chairs belong to it, mostly tucked to it. **What would close it:** every dining table seats at least one, its chairs drawn from the table\'s own stream so that an upstream piece does not re-draw them, and tucked within a seat\'s depth of the table unless pulled out on purpose; the library refurnished and attributed, the nav gate and the audit read before the look.', '*STATUS: OPEN 2026-10-21 -- measured shipping roadmap 283; not started.*', "*STATUS: NARROWED 2026-10-21 -- every piece that must seat somebody stands with its chair. Deli Counter 0.252.0 (8eb3233f, `patches/patch_dc_table_chairs.py`) seats a host the room left chairless LAST, when the room is furnished, so nothing else furnish drew there moves: one chair from the host's own stream, tucked then pushed in -- every side of a table, a desk's front -- off any route the room reserves; a host no chair fits beside goes. A dining table must seat one (`must_seat`), its draw still none to four; a desk and a cocktail table, which always asked one or more, too. Measured on 0.251.0's library against 0.252.0's (`patches/dc_table_chairs/seats.out.txt`): dining tables with no chair 51 -> 0 (255 -> 254), desks 41 -> 0 (263 -> 239: 17 seated, 24 taken away), cocktail tables 4 -> 0. 77 rooms in 55 specs moved, 76 by the rescue alone; the 77th, landmark_hall_a01's artifact_room, lost its chairless dining table, and the shelter pass stood a crate on the floor it freed, on a route, and refurnished the spec around it (`moved_why.out.txt`, `artifact_steps.out.txt`, the plan views `plan_*.png`). Every host taken away attributed (`gone_hosts.out.txt`): 14 of the 25 in rooms holding a marker, 8 of them only for the route check (`no_route_check.out.txt`). Read before the look: the nav gate (Deli Counter's commit hook, `commit_hook.out.txt`); the combat audit, COVER_ALL_LOW 8 -> 7 and SIGHT_INTENT 503 -> 502, both the artifact room, every other code unchanged (`audit_compare.out.txt`); the route census over the library (`docs/findings/furnish_route_cost/`), routes over 10 % 28 -> 26, narrowed to single file 150 -> 151 -- five of the six new narrowings the artifact room's -- closures unchanged, objective and loot routes over 10 % 12 -> 9. Cold run 9374 (restaurant_row_001 at seed 9003, cold run 9373's level, Deli Counter the only tool moved; its office's exec_suite lost its chairless desk): 0 interventions, findings 108 -> 108, identical by code, candidate and message; the bake's users 2,948 -> 2,940, the desk's eight meshes (`docs/cold_runs/cold_9374/NOTES.md`). Refuted and kept: the shape first built -- every host's chairs from its own stream, a chairless host moved to its next spot, a dining table drawing one to four, a table trying every side -- re-drew 265 rooms in 119 specs, routes over 10 % 28 -> 40, three more closed to the bake; feature by feature the re-draw alone cost 28 -> 34 on this draw (`variants_*.json`). LEFT: a table's regular chairs still spend the room's stream, so an upstream piece re-draws them -- the decoupling this item asked for re-draws the library once and on this draw costs routes, so it is held, not refuted: another draw would price it differently, and choosing by the census would be seed-shopping; 40 % of regular table chairs stand pulled out by a draw, which is the 'on purpose', not measured against play; the 24 desks taken away leave offices barer, marker rooms most (office's exec_suite 7.2 -> 5.4 %, train_yard_a01's dispatch_office 7.0 -> 4.0 %, its two desks gone from the middle of its routes) -- whether a desk no chair fits beside should move instead is the walker's call. Earlier status kept: OPEN 2026-10-21 -- measured shipping roadmap 283; not started.*")]


def main():
    raw = RM.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    for n, heading, old, new in ITEMS:
        if new[:80] in text:
            raise SystemExit("REFUSED: %d already applied; nothing written" % n)
        if text.count(heading) != 1:
            raise SystemExit("REFUSED: %d's heading is not there once; nothing written" % n)
        h = text.find(heading)
        s = text.rindex("\n\n", 0, h) + 2
        if text[s:h] != old:
            raise SystemExit("REFUSED: %d's status block is not the one this was written against; nothing written" % n)
        text = text[:s] + new + text[h:]
        if text.count(new + heading) != 1:
            raise SystemExit("REFUSED: %d's status no longer adjoins its heading; nothing written" % n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 284: NARROWED, the earlier status kept; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
