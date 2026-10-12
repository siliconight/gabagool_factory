"""Roadmap 239: Level Factory 0.192.0 -- the export timed process by process, the bake's clock
stopped, the open's floor and the localizer's scan. Two anchors, each asserted once, nothing written
on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_239_bake_clock.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

EDITS = [
    ("the status",
     "the drive 7.2 minutes. Open: the editor's scene opening and bake (about 56 s of its 68),",
     "the drive 7.2 minutes. Then the export process by process: Level Factory 0.192.0 stops the "
     "bake editor's clock, looks for the scene from frame 1 and skips class names a script lacks -- "
     "re-exported, the export 183 -> 172 s, and two exports bake the same bytes, where Lux's failing "
     "lenses had made every bake different. Open: the scene's first frame and the bake (about 46 s "
     "of the editor's 64), the level a failing lens bakes at (the walker's),"),
    ("item 1's export",
     "now with a consequence a texel-by-texel reading mistakes for a change of light.",
     "now with a consequence a texel-by-texel reading mistakes for a change of light. **THE EXPORT, "
     "PROCESS BY PROCESS: Level Factory 0.192.0.** `docs/findings/grader_speed/export_timeline_probe.py` "
     "times every process an export starts and stamps its lines: on 9257's workspace, 182.8 s -- the "
     "sidecar step's three imports 56.9 s, the bake's editor 68.0, the other imports 16, the scripts "
     "12.6, the export's own Python 29.3. Three cuts, each measured on its own: the bake's plugin "
     "looked for the opened scene 240 frames after asking, and it was open at that first look in "
     "every run (one frame now, about 4 s); the localizer searched every script for each of the "
     "tools' 68 class names (1.67 of a pass's 1.69 s; a substring test first, the pass 0.079 s); and, "
     "found while pricing the first, **the lightmap depended on when Bake was pressed** -- Lux's "
     "failing fixtures keep their clocks in the bake's editor and dim their lenses with their lamps, "
     "and a lens's emission is baked, so each bake caught every failing lens at a different level. "
     "With `Engine.time_scale` 0 from the plugin's start, two bakes pressed 4.4 s apart came out byte "
     "for byte the same. As shipped: exports of 172.5, 172.0 and 171.4 s against 182.9 and 184.7, "
     "and two exports of one level now differ in 18 files where they differed in 21. **The walker's "
     "call, queued:** which level a failing lens should bake at -- dark like its lamp, full, or its "
     "cycle's mean; at 0 a cycling streetlight (every third one) bakes wherever its seed puts it in "
     "its cycle, fixed for a level now where it was drawn anew every bake."),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "Level Factory 0.192.0.**" not in text, "already applied"
    for name, old, new in EDITS:
        assert text.count(old) == 1, (name, text.count(old))
        text = text.replace(old, new)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 239's Level Factory 0.192.0 recorded; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
