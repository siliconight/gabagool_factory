"""Which fixture species carry two or more visual parts in one material?

Run inside Blender, naming a Zoo root:

    blender -b --factory-startup --python docs/findings/fixture_merge/parts_probe.py -- <zoo root>

For every species in `core.fixtures.FIXTURES` it plans one `prop` slot at the genome's `default`
corner through `core.kit.plan_kit` and builds it with `bpylayer.build.build_module` (the coplanar
census's path, theme delco_1997, style 1), then prints each visual mesh the recipe left in the
scene -- name, the materials on its faces, triangles -- and, per species, the meshes and the
distinct materials among them. A fixtures GLB exports every part as its own mesh, so meshes minus
materials is the submissions one placement of that species could shed by a merge inside it. It
prints what it measured and stops.
"""
import json
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT = os.path.abspath(argv[0] if argv else ".")
sys.path.insert(0, ROOT)

import bpy  # noqa: E402

from zoo_keeper.bpylayer import build  # noqa: E402
from zoo_keeper.bpylayer.export import _COL_SUFFIXES  # noqa: E402
from zoo_keeper.core import fixtures, kit  # noqa: E402

OUT = os.path.join(os.environ.get("TEMP", "."), "fixture_parts_out")
species = sorted({row["species"] for row in fixtures.FIXTURES.values()})
print("[parts] root %s: %d species" % (ROOT, len(species)))
for sp in species:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with open(os.path.join(ROOT, "zoo_keeper", "genome", "species", sp + ".json"),
              encoding="utf-8") as f:
        g = json.load(f)
    dims = [float(g["dimensions"][k]["default"]) for k in ("width", "depth", "height")]
    slot = {"slot_id": sp + "_0", "role": "prop", "size_mod": "full", "style": 1,
            "species": sp, "fit": {"dims": dims, "pivot": "center"}}
    mod = kit.plan_kit({"building_id": "parts_probe", "slots": [slot]},
                       theme="delco_1997", style=1)["modules"][0]
    build.build_module(mod, OUT, theme="delco_1997", style=1, options={"save_blend": False})
    objs = sorted((o for o in bpy.context.scene.objects if o.type == "MESH"
                   and not o.name.endswith(_COL_SUFFIXES) and "_LOD" not in o.name),
                  key=lambda o: o.name)
    mats = set()
    for o in objs:
        me = o.data
        me.calc_loop_triangles()
        used = sorted({me.materials[p.material_index].name if me.materials and me.materials[p.material_index] else "-"
                       for p in me.polygons})
        mats.update(used)
        print("[parts]   %-16s %-24s tris %4d  materials %s" % (sp, o.name, len(me.loop_triangles), ", ".join(used)))
    print("[parts] %s: %d meshes, %d materials, %d a placement could shed"
          % (sp, len(objs), len(mats), len(objs) - len(mats)))
