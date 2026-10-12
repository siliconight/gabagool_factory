"""Roadmap 239: the walk copy starts from the export's own import (Level Factory 0.188.0 and the
factory's tools/walk_export.py), measured by re-exporting cold run 9253 and in cold run 9254. Two
anchors, each asserted once, nothing written on a miss. Run `python tools/roadmap_status.py
--write` then `--check`.

    python patches/patch_roadmap_239_walk_cache.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "Open: the walk copy's import (88 s in 9253), the sidecar step's two passes, the Lux job's "
     "staging and the work done for a cache hit before the cache is asked, the Blender builds' "
     "reproducibility, and the grader's step (4x against the game's 1/60 s, the walker's call).*",
     "Then the walk copy: Level Factory 0.188.0 keeps the export's import cache beside the package "
     "and the walk copy moves it in; cold run 9254: the walk step 88 -> 11 s, the drive 8.4 "
     "minutes. Open: the sidecar step's two passes, the Lux job's staging and the work done for a "
     "cache hit before the cache is asked, the Blender builds' reproducibility, and the grader's "
     "step (4x against the game's 1/60 s, the walker's call).*"),
    ("item 1's walk copy",
     "Left: the walk copy imports the package from scratch again -- 91 s, 15 % of cold run 9252's "
     "drive, by the step stamps `tools/cold_drive/cold_drive.sh` writes since that run, where the "
     "export has just imported the same files and dropped its cache.",
     "**The walk copy from the export's own import: Level Factory 0.188.0** and the factory's "
     "`tools/walk_export.py`. The walk copy imported the package from scratch -- 91 s, 15 % of cold "
     "run 9252's drive, by the step stamps `tools/cold_drive/cold_drive.sh` writes since that run -- "
     "where the export had just imported the same files and dropped its cache. Kept beside the "
     "package and moved into the copy (`docs/findings/grader_speed/walk_cache_probe.py`): 86.4 and "
     "88.2 s from scratch, 11.5 s from the cache, every model loading the same (501 of 501 by "
     "`import_digest.gd`, whose digest a one-sidecar positive control moves) and the level the same; "
     "cold run 9254, the walk step 88 -> 11 s, the drive 9.7 -> 8.4 minutes, 0 interventions. Left: "
     "the sidecar step's two passes."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**The walk copy from the export's own import: Level Factory 0.188.0**" not in text, \
        "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's walk copy recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
