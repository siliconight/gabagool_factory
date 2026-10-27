"""Does a longer baked fluorescent range light the gondola ends? Copies of the walker's walk preview, the
supermarket's 50 fluorescent rigs' `light_range` (4.85 m, the only rigs at that range) scaled in the copy's
`presentation/lux.applied.tscn` -- the value `lux_fluorescent_rig.gd` (`@tool`) rebuilds its lamps from at
`_ready`, in the editor's bake too -- and the saved lamps' `spot_range` with it, each re-baked with Level Factory's bake
(`tools/lux_rebake.py`) and shot at the gondola-end station and the walker's view.

    python docs/findings/black_gondola_ends/range_arm.py

The README's lead: the lamps are downward cones whose range is drop + 0.75 m (clamped 4.0-7.5), and the gondola's end
face looks toward the storefront from about 4.0 m off the one row on its side. ARMS:
  control   re-baked, nothing changed -- must reproduce the shipped frame, or no difference below is evidence
  r1.6      the range x 1.6
  r2.0      the range x 2.0
Each copy is deleted once shot. Writes `range_arm.out.json` and the frames under `_scratch/range_arm/`; draws no
conclusion.

SUPERSEDES `range_arm_loader.py` (`range_arm_loader.out.*`): that arm scaled `fluorescent_range` in the copy's
`runtime/lux/runtime/lux_light_loader.gd`, and all three arms read identically, because the bake does not call it --
the range is written into `lux.applied.tscn` when Lux applies the rig, and the re-bake loads that scene as saved. The range is also what a lamp claims realtime (per-object light slots) -- these arms price nothing.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[2]
SRC = F / "levels" / "restaurant_row" / "workspace" / ".level_factory" / "preview" / "restaurant_row_001_walk"
WORK = F / "_scratch" / "range_arm"
STATIONS = ["to_cooler:3.5,1.6,13.0,3.5,1.2,-8.0", "walker_sales:24.4,1.6,-6.8,0.0,1.2,-6.8"]
ARMS = {"control": None, "r1.6": 1.6, "r2.0": 2.0}
#: the black block's pixels in the 1600 x 900 to_cooler frame (the gondola end above its cap)
BLOCK = (620, 380, 800, 470)

sys.path.insert(0, str(F / "tools"))
import look_shots  # noqa: E402
from PIL import Image  # noqa: E402

OLDS = ("light_range = 4.85\n", "spot_range = 4.85\n")
out = {}
for arm, k in ARMS.items():
    staged = WORK / ("staged_" + arm)
    baked = WORK / ("baked_" + arm)
    for d in (staged, baked):
        if d.exists():
            shutil.rmtree(d)
    shutil.copytree(SRC, staged)
    if k is not None:
        applied = staged / "presentation" / "lux.applied.tscn"
        t = applied.read_bytes().decode("utf-8")
        for old in OLDS:
            assert t.count(old) == 50, ("the supermarket's lamps are not what they were", old, t.count(old))
            t = t.replace(old, old.replace("4.85", str(round(4.85 * k, 4))))
        applied.write_bytes(t.encode("utf-8"))
    r = subprocess.run([sys.executable, str(F / "tools" / "lux_rebake.py"), str(staged), str(baked)],
                       capture_output=True, text=True)
    shutil.rmtree(staged, ignore_errors=True)
    if r.returncode != 0:
        out[arm] = {"error": (r.stderr or r.stdout)[-400:]}
        print(arm, out[arm], flush=True)
        continue
    got = look_shots.shoot(str(baked), str(WORK / ("shots_" + arm)), stations=STATIONS, timeout=900)
    shots = {s["name"]: s for s in got.get("shots", [])}
    row = {n: [round(s["mean"], 1), s["p50"]] for n, s in shots.items() if n in ("to_cooler", "walker_sales")}
    if "to_cooler" in shots:
        im = Image.open(shots["to_cooler"]["png"]).convert("RGB")
        row["block_rgb"] = list(im.crop(BLOCK).resize((1, 1)).getpixel((0, 0)))
    out[arm] = row
    print(arm, row, flush=True)
    shutil.rmtree(baked, ignore_errors=True)
(HERE / "range_arm.out.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
