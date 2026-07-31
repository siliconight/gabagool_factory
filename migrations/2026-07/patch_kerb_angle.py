"""Make the kerb cut cover the crossing, the slab stack legal, and the gate honest.

The step gate's first real report was LOT_STEP_BLOCKS_A_ROUTE on ballpark_block,
7 transitions. Measured against the emitted scene, those 7 have THREE separate
causes, and only one of them is the geometry everybody looked at first.

    4  road_0's kerb cuts are too NARROW, not misplaced
    2  the gate is over-reporting -- the route never touches those boxes
    1  courtyard_0 is 0.12 m and a body walks up 0.1025 m

Each is fixed below, with the measurement that identified it.

--------------------------------------------------------------------------------
1. THE CUT IS THE WIDTH OF THE PATH, WHICH ASSUMES A HEAD-ON CROSSING.

The four cut CENTRES are right to the centimetre -- computed against
site_steps.routes() independently, they agree: road0L at x +0.11 and -64.60,
road0R at -14.33 and -66.60. So `_kerb_crossings` finds the crossing correctly
and `_split_span` places the cut correctly. What it gets wrong is how much kerb
one crossing consumes:

    half = w / 2.0 + margin          # w = the path's width

A strip of width w meeting a LINE at angle t leaves w/sin(t) on that line, not
w. And the kerb is not a line -- it is a band `depth` deep, so the strip also
shears along the kerb by depth*cos(t)/sin(t). The along-kerb span a crossing
actually needs is

    (w + depth * cos t) / sin t

On ballpark_block, measured:

    kerb     path   kerb x   angle   emitted   needed   short by
    road0L   p0       0.11   34.7d      7.20    11.99       5.99
    road0L   p1     -64.60   78.7d      7.20     6.32     (fits)
    road0R   p0     -14.33   34.7d      7.20    11.99       5.99
    road0R   p1     -66.60   78.7d      7.20     6.32     (fits)

p0 is ops_warehouse -> ballpark_concourse, the spawn-to-objective route, and it
meets the kerb at 35 degrees. Its 6 m band covers 12 m of kerb; 7.2 m was
dropped; so the route spilled onto sidewalk_0L_2, sidewalk_0L_4, sidewalk_0R_2
and sidewalk_0R_4 either side of each cut and met a 0.16 m wall on all four.
Those are 4 of the 7. p1 is nearly square to the kerb and was always fine, which
is why the defect looked like a placement error rather than a width error.

The `width` parameter `_kerb_crossings` already takes -- the sidewalk depth --
was accepted and never used. It is used now.

--------------------------------------------------------------------------------
2. THE GATE'S "IS THIS ON A ROUTE" TEST OVER-REPORTS AT A CORNER.

site_steps._point_in tests a point against a convex polygon by projecting onto
the polygon's own axes and allowing `margin` of slack on each. That inflates the
polygon per-axis -- a BOX inflation -- which is not the set of points within
`margin` of it. Near a corner it over-reports by up to sqrt(2)*margin.

Re-measured with an exact point-to-rectangle distance, route p1's clearance to
sidewalk_0L_0, sidewalk_0L_2, sidewalk_0R_0 and sidewalk_0R_2 is 3.43 m against
a half-width of 3.00 m. The route does not touch them. Two of those pairs were
in the blocking set, so the gate was reporting a wall a body never reaches --
the instrument reproducing the defect class it was written to catch.

The projection test is kept as a cheap REJECT (it is a superset, so it cannot
produce a false negative) and an exact distance decides.

--------------------------------------------------------------------------------
3. THE SLAB THICKNESSES WERE PICKED, AND ONE OF THEM DRIFTED OUT OF LEGAL RANGE.

    PATH_THICK = 0.1     COURT_THICK = 0.12     ROAD_THICK = 0.08

against clearances.unassisted_step_max_m = 0.1025. Ground -> courtyard is
0.12 m: a wall, and ballpark_block's own circulation crosses it. That is the
7th finding. Ground -> path at 0.10 is legal by 2.5 mm, which is not a margin.

These are not free to choose. Every adjacent pair has to be walkable in both
directions, and the sidewalk is on the other side of each of them:

    ground 0.00      -> slab                 slab <= step
    slab             -> sidewalk 0.16        SIDEWALK_H - slab <= step

so a walkable slab has to sit inside [SIDEWALK_H - step, step], today
[0.0575, 0.1025]. Placing the three at fixed fractions of that band keeps them
ordered and visually distinct and moves them together when the gameplay team
picks a different body:

    ROAD_THICK  = band 15%      PATH_THICK = band 50%     COURT_THICK = band 85%

SIDEWALK_H is NOT derived and does not move: a kerb is meant to be a wall, and
that is the whole reason kerb cuts exist. But note what the band being non-empty
depends on -- SIDEWALK_H <= 2 * step. At 0.16 against 0.205 it holds with room;
below a player radius of about 0.273 m it does not, and no slab thickness would
be walkable both ways. The band collapsing is reported rather than clamped
silently, because this pass has already found four defects that were nothing but
a check going quiet.

--------------------------------------------------------------------------------
Touches lot/lot.py and lot/site_steps.py. Asserts every target before writing,
refuses on a miss, idempotent, keeps a backup, byte-compiles both, and prints the
resulting surface stack checked pair by pair.
"""
import json
import math
import os
import pathlib
import py_compile
import shutil
import subprocess
import sys

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LOT_PY = ROOT / "lot" / "lot.py"
STEPS_PY = ROOT / "lot" / "site_steps.py"
CONTRACT = ROOT / "deli_counter" / "agent_contract.json"

