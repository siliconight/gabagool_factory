"""Roadmap 199: Lot's layout measured against the walkable-city brief.

Replaces 199's status block and adds the census to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_199_census.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: OPEN 2026-10-07 -- filed, not compared: the walker's Dynamic Walkable City brief "
    "(`docs/reference/DYNAMIC_WALKABLE_CITY_LEVEL_DESIGN_BRIEF.md`), the companion of the "
    "land-use guide Lot already builds to, \"should be placed and inform future Lot layout\". "
    "Nothing has been measured against it yet.*\n"
)
NEW_STATUS = (
    "*STATUS: OPEN 2026-10-10 -- measured, not started: every generated level is one street "
    "form. `docs/findings/walkable_city/route_census.py` over the 22 cold workspaces from 9180 "
    "to 9226: 22 of 22 are site shape `row` and road grammar `T`, two roads and one junction, "
    "two approaches at the plate's edge, zero cycles, two or three buildings, the objective 30 "
    "to 106 m from the junction. Against the brief: two approaches of the same profile where it "
    "asks three distinct, no loop where it asks a short one, a long bypass and a shortcut, the "
    "T's stem an unlabelled dead end; the edge is explained since 228. `road_grammar.py` names "
    "the step: roads first, buildings hung off them. Owner: Level Factory (`road_grammar`, "
    "`site_variation`) and Lot (the audit).*\n"
)
BODY_ANCHOR = (
    "**NEXT.** Map the brief's hard failures and design warnings onto those gates one by one, "
    "and measure the gap on a few briefs before any layout changes.\n"
)
ADDED = (
    "\n**MEASURED 2026-10-10** (`docs/findings/walkable_city/`): `route_census.py --cold` reads "
    "each cold workspace's themed drawn spec and counts the roads, the junctions (a road ending "
    "on another is a T, crossing it an X), the road ends at the plate's edge (approaches), the "
    "cycles of the road graph (loops), the buildings, the objective's distance to the nearest "
    "junction, the fence and the backdrop. 22 specs, four missions: all `row` and `T`, 161 to "
    "242 m of street in two roads, one T, two approaches (the T's stem ends inside the plate, 18 "
    "m short of the edge on restaurant_row_001), zero cycles, the hub 30 to 106 m from the "
    "junction. The missions differ in plate, building count and `route_shape`, not in street "
    "form; no brief has asked for a grammar but `T`, and `road_grammar.py`'s own docstring says "
    "the roads are derived from the buildings and that the reverse is the next step. The `paths` "
    "are door-to-street walks, not routes.\n"
    "- **The brief's gates, applied** (the README's table): hard failure 1 is not hit, the hub "
    "has an approach; the design warnings \"every route has the same tactical profile\" and "
    "\"all routes converge into one chokepoint\" both hold of a T with two mirrored ends; the "
    "traversal review is partial, Laser Tag judging routes on the building graph "
    "(`S_ONE_APPROACH`) with nothing reporting approaches or loops on the street graph.\n"
    "- **In order:** the inversion `road_grammar.py` names, with `T` reproducing today's output "
    "exactly; grammars that give the brief its counts, `X` (4 approaches, 0 loops), `block` (a "
    "back street and two cross streets: 4 and 1), `spine` (a parallel alley and two links: 2 to "
    "4 and 1 to 2; the alley the concealed service route); the audit growing approaches, cycles, "
    "the hub's distance and unlabelled dead ends as INFO beside `S_ONE_APPROACH`; the blocked-edge "
    "review as a run with a road end closed.\n"
    "- **Not measured:** exposure and cover along an approach, the street from a player's eye, "
    "and whether a T is wrong for a 105 m yard: the brief allows fewer approaches where the "
    "footprint does.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + ADDED).replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**199. "), "199's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 199: measured against the brief")


if __name__ == "__main__":
    main()
