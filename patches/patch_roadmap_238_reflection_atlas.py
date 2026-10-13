"""Roadmap 238, 2026-10-13: the texture memory re-measured by part, and the attribution retracted -- the sky is
not resident, the reflection atlas is 82 % (`docs/findings/texture_memory/`, `texture_split_probe.gd`,
`texture_resident_probe.gd`). Replaces 238's status (asserted once and still directly above its heading) and
appends one paragraph to its body, before 239's status. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_238_reflection_atlas.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S238_OLD = ("*STATUS: OPEN 2026-10-11 -- MEASURED, NOT STARTED. Cold run 9245's package holds 515.6 MiB of texture "
            "memory at scene load on GL Compatibility (the engine's own monitor, a pristine imported copy and the "
            "walk copy alike; `docs/findings/texture_memory/`): 579 images, 108.6 Mpx, 546 of 578 sidecars asking "
            "lossless import, which is uncompressed in VRAM, and the sky system's 140 images two-thirds of the "
            "pixels, all resident. Block-compressed the same set is 69.8 MiB. Two levers to price: VRAM "
            "compression in the sidecars the export writes (the cost is block artefacts on pixel-art packs, "
            "judged on frames first), and one sky resident at a time.*")
S238_NEW = ("*STATUS: OPEN 2026-10-13 -- RE-MEASURED BY PART, the first attribution RETRACTED and kept below. Cold "
            "run 9273's package holds 314.6 MiB of texture memory once its warm-up has run "
            "(`docs/findings/texture_memory/`, `texture_split_probe.gd`, one process an arm, the package's own "
            "mission and its rebuild reading the same): 257 MiB of it -- 82 % -- is the REFLECTION ATLAS, Godot's "
            "default 64 probes of 256 x 256 x 6 half-float with mips, allocated for the level's 23 Lux room "
            "probes; the lightmap 21.3 MiB; the level's own textures about 30. The sky is not resident: none of "
            "its 140 images in the resource cache at load. Levers: the atlas sized to the level -- its count from "
            "the package's probe count, as `max_renderable_lights` is from its lights (fewer slots than probes "
            "floods the log and stalls the run), its size a look priced at interior stations (32 slots of 128 "
            "are 32 MiB); compression of the level's ~30 MiB; the sky lever withdrawn.*")

BODY_238 = """

**THE MEMORY BY PART, 2026-10-13** (`docs/findings/texture_memory/`; `split_9273.txt`, `resident_9273.txt`). **RETRACTED, KEPT ABOVE:** "the sky system ships 140 images ... resident though one slot's sky is shown" and the 515.6 MiB's attribution with it. The census counted every image as resident and the lightmap as nothing -- Pillow cannot open `bake.exr`, a row of 0 x 0 -- and its total landing beside the engine's was a coincidence. SkyMint loads two skyboxes and builds each from its faces' images (`skymint.gd`); at load the resource cache holds 457 of the package's 602 image files and none of the sky's. **The method:** freeing parts of a loaded level and reading the monitor fails here -- with the whole scene freed and no image file cached, 266.9 of its 314.7 MiB stayed -- so each arm is a fresh process, the mission rebuilt as its entry script builds it with one part left out before it enters the tree, read after the Warmup's sweep. THE CONTROL: the package's own `mission.tscn` and the rebuild read 314.6 MiB, the mission twice. **The arms:** the window alone 5.7 MiB; without the lit site (`bake.tscn`) 7.8; without the dressing 313.3, the backdrop 313.9; without the LightmapGI 293.3; without the Warmup -- nothing renders, no probe updates -- 57.3; with no positional or a 256 directional shadow atlas, 314.6 each; with `reflection_size` 64 in an `override.cfg`, 73.5. **So:** the reflection atlas is 257 MiB, allocated the first time a probe renders (the warm-up's sweep, or a player's camera) and belonging to the window, which is why it outlived the freed scene; at 64 x 64 it is 16. The level has 23 probes, all Lux's interior `room_ambient`, all updating once, in 64 slots. **What does not work:** fewer slots than probes -- at 4, the engine raised `rpi->atlas_index < 0` 113,494 times and the run never finished its warm-up in 600 s. **The levers, revised:** (1) the atlas sized to the level, written by the export beside `max_renderable_lights` -- its count the package's probe count, rounded up; its face size a look, the sharpness of a room's ambient and reflections, to be priced at interior stations against today's 256 (32 slots: 128 MiB at 256, 32 at 128, 8 at 64); (2) VRAM compression of the level's own textures, now a lever on about 30 MiB; (3) the sky lever withdrawn. **Also measured:** without its lightmap the warm-up takes 36.5 s against about 6, its lights live."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "THE MEMORY BY PART, 2026-10-13" not in text, "already applied"
    assert text.count(S238_OLD) == 1, "238's status not found once"
    text = text.replace(S238_OLD, S238_NEW)
    h = text.find("\n\n**238. ")
    s = text.rfind("\n\n*STATUS:", 0, h)
    assert h > 0 and text[s + 2:h] == S238_NEW, "238's status does not sit directly above its heading"
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h and text.find("\n\n**239. ", nxt) > nxt \
        and not re.search(r"\n\n\*\*\d+\. ", text[h + 10:nxt]), "239 does not follow 238"
    text = text[:nxt] + BODY_238 + text[nxt:]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 238: status and a paragraph; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
