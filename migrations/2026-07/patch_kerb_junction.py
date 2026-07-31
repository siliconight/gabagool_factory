"""Drop the kerb where a ROAD crosses it, not only where a path does.

SEEN IN THE EDITOR on warehouse_district: sidewalk strips marching across the
asphalt at the crossroads.

MEASURED. warehouse_district has two roads --

    road_0  (-120, -15) -> (120, -15)   width 9, sidewalk
    road_1  (5, -90)    -> (5, 85)      width 8, sidewalk

-- which meet at (5, -15). _kerb_crossings only ever looks at `paths`:

    for p in site_spec.get("paths", []) or []:

so nothing cuts a kerb where another ROAD runs through it. Each road's 0.16 m
sidewalk therefore runs uncut straight across the other's carriageway: four
raised strips through the junction. That is a wall across a road, and it is
invisible to every gate we have -- site_steps only reports a rise where a
designed PATH crosses it, and a road is not a path.

THE FIX is the crossing list, not the arithmetic. The angle-aware span already
computed for paths is exactly right for a road; a road just brings its
carriageway width instead of a path width. Both go through the same loop.

A road does not cut its OWN kerb, and that falls out rather than needing a case:
a road is parallel to its own sidewalk, so the existing

    den = ux * (-vy) - uy * (-vx)
    if abs(den) < 1e-9:
        continue                      # parallel: never crosses

skips it exactly. Self-exclusion by geometry beats self-exclusion by name check.

WHAT THIS CHANGES. Junctions get their kerbs dropped for the full carriageway
width of the crossing road, so the crossing road's surface is continuous.
Sites with one road are untouched -- ballpark_block emits identical geometry.
warehouse_district and any other multi-road site change, so this needs a sweep
like every geometry change tonight.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LOT_PY = ROOT / "lot" / "lot.py"

DOC_OLD = '''    """(centre, span) per crossing: where a path crosses this kerb, and how much
    kerb that crossing consumes measured along it.

    Distances are from the road's start point. A path that runs parallel, or
    crosses beyond either end, contributes nothing -- there is no crossing to
    drop. `width` is the kerb band's depth."""
'''

DOC_NEW = '''    """(centre, span) per crossing: where a path OR another road crosses this
    kerb, and how much kerb that crossing consumes measured along it.

    Distances are from the road's start point. Anything that runs parallel, or
    crosses beyond either end, contributes nothing -- there is no crossing to
    drop. `width` is the kerb band's depth."""
'''

LOOP_OLD = '''    out = []
    for p in site_spec.get("paths", []) or []:
        try:
'''

LOOP_NEW = '''    out = []
    # Everything that crosses this kerb and therefore needs it dropped. `paths`
    # are the site's designed circulation; ROADS were missing entirely, and at a
    # junction that means one road's kerb runs uncut across the other's
    # carriageway -- four raised strips through the crossroads on
    # warehouse_district, a 0.16 m wall across a road. No gate catches it either:
    # site_steps reports a rise only where a designed PATH crosses it.
    #
    # The angle-aware span below is already correct for a road; a road simply
    # brings its carriageway width where a path brings its own. And a road does
    # not cut its own kerb without a special case, because a road is parallel to
    # its own sidewalk and the parallel test drops it.
    crossers = [(p, float(p.get("width", 6.0)), "path")
                for p in site_spec.get("paths", []) or []]
    crossers += [(r, float(r.get("width", 9.0)), "road")
                 for r in site_spec.get("roads", []) or []]
    for p, pw, kind in crossers:
        try:
'''

PW_OLD = '''        pw = float(p.get("width", 6.0))
        vl = math.hypot(vx, vy) or 1e-9
'''

PW_NEW = '''        vl = math.hypot(vx, vy) or 1e-9
'''

MSG_OLD = '''            print(f"[lot] LOT_KERB_CROSSED_SHALLOW: a {pw} m path meets this "
                  f"kerb at {math.degrees(math.asin(min(1.0, sin_t))):.0f} deg "
                  f"{t:.1f} m along it, so {span:.1f} m of kerb is dropped to "
                  f"keep the crossing walkable. Re-route it closer to square, "
                  f"or run it along the sidewalk rather than across it.")
