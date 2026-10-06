"""Bake one imported building three ways (meshes, colliders, both) inside a
mirror of a staged Level Factory project, and print which probe points share an
island. Measures; names no cause.

    python run_bake_modes.py <staged project> <res://glb> <points.json> [skip.json] [--label L]
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import godot_probe  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    label = ""
    if "--label" in sys.argv:
        label = sys.argv[sys.argv.index("--label") + 1]
        args = [a for a in args if a != label]
    project, glb, points_path = args[0], args[1], args[2]
    skip = json.load(open(args[3])) if len(args) > 3 else []
    points = json.load(open(points_path))
    scratch = tempfile.mkdtemp(prefix="bake_modes_")
    mirror = godot_probe.mirror_project(project, scratch)
    godot_probe.add_autoload(
        mirror, os.path.join(HERE, "bake_modes.gd"), "BakeModes",
        {"bake_modes": {"glb": glb, "points": json.dumps(points),
                        "skip": json.dumps(skip)}})
    with open(os.path.join(mirror, "probe_empty.tscn"), "w", encoding="utf-8") as f:
        f.write('[gd_scene format=3]\n\n[node name="probe_empty" type="Node3D"]\n')
    godot = godot_probe.require_godot()
    r = subprocess.run([godot, "--headless", "--path", mirror, "res://probe_empty.tscn"],
                       capture_output=True, text=True, timeout=900)
    out = (r.stdout or "") + (r.stderr or "")
    payload = godot_probe._fenced(out, "BAKE_MODES_BEGIN", "BAKE_MODES_END")
    if payload is None:
        print("NO RESULT FENCE; Godot exited", r.returncode)
        print("\n".join(out.strip().splitlines()[-30:]))
        sys.exit(1)
    names = {"0": "meshes", "1": "colliders", "2": "both"}
    print("label:", label or "-", "| removed shapes:", len(payload["removed"]))
    for m, res in payload["modes"].items():
        print(f"  {names[m]:9s} polys {res['polys']:5d} islands {res['islands']:3d}")
        for k, v in res["points"].items():
            print(f"      {k:16s} island {v['island']:4d} ({v['island_polys']:5d} polys) snap {v['snap_m']}")
    with open(os.path.join(HERE, "last_" + (label or "run") + ".json"), "w") as f:
        json.dump(payload, f, indent=1)
    import shutil
    shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    main()
