"""Roadmap 223: the street band's lettering, and a band drawn 1.5x too wide.

Item 223 is appended after 222, the file's last item, its status directly above its heading,
refused if a 223 exists. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"
LAST = ("control that cannot currently fail the way it is meant to: the slab control still proves "
        "shadows draw, but not that the cap's 5 mm can be seen.\n")

ITEM_223 = (
    "\n"
    "*STATUS: OPEN 2026-10-10 -- note 10 generalised (item 219): a business Level Factory deals a "
    "Pixelcoat sign pack still letters its street band and its door box in Pixel Operator, sampled "
    "nearest; and the band is drawn 1.5x too wide, a 512 x 128 pack (4:1) on Lot's 6:1 quad. "
    "Groundwork kept: a Pixelcoat mint of Blue Highway Condensed byte-identical to Zoo's. Not "
    "started in a repo.*\n"
    "\n"
    "**223. The street band: Pixel Operator, and stretched.** "
    "`docs/findings/street_band_type/`. A dealt business shows its Pixelcoat pack twice: on the "
    "band Lot hangs across its frontage, and on Zoo's door box, which wears the pack instead of "
    "painting a name (Level Factory 0.148.0, Zoo 1.79.0). Measured, nothing changed:\n"
    "- **The pack is a 4:1 cabinet, sampled nearest:** `theme-signs` renders `(size // 4, size)`; "
    "cold run 9217's `sign_flappahs` is 512 x 128 with `interpolation: nearest`.\n"
    "- **Lot hangs it on a 6:1 band:** `SIGN_ASPECT = 6.0  # width : height, matching the pack`. "
    "The comment is false, and every band's letters are 1.5x too wide.\n"
    "- **Zoo's door box samples every pack `Closest`:** "
    "`materials.make_emissive_textured_material`. `skins.load_pack` drops the hint. Lot honours "
    "it.\n"
    "- **Pixelcoat thresholds Pixel Operator to ink or none,** which is what keeps a pack "
    "byte-deterministic.\n"
    "\n"
    "A smooth face stretched 1.5x reads worse than a pixel one, so the font alone is not the "
    "change. Proposed:\n"
    "1. Pixelcoat renders the business signs smooth, from its own minted table, at the band's "
    "6:1 and about 240 px a metre, and marks the packs `linear`.\n"
    "2. Zoo's door box fits a pack's art without stretching it, and samples it as the pack asks.\n"
    "3. Proven on a level with dealt businesses: club_block_014 has none.\n"
    "\n"
    "Found alongside: Pixelcoat's `test_the_kinds_zoo_knows_are_the_kinds_zoo_knows` fails today. "
    "`paint_matte` (Zoo 1.82.0) is missing from `cli._ZOO_KINDS`. It is a one-word fix with the "
    "next Pixelcoat release.\n"
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    text = data.decode("utf-8")
    assert "**223." not in text, "item 223 exists"
    assert text.endswith(LAST) and text.count(LAST) == 1, "222 does not end the file"
    ROADMAP.write_bytes((text + ITEM_223).encode("utf-8"))
    print("roadmap 223 filed")


if __name__ == "__main__":
    main()
