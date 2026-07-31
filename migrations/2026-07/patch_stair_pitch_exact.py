"""Measure the ramp's actual tilt, not the bounding box around it.

TWO INSTRUMENTS DISAGREE, so one of them is wrong, and this decides which before
anything triggers a 57-building rebuild.

  check_stair_pitch.py reported 45-51 degrees, measured as

      atan2(dy, max(dx, dz))          # of the world-space AABB

  deli_counter/stair_place.stair_dims GENERATES the geometry as

      n   = max(6, round(H / profile["riser_target"]))
      run = min(8.0, max(3.0, round((n * 0.28) / 0.5) * 0.5))

  which for a 3.2 m storey at a ~0.18 riser is n=18, run=5.0, and a pitch of
  atan(3.2 / 5.0) = 32.6 degrees. Walkable, and nowhere near 45.

THE AABB IS THE WEAKER INSTRUMENT and I should have said so when I wrote it. A
stair ramp is a tilted SLAB, and the box around a tilted slab is taller and
shorter than the slab itself: for slab length L, thickness t and pitch p,

    aabb_dy = L*sin(p) + t*cos(p)
    aabb_dx = L*cos(p) + t*sin(p)

so the ratio always reads STEEPER than the surface is, and worse, `max(dx, dz)`
picks whichever horizontal extent is larger -- which is the stair's WIDTH, not its
run, whenever a short flight is wider than it is long. A basement flight with a
half-height rise is exactly that shape, and every steep reading was named
`stair0ramp_-1`, storey -1.

THE EXACT MEASUREMENT is already in the file. The ramp is a box rotated by its
pitch, so the inclination of its own local axes IS the pitch -- no inference from
extents needed. Take the node's world matrix, and for each of its three basis
vectors compute the angle between that axis and the horizontal plane. The slab's
long axis gives the surface pitch directly; its thin axis gives the same angle as
a normal, and the two agreeing is a self-check the AABB method cannot offer.

Reports BOTH numbers side by side, and flags rows where they disagree by more
than a degree, because a retracted measurement is cheaper to keep than to
rediscover -- and because the AABB reading is what a reader will remember unless
the correction sits next to it.

Asserts its target, refuses on a miss, idempotent.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
CHK = ROOT / "check_stair_pitch.py"

OLD_FN = '''def pitch_of(pts):
    """Pitch of the box's long axis, in degrees.

    A stair ramp is emitted as a tilted BOX, so its top surface pitch is the
    angle of its longest horizontal extent against its vertical extent. Measured
    from the oriented vertex cloud rather than assumed from the spec, because the
    spec is what produced it and two derivations of one number is the recurring
    defect here.
    """
    if len(pts) < 4:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    dx, dy, dz = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    run = max(dx, dz)
    if run < 1e-6:
        return None
    return math.degrees(math.atan2(dy, run))
'''

NEW_FN = '''def pitch_of(pts):
    """AABB estimate of pitch. RETAINED, AND WRONG -- see pitch_exact.

    This takes the world-space bounding box of the ramp and returns
    atan2(dy, max(dx, dz)). A stair ramp is a tilted SLAB, and the box around a
    tilted slab is both taller and shorter than the slab: for length L, thickness
    t and pitch p, dy = L*sin(p) + t*cos(p) and dx = L*cos(p) + t*sin(p), so the
    ratio always reads STEEPER than the surface is. Worse, max(dx, dz) picks the
    larger horizontal extent, which is the stair's WIDTH rather than its run
    whenever a flight is wider than it is long -- which a half-height basement
    flight is, and every steep reading was a storey -1 flight.

    It reported 45-51 degrees where stair_place.stair_dims generates about 33 for
    a 3.2 m storey. Kept beside the exact figure so the correction travels with
    the claim instead of the claim being remembered alone.
    """
    if len(pts) < 4:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    dx, dy, dz = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    run = max(dx, dz)
    if run < 1e-6:
        return None
    return math.degrees(math.atan2(dy, run))


def pitch_exact(m, local_pts):
    """Pitch of a ramp from its own world matrix, in degrees.

    Identify the slab's axes by its LOCAL EXTENTS, not by their inclination. A
    first version sorted the three axes by how steep they were and took the
    middle one as the run -- which is right below 45 degrees and silently returns
    the COMPLEMENT above it, because past 45 the long axis is steeper than the
    normal and the sort swaps them. It read a true 55 as 35, in exactly the range
    the stairs were being judged in, and its own agreement check reported perfect
    agreement because both readings came from the same swapped pair.

    The slab's thinnest local axis is its normal, unambiguously and at any pitch.
    The surface pitch is then the angle between that normal and vertical. The
    longest local axis is the run, and its inclination should equal the same
    pitch -- two genuinely independent readings, so their disagreement means
    something.

    Returns (pitch_deg, disagreement_deg) or None.
    """
    if len(local_pts) < 4:
        return None
    ext = []
    for ax in range(3):
        vals = [p[ax] for p in local_pts]
        ext.append(max(vals) - min(vals))
    thin = ext.index(min(ext))
    long_ = ext.index(max(ext))
    if thin == long_:
        return None

    def world_axis(c):
        v = (m[0][c], m[1][c], m[2][c])
        n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
        return None if n < 1e-9 else (v[0] / n, v[1] / n, v[2] / n)

    nv = world_axis(thin)
    rv = world_axis(long_)
    if nv is None or rv is None:
        return None
    # pitch from the NORMAL: a flat floor's normal is vertical, so the angle
    # between the normal and up IS the surface's tilt.
    from_normal = math.degrees(math.acos(min(1.0, abs(nv[1]))))
    # pitch from the RUN: how far the long axis rises out of horizontal.
    horiz = math.sqrt(rv[0] * rv[0] + rv[2] * rv[2])
    from_run = math.degrees(math.atan2(abs(rv[1]), horiz))
    return from_normal, abs(from_normal - from_run)
'''

OLD_CALL = '''            p = pitch_of(world)
            if p is None or p < 1.0:
                continue
            rows.append((stem, node.get("name"), p))
'''

NEW_CALL = '''            p = pitch_of(world)
            ex = pitch_exact(m, pts)
            if ex is None:
                continue
            exact, agree = ex
            if exact < 1.0:
                continue
            rows.append((stem, node.get("name"), exact, p, agree))
'''

OLD_WORST = '''    worst = {}
    for stem, nm, p in rows:
        if stem not in worst or p > worst[stem][1]:
            worst[stem] = (nm, p)
'''

NEW_WORST = '''    worst = {}
    for stem, nm, exact, aabb, agree in rows:
        if stem not in worst or exact > worst[stem][1]:
            worst[stem] = (nm, exact, aabb, agree)
'''

OLD_TABLE = '''    print(f"  {'building':<26}{'steepest ramp':<34}{'pitch':>7}   verdict")
    print("  " + "-" * 82)
    band = walls = fine = 0
    for stem, (nm, p) in sorted(worst.items(), key=lambda kv: -kv[1][1]):
        if p > nav_slope:
'''

NEW_TABLE = '''    print(f"  {'building':<24}{'steepest ramp':<30}{'pitch':>7}{'aabb':>7}"
          f"   verdict")
    print("  " + "-" * 88)
    band = walls = fine = 0
    disagree = 0
    for stem, (nm, p, aabb, agree) in sorted(worst.items(),
                                             key=lambda kv: -kv[1][1]):
        if agree > 1.0:
            disagree += 1
        if p > nav_slope:
'''

OLD_ROW = '''        print(f"  {stem:<26}{(nm or '')[:32]:<34}{p:6.1f}d   {v}")
'''

NEW_ROW = '''        print(f"  {stem:<24}{(nm or '')[:28]:<30}{p:6.1f}d{aabb:6.1f}d   {v}")
'''

OLD_SUM = '''    print(f"\\n  {fine} building(s) walkable, {band} in the 45-55 band, "
          f"{walls} above both")
'''

NEW_SUM = '''    print(f"\\n  {fine} building(s) walkable, {band} in the 45-55 band, "
          f"{walls} above both")
    print(f"  `pitch` is the ramp's own tilt, from its world matrix. `aabb` is "
          f"the old\\n  bounding-box estimate, kept visible because it read "
          f"steeper than the\\n  surface actually is and that number has already "
          f"been quoted.")
    if disagree:
        print(f"  {disagree} row(s) where the two axis readings disagree by more "
              f"than a degree --\\n  those rows are not trustworthy; the ramp may "
              f"not be a simple tilted slab.")
'''


def main() -> int:
    if not CHK.exists():
        raise SystemExit(f"missing {CHK}. Nothing written.")
    src = CHK.read_text(encoding="utf-8")
    if "def pitch_exact(" in src:
        print("check_stair_pitch.py: already measures the ramp's own tilt")
        return 0
    edits = (("pitch_of + pitch_exact", OLD_FN, NEW_FN),
             ("the measurement call", OLD_CALL, NEW_CALL),
             ("the per-building worst", OLD_WORST, NEW_WORST),
             ("the table header", OLD_TABLE, NEW_TABLE),
             ("the table row", OLD_ROW, NEW_ROW),
             ("the summary", OLD_SUM, NEW_SUM))
    for label, old, _new in edits:
        if src.count(old) != 1:
            raise SystemExit(f"check_stair_pitch.py: target for '{label}' "
                             f"appears {src.count(old)} time(s), expected "
                             f"exactly 1. NOTHING WRITTEN.")
    for label, old, new in edits:
        src = src.replace(old, new)
    backup = CHK.with_suffix(".py.pre_exact")
    if not backup.exists():
        shutil.copy2(CHK, backup)
    CHK.write_text(src, encoding="utf-8")
    py_compile.compile(str(CHK), doraise=True)
    print("  check_stair_pitch.py: pitch taken from the ramp's world matrix")
    print("  check_stair_pitch.py: the AABB estimate stays, labelled, beside it")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  Re-measure before changing any geometry:\n")
    print("    python check_stair_pitch.py")
    print("\n  If `pitch` comes back near 33 and `aabb` near 49, the stairs were "
          "never\n  too steep and the sliding has another cause -- do NOT rebuild "
          "57 buildings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
