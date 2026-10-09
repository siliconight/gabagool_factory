"""Each payphone form built the way a kit build builds it, read back out of its
GLB (Zoo 1.89.0, roadmap 210): the two atlases and the hood lamp's marker.

Run inside Blender, background, against a Zoo tree:

    C:\\blender\\blender.exe -b --factory-startup --python build_check.py -- <zoo root> <out dir>

For each form at the genome's min corner, the default slot (0.75 x 0.5 x 2.3
m) and its max corner: `kit.plan_kit` then `build.build_module`, as
`tests/test_payphone.py`'s Blender-gated test does. Prints, per build: the
stem, the validation status and any check that did not pass, the visual mesh
objects, and from the GLB its materials by name, meshes, primitives,
triangles by mesh, images, bytes, and every `LuxEmit_` node with its
translation (glTF, Y up, metres from the slot's centre) and extras. Prints
what it measured and stops. `docs/findings/payphone_redraw/build_check.py` is
1.88.0's, which this extends.
"""
import json
import os
import struct
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
ZOO, OUT = argv[0], os.path.abspath(argv[1])
sys.path.insert(0, ZOO)
os.makedirs(OUT, exist_ok=True)

import bpy  # noqa: E402
from zoo_keeper.bpylayer import build  # noqa: E402
from zoo_keeper.bpylayer.export import _COL_SUFFIXES  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

DIMS = {"min": [0.525, 0.35, 1.61], "default": [0.75, 0.5, 2.3], "max": [1.05, 0.7, 3.22]}


def glb_facts(path):
    raw = open(path, "rb").read()
    ln = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20:20 + ln])
    tris = {}
    for m in doc.get("meshes", []):
        n = 0
        for p in m["primitives"]:
            if "indices" in p:
                n += doc["accessors"][p["indices"]]["count"] // 3
        tris[m.get("name", "?")] = n
    markers = [{"name": n["name"], "translation": [round(c, 4) for c in n.get("translation", [0, 0, 0])],
                "extras": n.get("extras")}
               for n in doc.get("nodes", []) if n.get("name", "").startswith("LuxEmit")]
    return {"materials": [m.get("name") for m in doc.get("materials", [])],
            "meshes": len(doc.get("meshes", [])),
            "primitives": sum(len(m["primitives"]) for m in doc.get("meshes", [])),
            "tris": tris, "images": [im.get("uri") or im.get("name") for im in doc.get("images", [])],
            "bytes": len(raw), "markers": markers}


for form in ("booth", "pedestal", "wall"):
    for corner, dims in DIMS.items():
        slot = {"slot_id": "a", "role": "prop", "size_mod": "full", "style": 1, "species": "payphone",
                "material": "metal_painted", "form": form, "fit": {"dims": dims, "pivot": "center"}}
        plan = kit.plan_kit({"building_id": "check", "slots": [slot]}, theme="delco_1997", style=1)
        res = build.build_module(plan["modules"][0], OUT, theme="delco_1997", style=1,
                                 options={"save_blend": False})
        bad = [(c["id"], c["level"], c["msg"]) for c in res["report"]["checks"] if c["level"] != "pass"]
        objs = sorted(o.name for o in bpy.context.scene.objects
                      if o.type == "MESH" and not o.name.endswith(_COL_SUFFIXES))
        g = glb_facts(os.path.join(OUT, res["files"]["glb"]))
        print(f"[check] {form:8s} {corner:7s} {res['stem']} status={res['report']['status']} "
              f"objects={objs} glb={json.dumps(g)}" + (f" NOT_PASS={bad}" if bad else ""))