# ---------------------------------------------------------------------------
# lot.py -- 1. the slab stack
# ---------------------------------------------------------------------------

SLAB_OLD = '''PATH_THICK = 0.1
COURT_THICK = 0.12
GROUND_THICK = 0.5
WALL_THICK = 0.3
COVER = (1.0, 1.0, 1.0)
ROAD_THICK = 0.08
ROAD_COLOR = (0.13, 0.13, 0.14)        # asphalt
SIDEWALK_H = 0.16
SIDEWALK_COLOR = (0.55, 0.55, 0.57)    # concrete, raised curb
'''

SLAB_NEW = '''# The walkable slab thicknesses are DERIVED, not picked. A capsule walks up a
# step only while the contact normal stays inside floor_max_angle, which for the
# contract player is clearances.unassisted_step_max_m. Every adjacent pair of
# outdoor surfaces has to clear that in BOTH directions, and the sidewalk is on
# the other side of each slab:
#
#     ground 0.00  -> slab                    slab <= step
#     slab         -> sidewalk SIDEWALK_H     SIDEWALK_H - slab <= step
#
# so a walkable slab is squeezed into [SIDEWALK_H - step, step]. The picked
# values had drifted out of it: COURT_THICK was 0.12 against a step limit of
# 0.1025, which walled the courtyard edge on ballpark_block's own circulation,
# and PATH_THICK 0.10 was inside by 2.5 mm. Fixed fractions of the band keep the
# surfaces ordered and visually distinct and move them together when the
# gameplay team picks a different body.
GROUND_THICK = 0.5
WALL_THICK = 0.3
COVER = (1.0, 1.0, 1.0)
ROAD_COLOR = (0.13, 0.13, 0.14)        # asphalt
SIDEWALK_H = 0.16                      # a kerb is MEANT to be a wall
SIDEWALK_COLOR = (0.55, 0.55, 0.57)    # concrete, raised curb

#: The tallest step the contract player walks up with no step-up code.
STEP_MAX = float(_agent()["clearances"]["unassisted_step_max_m"])
#: Legal band for a slab walkable from the ground AND onto the sidewalk beside
#: it. Empty when the kerb is taller than two steps -- _outdoor_nodes says so
#: out loud rather than emitting a wall and letting play discover it.
SLAB_LO = SIDEWALK_H - STEP_MAX
SLAB_HI = STEP_MAX


def _slab(frac):
    """A walkable slab thickness at `frac` across the legal band."""
    if SLAB_LO > SLAB_HI:
        return round(SLAB_HI * 0.8, 4)
    return round(SLAB_LO + (SLAB_HI - SLAB_LO) * frac, 4)


ROAD_THICK = _slab(0.15)
PATH_THICK = _slab(0.50)
COURT_THICK = _slab(0.85)
'''

# ---------------------------------------------------------------------------
# lot.py -- 2. the crossing span
# ---------------------------------------------------------------------------

