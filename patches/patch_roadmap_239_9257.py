"""Roadmap 239: cold run 9257, Level Factory 0.191.0 in a drive, and what its lightmap showed. Two
anchors, each asserted once, nothing written on a miss. Run `python tools/roadmap_status.py --write`
then `--check`.

    python patches/patch_roadmap_239_9257.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "67.5 s against 87.6 and 92.6, the lightmap within what two exports differ by. Open:",
     "67.5 s against 87.6 and 92.6, the lightmap within what two exports differ by; cold run "
     "9257: the export 204 -> 187 s, the drive 7.2 minutes. Open:"),
    ("item 1's drive",
     "compiled into an empty shader cache) and the bake (35 s).",
     "compiled into an empty shader cache) and the bake (35 s). **Cold run 9257** measured it in a "
     "drive (`docs/cold_runs/cold_9257/NOTES.md`): 0 interventions, findings 122 -> 122, the "
     "bake's editor 88.1 -> 69.9 s, the export 204 -> 187 s, the drive 7.2 minutes, the walk copy "
     "carrying the cache and loading the same level. Its lightmap read texel by texel looked far "
     "from 9256's (a mean difference of 0.0246 against a mean of 0.031) and was packed "
     "differently: the deli's fixtures came out of Blender different, three dome glasses' charts "
     "changed size and 2,858 of 3,320 users moved. Read user by user "
     "(`docs/findings/grader_speed/lightmap_compare.py --layout`), the light is the same: where a "
     "user stayed, 0.000224 apart on average, as 9255 and 9254 are; where it moved, 0.0032 apart "
     "and falling either way (signed, 0.16 % of the mean). Seven models differed from 9256's in "
     "all, each with its own lightmap unwrap -- the Blender builds' reproducibility, still open, "
     "now with a consequence a texel-by-texel reading mistakes for a change of light."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**Cold run 9257**" not in text, "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's cold run 9257 recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
