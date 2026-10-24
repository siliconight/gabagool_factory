"""Build a doorway, an intact and a breached breach panel and a plain wall in the repo this runs from, and print each
exported GLB's meshes and primitives -- a primitive is a submission once placed. Run inside Blender from a zoo checkout:

    blender -b --factory-startup --python <this> -- <out dir>

Prints `GLB <stem> meshes <n> primitives <n> <mesh names>`. Measurements only.
"""
import glob
import json
import os
import struct
import sys

sys.path.insert(0, os.getcwd())
import bpy  # noqa: E402
from zoo_keeper.bpylayer import build as B  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

out = sys.argv[sys.argv.index("--") + 1]
BREACH = {"interactive": {"id": "t:if:1", "kind": "breach_wall", "states": ["intact", "breached"], "default": "intact",
                          "state_geometry": {"intact": "wall", "breached": "breach"},
                          "collision_per_state": {"intact": True, "breached": False}}}
slots = []
for role, extra in (("doorway", None), ("breach", BREACH), ("wall", None)):
    s = {"slot_id": role, "role": role, "size_mod": "full", "style": 1, "material": "concrete",
         "material_in": "drywall",
         "fit": {"dims": [1.4, 0.3, 3.1], "pivot": "center", "collision": "convex",
                 "openings": [{"kind": "door", "width": 1.0, "height": 2.2, "sill": 0.0}] if role == "doorway" else []}}
    s.update(extra or {})
    slots.append(s)
for m in kit.plan_kit({"building_id": "t", "slots": slots}, theme="delco_1997", style=1)["modules"]:
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    d = os.path.join(out, m["stem"])
    B.build_module(m, d, theme="delco_1997", style=1, options={"save_blend": False})
    for g in glob.glob(os.path.join(d, "**", "*.glb"), recursive=True):
        raw = open(g, "rb").read()
        n = struct.unpack_from("<I", raw, 12)[0]
        js = json.loads(raw[20:20 + n])
        meshes = js.get("meshes", [])
        print("GLB %s meshes %d primitives %d %s" % (os.path.basename(g), len(meshes),
                                                      sum(len(x["primitives"]) for x in meshes),
                                                      sorted(x.get("name", "") for x in meshes)))