CROSS_OLD = '''    """Distances along a kerb where the site's own paths cross it.

    Returns the centre of each crossing measured from the road's start point.
    A path that runs parallel, or crosses beyond either end, contributes
    nothing -- there is no crossing to drop."""
'''

CROSS_NEW = '''    """(centre, span) per crossing: where a path crosses this kerb, and how much
    kerb that crossing consumes measured along it.

    Distances are from the road's start point. A path that runs parallel, or
    crosses beyond either end, contributes nothing -- there is no crossing to
    drop. `width` is the kerb band's depth."""
'''

SPAN_OLD = '''        out.append((t, float(p.get("width", 6.0))))
    return out
'''

SPAN_NEW = '''        # How much kerb this crossing consumes ALONG the kerb. A strip of width
        # pw meeting a LINE at angle t leaves pw/sin(t) on that line, not pw --
        # and a kerb is not a line, it is a band `width` deep, so the strip also
        # shears along it by width*cos(t)/sin(t). Dropping only pw assumed every
        # crossing was head-on: on ballpark_block a 6 m path meets the kerb at
        # 35 deg and needs 12.0 m, so a 7.2 m cut left the route spilling onto
        # the sidewalk sections either side and hitting a 0.16 m wall on both.
        pw = float(p.get("width", 6.0))
        vl = math.hypot(vx, vy) or 1e-9
        cos_t = abs(vx * ux + vy * uy) / vl
        sin_t = abs(vx * px + vy * py) / vl
        span = (pw + float(width) * cos_t) / max(sin_t, 1e-6)
        if span > 3.0 * pw:
            # Shallow enough that the path is running ALONG the kerb rather than
            # across it. The span is still emitted, because a body has to get
            # over the rise somewhere -- but a designer should see it, since the
            # honest fix is usually to re-route or to run the path on the
            # sidewalk instead of through it.
            print(f"[lot] LOT_KERB_CROSSED_SHALLOW: a {pw} m path meets this "
                  f"kerb at {math.degrees(math.asin(min(1.0, sin_t))):.0f} deg "
                  f"{t:.1f} m along it, so {span:.1f} m of kerb is dropped to "
                  f"keep the crossing walkable. Re-route it closer to square, "
                  f"or run it along the sidewalk rather than across it.")
        out.append((t, span))
    return out
'''

SPLIT_OLD = '''    """[(t0, t1, is_cut)] along a kerb: crossings, and the kerb between them.

    `margin` widens each crossing past the path itself so a body approaching at
    an angle still meets the dropped section rather than clipping its corner --
    the same reason a real dropped kerb is wider than the crossing painted on
    it."""
    spans = []
    bands = []
    for t, w in sorted(cuts):
        half = w / 2.0 + margin
'''

SPLIT_NEW = '''    """[(t0, t1, is_cut)] along a kerb: crossings, and the kerb between them.

    Each entry in `cuts` is (centre, span) from _kerb_crossings: where a route
    crosses, and the along-kerb length it actually covers -- which is wider than
    the path wherever the path meets the kerb at an angle. `margin` widens it
    further so a body approaching off-centre still meets the dropped section
    rather than clipping its corner, the same reason a real dropped kerb is
    wider than the crossing painted on it."""
    spans = []
    bands = []
    for t, span in sorted(cuts):
        half = span / 2.0 + margin
'''

# ---------------------------------------------------------------------------
# lot.py -- 3. say so when the band collapses
# ---------------------------------------------------------------------------

GUARD_ANCHOR = '''    body, sub = [], []
    bld = {b["id"]: b for b in site_spec["buildings"]}
'''

GUARD_NEW = '''    body, sub = [], []
    bld = {b["id"]: b for b in site_spec["buildings"]}
    if SLAB_LO > SLAB_HI:
        # No slab thickness is walkable in both directions. Emitting anyway and
        # staying quiet is how a wall reaches play; four defects in this pass
        # were a check going silent.
        print(f"[lot] LOT_SURFACE_STACK_IMPOSSIBLE: climbing a {SIDEWALK_H} m "
              f"kerb from the ground needs two steps of {STEP_MAX:.4f} m, so no "
              f"slab thickness clears both. Lower SIDEWALK_H below "
              f"{2 * STEP_MAX:.3f} m, or the body has to get wider.")
'''

# ---------------------------------------------------------------------------
# site_steps.py -- 4. an exact distance, not a box inflation
# ---------------------------------------------------------------------------

