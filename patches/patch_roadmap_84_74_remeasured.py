"""Roadmap 84 CLOSED and 74 re-measured (OPEN), 2026-10-15 (`docs/findings/open_items_remeasure/`). Replaces each
item's status block (each asserted once, from its first line to the line ending the block's `*`). The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_84_74_remeasured.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [
    ("*STATUS: OPEN 2026-08-29 -- DIAGNOSED, NOT FIXED, AND THE FIX IS A DECISION\n",
     "\n\n**84. Zoo computes per-vertex wear, exports it correctly, and the engine does\nnot use it.**",
     "*STATUS: CLOSED 2026-10-15 -- the decision was made and built, re-read "
     "(`docs/findings/open_items_remeasure/`). Level Factory 0.86.0's `zoo_worldskin.gd` (`_vertex_colour_albedo`) "
     "draws COLOR_0 as albedo on every GLB that is an object rather than a tile -- a car, a container, a chair, a "
     "lamp -- for any material some surface of which is not white, and leaves it off for the kit and the tiled "
     "families, which is this item's 3.8x argument applied: objects wear, tiles do not; "
     "`tests/unit/test_vertex_colour_and_clutter_skins.py` pins both halves, from the 0 of 1,650 surfaces that drew "
     "it on walk 9052_rain. Zoo 1.59.0 built on it, a car's paint riding its vertices, measured on the eight cars "
     "of cold run 9141. The kit's wear stays off by that decision; that it repeats per module is item 79's, as "
     "this status already said.*"),
    ("*STATUS: OPEN 2026-08-29 -- MEASURED ACROSS TWELVE SHIPPED BUILDINGS WITH A\n",
     "\n\n**74. Every wall in every building is the same 2.00 m module, and it gets\nworse the longer the facade.**",
     "*STATUS: OPEN 2026-10-15 -- re-measured with its own instrument on cold run 9314's three mission buildings "
     "(`docs/findings/open_items_remeasure/`, `repetition_74_9314.out.txt`): deli_a01 347 wall instances, 64 "
     "forms, worst run 18 of 21 segments at one form; office 196 / 25 / 11; pharmacy_a01 73 / 24 / 7, where the "
     "2026-08-29 baseline read it 67 / 20 / 7; every run at a 2.00 m pitch. In the ruler's own terms nothing moved, "
     "and it says why: it measures the form vocabulary, and what shipped since is per-instance -- world-space UVs "
     "on every module (80's record) end the texture restart at the seam without making a run of eighteen fewer "
     "than eighteen placements of one mesh. The second ruler, one that reads appearance, still does not exist, and "
     "the Empties, merged one mesh a side, are outside this one. The two closing moves are still the two: a "
     "vocabulary that grows with the span, or per-instance variation seen by a ruler that can see it.*"),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    for old_head, heading, new in ITEMS:
        i = text.find(old_head)
        assert i >= 0 and text.count(old_head) == 1, ("status block not found once", old_head[:60])
        j = i
        while True:
            k = text.find("\n", j)
            assert k > 0
            if text[i:k].endswith("*"):
                break
            j = k + 1
        old = text[i:k]
        assert old.count("*STATUS:") == 1 and old.endswith("*"), old[-80:]
        assert text[k:].startswith(heading), ("the block does not end just above its heading", text[k:k + 80])
        text = text[:i] + new + text[k:]
        m = text.find(new)
        assert text[m + len(new):].startswith(heading), "status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 84 CLOSED, 74 re-measured; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
