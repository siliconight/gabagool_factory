"""Roadmap 239: cold run 9258, Level Factory 0.192.0 in a drive, its bake made again byte for byte,
and the deli's dome naming. Two anchors, each asserted once, nothing written on a miss. Run
`python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_9258.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "and two exports bake the same bytes, where Lux's failing lenses had made every bake different. "
     "Open:",
     "and two exports bake the same bytes, where Lux's failing lenses had made every bake different; "
     "cold run 9258: the export 187 -> 175 s, the drive 7.0 minutes, and a re-export of its workspace "
     "baked the run's lightmap byte for byte. Open:"),
    ("item 1's drive",
     "fixed for a level now where it was drawn anew every bake.",
     "fixed for a level now where it was drawn anew every bake. **Cold run 9258** measured it in a "
     "drive (`docs/cold_runs/cold_9258/NOTES.md`): 0 interventions, findings 122 -> 122, the bake's "
     "editor 69.9 -> 65.0 s, the export 187 -> 175 s, the drive 7.0 minutes; its workspace "
     "re-exported once baked `bake.exr`, `bake.lmbake` and `bake.exr.import` byte for byte the "
     "run's own. Against 9257 its atlas was packed differently again, by the same three deli dome "
     "glasses, and they swapped back: 001 and 005 are 14 x 6 texels in 9256 and 9258 and 14 x 10 in "
     "9257, 003 the other way -- the domes have two shapes, and which name each takes is a run's "
     "draw in the deli fixtures' Blender build. The light is the same user by user. That naming is "
     "the one thing now known to stop two cold runs baking the same lightmap; the reproducibility "
     "item below has a name."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**Cold run 9258**" not in text, "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's cold run 9258 recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
