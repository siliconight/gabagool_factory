"""Roadmap 219: note 5, the box truck and the litter bin, drawn in Zoo 1.92.0 (Lot 0.103.0 varies
the trucks' fleets); not yet run cold.

Row 5 of 219's table is replaced whole: the one line that starts with its unique opening, asserted
to be exactly one. 219's status line keeps its proofs and names what is fixed and not yet run.
Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

ROW = "| 5 | \"i dont know what this giant grey box is\" | Zoo |"
ROW_NEW = (
    "| 5 | \"i dont know what this giant grey box is\" | Zoo (Lot for the fleets) | `box_truck` "
    "was still a placeholder silhouette, one solid box; `litter_bin` was the only other one. Both "
    "ship in club_block_014. FIXED in Zoo 1.92.0, not yet run cold: the box truck is a 1990s "
    "cab-over delivery truck in four invented Delco fleets (BLUE ROUTE MOVERS, HOAGIE HAUL, NANA'S "
    "BASEMENT SELF STORAGE, DOWN THE SHORE PARTY RENTALS) -- five materials, 7,918 triangles at the "
    "default slot, glass over a cab interior, no maker's mark; the litter bin is a slatted municipal "
    "street bin in the township's green, LITTER / KEEP DELCO CLASSY-ISH, one atlas and one draw. "
    "Lot 0.103.0 gives each parked truck a fleet from where it stands, so a lot's trucks differ. |"
)

STATUS = "*STATUS: NARROWED 2026-10-10 -- seven of the twelve notes fixed and PROVEN on the walked level"
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-10 -- eight of the twelve notes fixed, seven PROVEN on the walked "
    "level, club_block_014 at seed 9181 by night. Six were proven together in cold run 9217 (0 "
    "interventions, 0 retries, findings 72 to 71 against 9213): notes 6 and 4 (Lot 0.102.1 and "
    "0.102.2), 3 (Deli Counter 0.204.1), 10 (Zoo 1.90.0), 9 (Level Factory 0.165.0) and 2 (Zoo "
    "1.91.0's drape, hung by Deli Counter 0.205.0). Note 1, the club's light, was proven in cold "
    "run 9218 (0 interventions, 0 retries, findings 71 to 71): Lux 0.72.0's wall washers and "
    "tinted fill. Mean and median luma at the room stations: the main floor 3.7 and 1 to 14.5 and "
    "8, the VIP wing 2.2 and 0 to 12.9 and 7, the bar 3.1 and 1 to 17.1 and 9 "
    "(`docs/cold_runs/cold_9218/`). Note 5 is FIXED and not yet run cold: Zoo 1.92.0 draws the box "
    "truck and the litter bin, and Lot 0.103.0 varies the trucks' fleets. Still the walker's: the "
    "brighter fill, and the club's office-tile ceiling. Next: a cold run of note 5; note 11, the "
    "bags; then the perimeter and the backdrop as a menu with frames. The moon waits on the "
    "walker.*"
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    lines = data.decode("utf-8").split("\n")
    for start, new in ((ROW, ROW_NEW), (STATUS, STATUS_NEW)):
        hits = [i for i, ln in enumerate(lines) if ln.startswith(start)]
        assert len(hits) == 1, (start[:50], len(hits))
        lines[hits[0]] = new
    ROADMAP.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 219: note 5 fixed in Zoo 1.92.0 and Lot 0.103.0, not yet run cold")


if __name__ == "__main__":
    main()
