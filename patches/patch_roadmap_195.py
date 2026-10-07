"""Roadmap item 195: a piece passes through a wall, and no gate asked.

    python patch_roadmap_195.py

Appends item 195 after item 194, the roadmap's last, anchored on 194's last
line as read 2026-10-06 (1,218,055 bytes, LF). Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

ANCHOR = ("4. The entrance check runs at the gate's own origin only; the grid "
          "sweep could ask it at all eight.\n")

ITEM = '''
*STATUS: NARROWED 2026-10-06 -- Deli Counter 0.199.0: layout_lint L25 (WARN) names every piece reaching past both faces of a wall the builder stands -- 19 pieces in 15 of 146 non-LF specs at 0.198.0, 7 THROUGH a wall and 12 ALONG one; `presets.make` trims a recipe's piece through its own wall (the corner deli's case, the hospital's waiting seats) and `migrate_wall_crossing` trimmed the library's 7 (six deli cases to x -14.0..-8.185, warehouse's shelving run to x -4.0..7.84); both instruments read 12 in 8 specs after. Open: the twelve ALONG a wall, frozen in `wall_crossing_baseline.json`, each to be looked at; `casino_tower`'s generated basement vault block, centred on a partition; a level frame of the trimmed case.*

**195. A piece passes through a wall, and no gate asked.** Found 2026-10-06 sizing the deli case for item 186's deli detail (`docs/findings/pieces_through_walls/`).

**WHAT WAS SEEN.** In cold run 9189's composed deli_a01 (the `presentation_compose` package's `site.tscn`), the deli case `deli_case_cover` stands at x -14.0..-7.0 and partition segment `int_0_0_seg6` at x -8.0 across it: 0.825 m of the case comes out of the wall into the market aisles. `presets.corner_deli` authors it so -- 7.0 m long from x -14.0, its own partition at x -8.0 -- so all six library delis carry it, and every deli the recipe generates.

**WHAT WAS MEASURED.** Every authored piece against every wall the builder stands, 146 non-LF specs: 19 pieces in 15 specs reach past both faces of a built wall.
- **THROUGH, 7** (the centre off the wall): the six deli cases, 0.825 m; `warehouse`'s 16 m `shelving_run`, 3.85 m.
- **ALONG, 12** (centred on the wall's line): `rack_long_b` and `forklift_bay` on y -3.0 in setback_demo and warehouse_a02; cbp_town_finale's two vomitory covers and its rollgate across a 2.2 m door; bank_branch_a04's `VAULT_DOOR` with no opening under it; four garage columns.
- **None at an opening:** 19 with the openings cut, the same 19 without.
- **The recipes:** `corner_deli` and `hospital` (its `waiting_seats`, 0.35 m) generate a piece through a wall; `casino_tower` (its basement `vault_block`) and `parking_garage` (a column) one along a wall. The hospital's is in every one-building hospital brief Level Factory 0.145.0 leaves generated.
- **No gate saw any of them.** Every rule asked a piece where it stands; none asked whether a wall stands in it.

**REFUTED, KEPT** (in the finding): the first instrument cut openings unsnapped and modelled only the exterior walls `ext_walls` lists, and skipped 465 turned pieces; the second, on the walls as the builder stands them, read the same 19 and found no turned piece across a wall. The tests patch first claimed one test passed either side of the release, which it cannot without the rule.

**WHAT SHIPPED, Deli Counter 0.199.0.**
- **L25 (WARN), `layout_lint.wall_crossings`**: the builder's own walls (`partition_bounds.partition_spans` clamped to the storey extent and split round `stairwell.wall_voids`; all four exterior sides on every storey under `auto_exterior`), each piece by its box and, when turned, its art.
- **`migrate_wall_crossing.trim`**: a piece THROUGH a wall keeps its near end and its far end comes back to the wall's near face less `level_design._WALL_PIECE_AIR` (0.01 m); refused, with the reason, along a wall, turned, past half the piece, or from under a marker. `presets.make` runs it on every recipe before any pass places round it; the migration trimmed the library's 7, each spec two numbers.
- **`wall_crossing_baseline.json`**: the twelve ALONG a wall. A new crossing fails `test_wall_crossing.py`; a fixed one still listed fails it too.

**OPEN.**
1. The twelve ALONG a wall. A column on a wall line may be structure; a 14 m rack centred on a partition is not.
2. `casino_tower`'s generated basement `vault_block`, centred on the partition at x 0: every generated casino stands its vault across a wall.
3. A level frame of the trimmed case, from the next cold run that draws a deli.
'''


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data, "CRLF in the roadmap; refusing"
    text = data.decode("utf-8")
    assert text.count(ANCHOR) == 1, "item 194's last line found %d times" % text.count(ANCHOR)
    assert text.endswith(ANCHOR), "item 194 is no longer the roadmap's last; refusing"
    assert "**195. " not in text, "an item 195 already exists; refusing"
    RM.write_bytes((text + ITEM).encode("utf-8"))
    print("roadmap: item 195 appended; %d -> %d bytes" % (len(data), len((text + ITEM).encode("utf-8"))))


if __name__ == "__main__":
    main()
