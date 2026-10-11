"""Does the dome build the same whichever half the hemisphere helper keeps?

Run inside Blender, naming a Zoo root and an output JSON:

    blender -b --factory-startup --python docs/findings/hemisphere_half/dome_same_probe.py -- <zoo root> <out.json>

Plans one `dome_fixture` slot at the genome's default corner through `core.kit.plan_kit`, builds it
with `bpylayer.build.build_module` (the coplanar census's path), and writes, per visual mesh, its
vertex positions and its face centres with their normals, in Blender world space (Z up, metres),
rounded to 0.01 mm and sorted, so two runs compare as sets. It prints the counts and the glass's
mean face normal z and stops; the comparison of two outputs is the reader's.
"""
import json
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ROOT, OUT = os.path.abspath(argv[0]), argv[1]
sys.path.insert(0, ROOT)

import bpy  # noqa: E402

from zoo_keeper.bpylayer import build  # noqa: E402
from zoo_keeper.bpylayer.export import _COL_SUFFIXES  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
with open(os.path.join(ROOT, "zoo_keeper", "genome", "species", "dome_fixture.json"),
          encoding="utf-8") as f:
    g = json.load(f)
dims = [float(g["dimensions"][k]["default"]) for k in ("width", "depth", "height")]
slot = {"slot_id": "dome_0", "role": "prop", "size_mod": "full", "style": 1,
        "species": "dome_fixture", "fit": {"dims": dims, "pivot": "center"}}
mod = kit.plan_kit({"building_id": "dome_same", "slots": [slot]},
                   theme="delco_1997", style=1)["modules"][0]
build.build_module(mod, os.path.join(os.environ.get("TEMP", "."), "dome_same_out"),
                   theme="delco_1997", style=1, options={"save_blend": False})
out = {}
for o in bpy.context.scene.objects:
    if o.type != "MESH" or o.name.endswith(_COL_SUFFIXES) or "_LOD" in o.name:
        continue
    m = o.matrix_world
    rot = m.to_3x3()
    verts = sorted([round(c, 5) for c in (m @ v.co)] for v in o.data.vertices)
    faces = sorted([round(c, 5) for c in (m @ p.center)] + [round(c, 4) for c in (rot @ p.normal).normalized()]
                   for p in o.data.polygons)
    nz = sum(f[5] for f in faces) / max(1, len(faces))
    out[o.name] = {"verts": verts, "faces": faces}
    print("[same] %s: %d verts, %d faces, mean face normal z %+.4f" % (o.name, len(verts), len(faces), nz))
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f)
