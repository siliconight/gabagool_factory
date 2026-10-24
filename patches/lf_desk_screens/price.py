"""PRICE the desk screens' motion overlay (the walker's walk of cold run 9386, finding 5) before it ships: draw calls
and frame time at fixed stations, three arms of one raw package in one session (`CLAUDE.md`).

    python patches/lf_desk_screens/price.py <raw package>

Arms, each a fresh copy with its import cache removed and re-imported:
  * ``shipped`` and ``shipped2`` -- the package as exported: the control, whose difference is the instrument's;
  * ``overlay`` -- the same, with `screen_overlay_prep.gd` hanging the CRT pass's overlay on the merged desk screens.
Every arm's `gameplay_anchors.json` gains ONE camera socket at the office's bullpen (`OFFICE_STATION`, Godot metres,
the floor under the eye), so a station looks across the desks; the package's own stations stay. Reports go to
<arm>.json beside this file via Level Factory's `tools/perf_stations_run.py` (windowed: headless draws nothing).
"""
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
#: the office (b2, placed at Godot 54, 0, -0.49) ground_bullpen's middle: spec (0, 6) -> Godot (54, 0, -6.49)
OFFICE_STATION = [54.0, 0.0, -6.49]

pkg = pathlib.Path(sys.argv[1])
assert (pkg / "gameplay_anchors.json").is_file(), pkg
for arm in ("shipped", "overlay", "shipped2"):
    dst = ROOT / "_runs" / "perf_inner" / ("desk_" + arm)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(pkg, dst)
    shutil.rmtree(dst / ".godot", ignore_errors=True)
    r = subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"], capture_output=True, text=True,
                       timeout=1800)
    print(arm, "import", r.returncode, flush=True)
    doc = json.loads((dst / "gameplay_anchors.json").read_text(encoding="utf-8"))
    doc["anchors"].append({"anchor_type": "camera_socket", "node_dispatch": "price/office_bullpen",
                           "transform": {"pos": OFFICE_STATION, "rot_y_deg": 0.0}})
    (dst / "gameplay_anchors.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    if arm == "overlay":
        shutil.copy2(HERE / "screen_overlay_prep.gd", dst / "screen_overlay_prep.gd")
        r = subprocess.run([GODOT, "--headless", "--path", str(dst), "--script", "res://screen_overlay_prep.gd"],
                           capture_output=True, text=True, timeout=600)
        (HERE / "prep.out.txt").write_text(r.stdout + r.stderr, encoding="utf-8", newline="\n")
        print(arm, "prep", r.returncode, [l for l in r.stdout.splitlines() if "given the overlay" in l], flush=True)
        if r.returncode != 0:
            raise SystemExit("the overlay arm could not be prepared; see prep.out.txt")
    r = subprocess.run([sys.executable, str(ROOT / "level_factory" / "tools" / "perf_stations_run.py"), str(dst),
                        "--json", str(HERE / (arm + ".json"))], capture_output=True, text=True, timeout=3600,
                       cwd=str(ROOT / "level_factory"))
    (HERE / (arm + ".out.txt")).write_text(r.stdout + r.stderr, encoding="utf-8", newline="\n")
    print(arm, "perf", r.returncode, flush=True)
