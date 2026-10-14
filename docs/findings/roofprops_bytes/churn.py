"""Which of a cold run's Zoo outputs another Zoo builds differently, file by file (roadmap 247).

    python docs/findings/roofprops_bytes/churn.py <workspace> <tag>

Per Zoo job of `<workspace>`, compares every output but the .blend that the run's own Zoo built
(`.level_factory/jobs/<job>/1/out/`) with the first kept replay of `zoo_repro_probe.py --jobs <workspace> --keep
--tag <tag>` (`_scratch/zoo_repro/<tag>_<job>_0/`): the same bytes, other bytes, or in one only. For each GLB with
other bytes, every mesh array is classed by the probe's own `how` -- the same rows in another order, or values
apart -- and the classes are counted by array kind (POSITION, NORMAL, indices, ...). Prints what it measured; it
names no cause.
"""
import hashlib
import importlib.util
import os
import sys
from collections import Counter

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_spec = importlib.util.spec_from_file_location(
    "zoo_repro_probe", os.path.join(F, "docs", "findings", "grader_speed", "zoo_repro_probe.py"))
probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(probe)


def files(root):
    out = {}
    for a, _d, fs in os.walk(root):
        for f in fs:
            if not f.endswith(".blend"):
                p = os.path.join(a, f)
                out[os.path.relpath(p, root).replace(os.sep, "/")] = p
    return out


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(ws, tag):
    jobs = os.path.join(os.path.abspath(ws), ".level_factory", "jobs")
    names = sorted(n for n in os.listdir(jobs) if "zoo_" in n and os.path.isdir(os.path.join(jobs, n, "1", "out")))
    totals, classes, changed_jobs = Counter(), Counter(), []
    for name in names:
        ran = files(os.path.join(jobs, name, "1", "out"))
        kept = os.path.join(probe.X, "%s_%s_0" % (tag, name.split(".", 1)[-1]))
        if not os.path.isdir(kept):
            print("%-55s NO REPLAY at %s" % (name, kept))
            totals["no replay"] += 1
            continue
        new = files(kept)
        same = [r for r in ran if r in new and sha(ran[r]) == sha(new[r])]
        other = sorted(r for r in ran if r in new and r not in same)
        only = sorted(set(ran) ^ set(new))
        totals["files"] += len(set(ran) | set(new))
        totals["same"] += len(same)
        totals["other"] += len(other)
        totals["one only"] += len(only)
        if other or only:
            changed_jobs.append(name)
        glbs = [r for r in other if r.endswith(".glb")]
        for rel in glbs:
            a, b = probe.arrays(ran[rel]), probe.arrays(new[rel])
            for key in set(a) | set(b):
                h = probe.how(a[key], b[key]) if key in a and key in b else "only in one"
                if h:
                    classes[(key[2], h.split(",")[0])] += 1
        print("%-55s %4d files: %4d the same, %3d other (%d GLB), %d in one only%s" % (
            name, len(set(ran) | set(new)), len(same), len(other), len(glbs), len(only),
            (": " + ", ".join(other[:3]) + (" ..." if len(other) > 3 else "")) if other else ""))
    print("jobs %d, %d with a file changed; files %d: %d the same, %d other, %d in one only" % (
        len(names), len(changed_jobs), totals["files"], totals["same"], totals["other"], totals["one only"]))
    print("arrays of the GLBs with other bytes, by kind and class:")
    for (kind, cls), n in sorted(classes.items()):
        print("  %-12s %-40s %d" % (kind, cls, n))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
