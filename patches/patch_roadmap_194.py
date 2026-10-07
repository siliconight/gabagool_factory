"""Roadmap item 194: deli_a01's upper storey was cut off, and nothing asked.

    python patch_roadmap_194.py

Appends item 194 after item 193, anchored on the roadmap's last line as read
2026-10-06 (1,209,673 bytes, LF). Touches neither the generated index nor the
counts line: run `tools/roadmap_status.py --write` and `--check` after.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

TAIL = ("3. The rest of the frozen list, case by case: foundry's skylight box and roof AC, "
        "the garages' columns, final_stand's statue and covers.\n")

ITEM = '''
*STATUS: NARROWED 2026-10-06 -- fixed, and proven on 9188's own site, not yet in a cold run. In cold runs 9187 and 9188 deli_a01's upper storey was a navmesh island the street could not reach: two `seed_cover` crate stacks shut both ways round its up-stair to the foot (0.79/0.54 m and 0.40/0.23 m against the bake's 0.8 m), and its server room had no door. Deli Counter 0.194.0 gave the server room a door (the walker's call) and added L24 (WARN), naming every room only a breach, window or drop reaches: 16 in 8 shells, 15 frozen for the walker. Deli Counter 0.195.0 makes the seeder leave `min_corridor_width` (1.1 m) round every piece -- 40 of the library's 69 seeded pieces did not -- moving 35 and dropping 7 in 13 shells. Swapped into 9188's staging and baked: islands 165 -> 164 -> 161, deli_a01's only island of its own is its roof, and the street's island covers its basement (783 m2), ground floor (672) and stair and upper storey (759). Open: a cold run; furniture may stand 0.9-1.1 m from a seeded piece; the nav gate never asks whether an entrance reaches a stair.*

**194. deli_a01's upper storey was cut off from the street, and nothing asked.** Found 2026-10-06 measuring playable area on cold run 9188 (`docs/findings/deli_a01_upper_storey_9188/`).

**WHAT WAS MEASURED.**
- 9188's walk-test site bake, 165 islands. deli_a01's ground floor and basement are the street's island at both doors; its upper storey is two islands, 592 m2 (the up-stair and three rooms) and 186 m2 (the server room). 9187, baked identically: 595 and 186 m2, so Deli Counter 0.192.0's refurnish did not do it.
- **Two crate stacks shut the stair's foot.** The up-stair and its guards run from the stairwell's south wall to its foot, so both ways from the stairwell's door to the foot run north past it. `crate_stack_stairwell_0` left 0.79 m and 0.54 m, `crate_stack_stairwell_1` 0.40 m and 0.23 m, where the bake's 0.4 m erosion a side needs 0.8. The first was stale (today's rule refused where it stood, 0.01 m off the foot landing); the second passed today's rule.
- `_seed_clear`'s margins were fractions of a body: 0.3 m off a stair's reserve, 0.9 m off a volume, 1.0 m from a partition's line, nothing off an exterior wall. Across the library: 69 seeded pieces in 128 shells; 23 stale, 35 within 1.1 m of something, 40 either.
- **The server room had no door**: two soft-wall breaches and a roofline breach. L12 counts a breach as a way in. Across the library, 16 rooms in 8 built shells are reachable only by breaching, vaulting or dropping.
- **No gate could see it.** The circulation gate keeps pieces out of stair volumes, and the crate stood 1 cm outside the landing. L23 asks over-a-hole or in-a-walk. The Godot nav gate proves a stair's two ends join, and they did, both on the cut-off island.

**REFUTED, KEPT.**
- "778 m2 of deli_a01 is disconnected from the street", as first said in conversation, implied the deli was shut. The ground floor and basement were open.
- The finding's first README called the bake Laser Tag's scene. It was the walk-test's `site_navqa.tscn`; only the site spec came from Laser Tag's staging, and all four stagings hold the same one.
- The seeder's first test passed without the rule: in a 20 x 14 m room the old seeder happened to land every piece a body off every wall. In a 6 m deep building it stood one 0.36 m off.

**WHAT SHIPPED.**
- Deli Counter 0.194.0: the server room's door (`hall_to_server_room`, at (-2, 7.0)); L24 (WARN), `layout_lint.walk_unreachable` -- L12's search, moved unchanged into `_reach_from_ext`, run again over doors, garages, vault doors, stairs, ladders and ramps only; `walk_reach_baseline.json`.
- Deli Counter 0.195.0: `_seed_clear(..., corridor=True)`, asked by `seed_cover`; `reseat_piece(..., corridor=True)`; `migrate_seed_corridor.py` -- 13 shells, 35 moved, 7 dropped (deli_a01-a03's stairwell crates, video_store_a01's stockroom shelter), every spec a fixed point of furnish, 13 shells rebuilt.

**PROVEN ON THE SITE, not in a cold run.** 9188's walk-test staging copied, deli_a01 swapped in, reimported, baked with the same instrument and settings (`swap_and_bake.py`). 0.194.0's door alone took islands 165 -> 164 (the server room joins the upper storey, 779 m2); with 0.195.0, 161, and deli_a01's only island of its own is its roof.

**OPEN.**
1. A cold run on restaurant_row_001.
2. The 15 frozen L24 rooms are the walker's call: the deli family's server rooms (the objective in cr_deli, deli_a02 and night_deli) and basement utility rooms, three apartment_walkup_a01 rooms, rowhouse_raid's kitchen and vault.
3. The nav gate proves a stair's ends join, never that an entrance reaches them. Asking it would have caught this in every build.
4. Furnish keeps 0.9 m from a volume: 4 seeded pieces in 2 shells have furniture 0.9-1.1 m off.
'''


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data, "CRLF in the roadmap; refusing"
    assert len(data) == 1209673, "roadmap is %d bytes, not the 1,209,673 read; refusing" % len(data)
    text = data.decode("utf-8")
    assert text.endswith(TAIL), "the roadmap no longer ends with item 193's open list; refusing"
    assert "**194. " not in text, "item 194 exists; refusing"
    RM.write_bytes((text + ITEM).encode("utf-8"))
    print("PIPELINE_ROADMAP.md: item 194 appended (%d -> %d bytes)" % (len(data), len((text + ITEM).encode("utf-8"))))


if __name__ == "__main__":
    main()
