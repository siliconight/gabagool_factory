"""Copy a staged site, swap one building's GLB for a fresh build, reimport,
and bake it with run_bake_sweep exactly as the original was baked.
Measures; names no cause.

    python swap_and_bake.py <staging dir> <building.glb> <points.json> <label> <out dir>

The copy lands in <out dir>/<staging name>; the original is never touched.
`godot --headless --path <copy> --import` refreshes the swapped asset's
import cache (a run without it loads the stale import). The sweep JSON lands
in <out dir>/sweep_<label>.json. Godot is run with timeouts and nothing is
left running: subprocess.run waits for each process to exit.
"""
import os
import shutil
import subprocess
import sys

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import godot_probe  # noqa: E402

SWEEP_DIR = os.path.join(ROOT, "docs", "findings", "stairwell_on_one_grid_in_four")


def main():
    staging, glb, points, label, out = sys.argv[1:6]
    name = os.path.basename(staging.rstrip("/\\"))
    copy = os.path.join(out, name)
    if os.path.exists(copy):
        shutil.rmtree(copy)
    shutil.copytree(staging, copy)
    target = os.path.join(copy, "buildings", os.path.basename(glb))
    assert os.path.exists(target), "no %s in the staging; refusing to add one" % target
    before = os.path.getsize(target)
    shutil.copy2(glb, target)
    print("swapped %s: %d -> %d bytes" % (os.path.basename(glb), before, os.path.getsize(target)))
    godot = godot_probe.require_godot()
    r = subprocess.run([godot, "--headless", "--path", copy, "--import"],
                       capture_output=True, text=True, timeout=900)
    print("import exit", r.returncode)
    r = subprocess.run([sys.executable, "run_bake_sweep.py", copy, "res://site_navqa.tscn",
                        points, "--label", label, "--dump"],
                       cwd=SWEEP_DIR, capture_output=True, text=True, timeout=1700)
    print((r.stdout or "")[-600:], (r.stderr or "")[-400:])
    src = os.path.join(SWEEP_DIR, "sweep_" + label + ".json")
    if os.path.exists(src):
        shutil.move(src, os.path.join(out, "sweep_" + label + ".json"))
        print("sweep ->", os.path.join(out, "sweep_" + label + ".json"))


if __name__ == "__main__":
    main()
