"""Where does each light anchor sit relative to the walls of its building?

Roadmap 85 was raised on one screenshot: a hanging light half-buried in a wall
at a wall/ceiling junction in `bank_block_001`. Lux's co-location gate
(item 71) asks whether the spawned rig landed on its MARKER; nothing asks
whether the marker is in open space. This measures that, at spec time, from
what Deli Counter already writes:

* `<building>.lights.json` -- every anchor, with `pos` (Blender Z-up, metres,
  building-local), `rot_y`, and a `row` {count, spacing} that expands into
  lamp points centred on `pos` along `rot_y` (the same expansion Zoo's
  `fixtures.row_points` and Lux's fluorescent rig make);
* `<building>.slots.json` -- every wall slot as a centre, a `rot_y` and
  `fit.dims` [length, thickness, height], so a wall is a rotated box in XY.

For each lamp point of each ceiling-mounted anchor (`fluorescent`, `pendant`)
the probe reports the smallest distance to any wall's centreline on the same
storey, in the wall's own frame: negative means the point is INSIDE the wall's
thickness. Wall-mounted types (`window`, `sign`, `wall_pack`, streetlights)
sit on or off a wall by design and are counted separately, not judged.

    python tools\\anchor_wall_probe.py [--build deli_counter\\build] [--band 0.3]
        [--json out.json]

Prints what it measured and stops. Whether a lamp 0.2 m from a wall is a
defect depends on the fixture's housing, which this file does not know; the
number is here so that decision can be made from a count rather than a
screenshot.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FACTORY = os.path.dirname(HERE)

CEILING_TYPES = ("fluorescent", "pendant")


def row_points(anchor: dict) -> list[tuple[float, float, float]]:
    pos = anchor.get("pos") or [0.0, 0.0, 0.0]
    x, y, z = float(pos[0]), float(pos[1]), float(pos[2]) if len(pos) > 2 else 0.0
    row = anchor.get("row") or {}
    count = max(1, int(row.get("count", 1)))
    spacing = float(row.get("spacing", 0.0))
    if count == 1 or spacing <= 0.0:
        return [(x, y, z)]
    a = math.radians(float(anchor.get("rot_y", 0.0)))
    dx, dy = math.cos(a), math.sin(a)
    start = -(count - 1) * 0.5 * spacing
    return [(x + (start + i * spacing) * dx, y + (start + i * spacing) * dy, z)
            for i in range(count)]


def wall_boxes(slots: dict) -> list[dict]:
    out = []
    for s in slots.get("slots", []):
        if s.get("role") != "wall":
            continue
        t = s.get("transform") or {}
        c = t.get("translation") or [0.0, 0.0, 0.0]
        dims = (s.get("fit") or {}).get("dims") or [0.0, 0.0, 0.0]
        out.append({
            "id": s.get("slot_id"), "wall": s.get("wall"),
            "story": s.get("story"),
            "cx": float(c[0]), "cy": float(c[1]),
            "rot": math.radians(float(t.get("rot_y", 0.0))),
            "half_len": float(dims[0]) * 0.5,
            "half_thick": float(dims[1]) * 0.5,
        })
    return out


def signed_clearance(px: float, py: float, w: dict) -> float:
    """Distance from a point to a wall box in XY; negative when inside.

    The box is axis-aligned in the wall's own frame (length along its local
    x, thickness along its local y), so the point is rotated into that frame
    and measured against the half-extents. Outside the box this is the exact
    Euclidean distance to it; inside it is minus the depth of penetration on
    the shallower axis.
    """
    dx, dy = px - w["cx"], py - w["cy"]
    c, s = math.cos(-w["rot"]), math.sin(-w["rot"])
    u = dx * c - dy * s
    v = dx * s + dy * c
    ou = abs(u) - w["half_len"]
    ov = abs(v) - w["half_thick"]
    if ou > 0.0 and ov > 0.0:
        return math.hypot(ou, ov)
    if ou > 0.0:
        return ou
    if ov > 0.0:
        return ov
    return max(ou, ov)   # both <= 0: inside; the shallower penetration


def room_stories(gameplay: dict) -> dict:
    return {r.get("id"): int(r.get("story", 0)) for r in gameplay.get("rooms", [])}


def probe_building(stem: str, build: str) -> dict | None:
    try:
        lights = json.load(open(os.path.join(build, stem + ".lights.json"), encoding="utf-8"))
        slots = json.load(open(os.path.join(build, stem + ".slots.json"), encoding="utf-8"))
        gameplay = json.load(open(os.path.join(build, stem + ".gameplay.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return None
    walls = wall_boxes(slots)
    stories = room_stories(gameplay)
    lamps = []
    other = 0
    mounted = []
    for a in lights.get("anchors", []):
        if a.get("type") not in CEILING_TYPES:
            other += 1
            # Not judged, but measured: a wall-mounted anchor's clearance to
            # the nearest wall says where the derivation puts it relative
            # to the surface it hangs on. Storey is unknown for these (no
            # room), so every wall is a candidate.
            pos = a.get("pos") or [0.0, 0.0, 0.0]
            best = None
            for w in walls:
                d = signed_clearance(float(pos[0]), float(pos[1]), w)
                if best is None or d < best[0]:
                    best = (d, w["id"])
            mounted.append({"anchor": a.get("id"), "type": a.get("type"),
                            "clearance": round(best[0], 3) if best else None,
                            "wall": best[1] if best else None})
            continue
        story = stories.get(a.get("room"))
        same = [w for w in walls if story is None or w["story"] == story]
        for (x, y, z) in row_points(a):
            best = None
            for w in same:
                d = signed_clearance(x, y, w)
                if best is None or d < best[0]:
                    best = (d, w["id"])
            lamps.append({"anchor": a.get("id"), "type": a.get("type"),
                          "room": a.get("room"), "story": story,
                          "x": round(x, 3), "y": round(y, 3), "z": round(z, 3),
                          "clearance": round(best[0], 3) if best else None,
                          "wall": best[1] if best else None})
    return {"building": stem, "walls": len(walls), "lamps": lamps,
            "wall_mounted_anchors": other, "mounted": mounted}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--build", default=os.path.join(FACTORY, "deli_counter", "build"))
    ap.add_argument("--band", type=float, default=0.3,
                    help="report lamps closer than this to a wall (m)")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    stems = sorted(os.path.basename(p)[:-len(".lights.json")]
                   for p in glob.glob(os.path.join(args.build, "*.lights.json")))
    if not stems:
        print(f"no *.lights.json under {args.build}", file=sys.stderr)
        return 2
    results = []
    for stem in stems:
        r = probe_building(stem, args.build)
        if r is not None:
            results.append(r)

    lamps = [l for r in results for l in r["lamps"] if l["clearance"] is not None]
    inside = [l for l in lamps if l["clearance"] < 0.0]
    band = [l for l in lamps if 0.0 <= l["clearance"] < args.band]
    print(f"{len(results)} buildings read of {len(stems)}; "
          f"{sum(r['walls'] for r in results)} wall slots; "
          f"{len(lamps)} ceiling lamp points from "
          f"{sum(1 for r in results for _ in r['lamps'])} expanded anchors; "
          f"{sum(r['wall_mounted_anchors'] for r in results)} wall-mounted "
          f"anchors not judged")
    print(f"inside a wall's thickness: {len(inside)}")
    print(f"within {args.band:.2f} m of a wall (not inside): {len(band)}")
    if lamps:
        cl = sorted(l["clearance"] for l in lamps)
        print(f"clearance: min {cl[0]:.3f}  median {cl[len(cl)//2]:.3f}  "
              f"max {cl[-1]:.3f}")
    worst = sorted(lamps, key=lambda l: l["clearance"])[:15]
    if worst:
        print("closest lamp points:")
        for l in worst:
            b = next(r["building"] for r in results if l in r["lamps"])
            print(f"  {l['clearance']:7.3f} m  {b:28} {l['type']:11} "
                  f"{l['room']:24} ({l['x']:.2f}, {l['y']:.2f}, {l['z']:.2f}) "
                  f"wall {l['wall']}")
    unread = sorted(set(stems) - {r["building"] for r in results})
    if unread:
        print(f"not read (no slots or gameplay beside the lights): "
              + ", ".join(unread))
    by_type: dict = {}
    for r in results:
        for m in r["mounted"]:
            if m["clearance"] is not None:
                by_type.setdefault(m["type"], []).append(m["clearance"])
    if by_type:
        print("wall-mounted anchors, clearance to the nearest wall (negative "
              "= inside its thickness), by type:")
        for t, cl in sorted(by_type.items()):
            cl.sort()
            print(f"  {t:12} n {len(cl):4}  min {cl[0]:7.3f}  "
                  f"median {cl[len(cl)//2]:7.3f}  max {cl[-1]:7.3f}")
    per = {}
    for r in results:
        n = sum(1 for l in r["lamps"] if l["clearance"] is not None
                and l["clearance"] < args.band)
        if n:
            per[r["building"]] = n
    if per:
        print(f"buildings with a lamp point under {args.band:.2f} m: {len(per)}")
        for b, n in sorted(per.items(), key=lambda kv: -kv[1])[:20]:
            print(f"  {n:3}  {b}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"band": args.band, "buildings": results}, f, indent=1)
        print("wrote", args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
