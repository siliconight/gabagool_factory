"""The level standard v1.3: what the package says about the score (roadmap
204), and Level Factory 0.153.0's pacing seen in cold run 9195 (roadmap 200).

    python patch_level_standard_v1_3.py

Read on 2026-10-07:
  - cold run 9194's `gameplay_anchors.json`: 64 anchors, 5 objectives,
    `objective: ""` and `source_building: ""` on all; its `deli_counter:*`
    anchors are the unplaced generated shell `lf_bank_block_001_9054`'s, in
    that shell's local frame. 9189, 9191 and 9193's packages mark no
    objective and name no building either. `tools/look_shots.gd::
    _anchor_spine` takes the first anchor of each type; §13's perf row says
    the station harness takes its stations from the same file.
  - cold run 9195's shell leg: every candidate's Lot pacing is `mode: heist`,
    travel counted, target 25-35 min, 2.8-3.4 min "likely TOO SHORT";
    Level Factory raised `LOT_PACING_OUTSIDE_TARGET` (moderate, non-blocking)
    once a candidate; the heist gate passed in all three assemblies.

Anchored on docs/LEVEL_STANDARD.md as patch_level_standard_v1_2.py left it
(65,457 bytes, LF; commit 4760cae). Every anchor must match once; nothing is
written on a miss.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "LEVEL_STANDARD.md"

EDITS = [
    # the version line
    ("**This is v1.2** (2026-10-07). It records cold run 9194, the first level\n"
     "whose score is the building its brief asked for (§4, §5, Part II's first\n"
     "item and Appendix A; `patches/patch_level_standard_v1_2.py`). v1.1\n",
     "**This is v1.3** (2026-10-07). v1.3 adds what the package says about the\n"
     "score (§4, roadmap 204) and the brief's pacing reaching Lot, seen in cold\n"
     "run 9195 (Part 0, §5, Appendix A; roadmap 200;\n"
     "`patches/patch_level_standard_v1_3.py`). v1.2 recorded cold run 9194, the\n"
     "first level whose score is the building its brief asked for (§4, §5,\n"
     "Part II's first item and Appendix A; `patches/patch_level_standard_v1_2.py`).\n"
     "v1.1\n"),
    # Part 0: the pacing row
    ("ef's `target_minutes` (25-35) is written where `site_pacing` does not look (roadmap 200) |\n",
     "ef's `target_minutes` (25-35) is written where `site_pacing` does not look (roadmap 200). **Since Level "
     "Factory 0.153.0** the estimate counts a heist's travel and reads the brief's window: cold run 9195's three "
     "candidates read 2.8-3.4 min against 25-35, \"likely TOO SHORT\". It counts travel, setup and objective work, "
     "and no fighting |\n"),
    # §4: the package's anchors
    ("- **Objective anchors** reach the package: 9 on cold run 9193's level.\n"
     "  BUILT.\n",
     "- **Objective anchors** reach the package: 9 on cold run 9193's level.\n"
     "  BUILT, and unmarked (roadmap 204). No anchor names its building and\n"
     "  none marks the score: on cold run 9194's bank level the score's vault\n"
     "  is the last of five objective anchors. On a library lot the mission's\n"
     "  own generated shell, which the lot does not place, contributes anchors\n"
     "  in its local frame, listed first. The package's own readers depend on\n"
     "  that list: `tools/look_shots.py` takes the first anchor of each type for\n"
     "  its eye-level shots, and the perf harness takes its stations from it\n"
     "  (§13). GAP, owner Level Factory: mark the score, name each anchor's\n"
     "  building, and stage no anchor from a shell the lot does not place.\n"),
    # §5: the heist gate
    ("  - Its hard gates fire only when the site spec carries a `mode`, and\n"
     "    Level Factory writes none. On every generated site it is intel, not a\n"
     "    gate (roadmap 200).\n",
     "  - Its hard gates fire only when the site spec carries a `mode`. Level\n"
     "    Factory writes `heist` since 0.153.0 (roadmap 200), so the heist gate\n"
     "    -- spawn, objective and extraction joined -- runs on every generated\n"
     "    site. It passed all 144 candidate specs on disk before it was\n"
     "    switched on, and cold run 9195's three assemblies after. GATE.\n"
     "    *v1.2 read: Level Factory writes none, so it is intel, not a gate.*\n"),
    # Appendix A: target_minutes
    ("| session_min | `target_minutes` | **nothing reads it.** *v1.1 read \"Laser Tag's scenario timing, BUILT\":* "
     "wrong. Nothing in Laser Tag or in Level Factory's Laser Tag path reads it (re-checked 2026-10-07). Lot's pacing "
     "estimate is the reader it was meant for, and is wired by Level Factory 0.153.0 | GAP (roadmap 200) |\n",
     "| session_min | `target_minutes` | Lot's pacing estimate, as its window (`pacing.target_minutes`, Level Factory "
     "0.153.0); a level outside it raises `LOT_PACING_OUTSIDE_TARGET`, non-blocking. What the window means -- a "
     "session, which the estimate cannot reach without a combat term, or the structural route, which it measures at "
     "about 3 min -- is the walker's call. *v1.1 read \"Laser Tag's scenario timing, BUILT\": wrong; nothing in Laser "
     "Tag reads it, and before 0.153.0 nothing read it at all* | BUILT (cold run 9195) |\n"),
    # Appendix A: the fields nothing builds from
    ("`route_shape` is Level Factory metadata that Lot ignores, and the other two feed only the functional lock's "
     "signature | GAP (roadmap 200) |\n",
     "`route_shape` is Level Factory metadata that Lot ignores, and the other two feed only the functional lock's "
     "signature. `batch create` says so out loud since Level Factory 0.153.0 (`UNBUILT_BRIEF_FIELDS`) | GAP "
     "(roadmap 200) |\n"),
]


def main():
    data = DOC.read_bytes()
    assert len(data) == 65457, "LEVEL_STANDARD.md is %d bytes, read at 65,457" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old, new in EDITS:
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:70])
    for old, new in EDITS:
        text = text.replace(old, new)
    DOC.write_bytes(text.encode("utf-8"))
    print("LEVEL_STANDARD.md: v1.3, %d edits, %d -> %d bytes" % (len(EDITS), len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
