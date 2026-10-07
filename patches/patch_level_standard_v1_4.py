"""The level standard v1.4: the walker's calls of 2026-10-07 -- the extraction is
the getaway vehicle, and `target_minutes` is not a hard rule.

    python patch_level_standard_v1_4.py

The walker, 2026-10-07: "On extraction, I would think the default is they have
to leave the building and return to the 'getaway' car or vehicle to leave the
scene", and "target minutes ... should account for fighting, the 'drilling' or
acquiring of the score time, and other. So not a hard rule now." Roadmap 206
and 200.

Anchored on docs/LEVEL_STANDARD.md as patch_level_standard_v1_3.py left it
(67,090 bytes, LF; commit d070546). Every anchor must match once; nothing is
written on a miss.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "LEVEL_STANDARD.md"

EDITS = [
    ("**This is v1.3** (2026-10-07). v1.3 adds what the package says about the\n",
     "**This is v1.4** (2026-10-07). v1.4 records two of the walker's calls: the\n"
     "extraction is the getaway vehicle (§11, roadmap 206), and `target_minutes`\n"
     "is not a hard rule (Appendix A, roadmap 200;\n"
     "`patches/patch_level_standard_v1_4.py`). v1.3 added what the package says about the\n"),
    ("| 2-3 extraction possibilities | extraction anchors (3 on 9193) | BUILT as points; GAP for a choice. The brief's "
     "`extraction_relationship` is read by nothing, and nothing varies between runs |\n",
     "| 2-3 extraction possibilities | extraction anchors (3 on 9193) | BUILT as points; GAP for a choice. The brief's "
     "`extraction_relationship` is read by nothing, and nothing varies between runs. **The default is the getaway "
     "vehicle** (the walker, 2026-10-07): the crew leaves the score building and returns to the car to leave the "
     "scene. GAP: the extraction is still a building drawn by seed, and it is the score building itself on 43 of 136 "
     "multi-building candidate specs on disk (roadmap 206) |\n"),
    ("about 3 min -- is the walker's call. *v1.1 read",
     "about 3 min -- was the walker's call, and the walker made it on 2026-10-07: **not a hard rule** until the "
     "estimate counts fighting and acquiring the score (\"the drilling\"). *v1.1 read"),
]


def main():
    data = DOC.read_bytes()
    assert len(data) == 67090, "LEVEL_STANDARD.md is %d bytes, read at 67,090" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old, new in EDITS:
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:70])
    for old, new in EDITS:
        text = text.replace(old, new)
    DOC.write_bytes(text.encode("utf-8"))
    print("LEVEL_STANDARD.md: v1.4, %d edits, %d -> %d bytes" % (len(EDITS), len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
