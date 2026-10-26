"""Which change lights the supermarket's sales floor: re-bake copies of the walked preview, one change each, and shoot
the same stations.

    python docs/findings/walk_2026-10-26_panel/sales_floor_rebake.py

ARMS (each a copy re-baked by tools/lux_rebake.py, Level Factory's own bake):
  control      nothing changed -- must reproduce the shipped frame, or no difference below is evidence
  texel2       the LightmapGI's texel_scale 2 (Level Factory leaves Godot's 1.0)
  fill2        the preset's bake_room_fill 0.05 (Blue Hour uses the default 0.025)
plus `shipped`, the preview as walked, shot without a re-bake.

STATIONS (Godot metres, eye then target): the walker's view down the sales floor, and a view down the back stock
(the bright room next door) as the reference. Prints frame mean and p50 per arm and station; draws no conclusion.
Each copy is deleted once shot (each is a few hundred MB). Writes `sales_floor_rebake.out.json` beside itself.
"""
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[2]
SRC = F / "levels" / "restaurant_row" / "workspace" / ".level_factory" / "preview" / "restaurant_row_001_walk"
WORK = F / "_scratch" / "sales_floor_rebake"
STATIONS = ["walker_sales:24.4,1.6,-6.8,0.0,1.2,-6.8", "back_stock:22.0,1.6,-13.0,0.0,1.2,-13.0"]
ARMS = {"control": [], "texel2": ["--texel-scale", "2"], "fill2": ["--set", "bake_room_fill=0.05"]}

sys.path.insert(0, str(F / "tools"))
import look_shots  # noqa: E402


def shoot(project, out):
    r = look_shots.shoot(str(project), str(out), stations=STATIONS, timeout=900)
    return {s["name"]: {"mean": round(s["mean"], 1), "p50": s["p50"]} for s in r.get("shots", [])
            if s.get("name") in ("walker_sales", "back_stock")}


results = {"shipped": shoot(SRC, WORK / "shots_shipped")}
print("shipped", results["shipped"], flush=True)
for arm, extra in ARMS.items():
    dest = WORK / ("copy_" + arm)
    if dest.exists():
        shutil.rmtree(dest)
    done = subprocess.run([sys.executable, str(F / "tools" / "lux_rebake.py"), str(SRC), str(dest), *extra],
                          capture_output=True, text=True)
    line = (done.stdout.strip().splitlines() or ["(no output)"])[-1]
    if done.returncode != 0:
        results[arm] = {"error": "lux_rebake exited %d: %s" % (done.returncode, (done.stderr or line)[-400:])}
    else:
        results[arm] = dict(shoot(dest, WORK / ("shots_" + arm)), bake=line[:300])
    print(arm, results[arm], flush=True)
    shutil.rmtree(dest, ignore_errors=True)
(HERE / "sales_floor_rebake.out.json").write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
