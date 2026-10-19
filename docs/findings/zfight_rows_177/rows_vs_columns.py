"""Deli Counter's z-fight gate on a composed package's buildings, twice: as it reads a Transform3D (the nine basis
numbers as COLUMNS) and with them read as ROWS, which is how Godot 4.7 writes and parses them (measured three
times: Deli Counter 0.120.1's `module_pose_census` on cold run 9013; Lot's `str_to_var` on 2026-09-13,
`lot/site_furniture.plate_facing`; and `tools/module_pose_census.py` on cold run 9324's deli_a01, 2026-10-19, in
this folder's README). Everything else is the gate's own code, imported: only the instance matrix differs.
For each building: findings (visible pairs the gate reports), buried pairs, solids, and the pair names that
appear under one reading and not the other. A probe: prints and stops (roadmap 177).

It swaps the gate's inline column matrix, which Deli Counter 0.230.0 replaced with `instance_matrix`, so it reads
0.229.0's gate and refuses any other (UNKNOWN SHAPE). The recorded run (`rows_vs_columns.out.txt`) pointed it at a
folder holding `git -C deli_counter show 54f5b5d4:zfight_gate.py`.

    python docs/findings/zfight_rows_177/rows_vs_columns.py <folder with 0.229.0's zfight_gate.py> <compose out presentation dir>
"""
import os
import re
import sys

dc = os.path.abspath(sys.argv[1])
pres = os.path.abspath(sys.argv[2])
sys.path.insert(0, dc)
import zfight_gate as Z  # noqa: E402

SRC = open(os.path.join(dc, "zfight_gate.py"), encoding="utf-8").read()
COLUMNS = """        m = [[f[0], f[3], f[6], f[9]],
             [f[1], f[4], f[7], f[10]],
             [f[2], f[5], f[8], f[11]]]
"""
ROWS = """        m = [[f[0], f[1], f[2], f[9]],
             [f[3], f[4], f[5], f[10]],
             [f[6], f[7], f[8], f[11]]]
"""
if SRC.count(COLUMNS) != 1:
    raise SystemExit("UNKNOWN SHAPE: zfight_gate.py's instance matrix is not the column reading this probe swaps")
ns = {}
exec(compile(SRC.replace(COLUMNS, ROWS), "zfight_gate_rows", "exec"), ns)


def run(fn, pkg):
    r = fn(pkg)
    if "error" in r:
        return r, set()
    names = {(f["a"], f["b"], f["axis"], round(f["plane"], 4)) for f in r.get("findings") or []}
    return r, names


lot = os.path.join(pres, "lot")
dirs = sorted(d for d in os.listdir(lot) if os.path.isdir(os.path.join(lot, d))) if os.path.isdir(lot) else []
tot = {"col": 0, "row": 0}
print("%-22s %16s %16s   only as columns / only as rows" % ("building", "columns: pairs/buried", "rows: pairs/buried"))
for d in dirs:
    pkg = os.path.join(lot, d)
    a, na = run(Z.check_package, pkg)
    b, nb = run(ns["check_package"], pkg)
    if "error" in a or "error" in b:
        print("%-22s %s" % (d, a.get("error") or b.get("error")))
        continue
    tot["col"] += a["pairs"]
    tot["row"] += b["pairs"]
    print("%-22s %8d / %-6d %8d / %-6d   %s / %s" % (d, a["pairs"], a["buried_pairs"], b["pairs"], b["buried_pairs"],
                                                   sorted(na - nb)[:3], sorted(nb - na)[:3]))
print("total visible pairs: columns %d, rows %d, over %d building(s)" % (tot["col"], tot["row"], len(dirs)))
