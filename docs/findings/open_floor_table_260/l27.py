"""layout_lint L27 (ceiling_hole_walls, Deli Counter 0.235.0) over every spec in a directory: each built partition under an
authored hole in its own ceiling, how far into it and along how much. A probe: prints and stops.

    python l27.py <deli_counter dir> <specs dir>
"""
import glob, json, os, sys
DC = os.path.abspath(sys.argv[1]); SPECS = os.path.abspath(sys.argv[2])
sys.path.insert(0, DC); os.chdir(DC)
import layout_lint
n = 0; rows = []
for path in sorted(glob.glob(os.path.join(SPECS, "*.json"))):
    d = json.load(open(path, encoding="utf-8"))
    if not isinstance(d, dict) or "partitions" not in d:
        continue
    n += 1
    for w in layout_lint.ceiling_hole_walls(d):
        rows.append((os.path.basename(path)[:-5], w["wall"], w["axis"], w["pos"], w["into"], w["along"], w["hole"], len(w["refs"])))
print("specs", n, "L27 rows", len(rows))
for r in rows:
    print("  %-40s %-9s %s@%-6g into %.3f along %.3f hole %s refs %d" % r)
