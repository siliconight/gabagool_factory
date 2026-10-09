"""Two or more light-check reports of one level, station by station.

    python compare_checks.py <name>=<light_check.json>[#slot] <name>=<light_check.json>[#slot] [...] [--slot own]

Reads each `tools/light_check.py` report (`slots.<slot>.stations`, a list of
rows carrying `station`, `region`, `mean`, `p50`, `verdict`) and prints one row
a station: each report's frame mean, and each later report's difference from
the first. The numbers are luma after the grade (Rec.709, 0-255), so a
difference is how much brighter the FRAME got, not a share of the light.
Refuses a report without the slot, or one whose station list differs from the
first's: two different levels are not a comparison. A report's own `#slot`
(after its path) overrides `--slot`, so a light check's night re-bake can stand
beside another copy's own slot. Prints and stops.
"""
import json
import sys


def stations(path, slot):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    s = (d.get("slots") or {}).get(slot)
    if not isinstance(s, dict) or not isinstance(s.get("stations"), list):
        raise SystemExit("%s: no slots.%s.stations list" % (path, slot))
    return s.get("preset"), {r["station"]: r for r in s["stations"]}


def main(argv):
    slot = "own"
    if "--slot" in argv:
        i = argv.index("--slot")
        slot = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    named = []
    for a in argv:
        name, sep, path = a.partition("=")
        if not sep:
            raise SystemExit("want NAME=PATH, got %r" % a)
        named.append((name, path))
    if len(named) < 2:
        raise SystemExit("want two reports or more")
    data = []
    for n, p in named:
        path, _, own = p.partition("#")
        data.append((n,) + stations(path, own or slot))
    first = data[0][2]
    for n, _, rows in data[1:]:
        if set(rows) != set(first):
            raise SystemExit("%s: its stations differ from %s's" % (n, data[0][0]))
    print("slots: %s; presets: %s" % (", ".join("%s=%s" % (n, (p.partition("#")[2] or slot)) for n, p in named),
                                      ", ".join("%s=%s" % (n, pr) for n, pr, _ in data)))
    head = "%-36s %-8s" % ("station", "region") + "".join(" %9s" % n[:9] for n, _, _ in data)
    head += "".join(" %10s" % ("d " + n[:8]) for n, _, _ in data[1:])
    print(head)
    for k in first:
        line = "%-36s %-8s" % (k[:36], first[k].get("region", ""))
        line += "".join(" %9.1f" % rows[k]["mean"] for _, _, rows in data)
        line += "".join(" %+10.1f" % (rows[k]["mean"] - first[k]["mean"]) for _, _, rows in data[1:])
        print(line)


if __name__ == "__main__":
    main(sys.argv[1:])
