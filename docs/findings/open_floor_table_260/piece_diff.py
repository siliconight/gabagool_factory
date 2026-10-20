"""Volumes out / in / moved between two spec directories, for the specs named. A probe: prints and stops.

    python piece_diff.py <old specs dir> <new specs dir> name [name ...]
"""
import json, os, sys
old_dir, new_dir, names = sys.argv[1], sys.argv[2], sys.argv[3:]
for n in names:
    a = json.load(open(os.path.join(old_dir, n + ".json"), encoding="utf-8"))
    b = json.load(open(os.path.join(new_dir, n + ".json"), encoding="utf-8"))
    va = {v["name"]: v for v in a.get("volumes", [])}
    vb = {v["name"]: v for v in b.get("volumes", [])}
    out = sorted(set(va) - set(vb)); inn = sorted(set(vb) - set(va))
    moved = sorted(k for k in set(va) & set(vb) if (va[k]["x"], va[k]["y"], va[k]["z"]) != (vb[k]["x"], vb[k]["y"], vb[k]["z"]))
    other = sorted(k for k in a if k not in ("volumes",) and a[k] != b.get(k))
    print("%-22s volumes %d -> %d; out %d, in %d, moved %d; other keys changed: %s" % (n, len(va), len(vb), len(out), len(inn), len(moved), other))
    for k in out: print("   out   %-34s (%.2f, %.2f, z %.2f) %gx%g" % (k, va[k]["x"], va[k]["y"], va[k]["z"], va[k]["size_x"], va[k]["size_y"]))
    for k in inn: print("   in    %-34s (%.2f, %.2f, z %.2f) %gx%g" % (k, vb[k]["x"], vb[k]["y"], vb[k]["z"], vb[k]["size_x"], vb[k]["size_y"]))
    for k in moved: print("   moved %-34s (%.2f, %.2f) -> (%.2f, %.2f)" % (k, va[k]["x"], va[k]["y"], vb[k]["x"], vb[k]["y"]))
