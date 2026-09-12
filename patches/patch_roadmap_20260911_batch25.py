"""Roadmap batch 25, 2026-09-11: item 147 gets the light-budget census that
decides which of its two closing moves is open. Body APPEND inside the item
(after its last paragraph, before the file end). Asserts.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

ANCHOR = """or in tiles, and that is item 54 reopened, not this item closed quietly.
"""

ADD = """or in tiles, and that is item 54 reopened, not this item closed quietly.

**THE BUDGET, MEASURED THE SAME HOUR** (`tools/mesh_light_census.py` on the
walked copy, its 57 lights as spawned by Lux 0.33.0, ranges 3.2..5.6 m,
median 4.0): three meshes are ALREADY over the engine default of 8 --
`ceiling_ground_east_ward/Ceiling_Panel_t1_0` at 10, `floor_ward_east_1/
Floor_Panel_t1_0` at 10, `ceiling_ward_east_1/Ceiling_Panel_t1_0` at 9,
each a 7.5 x 6.0 m plate tile (Zoo's `PLATE_TILE` 8.0, not Deli Counter's
5.0 -- item 54's two numbers, deliberately different, meeting here). The
worst mesh's claimants are four ward fluorescents at margins 0.18-0.75 m,
one window omni, four more fluorescents and a wall pack; the census says
every row clears if every range came down 0.52 m. So the second row has NO
headroom on this shell: the first closing move above cannot ship without
either the plate split (Zoo's tile to 5.0, item 54's own residue) or the
range cut it prices, and the item is a budget question before it is a
lighting one.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    n = text.count(ANCHOR)
    if n != 1:
        print(f"anchor matched {n} times; refusing", file=sys.stderr)
        return 1
    out = text.replace(ANCHOR, ADD, 1).encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 147 budget census added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
