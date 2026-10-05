"""Count Patina dressing orders per building and cover kind, across runs.

    python cover_census.py 9152 9153 [9154]

Reads each run's `gas_block_001.patina_dressing.<building>/out/*.dressing.json`
(Patina's own output, the orders Zoo builds covers from). Prints a table of
gutter_run and downspout per building per run, plus every cover kind's total.
Fails on a file without `orders`.
"""
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory\workspaces")

runs = sys.argv[1:]
table = {}
kinds_all = set()
for run in runs:
    jobs = ROOT / f"cold-{run}-ws" / ".level_factory" / "jobs"
    for d in sorted(jobs.glob("gas_block_001.patina_dressing.*")):
        b = d.name.split(".", 2)[2]
        files = list((d / "out").glob("*.dressing.json"))
        if len(files) != 1:
            raise SystemExit(f"{d}: {len(files)} dressing.json files")
        doc = json.loads(files[0].read_text(encoding="utf-8"))
        if "orders" not in doc:
            raise SystemExit(f"{files[0]}: no 'orders' key: {sorted(doc)}")
        c = collections.Counter(o["cover"] for o in doc["orders"])
        table[(run, b)] = c
        kinds_all |= set(c)

buildings = sorted({b for _, b in table})
print("per building, gutter_run / downspout / all orders:")
print("  %-24s" % "building" + "".join("%18s" % r for r in runs))
for b in buildings:
    cells = []
    for r in runs:
        c = table.get((r, b))
        cells.append("%18s" % ("-" if c is None else
                               "%d / %d / %d" % (c["gutter_run"], c["downspout"], sum(c.values()))))
    print("  %-24s" % b + "".join(cells))
print()
print("totals by cover kind:")
for k in sorted(kinds_all):
    print("  %-16s" % k + "".join("%10d" % sum(table[(r, b)][k] for b in buildings if (r, b) in table)
                                   for r in runs))
