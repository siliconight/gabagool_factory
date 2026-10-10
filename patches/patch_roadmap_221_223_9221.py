"""Roadmap 221 and 223: cold run 9221 proves and prices Patina 0.30.0 (221 CLOSED); the street band
is fixed across four repos and not yet run cold (223 NARROWED).

Each status line is replaced whole from its unique opening, and 223's last line gets the fix
after it, each asserted to be exactly one. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

S221 = "*STATUS: NARROWED 2026-10-10 -- the cause verified and fixed in Patina 0.30.0, not yet run cold."
N221 = (
    "*STATUS: CLOSED 2026-10-10 -- proven in cold run 9221 (club_block_014, seed 9181; 0 "
    "interventions, 0 retries, findings 71 to 71), only Patina changed, to 0.30.0. On all three "
    "signed buildings every base course, conduit, gutter and downspout faces out on its own side "
    "and none stands in the wall; the club's base courses were 0 of 51 out and 28 inside on 9220. "
    "Each concrete side merge lies on its own face: the club's CoverN_concrete went from 1,760 "
    "north and 432 south vertices to 2,960 north. Priced against 9220 on both sides: 9.4 fewer "
    "draws a heading on about 1,150, and p95 inside the controls' 1.50 ms spread "
    "(`docs/cold_runs/cold_9221/`). Not claimed: the empty rowhomes' slot-derived painted metal, "
    "which nearest-edge still reads as mixed.*"
)
S223 = "*STATUS: OPEN 2026-10-10 -- note 10 generalised (item 219): a business Level Factory deals"
N223 = (
    "*STATUS: NARROWED 2026-10-10 -- fixed in four repos, not yet run cold. Pixelcoat 0.62.0 "
    "letters a business's sign in Blue Highway Condensed, smooth, at the band's 6:1 (1536 x 256), "
    "and asks for `linear` and mips; every one of the delco profile's 47 names sets, caps 112 to "
    "137 px. Zoo 1.94.0's door box samples as the pack asks and keeps the art's shape. Lot "
    "0.105.0 carries the pack's manifest beside its maps, and Level Factory 0.166.0 pins the sign "
    "maps' import from it (compressed, mipped). Next: a cold run of restaurant_row_001, which "
    "deals its businesses packs.*"
)
LAST_223 = ("Found alongside: Pixelcoat's `test_the_kinds_zoo_knows_are_the_kinds_zoo_knows` fails "
            "today. `paint_matte` (Zoo 1.")
ADD_223 = (
    "\n\n**Fixed, 2026-10-10, as proposed, in four releases:**\n"
    "1. **Pixelcoat 0.62.0.** `core/smooth_type.py` and a minted Blue Highway Condensed table, "
    "byte-identical to Zoo's (162,355 bytes): the band and the door are one face at one em. "
    "`theme-signs` draws a business at 1536 x 256, 6:1, set as large as it fits, and its pack "
    "asks for `linear` and `generate_mipmaps`; a price board keeps its pixel figures. "
    "`paint_matte` joins `_ZOO_KINDS`.\n"
    "2. **Zoo 1.94.0.** `load_pack` returns the pack's `interpolation` and `art_aspect`; the sign "
    "material samples `Linear` for a smooth pack; `fit_uv` shows the art at its own shape. "
    "Across the library's 95 door signs (0.6 m tall, 3.33 to 8.33:1, 4.67 at the median), a 6:1 "
    "band on the median door is 78% of its height, its edge EXTENDed above and below.\n"
    "3. **Lot 0.105.0** copies the pack's manifest beside its maps, and `SIGN_ASPECT`'s comment "
    "is true at last.\n"
    "4. **Level Factory 0.166.0** pins each sign map's import as its manifest asks: "
    "`compress/mode=2` for `linear`, `mipmaps/generate=true` for mips. A shipped package had left "
    "them at mode 0 with no mips.\n"
    "\n**The price, by arithmetic:** a sign's three maps were 0.20 MB compressed at 512 x 128; "
    "they are 1.6 MB compressed with mips at 1536 x 256, and a level carries a few."
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    lines = data.decode("utf-8").split("\n")
    for start, new in ((S221, N221), (S223, N223)):
        hits = [i for i, ln in enumerate(lines) if ln.startswith(start)]
        assert len(hits) == 1, (start[:50], len(hits))
        lines[hits[0]] = new
    hits = [i for i, ln in enumerate(lines) if ln.startswith(LAST_223)]
    assert len(hits) == 1, ("223's last line", len(hits))
    lines[hits[0]] = lines[hits[0]] + ADD_223
    ROADMAP.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 221 closed in 9221; 223 fixed, not yet run cold")


if __name__ == "__main__":
    main()
