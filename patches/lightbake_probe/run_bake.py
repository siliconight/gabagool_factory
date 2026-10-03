"""Run the bake probe's editor once, bounded:

    python run_bake.py <bake dir> [timeout s]

Starts the Godot editor on <bake dir> (whose `bake_probe` plugin bakes and
quits), waits, and on a timeout kills that process TREE by PID (the console
launcher's engine is a grandchild; a plain timeout leaves it drawing).
Prints the plugin's result and the wall time. Kills nothing it did not
start.
"""
import json
import os
import subprocess
import sys
import time

GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"


def main():
    d = sys.argv[1]
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 1800.0
    out = os.path.join(d, "bake_result.json")
    if os.path.exists(out):
        os.remove(out)
    log = open(os.path.join(d, "bake_editor.log"), "w", encoding="utf-8")
    t0 = time.time()
    p = subprocess.Popen([GODOT, "--editor", "--path", d, "--resolution", "1280x720"],
                         stdout=log, stderr=subprocess.STDOUT)
    try:
        p.wait(timeout=limit)
        print("RUN editor exited", p.returncode, "after %.0f s" % (time.time() - t0))
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        print("RUN TIMED OUT after %.0f s; killed tree %d" % (time.time() - t0, p.pid))
    time.sleep(1.5)
    if os.path.exists(out):
        print("RUN result", json.dumps(json.load(open(out, encoding="utf-8"))))
    else:
        print("RUN no result file")


if __name__ == "__main__":
    main()
