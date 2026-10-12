"""Roadmap 239: the export's imports profiled -- Level Factory 0.181.0 (the census reads the bake's
cache) and 0.182.0 (the shared textures' pins read back off what ships, a defect the control
found). Rewrites 239's first open item and the status's open clause; each anchor asserted once,
nothing written on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_export.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S_OLD = ("Open: one import of a package instead of several (the export is now half the drive), and the "
         "grader's step (4x against the game's 1/60 s, the walker's call).*\n")
S_NEW = ("The export, then half the drive, profiled: importing was 65 % of it, the same files five times; "
         "Level Factory 0.181.0 removed the census's import (430.7 -> 340.1 s), and its control found the "
         "shared textures' import pins lost in a random sixth of every export, read back off what ships "
         "since 0.182.0. Open: the light bake's and the sidecar step's imports, the walk copy's, and the "
         "grader's step (4x against the game's 1/60 s, the walker's call).*\n")
O_OLD = ("1. **One import of a package, not several.** The export imports its package to bake it, the walk "
         "copy imports it again from scratch, and each walk test imports its staged project first; Godot "
         "re-verifies a reused import cache against each source's hash, so reuse is safe by construction "
         "where the sources are the same files. Worth about 1.5 to 3 minutes a run; to be measured before "
         "built.\n")
O_NEW = ("1. **One import of a package, not several -- MEASURED, PARTLY DONE.** Profiled on cold run 9248's "
         "export (430.7 s, `docs/findings/grader_speed/README.md`): the sidecar step's two passes 78 s, the "
         "light bake's two imports 112 s (the first re-imports every model for its lightmap UVs), the "
         "greybox census's one 100 s, the editor's bake 88 s. Level Factory 0.181.0 drops the cache after "
         "the census instead of before it: 340.1 s, the census 4.2 s, its report identical. Left: the "
         "lightmap UVs could be asked for in the sidecar step's second pass (the bake's first import "
         "gone, and with it the race below), the bake's second import is worth reading, and the walk copy "
         "imports the package from scratch again. **Found on the way** (`docs/findings/texture_pins/`): "
         "the bake's first import re-imports the shared textures 1,843 times for 476 models, several at "
         "once, and 62 to 86 of 415 sidecars lose their import pins to Godot's defaults, which ones "
         "varying; Level Factory 0.182.0 applies them again after the last import and refuses a package "
         "that still lacks one.\n")


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "MEASURED, PARTLY DONE.** Profiled on cold run 9248's" not in text, "already applied"
    for old, what in ((S_OLD, "239's status tail"), (O_OLD, "239's open item 1")):
        assert text.count(old) == 1, (what, text.count(old))
    text = text.replace(S_OLD, S_NEW).replace(O_OLD, O_NEW)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's export work recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
