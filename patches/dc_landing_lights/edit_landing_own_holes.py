import sys, pathlib
p = pathlib.Path(sys.argv[1]); t = p.read_text(encoding="utf-8")
O = '''    for s, rects in sorted(axonometric._slab_holes(spec).items()):
        for r, kind in rects:
            if kind != "stair":
                add(s - 1, (r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0, "hole")'''
N = '''    for s, rects in sorted(axonometric._slab_holes(spec).items()):
        for r, kind in rects:
            if kind != "stair" and not _own_hole(spec, s, r):
                add(s - 1, (r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0, "hole")'''
assert t.count(O) == 1
t = t.replace(O, N)
O2 = '''def _landing_point(x, y, bounds, voids):'''
N2 = '''def _own_hole(spec, s, r):
    """Whether the hole ``r`` in storey ``s``'s slab is a ladder's or a stair's OWN cut -- that opening, not a second
    one. The build cuts both into the slabs it lights from (`Builder`: `ladder_geom.through_hole` for a ladder, the
    stair's run for a stair), so read off a built spec each was counted twice -- deli_a03's basement corridor took a
    lamp for its ladder and another, at the same point, for the ladder's own hole. A ladder spanning that slab whose
    through-hole centre falls in it; a stair serving the storeys either side whose footprint overlaps it."""
    import ladder_geom
    import stairwell
    for ld in getattr(spec, "ladders", []) or []:
        lo, hi = sorted((ld.from_story, ld.to_story))
        if lo < s <= hi:
            hx, hy, _sx, _sy = ladder_geom.through_hole(ld.x, ld.y, ld.width, ld.facing)
            if r[0] - 1e-6 <= hx <= r[2] + 1e-6 and r[1] - 1e-6 <= hy <= r[3] + 1e-6:
                return True
    for st in getattr(spec, "stairs", []) or []:
        served = stairwell.floors_served(spec, st)
        if s in served and (s - 1) in served:
            f = stairwell.footprint_rect(st)
            if r[0] < f[2] and f[0] < r[2] and r[1] < f[3] and f[1] < r[3]:
                return True
    return False


def _landing_point(x, y, bounds, voids):'''
assert t.count(O2) == 1
t = t.replace(O2, N2)
p.write_text(t, encoding="utf-8", newline="\n")
print("own-hole rule added to", p)
