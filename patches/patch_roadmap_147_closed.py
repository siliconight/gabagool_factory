"""Roadmap 147 CLOSED, re-measured 2026-10-15 (`docs/findings/open_items_remeasure/`). Replaces 147's two-line
status block (asserted once). The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check` after it.

    python patches/patch_roadmap_147_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD = ("*STATUS: OPEN 2026-09-11 -- MEASURED FROM ITEM 142'S BLACK PROP; ITEM 54'S\nPRICE, NOW SEEN FROM "
              "THE FLOOR*")
HEADING = ("\n\n**147. One centre row at a 4.0 m reach cannot light a room wider than 8 m,\nand the median room is "
           "12 m.**")
STATUS_NEW = (
    "*STATUS: CLOSED 2026-10-15 -- the rows cover the room and the cap holds, re-measured "
    "(`docs/findings/open_items_remeasure/`). Deli Counter 0.206.0 (roadmap 229) lays a room's rows by its work "
    "plane -- at most 1.5 x A apart across the shorter axis, A the lamp's height over the work surface, the outer "
    "row within half of that of its wall, 3 rows and 12 lamps a room at most -- 0.207.0 down a shop's aisles, "
    "0.207.1 a fixture a bay in a home. Today's library: the rooms as this item measured them (714 in 130 built "
    "specs, median short side 12.0 m, p90 21.0, 80 % wider than 8.4 m) and 1,004 fluorescent rows, 957 off the "
    "centreline, 390 of 431 lit rooms with more than one run, where 0.206.0's census read 513 of 513 on the "
    "centreline (its own `row_census.py`, re-run). The budget, by what the renderer pairs (Level Factory 0.159.0; "
    "a baked light on a lightmapped mesh is skipped): on cold run 9308's package 3 of 3,275 meshes carry more "
    "than 8 -- the horizon glow at 238, a wires cell at 32, a roof at 9 -- and no room floor or ceiling tile; by "
    "reach alone 162 would, the number this item's instrument counted and not what is drawn. Kept: the spacing "
    "is derived from the work plane and Lux's range from the drop, two derivations and not the one formula this "
    "item proposed (rows at 2.7 to 6 m stand closer than twice the 4.0 m reach, which is why they cover); and "
    "cold run 9005's hospital was not re-walked.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD)
    assert i >= 0 and text.count(STATUS_OLD) == 1, "147's status block not found once"
    k = i + len(STATUS_OLD)
    assert text[k:].startswith(HEADING), ("the block does not end just above its heading", text[k:k + 80])
    text = text[:i] + STATUS_NEW + text[k:]
    m = text.find(STATUS_NEW)
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "147's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 147 CLOSED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
