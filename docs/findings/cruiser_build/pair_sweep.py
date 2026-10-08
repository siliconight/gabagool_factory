"""The cruiser's coincident pairs BETWEEN the genome's corners: every height
from min to max at 1 cm, at the lowest, default and highest width and depth,
through the census's build path and the probe's defaults.

    blender -b --python pair_sweep.py -- <zoo repo> [--livery black_white|white_blue]

Prints one line a build, then each pair a build found, and a total. Prints
what it measured and stops.
"""
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
repo = argv[0]
livery = argv[argv.index("--livery") + 1] if "--livery" in argv else "black_white"
sys.path.insert(0, repo)
import bpy  # noqa: E402
import mathutils  # noqa: E402
from zoo_keeper.bpylayer import build  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

src = open(os.path.join(repo, "tools", "coplanar_probe.py"), encoding="utf-8").read()
probe_mod = {"__name__": "coplanar_probe_lib"}
exec(compile(src, "coplanar_probe.py", "exec"), probe_mod)
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "pair_sweep")
os.makedirs(out_dir, exist_ok=True)

builds = with_pairs = failed = 0
for wd in ((2.1, 5.35), (2.196, 5.545), (2.3, 5.75)):
    for i in range(17):
        h = round(1.50 + 0.01 * i, 3)
        dims = [wd[0], wd[1], h]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        slot = {"slot_id": "cruiser_0", "role": "prop", "size_mod": "full", "style": 1,
                "species": "cruiser", "form": livery,
                "fit": {"dims": dims, "pivot": "center"}}
        builds += 1
        try:
            plan = kit.plan_kit({"building_id": "pair_sweep", "slots": [slot]}, theme="delco_1997", style=1)
            mod = plan["modules"][0]
            build.build_module(mod, out_dir, theme="delco_1997", style=1, options={"save_blend": False})
        except Exception as exc:                          # recorded, not hidden
            failed += 1
            print("[sweep] %s: ERROR %s: %s" % (dims, type(exc).__name__, exc))
            continue
        objs = probe_mod["_visual_meshes"](bpy, bpy.context.scene)
        rows, ntris = probe_mod["probe"](bpy, mathutils, objs, 0.002, 1e-6, 1e-3, samples=1)
        with_pairs += bool(rows)
        # the livery the recipe drew is its own "[cruiser] livery=" line; the
        # outputs beside this file also print "form None" here, read from the
        # module's params, where a slot's form does not live
        print("[sweep] %s %s: %d tris, %d pairs" % (dims, livery, ntris, len(rows)))
        for r in rows:
            print("[sweep]     %s gap %.2f mm %.2f cm2 n=%s %s <-> %s at %s" % (
                r["facing"], r["gap_mm"], r["overlap_m2"] * 1e4, r["normal_of_a"], r["a"], r["b"],
                ["%.3f" % c for c in (r.get("samples") or [[0, 0, 0]])[0]]))
print("[sweep] %d builds, %d with coincident pairs, %d that did not build" % (builds, with_pairs, failed))
