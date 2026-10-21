"""The route census on the specs a Deli Counter clone changed (git status against its HEAD), with that checkout's
modules loaded first so `route_cost.py` measures it; and the same specs' rows out of the factory's census at 0.250.0
(`docs/findings/furnish_route_cost/route_cost.json`), summarised the same way. Writes <out>.json (the clone's rows).

    python census_changed.py <clone> <out.json>
"""
import json
import os
import subprocess
import sys

dc, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, dc)
import level_design  # noqa: E402,F401  -- the checkout's, before route_cost asks for it
import migrate_furnish_recipes  # noqa: E402,F401
import partition_bounds  # noqa: E402,F401
import stairwell  # noqa: E402,F401
import spec_types  # noqa: E402,F401
FIND = r"C:\Projects\gabagool_studios\gabagool_factory\docs\findings\furnish_route_cost"
sys.path.insert(0, FIND)
import route_cost as R  # noqa: E402

assert os.path.samefile(R.L.__file__, os.path.join(dc, "level_design.py")), R.L.__file__
changed = sorted(os.path.basename(l.split()[-1])[:-5] for l in subprocess.run(
    ["git", "-C", dc, "status", "--short", "specs"], capture_output=True, text=True, check=True).stdout.splitlines()
    if l.strip().endswith(".json"))
rows = []
for name in changed:
    d = json.load(open(os.path.join(dc, "specs", name + ".json"), encoding="utf-8"))
    rows.extend(R.measure_spec(d, name))
json.dump(rows, open(out, "w", encoding="utf-8"))
base = [r for r in json.load(open(os.path.join(FIND, "route_cost.json"), encoding="utf-8")) if r["spec"] in changed]
print("== %d specs the clone changed; the factory's census at 0.250.0 over the same specs" % len(changed))
print("\n".join(R.summarise(base)[:12]))
print()
print("== the clone")
print("\n".join(R.summarise(rows)[:40]))
