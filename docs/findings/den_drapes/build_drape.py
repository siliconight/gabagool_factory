"""Build one window_drape module GLB from a Zoo checkout, in Blender:

    blender -b --python build_drape.py -- <zoo_root> <out_dir> <w> <d> <h>

Prints the GLB's path. The slot is the den's: strip_club_a01's window, 1.2 m, plus 0.15 m a side.
"""
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
zoo, out = argv[0], argv[1]
w, d, h = (float(x) for x in argv[2:5])
sys.path.insert(0, zoo)

from zoo_keeper.bpylayer import build  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

slot = {"slot_id": "drape", "role": "prop", "size_mod": "full", "style": 1,
        "species": "window_drape", "material": "velvet",
        "fit": {"dims": [w, d, h], "pivot": "center"}}
plan = kit.plan_kit({"building_id": "drape_probe", "slots": [slot]}, theme="delco_1997", style=1)
os.makedirs(out, exist_ok=True)
res = build.build_module(plan["modules"][0], out, theme="delco_1997", style=1,
                         options={"save_blend": False})
print("DRAPE_GLB", os.path.join(out, res["files"]["glb"]))
