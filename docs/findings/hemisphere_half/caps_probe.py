"""Where does each `add_hemisphere` caller's cap sit, as a kit build builds it?

Run inside Blender, naming a Zoo root:

    blender -b --factory-startup --python docs/findings/hemisphere_half/caps_probe.py -- <zoo root> [corner]

For bollard, exhaust_fan, soda_cup, helmet and dome_fixture it plans one `prop` slot at the
genome's `default` corner (or the corner named) through `core.kit.plan_kit` and builds it with
`bpylayer.build.build_module` -- the coplanar census's path, theme delco_1997, style 1 -- and
prints, per visual mesh in Blender world space (Z up, metres): its z range, its triangle count,
its half-width about its own bounding-box axis, and the CROWN REACH -- the largest horizontal
distance from that axis of any vertex within 1 mm of the mesh's top. A dome's crown is its pole,
reach near 0; a flat top or a bowl's rim reaches the full radius. It prints what it measured and
stops.
"""
import json
import math
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT = os.path.abspath(argv[0] if argv else ".")
CORNER = argv[1] if len(argv) > 1 else "default"
sys.path.insert(0, ROOT)

import bpy  # noqa: E402

from zoo_keeper.bpylayer import build  # noqa: E402
from zoo_keeper.bpylayer.export import _COL_SUFFIXES  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

SPECIES = ("bollard", "exhaust_fan", "soda_cup", "helmet", "dome_fixture")
OUT = os.path.join(os.environ.get("TEMP", "."), "caps_probe_out")

print("[caps] root %s, corner %s" % (ROOT, CORNER))
for sp in SPECIES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with open(os.path.join(ROOT, "zoo_keeper", "genome", "species", sp + ".json"),
              encoding="utf-8") as f:
        g = json.load(f)
    dims = [float(g["dimensions"][k][CORNER]) for k in ("width", "depth", "height")]
    slot = {"slot_id": sp + "_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": sp, "fit": {"dims": dims, "pivot": "center"}}
    plan = kit.plan_kit({"building_id": "caps_probe", "slots": [slot]},
                        theme="delco_1997", style=1)
    mod = plan["modules"][0]
    build.build_module(mod, OUT, theme="delco_1997", style=1, options={"save_blend": False})
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"
            and not o.name.endswith(_COL_SUFFIXES) and "_LOD" not in o.name]
    allz = [(o.matrix_world @ v.co).z for o in objs for v in o.data.vertices]
    print("[caps] %s (built %s) dims %s: module z %+.4f .. %+.4f"
          % (sp, mod.get("species"), [round(v, 3) for v in dims], min(allz), max(allz)))
    for o in sorted(objs, key=lambda o: o.name):
        pts = [o.matrix_world @ v.co for v in o.data.vertices]
        xs, ys, zs = [p.x for p in pts], [p.y for p in pts], [p.z for p in pts]
        cx, cy, top = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(zs)
        half = max(max(xs) - cx, max(ys) - cy)
        reach = max(math.hypot(p.x - cx, p.y - cy) for p in pts if p.z > top - 1e-3)
        o.data.calc_loop_triangles()
        print("[caps]   %-28s z %+.4f .. %+.4f  tris %4d  half-width %.4f  crown reach %.4f"
              % (o.name, min(zs), top, len(o.data.loop_triangles), half, reach))
