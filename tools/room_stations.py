"""Interior stations for look_shots: inside a building's biggest rooms, looking along the ceiling.

    python tools/room_stations.py <workspace> <mission> <building id> [--rooms 4] [--list]

Reads the mission's themed drawn spec for the building's position, rotation and archetype, and
the archetype's gameplay manifest (`<mission>.patina_apply.<archetype>/1/out/<archetype>.patina.gameplay.json`)
for its rooms; the building id is the drawn spec's (`b0`), the jobs are keyed by archetype. For the N largest rooms on storeys 0 and 1 (stairwells skipped) it prints
`--station <room>:ex,ey,ez,tx,ty,tz` in look_shots' Godot frame (x, up, -y): the eye 1.6 m over
the floor a third of the way along the room's longer axis, looking at the far end 2.8 m up, so
the ceiling row is in frame. Roadmap 229's before-and-after frames use these; the same building
in two packages gives the same stations. It prints what it derived and stops.
"""
import json
import math
import sys
from pathlib import Path


def _rooms_of(ws, mission, bid):
    p = Path(ws) / ".level_factory" / "jobs" / f"{mission}.patina_apply.{bid}" / "1" / "out" / f"{bid}.patina.gameplay.json"
    if not p.exists():
        raise SystemExit(f"no gameplay manifest at {p}")
    return json.load(open(p, encoding="utf-8")).get("rooms") or []


def _building(ws, mission, bid):
    p = Path(ws) / ".level_factory" / "jobs" / f"{mission}.themed_site_assemble" / "1" / "out" / "site.site.drawn.json"
    if not p.exists():
        raise SystemExit(f"no drawn spec at {p}")
    d = json.load(open(p, encoding="utf-8"))
    for b in d.get("buildings") or []:
        if b.get("id") == bid:
            return b
    raise SystemExit(f"no building {bid} in {p}; have {[b.get('id') for b in d.get('buildings') or []]}")


def stations(rooms, at, rot_deg, n):
    picked = [r for r in rooms if int(r.get("story", 0)) in (0, 1) and "stair" not in str(r.get("id"))
              and r.get("bounds")]
    picked.sort(key=lambda r: -(r["bounds"][2] - r["bounds"][0]) * (r["bounds"][3] - r["bounds"][1]))
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))

    def world(x, y):
        return at[0] + c * x - s * y, at[1] + s * x + c * y

    out = []
    for r in picked[:n]:
        x0, y0, x1, y1 = r["bounds"]
        floor = float((r.get("center") or [0, 0, 0])[2])
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        if x1 - x0 >= y1 - y0:
            L, ux, uy = x1 - x0, 1.0, 0.0
        else:
            L, ux, uy = y1 - y0, 0.0, 1.0
        ex, ey = world(cx - 0.35 * L * ux, cy - 0.35 * L * uy)
        tx, ty = world(cx + 0.45 * L * ux, cy + 0.45 * L * uy)
        out.append((str(r["id"]), int(r.get("story", 0)), ex, ey, floor + 1.6, tx, ty, floor + 2.8))
    return out


def main(argv):
    if len(argv) < 3:
        raise SystemExit(__doc__)
    ws, mission, bid = argv[:3]
    n = int(argv[argv.index("--rooms") + 1]) if "--rooms" in argv else 4
    b = _building(ws, mission, bid)
    at = b.get("at") or [0.0, 0.0]
    rot = float(b.get("rot") or 0.0)
    # the jobs are keyed by the building's ARCHETYPE (deli_a01), the drawn spec by its id (b0)
    rooms = _rooms_of(ws, mission, b.get("archetype") or bid)
    got = stations(rooms, (float(at[0]), float(at[1])), rot, n)
    for name, story, ex, ey, ez, tx, ty, tz in got:
        print("# %s (storey %d): eye plan (%.1f, %.1f) %.1f up, looking at (%.1f, %.1f) %.1f up"
              % (name, story, ex, ey, ez, tx, ty, tz), file=sys.stderr)
    print(" ".join("--station %s:%g,%g,%g,%g,%g,%g" % (name, round(ex, 2), round(ez, 2), round(-ey, 2),
                                                         round(tx, 2), round(tz, 2), round(-ty, 2))
                   for name, story, ex, ey, ez, tx, ty, tz in got))


if __name__ == "__main__":
    main(sys.argv[1:])
