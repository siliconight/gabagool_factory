"""Is the dressing standing in space a player walks through?

WHAT THIS IS FOR. The keep-out rule that shipped covers OPENINGS -- the lane
you walk or shoot through a door or window. It does not cover room interiors,
and the reason it does not is a measurement that was taken and misread:

    room bounds, raw   ->  1034 of 2098 orders flagged (603 of 1315 panels)

That was read as "the rule is unworkable" and the rule was dropped. It was not
unworkable. A room's bounds run to the WALL, and every facade cover sits on
that wall, so a raw box flags the entire dressing pass by construction. The
number was measuring the wall, not an intrusion.

`openings.room_boxes` shrinks the room by the wall's own half-thickness plus
the deepest a cover stands proud, which puts flat-mounted covers outside the
box and leaves only what genuinely sticks into the floor space. This tool is
here to check that BEFORE the rule is wired into anything, because the last
one was wired on reasoning and had to be un-wired.

    python tools\\room_intrusion.py <building>.slots.json [--seed 1999]

WHAT THE NUMBER MEANS. A handful of orders, concentrated in `pilaster` and
`panel_field` on interior-facing slots, is the defect you saw in the walk: a
free-standing rod on a floor. Half the dressing flagged again means the inset
is still wrong and the rule is still not ready -- and the honest response is
to say so rather than ship it and call the count a finding.

WHAT IT DOES NOT DO. It does not modify anything. It regenerates the orders
from the manifest the same way the pipeline does, so it measures intent rather
than a built GLB -- which is the right level for a placement rule, and the
wrong level for asking whether the geometry actually landed there.

WHAT A NONZERO EXIT MEANS. The manifests could not be read. An intrusion is a
finding and exits 0; a failure to measure is not, and exits 2.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.dirname(HERE)
for cand in (os.path.join(FACTORY, "patina"),):
    if os.path.isdir(cand) and cand not in sys.path:
        sys.path.insert(0, cand)


def sibling(path, suffix):
    """`<stem>.slots.json` -> `<stem>.<suffix>`, the DC naming convention."""
    base = path[:-len(".slots.json")] if path.endswith(".slots.json") else path
    return base + "." + suffix


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slots_json")
    ap.add_argument("--gameplay", default=None,
                    help="default: the sibling <stem>.gameplay.json")
    ap.add_argument("--seed", type=int, default=1999)
    ap.add_argument("--list", type=int, default=12,
                    help="how many offending orders to name (0 = none)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        from patina import framing, openings, paneling, slots, trim
    except ImportError as exc:
        sys.stderr.write("cannot import patina (%s). Run from the factory "
                         "root so patina/ is a sibling.\n" % exc)
        return 2

    gp_path = args.gameplay or sibling(args.slots_json, "gameplay.json")
    try:
        with open(args.slots_json, encoding="utf-8") as fh:
            manifest = slots.parse(json.load(fh))
        with open(gp_path, encoding="utf-8") as fh:
            gameplay = json.load(fh)
    except (OSError, ValueError, KeyError) as exc:
        sys.stderr.write("unreadable: %s\n" % exc)
        return 2

    _, regions = trim.build_sheet(size=64, seed=args.seed)
    orders = (paneling.panel_orders(manifest, regions, seed=args.seed)
              + framing.pilaster_orders(manifest, regions, seed=args.seed)
              + framing.gutter_orders(manifest, regions, seed=args.seed))

    boxes = openings.room_boxes(manifest, gameplay)
    rooms = len((gameplay or {}).get("rooms") or [])

    by_family = {}
    offenders = []
    for o in orders:
        fam = o.get("cover", "?")
        by_family.setdefault(fam, [0, 0])
        by_family[fam][0] += 1
        hit = openings.hits(o, boxes)
        if hit:
            by_family[fam][1] += 1
            offenders.append({"cover": fam, "slot_id": o.get("slot_id"),
                              "pos": o.get("pos"),
                              "rooms": [h["slot_id"] for h in hit]})

    total = len(orders)
    flagged = len(offenders)
    if args.json:
        print(json.dumps({"orders": total, "flagged": flagged,
                          "rooms": rooms, "boxes": len(boxes),
                          "by_family": by_family,
                          "offenders": offenders}, indent=2))
        return 0

    print("=" * 64)
    print(os.path.basename(args.slots_json))
    print("  %d rooms in gameplay.json -> %d keep-out boxes after inset"
          % (rooms, len(boxes)))
    print()
    print("%-16s %8s %9s %8s" % ("cover", "orders", "in a room", "pct"))
    for fam, (n, bad) in sorted(by_family.items(), key=lambda kv: -kv[1][1]):
        print("%-16s %8d %9d %7.1f%%"
              % (fam, n, bad, 100.0 * bad / n if n else 0.0))
    print("%-16s %8d %9d %7.1f%%"
          % ("TOTAL", total, flagged, 100.0 * flagged / total if total else 0.0))
    print()
    if not boxes:
        print("NO KEEP-OUT BOXES: every room inset to nothing, or gameplay.json "
              "carries no rooms. Nothing was measured.")
    elif flagged == 0:
        print("No order stands in a room interior.")
    else:
        for o in offenders[:args.list]:
            print("  %-14s %-22s at %s  in %s"
                  % (o["cover"], o["slot_id"], o["pos"],
                     ", ".join(o["rooms"])))
        if flagged > args.list > 0:
            print("  ... and %d more" % (flagged - args.list))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
