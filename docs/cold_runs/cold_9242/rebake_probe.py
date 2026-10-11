"""Bake a copy of cold run 9242's package with Level Factory's own bake, keeping the editor's output.

    python docs/cold_runs/cold_9242/rebake_probe.py <copy dir> <log file>

9242's export reported `{'error': 'bake.tscn did not open'}` after 83.7 s in the editor, where 9241's
same lot baked in 94.4 s. `light_bake._run` sends the editor's stdout and stderr to DEVNULL, so the
export kept nothing that says why. This calls `packages.exporting.light_bake.bake()` exactly as the
export does -- on a COPY, which it prepares itself (the copy must not exist) -- with one difference:
`_run` is wrapped so the editor's output is written to <log file>. Level Factory is imported, not
edited; `LF_ROOT` bakes with another checkout's plugin instead. The `spawned` set is 9241's, the same lot's responders' cars, as `tools/lux_rebake.py` takes
a package's own. It prints the bake's report and stops; what a failure or a success means belongs in
the record.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

F = Path(__file__).resolve().parents[3]
#: LF_ROOT names another Level Factory checkout to bake with (a test of a changed plugin)
sys.path.insert(0, os.environ.get("LF_ROOT") or str(F / "level_factory"))
from packages.exporting import light_bake  # noqa: E402

#: REBAKE_RUN names another run of the same lot to copy (9243 re-ran 9242 on Level Factory 0.178.5)
SRC = (F / "workspaces" / ("cold-%s-ws" % os.environ.get("REBAKE_RUN", "9242")) / ".level_factory"
       / "exports" / "LF_restaurant_row_001.portable-godot")
SPAWNED_FROM = (F / "workspaces" / "cold-9241-ws" / ".level_factory" / "exports"
                / "LF_restaurant_row_001.portable-godot" / "light_bake.json")
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"

copy, log_path = Path(sys.argv[1]), Path(sys.argv[2])
assert not copy.exists(), f"{copy} exists: the copy must be fresh"
shutil.copytree(SRC, copy)
# under `imports`, as tools/lux_rebake.py reads it; the first runs of this probe read a top-level
# `spawned` that the report does not carry, passed none, and baked the responders' car
spawned = tuple((json.loads(SPAWNED_FROM.read_text(encoding="utf-8")).get("imports") or {}).get("spawned") or ())


def _run_logged(cmd, timeout):
    """`light_bake._run`, with the process's output kept in <log file> instead of discarded."""
    t0 = time.time()
    with open(log_path, "wb") as fh:
        p = subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT)
        try:
            p.wait(timeout=timeout)
            return p.returncode, time.time() - t0
        except subprocess.TimeoutExpired:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
            return None, time.time() - t0


import inspect  # noqa: E402
if "log_path" in inspect.signature(light_bake._run).parameters:
    # Level Factory >= 0.178.5 keeps the editor's output itself; the record takes a copy of it
    report = light_bake.bake(copy, GODOT, spawned=spawned)
    if report.get("editor_log") and Path(report["editor_log"]).exists():
        shutil.copy(report["editor_log"], log_path)
else:
    light_bake._run = _run_logged
    report = light_bake.bake(copy, GODOT, spawned=spawned)
print(json.dumps({k: report.get(k) for k in ("ok", "editor_s", "room_fills", "reason", "result")}, indent=1))
