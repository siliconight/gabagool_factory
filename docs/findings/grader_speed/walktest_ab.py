"""Does the walk test wait on the wall clock too, and what does it read without waiting?

With Laser Tag on the fixed clock (Laser Tag 0.27.0, Level Factory 0.180.0) its evaluations take
11 to 39 s, and the shell leg's floor becomes the walk tests: 2.1 to 2.6 minutes each in cold run
9247. Lot's director advances `_sim_time` by the physics delta at Godot's default clock (no time
scale), its walkers covering 475 to 480 m at 4 m/s -- about 120 s simulated in a 126 s job, so it
looks paced by real seconds the way Laser Tag was. Three arms on copies of each of cold run 9247's
staged walk tests, one candidate at a time, each the job's own command (`walktest.run_one`: the
scene run directly, Deli Counter's `nav_env` in the environment), each report compared with the
job's own, field by field:
  A  as the job ran (the synchronised clock): does the job reproduce?
  B  `--fixed-fps 60`
  C  `--fixed-fps 60` with the navigation map's iterations synchronous (the two project settings)
It measures and prints.

    python docs/findings/grader_speed/walktest_ab.py
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
G = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
X = os.path.join(F, "_scratch", "grader_speed", "walktest")
WS = os.path.join(F, "workspaces", "cold-9247-ws", ".level_factory")
NAV = ("\n[navigation]\n\nworld/map_use_async_iterations=false\n"
       "world/region_use_async_iterations=false\n")
SCENE = "site_navqa.tscn"
REPORT = "site_navqa.walktest.json"

sys.path.insert(0, os.path.join(F, "deli_counter"))
from agent_contract import nav_env  # noqa: E402


def job_report(seed):
    hits = sorted(glob.glob(os.path.join(WS, "jobs", "restaurant_row_001.walktest_navqa.candidate.seed_%d" % seed,
                                         "*", "out", REPORT)))
    assert hits, ("no job report", seed)
    log = os.path.join(os.path.dirname(os.path.dirname(hits[-1])), "job.log")
    first = open(log, encoding="utf-8", errors="replace").readline()
    assert "walktest.py" in first and SCENE in first, first[:160]
    return json.load(open(hits[-1], encoding="utf-8"))


def run(seed, arm):
    src = os.path.join(WS, "staging", "restaurant_row_001.walktest_navqa.candidate.seed_%d" % seed)
    p = os.path.join(X, "p_%d_%s" % (seed, arm))
    shutil.copytree(src, p)
    stale = os.path.join(p, REPORT)
    if os.path.exists(stale):
        os.remove(stale)
    if arm == "C":
        proj = os.path.join(p, "project.godot")
        assert "[navigation]" not in open(proj, encoding="utf-8").read(), proj
        with open(proj, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(NAV)
    cmd = [G, "--headless"] + (["--fixed-fps", "60"] if arm in "BC" else []) + ["--path", p, "res://" + SCENE]
    t0 = time.time()
    with open(os.path.join(X, "run_%d_%s.log" % (seed, arm)), "w", encoding="utf-8") as log:
        rc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                            timeout=900, env=nav_env(dict(os.environ))).returncode
    wall = time.time() - t0
    out = os.path.join(p, REPORT)
    report = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else None
    if report is not None:
        shutil.copy2(out, os.path.join(X, "r_%d_%s.json" % (seed, arm)))
    shutil.rmtree(p, ignore_errors=True)
    return rc, wall, report


def differ(a, b, path=""):
    """Every leaf that differs, as (path, a, b)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += differ(a.get(k), b.get(k), "%s.%s" % (path, k) if path else str(k))
        return out
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += differ(x, y, "%s[%d]" % (path, i))
        return out
    return [] if a == b else [(path, a, b)]


def main():
    shutil.rmtree(X, ignore_errors=True)
    os.makedirs(X)
    for seed in (9003, 9104, 9205):
        job = job_report(seed)
        print("seed %d: the job's report ok=%s" % (seed, job.get("ok")))
        for arm in "ABC":
            rc, wall, report = run(seed, arm)
            if report is None:
                print("  %s: exit %d, wall %.1f s, NO REPORT" % (arm, rc, wall))
                continue
            d = differ(job, report)
            print("  %s: exit %d, wall %.1f s, ok=%s, against the job: %s" % (
                arm, rc, wall, report.get("ok"),
                "identical in every field" if not d else "%d field(s) differ" % len(d)))
            for path, x, y in d[:8]:
                print("      %s: %r -> %r" % (path, x, y))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
