"""Roadmap 230: step 3 (the connectors) landed as the `block` grammar's service lane and proven in
cold run 9233.

Replaces one sentence of 230's status block and appends the record to its body. Each anchor must
match exactly once; nothing is written on a miss, and nothing is written while the RESULT_
placeholder is unfilled. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`.

    python patches/patch_roadmap_230_step3.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

RESULT_9233 = ("proved it at 0 interventions (the lane stopped at both streets, one loop over four junctions, "
               "the lane counted, Laser Tag's route completion 1.00 where 9232's same lot read 0.92; seen as a "
               "dark back lane at dusk; priced at +107 draws and +0.55 ms a heading median against 9232's "
               "package, the second street's furniture and markings the cost)")

OLD = (
    "Step 3 is MEASURED (`docs/findings/rear_lane/`): 21.5 to 28.5 m of empty plate behind every strip "
    "row, the side road already reaching into it, a lane and an end connector the loop. "
)
NEW = (
    "Step 3 is LANDED as the guide's service lane: Level Factory 0.177.0's `block` road grammar "
    "(`patches/patch_lf_block_grammar.py`) lays a 5 m lane without a sidewalk behind the row between "
    "two side streets, 8 m past the deepest rear face, carrying `kind: service_lane` and the "
    "buildings it `serves`, and the road graph has its loop; Lot 0.113.0 stops the lane at the "
    "streets and `S_TARGETS` counts it; cold run 9233 " + RESULT_9233 + " "
    "(`docs/cold_runs/cold_9233/`). Measured first (`docs/findings/rear_lane/`): 21.5 to 28.5 m of "
    "empty plate behind every strip row, the side road already reaching into it. Left of step 3: "
    "the rear doors the lane serves (Deli Counter's shells have none on the rear face), the gate with "
    "a state, the rear passage and the shared court. "
)
BODY_ANCHOR = (
    "proves nothing. The lever if the tenth matters on the low-end target: one module a form with "
)


def main():
    raw = ROADMAP.read_bytes()
    assert raw.count(b"\r") == 0, "the roadmap is LF; a CR means something changed it"
    text = raw.decode("utf-8")
    assert not RESULT_9233.startswith("RESULT_"), "fill RESULT_9233 before applying"
    assert text.count(OLD) == 1, text.count(OLD)
    text = text.replace(OLD, NEW)
    i = text.index(NEW)
    j = text.index("\n", i)
    assert text[j:].startswith("\n\n**230. "), "230's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 230: step 3 landed")


if __name__ == "__main__":
    main()
