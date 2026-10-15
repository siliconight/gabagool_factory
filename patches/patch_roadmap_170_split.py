"""Roadmap 170: the split the item asked for first, measured 2026-10-15 (`docs/findings/roof_openings_170/`).
Replaces 170's status block (asserted once, from its first line to the line ending the block's `*`); the item
stays OPEN. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_170_split.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = "*STATUS: OPEN 2026-09-23 -- MEASURED, NOT STARTED. 58 of 58 `roof_access`\n"
HEADING = ("\n\n**170. Every roof opening in the library is an open hole, and a building does\nnot have an open "
           "hole in its roof.**")
STATUS_NEW = (
    "*STATUS: OPEN 2026-10-15 -- the split this item asked for first is measured, and nothing is built "
    "(`docs/findings/roof_openings_170/`, `census.py` over the 446 authored specs): 16 stairs reach the roof, "
    "all switchbacks with `cut_slabs`, in specs with no roof hatch link, so each leaves the slab open at its "
    "head -- nine of them the mission buildings Level Factory writes today (`lf_deli_001_*`, "
    "`lf_restaurant_row_001_*`, `lf_urban_row_001_*`), so every level made this week has a stair head open to "
    "the sky; that is the bulkhead's population. Of 69 roof ladders, 43 have a `hatch` link at their foot (42 "
    "`interior` with `roof_hatch_exit`) and cut the slab -- the lid's population -- and 26 are exterior, parapet "
    "or platform ladders that cut nothing and need no lid; the earlier 58 of 58 counted built output, this counts "
    "the contract. Build order by population and cost: the lid first (one Zoo species over each roof hatch link, "
    "placed where Deli Counter already emits `HATCH_<x>_<y>`), then the bulkhead over the 16 stair heads with "
    "its doorway derived like any door and the slab no longer cut. Both are look changes against the walker's "
    "reference: frames before either ships. Earlier status kept: MEASURED, NOT STARTED 2026-09-23 -- 58 of 58 "
    "`roof_access` ladders cut the slab they arrive through, 74 `hatch` links do the same, nothing in any tool "
    "emits a lid.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "170's status block not found once"
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
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "170's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 170 re-measured (OPEN); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
