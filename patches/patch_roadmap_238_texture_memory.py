"""Roadmap 238: a package's textures ship uncompressed and all resident -- 516 MiB on GL
Compatibility, measured 2026-10-11 (`docs/findings/texture_memory/`). Appends the item after 237
(asserting the roadmap still ends with 237's comps paragraph); nothing written on a miss. Run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_238_texture_memory.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

TAIL_237 = ("**The first recipe:** one wall family -- a `brick_whitewash` pack, the plinth, the streak "
            "cover, the exposure value -- measured against the pack it replaces at the fixed stations, "
            "then the walker's eye.\n")

STATUS_238 = (
    "*STATUS: OPEN 2026-10-11 -- MEASURED, NOT STARTED. Cold run 9245's package holds 515.6 MiB of "
    "texture memory at scene load on GL Compatibility (the engine's own monitor, a pristine imported "
    "copy and the walk copy alike; `docs/findings/texture_memory/`): 579 images, 108.6 Mpx, 546 of "
    "578 sidecars asking lossless import, which is uncompressed in VRAM, and the sky system's 140 "
    "images two-thirds of the pixels, all resident. Block-compressed the same set is 69.8 MiB. Two "
    "levers to price: VRAM compression in the sidecars the export writes (the cost is block artefacts "
    "on pixel-art packs, judged on frames first), and one sky resident at a time.*")

ITEM_238 = """

**238. A package's textures ship uncompressed and all resident: 516 MiB.** The walker, 2026-10-11, after an explainer that had one thing in it: "texture memory and compression, worth measuring on a package". Measured the same day on cold run 9245's package (`docs/findings/texture_memory/`, `texture_census.py` and `texture_mem_probe.gd`): the engine reports 515.6 MiB of texture memory and 550.8 MiB of video memory at scene load, on the package as shipped. The census explains it twice over. The export writes `.import` sidecars with `compress/mode=0` for 546 of 578 images -- lossless, which compresses the file and not the texture -- with `detect_3d/compress_to=1` that only an editor's 3D detection would act on, and the `--import` passes the walk and the price harness run never trip it: the import cache carries the compressed `s3tc` form for the 33 that ask for it and for nothing else. And the sky system ships 140 images for every time of day and variant, 73.4 of the package's 108.6 megapixels, resident though one slot's sky is shown. The three enterable buildings' kits are 28.5, 24.9 and 17.2 MiB raw; an Empty 4.8; the covers 25.2.

**WHY IT MATTERS HERE.** Every frame is spent on somebody else's machine, and texture memory is the one cost this repo had never put a number on: the draw-call rule, the light cap and the bake all price submissions and shading, and a package that holds half a gigabyte of textures on a card with two, beside the game's own assets, is a different kind of fall-over than a slow frame. Nothing in the perf report sees it (`rows` carry draws and p95), which is why it went unmeasured.

**THE LEVERS, each to be priced before it ships.** (1) `compress/mode=2` (VRAM Compressed) in the sidecars the export writes for the textures 3D materials read: the estimate is 69.8 MiB, a 7.9x cut, at the cost of block compression over Pixelcoat's pixel-art packs -- 4 x 4 blocks across Closest-sampled texels -- which may read as smear on exactly the look the walker chose; frames at the fixed stations, compressed beside lossless, decide it, and the posters and signs may keep lossless where the text must stay crisp. (2) One sky resident at a time: the cycle loads the slot's panorama and its neighbour, not all 140. (3) Nothing for the kits until (1) is judged: a building's textures are 17 to 29 MiB raw and a tenth of that compressed.

**WHAT WOULD CLOSE IT.** The engine's monitor read under 100 MiB on a package at the fixed stations with the walker's eye on the frames, the probe run in every cold run's record beside the price so the number cannot drift back unseen."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "\n**238. " not in text and "MEASURED, NOT STARTED. Cold run 9245's package holds" not in text, "already applied"
    assert text.endswith(TAIL_237), ("the roadmap does not end with 237's comps paragraph", text[-200:])
    text = text.rstrip("\n") + "\n\n" + STATUS_238 + ITEM_238 + "\n"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 238 appended after 237; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
