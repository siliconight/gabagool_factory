"""Level Factory 0.152.0's release: VERSION and the CHANGELOG entry.

    python patch_lf_0152_release.py

Anchored on VERSION (b'0.151.0') and on CHANGELOG.md's head (627,409 bytes,
LF, as read 2026-10-07).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

HEAD = "## [0.151.0] - The light bake lays the rooms' floor, and frees it before it saves\n"
ENTRY = """## [0.152.0] - The score is the building the brief asked for

**Roadmap 201, found writing the level standard** (`docs/LEVEL_STANDARD.md`
§4). `site_variation.site_placements` drew the spawn and the objective
building independently from the seed. So the score ignored the brief's
archetype, and it could be the building the crew spawned at.

**Measured on 0.151.0's own code**, seeds 9000-9011: spawn == objective on
3 of 12 three-building sites and 2 of 12 four-building sites.

**On the breadth sweep's picked seeds.** Seven of its eight library briefs
anchor a family; precinct_yard_001's `police_station` has none. Of those
seven, the roles were wrong on six:
- **The crew spawned at the score building:** gas_block_001,
  club_block_014 and video_block_001 (seed 9080).
- **The heist pointed at another building:** bank_block_001 (b2, not its
  bank), card_block_001 (b1) and gas_stop_001 (b2).
- **Right by chance:** only restaurant_row_001's score.

**`pick_lot` already places the archetype's family first** (roadmap 44, cold
run 9007), so on an anchored lot the score is b0:
- `building_library.score_building(entries, archetype)` says so: `"b0"` when
  a family answers to the archetype, `None` when none does.
- `site_placements(..., objective=)` takes it as the objective and draws the
  spawn among the other buildings. The objective's own draw is still made, so
  the extraction draw and every building's placement do not move.
- With no objective given -- a single generated shell, every copy the
  archetype's, or a library with no family for it -- the roles are the draw
  that always was.
- The site spec records which rule decided: `objective_from`, `archetype` or
  `seed`.

**What it invalidates:** every anchored library candidate's spawn, objective
and extraction. A graded mission re-rolls its roles on its next evaluation.
Its buildings and their placements do not move.

**Tests:** `tests/unit/test_score_building.py`, 11. On 0.151.0, 10 fail; the
one that passes pins the old draw for a site with no score given. Suite:
1,983 passed, 14 skipped, 1 xfailed (exit 0).

"""


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.151.0", repr(v)
    c = (LF / "CHANGELOG.md").read_bytes()
    assert len(c) == 627409 and b"\r\n" not in c, len(c)
    text = c.decode("utf-8")
    assert text.startswith(HEAD) and text.count(HEAD) == 1
    (LF / "VERSION").write_bytes(b"0.152.0")
    (LF / "CHANGELOG.md").write_bytes((ENTRY + text).encode("utf-8"))
    print("Level Factory 0.152.0: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
