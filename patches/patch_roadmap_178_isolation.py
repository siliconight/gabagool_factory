"""Roadmap 178: Lot's isolation instrument graduated, 2026-10-15 (Lot 0.124.0; `docs/findings/open_items_remeasure/`).
Replaces 178's status block (asserted once, from its first line to the line ending the block's `*`). The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_178_isolation.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = "*STATUS: NARROWED 2026-10-15 -- re-measured per instrument (`docs/findings/open_items_remeasure/`, "
HEADING = "\n\n**178. The instruments report and nothing blocks, and that is one defect\nrather than four.**"
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-15 -- one of the five graduated, the day it was re-measured. Lot 0.124.0 "
    "(732b4ad): `site_tactical.analyze` emits `LOT_ISOLATED_BUILDING`, severity major, in `report[\"findings\"]` "
    "beside the warning string nothing read -- the shape Level Factory's Lot adapter already ingests from "
    "`tactical.findings` and `pick.py` already counts, so a candidate with a building no path or street reaches "
    "loses the pick to one without and the finding stands in the report; not a blocker, by the rule the item "
    "itself gave (a number that does not block is fine when something counts it). Graduated by item 59's rule: "
    "the warning read 65 of 79 sites before Lot 0.77.0 taught the graph the street and 0 of 320 after "
    "(`lot_intel_178.py`), the four exceptions a 2026-09-23 experiment whose door paths predate the `building` "
    "key. Proven: 3 new tests fail on 0.123.0's tree and pass after; Lot's suite 847; cold run 9317 "
    "(urban_row_001, 0 interventions): the finding on 0 of 3 candidates, findings 109 -> 109 across the export, the "
    "pick seed_9104 PASS 100 as 9314's. The other four are where the morning's re-measure left them: the unbaked "
    "package stops the cold drive (root 4bf7bb5); `test_navgate_population` runs with every suite on a built "
    "library; `objective_approaches` reads 2 on 289 of 324 and S5 still warns only, a threshold being design; "
    "the z-fight gate fires and blocks nothing, its decision the walker's (177). Earlier status kept: filed with "
    "the z-fight gate on five runs called zeros, isolation on 65 of 79, approaches 0 on 38 and never above 2, the "
    "navgate test hiding a stair regression for five weeks (176).*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "RESULT_9317" not in STATUS_NEW, "fill the cold run's result first"
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
    print("roadmap 178 updated; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
