"""Roadmap 230: cold run 9232 proves steps 1, 2 and 4 in a shipped level.

Replaces the head of 230's status block and appends the record to its body. Each anchor must
match exactly once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_230_9232.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_HEAD = (
    "*STATUS: NARROWED 2026-10-10 -- steps 1, 2 and 4 are LANDED: Level Factory 0.176.0 and 0.176.1, "
    "Lot 0.111.0 and 0.112.0 (`patches/patch_lot_targets.py`, the targets in the audit, 774 passed on "
    "the repo). "
)
NEW_HEAD = (
    "*STATUS: NARROWED 2026-10-11 -- steps 1, 2 and 4 are LANDED AND PROVEN in a shipped level: cold "
    "run 9232 (restaurant_row_001 with `cluster: auto`, 0 interventions, 0 retries, the package closed "
    "and baked; `docs/cold_runs/cold_9232/`) drew every candidate by `C03_station_neighborhood` (the "
    "anchor deli, then the guide's pharmacy and office, where the untemplated draws gave depot and "
    "self-storage, office and station, supermarket and parking garage), placed, dressed and shipped "
    "ONE lot, drew no `S_ADJACENCY` line (a deli, a pharmacy and an office fit the matrix with no rule "
    "to quote: the quiet audit is the template's point), and said its targets as `S_TARGETS` (3 "
    "enterable inside 3 to 8; ordinary fabric 96 % above 50 to 75 %; 2 approaches; 0 loops, the way "
    "back the way in; a 55 m stretch without a focal point on each leg; 1 field, 1 driveway, 3 yards). "
    "Step 3 is MEASURED (`docs/findings/rear_lane/`): 21.5 to 28.5 m of empty plate behind every strip "
    "row, the side road already reaching into it, a lane and an end connector the loop. Level Factory "
    "0.176.0 and 0.176.1, Lot 0.111.0 and 0.112.0 (`patches/patch_lot_targets.py`, 774 passed). "
)
BODY_ANCHOR = (
    "the campus, the navmesh's second way round, and the built scene's clearance behind the yards.\n"
)
BODY_ADDED = (
    "\n**COLD RUN 9232, THE FIRST DRAW BY TEMPLATE THAT SHIPPED** (`docs/cold_runs/cold_9232/NOTES.md`): "
    "9231's brief on the landed set, 0 interventions, 0 retries, 3 candidates distinct, 0 blockers on "
    "both legs, picked seed_9104, `closure verdict: ok=true, 0 issue(s) over 81 resource(s)`, the bake "
    "run. `cluster_resolved` asked `auto`, got `C03_station_neighborhood` in every spec; the candidates' "
    "lots `deli_a03 + pharmacy_a01 + office`, `deli_a01 + pharmacy_a01 + office`, `deli_a03 + "
    "pharmacy_a02 + office`; the themed site, the art jobs and the package carry the same three. No "
    "pair rule spoke; the seven `S_TARGETS` lines read the level against the guide's starting numbers, "
    "and two of them -- no loop, a 55 m stretch without a focal point on each leg of the critical "
    "route -- are the case for step 3's lane. Beside it, Deli Counter 0.207.0's first level: the deli's "
    "market aisles on three rows over the three lanes between its authored aisle shelves (-5.2, +0.4, "
    "+4.8 off the room's centre, where 0.206.1 stood them at -5.6, -0.4, +4.4 across it) and its "
    "hideout on one fixture; `rooms_before_after.png` against 9229. Route completion read 0.92 on the "
    "templated lot where the station lot read 1.00, with no major finding; not chased here.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_HEAD) == 1, text.count(OLD_HEAD)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    assert "COLD RUN 9232, THE FIRST DRAW BY TEMPLATE THAT SHIPPED" not in text, "already applied"
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + BODY_ADDED).replace(OLD_HEAD, NEW_HEAD)
    i = text.index(NEW_HEAD)
    j = text.index("\n", i)
    assert text[j:].startswith("\n\n**230. "), "230's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 230: cold run 9232 proves steps 1, 2 and 4")


if __name__ == "__main__":
    main()
