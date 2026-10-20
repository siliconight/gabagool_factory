"""The coincident-face census of `roof_hatch` in a named form -- `floor`, the hatch Deli Counter 0.236.0 lets into a
floor over a drop (Zoo 1.114.0, the factory's roadmap 265).

As census_forms.py beside it, for `roof_hatch` alone: `tools/coplanar_census.py`'s loop with every roof_hatch slot
carrying the form, at the genome's three corners (the stock census plans it at its default form). The modules land in
`_census_hatch/` beside the JSON. A probe: prints and stops.

    blender -b --factory-startup --python patches/zoo_hole_causes/census_hatch.py -- <out.json> floor

The repo is the factory's zoo/, or ZOO_REPO. The record beside this file: census_floor_hatch.json / .log.
"""
import json
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, FORMS = os.path.abspath(argv[0]), argv[1:]
REPO = os.environ.get("ZOO_REPO") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "zoo")
sys.path.insert(0, REPO)
sys.argv = [sys.argv[0], "--"]                      # the census's own parser sees no arguments

import bpy  # noqa: E402
import mathutils  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

ns = {"__name__": "coplanar_census_lib", "__file__": os.path.join(REPO, "tools", "coplanar_census.py")}
exec(compile(open(os.path.join(REPO, "tools", "coplanar_census.py"), encoding="utf-8").read(),
             "coplanar_census.py", "exec"), ns)
probe_mod = {"__name__": "coplanar_probe_lib", "__file__": os.path.join(REPO, "tools", "coplanar_probe.py")}
exec(compile(open(os.path.join(REPO, "tools", "coplanar_probe.py"), encoding="utf-8").read(),
             "coplanar_probe.py", "exec"), probe_mod)

_plan_kit = kit.plan_kit
current = {"form": None}


def plan_with_form(manifest, *a, **k):
    for slot in manifest.get("slots", []):
        if slot.get("species") == "roof_hatch":
            slot["form"] = current["form"]
    return _plan_kit(manifest, *a, **k)


kit.plan_kit = plan_with_form
rows = []
for form in FORMS:
    current["form"] = form
    print("[census] == form", form)
    out = ns["run"](bpy, mathutils, probe_mod, ["roof_hatch"], ["min", "default", "max"],
                    "delco_1997", 1, os.path.join(os.path.dirname(OUT), "_census_hatch"), 0.002, 1e-6, 1e-3)
    for r in out:
        r["form"] = form
    rows += out
bad = [r for r in rows if r.get("pairs")]
err = [r for r in rows if "error" in r]
print("[census] %d builds, %d with coincident pairs, %d that did not build" % (len(rows), len(bad), len(err)))
json.dump({"rows": rows}, open(OUT, "w", encoding="utf-8"), indent=1)
