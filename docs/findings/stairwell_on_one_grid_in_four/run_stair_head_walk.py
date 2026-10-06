"""Walk Laser Tag's body down and up one stair, with the stair's collision
ramp as built and lowered by one riser (stair_head_walk.gd). Measures.

    python run_stair_head_walk.py [--build DIR]

Defaults are deli_a03's up-stair (`stair1ramp_0`), in the building's own
Godot frame: the landing at (-11.8, 3.3, -6.6), the foot at (-11.8, 0.0,
-11.8), the ramp lowered 0.206 m (one of its 16 risers of 3.3 m).
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import godot_probe  # noqa: E402

BUILD = ROOT / "deli_counter" / "build"
if "--build" in sys.argv:
    BUILD = pathlib.Path(sys.argv[sys.argv.index("--build") + 1])

SHELL = "deli_a03"
SETTINGS = {"glb": "res://%s.glb" % SHELL, "ramp": "stair1ramp_0-convcolonly",
            "down_from": "[-11.8, 3.3, -6.6]", "down_to": "[-11.8, 0.0, -11.8]",
            "up_from": "[-11.8, 0.0, -11.8]", "up_to": "[-11.8, 3.3, -6.6]",
            "lower_m": 0.206, "seconds": 8.0}


def main():
    proj = pathlib.Path(tempfile.mkdtemp(prefix="stair_head_walk_"))
    try:
        shutil.copy2(BUILD / (SHELL + ".glb"), proj / (SHELL + ".glb"))
        (proj / "project.godot").write_text(
            'config_version=5\n\n[application]\n\nconfig/name="stair_head_walk"\n'
            'config/features=PackedStringArray("4.7")\n', encoding="utf-8")
        (proj / "probe_empty.tscn").write_text(
            '[gd_scene format=3]\n\n[node name="probe_empty" type="Node3D"]\n', encoding="utf-8")
        godot_probe.add_autoload(str(proj), str(HERE / "stair_head_walk.gd"), "StairHeadWalk",
                                 {"stair_head_walk": SETTINGS})
        godot = godot_probe.require_godot()
        subprocess.run([godot, "--headless", "--path", str(proj), "--import"],
                       capture_output=True, text=True, timeout=600)
        r = subprocess.run([godot, "--headless", "--path", str(proj), "res://probe_empty.tscn"],
                           capture_output=True, text=True, timeout=600, encoding="utf-8", errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        payload = godot_probe._fenced(out, "STAIR_WALK_BEGIN", "STAIR_WALK_END")
        if payload is None:
            print("NO RESULT FENCE; Godot exited", r.returncode)
            print("\n".join(out.strip().splitlines()[-25:]))
            sys.exit(1)
    finally:
        shutil.rmtree(proj, ignore_errors=True)
    print("ramp:", payload["ramp"], "| control lowers it", payload["lower_m"], "m")
    for run in payload["runs"]:
        print("  %-4s ramp %-11s found %-5s arrived %-5s end %s closest %.2f m in %.1f s"
              % (run["walk"], "LOWERED" if run["ramp_lowered"] else "as built", run["ramp_found"],
                 run["arrived"], run["end"], run["closest_m"], run["seconds"]))
    (HERE / "stair_head_walk.json").write_text(json.dumps(payload, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
