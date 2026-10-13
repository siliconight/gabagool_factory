"""Did the pole line move seed_9104's Laser Tag route, and how? Cold run 9262 (Lot 0.118.0, the
pole line) read restaurant_row_001's picked candidate at route completion 0.64 and 29 player-stuck
events where cold run 9261 (Lot 0.117.0, steel lamps on both kerbs) read 1.00 and 9 -- and no stuck
event stood within 1.5 m of a pole (the nearest 16.6 m), every one at two places 9261's bot also
stuck at or beside: a kerb face at (-66, -5) and a meter between two parked cars at (35, -17), the
cover within 5 m of each the same in both runs. Four arms, each the job's own command (Laser Tag
0.27.0, the fixed clock) on a copy of a staged evaluation project:

    p9262       9262's project as staged: must read 9262's job (the control)
    p9262-pole  9262's project with its utility poles' nodes removed from site.tscn
    l9261       9261's project as staged: must read 9261's job (the control)
    l9261-lamp  9261's project with its streetlights' nodes removed

It measures and prints.

    python docs/findings/pole_line/lt_pole_ab.py

CANNOT RUN AGAIN AS WRITTEN (2026-10-13): workspaces/cold-9261-ws and workspaces/cold-9262-ws were
retired on 2026-10-12, when `_ws` built their names and nothing named them in a form
tools/factory_retire.py could see, so every arm has no project to copy. `lt_pole_ab.out.txt` is the
record, kept as measured.
"""
import glob
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

F = pathlib.Path(__file__).resolve().parents[3]
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
JOB = "restaurant_row_001.laser_tag_evaluate.candidate.seed_9104"
LOT = "restaurant_row_001.lot_assemble.candidate.seed_9104"
X = F / "_scratch" / "pole_line" / "lt_pole_ab"
#: the runs' workspaces, named in full so tools/factory_retire.py sees what this reads
WORKSPACES = {9261: "cold-9261-ws", 9262: "cold-9262-ws"}


def _ws(n):
    return F / "workspaces" / WORKSPACES[n] / ".level_factory"


def _slots(n, species):
    path = sorted(glob.glob(str(_ws(n) / "jobs" / LOT / "*" / "out" / "site.slots.json")))[-1]
    return [s["slot_id"] for s in json.load(open(path, encoding="utf-8"))["slots"]
            if s.get("species") == species]


def _strip(scene, names):
    """``site.tscn`` without the nodes ``names`` and their children: a block is
    a header line ``[...]`` and what follows it to the next header."""
    text = scene.read_text(encoding="utf-8")
    blocks = re.split(r"(?m)^(?=\[)", text)
    keep, dropped = [], 0
    for b in blocks:
        head = b.split("\n", 1)[0]
        if head.startswith("[node "):
            name = re.search(r'name="([^"]+)"', head)
            parent = re.search(r'parent="([^"]*)"', head)
            top = parent.group(1).lstrip("./").split("/")[0] if parent else ""
            if (name and name.group(1) in names and top == "") or top in names:
                dropped += 1
                continue
        keep.append(b)
    scene.write_text("".join(keep), encoding="utf-8", newline="\n")
    return dropped


def _run(arm, n, strip_species=None):
    proj = X / f"p_{arm}"
    if proj.exists():
        shutil.rmtree(proj)
    shutil.copytree(_ws(n) / "staging" / JOB, proj)
    dropped = 0
    if strip_species:
        dropped = _strip(proj / "site.tscn", set(_slots(n, strip_species)))
    out = X / f"r_{arm}.json"
    cmd = [GODOT, "--headless", "--fixed-fps", "60", "--path", str(proj), "-s",
           "res://addons/laser_tag_tool/runners/run_map_eval.gd", "--", "--bake-nav", "--map",
           "res://level.tscn", "--scenario", "res://mission_scenario.tres", "--runs", "25",
           "--seed", "9104", "--output", str(out)]
    t = time.perf_counter()
    with open(X / f"run_{arm}.log", "w", encoding="utf-8") as log:
        code = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                              timeout=1200).returncode
    print("%-11s exit %d, %5.1f s, %d node block(s) removed" % (arm, code, time.perf_counter() - t, dropped))
    shutil.rmtree(proj)
    return json.load(open(out, encoding="utf-8")) if out.is_file() else None


def _job(n):
    path = sorted(glob.glob(str(_ws(n) / "jobs" / JOB / "*" / "out" / "lasertag.report.json")))[-1]
    return json.load(open(path, encoding="utf-8"))


def _line(name, d):
    if d is None:
        return "%-11s NO REPORT" % name
    s = d["summary"]
    return ("%-11s %-16s %3s  route %4s  player stuck %2s  enemy stuck %2s  deaths %2s  events %4d"
            % (name, d["grade"], d["overall_score"], s["route_completion_rate"],
               s["player_stuck_events"], s["enemy_stuck_events"], s["player_deaths"], len(d["events"])))


def main():
    X.mkdir(parents=True, exist_ok=True)
    r = {"job9262": _job(9262), "job9261": _job(9261)}
    r["p9262"] = _run("p9262", 9262)
    r["p9262-pole"] = _run("p9262-pole", 9262, "utility_pole")
    r["l9261"] = _run("l9261", 9261)
    r["l9261-lamp"] = _run("l9261-lamp", 9261, "streetlight")
    for k, d in r.items():
        print(_line(k, d))
    for a, b in (("p9262", "job9262"), ("l9261", "job9261")):
        if r[a] and r[b]:
            differ = [k for k in r[a] if k != "map" and r[a][k] != r[b].get(k)]
            print("%s vs %s (the control): %s" % (a, b, "identical in every field" if not differ else differ))


if __name__ == "__main__":
    sys.exit(main())
