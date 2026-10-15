"""Roadmap 105 measured 2026-10-15 (`docs/findings/open_items_remeasure/`): the first step the item asked for.
Replaces 105's three-line status block (asserted once); the item stays OPEN. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_105_measured.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = ("*STATUS: OPEN 2026-09-06 -- RAISED FROM A WALK. ITEM 37 GAVE THE SITE\nDIFFERENT BUILDINGS; THIS IS "
              "ABOUT WHERE LOT PUTS THEM, WHICH IS A SEPARATE\nAXIS AND HAS NEVER BEEN VARIED OR MEASURED.*")
HEADING = "\n\n**105. Lot builds one arrangement of buildings, and nothing varies it.**"
STATUS_NEW = (
    "*STATUS: OPEN 2026-10-15 -- MEASURED, the first step this item asked for, and the premise holds with a number "
    "(`docs/findings/open_items_remeasure/`, `arrangements_105.py`). Six plans -- the three seeded candidates of "
    "urban_row_001 (cold run 9314) and of restaurant_row_001 (9311), read off each candidate's drawn site spec -- "
    "stand the mission's buildings in ONE arrangement: three in a row facing south at rot 0, at x -51 / +1 to +4 / "
    "+48 to +54, deli, pharmacy, office; the 1 to 6 m shifts between seeds are the drawn archetype's own width, and "
    "seed_9003's three stand at the same coordinates in both missions. What the seed varies is the block and not "
    "the row: the same `block` grammar cuts its side streets and rear lane at different x per seed (25.0 and "
    "-80.2; -20.0 and +75.2; -21.0 and +76.2), the far side's Empties are dealt afresh (0 of 13 at the same spot "
    "between any two seeds), and both missions are `site_shape: strip`, so what the shape varies was not read. "
    "Left, the item's own: a plan grammar that varies where the buildings stand and which faces address the "
    "street, measured against sightlines and cover before it ships.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD)
    assert i >= 0 and text.count(STATUS_OLD) == 1, "105's status block not found once"
    k = i + len(STATUS_OLD)
    assert text[k:].startswith(HEADING), ("the block does not end just above its heading", text[k:k + 80])
    text = text[:i] + STATUS_NEW + text[k:]
    m = text.find(STATUS_NEW)
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "105's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 105: status replaced (OPEN, measured); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
