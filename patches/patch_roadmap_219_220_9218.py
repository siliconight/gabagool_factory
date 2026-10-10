"""Roadmap 219 and 220: cold run 9218 proves note 1 (Lux 0.72.0) and closes 220 (Patina 0.29.2).

Each status line is replaced whole: the one line that starts with its unique opening, asserted to
be exactly one. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

S219 = "*STATUS: NARROWED 2026-10-10 -- seven of the twelve notes fixed. Six were PROVEN together in"
N219 = (
    "*STATUS: NARROWED 2026-10-10 -- seven of the twelve notes fixed and PROVEN on the walked level, "
    "club_block_014 at seed 9181 by night. Six were proven together in cold run 9217 (0 "
    "interventions, 0 retries, findings 72 to 71 against 9213): notes 6 and 4 (Lot 0.102.1 and "
    "0.102.2), 3 (Deli Counter 0.204.1), 10 (Zoo 1.90.0), 9 (Level Factory 0.165.0) and 2 (Zoo "
    "1.91.0's drape, hung by Deli Counter 0.205.0). Note 1, the club's light, was proven in cold "
    "run 9218 (0 interventions, 0 retries, findings 71 to 71): Lux 0.72.0's wall washers and "
    "tinted fill. Mean and median luma at the room stations: the main floor 3.7 and 1 to 14.5 and "
    "8, the VIP wing 2.2 and 0 to 12.9 and 7, the bar 3.1 and 1 to 17.1 and 9, the cold pipeline "
    "matching the release's own bake to the decimal (`docs/cold_runs/cold_9218/`). Still the "
    "walker's: the brighter fill, and the club's office-tile ceiling. Next: note 5, the box truck "
    "and the litter bin, drawn; note 11, the bags; then the perimeter and the backdrop as a menu "
    "with frames. The moon waits on the walker.*"
)

S220 = "*STATUS: NARROWED 2026-10-09 -- cause found and fixed, not yet run cold. The bar is Patina's"
N220 = (
    "*STATUS: CLOSED 2026-10-10 -- proven in cold run 9218 (club_block_014, seed 9181, night; 0 "
    "interventions, 0 retries). Patina 0.29.2 orders no conduit to a sign, and all three signed "
    "buildings' door signs frame head-on with no bar: strip_club_a01's, airport_terminal_a02's "
    "and funeral_home_a03's (`docs/cold_runs/cold_9218/door_signs.png`). 9217 had carried a "
    "0.27 m conduit stub through each face (`docs/findings/sign_bar/`).*"
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    lines = data.decode("utf-8").split("\n")
    for start, new in ((S219, N219), (S220, N220)):
        hits = [i for i, ln in enumerate(lines) if ln.startswith(start)]
        assert len(hits) == 1, (start[:50], len(hits))
        lines[hits[0]] = new
    ROADMAP.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 219: note 1 proven in 9218; 220 closed")


if __name__ == "__main__":
    main()
