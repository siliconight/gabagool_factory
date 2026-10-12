"""Time Level Factory's corpus walk (tests/test_archetype_resolution.py `_brief_paths`) against a
walk that never descends into the directories it discards, and prove the two find the same briefs.

    A  the test's own walk, verbatim: `root.rglob("*.json")`, then drop any path whose parts meet
       _SKIP_DIRS, keep `brief.json` or anything in a `briefs` directory
    B  os.walk(followlinks=False) from the same root, pruning a directory named in _SKIP_DIRS
       before descending, then the SAME final filter on every path it yields

Arms alternate A B A B (the first walk of a tree pays the filesystem cache; alternation keeps that
off either arm). It prints each arm's seconds and count, whether the two lists are identical, and
where a full walk spends its entries, top-level directory by top-level directory. It measures and
prints.

    python docs/findings/lf_suite_time/brief_walk_probe.py [--root <factory>] [--rounds 2]
"""
import argparse
import os
import pathlib
import sys
import time

SKIP_DIRS = {"_runs", "build", "node_modules", ".git"}      # tests/test_archetype_resolution.py


def keep(path):
    if SKIP_DIRS & set(path.parts):
        return False
    return path.name == "brief.json" or path.parent.name == "briefs"


def arm_a(root):
    return sorted(p for p in root.rglob("*.json") if keep(p))


def arm_b(root):
    out = []
    for d, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if f.endswith(".json"):
                p = pathlib.Path(d, f)
                if keep(p):
                    out.append(p)
    return sorted(out)


def census(root):
    """Entries a full walk meets under each top-level directory, and how many of them sit under a
    skipped directory -- which arm A enumerates and arm B never enters."""
    rows = {}
    for top in sorted(root.iterdir()):
        if not top.is_dir():
            continue
        n = skipped = jsons = 0
        for d, dirs, files in os.walk(top, followlinks=False):
            under = bool(SKIP_DIRS & set(pathlib.Path(d).parts))
            n += len(dirs) + len(files)
            jsons += sum(1 for f in files if f.endswith(".json"))
            if under:
                skipped += len(dirs) + len(files)
        rows[top.name] = (n, skipped, jsons)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parents[3]))
    ap.add_argument("--rounds", type=int, default=2)
    args = ap.parse_args()
    root = pathlib.Path(args.root).resolve()
    print("root %s, python %s" % (root, sys.version.split()[0]))
    results = {}
    for r in range(args.rounds):
        for name, fn in (("A", arm_a), ("B", arm_b)):
            t = time.perf_counter()
            got = fn(root)
            dt = time.perf_counter() - t
            results.setdefault(name, []).append(got)
            print("round %d  %s  %7.2f s  %d briefs" % (r + 1, name, dt, len(got)))
    lists = [tuple(x) for v in results.values() for x in v]
    print("every walk the same list:", all(x == lists[0] for x in lists))
    if not all(x == lists[0] for x in lists):
        a, b = set(results["A"][0]), set(results["B"][0])
        print("  only A:", sorted(map(str, a - b))[:10])
        print("  only B:", sorted(map(str, b - a))[:10])
    t = time.perf_counter()
    rows = census(root)
    print("\ncensus (%.1f s): entries a full walk meets, by top-level directory" % (time.perf_counter() - t))
    total = sum(v[0] for v in rows.values())
    for name, (n, skipped, jsons) in sorted(rows.items(), key=lambda kv: -kv[1][0])[:16]:
        print("  %9d  %5.1f%%  under a skipped dir %9d  .json %7d  %s" % (n, 100.0 * n / max(total, 1), skipped, jsons, name))
    print("  %9d  total, %d under a skipped dir" % (total, sum(v[1] for v in rows.values())))


if __name__ == "__main__":
    main()
