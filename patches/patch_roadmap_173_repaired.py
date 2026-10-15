"""Roadmap 173: the instrument repaired twice on the same package, 2026-10-16 (`docs/findings/drop_edges_173/`).
Replaces the status written an hour earlier (asserted once); the item stays OPEN. The index is NOT touched here:
run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_173_repaired.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: OPEN 2026-10-16 -- the instrument run on a current package and every edge it found put "
                   "in a named class")
HEADING = "\n\n**173. A drop is either guarded or declared, and today nothing declares one.**"
STATUS_NEW = (
    "*STATUS: OPEN 2026-10-16 -- the instrument run on a current package, every edge sorted, and the instrument "
    "repaired twice on the same package (`docs/findings/drop_edges_173/`, `sort_edges.py`, three runs kept). "
    "Cold run 9317's package (urban_row_001), a 0.5 m grid. Rays alone read 22,445 drop edges, 16,739 unguarded, "
    "6,004 indoors -- and the sort found 2,703 of them on a footprint's own wall line (939 indoors), the "
    "headroom ray starting inside the exterior wall and seeing nothing. A shin-high sphere test at each standing "
    "point (`PROBE_R` 0.20 at 0.60 m) took the indoor wall-line count to 32 and raised a second artefact, a floor "
    "cell beside a now-empty wall column reading a bottomless drop (2,090 indoors); testing the neighbour's own "
    "standing point before counting a drop took that to 191. Third run: 13,618 drop edges, 11,798 unguarded, "
    "2,998 indoors, sorted: 4,138 the plate's rim (188's fence), 1,357 wall-line outdoors (parapet tops and the "
    "sidewalk beside a face), 143 stair sides, 59 hatch holes, 16 declared `floor_hole` links, 266 roof rims, "
    "4,140 furniture and prop tops (1,428 indoors: a body on a desk walks off it, not a level defect), 57 ground, "
    "and 1,622 storey rims, 1,152 indoors, about 1,050 of them full-storey drops at a floor's level -- the item's "
    "class, left to attribute row by row against the slab holes `_stairs` and `_vertical_links` cut: cut-slab "
    "collars (168), discharge voids, mezzanine lips, or holes nobody railed. `walkable_edge.gd` carries both "
    "tests and MAX_ROWS 200,000 (4,000 kept only the rim). What would make the gate, in order: the storey rims "
    "attributed to zero on one package; standable meaning floor-like; the declared set read off the package's "
    "records and emitted as `walk_off_ledge` links in Dispatch's `navigation_hints`; the residue frozen, failing "
    "on a new entrant (178's pattern). Earlier status kept: 2026-09-23, the instrument exists and cannot yet be "
    "a gate -- 121 unguarded cells at the stairwell the walker stepped off, 2.90 m at floor level, and 5,897 "
    "drop edges on a clean package, 1,024 the deliberately open sides of staircases; a declaration is what "
    "separates the two.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "173's status block not found once"
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
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "173's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 173 updated (OPEN, repaired); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
