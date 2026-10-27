"""NULL, KNOB NOT READ (kept as the record; `range_arm.py` replaced it). Does a longer baked fluorescent range light the gondola ends? Copies of the walker's walk preview, Lux's
`fluorescent_range` scaled in the copy's own `runtime/lux`, each re-baked with Level Factory's bake
(`tools/lux_rebake.py`) and shot at the gondola-end station and the walker's view.

    python docs/findings/black_gondola_ends/range_arm.py

The README's lead: the lamps are downward cones whose range is drop + 0.75 m (clamped 4.0-7.5), and the gondola's end
face looks toward the storefront from about 4.0 m off the one row on its side. ARMS:
  control   re-baked, nothing changed -- must reproduce the shipped frame, or no difference below is evidence
  r1.6      the range x 1.6
  r2.0      the range x 2.0
Each copy is deleted once shot. Writes `range_arm.out.json` and the frames under `_scratch/range_arm/`; draws no
conclusion. The range is also what a lamp claims realtime (per-object light slots) -- these arms price nothing.
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

OLD = "\treturn clampf(to_floor + 0.75, 4.0, 7.5)\n"
out = {}
for arm, k in ARMS.items():
    staged = WORK / ("staged_" + arm)
    baked = WORK / ("baked_" + arm)
    for d in (staged, baked):
        if d.exists():
            shutil.rmtree(d)
    shutil.copytree(SRC, staged)
    if k is not None:
        loader = staged / "runtime" / "lux" / "runtime" / "lux_light_loader.gd"
        t = loader.read_text(encoding="utf-8")
        assert t.count(OLD) == 1, "the range rule is not where it was"
        loader.write_text(t.replace(OLD, "\treturn clampf(to_floor + 0.75, 4.0, 7.5) * %s\n" % k), encoding="utf-8")
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
(HERE / "range_arm_loader.out.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
