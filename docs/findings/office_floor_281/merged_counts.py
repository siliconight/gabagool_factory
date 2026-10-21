"""Each building's merged meshes in two packages: the `MergedR_<n>` nodes of `lot/<building>/site.tscn`, one per room
cell and material as Level Factory merges a building (a submission each when it is in view). Prints the counts and
stops; the draw price's directions are read against them, not from them.

    python merged_counts.py <package before> <package after> [<building> ...]
"""
import os
import re
import sys

before, after = sys.argv[1:3]
names = sys.argv[3:] or sorted(os.listdir(os.path.join(after, "lot")))
for b in names:
    row = []
    for pkg in (before, after):
        p = os.path.join(pkg, "lot", b, "site.tscn")
        if not os.path.exists(p):
            row.append(None)
            continue
        row.append(len(set(re.findall(r'\[node name="(MergedR_\d+)"', open(p, encoding="utf-8").read()))))
    if row[0] != row[1] or len(sys.argv) > 3:
        print("%-24s %s -> %s" % (b, row[0], row[1]))
