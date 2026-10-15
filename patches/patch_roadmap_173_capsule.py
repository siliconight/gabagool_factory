"""Roadmap 173: the instrument's standing test is the body's own capsule, 2026-10-16 (`docs/findings/drop_edges_173/`,
four runs on cold run 9317's package). Replaces the status written earlier the same night (asserted once); the item
stays OPEN. The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_173_capsule.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: OPEN 2026-10-16 -- the instrument run on a current package, every edge sorted, and the "
                   "instrument repaired twice")
HEADING = "\n\n**173. A drop is either guarded or declared, and today nothing declares one.**"
STATUS_NEW = (
    "*STATUS: OPEN 2026-10-16 -- the instrument made sound and the residue named: four runs on cold run 9317's "
    "package (`docs/findings/drop_edges_173/`, `sort_edges.py`). Rays alone read 22,445 drop edges, 16,739 "
    "unguarded, 6,004 indoors, and the sort found them full of the instrument's own: a floor's edge under an "
    "exterior wall (the headroom ray starting inside the wall), a surface inside a slab (the ray meeting a "
    "ceiling's underside, 236 cells at 6.3 m on the deli's roof whose top is 6.6), and once a shin-high sphere "
    "rejected the first, every floor cell beside a wall reading a bottomless drop toward it (2,090). "
    "`walkable_edge.gd`'s standing test is now the body's own capsule, 0.20 wide and 1.80 tall on the hit, "
    "overlapping nothing, asked of the cell and of a neighbour with no surface before it counts as a drop -- "
    "CLAUDE.md's rule that 'does a body fit' is a shape question. Fourth run: 8,722 drop edges, 7,330 unguarded, "
    "1,958 indoors, sorted: 1,855 the plate's rim (188), 545 wall-line outdoors (parapet tops, the sidewalk by a "
    "face), 45 stair sides, 52 hatch holes, 16 declared `floor_hole` links, 38 at a cut the builder recorded "
    "(the built slots' `fit.voids`, which land on deli_a01's stair, ladder, hatch and floor hole), 236 roof rims, "
    "3,858 furniture and prop tops (1,151 indoors: not a level defect, to be excluded by what a surface IS), 42 "
    "ground, and 643 storey rims, 592 indoors, which are THREE PLACES: deli_a01's ground floor (220 at 0.0 m, a "
    "storey down) and first floor (183 at 3.3 m, 6.6 m down to the basement along x -8, y 3.5-11.5 in its own "
    "frame), office's second floor (115 at 7.2 m), and about 75 smaller. None is at a hole the builder recorded: "
    "a void cut and not recorded, a wall with no collider at step-over height, or a lip somebody meant -- a "
    "morning's reading in the scene, not a census. Then, in order: the furniture excluded, the declared set read "
    "off the package's records and emitted as `walk_off_ledge` links in Dispatch's `navigation_hints`, the "
    "residue attributed to zero and frozen, failing on a new entrant (178's pattern). Earlier status kept: "
    "2026-09-23, the instrument exists and cannot yet be a gate -- 121 unguarded cells at the stairwell the "
    "walker stepped off, 2.90 m at floor level, and 5,897 drop edges on a clean package, 1,024 the deliberately "
    "open sides of staircases; a declaration is what separates the two.*"
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
    print("roadmap 173 updated (OPEN, the capsule); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
