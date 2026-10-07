"""Roadmap item 177: the five pairs, framed -- nothing visible at the level's own lighting.

    python patch_roadmap_177_frames.py

Anchored on the end of item 177's status line as patch_roadmap_177_facing.py
wrote it; must match once. Run `tools/roadmap_status.py --write` and
`--check` after.
"""
import pathlib

RM = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD = ("Open: a frame of those five (two partition-meets-exterior-wall junctions, the office's reception "
       "desk flush with its ledge), and then the decision this item owes -- block, warn or delete.*\n")
NEW = ("FRAMED the same day (`tools/look_shots.py` on 9189's walk copy, five given stations): the "
       "deli_a01 junction's north view (mean luminance 24.9/255) shows a dark seam and no stripe; the "
       "other four are under 7/255, the level's own night lighting, where nothing can show. Open: the "
       "decision this item owes -- block, warn or delete -- on a gate that now counts 5 pairs with an "
       "open side, none seen on screen.*\n")


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(OLD) == 1, "item 177's open clause not found once; refusing"
    RM.write_bytes(text.replace(OLD, NEW).encode("utf-8"))
    print("PIPELINE_ROADMAP.md: item 177 framed")


if __name__ == "__main__":
    main()
