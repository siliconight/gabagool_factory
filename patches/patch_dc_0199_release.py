"""Deli Counter 0.199.0: VERSION and CHANGELOG for "no piece passes through a wall".

    python patch_dc_0199_release.py <suite line>

Anchored on VERSION and the CHANGELOG head as read 2026-10-06.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.199.0] - no piece passes through a wall: the deli's case stopped 0.825 m into the market aisles

**How it was seen.** Sizing the deli case for roadmap item 186's deli detail.
In cold run 9189's composed deli_a01, `deli_case_cover` stands at
x -14.0..-7.0, and partition segment `int_0_0_seg6` stands at x -8.0 across
it. So the last 0.825 m of the case came out of the wall into the market
aisles. `presets.corner_deli` authors it that way, so it was in all six
library delis and in every deli the recipe generates.

**The measurement** (the factory's `docs/findings/pieces_through_walls/`, two
instruments that agree). Every authored piece was checked against every wall
the builder stands, across the 146 non-LF specs. 19 pieces in 15 specs reach
past both faces of a built wall:
- **THROUGH, 7:** the piece's centre stands off the wall and its far end
  comes out of it. Each deli's case (0.825 m), and `warehouse`'s 16 m
  shelving run (3.85 m).
- **ALONG, 12:** the piece is centred on the wall's line. These are racks
  and forklift bays on y -3.0, two vomitory covers and a rollgate, a vault
  door, and four columns.
- **The recipes:** `corner_deli` (the case) and `hospital` (its waiting
  seats, 0.35 m) generate a piece through a wall. `casino_tower` (its
  basement vault block) and `parking_garage` (a column) stand one along a
  wall.

No gate saw any of them. Every rule asked a piece where it stands; none
asked whether a wall stands in it.

**L25 (WARN), `layout_lint.wall_crossings`.** It measures the walls as the
builder stands them, asking the builder's own helpers.
- **Partitions:** `partition_bounds.partition_spans`, clamped to the storey's
  setback extent and split round `stairwell.wall_voids`.
- **Exterior walls:** every side on every storey under `auto_exterior`.
- **Pieces:** each is measured by its box, which is the greybox and its
  collider, and, when `rot_z` turns it, by its art turned.
- **Openings are not cut.** A leaf, a panel or a pane fills each, and no
  crossing stood at one.

**The trim, `migrate_wall_crossing.trim`.** A piece THROUGH a wall keeps its
near end. Its far end comes back to the wall's near face, less
`level_design._WALL_PIECE_AIR`. It is refused, with the reason, when:
- the piece stands along the wall;
- the piece is turned;
- the cut would take more than half the piece;
- the cut would take the ground from under a marker.

Where it runs:
- **`presets.make`** runs it on every recipe before any pass places round
  it. A generated deli's case stands x -14.0..-8.185, and a generated
  hospital's seats stop at their wall.
- **The library:** the migration trimmed 7 pieces, the six cases to
  x -14.0..-8.185 and the shelving run to x -4.0..7.84. Each spec changed in
  two numbers.
- **The twelve ALONG a wall** are frozen in `wall_crossing_baseline.json`,
  each needing a look. After the migration, both instruments read 12 in 8
  specs.

**Tests:** `test_wall_crossing.py`, 19. All 19 fail on 0.198.0. 16 pass with
the rule, the trim and the generator change, before the library is migrated.
The last 3 pass after the migration: the library's cases stop at their wall,
the migration is a fixed point, and no new crossing appears.

**Suite:** SUITE_LINE.

'''


def main():
    suite = " ".join(sys.argv[1:]).strip()
    assert suite, "pass the suite line as run"
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.198.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.198.0] - the z-fight gate judges a pair by the side"), text[:60]
    cl.write_bytes((ENTRY.replace("SUITE_LINE", suite) + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.199.0")
    print("Deli Counter 0.199.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
