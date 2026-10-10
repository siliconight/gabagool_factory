"""Census of the interior ceiling rows Deli Counter derives, from the shipped light manifests.

    python docs/findings/fixture_rows/row_census.py [<root> ...]

Reads every `*.lights.json` under the roots given (default: `deli_counter/build`), skipping
`_runs`, and prints: anchors by type; rows by lamp count; how many fluorescent rows stand at
their room's centre on the room's longer axis (the manifest carries `room`, `pos` and `rot_y`,
and `deli_counter/lights.py:_row_for_bounds` derives the row from the room's bounds, so this
reads the `.gameplay.json` beside each manifest for the bounds); and how many rooms carry more
than one row (runs split at voids and nudges). It prints what it counted and stops.
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
FACTORY = HERE.parents[3]


def rooms_of(manifest_path):
    gp = manifest_path.with_name(manifest_path.name.replace(".lights.json", ".gameplay.json"))
    if not gp.exists():
        return {}
    try:
        data = json.load(open(gp, encoding="utf-8"))
    except Exception:
        return {}
    return {r.get("id"): r for r in data.get("rooms", []) if r.get("id")}


def main(argv):
    roots = [Path(a) for a in argv] or [FACTORY / "deli_counter" / "build"]
    files = []
    for root in roots:
        for p in root.rglob("*.lights.json"):
            if "_runs" in p.parts or ".git" in p.parts:
                continue
            files.append(p)
    by_type = Counter()
    rows_by_count = Counter()
    rows_per_room = Counter()
    centred = Counter()
    long_axis = Counter()
    spacing = Counter()
    buildings = 0
    for p in sorted(files):
        try:
            data = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        buildings += 1
        rooms = rooms_of(p)
        for a in data.get("anchors", []):
            t = a.get("type")
            by_type[t] += 1
            if t != "fluorescent":
                continue
            row = a.get("row") or {}
            n = int(row.get("count", 1) or 1)
            rows_by_count[n] += 1
            spacing[round(float(row.get("spacing", 0.0) or 0.0), 1)] += 1
            rows_per_room[(str(p), a.get("room"))] += 1
            r = rooms.get(a.get("room"))
            if not r or not r.get("bounds") or not a.get("pos"):
                centred["unknown"] += 1
                continue
            x0, y0, x1, y1 = r["bounds"]
            cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            px, py = a["pos"][0], a["pos"][1]
            rot = float(a.get("rot_y", 0.0) or 0.0)
            along_x = abs(rot) < 45.0
            # the row's line is its across-axis coordinate; a run split at a void moves along it
            off = abs(py - cy) if along_x else abs(px - cx)
            centred["on the room's centreline" if off < 0.05 else "off the centreline (nudged or shifted)"] += 1
            long_axis["along the longer axis" if (along_x == ((x1 - x0) >= (y1 - y0))) else "across it"] += 1
    print("manifests: %d under %s" % (buildings, ", ".join(str(r) for r in roots)))
    print("anchors by type: %s" % dict(by_type.most_common()))
    print("fluorescent rows by lamp count: %s" % dict(sorted(rows_by_count.items())))
    print("row spacing (m, rounded): %s" % dict(sorted(spacing.items())))
    multi = sum(1 for k, v in rows_per_room.items() if v > 1)
    print("rooms with a fluorescent row: %d; with more than one run: %d" % (len(rows_per_room), multi))
    print("rows on the room centreline: %s" % dict(centred))
    print("rows along the room's longer axis: %s" % dict(long_axis))


if __name__ == "__main__":
    main(sys.argv[1:])
