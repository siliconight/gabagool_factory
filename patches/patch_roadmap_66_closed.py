"""Roadmap 66 CLOSED: answered by Level Factory 0.67.1 on 2026-09-11 and never recorded
(`docs/findings/open_items_remeasure/`). Replaces 66's status block (asserted once, from its first line to the line
ending the block's `*`). The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check` after it.

    python patches/patch_roadmap_66_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: OPEN 2026-08-25 -- MEASURED, AND THE FIRST READING OF IT WAS WRONG\nAND IS KEPT BELOW. "
                   "The suite is green and shallower than the sentence that\nrecommends it*")
HEADING = "\n\n**66. `verify-manifest` prescribes a remedy that under-proves what it\ncertifies.**"
STATUS_NEW = (
    "*STATUS: CLOSED 2026-10-15 -- both asks were answered by Level Factory 0.67.1 on 2026-09-11 and never recorded "
    "here (`docs/findings/open_items_remeasure/`). The DRIFT message (`packages/tools/contracts.py`, "
    "`ContractResult.message`) reads \"re-certify per docs/CERTIFY.md: the real-tool smoke (adapters and contracts, "
    "no geometry), the zoo walkabout (Blender), the engine leg (Godot) and the lux visual leg, as the changed tool "
    "requires; then promote the manifest\", pinned by `tests/unit/test_drift_remedy_names_the_legs.py`; "
    "`tests/real_tools/conftest.py` prints a coverage block after every run, each test by name as ran or skipped "
    "with the skip's reason -- the 1.40.0 re-ground's smoke read \"ran 10 of 12 real-tool tests, 1 skipped, 1 "
    "FAILED\" before the table moved and \"11 of 12\" after. Not this item's, kept in the record: the "
    "`docs/CERTIFY.md` the line names lives at the factory root and not in Level Factory's tree (0.97.0's note), "
    "and that runbook is written against zoo 0.34.0 and pixelcoat 0.10.0 while the set has been certified since "
    "factory 1.36.0 by an install test (roadmap 202); the doctor's own row says only \"re-certify\".*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "66's status block not found once"
    k = i + len(STATUS_OLD_HEAD)
    assert text[k:].startswith(HEADING), ("the block does not end just above its heading", text[k:k + 80])
    text = text[:i] + STATUS_NEW + text[k:]
    m = text.find(STATUS_NEW)
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "66's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 66 CLOSED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
