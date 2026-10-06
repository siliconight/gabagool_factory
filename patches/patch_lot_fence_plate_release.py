"""Lot 0.97.1: VERSION and the CHANGELOG entry for `patch_lot_fence_plate.py`.

    python patch_lot_fence_plate_release.py
"""
import pathlib

LOT = pathlib.Path(__file__).resolve().parent.parent / "lot"

ENTRY = '''## 0.97.1 - a fence does not grow the plate it marks the edge of

**Cold run 9183, measured on its own scenes.** The greybox `site.tscn` and
the themed one both stood `perim_S` at 254 m. 9182, the same candidate
without fences, stood it at 246 m.

**The mechanism** (`site_extent.required_rect`). The ground carries the union
of everything on the site grown by `CLEARANCE` (4 m), and every cover piece
is in that union.
- 0.97.0's end runs reach the plate's edge by design.
- Re-resolved with the fences standing, the plate grew 4 m past each one.
- Each end fence then stopped 4 m short of the perimeter wall. That left a
  walk-around at both ends of the row, which is exactly what the end runs
  were for.
- The `LOT_GROUND_EXTENDED` line still said 246 m, because it was printed by
  the resolve before the fences stood.

**The fix:** `content` leaves out cover that `site_fences` placed. A fence
marks the playable edge; it is not content the ground has to carry clearance
around.

**Re-assembled** with this checkout on 9183's own `site.json` (seed_9181):
`perim_S` is 246 m, and the 13.0 m end run stops at x -123.0, where
`perim_W` stands.

**Tests:** `tests/test_site_fences.py::test_the_fence_does_not_grow_the_plate_it_marks`.
It resolves the ground, plans the fences, resolves again with them standing,
and asserts the rect is unchanged and the end runs still reach it. It fails
on 0.97.0.

**Suite:** 661 passed (0.97.0's 660 and this test).

'''


def main():
    version = LOT / "VERSION"
    changelog = LOT / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"Lot 0.97.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## 0.97.0 - "), c[:60]
    version.write_bytes(b"Lot 0.97.1")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Lot 0.97.1: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
