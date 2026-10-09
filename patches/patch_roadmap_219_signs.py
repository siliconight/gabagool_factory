"""Roadmap 219: note 10 fixed (Zoo 1.90.0), not yet run cold; its owner corrected.

The status line is replaced whole: the one line that starts with its unique opening, asserted to
be exactly one. Note 10's table row is replaced whole, asserted once, and keeps the first
attribution it corrects. The body's "nothing is changed yet" goes, the status line being the
record of what has. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

START = "*STATUS: NARROWED 2026-10-09 -- three of the twelve notes fixed, not yet run cold."
NEW = (
    "*STATUS: NARROWED 2026-10-09 -- four of the twelve notes fixed, not yet run cold. Lot 0.102.1 "
    "stands the bus stop on its band before the corner is spaced against it (note 6: a marker swept "
    "along the kerb probe's stop band found 22 overlaps on 0.102.0 and none now); Lot 0.102.2 turns "
    "each meter's windows across the kerb, one to the sidewalk (note 4); Deli Counter 0.204.1 keeps 3 "
    "of the rowhomes' 10 roof fixtures, antennas on a and g and the dish on k (note 3), its 146 shells "
    "rebuilt; Zoo 1.90.0 letters the sign over a door in its owner's face at 240 px a metre, sampled "
    "filtered -- Blue Highway Condensed for a shop, Aileron Bold for a civic fascia (note 10: on every "
    "library sign width the median letter is 1.44 times 1.89.0's; the photographed sign goes from two "
    "pixel lines at 17.5 cm to one line at 24.2 cm). Pixelcoat's street band still letters in Pixel "
    "Operator; none is in club_block_014. Next, each a block of its own: the signals' runtime cycle "
    "(Zoo lit all three lenses dim on purpose, \"a signal whose state is baked is a signal that is "
    "wrong half the time\"), and the den windows; then the club's light, the moon, the two "
    "placeholders and the bags; then the perimeter and the backdrop as a menu with frames. A cold run "
    "of club_block_014 proves the quick ones together, with frames of the signs.*"
)

ROW_START = "| 10 | \"need better looking fonts on these signs\" | Pixelcoat |"
ROW_NEW = (
    "| 10 | \"need better looking fonts on these signs\" | Zoo (Pixelcoat for the street band) | The "
    "sign photographed, strip_club_a01's door box, is Zoo's: `storefront_names.paint` set the name in "
    "`pixel_type`'s Pixel Operator at 80 px a metre and `sign_box` sampled it Closest. In cold run "
    "9213's package its material is `_card_atlas.build_art`'s, and no Pixelcoat sign pack is in that "
    "package. *First attributed here to Pixelcoat's `core/signage.py`,* which letters the street band "
    "and a door that wears it (Level Factory 0.148.0), and is not in this level. DECIDED, the walker: "
    "\"use Blue Highway for the shop signs\". FIXED in Zoo 1.90.0; the band is Pixelcoat's own change. |"
)

BODY_OLD = "Owners and causes were found by reading the code; nothing is changed yet."
BODY_NEW = "Owners and causes were found by reading the code; the status line records what has changed."


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    lines = data.decode("utf-8").split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(START)]
    assert len(hits) == 1, len(hits)
    rows = [i for i, ln in enumerate(lines) if ln.startswith(ROW_START)]
    assert len(rows) == 1, len(rows)
    body = [i for i, ln in enumerate(lines) if BODY_OLD in ln]
    assert len(body) == 1, len(body)
    lines[hits[0]] = NEW
    lines[rows[0]] = ROW_NEW
    lines[body[0]] = lines[body[0]].replace(BODY_OLD, BODY_NEW)
    ROADMAP.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 219: note 10 fixed, its owner corrected")


if __name__ == "__main__":
    main()
