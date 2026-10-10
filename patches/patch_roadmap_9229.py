"""Roadmaps 228 and 229: cold run 9229 prices the seven-module borough and the ceiling rows.

Replaces both status blocks and adds 9229's record to each body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_9229.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

S228_OLD = (
    "shows the walker the trees and prices them; the borough's seven modules are priced by 9229. "
)
S228_NEW = (
    "shows the walker the trees and prices them; the borough's seven modules are PRICED by cold "
    "run 9229 (restaurant_row_001 rebuilt, 0 interventions): 277 instances in 7 modules and 25 "
    "draws where 9225 shipped 18 and 69, +27 draws a heading against the package's backdrop-off "
    "copy where 9225's cost +52. "
)
B228_ANCHOR = (
    "are authored starts, not measurements; the walker's eye on 9230's frames judges the current "
    "forms first.\n"
)
B228_ADDED = (
    "\n**THE SEVEN-MODULE BOROUGH PRICED, cold run 9229** (`docs/cold_runs/cold_9229/NOTES.md`): "
    "restaurant_row_001 rebuilt on the landed set at 0 interventions, the seed 9225 picked; Lot "
    "0.109.1's line reads `277 piece(s) (backdrop_rowhome 276, water_tower 1)`, Level Factory "
    "shipped `277 instances of 7 module(s) ... 25 draw calls` (9225: 18 modules, 69). Priced "
    "against the package's own backdrop-off copy: +27.0 draws a heading mean (+10 to +40) where "
    "9225's eighteen modules cost +52; p95 +0.29 ms median against a 0.18 ms spread on a level "
    "that now stands at 3,036 draws and 6.7 ms a frame (the rows, roadmap 229, are the 4 % "
    "between). Cold run 9230 (the hospital's parkland, from 9227) is running with Zoo 1.97.0's "
    "tree and Lot 0.110.0's clustered belt.\n"
)
S229_OLD = (
    "*STATUS: NARROWED 2026-10-10 -- the first step is shipped and not yet seen. "
)
S229_NEW = (
    "*STATUS: NARROWED 2026-10-10 -- the first step is shipped, SEEN and PRICED in cold run 9229 "
    "(restaurant_row_001, 0 interventions): 44 rows and 174 lamps where 9225 had 17 and 72 "
    "(`docs/cold_runs/cold_9229/`); the rooms read as ceilings laid out, three rows across each, "
    "on the tile grid (`rooms_before_after.png`); the rows cost +122 draws a heading mean, 4 % of "
    "the level, and no frame time the harness can see at these stations (p95 +0.27 ms median "
    "inside a 0.35 ms spread); the bake 12.5 s longer. A residence-like room inside a shop "
    "(the deli's apartment hideout) took an office ceiling: the home rule should key on the room's "
    "words too. "
)
B229_ANCHOR = (
    "- **Not yet seen.** Frames at interior stations (`tools/room_stations.py`) on 9229's package "
    "against 9225's are the evidence; the walker's eye is the gate.\n"
)
B229_ADDED = (
    "\n**SEEN AND PRICED, cold run 9229** (`docs/cold_runs/cold_9229/NOTES.md`): the same level 9225 "
    "built, rebuilt at 0 interventions on the same seed. The site manifest: 17 fluorescent rows "
    "and 72 lamps over three buildings became 44 and 174 (2.4 x; the 32 bulbs below grade "
    "unchanged); fourteen of sixteen rooms took three rows, most at the twelve-lamp cap, the "
    "deli's stairwell and stockroom two, the station's agent wing one; the lines on the tile "
    "grid (the market aisles at x -63.6, -58.4, -53.6 across a room centred on -58.5). "
    "`rooms_before_after.png`, six rooms from the same interior stations: one receding line of "
    "troffers in 9225, three rows across the ceiling in 9229, nothing skewed, the store reading "
    "as a store's ceiling and the office as an office's. Priced two ways: the borough's backdrop "
    "against its off copy (+27 draws, roadmap 228), and the rows as 9225's package against "
    "9229's with both backdrops off: **+121.9 draws a heading mean (0 to +276), 4 % of a "
    "2,914-draw level**, the troffer hardware and the light-budget tiles Zoo splits; p95 +0.27 ms "
    "median INSIDE that pair's 0.35 ms spread (the controls' own medians 6.34 and 7.01), so no "
    "frame time is attributable; the bake 104.2 s against 91.7.\n"
    "- **Refinement from the frames:** the deli's `apartment_hideout`, a residence-like room in a "
    "shop building, took three rows of four because the home rule keys on the building. A room "
    "whose words say apartment, hideout, bedroom or living takes the home rule's one fixture, "
    "whatever the building: one line in `_work_plane`'s table, the next Deli Counter release.\n"
    "- **For the walker's eye:** three rows of four at the cap, or two of five, for a 12 x 11 m "
    "room; and the grids are perfectly regular, the tile snap being the only structural cause so "
    "far. The draws are the number to watch as the species grow: every fixture is hardware.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    for old in (S228_OLD, B228_ANCHOR, S229_OLD, B229_ANCHOR):
        assert text.count(old) == 1, (text.count(old), old[:60])
    text = text.replace(B228_ANCHOR, B228_ANCHOR + B228_ADDED).replace(S228_OLD, S228_NEW)
    text = text.replace(B229_ANCHOR, B229_ANCHOR + B229_ADDED).replace(S229_OLD, S229_NEW)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmaps 228 and 229: cold run 9229 recorded")


if __name__ == "__main__":
    main()
