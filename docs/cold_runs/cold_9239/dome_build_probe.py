"""Build one dome_fixture module in Blender and report where its glass hangs against its canopy.

    blender -b --python docs/cold_runs/cold_9239/dome_build_probe.py -- <zoo root> <out dir>

Plans one `dome_fixture` slot at the genome default through `kit.plan_kit` and builds it with
`build.build_module`, the census's path, into <out dir>; then reads the built objects' world z
ranges and the glass's mean face normal z from the bmesh of each mesh object before export.
It prints what it measured and stops.
"""
import sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
root, out = argv[0], argv[1]
sys.path.insert(0, root)

import bpy  # noqa: E402

from zoo_keeper.core import kit  # noqa: E402
from zoo_keeper.bpylayer import build  # noqa: E402

plan = kit.plan_kit({"building_id": "probe", "slots": [{
    "slot_id": "dome_fixture_0", "role": "prop", "size_mod": "full", "style": 1,
    "species": "dome_fixture", "fit": {"dims": [0.3, 0.3, 0.11], "pivot": "center"}}]},
    theme="delco", style=1)
mod = plan["modules"][0] if isinstance(plan, dict) and "modules" in plan else plan[0]
res = build.build_module(mod, out, theme="delco", style=1, options={"save_blend": True})
print("[dome] built:", {k: res[k] for k in res if k in ("glb", "files", "tris")} if isinstance(res, dict) else res)
for obj in bpy.data.objects:
    if obj.type != "MESH" or not obj.name.startswith("Dome_"):
        continue
    zs = [(obj.matrix_world @ v.co).z for v in obj.data.vertices]
    obj.data.calc_normals_split() if hasattr(obj.data, "calc_normals_split") else None
    nz = sum(p.normal.z for p in obj.data.polygons) / max(1, len(obj.data.polygons))
    print("[dome] %-14s verts %4d faces %4d  z %.4f .. %.4f  mean face normal z %+.3f"
          % (obj.name, len(obj.data.vertices), len(obj.data.polygons), min(zs), max(zs), nz))
