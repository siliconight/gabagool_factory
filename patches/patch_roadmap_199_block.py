"""Roadmap 199: the loop exists -- Level Factory 0.177.0's `block` grammar and Lot 0.113.0, proven in
cold run 9233.

Replaces the head and the tail of 199's status block and appends the record to its body. Each
anchor must match exactly once; nothing is written on a miss, and nothing is written while the
RESULT_ placeholder is unfilled. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_199_block.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

RESULT_9233 = ("ran at 0 interventions and 0 retries, the package closing and baking: four roads, the lane "
               "resolved as two T stems stopped at the streets with no signal, `S_TARGETS` reading `1 loop(s) "
               "in the road graph over 4 junction(s)` and `1 service lane(s) ... serving 3 building(s)`, Laser "
               "Tag's route completion 1.00 where 9232's same lot read 0.92 (stuck events 19 where 65, player "
               "deaths 9 where 35), the lane seen as a dark back lane at dusk with no poles of its own, and the "
               "block priced against 9232's package at +107 draws and +0.55 ms p95 a heading median on a 5.7 ms "
               "frame, a tenth of it, where the second street is in view -- a street's kerbs, markings and "
               "furniture are per-piece draws, a merge per road per material the lever")

HEAD_OLD = ("*STATUS: OPEN 2026-10-10 -- measured, not started: every generated level is one street "
            "form. ")
HEAD_NEW = (
    "*STATUS: NARROWED 2026-10-11 -- the loop exists: Level Factory 0.177.0's `block` grammar "
    "(`patches/patch_lf_block_grammar.py`; spellings block, loop, service_lane, rear_lane, alley, "
    "back_lane) keeps the T and adds a second side street past the row's far end and a 5 m service "
    "lane without a sidewalk behind the row between the two streets, 8 m past the deepest rear face "
    "(Lot's dumpster pad and apron, and the road margin), ending on both as T stems, so the road graph "
    "has one cycle where every level had none; Lot 0.113.0 stops the lane at the streets, never a "
    "signal, and `S_TARGETS` counts it. Cold run 9233 (restaurant_row_001, `road_grammar: block` "
    "beside `cluster: auto`) " + RESULT_9233 + " (`docs/cold_runs/cold_9233/`). Before it, measured: "
    "every generated level was one street form. "
)
TAIL_OLD = ("`road_grammar.py` names the step: roads first, buildings hung off them. Owner: Level "
            "Factory (`road_grammar`, `site_variation`) and Lot (the audit).*")
TAIL_NEW = (
    "`road_grammar.py` names the next step for a crossroads with a loop and for the spine: roads "
    "first, buildings hung off them; `block` adds its loop inside the buildings-first dependency, "
    "which is why it cost no equivalence proof (T and cross are byte for byte what they were). Left: "
    "that inversion and the X and spine grammars; the rear doors the lane serves (Deli Counter's "
    "shells have none on the rear face, so every rear spur in 9233 was recorded undrawn, "
    "`LOT_PATH_END_OFF_DOOR`); a plate that keeps its parking field beside the lane (9233 lost its one "
    "field to the lane's band); the brief's three distinct approach profiles. Owner: Level Factory "
    "(`road_grammar`, `site_variation`) and Lot (the audit), with Deli Counter for the rear doors.*"
)
BODY_ANCHOR = (
    "- **Not measured:** exposure and cover along an approach, the street from a player's eye, and "
    "whether a T is wrong for a 105 m yard: the brief allows fewer approaches where the footprint "
    "does.\n"
)
BODY_ADDED = (
    "\n**THE LOOP, LANDED 2026-10-11.** The ground behind the row was measured first "
    "(`docs/findings/rear_lane/`, 27 cold workspaces): 21.5 to 28.5 m of empty plate beyond the "
    "row's rear line and its dumpster yards on every strip site, the one side street already "
    "reaching 9.5 to 16.5 m into it, the Empties always across the main road. **Level Factory "
    "0.177.0** (`block`, in `road_grammar.py` beside T and cross): `_far_line` stands the second side "
    "street past the row's end farther from the first, half a band off the last building, ending on "
    "the front road and running to the plate's far margin like the first; `_block` lays the lane "
    "between the two streets' centre lines at `LANE_SETBACK` (Lot's `PAD_OUT + APRON`, 6 m, plus "
    "`ROAD_MARGIN`) past the deepest rear face, `LANE_WIDTH` 5 m (the guide's van-scale service "
    "lane), no sidewalk, `kind: service_lane` and `serves` for the audit; `_rear_spurs` gives every "
    "building a door path from its rear face to the lane's edge, half a metre short of the "
    "carriageway, and the far building a side door onto the second street; the plate widens and "
    "deepens for them. The lane ends on both streets as T stems -- the junction Lot has drawn since "
    "0.61.0 -- so nothing asks Lot for a shape it has never resolved. **Lot 0.113.0:** a road without "
    "a sidewalk is a lane; its junction with a street is stop-controlled and never signalised (the "
    "rule as it stood signalised every yielding road at an arterial and would have hung a signal at "
    "the alley's mouth); `S_TARGETS` says the lane and the buildings it serves. Proven: 2,209 and 777 "
    "passed; one Level Factory test reads Lot's resolution (`terminal` on the crossed street, the "
    "stem's slab clipped, stop on the lane, no signal). **Cold run 9233** " + RESULT_9233 + ".\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert not RESULT_9233.startswith("RESULT_"), "fill RESULT_9233 before applying"
    for name, a in (("head", HEAD_OLD), ("tail", TAIL_OLD), ("body", BODY_ANCHOR)):
        assert text.count(a) == 1, (name, text.count(a))
    assert "THE LOOP, LANDED 2026-10-11" not in text, "already applied"
    text = (text.replace(BODY_ANCHOR, BODY_ANCHOR + BODY_ADDED)
                .replace(HEAD_OLD, HEAD_NEW).replace(TAIL_OLD, TAIL_NEW))
    i = text.index(TAIL_NEW)
    assert text[i + len(TAIL_NEW):].startswith("\n\n**199. "), "199's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 199: the loop landed")


if __name__ == "__main__":
    main()
