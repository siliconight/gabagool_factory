"""Roadmap 219: note 1, the club's light, fixed in Lux 0.72.0 (not yet run cold).

219's status line is replaced whole: the one line that starts with its unique opening, asserted
to be exactly one. Row 1 of 219's table is replaced whole the same way. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

START = "*STATUS: NARROWED 2026-10-09 -- six of the twelve notes fixed and PROVEN together in cold run 9217"
NEW = (
    "*STATUS: NARROWED 2026-10-10 -- seven of the twelve notes fixed. Six were PROVEN together in "
    "cold run 9217, club_block_014 at seed 9181 by night, the walked level: 0 interventions, 0 "
    "retries, findings 72 to 71 against 9213. They are notes 6 and 4 (Lot 0.102.1 and 0.102.2), 3 "
    "(Deli Counter 0.204.1), 10 (Zoo 1.90.0), 9 (Level Factory 0.165.0) and 2 (Zoo 1.91.0's drape, "
    "hung by Deli Counter 0.205.0); the table says what each changed. Note 1, the club's light, is "
    "FIXED in Lux 0.72.0 and not yet run cold: a den's bake lays washers on every wall in its "
    "washes' colours and fills the room in its own colour. On 9217's walk copy re-baked with the "
    "release's loader, the main floor reads 14.5 mean, median 8 (from 3.7 and 1), the VIP wing 13.0 and 7 (from 2.2 and 0), the cash office that holds the objective 6.9 and 3 (from 2.6 and 1), about half of each club frame still under 10; the bake took 83.5 s against 82.3, and a level carries none of it at run time. Pixelcoat's street band still letters in Pixel Operator; "
    "none is in club_block_014. Next: a cold run of 0.72.0 with Patina 0.29.2 (item 220), then "
    "the two placeholders and the bags, then the perimeter and the backdrop as a menu with frames; "
    "the moon waits on the walker.*"
)

ROW_START = "| 1 | \"strip club is still a tad too dark"
ROW_NEW = (
    "| 1 | \"strip club is still a tad too dark ... dark and moody, but lit enough for a player to "
    "see and experience it\" (comps: VtMB, KOTOR 2) | Lux | Dens of sin get no bake fills (Lux "
    "0.68.2); the club is lit by washes in pools. Measured, luma after the grade: our club frame "
    "mean 1.8, median 1, 98% under 10; the comps mean 36 to 43, median 15 to 39, 19 to 40% under "
    "10. Measured since (`docs/findings/club_light_trials/`): the club's light is almost all baked; "
    "its brightest pools were on the CEILING, from the stage lip's and the back bar's low omnis "
    "lighting the office tile (albedo 0.545), while the carpet (0.036) eats the washes' pools. A "
    "white fill reads the floor but greys the tile into an office grid. FIXED in Lux 0.72.0: "
    "bake-only washers on every wall of a tinted den room in the nearest wash's colour, 2.34 x "
    "`REFERENCE_POOL` on the wall, and a fill in the room's own colour at share 2; a den's back "
    "rooms take the bulb rooms' white 0.5. Open, and not Lux's: the club's ceiling is the office "
    "tile (Deli Counter's `dress_club_rooms` never sets it), and the washers have no hardware. The "
    "brighter fill at 4 is the walker's call. |"
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    text = data.decode("utf-8")
    assert "RESULT_" not in NEW, "the status still carries an unfilled result"
    lines = text.split("\n")
    for start, new in ((START, NEW), (ROW_START, ROW_NEW)):
        hits = [i for i, ln in enumerate(lines) if ln.startswith(start)]
        assert len(hits) == 1, (start[:50], len(hits))
        lines[hits[0]] = new
    ROADMAP.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 219: note 1 fixed in Lux 0.72.0, not yet run cold")


if __name__ == "__main__":
    main()
