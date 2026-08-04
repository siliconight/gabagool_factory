"""Do the facade rules hold on EVERY building, or only on the one we watched?

WHY THIS EXISTS. Four rules landed today, and all four were derived, checked and
walked against a single building -- `category5_baie_dore_001`, a rectangular
beachfront casino. Each one has a stated limit that a rectangle cannot exercise:

  * `slots.outward_sign` takes the outward face as the one facing away from the
    footprint's bbox midpoint. Exact for a CONVEX footprint. At the inner corner
    of an L, the outer face can be nearer the midpoint than the inner one, and
    the rule points the dressing into the building.
  * `slots.world_oriented` reads dims listing the thin axis first as already
    rotated. A wall stub shorter than the wall is thick would read as rotated
    and be turned 90 degrees.
  * `arch.relief_parts` needs a wall wide enough to carry a bay; below that it
    returns a plain panel, which is correct but silent.
  * `arch.authored_void` clamps an opening into its module. A module shorter
    than its authored door would clamp and say nothing.

Deli Counter ships 109 manifests covering airports, arenas, train yards,
parking garages, rowhomes and mansions -- shapes a casino is not. This runs the
real Patina rules over all of them offline: no Blender, no Godot, no rebuild.

    python tools\\facade_rules_sweep.py <dir-with-slots-json> [--patina DIR]

WHAT THE INTERIOR TEST IS, and why it is not the centroid rule again. Asking
"does the cover point away from the centroid" would grade the rule with its own
answer. So the interior is taken from the FLOOR slots: a floor plate is a room's
own footprint, authored by Deli Counter, and a cover standing inside one is
inside the building by the building's own account. A manifest with no floor
slots (emitted before floors/ceilings landed) reports UNTESTED rather than
clean -- a rule nobody could check is not a rule that passed.

WHAT A NONZERO EXIT MEANS. The sweep did not run: no directory, no manifests,
no Patina. Findings exit 0; this reports, it does not gate.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _load_patina(explicit=None):
    """Import Patina from the sibling repo, or die saying which path failed."""
    cands = []
    if explicit:
        cands.append(explicit)
    try:
        sys.path.insert(0, HERE)
        import factory_paths
        cands.append(str(factory_paths.factory_root(HERE) / "patina"))
    except BaseException:
        # factory_paths EXITS rather than raises when the marker is missing --
        # correct for a checker that must not silently narrow its scope, wrong
        # for one candidate among several here. Catch the exit, keep looking.
        pass
    cands.append(os.path.normpath(os.path.join(HERE, "..", "patina")))
    for c in cands:
        if os.path.isdir(os.path.join(c, "patina")):
            sys.path.insert(0, c)
            from patina import framing, paneling, trim   # noqa: F401
            from patina import slots as S                # noqa: F401
            return framing, paneling, trim, S
    raise SystemExit("[facade_rules_sweep] NOT MEASURED: no patina package "
                     "found. Looked in: " + ", ".join(cands))


def floor_rects(manifest):
    """Interior rectangles in world XY, from the FLOOR slots.

    Deli Counter's own account of where the rooms are. Returns [] when the
    manifest predates floor slots, which the caller must report as untested.
    """
    out = []
    for s in manifest.slots:
        if s.role != "floor" or not s.dims:
            continue
        w, d, _h = s.size()
        cx, cy = float(s.translation[0]), float(s.translation[1])
        out.append((cx - w / 2.0, cy - d / 2.0, cx + w / 2.0, cy + d / 2.0))
    return out


def _inside(rects, x, y, shrink=0.0):
    for x0, y0, x1, y1 in rects:
        if (x0 + shrink) <= x <= (x1 - shrink) and \
           (y0 + shrink) <= y <= (y1 - shrink):
            return True
    return False


def wall_segments(manifest, S):
    """{storey: [(x0, y0, x1, y1)]} for the EXTERIOR walls, in world XY.

    The building's own outline, taken from the walls that draw it. Run and
    direction come from ``slots.wall_frame``, whose axis half is derived from
    the dims convention and NOT from the centroid -- so the parity test below
    does not grade the outward rule with the outward rule's own answer.
    """
    segs = {}
    center = S.footprint_center(manifest)
    thick_m = S.modal_thickness(manifest)
    for s in manifest.slots:
        if s.role not in ("wall", "doorway", "window", "breach") or not s.dims:
            continue
        if s.slot_id.startswith("int_"):
            continue                      # partitions are not the outline
        run, _thick, along, _out = S.wall_frame(s, center, thick_m)
        cx, cy = float(s.translation[0]), float(s.translation[1])
        hx, hy = along[0] * run / 2.0, along[1] * run / 2.0
        segs.setdefault(s.story, []).append(
            (cx - hx, cy - hy, cx + hx, cy + hy))
    return segs


def _crossings_inside(segs, x, y):
    """Even-odd point-in-polygon against the wall outline, ray along +X.

    A count rather than a polygon because the walls arrive as an unordered
    soup of segments and stitching them into a ring would invent an ordering
    the manifest does not state. Parity needs no ordering.
    """
    n = 0
    for x0, y0, x1, y1 in segs:
        if (y0 > y) == (y1 > y):
            continue                      # the segment does not straddle the ray
        t = (y - y0) / (y1 - y0)
        if x0 + t * (x1 - x0) > x:
            n += 1
    return n % 2 == 1


def fill_ratio(rects):
    """Floor area over bbox area: how much of its own bounding box a building
    actually occupies. A rectangle is ~1.0; an L or a courtyard is well under,
    and that is exactly where the centroid rule is at risk. A HINT, not a
    verdict -- overlapping room rects can push it past 1.0."""
    if not rects:
        return None
    area = sum((x1 - x0) * (y1 - y0) for x0, y0, x1, y1 in rects)
    bx0 = min(r[0] for r in rects); by0 = min(r[1] for r in rects)
    bx1 = max(r[2] for r in rects); by1 = max(r[3] for r in rects)
    box = (bx1 - bx0) * (by1 - by0)
    return (area / box) if box > 0 else None


def sweep_one(path, mods, seed=1999):
    framing, paneling, trim, S = mods
    with open(path, "r", encoding="utf-8") as fh:
        man = S.parse(json.load(fh))
    _sheet, regions = trim.build_sheet(size=64, seed=seed)

    walls = [s for s in man.slots if s.role == "wall" and s.dims]
    world = sum(1 for s in walls if S.world_oriented(s))
    rects = floor_rects(man)

    orders = (framing.gutter_orders(man, regions, seed=seed)
              + framing.pilaster_orders(man, regions, seed=seed)
              + paneling.panel_orders(man, regions, seed=seed))

    # THE TEST. Is the cover inside the outline its own storey's walls draw?
    # Parity against the wall segments, which is independent of the rule that
    # chose the cover's side -- the two disagree exactly when the rule is wrong.
    by_id = man.by_id()
    segs = wall_segments(man, S)
    inside = untestable = 0
    for o in orders:
        story = by_id[o["slot_id"]].story
        ring = segs.get(story)
        if not ring or len(ring) < 3:
            untestable += 1
            continue
        if _crossings_inside(ring, o["pos"][0], o["pos"][1]):
            inside += 1
    # Floor plates, when the manifest has them, are Deli Counter's own account
    # of the interior and a second opinion on the same question.
    floor_hits = sum(1 for o in orders
                     if _inside(rects, o["pos"][0], o["pos"][1], shrink=0.2))

    # A wall whose run is shorter than its thickness would be misread as
    # world-oriented and turned 90 degrees. Nothing in the corpus should have
    # one; this is the assumption stated out loud.
    # Walls whose RUN is at or under the wall thickness: the shape that used
    # to be misread as pre-rotated. Reported because it is real -- the casino
    # has one -- not because it still breaks anything.
    thick_m = S.modal_thickness(man)
    square = sum(1 for s in walls
                 if min(s.size()[0], s.size()[1]) >= thick_m - 1e-6
                 and max(s.size()[0], s.size()[1]) <= thick_m + 0.05)
    return {
        "name": os.path.basename(path).replace(".slots.json", ""),
        "slots": len(man.slots), "walls": len(walls),
        "world_oriented": world, "canonical": len(walls) - world,
        "floors": len(rects), "fill": fill_ratio(rects),
        "orders": len(orders), "inside": inside,
        "untestable": untestable, "floor_hits": floor_hits,
        "square_walls": square,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir", help="a directory holding *.slots.json")
    ap.add_argument("--patina", default=None, help="the patina repo root")
    ap.add_argument("--seed", type=int, default=1999)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    mods = _load_patina(args.patina)
    paths = sorted(glob.glob(os.path.join(args.dir, "*.slots.json")))
    if not paths:
        sys.stderr.write("[facade_rules_sweep] NOT MEASURED: no *.slots.json "
                         "in " + args.dir + "\n")
        return 2

    rows, broke = [], []
    for p in paths:
        try:
            rows.append(sweep_one(p, mods, args.seed))
        except Exception as exc:
            broke.append((os.path.basename(p), repr(exc)))

    if args.json:
        print(json.dumps({"buildings": rows, "errors": broke}, indent=2))
        return 0

    print("=" * 78)
    print("[facade_rules_sweep] %d manifest(s) in %s"
          % (len(paths), os.path.abspath(args.dir)))
    print("")
    print("  %-28s %6s %6s %6s %7s %7s %7s"
          % ("building", "walls", "world", "orders", "fill", "inside", "sq"))
    for r in sorted(rows, key=lambda r: (-r["inside"], r["name"])):
        fill = "  n/a" if r["fill"] is None else "%5.2f" % r["fill"]
        flag = "  <-- INSIDE" if r["inside"] else ""
        if r["untestable"] == r["orders"] and r["orders"]:
            flag = "  (untested: no wall outline)"
        print("  %-28s %6d %6d %6d %7s %7d %7d%s"
              % (r["name"][:28], r["walls"], r["world_oriented"],
                 r["orders"], fill, r["inside"], r["square_walls"], flag))

    tested = [r for r in rows if r["orders"] and r["untestable"] < r["orders"]]
    print("")
    print("  %d building(s), %d testable against their own wall outline"
          % (len(rows), len(tested)))
    unt = sum(r["untestable"] for r in rows)
    if unt:
        print("  covers on a storey with too few walls to form an outline: %d"
              % unt)
    fh = sum(r["floor_hits"] for r in rows)
    print("  second opinion (floor plates, where the manifest has them): %d hit(s)"
          % fh)
    bad = [r for r in tested if r["inside"]]
    print("  covers inside a room: %d building(s), %d cover(s)"
          % (len(bad), sum(r["inside"] for r in bad)))
    sq = sum(r["square_walls"] for r in rows)
    print("  walls whose run equals their thickness (unclassifiable): %d" % sq)
    odd = [r for r in tested if r["fill"] is not None and r["fill"] < 0.7]
    print("  non-rectangular footprints (fill < 0.70): %d -- the shapes the"
          % len(odd))
    print("  centroid rule is least sure of, and worth walking by eye:")
    for r in sorted(odd, key=lambda r: r["fill"])[:12]:
        print("     %-28s fill %.2f  inside %d"
              % (r["name"][:28], r["fill"], r["inside"]))
    if broke:
        print("")
        print("  DID NOT PARSE: %d" % len(broke))
        for name, err in broke[:10]:
            print("     %-28s %s" % (name[:28], err[:60]))
    print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
