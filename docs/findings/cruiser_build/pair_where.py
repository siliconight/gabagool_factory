"""Where the cruiser's coincident pairs are: the census's build path, with each
pair's sample points printed (Blender world, Z up, metres, after re-centring).

    blender -b --python pair_where.py -- <zoo repo> <W> <D> <H>
"""
import json
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
repo, dims = argv[0], [float(v) for v in argv[1:4]]
sys.path.insert(0, repo)
import bpy  # noqa: E402
import mathutils  # noqa: E402
from zoo_keeper.bpylayer import build  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

src = open(os.path.join(repo, "tools", "coplanar_probe.py"), encoding="utf-8").read()
probe_mod = {"__name__": "coplanar_probe_lib"}
exec(compile(src, "coplanar_probe.py", "exec"), probe_mod)

bpy.ops.wm.read_factory_settings(use_empty=True)
slot = {"slot_id": "cruiser_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "cruiser", "fit": {"dims": dims, "pivot": "center"}}
plan = kit.plan_kit({"building_id": "pair_where", "slots": [slot]}, theme="delco_1997", style=1)
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "pair_where")
os.makedirs(out_dir, exist_ok=True)
build.build_module(plan["modules"][0], out_dir, theme="delco_1997", style=1, options={"save_blend": False})
objs = probe_mod["_visual_meshes"](bpy, bpy.context.scene)
rows, ntris = probe_mod["probe"](bpy, mathutils, objs, 0.002, 1e-6, 1e-3, samples=4)
print("[where] %d tris, %d pairs, dims %s" % (ntris, len(rows), dims))
for o in objs:
    if o.name.startswith(("Cruiser", "Car_Interior")):
        bb = [o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
        lo = [min(v[i] for v in bb) for i in range(3)]
        hi = [max(v[i] for v in bb) for i in range(3)]
        print("[where] bounds %-22s lo %s hi %s" % (o.name, ["%.3f" % v for v in lo], ["%.3f" % v for v in hi]))
for r in rows:
    print("[where] %s gap %.2f mm  %.2f cm2  n=%s  %s <-> %s" % (
        r["facing"], r["gap_mm"], r["overlap_m2"] * 1e4, r["normal_of_a"], r["a"], r["b"]))
    for p in r.get("samples", []):
        print("[where]      at (%.3f, %.3f, %.3f)" % tuple(p))