POINT_OLD = '''def _point_in(px, pz, corners, margin):
    for ax, az in _axes(corners):
        ln = math.hypot(ax, az)
        if ln < 1e-9:
            continue
        nx, nz = ax / ln, az / ln
        proj = [c[0] * nx + c[1] * nz for c in corners]
        d = px * nx + pz * nz
        if d < min(proj) - margin or d > max(proj) + margin:
            return False
    return True
'''

POINT_NEW = '''def _point_in(px, pz, corners, margin):
    """Is (px, pz) within `margin` of this convex plan polygon?

    The projection test is a cheap REJECT only. Allowing `margin` of slack on
    each of the polygon's own axes inflates it per-axis -- a BOX inflation --
    which is not the set of points within `margin` of the polygon. Near a corner
    it over-reports by up to sqrt(2)*margin, and it did: on ballpark_block it put
    two sidewalk sections into LOT_STEP_BLOCKS_A_ROUTE whose exact clearance from
    the route centreline was 3.43 m against a 3.00 m half-width. The route never
    reaches them. An instrument that reports a wall a body cannot touch is the
    same substitution defect it exists to catch, so the slack test rejects and an
    exact distance decides.
    """
    inside = True
    for ax, az in _axes(corners):
        ln = math.hypot(ax, az)
        if ln < 1e-9:
            continue
        nx, nz = ax / ln, az / ln
        proj = [c[0] * nx + c[1] * nz for c in corners]
        d = px * nx + pz * nz
        if d < min(proj) - margin or d > max(proj) + margin:
            return False                      # beyond margin on some axis
        if d < min(proj) or d > max(proj):
            inside = False
    if inside:
        return True
    n = len(corners)
    return any(_seg_point_dist(px, pz, corners[i], corners[(i + 1) % n])
               <= margin for i in range(n))


def _seg_point_dist(px, pz, a, b):
    """Exact distance from a plan point to a plan segment."""
    ax, az = a
    bx, bz = b
    dx, dz = bx - ax, bz - az
    ln2 = dx * dx + dz * dz
    if ln2 < 1e-12:
        return math.hypot(px - ax, pz - az)
    t = max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / ln2))
    return math.hypot(px - (ax + dx * t), pz - (az + dz * t))
'''

DOC_OLD = '''Lot's own outdoor surfaces sit at:

    Ground      top 0.00
    road        top 0.08     ROAD_THICK
    path        top 0.10     PATH_THICK
    courtyard   top 0.12     COURT_THICK
    sidewalk    top 0.16     SIDEWALK_H   -- "concrete, raised curb"

Stepping off the ground onto a sidewalk is a 0.16 m rise. That is a wall to a
stock CharacterBody3D, which is why walking from a spawn toward the street stops
at the kerb and needs a jump. The courtyard edge at 0.12 clears the limit by
3 mm, which is not a margin.
'''

DOC_NEW = '''Lot's own outdoor surfaces sit at:

    Ground      top 0.00
    road                     ROAD_THICK
    path                     PATH_THICK
    courtyard                COURT_THICK
    sidewalk    top 0.16     SIDEWALK_H   -- "concrete, raised curb"

The three slabs are derived in lot.py from this limit rather than pinned, and
have to satisfy it in both directions: walkable from the ground, and walkable
onto the sidewalk beside them, so each sits inside [SIDEWALK_H - limit, limit].
They were picked once and COURT_THICK had drifted to 0.12 against a limit of
0.1025 -- a wall, on ballpark_block's own circulation.

Stepping off the ground onto a sidewalk is a 0.16 m rise. That is a wall to a
stock CharacterBody3D, which is why walking from a spawn toward the street stops
at the kerb and needs a jump. It stays a wall on purpose; kerb cuts are what
make the crossings legal.
'''


def _swap(src, old, new, label, done, *, skip_if=None):
    if skip_if is not None and skip_if in src:
        done.append(f"  already applied: {label}")
        return src
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"{label}: target appears {n} time(s), expected exactly "
                         f"1. Read the file rather than forcing this. "
                         f"NOTHING WRITTEN.")
    done.append(f"  {label}")
    return src.replace(old, new)


