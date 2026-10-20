"""The coincident-face census of Zoo's hole species, form by form (Zoo 1.114.0, the factory's roadmap 265).

`tools/coplanar_census.py`'s own build-and-probe loop, run once per form with every `hole_edge` and `hole_spoil` slot
carrying that form (the stock census, `tests/test_coincident_faces.py`'s 411 builds, plans each species at its default
form only), at the genome's min / default / max corners, theme delco_1997, style 1, the census's probe defaults (2 mm,
1e-6 m2, normal 1e-3). A `form:stock` token also sets the spoil's `stock` (its finish: `carpet`, `tile`) -- the
spoil's only: the edge takes none, and Zoo keeps a slot's dressing all or nothing (`kit.honour_dressing`), so a stock
on the edge builds the plain edge. The modules land in `_census_forms/` beside the JSON. A probe: prints and stops.

    blender -b --factory-startup --python patches/zoo_hole_causes/census_forms.py -- <out.json> <form>[:<stock>] ...

The repo is the factory's zoo/, or ZOO_REPO. Run on 2026-10-19 from the clone this release was proven in: the
records beside this file (census_forms_*.json / .log).
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
current = {"form": None, "stock": None}


def plan_with_form(manifest, *a, **k):
    for slot in manifest.get("slots", []):
        if slot.get("species") in ("hole_edge", "hole_spoil"):
            slot["form"] = current["form"]
            if current["stock"] and slot.get("species") == "hole_spoil":
                slot["stock"] = current["stock"]
    return _plan_kit(manifest, *a, **k)


kit.plan_kit = plan_with_form
rows = []
for token in FORMS:
    form, _sep, stock = token.partition(":")
    current["form"], current["stock"] = form, stock or None
    print("[census] == form", form, "stock", stock or "-")
    out = ns["run"](bpy, mathutils, probe_mod, ["hole_edge", "hole_spoil"], ["min", "default", "max"],
                    "delco_1997", 1, os.path.join(os.path.dirname(OUT), "_census_forms"), 0.002, 1e-6, 1e-3)
    for r in out:
        r["form"] = form
        r["stock"] = stock or None
    rows += out
bad = [r for r in rows if r.get("pairs")]
err = [r for r in rows if "error" in r]
print("[census] %d builds, %d with coincident pairs, %d that did not build" % (len(rows), len(bad), len(err)))
json.dump({"rows": rows}, open(OUT, "w", encoding="utf-8"), indent=1)
