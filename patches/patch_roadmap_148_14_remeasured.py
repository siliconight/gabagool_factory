"""Roadmap 148 NARROWED and 14 SUPERSEDED, re-measured 2026-10-15 (`docs/findings/open_items_remeasure/`).
Replaces each item's status block (each asserted once, from its first line to the line ending the block's `*`).
The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_148_14_remeasured.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [
    ("*STATUS: OPEN 2026-09-11 -- RAISED BY THE WALKER BEFORE THE RE-WALK; THE\nINTERIOR HALF OF LAYER 3, WHICH "
     "TODAY HAS ONLY AN EXTERIOR*",
     "\n\n**148. Nothing dresses the inside of a building: no posters, clocks, vents,\nsmoke detectors, garbage -- "
     "the non-collision layer that gives a room\ncharacter and depth.**",
     "*STATUS: NARROWED 2026-10-15 -- re-measured on cold run 9314's package and Zoo's recipes "
     "(`docs/findings/open_items_remeasure/`, `interior_dressing_148.py`). Of the ask's seven kinds, two exist as "
     "species -- posters (`poster`, `poster_wall`, on four wall kinds since 2026-10-02) and garbage (`litter_bin`, "
     "`litter_scrap`, `trash_bags`) -- and they reach rooms by Deli Counter's furnish recipes, a slot at a time: "
     "9314's deli carries 22 prop species including three poster walls and two litter bins, the pharmacy three "
     "poster walls and a bin, the office its desks, cabinets and machines and none of the asked kinds. Left: no "
     "species for a clock, a ceiling vent (`vent_stack` and `exhaust_fan` are roof pieces), a smoke detector, a "
     "light switch or an exit sign; interior litter is a bin, not a scatter; and the no-collision interior dressing "
     "LAYER this item names -- one MultiMesh over a room's walls and ceiling, placed by a rule on room roles -- is "
     "not built. Whether a room reads as inhabited is the walker's eye.*"),
    ("*STATUS: OPEN 2026-08-12 -- unchanged; re-measure after the first run on a level that has walls*",
     "\n\n**14. Seed 5017 has a collision trap the path query cannot see.**",
     "*STATUS: SUPERSEDED 2026-10-15 by 197 and 208 -- the site cannot be re-read and its class is gated. Seed 5017 "
     "is in no cold run's batch and no record names it; the lot-demo-era generators that built it are gone. What "
     "catches the class it named: Deli Counter 0.214.0 widens every walkable door to the agent contract's 1.25 m "
     "(197), and the walk test walks the crew's body over every leg of every candidate (208) -- cold run 9314 "
     "reads every path proof and every walker ok on all three candidates and Laser Tag's crew at 0 player-stuck "
     "events on each (`docs/findings/open_items_remeasure/`, `docs/cold_runs/cold_9314/`).*"),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    for old_head, heading, new in ITEMS:
        i = text.find(old_head)
        assert i >= 0 and text.count(old_head) == 1, ("status block not found once", old_head[:60])
        j = i
        while True:
            k = text.find("\n", j)
            assert k > 0
            if text[i:k].endswith("*"):
                break
            j = k + 1
        old = text[i:k]
        assert old.count("*STATUS:") == 1 and old.endswith("*"), old[-80:]
        assert text[k:].startswith(heading), ("the block does not end just above its heading", text[k:k + 80])
        text = text[:i] + new + text[k:]
        m = text.find(new)
        assert text[m + len(new):].startswith(heading), "status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 148 NARROWED, 14 SUPERSEDED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
