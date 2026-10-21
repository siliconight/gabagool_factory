"""The parked car's measured matrix, again, with its history: coincident faces, fit and triangles over every body
style, size and history Zoo can build (Zoo 1.120.0, the factory's roadmap 44).

    blender -b --python car_matrix.py -- <zoo repo> <out.json> [--random N] [--seed S]

What `tests/test_car_forms.py`'s MEASURED was read from, rebuilt: every street style (`car_forms.STREET_STYLES`)
forced at the genome's min, default and max dims with slot style ints 1-8 -- 96 builds, each a BEATER, the history
that lays the most pieces -- and N builds at random slot sizes inside the genome's ranges (default 550), each a random
street style or `auto`, a random style int, and a random history or `auto`. Each is planned by `core.kit.plan_kit` and
built by `bpylayer.build.build_module`, the path a `zoo_kit_build` job takes, and probed by
`tools/coplanar_probe.probe` at its defaults (tol 2 mm, min_area 1 mm2, normal_tol 1e-3).

HOW A STYLE AND A HISTORY ARE FORCED: a module's params are the genome's defaults and its slot's dressing fields
(`dna.resolve_module_plan`), and neither `body_style` nor `history` is a dressing field. This wraps
`dna.resolve_module_plan` and sets both on the plan it returns -- a measurement's lever, not a path a level takes.

Writes one row a build -- the asked style, history and dims, the stem, the build's status and every check that did
not pass, the visual triangles and the coincident pairs -- and prints a summary. It names no cause.
"""
import json
import os
import random
import sys
import traceback

argv = sys.argv[sys.argv.index("--") + 1:]
repo, out_path = argv[0], argv[1]
n_random = int(argv[argv.index("--random") + 1]) if "--random" in argv else 550
seed = int(argv[argv.index("--seed") + 1]) if "--seed" in argv else 20261021
for p in (repo, os.path.join(repo, "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

import bpy  # noqa: E402
import mathutils  # noqa: E402

import coplanar_probe as CP  # noqa: E402
from zoo_keeper.bpylayer import build  # noqa: E402
from zoo_keeper import SEED_EPOCH  # noqa: E402
from zoo_keeper.core import car_forms, dna, genome as genome_mod, kit, seeding  # noqa: E402

FORCE = {}
_orig = dna.resolve_module_plan


def _forced(module, genome, theme, style, tool_version):
    plan = _orig(module, genome, theme, style, tool_version)
    plan["params"].update(FORCE)
    return plan


dna.resolve_module_plan = _forced

g = genome_mod.load_species("simple_car")
dims = {k: [g["dimensions"][a][k] for a in ("width", "depth", "height")] for k in ("min", "default", "max")}
cases = []
for body in car_forms.STREET_STYLES:
    for corner in ("min", "default", "max"):
        for s in range(1, 9):
            cases.append((body, "beater", dims[corner], s))
rng = random.Random(seed)
for _ in range(n_random):
    d = [round(rng.uniform(g["dimensions"][a]["min"], g["dimensions"][a]["max"]), 2)
         for a in ("width", "depth", "height")]
    cases.append((rng.choice(list(car_forms.STREET_STYLES) + ["auto"]),
                  rng.choice(["kept", "driven", "beater", "auto"]), d, rng.randint(1, 8)))

out_dir = os.path.join(os.path.dirname(os.path.abspath(out_path)), "_car_matrix_glb")
rows = []
for k, (body, hist, d, s) in enumerate(cases):
    FORCE.clear()
    FORCE.update({"body_style": body, "history": hist})
    row = {"k": k, "body_style": body, "history": hist, "dims": d, "style": s}
    try:
        plan = kit.plan_kit({"building_id": "car_matrix", "slots": [{
            "slot_id": "car_0", "role": "prop", "size_mod": "full", "style": s, "species": "simple_car",
            "fit": {"dims": d, "pivot": "center"}}]}, theme="delco_1997", style=s)
        res = build.build_module(plan["modules"][0], out_dir, theme="delco_1997", style=s,
                                 options={"save_blend": False})
        objs = CP._visual_meshes(bpy, bpy.context.scene)
        pairs, ntris = CP.probe(bpy, mathutils, objs, 0.002, 1e-6, 1e-3)
        # the recipe's own decisions, drawn again from the streams its stem seeds (`build.build_module`)
        form = car_forms.resolve(res["plan"], seeding.RNGStreams(
            seeding.root_key(res["stem"], "simple_car", 0, SEED_EPOCH)))
        row.update(stem=res["stem"], status=res["report"]["status"],
                   checks=[(c["id"], c["level"], c["msg"]) for c in res["report"]["checks"] if c["level"] != "pass"],
                   tris=ntris, pairs=len(pairs), pair_rows=[str(r)[:200] for r in pairs[:6]],
                   built_style=form.get("style"), built_history=form.get("history"))
    except Exception:
        row.update(error=traceback.format_exc()[-1500:])
    rows.append(row)
    if k % 50 == 0:
        print("[car_matrix] %d of %d" % (k, len(cases)), flush=True)

with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(rows, fh, indent=1)
errors = [r for r in rows if "error" in r]
bad = [r for r in rows if r.get("status") not in (None, "pass", "PASS") or r.get("checks")]
paired = [r for r in rows if r.get("pairs")]
tmax = {}
for r in rows:
    if "tris" in r:
        key = r.get("built_style")
        tmax[key] = max(tmax.get(key, 0), r["tris"])
print("[car_matrix] builds %d, errors %d, not passing %d, with coincident pairs %d" % (
    len(rows), len(errors), len(bad), len(paired)))
print("[car_matrix] largest visual tris by built style: %s" % json.dumps(tmax, sort_keys=True))
