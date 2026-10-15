"""Roadmap 178 NARROWED, re-measured per instrument 2026-10-15 (`docs/findings/open_items_remeasure/`). Replaces
178's status block (asserted once, from its first line to the line ending the block's `*`). The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_178_narrowed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = "*STATUS: OPEN 2026-09-24 -- FOUR INSTRUMENTS, ALL REPORTING, NONE BLOCKING,\n"
HEADING = "\n\n**178. The instruments report and nothing blocks, and that is one defect\nrather than four.**"
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-15 -- re-measured per instrument (`docs/findings/open_items_remeasure/`, "
    "`lot_intel_178.py`): two of the five changed shape, two moved under a Lot fix, one is where it was. The "
    "fifth, the unbaked package: the cold drive stops the run when `light_bake.json`'s `ok` is not true (root "
    "4bf7bb5, 2026-10-11, the day it was found), Level Factory 0.178.5 retries the bake and records every attempt, "
    "and 9314 baked on attempt 1. `test_navgate_population`: it runs with every Deli Counter suite run on a "
    "machine whose `build/` exists -- 157 `*.navgate.json` there today, rebuilt 2026-10-15 08:44 for 0.223.0, "
    "the suite passed after it -- so its cadence is the library rebuild's, most releases this month. Lot's "
    "isolation warning: `build_graph` joined the buildings sharing a road in Lot 0.77.0 (2026-09-24, the day "
    "this was filed), and over the 324 cold-run sites on disk in 107 workspaces 4 read an isolated building, all "
    "four in one lot-shape experiment (`shape-sweep-9500-ws`), 0 on any cold run proper. `objective_approaches` "
    "over the same 324: 0 on 14, 1 on 16, 2 on 289, 3 on 4, 4 on 1 (was 0 on 38 of 79, never above 2); S5 still "
    "warns only. The z-fight gate: fires and blocks nothing still -- 9314's compose printed FAIL and ERROR for "
    "deli_a01 (2 pairs in 755 solids) and office (2 in 425), OK on the other 15 scenes, and exited 0; the "
    "decision it owes is the walker's (177). Left: that decision; the isolation warning's graduation by 59's rule "
    "once the four experimental sites are attributed; a threshold for the approaches, which is design. Earlier "
    "status kept: filed with the z-fight gate on five runs called zeros, isolation on 65 of 79, approaches 0 on "
    "38 and never above 2, the navgate test hiding a stair regression for five weeks (176).*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "178's status block not found once"
    j = i
    while True:
        k = text.find("\n", j)
        assert k > 0
        if text[i:k].endswith("*"):
            break
        j = k + 1
    old = text[i:k]
    assert old.count("*STATUS:") == 1 and old.endswith("*"), old[-80:]
    assert text[k:].startswith(HEADING), ("the block does not end just above its heading", text[k:k + 80])
    text = text[:i] + STATUS_NEW + text[k:]
    m = text.find(STATUS_NEW)
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "178's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 178 NARROWED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
