"""Which station-headings' draw counts differ between two price reports, and by how much -- to tell a package's change
from the run-to-run flicker two runs of one package show.

    python docs/cold_runs/cold_9355/draw_flicker.py <a.json> <b.json> [<a2.json> <b2.json> ...]

Reads `level_factory.perf_stations.v1` reports; refuses another shape. Prints each differing heading with both counts.
"""
import json
import sys


def draws(path):
    r = json.load(open(path, encoding="utf-8"))
    if r.get("schema") != "level_factory.perf_stations.v1":
        raise SystemExit("UNRECOGNISED: %s is %r" % (path, r.get("schema")))
    return {(row["station"], float(h["yaw"])): int(h["draws"]) for row in r["rows"] for h in row["headings"]}


args = sys.argv[1:]
for a, b in zip(args[::2], args[1::2]):
    da, db = draws(a), draws(b)
    if set(da) != set(db):
        raise SystemExit("the two reports' stations differ: %s, %s" % (a, b))
    diff = sorted(k for k in da if da[k] != db[k])
    print("%s -> %s: %d of %d headings differ, %+d draws in all" % (a.split("/")[-1], b.split("/")[-1], len(diff),
                                                                  len(da), sum(db.values()) - sum(da.values())))
    for k in diff:
        print("    %-22s %5.0f  %5d -> %5d  (%+d)" % (k[0], k[1], da[k], db[k], db[k] - da[k]))
