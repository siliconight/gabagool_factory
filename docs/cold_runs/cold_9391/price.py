"""PRICE cold run 9391's fixes and roadmap 305's horizon ring: draw calls and frame time at fixed stations, every arm
in one session (`CLAUDE.md`; prices drift between sessions).

    python docs/cold_runs/cold_9391/price.py

Arms, each a fresh copy of a WALK COPY with its import cache removed and re-imported (a walk copy runs `_walk.tscn`,
its harness included, so these prices compare with each other and not with a raw package's):
  * ``ctrl`` and ``ctrl2`` -- cold run 9389's walk copy, twice: the control, whose spread is the instrument's;
  * ``fixes`` -- cold run 9391's: one sign, door hardware, the painted safe, pallet stacks, casings (net of all);
  * ``ring`` -- 9389's with roadmap 305's prototype ring (`docs/findings/vistas_305/proto_ring.py`, the test strip);
    its SkyMint shader edit (`proto_apply.py`) is inert in this level, which runs `blue_hour`.
Stations are each package's own (`gameplay_anchors.json`). Reports go to <arm>.json beside this file via Level
Factory's `tools/perf_stations_run.py` (windowed); each copy is deleted once its report exists.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
ARMS = (("ctrl", ROOT / "_runs" / "walk_9389_restaurant_row_001"),
        ("fixes", ROOT / "_runs" / "walk_9391_restaurant_row_001"),
        ("ring", ROOT / "_scratch" / "vista_proto"),
        ("ctrl2", ROOT / "_runs" / "walk_9389_restaurant_row_001"))
for arm, src in ARMS:
    assert (src / "gameplay_anchors.json").is_file(), src
    dst = ROOT / "_runs" / "perf_inner" / ("price9391_" + arm)
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
