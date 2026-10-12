"""Roadmap 239: Zoo 1.103.0 and cold runs 9260 and 9261 -- two cold runs of one set bake one
lightmap. Two anchors, each asserted once, nothing written on a miss. Run
`python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_one_lightmap.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "cold run 9259: the export 175 -> 167 s, the drive 6.9 minutes. Open: the opened scene's first "
     "frame (about 10 s, and not the viewport's drawing) and the bake (31.5 s), the level a failing "
     "lens bakes at (the walker's), the Lux job's staging and the work done for a cache hit before "
     "the cache is asked, the Blender builds' reproducibility, and the grader's step (4x against the "
     "game's 1/60 s), the walker's call.*",
     "cold run 9259: the export 175 -> 167 s, the drive 6.9 minutes. Then two cold runs of one set: "
     "Zoo 1.103.0 makes every Zoo job of a cold run build the same bytes twice (7 of 38 had not), "
     "and cold runs 9260 and 9261 baked one lightmap -- every user placed the same, all but 15 of "
     "16.8 million texels bit for bit the same. Open: the opened scene's first frame (about 10 s, "
     "and not the viewport's drawing) and the bake (about 30 s), the level a failing lens bakes at "
     "(the walker's), the Lux job's staging and the work done for a cache hit before the cache is "
     "asked, the last of the Blender builds' reproducibility (one rowhome's merged covers), and the "
     "grader's step (4x against the game's 1/60 s), the walker's call.*"),
    ("item 1's Zoo 1.103.0",
     "so the fixtures' Blender build names its domes in an order a run draws, not one of two.",
     "so the fixtures' Blender build names its domes in an order a run draws, not one of two. "
     "**TWO COLD RUNS, ONE LIGHTMAP: Zoo 1.103.0.** The deli fixtures job had the same inputs in "
     "9258 and 9259 and wrote two GLBs; `docs/findings/grader_speed/zoo_repro_probe.py` replays Zoo "
     "builds and compares them array by array: the domes' and bulbs' triangles in another order, "
     "nothing else. Not Python's hash seeds and not Blender's threads: Blender's own "
     "`create_uvsphere` and `bisect_plane` lay faces in a process's order (`uvsphere_order_probe.py`, "
     "no Zoo code), `holes_fill` and the bisect start a face at a corner of their own choosing, and "
     "`add_hemisphere` handed its bisect a set. Zoo 1.103.0 sorts every mesh's faces before writing "
     "it, gives those operators their input in one order and starts the faces they make at their "
     "lowest vertex. Replayed twice each, cold run 9259's 38 Zoo jobs: on 1.102.0 seven built "
     "different bytes, on 1.103.0 none. Cold runs 9260 and 9261 placed every lightmap user the same "
     "and baked all but 15 of 16,777,216 texels bit for bit the same "
     "(`docs/cold_runs/cold_9261/NOTES.md`). Left: one rowhome's merged covers still came out in "
     "another triangle order from the same plan. The atlas is 16 slices where it was 15 (about a "
     "megabyte); Zoo's build time unchanged within the noise of its kit builds alternated. Both runs "
     "were slower than 9259 in every leg, Pixelcoat and the export included -- the machine, and "
     "nothing measured says why."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "TWO COLD RUNS, ONE LIGHTMAP" not in text, "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's Zoo 1.103.0 and cold runs 9260/9261 recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
