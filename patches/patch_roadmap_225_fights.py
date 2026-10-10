"""Roadmap 225 NARROWED: Level Factory 0.172.0's gate fails a fight, not a sparkle.

Replaces 225's status block and adds the measurement to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`, never by this script.

    python patches/patch_roadmap_225_fights.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: OPEN 2026-10-10 -- found the moment the walk's shot bot could see again (Level "
    "Factory 0.171.0): it FAILS two of cold run 9222's ladder stations on jitter, 3.60% and "
    "2.33% over a 2.0% gate, and says coplanar surfaces are fighting. Mapped pixel by pixel, "
    "every change is scattered speckle over the drop ceiling's acoustic tiles, a wall and the "
    "floor, and no surface flips as a block: texture sparkle, which the gate's one number cannot "
    "tell from z-fighting. Not known: whether the sparkle shows in play.*\n"
)
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- the gate tells them apart (Level Factory 0.172.0): a fight "
    "is a sampled pixel that changes by more than 64 of 255, and a station fails past 0.5% of "
    "the frame. A control of two quads 0.01 mm apart fails at 2.02%; 9222's five stations pass "
    "at 0.00% to 0.12%, the two sparkling ones noted as sparkle. Two designs were refuted "
    "against the control first (largest connected region; moving the near plane). Left: whether "
    "the ceiling's sparkle shows in play.*\n"
)
BODY_ANCHOR = (
    "Owner: Level Factory for the gate; whoever owns the ceiling's texture for the second.\n"
)
PROOF = (
    "\n**1. DONE, Level Factory 0.172.0** (`docs/findings/shotbot_sparkle/`, `measured.txt`). A "
    "control was built first, `zfight_control.tscn`: two quads, red and blue, 0.01 mm apart.\n"
    "- **Refuted, the proposal above:** judging the largest connected region. The control's "
    "fight broke into regions of at most 54 samples, the sparkle's of 28, and a gate at 64 "
    "written into the shot bot passed the control.\n"
    "- **Refuted:** moving the near plane instead of the camera. No texture sample moves, so no "
    "sparkle, but the control flipped 0 samples too.\n"
    "- **Kept, the size of a flip.** The control's flips are all 255 of 255. 9222's four "
    "interiors flip by a median of 16 to 19, at most 7.6% of their flips over 64. Counted over "
    "64 as a share of the frame: the control 2.02%, 9222 0.00% to 0.12%, and the gate sits at "
    "0.5%. Run as the verdict, the control fails and all of 9222's stations pass.\n"
    "- **What it gives up:** a fight between two surfaces within 64 of each other, which a "
    "person can barely see.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    for name, anchor in (("status", OLD_STATUS), ("body", BODY_ANCHOR)):
        n = text.count(anchor)
        assert n == 1, (name, "anchor matches", n, "times")
    text = text.replace(OLD_STATUS, NEW_STATUS).replace(BODY_ANCHOR, BODY_ANCHOR + PROOF)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**225. "), "225's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 225: NARROWED, the gate fails a fight and notes sparkle")


if __name__ == "__main__":
    main()
