#!/usr/bin/env python3
"""
migrate_bins_on_walls.py  --  the library's litter bins stand against a wall (0.266.0)
=====================================================================================
One-shot, idempotent migration over specs/*.json. The walker, walking cold run 9386: "garbage cans are usually up
against walls inside buildings". 0.266.0 makes `litter_bin` a wall piece and moves it out of five recipes' clusters
into their wall runs, so every room of those kinds -- and the corridors and hallways, whose wall runs named it all
along -- draws differently. Each spec holding such a room is stripped and refurnished
(`migrate_furnish_recipes.migrate`), and only those: the whole-library script would also refurnish the strip clubs,
whose furnishing is `migrate_club_rooms`'s. A strip club holding such a room is reported, not touched.

The shelter pass and the seeded lattice run after it (`migrate_shelter.py`, `migrate_seed_lines.py`), as a refurnish
always needs.

    python migrations/migrate_bins_on_walls.py            # write specs/
    python migrations/migrate_bins_on_walls.py --check    # report only
"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import level_design  # noqa: E402
import migrate_furnish_recipes  # noqa: E402

#: the kinds whose rooms draw differently: the five recipes that clustered the bin, and the two whose wall runs named it
KINDS = ("mechanical", "kitchen", "lobby", "hall", "shop_floor", "corridor", "hallway")


def affected(d):
    """The ids of the rooms in one spec of a kind whose draw 0.266.0 changes."""
    building = level_design.club_building_id(d)
    return [r["id"] for r in d.get("rooms") or []
            if r.get("bounds") and level_design._room_kind(r, building) in KINDS]


def main():
    check = "--check" in sys.argv
    specs = rooms = removed = added = 0
    clubs = []
    for p in sorted(glob.glob(os.path.join(ROOT, "specs", "*.json"))):
        name = os.path.basename(p)
        if name.startswith("lf_"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(d, dict) or not d.get("rooms"):
            continue
        hit = affected(d)
        if not hit:
            continue
        # `club_building_id` is the id a building's kind is read from, a string, not a yes or no
        if level_design._strip_club_building(level_design.club_building_id(d)):
            clubs.append((name, hit))
            continue
        before = json.dumps(d, sort_keys=True)
        r, a = migrate_furnish_recipes.migrate(d)
        specs += 1
        rooms += len(hit)
        removed += r
        added += a
        if not check and json.dumps(d, sort_keys=True) != before:
            io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=1) + "\n")
    for name, hit in clubs:
        print("  a strip club, not touched: %s %s" % (name, hit))
    print(f"[bins_on_walls] {specs} specs, {rooms} rooms of the changed kinds: -{removed} furnished volumes, "
          f"+{added} refurnished")


if __name__ == "__main__":
    main()
