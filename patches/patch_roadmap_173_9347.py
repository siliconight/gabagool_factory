"""Roadmap 173 stays CLOSED: its status and body take cold run 9347 -- the drop-edge probe's slot refusal on a package
with deli_a03, reproduced on Level Factory 0.221.0's instrument and gone on 0.222.0's
(docs/findings/drop_edges_173/probe_body/).

Anchored: two passages read verbatim from the roadmap when this was written must each be there exactly once; nothing
is written otherwise. Every line LF. Then `python tools/roadmap_status.py --write` and `--check`.

    python patches/patch_roadmap_173_9347.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
EDITS = [("roadmap 173's status", 'refusal reproduced and removed on a fixture. Still not proven: a package with deli_a03 through the sweep, and a drop link in the flood (item 6). Earlier status kept: CLOSED 2026-10-18;', "refusal reproduced and removed on a fixture and on a package -- cold run 9347 (restaurant_row_001 with deli_a03, 0 interventions): the old instrument refuses at the sweep's phase on 9335's very row, (-61.62, 3.30, -9.87), and the new passes at all six. Still not proven: a drop link in the flood (item 6). Earlier status kept: CLOSED 2026-10-18;"), ("roadmap 173's probe-body paragraph", "occupies the cell beside it, outdoor rims, a flight's own side). Not attributed: precinct_yard_001's reach still spans 14,000 cells across phases, not the kerb's.\n", "occupies the cell beside it, outdoor rims, a flight's own side). Not attributed: precinct_yard_001's reach still spans 14,000 cells across phases, not the kerb's. **On a package with deli_a03** (cold run 9347, restaurant_row_001, seed 9003, made for this on 0.222.0, 0 interventions; its control arm reproduces its export's scan): the old instrument at the sweep's refusing phase refuses on (-61.62, 3.30, -9.87), a 3.3 m drop from slab_col_1 to slab_col_0 -- 9335's row to the centimetre -- with its flood at 41,244 cells (9335's 41,322); the new instrument passes at all six phases, 55,027 cells at that one. Over the four levels the old instrument refuses 1 of 24 arms and the new 0 of 24.\n")]


def main():
    raw = ROADMAP.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap has CRLF lines; nothing written")
    text = raw.decode("utf-8")
    for what, old, new in EDITS:
        if text.count(old) != 1:
            raise SystemExit("REFUSED: %s is there %d times, not once; nothing written" % (what, text.count(old)))
    for what, old, new in EDITS:
        text = text.replace(old, new)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 173 updated; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
