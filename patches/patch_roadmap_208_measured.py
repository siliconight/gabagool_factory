"""Roadmap 208 NARROWED: measured with the crew's whole body -- radius, floor
and step-up -- on the 18 distinct walk tests in the kept workspaces, and none
fails (docs/findings/walktest_crew_body/). The walk order stays open, and so
does whether the gate adopts the crew's body, which today would put out no
kept candidate.

Anchored on 208's status line (its unique opening, then to its line end) and
on the measure-first NEXT bullet; each must match exactly once, or nothing is
written.
"""
import pathlib
import sys

ROADMAP = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\PIPELINE_ROADMAP.md")

STATUS_HEAD = "*STATUS: OPEN 2026-10-07 -- measured, not fixed: `walktest_navqa`'s walker is a thinner body"
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-09 -- the body measured, the order open. The 18 distinct walk tests in the kept "
    "workspaces (cold-9193-ws to cold-9204-ws, four missions) re-walked from patched copies "
    "(`docs/findings/walktest_crew_body/rewalk.py`): `crew_body` (radius 0.35, floor 45 degrees) passes 18 of 18 "
    "(2026-10-08), and `crew_full` (that body with Laser Tag 0.24.0's step-up) passes 18 of 18 (2026-10-09), its "
    "own refusal strings in 12 walks' records and 110 of 312 walkers travelling differently -- the dial turned. "
    "The control reproduces the job exactly. Open: the mission's order (spawn, objective, extraction), which the "
    "director never walks, and whether the gate adopts the crew's body, which would put out no kept candidate "
    "today.*"
)

TAIL = ("- Measure first: re-walk the kept workspaces' candidates with the contract's body and count what fails, "
        "before it becomes the gate it already is.\n")
DONE = (
    "\n"
    "**MEASURED: THE CREW'S BODY FAILS NO KEPT CANDIDATE (2026-10-08 and 2026-10-09)** (finding "
    "`docs/findings/walktest_crew_body/`).\n"
    "- **What was walked.** The 18 distinct staged walk tests in cold-9193-ws to cold-9204-ws: restaurant_row_001, "
    "bank_block_001 (three Lot generations), gas_block_001 and club_block_014, all 36 recorded ok.\n"
    "- **How.** Patched copies of each, through `walktest.py`'s own steps and not its `main()`, whose `sync_addon` "
    "would copy the shipped director over the patch.\n"
    "  - **The control:** the copy unpatched reproduces the job, 158.2 simulated seconds against 158.2.\n"
    "- **`crew_body`, radius 0.35 and floor 45:** 18 of 18 pass.\n"
    "- **`crew_full`, that body with Laser Tag 0.24.0's step-up:** 18 of 18 pass.\n"
    "  - **The dial turned:** the crew step's own refusals are in 12 walks' records, and 110 of 312 walkers "
    "travelled differently from `crew_body`, by up to 2.50 m.\n"
    "- **What it says.** On these candidates none of the three leniencies -- the thin body, the steep floor, the "
    "teleport step-up -- passed geometry the crew cannot cross.\n"
    "  - *Retracted, kept:* the first `crew_body` run derived a 0.03 m waypoint radius for the wider body, and "
    "froze every walker. A body moves 0.067 m a frame, and the director's own 0.072 m was kept.\n"
    "\n"
    "**STILL OPEN.**\n"
    "- **The order.** The director walks home to each anchor and a chain through them, never spawn, objective, "
    "extraction. That is a director change to measure, not a variant of this one.\n"
    "- **The gate's body.** Moving the walker to the contract's body (`qa.walker_capsule_radius_m`, still read by "
    "nothing) and Laser Tag's step-up would put out no kept candidate today. Whether to make that change is now "
    "a question of what the gate should mean, not of what it would cost.\n"
)


def main():
    data = ROADMAP.read_bytes()
    if b"\r\n" in data:
        sys.exit("refusing: the roadmap has CRLF endings; it is LF")
    text = data.decode("utf-8")
    if text.count(STATUS_HEAD) != 1:
        sys.exit("refusing: 208's status opening matches %d times" % text.count(STATUS_HEAD))
    i = text.index(STATUS_HEAD)
    j = text.index("\n", i)
    if not text[i:j].endswith(".*"):
        sys.exit("refusing: 208's status line does not end its block on one line")
    text = text[:i] + NEW_STATUS + text[j:]
    if text.count(TAIL) != 1:
        sys.exit("refusing: 208's measure-first bullet matches %d times" % text.count(TAIL))
    text = text.replace(TAIL, TAIL + DONE)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 208 narrowed; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
