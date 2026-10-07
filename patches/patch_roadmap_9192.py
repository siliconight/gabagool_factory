"""Roadmap: item 196 on cold run 9192.

    python patch_roadmap_9192.py

Anchored on 196's status line in full, as patch_roadmap_0202.py wrote it and
as read 2026-10-07 (1,227,746 bytes, LF). Then run
`tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S196_OLD = ("*STATUS: NARROWED 2026-10-07 -- fixed in the generator, unproven in a level. Deli Counter 0.202.0: "
            "`_wall_slots` offers a slot only where a built wall (`layout_lint.built_walls`) holds the piece's "
            "whole run, the unheld slots dropped after the shuffle so only a piece that stood against nothing moves "
            "(dropped before it, the first draft re-rolled 33 specs); the refurnished library's census reads 0 of "
            "3,998 (was 155 of 4,086 in 18 shells), 20 specs moved, 153 fewer pieces, cigarette machines 121 -> "
            "119. The furnish and club probes stood their rooms in walls that were open edges, and now stand them "
            "in the shell. Open: the next cold run that draws a deli, to see the customer floor's open edge bare; "
            "a partition is still unfurnished (`_seed_clear` keeps every piece 1.0 m off a partition's line).*\n")
S196_NEW = ("*STATUS: NARROWED 2026-10-07 -- fixed in the generator and seen in a level, with a regression. Deli "
            "Counter 0.202.0: `_wall_slots` offers a slot only where a built wall (`layout_lint.built_walls`) holds "
            "the piece's whole run, the unheld slots dropped after the shuffle (dropped before it, the first draft "
            "re-rolled 33 specs); the refurnished library's census reads 0 of 3,998 (was 155 of 4,086 in 18 "
            "shells), 20 specs moved, 153 fewer pieces, cigarette machines 121 -> 119. Cold run 9192 (0 "
            "interventions, findings 64 -> 64, 9190's draw): deli_a01's ATM stands on the west wall, not 2.3 m in "
            "front of the case, its two poster boards on the south wall, the case clear in the frame; Laser Tag's "
            "PlayerStuck 9 -> 4, the four gone all at the customer floor. THE REGRESSION: a piece no built wall in "
            "its room holds is dropped, not placed elsewhere, and the six delis lost 18 of their 20 video poker "
            "cabinets (deli_a01 4 -> 0, cr_deli, night_deli and corner_deli_heist_01 3 -> 0, deli_a02 3 -> 1, "
            "deli_a03 4 -> 1) against the walker's two a store. Open: the delis' cabinets; a partition is still "
            "unfurnished (`_seed_clear` keeps every piece 1.0 m off a partition's line), which is where they would "
            "go.*\n")


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(S196_OLD) == 1, "anchor found %d times" % text.count(S196_OLD)
    text = text.replace(S196_OLD, S196_NEW)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 196 moved on; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
