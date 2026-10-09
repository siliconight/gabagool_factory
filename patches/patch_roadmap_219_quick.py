"""Roadmap 219: three of the walker's twelve walk notes fixed (Lot 0.102.1 and 0.102.2, Deli
Counter 0.204.1), not yet run cold.

The status line is replaced whole: the one line that starts with its unique opening, asserted
to be exactly one. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

START = "*STATUS: OPEN 2026-10-09 -- twelve notes from the walker's walk of club_block_014"
NEW = (
    "*STATUS: NARROWED 2026-10-09 -- three of the twelve notes fixed, not yet run cold. Lot 0.102.1 "
    "stands the bus stop on its band before the corner is spaced against it (note 6: a marker swept "
    "along the kerb probe's stop band found 22 overlaps on 0.102.0 and none now); Lot 0.102.2 turns "
    "each meter's windows across the kerb, one to the sidewalk (note 4); Deli Counter 0.204.1 keeps 3 "
    "of the rowhomes' 10 roof fixtures, antennas on a and g and the dish on k (note 3), its 146 shells "
    "rebuilt. Decided: Blue Highway for the shop signs. Next, each a block of its own: the sign face "
    "(Zoo sets shop signs in minted Pixel Operator bitmaps, inside Blender, so Blue Highway is minted "
    "with coverage at a higher density and sampled smooth), the signals' runtime cycle (Zoo lit all "
    "three lenses dim on purpose, \"a signal whose state is baked is a signal that is wrong half the "
    "time\"), and the den windows; then the club's light, the moon, the two placeholders and the bags; "
    "then the perimeter and the backdrop as a menu with frames. A cold run of club_block_014 proves the "
    "quick ones together.*"
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    lines = data.decode("utf-8").split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(START)]
    assert len(hits) == 1, len(hits)
    assert "three of the twelve notes fixed" not in lines[hits[0]], "already applied"
    lines[hits[0]] = NEW
    ROADMAP.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 219: three notes fixed")


if __name__ == "__main__":
    main()
