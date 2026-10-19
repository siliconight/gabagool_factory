"""look_shots stations aimed at each store video poker cabinet of one building in a mission's themed site: the
eye 1.6 m over the cabinet's floor, `--back` metres (default 3.0) from the cabinet toward its room's centre,
looking at the cabinet's middle 1.0 m up. Reads the building's spec (its cabinets and rooms, in the building's
own frame) and the themed drawn spec (where the building stands and its turn). Prints `--station` arguments in
look_shots' Godot frame (x, up, -y), the same convention as tools/room_stations.py, and on stderr what it
derived. The same arguments framed against an earlier run's package show the walls the cabinets now stand on.
A probe: prints and stops.

    python docs/cold_runs/cold_9324/cabinet_stations.py <workspace> <mission> <building id> <spec.json> [--back 3.0]
"""
import json
import math
import sys
from pathlib import Path

KEY = "video_poker_store_r"


def main(argv):
    if len(argv) < 4:
        raise SystemExit(__doc__)
    ws, mission, bid, spec_path = argv[:4]
    back = float(argv[argv.index("--back") + 1]) if "--back" in argv else 3.0
    drawn = Path(ws) / ".level_factory" / "jobs" / f"{mission}.themed_site_assemble" / "1" / "out" / "site.site.drawn.json"
    site = json.load(open(drawn, encoding="utf-8"))
    b = next((b for b in site.get("buildings") or [] if b.get("id") == bid), None)
    if b is None:
        raise SystemExit(f"no building {bid} in {drawn}")
    at = b.get("at")
    if not at or len(at) < 2:
        raise SystemExit(f"building {bid} carries no `at`: {sorted(b)}")
    rot = float(b.get("rot") or 0.0)
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def world(x, y):
        return float(at[0]) + c * x - s * y, float(at[1]) + s * x + c * y

    spec = json.load(open(spec_path, encoding="utf-8"))
    sh = float(spec.get("story_height") or 0.0)
    if not sh:
        raise SystemExit("the spec carries no story_height")
    rooms = spec.get("rooms") or []
    cabs = [v for v in spec.get("volumes") or [] if str(v.get("name", "")).startswith(KEY)]
    if not cabs:
        raise SystemExit("no %s* volume in %s" % (KEY, spec_path))
    out = []
    for v in cabs:
        x, y, z, hz = float(v["x"]), float(v["y"]), float(v["z"]), float(v["size_z"])
        floor = z - hz / 2.0
        story = int(round(floor / sh))
        room = next((r for r in rooms if int(r.get("story", 0)) == story
                     and r["bounds"][0] <= x <= r["bounds"][2] and r["bounds"][1] <= y <= r["bounds"][3]), None)
        if room is None:
            raise SystemExit("cabinet %s stands in no room on storey %d" % (v["name"], story))
        x0, y0, x1, y1 = room["bounds"]
        dx, dy = (x0 + x1) / 2.0 - x, (y0 + y1) / 2.0 - y
        n = math.hypot(dx, dy) or 1.0
        ex, ey = x + dx / n * back, y + dy / n * back
        wex, wey = world(ex, ey)
        wtx, wty = world(x, y)
        name = "cab_" + str(room["id"]) + "_" + v["name"].rsplit("_", 1)[-1]
        print("# %s: %s in %s (storey %d), plan (%.2f, %.2f) floor %.2f; eye (%.2f, %.2f) %.2f up -> (%.2f, %.2f) %.2f up"
              % (name, v["name"], room["id"], story, wtx, wty, floor, wex, wey, floor + 1.6, wtx, wty, floor + 1.0),
              file=sys.stderr)
        out.append("--station %s:%g,%g,%g,%g,%g,%g" % (name, round(wex, 2), round(floor + 1.6, 2), round(-wey, 2),
                                                      round(wtx, 2), round(floor + 1.0, 2), round(-wty, 2)))
    print(" ".join(out))


if __name__ == "__main__":
    main(sys.argv[1:])
