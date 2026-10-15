"""Roadmap 170 NARROWED: the lid shipped (Zoo 1.113.x + Deli Counter 0.224.x), proven by cold run 9316. Replaces
170's status block (asserted once, from its first line to the line ending the block's `*`). The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_170_lid.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: OPEN 2026-10-15 -- the split this item asked for first is measured, and nothing is "
                   "built")
HEADING = ("\n\n**170. Every roof opening in the library is an open hole, and a building does\nnot have an open "
           "hole in its roof.**")
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-15 -- the lid shipped, the bulkhead is left (`docs/findings/roof_openings_170/`, "
    "`patches/patch_roof_hatch.py` + `patch_roof_hatch_gates.py`). Zoo 1.113.0/1.113.1 `roof_hatch`: a steel "
    "curb ring on the slot's edges and a lid hinged along the back top edge, the lid the species' interactive "
    "-- `open` (the default) stands it vertical, inside the curb's footprint, `closed` lays it flush; 260 tris "
    "and 0 coincident pairs at every genome corner (the bollard control at its 2 / 2 / 1). Deli Counter "
    "0.224.0/0.224.1: one `roof_hatch` prop slot per `hatch` link on the roof slab, the hole plus 0.08 m of curb "
    "a side, 0.2 m tall, with a `hatch` interactive machine (open by default so the ladder's `roof_hatch_exit` "
    "stays a route for every walker; shutting it is the game's) and its gameplay entry, the hinge turned away "
    "from the ladder's climber; the library rebuilt with it, 40 slots in 40 of 159 built specs. Cold run 9315 "
    "stopped at the art pass on two gates that were right -- the placement gate measured the lid leaning past "
    "vertical 0.33 m outside the slot, the circulation gate found the hatch's own box 0.2 m inside its ladder's "
    "climb volume -- so the lid stands at 90 degrees on a hinge 4 cm inside the back wall, and `circulation` "
    "excuses a hatch in its own ladder's volume as it excuses a stair's guard in its stair. Cold run 9316: 0 "
    "interventions, courthouse_a02 placement 340/340, circulation 0 conflicts with 1 excused, z-fight 0 pairs; "
    "frames in `docs/cold_runs/cold_9316/hatch_frames/`. Left: the bulkhead over the 16 stair heads (step 2), "
    "the walker's eye on the frames and on the open default, and 3 of the 43 authored hatches whose specs are not "
    "built. Earlier status kept: the split (16 stairs reaching the roof, 43 hatch links under 69 roof ladders, "
    "26 ladders cutting nothing) and 2026-09-23's MEASURED, NOT STARTED -- 58 of 58 `roof_access` ladders cut "
    "the slab, 74 `hatch` links do, nothing in any tool emits a lid.*"
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
    print("roadmap 170 NARROWED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
