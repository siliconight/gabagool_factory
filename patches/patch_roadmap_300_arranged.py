"""Roadmap 300 NARROWED (Deli Counter 0.263.0 hallways and 0.264.0 seeded pieces on a lattice with its census,
cold run 9386). Copied from `patch_roadmap_296_298_drawings.py`: the status block the paragraph directly above its
heading, asserted to be the one this was written against, replaced with one that keeps it after "Earlier status
kept:". The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_300_arranged.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUSES = [(300, '\n\n**300. Furniture is placed with no arrangement.** The walker, 2026-10-23, of deli_a03\'s stair landing: "layout of these tables doesn\'t seem to have a rhyme or reason". Read off Deli Counter (`docs/findings/walk_2026-10-23_deli/`, finding 3): no pass that places these pieces has a notion of arrangement. The landing, `upper_hall`, role `connector`, takes the gallery-and-chapel `hall` kind by its id\'s token (`level_design._room_kind`: id tokens before role, by design) and gets a service counter, benches, vending and a dining table; 45 connector rooms in the library resolve to that kind, nearly all `upper_hall` or `back_hall` -- hallways. Role alone cannot decide: `connector` covers 896 rooms, kitchens, offices and bars among them (2026-10-23 census). seed_cover lays shuffled first-fit pieces on a jittered grid, facing by coin flip; wall pieces at shuffled random spots; floor hosts first fit, facing away from the room\'s middle. Over 427 specs, 59 % of seed_cover\'s archetype pieces stand isolated. **What would close it:** a room a stair or ladder lands in is circulation first -- its landing kept clear and its kind not a seating hall; floor pieces laid in rows or against a wall by a rule a reader can state (desks in rows, wall runs packed from a corner); seed_cover\'s archetype pass retired where furnish runs; each step held to the route census (`route_cost.py`) and the walker\'s density band (2026-10-21: not crowded, not barren, 12-25 % floor share); a refurnish, since stored specs carry older furnishing; the walker\'s eye on a walk copy.', "*STATUS: OPEN 2026-10-23 -- the walker's walk of cold run 9383, finding 3; read, not started.*", '*STATUS: NARROWED 2026-10-23 -- the walker: "do the full correct fix, allowing us to have nuance and flavor, but not look like random assortment". Two steps shipped. Deli Counter 0.263.0 (0250b6ea, `patches/patch_dc_hallway.py`): a hall that names nothing else is a hallway, furnished on its walls -- 40 rooms in 38 specs lost their gallery sets, deli_a03\'s landing among them; routes over 10 % 26 -> 23 pairs. Deli Counter 0.264.0 (af649258, `patches/patch_dc_seed_lines.py`): `arrangement.py`, the first instrument for "reads as designed" (roadmap 18) -- each piece\'s visible reason, or loose -- and a room\'s seeded pieces on a lattice, one line or rows, one kind a row, each cleared by its own footprint and off the room\'s routes; seeded pieces loose 95.4 -> 13.8 % in fresh presets, which is what Level Factory builds a mission\'s shell from, 71.8 -> 3.8 % in the library; routes no worse. Cold run 9386 (0 interventions): the landing\'s frames before and after (`docs/findings/walk_2026-10-23_deli/landing_938[56]_*.png`). LEFT: floor hosts -- desks and tables, 258 rooms repeating one, a seeded desk with no chair -- laid in patterns with their chairs (prototyped, `_scratch/wip_dc_seed_lines/hosts_proto.py`); the lived-in touches on the order (`lived-in-touches`); the counter islands and planters rendering as plain boxes; the walker\'s eye on 9386. Earlier status kept: OPEN 2026-10-23 -- the walker\'s walk of cold run 9383, finding 3; read, not started.*')]


def main():
    raw = RM.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    for n, heading, old, new in STATUSES:
        if text.count(heading) != 1:
            raise SystemExit("REFUSED: %d's heading is not there once; nothing written" % n)
        h = text.find(heading)
        s = text.rindex("\n\n", 0, h) + 2
        if text[s:h] != old:
            raise SystemExit("REFUSED: %d's status block is not the one this was written against; nothing written" % n)
        text = text[:s] + new + text[h:]
        if text.count(new + heading) != 1:
            raise SystemExit("REFUSED: %d's status no longer adjoins its heading; nothing written" % n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 300 NARROWED; now roadmap_status.py --write / --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
