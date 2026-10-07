"""Deli Counter 0.202.0: the two baselines the refurnish moves.

    python patch_dc_wall_backing_baselines.py

Run AFTER `migrate_furnish_recipes.py` has refurnished the library under both
of 0.202.0's rules. As read 2026-10-07 (both LF):
  * `stale_pieces_baseline.json` (2,500 bytes): 29 furnished pieces leave it,
    moved off authored holes by the hole rule; nothing joins it;
  * `test_club_fixtures.py` (14,510 bytes, after the fixtures patch): the
    library's cigarette machines 121 -> 119.

MEASURED, both, on the refurnished library before this was written:
  * L23 (`layout_lint.stale_pieces`) over the built non-LF library: 47 pieces
    in 8 shells -> 18 in 7. Gone: apartment_walkup_a01's dining set (3, the
    shell leaves the list), cbp_town_finale's 20 furnished pieces, and
    final_stand's 6. New: none -- rowhouse_raid's dining set, which the wall
    rule's re-roll first stood over its hole, stands clear under the hole rule.
  * Every library spec: 11 dartboards and 119 cigarette machines, where 0.201.0
    had 121. The two stood against open room edges, and no wall in their rooms
    holds them.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"
BASE = DC / "stale_pieces_baseline.json"
CLUB = DC / "test_club_fixtures.py"

GONE = {
    "apartment_walkup_a01": ["chair_set_re6154351_10_1", "table_dining_re6154351_10",
                             "table_dining_re6154351_7"],
    "cbp_town_finale_midbalanced_schemafixed": [
        "cartons_r1fea40f7_11", "cartons_r1fea40f7_12", "cartons_r1fea40f7_2",
        "cartons_r1fea40f7_3", "cartons_r1fea40f7_4", "cartons_r1fea40f7_8",
        "cartons_r1fea40f7_9", "chair_set_r16b4c2ae_4_2", "chair_set_r1fea40f7_1_1",
        "chair_set_r1fea40f7_7_1", "chair_set_r1fea40f7_7_2", "chair_set_r1fea40f7_7_3",
        "chair_set_r1fea40f7_7_4", "chair_set_r5c2f4b93_1_1", "desk_r5c2f4b93_1",
        "table_dining_r16b4c2ae_4", "table_dining_r1fea40f7_1", "table_dining_r1fea40f7_10",
        "table_dining_r1fea40f7_5", "table_dining_r1fea40f7_7"],
    "final_stand": ["cartons_rd8bd0867_7", "dust_sheet_rd8bd0867_1", "dust_sheet_rd8bd0867_2",
                    "dust_sheet_rd8bd0867_5", "dust_sheet_rd8bd0867_8",
                    "table_dining_r93a11b70_10"],
}

REASON = (
    "Pieces standing over a slab opening or in a stair's walk on their own storey "
    "(layout_lint L23), left in place by 0.192.0 because each needs a look before it moves: "
    "cbp_town_finale's cash counting tables, power cabinet and security consoles and "
    "final_stand's boss desk, statue and cover blocks are AUTHORED volumes standing inside "
    "atrium holes nothing fills; foundry's skylight box and roof AC stand over roof openings, "
    "which may be by design; the garages' columns stand at a ramp opening's edge and are "
    "structure. A fixed piece must leave this list (test_stale_baseline_has_not_gone_stale); a "
    "new one fails (test_no_new_stale_piece). 0.202.0 taught furnish an authored hole in its own "
    "floor (`level_design._seed_clear`): apartment_walkup_a01's dining set and cbp_town_finale's "
    "and final_stand's 26 furnished pieces moved off theirs and left this list."
)

OLD_COUNT = '''    assert counts == {"dartboard": 11, "cigarettes": 121}, counts
'''
NEW_COUNT = '''    # 121 -> 119 cigarette machines (0.202.0): two stood against open room
    # edges, and no wall in their rooms holds them
    assert counts == {"dartboard": 11, "cigarettes": 119}, counts
'''


def main():
    raw = BASE.read_bytes()
    assert len(raw) == 2500, "stale_pieces_baseline.json is %d bytes, not the 2,500 read" % len(raw)
    assert b"\r\n" not in raw
    d = json.loads(raw)
    assert d["counts"] == {"pieces": 47, "shells": 8}, d["counts"]
    for shell, names in GONE.items():
        have = d["stale_pieces"][shell]
        missing = [n for n in names if n not in have]
        assert not missing, (shell, missing)
        keep = [n for n in have if n not in names]
        if keep:
            d["stale_pieces"][shell] = keep
        else:
            del d["stale_pieces"][shell]
    d["counts"] = {"pieces": sum(map(len, d["stale_pieces"].values())),
                   "shells": len(d["stale_pieces"])}
    assert d["counts"] == {"pieces": 18, "shells": 7}, d["counts"]
    d["reason"] = REASON
    BASE.write_bytes((json.dumps(d, indent=2) + "\n").encode("utf-8"))

    text = CLUB.read_bytes()
    assert len(text) == 14510, "test_club_fixtures.py is %d bytes, not the 14,510 read" % len(text)
    assert b"\r\n" not in text
    text = text.decode("utf-8")
    assert text.count(OLD_COUNT) == 1
    CLUB.write_bytes(text.replace(OLD_COUNT, NEW_COUNT).encode("utf-8"))
    print("stale_pieces_baseline.json: 47 -> 18 pieces, 8 -> 7 shells; cigarettes 121 -> 119")


if __name__ == "__main__":
    main()
