"""Roadmap 225 CLOSED: the gate tells a fight from a sparkle, and the ceiling's sparkle is its sampling.

Replaces 225's status block and adds the answer to its body. Each anchor must match exactly once;
nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`, never by this script.

    python patches/patch_roadmap_225_closed.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- the gate tells them apart (Level Factory 0.172.0): a fight "
    "is a sampled pixel that changes by more than 64 of 255, and a station fails past 0.5% of "
    "the frame. A control of two quads 0.01 mm apart fails at 2.02%; 9222's five stations pass "
    "at 0.00% to 0.12%, the two sparkling ones noted as sparkle. Two designs were refuted "
    "against the control first (largest connected region; moving the near plane). Left: whether "
    "the ceiling's sparkle shows in play.*\n"
)
NEW_STATUS = (
    "*STATUS: CLOSED 2026-10-10 -- the gate tells a fight from a sparkle (Level Factory "
    "0.172.0: a control z-fight fails at 2.02%, 9222's stations pass at 0.00% to 0.12%), and "
    "the sparkle is the skins' own sampling: the acoustic ceiling tile is a 256 x 256 skin "
    "sampled NEAREST / NEAREST_MIPMAP_NEAREST, as Pixelcoat's pixel skins are by design, so it "
    "swaps whole texels under any motion in play too. Filtering skins linear is a look call for "
    "the walker, not a defect here.*\n"
)
BODY_ANCHOR = (
    "- **What it gives up:** a fight between two surfaces within 64 of each other, which a "
    "person can barely see.\n"
)
ANSWER = (
    "\n**2. ANSWERED, read off 9222's package:** the drop ceiling's tiles are "
    "`M_Skin_ceiling_tile_delco_1997` (Zoo's `ceiling_delco_1997_13_*`), a 256 x 256 skin, "
    "mipmapped and lossless, sampled magFilter NEAREST and minFilter NEAREST_MIPMAP_NEAREST -- "
    "the drywall ceilings sample the same way. Nearest sampling takes one texel a pixel, so any "
    "sub-pixel camera motion swaps whole texels on a fine-grained skin: the speckle in the maps, "
    "and the shimmer a moving camera sees. It is the pixel skins' look, which Pixelcoat asks for "
    "and Zoo honours, not this ceiling's defect. Filtering skins `linear`, as the business signs "
    "have been since Pixelcoat 0.62.0, is the realism direction and the walker's call to make "
    "and price.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    for name, anchor in (("status", OLD_STATUS), ("body", BODY_ANCHOR)):
        n = text.count(anchor)
        assert n == 1, (name, "anchor matches", n, "times")
    text = text.replace(OLD_STATUS, NEW_STATUS).replace(BODY_ANCHOR, BODY_ANCHOR + ANSWER)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**225. "), "225's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 225: CLOSED")


if __name__ == "__main__":
    main()
