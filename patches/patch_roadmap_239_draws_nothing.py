"""Roadmap 239: Level Factory 0.193.0 -- the bake's editor stops drawing for the bake, the work copy
copied in parallel and removed in the background. Two anchors, each asserted once, nothing written
on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_draws_nothing.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "baked the run's lightmap byte for byte. Open: the scene's first frame and the bake (about 46 s "
     "of the editor's 64),",
     "baked the run's lightmap byte for byte. Then the bake's editor stops drawing while it bakes and "
     "the work copy is copied on eight threads and removed behind (Level Factory 0.193.0): "
     "re-exported, the export 173 -> 164 s with the same bytes. Open: the opened scene's first frame "
     "(about 10 s, and not the viewport's drawing) and the bake (31.5 s),"),
    ("item 1's 0.193.0",
     "the reproducibility item below has a name.",
     "the reproducibility item below has a name. **THE BAKE DRAWS NOTHING WHILE IT BAKES: Level "
     "Factory 0.193.0.** The bake's progress bar pumps the editor's main loop, and every pump drew "
     "the whole level again: with the four 3D viewports' render targets stopped as Bake is pressed, "
     "9258's level baked in 31.4 and 31.5 s against 35.7, byte for byte the same files. "
     "**REFUTED, KEPT:** stopped from the start instead, the bakes came out 17.5 % darker on average, "
     "the outdoor ground most -- the bake reads something only a drawn frame makes, the sky's light "
     "the likely one -- and the opened scene's first frame still took about 10 s, so that frame is "
     "not the viewport's; the probe's first try at it set a property a SubViewport does not have and "
     "stopped nothing, found by a missing log line. The work copy, 6,058 files and 252 MB, is copied "
     "on eight threads (4.7-5.3 -> 2.0-2.1 s) and removed on a thread while the export goes on "
     "(2.1-2.8 s off its path). As shipped: exports of 162.4, 164.3 and 163.8 s against 171.4 to "
     "173.2, the editor about 60 s, the export's own Python 17.2 s against 22.3, the bake's bytes "
     "the run's own (`docs/findings/grader_speed/README.md`)."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "Level Factory 0.193.0.**" not in text, "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's Level Factory 0.193.0 recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
