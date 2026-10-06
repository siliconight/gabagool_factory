"""Mirror a staged project, bake a scene with the site's navmesh settings (once,
or over a sweep of grid-origin offsets) and print island membership.

    python run_bake_sweep.py <project> <res://scene> <points.json> [sweep.json] --label L [--pad M]
"""
import json, os, shutil, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import godot_probe  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    argv = sys.argv[1:]
    label = argv[argv.index("--label") + 1]
    pad = float(argv[argv.index("--pad") + 1]) if "--pad" in argv else 2.0
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or not argv[i - 1].startswith("--"))]
    project, scene, points_path = pos[0], pos[1], pos[2]
    sweep = json.load(open(pos[3])) if len(pos) > 3 else []
    points = json.load(open(points_path))
    scratch = tempfile.mkdtemp(prefix="bake_sweep_")
    mirror = godot_probe.mirror_project(project, scratch)
    godot_probe.add_autoload(mirror, os.path.join(HERE, "bake_sweep.gd"), "BakeSweep",
        {"bake_sweep": {"scene": scene, "points": json.dumps(points), "sweep": json.dumps(sweep), "pad": pad, "dump": "--dump" in argv}})
    with open(os.path.join(mirror, "probe_empty.tscn"), "w", encoding="utf-8") as f:
        f.write('[gd_scene format=3]\n\n[node name="probe_empty" type="Node3D"]\n')
    r = subprocess.run([godot_probe.require_godot(), "--headless", "--path", mirror, "res://probe_empty.tscn"],
                       capture_output=True, text=True, timeout=1500)
    out = (r.stdout or "") + (r.stderr or "")
    payload = godot_probe._fenced(out, "BAKE_SWEEP_BEGIN", "BAKE_SWEEP_END")
    shutil.rmtree(scratch, ignore_errors=True)
    if payload is None:
        print("NO RESULT FENCE; Godot exited", r.returncode)
        print("\n".join(out.strip().splitlines()[-30:]))
        sys.exit(1)
    json.dump(payload, open(os.path.join(HERE, "sweep_" + label + ".json"), "w"), indent=1)
    print("label", label, "bounds", [round(v, 3) for v in payload["bounds"]])
    names = list(points)
    print("  offset               polys isl | " + " | ".join(n[:10] for n in names))
    for b in payload["bakes"]:
        off = b.get("offset", "own bounds")
        cells = " | ".join(f"{b['points'][n][0]:>4d}:{b['points'][n][1]:<5d}" for n in names)
        print(f"  {str(off):20s} {b['polys']:5d} {b['islands']:3d} | {cells}")

main()
