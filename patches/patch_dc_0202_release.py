"""Deli Counter 0.202.0: VERSION and CHANGELOG for "a wall piece needs a wall behind it".

    python patch_dc_0202_release.py <suite line>

Anchored on VERSION and the CHANGELOG head as read 2026-10-07.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.202.0] - a wall piece needs a wall behind it, and furniture keeps off a hole in its own floor

**How it was seen.** Framing the deli case in cold run 9190's deli_a01, two
things stood in front of its service front: an ATM, and two paper lottery
boards hanging in mid-air. All were furnish's wall pieces, slotted against
the customer floor's north edge (y -3.0). No wall stands there: the customer
floor meets the deli counter room across open floor.

**The measurement** (the factory's `docs/findings/wall_pieces_without_walls/`):
- **155 of the library's 4,086 furnished wall pieces, in 18 shells,** stood
  against a room edge with no built wall behind them.
- The six delis held 76, apartment_walkup_a01 18, rowhouse_raid 17.
- By kind: shelf runs 43, file cabinets 27, store poster boards 17, waiting
  chairs 10, service counters 10.

**Why.** `_wall_slots` offered a wall piece every edge of its room. It
checked an exterior edge's openings and glazing, but an interior edge it took
for a wall and never asked. Measured against 0.201.0's library:
- 3,924 wall pieces stood against exterior walls, 42 near a partition and
  120 against nothing.
- `_seed_clear` keeps every piece 1.0 m from a partition's line, so furnish
  furnished partitions almost never.
- Its "interior walls" were, in practice, open edges.

**The rule** (`_edge_backing`, `_held`).
- **Where a slot is offered.** Only where a wall the builder stands lies on
  the edge, and holds the piece's whole run. These are
  `layout_lint.built_walls`, the walls L25 measures, cached per spec.
- **Every slot is drawn and shuffled as before.** The unheld ones are
  dropped after the shuffle, so the held slots keep their order and the
  random stream is untouched. Only a piece that stood against nothing moves,
  and what its move displaces.
- **Refuted, kept:** the first draft dropped an unheld slot before the
  shuffle. That changed the length of every shuffled list, and its dry run
  re-rolled 33 specs where 18 held a piece against nothing.

**Furniture keeps off an authored hole in its own floor** (`_seed_clear`).
- L23's second cause, "UNSEEN": furnish cleared the stairs and never an
  authored `slab_holes` opening.
- The wall rule's refurnish re-rolled apartment_walkup_a01's dining room and
  rowhouse_raid's. Both dining sets landed over their 2 x 2 m drop holes,
  rowhouse_raid's for the first time.
- **The rule:** a piece standing on a storey keeps the stair reserve's own
  0.3 m off every authored hole in that storey's floor.
  - Its own storey only: the storey below stands under a hole, not on it.
  - A hung piece is not asked.
- **What it moved.** cbp_town_finale's and final_stand's furnished pieces,
  inside atrium holes of 28 x 22 m and 10 x 8 m that nothing fills, and both
  dining sets.

**The library** (`migrate_furnish_recipes`, both rules): 20 specs moved.
- These are the census's 18, plus cbp_town_finale and final_stand. 153 fewer
  furnished pieces in all: most of the 155 had no other wall to go to.
- deli_a01's customer floor carries nothing on its open edge, and no
  library wall piece stands without a wall.
- **The 20 shells are rebuilt.** `level_design.py` is not a geometry
  source, so nothing else needed it.

**Baselines moved, each by measurement:**
- `stale_pieces_baseline.json`: 47 pieces in 8 shells -> 18 in 7.
  apartment_walkup_a01 leaves the list, along with 20 of cbp_town_finale's
  pieces and 6 of final_stand's. Nothing joins it. The 18 left are authored
  volumes and structure.
- `test_club_fixtures`: the library's cigarette machines 121 -> 119. The two
  stood against open edges.

**The furnish and club probes stand their rooms in walls.**
- They stood a room 2 m inside a larger footprint, "so its walls are
  interior": edges the rule now refuses. 18 failed for that alone.
- Each room becomes the shell, and two basement probes declare their
  basement. All 68 tests in the three files pass on 0.201.0 with the new
  fixtures, so the fixtures changed what they stand in, not what they test.

**Tests:**
- `test_wall_backing.py`, 8. Five fail on 0.201.0: an open edge, a
  part-wall, the library, the deli's open edge, and a generated deli. The
  guards (a walled edge, an exterior edge) and the fixed point pass either
  side.
- `test_stale_pieces.py` +2. The hole test fails on 0.201.0; the storey-below
  guard passes either side.

**Open:** a partition is still unfurnished. `_seed_clear`'s 1.0 m rule keeps
pieces off every partition's line to keep its doors clear, and a rule that
clears a partition's openings, not its length, would let its walls be used.

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.201.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.201.0] - a deli hangs its beer sign"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.202.0")
    print("Deli Counter 0.202.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
