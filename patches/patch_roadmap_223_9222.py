"""Roadmap 223 CLOSED by cold run 9222: the deli's band and door box in Blue Highway, smooth, at 6:1.

Replaces 223's status block and adds the proof to its body. Each anchor must match exactly once;
nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`, never by this script.

    python patches/patch_roadmap_223_9222.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- fixed in four repos, not yet run cold. Pixelcoat 0.62.0 "
    "letters a business's sign in Blue Highway Condensed, smooth, at the band's 6:1 (1536 x 256), "
    "and asks for `linear` and mips; every one of the delco profile's 47 names sets, caps 112 to "
    "137 px. Zoo 1.94.0's door box samples as the pack asks and keeps the art's shape. Lot 0.105.0 "
    "carries the pack's manifest beside its maps, and Level Factory 0.166.0 pins the sign maps' "
    "import from it (compressed, mipped). Next: a cold run of restaurant_row_001, which deals its "
    "businesses packs.*\n"
)
NEW_STATUS = (
    "*STATUS: CLOSED 2026-10-10 -- proven in cold run 9222 (restaurant_row_001, 0 interventions, "
    "0 retries): deli_a01's band and its door box read SCRAPPLE & SONS DELI in Blue Highway "
    "Condensed, smooth. Read off the walk copy: the pack is 1536 x 256 asking `linear` and mips; "
    "its manifest is in `signs/`; the band samples filtered, where 9185's was nearest; both maps "
    "import at `compress/mode=2` with mips; the door box samples LINEAR with mips and shows the "
    "art at 6.0:1 on its 2.05 x 0.6 m face. Frames: `docs/cold_runs/cold_9222/`.*\n"
)

BODY_ANCHOR = (
    "**The price, by arithmetic:** a sign's three maps were 0.20 MB compressed at 512 x 128; they "
    "are 1.6 MB compressed with mips at 1536 x 256, and a level carries a few.\n"
)
PROOF = (
    "\n**PROVEN, cold run 9222** (`docs/cold_runs/cold_9222/NOTES.md`). restaurant_row_001, "
    "seed_9104, evening; the deal is `b0=scrapple_sons_deli`, as in 9185. What each release "
    "asked for is in the walk copy:\n"
    "- **Pixelcoat 0.62.0:** albedo and emissive 1,536 x 256; `import_hints` asks "
    "`interpolation: linear` and `generate_mipmaps: true`.\n"
    "- **Lot 0.105.0:** `signs/sign_scrapple_sons_deli.pack.json` beside its maps. The band's "
    "material carries no `texture_filter`, so it samples filtered; 9185's carried "
    "`texture_filter = 2`.\n"
    "- **Level Factory 0.166.0:** both maps' `.import` read `compress/mode=2` and "
    "`mipmaps/generate=true`.\n"
    "- **Zoo 1.94.0:** `M_SignBox_sign_scrapple_sons_deli_Face` samples magFilter 9729 and "
    "minFilter 9987, clamped. Its face is 2.05 x 0.60 m with UV v from -0.378 to 1.378, so the "
    "art lies on it at 6.0:1, its own shape.\n"
    "\n"
    "Observed in the frames, and left for the walker: a lamp pole stands in front of the band "
    "and hides the E of SCRAPPLE (no rule in Lot keeps a pole out of a band's sightline from "
    "the street), and the door box reads brighter than the band (its face emits at Zoo's "
    "strength; the band's multiplier is 0.65).\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    for name, anchor in (("status", OLD_STATUS), ("body", BODY_ANCHOR)):
        n = text.count(anchor)
        assert n == 1, (name, "anchor matches", n, "times")
    text = text.replace(OLD_STATUS, NEW_STATUS).replace(BODY_ANCHOR, BODY_ANCHOR + PROOF)
    # the status block must still sit directly above 223's heading
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**223. "), "223's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 223: CLOSED by cold run 9222")


if __name__ == "__main__":
    main()
