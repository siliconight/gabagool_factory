"""Roadmap 230: cold run 9231 stopped at the export (the site spec's draw missed the template),
Level Factory 0.176.1 drafted for it, and step 4 (the targets in the audit) drafted as Lot 0.112.0.

Replaces the head of 230's status block and appends the record to its body. Each anchor must
match exactly once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_230_9231.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_HEAD = (
    "*STATUS: NARROWED 2026-10-10 -- steps 1 and 2 are LANDED; cold run 9231 (restaurant_row_001 "
    "with `cluster: auto` in its brief) is the first level drawn by a template and audited by the "
    "pair rules. "
)
NEW_HEAD = (
    "*STATUS: NARROWED 2026-10-10 -- steps 1 and 2 are LANDED and step 4 (the targets in the audit) "
    "is DRAFTED as Lot 0.112.0 (`patches/patch_lot_targets.py`, proven on a clone). Cold run 9231 "
    "(restaurant_row_001 with `cluster: auto` in its brief), the first level drawn by a template, "
    "STOPPED at the export's closure gate with 0 interventions: the template resolved itself "
    "(`C03_station_neighborhood`) in every candidate and the pair rules spoke (P17 prefer on the "
    "deli, the office and the station), but the site spec builder's own `pick_lot` draw missed the "
    "template while the planner and the compose spec took it through `lot_for_brief`, so the art "
    "leg dressed a pharmacy the site never placed and the station's glb went unresolved "
    "(`docs/cold_runs/cold_9231/`). Level Factory 0.176.1 (`patches/patch_lf_cluster_site.py`) reads "
    "the template in one function for all four draws and refuses, by test, any `pick_lot` outside "
    "the library without it; cold run 9232 re-runs the brief on it. "
)
BODY_ANCHOR = (
    "so a hideout over a deli takes one fixture; the library rebuilt reads 1,140 rows and 4,133 "
    "lamps where 0.206.0 read 1,156 and 4,217, ten more rooms on the home's one fixture "
    "(`docs/findings/fixture_rows/row_census_0206_1.txt`).\n"
)
BODY_ADDED = (
    "\n**COLD RUN 9231, THE FIRST DRAW BY TEMPLATE, STOPPED AT THE EXPORT** "
    "(`docs/cold_runs/cold_9231/NOTES.md`): 9229's restaurant_row_001 brief with `\"cluster\": "
    "\"auto\"` added; 0 interventions, 0 retries, 3 candidates distinct, 0 blockers on the shell "
    "and art legs, picked seed_9104 -- and `EXPORT_CLOSURE_BROKEN: 1 unresolved res:// "
    "reference(s)`: `rail_station_a02.glb` unresolved in the site and the lux scene, a themed "
    "`lot/pharmacy_a01/site.tscn` that `mission.tscn` never reaches, the bake then failing on the "
    "broken scene. The cause, read off the jobs: every candidate's site spec recorded "
    "`cluster_resolved` (asked `auto`, got `C03_station_neighborhood`, preferred deli, cr_deli, "
    "night_deli, pharmacy, office, office_stepped, bank_tower, apartment_walkup, twin) and drew "
    "9229's lots byte for byte (deli_a01, office, rail_station_a02 on the pick), while the art jobs "
    "were planned for deli_a01, office and pharmacy_a01: `lot_for_brief` (the planner, the compose "
    "spec) took the template and the site spec builder's `pick_lot` call, anchored since 0.73.0, "
    "did not. 0.176.0's own note said \"`grep lot_for` over the package names all three call "
    "sites\"; the fourth draw is a `pick_lot`, and the planner's disagreement guard compares the art "
    "jobs with the compose spec, not the site spec, so nothing before the export could see it. The "
    "closure gate did its job. **Level Factory 0.176.1:** `building_library.preferred_for_brief` is "
    "the one place the template is read off a brief, asked by `lot_for_brief` and by the site spec "
    "builder; a test walks `apps/` and `packages/` for every `pick_lot(` outside the library, "
    "brackets balanced, and refuses one without `preferred=`; a brief naming no cluster keeps its "
    "draw. What 9231 did prove: the template resolves and records itself; the pair rules read a "
    "drawn lot (`S_ADJACENCY`: deli and station across the local street, P17 prefer; office and "
    "station on one block, P17 prefer; a candidate's deli and depot, P14 prefer); Deli Counter "
    "0.206.1's hideout takes one anchor where 9229's took three (42 rows and 163 lamps site-wide "
    "where 9229 had 44 and 174). Not proven: the draw by template in a shipped level, and the home "
    "rule's look -- cold run 9232.\n"
    "\n**STEP 4 DRAFTED, Lot 0.112.0** (`patches/patch_lot_targets.py`, `site_targets.py`, six "
    "tests; 758 passed on a clone, the 8 failures the clone's missing `../deli_counter`): the level's "
    "numbers against the guide's starting targets (10.9) from the drawn spec alone, every line "
    "INFO as `S_TARGETS` -- the enterable buildings against 3 to 8; the ordinary fabric (every "
    "Empty instance and every lot building but the objective, over all of them) against 50 to "
    "75 %; the road ends at the plate's edge and the distinct first hops to the objective across "
    "the site graph against 2 meaningful approaches; the road graph's loops (edges less nodes plus "
    "components over the axis-aligned roads' junctions) against the preferred return loop; the "
    "longest stretch between focal points along the straight legs spawn to objective and objective "
    "to extraction (the leg's ends, the lot buildings and the junctions within 20 m of the line) "
    "against the guide's 20 to 50 m traveled, said as a floor on the real gap; the parking fields "
    "and bays, driveways and dumpster yards for the buildings they serve. Not measured, and said: "
    "landmarks (the spec carries signs, the brief the landmark), choices at a decision, regrouping "
    "room, anything needing the navmesh. Lands after 9231's record with 0.176.1 and Deli Counter "
    "0.207.0.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_HEAD) == 1, text.count(OLD_HEAD)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    assert "COLD RUN 9231, THE FIRST DRAW BY TEMPLATE" not in text, "already applied"
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + BODY_ADDED).replace(OLD_HEAD, NEW_HEAD)
    i = text.index(NEW_HEAD)
    j = text.index("\n", i)
    assert text[j:].startswith("\n\n**230. "), "230's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 230: cold run 9231 recorded, 0.176.1 and step 4 drafted")


if __name__ == "__main__":
    main()
