"""Roadmap 188 NARROWED, 2026-10-19: the plate perimeter it left open shipped under roadmap 228 (step B, Lot 0.107.0,
2026-10-10) and was never marked here. Found choosing the next item: the status (OPEN 2026-10-06) still named
"the plate perimeter, which needs the backdrop behind it" as open, while `site_fences.plan_perimeter` has fenced
every plate since cold run 9224 and cold run 9324's site records `perimeter.fenced_runs` 6. The status line is
replaced whole, the OPEN status kept after it verbatim; a paragraph goes after the item's last body line.
Anchored on both lines' sha256, the heading two lines below the status. The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_188_perimeter.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
STATUS_SHA = "900dd6bb3983156a6d5554d625353626a6d488603a6dbea6a2cb2eb0593b69f8"
HEADING_PREFIX = "**188. The fence at the playable edge.**"
OLD_PREFIX = "*STATUS: OPEN 2026-10-06 -- "
BODY_END_SHA = "3708219d9d57bc8ecd6cf6084f5b8af8017a93b16cb0aacc04b0909309ec115f"

NEW = ("*STATUS: NARROWED 2026-10-19 -- the plate perimeter is fenced, shipped under roadmap 228 and not marked here "
       "until now. Lot 0.107.0 (2026-10-10, 228's step B, `patches/patch_lot_perimeter_fence.py`): "
       "`site_fences.plan_perimeter` lays one chain-link run a side 0.25 m inside the plate's wall, a side longer "
       "than 120 m split into equal runs, a run that would stand on a mission marker left out and said; the wall "
       "keeps its collision and shows nothing. Cold run 9224 is its first level (`LOT_PERIMETER_FENCED: 6 run(s), "
       "589.7 m of chain-link`), the backdrop has stood behind it since Lot 0.108.0 (cold run 9225), and it stands "
       "in every level since -- cold run 9324's site records `perimeter.fenced_runs` 6. Left: vacant lots, and "
       "Empties not in a row. Earlier status kept: OPEN 2026-10-06 -- ")

BODY = [
    "",
    "**THE PERIMETER, 2026-10-19: SHIPPED UNDER 228, MARKED HERE LATE.** The paragraph above was right that a "
    "see-through fence at the edge needed a backdrop behind it, and 228 built both: the fence in Lot 0.107.0 "
    "(cold run 9224, six runs and 589.7 m on restaurant_row_001's plate, the wall's 324 `perim_` names in 9223's "
    "`site.tscn` down to the 16 of its four bodies and their shapes) and the backdrop in Lot 0.108.0 (cold run "
    "9225). Nothing then came back to this item, so its status named the perimeter as open for nine days after "
    "it stood. What this item still asks of the edge: a fence on a vacant lot, and on an Empty that stands alone "
    "rather than in a row.",
]


def _sha(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if _sha(l) == STATUS_SHA]
    assert len(hits) == 1, f"item 188's OPEN status found {len(hits)} times"
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(HEADING_PREFIX), "the status no longer adjoins 188's heading"
    old = lines[i]
    assert old.startswith(OLD_PREFIX) and old.endswith("*")
    ends = [j for j, l in enumerate(lines) if _sha(l) == BODY_END_SHA]
    assert len(ends) == 1 and ends[0] > i, f"item 188's last body line found {len(ends)} times"
    j = ends[0]
    assert lines[j + 1] == "" and lines[j + 2].startswith("*STATUS:"), "item 188's body no longer ends there"
    for k in range(i + 3, j):
        assert not lines[k].startswith("*STATUS:"), "another status inside item 188 at line %d" % (k + 1)
    for block in BODY:
        assert not (block.startswith("**") and block[2:3].isdigit()), "a body line would parse as an item"
    lines[i] = NEW + old[len(OLD_PREFIX):]
    assert lines[i].startswith("*STATUS: NARROWED 2026-10-19 -- ") and lines[i].endswith("*")
    lines[j + 1:j + 1] = BODY
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 188 NARROWED (the perimeter, Lot 0.107.0 under 228); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
