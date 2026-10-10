"""Roadmap 230: step 3 (the connectors) measured -- the ground behind the row, where a rear lane would run.

Appends the measurement to 230's body. The anchor must match exactly once; nothing is written on
a miss. The generated index is regenerated afterwards by `tools/roadmap_status.py --write`.

    python patches/patch_roadmap_230_step3_measured.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

BODY_ANCHOR = (
    "room, anything needing the navmesh. Lands after 9231's record with 0.176.1 and Deli Counter "
    "0.207.0.\n"
)
BODY_ADDED = (
    "\n**STEP 3 MEASURED, 2026-10-11** (`docs/findings/rear_lane/`, `rear_census.py --cold` over the 27 "
    "cold workspaces' themed specs): every strip site turns its back on the same side -- every "
    "building fronts the main road, the yards with a dumpster stand on the rear walls 6 m out, and "
    "the plate's far edge lies 21.5 to 28.5 m beyond the row's rear line plus its yards, over the "
    "row's whole length (117 to 190 m), with nothing in that band but one parking field and the "
    "cover; the Empties always stand across the main road, never behind; and the one side road "
    "already reaches 9.5 to 16.5 m into the band on every strip site, so a lane laid 3 m past the "
    "yards crosses it for a junction. The hospital's courtyard has 14.5 m behind and no side road, "
    "and wants the guide's institutional service edge instead. What a lane needs, by the guide's "
    "numbers: 3.5 to 5 m wide at the yards' edge plus a 3 m apron; an owner (the row's businesses) "
    "and users (deliveries to the rear doors Lot 0.91.0 gives landings, refuse at the dumpsters, "
    "staff), which is what P14 and P17 ask `S_ADJACENCY` to see; and TWO connectors to the main road "
    "for a loop rather than two more approaches -- the side road, and an end connector in the 13 m "
    "between the last building and the plate's edge, with a gate carrying a state where it meets "
    "the lane. The roads are Level Factory's (`site_variation`'s road grammar, roadmap 199's "
    "inversion), so the lane is a grammar element placed from the row's rear line and yards the "
    "spec carries; Lot lays its surface, kerbs and junctions and its audit counts the loop "
    "(`site_targets.road_graph` reads 0 loops on every site today) and the lane's users. Priced "
    "before the look: a lane is a road -- a slab, two junctions, its own poles, and the responder "
    "and getaway routes change (212/215's gates). Not measured: whether it reads as a lane, the "
    "campus, the navmesh's second way round, and the built scene's clearance behind the yards.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    assert "STEP 3 MEASURED, 2026-10-11" not in text, "already applied"
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + BODY_ADDED)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 230: step 3 measured")


if __name__ == "__main__":
    main()