def main() -> int:
    for p in (LOT_PY, STEPS_PY, CONTRACT):
        if not p.exists():
            raise SystemExit(f"missing {p}. Nothing written.")

    done = []

    src = LOT_PY.read_text(encoding="utf-8")
    src = _swap(src, SLAB_OLD, SLAB_NEW,
                "lot.py: slab thicknesses derived from the contract step limit",
                done, skip_if="def _slab(frac):")
    src = _swap(src, CROSS_OLD, CROSS_NEW,
                "lot.py: _kerb_crossings docstring says (centre, span)",
                done, skip_if="(centre, span) per crossing")
    src = _swap(src, SPAN_OLD, SPAN_NEW,
                "lot.py: crossing span accounts for the angle and the band depth",
                done, skip_if="LOT_KERB_CROSSED_SHALLOW")
    src = _swap(src, SPLIT_OLD, SPLIT_NEW,
                "lot.py: _split_span consumes a span, not a path width",
                done, skip_if="for t, span in sorted(cuts):")
    src = _swap(src, GUARD_ANCHOR, GUARD_NEW,
                "lot.py: an empty slab band is reported, not clamped quietly",
                done, skip_if="LOT_SURFACE_STACK_IMPOSSIBLE")

    steps_src = STEPS_PY.read_text(encoding="utf-8")
    steps_src = _swap(steps_src, POINT_OLD, POINT_NEW,
                      "site_steps.py: on-route test uses an exact distance",
                      done, skip_if="def _seg_point_dist(")
    steps_src = _swap(steps_src, DOC_OLD, DOC_NEW,
                      "site_steps.py: docstring stops quoting pinned heights",
                      done, skip_if="derived in lot.py from this limit")

    for path, text, suffix in ((LOT_PY, src, ".py.pre_angle"),
                               (STEPS_PY, steps_src, ".py.pre_angle")):
        backup = path.with_suffix(suffix)
        if not backup.exists():
            shutil.copy2(path, backup)
        path.write_text(text, encoding="utf-8")
        py_compile.compile(str(path), doraise=True)

    print("applied:")
    for line in done:
        print(line)
    print(f"  both files compile; previous copies kept as *{'.pre_angle'}")

    # ---- what the change produces, checked pair by pair ---------------------
    probe = r"""
import math, sys, os
sys.path.insert(0, os.getcwd())
import lot, site_steps
step = lot.STEP_MAX
stack = [("Ground", 0.0), ("road", lot.ROAD_THICK), ("path", lot.PATH_THICK),
         ("courtyard", lot.COURT_THICK), ("sidewalk", lot.SIDEWALK_H)]
print("  step limit %.4f m   legal slab band [%.4f, %.4f]"
      % (step, lot.SLAB_LO, lot.SLAB_HI))
print()
print("  %-12s %8s" % ("surface", "top"))
for n, h in stack:
    print("  %-12s %8.4f" % (n, h))
print()
print("  every pair a body can meet outdoors:")
bad = 0
for i in range(len(stack)):
    for j in range(len(stack)):
        if i >= j:
            continue
        a, b = stack[i], stack[j]
        rise = abs(b[1] - a[1])
        if rise <= 0.02:
            continue
        ok = rise <= step
        # ground -> sidewalk is a kerb and MEANT to be a wall; a cut is what
        # makes a crossing legal, and the cut is at road height.
        kerb = (a[0] == "Ground" and b[0] == "sidewalk")
        tag = "kerb, by design" if (kerb and not ok) else ("walks" if ok else "WALL")
        if not ok and not kerb:
            bad += 1
        print("    %-12s -> %-12s %6.4f  %s" % (a[0], b[0], rise, tag))
print()
print("  illegal pairs that are not the kerb itself: %d" % bad)
"""
    print("\n=========== the surface stack this produces ===========")
    r = subprocess.run([sys.executable, "-c", probe], capture_output=True,
                       text=True, cwd=str(LOT_PY.parent))
    print((r.stdout or "").rstrip() or (r.stderr or "").rstrip()[-1500:])

    print("\n  Rebuild changes GEOMETRY on every site with a road or a "
          "courtyard,\n  so the sweep is the check, not this script:\n")
    print("    python library_walk.py --timeout 1800")
    print("\n  On ballpark_block expect LOT_STEP_BLOCKS_A_ROUTE to clear: the "
          "four\n  spilled sidewalk sections are inside a wider cut, the two "
          "p1 sections\n  were never touched, and the courtyard edge is now "
          "under the limit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
