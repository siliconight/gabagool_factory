"""Build `aisle_sign` in its `grocery` form in Blender, three variants, and print what each built. Run from a Zoo
checkout:

    blender -b --factory-startup --python <this> -- <out dir>

Prints each variant's mesh names, material names, and the recipe's own report line; draws no conclusion.
"""
import os
import sys

sys.path.insert(0, os.getcwd())
import bpy  # noqa: E402

from zoo_keeper.bpylayer import build as B  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

out = sys.argv[sys.argv.index("--") + 1]
for v in (0, 4, 11):
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    plan = kit.plan_kit({"building_id": "t", "slots": [{
        "slot_id": "aisle_sign_r00000000_%d" % v, "role": "prop", "size_mod": "full", "style": 1,
        "species": "aisle_sign", "form": "grocery", "variant": v,
        "fit": {"dims": [1.4, 0.06, 0.5], "pivot": "center"}}]}, theme="delco", style=1)
    m = plan["modules"][0]
    print("variant", v, "module", m["stem"], "params", m.get("params"), "fallbacks", plan["species_fallbacks"])
    B.build_module(m, os.path.join(out, m["stem"]), theme="delco", style=1, options={"save_blend": False})
    meshes = sorted(o.name for o in bpy.data.objects if o.type == "MESH")
    mats = sorted({s.material.name for o in bpy.data.objects if o.type == "MESH" for s in o.material_slots if s.material})
    print("  meshes", meshes)
    print("  materials", mats)
