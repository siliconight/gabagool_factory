"""Roadmap item 177: the z-fight pairs, measured -- 436 were 5 (Deli Counter 0.198.0).

    python patch_roadmap_177_facing.py

Anchored on item 177's status line as read 2026-10-06; must match once.
Run `tools/roadmap_status.py --write` and `--check` after.
"""
import pathlib

RM = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD = (" from 9164 to 9187, on merged cover boxes, and reached no finding; with Deli Counter 0.191.0, "
       "9188's compose exited 0 for the first time. Open: the z-fight pairs themselves, on three of "
       "9188's fifteen buildings.*\n")
NEW = (" from 9164 to 9187, on merged cover boxes, and reached no finding; with Deli Counter 0.191.0, "
       "9188's compose exited 0 for the first time. THE PAIRS, MEASURED 2026-10-06 (cold run 9189's "
       "composed buildings, `docs/findings/zfight_by_facing_side/`): 431 of deli_a01's 198, office's 121 "
       "and rail_station_a02's 117 were faces no camera can reach -- bottoms pressed on a slab, caps sunk "
       "4 mm under the next one, pieces over tile seams -- counted because the gate buried a pair only "
       "inside matter on BOTH sides of its plane. Deli Counter 0.198.0 judges a pair by the side its faces "
       "face, with a 2-D cover to the gate's tolerance: 2, 2 and 1. Open: a frame of those five (two "
       "partition-meets-exterior-wall junctions, the office's reception desk flush with its ledge), and "
       "then the decision this item owes -- block, warn or delete.*\n")


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(OLD) == 1, "item 177's status line not found once; refusing"
    RM.write_bytes(text.replace(OLD, NEW).encode("utf-8"))
    print("PIPELINE_ROADMAP.md: item 177's pairs measured")


if __name__ == "__main__":
    main()
