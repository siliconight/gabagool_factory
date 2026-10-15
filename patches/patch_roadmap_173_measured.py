"""Roadmap 173: the instrument run on a current package and every edge sorted, 2026-10-16
(`docs/findings/drop_edges_173/`). Replaces 173's status block (asserted once, from its first line to the line
ending the block's `*`); the item stays OPEN. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_173_measured.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = "*STATUS: OPEN 2026-09-23 -- THE INSTRUMENT EXISTS AND CANNOT YET BE A GATE.\n"
HEADING = "\n\n**173. A drop is either guarded or declared, and today nothing declares one.**"
STATUS_NEW = (
    "*STATUS: OPEN 2026-10-16 -- the instrument run on a current package and every edge it found put in a named "
    "class (`docs/findings/drop_edges_173/`, `sort_edges.py`). Cold run 9317's package (urban_row_001), a 0.5 m "
    "grid: 133,992 standable cells, 22,445 drop edges, 16,739 unguarded, 6,004 of them indoors. Sorted by what "
    "each stands beside: 3,753 the plate's rim (188's fence), 2,703 the INSTRUMENT'S OWN -- a cell on a "
    "footprint's wall line, where the headroom ray starts inside the exterior wall and sees nothing, so a slab's "
    "edge under a wall reads standable with a bottomless drop beyond (939 of those indoors; the fix is a shape "
    "test at the standing point, CLAUDE.md's ray-versus-shape rule); 278 inside a stair's footprint, the open "
    "side of a flight; 48 a hatch or ladder's own hole; 16 a `floor_hole` link, a drop the spec declared; 34 roof "
    "rims; 8,757 the tops of furniture and props (3,862 indoors: a body on a desk can walk off it, and that is "
    "not a level defect -- a gate must read what a surface IS, not its height); and 1,053 storey rims, 651 "
    "indoors, which is the item's class and the number left: edges at a floor's level inside a building with a "
    "full-storey drop and nothing above step-over height -- cut-slab collars (168), stair discharge voids, "
    "mezzanine lips, or holes nobody railed, not yet told apart. `walkable_edge.gd`'s MAX_ROWS was 4,000 and kept "
    "the deepest rows, the rim and not one indoor edge; it is 200,000. What would make the gate, in order: the "
    "instrument's blind spot closed; standable meaning floor-like; the declared set read off the package's own "
    "records and emitted as `walk_off_ledge` links in Dispatch's `navigation_hints`; the residue attributed to "
    "zero on one package and then frozen, failing on a new entrant (178's baseline pattern). Earlier status "
    "kept: 2026-09-23, the instrument exists and cannot yet be a gate -- 121 unguarded cells at the stairwell the "
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
    print("roadmap 173 re-measured (OPEN); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
