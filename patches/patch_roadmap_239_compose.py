"""Roadmap 239: the compose job's buildings side by side (Level Factory 0.186.0), measured by a
replay of cold run 9251's own commands and in cold run 9252, and the walk copy's import, which
9252's step stamps showed at 15 % of the drive. Three anchors, each asserted once, nothing
written on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_compose.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "Open: the compose job's sixteen commands in turn, the work done for a cache hit before the "
     "cache is asked, the light bake's and the sidecar step's imports, the walk copy's, the Blender "
     "builds' reproducibility, and the grader's step (4x against the game's 1/60 s, the walker's "
     "call).*",
     "Then the compose: Level Factory 0.186.0 runs the buildings' composes side by side, and cold "
     "run 9252 measured it in a drive: the compose job 64.1 -> 31.0 s, the drive 10.3 minutes, the "
     "export now 46 % of it. Open: the light bake's and the sidecar step's imports, the walk copy's "
     "(91 s in 9252), the Lux job's staging and the work done for a cache hit before the cache is "
     "asked, the Blender builds' reproducibility, and the grader's step (4x against the game's "
     "1/60 s, the walker's call).*"),
    ("item 1's walk copy",
     "and the walk copy imports the package from scratch again.",
     "and the walk copy imports the package from scratch again -- 91 s, 15 % of cold run 9252's "
     "drive, by the step stamps `tools/cold_drive/cold_drive.sh` writes since that run, where the "
     "export has just imported the same files and dropped its cache."),
    ("item 2's left",
     "Left: the compose commands side by side, the probe and the staging after the cache is asked.",
     "**The compose commands side by side: Level Factory 0.186.0.** A replay of 9251's own sixteen "
     "commands (`docs/findings/grader_speed/compose_replay_ab.py`) read 58.3 s in turn and 25.4 s "
     "with the buildings four at a time, the same 928 files, 928 of 928 identical to the run's "
     "own; cold run 9252, the compose job 64.1 -> 31.0 s and the drive 10.8 -> 10.3 minutes, "
     "0 interventions, findings unchanged. `job.log` now keeps every command of a job (it held only "
     "the last: the source of 9249's refuted note). Left: the Lux job's staging -- 26.9 s before "
     "its command in 9252 with nothing else running, a project of the whole themed site copied and "
     "imported (`leg_spans.py`) -- and the probe and the staging after the cache is asked."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "**The compose commands side by side: Level Factory 0.186.0.**" not in text, "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's compose and walk copy recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
