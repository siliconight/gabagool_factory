"""Roadmap 229: Deli Counter 0.207.0 landed, the rows over the aisles and the long hall's trade.

Replaces two sentences of 229's status block and appends the landing record to its body. Each
anchor must match exactly once; nothing is written on a miss, and nothing is written while the
RESULT_ placeholder is unfilled. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_229_aisles.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

RESULT_CENSUS = "RESULT_CENSUS"

OLD_A = "(`docs/findings/fixture_rows/row_census_0206_1.txt`); cold run 9231 shows it. "
NEW_A = (
    "(`docs/findings/fixture_rows/row_census_0206_1.txt`); cold run 9231's hideout took one anchor where "
    "9229's took three, the frames waiting on 9232 (9231 stopped at the export). Deli Counter 0.207.0 "
    "(`patches/patch_dc_aisle_rows.py`) lays a selling or storage room's rows over the AISLES between "
    "its shelf runs: the floor-standing shelf, gondola, rack and pack-wall volumes projected across the "
    "room's long axis, every gap at least the contract's 1.25 m aisle a lane laid as a floor of its own "
    "width (`_lanes_for_room`); and where the twelve-lamp cap binds it trades rows across for lamps "
    "along while the larger spacing shrinks (the long hall: a 58 x 20 m hall is two rows of five at "
    "11.6 m rather than three of four at 14.5). Everything else is laid as 0.206.1 laid it, proven over "
    "the furnished library (`docs/findings/fixture_rows/aisle_rows_diff_0207_draft.txt`: 322 rooms "
    "identical, 165 changed, the 61 aisle rooms and the 114 where the cap bound); the library rebuilt "
    + RESULT_CENSUS + "; cold run 9232 shows the deli's market aisles. "
)
OLD_B = (
    "Left: the layout by use (aisles, benches, the bar), structural causes beyond the grid, the species "
    "(strip light, sconce, high-bay, exit sign), and the long hall's thinned rows. Owner: Deli Counter, "
    "with Zoo for the species and Lux for the rigs.*"
)
NEW_B = (
    "Left: the layout by use beyond the aisles (benches, the bar's pendants, the counter's work side), "
    "structural causes beyond the grid and the aisles (a duct run), and the species (strip light, "
    "sconce, high-bay, exit sign). Owner: Deli Counter, with Zoo for the species and Lux for the rigs.*"
)
BODY_ANCHOR = (
    "124 single-fixture rows where 114 stood (`docs/findings/fixture_rows/row_census_0206_1.txt`).\n"
)
BODY_ADDED = (
    "\n**THE ROWS OVER THE AISLES, AND THE LONG HALL, 2026-10-10.** Deli Counter 0.207.0 "
    "(`patches/patch_dc_aisle_rows.py`). The furnish's pieces are spec volumes by the time the "
    "lights derive, so a room's shelving is visible to `derive_light_anchors` as `shelf_run_r<hash>`, "
    "`gondola_aisle_N`, `stock_rack`, `pack_wall_island` and their kin; the aisle census before the "
    "change (`docs/findings/fixture_rows/aisle_census.py`, `aisle_census_0206_1.txt`) read 514 of 702 "
    "rooms with a shelf volume and 293 with two or more lanes at least an aisle wide, most lanes 2 to "
    "6 m. `_lanes_for_room`: in a room whose words say it sells or stores (`_AISLE_ROOM_WORDS`; an "
    "office with a shelf unit keeps its tile grid), the floor-standing shelf volumes (`_SHELF_WORDS`, "
    "foot within 0.5 m of the floor, so a sign hung over an aisle is not a shelf) are projected across "
    "the room's long axis, clipped and merged, and every gap at least `level_design.island_aisle_width` "
    "(the contract's door width, 1.25 m) between them and the bounds is a lane; `_rows_for_room(..., "
    "lanes=)` lays each lane as a floor of its own width by WOOD's rule, the lines snapped to the pitch "
    "and kept inside the lane, the lamps along the room's length, the room's cap thinning every row "
    "alike; shelving that leaves no lane is laid across as before. The long hall: where the cap binds, "
    "WOOD's rule cannot hold both ways, and 0.206.0 kept the rows and thinned the lamps (a 58 x 20 m "
    "hall: three rows of four, 14.5 m between lamps); now rows across are traded for lamps along "
    "while the larger of the two spacings shrinks, a row at a time from the band that loses least "
    "(that hall: two rows of five at 11.6 m along and 10 m across; a 24 x 20 m hall keeps its three of "
    "four, whose across spacing is the larger). Proven over the furnished library before landing "
    "(`aisle_rows_diff.py`, 0.206.1 against the draft, a flat cap and no partitions): 322 rooms "
    "identical, 165 changed, which are the 61 rooms laid over their aisles and the 114 where the cap "
    "bound; rows moved 448, added 4, removed 125; lamps 4,374 to 4,099 in that derivation. The aisle "
    "rule alone changed the 61 and nothing else. Seven tests; the suite and the library rebuilt: "
    + RESULT_CENSUS + ". Cold run 9232 shows the deli's market aisles and the hideout from room "
    "stations.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert not RESULT_CENSUS.startswith("RESULT_"), "fill RESULT_CENSUS before applying"
    assert text.count(OLD_A) == 1, text.count(OLD_A)
    assert text.count(OLD_B) == 1, text.count(OLD_B)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    assert "THE ROWS OVER THE AISLES, AND THE LONG HALL" not in text, "already applied"
    text = (text.replace(BODY_ANCHOR, BODY_ANCHOR + BODY_ADDED)
                .replace(OLD_A, NEW_A).replace(OLD_B, NEW_B))
    i = text.index(NEW_B)
    assert text[i + len(NEW_B):].startswith("\n\n**229. "), "229's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 229: Deli Counter 0.207.0 landed")


if __name__ == "__main__":
    main()
