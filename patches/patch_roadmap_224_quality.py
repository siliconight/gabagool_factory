"""Roadmap 224 NARROWED: the bake's quality is not the lever for the box truck's blotches.

Replaces 224's status block and adds the measurement to its body. Each anchor must match exactly
once; nothing is written on a miss. The generated index is regenerated afterwards by
`tools/roadmap_status.py --write`, never by this script.

    python patches/patch_roadmap_224_quality.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: OPEN 2026-10-10 -- found in cold run 9219: a large pale face lit only by the "
    "bake's bounce carries blotches. The box truck's side at midnight, in the moon's shadow, runs "
    "from luma 1 to 6 (p5 to p95 after an 8 px blur, median 2), and with the lightmap switched "
    "off it is black all over, so the blotches are the bake's. Not yet measured: the bake at a "
    "higher quality.*\n"
)
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- the bake's quality is not the lever. 9221's walk copy "
    "re-baked at Low, Medium and High (`docs/findings/bake_quality/`): the box's face reads p95 "
    "6, 5 and 5 of 255, and the brightened crops show the same blotches in the same places at "
    "all three, for +24% and +137% of the editor's bake time (94.1, 117.0, 222.7 s). Level "
    "Factory keeps Low. Next: the truck's lightmap texel density, then the denoiser off.*\n"
)

BODY_ANCHOR = (
    "Owner: Level Factory for the bake's settings and the import. Nothing changes until one of "
    "these has been measured.\n"
)
PROOF = (
    "\n**1. MEASURED 2026-10-10: the quality does not move them** "
    "(`docs/findings/bake_quality/`).\n"
    "- **The re-bakes:** cold run 9221's walk copy of the same level, re-baked through "
    "`tools/lux_rebake.py --bake-quality Q` (Level Factory's own `light_bake.bake()`, only "
    "`QUALITY` changed). Each report records the dial it set, and the editor's time rose with "
    "each step.\n"
    "- **The control:** quality 0, Level Factory's own, reproduces 9219's face, p5 1 and p95 6.\n"
    "- **The result:** Low, Medium and High read p95 6, 5 and 5, with p5 and p50 at 1 "
    "throughout. The editor's bake took 94.1, 117.0 and 222.7 s.\n"
    "- **The look:** `truck_side_by_quality.png` brightens the face 20 times. The same blobs "
    "stand in the same places at all three qualities, so they are not sampling noise that more "
    "rays would clear.\n"
    "\n"
    "So 2 is next: the truck's texel density (`lightmap_size_hint`, or `LightmapGI.texel_scale`). "
    "Large texels, interpolated and denoised, draw exactly this kind of blob, and it is priced "
    "in lightmap memory rather than in draw calls. After it, the denoiser off.\n"
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
    assert text[i + len(NEW_STATUS):].startswith("\n**224. "), "224's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 224: NARROWED, the quality is not the lever")


if __name__ == "__main__":
    main()
