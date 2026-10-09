"""`census.json` as a table, one row a species, most domed first.

    python census_table.py census.json > census.txt

Columns: big-face corners over 10 degrees (OFF, ON), their mean splay in
degrees (OFF, ON), triangle corners whose normal moved over 1 degree, the
largest move, and vertices / triangles / primitives / bytes when they differ
ON against OFF (blank when identical, which the census found for all 121).
Prints what the file holds and stops.
"""
import json
import sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
rows = d["rows"]
ok = [r for r in rows if "error" not in r]
ok.sort(key=lambda r: (-(r.get("domed") or [0, 0])[0], -(r.get("moved_over_1") or 0), r["species"]))
print(f"theme {d['theme']}, style {d['style']}, big face > {d['big_m2']} m2, "
      f"domed > {d['domed_deg']} deg; {len(ok)} built, {len(rows) - len(ok)} did not")
print(f"{'species':20} {'domed off':>9} {'on':>6} {'splay off':>9} {'on':>6} "
      f"{'moved>1':>8} {'of':>7} {'max':>6}  differs")
for r in ok:
    dm = r.get("domed") or ["", ""]
    sp = r.get("splay_mean") or ["", ""]
    diff = [k for k in ("verts", "tris", "prims", "bytes") if r[k][0] != r[k][1]]
    print(f"{r['species']:20} {dm[0]!s:>9} {dm[1]!s:>6} {sp[0]!s:>9} {sp[1]!s:>6} "
          f"{r.get('moved_over_1')!s:>8} {r.get('corners')!s:>7} {r.get('moved_max')!s:>6}  "
          f"{' '.join(diff) or '-'}")
for r in rows:
    if "error" in r:
        print(f"{r['species']:20} did not build: {r['error']}")
