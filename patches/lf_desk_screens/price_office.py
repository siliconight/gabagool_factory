"""The office alone: `price.py`'s three arm copies (still under _runs/perf_inner/desk_*), each with its anchors replaced
by the one bullpen station `price.py` appended -- the harness keeps 12 stations round-robin by type and dropped it
(the first run's rows) -- measured again in the same order. Reports office_<arm>.json beside this file."""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for arm in ("shipped", "overlay", "shipped2"):
    dst = ROOT / "_runs" / "perf_inner" / ("desk_" + arm)
    doc = json.loads((dst / "gameplay_anchors.json").read_text(encoding="utf-8"))
    mine = [a for a in doc["anchors"] if a.get("node_dispatch") == "price/office_bullpen"]
    assert len(mine) == 1, (arm, len(mine))
    (dst / "gameplay_anchors.json").write_text(json.dumps({"anchors": mine}, indent=1), encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "level_factory" / "tools" / "perf_stations_run.py"), str(dst),
                        "--json", str(HERE / ("office_" + arm + ".json"))], capture_output=True, text=True,
                       timeout=3600, cwd=str(ROOT / "level_factory"))
    (HERE / ("office_" + arm + ".out.txt")).write_text(r.stdout + r.stderr, encoding="utf-8", newline="\n")
    print(arm, "perf", r.returncode, flush=True)
