"""Roadmap: item 201, the score building is a seeded pick.

    python patch_roadmap_201.py

Appends after item 200, anchored on 200's last line as
patch_roadmap_200_mode.py left it (LF). Then run `tools/roadmap_status.py
--write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

TAIL = ("- Set the pacing `mode` from the brief (a heist's spawn -> objective -> extraction), with a test that the "
        "manifest's breakdown carries travel legs.\n")

ADD = """
*STATUS: OPEN 2026-10-07 -- found by the level standard's capability sweep and re-read in the code: `site_variation.site_placements` draws the spawn and the objective building independently from the seed (`ids[next(rng) % count]`, twice), so the score is not the archetype's building, not the one holding the objective rooms, and can be the spawn building itself.*

**201. The score building is a seeded pick.** Found 2026-10-07 writing `docs/LEVEL_STANDARD.md` (§4, and Part II's first item).

**WHAT THE CODE DOES.** `level_factory/packages/pipeline/site_variation.py::site_placements` returns `spawn`, `objective` and `extraction` building ids for Lot. The spawn and the objective are each `ids[next(rng) % count]` -- two independent draws -- and the extraction prefers a building other than the spawn. Nothing reads the brief's `archetype`, the lot library's anchor family, or which building's Deli Counter spec carries `objective_room`s or `Objective` records. Lot then puts the objective point at that building's first `objective` marker, else its first objective record, else its origin (`lot.py::_walk_positions`).

**WHY IT MATTERS.** A brief that asks for a bank job puts the bank on the site as the anchor family and then may point the heist at the row home beside it. Every level's score, approaches census and pacing estimate is computed against whichever building the seed drew. On cold run 9193's pick the draw happened to land on the deli (b0).

**NEXT.**
- Make the objective the building the brief asked for: the anchor family's building, or the one whose spec carries the objective rooms.
- Keep the spawn and extraction seeded, and never the objective's building.
- A test pins it, and a cold run of a library brief shows the score where the brief put it.
"""


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(TAIL) and text.count(TAIL) == 1, "the tail anchor is not the file's end"
    RM.write_bytes((text + ADD).encode("utf-8"))
    print("roadmap: 201 appended")


if __name__ == "__main__":
    main()
