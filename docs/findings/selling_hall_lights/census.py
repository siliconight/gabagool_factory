"""Every room of the built library with its floor area and its fluorescent lamp count, as Deli Counter's
`build/<shell>.lights.json` and `specs/<shell>.json` hold them. Prints rooms whose id sells
(floors.floor_by_use == "tile") from the largest down, then the area per lamp.

Run from a Deli Counter checkout:  python <this> [min_area_m2]"""
import glob
import json
import os
import sys

sys.path.insert(0, os.getcwd())
import floors  # noqa: E402

MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
rows = []
for lp in sorted(glob.glob("build/*.lights.json")):
    shell = os.path.basename(lp)[:-len(".lights.json")]
    sp = os.path.join("specs", shell + ".json")
    if not os.path.isfile(sp):
        continue
    spec = json.load(open(sp, encoding="utf-8"))
    lamps = {}
    for a in json.load(open(lp, encoding="utf-8"))["anchors"]:
        if a.get("type") == "fluorescent":
            lamps[a.get("room")] = lamps.get(a.get("room"), 0) + int((a.get("row") or {}).get("count", 1))
    for r in spec.get("rooms", []):
        b = r.get("bounds")
        if not b or floors.floor_by_use(r.get("id")) != "tile":
            continue
        area = (b[2] - b[0]) * (b[3] - b[1])
        if area < MIN:
            continue
        n = lamps.get(r.get("id"), 0)
        rows.append((area, shell, r.get("id"), r.get("story", 0), n))
rows.sort(reverse=True)
print("area_m2 lamps m2_per_lamp shell room story")
for area, shell, rid, st, n in rows:
    print("%7.1f %5d %11s %s %s %s" % (area, n, ("%.1f" % (area / n)) if n else "-", shell, rid, st))
print("rooms:", len(rows), " at the 12-lamp cap:", sum(1 for r in rows if r[4] == 12))
