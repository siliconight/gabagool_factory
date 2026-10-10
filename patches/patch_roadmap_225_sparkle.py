"""Roadmap 225, new: the walk's jitter gate reads texture sparkle as z-fighting.

Appends item 225 after item 224's last line. The anchor must match exactly once; nothing is written
on a miss. The generated index is regenerated afterwards by `tools/roadmap_status.py --write`,
never by this script.

    python patches/patch_roadmap_225_sparkle.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

END_OF_224 = (
    "So 2 is next: the truck's texel density (`lightmap_size_hint`, or `LightmapGI.texel_scale`). "
    "Large texels, interpolated and denoised, draw exactly this kind of blob, and it is priced "
    "in lightmap memory rather than in draw calls. After it, the denoiser off.\n"
)
ITEM = (
    "\n*STATUS: OPEN 2026-10-10 -- found the moment the walk's shot bot could see again (Level "
    "Factory 0.171.0): it FAILS two of cold run 9222's ladder stations on jitter, 3.60% and "
    "2.33% over a 2.0% gate, and says coplanar surfaces are fighting. Mapped pixel by pixel, "
    "every change is scattered speckle over the drop ceiling's acoustic tiles, a wall and the "
    "floor, and no surface flips as a block: texture sparkle, which the gate's one number cannot "
    "tell from z-fighting. Not known: whether the sparkle shows in play.*\n"
    "\n"
    "**225. The walk's jitter gate reads texture sparkle as z-fighting.** "
    "`docs/findings/shotbot_sparkle/`. The shot bot renders each station twice, 1 mm apart, and "
    "fails a station when more than 2.0% of sampled pixels change by more than 12 of 255. It was "
    "calibrated in August on a package whose worst honest station was 0.68% (\"edge aliasing "
    "along a ladder's rungs\") and whose real double-wall z-fight was 30.67%. It was then blind "
    "from Level Factory 0.100.0 to 0.170.0, photographing under the shader warm-up's black cover "
    "(roadmap 202's install test; 0.171.0 holds the warm-up).\n"
    "- **What it now fails:** Ladder_ladder_0_base 3.60% and Ladder_ladder_1_top 2.33% on 9222's "
    "preview, both interiors under a drop ceiling.\n"
    "- **What the changed pixels are:** `jitter_map.py` over both frames of each station puts "
    "49% and 51% of them in the frame's top fifth, the ceiling, as fine speckle and short "
    "streaks, with the rest on a wall, the floor and rung edges. No region is solid.\n"
    "- **Why, read rather than measured:** 1 mm at 1.5 to 3 m moves the image by a fraction of a "
    "pixel, and under bilinear filtering a fine high-contrast texture at a grazing angle changes "
    "by more than 12 of 255 across that fraction.\n"
    "\n"
    "Not yet looked at, in this order:\n"
    "1. **Separate the two in the gate:** judge connected regions of changed pixels (a z-fight "
    "is a block; sparkle is single pixels), fail on regions, and report the scattered "
    "remainder as sparkle.\n"
    "2. **Whether the ceiling shimmers in play:** its texture's mips and the renderer's "
    "anisotropic filtering, seen moving at full resolution.\n"
    "\n"
    "Owner: Level Factory for the gate; whoever owns the ceiling's texture for the second.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(END_OF_224) == 1, ("anchor", text.count(END_OF_224))
    assert "**225. " not in text, "item 225 already exists"
    text = text.replace(END_OF_224, END_OF_224 + ITEM)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 225: filed, OPEN")


if __name__ == "__main__":
    main()
