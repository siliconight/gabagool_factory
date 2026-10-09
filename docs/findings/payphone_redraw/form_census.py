"""Coincident faces on every payphone form, read off the built meshes (Zoo
1.88.0, roadmap 210).

Run inside Blender, background, against a Zoo tree:

    C:\\blender\\blender.exe -b --factory-startup --python form_census.py -- <zoo root> <out dir>

`tools/coplanar_census.py` plans a slot with no form, so it sees only the
default (the booth). This builds each form at the genome's min, default and
max corners the way the census does (`kit.plan_kit`, then
`build.build_module`), and runs the census's own probe (`coplanar_probe.probe`,
loaded as the census loads it) over the visual meshes, at its defaults: within
2 mm, overlapping by at least 1 mm2, normals within 1e-3.

Prints, per build, the pairs and their facing, gap and overlap, then the
total. Prints what it measured and stops.
"""
import json
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
ZOO, OUT = argv[0], os.path.abspath(argv[1])
sys.path.insert(0, ZOO)
sys.path.insert(0, os.path.join(ZOO, "tools"))
os.makedirs(OUT, exist_ok=True)

import bpy  # noqa: E402
import mathutils  # noqa: E402
import coplanar_census as cc  # noqa: E402
from zoo_keeper.bpylayer import build  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

src = open(os.path.join(ZOO, "tools", "coplanar_probe.py"), encoding="utf-8").read()
probe_mod = {"__name__": "coplanar_probe_lib"}
exec(compile(src, "coplanar_probe.py", "exec"), probe_mod)

with open(os.path.join(ZOO, "zoo_keeper", "genome", "species", "payphone.json"), encoding="utf-8") as f:
    G = json.load(f)

total = 0
for form in ("booth", "pedestal", "wall"):
    for corner in ("min", "default", "max"):
        dims = cc._corner_dims(G, corner)
        cc._clear(bpy)
        slot = {"slot_id": "census", "role": "prop", "size_mod": "full", "style": 1, "species": "payphone",
                "form": form, "fit": {"dims": dims, "pivot": "center"}}
        plan = kit.plan_kit({"building_id": "form_census", "slots": [slot]}, theme="delco_1997", style=1)
        res = build.build_module(plan["modules"][0], OUT, theme="delco_1997", style=1,
                                 options={"save_blend": False})
        objs = probe_mod["_visual_meshes"](bpy, bpy.context.scene)
        pairs, ntris = probe_mod["probe"](bpy, mathutils, objs, 0.002, 1e-6, 1e-3, samples=3)
        total += len(pairs)
        print(f"[form_census] {form:8} {corner:7} {res['stem']}: {ntris} tris, {len(pairs)} pairs")
        for p in pairs:
            print(f"[form_census]    {p}")
print(f"[form_census] total pairs over 9 builds: {total}")
