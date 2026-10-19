"""Roadmap 169 CLOSED, 2026-10-19: the ladder skin shipped on 2026-10-04 (Level Factory 0.136.0, 1343cc2) and the
item was never marked -- its status still read "held behind a cold run" from 2026-09-23. Re-measured on cold run
9321's package: no ladder surface ships in greybox. The status block is replaced whole, the OPEN 2026-09-23
status kept after it verbatim. Anchored on that block's sha256 and on the item heading below it (asserted once).
The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_169_closed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

OLD_FIRST = "*STATUS: OPEN 2026-09-23 -- DESIGNED, STAGED AND DRY-RUN CLEAN, HELD BEHIND A"
OLD_LINES = 5
OLD_SHA256 = "986b45376d11ec3673fb2e981679f69c24bbc3c58c90b060a5407895cfc26a95"
HEADING = "**169. A ladder ships in the greybox yellow, and skinning it spends a"
OLD_PREFIX = "*STATUS: OPEN 2026-09-23 -- "

CLOSED = """*STATUS: CLOSED 2026-10-19 -- shipped on 2026-10-04 and never marked here.
Level Factory 0.136.0 (1343cc2) applied the four staged patches' work, every
anchor still matching: `zoo_worldskin.gd`'s `_assign_ladders` skins a ladder
with the building's own metals, the rails on the darkest and the rungs on the
lightest, and an exterior ladder takes the theme's rusted steel; Deli Counter
writes the exterior mark it reads (`deli_counter.py:2259`, `ladder<n>ext_`,
from `Ladder.placement_mode`, since 0.173.0); `test_worldskin_ladders.py` (10,
through a real Godot import) pins it. Re-measured on cold run 9321's package
(`greybox_skin_scan.json`): 0 `gb_ladder` surfaces, where cold run 9070's had
38 (22.82 m2). The only greybox left in that themed package is three
`VAULTLEDGE_n` surfaces on `gb_floor` (49.7 m2), a separate defect. Earlier
status kept: OPEN 2026-09-23 -- """


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if l == OLD_FIRST]
    assert len(hits) == 1, f"the OPEN 2026-09-23 status found {len(hits)} times"
    i = hits[0]
    block = "\n".join(lines[i:i + OLD_LINES])
    assert hashlib.sha256(block.encode("utf-8")).hexdigest() == OLD_SHA256, "the status block changed"
    assert lines[i + OLD_LINES] == "" and lines[i + OLD_LINES + 1] == HEADING, \
        "the status no longer adjoins item 169's heading"
    assert block.startswith(OLD_PREFIX) and block.endswith("*")
    new = CLOSED + block[len(OLD_PREFIX):]
    assert new.startswith("*STATUS: CLOSED 2026-10-19 -- ") and new.endswith("*")
    for ln in new.split("\n"):
        assert not ln.startswith("**"), f"a status line must not start a parseable heading: {ln[:40]!r}"
    lines[i:i + OLD_LINES] = new.split("\n")
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 169 CLOSED (shipped in Level Factory 0.136.0, re-measured on cold run 9321); now "
          "roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
