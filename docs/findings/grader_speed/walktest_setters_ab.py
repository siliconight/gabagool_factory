"""Do Lot 0.117.0's runtime setters do for the walk test what the project settings did?

`walktest_ab.py` made the navigation synchronous with two lines in each copy's project.godot (its
arm C: every report the job's, the map's iteration count aside, in about 4 s). The release does it
in `lot_navqa_setup.gd` at run time. Arms on copies of cold run 9247's three staged walk tests,
each with `patch_lot_walk_clock.py --draft` applied to the copy's own setup script and nothing in
project.godot, all under `--fixed-fps 60`:
  D   one at a time, against C and against the job
  D2  the same again: does it repeat?
  L   all three candidates at once: does load move it?
It measures and prints.

    python docs/findings/grader_speed/walktest_setters_ab.py
"""
import concurrent.futures as cf
import json
import os
import shutil
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import walktest_ab as W  # noqa: E402  (the same job reports, environment and differ)

X = os.path.join(F, "_scratch", "grader_speed", "walktest_setters")
C_DIR = os.path.join(F, "_scratch", "grader_speed", "walktest")
PATCH = os.path.join(F, "patches", "patch_lot_walk_clock.py")


def run(seed, arm):
    src = os.path.join(W.WS, "staging", "restaurant_row_001.walktest_navqa.candidate.seed_%d" % seed)
    p = os.path.join(X, "p_%d_%s" % (seed, arm))
    shutil.copytree(src, p)
    stale = os.path.join(p, W.REPORT)
    if os.path.exists(stale):
        os.remove(stale)
    assert "[navigation]" not in open(os.path.join(p, "project.godot"), encoding="utf-8").read()
    draft = subprocess.run([sys.executable, PATCH, "--draft"], env=dict(os.environ, LOT_ROOT=p),
                           capture_output=True, text=True)
    assert draft.returncode == 0 and "DRAFT" in draft.stdout, (draft.stdout, draft.stderr)
    cmd = [W.G, "--headless", "--fixed-fps", "60", "--path", p, "res://" + W.SCENE]
    t0 = time.time()
    with open(os.path.join(X, "run_%d_%s.log" % (seed, arm)), "w", encoding="utf-8") as log:
        rc = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                            timeout=900, env=W.nav_env(dict(os.environ))).returncode
    wall = time.time() - t0
    out = os.path.join(p, W.REPORT)
    report = json.load(open(out, encoding="utf-8")) if os.path.exists(out) else None
    shutil.rmtree(p, ignore_errors=True)
    return seed, arm, rc, wall, report


def show(seed, arm, rc, wall, report, against):
    if report is None:
        print("  %s: exit %d, wall %.1f s, NO REPORT" % (arm, rc, wall))
        return
    parts = []
    for name, ref in against:
        d = W.differ(ref, report)
        parts.append("%s %s" % (name, "identical" if not d else "differs in %s" % [p for p, _, _ in d]))
    print("  %s: exit %d, wall %.1f s, ok=%s; against %s" % (arm, rc, wall, report.get("ok"), "; ".join(parts)))


def main():
    shutil.rmtree(X, ignore_errors=True)
    os.makedirs(X)
    seeds = (9003, 9104, 9205)
    first = {}
    for seed in seeds:
        job = W.job_report(seed)
        c = json.load(open(os.path.join(C_DIR, "r_%d_C.json" % seed), encoding="utf-8"))
        print("seed %d" % seed)
        for arm in ("D", "D2"):
            s, a, rc, wall, rep = run(seed, arm)
            refs = [("C", c), ("the job", job)] + ([("D", first[seed])] if arm == "D2" and first.get(seed) else [])
            show(s, a, rc, wall, rep, refs)
            if arm == "D":
                first[seed] = rep
        sys.stdout.flush()
    print("all three at once")
    with cf.ThreadPoolExecutor(3) as pool:
        for s, a, rc, wall, rep in pool.map(lambda sd: run(sd, "L"), seeds):
            print("seed %d" % s)
            show(s, a, rc, wall, rep, [("D", first[s])])


if __name__ == "__main__":
    main()
