"""Every wall pack Deli Counter's built shells carry, counted by where it came from.

    python wall_pack_census.py [<deli_counter>]

Reads each `build/*.json` under Deli Counter (default: the sibling checkout),
walks it for objects whose `type` is `wall_pack`, and counts them by their
`source`. Deli Counter's `lights.py` derives one over each exterior door
(`_exterior_doors`), outside the wall by half its thickness plus
`_WALL_PACK_OUT`; a spec could also author one, which would read as another
source. Prints what it counted and stops.
"""
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def walk(o):
    if isinstance(o, dict):
        if o.get("type") == "wall_pack":
            yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def main():
    dc = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "deli_counter")
    by_source = collections.Counter()
    files = 0
    unreadable = []
    for p in sorted(glob.glob(os.path.join(dc, "build", "*.json"))):
        try:
            with open(p, encoding="utf-8") as fh:
                d = json.load(fh)
        except (OSError, ValueError):
            unreadable.append(os.path.basename(p))
            continue
        hit = list(walk(d))
        if hit:
            files += 1
        for a in hit:
            by_source[str(a.get("source"))] += 1
    print("build files carrying a wall pack: %d" % files)
    print("wall packs by source: %s" % dict(sorted(by_source.items())))
    print("unreadable build files: %d %s" % (len(unreadable), unreadable[:5]))


if __name__ == "__main__":
    main()