'''

MSG_NEW = '''            print(f"[lot] LOT_KERB_CROSSED_SHALLOW: a {pw} m {kind} meets "
                  f"this kerb at "
                  f"{math.degrees(math.asin(min(1.0, sin_t))):.0f} deg "
                  f"{t:.1f} m along it, so {span:.1f} m of kerb is dropped to "
                  f"keep the crossing walkable. Re-route it closer to square, "
                  f"or run it along the sidewalk rather than across it.")
'''


def main() -> int:
    if not LOT_PY.exists():
        raise SystemExit(f"missing {LOT_PY}. Nothing written.")
    src = LOT_PY.read_text(encoding="utf-8")
    if "crossers = [" in src:
        print("lot.py: kerbs already dropped where roads cross them")
        return 0
    edits = (("the docstring", DOC_OLD, DOC_NEW),
             ("the crossing loop", LOOP_OLD, LOOP_NEW),
             ("the width lookup", PW_OLD, PW_NEW),
             ("the shallow-crossing notice", MSG_OLD, MSG_NEW))
    for label, old, _new in edits:
        if src.count(old) != 1:
            raise SystemExit(f"lot.py: target for '{label}' appears "
                             f"{src.count(old)} time(s), expected exactly 1. "
                             f"NOTHING WRITTEN.")
    for label, old, new in edits:
        src = src.replace(old, new)
    backup = LOT_PY.with_suffix(".py.pre_junction")
    if not backup.exists():
        shutil.copy2(LOT_PY, backup)
    LOT_PY.write_text(src, encoding="utf-8")
    py_compile.compile(str(LOT_PY), doraise=True)
    print("  lot.py: kerbs drop where a road crosses them, not only a path")
    print(f"  compiles; previous file kept at {backup.name}")

    # what it does to every site that has a kerb, before any rebuild
    import json
    import math
    import subprocess
    import sys
    probe = r"""
import json, math, os, sys
sys.path.insert(0, os.getcwd())
import lot
base = os.path.join(os.getcwd(), "specs")
for site in sorted(os.listdir(base)):
    spec_path = os.path.join(base, site, site + "_site.json")
    if not os.path.exists(spec_path):
        continue
    spec = json.load(open(spec_path, encoding="utf-8"))
    roads = spec.get("roads") or []
    if not any(r.get("sidewalk") for r in roads):
        continue
    bld = {b["id"]: b for b in spec["buildings"]}
    def ends(d):
        a = bld[d["from"]]["at"] if "from" in d else d["a"]
        b = bld[d["to"]]["at"] if "to" in d else d["b"]
        return (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))
    print("  " + site)
    for i, rd in enumerate(roads):
        sw = rd.get("sidewalk")
        if not sw:
            continue
        (ax, ay), (bx, by) = ends(rd)
        w = float(rd.get("width", 9.0))
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy) or 0.001
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        off = w / 2 + float(sw) / 2
        for side, sgn in (("L", 1), ("R", -1)):
            cuts = lot._kerb_crossings(spec, bld, (ax, ay), (ux, uy), (px, py),
                                       off * sgn, length, sw)
            spans = lot._split_span(length, cuts)
            drop = sum(b - a for a, b, c in spans if c)
            print("    road_%d%s  %d crossing(s), %.1f m dropped of %.0f m"
                  % (i, side, len(cuts), drop, length))
"""
    print("\n=========== crossings per kerb, after the change ===========")
    r = subprocess.run([sys.executable, "-c", probe], capture_output=True,
                       text=True, cwd=str(LOT_PY.parent))
    print((r.stdout or "").rstrip() or (r.stderr or "").rstrip()[-800:])
    print("\n  A single-road site should be unchanged. warehouse_district's two "
          "kerbs\n  should each gain one crossing -- the other road.")
    print("\n  This moves geometry, so it needs the sweep:\n")
    print("    python library_walk.py --timeout 1800")
    print("    python check_steps.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
