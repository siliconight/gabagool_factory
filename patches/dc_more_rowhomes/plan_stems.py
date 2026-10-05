"""Plan every built Deli Counter building through Zoo's own kit planner and
print what it would refuse: stem collisions (two geometries under one module
name, a failed `--build-kit` since Zoo 1.62.0) and slot materials outside
Zoo's kind vocabulary.

    python plan_stems.py [theme]          (default delco_1997)

Reads `deli_counter/build/*.slots.json` as built now, with the Zoo checked
out now. Prints counts and the offenders; names no cause.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "zoo"))
from zoo_keeper.core import kit  # noqa: E402

theme = sys.argv[1] if len(sys.argv) > 1 else "delco_1997"
files = sorted((ROOT / "deli_counter" / "build").glob("*.slots.json"))
if not files:
    print("NO SLOTS FILES under deli_counter/build -- nothing was planned")
    sys.exit(2)
n_coll = n_unknown = 0
modules = 0
for f in files:
    man = json.loads(f.read_text(encoding="utf-8"))
    plan = kit.plan_kit(man, theme=theme, style=1)
    if "stem_collisions" not in plan or "modules" not in plan:
        print("UNRECOGNISED PLAN for %s: keys %s" % (f.name, sorted(plan)))
        sys.exit(2)
    modules += len(plan["modules"])
    for c in plan["stem_collisions"]:
        n_coll += 1
        print("COLLISION %-40s %s x%d dims=%s" % (f.name, c["stem"], c["count"], c["dims"]))
    for u in plan.get("unknown_materials") or []:
        n_unknown += 1
        print("UNKNOWN   %-40s %s" % (f.name, u))
print("planned %d building(s), %d module(s), theme %s: %d stem collision(s), %d unknown material slot(s)"
      % (len(files), modules, theme, n_coll, n_unknown))
sys.exit(1 if (n_coll or n_unknown) else 0)
