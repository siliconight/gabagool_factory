"""Roadmap 239: cold run 9259, Level Factory 0.193.0 in a drive, and the domes a third way. Two
anchors, each asserted once, nothing written on a miss. Run `python tools/roadmap_status.py --write`
then `--check`.

    python patches/patch_roadmap_239_9259.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "re-exported, the export 173 -> 164 s with the same bytes. Open:",
     "re-exported, the export 173 -> 164 s with the same bytes; cold run 9259: the export 175 -> "
     "167 s, the drive 6.9 minutes. Open:"),
    ("item 1's 9259",
     "the bake's bytes the run's own (`docs/findings/grader_speed/README.md`).",
     "the bake's bytes the run's own (`docs/findings/grader_speed/README.md`). **Cold run 9259** "
     "measured it in a drive (`docs/cold_runs/cold_9259/NOTES.md`): 0 interventions, findings 122 -> "
     "122, the bake 35.7 -> 31.7 s, the editor 65.0 -> 61.5 s, the export 175 -> 167 s, the drive "
     "6.9 minutes, no work copy left. Its atlas was packed differently from 9258's by one deli dome "
     "this time (005 alone): four runs, three namings, so the fixtures' Blender build names its domes "
     "in an order a run draws, not one of two."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**Cold run 9259**" not in text, "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's cold run 9259 recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
