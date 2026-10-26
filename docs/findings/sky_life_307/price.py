"""PRICE roadmap 307's sky life: draw calls and frame time at fixed stations, every arm in one session (`CLAUDE.md`;
prices drift between sessions). Copied from `docs/cold_runs/cold_9391/price.py`; its arms changed.

    python docs/findings/sky_life_307/price.py

Arms, each a fresh copy of a WALK COPY with its import cache removed and re-imported:
  * ``ctrl`` and ``ctrl2`` -- cold run 9391's walk copy, twice: the control, whose spread is the instrument's;
  * ``sky`` -- 9391's with the flock and the airliner ON THE CLOCK (`proto_sky.py`, no pin; `_scratch/sky_clock`):
    most of the time both are collapsed to a point, and their bounds hold every camera, so what this prices is their
    standing cost -- submitted at every heading whether or not anything is in the sky.
Stations are the package's own (`gameplay_anchors.json`). Reports go to price_<arm>.json beside this file via Level
Factory's `tools/perf_stations_run.py` (windowed); each copy is deleted once its report exists.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
ARMS = (("ctrl", ROOT / "_runs" / "walk_9391_restaurant_row_001"),
        ("sky", ROOT / "_scratch" / "sky_clock"),
        ("ctrl2", ROOT / "_runs" / "walk_9391_restaurant_row_001"))
for arm, src in ARMS:
    assert (src / "gameplay_anchors.json").is_file(), src
    dst = ROOT / "_runs" / "perf_inner" / ("price307_" + arm)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    shutil.rmtree(dst / ".godot", ignore_errors=True)
    r = subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"], capture_output=True, text=True,
                       timeout=1800)
    print(arm, "import", r.returncode, flush=True)
    r = subprocess.run([sys.executable, str(ROOT / "level_factory" / "tools" / "perf_stations_run.py"), str(dst),
                        "--json", str(HERE / ("price_" + arm + ".json"))], capture_output=True, text=True,
                       timeout=3600, cwd=str(ROOT / "level_factory"))
    (HERE / ("price_" + arm + ".out.txt")).write_text(r.stdout + r.stderr, encoding="utf-8", newline="\n")
    print(arm, "perf", r.returncode, flush=True)
    if (HERE / ("price_" + arm + ".json")).is_file():
        shutil.rmtree(dst)
