"""Photograph every interior room of a walk copy at night and measure it.

    python night_interior_census.py <walk_copy> <shots_dir> [--dc DIR] [--only NAME[,NAME]]

Frames: Deli Counter's spec frame (metres, x east, y north, z up from the
storey-0 floor) for rooms; Godot's for the site (x, y up, z = -spec y), and
each building's node transform in the walk copy's `site.tscn` takes one to
the other.

ONE STATION A ROOM, at a person's eye (1.6 m over the room's floor), standing
20% along the room's long axis and looking 80% along it at 1.0 m: across the
room, the way a body entering it sees it. Rooms come from Deli Counter's
`build/<building>.gameplay.json` (the library build the level's shell was
composed from); a building with none is skipped and named.

Each room is labelled by Deli Counter's own lighting rule (`lights.py`):
MOODY when below grade or an objective room that is not a public entrance
(bare bulbs, `_PENDANT_AREA`), else ROW (a fluorescent ceiling row).

Prints, per room: mean, median (p50) and crushed share (look_shots'
`crushed_pct`) of the 8-bit frame -- what it measured, not why. Run with the
walk copy's own lighting: `tools/look_shots.py` hides no light and keeps
Lux's post stack.
"""
import json
import os
import re
import subprocess
import sys

FACTORY = r"C:\Projects\gabagool_studios\gabagool_factory"
EYE = 1.6
LOOK_Z = 1.0


def _placements(walk):
    """``{building: (basis rows, origin)}`` from the walk copy's site.tscn."""
    t = open(os.path.join(walk, "site.tscn"), encoding="utf-8").read()
    res = dict(re.findall(r'\[ext_resource type="PackedScene" path="lot/([^/"]+)/site\.tscn" id="([^"]+)"\]', t))
    ids = {v: k for k, v in res.items()}
    out = {}
    for rid, tr in re.findall(r'\[node name="[^"]+"[^\]]*instance=ExtResource\("([^"]+)"\)\]\ntransform = Transform3D\(([^)]*)\)', t):
        if rid not in ids:
            continue
        v = [float(x) for x in tr.split(",")]
        basis = ((v[0], v[3], v[6]), (v[1], v[4], v[7]), (v[2], v[5], v[8]))   # rows: x', y', z'
        out[ids[rid]] = (basis, (v[9], v[10], v[11]))
    return out


def _to_site(placement, p):
    """Spec (x, y, z up) -> Godot building local (x, z, -y) -> site."""
    basis, origin = placement
    local = (p[0], p[2], -p[1])
    return tuple(sum(basis[r][c] * local[c] for c in range(3)) + origin[r] for r in range(3))


def stations(walk, dc, only=None):
    out, skipped = [], []
    for name, place in sorted(_placements(walk).items()):
        if only and name not in only:
            continue
        g = os.path.join(dc, "build", name + ".gameplay.json")
        if not os.path.exists(g):
            skipped.append(name)
            continue
        rooms = json.load(open(g, encoding="utf-8")).get("rooms") or []
        for r in rooms:
            x0, y0, x1, y1 = r["bounds"]
            fz = float((r.get("center") or [0, 0, 0])[2])
            story = int(r.get("story", 0) or 0)
            moody = story < 0 or (bool(r.get("objective")) and r.get("role") != "public_entry")
            if (x1 - x0) >= (y1 - y0):
                cy = (y0 + y1) / 2.0
                eye = (x0 + 0.2 * (x1 - x0), cy, fz + EYE)
                tgt = (x0 + 0.8 * (x1 - x0), cy, fz + LOOK_Z)
            else:
                cx = (x0 + x1) / 2.0
                eye = (cx, y0 + 0.2 * (y1 - y0), fz + EYE)
                tgt = (cx, y0 + 0.8 * (y1 - y0), fz + LOOK_Z)
            e, t = _to_site(place, eye), _to_site(place, tgt)
            sid = "%s__%s" % (name, r["id"])
            out.append({"name": sid, "building": name, "room": r["id"], "story": story,
                        "role": r.get("role"), "kind": "MOODY" if moody else "ROW",
                        "spec": ",".join("%.3f" % c for c in e + t)})
    return out, skipped


def main(argv):
    walk, shots = argv[0], argv[1]
    dc = os.path.join(FACTORY, "deli_counter")
    if "--dc" in argv:
        dc = argv[argv.index("--dc") + 1]
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    st, skipped = stations(walk, dc, only)
    if skipped:
        print("no gameplay.json, skipped:", ", ".join(skipped))
    cmd = [sys.executable, os.path.join(FACTORY, "tools", "look_shots.py"), walk, "--out", shots]
    for s in st:
        cmd += ["--station", "%s:%s" % (s["name"], s["spec"])]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit("look_shots failed: %d" % r.returncode)
    m = json.load(open(shots.rstrip("/\\") + ".json", encoding="utf-8"))
    got = {s["name"]: s for s in m["shots"]}
    print("%-44s %-6s %-14s %5s %6s %4s %8s" % ("room", "storey", "role", "kind", "mean", "p50", "crushed"))
    rows = []
    for s in st:
        g = got.get(s["name"])
        if g is None:
            print("%-44s NO SHOT" % s["name"])
            continue
        rows.append((s, g))
        print("%-44s %-6d %-14s %5s %6.1f %4d %7.1f%%" % (s["name"], s["story"], str(s["role"])[:14],
              s["kind"], g["mean"], g["p50"], g["crushed_pct"]))
    for kind in ("ROW", "MOODY"):
        k = [g for s, g in rows if s["kind"] == kind]
        if k:
            k.sort(key=lambda g: g["mean"])
            print("%s: %d rooms, mean of means %.1f, median room mean %.1f, rooms with p50 < 10: %d"
                  % (kind, len(k), sum(g["mean"] for g in k) / len(k), k[len(k) // 2]["mean"],
                     sum(1 for g in k if g["p50"] < 10)))


if __name__ == "__main__":
    main(sys.argv[1:])
