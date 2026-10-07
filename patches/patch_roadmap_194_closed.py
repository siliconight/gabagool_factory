"""Roadmap item 194: CLOSED by cold run 9189.

    python patch_roadmap_194_closed.py

Anchored on item 194 as `patch_roadmap_194.py` wrote it (status block, the
proof paragraph, the shipped list's last bullet, the open list); each must
match exactly once. Touches neither the generated index nor the counts line:
run `tools/roadmap_status.py --write` and `--check` after.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("*STATUS: NARROWED 2026-10-06 -- fixed, and proven on 9188's own site, not yet in a cold run. In cold runs 9187 and 9188 deli_a01's upper storey was a navmesh island the street could not reach: two `seed_cover` crate stacks shut both ways round its up-stair to the foot (0.79/0.54 m and 0.40/0.23 m against the bake's 0.8 m), and its server room had no door. Deli Counter 0.194.0 gave the server room a door (the walker's call) and added L24 (WARN), naming every room only a breach, window or drop reaches: 16 in 8 shells, 15 frozen for the walker. Deli Counter 0.195.0 makes the seeder leave `min_corridor_width` (1.1 m) round every piece -- 40 of the library's 69 seeded pieces did not -- moving 35 and dropping 7 in 13 shells. Swapped into 9188's staging and baked: islands 165 -> 164 -> 161, deli_a01's only island of its own is its roof, and the street's island covers its basement (783 m2), ground floor (672) and stair and upper storey (759). Open: a cold run; furniture may stand 0.9-1.1 m from a seeded piece; the nav gate never asks whether an entrance reaches a stair.*\n",
     "*STATUS: CLOSED 2026-10-06 -- proven in a level. Cold run 9189 (restaurant_row_001, 0 interventions, findings 64 -> 64): deli_a01's only navmesh island of its own is its roof, and the street's island covers its basement (783 m2), ground floor (672) and stair and upper storey (759); islands 165 -> 161, the street's island 16,944 -> 17,728 m2. In 9187 and 9188 two `seed_cover` crate stacks shut its up-stair's foot (0.79/0.54 m and 0.40/0.23 m against the bake's 0.8 m) and its server room had no door. Deli Counter 0.194.0 gave the server room a door (the walker's call) and added L24 (WARN: 16 rooms only a breach reaches, 15 frozen for the walker); 0.195.0 makes the seeder leave `min_corridor_width` (1.1 m) round every piece (35 moved, 7 dropped in 13 shells); 0.196.0's nav gate asks whether an entrance reaches each stair -- 148 of the library's 149 do, primos_pizza's is frozen (item 189). Open, as their own work: the 15 L24 rooms, furnish's 0.9 m margin, and seed_9104's player stuck events 4 -> 9, all five new inside deli_a01.*\n"),
    ("**PROVEN ON THE SITE, not in a cold run.** 9188's walk-test staging copied, deli_a01 swapped in, reimported, baked with the same instrument and settings (`swap_and_bake.py`). 0.194.0's door alone took islands 165 -> 164 (the server room joins the upper storey, 779 m2); with 0.195.0, 161, and deli_a01's only island of its own is its roof.\n",
     "**PROVEN ON THE SITE, before shipping.** 9188's walk-test staging copied, deli_a01 swapped in, reimported, baked with the same instrument and settings (`swap_and_bake.py`). 0.194.0's door alone took islands 165 -> 164 (the server room joins the upper storey, 779 m2); with 0.195.0, 161, and deli_a01's only island of its own is its roof.\n"
     "\n"
     "**PROVEN IN A LEVEL, cold run 9189** (`docs/cold_runs/cold_9189/NOTES.md`). 0 interventions; the same draw (seed_9104); findings 64 -> 64. The run's own walk-test site, baked as 9188's was: 161 islands, deli_a01's only island of its own its roof, the street's island 17,728 m2 (9188: 16,944) over deli_a01's basement, ground floor, stair and upper storey -- as the swap-and-bake predicted. Laser Tag reads as 9188 on all three candidates but one field: seed_9104's player stuck events 4 -> 9, every other event count identical; the five new are one crew member, inside deli_a01, beside its front register counter (four) and a basement counting table (one), where no piece moved.\n"
     "\n"
     "**A BAD BAKE, DISCARDED AND KEPT.** The first bake of 9189's walk-test site, three minutes into its art leg, came back with no building in it (1,643 polygons, 72 islands, heights -0.5 to 6.6 m). The same command twice more, and once keeping Godot's output, read 4,362 and 161. Not reproduced; the cause is not established. A bake's bounds belong in its reading.\n"),
    ("- Deli Counter 0.195.0: `_seed_clear(..., corridor=True)`, asked by `seed_cover`; `reseat_piece(..., corridor=True)`; `migrate_seed_corridor.py` -- 13 shells, 35 moved, 7 dropped (deli_a01-a03's stairwell crates, video_store_a01's stockroom shelter), every spec a fixed point of furnish, 13 shells rebuilt.\n",
     "- Deli Counter 0.195.0: `_seed_clear(..., corridor=True)`, asked by `seed_cover`; `reseat_piece(..., corridor=True)`; `migrate_seed_corridor.py` -- 13 shells, 35 moved, 7 dropped (deli_a01-a03's stairwell crates, video_store_a01's stockroom shelter), every spec a fixed point of furnish, 13 shells rebuilt.\n"
     "- Deli Counter 0.196.0: the nav gate snaps each storey-0 exterior door a step inside and reports, per stair, `from_entry`. On the shipped deli_a01 it reads 1/2 where the old gate read every stair \"ok\" and navigable \"yes\"; on 0.195.0's, 2/2. Across the library 148 of 149 judged stairs are reached; primos_pizza's is frozen in `navgate_baseline.json`, item 189's discharge neck. Reported, not gated.\n"),
    ("**OPEN.**\n1. A cold run on restaurant_row_001.\n2. The 15 frozen L24 rooms are the walker's call: the deli family's server rooms (the objective in cr_deli, deli_a02 and night_deli) and basement utility rooms, three apartment_walkup_a01 rooms, rowhouse_raid's kitchen and vault.\n3. The nav gate proves a stair's ends join, never that an entrance reaches them. Asking it would have caught this in every build.\n4. Furnish keeps 0.9 m from a volume: 4 seeded pieces in 2 shells have furniture 0.9-1.1 m off.\n",
     "**OPEN, AS THEIR OWN WORK.**\n1. The 15 frozen L24 rooms are the walker's call: the deli family's server rooms (the objective in cr_deli, deli_a02 and night_deli) and basement utility rooms, three apartment_walkup_a01 rooms, rowhouse_raid's kitchen and vault.\n2. Furnish keeps 0.9 m from a volume: 4 seeded pieces in 2 shells have furniture 0.9-1.1 m off.\n3. seed_9104's five new player stuck events inside deli_a01 (9189): one crew member, late in its runs, where no piece moved. The report carries no goal; Laser Tag's player path would say why.\n4. The entrance check runs at the gate's own origin only; the grid sweep could ask it at all eight.\n"),
]


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data, "CRLF in the roadmap; refusing"
    text = data.decode("utf-8")
    for old, _new in EDITS:
        n = text.count(old)
        assert n == 1, "anchor found %d times, not once: %r" % (n, old[:80])
    for old, new in EDITS:
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("PIPELINE_ROADMAP.md: item 194 CLOSED (%d edits; %d -> %d bytes)" % (len(EDITS), len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
