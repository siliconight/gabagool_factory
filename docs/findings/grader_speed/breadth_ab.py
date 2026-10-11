"""Does the unsynchronised clock reproduce every job, not only the one it was found on?

`fixedfps_ab.sh` and `syncnav_ab.sh` showed, on cold run 9247's seed_9104 evaluation, that Godot's
`--fixed-fps 60` with the navigation map's iterations synchronous reproduces the job's report in
every field in 21 s against 593. One candidate of one mission is not a claim about the grader, so
this runs the same configuration on fourteen staged evaluations across five missions -- each a copy
of the job's staged project with both async-iteration settings turned off, each the job's own
command with `--fixed-fps 60` added -- TWICE, three at a time (the scheduler's width), and compares
the first report with the job's own and the second with the first, field by field: whether the
fast clock reads as the job did, and whether it reads the same every time. Older staged projects
carry the Laser Tag of their day; the comparison is always that code against itself under the two
clocks. It measures and prints.

REFUTED, KEPT: the first draft guessed every workspace's seeds as 9003/9104/9205 and stopped on the
fifth case; the four it had run are kept in `breadth_ab.draft1.out.txt`.

    python docs/findings/grader_speed/breadth_ab.py
"""
import concurrent.futures as cf
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
G = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
X = os.path.join(F, "_scratch", "grader_speed", "breadth")
RUNNER = "res://addons/laser_tag_tool/runners/run_map_eval.gd"
NAV = ("\n[navigation]\n\nworld/map_use_async_iterations=false\n"
       "world/region_use_async_iterations=false\n")
#: The workspaces, newest Laser Tag first; their candidates are READ from the staging folder's
#: names, never assumed (the first draft guessed 9003/9104/9205 everywhere and stopped on
#: warehouse_yard_001, whose seeds are 9004/9105/9206). 9247's seed_9104 is `syncnav_ab.sh`'s.
WORKSPACES = ("cold-9247-ws", "cold-9246-ws", "cold-9240-ws", "cold-9214-ws", "cold-9209-ws")


def _cases():
    out = []
    for ws in WORKSPACES:
        staged = os.path.join(F, "workspaces", ws, ".level_factory", "staging")
        for name in sorted(os.listdir(staged)):
            m = re.fullmatch(r"(.+)\.laser_tag_evaluate\.candidate\.seed_(\d+)", name)
            if m and not (ws == "cold-9247-ws" and m.group(2) == "9104"):
                out.append((ws, m.group(1), int(m.group(2))))
    return out


CASES = _cases()


def job_of(ws, mission, seed):
    base = os.path.join(F, "workspaces", ws, ".level_factory")
    name = "%s.laser_tag_evaluate.candidate.seed_%d" % (mission, seed)
    reports = sorted(glob.glob(os.path.join(base, "jobs", name, "*", "out", "lasertag.report.json")))
    assert reports, ("no report for", ws, name)
    report = reports[-1]
    log = os.path.join(os.path.dirname(os.path.dirname(report)), "job.log")
    text = open(log, encoding="utf-8", errors="replace").read()
    first = text.splitlines()[0]
    assert first.startswith("$ ") and RUNNER in first, (log, first[:120])
    argv = first[2:].split()
    user = argv[argv.index("--") + 1:]
    assert "--output" in user and "--seed" in user, (log, user)
    wall = sum(float(x) for x in re.findall(r"duration=([0-9.]+)s", text))
    staging = os.path.join(base, "staging", name)
    assert os.path.isdir(staging), ("no staged project", staging)
    return staging, user, report, wall


def _fixed(staging, user, tag):
    """One run of the job's command on a copy, synchronous navigation, `--fixed-fps 60`."""
    p = os.path.join(X, "p_" + tag)
    shutil.copytree(staging, p)
    proj = os.path.join(p, "project.godot")
    assert "[navigation]" not in open(proj, encoding="utf-8").read(), ("a [navigation] section already", proj)
    with open(proj, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(NAV)
    out = os.path.join(X, "r_%s.json" % tag)
    args = list(user)
    args[args.index("--output") + 1] = out
    cmd = [G, "--headless", "--fixed-fps", "60", "--path", p, "-s", RUNNER, "--"] + args
    t0 = time.time()
    with open(os.path.join(X, "run_%s.log" % tag), "w", encoding="utf-8") as log:
        rc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                            timeout=1800).returncode
    wall = time.time() - t0
    shutil.rmtree(p, ignore_errors=True)
    return rc, wall, (json.load(open(out, encoding="utf-8")) if os.path.isfile(out) else None)


def _against(a, b):
    """Every field compared; the events that differ listed with the keys that moved."""
    if a is None or b is None:
        return "NO REPORT", []
    differ = sorted(set(k for k in a if a[k] != b.get(k)) | set(k for k in b if k not in a))
    if not differ:
        return "identical in every field", []
    moved = []
    for i, (x, y) in enumerate(zip(a["events"], b["events"])):
        if x != y:
            moved.append((i, x.get("run_id"), x.get("event"),
                          {k: (x.get(k), y.get(k)) for k in set(x) | set(y) if x.get(k) != y.get(k)}))
    extra = "" if len(a["events"]) == len(b["events"]) else ", events %d vs %d" % (len(b["events"]), len(a["events"]))
    return "DIFFER in %s (%d events%s)" % (differ, len(moved), extra), moved


def run(case):
    ws, mission, seed = case
    staging, user, report, job_wall = job_of(ws, mission, seed)
    tag = "%s_%s_%d" % (ws, mission, seed)
    rc1, wall1, r1 = _fixed(staging, user, tag + "_1")
    rc2, wall2, r2 = _fixed(staging, user, tag + "_2")
    job = json.load(open(report, encoding="utf-8"))
    return case, (rc1, rc2), (wall1, wall2), job_wall, _against(job, r1), _against(r1, r2), len(job["events"])


def main():
    shutil.rmtree(X, ignore_errors=True)
    os.makedirs(X)
    print("Each candidate: the job's report against the first fixed-clock run, and the second run")
    print("against the first. Walls: the job's (synchronised, from its log) and each fixed run's.\n")
    same_job = same_self = 0
    with cf.ThreadPoolExecutor(3) as pool:
        for case, rcs, walls, job_wall, vs_job, vs_self, events in pool.map(run, CASES):
            ws, mission, seed = case
            print("%s %s seed %d: %d events; job %.1f s, fixed %.1f s and %.1f s (exit %d, %d)" % (
                ws, mission, seed, events, job_wall, walls[0], walls[1], rcs[0], rcs[1]))
            print("    against the job:   " + vs_job[0])
            for i, run_id, kind, keys in vs_job[1][:6]:
                print("        #%d run %s %s %s" % (i, run_id, kind, keys))
            print("    second against first: " + vs_self[0])
            for i, run_id, kind, keys in vs_self[1][:6]:
                print("        #%d run %s %s %s" % (i, run_id, kind, keys))
            same_job += vs_job[0].startswith("identical")
            same_self += vs_self[0].startswith("identical")
            sys.stdout.flush()
    print("\n%d of %d identical to their jobs' reports; %d of %d identical to themselves run again" % (
        same_job, len(CASES), same_self, len(CASES)))


if __name__ == "__main__":
    main()
