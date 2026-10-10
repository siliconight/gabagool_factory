"""Roadmap 219: note 2 fixed (Zoo 1.91.0, Deli Counter 0.205.0), not yet run cold.

The status line is replaced whole: the one line that starts with its unique opening, asserted to
be exactly one. Note 2's table row is replaced whole, asserted once, keeping what it first
proposed. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

START = "*STATUS: NARROWED 2026-10-09 -- five of the twelve notes fixed, not yet run cold."
NEW = (
    "*STATUS: NARROWED 2026-10-09 -- six of the twelve notes fixed, not yet run cold. Lot 0.102.1 "
    "stands the bus stop on its band before the corner is spaced against it (note 6: a marker swept "
    "along the kerb probe's stop band found 22 overlaps on 0.102.0 and none now); Lot 0.102.2 turns "
    "each meter's windows across the kerb, one to the sidewalk (note 4); Deli Counter 0.204.1 keeps 3 "
    "of the rowhomes' 10 roof fixtures, antennas on a and g and the dish on k (note 3), its 146 shells "
    "rebuilt; Zoo 1.90.0 letters the sign over a door in its owner's face at 240 px a metre, sampled "
    "filtered -- Blue Highway Condensed for a shop, Aileron Bold for a civic fascia (note 10: on every "
    "library sign width the median letter is 1.44 times 1.89.0's; the photographed sign goes from two "
    "pixel lines at 17.5 cm to one line at 24.2 cm); Level Factory 0.165.0 gives a signal's lenses one "
    "60 s clock at import, green 33 s, amber 4 s, red 23 s, every head in step (note 9: cold run 9213's "
    "signal through the new import in Godot 4.7, sampled every half second, went green to amber "
    "between 33.0 and 33.5 s and amber to red between 37.0 and 37.5 s, its two heads agreeing in all "
    "31 samples); Zoo 1.91.0 draws `window_drape`, two velvet panels drawn shut under a pelmet, and "
    "Deli Counter 0.205.0 hangs one in every strip club window with no window light behind it (note "
    "2: four drapes, a01's one and a03's three, each centred on the window the builder cut; the "
    "census found 0 coincident pairs at its three corners). Pixelcoat's street band still letters in "
    "Pixel Operator; none is in club_block_014. Next: the club's light, the moon, the two "
    "placeholders and the bags; then the perimeter and the backdrop as a menu with frames. A cold "
    "run of club_block_014 proves the quick ones together, with frames of the signs, the signals and "
    "the drapes.*"
)

ROW_START = "| 2 | den windows get curtains, drapes or blinds:"
ROW_NEW = (
    "| 2 | den windows get curtains, drapes or blinds: \"people outside can't see in, and you keep the "
    "streetlight light out\" | Zoo (the drape), Deli Counter (where it hangs) | No rule covered a den's "
    "windows; strip_club_a01's are clear glass, with a window light behind them. FIXED: Zoo 1.91.0's "
    "`window_drape` (two velvet panels drawn shut under a pelmet, both sides cloth), hung by Deli "
    "Counter 0.205.0 on every window of a strip club, which then derives no window light behind it. "
    "*First proposed here as \"Zoo paints the states\"* -- `empty_panes.py`'s painted curtain, blind "
    "and shade -- which are an Empty's: seen from outside alone, over a hollow box. A den has a room "
    "behind its glass, and the room sees the drape too. |"
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    lines = data.decode("utf-8").split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(START)]
    assert len(hits) == 1, len(hits)
    rows = [i for i, ln in enumerate(lines) if ln.startswith(ROW_START)]
    assert len(rows) == 1, len(rows)
    lines[hits[0]] = NEW
    lines[rows[0]] = ROW_NEW
    ROADMAP.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 219: note 2 fixed")


if __name__ == "__main__":
    main()
