"""Each payphone form built the way a kit build builds it, read back out of its
GLB (Zoo 1.88.0, roadmap 210).

Run inside Blender, background, against a Zoo tree:

    C:\\blender\\blender.exe -b --factory-startup --python build_check.py -- <zoo root> <out dir>

For each form at the default slot (0.75 x 0.5 x 2.3 m) and the genome's two
other corners: `kit.plan_kit` then `build.build_module`, as
`tests/test_payphone.py`'s Blender-gated test does. Prints, per build: the
stem, the validation status and any check that did not pass, the visual mesh
objects, and from the GLB its materials, meshes, primitives, triangles and
images, with each image's size. Prints what it measured and stops.
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
    tris = 0
    for m in doc.get("meshes", []):
        for p in m["primitives"]:
            if "indices" in p:
                tris += doc["accessors"][p["indices"]]["count"] // 3
    images = []
    for im in doc.get("images", []):
        images.append(im.get("uri") or im.get("name"))
    return {"materials": len(doc.get("materials", [])), "meshes": len(doc.get("meshes", [])),
            "primitives": sum(len(m["primitives"]) for m in doc.get("meshes", [])),
            "tris": tris, "images": images, "bytes": len(raw)}


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
        print(f"[check] {form:8} {corner:7} {res['stem']} status={res['report']['status']} "
              f"objects={objs} glb={g}")
        for b in bad:
            print(f"[check]    {b}")
