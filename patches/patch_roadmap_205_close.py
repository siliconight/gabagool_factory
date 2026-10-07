"""Roadmap: close item 205 on cold run 9196 -- and refute the reading it was
filed on: there was no 25 m cooler run.

    python patch_roadmap_205_close.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_walker_answers.py left it
(1,265,410 bytes, LF, as read 2026-10-07). The status line is found by its
unique prefix and must sit directly above its item's heading. Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_PREFIX = "*STATUS: OPEN 2026-10-07 -- found by cold run 9195, which stopped at the art leg on it"
STATUS_NEW = ("*STATUS: CLOSED 2026-10-07 -- proven in a level, and the reading it was filed on refuted: there was no "
              "25 m cooler run. The placement gate and the composer's fit took a sibling slot whose id begins "
              "`<slot_id>_` as one of the slot's parts, so gas_station_a02's 3.28 m `cooler_run` took in "
              "`cooler_run_sales` (8.0 m) and read 25.442 m. Deli Counter 0.203.0: a node belongs to the longest slot "
              "id that names it (`themed_tscn.owns_node`), one rule for both readers; it had blocked 5 library "
              "buildings (three pawn shops, two gas stations). Cold run 9196 (gas_block_001, 0 interventions): the "
              "art leg passed with 0 blockers, `PRESENTATION_PLACEMENT_MISMATCH` 1 -> 0, and the level shipped.*\n")

NEXT = ("**NEXT.**\n"
        "- Read where the 25.442 m comes from:")
NEXT_NEW = ("**REFUTED, KEPT: there was no 25 m cooler run.** The status line above this item's first version read the "
            "greybox as laying one run 25.442 m long. The built slots say otherwise: `cooler_run` is 3.28 m at x 14.26 "
            "and `cooler_run_sales` 8.0 m at x -5.54, and the module placed was built to its slot. 25.442 m is exactly "
            "their union, x -9.54 to 15.90.\n"
            "\n"
            "**THE CAUSE.** `portable_building._slot_greybox_extent` (the gate) and `themed_tscn._slot_extent` (the "
            "composer's fit, which orients every module) counted a greybox node as the slot's when its name was the "
            "slot id or began `<slot_id>_` -- the rule for an opening's own parts (`_lintel`, `_sill`, `_pane`), "
            "written so `seg1` would not swallow `seg10`. A sibling slot whose id begins the same way was swallowed "
            "with them. Over the library: 9 of 145 buildings carry such an id pair (19 pairs), and in 5 the sibling "
            "has greybox nodes -- `counter` in cr_pawn, night_pawn and pawn_shop_a01 (read 9.86 x 6.36 m against "
            "its own 4.0 x 0.7), `cooler_run` in gas_station_a02 and fuel_stop_heist. Every level placing one of the "
            "five stopped at its art leg.\n"
            "\n"
            "**FIXED: Deli Counter 0.203.0** (`patches/patch_dc_slot_owner_tests.py`, `patches/patch_dc_slot_owner.py`). "
            "One rule, `themed_tscn.longer_siblings` and `themed_tscn.owns_node`: a node belongs to the longest slot "
            "id that names it. Both extents take the building's slot ids. The gate re-run on the real greybox with "
            "9195's kit read 167 of 167 matched. `build.py --all` changed no shell, slot or gameplay file, only each "
            "manifest's `built_utc`. Tests: 7, all failing on 0.202.0.\n"
            "\n"
            "**PROVEN: cold run 9196** (`docs/cold_runs/cold_9196/NOTES.md`): art leg 0 blockers of 69 findings, "
            "`PRESENTATION_PLACEMENT_MISMATCH` 1 -> 0, gas_block_001 exported and walked.\n"
            "\n"
            "**NEXT, as filed (answered above).**\n"
            "- Read where the 25.442 m comes from:")


def _replace_status(text, prefix, new_line, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times" % len(hits)
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    lines[i] = new_line.rstrip("\n")
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1265410, "PIPELINE_ROADMAP.md is %d bytes, read at 1,265,410" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(NEXT) == 1, "NEXT anchor found %d times" % text.count(NEXT)
    text = _replace_status(text, STATUS_PREFIX, STATUS_NEW, "**205. ")
    text = text.replace(NEXT, NEXT_NEW)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 205 closed, its first reading kept as refuted")


if __name__ == "__main__":
    main()
