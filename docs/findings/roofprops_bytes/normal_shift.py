"""How far a Zoo build's normals moved between two builds of the same outputs, vertex by vertex (roadmap 247).

    python docs/findings/roofprops_bytes/normal_shift.py <workspace> <tag>

For every GLB `churn.py` finds with other bytes -- the run's own build (`.level_factory/jobs/<job>/1/out/`) against
the first kept replay (`_scratch/zoo_repro/<tag>_<job>_0/`) -- pairs each mesh primitive's vertices across the two
by their position and UV (rounded to 1e-5), and measures the angle between the paired vertices' normals. Prints the
count of vertices paired and unpaired, and the angles' distribution: every vertex, and the primitives whose largest
angle passes 1, 10 and 45 degrees, naming the worst ten. A vertex the other build has twice (two normals at one
position and UV) is paired with the nearer normal. Prints what it measured; it names no cause.
"""
import importlib.util
import math
import os
import sys
from collections import defaultdict

import numpy as np

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_spec = importlib.util.spec_from_file_location(
    "zoo_repro_probe", os.path.join(F, "docs", "findings", "grader_speed", "zoo_repro_probe.py"))
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)
_spec2 = importlib.util.spec_from_file_location("churn", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                       "churn.py"))
churn = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(churn)


def table(arr, prim):
    out = defaultdict(list)
    pos, nor = arr.get(prim + ("POSITION",)), arr.get(prim + ("NORMAL",))
    uv = arr.get(prim + ("TEXCOORD_0",))
    if pos is None or nor is None:
        return None
    for i in range(len(pos)):
        key = tuple(np.round(pos[i], 5)) + (tuple(np.round(uv[i], 5)) if uv is not None else ())
        out[key].append(nor[i].astype(np.float64))
    return out


def angle(a, b):
    c = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) or 1.0))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def main(ws, tag):
    jobs = os.path.join(os.path.abspath(ws), ".level_factory", "jobs")
    names = sorted(n for n in os.listdir(jobs) if "zoo_" in n and os.path.isdir(os.path.join(jobs, n, "1", "out")))
    angles, unpaired, worst = [], 0, []
    for name in names:
        ran = churn.files(os.path.join(jobs, name, "1", "out"))
        kept = os.path.join(probe.X, "%s_%s_0" % (tag, name.split(".", 1)[-1]))
        if not os.path.isdir(kept):
            continue
        new = churn.files(kept)
        for rel in sorted(r for r in ran if r.endswith(".glb") and r in new):
            if churn.sha(ran[rel]) == churn.sha(new[rel]):
                continue
            a, b = probe.arrays(ran[rel]), probe.arrays(new[rel])
            for prim in sorted({k[:2] for k in a} & {k[:2] for k in b}):
                ta, tb = table(a, prim), table(b, prim)
                if ta is None or tb is None:
                    continue
                prim_max = 0.0
                for key, ns in ta.items():
                    if key not in tb:
                        unpaired += len(ns)
                        continue
                    for n in ns:
                        d = min(angle(n, m) for m in tb[key])
                        angles.append(d)
                        prim_max = max(prim_max, d)
                worst.append((prim_max, name.split(".", 1)[-1], rel, prim[0]))
    angles = np.array(angles)
    print("vertices paired %d, unpaired %d" % (len(angles), unpaired))
    if len(angles):
        print("angle, degrees: median %.4f, 99th %.4f, max %.3f; over 1: %d, over 10: %d, over 45: %d" % (
            np.median(angles), np.percentile(angles, 99), angles.max(), (angles > 1).sum(), (angles > 10).sum(),
            (angles > 45).sum()))
    print("primitives compared %d; largest angle over 1: %d, over 10: %d, over 45: %d" % (
        len(worst), sum(1 for w in worst if w[0] > 1), sum(1 for w in worst if w[0] > 10),
        sum(1 for w in worst if w[0] > 45)))
    for w in sorted(worst, reverse=True)[:10]:
        print("  %7.2f deg  %-40s %s  %s" % w)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
