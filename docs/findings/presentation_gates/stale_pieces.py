"""Every library shell: which existing volumes stand where a stair now is.
Measures; names no cause.

    python stale_pieces.py [--only a,b]

Two questions, per volume, on the storey it stands on (its base):
- HOLE: over a slab opening (`stairwell.slab_openings`), the holes the
  builder cuts.
- WALK: inside a flight's reserved rectangle on the storey the flight climbs
  from (`stairwell.flight_rect(st, s)` on storey s), or a landing or endpoint
  rect (`stairwell.stair_endpoints`) on a storey the stair serves.

Stair guards (`stair_guard_*`) are left out: they stand at a hole's edge by
design. The placement rules (`level_design._stair_reserved_rects`) are
applied only when a piece is placed, and every placement pass is idempotent
by name, so a piece placed before a stair changed is never asked again.
"""
import glob
import os
import sys

DC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "deli_counter"))
sys.path.insert(0, DC)
import stairwell  # noqa: E402
from spec_loader import load_spec  # noqa: E402

GUARD = "stair_guard_"
TOL = 0.02


def overlap(a, b):
    ox = min(a[2], b[2]) - max(a[0], b[0])
    oy = min(a[3], b[3]) - max(a[1], b[1])
    return ox * oy if ox > TOL and oy > TOL else 0.0


def walk_rects(s):
    """``{storey: [rect]}`` -- a flight's rectangle on the storey it climbs
    from, and every endpoint rect on its endpoint storeys."""
    out = {}
    for st in getattr(s, "stairs", ()) or ():
        if getattr(st, "style", None) == "spiral":
            continue
        lo = min(st.from_story, st.to_story)
        hi = max(st.from_story, st.to_story)
        for k in range(lo, hi):
            out.setdefault(k, []).append(stairwell.flight_rect(st, k))
        # An endpoint carries no storey: "lower" is the stair's lowest,
        # "upper" its highest (`stair_endpoints`' docstring). The first run
        # of this census filed both under the lowest.
        for e in stairwell.stair_endpoints(st):
            out.setdefault(lo if e["end"] == "lower" else hi, []).append(e["rect"])
    return out


def main():
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else None
    shells = sorted(os.path.basename(p)[:-len(".manifest.json")]
                    for p in glob.glob(os.path.join(DC, "build", "*.manifest.json")))
    rows, checked = [], 0
    for name in shells:
        if only and name not in only:
            continue
        path = os.path.join(DC, "specs", name + ".json")
        if not os.path.exists(path):
            continue
        s = load_spec(path)
        checked += 1
        holes = stairwell.slab_openings(s)
        walks = walk_rects(s)
        H = s.story_height
        for v in s.volumes:
            if v.name.startswith(GUARD):
                continue
            storey = int(round((v.z - v.size_z / 2.0) / H))
            r = (v.x - v.size_x / 2.0, v.y - v.size_y / 2.0, v.x + v.size_x / 2.0, v.y + v.size_y / 2.0)
            hole = sum(overlap(r, h) for h in holes.get(storey, []))
            walk = sum(overlap(r, w) for w in walks.get(storey, []))
            if hole or walk:
                rows.append((name, v.name, storey, round(hole, 2), round(walk, 2)))
    print("shells checked %d" % checked)
    print("volumes over a hole or in a stair's walk: %d in %d shells" % (len(rows), len({r[0] for r in rows})))
    print("  over a hole: %d; in a walk rect: %d; both: %d" % (
        sum(1 for r in rows if r[3]), sum(1 for r in rows if r[4]), sum(1 for r in rows if r[3] and r[4])))
    for r in rows:
        print("  %-30s %-40s storey %2d  hole %5.2f m2  walk %5.2f m2" % r)


if __name__ == "__main__":
    main()
