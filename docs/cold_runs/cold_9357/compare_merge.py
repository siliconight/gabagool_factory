"""Cold run 9357 against 9356: the buildings' merge report row by row, and each building scene's ladders and markers.

    python docs/cold_runs/cold_9357/compare_merge.py <9356 package> <9357 package>

For every building both reports name: each count the report carries, the first package's and the second's, and the
second's `kept_carrying` list (Level Factory 0.227.0); then, in each package's `lot/<id>/site.tscn`, the node headers
in group `ladder_area3d` and in group `dc_marker`, as Godot writes a group (`groups=["ladder", "dc_marker"]` in the
header). A report without a field it is read for FAILS. Prints what it counted and stops.
"""
import json
import pathlib
import re
import sys

KEYS = ("slots_merged", "meshes_in", "surfaces_in", "merged", "unwrapped", "colliders", "lit_surfaces", "lit_meshes")
HEADER = re.compile(r'^\[node name="([^"]+)"[^\n]*? groups=\[([^\]]*)\]', re.M)


def report(pkg):
    d = json.loads((pkg / "merge_buildings.json").read_text(encoding="utf-8"))
    if d.get("schema") != "lf.merge_buildings.v1" or d.get("ok") is not True or not isinstance(d.get("scenes"), list):
        raise SystemExit("FAIL: %s: not a finished merge report" % pkg)
    rows = {}
    for r in d["scenes"]:
        for k in KEYS:
            if not isinstance(r.get(k), int):
                raise SystemExit("FAIL: %s: %s has no integer %s" % (pkg, r.get("scene"), k))
        rows[r["scene"]] = r
    return rows


def in_group(text, group):
    return sum(1 for m in HEADER.finditer(text) if '"%s"' % group in m.group(2).split(", "))


a, b = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
ra, rb = report(a), report(b)
if sorted(ra) != sorted(rb):
    raise SystemExit("FAIL: the reports name different buildings: %s / %s" % (sorted(ra), sorted(rb)))
totals = {k: [0, 0] for k in KEYS}
for scene in sorted(ra):
    print(scene)
    for k in KEYS:
        totals[k][0] += ra[scene][k]
        totals[k][1] += rb[scene][k]
        print("   %-14s %6d -> %6d  %+d" % (k, ra[scene][k], rb[scene][k], rb[scene][k] - ra[scene][k]))
    kept = rb[scene].get("kept_carrying")
    if not isinstance(kept, list):
        raise SystemExit("FAIL: %s: the second report's row has no kept_carrying list" % scene)
    print("   kept_carrying %s" % kept)
    rel = scene[len("res://"):]
    for name, pkg in (("first", a), ("second", b)):
        text = (pkg / rel).read_text(encoding="utf-8")
        print("   %-6s package: ladder_area3d %d, dc_marker %d" % (name, in_group(text, "ladder_area3d"),
                                                                  in_group(text, "dc_marker")))
print("all buildings")
for k in KEYS:
    print("   %-14s %6d -> %6d  %+d" % (k, totals[k][0], totals[k][1], totals[k][1] - totals[k][0]))
