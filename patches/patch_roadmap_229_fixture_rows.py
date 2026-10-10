"""Roadmap 229: indoor fixtures stand in a perfect line (the walker's ask, 2026-10-10).

Appends item 229 after 228's body, which closes the file. The anchor must be the file's last
line; nothing is written otherwise. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_229_fixture_rows.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ANCHOR = (
    "Cold runs 9226 (warehouse_yard_001), 9227 "
    "(county_hospital_001) and 9228 (gas_stop_001) are staged to prove a recipe each.\n"
)
STATUS = (
    "*STATUS: OPEN 2026-10-10 -- the walker's ask, grounded and not yet built: 513 of 513 shipped "
    "fluorescent rows stand on their room's centreline along its longer axis, 303 of them at the "
    "five-lamp cap (`docs/findings/fixture_rows/`); the nine references are digested in "
    "`docs/reference/INDOOR_FIXTURE_PLACEMENT_GUIDE.md`. Owner: Deli Counter, with Zoo for the "
    "species and Lux for the rigs.*\n"
)
BODY = (
    "**229. Indoor fixtures stand in a perfect line.** The walker, 2026-10-10: \"making indoor "
    "light fixtures not always be in a perfect line, so it looks a little less robotic in the "
    "line/lighting placement\", with nine references on where fixtures go and a sheet of twenty "
    "fixture types, digested in `docs/reference/INDOOR_FIXTURE_PLACEMENT_GUIDE.md`.\n"
    "\n"
    "**Why it is a line.** `deli_counter/lights.py` derives one `fluorescent` row per interior "
    "room (`derive_light_anchors`, line 1166): at the room's centre, along its longer axis "
    "(`_row_for_bounds`, 941), `count = round(length / 4.0)` held to 1..5 (`_TARGET_SPACING`, "
    "137; `_MAX_FIXTURES`, 173) and `spacing = length / count`, so the lamps spread evenly over "
    "the whole room whatever stands in it. Zoo expands the row centred on `pos` "
    "(`zoo_keeper/core/fixtures.py:row_points`, the same `start = -(count-1)/2 * spacing` as "
    "Lux's rig) and stands a troffer at every lamp; Lux puts a rig at every marker. The "
    "departures are caused and rare: a run splits at a ceiling void, a lamp steps 0.40 m off a "
    "partition it would hang in, a row lying along a partition moves to the larger side (DC "
    "0.116.0, roadmap 143). Counted over the 131 shipped manifests "
    "(`docs/findings/fixture_rows/row_census.py`): 513 rows in 478 rooms, 513 on the "
    "centreline, 513 along the longer axis, 35 rooms with more than one run; 303 rows carry five "
    "lamps and the spacing runs from 3.0 to 11.6 m, because the cap, not the room, decides the "
    "count. The 222 pendants follow the same line at `area / 25` bulbs; the club set's 32 washes "
    "are the one layout that steps side to side.\n"
    "\n"
    "So the look the walker names is three things at once, and jitter would fix none of them:\n"
    "- **Every room is lit by one rule,** office or stockroom, bar or bedroom: a troffer row down "
    "the middle. The references' first rule is the opposite, start with function, not symmetry "
    "(DSG Metro); the fixture follows what it lights. The sheet names twenty fixtures and Zoo "
    "builds three indoor ones: the troffer, the bare bulb on a cord, the club can.\n"
    "- **The row is spread over the room, not laid to the work.** WOOD's shop formula: rows at "
    "most 1.5 x the height from the work surface to the fixture apart, the outer row no more "
    "than a third to a half of that from the wall; a 24 x 24 ft shop under a 9 ft ceiling takes "
    "three rows 8 ft apart, and two rows leave its sides dark. On this kit's lamps near 3.0 m "
    "over a 0.9 to 1.05 m counter that is rows about 3 m apart with the outer one within 1.5 m "
    "of the wall: a sales floor 8 m wide is three rows over its aisles, not one down its centre; "
    "a 4 m stockroom is one; a corridor is one. The line is right in the narrow room and wrong "
    "in the wide one.\n"
    "- **Nothing in the ceiling causes an offset.** A real row sits in a joist bay or a tile "
    "grid, so it is off the room's centreline by a structural number; a duct, a beam or a hatch "
    "breaks it; a fixture added later over a bench stands off the grid; a dark tile is a tube "
    "nobody replaced (Lux 0.62.0 already fails one a room). The alternative is forbidden in so "
    "many words by the walker's own guide (`docs/reference/HUMAN_AUTHORSHIP_GUIDE.md`): "
    "asymmetry sprinkled without cause is token humanity, and uniform irregularity is the first "
    "anti-pattern it names. The lampsusa taxonomy says where the grid is RIGHT: the formal room "
    "(an office, a bank, a ward, a terminal) is balanced, evenly spaced and symmetrical; the "
    "relaxed room (a home, a dive bar) avoids pattern; the dynamic room (a club, an arcade) is "
    "asymmetric, some areas brighter, clusters.\n"
    "\n"
    "**The shape of the fix, in Deli Counter, as rules with causes** (`derive_light_anchors` "
    "already holds the room's `role`, the business and its volumes through `_volumes_in`):\n"
    "- **The layout follows the room's use and furniture.** A sales floor's rows run over its "
    "aisles between the `shelf_run`s and over the counter's work side (never behind the clerk); "
    "a workshop's over the benches; an office's on a tile grid; a corridor's one flush mount "
    "every few metres; a stair's one a landing; a home's one centre fixture a room, a pendant "
    "over the table, a sconce in the hall; a dive bar's pendants over the bar and the tables "
    "with sconces on the walls. WOOD's rule decides how many rows a wide room gets.\n"
    "- **Offsets have structural causes and come from the seed:** the joist pitch the row's line "
    "snaps to (0.4 m), the tile grid the troffers sit in (0.6 m), a duct run that breaks a row "
    "the way a void does now (`_row_runs`).\n"
    "- **The retrofit layer, sparingly:** a later task light off the grid over one work point, a "
    "sconce pair at a door, a fixture missing; clusters with space between them, never uniform "
    "density (the guide's rule for props, line 587, holds for lights).\n"
    "- **Species to grow in Zoo,** from the sheet: a strip light (the open two-lamp industrial "
    "luminaire, for stockrooms and garages), a wall sconce, a high-bay for the warehouses, an "
    "exit sign over every exit door of a public building; recessed cans and under-cabinet light "
    "as emission on the pieces that carry them. One row in `FIXTURES`, one genome, one recipe "
    "each, as the module says.\n"
    "- **Daylight switches the window row** (WBDG: the first 10 to 15 ft from the glass is "
    "daylit): by day a store's window row is off and its back rows on. That belongs to the "
    "five-times-of-day work, and it is a second honest cause of a ceiling that is not uniform.\n"
    "\n"
    "**Price before look** (the hard rule). `_TARGET_SPACING` went from 3.0 to 4.0 m on "
    "2026-08-24 for the eight-light cap (line 129: density is a budget number first), before the "
    "light bake (Level Factory 0.131.0, on by default since 0.144.0) and before the paired count "
    "(0.159.0) showed the cap at 0 over on a baked level. What more lamps cost now is bake time "
    "and the troffers' draws, to be measured and not assumed: interior stations, control and "
    "subject, before a layout that triples a sales floor's rows ships.\n"
    "\n"
    "**Not measured:** how the rows READ. The census counts lines; whether a room looks designed "
    "is roadmap 18's gate and a person's eye, and the walker's named it. Frames at interior "
    "stations before and after are the fix's evidence.\n"
    "\n"
    "Owner: Deli Counter, with Zoo for the species and Lux for the rigs.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(ANCHOR) == 1, text.count(ANCHOR)
    assert text.endswith(ANCHOR), "228's body no longer closes the file"
    assert "**229. " not in text, "229 already exists"
    text = text + "\n" + STATUS + "\n" + BODY
    i = text.index(STATUS)
    assert text[i + len(STATUS):].startswith("\n**229. "), "229's status is not above its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 229 added: indoor fixtures stand in a perfect line")


if __name__ == "__main__":
    main()
